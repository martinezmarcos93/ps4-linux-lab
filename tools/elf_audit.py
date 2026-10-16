#!/usr/bin/env python3
"""Auditoría estática de solo lectura de los ELF de payload del loader (no los ejecuta ni los desensambla).

Comprueba hechos concretos y verificables sobre un ELF ya construido:
  * que su tabla de offsets por firmware (`fw_table`, sección .data) coincide fila a fila con `fw_offsets.h` de una revisión fija;
  * qué rutas de archivo literales contiene en .rodata (¿incluye rutas internas del almacenamiento?);
  * en qué secciones difieren dos ELF (p. ej. los payloads de distintos tamaños de VRAM).

Una coincidencia de tabla NO prueba que el resto del código (p. ej. los blobs kexec embebidos) corresponda a esa revisión.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

MAX_ELF = 64 * 1024 * 1024
FILA = 64  # sizeof(fw_offsets_t): u16 + padding + 7 x u64
CAMPOS = ("xfast_syscall", "printf_off", "kmem_alloc", "kernel_map", "patch1", "patch2", "pstate")


class ElfError(Exception):
    pass


def leer_elf(path: Path) -> bytes:
    p = Path(path)
    try:
        if p.is_symlink() or not p.is_file():
            raise ElfError(f"'{p}' no es un archivo regular")
        if p.stat().st_size > MAX_ELF:
            raise ElfError(f"'{p}' supera {MAX_ELF} bytes")
        return p.read_bytes()
    except OSError as exc:
        raise ElfError(f"no se pudo leer '{p}': {exc}") from exc


def secciones(elf: bytes) -> dict[str, tuple[int, int, int]]:
    """{nombre: (offset_en_archivo, tamaño, tipo)} de un ELF64 little-endian. Valida límites."""
    if len(elf) < 64 or elf[:4] != b"\x7fELF" or elf[4] != 2 or elf[5] != 1:
        raise ElfError("no es un ELF64 little-endian")
    shoff, = struct.unpack_from("<Q", elf, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", elf, 0x3A)
    if shentsize != 64 or shnum == 0 or shstrndx >= shnum:
        raise ElfError("tabla de secciones inválida")
    if shoff + shnum * 64 > len(elf):
        raise ElfError("la tabla de secciones excede el archivo")
    cab = []
    for i in range(shnum):
        nombre, tipo, _fl, _addr, off, size = struct.unpack_from("<IIQQQQ", elf, shoff + i * 64)
        cab.append((nombre, tipo, off, size))
    _, _, stroff, strsize = cab[shstrndx]
    if stroff + strsize > len(elf):
        raise ElfError("la tabla de nombres de sección excede el archivo")
    tabla = elf[stroff:stroff + strsize]
    salida: dict[str, tuple[int, int, int]] = {}
    for nombre, tipo, off, size in cab:
        fin = tabla.find(b"\0", nombre)
        n = tabla[nombre:fin if fin >= 0 else len(tabla)].decode("ascii", errors="replace")
        if tipo != 8 and off + size > len(elf):  # SHT_NOBITS (8) no ocupa archivo
            raise ElfError(f"la sección '{n}' excede el archivo")
        salida[n] = (off, size, tipo)
    return salida


def leer_fw_table(elf: bytes) -> list[tuple[int, ...]]:
    sec = secciones(elf)
    if ".data" not in sec:
        raise ElfError("el ELF no tiene sección .data")
    off, size, _ = sec[".data"]
    filas: list[tuple[int, ...]] = []
    for i in range(0, size - FILA + 1, FILA):
        ver, = struct.unpack_from("<H", elf, off + i)
        if ver == 0:
            break
        filas.append((ver,) + struct.unpack_from("<7Q", elf, off + i + 8))
    return filas


def leer_fw_table_fuente(texto: str) -> list[tuple[int, ...]]:
    filas = []
    for m in re.finditer(r"\{\s*(\d+),\s*((?:0x[0-9A-Fa-f]+,?\s*){7})\}", texto):
        vals = [int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", m.group(2))]
        filas.append((int(m.group(1)),) + tuple(vals))
    return filas


def comparar_tablas(elf_filas: list, src_filas: list) -> list[str]:
    errores = []
    if len(elf_filas) != len(src_filas):
        errores.append(f"número de filas distinto: ELF {len(elf_filas)} != fuente {len(src_filas)}")
    for a, b in zip(elf_filas, src_filas):
        if a != b:
            errores.append(f"fila {a[0]} difiere: ELF {[hex(x) for x in a[1:]]} != fuente {[hex(x) for x in b[1:]]}")
    return errores


def rutas_literales(elf: bytes) -> list[str]:
    sec = secciones(elf)
    if ".rodata" not in sec:
        return []
    off, size, _ = sec[".rodata"]
    return sorted({m.group().decode("ascii") for m in re.finditer(rb"/[\x21-\x7e]{2,120}", elf[off:off + size])})


def diferencias(a: bytes, b: bytes) -> dict:
    if len(a) != len(b):
        return {"mismo_tamano": False, "bytes_a": len(a), "bytes_b": len(b)}
    sec = secciones(a)
    por_seccion: dict[str, int] = {}
    total = 0
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            total += 1
            nombre = next((n for n, (off, size, tipo) in sec.items() if tipo != 8 and off <= i < off + size), "(fuera de secciones: cabeceras)")
            por_seccion[nombre] = por_seccion.get(nombre, 0) + 1
    return {"mismo_tamano": True, "bytes_distintos": total, "por_seccion": por_seccion}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("elf", type=Path)
    ap.add_argument("--fuente", type=Path, help="fw_offsets.h de la revisión del loader con la que contrastar")
    ap.add_argument("--comparar", type=Path, help="otro ELF cuyas diferencias por sección se informan")
    args = ap.parse_args(argv)
    try:
        elf = leer_elf(args.elf)
        filas = leer_fw_table(elf)
        salida: dict = {"filas_fw_table": len(filas), "firmwares": [f[0] for f in filas],
                        "rutas_literales_rodata": rutas_literales(elf)}
        codigo = 0
        if args.fuente:
            errores = comparar_tablas(filas, leer_fw_table_fuente(leer_elf(args.fuente).decode("utf-8")))
            salida["tabla_coincide_con_fuente"] = not errores
            salida["errores_tabla"] = errores
            codigo = 1 if errores else 0
        if args.comparar:
            salida["diferencias"] = diferencias(elf, leer_elf(args.comparar))
    except (ElfError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(salida, ensure_ascii=False, indent=2))
    return codigo


if __name__ == "__main__":
    sys.exit(main())

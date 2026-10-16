#!/usr/bin/env python3
"""Inspección de solo lectura de una imagen de disco (archivo regular).

Informa tamaño y tabla de particiones MBR/GPT de forma conservadora. NO abre
dispositivos de bloque, NO monta, NO repara y NO escribe: el archivo se abre
con O_RDONLY | O_NOFOLLOW y se rechaza todo lo que no sea un archivo regular.

Códigos de salida: 0 = sin hallazgos, 1 = hay advertencias, 2 = entrada rechazada.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import struct
import sys
import uuid
import zlib
from typing import Any

SECTOR = 512
GPT_SIGNATURE = b"EFI PART"
MAX_GPT_ENTRIES = 1024
MAX_GPT_ENTRY_SIZE = 4096


class ImageError(ValueError):
    """La entrada no es una imagen inspeccionable."""


def _open_regular(path: str) -> tuple[int, int]:
    """Abre en solo lectura y valida que sea un archivo regular (sin symlinks)."""
    if not path or "\x00" in path:
        raise ImageError("ruta vacía o con byte NUL")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        # lstat previo: evita abrir un FIFO/dispositivo (abrir ya puede tener efectos).
        pre = os.lstat(path)
        if not stat.S_ISREG(pre.st_mode):
            kind = "enlace simbólico" if stat.S_ISLNK(pre.st_mode) else "no es un archivo regular (dispositivo, directorio, FIFO…)"
            raise ImageError(f"{kind}: se rechaza")
        fd = os.open(path, flags)
    except OSError as exc:
        raise ImageError(f"no se puede abrir: {exc.strerror or exc}") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ImageError("no es un archivo regular")
    except BaseException:
        os.close(fd)
        raise
    return fd, info.st_size


def _read_at(fd: int, offset: int, length: int, size: int) -> bytes:
    if offset < 0 or offset >= size:
        return b""
    return os.pread(fd, min(length, size - offset), offset)


def _fs_hint(fd: int, offset_bytes: int, size: int) -> str:
    """Pista conservadora por firmas; no es una validación del sistema de archivos."""
    boot = _read_at(fd, offset_bytes, SECTOR, size)
    ext = _read_at(fd, offset_bytes + 1024, 1024, size)
    if len(ext) >= 58 and struct.unpack_from("<H", ext, 56)[0] == 0xEF53:
        return "ext2/3/4 (firma 0xEF53)"
    if len(boot) == SECTOR and boot[510:512] == b"\x55\xaa":
        if boot[82:90] == b"FAT32   ":
            return "FAT32 (firma)"
        if boot[54:59] == b"FAT16" or boot[54:59] == b"FAT12":
            return boot[54:59].decode("ascii") + " (firma)"
    return "desconocido"


def _parse_mbr(fd: int, size: int, warnings: list[str]) -> list[dict[str, Any]] | None:
    sector0 = _read_at(fd, 0, SECTOR, size)
    if len(sector0) < SECTOR or sector0[510:512] != b"\x55\xaa":
        return None
    parts: list[dict[str, Any]] = []
    for i in range(4):
        raw = sector0[446 + 16 * i: 462 + 16 * i]
        status, ptype = raw[0], raw[4]
        lba, count = struct.unpack_from("<II", raw, 8)
        if ptype == 0 and lba == 0 and count == 0:
            continue
        if status not in (0x00, 0x80):
            warnings.append(f"MBR[{i}]: byte de estado inválido 0x{status:02x}")
        if count == 0:
            warnings.append(f"MBR[{i}]: partición con 0 sectores")
        end = (lba + count) * SECTOR
        if lba * SECTOR >= size or end > size:
            warnings.append(f"MBR[{i}]: se extiende más allá del final de la imagen (¿truncada?)")
        parts.append({"indice": i, "tipo": f"0x{ptype:02x}", "activa": status == 0x80,
                      "lba_inicio": lba, "sectores": count, "bytes": count * SECTOR,
                      "fs_hint": _fs_hint(fd, lba * SECTOR, size) if lba * SECTOR < size else "fuera de imagen"})
    _check_overlaps(parts, "MBR", warnings, "lba_inicio", "sectores")
    return parts


def _check_overlaps(parts, etiqueta, warnings, key_start, key_len):
    spans = sorted((p[key_start], p[key_start] + p[key_len], p["indice"]) for p in parts if p[key_len])
    for (s1, e1, i1), (s2, e2, i2) in zip(spans, spans[1:]):
        if s2 < e1:
            warnings.append(f"{etiqueta}: las particiones {i1} y {i2} se solapan")


def _parse_gpt(fd: int, size: int, warnings: list[str]) -> list[dict[str, Any]] | None:
    hdr = _read_at(fd, SECTOR, SECTOR, size)
    if len(hdr) < 92 or hdr[:8] != GPT_SIGNATURE:
        return None
    (_rev, hsize, crc, _res, my_lba, alt_lba, first_usable, last_usable,
     _guid, entries_lba, n_entries, entry_size, entries_crc) = struct.unpack_from("<IIIIQQQQ16sQIII", hdr, 8)
    if not 92 <= hsize <= SECTOR:
        warnings.append(f"GPT: tamaño de cabecera inválido ({hsize})")
        return []
    check = bytearray(hdr[:hsize])
    check[16:20] = b"\x00\x00\x00\x00"
    if zlib.crc32(bytes(check)) != crc:
        warnings.append("GPT: CRC32 de la cabecera no coincide")
    if my_lba != 1:
        warnings.append(f"GPT: my_lba={my_lba}, se esperaba 1")
    if n_entries == 0 or n_entries > MAX_GPT_ENTRIES or entry_size < 128 or entry_size > MAX_GPT_ENTRY_SIZE or entry_size % 8:
        warnings.append(f"GPT: tabla de entradas inválida (n={n_entries}, tamaño={entry_size}); no se lee")
        return []
    table = _read_at(fd, entries_lba * SECTOR, n_entries * entry_size, size)
    if len(table) < n_entries * entry_size:
        warnings.append("GPT: la tabla de entradas está truncada")
    elif zlib.crc32(table) != entries_crc:
        warnings.append("GPT: CRC32 de la tabla de entradas no coincide")
    if alt_lba * SECTOR >= size:
        warnings.append("GPT: la cabecera de respaldo cae fuera de la imagen (¿truncada o disco más grande?)")
    parts: list[dict[str, Any]] = []
    for i in range(len(table) // entry_size):
        e = table[i * entry_size:(i + 1) * entry_size]
        tguid = uuid.UUID(bytes_le=e[:16])
        if tguid.int == 0:
            continue
        first, last = struct.unpack_from("<QQ", e, 32)
        name = e[56:128].decode("utf-16-le", "replace").split("\x00", 1)[0]
        if last < first:
            warnings.append(f"GPT[{i}]: LBA final < inicial")
        elif last >= first_usable and last_usable and last > last_usable:
            warnings.append(f"GPT[{i}]: fuera del rango usable declarado")
        if (last + 1) * SECTOR > size:
            warnings.append(f"GPT[{i}]: se extiende más allá del final de la imagen")
        parts.append({"indice": i, "tipo_guid": str(tguid), "nombre": name, "lba_inicio": first,
                      "lba_fin": last, "sectores": max(0, last - first + 1),
                      "fs_hint": _fs_hint(fd, first * SECTOR, size) if first * SECTOR < size else "fuera de imagen"})
    _check_overlaps(parts, "GPT", warnings, "lba_inicio", "sectores")
    return parts


def inspect_image(path: str) -> dict[str, Any]:
    try:
        fd, size = _open_regular(path)
    except OSError as exc:
        raise ImageError(f"no se puede abrir: {exc.strerror or exc}") from exc
    warnings: list[str] = []
    try:
        report: dict[str, Any] = {"ruta": path, "tamano_bytes": size, "solo_lectura": True}
        if size == 0:
            warnings.append("imagen vacía")
            report.update(tabla="ninguna", particiones=[])
        elif size < SECTOR:
            warnings.append("imagen menor que un sector (512 bytes)")
            report.update(tabla="ninguna", particiones=[])
        else:
            if size % SECTOR:
                warnings.append(f"tamaño no múltiplo de 512 ({size % SECTOR} bytes sobrantes)")
            mbr = _parse_mbr(fd, size, warnings)
            gpt = _parse_gpt(fd, size, warnings)
            if gpt is not None:
                report.update(tabla="gpt", particiones=gpt)
                if mbr is not None and not any(p["tipo"] == "0xee" for p in mbr):
                    warnings.append("GPT presente pero el MBR no es protector (tipo 0xEE): estructura híbrida o ambigua")
            elif mbr is not None:
                if any(p["tipo"] == "0xee" for p in mbr):
                    warnings.append("MBR protector 0xEE sin cabecera GPT válida")
                report.update(tabla="mbr", particiones=mbr)
            else:
                report.update(tabla="ninguna", particiones=[])
                warnings.append("sin firma de MBR (0x55AA) ni de GPT")
    finally:
        os.close(fd)
    report["advertencias"] = warnings
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagen")
    ap.add_argument("--json", action="store_true", help="salida en JSON")
    a = ap.parse_args(argv)
    try:
        r = inspect_image(a.imagen)
    except (ImageError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print(f"{r['ruta']}: {r['tamano_bytes']} bytes, tabla={r['tabla']}")
        for p in r["particiones"]:
            print("  ", {k: v for k, v in p.items()})
        for w in r["advertencias"]:
            print("ADVERTENCIA:", w)
    return 1 if r["advertencias"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

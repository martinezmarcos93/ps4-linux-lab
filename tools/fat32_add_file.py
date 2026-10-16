#!/usr/bin/env python3
"""Agrega un archivo al directorio raíz de una partición FAT32 dentro de una IMAGEN (archivo regular).

Sin privilegios, sin montar, sin loop devices. Rechaza dispositivos de bloque, symlinks y cualquier
cosa que no sea un archivo regular; nunca sobrescribe ni elimina entradas existentes.

Pensado para preparar la partición de arranque de una copia de imagen (p. ej. añadir `bzImage`),
verificable después con `fsck.vfat -n` y con tools/verify_boot_chain.py. No sustituye a un driver FAT completo:
solo escribe en el directorio raíz, con nombre largo (LFN) y alias corto generado.
"""
from __future__ import annotations

import argparse
import os
import re
import stat
import struct
import sys
from pathlib import Path

SECTOR = 512
FIJA_FECHA = (2026, 1, 1)  # fecha determinista para builds reproducibles
NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9 ._+,;=\[\]()@#$%&'!~^{}-]{1,255}$")
RESERVADOS_DOS = {"CON", "PRN", "AUX", "NUL", *{f"COM{i}" for i in range(1, 10)}, *{f"LPT{i}" for i in range(1, 10)}}


class FatError(Exception):
    pass


class _Fat32:
    def __init__(self, fd: int, part_off: int, part_size: int):
        self.fd, self.off, self.size = fd, part_off, part_size
        boot = self._leer(0, 512)
        if len(boot) < 512 or boot[510:512] != b"\x55\xaa":
            raise FatError("la partición no tiene sector de arranque válido (firma 0x55AA)")
        if boot[0x52:0x5A] != b"FAT32   ":
            raise FatError("la partición no es FAT32 (marca 'FAT32   ' ausente)")
        self.bps, self.spc, self.reservados, self.nfats = struct.unpack_from("<HBHB", boot, 0x0B)
        total16, = struct.unpack_from("<H", boot, 0x13)
        total32, = struct.unpack_from("<I", boot, 0x20)
        self.fat_sectores, = struct.unpack_from("<I", boot, 0x24)
        self.raiz, = struct.unpack_from("<I", boot, 0x2C)
        self.fsinfo, = struct.unpack_from("<H", boot, 0x30)
        if self.bps != 512 or self.spc not in (1, 2, 4, 8, 16, 32, 64, 128) or self.nfats not in (1, 2) or self.reservados < 1 or self.fat_sectores < 1:
            raise FatError("parámetros BPB no soportados")
        total = total32 or total16
        if total <= 0 or total * self.bps > part_size:
            raise FatError("el BPB declara un tamaño de partición inválido")
        self.inicio_datos = self.reservados + self.nfats * self.fat_sectores
        if self.inicio_datos >= total:
            raise FatError("las regiones reservada/FAT exceden el volumen declarado")
        self.cluster_bytes = self.spc * self.bps
        self.clusters = (total - self.inicio_datos) // self.spc
        if self.clusters < 65525:
            raise FatError("menos de 65525 clusters: no es FAT32")
        # La FAT debe contener una entrada de 32 bits para cada cluster y las reservadas.
        if self.fat_sectores * self.bps // 4 < self.clusters + 2:
            raise FatError("la FAT declarada no contiene entradas suficientes para el volumen")
        if self.raiz < 2 or self.raiz >= self.clusters + 2:
            raise FatError("cluster raíz inválido")

    # --- E/S
    def _leer(self, rel: int, n: int) -> bytes:
        if rel < 0 or rel + n > self.size:
            raise FatError("lectura fuera de la partición")
        return os.pread(self.fd, n, self.off + rel)

    def _escribir(self, rel: int, datos: bytes) -> None:
        if rel < 0 or rel + len(datos) > self.size:
            raise FatError("escritura fuera de la partición")
        if os.pwrite(self.fd, datos, self.off + rel) != len(datos):
            raise FatError("escritura incompleta")

    def _off_cluster(self, c: int) -> int:
        return (self.inicio_datos + (c - 2) * self.spc) * self.bps

    # --- FAT
    def _fat_entrada(self, c: int) -> int:
        raw = self._leer(self.reservados * self.bps + c * 4, 4)
        return struct.unpack("<I", raw)[0] & 0x0FFFFFFF

    def _fijar_fat(self, c: int, valor: int) -> None:
        for i in range(self.nfats):
            base = (self.reservados + i * self.fat_sectores) * self.bps
            self._escribir(base + c * 4, struct.pack("<I", valor & 0x0FFFFFFF))

    def _cadena(self, c: int) -> list[int]:
        cad, vistos = [], set()
        while True:
            # Solo 0x0FFFFFF8..0x0FFFFFFF son marcadores válidos de fin de cadena.
            # Un cluster libre/reservado/dañado no puede aceptarse como terminación.
            if c >= 0x0FFFFFF8:
                return cad
            if c in (0, 1) or 0x0FFFFFF0 <= c <= 0x0FFFFFF7:
                raise FatError("cadena de clusters termina en un valor FAT inválido")
            if c < 2 or c >= self.clusters + 2:
                raise FatError("cadena de clusters fuera de rango")
            if c in vistos or len(cad) >= self.clusters:
                raise FatError("cadena de clusters con ciclo")
            vistos.add(c)
            cad.append(c)
            c = self._fat_entrada(c)

    def _libres(self, n: int) -> list[int]:
        libres: list[int] = []
        tabla_off = self.reservados * self.bps
        bloque = 1 << 16
        total_entradas = self.clusters + 2
        c = 2
        while c < total_entradas and len(libres) < n:
            cant = min(bloque // 4, total_entradas - c)
            datos = self._leer(tabla_off + c * 4, cant * 4)
            for i in range(cant):
                if struct.unpack_from("<I", datos, i * 4)[0] & 0x0FFFFFFF == 0:
                    libres.append(c + i)
                    if len(libres) == n:
                        break
            c += cant
        if len(libres) < n:
            raise FatError("no hay clusters libres suficientes")
        return libres

    # --- FSInfo
    def _actualizar_fsinfo(self, usados: int, ultimo: int) -> None:
        if self.fsinfo in (0, 0xFFFF):
            return
        rel = self.fsinfo * self.bps
        fs = bytearray(self._leer(rel, 512))
        if fs[0:4] != b"RRaA" or fs[484:488] != b"rrAa":
            return
        libres, = struct.unpack_from("<I", fs, 488)
        if libres != 0xFFFFFFFF:
            struct.pack_into("<I", fs, 488, max(libres - usados, 0))
        struct.pack_into("<I", fs, 492, ultimo)
        self._escribir(rel, bytes(fs))

    # --- directorio raíz
    def entradas_raiz(self) -> tuple[list[int], bytes]:
        cad = self._cadena(self.raiz)
        return cad, b"".join(self._leer(self._off_cluster(c), self.cluster_bytes) for c in cad)


def _checksum_corto(corto11: bytes) -> int:
    s = 0
    for c in corto11:
        s = (((s & 1) << 7) + (s >> 1) + c) & 0xFF
    return s


def _fecha_hora() -> tuple[int, int]:
    a, m, d = FIJA_FECHA
    return ((a - 1980) << 9) | (m << 5) | d, 0


def _alias_corto(nombre: str, existentes: set[bytes]) -> bytes:
    base, _, ext = nombre.rpartition(".") if "." in nombre.strip(".") else (nombre, "", "")
    limpio = lambda s: re.sub(r"[^A-Z0-9_$%'\-@~!#&(){}^]", "", s.upper())
    b, e = limpio(base) or "ARCH", limpio(ext)[:3]
    for n in range(1, 1_000_000):
        sufijo = f"~{n}"
        cand = (b[:8 - len(sufijo)] + sufijo).ljust(8).encode("ascii") + e.ljust(3).encode("ascii")
        if cand not in existentes:
            return cand
    raise FatError("no se pudo generar un alias corto único")


def _entradas_lfn(nombre: str, corto11: bytes) -> list[bytes]:
    chk = _checksum_corto(corto11)
    u = nombre.encode("utf-16-le")
    unidades = [struct.unpack_from("<H", u, i)[0] for i in range(0, len(u), 2)]
    if len(unidades) % 13:
        unidades.append(0x0000)
    while len(unidades) % 13:
        unidades.append(0xFFFF)
    trozos = [unidades[i:i + 13] for i in range(0, len(unidades), 13)]
    salida = []
    for idx in range(len(trozos), 0, -1):
        t = trozos[idx - 1]
        e = bytearray(32)
        e[0] = idx | (0x40 if idx == len(trozos) else 0)
        e[11], e[12], e[13] = 0x0F, 0, chk
        for k, pos in enumerate((1, 3, 5, 7, 9, 14, 16, 18, 20, 22, 24, 28, 30)):
            struct.pack_into("<H", e, pos, t[k])
        salida.append(bytes(e))
    return salida


def _nombres_existentes(raiz: bytes) -> tuple[set[str], set[bytes]]:
    largos: set[str] = set()
    cortos: set[bytes] = set()
    lfn: dict[int, str] = {}
    for i in range(0, len(raiz), 32):
        e = raiz[i:i + 32]
        if e[0] == 0x00:
            break
        if e[0] == 0xE5:
            lfn.clear()
            continue
        if e[11] == 0x0F:
            trozo = b"".join(e[p:p + 2] for p in (1, 3, 5, 7, 9, 14, 16, 18, 20, 22, 24, 28, 30))
            texto = trozo.decode("utf-16-le", errors="replace").split("\x00")[0].split("￿")[0]
            lfn[e[0] & 0x1F] = texto
            continue
        cortos.add(bytes(e[:11]))
        nombre_corto = e[:8].decode("cp437", "replace").rstrip() + ("." + e[8:11].decode("cp437", "replace").rstrip() if e[8:11].strip() else "")
        largos.add(nombre_corto.lower())
        if lfn:
            largos.add("".join(lfn[k] for k in sorted(lfn)).lower())
        lfn.clear()
    return largos, cortos


def validar_nombre(nombre: str) -> None:
    if not NOMBRE_VALIDO.match(nombre) or nombre in (".", "..") or nombre != nombre.strip() or nombre.endswith("."):
        raise FatError(f"nombre de archivo no admitido: {nombre!r}")
    if nombre.split(".")[0].upper() in RESERVADOS_DOS:
        raise FatError(f"nombre reservado de DOS: {nombre!r}")


def agregar_archivo(imagen: Path, part_off: int, part_size: int, nombre: str, datos: bytes) -> dict:
    """Escribe `datos` como `nombre` en la raíz de la FAT32. Devuelve un resumen. Falla si ya existe."""
    validar_nombre(nombre)
    if not datos:
        raise FatError("no se agregan archivos vacíos")
    p = Path(imagen)
    st = os.lstat(p)
    if stat.S_ISBLK(st.st_mode) or stat.S_ISCHR(st.st_mode):
        raise FatError("se rechazan dispositivos: solo archivos de imagen")
    if not stat.S_ISREG(st.st_mode):
        raise FatError("la imagen debe ser un archivo regular (no symlink, directorio ni FIFO)")
    if part_off < 0 or part_size <= 0 or part_off + part_size > st.st_size:
        raise FatError("la partición indicada excede el archivo de imagen")
    fd = os.open(p, os.O_RDWR | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    try:
        fat = _Fat32(fd, part_off, part_size)
        cad_raiz, raiz = fat.entradas_raiz()
        largos, cortos = _nombres_existentes(raiz)
        if nombre.lower() in largos:
            raise FatError(f"ya existe '{nombre}' en el directorio raíz; no se sobrescribe")
        corto = _alias_corto(nombre, cortos)
        lfn = _entradas_lfn(nombre, corto)
        necesarias = len(lfn) + 1

        n_clusters = -(-len(datos) // fat.cluster_bytes)
        libres = fat._libres(n_clusters + 1)  # +1 de reserva por si la raíz debe crecer
        datos_cl, extra = libres[:n_clusters], libres[n_clusters]

        # hueco de entradas contiguas en la raíz
        total_slots = len(raiz) // 32
        inicio = None
        corrida = 0
        for s in range(total_slots):
            if raiz[s * 32] in (0x00, 0xE5):
                corrida += 1
                if corrida == necesarias:
                    inicio = s - necesarias + 1
                    break
            else:
                corrida = 0
        crece = inicio is None
        if crece:
            inicio = total_slots - corrida if corrida else total_slots
            if inicio + necesarias > total_slots + fat.cluster_bytes // 32:
                raise FatError("la entrada de directorio no cabe ni agregando un cluster a la raíz")
        # --- escritura (datos primero, metadatos al final)
        for i, c in enumerate(datos_cl):
            trozo = datos[i * fat.cluster_bytes:(i + 1) * fat.cluster_bytes]
            fat._escribir(fat._off_cluster(c), trozo.ljust(fat.cluster_bytes, b"\0"))
        for i, c in enumerate(datos_cl):
            fat._fijar_fat(c, datos_cl[i + 1] if i + 1 < len(datos_cl) else 0x0FFFFFFF)
        usados = n_clusters
        if crece:
            fat._escribir(fat._off_cluster(extra), b"\0" * fat.cluster_bytes)
            fat._fijar_fat(cad_raiz[-1], extra)
            fat._fijar_fat(extra, 0x0FFFFFFF)
            cad_raiz = cad_raiz + [extra]
            usados += 1
        fecha, hora = _fecha_hora()
        ent = bytearray(32)
        ent[0:11] = corto
        ent[11] = 0x20
        struct.pack_into("<HHH", ent, 14, hora, fecha, fecha)
        struct.pack_into("<H", ent, 20, (datos_cl[0] >> 16) & 0xFFFF)
        struct.pack_into("<HH", ent, 22, hora, fecha)
        struct.pack_into("<H", ent, 26, datos_cl[0] & 0xFFFF)
        struct.pack_into("<I", ent, 28, len(datos))
        bloque = b"".join(lfn) + bytes(ent)
        for k in range(0, len(bloque), 32):
            slot = inicio + k // 32
            cl_idx, dentro = divmod(slot * 32, fat.cluster_bytes)
            fat._escribir(fat._off_cluster(cad_raiz[cl_idx]) + dentro, bloque[k:k + 32])
        fat._actualizar_fsinfo(usados, datos_cl[-1])
        os.fsync(fd)
        return {"nombre": nombre, "alias_corto": corto.decode("ascii").rstrip(), "bytes": len(datos),
                "clusters": n_clusters, "raiz_crecio": crece}
    finally:
        os.close(fd)


def particion_mbr(imagen: Path, numero: int) -> tuple[int, int]:
    """(offset_bytes, tamaño_bytes) de una partición primaria MBR (1-4)."""
    if not 1 <= numero <= 4:
        raise FatError("número de partición fuera de 1-4")
    with open(imagen, "rb") as f:
        mbr = f.read(512)
    if len(mbr) < 512 or mbr[510:512] != b"\x55\xaa":
        raise FatError("la imagen no tiene MBR válido")
    e = mbr[0x1BE + (numero - 1) * 16: 0x1BE + numero * 16]
    lba, sectores = struct.unpack_from("<II", e, 8)
    if e[4] == 0 or sectores == 0:
        raise FatError(f"la partición {numero} está vacía")
    return lba * SECTOR, sectores * SECTOR


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagen", type=Path, help="archivo de imagen (COPIA de trabajo; se modifica en el lugar)")
    ap.add_argument("--particion", type=int, default=1, help="partición MBR primaria que contiene la FAT32 (por defecto 1)")
    ap.add_argument("--nombre", required=True, help="nombre destino en la raíz de la FAT (p. ej. bzImage)")
    ap.add_argument("--archivo", required=True, type=Path, help="archivo local cuyo contenido se copia")
    args = ap.parse_args(argv)
    try:
        src = Path(args.archivo)
        if src.is_symlink() or not src.is_file():
            raise FatError(f"'{src}' no es un archivo regular")
        off, size = particion_mbr(args.imagen, args.particion)
        r = agregar_archivo(args.imagen, off, size, args.nombre, src.read_bytes())
    except (FatError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"OK: '{r['nombre']}' (alias {r['alias_corto']}) agregado: {r['bytes']} bytes en {r['clusters']} clusters")
    return 0


if __name__ == "__main__":
    sys.exit(main())

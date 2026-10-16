#!/usr/bin/env python3
"""Inspección estática de solo lectura de un bzImage x86: versión, compresión, tamaño descomprimido y configuración embebida.

Nunca ejecuta el kernel. Pasos: (1) valida la cabecera del protocolo de arranque; (2) localiza la carga comprimida con
`payload_offset`/`payload_length`; (3) la descomprime en memoria (gzip/bzip2/xz/lzma con la biblioteca estándar; zstd con
el binario `zstd` por una tubería) con tope de tamaño; (4) comprueba que el tamaño obtenido coincide con el pie de 4 bytes
que añade el kernel; (5) extrae `IKCFG_ST…IKCFG_ED` (CONFIG_IKCONFIG) y resume los símbolos pedidos.

Una configuración embebida describe cómo se compiló el kernel, no que arranque en una consola concreta.
"""
from __future__ import annotations

import argparse
import bz2
import gzip
import hashlib
import json
import lzma
import re
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

TOPE = 512 * 1024 * 1024
SIMBOLOS = ("X86_PS4", "X86_PS4_BAIKAL", "PS4_DMI_SPOOF", "USB_XHCI_AEOLIA", "MODULES", "IKCONFIG", "BLK_DEV_INITRD",
            "SATA_AHCI", "BLK_DEV_SD", "UFS_FS", "DM_CRYPT", "CRYPTO_XTS", "EXT4_FS", "VFAT_FS", "USB_STORAGE",
            "DRM_AMDGPU", "DRM_AMDGPU_CIK", "DRM_RADEON", "EFI", "CMDLINE_BOOL")


class KernelError(Exception):
    pass


def _descomprimir(carga: bytes) -> tuple[str, bytes]:
    if carga[:2] == b"\x1f\x8b":
        d = zlib.decompressobj(wbits=31)
        out = d.decompress(carga, TOPE)
        if not d.eof:
            raise KernelError("gzip truncado o más grande que el tope")
        return "gzip", out
    if carga[:3] == b"BZh":
        d = bz2.BZ2Decompressor()
        out = d.decompress(carga, TOPE)
        return "bzip2", out
    if carga[:6] == b"\xfd7zXZ\x00":
        d = lzma.LZMADecompressor(format=lzma.FORMAT_XZ)
        return "xz", d.decompress(carga, TOPE)
    if carga[:4] == b"\x28\xb5\x2f\xfd":
        exe = shutil.which("zstd")
        if not exe:
            raise KernelError("el kernel usa zstd y no hay binario `zstd` en el sistema")
        # el kernel agrega 4 bytes tras el marco; el CLI los rechaza al final pero ya emitió todo el contenido
        r = subprocess.run([exe, "-dc"], input=carga, capture_output=True, timeout=300)
        if len(r.stdout) == 0:
            raise KernelError("zstd no produjo salida: " + r.stderr.decode("utf-8", "replace")[:200])
        if len(r.stdout) > TOPE:
            raise KernelError("contenido descomprimido mayor que el tope")
        return "zstd", r.stdout
    raise KernelError(f"formato de compresión no reconocido (primeros bytes {carga[:4].hex()})")


def inspeccionar(path: Path, simbolos=SIMBOLOS) -> dict:
    datos = Path(path).read_bytes()
    if len(datos) < 0x264 or datos[0x1FE:0x200] != b"\x55\xaa" or datos[0x202:0x206] != b"HdrS":
        raise KernelError("no es un bzImage x86 (firma 0xAA55 / 'HdrS' ausentes)")
    setup = ((datos[0x1F1] or 4) + 1) * 512
    off, ln = struct.unpack_from("<II", datos, 0x248)
    if ln < 8 or setup + off + ln > len(datos):
        raise KernelError("payload_offset/payload_length fuera del archivo")
    carga = datos[setup + off: setup + off + ln]
    metodo, vmlinux = _descomprimir(carga)
    declarado = struct.unpack("<I", carga[-4:])[0]
    informe = {
        "sha256_bzimage": hashlib.sha256(datos).hexdigest(),
        "bytes_bzimage": len(datos),
        "compresion": metodo,
        "bytes_payload_comprimido": ln,
        "bytes_descomprimidos": len(vmlinux),
        "pie_tamano_declarado": declarado,
        "pie_coincide": declarado == len(vmlinux),
        "es_elf": vmlinux[:4] == b"\x7fELF",
        "sha256_vmlinux": hashlib.sha256(vmlinux).hexdigest(),
    }
    v = re.search(rb"Linux version ([\x20-\x7e]{8,240})", vmlinux)
    informe["cadena_linux_version"] = v.group(1).decode("ascii") if v else None
    i = vmlinux.find(b"IKCFG_ST")
    if i < 0:
        informe["config_embebida"] = None
        return informe
    j = vmlinux.find(b"IKCFG_ED", i)
    if j < 0:
        raise KernelError("IKCFG_ST sin IKCFG_ED")
    try:
        cfg = gzip.decompress(vmlinux[i + 8: j]).decode("utf-8", "replace")
    except (OSError, EOFError, zlib.error) as exc:
        raise KernelError(f"configuración embebida corrupta: {exc}") from exc
    lineas = cfg.splitlines()
    estado = {}
    for s in simbolos:
        m = next((l for l in lineas if l.startswith(f"CONFIG_{s}=") or l == f"# CONFIG_{s} is not set"), None)
        estado[s] = m.split("=", 1)[1] if m and "=" in m else ("no establecido" if m else "ausente")
    informe["config_embebida"] = {
        "sha256": hashlib.sha256(cfg.encode("utf-8")).hexdigest(),
        "lineas": len(lineas),
        "cabecera": lineas[2] if len(lineas) > 2 else None,
        "modulos_m": sum(1 for l in lineas if l.endswith("=m")),
        "integrados_y": sum(1 for l in lineas if l.endswith("=y")),
        "simbolos": estado,
    }
    return informe


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bzimage", type=Path)
    ap.add_argument("--extraer-config", type=Path, help="escribe la configuración embebida en este archivo NUEVO")
    args = ap.parse_args(argv)
    try:
        informe = inspeccionar(args.bzimage)
        if args.extraer_config:
            datos = Path(args.bzimage).read_bytes()
            # reutiliza la extracción: se vuelve a obtener el texto para escribirlo
            setup = ((datos[0x1F1] or 4) + 1) * 512
            off, ln = struct.unpack_from("<II", datos, 0x248)
            _, vm = _descomprimir(datos[setup + off: setup + off + ln])
            i = vm.find(b"IKCFG_ST")
            if i < 0:
                raise KernelError("el kernel no trae configuración embebida")
            cfg = gzip.decompress(vm[i + 8: vm.find(b"IKCFG_ED", i)])
            with open(args.extraer_config, "xb") as f:
                f.write(cfg)
    except (KernelError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(informe, indent=2, ensure_ascii=False))
    return 0 if informe["pie_coincide"] and informe["es_elf"] else 1


if __name__ == "__main__":
    sys.exit(main())

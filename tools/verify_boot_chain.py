#!/usr/bin/env python3
"""Verifica la estructura de archivos requerida para el arranque USB-only de PS4 Linux."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

class BootChainError(Exception):
    pass

def _check_file_type(path: Path, description: str, errors: list[str]) -> bool:
    if not path.exists():
        return False
    if path.is_symlink():
        errors.append(f"'{description}' no debe ser un enlace simbólico: {path}")
        return False
    if not path.is_file():
        errors.append(f"'{description}' debe ser un archivo regular, no un directorio u otro tipo especial: {path}")
        return False
    return True

def verify_boot_layout(boot_dir: Path) -> dict:
    if not boot_dir.is_dir():
        raise BootChainError(f"'{boot_dir}' no es un directorio válido")

    errors = []
    warnings = []

    bzimage = boot_dir / "bzImage"
    initramfs = boot_dir / "initramfs.cpio.gz"
    bootargs = boot_dir / "bootargs.txt"
    vram = boot_dir / "vram.txt"

    # Verificar bzImage
    if not _check_file_type(bzimage, "bzImage", errors):
        errors.append("Falta bzImage para arranque USB-only (el loader busca este nombre)")
        # Chequear si hay kernels renombrados como advertencia
        for p in boot_dir.glob("bzImage.*"):
            if _check_file_type(p, p.name, []): # Validar que sea un archivo regular
                warnings.append(f"'{p.name}' presente, pero el loader busca 'bzImage'")

    # Verificar initramfs
    if not _check_file_type(initramfs, "initramfs.cpio.gz", errors):
        errors.append("Falta initramfs.cpio.gz para arranque USB-only")

    # Verificar bootargs.txt y vram.txt si existen, pero no son obligatorios
    if bootargs.exists() and not _check_file_type(bootargs, "bootargs.txt", errors):
        pass # Error ya reportado por _check_file_type
    if vram.exists() and not _check_file_type(vram, "vram.txt", errors):
        pass # Error ya reportado por _check_file_type

    valid_usb_only = len(errors) == 0

    return {
        "valid_usb_only": valid_usb_only,
        "errors": errors,
        "warnings": warnings,
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boot_dir", type=Path, help="Ruta a la partición o directorio de boot")
    args = parser.parse_args(argv)

    try:
        res = verify_boot_layout(args.boot_dir)
    except BootChainError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for err in res["errors"]:
        print(f"[ERROR] {err}")
    for warn in res["warnings"]:
        print(f"[WARN] {warn}")

    if res["valid_usb_only"]:
        print("[OK] Estructura USB-only válida.")
        return 0
    else:
        print("[FAIL] Estructura USB-only incompleta o incorrecta.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

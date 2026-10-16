#!/usr/bin/env python3
"""Preflight estricto de configuración mínima para un candidato USB-only.

No monta, escribe ni ejecuta archivos. Solo inspecciona un directorio de archivos
extraídos o montado por el operador en modo de solo lectura. No demuestra que el
loader/kernel arranquen ni que el runtime evite el almacenamiento interno.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools import verify_boot_chain as vbc


def verificar_configuracion_minima(boot_dir: Path) -> list[str]:
    """Devuelve errores; exige ambos obligatorios y prohíbe los dos opcionales."""
    boot_dir = Path(boot_dir)
    errores: list[str] = []
    if not boot_dir.is_dir():
        raise vbc.BootChainError(f"'{boot_dir}' no es un directorio")

    estructura = vbc.verificar_estructura(boot_dir)
    errores.extend(estructura["errores"])

    for nombre in (vbc.BOOTARGS, vbc.VRAM):
        ruta = boot_dir / nombre
        # lexists detecta también symlinks rotos, que no deben pasar como ausencia.
        if ruta.is_symlink() or ruta.exists():
            errores.append(
                f"'{nombre}' está presente; el candidato mínimo exige omitirlo "
                "y usar los valores por defecto del loader"
            )
    return errores


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boot_dir", type=Path, help="directorio de arranque extraído para inspección host-side")
    args = parser.parse_args(argv)
    try:
        errores = verificar_configuracion_minima(args.boot_dir)
    except vbc.BootChainError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if errores:
        for error in errores:
            print(f"FALLO: {error}")
        return 1
    print("OK: estructura mínima presente; bootargs.txt y vram.txt ausentes.")
    print("NOTA: esto no verifica hashes, procedencia, compatibilidad, USB físico ni arranque.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

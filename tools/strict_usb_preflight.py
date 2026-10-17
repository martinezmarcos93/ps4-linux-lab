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

# Tomado de linux/main-aio.c en ps4-linux/ps4-linux-loader@f70f43a6.
# bootargs.txt sustituye la línea completa: no basta con añadir "rescueshell".
CMDLINE_DEFAULT = (
    "panic=0 clocksource=tsc consoleblank=0 net.ifnames=0 "
    "radeon.dpm=0 amdgpu.dpm=0 drm.debug=0 "
    "console=ttyS0,115200n8 console=tty0 video=HDMI-A-1:1920x1080@60"
)
CMDLINE_MAX_BYTES = 2047  # COMMAND_LINE_SIZE de x86 es 2048 incluyendo NUL


def _validar_bootargs_rescue(ruta: Path, errores: list[str]) -> None:
    """Valida una cmdline completa para rescue-shell; no ejecuta ni interpreta comandos."""
    try:
        st = ruta.lstat()
    except OSError as exc:
        errores.append(f"bootargs.txt: no se pueden consultar los metadatos: {exc}")
        return
    if not ruta.is_file() or ruta.is_symlink():
        errores.append("bootargs.txt debe ser un archivo regular, no un symlink ni directorio")
        return
    if st.st_size == 0:
        errores.append("bootargs.txt está vacío")
        return
    if st.st_size > CMDLINE_MAX_BYTES:
        errores.append(f"bootargs.txt supera {CMDLINE_MAX_BYTES} bytes (límite x86, incluido el terminador NUL)")
        return
    try:
        contenido = ruta.read_bytes()
    except OSError as exc:
        errores.append(f"bootargs.txt no se puede leer: {exc}")
        return
    try:
        texto = contenido.decode("ascii")
    except UnicodeDecodeError:
        errores.append("bootargs.txt debe contener solo ASCII imprimible")
        return
    if not texto or any(ord(ch) < 32 or ord(ch) > 126 for ch in texto):
        errores.append("bootargs.txt debe contener solo ASCII imprimible, sin saltos de línea ni controles")
        return
    tokens = texto.split()
    requeridos = CMDLINE_DEFAULT.split()
    faltantes = [token for token in requeridos if token not in tokens]
    if faltantes:
        errores.append("bootargs.txt no contiene la cmdline por defecto completa del loader; faltan: "
                       + ", ".join(faltantes))
    if tokens.count("rescueshell") != 1:
        errores.append("bootargs.txt debe contener exactamente un token 'rescueshell'")


def verificar_configuracion_minima(boot_dir: Path, perfil: str = "minimal-default") -> list[str]:
    """Valida un perfil explícito: minimal-default o rescue-shell."""
    boot_dir = Path(boot_dir)
    errores: list[str] = []
    if perfil not in {"minimal-default", "rescue-shell"}:
        raise vbc.BootChainError(f"perfil desconocido '{perfil}' (use minimal-default o rescue-shell)")
    if not boot_dir.is_dir():
        raise vbc.BootChainError(f"'{boot_dir}' no es un directorio")

    estructura = vbc.verificar_estructura(boot_dir)
    errores.extend(estructura["errores"])

    # Rechazar variantes de mayúsculas/minúsculas también: la partición FAT
    # puede resolver nombres sin distinguir el caso aunque el host use otro FS.
    reservados = {vbc.BOOTARGS.casefold(), vbc.VRAM.casefold()}
    try:
        presentes = list(boot_dir.iterdir())
    except OSError as exc:
        raise vbc.BootChainError(f"no se pudo listar '{boot_dir}': {exc}") from exc

    for ruta in presentes:
        if ruta.name.casefold() not in reservados:
            continue
        es_bootargs = ruta.name.casefold() == vbc.BOOTARGS.casefold()
        if es_bootargs and perfil == "rescue-shell" and ruta.name == vbc.BOOTARGS:
            _validar_bootargs_rescue(ruta, errores)
            continue
        nombre_esperado = vbc.BOOTARGS if es_bootargs else vbc.VRAM
        errores.append(
            f"'{ruta.name}' está presente (nombre reservado '{nombre_esperado}'); "
            + ("el perfil rescue-shell solo permite bootargs.txt con la cmdline completa validada"
               if es_bootargs and perfil == "rescue-shell"
               else f"el perfil {perfil} exige omitirlo")
        )
    if perfil == "rescue-shell" and not any(r.name == vbc.BOOTARGS for r in presentes):
        errores.append("el perfil rescue-shell requiere 'bootargs.txt'")
    return errores


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("boot_dir", type=Path, help="directorio de arranque extraído para inspección host-side")
    parser.add_argument("--perfil", choices=("minimal-default", "rescue-shell"), default="minimal-default",
                        help="política de archivos opcionales (por defecto: minimal-default)")
    args = parser.parse_args(argv)
    try:
        errores = verificar_configuracion_minima(args.boot_dir, args.perfil)
    except vbc.BootChainError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if errores:
        for error in errores:
            print(f"FALLO: {error}")
        return 1
    print(f"OK: perfil {args.perfil} validado; estructura mínima presente.")
    print("NOTA: esto no verifica hashes, procedencia, compatibilidad, USB físico ni arranque.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

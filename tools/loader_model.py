#!/usr/bin/env python3
"""MODELO (no es el loader) de cómo resuelve rutas de archivos de arranque el payload upstream y la variante USB-only.

Sirve para probar el diseño sobre fixtures, no para validar el binario. Las reglas de `resolver_upstream`
reproducen la macro `L(...)` de linux/main-aio.c en ps4-linux/ps4-linux-loader@f70f43a (líneas 375-389);
las de `resolver_usb_only` reproducen patches/loader-usb-only-f70f43a.patch. Un sistema de archivos se
representa como dict {ruta_absoluta: bytes}; una ruta ausente significa que open() fallaría.
"""
from __future__ import annotations

RUTAS_UPSTREAM = ("/mnt/usb0/", "/mnt/usb1/", "/data/linux/boot/", "/user/system/boot/")
DIRS_USB = ("/mnt/usb0/", "/mnt/usb1/")
OBLIGATORIOS = ("bzImage", "initramfs.cpio.gz")
OPCIONALES = ("bootargs.txt", "vram.txt")


class ArranqueRechazado(Exception):
    """El loader mostraría una alerta y terminaría (return 1) sin iniciar kexec."""


def _legible(fs: dict, ruta: str) -> bool:
    return isinstance(fs.get(ruta), (bytes, bytearray))


def resolver_upstream(fs: dict) -> dict:
    """Cada archivo se busca por separado en las cuatro rutas, en orden. Devuelve {nombre: ruta|None}."""
    resultado: dict = {}
    for nombre in OBLIGATORIOS + OPCIONALES:
        resultado[nombre] = next((d + nombre for d in RUTAS_UPSTREAM if _legible(fs, d + nombre)), None)
    for nombre in OBLIGATORIOS:
        if resultado[nombre] is None:
            raise ArranqueRechazado(f"no se pudo cargar '{nombre}' de ninguna de las cuatro rutas")
    return resultado


def resolver_usb_only(fs: dict) -> dict:
    """Una sola carpeta USB con ambos archivos obligatorios; los opcionales solo de esa carpeta."""
    for d in DIRS_USB:
        if all(_legible(fs, d + n) for n in OBLIGATORIOS):
            return {n: (d + n if _legible(fs, d + n) else None) for n in OBLIGATORIOS + OPCIONALES}
    raise ArranqueRechazado("ninguna carpeta USB contiene a la vez bzImage e initramfs.cpio.gz")


def carpetas_usadas(resolucion: dict) -> set[str]:
    return {ruta.rsplit("/", 1)[0] + "/" for ruta in resolucion.values() if ruta}


def usa_almacenamiento_interno(resolucion: dict) -> bool:
    return any(not ruta.startswith(DIRS_USB) for ruta in resolucion.values() if ruta)


def hay_mezcla(resolucion: dict) -> bool:
    """True si los archivos cargados provienen de más de una carpeta."""
    return len(carpetas_usadas(resolucion)) > 1

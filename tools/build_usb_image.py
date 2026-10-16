#!/usr/bin/env python3
"""Construye una IMAGEN de USB de arranque (archivo regular) sin privilegios, sin montar y sin loop devices.

Separación deliberada: este programa solo CONSTRUYE un archivo. Escribirlo en un pendrive físico es otro
paso, manual y revisado, que esta herramienta no hace ni facilita (ver docs/USB_ONLY_DESIGN.md).

Layout (igual al de la distribución): p1 FAT32 con initramfs.cpio.gz y bzImage (política USB-only) y
p2 ext4 con etiqueta `psxitarch` poblada desde un directorio. Todo se arma en un archivo temporal junto al
destino y se renombra al final; ante cualquier error el temporal se elimina.

Limitación conocida: al no ser root, los archivos de p2 quedan con el uid/gid de quien ejecuta. Para un
rootfs real, prepare el directorio y ejecute esta herramienta bajo `fakeroot`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from tools import fat32_add_file as fat
    from tools import verify_boot_chain as vbc
except ModuleNotFoundError:  # ejecución directa: python3 tools/build_usb_image.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools import fat32_add_file as fat
    from tools import verify_boot_chain as vbc

MIB = 1024 * 1024
P1_MIN_MIB = 40  # mkfs.fat necesita >= 65525 clusters; con clusters de 512 B son ~33 MiB + FATs
P2_MIN_MIB = 16
TOTAL_MAX_MIB = 64 * 1024
PREFIJOS_PROHIBIDOS = ("/dev", "/proc", "/sys", "/run", "/boot", "/etc", "/bin", "/sbin", "/usr", "/lib", "/var/lib")
HERRAMIENTAS = {"sfdisk": "/usr/sbin/sfdisk", "mkfs.vfat": "/usr/sbin/mkfs.vfat", "mkfs.ext4": "/usr/sbin/mkfs.ext4"}


class BuildError(Exception):
    pass


def _herramienta(nombre: str) -> str:
    ruta = shutil.which(nombre) or (HERRAMIENTAS[nombre] if os.path.exists(HERRAMIENTAS[nombre]) else None)
    if not ruta:
        raise BuildError(f"falta la herramienta '{nombre}' (paquetes util-linux, dosfstools, e2fsprogs)")
    return ruta


def validar_salida(salida: Path) -> Path:
    """Devuelve la ruta absoluta validada. No crea nada."""
    if not str(salida) or "\x00" in str(salida):
        raise BuildError("ruta de salida vacía o inválida")
    if salida.suffix != ".img":
        raise BuildError("la salida debe terminar en .img")
    padre = salida.expanduser().absolute().parent
    try:
        padre_real = padre.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise BuildError(f"el directorio de salida no existe: {padre}") from exc
    if not padre_real.is_dir():
        raise BuildError(f"'{padre_real}' no es un directorio")
    cadena = str(padre_real)
    for pref in PREFIJOS_PROHIBIDOS:
        if cadena == pref or cadena.startswith(pref + "/"):
            raise BuildError(f"se rechaza escribir bajo '{pref}'")
    if padre_real == Path(padre_real.anchor):
        raise BuildError("se rechaza escribir en la raíz del sistema de archivos")
    destino = padre_real / salida.name
    if os.path.lexists(destino):
        raise BuildError(f"'{destino}' ya existe; no se sobrescribe (elija otro nombre o bórrelo usted)")
    return destino


def validar_entrada(ruta: Path, nombre: str) -> Path:
    try:
        st = os.lstat(ruta)
    except OSError as exc:
        raise BuildError(f"{nombre}: no se puede consultar '{ruta}': {exc.strerror or exc}") from exc
    if not stat.S_ISREG(st.st_mode):
        raise BuildError(f"{nombre}: '{ruta}' debe ser un archivo regular (no symlink, dispositivo ni directorio)")
    if st.st_size == 0:
        raise BuildError(f"{nombre}: '{ruta}' está vacío")
    return Path(ruta)


def validar_rootfs(directorio: Path) -> Path:
    try:
        st = os.lstat(directorio)
    except OSError as exc:
        raise BuildError(f"rootfs: no se puede consultar '{directorio}': {exc.strerror or exc}") from exc
    if not stat.S_ISDIR(st.st_mode):
        raise BuildError(f"rootfs: '{directorio}' debe ser un directorio real (no symlink)")
    for raiz, dirs, archivos in os.walk(directorio):
        for n in dirs + archivos:
            modo = os.lstat(os.path.join(raiz, n)).st_mode
            if not (stat.S_ISREG(modo) or stat.S_ISDIR(modo) or stat.S_ISLNK(modo)):
                raise BuildError(f"rootfs: '{os.path.join(raiz, n)}' es un archivo especial (dispositivo/FIFO/socket)")
    return Path(directorio)


def _tamano_rootfs(directorio: Path) -> int:
    total = 0
    for raiz, _d, archivos in os.walk(directorio):
        for n in archivos:
            try:
                total += os.lstat(os.path.join(raiz, n)).st_size
            except OSError:
                pass
    return total


def planificar(args) -> dict:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        raise BuildError("no ejecute esta herramienta como root: no lo necesita y reduce la protección ante errores")
    salida = validar_salida(args.salida)
    initramfs = validar_entrada(args.initramfs, "initramfs")
    kernel = validar_entrada(args.kernel, "kernel")
    rootfs = validar_rootfs(args.rootfs_dir)
    p1, total = args.p1_mib, args.tamano_mib
    if p1 < P1_MIN_MIB:
        raise BuildError(f"p1 debe medir al menos {P1_MIN_MIB} MiB")
    if total > TOTAL_MAX_MIB:
        raise BuildError(f"el tamaño total supera {TOTAL_MAX_MIB} MiB")
    p2 = total - p1 - 1  # 1 MiB de alineación inicial
    if p2 < P2_MIN_MIB:
        raise BuildError(f"p2 quedaría en {p2} MiB; mínimo {P2_MIN_MIB} (aumente --tamano-mib)")
    arranque = initramfs.stat().st_size + kernel.stat().st_size
    datos_rootfs = _tamano_rootfs(rootfs)
    usado = arranque + datos_rootfs
    if arranque * 11 // 10 > p1 * MIB:
        raise BuildError("kernel e initramfs no caben en la partición de arranque (p1)")
    if datos_rootfs * 115 // 100 > p2 * MIB:
        raise BuildError("el rootfs (más ~15 % de sobrecarga ext4) no cabe en p2")
    libre = shutil.disk_usage(salida.parent).free
    if usado * 12 // 10 + 64 * MIB > libre:
        raise BuildError("no hay espacio libre suficiente en el directorio de salida")
    if not args.omitir_verificacion:
        err, _ = vbc.comprobar_cabecera_bzimage(kernel)
        if err:
            raise BuildError("el kernel no pasa la comprobación de formato: " + "; ".join(err))
        err, _ = vbc.comprobar_initramfs(initramfs)
        if err:
            raise BuildError("el initramfs no pasa la comprobación de formato: " + "; ".join(err))
    return {"salida": str(salida), "p1_mib": p1, "p2_mib": p2, "tamano_total_mib": total,
            "initramfs": str(initramfs), "kernel": str(kernel), "rootfs_dir": str(rootfs),
            "bytes_a_copiar": usado}


def _ejecutar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise BuildError(f"falló {' '.join(cmd[:2])}: {(r.stderr or r.stdout).strip()[:400]}")


def construir(plan: dict) -> Path:
    sfdisk, mkvfat, mkext4 = _herramienta("sfdisk"), _herramienta("mkfs.vfat"), _herramienta("mkfs.ext4")
    destino = Path(plan["salida"])
    parcial_img = destino.with_name(f".{destino.name}.parcial")
    parcial_json = destino.with_suffix(".json.parcial")
    informe_json = destino.with_suffix(".json")
    
    if os.path.lexists(parcial_img):
        raise BuildError(f"existe un temporal previo '{parcial_img}'; revíselo y bórrelo manualmente")
    try:
        fd = os.open(parcial_img, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            os.ftruncate(fd, plan["tamano_total_mib"] * MIB)  # archivo disperso
        finally:
            os.close(fd)
        p1, p2 = plan["p1_mib"], plan["p2_mib"]
        subprocess.run([sfdisk, "--quiet", str(parcial_img)], input=f"label: dos\nstart=2048, size={p1}MiB, type=c\ntype=83\n",
                       text=True, capture_output=True, check=True, timeout=120)
        _ejecutar([mkvfat, "-F", "32", "-n", "PS4BOOT", "--offset", "2048", str(parcial_img), str(p1 * 1024)])
        off1, size1 = fat.particion_mbr(parcial_img, 1)
        fat.agregar_archivo(parcial_img, off1, size1, "initramfs.cpio.gz", Path(plan["initramfs"]).read_bytes())
        fat.agregar_archivo(parcial_img, off1, size1, "bzImage", Path(plan["kernel"]).read_bytes())
        off2, size2 = fat.particion_mbr(parcial_img, 2)
        _ejecutar([mkext4, "-q", "-F", "-L", "psxitarch", "-E", f"offset={off2}", "-d", plan["rootfs_dir"],
                   str(parcial_img), str(size2 // 1024)])
        _verificar_p1(parcial_img, off1, size1)
        
        # Escribir informe atómicamente
        plan_anon = plan.copy()
        for k in ("salida", "initramfs", "kernel", "rootfs_dir"):
            plan_anon[k] = str(Path(plan_anon[k]).name)
        informe = {"imagen": destino.name, "plan": plan_anon, "estado": "ok"}
        with open(parcial_json, "w", encoding="utf-8") as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(parcial_json, informe_json)
        
        # Finalizar imagen
        os.replace(parcial_img, destino)
        return destino
    except (subprocess.CalledProcessError, fat.FatError, OSError) as exc:
        raise BuildError(str(exc)) from exc
    finally:
        if os.path.lexists(parcial_img):
            os.unlink(parcial_img)
        if os.path.lexists(parcial_json):
            os.unlink(parcial_json)
        if os.path.lexists(informe_json) and not os.path.lexists(destino):
            os.unlink(informe_json)


def _verificar_p1(imagen: Path, off: int, size: int) -> None:
    fsck = shutil.which("fsck.vfat") or ("/usr/sbin/fsck.vfat" if os.path.exists("/usr/sbin/fsck.vfat") else None)
    if not fsck:
        return
    with tempfile.TemporaryDirectory(dir=imagen.parent, prefix=".p1-") as t:
        extraida = Path(t) / "p1.img"
        with open(imagen, "rb") as src, open(extraida, "wb") as dst:
            src.seek(off)
            restante = size
            while restante:
                bloque = src.read(min(restante, 8 * MIB))
                if not bloque:
                    break
                dst.write(bloque)
                restante -= len(bloque)
        r = subprocess.run([fsck, "-n", str(extraida)], capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise BuildError("fsck.vfat reporta problemas en la partición de arranque: " + (r.stdout + r.stderr).strip()[:400])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", required=True, type=Path, help="archivo .img a crear (no debe existir)")
    ap.add_argument("--initramfs", required=True, type=Path)
    ap.add_argument("--kernel", required=True, type=Path, help="bzImage que va en la FAT del USB (política USB-only, D-008)")
    ap.add_argument("--rootfs-dir", required=True, type=Path, help="directorio cuyo contenido va a p2 (ext4, etiqueta psxitarch)")
    ap.add_argument("--p1-mib", type=int, default=512)
    ap.add_argument("--tamano-mib", type=int, default=12 * 1024)
    ap.add_argument("--omitir-verificacion", action="store_true", help="no comprobar el formato de kernel/initramfs (no recomendado)")
    ap.add_argument("--dry-run", action="store_true", help="validar y mostrar el plan sin crear nada")
    args = ap.parse_args(argv)
    try:
        plan = planificar(args)
        if args.dry_run:
            print(json.dumps({"dry_run": True, **plan}, ensure_ascii=False, indent=2))
            return 0
        destino = construir(plan)
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"OK: imagen creada en {destino}. No se escribió en ningún dispositivo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

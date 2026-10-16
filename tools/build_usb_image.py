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
import hashlib
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
HERRAMIENTAS = {"sfdisk": "/usr/sbin/sfdisk", "mkfs.vfat": "/usr/sbin/mkfs.vfat", "mkfs.ext4": "/usr/sbin/mkfs.ext4",
                "fsck.vfat": "/usr/sbin/fsck.vfat", "e2fsck": "/usr/sbin/e2fsck"}


class BuildError(Exception):
    pass


def _buscar(nombre: str) -> str | None:
    return shutil.which(nombre) or (HERRAMIENTAS[nombre] if os.path.exists(HERRAMIENTAS[nombre]) else None)


def _herramienta(nombre: str) -> str:
    ruta = _buscar(nombre)
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
    informe = salida.with_name(salida.name + ".informe.json")
    if os.path.lexists(informe):
        raise BuildError(f"ya existe '{informe}'; no se sobrescribe (bórrelo usted si es de una construcción descartada)")
    return {"omitir_fsck": bool(getattr(args, "omitir_fsck", False)), "salida": str(salida), "p1_mib": p1, "p2_mib": p2, "tamano_total_mib": total,
            "initramfs": str(initramfs), "kernel": str(kernel), "rootfs_dir": str(rootfs),
            "bytes_a_copiar": usado}


def _ejecutar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise BuildError(f"falló {' '.join(cmd[:2])}: {(r.stderr or r.stdout).strip()[:400]}")


def construir(plan: dict) -> Path:
    sfdisk, mkvfat, mkext4 = _herramienta("sfdisk"), _herramienta("mkfs.vfat"), _herramienta("mkfs.ext4")
    destino = Path(plan["salida"])
    informe_final = destino.with_name(destino.name + ".informe.json")
    parcial = destino.with_name(f".{destino.name}.parcial")
    informe_parcial = destino.with_name(f".{destino.name}.informe.json.parcial")
    for previo in (parcial, informe_parcial):
        if os.path.lexists(previo):
            raise BuildError(f"existe un temporal previo '{previo}'; revíselo y bórrelo manualmente")
    for existente in (destino, informe_final):
        if os.path.lexists(existente):
            raise BuildError(f"ya existe '{existente}'; no se sobrescribe")
    exito = False
    publicados: list[Path] = []  # archivos finales creados por ESTA ejecución (para revertir si algo falla después)
    try:
        fd = os.open(parcial, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            os.ftruncate(fd, plan["tamano_total_mib"] * MIB)  # archivo disperso
        finally:
            os.close(fd)
        p1, p2 = plan["p1_mib"], plan["p2_mib"]
        subprocess.run([sfdisk, "--quiet", str(parcial)], input=f"label: dos\nstart=2048, size={p1}MiB, type=c\ntype=83\n",
                       text=True, capture_output=True, check=True, timeout=120)
        _ejecutar([mkvfat, "-F", "32", "-n", "PS4BOOT", "--offset", "2048", str(parcial), str(p1 * 1024)])
        off1, size1 = fat.particion_mbr(parcial, 1)
        fat.agregar_archivo(parcial, off1, size1, "initramfs.cpio.gz", Path(plan["initramfs"]).read_bytes())
        fat.agregar_archivo(parcial, off1, size1, "bzImage", Path(plan["kernel"]).read_bytes())
        off2, size2 = fat.particion_mbr(parcial, 2)
        _ejecutar([mkext4, "-q", "-F", "-L", "psxitarch", "-E", f"offset={off2}", "-d", plan["rootfs_dir"],
                   str(parcial), str(size2 // 1024)])
        verificaciones = _verificar_sistemas_de_archivos(parcial, off1, size1, off2, plan.get("omitir_fsck", False))
        # El informe se prepara (hash de la imagen incluido) ANTES de publicar nada y se publica PRIMERO:
        # si algo falla, nunca queda una imagen final sin su informe de verificación.
        _preparar_informe(informe_parcial, parcial, destino, plan, verificaciones)
        _publicar(informe_parcial, informe_final)
        publicados.append(informe_final)
        _publicar(parcial, destino)
        publicados.append(destino)
        exito = True
        return destino
    except subprocess.CalledProcessError as exc:
        raise BuildError(f"falló {exc.cmd[0]}: {(exc.stderr or exc.stdout or '').strip()[:400]}") from exc
    except (fat.FatError, OSError) as exc:
        raise BuildError(str(exc)) from exc
    finally:
        if not exito:
            for p in publicados:  # se retira lo que ESTA ejecución llegó a publicar: nada queda a medias
                if os.path.lexists(p):
                    os.unlink(p)
        for temporal in (parcial, informe_parcial):
            if os.path.lexists(temporal):
                os.unlink(temporal)


def _publicar(origen: Path, destino: Path) -> None:
    """Publica `origen` como `destino` SIN sobrescribir: enlace duro (falla si existe) y, si el sistema de archivos
    no admite enlaces duros, comprobación previa + os.replace (ventana mínima de carrera)."""
    try:
        os.link(origen, destino)
    except FileExistsError as exc:
        raise BuildError(f"'{destino}' apareció durante la construcción; no se sobrescribe") from exc
    except OSError:
        if os.path.lexists(destino):
            raise BuildError(f"'{destino}' apareció durante la construcción; no se sobrescribe")
        os.replace(origen, destino)
        return
    os.unlink(origen)


def _verificar_sistemas_de_archivos(imagen: Path, off1: int, size1: int, off2: int, omitir: bool) -> dict:
    """Comprueba FAT (fsck.vfat -n) y ext4 (e2fsck -fn) sin escribir. Devuelve qué se ejecutó DE VERDAD.

    Si falta una herramienta, la construcción FALLA salvo que se pidiera `--omitir-fsck`; en ese caso el estado es
    OMITIDA y queda registrado: nunca se presenta como verificado un sistema de archivos que no se comprobó.
    """
    resultado: dict = {}
    # --- FAT
    fsck = _buscar("fsck.vfat")
    if fsck is None:
        if not omitir:
            raise BuildError("falta fsck.vfat: la FAT no se puede verificar. Instale dosfstools o use --omitir-fsck "
                             "(la imagen quedará registrada como SIN verificar)")
        resultado["fat"] = {"estado": "OMITIDA", "motivo": "fsck.vfat no está instalado y se pidió --omitir-fsck"}
    else:
        with tempfile.TemporaryDirectory(dir=imagen.parent, prefix=".p1-") as t:
            extraida = Path(t) / "p1.img"
            with open(imagen, "rb") as src, open(extraida, "wb") as dst:
                src.seek(off1)
                restante = size1
                while restante:
                    bloque = src.read(min(restante, 8 * MIB))
                    if not bloque:
                        break
                    dst.write(bloque)
                    restante -= len(bloque)
            r = subprocess.run([fsck, "-n", str(extraida)], capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise BuildError("fsck.vfat reporta problemas en la partición de arranque: " + (r.stdout + r.stderr).strip()[:400])
        resultado["fat"] = {"estado": "OK", "herramienta": "fsck.vfat -n", "ruta": fsck}
    # --- ext4 (e2fsck lee la partición in situ con ?offset=; -n = solo lectura)
    e2 = _buscar("e2fsck")
    if e2 is None:
        if not omitir:
            raise BuildError("falta e2fsck: el ext4 no se puede verificar. Instale e2fsprogs o use --omitir-fsck "
                             "(la imagen quedará registrada como SIN verificar)")
        resultado["ext4"] = {"estado": "OMITIDA", "motivo": "e2fsck no está instalado y se pidió --omitir-fsck"}
    else:
        r = subprocess.run([e2, "-fn", f"{imagen}?offset={off2}"], capture_output=True, text=True, timeout=1800)
        if r.returncode != 0:
            raise BuildError("e2fsck reporta problemas en el ext4: " + (r.stdout + r.stderr).strip()[-400:])
        resultado["ext4"] = {"estado": "OK", "herramienta": "e2fsck -fn", "ruta": e2}
    return resultado


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8 * MIB), b""):
            h.update(b)
    return h.hexdigest()


def _preparar_informe(informe_parcial: Path, imagen_parcial: Path, destino: Path, plan: dict, verificaciones: dict) -> None:
    """Escribe el informe en un temporal (nuevo, nunca sobrescribe): entradas con hash, hash de la imagen terminada y
    verificaciones realmente ejecutadas. El hash se calcula sobre la imagen parcial, que es la que se publicará."""
    informe = {
        "imagen": destino.name,
        "sha256_imagen": _sha256(imagen_parcial),
        "bytes_imagen": imagen_parcial.stat().st_size,
        "entradas": {n: {"archivo": plan[n], "sha256": _sha256(Path(plan[n])), "bytes": Path(plan[n]).stat().st_size}
                     for n in ("initramfs", "kernel")},
        "rootfs_dir": plan["rootfs_dir"],
        "particiones_mib": {"p1": plan["p1_mib"], "p2": plan["p2_mib"]},
        "verificaciones": verificaciones,
        "totalmente_verificada": all(v["estado"] == "OK" for v in verificaciones.values()),
        "nota": "Una imagen verificada no prueba compatibilidad con la consola ni que arranque; el rootfs puede ser ficticio.",
    }
    with open(informe_parcial, "x", encoding="utf-8") as f:
        json.dump(informe, f, indent=2, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", required=True, type=Path, help="archivo .img a crear (no debe existir)")
    ap.add_argument("--initramfs", required=True, type=Path)
    ap.add_argument("--kernel", required=True, type=Path, help="bzImage que va en la FAT del USB (política USB-only, D-008)")
    ap.add_argument("--rootfs-dir", required=True, type=Path, help="directorio cuyo contenido va a p2 (ext4, etiqueta psxitarch)")
    ap.add_argument("--p1-mib", type=int, default=512)
    ap.add_argument("--tamano-mib", type=int, default=12 * 1024)
    ap.add_argument("--omitir-verificacion", action="store_true", help="no comprobar el formato de kernel/initramfs (no recomendado)")
    ap.add_argument("--omitir-fsck", action="store_true",
                    help="permitir construir aunque falten fsck.vfat/e2fsck; la imagen se registra como SIN verificar")
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
    informe = json.loads(destino.with_name(destino.name + ".informe.json").read_text(encoding="utf-8"))
    v = informe["verificaciones"]
    estado = ", ".join(f"{k}: {x['estado']}" + (f" ({x['herramienta']})" if x["estado"] == "OK" else f" — {x['motivo']}") for k, x in v.items())
    if informe["totalmente_verificada"]:
        print(f"OK: imagen creada en {destino} (sha256 {informe['sha256_imagen']}). Sistemas de archivos verificados -> {estado}. No se escribió en ningún dispositivo.")
    else:
        print(f"ATENCIÓN: imagen creada en {destino} pero NO totalmente verificada -> {estado}. No se escribió en ningún dispositivo.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

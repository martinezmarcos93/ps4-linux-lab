#!/usr/bin/env python3
"""Inventario de solo lectura de artefactos de arranque ya presentes en disco (no descarga ni ejecuta nada).

Recorre las raíces indicadas SIN seguir symlinks, selecciona por nombre kernels, initramfs, imágenes, payloads ELF,
binarios GoldHEN y rootfs, calcula SHA-256 y tamaño de cada uno y los contrasta con fuentes de procedencia que
usted aporta (catálogo de arranque, manifiestos, listas SHA256SUMS). Aplica además las comprobaciones de formato que
ya existen en el repositorio (cabecera x86, gzip+cpio, MBR/GPT, tabla del ELF).

Una coincidencia con una lista publicada por el MISMO autor prueba igualdad, no autenticidad. Un archivo sin
coincidencia queda como `desconocido`. Que un archivo no aparezca aquí significa que no se encontró en las raíces
indicadas, no que no exista en otra parte.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

try:
    from tools import elf_audit, inspect_image, verify_boot_chain as vbc
except ModuleNotFoundError:  # ejecución directa
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools import elf_audit, inspect_image, verify_boot_chain as vbc

PODAR = {".git", "node_modules", "__pycache__", ".cache"}
REGLAS = (
    ("parte_de_imagen", re.compile(r"\.img\.xz\.part\d+$", re.I)),
    ("imagen_comprimida", re.compile(r"\.img\.xz$", re.I)),
    ("imagen", re.compile(r"\.img$", re.I)),
    ("kernel", re.compile(r"^(bzImage.*|vmlinuz.*)$")),
    ("initramfs", re.compile(r"^(initramfs.*|initrd.*|.*\.cpio(\.gz)?)$", re.I)),
    ("payload_loader", re.compile(r"^linux-\d+mb\.(elf|bin)$")),
    ("goldhen", re.compile(r"^(goldhen.*\.bin|payload2\.bin|goldhen.*\.7z)$", re.I)),
    ("rootfs", re.compile(r"(rootfs|psxitarch).*\.(tar(\.(xz|gz|zst))?|tgz)$", re.I)),
)


def clasificar(nombre: str) -> str | None:
    for rol, rx in REGLAS:
        if rx.search(nombre):
            return rol
    return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cargar_procedencia(catalogo: list[Path], manifiestos: list[Path], sumas: list[Path]) -> dict[str, list[dict]]:
    """sha256 -> lista de {fuente, nombre, nivel}. Niveles: catalogo | manifiesto | publicado_por_autor."""
    prov: dict[str, list[dict]] = {}

    def anotar(h, fuente, nombre, nivel):
        prov.setdefault(h, []).append({"fuente": fuente, "nombre": nombre, "nivel": nivel})

    for c in catalogo:
        for a in vbc.cargar_catalogo(c)["artefactos"]:
            anotar(a["sha256"], str(c.name), a["id"], "catalogo")
    for m in manifiestos:
        datos = json.loads(Path(m).read_text(encoding="utf-8"))
        for a in datos.get("artifacts", []):
            anotar(a["sha256"], str(Path(m).name), a["path"], "manifiesto")
    for s in sumas:
        for linea in Path(s).read_text(encoding="utf-8").splitlines():
            partes = linea.split(None, 1)
            if len(partes) == 2 and re.fullmatch(r"[0-9a-f]{64}", partes[0]):
                anotar(partes[0], str(Path(s).name), partes[1].strip().lstrip("*"), "publicado_por_autor")
    return prov


def validar(ruta: Path, rol: str) -> dict:
    """Comprobaciones de formato existentes; nunca ejecutan el archivo."""
    try:
        if rol == "kernel":
            err, datos = vbc.comprobar_cabecera_bzimage(ruta)
            return {"formato": "FALLO" if err else "OK", "detalle": err or [f"protocolo x86 {datos.get('protocolo_arranque')}; versión declarada: {datos.get('version_declarada', 'no legible')}"]}
        if rol == "initramfs" and ruta.name.endswith(".gz"):
            err, datos = vbc.comprobar_initramfs(ruta)
            return {"formato": "FALLO" if err else "OK", "detalle": err or [f"gzip+cpio íntegros, {datos['entradas_cpio']} entradas"]}
        if rol == "imagen":
            r = inspect_image.inspect_image(str(ruta))
            partes = ", ".join(f"{p['tipo']} {p['bytes']} B {p['fs_hint']}" for p in r["particiones"])
            return {"formato": "OK" if r["particiones"] and not r["advertencias"] else "ADVERTENCIAS", "detalle": [f"tabla {r['tabla']}: {partes}"] + r["advertencias"]}
        if rol == "payload_loader" and ruta.suffix == ".elf":
            filas = elf_audit.leer_fw_table(ruta.read_bytes())
            return {"formato": "OK", "detalle": [f"ELF con fw_table de {len(filas)} filas (sin contrastar con una revisión de fuente)"]}
    except (OSError, ValueError, elf_audit.ElfError, inspect_image.ImageError) as exc:
        return {"formato": "FALLO", "detalle": [f"no se pudo validar: {exc}"]}
    return {"formato": "NO_VALIDADO", "detalle": ["sin comprobación de formato disponible para este tipo/extensión"]}


def inventariar(raices: dict[str, Path], procedencia: dict[str, list[dict]]) -> list[dict]:
    filas: list[dict] = []
    for etiqueta, raiz in raices.items():
        for dirpath, dirnames, nombres in os.walk(raiz, followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if d not in PODAR)
            for n in sorted(nombres):
                rol = clasificar(n)
                if rol is None:
                    continue
                p = Path(dirpath) / n
                st = os.lstat(p)
                rel = str(p.relative_to(raiz))
                if not stat.S_ISREG(st.st_mode):
                    filas.append({"raiz": etiqueta, "ruta": rel, "rol": rol, "omitido": "no es un archivo regular (symlink u otro): no se sigue"})
                    continue
                if st.st_size == 0:
                    filas.append({"raiz": etiqueta, "ruta": rel, "rol": rol, "bytes": 0, "omitido": "archivo vacío"})
                    continue
                h = sha256(p)
                coincide = procedencia.get(h, [])
                niveles = {c["nivel"] for c in coincide}
                if "catalogo" in niveles:
                    estado = "coincide con el catálogo"
                elif "publicado_por_autor" in niveles:
                    estado = "coincide con la lista publicada por el autor (no independiente)"
                elif "manifiesto" in niveles:
                    estado = "coincide con un manifiesto local"
                else:
                    estado = "desconocido (sin referencia de procedencia)"
                filas.append({"raiz": etiqueta, "ruta": rel, "rol": rol, "bytes": st.st_size, "sha256": h,
                              "origen_conocido": coincide, "procedencia": estado, "validacion": validar(p, rol)})
    return filas


AVISO = ("`formato: OK` significa solo que la estructura del archivo es coherente con lo que dice ser (cabecera x86, gzip+cpio, "
         "MBR/GPT, tabla del ELF). NO significa compatibilidad con ninguna consola, autenticidad ni que arranque. `procedencia` "
         "compara hashes con las referencias aportadas; una lista publicada por el mismo autor no es independiente.")


def documento(raices: dict[str, Path], filas: list[dict], incluir_ruta_absoluta: bool) -> dict:
    """Estructura publicable. Por defecto NO incluye rutas absolutas del equipo: cada archivo ya lleva su ruta relativa y la
    etiqueta de su raíz; de la raíz solo se conserva el nombre del directorio."""
    r = {k: ({"directorio": v.name, "ruta_absoluta": str(v)} if incluir_ruta_absoluta else
             {"directorio": v.name, "ruta_absoluta": "(omitida; use --incluir-ruta-absoluta)"}) for k, v in raices.items()}
    return {"aviso": AVISO, "raices": r, "archivos": filas}


def a_markdown(filas: list[dict]) -> str:
    out = ["| Raíz | Ruta | Rol | Bytes | SHA-256 | Procedencia | Formato (no es compatibilidad) |", "|---|---|---|---:|---|---|---|"]
    for f in filas:
        if "omitido" in f:
            out.append(f"| {f['raiz']} | `{f['ruta']}` | {f['rol']} | {f.get('bytes', '–')} | – | omitido: {f['omitido']} | – |")
            continue
        v = f["validacion"]
        out.append(f"| {f['raiz']} | `{f['ruta']}` | {f['rol']} | {f['bytes']} | `{f['sha256'][:16]}…` | {f['procedencia']} | {v['formato']} |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", action="append", required=True, metavar="ETIQUETA=RUTA")
    ap.add_argument("--catalogo", action="append", default=[], type=Path)
    ap.add_argument("--manifiesto", action="append", default=[], type=Path)
    ap.add_argument("--sumas", action="append", default=[], type=Path, help="archivo estilo sha256sum publicado por el autor")
    ap.add_argument("--json", type=Path, help="escribe el inventario completo (archivo NUEVO)")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--incluir-ruta-absoluta", action="store_true", help="guardar en el JSON la ruta absoluta de cada raíz (por defecto se omite)")
    args = ap.parse_args(argv)
    raices: dict[str, Path] = {}
    for r in args.raiz:
        if "=" not in r:
            print("ERROR: --raiz espera ETIQUETA=RUTA", file=sys.stderr)
            return 2
        et, ruta = r.split("=", 1)
        if not Path(ruta).is_dir():
            print(f"ERROR: '{ruta}' no es un directorio", file=sys.stderr)
            return 2
        raices[et] = Path(ruta)
    if args.json and args.json.exists():
        print(f"ERROR: '{args.json}' ya existe; no se sobrescribe", file=sys.stderr)
        return 2
    try:
        prov = cargar_procedencia(args.catalogo, args.manifiesto, args.sumas)
    except (OSError, ValueError, vbc.BootChainError) as exc:
        print(f"ERROR: no se pudo leer una fuente de procedencia: {exc}", file=sys.stderr)
        return 2
    filas = inventariar(raices, prov)
    if args.json:
        with open(args.json, "x", encoding="utf-8") as f:
            json.dump(documento(raices, filas, args.incluir_ruta_absoluta), f, indent=2, ensure_ascii=False)
            f.write("\n")
    print(a_markdown(filas) if args.markdown else json.dumps(filas, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

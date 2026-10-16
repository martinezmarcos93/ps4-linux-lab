#!/usr/bin/env python3
"""Verifica el resultado de una compilación aislada del loader (solo lectura; no ejecuta ningún artefacto).

Una compilación se acepta únicamente si:
  * `make.exit` existe y vale 0 (un ELF suelto nunca basta);
  * existen, son archivos regulares (no symlinks) y no están vacíos los 9 ELF, los 9 BIN y los 20 `kexec.bin` esperados;
  * los ELF empiezan con la firma 7f 45 4c 46;
  * no hay archivos inesperados en `payloads/` ni directorios inesperados en `kexec-build/`;
  * no hay hashes duplicados entre los ELF, entre los BIN ni entre los kexec.bin;
  * (opcional) los hashes coinciden con los registrados para la variante en un manifiesto.
Escribe `verificacion.json` siempre (también ante fallo) y `artefactos.sha256` solo si todo es correcto.
Códigos de salida: 0 correcto, 1 verificación fallida, 2 uso incorrecto.
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

TAMANOS_VRAM = (32, 64, 128, 256, 512, 1024, 2048, 3072, 4096)
FIRMWARES = (505, 672, 700, 750, 800, 850, 900, 903, 960, 1000, 1050, 1100, 1102, 1150, 1200, 1250, 1300, 1302, 1350, 1352)
ESPERADOS = {"elf": len(TAMANOS_VRAM), "bin": len(TAMANOS_VRAM), "kexec": len(FIRMWARES)}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _archivo_valido(path: Path, nombre: str, errores: list[str]) -> bool:
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        errores.append(f"falta {nombre}")
        return False
    if not stat.S_ISREG(st.st_mode):
        errores.append(f"{nombre} no es un archivo regular")
        return False
    if st.st_size == 0:
        errores.append(f"{nombre} está vacío")
        return False
    return True


def clasificar_advertencias(log: Path) -> dict:
    """Cuenta las advertencias del enlazador/compilador por clase. No las oculta ni las filtra."""
    cuentas = {"ld_pila_ejecutable": 0, "ld_segmento_rwx": 0, "otras": 0}
    if not log.is_file():
        return cuentas
    for linea in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if "warning:" not in linea:
            continue
        if "executable stack" in linea:
            cuentas["ld_pila_ejecutable"] += 1
        elif "RWX permissions" in linea:
            cuentas["ld_segmento_rwx"] += 1
        else:
            cuentas["otras"] += 1
    return cuentas


def verificar(salida: Path, esperado: dict | None = None, variante: str | None = None) -> dict:
    errores: list[str] = []
    src = salida / "src" / "linux"
    payloads, kexec = src / "payloads", src / "kexec-build"

    # 1. código de salida real de make
    codigo = None
    estado = salida / "make.exit"
    try:
        texto = estado.read_text(encoding="utf-8").strip()
        codigo = int(texto)
    except (OSError, ValueError):
        errores.append("no hay registro válido del código de salida de make (make.exit): la compilación no terminó con normalidad")
    if codigo is not None and codigo != 0:
        errores.append(f"make terminó con código {codigo}")

    # 2. conjunto esperado
    hashes: dict[str, str] = {"elf": {}, "bin": {}, "kexec": {}}  # type: ignore[assignment]
    esperados_payload = set()
    for t in TAMANOS_VRAM:
        for ext in ("elf", "bin"):
            nombre = f"linux-{t}mb.{ext}"
            esperados_payload.add(nombre)
            p = payloads / nombre
            if _archivo_valido(p, f"payloads/{nombre}", errores):
                if ext == "elf":
                    with open(p, "rb") as f:
                        if f.read(4) != b"\x7fELF":
                            errores.append(f"payloads/{nombre} no empieza con la firma ELF")
                            continue
                hashes[ext][nombre] = sha256(p)
    for fw in FIRMWARES:
        p = kexec / str(fw) / "kexec.bin"
        if _archivo_valido(p, f"kexec-build/{fw}/kexec.bin", errores):
            hashes["kexec"][str(fw)] = sha256(p)

    # 3. inesperados
    if payloads.is_dir():
        extra = sorted(n for n in os.listdir(payloads) if n not in esperados_payload)
        if extra:
            errores.append("archivos inesperados en payloads/: " + ", ".join(extra))
    if kexec.is_dir():
        extra = sorted(n for n in os.listdir(kexec) if n not in {str(fw) for fw in FIRMWARES})
        if extra:
            errores.append("directorios inesperados en kexec-build/: " + ", ".join(extra))

    # 4. duplicados
    for grupo, valores in hashes.items():
        vistos: dict[str, str] = {}
        for nombre, h in valores.items():
            if h in vistos:
                errores.append(f"hash duplicado en {grupo}: {nombre} y {vistos[h]} son idénticos")
            vistos[h] = nombre

    # 5. contraste con el manifiesto (opcional)
    if esperado is not None and variante is not None:
        reg = esperado.get("resultados", {}).get(variante)
        if reg is None:
            errores.append(f"el manifiesto no tiene la variante '{variante}'")
        else:
            for nombre, h in reg["sha256"].items():
                real = hashes["elf" if nombre.endswith(".elf") else "bin"].get(nombre)
                if real != h:
                    errores.append(f"hash de {nombre} distinto al del manifiesto (obtenido {real}, registrado {h})")
            for fw, h in reg["sha256_kexec_bin"].items():
                if hashes["kexec"].get(fw) != h:
                    errores.append(f"hash de kexec-build/{fw}/kexec.bin distinto al del manifiesto")

    encontrados = {k: len(v) for k, v in hashes.items()}
    informe = {
        "ok": not errores,
        "make_exit": codigo,
        "esperados": ESPERADOS,
        "encontrados_validos": encontrados,
        "errores": errores,
        "advertencias": clasificar_advertencias(salida / "build.log"),
        "sha256": hashes,
    }
    return informe


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("salida", type=Path, help="directorio de salida de scripts/build_loader_isolated.sh")
    ap.add_argument("--manifiesto", type=Path, help="manifests/loader-f70f43a-build.json para contrastar hashes")
    ap.add_argument("--variante", choices=("original", "parcheado"))
    args = ap.parse_args(argv)
    if bool(args.manifiesto) != bool(args.variante):
        print("ERROR: --manifiesto y --variante van juntos", file=sys.stderr)
        return 2
    if not args.salida.is_dir():
        print(f"ERROR: '{args.salida}' no es un directorio", file=sys.stderr)
        return 2
    esperado = None
    if args.manifiesto:
        try:
            esperado = json.loads(args.manifiesto.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"ERROR: no se pudo leer el manifiesto: {exc}", file=sys.stderr)
            return 2
    informe = verificar(args.salida, esperado, args.variante)
    (args.salida / "verificacion.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    e, f = informe["esperados"], informe["encontrados_validos"]
    print(f"esperados: ELF={e['elf']} BIN={e['bin']} kexec.bin={e['kexec']} | válidos encontrados: ELF={f['elf']} BIN={f['bin']} kexec.bin={f['kexec']}")
    adv = informe["advertencias"]
    print(f"advertencias del enlazador (visibles, no filtradas): pila ejecutable={adv['ld_pila_ejecutable']}, segmento RWX={adv['ld_segmento_rwx']}, otras={adv['otras']}")
    if not informe["ok"]:
        for err in informe["errores"]:
            print(f"FALLO: {err}", file=sys.stderr)
        return 1
    lineas = []
    for grupo, prefijo in (("elf", "payloads/"), ("bin", "payloads/"), ("kexec", "")):
        for nombre, h in informe["sha256"][grupo].items():
            ruta = f"{prefijo}{nombre}" if grupo != "kexec" else f"kexec-build/{nombre}/kexec.bin"
            lineas.append(f"{h}  {ruta}")
    (args.salida / "artefactos.sha256").write_text("\n".join(sorted(lineas, key=lambda x: x.split("  ")[1])) + "\n", encoding="utf-8")
    print(f"OK: {sum(f.values())} artefactos verificados (artefactos.sha256)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

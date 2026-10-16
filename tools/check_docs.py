#!/usr/bin/env python3
"""Validación de coherencia de la documentación (solo lectura, sin red).

Comprueba, sobre README.md y docs/**/*.md:
  1. enlaces markdown relativos que apuntan a archivos inexistentes;
  2. referencias `D-NNN`/`Q-NNN` que no existen en docs/DECISION_LOG.md;
  3. frases obsoletas que contradicen decisiones tomadas (p. ej. "Opción A/B" de D-008);
  4. en el roadmap: casillas sin etiqueta de evidencia, fases con estado `VERIFIED` sin prueba de laboratorio,
     y la selección de kernel marcada como resuelta mientras el southbridge siga desconocido.
Sale con 1 si hay problemas, 0 si no.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ETIQUETAS = ("PENDIENTE", "BLOQUEADO", "IMPLEMENTADO", "TERCEROS", "CÓDIGO", "TESTS", "LAB")
FRASES_OBSOLETAS = (
    "Estructura USB-only válida",
    "Opción A (",
    "Opción B (",
    "entrada pendiente D-008",
    "valid_usb_only",
    "pendiente de elegir entre",
)
ENLACE_RE = re.compile(r"(?<!\!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REF_RE = re.compile(r"\b([DQ])-(\d{3})\b")
CASILLA_RE = re.compile(r"^- \[( |x)\] (.*)$")


def archivos_md(raiz: Path) -> list[Path]:
    salida = [raiz / "README.md"] if (raiz / "README.md").is_file() else []
    docs = raiz / "docs"
    if docs.is_dir():
        salida += sorted(p for p in docs.rglob("*.md") if p.is_file() and not p.is_symlink())
    return salida


def _sin_codigo(texto: str) -> str:
    """Quita bloques de código para no interpretar su contenido como enlaces o referencias."""
    return re.sub(r"```.*?```", "", texto, flags=re.S)


def comprobar_enlaces(raiz: Path, archivos: list[Path]) -> list[str]:
    problemas = []
    for md in archivos:
        texto = _sin_codigo(md.read_text(encoding="utf-8"))
        for destino in ENLACE_RE.findall(texto):
            if re.match(r"^[a-z][a-z0-9+.-]*:", destino, re.I) or destino.startswith("#"):
                continue
            ruta = destino.split("#", 1)[0]
            if not ruta:
                continue
            objetivo = (md.parent / ruta).resolve()
            if not objetivo.exists():
                problemas.append(f"{md.relative_to(raiz)}: enlace roto -> {destino}")
    return problemas


def referencias_definidas(raiz: Path) -> tuple[set[str], set[str]]:
    log = raiz / "docs" / "DECISION_LOG.md"
    if not log.is_file():
        return set(), set()
    texto = log.read_text(encoding="utf-8")
    d = set(re.findall(r"(?m)^## (D-\d{3})\b", texto))
    q = set(re.findall(r"(?m)^- \*\*(Q-\d{3}):", texto))
    return d, q


def comprobar_referencias(raiz: Path, archivos: list[Path]) -> list[str]:
    d, q = referencias_definidas(raiz)
    problemas = []
    for md in archivos:
        for tipo, num in REF_RE.findall(md.read_text(encoding="utf-8")):
            ref = f"{tipo}-{num}"
            if (tipo == "D" and ref not in d) or (tipo == "Q" and ref not in q):
                problemas.append(f"{md.relative_to(raiz)}: referencia {ref} inexistente en DECISION_LOG.md")
    return sorted(set(problemas))


def comprobar_frases(raiz: Path, archivos: list[Path]) -> list[str]:
    problemas = []
    for md in archivos:
        texto = md.read_text(encoding="utf-8")
        for frase in FRASES_OBSOLETAS:
            if frase in texto:
                problemas.append(f"{md.relative_to(raiz)}: frase obsoleta '{frase}'")
    return problemas


def comprobar_roadmap(raiz: Path) -> list[str]:
    ruta = raiz / "docs" / "ROADMAP.md"
    if not ruta.is_file():
        return []
    problemas = []
    texto = ruta.read_text(encoding="utf-8")
    patron_etiqueta = re.compile(r"^`(%s)`" % "|".join(ETIQUETAS))
    for n, linea in enumerate(texto.splitlines(), 1):
        m = CASILLA_RE.match(linea)
        if m and not patron_etiqueta.match(m.group(2)):
            problemas.append(f"docs/ROADMAP.md:{n}: casilla sin etiqueta de evidencia")
        if m and m.group(1) == "x" and patron_etiqueta.match(m.group(2)) and m.group(2).startswith(("`PENDIENTE`", "`BLOQUEADO`")):
            problemas.append(f"docs/ROADMAP.md:{n}: casilla marcada como hecha con etiqueta PENDIENTE/BLOQUEADO")
        if linea.startswith("**Estado:**") and re.match(r"\*\*Estado:\*\* VERIFIED\b", linea) and "`LAB`" not in linea:
            problemas.append(f"docs/ROADMAP.md:{n}: fase VERIFIED sin evidencia LAB")
    matriz = raiz / "docs" / "COMPATIBILITY_MATRIX.md"
    lab = list((raiz / "docs" / "lab-logs").glob("LAB-0[0-9][1-9]*.md")) if (raiz / "docs" / "lab-logs").is_dir() else []
    if matriz.is_file() and "**DESCONOCIDO**" in matriz.read_text(encoding="utf-8") and not lab:
        for n, linea in enumerate(texto.splitlines(), 1):
            if "Elegir kernel" in linea and CASILLA_RE.match(linea) and CASILLA_RE.match(linea).group(1) == "x":
                problemas.append(f"docs/ROADMAP.md:{n}: selección de kernel marcada como resuelta con el southbridge desconocido")
    return problemas


def revisar(raiz: Path) -> list[str]:
    archivos = archivos_md(raiz)
    return (comprobar_enlaces(raiz, archivos) + comprobar_referencias(raiz, archivos)
            + comprobar_frases(raiz, archivos) + comprobar_roadmap(raiz))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raiz", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
    args = ap.parse_args(argv)
    if not args.raiz.is_dir():
        print(f"ERROR: '{args.raiz}' no es un directorio", file=sys.stderr)
        return 2
    problemas = revisar(args.raiz)
    for p in problemas:
        print(p)
    print(f"{len(problemas)} problema(s) de documentación" if problemas else "Documentación coherente (enlaces, referencias, frases y roadmap).")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())

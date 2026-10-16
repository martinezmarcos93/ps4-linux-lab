#!/usr/bin/env python3
"""Análisis estático de solo lectura de blobs de payload (p. ej. goldhen.bin). No ejecuta, no desensambla.

Qué hace (reproducible, determinista):
  * hash y tamaño del archivo;
  * entropía por ventanas, para delimitar código/datos/comprimido (heurística);
  * búsqueda de flujos zlib y descompresión en memoria con tope de tamaño;
  * cadenas ASCII de los cuerpos descomprimidos;
  * comparación contra una referencia: cadenas en común y solapamiento de ventanas de bytes.

Qué NO hace ni prueba:
  * no determina qué hace el código ni si es seguro;
  * cadenas o bytes en común indican parentesco, no equivalencia ni ausencia de cambios de lógica;
  * un flujo zlib que descomprime no demuestra que su contenido sea el que debía ser.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zlib
from pathlib import Path

MAX_ARCHIVO = 64 * 1024 * 1024
MAX_SALIDA_ZLIB = 64 * 1024 * 1024
MIN_SALIDA_ZLIB = 4096
MAX_INTENTOS_ZLIB = 20000
VENTANA = 256
CADENA_MIN = 6
SHINGLE = 16
_CADENA_RE = re.compile(rb"[\x20-\x7e]{%d,}" % CADENA_MIN)


class PayloadError(Exception):
    pass


def leer_acotado(path: Path, maximo: int = MAX_ARCHIVO) -> bytes:
    p = Path(path)
    try:
        if p.is_symlink() or not p.is_file():
            raise PayloadError(f"'{p}' no es un archivo regular")
        if p.stat().st_size > maximo:
            raise PayloadError(f"'{p}' supera {maximo} bytes")
        return p.read_bytes()
    except OSError as exc:
        raise PayloadError(f"no se pudo leer '{p}': {exc}") from exc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entropia(bloque: bytes) -> float:
    if not bloque:
        return 0.0
    n = len(bloque)
    cuentas = [0] * 256
    for b in bloque:
        cuentas[b] += 1
    return -sum((c / n) * math.log2(c / n) for c in cuentas if c)


def regiones_por_entropia(data: bytes, ventana: int = VENTANA) -> list[dict]:
    """Agrupa ventanas consecutivas de la misma clase: 'codigo_o_datos' (<6.5), 'denso' (6.5-7.5), 'aleatorio' (>7.5)."""
    def clase(e: float) -> str:
        return "codigo_o_datos" if e < 6.5 else ("denso" if e < 7.5 else "aleatorio")

    regiones: list[dict] = []
    for off in range(0, len(data), ventana):
        e = entropia(data[off:off + ventana])
        c = clase(e)
        if regiones and regiones[-1]["clase"] == c:
            regiones[-1]["fin"] = min(off + ventana, len(data))
        else:
            regiones.append({"inicio": off, "fin": min(off + ventana, len(data)), "clase": c})
    return regiones


def buscar_flujos_zlib(data: bytes, maximo_salida: int = MAX_SALIDA_ZLIB, intentos: int = MAX_INTENTOS_ZLIB) -> list[dict]:
    """Prueba descomprimir en cada offset con cabecera zlib plausible. Solo devuelve flujos completos."""
    hallados: list[dict] = []
    saltar_hasta = 0
    probados = 0
    for off in range(len(data) - 1):
        if off < saltar_hasta:
            continue
        b0, b1 = data[off], data[off + 1]
        if b0 != 0x78 or ((b0 << 8) | b1) % 31 != 0:
            continue
        probados += 1
        if probados > intentos:
            break
        d = zlib.decompressobj()
        try:
            salida = d.decompress(data[off:], maximo_salida)
        except zlib.error:
            continue
        if not d.eof or len(salida) < MIN_SALIDA_ZLIB or d.unconsumed_tail:
            continue
        consumido = len(data) - off - len(d.unused_data)
        hallados.append({
            "offset": off,
            "bytes_comprimidos": consumido,
            "bytes_descomprimidos": len(salida),
            "sha256_descomprimido": sha256(salida),
            "formato": "ELF" if salida[:4] == b"\x7fELF" else "crudo/desconocido",
            "primeros_bytes": salida[:8].hex(),
            "_datos": salida,
        })
        saltar_hasta = off + consumido
    return hallados


def cadenas(data: bytes) -> set[str]:
    return {m.group().decode("ascii") for m in _CADENA_RE.finditer(data)}


_URL_RE = re.compile(rb"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]{4,200}")
_IPV4_RE = re.compile(rb"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])")
_HOST_RE = re.compile(rb"(?<![A-Za-z0-9.-])(?:[A-Za-z0-9-]{1,63}\.)+(?:com|net|org|io|dev|xyz|cn|ru|info|me|tv|co|app|site|top|cc|gg|ly|to)(?![A-Za-z0-9-])")


def indicadores_red(data: bytes) -> dict:
    """URLs, IPv4 y nombres de host presentes como texto. La ausencia NO prueba que no haya red (cadenas ofuscadas, direcciones calculadas)."""
    return {
        "urls": sorted({m.group().decode("ascii") for m in _URL_RE.finditer(data)}),
        "ipv4": sorted({m.group().decode("ascii") for m in _IPV4_RE.finditer(data)}),
        "hosts": sorted({m.group().decode("ascii").lower() for m in _HOST_RE.finditer(data)}),
    }


def _ventanas(data: bytes, n: int = SHINGLE) -> set[bytes]:
    nulos = b"\0" * n
    return {data[i:i + n] for i in range(0, max(len(data) - n + 1, 0)) if data[i:i + n] != nulos}


def analizar(data: bytes) -> dict:
    info = {
        "sha256": sha256(data),
        "bytes": len(data),
        "primer_byte": f"{data[0]:02x}" if data else None,
        "regiones_entropia": regiones_por_entropia(data),
        "flujos_zlib": [],
    }
    cuerpos: list[bytes] = []
    for f in buscar_flujos_zlib(data):
        cuerpos.append(f.pop("_datos"))
        info["flujos_zlib"].append(f)
    info["_cuerpos"] = cuerpos
    info["indicadores_red_cuerpos"] = [indicadores_red(c) for c in cuerpos]
    info["indicadores_red_archivo"] = indicadores_red(data)
    return info


def comparar(a: dict, b: dict) -> dict:
    """Compara dos análisis (con '_cuerpos'). Parentesco, no equivalencia."""
    sa = set().union(*[cadenas(c) for c in a["_cuerpos"]]) if a["_cuerpos"] else set()
    sb = set().union(*[cadenas(c) for c in b["_cuerpos"]]) if b["_cuerpos"] else set()
    comunes = sa & sb
    ventanas_a = _ventanas(max(a["_cuerpos"], key=len)) if a["_cuerpos"] else set()
    ventanas_b = _ventanas(max(b["_cuerpos"], key=len)) if b["_cuerpos"] else set()
    inter = ventanas_a & ventanas_b
    return {
        "cadenas_a": len(sa), "cadenas_b": len(sb), "cadenas_comunes": len(comunes),
        "solo_en_a": len(sa - sb), "solo_en_b": len(sb - sa),
        "fraccion_cadenas_de_a_en_b": round(len(comunes) / len(sa), 4) if sa else None,
        "ventanas_a": len(ventanas_a), "ventanas_comunes": len(inter),
        "fraccion_ventanas_de_a_en_b": round(len(inter) / len(ventanas_a), 4) if ventanas_a else None,
        "aviso": "similitud estadística: no demuestra equivalencia de binarios ni ausencia de cambios de lógica",
    }


def _publico(info: dict) -> dict:
    return {k: v for k, v in info.items() if not k.startswith("_")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo", type=Path)
    ap.add_argument("--referencia", type=Path, help="otro blob con el que comparar (p. ej. el goldhen.bin oficial)")
    ap.add_argument("--esperado-sha256", help="si se indica y no coincide, termina con código 1")
    args = ap.parse_args(argv)
    try:
        info = analizar(leer_acotado(args.archivo))
        salida: dict = {"archivo": _publico(info)}
        if args.referencia:
            ref = analizar(leer_acotado(args.referencia))
            salida["referencia"] = _publico(ref)
            salida["comparacion"] = comparar(info, ref)
    except PayloadError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(salida, ensure_ascii=False, indent=2))
    if args.esperado_sha256 and args.esperado_sha256.lower() != info["sha256"]:
        print(f"ERROR: sha256 {info['sha256']} != esperado {args.esperado_sha256}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

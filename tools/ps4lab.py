#!/usr/bin/env python3
"""ps4lab: utilidades no destructivas del laboratorio PS4 Linux.

Subcomandos:
  doctor   revisa el host (herramientas, interfaces de red privadas).
  verify   verifica un directorio de artefactos contra un manifiesto (SHA-256).
  serve    sirve SOLO los archivos del manifiesto, solo lectura, solo en una IP privada,
           tras verificar hashes. Registra cada petición. No ejecuta nada.

Solo usa la biblioteca estándar. No escribe nada fuera de la carpeta de logs indicada.
"""
import argparse
import hashlib
import http.server
import ipaddress
import json
import logging
import shutil
import socket
import sys
from pathlib import Path

logger = logging.getLogger("ps4lab")
MAX_POST = 4096
CHUNK = 1024 * 1024


class ErrorManifiesto(Exception):
    pass


def cargar_manifiesto(ruta):
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ErrorManifiesto(f"no se pudo leer el manifiesto {ruta}: {e}") from e
    archivos = datos.get("archivos")
    if not isinstance(archivos, list) or not archivos:
        raise ErrorManifiesto("manifiesto sin lista 'archivos'")
    for a in archivos:
        if not all(k in a for k in ("ruta", "tamano", "sha256")):
            raise ErrorManifiesto(f"entrada incompleta en manifiesto: {a}")
    return datos


def ruta_segura(base, relativa):
    """Resuelve 'relativa' dentro de 'base'; None si intenta salir."""
    base = Path(base).resolve()
    destino = (base / relativa).resolve()
    try:
        destino.relative_to(base)
    except ValueError:
        return None
    return destino


def sha256_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(CHUNK), b""):
            h.update(bloque)
    return h.hexdigest()


def verificar(directorio, manifiesto):
    """Devuelve (ok, lista_de_problemas). No modifica nada."""
    problemas = []
    for a in manifiesto["archivos"]:
        p = ruta_segura(directorio, a["ruta"])
        if p is None:
            problemas.append(f"{a['ruta']}: ruta fuera del directorio")
        elif not p.is_file():
            problemas.append(f"{a['ruta']}: falta")
        elif p.stat().st_size != a["tamano"]:
            problemas.append(f"{a['ruta']}: tamaño {p.stat().st_size} != {a['tamano']}")
        elif sha256_archivo(p) != a["sha256"]:
            problemas.append(f"{a['ruta']}: SHA-256 distinto")
    return (not problemas), problemas


def validar_ip_privada(texto):
    ip = ipaddress.ip_address(texto)
    if ip.is_unspecified or ip.is_multicast or not ip.is_private:
        raise ValueError(f"{texto} no es una IP privada concreta (0.0.0.0 y públicas se rechazan)")
    return str(ip)


def crear_handler(directorio, permitidos):
    base = Path(directorio).resolve()

    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "ps4lab"

        def log_message(self, fmt, *args):
            logger.info("%s %s", self.client_address[0], fmt % args)

        def _ruta(self):
            r = self.path.split("?", 1)[0].lstrip("/") or "index.html"
            return r if r in permitidos else None

        def do_GET(self):
            r = self._ruta()
            p = ruta_segura(base, r) if r else None
            if p is None or not p.is_file():
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Length", str(p.stat().st_size))
            self.send_header("Content-Type", "application/octet-stream" if r.endswith(".bin") else
                             "text/html; charset=utf-8" if r.endswith(".html") else
                             "application/javascript" if r.endswith(".js") else "application/octet-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with open(p, "rb") as f:
                shutil.copyfileobj(f, self.wfile)

        def do_POST(self):
            # el exploit envía trazas de depuración a /t; se registran y se descartan
            if self.path.split("?", 1)[0] != "/t":
                self.send_error(404)
                return
            n = min(int(self.headers.get("Content-Length") or 0), MAX_POST)
            cuerpo = self.rfile.read(n).decode("utf-8", "replace")
            logger.info("TRAZA %s %s", self.client_address[0], cuerpo)
            self.send_response(204)
            self.end_headers()

    return Handler


def cmd_doctor(_):
    for h in ("python3", "objdump", "nmap", "avahi-browse", "git"):
        print(f"{h:14s}", shutil.which(h) or "NO ENCONTRADO")
    print("hostname:", socket.gethostname())
    return 0


def cmd_verify(a):
    ok, problemas = verificar(a.dir, cargar_manifiesto(a.manifiesto))
    for p in problemas:
        print("FALLA:", p)
    print("OK: todos los artefactos coinciden" if ok else "VERIFICACIÓN FALLIDA")
    return 0 if ok else 1


def cmd_serve(a):
    manifiesto = cargar_manifiesto(a.manifiesto)
    ok, problemas = verificar(a.dir, manifiesto)
    if not ok:
        print("No se sirve: la verificación falló:\n  " + "\n  ".join(problemas))
        return 1
    try:
        ip = validar_ip_privada(a.ip)
    except ValueError as e:
        print("IP rechazada:", e)
        return 2
    permitidos = {x["ruta"] for x in manifiesto["archivos"]}
    srv = http.server.ThreadingHTTPServer((ip, a.puerto), crear_handler(a.dir, permitidos))
    print(f"Sirviendo {len(permitidos)} archivos verificados en http://{ip}:{a.puerto}/  (Ctrl+C para parar)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        srv.server_close()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="archivo de log (por defecto solo consola)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(f=cmd_doctor)
    v = sub.add_parser("verify")
    v.add_argument("--dir", required=True)
    v.add_argument("--manifiesto", required=True)
    v.set_defaults(f=cmd_verify)
    s = sub.add_parser("serve")
    s.add_argument("--dir", required=True)
    s.add_argument("--manifiesto", required=True)
    s.add_argument("--ip", required=True, help="IP privada de ESTA PC (obligatoria, sin 0.0.0.0)")
    s.add_argument("--puerto", type=int, default=8080)
    s.set_defaults(f=cmd_serve)
    a = ap.parse_args(argv)
    handlers = [logging.StreamHandler()]
    if a.log:
        handlers.append(logging.FileHandler(a.log, encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=handlers)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())

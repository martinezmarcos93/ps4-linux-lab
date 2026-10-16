# Ejecuta lib/syscalls.py SIN red: sustituye urllib.request.urlopen por lecturas de archivos locales ya descargados.
import io, runpy, sys, urllib.request
FUENTES = {
    "https://raw.githubusercontent.com/freebsd/freebsd/stable/9/sys/kern/syscalls.master": "/net/syscalls.master",
    "http://web.archive.org/web/20210124215126js_/https://psdevwiki.com/ps4/edit/Syscalls": "/net/psdevwiki.html",
}
def falso(url, *a, **k):
    if url not in FUENTES:
        raise SystemExit("URL no prevista (bloqueada): " + url)
    print("[shim] sirviendo " + url + " desde " + FUENTES[url], file=sys.stderr)
    return io.BytesIO(open(FUENTES[url], "rb").read())
urllib.request.urlopen = falso
runpy.run_path("/src/lib/syscalls.py", run_name="__main__")

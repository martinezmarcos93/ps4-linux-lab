#!/usr/bin/env python3
"""Verificador de la cadena de arranque (kernel + initramfs) en cinco niveles independientes.

Cada nivel responde una pregunta distinta y NO implica a los siguientes:

1. estructura     ¿existen los archivos esperados, son regulares, sin symlinks y con tamaño admisible?
2. integridad     ¿coinciden tamaño y SHA-256 con un catálogo de procedencia confiable? (si se aporta)
3. formato        ¿la cabecera es coherente con el formato que dice tener? (solo comprobaciones
                  respaldadas por especificación: protocolo de arranque x86 y cpio "newc")
4. compatibilidad ¿el kernel está asociado, en la documentación del catálogo, a la plataforma indicada?
5. arranque       ¿existe un registro de laboratorio con los mismos hashes? (la herramienta NO arranca nada)

Solo lectura: nunca escribe, monta, ejecuta ni abre dispositivos. Estados posibles de un nivel:
OK, FALLO, NO_EVALUADO. Que un nivel sea OK no autoriza a afirmar nada del siguiente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import struct
import sys
import zlib
from pathlib import Path

NIVELES = ("estructura", "integridad", "formato", "compatibilidad", "arranque")

KERNEL = "bzImage"
INITRAMFS = "initramfs.cpio.gz"
BOOTARGS = "bootargs.txt"
VRAM = "vram.txt"

MAX_KERNEL_BYTES = 128 * 1024 * 1024
MAX_INITRAMFS_BYTES = 512 * 1024 * 1024
MAX_INITRAMFS_DESCOMPRIMIDO = 1024 * 1024 * 1024
MAX_ENTRADAS_CPIO = 200_000
MAX_BOOTARGS_BYTES = 4096
MAX_VRAM_BYTES = 32
CMDLINE_X86_MAX = 2047  # COMMAND_LINE_SIZE de x86 es 2048 incluyendo el NUL
VRAM_MIN_MB, VRAM_MAX_MB = 32, 4096  # -DVRAM_MB_MIN / -DVRAM_MB_MAX en linux/Makefile del loader

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class BootChainError(Exception):
    """Error de uso (directorio inválido, catálogo ilegible). Se traduce a código de salida 2."""


def _nivel(estado: str, errores: list[str], avisos: list[str], info: list[str]) -> dict:
    return {"estado": estado, "errores": errores, "avisos": avisos, "info": info}


def _no_evaluado(motivo: str) -> dict:
    return _nivel("NO_EVALUADO", [], [], [motivo])


def _sha256_y_tamano(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
            total += len(bloque)
    return h.hexdigest(), total


def _inspeccionar(path: Path, nombre: str, maximo: int | None, errores: list[str]) -> bool:
    """True si `path` es un archivo regular legible, no vacío y dentro del tamaño máximo.

    Usa lstat: un symlink roto existe como symlink (os.path.exists lo reportaría como ausente).
    """
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return False
    except OSError as exc:
        errores.append(f"'{nombre}': no se pudo consultar ({exc.strerror or exc})")
        return False
    if stat.S_ISLNK(st.st_mode):
        errores.append(f"'{nombre}' es un enlace simbólico; se exige un archivo regular")
        return False
    if not stat.S_ISREG(st.st_mode):
        errores.append(f"'{nombre}' no es un archivo regular (directorio, dispositivo, FIFO u otro)")
        return False
    if st.st_size == 0:
        errores.append(f"'{nombre}' está vacío")
        return False
    if maximo is not None and st.st_size > maximo:
        errores.append(f"'{nombre}' pesa {st.st_size} bytes; supera el máximo admitido ({maximo})")
        return False
    try:
        with open(path, "rb") as f:
            f.read(1)
    except OSError as exc:
        errores.append(f"'{nombre}' no se puede leer ({exc.strerror or exc})")
        return False
    return True


def _entrada_inexistente(path: Path) -> bool:
    return not os.path.lexists(path)


# ---------------------------------------------------------------- 1. estructura
def verificar_estructura(boot_dir: Path) -> dict:
    errores: list[str] = []
    avisos: list[str] = []
    info: list[str] = []
    boot_dir = Path(boot_dir)
    if not boot_dir.is_dir():
        raise BootChainError(f"'{boot_dir}' no es un directorio")

    for nombre, maximo in ((KERNEL, MAX_KERNEL_BYTES), (INITRAMFS, MAX_INITRAMFS_BYTES)):
        p = boot_dir / nombre
        if _entrada_inexistente(p):
            errores.append(f"falta '{nombre}'")
        else:
            _inspeccionar(p, nombre, maximo, errores)

    p = boot_dir / BOOTARGS
    if not _entrada_inexistente(p):
        _inspeccionar(p, BOOTARGS, MAX_BOOTARGS_BYTES, errores)
    p = boot_dir / VRAM
    if not _entrada_inexistente(p):
        _inspeccionar(p, VRAM, MAX_VRAM_BYTES, errores)

    exactos = {KERNEL, INITRAMFS, BOOTARGS, VRAM}
    try:
        presentes = sorted(os.listdir(boot_dir))
    except OSError as exc:
        raise BootChainError(f"no se pudo listar '{boot_dir}': {exc}") from exc
    for n in presentes:
        if n in exactos:
            continue
        bajo = n.lower()
        if bajo in {x.lower() for x in exactos}:
            avisos.append(f"'{n}' difiere en mayúsculas de un nombre esperado; el loader busca el nombre exacto")
        elif bajo.startswith("bzimage."):
            avisos.append(f"'{n}' es un kernel de reserva: el loader lo ignora (busca exactamente '{KERNEL}')")
        elif bajo.startswith("initramfs"):
            avisos.append(f"'{n}' no se usa: el loader busca exactamente '{INITRAMFS}'")

    info.append("Solo comprueba nombres, tipo y tamaño de archivos en el directorio indicado; "
                "no valida su contenido ni el aislamiento respecto del almacenamiento interno de la consola.")
    return _nivel("FALLO" if errores else "OK", errores, avisos, info)


# ---------------------------------------------------------------- 3. formato
def comprobar_cabecera_bzimage(path: Path) -> tuple[list[str], dict]:
    """Cabecera del protocolo de arranque x86 (Documentation/arch/x86/boot.rst del kernel Linux)."""
    errores: list[str] = []
    datos: dict = {}
    try:
        with open(path, "rb") as f:
            cab = f.read(0x4000)
    except OSError as exc:
        return [f"{KERNEL}: no se pudo leer ({exc.strerror or exc})"], datos
    if len(cab) < 0x264:
        return [f"{KERNEL}: tiene {len(cab)} bytes; la cabecera de arranque x86 ocupa al menos 0x264"], datos
    if cab[0x1FE:0x200] != b"\x55\xaa":
        errores.append(f"{KERNEL}: falta la firma 0xAA55 en el offset 0x1FE")
    if cab[0x202:0x206] != b"HdrS":
        errores.append(f"{KERNEL}: falta la marca 'HdrS' en el offset 0x202")
    if errores:
        return errores, datos
    version = struct.unpack_from("<H", cab, 0x206)[0]
    datos["protocolo_arranque"] = f"{version >> 8}.{version & 0xFF:02d}"
    if version < 0x0200:
        errores.append(f"{KERNEL}: protocolo de arranque {datos['protocolo_arranque']} < 2.00")
    datos["cargado_en_alto"] = bool(cab[0x211] & 1)
    if not datos["cargado_en_alto"]:
        errores.append(f"{KERNEL}: LOADED_HIGH no está activo; no es un 'bzImage' (kernel comprimido grande)")
    sectores = cab[0x1F1] or 4
    datos["sectores_setup"] = sectores
    if (sectores + 1) * 512 > path.stat().st_size:
        errores.append(f"{KERNEL}: setup_sects={sectores} excede el tamaño del archivo")
    puntero = struct.unpack_from("<H", cab, 0x20E)[0]
    if puntero and 0x200 + puntero < len(cab):
        crudo = cab[0x200 + puntero:0x200 + puntero + 200].split(b"\0")[0]
        texto = crudo.decode("ascii", errors="replace")
        if texto and all(32 <= ord(c) < 127 for c in texto):
            datos["version_declarada"] = texto
    return errores, datos


class _LectorGzip:
    """Descomprime gzip en streaming con tope de bytes descomprimidos."""

    def __init__(self, f, tope: int):
        self.f = f
        self.d = zlib.decompressobj(wbits=31)
        self.buf = bytearray()
        self.tope = tope
        self.total = 0
        self.fin = False

    def _llenar(self) -> bool:
        if self.fin:
            return False
        crudo = self.f.read(256 * 1024)
        if not crudo:
            self.fin = True
            if not self.d.eof:
                raise zlib.error("el flujo gzip termina antes de tiempo")
            return False
        salida = self.d.decompress(crudo)
        self.total += len(salida)
        if self.total > self.tope:
            raise zlib.error(f"el contenido descomprimido supera {self.tope} bytes")
        self.buf += salida
        if self.d.eof:
            self.fin = True
        return True

    def leer(self, n: int) -> bytes:
        while len(self.buf) < n and self._llenar():
            pass
        salida = bytes(self.buf[:n])
        del self.buf[:n]
        return salida

    def descartar(self, n: int) -> int:
        quitado = 0
        while quitado < n:
            if not self.buf and not self._llenar():
                break
            k = min(n - quitado, len(self.buf))
            del self.buf[:k]
            quitado += k
        return quitado


def comprobar_initramfs(path: Path) -> tuple[list[str], dict]:
    """gzip íntegro (CRC) + archivo cpio 'newc' (magic 070701/070702) recorrido hasta TRAILER!!!."""
    errores: list[str] = []
    datos: dict = {}
    try:
        with open(path, "rb") as f:
            if f.read(3) != b"\x1f\x8b\x08":
                return [f"{INITRAMFS}: no empieza con la firma gzip (1f 8b 08)"], datos
            f.seek(0)
            lector = _LectorGzip(f, MAX_INITRAMFS_DESCOMPRIMIDO)
            nombres_clave: set[str] = set()
            entradas = 0
            trailer = False
            try:
                while entradas <= MAX_ENTRADAS_CPIO:
                    cab = lector.leer(110)
                    if len(cab) < 110:
                        errores.append(f"{INITRAMFS}: el cpio termina antes de TRAILER!!!")
                        break
                    if cab[:6] not in (b"070701", b"070702"):
                        errores.append(f"{INITRAMFS}: cabecera cpio inválida en la entrada {entradas} "
                                       "(se esperaba magic 'newc' 070701/070702)")
                        break
                    try:
                        tam = int(cab[54:62], 16)
                        tam_nombre = int(cab[94:102], 16)
                    except ValueError:
                        errores.append(f"{INITRAMFS}: campos hexadecimales inválidos en la entrada {entradas}")
                        break
                    if tam_nombre == 0 or tam_nombre > 4096:
                        errores.append(f"{INITRAMFS}: tamaño de nombre fuera de rango en la entrada {entradas}")
                        break
                    nombre_crudo = lector.leer(tam_nombre)
                    if len(nombre_crudo) < tam_nombre or not nombre_crudo.endswith(b"\0"):
                        errores.append(f"{INITRAMFS}: nombre de entrada truncado o sin NUL en la entrada {entradas}")
                        break
                    nombre = nombre_crudo[:-1].decode("utf-8", errors="replace")
                    lector.descartar((-(110 + tam_nombre)) % 4)
                    if nombre == "TRAILER!!!":
                        trailer = True
                        break
                    if lector.descartar(tam) < tam:
                        errores.append(f"{INITRAMFS}: contenido de '{nombre}' truncado")
                        break
                    lector.descartar((-tam) % 4)
                    entradas += 1
                    nombre_norm = nombre[2:] if nombre.startswith("./") else nombre.lstrip("/")
                    if nombre_norm in ("init", "sbin/init"):
                        nombres_clave.add(nombre_norm)
                else:
                    errores.append(f"{INITRAMFS}: más de {MAX_ENTRADAS_CPIO} entradas; se aborta el recorrido")
            except zlib.error as exc:
                errores.append(f"{INITRAMFS}: gzip corrupto o truncado ({exc})")
            if not errores:
                if not trailer:
                    errores.append(f"{INITRAMFS}: no se encontró TRAILER!!!")
                if "init" not in nombres_clave and "sbin/init" not in nombres_clave:
                    errores.append(f"{INITRAMFS}: no contiene /init ni /sbin/init; el kernel no tendría qué ejecutar")
            datos["entradas_cpio"] = entradas
            datos["bytes_descomprimidos"] = lector.total
    except OSError as exc:
        errores.append(f"{INITRAMFS}: no se pudo leer ({exc.strerror or exc})")
    return errores, datos


def _verificar_opcionales(boot_dir: Path, errores: list[str], avisos: list[str], info: list[str]) -> None:
    p = boot_dir / VRAM
    if os.path.lexists(p) and p.is_file() and not p.is_symlink():
        try:
            texto = p.read_bytes().decode("ascii")
        except (OSError, UnicodeDecodeError):
            errores.append(f"{VRAM}: no es texto ASCII legible")
        else:
            m = re.match(r"^\s*(\d+)\s*$", texto)
            if not m:
                errores.append(f"{VRAM}: debe contener solo un entero (MB); el loader lo ignora y usa el valor por defecto")
            else:
                mb = int(m.group(1))
                if not VRAM_MIN_MB <= mb <= VRAM_MAX_MB:
                    errores.append(f"{VRAM}: {mb} MB fuera de {VRAM_MIN_MB}-{VRAM_MAX_MB}; el loader usaría el valor por defecto")
                else:
                    info.append(f"{VRAM}: {mb} MB (el loader da prioridad a vram.txt sobre el tamaño del payload)")
    p = boot_dir / BOOTARGS
    if os.path.lexists(p) and p.is_file() and not p.is_symlink():
        try:
            crudo = p.read_bytes()
        except OSError:
            errores.append(f"{BOOTARGS}: no se pudo leer")
            return
        linea = crudo.split(b"\n", 1)[0]
        if b"\0" in crudo:
            avisos.append(f"{BOOTARGS}: contiene NUL; el loader cortaría la línea de órdenes ahí")
        if len(linea) > CMDLINE_X86_MAX:
            errores.append(f"{BOOTARGS}: la primera línea mide {len(linea)} > {CMDLINE_X86_MAX} bytes (límite x86)")
        if not linea.strip():
            errores.append(f"{BOOTARGS}: la primera línea está vacía")
        if len(crudo.split(b"\n")) > 2 or (len(crudo.split(b"\n")) == 2 and crudo.split(b"\n")[1].strip()):
            avisos.append(f"{BOOTARGS}: solo se usa la primera línea; las demás se descartan")
        info.append(f"{BOOTARGS} reemplaza por completo los parámetros por defecto del loader")


def verificar_formato(boot_dir: Path) -> dict:
    errores: list[str] = []
    avisos: list[str] = []
    info: list[str] = []
    boot_dir = Path(boot_dir)
    k, i = boot_dir / KERNEL, boot_dir / INITRAMFS
    evaluados = 0
    if os.path.lexists(k) and k.is_file() and not k.is_symlink() and k.stat().st_size:
        e, datos = comprobar_cabecera_bzimage(k)
        errores += e
        evaluados += 1
        if not e:
            info.append(f"{KERNEL}: cabecera x86 coherente (protocolo {datos['protocolo_arranque']}, "
                        f"versión declarada: {datos.get('version_declarada', 'no legible')})")
    if os.path.lexists(i) and i.is_file() and not i.is_symlink() and i.stat().st_size:
        e, datos = comprobar_initramfs(i)
        errores += e
        evaluados += 1
        if not e:
            info.append(f"{INITRAMFS}: gzip y cpio newc íntegros ({datos['entradas_cpio']} entradas, "
                        f"{datos['bytes_descomprimidos']} bytes descomprimidos)")
    if evaluados == 0:
        return _no_evaluado("no hay kernel ni initramfs legibles que inspeccionar")
    _verificar_opcionales(boot_dir, errores, avisos, info)
    info.append("Coherencia de formato no equivale a que el kernel arranque en la PS4 ni a que el initramfs "
                "sea el esperado: no se ejecuta nada.")
    return _nivel("FALLO" if errores else "OK", errores, avisos, info)


# ---------------------------------------------------------------- catálogo
def cargar_catalogo(path: Path) -> dict:
    try:
        crudo = Path(path).read_text(encoding="utf-8")
        cat = json.loads(crudo)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise BootChainError(f"no se pudo leer el catálogo '{path}': {exc}") from exc
    if not isinstance(cat, dict) or cat.get("schema_version") != 1 or isinstance(cat.get("schema_version"), bool):
        raise BootChainError("catálogo inválido: se exige un objeto con schema_version = 1")
    arts = cat.get("artefactos")
    if not isinstance(arts, list) or not arts:
        raise BootChainError("catálogo inválido: 'artefactos' debe ser una lista no vacía")
    vistos: set[str] = set()
    for a in arts:
        if not isinstance(a, dict):
            raise BootChainError("catálogo inválido: cada artefacto debe ser un objeto")
        for campo in ("id", "rol", "sha256", "size_bytes", "release"):
            if campo not in a:
                raise BootChainError(f"catálogo inválido: artefacto sin '{campo}'")
        if a["rol"] not in ("kernel", "initramfs"):
            raise BootChainError(f"catálogo inválido: rol '{a['rol']}' desconocido")
        if not isinstance(a["sha256"], str) or not SHA256_RE.match(a["sha256"]):
            raise BootChainError(f"catálogo inválido: sha256 de '{a['id']}' no es hexadecimal de 64 caracteres")
        if not isinstance(a["size_bytes"], int) or isinstance(a["size_bytes"], bool) or a["size_bytes"] <= 0:
            raise BootChainError(f"catálogo inválido: size_bytes de '{a['id']}'")
        if a["id"] in vistos:
            raise BootChainError(f"catálogo inválido: id duplicado '{a['id']}'")
        vistos.add(a["id"])
    return cat


def _identificar(cat: dict, rol: str, sha: str) -> dict | None:
    for a in cat["artefactos"]:
        if a["rol"] == rol and a["sha256"] == sha:
            return a
    return None


# ---------------------------------------------------------------- 2. integridad
def verificar_integridad(boot_dir: Path, catalogo: dict | None) -> tuple[dict, dict]:
    """Devuelve (nivel, identificados) donde identificados mapea 'kernel'/'initramfs' a su entrada del catálogo."""
    if catalogo is None:
        return _no_evaluado("no se aportó un catálogo de procedencia; un hash sin referencia confiable no prueba nada"), {}
    errores: list[str] = []
    avisos: list[str] = []
    info: list[str] = []
    ident: dict = {}
    boot_dir = Path(boot_dir)
    for rol, nombre in (("kernel", KERNEL), ("initramfs", INITRAMFS)):
        p = boot_dir / nombre
        if _entrada_inexistente(p) or p.is_symlink() or not p.is_file():
            errores.append(f"{nombre}: no hay un archivo regular que contrastar con el catálogo")
            continue
        try:
            sha, tam = _sha256_y_tamano(p)
        except OSError as exc:
            errores.append(f"{nombre}: error de lectura ({exc.strerror or exc})")
            continue
        art = _identificar(catalogo, rol, sha)
        if art is None:
            errores.append(f"{nombre}: sha256 {sha[:12]}… no figura en el catálogo "
                           "(archivo desconocido, alterado o de otra versión)")
            continue
        if art["size_bytes"] != tam:
            errores.append(f"{nombre}: el hash coincide con '{art['id']}' pero el tamaño difiere ({tam} != {art['size_bytes']})")
            continue
        ident[rol] = art
        info.append(f"{nombre}: coincide con '{art['id']}' (release {art['release']})")
    if "kernel" in ident and "initramfs" in ident:
        if ident["kernel"]["release"] != ident["initramfs"]["release"]:
            errores.append("mezcla de versiones: el kernel es de la release "
                           f"'{ident['kernel']['release']}' y el initramfs de '{ident['initramfs']['release']}'")
    info.append("El catálogo prueba igualdad con valores publicados, no autenticidad del publicador.")
    return _nivel("FALLO" if errores else "OK", errores, avisos, info), ident


# ---------------------------------------------------------------- 4. compatibilidad
def verificar_compatibilidad(ident: dict, southbridge: str | None, catalogo: dict | None) -> dict:
    if catalogo is None:
        return _no_evaluado("sin catálogo no hay asociación documentada de kernel y plataforma")
    sb = (southbridge or "desconocido").strip().lower()
    if sb in ("", "desconocido", "unknown"):
        return _no_evaluado("southbridge de la consola no confirmado: no se declara compatibilidad (regla D-002)")
    kernel = ident.get("kernel")
    if kernel is None:
        return _no_evaluado("el kernel no fue identificado en el catálogo (nivel de integridad)")
    declarados = [s.lower() for s in kernel.get("southbridges", [])]
    if not declarados:
        return _no_evaluado(f"el catálogo no declara southbridge para '{kernel['id']}'")
    evid = kernel.get("evidencia_compatibilidad", "sin especificar")
    if sb in declarados:
        return _nivel("OK", [], [], [
            f"'{kernel['id']}' está documentado para southbridge {sb} (evidencia: {evid}). "
            "Es una asociación documental, no una prueba de arranque."])
    return _nivel("FALLO", [f"'{kernel['id']}' está documentado para {', '.join(declarados)}; se indicó {sb}"], [], [])


# ---------------------------------------------------------------- 5. arranque
def verificar_arranque(boot_dir: Path, evidencia_path: Path | None) -> dict:
    if evidencia_path is None:
        return _no_evaluado("sin registro de laboratorio: el arranque no está confirmado")
    try:
        ev = json.loads(Path(evidencia_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise BootChainError(f"no se pudo leer la evidencia de arranque '{evidencia_path}': {exc}") from exc
    errores: list[str] = []
    if not isinstance(ev, dict):
        raise BootChainError("evidencia de arranque inválida: se esperaba un objeto JSON")
    for campo in ("schema_version", "registro", "fecha", "resultado", "sha256_bzImage", "sha256_initramfs"):
        if campo not in ev:
            errores.append(f"la evidencia no declara '{campo}'")
    if errores:
        return _nivel("FALLO", errores, [], [])
    if ev["resultado"] != "arranque_linux_observado":
        return _nivel("FALLO", [f"el registro '{ev['registro']}' declara resultado '{ev['resultado']}', no un arranque observado"], [], [])
    boot_dir = Path(boot_dir)
    for nombre, campo in ((KERNEL, "sha256_bzImage"), (INITRAMFS, "sha256_initramfs")):
        p = boot_dir / nombre
        try:
            sha, _ = _sha256_y_tamano(p)
        except OSError:
            errores.append(f"{nombre}: no se pudo leer para contrastar con la evidencia")
            continue
        if sha != ev[campo]:
            errores.append(f"{nombre}: el hash actual no coincide con el del registro '{ev['registro']}'; "
                           "esa evidencia corresponde a otro archivo")
    if errores:
        return _nivel("FALLO", errores, [], [])
    return _nivel("OK", [], [], [
        f"existe el registro '{ev['registro']}' ({ev['fecha']}) con estos mismos hashes. "
        "La herramienta no arrancó nada: confía en el registro humano."])


# ---------------------------------------------------------------- agregado
def verificar_cadena(boot_dir: Path, catalogo: dict | None = None, southbridge: str | None = None,
                     evidencia_arranque: Path | None = None) -> dict:
    boot_dir = Path(boot_dir)
    resultado: dict = {}
    resultado["estructura"] = verificar_estructura(boot_dir)
    integridad, ident = verificar_integridad(boot_dir, catalogo)
    resultado["integridad"] = integridad
    resultado["formato"] = verificar_formato(boot_dir)
    resultado["compatibilidad"] = verificar_compatibilidad(ident, southbridge, catalogo)
    resultado["arranque"] = verificar_arranque(boot_dir, evidencia_arranque)
    return resultado


def _imprimir(res: dict) -> None:
    for nombre in NIVELES:
        n = res[nombre]
        print(f"[{n['estado']}] {nombre}")
        for m in n["errores"]:
            print(f"    error: {m}")
        for m in n["avisos"]:
            print(f"    aviso: {m}")
        for m in n["info"]:
            print(f"    nota: {m}")
    print("Resumen: cada nivel es independiente. Ninguno prueba por sí mismo que la PS4 arranque; "
          "solo el nivel 'arranque' con registro de laboratorio lo respalda.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("boot_dir", type=Path, help="directorio con bzImage e initramfs.cpio.gz (p. ej. la partición FAT del USB montada o extraída)")
    ap.add_argument("--catalogo", type=Path, help="catálogo JSON de procedencia (ver manifests/arranque-catalogo.json)")
    ap.add_argument("--southbridge", help="southbridge confirmado de la consola (aeolia|belize|belize2|baikal); omitir si es desconocido")
    ap.add_argument("--evidencia-arranque", type=Path, help="JSON que apunta a un registro de laboratorio con los mismos hashes")
    ap.add_argument("--requerir", default="estructura,formato",
                    help="niveles que deben estar en OK, separados por coma (por defecto estructura,formato)")
    ap.add_argument("--json", action="store_true", help="salida JSON")
    args = ap.parse_args(argv)

    requeridos = [x.strip() for x in args.requerir.split(",") if x.strip()]
    desconocidos = [x for x in requeridos if x not in NIVELES]
    if desconocidos:
        print(f"ERROR: niveles desconocidos en --requerir: {', '.join(desconocidos)}", file=sys.stderr)
        return 2
    try:
        cat = cargar_catalogo(args.catalogo) if args.catalogo else None
        res = verificar_cadena(args.boot_dir, cat, args.southbridge, args.evidencia_arranque)
    except BootChainError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        _imprimir(res)
    if any(res[n]["estado"] == "FALLO" for n in NIVELES):
        return 1
    if any(res[n]["estado"] != "OK" for n in requeridos):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests de tools/verify_boot_chain.py. Solo archivos temporales ficticios: nada toca hardware ni medios reales."""
import contextlib
import gzip
import hashlib
import io
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path

from tools import verify_boot_chain as vbc
from tools.verify_boot_chain import BootChainError


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hacer_bzimage(version: bytes = b"6.99.0-test (ficticio)", protocolo: int = 0x020F, loadflags: int = 1,
                  firma: bool = True, hdrs: bool = True, setup_sects: int = 4, relleno: int = 0x6000) -> bytes:
    """Kernel FICTICIO con cabecera x86 válida; no es ejecutable."""
    d = bytearray(relleno)
    d[0x1F1] = setup_sects
    if firma:
        d[0x1FE:0x200] = b"\x55\xaa"
    if hdrs:
        d[0x202:0x206] = b"HdrS"
    struct.pack_into("<H", d, 0x206, protocolo)
    d[0x211] = loadflags
    puntero = 0x2E0
    struct.pack_into("<H", d, 0x20E, puntero)
    d[0x200 + puntero:0x200 + puntero + len(version) + 1] = version + b"\0"
    return bytes(d)


def _entrada_newc(nombre: str, datos: bytes = b"", modo: int = 0o100644) -> bytes:
    nb = nombre.encode() + b"\0"
    cab = b"070701" + b"".join(b"%08X" % v for v in (
        1, modo, 0, 0, 1, 0, len(datos), 0, 0, 0, 0, len(nb), 0))
    salida = cab + nb
    salida += b"\0" * ((-len(salida)) % 4)
    salida += datos + b"\0" * ((-len(datos)) % 4)
    return salida


def hacer_cpio(nombres=("init",), trailer=True, extra=b"") -> bytes:
    cuerpo = b"".join(_entrada_newc(n, b"#!/bin/sh\n") for n in nombres)
    if trailer:
        cuerpo += _entrada_newc("TRAILER!!!")
    return cuerpo + extra


def hacer_initramfs(**kw) -> bytes:
    return gzip.compress(hacer_cpio(**kw), mtime=0)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def poner(self, nombre: str, datos: bytes) -> Path:
        p = self.dir / nombre
        p.write_bytes(datos)
        return p

    def cadena_valida(self):
        self.poner("bzImage", hacer_bzimage())
        self.poner("initramfs.cpio.gz", hacer_initramfs())

    def catalogo(self, kernel: bytes, initramfs: bytes, rel_k="r1", rel_i="r1", sb=("belize",)) -> dict:
        return {"schema_version": 1, "artefactos": [
            {"id": "k", "rol": "kernel", "sha256": sha(kernel), "size_bytes": len(kernel), "release": rel_k,
             "southbridges": list(sb), "evidencia_compatibilidad": "ficticia"},
            {"id": "i", "rol": "initramfs", "sha256": sha(initramfs), "size_bytes": len(initramfs), "release": rel_i},
        ]}


class TestEstructura(Base):
    def test_cadena_minima_ok(self):
        self.cadena_valida()
        self.assertEqual(vbc.verificar_estructura(self.dir)["estado"], "OK")

    def test_falta_kernel(self):
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        r = vbc.verificar_estructura(self.dir)
        self.assertEqual(r["estado"], "FALLO")
        self.assertTrue(any("falta 'bzImage'" in e for e in r["errores"]))

    def test_falta_initramfs(self):
        self.poner("bzImage", hacer_bzimage())
        r = vbc.verificar_estructura(self.dir)
        self.assertTrue(any("falta 'initramfs.cpio.gz'" in e for e in r["errores"]))

    def test_directorio_inexistente_es_error_de_uso(self):
        with self.assertRaises(BootChainError):
            vbc.verificar_estructura(self.dir / "no_existe")

    def test_ruta_es_un_archivo_es_error_de_uso(self):
        f = self.poner("x", b"1")
        with self.assertRaises(BootChainError):
            vbc.verificar_estructura(f)

    def test_archivo_vacio_rechazado(self):
        self.poner("bzImage", b"")
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        r = vbc.verificar_estructura(self.dir)
        self.assertTrue(any("vacío" in e for e in r["errores"]))

    def test_directorio_en_lugar_de_archivo(self):
        (self.dir / "bzImage").mkdir()
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        r = vbc.verificar_estructura(self.dir)
        self.assertTrue(any("no es un archivo regular" in e for e in r["errores"]))

    def test_symlink_valido_rechazado(self):
        real = self.poner("real", hacer_bzimage())
        try:
            (self.dir / "bzImage").symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks no soportados")
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        r = vbc.verificar_estructura(self.dir)
        self.assertTrue(any("enlace simbólico" in e for e in r["errores"]))

    def test_symlink_roto_se_reporta_como_symlink_no_como_ausente(self):
        try:
            (self.dir / "bzImage").symlink_to(self.dir / "no_existe")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks no soportados")
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        r = vbc.verificar_estructura(self.dir)
        self.assertTrue(any("enlace simbólico" in e for e in r["errores"]))
        self.assertFalse(any("falta 'bzImage'" in e for e in r["errores"]))

    def test_tamano_maximo(self):
        self.cadena_valida()
        original = vbc.MAX_KERNEL_BYTES
        vbc.MAX_KERNEL_BYTES = 100
        try:
            r = vbc.verificar_estructura(self.dir)
        finally:
            vbc.MAX_KERNEL_BYTES = original
        self.assertTrue(any("supera el máximo" in e for e in r["errores"]))

    @unittest.skipIf(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), "chmod no aplica como root/Windows")
    def test_archivo_ilegible(self):
        self.cadena_valida()
        p = self.dir / "bzImage"
        p.chmod(0)
        try:
            r = vbc.verificar_estructura(self.dir)
        finally:
            p.chmod(0o600)
        self.assertTrue(any("no se puede leer" in e for e in r["errores"]))

    def test_kernels_de_reserva_y_mayusculas_dan_aviso(self):
        self.cadena_valida()
        self.poner("bzImage.belize", b"x")
        self.poner("BZIMAGE", b"x")
        self.poner("initramfs.old", b"x")
        r = vbc.verificar_estructura(self.dir)
        self.assertEqual(r["estado"], "OK")
        texto = " ".join(r["avisos"])
        self.assertIn("bzImage.belize", texto)
        self.assertIn("BZIMAGE", texto)
        self.assertIn("initramfs.old", texto)

    def test_opcionales_invalidos(self):
        self.cadena_valida()
        self.poner("vram.txt", b"")
        (self.dir / "bootargs.txt").mkdir()
        r = vbc.verificar_estructura(self.dir)
        self.assertEqual(r["estado"], "FALLO")

    def test_mensaje_no_promete_mas_de_lo_verificado(self):
        self.cadena_valida()
        r = vbc.verificar_estructura(self.dir)
        texto = " ".join(r["info"] + r["errores"] + r["avisos"])
        self.assertNotIn("USB-only válida", texto)
        self.assertIn("no valida su contenido", texto)


class TestFormato(Base):
    def test_cadena_ficticia_bien_formada_ok_y_lee_version(self):
        self.cadena_valida()
        r = vbc.verificar_formato(self.dir)
        self.assertEqual(r["estado"], "OK", r)
        self.assertIn("6.99.0-test", " ".join(r["info"]))

    def test_bytes_arbitrarios_no_pasan_como_kernel_ni_initramfs(self):
        self.poner("bzImage", b"dummy kernel")
        self.poner("initramfs.cpio.gz", b"dummy initramfs")
        r = vbc.verificar_formato(self.dir)
        self.assertEqual(r["estado"], "FALLO")
        self.assertTrue(any(e.startswith("bzImage") for e in r["errores"]))
        self.assertTrue(any(e.startswith("initramfs.cpio.gz") for e in r["errores"]))

    def test_ceros_grandes_no_son_kernel(self):
        self.poner("bzImage", b"\0" * 0x8000)
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        r = vbc.verificar_formato(self.dir)
        self.assertTrue(any("0xAA55" in e for e in r["errores"]))

    def test_bzimage_sin_hdrs(self):
        self.poner("bzImage", hacer_bzimage(hdrs=False))
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        self.assertTrue(any("HdrS" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_bzimage_sin_firma(self):
        self.poner("bzImage", hacer_bzimage(firma=False))
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        self.assertTrue(any("0xAA55" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_bzimage_protocolo_viejo(self):
        self.poner("bzImage", hacer_bzimage(protocolo=0x0100))
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        self.assertTrue(any("2.00" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_bzimage_no_cargado_en_alto(self):
        self.poner("bzImage", hacer_bzimage(loadflags=0))
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        self.assertTrue(any("LOADED_HIGH" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_bzimage_truncado(self):
        self.poner("bzImage", hacer_bzimage()[:0x100])
        self.poner("initramfs.cpio.gz", hacer_initramfs())
        self.assertTrue(any("0x264" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_initramfs_gzip_truncado(self):
        self.poner("bzImage", hacer_bzimage())
        datos = hacer_initramfs()
        self.poner("initramfs.cpio.gz", datos[: len(datos) // 2])
        self.assertTrue(any("gzip" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_initramfs_gzip_con_crc_roto(self):
        self.poner("bzImage", hacer_bzimage())
        datos = bytearray(hacer_initramfs())
        datos[-5] ^= 0xFF  # corrompe el CRC32 del pie gzip
        self.poner("initramfs.cpio.gz", bytes(datos))
        self.assertTrue(any("gzip" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_initramfs_rechaza_bytes_tras_miembro_gzip_valido(self):
        self.poner("bzImage", hacer_bzimage())
        datos = hacer_initramfs() + b"\x00basura-final"
        self.poner("initramfs.cpio.gz", datos)
        r = vbc.verificar_formato(self.dir)
        self.assertEqual(r["estado"], "FALLO")
        self.assertTrue(any("datos posteriores" in e for e in r["errores"]), r)

    def test_initramfs_rechaza_miembros_gzip_concatenados_explicito(self):
        self.poner("bzImage", hacer_bzimage())
        datos = hacer_initramfs() + gzip.compress(b"segundo miembro", mtime=0)
        self.poner("initramfs.cpio.gz", datos)
        r = vbc.verificar_formato(self.dir)
        self.assertEqual(r["estado"], "FALLO")
        self.assertTrue(any("datos posteriores" in e for e in r["errores"]), r)

    def test_initramfs_gzip_valido_pero_no_cpio(self):
        self.poner("bzImage", hacer_bzimage())
        self.poner("initramfs.cpio.gz", gzip.compress(b"esto no es cpio" * 20, mtime=0))
        self.assertTrue(any("cpio" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_initramfs_sin_trailer(self):
        self.poner("bzImage", hacer_bzimage())
        self.poner("initramfs.cpio.gz", hacer_initramfs(trailer=False))
        self.assertTrue(any("TRAILER" in e or "termina antes" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_initramfs_sin_init(self):
        self.poner("bzImage", hacer_bzimage())
        self.poner("initramfs.cpio.gz", hacer_initramfs(nombres=("etc/profile",)))
        self.assertTrue(any("/init" in e for e in vbc.verificar_formato(self.dir)["errores"]))

    def test_initramfs_init_con_prefijo_punto_barra(self):
        self.poner("bzImage", hacer_bzimage())
        self.poner("initramfs.cpio.gz", hacer_initramfs(nombres=("./init",)))
        self.assertEqual(vbc.verificar_formato(self.dir)["estado"], "OK")

    def test_initramfs_tope_descomprimido(self):
        self.poner("bzImage", hacer_bzimage())
        self.poner("initramfs.cpio.gz", gzip.compress(b"0" * 5_000_000, mtime=0))
        original = vbc.MAX_INITRAMFS_DESCOMPRIMIDO
        vbc.MAX_INITRAMFS_DESCOMPRIMIDO = 1000
        try:
            r = vbc.verificar_formato(self.dir)
        finally:
            vbc.MAX_INITRAMFS_DESCOMPRIMIDO = original
        self.assertEqual(r["estado"], "FALLO")

    def test_sin_archivos_no_evaluado(self):
        self.assertEqual(vbc.verificar_formato(self.dir)["estado"], "NO_EVALUADO")

    def test_vram_valida_y_limites(self):
        self.cadena_valida()
        for contenido, esperado in ((b"1024\n", "OK"), (b"32", "OK"), (b"4096", "OK"),
                                    (b"31", "FALLO"), (b"4097", "FALLO"), (b"1gb", "FALLO"), (b"-5", "FALLO")):
            self.poner("vram.txt", contenido)
            self.assertEqual(vbc.verificar_formato(self.dir)["estado"], esperado, contenido)

    def test_vram_no_ascii(self):
        self.cadena_valida()
        self.poner("vram.txt", b"\xff\xfe")
        self.assertEqual(vbc.verificar_formato(self.dir)["estado"], "FALLO")

    def test_bootargs_limites(self):
        self.cadena_valida()
        self.poner("bootargs.txt", b"panic=0 console=tty0\n")
        self.assertEqual(vbc.verificar_formato(self.dir)["estado"], "OK")
        self.poner("bootargs.txt", b"a" * 3000)
        self.assertEqual(vbc.verificar_formato(self.dir)["estado"], "FALLO")
        self.poner("bootargs.txt", b"\nsegunda")
        self.assertEqual(vbc.verificar_formato(self.dir)["estado"], "FALLO")

    def test_bootargs_con_segunda_linea_avisa(self):
        self.cadena_valida()
        self.poner("bootargs.txt", b"panic=0\nignorada=1\n")
        r = vbc.verificar_formato(self.dir)
        self.assertEqual(r["estado"], "OK")
        self.assertTrue(any("primera línea" in a for a in r["avisos"]))


class TestIntegridadYMezclas(Base):
    def setUp(self):
        super().setUp()
        self.k, self.i = hacer_bzimage(), hacer_initramfs()
        self.poner("bzImage", self.k)
        self.poner("initramfs.cpio.gz", self.i)

    def test_sin_catalogo_no_evaluado(self):
        r, ident = vbc.verificar_integridad(self.dir, None)
        self.assertEqual(r["estado"], "NO_EVALUADO")
        self.assertEqual(ident, {})

    def test_coincide(self):
        r, ident = vbc.verificar_integridad(self.dir, self.catalogo(self.k, self.i))
        self.assertEqual(r["estado"], "OK", r)
        self.assertEqual(set(ident), {"kernel", "initramfs"})

    def test_hash_distinto(self):
        self.poner("bzImage", hacer_bzimage(version=b"otra"))
        r, _ = vbc.verificar_integridad(self.dir, self.catalogo(self.k, self.i))
        self.assertEqual(r["estado"], "FALLO")

    def test_tamano_distinto_con_hash_igual(self):
        cat = self.catalogo(self.k, self.i)
        cat["artefactos"][0]["size_bytes"] += 1
        r, _ = vbc.verificar_integridad(self.dir, cat)
        self.assertTrue(any("tamaño" in e for e in r["errores"]))

    def test_mezcla_de_versiones(self):
        r, _ = vbc.verificar_integridad(self.dir, self.catalogo(self.k, self.i, rel_k="v1", rel_i="v2"))
        self.assertEqual(r["estado"], "FALLO")
        self.assertTrue(any("mezcla de versiones" in e for e in r["errores"]))

    def test_catalogo_invalido(self):
        base = self.catalogo(self.k, self.i)
        casos = []
        c = json.loads(json.dumps(base)); c["schema_version"] = True; casos.append(c)
        c = json.loads(json.dumps(base)); c["schema_version"] = 2; casos.append(c)
        c = json.loads(json.dumps(base)); c["artefactos"] = []; casos.append(c)
        c = json.loads(json.dumps(base)); c["artefactos"][0]["sha256"] = "XYZ"; casos.append(c)
        c = json.loads(json.dumps(base)); c["artefactos"][0]["rol"] = "rootfs"; casos.append(c)
        c = json.loads(json.dumps(base)); c["artefactos"][1]["id"] = "k"; casos.append(c)
        c = json.loads(json.dumps(base)); c["artefactos"][0]["size_bytes"] = True; casos.append(c)
        c = json.loads(json.dumps(base)); del c["artefactos"][0]["release"]; casos.append(c)
        for caso in casos:
            ruta = self.dir.parent / "cat_tmp.json"
            ruta.write_text(json.dumps(caso), encoding="utf-8")
            try:
                with self.assertRaises(BootChainError, msg=caso):
                    vbc.cargar_catalogo(ruta)
            finally:
                ruta.unlink()

    def test_catalogo_no_json(self):
        ruta = self.dir.parent / "cat_tmp2.json"
        ruta.write_text("{no json", encoding="utf-8")
        try:
            with self.assertRaises(BootChainError):
                vbc.cargar_catalogo(ruta)
        finally:
            ruta.unlink()

    def test_catalogo_del_repositorio_es_valido(self):
        raiz = Path(__file__).resolve().parent.parent
        cat = vbc.cargar_catalogo(raiz / "manifests" / "arranque-catalogo.json")
        self.assertGreaterEqual(len(cat["artefactos"]), 3)


class TestCompatibilidad(Base):
    def setUp(self):
        super().setUp()
        self.k, self.i = hacer_bzimage(), hacer_initramfs()
        self.poner("bzImage", self.k)
        self.poner("initramfs.cpio.gz", self.i)
        self.cat = self.catalogo(self.k, self.i, sb=("belize",))
        _, self.ident = vbc.verificar_integridad(self.dir, self.cat)

    def test_southbridge_desconocido_no_evalua(self):
        for sb in (None, "", "desconocido", "Unknown"):
            self.assertEqual(vbc.verificar_compatibilidad(self.ident, sb, self.cat)["estado"], "NO_EVALUADO")

    def test_coincide(self):
        r = vbc.verificar_compatibilidad(self.ident, "Belize", self.cat)
        self.assertEqual(r["estado"], "OK")
        self.assertIn("no una prueba de arranque", " ".join(r["info"]))

    def test_no_coincide(self):
        self.assertEqual(vbc.verificar_compatibilidad(self.ident, "baikal", self.cat)["estado"], "FALLO")

    def test_kernel_no_identificado(self):
        self.assertEqual(vbc.verificar_compatibilidad({}, "belize", self.cat)["estado"], "NO_EVALUADO")

    def test_sin_catalogo(self):
        self.assertEqual(vbc.verificar_compatibilidad(self.ident, "belize", None)["estado"], "NO_EVALUADO")


class TestArranque(Base):
    def setUp(self):
        super().setUp()
        self.k, self.i = hacer_bzimage(), hacer_initramfs()
        self.poner("bzImage", self.k)
        self.poner("initramfs.cpio.gz", self.i)

    def evidencia(self, **cambios) -> Path:
        ev = {"schema_version": 1, "registro": "docs/lab-logs/LAB-FICTICIO.md", "fecha": "2099-01-01",
              "resultado": "arranque_linux_observado", "sha256_bzImage": sha(self.k), "sha256_initramfs": sha(self.i)}
        ev.update(cambios)
        p = self.dir.parent / "evidencia_tmp.json"
        p.write_text(json.dumps(ev), encoding="utf-8")
        self.addCleanup(lambda: p.exists() and p.unlink())
        return p

    def test_sin_evidencia_no_evaluado(self):
        self.assertEqual(vbc.verificar_arranque(self.dir, None)["estado"], "NO_EVALUADO")

    def test_con_evidencia_coincidente(self):
        r = vbc.verificar_arranque(self.dir, self.evidencia())
        self.assertEqual(r["estado"], "OK")
        self.assertIn("no arrancó nada", " ".join(r["info"]))

    def test_evidencia_de_otro_archivo(self):
        r = vbc.verificar_arranque(self.dir, self.evidencia(sha256_bzImage="0" * 64))
        self.assertEqual(r["estado"], "FALLO")

    def test_evidencia_de_fallo_no_confirma(self):
        r = vbc.verificar_arranque(self.dir, self.evidencia(resultado="led_blanco_sin_handoff"))
        self.assertEqual(r["estado"], "FALLO")

    def test_evidencia_incompleta(self):
        p = self.dir.parent / "evidencia_tmp2.json"
        p.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
        self.addCleanup(lambda: p.exists() and p.unlink())
        self.assertEqual(vbc.verificar_arranque(self.dir, p)["estado"], "FALLO")

    def test_evidencia_ilegible(self):
        with self.assertRaises(BootChainError):
            vbc.verificar_arranque(self.dir, self.dir / "nada.json")


class TestCLI(Base):
    def correr(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = vbc.main([str(a) for a in args])
        return codigo, out.getvalue(), err.getvalue()

    def test_cadena_valida_codigo_0_y_no_confirma_arranque(self):
        self.cadena_valida()
        codigo, out, _ = self.correr(self.dir)
        self.assertEqual(codigo, 0)
        self.assertIn("[NO_EVALUADO] arranque", out)
        self.assertNotIn("USB-only válida", out)

    def test_bytes_basura_codigo_1(self):
        self.poner("bzImage", b"dummy kernel")
        self.poner("initramfs.cpio.gz", b"dummy initramfs")
        self.assertEqual(self.correr(self.dir)[0], 1)

    def test_requerir_integridad_sin_catalogo_falla(self):
        self.cadena_valida()
        self.assertEqual(self.correr(self.dir, "--requerir", "estructura,formato,integridad")[0], 1)

    def test_requerir_nivel_desconocido(self):
        self.cadena_valida()
        self.assertEqual(self.correr(self.dir, "--requerir", "magia")[0], 2)

    def test_directorio_invalido_codigo_2(self):
        codigo, _, err = self.correr(self.dir / "no_existe")
        self.assertEqual(codigo, 2)
        self.assertIn("ERROR", err)

    def test_json_parseable(self):
        self.cadena_valida()
        codigo, out, _ = self.correr(self.dir, "--json")
        self.assertEqual(codigo, 0)
        self.assertEqual(set(json.loads(out)), set(vbc.NIVELES))


if __name__ == "__main__":
    unittest.main()

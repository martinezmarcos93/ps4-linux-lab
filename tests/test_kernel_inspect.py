"""Tests de tools/kernel_inspect.py con kernels FICTICIOS (carga comprimida sintética). No hay kernels reales."""
import bz2
import contextlib
import gzip
import io
import lzma
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from tests.test_verify_boot_chain import hacer_bzimage
from tools import kernel_inspect as ki

CONFIG = ("#\n# Automatically generated file; DO NOT EDIT.\n# Linux/x86_64 6.99.0 Kernel Configuration\n#\n"
          "CONFIG_X86_PS4=y\nCONFIG_X86_PS4_BAIKAL=y\nCONFIG_MODULES=y\nCONFIG_TCP_CONG_BIC=m\n# CONFIG_DRM_RADEON is not set\n"
          "CONFIG_UFS_FS=y\n").encode()


def vmlinux_falso(config: bytes = CONFIG, con_config=True) -> bytes:
    cuerpo = b"\x7fELF" + b"\0" * 60 + b"Linux version 6.99.0-ficticio (x@y) #1\0"
    if con_config:
        cuerpo += b"IKCFG_ST" + gzip.compress(config, mtime=0) + b"IKCFG_ED"
    return cuerpo + b"\0" * 100


def bzimage_con(carga_comprimida: bytes, pie: int | None, vm_len: int) -> bytes:
    base = bytearray(hacer_bzimage(setup_sects=4, relleno=0x6000))
    setup = (base[0x1F1] + 1) * 512
    pie = vm_len if pie is None else pie
    carga = carga_comprimida + struct.pack("<I", pie)
    struct.pack_into("<II", base, 0x248, 0, len(carga))
    return bytes(base[:setup]) + carga


class TestKernelInspect(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def escribir(self, datos: bytes) -> Path:
        p = self.d / "bzImage"
        p.write_bytes(datos)
        return p

    def comprobar(self, comprimir, nombre):
        vm = vmlinux_falso()
        r = ki.inspeccionar(self.escribir(bzimage_con(comprimir(vm), None, len(vm))))
        self.assertEqual(r["compresion"], nombre)
        self.assertTrue(r["pie_coincide"])
        self.assertTrue(r["es_elf"])
        self.assertEqual(r["cadena_linux_version"][:12], "6.99.0-ficti")
        c = r["config_embebida"]
        self.assertEqual(c["simbolos"]["X86_PS4_BAIKAL"], "y")
        self.assertEqual(c["simbolos"]["DRM_RADEON"], "no establecido")
        self.assertEqual(c["simbolos"]["DM_CRYPT"], "ausente")
        self.assertEqual(c["modulos_m"], 1)

    def test_gzip(self):
        self.comprobar(lambda v: gzip.compress(v, mtime=0), "gzip")

    def test_xz(self):
        self.comprobar(lzma.compress, "xz")

    def test_bzip2(self):
        self.comprobar(bz2.compress, "bzip2")

    @unittest.skipUnless(shutil.which("zstd"), "sin zstd")
    def test_zstd_con_pie_de_4_bytes(self):
        self.comprobar(lambda v: subprocess.run(["zstd", "-c", "-q"], input=v, capture_output=True, check=True).stdout, "zstd")

    @unittest.skipUnless(shutil.which("zstd"), "sin zstd")
    def test_zstd_rechaza_salida_mayor_que_tope_sin_acumularla(self):
        vm = b"A" * 4096
        comprimido = subprocess.run(
            ["zstd", "-c", "-q"], input=vm, capture_output=True, check=True
        ).stdout
        # El límite reducido permite probar la barrera sin reservar cientos de MiB.
        with patch.object(ki, "TOPE", 128):
            with self.assertRaisesRegex(ki.KernelError, "mayor que el tope"):
                ki._descomprimir(comprimido + struct.pack("<I", len(vm)))

    def test_pie_de_tamano_incorrecto_se_detecta(self):
        vm = vmlinux_falso()
        r = ki.inspeccionar(self.escribir(bzimage_con(gzip.compress(vm), len(vm) + 1, len(vm))))
        self.assertFalse(r["pie_coincide"])

    def test_sin_config_embebida(self):
        vm = vmlinux_falso(con_config=False)
        r = ki.inspeccionar(self.escribir(bzimage_con(gzip.compress(vm), None, len(vm))))
        self.assertIsNone(r["config_embebida"])

    def test_config_corrupta(self):
        vm = b"\x7fELF" + b"IKCFG_ST" + b"no es gzip" + b"IKCFG_ED"
        with self.assertRaises(ki.KernelError):
            ki.inspeccionar(self.escribir(bzimage_con(gzip.compress(vm), None, len(vm))))

    def test_entradas_invalidas(self):
        for malo in (b"dummy kernel", b"\0" * 0x8000, hacer_bzimage()[:0x100]):
            with self.assertRaises(ki.KernelError):
                ki.inspeccionar(self.escribir(malo))
        with self.assertRaises(ki.KernelError):  # payload fuera del archivo
            base = bytearray(hacer_bzimage(setup_sects=4))
            struct.pack_into("<II", base, 0x248, 0, 10**9)
            ki.inspeccionar(self.escribir(bytes(base)))
        with self.assertRaises(ki.KernelError):  # compresión desconocida
            ki.inspeccionar(self.escribir(bzimage_con(b"\x01\x02\x03\x04" * 10, None, 0)))

    def test_gzip_truncado(self):
        vm = vmlinux_falso()
        comp = gzip.compress(vm)[:-20]
        with self.assertRaises(ki.KernelError):
            ki.inspeccionar(self.escribir(bzimage_con(comp, None, len(vm))))

    def test_cli_y_extraccion_sin_sobrescribir(self):
        vm = vmlinux_falso()
        p = self.escribir(bzimage_con(gzip.compress(vm), None, len(vm)))
        out = self.d / "cfg.txt"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ki.main([str(p), "--extraer-config", str(out)]), 0)
        self.assertEqual(out.read_bytes(), CONFIG)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ki.main([str(p), "--extraer-config", str(out)]), 2)  # ya existe
            self.assertEqual(ki.main([str(self.d / "no_existe")]), 2)


if __name__ == "__main__":
    unittest.main()

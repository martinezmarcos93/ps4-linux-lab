"""Tests de tools/fat32_add_file.py contra herramientas reales (mkfs.vfat, fsck.vfat, 7z) sobre imágenes temporales.

Se omiten si faltan las herramientas. Nunca se usan dispositivos: solo archivos en un directorio temporal.
"""
import contextlib
import hashlib
import io
import os
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import fat32_add_file as fa

MKFS = shutil.which("mkfs.vfat") or "/usr/sbin/mkfs.vfat"
FSCK = shutil.which("fsck.vfat") or "/usr/sbin/fsck.vfat"
SFDISK = shutil.which("sfdisk") or "/usr/sbin/sfdisk"
SIETE_Z = shutil.which("7z")
TIENE_MKFS = os.path.exists(MKFS) and os.path.exists(FSCK)


def aleatorio(n: int, semilla: int = 1) -> bytes:
    return random.Random(semilla).randbytes(n)


@unittest.skipUnless(TIENE_MKFS, "faltan mkfs.vfat/fsck.vfat")
class TestFat32(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.img = self.dir / "fat.img"
        with open(self.img, "wb") as f:
            f.truncate(40 * 1024 * 1024)
        subprocess.run([MKFS, "-F", "32", "-s", "1", "-n", "PRUEBA", str(self.img)], check=True, capture_output=True)

    def tearDown(self):
        self._tmp.cleanup()

    def fsck(self, imagen=None) -> subprocess.CompletedProcess:
        return subprocess.run([FSCK, "-n", str(imagen or self.img)], capture_output=True, text=True)

    def agregar(self, nombre, datos):
        return fa.agregar_archivo(self.img, 0, self.img.stat().st_size, nombre, datos)

    def sha_img(self):
        return hashlib.sha256(self.img.read_bytes()).hexdigest()

    def test_oraculo_fsck_acepta_imagen_vacia(self):
        self.assertEqual(self.fsck().returncode, 0, self.fsck().stdout)

    def test_agrega_archivos_y_fsck_queda_limpio(self):
        self.agregar("bzImage", aleatorio(100_000, 1))
        self.agregar("initramfs.cpio.gz", aleatorio(300_000, 2))
        r = self.fsck()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    @unittest.skipUnless(SIETE_Z, "falta 7z")
    def test_lectura_independiente_con_7z(self):
        k, i = aleatorio(100_000, 1), aleatorio(300_000, 2)
        self.agregar("bzImage", k)
        self.agregar("initramfs.cpio.gz", i)
        listado = subprocess.run([SIETE_Z, "l", str(self.img)], capture_output=True, text=True).stdout
        self.assertIn("bzImage", listado)
        self.assertIn("initramfs.cpio.gz", listado)
        leido = subprocess.run([SIETE_Z, "e", "-so", str(self.img), "bzImage"], capture_output=True).stdout
        self.assertEqual(hashlib.sha256(leido).hexdigest(), hashlib.sha256(k).hexdigest())

    def test_duplicado_no_sobrescribe_ni_modifica_la_imagen(self):
        self.agregar("bzImage", aleatorio(5000))
        antes = self.sha_img()
        with self.assertRaises(fa.FatError):
            self.agregar("BZIMAGE", b"otro")
        self.assertEqual(self.sha_img(), antes)

    def test_nombres_invalidos_y_vacio(self):
        for malo in ("", ".", "..", "a/b", "a\\b", "nul", "con.txt", "x" * 256, " espacio", "punto.", "ñandú"):
            with self.assertRaises(fa.FatError, msg=repr(malo)):
                self.agregar(malo, b"x")
        with self.assertRaises(fa.FatError):
            self.agregar("vacio", b"")

    def test_la_raiz_crece_cuando_se_llena(self):
        for n in range(30):
            self.agregar(f"archivo-largo-{n:02d}.bin", aleatorio(700, n))
        r = self.fsck()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_alias_cortos_no_colisionan(self):
        for n in range(5):
            self.agregar(f"initramfs.cpio.v{n}", aleatorio(600, n))
        self.assertEqual(self.fsck().returncode, 0)

    def test_rechaza_dispositivos_symlinks_y_directorios(self):
        for destino in (Path("/dev/null"), self.dir):
            with self.assertRaises((fa.FatError, OSError)):
                fa.agregar_archivo(destino, 0, 1024 * 1024, "x", b"x")
        try:
            (self.dir / "enlace.img").symlink_to(self.img)
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(fa.FatError):
            fa.agregar_archivo(self.dir / "enlace.img", 0, self.img.stat().st_size, "x", b"x")

    def test_particion_fuera_de_la_imagen(self):
        with self.assertRaises(fa.FatError):
            fa.agregar_archivo(self.img, 0, self.img.stat().st_size + 1, "x", b"x")

    def test_no_es_fat32(self):
        raw = self.dir / "raw.img"
        raw.write_bytes(b"\0" * (1024 * 1024))
        with self.assertRaises(fa.FatError):
            fa.agregar_archivo(raw, 0, raw.stat().st_size, "x", b"x")

    def test_sin_espacio(self):
        with self.assertRaises(fa.FatError):
            self.agregar("grande.bin", b"\1" * (45 * 1024 * 1024))
        self.assertEqual(self.fsck().returncode, 0)

    @unittest.skipUnless(os.path.exists(SFDISK), "falta sfdisk")
    def test_particion_mbr_y_cli(self):
        img = self.dir / "usb.img"
        with open(img, "wb") as f:
            f.truncate(60 * 1024 * 1024)
        subprocess.run([SFDISK, str(img)], input="label: dos\nstart=2048, size=45MiB, type=c\n", text=True, check=True, capture_output=True)
        subprocess.run([MKFS, "-F", "32", "-s", "1", "--offset", "2048", str(img), str(45 * 1024)], check=True, capture_output=True)
        off, size = fa.particion_mbr(img, 1)
        self.assertEqual(off, 2048 * 512)
        k = self.dir / "k.bin"
        k.write_bytes(aleatorio(50_000, 9))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(fa.main([str(img), "--nombre", "bzImage", "--archivo", str(k)]), 0)
        parte = self.dir / "p1.img"
        with open(img, "rb") as f:
            f.seek(off)
            parte.write_bytes(f.read(size))
        r = self.fsck(parte)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with self.assertRaises(fa.FatError):
            fa.particion_mbr(img, 2)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(fa.main([str(img), "--nombre", "bzImage", "--archivo", str(k)]), 2)  # duplicado


if __name__ == "__main__":
    unittest.main()

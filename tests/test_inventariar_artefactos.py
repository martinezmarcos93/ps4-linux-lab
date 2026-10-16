"""Tests de tools/inventariar_artefactos.py con árboles ficticios. No toca artefactos reales."""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests.test_verify_boot_chain import hacer_bzimage, hacer_initramfs
from tools import inventariar_artefactos as inv


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.r = Path(self._t.name) / "raiz"
        (self.r / "boot").mkdir(parents=True)
        self.k, self.i = hacer_bzimage(), hacer_initramfs()
        (self.r / "boot" / "bzImage").write_bytes(self.k)
        (self.r / "boot" / "initramfs.cpio.gz").write_bytes(self.i)

    def tearDown(self):
        self._t.cleanup()

    def correr(self, prov=None):
        return {f["ruta"]: f for f in inv.inventariar({"t": self.r}, prov or {})}


class TestInventario(Base):
    def test_clasificacion_por_nombre(self):
        c = inv.clasificar
        self.assertEqual(c("bzImage"), "kernel")
        self.assertEqual(c("bzImage.belize"), "kernel")
        self.assertEqual(c("initramfs.cpio.gz"), "initramfs")
        self.assertEqual(c("psxitarch-usb.img"), "imagen")
        self.assertEqual(c("psxitarch-usb.img.xz"), "imagen_comprimida")
        self.assertEqual(c("psxitarch-usb.img.xz.part1"), "parte_de_imagen")
        self.assertEqual(c("linux-1024mb.elf"), "payload_loader")
        self.assertEqual(c("goldhen.bin"), "goldhen")
        self.assertEqual(c("psxitarch.tar.xz"), "rootfs")
        self.assertIsNone(c("notas.txt"))
        self.assertIsNone(c("README.md"))

    def test_hash_tamano_y_validacion_de_formato(self):
        f = self.correr()
        self.assertEqual(f["boot/bzImage"]["sha256"], sha(self.k))
        self.assertEqual(f["boot/bzImage"]["bytes"], len(self.k))
        self.assertEqual(f["boot/bzImage"]["validacion"]["formato"], "OK")
        self.assertEqual(f["boot/initramfs.cpio.gz"]["validacion"]["formato"], "OK")
        self.assertTrue(f["boot/bzImage"]["procedencia"].startswith("desconocido"))

    def test_bytes_arbitrarios_no_pasan_el_formato(self):
        (self.r / "boot" / "bzImage.otro").write_bytes(b"dummy kernel")
        self.assertEqual(self.correr()["boot/bzImage.otro"]["validacion"]["formato"], "FALLO")

    def test_procedencia_por_nivel(self):
        prov = {sha(self.k): [{"fuente": "c", "nombre": "k", "nivel": "catalogo"}],
                sha(self.i): [{"fuente": "SHA256SUMS", "nombre": "initramfs", "nivel": "publicado_por_autor"}]}
        f = self.correr(prov)
        self.assertEqual(f["boot/bzImage"]["procedencia"], "coincide con el catálogo")
        self.assertIn("no independiente", f["boot/initramfs.cpio.gz"]["procedencia"])

    def test_vacios_y_symlinks_se_omiten_sin_seguirlos(self):
        (self.r / "boot" / "bzImage.vacio").write_bytes(b"")
        try:
            (self.r / "boot" / "bzImage.enlace").symlink_to(self.r / "boot" / "bzImage")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks")
        f = self.correr()
        self.assertEqual(f["boot/bzImage.vacio"]["omitido"], "archivo vacío")
        self.assertIn("no se sigue", f["boot/bzImage.enlace"]["omitido"])

    def test_directorios_podados_y_archivos_no_relevantes(self):
        (self.r / ".git").mkdir()
        (self.r / ".git" / "bzImage").write_bytes(b"x")
        (self.r / "boot" / "notas.txt").write_text("x")
        self.assertEqual(sorted(self.correr()), ["boot/bzImage", "boot/initramfs.cpio.gz"])

    def test_imagen_mbr(self):
        import subprocess, shutil
        sfdisk = shutil.which("sfdisk") or "/usr/sbin/sfdisk"
        if not Path(sfdisk).exists():
            self.skipTest("sin sfdisk")
        img = self.r / "x.img"
        with open(img, "wb") as f:
            f.truncate(8 * 1024 * 1024)
        subprocess.run([sfdisk, "--quiet", str(img)], input="label: dos\nstart=2048, size=2MiB, type=83\n", text=True, check=True, capture_output=True)
        v = self.correr()["x.img"]["validacion"]
        self.assertIn("tabla mbr", v["detalle"][0])


class TestProcedenciaYCLI(Base):
    def test_cargar_procedencia(self):
        d = Path(self._t.name)
        (d / "SUMAS").write_text(f"{sha(self.k)}  bzImage\n{'0'*64} *otro\nbasura\n")
        (d / "m.json").write_text(json.dumps({"artifacts": [{"path": "p", "sha256": sha(self.i)}]}))
        prov = inv.cargar_procedencia([], [d / "m.json"], [d / "SUMAS"])
        self.assertEqual(prov[sha(self.k)][0]["nivel"], "publicado_por_autor")
        self.assertEqual(prov[sha(self.i)][0]["nivel"], "manifiesto")
        self.assertEqual(prov["0" * 64][0]["nombre"], "otro")

    def test_cli(self):
        out = Path(self._t.name) / "inv.json"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(inv.main(["--raiz", f"t={self.r}", "--json", str(out), "--markdown"]), 0)
        self.assertIn("| t | `boot/bzImage` | kernel |", buf.getvalue())
        self.assertEqual(len(json.loads(out.read_text())["archivos"]), 2)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(inv.main(["--raiz", f"t={self.r}", "--json", str(out)]), 2)  # no sobrescribe
            self.assertEqual(inv.main(["--raiz", "sin_igual"]), 2)
            self.assertEqual(inv.main(["--raiz", "t=/no/existe"]), 2)


if __name__ == "__main__":
    unittest.main()

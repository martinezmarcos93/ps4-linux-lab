"""Pruebas del preflight mínimo con fixtures temporales; nunca toca hardware."""
import tempfile
import unittest
from pathlib import Path

from tools.strict_usb_preflight import verificar_configuracion_minima
from tools.verify_boot_chain import BootChainError


class TestPreflightMinimo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.boot = Path(self.tmp.name)
        (self.boot / "bzImage").write_bytes(b"kernel-ficticio")
        (self.boot / "initramfs.cpio.gz").write_bytes(b"initramfs-ficticio")

    def test_solo_obligatorios_pasa_politica_de_ausencia(self):
        errores = verificar_configuracion_minima(self.boot)
        # El preflight mínimo comprueba estructura, no formato ni integridad.
        self.assertEqual(errores, [])

    def test_bootargs_valido_se_rechaza_por_politica(self):
        (self.boot / "bootargs.txt").write_text("console=tty0\n", encoding="ascii")
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("bootargs.txt" in e and "está presente" in e for e in errores))

    def test_vram_valido_se_rechaza_por_politica(self):
        (self.boot / "vram.txt").write_text("1024\n", encoding="ascii")
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("vram.txt" in e and "está presente" in e for e in errores))

    def test_nombre_opcional_con_mayusculas_se_rechaza(self):
        (self.boot / "BOOTARGS.TXT").write_text("console=tty0\n", encoding="ascii")
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("BOOTARGS.TXT" in e and "nombre reservado" in e for e in errores))

    def test_vram_con_mayusculas_y_symlink_roto_se_rechaza(self):
        try:
            (self.boot / "VRAM.TXT").symlink_to(self.boot / "ausente")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks no soportados en este entorno")
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("VRAM.TXT" in e and "nombre reservado" in e for e in errores))

    def test_opcional_vacio_se_rechaza(self):
        (self.boot / "bootargs.txt").write_bytes(b"")
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("vacío" in e for e in errores))
        self.assertTrue(any("bootargs.txt" in e and "está presente" in e for e in errores))

    def test_opcional_directorio_se_rechaza(self):
        (self.boot / "vram.txt").mkdir()
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("no es un archivo regular" in e for e in errores))
        self.assertTrue(any("vram.txt" in e and "está presente" in e for e in errores))

    def test_symlink_roto_no_cuenta_como_ausente(self):
        try:
            (self.boot / "vram.txt").symlink_to(self.boot / "no-existe")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks no soportados en este entorno")
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("vram.txt" in e and "está presente" in e for e in errores))

    def test_falta_kernel(self):
        (self.boot / "bzImage").unlink()
        errores = verificar_configuracion_minima(self.boot)
        self.assertTrue(any("falta 'bzImage'" in e for e in errores))

    def test_directorio_invalido_es_error_de_uso(self):
        with self.assertRaises(BootChainError):
            verificar_configuracion_minima(self.boot / "no-existe")


if __name__ == "__main__":
    unittest.main()

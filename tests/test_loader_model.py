"""Pruebas de diseño USB-only sobre un MODELO del loader y sobre el parche revisable. No ejecutan ni compilan el loader."""
import re
import unittest
from pathlib import Path

from tools import loader_model as m

RAIZ = Path(__file__).resolve().parent.parent
PARCHE = RAIZ / "patches" / "loader-usb-only-f70f43a.patch"
K, I, B, V = b"k", b"i", b"cmd", b"1024"


def fs(**dirs) -> dict:
    """fs(usb0={"bzImage": K}, interno={...}) -> dict de rutas absolutas."""
    base = {"usb0": "/mnt/usb0/", "usb1": "/mnt/usb1/", "interno": "/data/linux/boot/", "interno2": "/user/system/boot/"}
    salida = {}
    for clave, archivos in dirs.items():
        for nombre, datos in archivos.items():
            salida[base[clave] + nombre] = datos
    return salida


COMPLETO = {"bzImage": K, "initramfs.cpio.gz": I}


class TestUpstreamTalCualEs(unittest.TestCase):
    """Comportamiento del código auditado: demuestra por qué la prioridad USB no es aislamiento."""

    def test_prefiere_usb_si_esta_todo(self):
        r = m.resolver_upstream(fs(usb0=COMPLETO, interno=COMPLETO))
        self.assertFalse(m.usa_almacenamiento_interno(r))

    def test_sin_usb_usa_el_interno_en_silencio(self):
        r = m.resolver_upstream(fs(interno=COMPLETO))
        self.assertTrue(m.usa_almacenamiento_interno(r))

    def test_mezcla_kernel_usb_con_initramfs_interno(self):
        r = m.resolver_upstream(fs(usb0={"bzImage": K}, interno={"initramfs.cpio.gz": I}))
        self.assertTrue(m.hay_mezcla(r))
        self.assertTrue(m.usa_almacenamiento_interno(r))

    def test_mezcla_entre_dos_usb(self):
        r = m.resolver_upstream(fs(usb0={"bzImage": K}, usb1={"initramfs.cpio.gz": I}))
        self.assertTrue(m.hay_mezcla(r))

    def test_opcionales_internos_obsoletos_se_cuelan(self):
        r = m.resolver_upstream(fs(usb0=COMPLETO, interno={"vram.txt": V, "bootargs.txt": B}))
        self.assertEqual(r["vram.txt"], "/data/linux/boot/vram.txt")
        self.assertTrue(m.usa_almacenamiento_interno(r))

    def test_segunda_ruta_interna(self):
        r = m.resolver_upstream(fs(interno2=COMPLETO))
        self.assertEqual(r["bzImage"], "/user/system/boot/bzImage")

    def test_falta_obligatorio_en_todas_las_rutas(self):
        with self.assertRaises(m.ArranqueRechazado):
            m.resolver_upstream(fs(usb0={"bzImage": K}))


class TestVarianteUsbOnly(unittest.TestCase):
    def test_carpeta_usb_completa(self):
        r = m.resolver_usb_only(fs(usb0=COMPLETO))
        self.assertFalse(m.usa_almacenamiento_interno(r))
        self.assertFalse(m.hay_mezcla(r))

    def test_ignora_interno_aunque_este_completo(self):
        with self.assertRaises(m.ArranqueRechazado):
            m.resolver_usb_only(fs(interno=COMPLETO))

    def test_rechaza_mezcla_usb_interno(self):
        with self.assertRaises(m.ArranqueRechazado):
            m.resolver_usb_only(fs(usb0={"bzImage": K}, interno={"initramfs.cpio.gz": I}))

    def test_rechaza_mezcla_entre_usb(self):
        with self.assertRaises(m.ArranqueRechazado):
            m.resolver_usb_only(fs(usb0={"bzImage": K}, usb1={"initramfs.cpio.gz": I}))

    def test_usa_usb1_si_usb0_incompleto(self):
        r = m.resolver_usb_only(fs(usb0={"bzImage": K}, usb1=COMPLETO))
        self.assertEqual(r["bzImage"], "/mnt/usb1/bzImage")
        self.assertFalse(m.hay_mezcla(r))

    def test_opcionales_solo_de_la_misma_carpeta(self):
        r = m.resolver_usb_only(fs(usb0=COMPLETO, usb1={"vram.txt": V}, interno={"bootargs.txt": B}))
        self.assertIsNone(r["vram.txt"])
        self.assertIsNone(r["bootargs.txt"])

    def test_opcionales_de_la_carpeta_elegida(self):
        r = m.resolver_usb_only(fs(usb0={**COMPLETO, "vram.txt": V, "bootargs.txt": B}))
        self.assertEqual(r["vram.txt"], "/mnt/usb0/vram.txt")
        self.assertEqual(r["bootargs.txt"], "/mnt/usb0/bootargs.txt")

    def test_directorio_no_cuenta_como_archivo(self):
        with self.assertRaises(m.ArranqueRechazado):
            m.resolver_usb_only({"/mnt/usb0/bzImage": None, "/mnt/usb0/initramfs.cpio.gz": I})

    def test_ambas_variantes_coinciden_en_el_caso_feliz(self):
        sistema = fs(usb0={**COMPLETO, "vram.txt": V})
        self.assertEqual(m.resolver_upstream(sistema), m.resolver_usb_only(sistema))


class TestParcheRevisable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lineas = PARCHE.read_text(encoding="utf-8").splitlines()
        cls.agregadas = [l[1:] for l in cls.lineas if l.startswith("+") and not l.startswith("+++")]
        cls.quitadas = [l[1:] for l in cls.lineas if l.startswith("-") and not l.startswith("---")]

    def test_apunta_a_la_revision_estudiada(self):
        self.assertEqual(self.lineas[0], "--- a/linux/main-aio.c")
        self.assertEqual(self.lineas[1], "+++ b/linux/main-aio.c")

    def test_elimina_las_rutas_internas(self):
        texto = "\n".join(self.quitadas)
        self.assertIn("HDD_BOOT_PATH", texto)
        self.assertIn("HDD_SECOND_BOOT_PATH", texto)

    def test_no_agrega_literales_de_ruta_interna(self):
        for linea in self.agregadas:
            self.assertNotIn('"/data', linea)
            self.assertNotIn('"/user/system', linea)
            self.assertNotIn("HDD_", linea)

    def test_no_agrega_escritura_de_archivos(self):
        for linea in self.agregadas:
            for prohibido in ("O_WRONLY", "O_RDWR", "O_CREAT", "unlink", "rename(", "mkdir", "write(", "fopen"):
                self.assertNotIn(prohibido, linea)

    def test_solo_dos_carpetas_usb(self):
        usb = re.findall(r'"(/mnt/[^"]+)"', "\n".join(self.agregadas))
        self.assertEqual(sorted(set(usb)), ["/mnt/usb0/", "/mnt/usb1/"])


if __name__ == "__main__":
    unittest.main()

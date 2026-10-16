"""Tests de tools/build_usb_image.py: imágenes pequeñas en directorios temporales con datos ficticios.

No se usan dispositivos ni privilegios. Se omiten si faltan sfdisk/mkfs.vfat/mkfs.ext4.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_verify_boot_chain import hacer_bzimage, hacer_initramfs
from tools import build_usb_image as bu
from tools import fat32_add_file as fat

FALTAN = [h for h, r in bu.HERRAMIENTAS.items() if not (shutil.which(h) or os.path.exists(r))]
ES_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.kernel = self.dir / "k.bin"
        self.kernel.write_bytes(hacer_bzimage())
        self.initramfs = self.dir / "i.cpio.gz"
        self.initramfs.write_bytes(hacer_initramfs())
        self.rootfs = self.dir / "rootfs"
        (self.rootfs / "etc").mkdir(parents=True)
        (self.rootfs / "etc" / "marca.txt").write_text("rootfs ficticio\n", encoding="utf-8")
        (self.dir / "out").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def args(self, **cambios):
        base = dict(salida=self.dir / "out" / "prueba.img", initramfs=self.initramfs, kernel=self.kernel,
                    rootfs_dir=self.rootfs, p1_mib=40, tamano_mib=72, omitir_verificacion=False, dry_run=False)
        base.update(cambios)
        return argparse.Namespace(**base)


@unittest.skipIf(ES_ROOT, "estas pruebas asumen ejecución sin root")
class TestValidaciones(Base):
    def test_dry_run_valida_y_no_crea_nada(self):
        plan = bu.planificar(self.args())
        self.assertEqual(plan["p2_mib"], 72 - 40 - 1)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_salida_existente_se_rechaza(self):
        (self.dir / "out" / "prueba.img").write_bytes(b"x")
        with self.assertRaisesRegex(bu.BuildError, "ya existe"):
            bu.planificar(self.args())

    def test_salida_sin_extension_img(self):
        with self.assertRaisesRegex(bu.BuildError, r"\.img"):
            bu.planificar(self.args(salida=self.dir / "out" / "prueba.bin"))

    def test_salida_en_rutas_prohibidas(self):
        for ruta in ("/dev/sdz.img", "/dev/shm/x.img", "/proc/x.img", "/sys/x.img", "/etc/x.img", "/usr/x.img"):
            with self.assertRaises(bu.BuildError, msg=ruta):
                bu.validar_salida(Path(ruta))

    def test_salida_en_raiz_o_directorio_inexistente(self):
        with self.assertRaises(bu.BuildError):
            bu.validar_salida(Path("/x.img"))
        with self.assertRaises(bu.BuildError):
            bu.validar_salida(self.dir / "no_existe" / "x.img")

    def test_salida_con_padre_symlink_a_ruta_prohibida(self):
        try:
            (self.dir / "enlace").symlink_to("/dev")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks no soportados")
        with self.assertRaises(bu.BuildError):
            bu.validar_salida(self.dir / "enlace" / "x.img")

    def test_entradas_invalidas(self):
        (self.dir / "vacio").write_bytes(b"")
        with self.assertRaisesRegex(bu.BuildError, "vacío"):
            bu.planificar(self.args(kernel=self.dir / "vacio"))
        with self.assertRaisesRegex(bu.BuildError, "regular"):
            bu.planificar(self.args(initramfs=self.dir))
        with self.assertRaises(bu.BuildError):
            bu.planificar(self.args(kernel=self.dir / "no_existe"))
        try:
            (self.dir / "ln").symlink_to(self.kernel)
        except (OSError, NotImplementedError):
            return
        with self.assertRaisesRegex(bu.BuildError, "regular"):
            bu.planificar(self.args(kernel=self.dir / "ln"))

    def test_dispositivo_como_entrada(self):
        with self.assertRaises(bu.BuildError):
            bu.planificar(self.args(kernel=Path("/dev/null")))

    def test_formato_invalido_rechazado_salvo_que_se_omita(self):
        self.kernel.write_bytes(b"dummy kernel")
        with self.assertRaisesRegex(bu.BuildError, "formato"):
            bu.planificar(self.args())
        bu.planificar(self.args(omitir_verificacion=True))
        self.initramfs.write_bytes(b"dummy initramfs")
        self.kernel.write_bytes(hacer_bzimage())
        with self.assertRaisesRegex(bu.BuildError, "formato"):
            bu.planificar(self.args())

    def test_tamanos(self):
        with self.assertRaises(bu.BuildError):
            bu.planificar(self.args(p1_mib=10))
        with self.assertRaises(bu.BuildError):
            bu.planificar(self.args(tamano_mib=50))
        with self.assertRaises(bu.BuildError):
            bu.planificar(self.args(tamano_mib=10_000_000))

    def test_rootfs_invalido(self):
        with self.assertRaises(bu.BuildError):
            bu.planificar(self.args(rootfs_dir=self.kernel))
        fifo = self.rootfs / "fifo"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(bu.BuildError, "especial"):
            bu.planificar(self.args())

    def test_contenido_que_no_cabe(self):
        with open(self.rootfs / "grande.bin", "wb") as f:
            f.truncate(40 * 1024 * 1024)  # disperso: no ocupa disco real
        with self.assertRaisesRegex(bu.BuildError, "no cabe"):
            bu.planificar(self.args())
        with open(self.kernel, "ab") as f:
            f.truncate(60 * 1024 * 1024)
        with self.assertRaisesRegex(bu.BuildError, "no caben"):
            bu.planificar(self.args(omitir_verificacion=True))

    def test_root_rechazado(self):
        with mock.patch("os.geteuid", return_value=0):
            with self.assertRaisesRegex(bu.BuildError, "root"):
                bu.planificar(self.args())

    def test_cli_codigos_de_salida(self):
        base = ["--salida", str(self.dir / "out" / "cli.img"), "--initramfs", str(self.initramfs),
                "--kernel", str(self.kernel), "--rootfs-dir", str(self.rootfs), "--p1-mib", "40", "--tamano-mib", "72"]
        with mock.patch("sys.stdout"):
            self.assertEqual(bu.main(base + ["--dry-run"]), 0)
        self.assertFalse((self.dir / "out" / "cli.img").exists())
        with mock.patch("sys.stderr"):
            self.assertEqual(bu.main(["--salida", "/dev/x.img"] + base[2:]), 2)


@unittest.skipIf(ES_ROOT or FALTAN, f"root o faltan herramientas: {FALTAN}")
class TestConstruccion(Base):
    def test_construye_imagen_verificable(self):
        plan = bu.planificar(self.args())
        destino = bu.construir(plan)
        self.assertTrue(destino.is_file())
        self.assertEqual(sorted(p.name for p in (self.dir / "out").iterdir()), ["prueba.img", "prueba.json"])  # sin temporales
        off1, size1 = fat.particion_mbr(destino, 1)
        off2, size2 = fat.particion_mbr(destino, 2)
        self.assertEqual(off1, 2048 * 512)
        self.assertGreater(off2, off1 + size1 - 1)
        # contenido de la FAT leído sin montar
        p1 = self.dir / "p1.img"
        with open(destino, "rb") as f:
            f.seek(off1)
            p1.write_bytes(f.read(size1))
        siete = shutil.which("7z")
        if siete:
            nombres = subprocess.run([siete, "l", str(p1)], capture_output=True, text=True).stdout
            self.assertIn("bzImage", nombres)
            self.assertIn("initramfs.cpio.gz", nombres)
            leido = subprocess.run([siete, "e", "-so", str(p1), "bzImage"], capture_output=True).stdout
            self.assertEqual(leido, self.kernel.read_bytes())
        # rootfs ext4 leído sin montar
        debugfs = shutil.which("debugfs") or "/usr/sbin/debugfs"
        if os.path.exists(debugfs):
            r = subprocess.run([debugfs, "-R", "cat /etc/marca.txt", f"{destino}?offset={off2}"], capture_output=True, text=True)
            self.assertEqual(r.stdout, "rootfs ficticio\n")
            r = subprocess.run([debugfs, "-R", "stats", f"{destino}?offset={off2}"], capture_output=True, text=True)
            self.assertIn("psxitarch", r.stdout)

    def test_el_resultado_pasa_la_verificacion_de_estructura_y_formato(self):
        from tools import verify_boot_chain as vbc
        destino = bu.construir(bu.planificar(self.args()))
        off1, size1 = fat.particion_mbr(destino, 1)
        p1 = self.dir / "p1.img"
        with open(destino, "rb") as f:
            f.seek(off1)
            p1.write_bytes(f.read(size1))
        siete = shutil.which("7z")
        if not siete:
            self.skipTest("falta 7z")
        extraido = self.dir / "extraido"
        subprocess.run([siete, "x", f"-o{extraido}", str(p1), "bzImage", "initramfs.cpio.gz", "-y"], capture_output=True, check=True)
        self.assertEqual(vbc.verificar_estructura(extraido)["estado"], "OK")
        self.assertEqual(vbc.verificar_formato(extraido)["estado"], "OK")

    def test_fallo_intermedio_no_deja_temporales_ni_destino(self):
        plan = bu.planificar(self.args())
        with mock.patch.object(bu.fat, "agregar_archivo", side_effect=fat.FatError("fallo simulado")):
            with self.assertRaisesRegex(bu.BuildError, "fallo simulado"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_fallo_de_herramienta_externa_limpia(self):
        plan = bu.planificar(self.args())
        real = subprocess.run

        def falso(cmd, *a, **k):
            if cmd and str(cmd[0]).endswith("mkfs.ext4"):
                return subprocess.CompletedProcess(cmd, 1, "", "error simulado")
            return real(cmd, *a, **k)

        with mock.patch("tools.build_usb_image.subprocess.run", side_effect=falso):
            with self.assertRaisesRegex(bu.BuildError, "error simulado"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_temporal_previo_se_respeta_y_no_se_borra(self):
        plan = bu.planificar(self.args())
        previo = self.dir / "out" / ".prueba.img.parcial"
        previo.write_bytes(b"ajeno")
        with self.assertRaisesRegex(bu.BuildError, "temporal previo"):
            bu.construir(plan)
        self.assertEqual(previo.read_bytes(), b"ajeno")

    def test_herramienta_faltante(self):
        with mock.patch("shutil.which", return_value=None), mock.patch("os.path.exists", return_value=False):
            with self.assertRaisesRegex(bu.BuildError, "falta la herramienta"):
                bu.construir({"salida": str(self.dir / "out" / "x.img"), "tamano_total_mib": 0})

    def test_informe_preexistente(self):
        plan = bu.planificar(self.args())
        (self.dir / "out" / "prueba.json").write_bytes(b"{}")
        destino = bu.construir(plan)
        self.assertTrue(destino.is_file())
        self.assertTrue((self.dir / "out" / "prueba.json").is_file())
        informe = json.loads((self.dir / "out" / "prueba.json").read_text(encoding="utf-8"))
        self.assertNotIn(str(self.dir), json.dumps(informe))

    def test_rutas_anonimizadas(self):
        plan = bu.planificar(self.args())
        bu.construir(plan)
        informe = json.loads((self.dir / "out" / "prueba.json").read_text(encoding="utf-8"))
        self.assertEqual(informe["plan"]["initramfs"], "i.cpio.gz")
        self.assertEqual(informe["plan"]["kernel"], "k.bin")
        self.assertEqual(informe["plan"]["rootfs_dir"], "rootfs")

    def test_fsck_falla_limpia(self):
        plan = bu.planificar(self.args())
        with mock.patch("tools.build_usb_image._verificar_p1", side_effect=bu.BuildError("fsck falló")):
            with self.assertRaisesRegex(bu.BuildError, "fsck falló"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])


if __name__ == "__main__":
    unittest.main()

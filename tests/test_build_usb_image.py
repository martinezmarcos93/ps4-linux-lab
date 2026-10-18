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
                    rootfs_dir=self.rootfs, p1_mib=40, tamano_mib=72, omitir_verificacion=False, omitir_fsck=False, dry_run=False)
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

    def test_plan_fija_hashes_y_rechaza_entrada_modificada(self):
        plan = bu.planificar(self.args())
        esperado = plan["entradas"]["kernel"]
        self.assertEqual(esperado["bytes"], self.kernel.stat().st_size)
        self.assertEqual(esperado["sha256"], bu.hashlib.sha256(self.kernel.read_bytes()).hexdigest())
        self.kernel.write_bytes(b"kernel cambiado tras planificar")
        with self.assertRaisesRegex(bu.BuildError, "cambió desde la planificación"):
            bu._leer_snapshot_entrada(self.kernel, "kernel", esperado["sha256"], esperado["bytes"])

    def test_informe_hash_usa_snapshot_incorporada_no_fuente_actual(self):
        kernel_snapshot = self.kernel.read_bytes()
        initramfs_snapshot = self.initramfs.read_bytes()
        self.kernel.write_bytes("contenido distinto posterior a la instantánea".encode("utf-8"))
        imagen_parcial = self.dir / "imagen.parcial"
        informe_parcial = self.dir / "informe.parcial"
        imagen_parcial.write_bytes(b"imagen ficticia")
        plan = {
            "kernel": str(self.kernel),
            "initramfs": str(self.initramfs),
            "rootfs_dir": str(self.rootfs),
            "p1_mib": 40,
            "p2_mib": 31,
        }
        bu._preparar_informe(
            informe_parcial, imagen_parcial, self.dir / "final.img", plan,
            {"fat": {"estado": "OK"}, "ext4": {"estado": "OK"}},
            {"kernel": kernel_snapshot, "initramfs": initramfs_snapshot},
        )
        informe = json.loads(informe_parcial.read_text(encoding="utf-8"))
        self.assertEqual(informe["entradas"]["kernel"]["sha256"],
                         bu.hashlib.sha256(kernel_snapshot).hexdigest())
        self.assertEqual(informe["entradas"]["kernel"]["bytes"], len(kernel_snapshot))
        self.assertNotEqual(informe["entradas"]["kernel"]["sha256"],
                            bu.hashlib.sha256(self.kernel.read_bytes()).hexdigest())

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

    def test_rootfs_recorrido_inaccesible_aborta(self):
        def walk_falla(directorio, onerror=None):
            exc = PermissionError("Permission denied", 13, str(Path(directorio) / "etc"))
            if onerror is not None:
                onerror(exc)
            return iter(())

        with mock.patch("tools.build_usb_image.os.walk", side_effect=walk_falla):
            with self.assertRaisesRegex(bu.BuildError, "no se pudo recorrer"):
                bu.validar_rootfs(self.rootfs)

    def test_tamano_rootfs_recorrido_inaccesible_aborta(self):
        def walk_falla(directorio, onerror=None):
            exc = PermissionError("Permission denied", 13, str(Path(directorio) / "etc"))
            if onerror is not None:
                onerror(exc)
            return iter(())

        with mock.patch("tools.build_usb_image.os.walk", side_effect=walk_falla):
            with self.assertRaisesRegex(bu.BuildError, "no se pudo recorrer"):
                bu._tamano_rootfs(self.rootfs)

    def test_tamano_rootfs_metadatos_inaccesibles_aborta(self):
        lstat_original = os.lstat
        objetivo = str(self.rootfs / "etc" / "marca.txt")

        def lstat_falla(ruta, *args, **kwargs):
            if os.fspath(ruta) == objetivo:
                raise PermissionError("Permission denied", 13, objetivo)
            return lstat_original(ruta, *args, **kwargs)

        with mock.patch("tools.build_usb_image.os.lstat", side_effect=lstat_falla):
            with self.assertRaisesRegex(bu.BuildError, "metadatos"):
                bu._tamano_rootfs(self.rootfs)

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
        self.assertEqual(sorted(p.name for p in (self.dir / "out").iterdir()), ["prueba.img", "prueba.img.informe.json"])  # sin temporales
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

    def _sin(self, *nombres):
        real = bu._buscar
        return mock.patch.object(bu, "_buscar", side_effect=lambda n: None if n in nombres else real(n))

    def test_sin_fsck_vfat_la_construccion_falla_y_no_publica_nada(self):
        plan = bu.planificar(self.args())
        with self._sin("fsck.vfat"):
            with self.assertRaisesRegex(bu.BuildError, "falta fsck.vfat"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_sin_e2fsck_la_construccion_falla_y_no_publica_nada(self):
        plan = bu.planificar(self.args())
        with self._sin("e2fsck"):
            with self.assertRaisesRegex(bu.BuildError, "falta e2fsck"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_omitir_fsck_explicito_queda_registrado_como_no_verificada(self):
        plan = bu.planificar(self.args(omitir_fsck=True))
        with self._sin("fsck.vfat", "e2fsck"):
            destino = bu.construir(plan)
        inf = json.loads((destino.parent / (destino.name + ".informe.json")).read_text())
        self.assertFalse(inf["totalmente_verificada"])
        self.assertEqual(inf["verificaciones"]["fat"]["estado"], "OMITIDA")
        self.assertEqual(inf["verificaciones"]["ext4"]["estado"], "OMITIDA")
        self.assertNotIn("herramienta", inf["verificaciones"]["fat"])

    def test_omitir_fsck_solo_omite_lo_que_falta(self):
        plan = bu.planificar(self.args(omitir_fsck=True))
        with self._sin("fsck.vfat"):
            destino = bu.construir(plan)
        inf = json.loads((destino.parent / (destino.name + ".informe.json")).read_text())
        self.assertEqual(inf["verificaciones"]["fat"]["estado"], "OMITIDA")
        self.assertEqual(inf["verificaciones"]["ext4"]["estado"], "OK")
        self.assertFalse(inf["totalmente_verificada"])

    def test_fallo_de_fsck_no_publica_la_imagen(self):
        plan = bu.planificar(self.args())
        real = subprocess.run

        def falso(cmd, *a, **k):
            if cmd and str(cmd[0]).endswith("fsck.vfat"):
                return subprocess.CompletedProcess(cmd, 4, "daño simulado", "")
            return real(cmd, *a, **k)

        with mock.patch("tools.build_usb_image.subprocess.run", side_effect=falso):
            with self.assertRaisesRegex(bu.BuildError, "fsck.vfat reporta problemas"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_fallo_de_e2fsck_no_publica_la_imagen(self):
        plan = bu.planificar(self.args())
        real = subprocess.run

        def falso(cmd, *a, **k):
            if cmd and str(cmd[0]).endswith("e2fsck"):
                return subprocess.CompletedProcess(cmd, 4, "daño simulado", "")
            return real(cmd, *a, **k)

        with mock.patch("tools.build_usb_image.subprocess.run", side_effect=falso):
            with self.assertRaisesRegex(bu.BuildError, "e2fsck reporta problemas"):
                bu.construir(plan)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    def test_informe_de_una_construccion_completa(self):
        import hashlib
        destino = bu.construir(bu.planificar(self.args()))
        inf = json.loads((destino.parent / (destino.name + ".informe.json")).read_text())
        self.assertTrue(inf["totalmente_verificada"])
        self.assertEqual(inf["verificaciones"]["fat"]["herramienta"], "fsck.vfat -n")
        self.assertEqual(inf["verificaciones"]["ext4"]["herramienta"], "e2fsck -fn")
        self.assertEqual(inf["sha256_imagen"], hashlib.sha256(destino.read_bytes()).hexdigest())
        self.assertEqual(inf["entradas"]["kernel"]["sha256"], hashlib.sha256(self.kernel.read_bytes()).hexdigest())

    def test_cli_no_dice_verificada_si_se_omitio(self):
        import io, contextlib
        base = ["--salida", str(self.dir / "out" / "cli2.img"), "--initramfs", str(self.initramfs), "--kernel", str(self.kernel),
                "--rootfs-dir", str(self.rootfs), "--p1-mib", "40", "--tamano-mib", "72", "--omitir-fsck"]
        out, err = io.StringIO(), io.StringIO()
        with self._sin("fsck.vfat", "e2fsck"), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = bu.main(base)
        self.assertEqual(rc, 0)
        self.assertNotIn("verificados ->", out.getvalue())
        self.assertIn("NO totalmente verificada", err.getvalue())

    def test_cli_sin_fsck_falla_con_codigo_2(self):
        import io, contextlib
        base = ["--salida", str(self.dir / "out" / "cli3.img"), "--initramfs", str(self.initramfs), "--kernel", str(self.kernel),
                "--rootfs-dir", str(self.rootfs), "--p1-mib", "40", "--tamano-mib", "72"]
        with self._sin("fsck.vfat"), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bu.main(base), 2)
        self.assertEqual(list((self.dir / "out").iterdir()), [])

    # ---- publicación atómica del par imagen + informe
    def _carpeta_limpia(self):
        return sorted(p.name for p in (self.dir / "out").iterdir())

    def test_informe_preexistente_se_rechaza_en_el_plan_y_no_se_toca(self):
        previo = self.dir / "out" / "prueba.img.informe.json"
        previo.write_text("ajeno")
        with self.assertRaisesRegex(bu.BuildError, "ya existe .*informe"):
            bu.planificar(self.args())
        self.assertEqual(previo.read_text(), "ajeno")
        self.assertEqual(self._carpeta_limpia(), ["prueba.img.informe.json"])

    def test_informe_que_aparece_despues_del_plan_no_se_sobrescribe_ni_se_publica_la_imagen(self):
        plan = bu.planificar(self.args())
        previo = self.dir / "out" / "prueba.img.informe.json"
        previo.write_text("ajeno")
        with self.assertRaisesRegex(bu.BuildError, "ya existe"):
            bu.construir(plan)
        self.assertEqual(previo.read_text(), "ajeno")
        self.assertEqual(self._carpeta_limpia(), ["prueba.img.informe.json"])

    def test_el_informe_aparece_durante_la_construccion(self):
        plan = bu.planificar(self.args())
        previo = self.dir / "out" / "prueba.img.informe.json"
        real = bu._verificar_sistemas_de_archivos

        def con_carrera(*a, **k):
            previo.write_text("ajeno")
            return real(*a, **k)

        with mock.patch.object(bu, "_verificar_sistemas_de_archivos", side_effect=con_carrera):
            with self.assertRaisesRegex(bu.BuildError, "apareció durante la construcción"):
                bu.construir(plan)
        self.assertEqual(previo.read_text(), "ajeno")
        self.assertEqual(self._carpeta_limpia(), ["prueba.img.informe.json"])

    def test_el_destino_aparece_durante_la_construccion_no_se_sobrescribe_y_se_retira_el_informe_propio(self):
        plan = bu.planificar(self.args())
        destino = self.dir / "out" / "prueba.img"
        real = bu._verificar_sistemas_de_archivos

        def con_carrera(*a, **k):
            destino.write_text("ajeno")
            return real(*a, **k)

        with mock.patch.object(bu, "_verificar_sistemas_de_archivos", side_effect=con_carrera):
            with self.assertRaisesRegex(bu.BuildError, "apareció durante la construcción"):
                bu.construir(plan)
        self.assertEqual(destino.read_text(), "ajeno")
        self.assertEqual(self._carpeta_limpia(), ["prueba.img"], "debe quedar solo el archivo ajeno, sin informe huérfano ni temporales")

    def test_error_al_escribir_el_informe_no_deja_imagen_publicada(self):
        plan = bu.planificar(self.args())
        with mock.patch.object(bu, "_preparar_informe", side_effect=OSError("disco lleno simulado")):
            with self.assertRaisesRegex(bu.BuildError, "disco lleno"):
                bu.construir(plan)
        self.assertEqual(self._carpeta_limpia(), [])

    def test_error_a_mitad_del_informe_deja_el_directorio_limpio(self):
        plan = bu.planificar(self.args())
        with mock.patch.object(bu, "_sha256", side_effect=OSError("lectura fallida simulada")):
            with self.assertRaises(bu.BuildError):
                bu.construir(plan)
        self.assertEqual(self._carpeta_limpia(), [])

    def test_fallo_al_publicar_la_imagen_retira_el_informe_ya_publicado(self):
        plan = bu.planificar(self.args())
        real = bu._publicar
        llamadas = []

        def segunda_falla(o, d):
            llamadas.append(d.name)
            if len(llamadas) == 2:
                raise bu.BuildError("fallo simulado al publicar la imagen")
            return real(o, d)

        with mock.patch.object(bu, "_publicar", side_effect=segunda_falla):
            with self.assertRaisesRegex(bu.BuildError, "fallo simulado"):
                bu.construir(plan)
        self.assertEqual(llamadas, ["prueba.img.informe.json", "prueba.img"], "el informe se publica primero")
        self.assertEqual(self._carpeta_limpia(), [])

    def test_el_informe_describe_exactamente_las_comprobaciones_ejecutadas(self):
        real = subprocess.run
        invocadas = []

        def registra(cmd, *a, **k):
            invocadas.append(os.path.basename(str(cmd[0])))
            return real(cmd, *a, **k)

        with mock.patch("tools.build_usb_image.subprocess.run", side_effect=registra):
            destino = bu.construir(bu.planificar(self.args()))
        inf = json.loads((destino.parent / (destino.name + ".informe.json")).read_text())
        self.assertIn("fsck.vfat", invocadas)
        self.assertIn("e2fsck", invocadas)
        self.assertEqual({k: v["estado"] for k, v in inf["verificaciones"].items()}, {"fat": "OK", "ext4": "OK"})
        # y a la inversa: lo omitido no ejecuta la herramienta ni consta como OK
        shutil.rmtree(self.dir / "out")
        (self.dir / "out").mkdir()
        invocadas.clear()
        with self._sin("fsck.vfat", "e2fsck"), mock.patch("tools.build_usb_image.subprocess.run", side_effect=registra):
            destino = bu.construir(bu.planificar(self.args(omitir_fsck=True)))
        inf = json.loads((destino.parent / (destino.name + ".informe.json")).read_text())
        self.assertNotIn("fsck.vfat", invocadas)
        self.assertNotIn("e2fsck", invocadas)
        self.assertTrue(all(v["estado"] == "OMITIDA" for v in inf["verificaciones"].values()))
        self.assertFalse(inf["totalmente_verificada"])

    def test_hash_del_informe_es_el_de_la_imagen_publicada(self):
        import hashlib
        destino = bu.construir(bu.planificar(self.args()))
        inf = json.loads((destino.parent / (destino.name + ".informe.json")).read_text())
        self.assertEqual(inf["sha256_imagen"], hashlib.sha256(destino.read_bytes()).hexdigest())
        self.assertEqual(self._carpeta_limpia(), ["prueba.img", "prueba.img.informe.json"])

    def test_publicar_sin_enlaces_duros_falla_sin_publicar_ni_sobrescribir(self):
        a, b = self.dir / "a", self.dir / "b"
        a.write_text("nuevo")
        with mock.patch("os.link", side_effect=OSError("sistema de archivos sin soporte")):
            with self.assertRaisesRegex(bu.BuildError, "de forma atómica y sin sobrescritura"):
                bu._publicar(a, b)
        self.assertEqual(a.read_text(), "nuevo", "el temporal de origen debe conservarse para diagnóstico/limpieza")
        self.assertFalse(b.exists(), "no debe publicarse usando una secuencia con carrera TOCTOU")

    def test_publicar_si_el_destino_aparece_no_lo_sobrescribe(self):
        a, b = self.dir / "a", self.dir / "b"
        a.write_text("nuevo")
        b.write_text("ajeno")
        with self.assertRaisesRegex(bu.BuildError, "apareció durante la construcción"):
            bu._publicar(a, b)
        self.assertEqual(a.read_text(), "nuevo")
        self.assertEqual(b.read_text(), "ajeno")

    def test_publicar_revierte_el_destino_si_falla_el_unlink_del_temporal(self):
        a, b = self.dir / "a", self.dir / "b"
        a.write_text("nuevo")
        unlink_real = os.unlink
        llamadas = []

        def falla_una_vez(path, *args, **kwargs):
            llamadas.append(Path(path))
            if len(llamadas) == 1:
                raise PermissionError("fallo simulado al retirar temporal")
            return unlink_real(path, *args, **kwargs)

        with mock.patch("os.unlink", side_effect=falla_una_vez):
            with self.assertRaisesRegex(bu.BuildError, "no se pudo retirar el temporal"):
                bu._publicar(a, b)
        self.assertTrue(a.exists(), "el temporal original debe quedar disponible para diagnóstico")
        self.assertFalse(b.exists(), "la publicación debe revertirse si no se pudo retirar el temporal")

    def test_herramienta_faltante(self):
        with mock.patch("shutil.which", return_value=None), mock.patch("os.path.exists", return_value=False):
            with self.assertRaisesRegex(bu.BuildError, "falta la herramienta"):
                bu.construir({"salida": str(self.dir / "out" / "x.img")})


if __name__ == "__main__":
    unittest.main()

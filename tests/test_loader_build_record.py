"""Coherencia del registro de la compilación aislada del loader y de las salvaguardas del script. No usa Docker."""
import hashlib
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MANIFIESTO = RAIZ / "manifests" / "loader-f70f43a-build.json"
FUENTES = RAIZ / "manifests" / "loader-f70f43a-sources.sha256"
PARCHE = RAIZ / "patches" / "loader-usb-only-f70f43a.patch"
SCRIPT = RAIZ / "scripts" / "build_loader_isolated.sh"
DOCKERFILE = RAIZ / "build-env" / "loader" / "Dockerfile"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class TestRegistro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))

    def test_el_hash_del_parche_registrado_es_el_del_archivo(self):
        real = hashlib.sha256(PARCHE.read_bytes()).hexdigest()
        self.assertEqual(self.m["parche"]["sha256"], real, "el parche cambió: hay que recompilar y regenerar el registro")

    def test_hashes_bien_formados(self):
        for variante in ("original", "parcheado"):
            r = self.m["resultados"][variante]
            self.assertEqual(r["make_exit"], 0)
            self.assertEqual(len(r["sha256"]), 18)
            self.assertEqual(len(r["sha256_kexec_bin"]), 20)
            for h in list(r["sha256"].values()) + list(r["sha256_kexec_bin"].values()):
                self.assertRegex(h, HEX64)

    def test_original_y_parcheado_difieren_solo_donde_corresponde(self):
        o, p = self.m["resultados"]["original"], self.m["resultados"]["parcheado"]
        self.assertTrue(all(o["sha256"][k] != p["sha256"][k] for k in o["sha256"]))
        self.assertEqual(o["sha256_kexec_bin"], p["sha256_kexec_bin"])

    def test_no_se_afirma_reproduccion_bit_a_bit(self):
        c = self.m["comparacion_con_binario_de_la_distribucion"]
        self.assertFalse(c["reproducido_bit_a_bit"])
        self.assertTrue(self.m["resultados"]["original_segunda_vez"]["identico_al_primero"])
        self.assertFalse(self.m["entradas_remotas_de_lib_syscalls_py"]["usadas_en_la_compilacion"])

    def test_fuentes_registradas(self):
        lineas = FUENTES.read_text(encoding="utf-8").splitlines()
        datos = [l for l in lineas if not l.startswith("#")]
        self.assertEqual(len(datos), 41)
        for l in datos:
            h, ruta = l.split("  ", 1)
            self.assertRegex(h, HEX64)
            self.assertFalse(ruta.startswith("freebsd-headers/"))
        self.assertIn(self.m["fuente"]["commit"], lineas[-1])
        self.assertIn(self.m["fuente"]["tree"], lineas[-1])

    def test_evidencia_adjunta_existe(self):
        for n in ("build-original.log.gz", "build-parcheado.log.gz", "regen_syscalls_sin_red.py",
                  "fuente1-cabeceras-http.txt", "fuente2-cabeceras-http.txt"):
            self.assertTrue((RAIZ / "docs" / "evidence" / "loader-build" / n).is_file(), n)

    def test_cabeceras_http_sin_cookies(self):
        for n in ("fuente1-cabeceras-http.txt", "fuente2-cabeceras-http.txt"):
            texto = (RAIZ / "docs" / "evidence" / "loader-build" / n).read_text(encoding="utf-8").lower()
            self.assertNotIn("set-cookie", texto)
            self.assertNotRegex(texto, r"(?m)^cookie:")


class TestSalvaguardasDelScript(unittest.TestCase):
    def test_flags_de_aislamiento_presentes(self):
        s = SCRIPT.read_text(encoding="utf-8")
        for flag in ("--network none", "--read-only", "--cap-drop ALL", "no-new-privileges", "--pids-limit", "--memory"):
            self.assertIn(flag, s)

    def test_flags_peligrosos_ausentes(self):
        s = SCRIPT.read_text(encoding="utf-8") + DOCKERFILE.read_text(encoding="utf-8")
        for malo in ("--privileged", "docker.sock", "--device", "--network host", "--net=host", "$HOME", "~/", "-v /:", "--pid host", "--cap-add"):
            self.assertNotIn(malo, s)

    def test_solo_se_montan_la_copia_y_la_salida(self):
        montajes = re.findall(r'-v "([^"]+)":', SCRIPT.read_text(encoding="utf-8"))
        self.assertEqual(montajes, ['$OUT/src', '$OUT'])

    def test_la_compilacion_no_usa_red_ni_python(self):
        d = "\n".join(l for l in DOCKERFILE.read_text(encoding="utf-8").lower().splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("python", d)
        self.assertNotIn("curl", d)
        self.assertNotIn("wget", d)
        self.assertIn("user 10001", d)

    def test_el_script_no_ejecuta_los_elf(self):
        s = SCRIPT.read_text(encoding="utf-8")
        self.assertNotRegex(s, r"\./(payloads|linux-)|payloads/linux-[^ ]*\.elf\s*(;|&&|\|\|)\s*$")

    def test_argumentos_invalidos_fallan_antes_de_docker(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            r = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            r = subprocess.run(["bash", str(SCRIPT), str(t), str(t / "salida")], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)  # no es el loader
            (t / "linux").mkdir()
            (t / "lib").mkdir()
            (t / "ya_existe").mkdir()
            r = subprocess.run(["bash", str(SCRIPT), str(t), str(t / "ya_existe")], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertIn("ya existe", r.stderr)
            r = subprocess.run(["bash", str(SCRIPT), str(t), "/etc/x_salida"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()

"""Inyección de fallos sobre scripts/build_loader_isolated.sh y tools/verify_loader_build.py.

El script y el `inner_build.sh` se ejecutan DE VERDAD en el anfitrión; solo se sustituyen `docker` (por un docker simulado
que ejecuta inner_build.sh localmente, sin contenedor) y `make` (por un make simulado con modos de fallo). No hay red,
no hay PS4 y no se ejecuta ningún binario real del loader. El docker simulado NO prueba el aislamiento del contenedor.
"""
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import verify_loader_build as vlb

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "build_loader_isolated.sh"
INNER = RAIZ / "build-env" / "loader" / "inner_build.sh"

FAKE_DOCKER = r'''#!/usr/bin/env bash
# docker simulado: run => ejecuta inner_build.sh en el anfitrión con rutas traducidas
case "$1 $2" in
  "image inspect") [ -z "${FAKE_NO_IMAGE:-}" ] && { echo sha256:fake; exit 0; } || exit 1;;
esac
[ "$1" = build ] && exit "${FAKE_BUILD_RC:-0}"
if [ "$1" = run ]; then
  shift
  src=""; out=""
  while [ $# -gt 0 ]; do
    if [ "$1" = "-v" ]; then
      IFS=: read -r host cont _ <<< "$2"
      [ "$cont" = /work/src ] && src=$host
      [ "$cont" = /out ] && out=$host
      shift 2
    else shift; fi
  done
  [ -z "${FAKE_DOCKER_RUN_RC:-}" ] || exit "$FAKE_DOCKER_RUN_RC"
  PS4LAB_SRC=$src PS4LAB_OUT=$out PATH="$FAKE_BIN:$PATH" exec bash "$FAKE_INNER"
fi
exit 0
'''

FAKE_MAKE = r'''#!/usr/bin/env bash
mode=${FAKE_MODE:-ok}
mkdir -p linux/payloads
mk() { mkdir -p "$(dirname "$1")"; printf '%s' "$2" > "$1"; }
for t in 32 64 128 256 512 1024 2048 3072 4096; do
  mk linux/payloads/linux-${t}mb.elf "$(printf '\177ELF')elf-$t"
  mk linux/payloads/linux-${t}mb.bin "bin-$t"
done
for f in 505 672 700 750 800 850 900 903 960 1000 1050 1100 1102 1150 1200 1250 1300 1302 1350 1352; do
  mk linux/kexec-build/$f/kexec.bin "kexec-$f"
done
case "$mode" in
  ok) exit 0;;
  make_fail) exit 2;;
  make_fail_sin_artefactos) rm -rf linux/payloads linux/kexec-build; exit 1;;
  parcial) rm linux/payloads/linux-4096mb.bin; rm linux/payloads/linux-4096mb.elf; rm -r linux/kexec-build/1352; exit 0;;
  sin_elf) rm linux/payloads/linux-512mb.elf; exit 0;;
  sin_bin) rm linux/payloads/linux-512mb.bin; exit 0;;
  sin_kexec) rm linux/kexec-build/1352/kexec.bin; exit 0;;
  elf_vacio) : > linux/payloads/linux-64mb.elf; exit 0;;
  bin_vacio) : > linux/payloads/linux-64mb.bin; exit 0;;
  kexec_vacio) : > linux/kexec-build/700/kexec.bin; exit 0;;
  elf_sin_firma) mk linux/payloads/linux-64mb.elf "no-es-un-elf"; exit 0;;
  extra) mk linux/payloads/linux-128mb.elf.old "viejo"; exit 0;;
  dir_extra) mkdir linux/kexec-build/9999; exit 0;;
  duplicado) cp linux/payloads/linux-32mb.elf linux/payloads/linux-64mb.elf; exit 0;;
  symlink) rm linux/kexec-build/700/kexec.bin; ln -s ../505/kexec.bin linux/kexec-build/700/kexec.bin; exit 0;;
esac
exit 0
'''


def escribir_ejecutable(ruta: Path, texto: str):
    ruta.write_text(texto, encoding="utf-8")
    ruta.chmod(ruta.stat().st_mode | stat.S_IXUSR)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.t = Path(self._tmp.name)
        self.bin = self.t / "bin"
        self.bin.mkdir()
        escribir_ejecutable(self.bin / "docker", FAKE_DOCKER)
        escribir_ejecutable(self.bin / "make", FAKE_MAKE)
        self.src = self.t / "loader"
        (self.src / "linux").mkdir(parents=True)
        (self.src / "lib").mkdir()
        (self.src / "lib" / "syscalls.asm").write_text("; asm\n")
        (self.src / "lib" / "syscalls.py").write_text("# py\n")
        self.out = self.t / "salida"

    def tearDown(self):
        self._tmp.cleanup()

    def correr(self, modo="ok", extra_env=None, args=()):
        env = dict(os.environ, DOCKER=str(self.bin / "docker"), FAKE_BIN=str(self.bin), FAKE_INNER=str(INNER), FAKE_MODE=modo)
        env.update(extra_env or {})
        return subprocess.run(["bash", str(SCRIPT), str(self.src), str(self.out), *args], capture_output=True, text=True, env=env)

    def informe(self):
        return json.loads((self.out / "verificacion.json").read_text(encoding="utf-8"))


class TestCompilacionValida(Base):
    def test_compilacion_completa_y_valida_pasa(self):
        r = self.correr("ok")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK: compilación y conjunto de artefactos verificados", r.stdout)
        self.assertEqual((self.out / "make.exit").read_text().strip(), "0")
        lineas = (self.out / "artefactos.sha256").read_text().splitlines()
        self.assertEqual(len(lineas), 38)
        self.assertEqual(sum(l.endswith(".elf") for l in lineas), 9)
        self.assertEqual(sum(l.endswith(".bin") and "kexec" not in l for l in lineas), 9)
        self.assertEqual(sum("kexec.bin" in l for l in lineas), 20)
        inf = self.informe()
        self.assertTrue(inf["ok"])
        self.assertEqual(inf["encontrados_validos"], {"elf": 9, "bin": 9, "kexec": 20})

    def test_hash_registrado_es_el_del_archivo(self):
        import hashlib
        self.correr("ok")
        h = hashlib.sha256((self.out / "src/linux/payloads/linux-1024mb.bin").read_bytes()).hexdigest()
        self.assertIn(f"{h}  payloads/linux-1024mb.bin", (self.out / "artefactos.sha256").read_text())


class TestInyeccionDeFallos(Base):
    def assert_falla(self, modo, esperado_en_informe, rc_esperado=None, **kw):
        r = self.correr(modo, **kw)
        self.assertNotEqual(r.returncode, 0, f"{modo}: el script reportó éxito falso\n{r.stdout}{r.stderr}")
        if rc_esperado is not None:
            self.assertEqual(r.returncode, rc_esperado, f"{modo}\n{r.stdout}{r.stderr}")
        self.assertTrue((self.out / "build.log").is_file(), f"{modo}: se perdió el log")
        self.assertFalse((self.out / "artefactos.sha256").exists(), f"{modo}: se publicó artefactos.sha256 ante un fallo")
        inf = self.informe()
        self.assertFalse(inf["ok"])
        self.assertTrue(any(esperado_en_informe in e for e in inf["errores"]), f"{modo}: {inf['errores']}")
        self.assertIn("FALLO", r.stderr)
        return r

    def test_make_con_codigo_distinto_de_cero_falla_aunque_existan_todos_los_artefactos(self):
        r = self.assert_falla("make_fail", "make terminó con código 2", rc_esperado=2)
        self.assertIn("NO terminó bien", r.stderr)
        self.assertEqual((self.out / "make.exit").read_text().strip(), "2")
        self.assertTrue((self.out / "src/linux/payloads/linux-1024mb.elf").exists(), "los resultados de una compilación fallida no se borran")

    def test_make_falla_sin_artefactos(self):
        self.assert_falla("make_fail_sin_artefactos", "make terminó con código 1", rc_esperado=1)

    def test_compilacion_parcial_no_se_acepta(self):
        r = self.assert_falla("parcial", "falta payloads/linux-4096mb.elf", rc_esperado=1)
        self.assertIn("conjunto de artefactos no es válido", r.stderr)
        self.assertEqual(self.informe()["encontrados_validos"], {"elf": 8, "bin": 8, "kexec": 19})

    def test_falta_un_elf(self):
        self.assert_falla("sin_elf", "falta payloads/linux-512mb.elf")

    def test_falta_un_bin(self):
        self.assert_falla("sin_bin", "falta payloads/linux-512mb.bin")

    def test_falta_un_kexec_bin(self):
        self.assert_falla("sin_kexec", "falta kexec-build/1352/kexec.bin")

    def test_artefactos_vacios(self):
        self.assert_falla("elf_vacio", "payloads/linux-64mb.elf está vacío")
        shutil.rmtree(self.out)
        self.assert_falla("bin_vacio", "payloads/linux-64mb.bin está vacío")
        shutil.rmtree(self.out)
        self.assert_falla("kexec_vacio", "kexec-build/700/kexec.bin está vacío")

    def test_elf_sin_firma(self):
        self.assert_falla("elf_sin_firma", "no empieza con la firma ELF")

    def test_archivo_inesperado_en_payloads(self):
        self.assert_falla("extra", "archivos inesperados en payloads/")

    def test_directorio_inesperado_en_kexec_build(self):
        self.assert_falla("dir_extra", "directorios inesperados en kexec-build/")

    def test_hash_duplicado(self):
        self.assert_falla("duplicado", "hash duplicado en elf")

    def test_symlink_no_cuenta_como_artefacto(self):
        self.assert_falla("symlink", "no es un archivo regular")

    def test_el_contenedor_no_arranca(self):
        r = self.correr("ok", extra_env={"FAKE_DOCKER_RUN_RC": "125"})
        self.assertEqual(r.returncode, 125, r.stdout + r.stderr)
        inf = self.informe()
        self.assertFalse(inf["ok"])
        self.assertTrue(any("make.exit" in e for e in inf["errores"]))
        self.assertFalse((self.out / "artefactos.sha256").exists())

    def test_falla_la_construccion_de_la_imagen(self):
        r = self.correr("ok", extra_env={"FAKE_NO_IMAGE": "1", "FAKE_BUILD_RC": "1"})
        self.assertEqual(r.returncode, 3)
        self.assertIn("no se pudo construir la imagen", r.stderr)

    def test_make_exit_obsoleto_no_se_reutiliza(self):
        # inner_build.sh borra make.exit antes de compilar: un 0 viejo no puede validar una corrida nueva
        out = self.t / "out_inner"
        out.mkdir()
        (out / "make.exit").write_text("0\n")
        env = dict(os.environ, PS4LAB_SRC=str(self.src), PS4LAB_OUT=str(out), PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_MODE="make_fail")
        r = subprocess.run(["bash", str(INNER)], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)
        self.assertEqual((out / "make.exit").read_text().strip(), "2")
        self.assertIn("make exit=2", (out / "build.log").read_text())


class TestVerificadorDirecto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.o = Path(self._tmp.name)
        (self.o / "src/linux").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_sin_make_exit_falla(self):
        self.assertFalse(vlb.verificar(self.o)["ok"])

    def test_make_exit_ilegible(self):
        (self.o / "make.exit").write_text("basura")
        self.assertTrue(any("make.exit" in e for e in vlb.verificar(self.o)["errores"]))

    def test_manifiesto_distingue_variantes(self):
        t = Path(self._tmp.name)
        # Construye una salida válida y un manifiesto cuyo hash de un ELF no coincide
        env_bin = t / "b"
        env_bin.mkdir()
        escribir_ejecutable(env_bin / "make", FAKE_MAKE)
        (self.o / "make.exit").write_text("0")
        subprocess.run(["bash", "-c", f'cd {self.o}/src && PATH={env_bin}:$PATH make'], check=True)
        inf = vlb.verificar(self.o)
        self.assertTrue(inf["ok"], inf["errores"])
        manifiesto = {"resultados": {"original": {"sha256": dict(inf["sha256"]["elf"], **inf["sha256"]["bin"]),
                                                   "sha256_kexec_bin": dict(inf["sha256"]["kexec"])}}}
        self.assertTrue(vlb.verificar(self.o, manifiesto, "original")["ok"])
        self.assertTrue(any("no tiene la variante" in e for e in vlb.verificar(self.o, manifiesto, "parcheado")["errores"]))
        manifiesto["resultados"]["original"]["sha256"]["linux-32mb.elf"] = "0" * 64
        self.assertTrue(any("distinto al del manifiesto" in e for e in vlb.verificar(self.o, manifiesto, "original")["errores"]))

    def test_clasificacion_de_advertencias_del_enlazador(self):
        (self.o / "build.log").write_text(
            "/usr/bin/ld: warning: x.o: missing .note.GNU-stack section implies executable stack\n"
            "/usr/bin/ld: warning: ../lib/lib.a: requires executable stack (because ...)\n"
            "/usr/bin/ld: warning: kexec.elf has a LOAD segment with RWX permissions\n"
            "main.c:1: warning: algo distinto\n", encoding="utf-8")
        self.assertEqual(vlb.clasificar_advertencias(self.o / "build.log"),
                         {"ld_pila_ejecutable": 2, "ld_segmento_rwx": 1, "otras": 1})


class TestEstaticas(unittest.TestCase):
    def test_el_script_no_oculta_fallos_ni_abre_permisos(self):
        s = SCRIPT.read_text(encoding="utf-8") + INNER.read_text(encoding="utf-8")
        self.assertNotIn("exit 0", s)
        self.assertNotIn("chmod", s)
        self.assertNotIn("a+rwx", s)
        self.assertNotIn("a+rwX", s)
        self.assertIn('echo "$rc" > "$OUT/make.exit"', INNER.read_text(encoding="utf-8"))
        self.assertIn('exit "$rc"', INNER.read_text(encoding="utf-8"))

    def test_el_contenedor_corre_con_el_uid_del_anfitrion_y_plataforma_fija(self):
        s = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('--user "$(id -u):$(id -g)"', s)
        self.assertIn("--platform linux/amd64", s)

    def test_el_script_acepta_y_aplica_parches_en_orden(self):
        s = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("PARCHEES=()", s)
        self.assertIn('PARCHEES+=("$(readlink -f "$PARCHE")")', s)
        self.assertIn('for PARCHE in "${PARCHEES[@]}"; do', s)
        self.assertIn('git apply --check "$PARCHE" && git apply "$PARCHE"', s)
        self.assertIn('tee -a "$OUT/parches.txt"', s)


if __name__ == "__main__":
    unittest.main()

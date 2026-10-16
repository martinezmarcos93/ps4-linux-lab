"""Tests de tools/payload_static.py con blobs FICTICIOS. No hay payloads reales ni ejecución de nada."""
import contextlib
import hashlib
import io
import json
import os
import random
import tempfile
import unittest
import zlib
from pathlib import Path

from tools import payload_static as ps


def cuerpo_ficticio(semilla: int = 1, n: int = 20000) -> bytes:
    rnd = random.Random(semilla)
    palabras = [b"[Ficticio] iniciando modulo", b"ruta /dev/null", b"valor=%d", b"SIN_URL_REAL", b"fin de prueba"]
    partes = []
    while sum(map(len, partes)) < n:
        partes.append(rnd.choice(palabras) + bytes([rnd.randrange(1, 40)]))
    return b"".join(partes)[:n]


def blob(cuerpo: bytes, prefijo: bytes = b"\xe9\x10\x00\x00\x00" + b"\x90" * 300, cola: bytes = b"\x00" * 64) -> bytes:
    return prefijo + zlib.compress(cuerpo, 9) + cola


class TestPayloadStatic(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_encuentra_y_descomprime_el_flujo(self):
        cuerpo = cuerpo_ficticio()
        datos = blob(cuerpo)
        info = ps.analizar(datos)
        self.assertEqual(len(info["flujos_zlib"]), 1)
        f = info["flujos_zlib"][0]
        self.assertEqual(f["offset"], 305)
        self.assertEqual(f["bytes_descomprimidos"], len(cuerpo))
        self.assertEqual(f["sha256_descomprimido"], hashlib.sha256(cuerpo).hexdigest())
        self.assertEqual(f["formato"], "crudo/desconocido")

    def test_reconoce_elf(self):
        cuerpo = b"\x7fELF" + cuerpo_ficticio(2)
        self.assertEqual(ps.analizar(blob(cuerpo))["flujos_zlib"][0]["formato"], "ELF")

    def test_sin_flujo_zlib(self):
        rnd = random.Random(7)
        datos = bytes(rnd.randrange(256) for _ in range(5000))
        self.assertEqual(ps.analizar(datos)["flujos_zlib"], [])

    def test_flujo_truncado_no_se_acepta(self):
        comprimido = zlib.compress(cuerpo_ficticio(), 9)
        datos = b"\x90" * 100 + comprimido[: len(comprimido) // 2]
        self.assertEqual(ps.analizar(datos)["flujos_zlib"], [])

    def test_tope_de_salida_zlib(self):
        bomba = b"\x00" * 100 + zlib.compress(b"0" * 5_000_000, 9)
        self.assertEqual(ps.buscar_flujos_zlib(bomba, maximo_salida=10_000), [])

    def test_salida_chica_no_cuenta(self):
        self.assertEqual(ps.analizar(blob(b"hola"))["flujos_zlib"], [])

    def test_entropia(self):
        self.assertEqual(ps.entropia(b""), 0.0)
        self.assertEqual(ps.entropia(b"\x00" * 100), 0.0)
        self.assertAlmostEqual(ps.entropia(bytes(range(256))), 8.0, places=6)

    def test_regiones_distinguen_codigo_y_denso(self):
        rnd = random.Random(3)
        denso = bytes(rnd.randrange(256) for _ in range(2048))
        regs = ps.regiones_por_entropia(b"\x90" * 1024 + denso)
        self.assertEqual(regs[0]["clase"], "codigo_o_datos")
        self.assertEqual(regs[-1]["clase"], "denso")  # 256 bytes pseudoaleatorios rondan 7.2 bits, no 8
        self.assertEqual(ps.regiones_por_entropia(bytes(range(256)))[0]["clase"], "aleatorio")

    def test_cadenas(self):
        self.assertEqual(ps.cadenas(b"\x00abcdef\x01ab\x00hola mundo\xff"), {"abcdef", "hola mundo"})

    def test_indicadores_red(self):
        datos = (b"x\0https://api.ejemplo.test/v1/a?b=1\0srv 10.1.2.3 y 999.1.1.1 y 1.2.3.4.5\0host cdn.ejemplo.com.\0"
                 b"version 1.2.3 libfoo.so no_es_host")
        r = ps.indicadores_red(datos)
        self.assertEqual(r["urls"], ["https://api.ejemplo.test/v1/a?b=1"])
        self.assertEqual(r["ipv4"], ["10.1.2.3"])
        self.assertIn("cdn.ejemplo.com", r["hosts"])
        self.assertNotIn("libfoo.so", r["hosts"])

    def test_indicadores_se_calculan_sobre_cuerpo_descomprimido(self):
        cuerpo = cuerpo_ficticio() + b"\0https://ejemplo.invalid/x\0"
        info = ps.analizar(blob(cuerpo))
        self.assertEqual(info["indicadores_red_archivo"]["urls"], [])
        self.assertEqual(info["indicadores_red_cuerpos"][0]["urls"], ["https://ejemplo.invalid/x"])

    def test_comparar_identicos_y_distintos(self):
        a = ps.analizar(blob(cuerpo_ficticio(1)))
        b = ps.analizar(blob(cuerpo_ficticio(1)))
        c = ps.analizar(blob(b"\x01\x02\x03unico" * 2000))
        ig = ps.comparar(a, b)
        self.assertEqual(ig["fraccion_ventanas_de_a_en_b"], 1.0)
        self.assertEqual(ig["fraccion_cadenas_de_a_en_b"], 1.0)
        dist = ps.comparar(a, c)
        self.assertLess(dist["fraccion_ventanas_de_a_en_b"], 0.5)
        self.assertIn("no demuestra equivalencia", ig["aviso"])

    def test_comparar_sin_flujos(self):
        a = ps.analizar(b"\x90" * 100)
        b = ps.analizar(blob(cuerpo_ficticio()))
        r = ps.comparar(a, b)
        self.assertIsNone(r["fraccion_cadenas_de_a_en_b"])

    def test_leer_acotado_rechaza_symlink_directorio_y_tamano(self):
        real = self.dir / "r.bin"
        real.write_bytes(b"x" * 10)
        with self.assertRaises(ps.PayloadError):
            ps.leer_acotado(self.dir)
        with self.assertRaises(ps.PayloadError):
            ps.leer_acotado(real, maximo=5)
        with self.assertRaises(ps.PayloadError):
            ps.leer_acotado(self.dir / "no_existe")
        try:
            (self.dir / "l.bin").symlink_to(real)
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(ps.PayloadError):
            ps.leer_acotado(self.dir / "l.bin")

    def correr(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = ps.main([str(a) for a in args])
        return codigo, out.getvalue(), err.getvalue()

    def test_cli_json_hash_esperado_y_no_expone_datos_internos(self):
        p = self.dir / "b.bin"
        datos = blob(cuerpo_ficticio())
        p.write_bytes(datos)
        codigo, out, _ = self.correr(p, "--esperado-sha256", hashlib.sha256(datos).hexdigest())
        self.assertEqual(codigo, 0)
        j = json.loads(out)
        self.assertNotIn("_cuerpos", j["archivo"])
        self.assertNotIn("_datos", j["archivo"]["flujos_zlib"][0])
        codigo, _, err = self.correr(p, "--esperado-sha256", "0" * 64)
        self.assertEqual(codigo, 1)
        self.assertIn("!= esperado", err)

    def test_cli_error_de_uso(self):
        self.assertEqual(self.correr(self.dir / "nada.bin")[0], 2)


if __name__ == "__main__":
    unittest.main()

"""Tests de tools/check_docs.py con árboles de documentación temporales, más una comprobación sobre la documentación real."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tools import check_docs as cd

RAIZ_REAL = Path(__file__).resolve().parent.parent
LOG = "# Registro\n\n## D-001 — Uno\n\n## D-008 — Ocho\n\n## Preguntas abiertas\n\n- **Q-001:** algo\n"
ROADMAP_OK = ("# Roadmap\n\n## Fase 1\n**Estado:** PARCIAL\n- [ ] `PENDIENTE` Algo\n- [x] `IMPLEMENTADO` Hecho\n"
              "- [ ] `BLOQUEADO` Elegir kernel según southbridge\n")


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        (self.raiz / "docs").mkdir()
        self.escribir("docs/DECISION_LOG.md", LOG)
        self.escribir("docs/ROADMAP.md", ROADMAP_OK)
        self.escribir("README.md", "# P\n[roadmap](docs/ROADMAP.md) y [ext](https://x.test/a) y [ancla](#abajo)\n")

    def tearDown(self):
        self._tmp.cleanup()

    def escribir(self, rel, texto):
        p = self.raiz / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")


class TestCheckDocs(Base):
    def test_arbol_limpio(self):
        self.assertEqual(cd.revisar(self.raiz), [])

    def test_enlace_roto(self):
        self.escribir("docs/A.md", "ver [x](NOEXISTE.md#h) y [ok](ROADMAP.md#fase)\n")
        p = cd.revisar(self.raiz)
        self.assertEqual(len(p), 1)
        self.assertIn("NOEXISTE.md", p[0])

    def test_enlaces_en_bloques_de_codigo_se_ignoran(self):
        self.escribir("docs/A.md", "```\n[x](NOEXISTE.md)\n```\n")
        self.assertEqual(cd.revisar(self.raiz), [])

    def test_imagenes_y_esquemas_no_cuentan(self):
        self.escribir("docs/A.md", "![img](no.png) [m](mailto:a@b.c) [h](http://x.test)\n")
        self.assertEqual(cd.revisar(self.raiz), [])

    def test_referencias_inexistentes(self):
        self.escribir("docs/A.md", "Ver D-008, D-099 y Q-001, Q-050.\n")
        p = cd.revisar(self.raiz)
        self.assertEqual(len(p), 2)
        self.assertTrue(any("D-099" in x for x in p))
        self.assertTrue(any("Q-050" in x for x in p))

    def test_frases_obsoletas(self):
        self.escribir("docs/A.md", "[OK] Estructura USB-only válida. Opción A (FTP) y Opción B (USB).\n")
        p = cd.revisar(self.raiz)
        self.assertGreaterEqual(len(p), 3)

    def test_casilla_sin_etiqueta(self):
        self.escribir("docs/ROADMAP.md", ROADMAP_OK + "- [x] Hecho sin etiqueta\n")
        self.assertTrue(any("sin etiqueta" in x for x in cd.revisar(self.raiz)))

    def test_hecha_con_etiqueta_pendiente(self):
        self.escribir("docs/ROADMAP.md", ROADMAP_OK + "- [x] `PENDIENTE` contradictoria\n")
        self.assertTrue(any("PENDIENTE/BLOQUEADO" in x for x in cd.revisar(self.raiz)))

    def test_fase_verified_sin_lab(self):
        self.escribir("docs/ROADMAP.md", "## Fase\n**Estado:** VERIFIED (solo documentación)\n")
        self.assertTrue(any("VERIFIED sin evidencia LAB" in x for x in cd.revisar(self.raiz)))
        self.escribir("docs/ROADMAP.md", "## Fase\n**Estado:** VERIFIED con `LAB` LAB-001\n")
        self.assertEqual(cd.revisar(self.raiz), [])

    def test_kernel_resuelto_con_southbridge_desconocido(self):
        self.escribir("docs/COMPATIBILITY_MATRIX.md", "| Southbridge | **DESCONOCIDO** |\n")
        self.escribir("docs/ROADMAP.md", ROADMAP_OK + "- [x] `IMPLEMENTADO` Elegir kernel para la consola\n")
        self.assertTrue(any("selección de kernel" in x for x in cd.revisar(self.raiz)))

    def test_kernel_resuelto_permitido_con_registro_de_laboratorio(self):
        self.escribir("docs/COMPATIBILITY_MATRIX.md", "| Southbridge | **DESCONOCIDO** |\n")
        self.escribir("docs/lab-logs/LAB-001-primer-intento.md", "# LAB-001\n")
        self.escribir("docs/ROADMAP.md", ROADMAP_OK + "- [x] `LAB` Elegir kernel para la consola\n")
        self.assertEqual(cd.revisar(self.raiz), [])

    def test_cli(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cd.main([str(self.raiz)]), 0)
        self.escribir("docs/A.md", "[x](NOEXISTE.md)\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cd.main([str(self.raiz)]), 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cd.main([str(self.raiz / "no_existe")]), 2)


class TestDocumentacionReal(unittest.TestCase):
    def test_la_documentacion_del_repositorio_es_coherente(self):
        self.assertEqual(cd.revisar(RAIZ_REAL), [])

    def test_hay_documentos_y_enlaces_que_comprobar(self):
        archivos = cd.archivos_md(RAIZ_REAL)
        self.assertGreater(len(archivos), 15)
        total = sum(len(cd.ENLACE_RE.findall(cd._sin_codigo(a.read_text(encoding="utf-8")))) for a in archivos)
        self.assertGreater(total, 30)


if __name__ == "__main__":
    unittest.main()

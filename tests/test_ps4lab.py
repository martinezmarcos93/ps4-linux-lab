import hashlib
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import http.server
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import ps4lab  # noqa: E402


def _montar(tmp, contenido=b"hola"):
    d = Path(tmp)
    (d / "a.js").write_bytes(contenido)
    (d / "secreto.txt").write_bytes(b"no listado")
    m = {"schema_version": 1,
         "artifacts": [{"path": "a.js", "size_bytes": len(contenido),
                        "sha256": hashlib.sha256(contenido).hexdigest()}]}
    (d / "m.json").write_text(json.dumps(m), encoding="utf-8")
    return d


class TestManifiesto(unittest.TestCase):
    def test_permitidos(self):
        with tempfile.TemporaryDirectory() as t:
            d = _montar(t)
            self.assertEqual(ps4lab.permitidos_desde_manifiesto(d / "m.json"), {"a.js"})

    def test_ruta_segura(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertIsNone(ps4lab.ruta_segura(t, "../x"))
            self.assertIsNotNone(ps4lab.ruta_segura(t, "a.js"))


class TestIP(unittest.TestCase):
    def test_rechaza(self):
        for ip in ("0.0.0.0", "8.8.8.8", "::"):
            with self.assertRaises(ValueError):
                ps4lab.validar_ip_privada(ip)

    def test_acepta(self):
        self.assertEqual(ps4lab.validar_ip_privada("192.168.1.69"), "192.168.1.69")


class TestServidor(unittest.TestCase):
    def test_solo_lista_blanca_y_solo_lectura(self):
        with tempfile.TemporaryDirectory() as t:
            d = _montar(t)
            h = ps4lab.crear_handler(d, {"a.js"})
            srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            base = f"http://127.0.0.1:{srv.server_address[1]}"
            try:
                self.assertEqual(urllib.request.urlopen(base + "/a.js").read(), b"hola")
                for ruta in ("/secreto.txt", "/m.json", "/../../etc/passwd", "/%2e%2e/m.json"):
                    with self.assertRaises(urllib.error.HTTPError, msg=ruta) as e:
                        urllib.request.urlopen(base + ruta)
                    self.assertEqual(e.exception.code, 404)
                r = urllib.request.urlopen(urllib.request.Request(base + "/t", data=b"x=1", method="POST"))
                self.assertEqual(r.status, 204)
                with self.assertRaises(urllib.error.HTTPError) as e:
                    urllib.request.urlopen(urllib.request.Request(base + "/a.js", data=b"x", method="PUT"))
                self.assertIn(e.exception.code, (501, 404, 405))
            finally:
                srv.shutdown()
                srv.server_close()


if __name__ == "__main__":
    unittest.main()

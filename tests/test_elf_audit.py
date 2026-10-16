"""Tests de tools/elf_audit.py con ELF64 FICTICIOS construidos en memoria. No hay binarios reales."""
import contextlib
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools import elf_audit as ea

FILAS = [
    (505, 0x1C0, 0x436040, 0x0FCC80, 0x1AC60E0, 0x0FCD48, 0x0FCD56, 0x10D97E),
    (1352, 0x1C0, 0x2E0510, 0x466290, 0x22D1D50, 0x46635C, 0x466364, 0x3A2B90),
]
FUENTE = """static fw_offsets_t fw_table[] = {
    {  505, 0x1c0,  0x436040,   0x0FCC80,   0x1AC60E0,  0x0FCD48,   0x0FCD56,   0x10D97E  },
    { 1352, 0x1c0,  0x2E0510,   0x466290,   0x22D1D50,  0x46635C,   0x466364,   0x3A2B90  },
    { 0 }   /* sentinel */
};"""


def tabla(filas) -> bytes:
    salida = b""
    for f in filas:
        salida += struct.pack("<H6x7Q", *f)
    return salida + b"\0" * ea.FILA


def hacer_elf(filas=FILAS, rodata=b"\0/mnt/usb0/bzImage\0/data/linux/boot/bzImage\0", extra_text=b"\x90" * 16,
              con_data=True) -> bytes:
    nombres = b"\0.text\0.rodata\0.data\0.shstrtab\0"

    def idx(n: bytes) -> int:
        return nombres.index(b"\0" + n + b"\0") + 1

    cuerpos = [(".text", 1, extra_text), (".rodata", 1, rodata)]
    if con_data:
        cuerpos.append((".data", 1, tabla(filas)))
    datos = bytearray(b"\0" * 64)
    cab = [(0, 0, 0, 0)]
    for n, tipo, c in cuerpos:
        cab.append((idx(n.encode()), tipo, len(datos), len(c)))
        datos += c
    cab.append((idx(b".shstrtab"), 3, len(datos), len(nombres)))
    datos += nombres
    shoff = len(datos)
    for nombre, tipo, off, size in cab:
        datos += struct.pack("<IIQQQQIIQQ", nombre, tipo, 0, 0, off, size, 0, 0, 1, 0)
    datos[0:4] = b"\x7fELF"
    datos[4], datos[5], datos[6] = 2, 1, 1
    struct.pack_into("<Q", datos, 0x28, shoff)
    struct.pack_into("<HHH", datos, 0x3A, 64, len(cab), len(cab) - 1)
    return bytes(datos)


class TestElfAudit(unittest.TestCase):
    def test_secciones(self):
        sec = ea.secciones(hacer_elf())
        self.assertEqual(set(sec) - {""}, {".text", ".rodata", ".data", ".shstrtab"})

    def test_rechaza_no_elf_y_truncados(self):
        for malo in (b"", b"MZ" + b"\0" * 100, b"\x7fELF\x01\x01" + b"\0" * 100):
            with self.assertRaises(ea.ElfError):
                ea.secciones(malo)
        elf = hacer_elf()
        with self.assertRaises(ea.ElfError):
            ea.secciones(elf[: len(elf) - 70])

    def test_seccion_fuera_de_limites(self):
        elf = bytearray(hacer_elf())
        shoff, = struct.unpack_from("<Q", elf, 0x28)
        # agranda el tamaño de la sección 1 más allá del archivo
        struct.pack_into("<Q", elf, shoff + 64 + 32, 10_000_000)
        with self.assertRaises(ea.ElfError):
            ea.secciones(bytes(elf))

    def test_leer_fw_table(self):
        self.assertEqual(ea.leer_fw_table(hacer_elf()), FILAS)

    def test_sin_data(self):
        with self.assertRaises(ea.ElfError):
            ea.leer_fw_table(hacer_elf(con_data=False))

    def test_fuente_y_comparacion_coinciden(self):
        src = ea.leer_fw_table_fuente(FUENTE)
        self.assertEqual(src, FILAS)
        self.assertEqual(ea.comparar_tablas(ea.leer_fw_table(hacer_elf()), src), [])

    def test_comparacion_detecta_fila_alterada_y_faltante(self):
        alterada = [FILAS[0], FILAS[1][:3] + (0xDEAD,) + FILAS[1][4:]]
        errores = ea.comparar_tablas(ea.leer_fw_table(hacer_elf(alterada)), ea.leer_fw_table_fuente(FUENTE))
        self.assertTrue(any("1352" in e for e in errores))
        errores = ea.comparar_tablas(ea.leer_fw_table(hacer_elf(FILAS[:1])), ea.leer_fw_table_fuente(FUENTE))
        self.assertTrue(any("número de filas" in e for e in errores))

    def test_rutas_literales(self):
        self.assertEqual(ea.rutas_literales(hacer_elf()), ["/data/linux/boot/bzImage", "/mnt/usb0/bzImage"])
        self.assertEqual(ea.rutas_literales(hacer_elf(rodata=b"\0solo texto\0")), [])

    def test_diferencias_por_seccion(self):
        a = hacer_elf(extra_text=b"\x90" * 16)
        b = hacer_elf(extra_text=b"\x90" * 15 + b"\xcc")
        r = ea.diferencias(a, b)
        self.assertEqual(r, {"mismo_tamano": True, "bytes_distintos": 1, "por_seccion": {".text": 1}})
        self.assertFalse(ea.diferencias(a, b + b"\0")["mismo_tamano"])
        self.assertEqual(ea.diferencias(a, a)["bytes_distintos"], 0)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "a.elf").write_bytes(hacer_elf())
            (d / "fw.h").write_text(FUENTE, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(ea.main([str(d / "a.elf"), "--fuente", str(d / "fw.h")]), 0)
            self.assertTrue(json.loads(out.getvalue())["tabla_coincide_con_fuente"])
            (d / "fw2.h").write_text(FUENTE.replace("0x46635C", "0x46635D"), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ea.main([str(d / "a.elf"), "--fuente", str(d / "fw2.h")]), 1)
                self.assertEqual(ea.main([str(d / "no_existe")]), 2)


if __name__ == "__main__":
    unittest.main()

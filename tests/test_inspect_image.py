import os
import struct
import tempfile
import unittest
import uuid
import zlib
from pathlib import Path
from unittest import mock

from tools import inspect_image as ii

SECTOR = 512


def mbr_entry(status, ptype, lba, count):
    return struct.pack("<B3sB3sII", status, b"\0\0\0", ptype, b"\0\0\0", lba, count)


def make_mbr_image(entries, total_sectors, signature=b"\x55\xaa"):
    img = bytearray(total_sectors * SECTOR)
    for i, e in enumerate(entries):
        img[446 + 16 * i: 462 + 16 * i] = e
    img[510:512] = signature
    return img


def make_gpt_image(total_sectors, parts, bad_header_crc=False, bad_table_crc=False):
    """parts: lista de (first_lba, last_lba, nombre)."""
    img = bytearray(total_sectors * SECTOR)
    img[446:462] = mbr_entry(0, 0xEE, 1, min(total_sectors - 1, 0xFFFFFFFF))
    img[510:512] = b"\x55\xaa"
    n, esz = 128, 128
    table = bytearray(n * esz)
    for i, (first, last, name) in enumerate(parts):
        e = bytearray(esz)
        e[:16] = uuid.UUID("0fc63daf-8483-4772-8e79-3d69d8477de4").bytes_le
        e[16:32] = uuid.uuid4().bytes_le
        struct.pack_into("<QQ", e, 32, first, last)
        e[56:56 + 2 * len(name)] = name.encode("utf-16-le")
        table[i * esz:(i + 1) * esz] = e
    tcrc = zlib.crc32(bytes(table)) ^ (1 if bad_table_crc else 0)
    hdr = bytearray(92)
    hdr[:8] = b"EFI PART"
    struct.pack_into("<IIIIQQQQ16sQIII", hdr, 8, 0x00010000, 92, 0, 0, 1, total_sectors - 1,
                     34, total_sectors - 34, uuid.uuid4().bytes_le, 2, n, esz, tcrc)
    crc = zlib.crc32(bytes(hdr)) ^ (1 if bad_header_crc else 0)
    struct.pack_into("<I", hdr, 16, crc)
    img[SECTOR:SECTOR + 92] = hdr
    img[2 * SECTOR:2 * SECTOR + len(table)] = table
    return img


class InspectImageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data, name="img"):
        p = self.dir / name
        p.write_bytes(bytes(data))
        return str(p)

    def test_empty_image(self):
        r = ii.inspect_image(self.write(b""))
        self.assertEqual((r["tabla"], r["tamano_bytes"]), ("ninguna", 0))
        self.assertIn("imagen vacía", r["advertencias"])

    def test_smaller_than_sector(self):
        r = ii.inspect_image(self.write(b"x" * 100))
        self.assertEqual(r["tabla"], "ninguna")
        self.assertTrue(r["advertencias"])

    def test_no_signature(self):
        r = ii.inspect_image(self.write(bytes(4 * SECTOR)))
        self.assertEqual(r["tabla"], "ninguna")
        self.assertTrue(any("sin firma" in w for w in r["advertencias"]))

    def test_valid_mbr(self):
        img = make_mbr_image([mbr_entry(0x80, 0x0C, 2048, 100), mbr_entry(0, 0x83, 4096, 100)], 8192)
        r = ii.inspect_image(self.write(img))
        self.assertEqual(r["tabla"], "mbr")
        self.assertEqual([p["tipo"] for p in r["particiones"]], ["0x0c", "0x83"])
        self.assertEqual(r["advertencias"], [])

    def test_mbr_overlap_detected(self):
        img = make_mbr_image([mbr_entry(0, 0x83, 2048, 1000), mbr_entry(0, 0x83, 2500, 1000)], 8192)
        r = ii.inspect_image(self.write(img))
        self.assertTrue(any("se solapan" in w for w in r["advertencias"]))

    def test_mbr_truncated_image(self):
        img = make_mbr_image([mbr_entry(0, 0x83, 2048, 100000)], 4096)
        r = ii.inspect_image(self.write(img))
        self.assertTrue(any("más allá del final" in w for w in r["advertencias"]))

    def test_mbr_bad_status_byte(self):
        img = make_mbr_image([mbr_entry(0x13, 0x83, 2048, 100)], 4096)
        r = ii.inspect_image(self.write(img))
        self.assertTrue(any("estado inválido" in w for w in r["advertencias"]))

    def test_size_not_multiple_of_sector(self):
        img = make_mbr_image([mbr_entry(0, 0x83, 2048, 1)], 4096) + b"x"
        r = ii.inspect_image(self.write(img))
        self.assertTrue(any("no múltiplo" in w for w in r["advertencias"]))

    def test_valid_gpt(self):
        img = make_gpt_image(4096, [(2048, 3000, "datos")])
        r = ii.inspect_image(self.write(img))
        self.assertEqual(r["tabla"], "gpt")
        self.assertEqual(r["particiones"][0]["nombre"], "datos")
        self.assertEqual(r["advertencias"], [])

    def test_gpt_bad_header_crc(self):
        r = ii.inspect_image(self.write(make_gpt_image(4096, [(2048, 3000, "a")], bad_header_crc=True)))
        self.assertTrue(any("CRC32 de la cabecera" in w for w in r["advertencias"]))

    def test_gpt_bad_table_crc(self):
        r = ii.inspect_image(self.write(make_gpt_image(4096, [(2048, 3000, "a")], bad_table_crc=True)))
        self.assertTrue(any("CRC32 de la tabla" in w for w in r["advertencias"]))

    def test_gpt_partition_beyond_image(self):
        r = ii.inspect_image(self.write(make_gpt_image(4096, [(2048, 99999, "a")])))
        self.assertTrue(any("más allá del final" in w for w in r["advertencias"]))

    def test_gpt_truncated_before_table(self):
        img = make_gpt_image(4096, [(2048, 3000, "a")])[: 2 * SECTOR + 100]
        r = ii.inspect_image(self.write(img))
        self.assertEqual(r["tabla"], "gpt")
        self.assertTrue(any("truncada" in w for w in r["advertencias"]))

    def test_gpt_absurd_entry_count_not_read(self):
        img = make_gpt_image(4096, [(2048, 3000, "a")])
        struct.pack_into("<I", img, SECTOR + 80, 4_000_000_000)
        r = ii.inspect_image(self.write(img))
        self.assertEqual(r["particiones"], [])
        self.assertTrue(any("inválida" in w for w in r["advertencias"]))

    def test_gpt_without_protective_mbr_warns(self):
        img = make_gpt_image(4096, [(2048, 3000, "a")])
        img[446:462] = bytes(16)
        r = ii.inspect_image(self.write(img))
        self.assertTrue(any("protector" in w for w in r["advertencias"]))

    def test_protective_mbr_without_gpt_warns(self):
        img = make_mbr_image([mbr_entry(0, 0xEE, 1, 100)], 4096)
        r = ii.inspect_image(self.write(img))
        self.assertTrue(any("0xEE" in w for w in r["advertencias"]))

    def test_filesystem_hints(self):
        img = make_mbr_image([mbr_entry(0, 0x0C, 8, 8), mbr_entry(0, 0x83, 16, 16)], 64)
        img[8 * SECTOR + 82: 8 * SECTOR + 90] = b"FAT32   "
        img[8 * SECTOR + 510: 8 * SECTOR + 512] = b"\x55\xaa"
        struct.pack_into("<H", img, 16 * SECTOR + 1024 + 56, 0xEF53)
        r = ii.inspect_image(self.write(img))
        self.assertIn("FAT32", r["particiones"][0]["fs_hint"])
        self.assertIn("ext", r["particiones"][1]["fs_hint"])

    def test_does_not_modify_file(self):
        p = self.write(make_gpt_image(4096, [(2048, 3000, "a")]))
        before = (os.stat(p).st_mtime_ns, Path(p).read_bytes())
        ii.inspect_image(p)
        self.assertEqual((os.stat(p).st_mtime_ns, Path(p).read_bytes()), before)

    def test_readonly_file_is_fine(self):
        p = self.write(make_mbr_image([], 8))
        os.chmod(p, 0o400)
        self.assertEqual(ii.inspect_image(p)["tabla"], "mbr")

    def test_rejects_directory(self):
        with self.assertRaises(ii.ImageError):
            ii.inspect_image(str(self.dir))

    def test_rejects_symlink(self):
        p = self.write(b"x" * 1024)
        link = self.dir / "link"
        os.symlink(p, link)
        with self.assertRaises(ii.ImageError):
            ii.inspect_image(str(link))

    def test_fstat_failure_no_deja_pasar_oserror_sin_convertir(self):
        # Regresión: _open_regular puede filtrar un OSError crudo si fstat()
        # falla después de abrir (ventana entre lstat y fstat). inspect_image()
        # y main() deben tratarlo como un error limpio, no una traza sin manejar.
        p = self.write(make_mbr_image([], 8))
        with mock.patch("os.fstat", side_effect=OSError("fallo simulado de fstat")):
            with self.assertRaises(ii.ImageError):
                ii.inspect_image(p)
            self.assertEqual(ii.main([p]), 2)

    def test_rejects_device_and_fifo(self):
        with self.assertRaises(ii.ImageError):
            ii.inspect_image("/dev/null")
        fifo = self.dir / "fifo"
        os.mkfifo(fifo)
        with self.assertRaises(ii.ImageError):
            ii.inspect_image(str(fifo))

    def test_rejects_missing_empty_and_nul(self):
        for bad in (str(self.dir / "nope"), "", "a\x00b"):
            with self.assertRaises(ii.ImageError, msg=repr(bad)):
                ii.inspect_image(bad)

    def test_exit_codes(self):
        ok = self.write(make_mbr_image([mbr_entry(0, 0x83, 8, 8)], 64), "ok")
        bad = self.write(b"", "bad")
        self.assertEqual(ii.main([ok]), 0)
        self.assertEqual(ii.main([bad]), 1)
        self.assertEqual(ii.main([str(self.dir / "nada")]), 2)


if __name__ == "__main__":
    unittest.main()

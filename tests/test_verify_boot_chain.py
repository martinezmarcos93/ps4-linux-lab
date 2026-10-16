import os
import tempfile
import unittest
from pathlib import Path
from tools.verify_boot_chain import verify_boot_layout, BootChainError

class TestVerifyBootChain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.boot_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_bzimage(self):
        (self.boot_dir / "initramfs.cpio.gz").write_bytes(b"dummy initramfs")
        res = verify_boot_layout(self.boot_dir)
        self.assertFalse(res["valid_usb_only"])
        self.assertTrue(any("Falta bzImage" in e for e in res["errors"]))

    def test_missing_initramfs(self):
        (self.boot_dir / "bzImage").write_bytes(b"dummy kernel")
        res = verify_boot_layout(self.boot_dir)
        self.assertFalse(res["valid_usb_only"])
        self.assertTrue(any("Falta initramfs.cpio.gz" in e for e in res["errors"]))

    def test_valid_layout(self):
        (self.boot_dir / "bzImage").write_bytes(b"dummy kernel")
        (self.boot_dir / "initramfs.cpio.gz").write_bytes(b"dummy initramfs")
        res = verify_boot_layout(self.boot_dir)
        self.assertTrue(res["valid_usb_only"])
        self.assertEqual(len(res["errors"]), 0)

    def test_warns_on_renamed_kernels_without_main(self):
        (self.boot_dir / "bzImage.belize").write_bytes(b"dummy kernel")
        (self.boot_dir / "bzImage.baikal").write_bytes(b"dummy kernel")
        (self.boot_dir / "initramfs.cpio.gz").write_bytes(b"dummy initramfs")
        res = verify_boot_layout(self.boot_dir)
        self.assertFalse(res["valid_usb_only"])
        self.assertTrue(any("bzImage.belize" in w for w in res["warnings"]))
        self.assertTrue(any("bzImage.baikal" in w for w in res["warnings"]))

    def test_invalid_directory(self):
        with self.assertRaises(BootChainError):
            verify_boot_layout(self.boot_dir / "non_existent")

    def test_rejects_directory_as_file(self):
        (self.boot_dir / "bzImage").mkdir()
        (self.boot_dir / "initramfs.cpio.gz").write_bytes(b"dummy initramfs")
        res = verify_boot_layout(self.boot_dir)
        self.assertFalse(res["valid_usb_only"])
        self.assertTrue(any("debe ser un archivo regular" in e for e in res["errors"]))

    def test_rejects_symlink(self):
        target = self.boot_dir / "target_kernel"
        target.write_bytes(b"dummy kernel")
        link = self.boot_dir / "bzImage"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks no soportados")
        (self.boot_dir / "initramfs.cpio.gz").write_bytes(b"dummy initramfs")
        res = verify_boot_layout(self.boot_dir)
        self.assertFalse(res["valid_usb_only"])
        self.assertTrue(any("no debe ser un enlace simbólico" in e for e in res["errors"]))

    def test_optional_files(self):
        (self.boot_dir / "bzImage").write_bytes(b"dummy kernel")
        (self.boot_dir / "initramfs.cpio.gz").write_bytes(b"dummy initramfs")
        (self.boot_dir / "bootargs.txt").write_bytes(b"panic=0")
        (self.boot_dir / "vram.txt").write_bytes(b"1024")
        res = verify_boot_layout(self.boot_dir)
        self.assertTrue(res["valid_usb_only"])
        self.assertEqual(len(res["errors"]), 0)

if __name__ == "__main__":
    unittest.main()

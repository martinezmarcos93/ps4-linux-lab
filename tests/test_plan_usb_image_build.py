import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.plan_usb_image_build import PreflightError, REQUIRED_COMMANDS, build_plan


class PlanUsbImageBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.rootfs = self.root / "rootfs.tar.xz"
        self.initramfs = self.root / "initramfs.cpio.gz"
        self.output = self.root / "out.img"
        self.rootfs.write_bytes(b"dummy archive bytes")
        self.initramfs.write_bytes(b"dummy initramfs bytes")

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, **kwargs):
        defaults = {
            "rootfs_archive": str(self.rootfs),
            "initramfs": str(self.initramfs),
            "output": str(self.output),
            "image_size_bytes": 1024,
            "temp_dir": str(self.root),
        }
        defaults.update(kwargs)
        with patch("tools.plan_usb_image_build.shutil.disk_usage") as usage, patch(
            "tools.plan_usb_image_build.shutil.which", return_value="/usr/bin/fake"
        ):
            usage.return_value.free = 10**12
            return build_plan(**defaults)

    def test_valid_inputs_produce_read_only_plan(self):
        plan = self.plan()
        self.assertEqual(plan["mode"], "preflight-only")
        self.assertFalse(plan["side_effects"])
        self.assertTrue(plan["ready_for_build"])
        self.assertFalse(self.output.exists())

    def test_missing_input_is_rejected(self):
        with self.assertRaises(PreflightError):
            self.plan(rootfs_archive=str(self.root / "missing.tar.xz"))

    def test_directory_is_not_accepted_as_input(self):
        with self.assertRaises(PreflightError):
            self.plan(rootfs_archive=str(self.root))

    def test_symlink_input_is_rejected(self):
        link = self.root / "rootfs-link.tar.xz"
        try:
            link.symlink_to(self.rootfs)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(PreflightError):
            self.plan(rootfs_archive=str(link))

    def test_existing_output_is_never_overwritten(self):
        self.output.write_bytes(b"keep me")
        with self.assertRaises(PreflightError):
            self.plan()
        self.assertEqual(self.output.read_bytes(), b"keep me")

    def test_duplicate_inputs_are_rejected(self):
        with self.assertRaises(PreflightError):
            self.plan(initramfs=str(self.rootfs))

    def test_nonpositive_image_size_is_rejected(self):
        with self.assertRaises(PreflightError):
            self.plan(image_size_bytes=0)

    def test_missing_commands_mark_plan_not_ready(self):
        with patch("tools.plan_usb_image_build.shutil.which", return_value=None), patch(
            "tools.plan_usb_image_build.shutil.disk_usage"
        ) as usage:
            usage.return_value.free = 10**12
            plan = build_plan(
                str(self.rootfs), str(self.initramfs), str(self.output),
                image_size_bytes=1024, temp_dir=str(self.root),
            )
        self.assertEqual(plan["missing_commands"], list(REQUIRED_COMMANDS))
        self.assertFalse(plan["ready_for_build"])

    def test_insufficient_space_fails_preflight(self):
        with patch("tools.plan_usb_image_build.shutil.disk_usage") as usage, patch(
            "tools.plan_usb_image_build.shutil.which", return_value="/usr/bin/fake"
        ):
            usage.return_value.free = 0
            with self.assertRaises(PreflightError):
                build_plan(
                    str(self.rootfs), str(self.initramfs), str(self.output),
                    image_size_bytes=1024, temp_dir=str(self.root),
                )

    def test_symlink_output_is_rejected(self):
        link = self.root / "out-link.img"
        try:
            link.symlink_to(self.rootfs)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(PreflightError):
            self.plan(output=str(link))


    def test_output_under_system_paths_is_refused(self):
        for target in ("/dev/shm/x.img", "/etc/x.img", "/usr/x.img", "/proc/x.img"):
            with self.assertRaises(PreflightError, msg=target):
                self.plan(output=target)

    def test_output_in_filesystem_root_is_refused(self):
        with self.assertRaises(PreflightError):
            self.plan(output="/x.img")

    def test_output_symlinked_parent_into_system_path_is_refused(self):
        link = self.root / "enlace"
        try:
            link.symlink_to("/dev")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not supported")
        with self.assertRaises(PreflightError):
            self.plan(output=str(link / "x.img"))


if __name__ == "__main__":
    unittest.main()

"""Static contract tests for the sequential loader hardening patch.

These tests validate the patch text only. They do not compile upstream C and
must never be described as proving the loader works on a PS4.
"""
import re
import unittest
from pathlib import Path


PATCH = Path(__file__).resolve().parents[1] / "patches" / "loader-read-file-hardening-f70f43a.patch"


class TestLoaderReadFileHardeningPatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PATCH.read_text(encoding="utf-8")

    def test_patch_has_well_formed_unified_hunk_counts(self):
        lines = self.text.splitlines()
        hunks = []
        current = None
        for line in lines:
            match = re.match(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@", line)
            if match:
                current = {
                    "old_expected": int(match.group(2)),
                    "new_expected": int(match.group(4)),
                    "old": 0,
                    "new": 0,
                }
                hunks.append(current)
                continue
            if current is None:
                continue
            if line.startswith("+") and not line.startswith("+++ "):
                current["new"] += 1
            elif line.startswith("-") and not line.startswith("--- "):
                current["old"] += 1
            elif line.startswith(" "):
                current["old"] += 1
                current["new"] += 1
            elif line == "\\ No newline at end of file":
                continue
            elif line == "":
                # Blank lines in the mail header / between hunks are not diff context.
                continue
            else:
                # A raw source line inside a hunk is malformed: diff lines must
                # be prefixed by space, +, or -.
                if hunks and (hunks[-1]["old"] < hunks[-1]["old_expected"]
                              or hunks[-1]["new"] < hunks[-1]["new_expected"]):
                    self.fail(f"malformed raw line inside unified diff: {line!r}")
        for hunk in hunks:
            self.assertEqual(hunk["old"], hunk["old_expected"])
            self.assertEqual(hunk["new"], hunk["new_expected"])

    def test_reader_checks_seek_mapping_and_partial_reads(self):
        for token in (
            "end = lseek(fd, 0, SEEK_END);",
            "if (end <= 0)",
            "if (buffer == MAP_FAILED)",
            "if (lseek(fd, 0, SEEK_SET) != 0)",
            "if (got <= 0)",
            "munmap(buffer, (size_t)end);",
            "*ptr = NULL;",
            "*sz = 0;",
        ):
            self.assertIn(token, self.text)

    def test_candidate_does_not_load_optional_config(self):
        self.assertNotIn('load_from(boot_dir, "bootargs.txt"', self.text)
        self.assertNotIn('load_from(boot_dir, "vram.txt"', self.text)
        self.assertIn("do not load bootargs.txt or vram.txt", self.text)
        self.assertIn("host preflight rejects these files", self.text)

    def test_reads_are_bounded_and_no_internal_fallback_is_added(self):
        self.assertIn("remaining > 1048576ULL", self.text)
        self.assertNotIn('"/data/linux/boot/"', self.text)
        self.assertNotIn('"/user/system/boot/"', self.text)


if __name__ == "__main__":
    unittest.main()

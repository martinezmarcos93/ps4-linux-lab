import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.verify_artifacts import ManifestError, verify_manifest


class VerifyArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "files").mkdir()
        self.manifest_path = self.root / "manifest.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_manifest(self, artifacts, schema_version=1):
        self.manifest_path.write_text(
            json.dumps({"schema_version": schema_version, "artifacts": artifacts}),
            encoding="utf-8",
        )

    def artifact(self, path, data, size=True):
        return {
            "path": path,
            "sha256": hashlib.sha256(data).hexdigest(),
            **({"size_bytes": len(data)} if size else {}),
        }

    def test_valid_file_passes(self):
        data = b"PS4 Linux lab\x00"
        (self.root / "files" / "sample.bin").write_bytes(data)
        self.write_manifest([self.artifact("files/sample.bin", data)])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 0)
        self.assertEqual(results[0]["status"], "PASS")

    def test_empty_file_passes_when_hash_matches(self):
        data = b""
        (self.root / "files" / "empty.bin").write_bytes(data)
        self.write_manifest([self.artifact("files/empty.bin", data)])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 0)
        self.assertEqual(results[0]["size_bytes"], 0)

    def test_hash_mismatch_fails(self):
        (self.root / "files" / "sample.bin").write_bytes(b"actual")
        self.write_manifest([{"path": "files/sample.bin", "sha256": "0" * 64}])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 1)
        self.assertEqual(results[0]["message"], "SHA-256 mismatch")

    def test_size_mismatch_fails(self):
        (self.root / "files" / "sample.bin").write_bytes(b"abc")
        self.write_manifest([{"path": "files/sample.bin", "sha256": hashlib.sha256(b"abc").hexdigest(), "size_bytes": 4}])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 1)
        self.assertIn("size mismatch", results[0]["message"])

    def test_missing_file_fails(self):
        self.write_manifest([{"path": "files/missing.bin", "sha256": "0" * 64}])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 1)
        self.assertEqual(results[0]["status"], "FAIL")

    def test_parent_traversal_rejected(self):
        self.write_manifest([{"path": "../outside.bin", "sha256": "0" * 64}])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_absolute_path_rejected(self):
        self.write_manifest([{"path": "/etc/passwd", "sha256": "0" * 64}])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_invalid_hash_rejected(self):
        self.write_manifest([{"path": "files/sample.bin", "sha256": "xyz"}])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_empty_artifact_list_rejected(self):
        self.write_manifest([])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_invalid_json_rejected(self):
        self.manifest_path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_symlink_rejected(self):
        target = self.root / "files" / "target.bin"
        target.write_bytes(b"safe")
        link = self.root / "files" / "link.bin"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this platform")
        self.write_manifest([self.artifact("files/link.bin", b"safe")])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 1)
        self.assertIn("symlink", results[0]["message"])


if __name__ == "__main__":
    unittest.main()


class VerifyArtifactsAdversarialTests(VerifyArtifactsTests):
    """Regresiones de entradas hostiles (hallazgos de la revisión 2026-10-15)."""

    def test_schema_version_true_rejected(self):
        self.write_manifest([self.artifact("files/a", b"x")], schema_version=True)
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_schema_version_float_and_string_rejected(self):
        for bad in (1.0, "1"):
            self.write_manifest([self.artifact("files/a", b"x")], schema_version=bad)
            with self.assertRaises(ManifestError, msg=repr(bad)):
                verify_manifest(self.manifest_path, self.root)

    def test_nul_byte_in_path_rejected(self):
        self.write_manifest([self.artifact("files/a\x00b", b"x")])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_duplicate_paths_rejected(self):
        (self.root / "files" / "a").write_bytes(b"x")
        entry = self.artifact("files/a", b"x")
        self.write_manifest([entry, dict(entry)])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_duplicate_paths_equivalent_spelling_rejected(self):
        (self.root / "files" / "a").write_bytes(b"x")
        self.write_manifest([self.artifact("files/a", b"x"), self.artifact("files//a", b"x")])
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_deeply_nested_json_is_manifest_error_not_crash(self):
        self.manifest_path.write_bytes(b"[" * 100000)
        with self.assertRaises(ManifestError):
            verify_manifest(self.manifest_path, self.root)

    def test_overlong_filename_fails_cleanly(self):
        self.write_manifest([self.artifact("files/" + "ñ" * 300, b"x")])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual(code, 1)
        self.assertEqual(results[0]["status"], "FAIL")

    def test_directory_is_not_a_regular_file(self):
        (self.root / "files" / "d").mkdir()
        self.write_manifest([self.artifact("files/d", b"x")])
        results, code = verify_manifest(self.manifest_path, self.root)
        self.assertEqual((code, results[0]["message"]), (1, "not a regular file"))

    def test_uppercase_sha256_accepted(self):
        (self.root / "files" / "a").write_bytes(b"x")
        entry = self.artifact("files/a", b"x")
        entry["sha256"] = entry["sha256"].upper()
        self.write_manifest([entry])
        self.assertEqual(verify_manifest(self.manifest_path, self.root)[1], 0)

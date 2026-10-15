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

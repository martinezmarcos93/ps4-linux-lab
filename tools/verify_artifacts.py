#!/usr/bin/env python3
"""Read-only SHA-256 and size verifier for a JSON artifact manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
CHUNK_SIZE = 1024 * 1024


class ManifestError(ValueError):
    """Raised when the manifest is malformed or unsafe."""


def _validate_manifest(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be a JSON object")
    version = data.get("schema_version")
    if type(version) is not int or version != 1:  # excluye True, 1.0 y "1"
        raise ManifestError("schema_version must be the integer 1")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ManifestError("artifacts must be a non-empty array")

    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise ManifestError(f"{prefix} must be an object")
        path_value = artifact.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            raise ManifestError(f"{prefix}.path must be a non-empty string")
        if "\x00" in path_value:
            raise ManifestError(f"{prefix}.path must not contain NUL bytes")
        if "\\" in path_value:
            raise ManifestError(f"{prefix}.path must use POSIX separators")
        rel_path = PurePosixPath(path_value)
        if rel_path.is_absolute() or any(part in ("", ".", "..") for part in rel_path.parts):
            raise ManifestError(f"{prefix}.path must be a safe relative path")
        normalized = rel_path.as_posix()
        if normalized in seen:
            raise ManifestError(f"{prefix}.path duplicates another artifact: {normalized}")
        seen.add(normalized)
        expected_hash = artifact.get("sha256")
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
            raise ManifestError(f"{prefix}.sha256 must contain 64 hexadecimal characters")
        if "size_bytes" in artifact:
            size = artifact["size_bytes"]
            if isinstance(size, bool) or not isinstance(size, int) or size < 0:
                raise ManifestError(f"{prefix}.size_bytes must be a non-negative integer")
    return artifacts


def verify_manifest(manifest_path: Path, root: Path | None = None) -> tuple[list[dict[str, Any]], int]:
    """Verify manifest artifacts without modifying any file or device."""
    manifest_path = manifest_path.expanduser().resolve()
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestError(f"cannot read manifest: {exc}") from exc
    except UnicodeError as exc:
        raise ManifestError("manifest is not valid UTF-8") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    except RecursionError as exc:
        raise ManifestError("JSON nesting is too deep") from exc

    artifacts = _validate_manifest(data)
    root_path = (root if root is not None else manifest_path.parent).expanduser().resolve()
    if not root_path.is_dir():
        raise ManifestError("root must be an existing directory")

    results: list[dict[str, Any]] = []
    for artifact in artifacts:
        relative = PurePosixPath(artifact["path"])
        candidate = root_path.joinpath(*relative.parts)
        cursor = root_path
        has_symlink = False
        try:
            for part in relative.parts:
                cursor = cursor / part
                if cursor.is_symlink():
                    has_symlink = True
                    break
            resolved = candidate.resolve(strict=False)
        except (OSError, ValueError) as exc:
            reason = getattr(exc, "strerror", None) or str(exc)
            results.append({"status": "FAIL", "path": artifact["path"], "message": f"cannot inspect path: {reason}"})
            continue
        try:
            resolved.relative_to(root_path)
        except ValueError:
            results.append({"status": "FAIL", "path": artifact["path"], "message": "path escapes root"})
            continue
        if has_symlink:
            results.append({"status": "FAIL", "path": artifact["path"], "message": "symlink paths are not allowed"})
            continue
        try:
            info = candidate.stat()
        except OSError as exc:
            results.append({"status": "FAIL", "path": artifact["path"], "message": f"cannot stat file: {exc.strerror or exc}"})
            continue
        if not stat.S_ISREG(info.st_mode):
            results.append({"status": "FAIL", "path": artifact["path"], "message": "not a regular file"})
            continue
        if "size_bytes" in artifact and info.st_size != artifact["size_bytes"]:
            results.append({
                "status": "FAIL", "path": artifact["path"],
                "message": f"size mismatch: expected {artifact['size_bytes']}, got {info.st_size}",
                "size_bytes": info.st_size,
            })
            continue
        digest = hashlib.sha256()
        try:
            with candidate.open("rb") as stream:
                for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                    digest.update(chunk)
        except OSError as exc:
            results.append({"status": "FAIL", "path": artifact["path"], "message": f"cannot read file: {exc.strerror or exc}"})
            continue
        actual_hash = digest.hexdigest()
        if actual_hash.lower() != artifact["sha256"].lower():
            results.append({
                "status": "FAIL", "path": artifact["path"],
                "message": "SHA-256 mismatch", "sha256": actual_hash,
                "size_bytes": info.st_size,
            })
            continue
        results.append({
            "status": "PASS", "path": artifact["path"],
            "message": "size and SHA-256 verified", "sha256": actual_hash,
            "size_bytes": info.st_size,
        })
    return results, (0 if all(item["status"] == "PASS" for item in results) else 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="path to a JSON manifest")
    parser.add_argument("--root", type=Path, help="base directory for artifact paths (default: manifest directory)")
    args = parser.parse_args(argv)
    try:
        results, exit_code = verify_manifest(args.manifest, args.root)
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for item in results:
        suffix = f" sha256={item['sha256']} size={item['size_bytes']}" if "sha256" in item else ""
        print(f"[{item['status']}] {item['path']}: {item['message']}{suffix}")
    passed = sum(item["status"] == "PASS" for item in results)
    failed = len(results) - passed
    print(f"Summary: {passed} passed, {failed} failed")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

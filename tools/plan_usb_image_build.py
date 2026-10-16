#!/usr/bin/env python3
"""Read-only preflight planner for a future PS4 Linux image builder.

This tool never creates images, mounts filesystems, invokes privileged commands,
or writes to block devices. It validates paths and emits a JSON build plan only.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Sequence

DEFAULT_IMAGE_SIZE = 12 * 1024**3
REQUIRED_COMMANDS = ("sfdisk", "losetup", "mkfs.vfat", "mkfs.ext4", "mount", "umount", "tar", "e2fsck", "blkid")


class PreflightError(ValueError):
    """Raised when the proposed build cannot safely proceed."""


def _input_file(value: str, label: str) -> Path:
    raw = Path(value).expanduser()
    if raw.is_symlink():
        raise PreflightError(f"{label}: symbolic links are not accepted: {raw}")
    try:
        resolved = raw.resolve(strict=True)
        info = resolved.stat()
    except (OSError, RuntimeError) as exc:
        raise PreflightError(f"{label}: cannot resolve input: {exc}") from exc
    if not stat.S_ISREG(info.st_mode):
        raise PreflightError(f"{label}: expected a regular file: {resolved}")
    if not os.access(resolved, os.R_OK):
        raise PreflightError(f"{label}: file is not readable: {resolved}")
    return resolved


def _output_path(value: str) -> Path:
    raw = Path(value).expanduser()
    if raw.exists() or raw.is_symlink():
        raise PreflightError(f"output already exists; choose a new path (preflight never overwrites): {raw}")
    parent = raw.parent.resolve(strict=True)
    if not parent.is_dir():
        raise PreflightError(f"output parent is not a directory: {parent}")
    if not raw.name or raw.name in (".", ".."):
        raise PreflightError("output must name a file")
    return parent / raw.name


def build_plan(
    rootfs_archive: str,
    initramfs: str,
    output: str,
    spare_kernels: Sequence[str] = (),
    image_size_bytes: int = DEFAULT_IMAGE_SIZE,
    temp_dir: str | None = None,
) -> dict:
    """Validate inputs and return a JSON-serializable plan without side effects."""
    if type(image_size_bytes) is not int or image_size_bytes <= 0:
        raise PreflightError("image size must be a positive integer number of bytes")

    rootfs = _input_file(rootfs_archive, "rootfs archive")
    initrd = _input_file(initramfs, "initramfs")
    kernels = [_input_file(item, f"spare kernel #{i + 1}") for i, item in enumerate(spare_kernels)]
    destination = _output_path(output)

    inputs = [rootfs, initrd, *kernels]
    if len({str(path) for path in inputs}) != len(inputs):
        raise PreflightError("the same input file was supplied more than once")
    if destination in inputs:
        raise PreflightError("output path collides with an input")

    temporary = Path(temp_dir).expanduser().resolve(strict=True) if temp_dir else Path(tempfile.gettempdir()).resolve(strict=True)
    if not temporary.is_dir():
        raise PreflightError(f"temporary path is not a directory: {temporary}")

    # Building and then copying an image can require two full image-sized
    # allocations if both paths share a filesystem. Add 5% headroom.
    output_device = destination.parent.stat().st_dev
    temp_device = temporary.stat().st_dev
    same_filesystem = output_device == temp_device
    required_output = image_size_bytes + (image_size_bytes if same_filesystem else 0)
    required_temp = image_size_bytes if not same_filesystem else 0
    margin_output = max(64 * 1024**2, required_output // 20)
    margin_temp = max(64 * 1024**2, required_temp // 20) if required_temp else 0
    output_free = shutil.disk_usage(destination.parent).free
    temp_free = shutil.disk_usage(temporary).free
    if output_free < required_output + margin_output:
        raise PreflightError(
            f"insufficient free space at output filesystem: need at least "
            f"{required_output + margin_output} bytes, have {output_free}"
        )
    if required_temp and temp_free < required_temp + margin_temp:
        raise PreflightError(
            f"insufficient free space at temporary filesystem: need at least "
            f"{required_temp + margin_temp} bytes, have {temp_free}"
        )

    commands = {name: shutil.which(name) for name in REQUIRED_COMMANDS}
    missing = [name for name, location in commands.items() if location is None]
    return {
        "schema_version": 1,
        "mode": "preflight-only",
        "side_effects": False,
        "image_size_bytes": image_size_bytes,
        "inputs": {
            "rootfs_archive": str(rootfs),
            "initramfs": str(initrd),
            "spare_kernels": [str(path) for path in kernels],
        },
        "output": str(destination),
        "temporary_directory": str(temporary),
        "same_filesystem_for_temp_and_output": same_filesystem,
        "free_space_bytes": {
            "output_filesystem": output_free,
            "temporary_filesystem": temp_free,
        },
        "required_commands": commands,
        "missing_commands": missing,
        "ready_for_build": not missing,
        "limitations": [
            "does not validate archive contents or kernel/initramfs formats",
            "does not create or write an image",
            "does not inspect or write physical devices",
            "available-space checks are a point-in-time estimate and can become stale",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rootfs_archive")
    parser.add_argument("initramfs")
    parser.add_argument("output")
    parser.add_argument("--spare-kernel", action="append", default=[], dest="spare_kernels")
    parser.add_argument("--image-size-gib", type=int, default=12)
    parser.add_argument("--temp-dir")
    args = parser.parse_args(argv)
    try:
        plan = build_plan(
            args.rootfs_archive, args.initramfs, args.output,
            args.spare_kernels, args.image_size_gib * 1024**3, args.temp_dir,
        )
    except (PreflightError, OSError) as exc:
        print(f"PREFLIGHT_FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    if plan["missing_commands"]:
        print("PREFLIGHT_WARNING: missing commands: " + ", ".join(plan["missing_commands"]), file=sys.stderr)
        return 2
    print("PREFLIGHT_OK: validation only; no image was created", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Explicit single-owner snapshot files; no automatic persistence or overwrite."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat

from .reconvergence import ReconvergenceConfig, ReconvergenceGuard, _SNAPSHOT_MAX_BYTES


def _checked_path(value: str | os.PathLike[str], *, missing: bool = False) -> Path:
    try:
        path = Path(value)
    except (TypeError, ValueError) as error:
        raise ValueError("snapshot path must be explicit and local") from error
    if (not path.is_absolute() or path.anchor.startswith("\\\\") or ".." in path.parts
            or any(":" in part for part in path.parts[1:])):
        raise ValueError("snapshot path must be absolute, local and without traversal")
    for part in (*reversed(path.parents), path):
        try:
            info = part.lstat()
        except FileNotFoundError:
            if missing and part == path:
                continue
            raise
        if (stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
            raise ValueError("snapshot paths cannot contain links or reparse points")
        if part != path:
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("snapshot ancestors must be ordinary directories")
        elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("snapshot must be an ordinary single-link file")
    return path


def _ordinary_handle(handle) -> os.stat_result:
    info = os.fstat(handle.fileno())
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("snapshot handle must reference an ordinary single-link file")
    return info


def save_new_snapshot(path: str | os.PathLike[str], guard: ReconvergenceGuard) -> dict[str, object]:
    """Create one new file; any write/flush/fsync/close failure returns no receipt.

    Existing files are never overwritten. A failed partial file is left in place;
    callers inspect it and choose a separately admitted new destination, not retry.
    """
    destination = _checked_path(path, missing=True)
    if not isinstance(guard, ReconvergenceGuard):
        raise ValueError("guard must be a ReconvergenceGuard")
    head = guard.head
    raw = guard.export_snapshot()
    if head != guard.head:
        raise ValueError("single-owner guard changed during snapshot export")
    digest = hashlib.sha256(raw).hexdigest()
    with destination.open("xb") as handle:
        _ordinary_handle(handle)
        if handle.write(raw) != len(raw):
            raise OSError("snapshot write was incomplete; retain the partial file")
        handle.flush()
        os.fsync(handle.fileno())
        if _ordinary_handle(handle).st_size != len(raw):
            raise OSError("snapshot size changed during save")
    return {"path": str(destination), "bytes": len(raw), "sha256": digest, "head": head}


def load_snapshot(path: str | os.PathLike[str], config: ReconvergenceConfig, *,
                  expected_snapshot_sha256: str, expected_head: str) -> ReconvergenceGuard:
    """Read at most 8 MiB + 1 before decoding; restore only with explicit anchors."""
    source = _checked_path(path)
    with source.open("rb") as handle:
        info = _ordinary_handle(handle)
        if info.st_size > _SNAPSHOT_MAX_BYTES:
            raise ValueError("snapshot file exceeds 8 MiB")
        raw = handle.read(_SNAPSHOT_MAX_BYTES + 1)
        if len(raw) > _SNAPSHOT_MAX_BYTES:
            raise ValueError("snapshot file exceeds 8 MiB")
        if _ordinary_handle(handle).st_size != len(raw):
            raise ValueError("snapshot file changed during bounded read")
    return ReconvergenceGuard.from_snapshot(config, raw,
        expected_snapshot_sha256=expected_snapshot_sha256, expected_head=expected_head)

#!/usr/bin/env python3
"""Opt-in fail-closed source inventory for the retained selected-record checker.

Nick Petalas. Apache-2.0. The production checker is unchanged.
"""
import errno
import hashlib
import json
import os
import stat
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = 'scripts/verify_selected_result.py'


def source(name):
    """Authenticate the exact bytes compiled or consumed, without a pyc lookup."""
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    rows = [row for row in manifest['files'] if row['path'] == name]
    if len(rows) != 1:
        raise ValueError('missing unique source pin: ' + name)
    raw = (ROOT / name).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if (hashlib.sha256(raw).hexdigest() != rows[0]['sha256']
            or blob != rows[0]['git_blob']):
        raise ValueError('source bytes differ: ' + name)
    return raw


def predecessor():
    module = ModuleType('_selected_inventory_predecessor')
    module.__file__ = str(ROOT / PREDECESSOR)
    exec(compile(source(PREDECESSOR), module.__file__, 'exec'), module.__dict__)  # noqa: S102
    return module


checker = predecessor()
MAX_ENTRIES = 1_000_000


def package_files(package, *, max_entries=MAX_ENTRIES):
    """Enumerate completely or fail, preserving contained regular-file aliases.

    Inputs must remain stable during the check. The budget counts descendants,
    including directories, and bounds the worklist without recursion.
    """
    checker.require(type(max_entries) is int and max_entries >= 0,
                    'inventory entry budget must be a nonnegative integer')
    checker.require(stat.S_ISDIR(package.stat().st_mode), 'Package root is not a directory')
    pending = [package]
    count = 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                count += 1
                checker.require(count <= max_entries, 'Package inventory entry budget exceeded')
                path = directory / entry.name
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    try:
                        mode = entry.stat(follow_symlinks=True).st_mode
                    except OSError as exc:
                        # Preserve the retained missing/cyclic-link diagnostic,
                        # but never turn an access or I/O failure into absence.
                        if exc.errno in (errno.ENOENT, errno.ENOTDIR, errno.ELOOP):
                            raise ValueError('Package symlink is not a regular file: ' + str(path)) from exc
                        raise
                    checker.require(stat.S_ISREG(mode),
                                    'Package symlink is not a regular file: ' + str(path))
                elif stat.S_ISDIR(mode):
                    pending.append(path)
                    continue
                checker.require(stat.S_ISREG(mode), 'Package entry is not a regular file: ' + str(path))
                checker.require(path.resolve().is_relative_to(package), 'Package symlink escapes root')
                yield path


checker.package_files = package_files


if __name__ == '__main__':
    checker.main()

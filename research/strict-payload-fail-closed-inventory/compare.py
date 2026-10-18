#!/usr/bin/env python3
"""Opt-in strict replay comparison with fail-closed filesystem inventory.

Nick Petalas. Apache-2.0. The retained comparator remains unchanged.
"""
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = 'research/strict-replay-payload-comparison/compare.py'


def source(name):
    """Read and authenticate the same bytes that will be compiled or inspected."""
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    rows = [row for row in manifest['files']
            if row['usage'] == 'input' and row['path'] == name]
    if len(rows) != 1:
        raise ValueError('missing unique source pin: ' + name)
    raw = (ROOT / name).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if (hashlib.sha256(raw).hexdigest() != rows[0]['sha256']
            or blob != rows[0]['git_blob']):
        raise ValueError('source bytes differ: ' + name)
    return raw


def predecessor():
    module = ModuleType('_strict_inventory_predecessor')
    module.__file__ = str(ROOT / PREDECESSOR)
    # Only SHA256/Git-blob-authenticated retained bytes execute, never cached .pyc.
    exec(compile(source(PREDECESSOR), module.__file__, 'exec'), module.__dict__)  # noqa: S102
    return module


strict = predecessor()
MAX_ENTRIES = 1_000_000


def inventory(root, *, max_entries=MAX_ENTRIES):
    """Enumerate completely or raise; never interpret an I/O failure as absence.

    The entry budget includes directories. Thus at most max_entries + 1
    directories, counting the root, can enter the worklist. No symlinks are
    followed. Inputs must remain stable while inventory and comparison run.
    """
    strict.require(type(max_entries) is int and max_entries >= 0,
                   'inventory entry budget must be a nonnegative integer')
    strict.require(stat.S_ISDIR(root.lstat().st_mode),
                   'comparison root must be a real directory: ' + str(root))
    pending, result = [root], {}
    count = 0
    while pending:
        directory = pending.pop()
        # scandir creation, iteration and lstat errors all propagate. Path.rglob
        # suppresses traversal errors, and Path.is_file can suppress stat errors.
        with os.scandir(directory) as entries:
            for entry in entries:
                count += 1
                strict.require(count <= max_entries, 'inventory entry budget exceeded')
                mode = entry.stat(follow_symlinks=False).st_mode
                path = directory / entry.name
                if stat.S_ISDIR(mode):
                    pending.append(path)
                else:
                    strict.require(stat.S_ISREG(mode),
                                   'nonregular entry outside comparison contract: ' + str(path))
                    result[path.relative_to(root).as_posix()] = path
    return result


strict.inventory = inventory


def __getattr__(name):
    return getattr(strict, name)


if __name__ == '__main__':
    sys.exit(strict.main())

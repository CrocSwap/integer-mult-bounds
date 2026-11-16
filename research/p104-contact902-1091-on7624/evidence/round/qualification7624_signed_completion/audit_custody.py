"""Strict source inventory and no-replace audit custody; contains no scientific code."""
import ctypes
import hashlib
import json
import os
from pathlib import Path

PINS_SHA = '6a84e8ce4a23a9d60d388e2f42f583903d0a275b4be27e1c42738385b236a4a3'
LOG = 'windows-path-adaptations.jsonl'
KNOWN = {'source_sha256': '35a3a38c6fe57cfb703a57a0382ef6f6b738131753b5fb5b97a68185b82994e1',
         'before': 'str(arc.relative_to(HERE))', 'after': 'arc.relative_to(HERE).as_posix()',
         'adapted_sha256': '57d9c83ecbcb3e9d7697dfa0d78bce6ff98958a1ee53267bffb710e362844caf',
         'path_name': 'source.py'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(package, allow_log):
    need(package.is_dir() and not package.is_symlink(), 'source package missing or symlink')
    pins_path = package / 'PINS.json'
    need(pins_path.is_file() and not pins_path.is_symlink() and sha(pins_path) == PINS_SHA, 'pins receipt changed')
    pins = json.loads(pins_path.read_bytes())
    need(len(pins) == 33, 'pin count')
    allowed = set(pins) | {'PINS.json'}
    dirs = {str(parent) for name in allowed for parent in Path(name).parents if str(parent) != '.'}
    found_files, found_dirs = set(), set()
    for path in package.rglob('*'):
        need(not path.is_symlink(), 'source tree symlink')
        rel = path.relative_to(package).as_posix()
        if path.is_file():
            found_files.add(rel)
        else:
            need(path.is_dir(), 'source special file')
            found_dirs.add(rel)
    need(found_dirs == dirs and found_files in (allowed, allowed | {LOG}) and
         (allow_log or LOG not in found_files), 'source inventory contains missing or extra entries')
    for name, pin in pins.items():
        p = package / name
        need(p.resolve().is_relative_to(package.resolve()) and p.is_file() and not p.is_symlink() and sha(p) == pin,
             'source pin changed: ' + name)
    return LOG in found_files


def validate_log(path):
    need(path.is_file() and not path.is_symlink(), 'audit log missing or symlink')
    raw = path.read_bytes()
    need(0 < len(raw) <= 4 * 1024 * 1024 and raw.endswith(b'\n'), 'audit log bounds or trailing newline')
    rows = raw.splitlines()
    for row in rows:
        need(json.loads(row) == KNOWN, 'unknown audit row')
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'rows': len(rows)}


def archive(package, destination, *, expected_sha=None, allow_absent=False):
    """After writer is absent: verify and atomically move exactly the known log, without replacement."""
    present = inventory(package, True)
    if not present:
        need(allow_absent, 'required predecessor audit missing')
        inventory(package, False)
        return {'status': 'ABSENT', 'rows': 0}
    source = package / LOG
    stats = validate_log(source)
    if expected_sha is not None:
        need(stats['sha256'] == expected_sha, 'predecessor audit changed')
    need(destination.parent.is_dir() and not destination.exists() and not destination.is_symlink(), 'audit destination exists or missing parent')
    need(source.stat().st_dev == destination.parent.stat().st_dev, 'atomic move crosses filesystems')
    before = source.stat(follow_symlinks=False)
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = libc.renameat2
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    if renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1) != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    after = destination.stat(follow_symlinks=False)
    need((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino), 'audit move identity changed')
    need(validate_log(destination) == stats, 'archived audit bytes changed')
    inventory(package, False)
    return {'status': 'ARCHIVED', **stats}

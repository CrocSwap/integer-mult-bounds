"""Immutable copies and fresh identity authentication. No target imports."""
import hashlib
import json
import os
from pathlib import Path
import stat

CHUNK = 65536


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def safe(path):
    path = Path(path)
    need(path.is_absolute() and path.resolve() == path, 'noncanonical/symlink path: ' + str(path))
    for ancestor in (path, *path.parents):
        need(not ancestor.is_symlink(), 'symlink ancestor: ' + str(ancestor))
    return path


def fields(info, directory=False):
    result = {key: getattr(info, 'st_' + key) for key in
              ('dev', 'ino', 'uid', 'gid', 'nlink', 'mtime_ns', 'ctime_ns')}
    result['mode'] = stat.S_IMODE(info.st_mode)
    if not directory:
        result['size'] = info.st_size
    return result


def pin(path, immutable=False):
    path = safe(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'regular unique-link file required')
    if immutable:
        need(stat.S_IMODE(before.st_mode) == 0o444, 'immutable0444 required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb', buffering=0) as stream:
        opened = os.fstat(stream.fileno())
        h, count = hashlib.sha256(), 0
        while True:
            data = stream.read(CHUNK)
            if not data:
                break
            h.update(data)
            count += len(data)
        after = os.fstat(stream.fileno())
    need(fields(before) == fields(opened) == fields(after) == fields(path.lstat()), 'identity drift')
    need(count == after.st_size, 'size drift')
    return dict(fields(after), sha256=h.hexdigest())


def same(path, expected, immutable=False):
    actual = pin(path, immutable)
    need(all(actual.get(k) == v for k, v in expected.items()), 'pin mismatch: ' + str(path))
    return actual


def read_json(path, expected_sha=None):
    path = safe(path)
    info = pin(path)
    need(info['size'] <= 4 * 1024 * 1024, 'metadata cap')
    if expected_sha is not None:
        need(info['sha256'] == expected_sha, 'metadata anchor mismatch')
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == info['sha256'], 'metadata read drift')
    return json.loads(raw)


def write_json(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    need(len(raw) <= 4 * 1024 * 1024, 'metadata cap')
    with Path(path).open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def stage(root, sources):
    """sources maps safe relative destination to {path,sha256,size,mode optional}."""
    root = safe(root)
    root.mkdir(mode=0o700)
    for name, spec in sorted(sources.items()):
        relative = Path(name)
        need(not relative.is_absolute() and '..' not in relative.parts, 'unsafe relative copy')
        source = safe(Path(spec['path']))
        before = same(source, {k: v for k, v in spec.items() if k != 'path'})
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with source.open('rb') as src, destination.open('xb') as dst:
            while True:
                data = src.read(CHUNK)
                if not data:
                    break
                dst.write(data)
            dst.flush()
            os.fsync(dst.fileno())
        destination.chmod(0o444)
        copied = pin(destination, True)
        need(copied['sha256'] == before['sha256'] and copied['size'] == before['size'], 'copy mismatch')
        need((copied['dev'], copied['ino']) != (before['dev'], before['ino']), 'copy aliases source')
        same(source, before)
    directories = sorted((p for p in root.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True)
    for directory in directories:
        directory.chmod(0o555)
    root.chmod(0o555)
    return snapshot(root)


def snapshot(root):
    root = safe(root)
    need(root.is_dir() and stat.S_IMODE(root.stat().st_mode) == 0o555, 'root0555 required')
    files, directories = {}, {}
    for path in sorted(root.rglob('*')):
        safe(path)
        if path.is_dir():
            need(stat.S_IMODE(path.stat().st_mode) == 0o555, 'directory0555 required')
            directories[str(path.relative_to(root))] = fields(path.stat(), True)
        else:
            files[str(path.relative_to(root))] = pin(path, True)
    identities = [(v['dev'], v['ino']) for v in files.values()]
    need(len(identities) == len(set(identities)), 'aliased staged files')
    return {'schema': 'h25-input-custody-v1', 'root': str(root),
            'root_identity': fields(root.stat(), True), 'directories': directories, 'files': files}


def check_snapshot(custody):
    need(snapshot(Path(custody['root'])) == custody, 'fresh custody mismatch')
    return {'files': len(custody['files']), 'fresh_full_read': True}

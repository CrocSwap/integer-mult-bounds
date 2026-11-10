"""Check this inert source archive's bytes only; never import its contents."""
from pathlib import Path
import hashlib
import json
import re
import stat
import sys
import tarfile

MAX_FILES = 3000
MAX_PAYLOAD = 256 * 1024 * 1024
MAX_OBJECT = 32 * 1024 * 1024


def need(value, message):
    if not value:
        raise ValueError(message)


def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'MANIFEST.json').read_bytes())
    need(manifest['schema'] == 'inert-source-package-file-manifest-v1', 'manifest schema')
    rows = manifest['files']
    need(type(rows) is list and 1 <= len(rows) < 100, 'package file bound')
    expected = {'MANIFEST.json'}
    for row in rows:
        name = row['path']
        need(type(name) is str and name not in expected and
             all(part not in ('', '.', '..') for part in name.split('/')) and
             not name.startswith('/'), 'package path or duplicate')
        expected.add(name)
        path = root / name
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and not info.st_mode & 0o111, 'nonregular/executable package file')
        need(info.st_size == row['bytes'] and hash_file(path) == row['sha256'], 'package bytes differ: ' + name)
    found = set()
    for path in root.rglob('*'):
        info = path.lstat()
        need(not stat.S_ISLNK(info.st_mode), 'package symlink')
        if path.is_file():
            found.add(path.relative_to(root).as_posix())
    need(found == expected, 'package membership differs')
    source = json.loads((root / 'SOURCE-MAP.json').read_bytes())
    origins = source['origins']
    need(type(origins) is list and 1 <= len(origins) <= MAX_FILES, 'origin bound')
    objects = {}
    paths = set()
    opaque = 0
    opaque_objects = {}
    for row in origins:
        need(row['origin_path'] not in paths, 'duplicate original path')
        paths.add(row['origin_path'])
        sha = row['sha256']
        need(re.fullmatch('[0-9a-f]{64}', sha) is not None, 'source digest shape')
        member = 'objects/' + sha + '.txt'
        size = row['bytes']
        need(type(size) is int and 0 <= size <= MAX_OBJECT, 'source object bound')
        if row['opaque_historical_compressed_input']:
            name = row['package_file']
            need(type(name) is str and re.fullmatch('opaque/[A-Za-z0-9_.-]+\\.gz', name), 'opaque package path')
            need(row['archive_member'] is None and row['archive_mode'] is None, 'opaque storage mapping')
            need((root/name).stat().st_size == size and hash_file(root/name) == sha, 'opaque bytes differ')
            opaque_objects[sha] = size
            opaque += 1
            continue
        need(row['archive_member'] == member and row['archive_mode'] == 0o444 and row['package_file'] is None, 'source member mapping')
        need(member not in objects or objects[member] == size, 'object size alias')
        objects[member] = size
    need(len(objects) == source['archive_objects'] and len(objects)+len(opaque_objects) == source['unique_objects'] and len(origins) == source['origin_count'], 'source cardinalities')
    need(sum(objects.values()) == source['archive_payload_bytes'] and sum(opaque_objects.values()) == source['opaque_payload_bytes'], 'storage payload counters')
    need(sum(objects.values())+sum(opaque_objects.values()) == source['unique_payload_bytes'] <= MAX_PAYLOAD, 'source payload bound')
    need(opaque == 3, 'three expressly opaque inherited gzip inputs required')
    seen = set()
    total = 0
    # This decompresses ONLY the newly authored wrapper. The three inherited
    # gzip files are separate opaque files, hashed directly and never decoded.
    with tarfile.open(root / 'SOURCE-ARCHIVE.tar.xz', mode='r|xz') as archive:
        for member in archive:
            need(member.isfile() and member.name in objects and member.name not in seen, 'archive member/type')
            need(member.mode == 0o444 and member.uid == 0 and member.gid == 0 and member.mtime == 0, 'archive metadata')
            need(member.size == objects[member.name], 'archive object size')
            stream = archive.extractfile(member)
            need(stream is not None, 'archive object unavailable')
            h = hashlib.sha256()
            length = 0
            with stream:
                for block in iter(lambda: stream.read(65536), b''):
                    h.update(block); length += len(block)
            need(length == member.size and h.hexdigest() == member.name[8:-4], 'archive object bytes')
            seen.add(member.name); total += length
    need(seen == set(objects) and total == source['archive_payload_bytes'], 'archive membership/payload')
    print(json.dumps({'status': 'PASS_ARCHIVAL_BYTES_ONLY', 'package_files': len(found),
                      'origin_paths': len(origins), 'unique_objects': len(objects)+len(opaque_objects),
                      'unique_payload_bytes': total+sum(opaque_objects.values()), 'old_gzip_payloads_decoded': 0,
                      'source_or_control_execution': False, 'runtime_admission': False}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('FAIL_ARCHIVAL_BYTES_ONLY: ' + type(error).__name__ + ': ' + str(error), file=sys.stderr)
        raise SystemExit(1)

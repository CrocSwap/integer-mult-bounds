"""Check only this archive's ordinary-file bytes; never import its source."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import stat
import sys


def fail(message):
    raise ValueError(message)


def checked_relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        fail('invalid relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        fail('noncanonical relative path')
    return p


def check(root):
    raw = (root / 'MANIFEST.json').read_bytes()
    if len(raw) > 16 * 1024 * 1024:
        fail('manifest too large')
    manifest = json.loads(raw)
    rows = manifest['files']
    if not isinstance(rows, list) or len(rows) > 1000:
        fail('invalid file inventory')
    expected = set()
    by_path = {}
    total = 0
    for row in rows:
        rel = checked_relative(row['path'])
        if str(rel) == 'MANIFEST.json' or str(rel) in expected:
            fail('self or duplicate file inventory')
        if not isinstance(row['bytes'], int) or row['bytes'] < 0:
            fail('invalid byte count')
        if not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            fail('invalid SHA256')
        if row['archival_git_mode'] != '100644':
            fail('unexpected archival mode declaration')
        path = root / rel
        for parent in (path, *path.parents):
            if parent == root:
                break
            if parent.is_symlink():
                fail('symlink in archived path: ' + str(rel))
        if not stat.S_ISREG(path.lstat().st_mode):
            fail('not an ordinary file: ' + str(rel))
        data = path.read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            fail('byte/hash mismatch: ' + str(rel))
        expected.add(str(rel))
        by_path[str(rel)] = row
        total += len(data)
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            fail('unexpected symlink')
        if path.is_file():
            actual.add(str(path.relative_to(root)))
    if actual != expected | {'MANIFEST.json'}:
        fail('missing or extra ordinary files')
    mapping = json.loads((root / 'SOURCE-MAPPING.json').read_bytes())
    for row in mapping['mapping']:
        path = str(checked_relative(row['export_path']))
        item = by_path.get(path)
        if item is None or item['bytes'] != row['bytes'] or item['sha256'] != row['sha256']:
            fail('source-map binding mismatch: ' + path)
        if row['archival_git_mode'] != '100644':
            fail('source-map archival mode mismatch')
    subject = root / 'evidence/source/SOURCE-MANIFEST-v2.json'
    if hashlib.sha256(subject.read_bytes()).hexdigest() != mapping['subject_sha256']:
        fail('subject-manifest identity mismatch')
    return {'status': 'PASS_ARCHIVAL_BYTES_ONLY', 'files_checked': len(rows), 'payload_bytes': total,
            'mapping_rows_checked': len(mapping['mapping']), 'candidate_imported_or_executed': False,
            'manifest_self_identity': 'Bound separately by publication commit/allowlist; not self-hashed.',
            'source_acceptance_or_runtime_grant': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'FAIL_ARCHIVAL_BYTES_ONLY', 'error': str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())

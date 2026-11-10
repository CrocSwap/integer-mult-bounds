#!/usr/bin/env python3
"""Offline file-integrity check only; never executes or parses archived programs."""
import hashlib
import json
from pathlib import Path
import stat
import sys

root = Path(__file__).resolve().parent
manifest_name = 'SOURCE-EXPORT-MANIFEST-v1.json'
manifest = json.loads((root / manifest_name).read_bytes())
expected = {row['path']: row for row in manifest['files']}
seen = set()
for p in root.rglob('*'):
    if p.is_symlink():
        sys.exit('Unexpected symlink: ' + str(p))
    if p.is_file():
        rel = p.relative_to(root).as_posix()
        if rel == manifest_name:
            continue
        seen.add(rel)
        if rel not in expected:
            sys.exit('Unmanifested file: ' + rel)
        row = expected[rel]
        data = p.read_bytes()
        bsha = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256'] or bsha != row['git_blob_sha1']:
            sys.exit('Byte/hash mismatch: ' + rel)
        if row['git_mode'] != '100644' or stat.S_IMODE(p.stat().st_mode) & 0o111:
            sys.exit('Unexpected executable mode: ' + rel)
if seen != set(expected):
    sys.exit('Missing manifest files: ' + repr(sorted(set(expected) - seen)))
print(json.dumps({'status': 'PASS_SOURCE_ARCHIVE_FILE_INTEGRITY_ONLY', 'files': len(seen), 'bytes': sum(row['bytes'] for row in expected.values()), 'target_executions': 0, 'manifest_self_excluded': True, 'runtime_or_scientific_acceptance': False}, sort_keys=True))

"""Step 0 of verify.sh: the package's files, its vendored inputs and the files of main it reads.

MANIFEST.sha256  every file of the package (except MANIFEST.sha256 itself) with its sha256; a mismatch, a missing file
                 or an unlisted file fails.
SOURCES.json     every file under data/vendor/ with the PR, author, commit and path it was copied from and the git blob
                 id of the original file (for a .gz copy: of the decompressed content); the blob id is recomputed here,
                 so anyone can compare it with `git rev-parse <commit>:<path>`.
DEPENDS.json     the files of main the checks read, by sha256.
"""
import gzip
import hashlib
import json
import os
import sys

from report import PKG, REPO, check, finish


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


listed, bad = set(), []
for line in (PKG / 'MANIFEST.sha256').read_text().splitlines():
    h, rel = line.split('  ', 1)
    listed.add(rel)
    p = PKG / rel
    if not p.is_file() or sha256(p) != h:
        bad.append(rel)
present = set()
for root, dirs, files in os.walk(PKG):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), PKG)
        if rel != 'MANIFEST.sha256':
            present.add(rel)
unlisted = sorted(present - listed)
check('0.manifest', not bad and not unlisted,
      '%d files match MANIFEST.sha256' % len(listed) if not bad and not unlisted
      else 'mismatch or missing: %s; unlisted: %s' % (bad, unlisted))

src = json.loads((PKG / 'SOURCES.json').read_text())
vend = sorted(os.path.relpath(os.path.join(r, f), PKG) for r, _, fs in os.walk(PKG / 'data' / 'vendor') for f in fs)
bad = []
for e in src['files']:
    data = (PKG / e['file']).read_bytes()
    if e['file'].endswith('.gz') and not e['source_path'].endswith('.gz'):
        data = gzip.decompress(data)
    if blob_id(data) != e['blob']:
        bad.append(e['file'])
check('0.sources', not bad and sorted(e['file'] for e in src['files']) == vend,
      '%d vendored files match the git blob ids of their PR commits' % len(vend) if not bad else 'blob mismatch: %s' % bad)

dep = json.loads((PKG / 'DEPENDS.json').read_text())
bad = [d['path'] for d in dep['files'] if not (REPO / d['path']).is_file() or sha256(REPO / d['path']) != d['sha256']]
check('0.depends', not bad, '%d files of main match DEPENDS.json (repository root %s)' % (len(dep['files']), REPO)
      if not bad else 'missing or changed: %s' % bad)
finish()

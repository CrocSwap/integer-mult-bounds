# SPDX-License-Identifier: Apache-2.0
"""Literal two-copy lift and one cold-start residue coalescing move.

Prepared for Yiyang (@Lyy-iiis) with substantial OpenAI Codex assistance.
PR2833 words: Jeremy Kothe and the retained predecessor lineage.
PR2843 T124 allocation: Marius-Paul Dumitrean.
PR2839 arbitrary replica geometry and checks: Dugongue and retained contributors.
"""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate():
    pins = read(HERE / 'SOURCE-PINS.json')
    for record in pins['files']:
        raw = (HERE / 'sources' / record['name']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record['sha256'],
             'source SHA256: ' + record['name'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == record['git_blob'], 'source Git blob: ' + record['name'])
    for record in pins.get('additional_files', []):
        raw = (HERE / record['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record['sha256'],
             'additional source SHA256: ' + record['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == record['git_blob'], 'additional Git blob: ' + record['path'])
    return pins


def build():
    authenticate()
    source = HERE / 'sources'
    old_order = read(source / 'PR2843-ORDER.json')
    old_fill = read(source / 'PR2843-FILL.json.gz')
    old_dispatch = read(source / 'PR2843-DISPATCH.json')
    need(len(old_order) == 1116, 'exact T124 predecessor')
    order = [[stage, replica + 124 * copy]
             for stage, replica in old_order for copy in (0, 1)]
    dispatch = [[stage, replica + 124 * copy, provider]
                for stage, replica, provider in old_dispatch for copy in (0, 1)]
    rows = [[2 * time + copy, helper, owner + 124 * copy, child, port, offset]
            for time, helper, owner, child, port, offset in old_fill['rows']
            for copy in (0, 1)]
    fill = {
        'columns': old_fill['columns'],
        'dispatch_overrides': [[stage, replica + 124 * copy, provider]
                               for stage, replica, provider in old_fill['dispatch_overrides']
                               for copy in (0, 1)],
        'rows': rows,
    }
    first = [row for row in rows if row == [0, 224, 0, 0, 0, 0]]
    second = [row for row in rows if row == [1, 224, 124, 0, 0, 0]]
    need(len(first) == len(second) == 1, 'two exact exceptional roles')
    first[0][2] = 124
    second[0][5] = 7
    return order, dispatch, fill


if __name__ == '__main__':
    # Explicit regeneration only. The verifier compares in memory.
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    need(not args.out.exists(), 'fresh output directory required')
    args.out.mkdir(parents=True)
    order, dispatch, fill = build()
    for name, data in [('ORDER.json', order), ('DISPATCH.json', dispatch),
                       ('FILL.json.gz', fill)]:
        raw = json.dumps(data, sort_keys=True, separators=(',', ':')).encode()
        if name.endswith('.gz'):
            encoded = bytearray(gzip.compress(raw, mtime=0))
            encoded[9] = 255
            raw = bytes(encoded)
        (args.out / name).write_bytes(raw)
    print('PASS_DETERMINISTIC_TWO_COPY_RESIDUE_GENERATION')

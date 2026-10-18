#!/usr/bin/env python3
"""Retain both predecessor audits and check complete mismatch diagnostics.

Nick Petalas. Apache-2.0. Substantial automated assistance was used.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAIRED = ROOT / 'research/strict-payload-paired-walk'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def bind(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    rows = [r for r in manifest['files'] if r['usage'] == 'input']
    expected = {'research/strict-payload-paired-walk/' + name for name in
                ('compare.py', 'verify.py', 'test_compare.py', 'RESULT.json', 'SOURCES.json')}
    expected |= {'research/strict-replay-payload-comparison/' + name for name in
                 ('compare.py', 'verify.py', 'RESULT.json', 'SOURCES.json', 'TIMINGS.json', 'test_compare.py')}
    expected |= {'research/community-frontier1094-audit/' + name for name in
                 ('selected-replay.tar.gz', 'RESULT.json', 'REPLAY.json', 'ASSEMBLY.json')}
    expected |= {'research/selected-final-stage-portability/' + name for name in
                 ('compare_payloads.py', 'README.md')}
    require(len(rows) == len(expected) and {r['path'] for r in rows} == expected,
            'input inventory differs')
    for row in rows:
        raw = (root / row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'],
                'input SHA256 differs: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == row['git_blob'], 'input blob differs: ' + row['path'])


def setup():
    bind()
    namespace = {'__file__': str(PAIRED / 'verify.py'), '__name__': 'paired_checks'}
    exec(compile((PAIRED / 'verify.py').read_bytes(), namespace['__file__'], 'exec'), namespace)
    fast = namespace['module'](HERE / 'compare.py')
    paired = namespace['module'](PAIRED / 'verify.py')
    return fast, paired


def run():
    fast, paired = setup()
    retained = paired.module(ROOT / paired.OLD / 'verify.py', {'compare': fast.source})
    # Run PR2693's complete differential suite with this successor substituted.
    paired.setup = lambda: (fast, retained)
    result = paired.run()
    expected = json.loads((PAIRED / 'RESULT.json').read_bytes())
    require(encoded(result) == encoded(expected), 'complete predecessor result differs')
    return {'status': 'PASS_STRICT_PAYLOAD_NEGATIVE_REUSE', 'retained_result': result,
            'scope': 'Complete comparison results on the retained corpus and controls; no supplier replay or new kappa'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        require(encoded(result) == encoded(json.loads((HERE / 'RESULT.json').read_bytes())),
                'complete result differs')
    print(result['status'])

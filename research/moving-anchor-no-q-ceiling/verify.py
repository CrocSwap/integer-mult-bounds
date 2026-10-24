#!/usr/bin/env python3
"""Portable read-only verification of exactly the frozen p=3 no-Q invoice.
Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0; scientific code/source contributions remain unchanged in evidence/.
"""
from pathlib import Path
from hashlib import sha256
import json
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate(root, manifest):
    for name, expected in manifest.items():
        p = root / name
        need(p.is_file() and not p.is_symlink(), 'Missing regular input: ' + name)
        need(sha256(p.read_bytes()).hexdigest() == expected, 'Input hash mismatch: ' + name)


def capture_relation(capture, raw):
    need(capture == raw + b'\n', 'Design capture must equal raw source plus exactly one LF')


def main():
    package_manifest = json.loads((HERE / 'PACKAGE-FILES.json').read_bytes())
    authenticate(HERE, package_manifest)
    authenticate(HERE, json.loads((HERE / 'ARCHIVE-FILES.json').read_bytes()))
    for group in ('design', 'review', 'pair-inventory'):
        base = HERE / 'evidence' / group
        manifest = json.loads((base / 'FILES.json').read_bytes())
        authenticate(base, manifest.get('files', manifest))
    for request in json.loads((HERE / 'SOURCE-REQUESTS.json').read_bytes()):
        data = (HERE / request['snapshot']).read_bytes()
        need(request['head'] == 'b893ba6bd6c77c6e7efc48acb6f448218df671b7', 'Original source head retained')
        need(sha256(data).hexdigest() == request['sha256'], 'Original raw source bytes')
    for relation in json.loads((HERE / 'CAPTURE-RELATIONS.json').read_bytes()):
        raw = (HERE / relation['raw_snapshot']).read_bytes()
        capture = (HERE / relation['design_capture']).read_bytes()
        capture_relation(capture, raw)
        try:
            capture_relation(raw, raw)
        except ValueError:
            pass
        else:
            raise ValueError('Capture relation rejection control accepted wrong bytes')
    with tempfile.TemporaryDirectory(prefix='moving-anchor-check-') as d:
        temporary = Path(d)
        command = [sys.executable, '-I']
        if sys.flags.optimize:
            command.append('-O')
        command += ['-X', 'pycache_prefix=' + str(temporary / 'cache'), '-W', 'error', '-B',
                    str(HERE / 'evidence/review/check_ceiling.py')]
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env.pop('PYTHONOPTIMIZE', None)
        result = subprocess.run(command, cwd=temporary, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=60, check=False)
        need(result.returncode == 0, result.stderr.decode(errors='replace'))
        need(not result.stderr, 'Unexpected checker stderr')
        expected = (HERE / 'evidence/review/CHECK-RESULT.json').read_bytes()
        need(result.stdout == expected, 'Fresh independent result differs from frozen receipt')
        need(expected == (HERE / 'evidence/review/CHECK-RESULT-OPTIMIZED.json').read_bytes(), 'Frozen normal/optimized equality')
        receipt = json.loads(expected)
        need(receipt['status'] == 'PASS_INDEPENDENT_SCOPED_P3_MOVING_ANCHOR_CEILING', 'Exact p3 scope')
        need(receipt['source_bound_full_calls'] == 3 and not receipt['all_p_source_admission_claimed'], 'No all-p source admission')
    authenticate(HERE, package_manifest)
    print(json.dumps({'status': 'PASS_MOVING_ANCHOR_NO_Q_CEILING', 'full_calls': 3,
                      'main_owners': 224, 'fresh_helper_owners': 1224, 'main_target_rank': 24,
                      'positive_rank_mass': 15453, 'negative_rank_mass': 15453,
                      'scope': 'fixed source-bound optimistic invoice; strict loss for C>0',
                      'source_capture_relation': 'all three exact raw sources plus one preserved LF',
                      'capture_relation_control': 'same validator rejects missing LF',
                      'unchanged_independent_receipt': True, 'native_execution': False,
                      'complete_caller': False, 'all_p_admission': False, 'new_kappa': None}, sort_keys=True))


if __name__ == '__main__':
    main()

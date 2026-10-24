#!/usr/bin/env python3
"""Portable, read-only wrapper; no scientific expressions or source bytes changed.
Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0. Retained authorship and notices are in evidence/ and NOTICE.md.
"""
from pathlib import Path
from hashlib import sha256
import json
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
EXPECTED_MANIFEST = '2a54c76896586db9cd3562652531959bd524818d6e438baed39641911073079a'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root, records):
    for name, expected in records.items():
        path = root / name
        need(path.is_file() and not path.is_symlink(), 'Missing regular input: ' + name)
        need(sha256(path.read_bytes()).hexdigest() == expected, 'Input hash mismatch: ' + name)


def semantic(value, summary=False):
    if isinstance(value, dict):
        excluded = {'runtime_seconds', 'total_runtime_seconds'}
        if summary:
            excluded.add('receipt_sha256')
        return {k: semantic(v, summary) for k, v in value.items() if k not in excluded}
    if isinstance(value, list):
        return [semantic(v, summary) for v in value]
    return value


def same_receipt(actual, expected, summary=False):
    a, b = json.loads(actual.read_bytes()), json.loads(expected.read_bytes())
    need(semantic(a, summary) == semantic(b, summary), 'Semantic receipt mismatch: ' + expected.name)


def run(script, arguments, temporary, name):
    # Each child has a new cache namespace: -B alone does not disable cache reads.
    cache = temporary / ('cache-' + name)
    command = [sys.executable, '-I']
    if sys.flags.optimize:
        command.append('-O')
    command += ['-X', 'pycache_prefix=' + str(cache), '-W', 'error', '-B', str(script)] + arguments
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    result = subprocess.run(command, cwd=temporary, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False, timeout=150)
    need(result.returncode == 0, name + ' failed: ' + result.stderr.decode(errors='replace')[-3000:])
    need(not result.stderr, name + ' unexpected stderr: ' + result.stderr.decode(errors='replace')[-3000:])
    return result.stdout


def main():
    package_manifest = json.loads((HERE / 'PACKAGE-FILES.json').read_bytes())
    authenticate(HERE, package_manifest)
    manifest_bytes = (EVIDENCE / 'FILES.json').read_bytes()
    need(sha256(manifest_bytes).hexdigest() == EXPECTED_MANIFEST, 'Independent manifest changed')
    records = json.loads(manifest_bytes)
    authenticate(EVIDENCE, records)
    # Original requests remain unchanged and bind local copies as well as Git provenance.
    for row in json.loads((HERE / 'ORIGINS.json').read_bytes())['upstream_requests']:
        local = HERE.parent.parent / row['retained_path']
        need(sha256(local.read_bytes()).hexdigest() == row['sha256'], 'Original source request mismatch')
    with tempfile.TemporaryDirectory(prefix='small-frame-verify-') as directory:
        temporary = Path(directory)
        independent = run(EVIDENCE / 'check.py', [], temporary, 'independent')
        need(independent == (EVIDENCE / 'REVIEW-RESULT.json').read_bytes(), 'Independent result changed')
        result = json.loads(independent)
        need(result['status'] == 'PASS_FIXED_C_AND_K3_DISTINCT_RESULTS', 'Independent status')
        need(result['independent_message_states_verified'] == 8760, 'Independent complete bucket coverage')
        need(not result['all_concave_ceiling'] and not result['cuts4_to8_executed'], 'Scope guard')
        output = temporary / 'fixed.json'
        source = EVIDENCE / 'source'
        run(EVIDENCE / 'frozen/optimize.py', ['--source-root', str(source), '--output', str(output)], temporary, 'author-fixed')
        same_receipt(output, EVIDENCE / 'frozen/RESULT.json')
        cuts = temporary / 'cuts'
        run(EVIDENCE / 'frozen/min_rank_cuts.py', ['--source-root', str(source), '--output-dir', str(cuts)], temporary, 'author-cuts')
        need({x.name for x in cuts.iterdir()} == {'SUMMARY.json', 'CUT-1.json', 'CUT-2.json', 'CUT-3.json'}, 'Stop at cut3 exactly')
        for k in (1, 2, 3):
            same_receipt(cuts / f'CUT-{k}.json', EVIDENCE / f'frozen/cuts-normal/CUT-{k}.json')
        same_receipt(cuts / 'SUMMARY.json', EVIDENCE / 'frozen/cuts-normal/SUMMARY.json', summary=True)
    authenticate(HERE, package_manifest)
    print(json.dumps({'status': 'PASS_SMALL_COUPLED_FRAME_OPTIMUM', 'fixed_C': '15108879/5000000000',
                      'small_components': 18, 'small_variables': 68, 'big_variables_held_source': 1271,
                      'independent_bucket_evaluations': 8760, 'author_fresh_receipts': 'fixed and cuts1..3 match frozen semantics',
                      'source_histogram_is_fixed_C_optimum': True, 'all_concave_extension': False,
                      'cuts4_to8_executed': False, 'new_kappa': None}, sort_keys=True))


if __name__ == '__main__':
    main()

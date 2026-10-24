#!/usr/bin/env python3
"""Replay the frozen reviews from a copied source tree."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
STAGES = [
    ('formation', 'new-native-recipes-20261017/row-capture-native-review-20261020', 'check.py', '--out', 'normal/REVIEW.json', 'PASS_INDEPENDENT_ROW_CAPTURE_NATIVE'),
    ('line-entry', 'new-native-recipes-20261017/line-entry-reuse-review-20261020', 'check.py', '--out', 'normal/REVIEW.json', 'PASS_INDEPENDENT_LOCAL_LINE_ENTRY_REUSE'),
    ('clean-exchange', 'new-native-recipes-20261017/clean-centre-exchange-review-20261020', 'check.py', '--out', 'normal/REVIEW.json', 'PASS_INDEPENDENT_CLEAN_CENTRE_EXCHANGE'),
    ('clean-dual', 'new-native-recipes-20261017/clean-dual-review-20261020', 'check.py', '--out', 'normal/REVIEW.json', 'PASS_INDEPENDENT_CLEAN_DUAL_AND_SELECTED_CONJUGATE'),
    ('involution-model', 'independent-review-20261017/row-involution-review-20261020', 'check_review.py', '--out', 'verified-normal/CHECKS.json', 'PASS'),
    ('involution-native', 'new-native-recipes-20261017/row-involution-native-review-20261020', 'check.py', '--out', 'normal/REVIEW.json', 'PASS_INDEPENDENT_NATIVE_ROW_INVOLUTIONS'),
    ('reader-forward', 'bridge-review-20261017/involution-reader-review-20261020', 'check_review.py', '--output', 'normal/REVIEW-CHECKS.json', 'PASS_INDEPENDENT_ROUTED_INVOLUTION_READER'),
    ('reader-dual', 'new-native-recipes-20261017/complete-reader-dual-review-20261020', 'check.py', '--out', 'normal/REVIEW-CHECKS.json', 'PASS_INDEPENDENT_COMPLETE_READER_DUAL'),
    ('route32-model', 'independent-review-20261017/route32-capture-review-20261020', 'check_review.py', '--out', 'run-normal/CHECKS.json', 'PASS_INDEPENDENT_ROUTE32_RESPONSE_AND_CAPTURE'),
    ('simple-clean', 'new-native-recipes-20261017/simple-clean-native-review-20261020', 'check.py', '--out', 'normal/REVIEW-CHECKS.json', 'PASS_INDEPENDENT_DIRECT_SIMPLE_CLEAN_NATIVE'),
    ('route32-native', 'new-native-recipes-20261017/route32-native-review-20261020', 'check.py', '--out', 'normal/REVIEW.json', 'PASS_INDEPENDENT_ROUTE32_NATIVE'),
]

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def need(value, reason):
    if not value:
        raise ValueError(reason)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--optimized', action='store_true')
    parser.add_argument('--stage', choices=[x[0] for x in STAGES])
    args = parser.parse_args()
    output = args.out.resolve()
    need(not output.exists(), 'The output directory must be absent.')
    manifest = json.loads((ROOT/'SOURCE-MANIFEST.json').read_text())
    for row in manifest['files']:
        need(digest((ROOT/row['path']).read_bytes()) == row['sha256'], 'Source pin: '+row['path'])
    need(shutil.disk_usage(ROOT).free >= 3*1024**3, 'Keep at least 3 GiB free.')
    output.mkdir(parents=True)
    campaign = output/'campaign'
    shutil.copytree(ROOT/'frozen', campaign)
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    results = []
    for name, directory, script, option, expected, status in STAGES:
        if args.stage and args.stage != name:
            continue
        target = output/name
        command = [sys.executable, '-I', '-B'] + (['-O'] if args.optimized else []) + [str(campaign/'lanes'/directory/script), option, str(target)]
        start = time.monotonic()
        run = subprocess.run(command, cwd=output, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output/(name+'.log')).write_text(run.stdout)
        need(run.returncode == 0, name+' failed; see '+str(output/(name+'.log')))
        need(status in run.stdout, name+' did not report its expected status')
        expected_path = ROOT/'frozen/lanes'/directory/expected
        result_path = target/Path(expected).name
        need(result_path.read_bytes() == expected_path.read_bytes(), name+' receipt differs from the frozen receipt')
        inputs = ROOT/'frozen/lanes'/directory/'normal/INPUTS.json'
        if inputs.exists():
            need((target/'INPUTS.json').read_bytes() == inputs.read_bytes(), name+' input receipt differs')
        results.append(dict(stage=name, status=status, receipt_sha256=digest(result_path.read_bytes()), seconds=round(time.monotonic()-start,3)))
        print(name+': PASS; exact frozen receipt', flush=True)
    receipt = dict(status='PASS_NATIVE_CENTRE_CAPTURE_REPLAY', optimized=args.optimized, source_manifest_sha256=digest((ROOT/'SOURCE-MANIFEST.json').read_bytes()), source_files=len(manifest['files']), stages=results)
    (output/'REPLAY.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'], flush=True)

if __name__ == '__main__':
    main()

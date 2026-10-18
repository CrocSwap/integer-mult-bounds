"""Local reproducible bounded repair receipt. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REQUIRED = (
    'certificates/selected-result.json',
    'docs/research/community-batch1099-review.md',
    'research/bit-profile-pair-audit/EXPECTED.json',
    'research/bit-profile-pair-audit/LICENSE',
    'research/bit-profile-pair-audit/NOTICE.md',
    'research/bit-profile-pair-audit/README.md',
    'research/bit-profile-pair-audit/code/bitprof.py',
    'research/bit-profile-pair-audit/code/replay.py',
    'research/bit-profile-pair-audit/code/search.py',
    'research/bit-profile-pair-audit/code/stateprof.py',
    'research/bit-profile-pair-audit/verify.py',
    'research/community-batch1099-audit/check_pr1048_counterexample.py',
    'research/community-batch1099-audit/logs/batch1099-1048-finding.json',
    'research/community-batch1099-audit/pr1048-metadata.json',
    'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py',
    'research/e8-bit-p111-tuned/tune/EXPECTED.json',
    'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
    'research/e8-bit-p111-tuned/tune/moves.json',
    'research/e8-bit-p111-tuned/tune/tune.py',
    'research/e8-bit-p111-tuned/tune/wlib.py',
    'research/e8-bit-p111/data/bitE8mut-p111.json.gz',
    'research/profile-bracket-audit64/BASE-SELECTED.json',
    'research/profile-bracket-audit64/EXPECTED.json',
    'research/profile-bracket-audit64/PR-BODY.md',
    'research/profile-bracket-audit64/PROOF.md',
    'research/profile-bracket-audit64/PROVENANCE.md',
    'research/profile-bracket-audit64/README.md',
    'research/profile-bracket-audit64/SOURCES.json',
    'research/profile-bracket-audit64/VALIDATION.json',
    'research/profile-bracket-audit64/controls.py',
    'research/profile-bracket-audit64/independent.py',
    'research/profile-bracket-audit64/repair.py',
    'research/profile-bracket-audit64/vendor/LICENSE',
    'research/profile-bracket-audit64/vendor/NOTICE.md',
    'research/profile-bracket-audit64/vendor/bitprof.py',
    'research/profile-bracket-audit64/verify.py',
)


def check_sources(manifest=None):
    data = json.loads((HERE/'SOURCE-PINS.json').read_text()) if manifest is None else manifest
    if data.get('schema') != 'pr1048-certified-repair-inputs-v1' or set(data.get('inputs', {})) != set(REQUIRED):
        raise ValueError('mandatory input inventory differs')
    for name, record in data['inputs'].items():
        b = (ROOT/name).read_bytes()
        if hashlib.sha256(b).hexdigest() != record['sha256']:
            raise ValueError('input SHA256 mismatch: '+name)
        if 'git_blob' in record and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() != record['git_blob']:
            raise ValueError('input Git blob mismatch: '+name)
    return len(REQUIRED)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--pricing-only', action='store_true', help='explicitly skip coverage; not a full package pass')
    args = ap.parse_args()
    args.out = args.out.resolve()
    pins = check_sources()
    args.out.mkdir(parents=True, exist_ok=False)
    timings = []
    scripts = [('pricing.py', 'PRICING.json')]
    if not args.pricing_only:
        scripts += [('coverage.py', 'COVERAGE.json'), ('independent.py', 'INDEPENDENT.json')]
    for script, target in scripts:
        command = [sys.executable, '-I', '-O', '-B', str(HERE/script)]
        if script == 'coverage.py':
            command += ['--output', str(args.out/'COVERAGE.json')]
        elif script == 'independent.py':
            command += ['--pricing', str(args.out/'PRICING.json'), '--coverage', str(args.out/'COVERAGE.json')]
        start = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        timings.append({'command': command, 'returncode': result.returncode, 'elapsed_seconds': round(time.monotonic()-start, 3)})
        (args.out/(target+'.stderr')).write_text(result.stderr)
        if result.returncode:
            (args.out/(target+'.failed-stdout')).write_text(result.stdout)
            raise RuntimeError(script+' failed; inspect output directory')
        # Coverage writes the full receipt separately and emits a short summary.
        # Both shapes must be valid JSON; no parser tolerance hides extra text.
        stdout = json.loads(result.stdout)
        receipt = json.loads((args.out/target).read_text()) if script == 'coverage.py' else stdout
        (args.out/target).write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
        print(script+': '+receipt['status'], flush=True)
    (args.out/'EXECUTION.json').write_text(json.dumps({'python': sys.version, 'source_pins': pins, 'runs':timings},indent=2)+'\n')
    print('PASS_PRICING_ONLY' if args.pricing_only else 'PASS_LOCAL_BOUNDED_REPAIR')


if __name__ == '__main__':
    main()

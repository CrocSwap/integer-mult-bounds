"""Re-run the complete PR1218 verifier with the 1e-24 outer grid and bind the release receipt."""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
PR1218_KAPPA = Fraction('0.001675809683500501')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--base-native-from', type=Path)
    parser.add_argument('--extra-native-from', type=Path)
    args = parser.parse_args()
    if sys.flags.optimize:
        raise ValueError('Full proof requires assertions enabled')
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    manifest_sha = digest(PACKAGE / 'MANIFEST.json')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []

    def run(name, script, *arguments):
        started = time.monotonic()
        with (work / (name + '.log')).open('w', encoding='utf-8') as output:
            result = subprocess.run(
                [sys.executable, '-B', str(script), *map(str, arguments)],
                cwd=args.main.resolve(), env=env, stdin=subprocess.DEVNULL,
                stdout=output, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        stages.append(dict(stage=name, exit_code=result.returncode,
                           seconds=round(time.monotonic() - started, 3)))
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n', encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'{name} failed; see {work / (name + ".log")}')
        print('PASS', name, flush=True)

    run('manifest', PACKAGE / 'verify_manifest.py')
    extra = []
    if args.base_native_from:
        extra += ['--base-native-from', args.base_native_from]
    if args.extra_native_from:
        extra += ['--extra-native-from', args.extra_native_from]
    run('pr1218-full-verifier-with-1e-24-grid', PACKAGE / 'verify.py', '--work', work / 'full', *extra)
    result = read_json(work / 'full/RESULT.json')
    if result['status'] != 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION':
        raise RuntimeError('Incomplete PR1218 replay')
    strict = read_json(work / 'full/strict/RESULT.json')
    refined = Fraction(strict['kappa'])
    claim = read_json(PACKAGE / 'CLAIM.json')
    if refined != Fraction(claim['kappa']) or strict['kappa_decimal'] != claim['kappa_decimal']:
        raise RuntimeError('Receipt kappa differs from CLAIM.json')
    # The refinement must be the same construction on a finer grid: the old 1e-18 floor reproduces PR1218.
    floor18 = Fraction((refined * 10**18).numerator // (refined * 10**18).denominator, 10**18)
    if not refined > PR1218_KAPPA or floor18 != PR1218_KAPPA:
        raise RuntimeError('Refined kappa is not the finer-grid value of the PR1218 construction')
    if digest(PACKAGE / 'MANIFEST.json') != manifest_sha:
        raise RuntimeError('Package manifest changed during verification')
    receipt = dict(
        status='PASS_RELEASE', kappa_decimal=str(strict['kappa_decimal']),
        manifest_sha256=manifest_sha,
        proof='Re-ran the complete PR1218 verifier (literal words, independent local audits, fusion and X54 '
              'controls, leaver premises, native replays, literal owner construction, strict global admission '
              'with all 114+12 controls and 47 outer inequalities) with the outer objective grid refined from '
              '1e-18 to 1e-24 (three grid expressions in the retained assembler); the 1e-18 floor of the '
              'refined value equals PR1218 exactly.',
        full_receipt_sha256=digest(work / 'full/RESULT.json'),
        strict_receipt_sha256=digest(work / 'full/strict/RESULT.json'), stages=stages)
    (work / 'RELEASE-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print('PASS_RELEASE', receipt['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

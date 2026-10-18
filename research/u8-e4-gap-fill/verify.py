"""Fresh source-bound local and mixed-controller replay; no optimizer runs.

Optional --baseline942 reuses a completed scripts/verify_frontier942.py output
after checking its entire evidence closure again. All outputs stay outside Git.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from support import P, ROOT, T37, dump, read, require, sha, validate_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline942', type=Path)
    args = parser.parse_args()
    require(__debug__, 'Supplier checks require assertions')
    validate_sources()
    work = args.work.resolve()
    require(not work.exists() and not work.is_relative_to(ROOT), 'Fresh output outside checkout required')
    work.mkdir(parents=True)
    baseline_root = args.baseline942.resolve() if args.baseline942 else work / 'baseline942'
    baseline = baseline_root / 'replay'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               PYTHON=sys.executable, SW4_FRAME8_PYTHON=sys.executable, T37_WORK=str(work),
               T37_BASELINE=str(baseline / 'baseline799'), T37_LOCAL=str(baseline / 'native/local'))
    temp = work / 'temp'
    temp.mkdir()
    env.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    input_sources = {str(p.relative_to(P)): sha(p) for p in P.rglob('*')
                     if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
    stages = []

    def run(name, script, *argv):
        start = time.monotonic()
        log = work / (name + '.log')
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, '-B', str(script), *map(str, argv)],
                                    cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode,
                           seconds=round(time.monotonic()-start, 3), log_sha256=sha(log)))
        dump(work / 'STAGES.json', stages)
        require(result.returncode == 0, name + ': ' + log.read_text(errors='replace')[-7000:])
        print('PASS', name, stages[-1]['seconds'], flush=True)

    if args.baseline942 is None:
        run('baseline942-cold', ROOT / 'scripts/verify_frontier942.py', '--work', baseline_root)
    run('ancestry942', ROOT / 'scripts/verify_frontier942.py', '--check-only', '--work', baseline,
        '--out', work / 'ANCESTRY-942.json')
    run('construct', P / 'build.py', '--u8-word', baseline / 'native/barch/FULL-WORD.json.gz', '--out', work / 'construction')
    run('native-e4', P / 'native.py', '--word', work / 'construction/WORD.json.gz', '--out', work / 'native')
    run('runtime', T37 / 'prepare.py')
    run('plan', P / 'prepare.py', '--work', work, '--baseline942', baseline)
    run('independent-owners', P / 'independent.py', '--work', work, '--baseline942', baseline)
    run('independent-price', P / 'price.py', '--work', work)
    for mode in ('discovery', 'strict'):
        run(mode, P / 'replay.py', mode, '--work', work, '--baseline942', baseline)
    run('payload-controls', P / 'payload.py', '--work', work)
    run('final-binding', P / 'binding.py', '--work', work, '--baseline942', baseline)
    for name, digest in input_sources.items():
        require(sha(P / name) == digest, 'Package changed during replay: ' + name)
    validate_sources()
    claim = read(P / 'CLAIM.json')
    require(read(work / 'FINAL-BINDING.json')['kappa'] == claim['kappa'], 'Bound final result')
    result = dict(status='PASS_U8_E4_GAP_FILL_WITH_COMPLETE_SOURCE_BOUND_ANCESTRY',
                  kappa=claim['kappa'], kappa_decimal=claim['kappa_decimal'],
                  baseline942=str(baseline), reused_completed_baseline=args.baseline942 is not None,
                  source_sha256=input_sources, final_binding_sha256=sha(work / 'FINAL-BINDING.json'),
                  stages=stages, scope=claim['scope'])
    dump(work / 'RESULT.json', result)
    print(result['status'], result['kappa_decimal'])


if __name__ == '__main__':
    main()

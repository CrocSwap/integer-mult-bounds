#!/usr/bin/env python3
"""Replay Rohan Arun's PR1094 on Jeremy Kothe's checked k8/T16 construction.

Retains Hao Yan's controller and the credited bit/complex supplier lineage.
Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from verify_replay_coverage import check_selected, require

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline1042', type=Path,
                        help='Reuse the published source-bound PR1042 review replay')
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Supplier checks require assertions')
    work = args.work.resolve()
    require(not work.exists() and not work.is_relative_to(ROOT), 'Use fresh external output')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHON=sys.executable)
    for key in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)
    stages = []

    def run(name, script, *argv):
        log = work / (name + '.log')
        start = time.monotonic()
        with log.open('w') as stream:
            p = subprocess.run([sys.executable, '-B', str(script), *map(str, argv)],
                               cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=p.returncode, seconds=time.monotonic()-start,
                           script=str(script.relative_to(ROOT)), script_sha256=sha(script),
                           log_sha256=sha(log)))
        (work/'STAGES.json').write_text(json.dumps(stages, indent=2)+'\n')
        require(p.returncode == 0, name + ' failed: ' + str(log))
        print('PASS', name, flush=True)

    run('historical-source', ROOT/'scripts/verify_selected_result.py', '--record',
        'certificates/checkpoints/frontier1042.json')
    baseline = args.baseline1042.resolve() if args.baseline1042 else work/'baseline1042'
    if args.baseline1042 is None:
        run('baseline1042-cold', ROOT/'scripts/verify_frontier1042.py', '--work', baseline)
    receipt = read(baseline/'RESULT.json')
    if args.baseline1042 is not None:
        require(sha(baseline/'RESULT.json') == sha(ROOT/'research/community-frontier1042-audit/RESULT.json'),
                'Reuse requires the published reviewed receipt; otherwise use the cold default')
    require(receipt['status'] == 'PASS_COMPLETE_PR1042_COMPOSITION' and
            Fraction(receipt['kappa']) == Fraction('0.001672188119205421'), 'Complete historical result')
    expected = ['leaver-manifest', 'slots-manifest', 't16-manifest', 'base', 'cells', 'chain',
                'independent-leaver', 'leaver-global', 'slots', 't16']
    steps = receipt['stages']
    require([s['name'] for s in steps] in [expected, ['baseline799-cold']+expected], 'Full stage coverage')
    require(steps == read(baseline/'STAGES.json'), 'Stage receipt binding')
    for s in steps:
        require(s['exit_code'] == 0 and sha(ROOT/s['script']) == s['script_sha256'] and
                sha(baseline/(s['name']+'.log')) == s['log_sha256'], 'Source-bound completed stage')
    require(receipt['artifacts'], 'Missing artifact coverage')
    for name, digest in receipt['artifacts'].items():
        p = (baseline/name).resolve()
        require(p.is_relative_to(baseline) and p.is_file() and sha(p) == digest, 'Artifact: '+name)
    ancestor = Path(receipt['baseline']).resolve()
    check_selected(ancestor, ancestor/'ancestor')
    require(sha(baseline/'BASELINE-BINDING.json') == receipt['baseline_binding_sha256'], 'Ancestor binding')
    run('rare-pattern-exchanges', PACKAGE/'verify.py', '--main', ROOT,
        '--local', baseline/'slots/local', '--work', work/'candidate')
    final = read(work/'candidate/strict/REPLAY.json')
    assembly = read(work/'candidate/strict/ASSEMBLY.json')
    require(Fraction(final['kappa']) == Fraction('0.001672660197076918') and
            final['kappa'] == assembly['kappa'], 'Exact selected kappa')
    require(assembly['bit_supplier'] == read(baseline/'t16/ASSEMBLY.json')['bit_supplier'], 'Retained bit supplier')
    require(len(assembly['outer']) == 47 and all(Fraction(v)>0 for v in assembly['outer'].values()), 'Strict outer assembly')
    require(final['controls'] == dict(admission=69, bit_supplier=12, independent_t16=6, controller_mutations=15), 'Full controls')
    require(final['roles'] == 69120 and final['complete_invocations'] == 144 and
            final['prefix_bits'] == 397 and final['charged_prefix_bits'] == 512 and
            final['physical_row_coefficient'] == 16469, 'Physical inventory')
    result = dict(status='PASS_COMPLETE_PR1094_COMPOSITION', kappa=assembly['kappa'],
                  decimal=assembly['kappa_decimal'], stages=stages,
                  reused_completed_baseline=bool(args.baseline1042), baseline=str(baseline),
                  baseline_receipt_sha256=sha(baseline/'RESULT.json'),
                  assembly_sha256=sha(work/'candidate/strict/ASSEMBLY.json'),
                  scope=receipt['scope'])
    (work/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], result['decimal'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Rebuild the mutable-leaver/slot/T16 composition with complete bit ancestry.

Construction: Jeremy Kothe, with Rohan Arun's slot search and Hao Yan's T16
controller, on the retained credited E8 lineage. Maintainer orchestration:
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
PKG = ROOT / 'research/gauge44-slots-t16'


def read(p):
    return json.loads(p.read_bytes())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--baseline799', type=Path,
                   help='Reuse a completed source-bound PR799/PR741/PR589 replay')
    a = p.parse_args()
    require(not sys.flags.optimize, 'Supplier workers require assertions')
    work = a.work.resolve()
    require(not work.exists() and not work.is_relative_to(ROOT), 'Use fresh external output')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHON=sys.executable)
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []

    def run(name, script, *args):
        log = work / (name + '.log'); start = time.monotonic()
        print('RUN', name, flush=True)
        with log.open('w') as stream:
            rc = subprocess.call([sys.executable, '-B', str(script), *map(str, args)],
                                 cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=rc, seconds=time.monotonic()-start,
                           script=str(script.relative_to(ROOT)), script_sha256=digest(script),
                           log_sha256=digest(log)))
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2)+'\n')
        require(rc == 0, name+' failed; see '+str(log))
        print('PASS', name, flush=True)

    baseline = a.baseline799.resolve() if a.baseline799 else work/'baseline799'
    if not a.baseline799:
        run('baseline799-cold', ROOT/'scripts/verify_frontier799.py', '--work', baseline)
    ancestor = check_selected(baseline, baseline/'ancestor')
    (work/'BASELINE-BINDING.json').write_text(json.dumps(ancestor, indent=2)+'\n')
    supplier = ROOT/'research/complex-sw4-frame8/vendor/pr635'
    leaver = ROOT/'research/gauge44-leaver8'
    slots = ROOT/'research/gauge44-slots'
    for name, package in [('leaver-manifest', leaver), ('slots-manifest', slots), ('t16-manifest', PKG)]:
        run(name, package/'verify_manifest.py')
    common = ['--main', ROOT, '--pr635', supplier]
    run('base', leaver/'construction/reproduce.py', *common, '--out', work/'base', '--until', 'word')
    run('cells', leaver/'construction/leaver/reproduce_leaver.py', *common,
        '--word-dir', work/'base', '--id', 'k8', '--out', work/'cells')
    run('chain', leaver/'construction/leaver/reproduce_leaver_chain.py', *common,
        '--leaver-dir', work/'cells', '--hamming', work/'base/hamming', '--id', 'k8', '--out', work/'chain')
    run('independent-leaver', leaver/'independent/audit_local.py', '--main', ROOT,
        '--word', work/'chain/frames/FULL-WORD.json.gz', '--output', work/'INDEPENDENT-LEAVER.json')
    run('leaver-global', leaver/'verify_global.py', '--main', ROOT,
        '--local', work/'chain/local', '--work', work/'leaver-global')
    run('slots', slots/'construction/slots/verify_slots.py', *common,
        '--baseline', work/'chain', '--work', work/'slots')
    run('t16', PKG/'verify_t16.py', '--main', ROOT,
        '--local', work/'slots/local', '--work', work/'t16')
    assembly = read(work/'t16/ASSEMBLY.json')
    result = read(work/'t16/REPLAY.json')
    parent_assembly = read(baseline/'global/ASSEMBLY.json')
    require(assembly['bit_supplier'] == parent_assembly['bit_supplier'],
            'New assembly does not use the completely checked inherited bit supplier')
    require(Fraction(assembly['kappa']) == Fraction('0.001672188119205421'), 'Unexpected selected kappa')
    require(result['kappa'] == assembly['kappa'] and len(assembly['outer']) == 47 and
            all(Fraction(x)>0 for x in assembly['outer'].values()), 'Final strict assembly')
    require(result['controls'] == dict(admission=69, bit_supplier=12, independent_t16=6, controller_mutations=15),
            'Incomplete T16 controls')
    require(result['roles'] == 69120 and result['complete_invocations'] == 144 and
            result['prefix_bits'] == 397 and result['charged_prefix_bits'] == 512 and
            result['physical_row_coefficient'] == 16469, 'Final physical inventory')
    artifacts = {}
    for path in sorted(work.rglob('*')):
        if path.is_file() and path.suffix in ('.json', '.gz', '.log') and not path.is_relative_to(work/'baseline799'):
            artifacts[path.relative_to(work).as_posix()] = digest(path)
    receipt = dict(status='PASS_COMPLETE_PR1042_COMPOSITION', kappa=assembly['kappa'],
                   decimal=assembly['kappa_decimal'], stages=stages, artifacts=artifacts,
                   reused_completed_baseline=bool(a.baseline799), baseline=str(baseline),
                   baseline_binding_sha256=digest(work/'BASELINE-BINDING.json'),
                   selected_assembly_sha256=digest(work/'t16/ASSEMBLY.json'),
                   scope='Finite composition under inherited all-size/compiler, common-label/mutable-source, '
                         'whole-call hosting, precision/tape, analytic and bit H1-H5 assumptions. '
                         'Not a full Lean multiplication theorem.')
    (work/'RESULT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'], receipt['decimal'])


if __name__ == '__main__':
    main()

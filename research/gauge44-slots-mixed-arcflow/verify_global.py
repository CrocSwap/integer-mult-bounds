"""Replay the changed global admission against pinned upstream dependencies.

The local directory must contain the fresh canonical/native/phase/wrapper
artifacts produced by construction/reproduce.py. Frozen evidence may be used
for a short admission-only replay. No optimizer runs during this verifier.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

assert __debug__, 'Assertions required'
PACKAGE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--main', type=Path, required=True, help='Pinned CrocSwap main checkout')
ap.add_argument('--local-r16', type=Path, required=True, help='native locals of the sixteen-restoration word (6ace902a)')
ap.add_argument('--local-r12', type=Path, required=True, help='native locals of the twelve-restoration word (keep603)')
ap.add_argument('--work', type=Path, required=True, help='New output directory')
ap.add_argument('--discover', action='store_true', help=argparse.SUPPRESS)
args = ap.parse_args()
main, work = args.main.resolve(), args.work.resolve()
assert not work.exists(), 'Output directory must be new'
source = main/'research/complex-k492-owner-repair/vendor/multicold'
baseline = main/'research/community-k492-audit/pr622/replay/baseline558'
vendor = source/'vendor/pr558/vendor/pr552/complex-global/vendor531'
pins = PACKAGE/'data/UPSTREAM-PINS.json'
if pins.exists():
    for rel, expected in json.loads(pins.read_text()).items():
        assert sha(main/rel) == expected, 'Upstream dependency changed: ' + rel
else:
    assert args.discover, 'Missing upstream pins'
    paths = list((baseline/'complex-global/base').rglob('*'))
    paths += [source/'code/run_portable.py', source/'inputs/PR543-EXPECTED.json',
              vendor/'evidence/audit/PREFIX-AND-INVOICE.json']
    paths += [source/'vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz',
              baseline/'complex-global/controller-input/split-centres/CANONICAL-WORD.json.gz',
              vendor/'code/prepare_supplier_base.py']
    paths += [source/'engines'/name for name in ('moment.py', 'base_two_moment.py', 'outer.py')]
    dump(pins, {p.relative_to(main).as_posix(): sha(p) for p in sorted(paths) if p.is_file()})
work.mkdir(parents=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
           PYTHONINTMAXSTRDIGITS='0', MULTICOLD_SOURCE=str(source),
           GAIN_PR564_SOURCE=str(source), WITNESS_SPEC=str(PACKAGE/'data/SPEC.json'))
env.pop('PYTHONOPTIMIZE', None)
env.pop('WITNESS_DISCOVER', None)
env.pop('WITNESS_RECORD', None)
if args.discover:
    env.update(WITNESS_DISCOVER='1', WITNESS_RECORD=str(work/'WITNESS-RECORD.jsonl'))
stages = []


def run(name, script, *arguments):
    started = time.monotonic()
    log = work/(name + '.log')
    with log.open('w') as stream:
        result = subprocess.run([sys.executable, '-B', str(source/'code/run_portable.py'),
                                 str(script), *map(str, arguments)], env=env,
                                stdout=stream, stderr=subprocess.STDOUT)
    stages.append(dict(name=name, seconds=round(time.monotonic()-started, 3),
                       exit_code=result.returncode, log_sha256=sha(log)))
    dump(work/'STAGES.json', stages)
    if result.returncode:
        raise RuntimeError(name + ' failed:\n' + log.read_text()[-7000:])
    print('PASS', name, stages[-1]['seconds'], flush=True)


code = PACKAGE/'code'
global_dir = work/'global'
run('restore-parent', code/'restore_parent.py', '--source', source,
    '--baseline', baseline, '--out', work/'parent558')
run('bind', code/'bind_providers_portable.py', '--baseline', work/'parent558',
    '--provider', 'gauge44r16='+str(args.local_r16.resolve()), '--provider', 'gauge44r12='+str(args.local_r12.resolve()),
    '--plan', PACKAGE/'data/PLAN.json', '--out', global_dir)
run('emit', code/'emit_allcold.py', '--base', global_dir/'base',
    '--owners', PACKAGE/'data/OWNERS.json.gz', '--plan', global_dir/'PLAN.json', '--out', global_dir/'hosted')
run('audit', code/'audit_allcold.py', global_dir/'base', global_dir/'hosted',
    global_dir/'audit/ASYNC-AUDIT.json', '--mutation-controls')
run('invoice', code/'invoice_allcold.py', '--base', global_dir/'base',
    '--hosted', global_dir/'hosted', '--audit', global_dir/'audit', '--out', global_dir/'audit',
    '--retained-invoice', vendor/'evidence/audit/PREFIX-AND-INVOICE.json')
run('assembly', code/'assemble.py', source, global_dir, work/'ASSEMBLY.json')
if not args.discover:
    run('admission-controls', code/'assembly_controls.py', '--source-package', source,
        '--owner', global_dir/'audit/OWNERS-AND-PROFILE.json',
        '--invoice', global_dir/'audit/PREFIX-AND-INVOICE.json', '--out', work/'ADMISSION-CONTROLS.json')
    run('bit-supplier-controls', code/'bit_supplier_controls.py', '--source-package', source,
        '--owner', global_dir/'audit/OWNERS-AND-PROFILE.json',
        '--invoice', global_dir/'audit/PREFIX-AND-INVOICE.json', '--out', work/'BIT-SUPPLIER-CONTROLS.json')
    bit_controls = json.loads((work/'BIT-SUPPLIER-CONTROLS.json').read_text())
    assert bit_controls['status'] == 'PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS'
    assert len(bit_controls['rejected_controls']) == 12 and bit_controls['derived_deficit'] == 10272
result = json.loads((work/'ASSEMBLY.json').read_text())
dump(work/'REPLAY.json', dict(status='PASS_GAUGE44_DISCOVERY' if args.discover else 'PASS_GAUGE44_STRICT_GLOBAL_REPLAY',
                            kappa=result['kappa'], kappa_decimal=result['kappa_decimal'],
                            complex_lower=result['complex_lower'], bit_lower=result['bit_lower'],
                            bit_supplier=result['bit_supplier'],
                            gain_over_pr635_percent=result['gain_over_pr635_percent'],
                            spec_sha256=sha(PACKAGE/'data/SPEC.json'), stages=stages,
                            scope=result['scope']))
print(result['status'], result['kappa_decimal'], result['gain_over_pr635_percent'], flush=True)

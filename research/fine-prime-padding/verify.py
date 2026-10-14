"""Fresh signed-554 supplier admission and fine-prime padding composition.

Runs the pinned PR1699 default verifier without reuse flags. All generated
files are written beneath --work, never into the committed source packages.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
P = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--work', type=Path, required=True)
args = ap.parse_args()
work = args.work.resolve()
assert not work.exists() and not work.is_relative_to(P)
rd = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pins = rd(P/'SOURCE-PINS.json')
manifest = rd(P/'MANIFEST.json')
inventory = {f.relative_to(P).as_posix() for f in P.rglob('*')
             if f.is_file() and '__pycache__' not in f.parts and f != P/'MANIFEST.json'}
assert inventory == set(manifest), 'package inventory'
for rel, h in manifest.items():
    assert sha(P/rel) == h, rel
for rel, h in pins['pr1758']['files'].items():
    assert sha(P/'vendor/pr1758'/rel) == h, rel
supplier = (P/pins['dependency']['path']).resolve()
assert sha(supplier/'MANIFEST.json') == pins['dependency']['manifest_sha256']
assert (P/'inputs/SUPPLIER-SPEC.json').read_bytes() == (supplier/'data/SPEC.json').read_bytes()
assert not work.is_relative_to(supplier)

work.mkdir()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
           PYTHONUTF8='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
    env.pop(key, None)
stages = []

def run(name, script, *argv):
    start = time.monotonic()
    log = work/(name+'.log')
    with log.open('w') as f:
        result = subprocess.run([sys.executable, '-u', '-B', str(script),
                                 *map(str, argv)], cwd=work, env=env,
                                stdout=f, stderr=subprocess.STDOUT)
    stages.append(dict(name=name, exit_code=result.returncode,
                       seconds=time.monotonic()-start, log_sha256=sha(log)))
    (work/'STAGES.json').write_text(json.dumps(stages, indent=2)+'\n')
    assert result.returncode == 0, (name, log.read_text()[-6000:])
    print('PASS', name, flush=True)

run('fresh-pr1699-complete-supplier', supplier/'verify.py', '--work', work/'supplier')
finite = rd(work/'supplier/MATH.json')
result = rd(work/'supplier/RESULT.json')
assert finite['status'] == 'PASS_FRESH_SIGNED554_T74_CLASSICAL_MATRIX_COMPOSITION'
assert finite['native_reuse'] is False
assert finite['manifest_sha256'] == pins['dependency']['manifest_sha256']
assert len(result['stages']) == 18 and all(s['exit_code'] == 0 for s in result['stages'])
spec = rd(P/'inputs/SUPPLIER-SPEC.json')
assert finite['independent']['profile'] == spec['expected']['global_profile']
assert finite['independent']['live'] == spec['expected']['live'] == 66304
assert finite['traditional_kappa'] == spec['expected']['kappa']

source = P
P = work/'package'
shutil.copytree(source, P, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
P.chmod(0o755)
for f in P.rglob('*'):
    f.chmod(0o755 if f.is_dir() else 0o644)
run('retained-union-schedule', P/'vendor/pr1758/outer/sched_test.py')
assert 'PASS_UNION_SCHEDULE' in (work/'retained-union-schedule.log').read_text()
run('retained-union-review-exact-comparison', P/'check_schedule_exact.py')
assert 'PASS_RETAINED_UNION_REVIEW_EXACT_EQUALITY' in (work/'retained-union-review-exact-comparison.log').read_text()
run('fine-padding-controls', P/'check_fine_padding.py', '--out', work/'FINE-CONTROLS.json')
assert rd(work/'FINE-CONTROLS.json') == rd(source/'EXPECTED-FINE-CONTROLS.json')
run('retained-gaugefree-strengthened-checks', P/'check_gaugefree_strict.py')
assert 'PASS_STRICT_GAUGEFREE_REPLAY circuit cases 12 fine-theta symbol samples 64' in (work/'retained-gaugefree-strengthened-checks.log').read_text()
run('fine-padding-ledger', P/'check_ledger.py')
ledger = rd(P/'LEDGER.json')
assert ledger == rd(source/'LEDGER.json'), 'regenerated mathematical ledger'
run('separate-balance', P/'independent_balance.py', '--out', work/'BALANCE.json')
balance = rd(work/'BALANCE.json')
assert balance == rd(source/'EXPECTED-BALANCE.json'), 'separate mathematical derivation'
claim = rd(P/'CLAIM.json')
row = ledger['rows']['fine_prime_padding_strassen']
assert F(row['kappa']['rational']) == F(balance['kappa']) > F(claim['kappa'])
assert balance['headline'] == str(F(claim['kappa']))
assert ledger['complex_lower_pinned']['rational'] == spec['expected']['complex_lower']
assert ledger['profile'] == spec['expected']['global_profile']
assert ledger['m'] == 73 and ledger['W'] == 66304
assert len(row['strict_checks']) == 56
assert all(F(x['rational']) > 0 for x in row['strict_checks'].values())
assert len(ledger['rejecting_controls']['fine_prime_padding_strassen']) == 14

math = dict(status='PASS_FRESH_FINE_PRIME_PADDING_COMPOSITION',
            kappa=str(F(claim['kappa'])), kappa_decimal=claim['kappa'],
            manifest_sha256=sha(source/'MANIFEST.json'),
            source_pins=pins, finite_supplier=finite,
            fresh_supplier_math_sha256=sha(work/'supplier/MATH.json'),
            supplier_native_reuse=False, balance=balance,
            outer=row, geometry_changes=ledger['geometry_changes'],
            native_moment=ledger['native_moment'],
            rejecting_controls=ledger['rejecting_controls']['fine_prime_padding_strassen'],
            retained_schedule_exact_checks=4, retained_review_exact_checks=7,
            retained_gaugefree_circuit_cases=12, fine_theta_symbol_samples=64,
            fine_controls=rd(work/'FINE-CONTROLS.json'),
            scope=claim['scope'])
(work/'MATH.json').write_text(json.dumps(math, sort_keys=True, indent=2)+'\n')
(work/'RESULT.json').write_text(json.dumps(dict(status=math['status'],
    kappa=math['kappa'], kappa_decimal=math['kappa_decimal'], stages=stages,
    fresh_supplier_stages=18, math_sha256=sha(work/'MATH.json')),
    indent=2)+'\n')
for rel, h in manifest.items():
    assert sha(source/rel) == h, ('source modified', rel)
assert sha(supplier/'MANIFEST.json') == pins['dependency']['manifest_sha256']
print(math['status'], math['kappa_decimal'], flush=True)

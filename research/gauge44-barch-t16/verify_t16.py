"""Strict T16 replay: the T8 package's frozen admission, then the sixteen-replica two-bank controller.

Credit: the T16 controller, source adapters, direct-sum parent lift, actual-window reconstruction and the
independent T16 checker are Hao Yan's (@FanPUYen) PR #858 (research/complex-double-replica-owners, Apache-2.0),
vendored in t16/ with only the documented generalisations (word-derived widths/idle profile, owner-derived PLAN profile).

Stages (strict only, no discovery, no optimizer):
 restore-parent, bind8 (T8 SPEC data/T8/SPEC.json, T8 PLAN/OWNERS), build-owners (T8 owners duplicated into two
 interleaved groups + t16/MOVES.json whole-role moves; must equal data/OWNERS.json.gz), lift16 (direct-sum parent and
 actual source-event windows; PLAN must equal data/PLAN.json), bind, emit, audit, invoice, assembly, admission-controls,
 bit-supplier-controls (code/ = pinned gauge44 code + #858's exact multiplicity-checked T16 edits), independent-t16.
"""
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, time
from fractions import Fraction
from pathlib import Path

assert __debug__, 'Assertions required'
PKG = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rd = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--main', type=Path, required=True)
ap.add_argument('--local', type=Path, required=True)
ap.add_argument('--work', type=Path, required=True)
a = ap.parse_args()
main, local, work = a.main.resolve(), a.local.resolve(), a.work.resolve()
assert not work.exists(), 'Output directory must be new'
source = main / 'research/complex-k492-owner-repair/vendor/multicold'
baseline = main / 'research/community-k492-audit/pr622/replay/baseline558'
vendor = source / 'vendor/pr558/vendor/pr552/complex-global/vendor531'
for rel, expected in rd(PKG / 'data/UPSTREAM-PINS.json').items():
    assert sha(main / rel) == expected, 'Upstream dependency changed: ' + rel
work.mkdir(parents=True)
env0 = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
            MULTICOLD_SOURCE=str(source), GAIN_PR564_SOURCE=str(source))
for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
    env0.pop(k, None)
stages = []
SPEC8, SPEC16 = PKG / 'data/SPEC-T8.json', PKG / 'data/SPEC.json'
PLAN8, OWN8 = PKG / 'data/T8/PLAN.json', PKG / 'data/T8/OWNERS.json.gz'


def run(name, script, *args, spec=SPEC16, extra=None):
    t0 = time.monotonic()
    log = work / (name + '.log')
    with log.open('w') as s:
        rc = subprocess.run([sys.executable, '-B', str(source / 'code/run_portable.py'), str(script), *map(str, args)],
                            env=dict(env0, WITNESS_SPEC=str(spec), **(extra or {})), stdout=s, stderr=subprocess.STDOUT).returncode
    stages.append(dict(name=name, seconds=round(time.monotonic() - t0, 3), exit_code=rc, log_sha256=sha(log)))
    (work / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
    if rc:
        raise RuntimeError(name + ' failed:\n' + log.read_text()[-6000:])
    print('PASS', name, stages[-1]['seconds'], flush=True)


code, t16 = PKG / 'code', PKG / 't16'
run('restore-parent', code / 'restore_parent.py', '--source', source, '--baseline', baseline, '--out', work / 'parent558', spec=SPEC8)
run('bind8', code / 'bind_providers_portable.py', '--baseline', work / 'parent558', '--provider', 'gauge44=' + str(local),
    '--plan', PLAN8, '--out', work / 'global8', spec=SPEC8)
run('build-owners', t16 / 'own16.py', PLAN8, OWN8, work / 'OWNERS16.json.gz', t16 / 'MOVES.json',
    json.dumps(rd(SPEC16)['expected']['idle_remainder_profile']), spec=SPEC8)
assert rd(work / 'OWNERS16.json.gz') == rd(PKG / 'data/OWNERS.json.gz'), 'rebuilt T16 owners differ from data/OWNERS.json.gz'
run('lift16', t16 / 'lift16.py', work / 'global8/base', PLAN8, OWN8, PKG / 'data/OWNERS.json.gz', work / 'lift', spec=SPEC8)
assert rd(work / 'lift/PLAN.json') == rd(PKG / 'data/PLAN.json'), 'lifted PLAN differs from data/PLAN.json'
parent16 = work / 'parent16'
shutil.copytree(work / 'parent558', parent16)
shutil.copyfile(work / 'lift/GLOBAL-TEMPLATE.json.gz', parent16 / 'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
g = work / 'global'
run('bind', code / 'bind_providers_portable.py', '--baseline', parent16, '--provider', 'gauge44=' + str(local),
    '--plan', PKG / 'data/PLAN.json', '--out', g)
run('emit', code / 'emit_allcold.py', '--base', g / 'base', '--owners', PKG / 'data/OWNERS.json.gz', '--plan', g / 'PLAN.json', '--out', g / 'hosted')
run('audit', code / 'audit_allcold.py', g / 'base', g / 'hosted', g / 'audit/ASYNC-AUDIT.json', '--mutation-controls')
run('invoice', code / 'invoice_allcold.py', '--base', g / 'base', '--hosted', g / 'hosted', '--audit', g / 'audit',
    '--out', g / 'audit', '--retained-invoice', vendor / 'evidence/audit/PREFIX-AND-INVOICE.json')
run('assembly', code / 'assemble.py', source, g, work / 'ASSEMBLY.json')
for nm, sc, out in (('admission-controls', 'assembly_controls.py', 'ADMISSION-CONTROLS.json'),
                    ('bit-supplier-controls', 'bit_supplier_controls.py', 'BIT-SUPPLIER-CONTROLS.json')):
    run(nm, code / sc, '--source-package', source, '--owner', g / 'audit/OWNERS-AND-PROFILE.json',
        '--invoice', g / 'audit/PREFIX-AND-INVOICE.json', '--out', work / out)
lift = rd(work / 'lift/PARENT-LIFT-RECEIPT.json')
run('independent-t16', t16 / 'indep16.py', '--baseline-parent', work / 'global8/base/split-centres/GLOBAL-TEMPLATE.json.gz',
    '--owners', PKG / 'data/OWNERS.json.gz', '--word', local / 'CANONICAL-WORD.json.gz', '--out', work / 'INDEPENDENT-T16.json',
    extra={'T16_EXPECTED_IDLE': json.dumps(rd(SPEC16)['expected']['idle_remainder_profile']),
           'T16_EXPECTED_WIDTHS': json.dumps(rd(SPEC16)['providers']['gauge44']['inventory'])})
asm, ind = rd(work / 'ASSEMBLY.json'), rd(work / 'INDEPENDENT-T16.json')
inv = rd(g / 'audit/PREFIX-AND-INVOICE.json')
bc, ac = rd(work / 'BIT-SUPPLIER-CONTROLS.json'), rd(work / 'ADMISSION-CONTROLS.json')
assert asm['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and asm['kappa'] == rd(SPEC16)['expected']['kappa']
assert bc['status'] == 'PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS' and len(bc['rejected_controls']) == 12 and bc['derived_deficit'] == 10272
assert not ac['discovery_accepted_controls'] and len(ac['rejected_controls']) == 69
assert ind['status'] == 'PASS_INDEPENDENT_T16_LITERAL_WINDOWS_CHARTS_PREFIX_ROW' and len(ind['controls_rejected']) == 6
assert ind['profile'] == asm['complex_profile'] and {str(k): v for k, v in lift['idle16'].items()} == {str(k): v for k, v in ind['idle'].items()}
assert ind['prefix_bits'] == inv['global_prefix_bits'] < 512 and ind['physical_row_coefficient'] < 20161
# Final binding (as #858 verify.py final_binding).
owner, audit = rd(g / 'audit/OWNERS-AND-PROFILE.json'), rd(g / 'audit/ASYNC-AUDIT.json')
assert ind['physical_row_coefficient'] == inv['finite']['physical_row_coefficient'] < inv['finite']['retained_row_coefficient'] == 20161
assert inv['charged_prefix_bits'] == 512
assert ind['rank_mass'] == owner['rank_mass'] == 1041408 and ind['deficit'] == owner['deficit'] == 5120
assert inv['strict_checks'] and all(inv['strict_checks'].values()), 'every finite invoice inequality'
assert len(asm['outer']) == 47 and all(Fraction(v) > 0 for v in asm['outer'].values()), 'all 47 strict outer margins'
assert audit['mutation_controls_run'] and len(audit['mutations_rejected']) == 15
assert ind['roles'] == owner['hosted_residuals'] == audit['complex_hosted_residuals'] == 72576
assert ind['calls'] == audit['complete_invocations'] == inv['complete_invocation_sweeps'] == 144
assert ind['actual_73_axis_charts'] == owner['actual_73column_sigmas'] == audit['actual_orthogonal_73column_maps']
assert lift['actual_window_membership_checked'] == 72576 and lift['T8_identity_control'] and lift['T8_source_window_identity']
for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json', 'INDEPENDENT-LOCAL-REPLAY.json',
             'RESIDUAL-ADAPTERS.json', 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json'):
    assert rd(g / 'base/providers/gauge44' / name) == rd(local / name), 'provider content binding: ' + name
assert asm['template_sha256'] == owner['template_sha256'] == inv['template_sha256']
assert inv['owner_audit_sha256'] == sha(g / 'audit/OWNERS-AND-PROFILE.json') and inv['controller_audit_sha256'] == sha(g / 'audit/ASYNC-AUDIT.json')
assert Fraction(asm['kappa']) > Fraction(rd(SPEC8)['expected']['kappa']), 'T16 must strictly improve the T8 package'
res = dict(status='PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY', kappa=asm['kappa'], kappa_decimal=asm['kappa_decimal'],
           conservative_kappa_decimal=asm['conservative_kappa_decimal'], complex_lower=asm['complex_lower'], bit_lower=asm['bit_lower'],
           complex_profile=asm['complex_profile'], idle_remainder_profile=ind['idle'], complete_invocations=144, roles=ind['roles'],
           prefix_bits=ind['prefix_bits'], charged_prefix_bits=512, physical_row_coefficient=ind['physical_row_coefficient'],
           retained_row_coefficient=20161, actual_73_axis_charts=ind['actual_73_axis_charts'],
           controls=dict(admission=69, bit_supplier=12, independent_t16=6, controller_mutations=15),
           t8_kappa=rd(SPEC8)['expected']['kappa'], spec_sha256=sha(SPEC16), stages=stages, scope=asm['scope'])
(work / 'REPLAY.json').write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], res['kappa_decimal'], flush=True)

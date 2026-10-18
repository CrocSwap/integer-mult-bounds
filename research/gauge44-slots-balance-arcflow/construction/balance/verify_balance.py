#!/usr/bin/env python3
"""Partner-balance layer on the seven-slot k8 word, with explicit, hash-checked reuse of a completed
research/gauge44-slots-arcflow replay (the pattern of research/gauge44-slots's verify_slots.py).

  1. parent manifest, then baseline: the completed research/gauge44-slots-arcflow verify_slots.py --work directory; its
     slot word must equal the recipe's base pin and its step receipt must be complete.
  2. apply: apply_balance.py (standard library) restores fourteen dimension-four entrance frames, sets ten seven-dimensional
     end frames and the 86 recorded gate frames; the output is pinned. Four mutants are built and each must be rejected by
     the independent audit_local.py (frame not monotone three times, paid-profile mismatch once).
  3. native locals of the new word (the chain's steps); canonical/programs/Clifford pinned.
  4. independent audit_local on the new word.
  5. strict global replay (verify_global.py) of this package's data (the new whole-owner map) on the new locals.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
BASE_STEPS = ['parent-manifest', 'slots', 'slot-controls', 'native', 'ledgers', 'local-replay', 'wrappers', 'phases', 'audit-local', 'strict']


def read(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)


def csha(p): return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True, help='repository root')
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--baseline', type=Path, required=True,
                    help='completed research/gauge44-slots-arcflow construction/slots/verify_slots.py --work directory')
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    root = a.main.resolve(); work = a.work.resolve(); assert not work.exists(); work.mkdir(parents=True)
    parent_pkg = root / 'research/gauge44-slots-arcflow'
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = root / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; par = base / 'vendor/pr552'
    routing = par / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    env.pop('PYTHONOPTIMIZE', None)
    pins = read(HERE / 'BALANCE-PINS-k8.json'); recipe = HERE / 'RECIPE-BALANCE-k8.json'; r = read(recipe); steps = []

    def run(label, script, *args, portable=True, expect_fail=False):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (work / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, cwd=root)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3), expected_failure=expect_fail))
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert (rc != 0) if expect_fail else (rc == 0), label
        print('PASS', label, '(rejected as required)' if expect_fail else '', flush=True)
        return (work / (label + '.log')).read_text()

    # 1. parent package and baseline coverage
    run('parent-manifest', parent_pkg / 'verify_manifest.py', portable=False)
    bl = a.baseline.resolve(); bw = bl / 'slots/FULL-WORD.json.gz'
    bsteps = read(bl / 'STEPS.json')
    assert [s['step'] for s in bsteps] == BASE_STEPS and all(s['exit_code'] == 0 for s in bsteps), 'baseline is not a complete research/gauge44-slots-arcflow replay'
    assert read(bl / 'RESULT.json')['status'] == 'PASS_ARCFLOW_OWNERS_ON_CHECKED_K8_SLOT_BASELINE'
    assert csha(bw) == r['base_sha256'] == pins['base_sha256'], 'baseline slot word'
    print('PASS baseline', flush=True)

    # 2. apply the recipe; mutants must be rejected by the independent audit
    (work / 'word').mkdir(); fw = work / 'word/FULL-WORD.json.gz'
    run('apply', HERE / 'apply_balance.py', bw, recipe, fw, portable=False)
    assert csha(fw) == r['expect_sha256'] == pins['word_sha256'], 'balanced word pin'
    for m in pins['mutants']:
        mw = work / ('word/mutant-%s.json.gz' % m)
        run('mutant-' + m, HERE / 'apply_balance.py', bw, recipe, mw, '--mutant=' + m, portable=False)
        run('mutant-%s-audit' % m, parent_pkg / 'independent/audit_local.py', '--word', mw, '--main', root,
            '--output', work / ('MUTANT-%s.json' % m), portable=False, expect_fail=True)

    # 3. native locals of the new word
    local = work / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', fw, '--routing', routing, '--out', local)
    assert csha(local / 'CANONICAL-WORD.json.gz') == pins['canonical_sha256']
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz', local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    chk = read(local / 'LOCAL-CHECKS.json')
    assert {o: chk[o]['sha256'] for o in ('forward', 'backward')} == pins['program_sha256']
    assert chk['forward']['paid_profile'] == r['expected_profile'], 'paid profile'
    run('phases', base / 'code/phases_full.py', local, par / 'complex-global/vendor531/vendor/clifford')
    assert fsha(local / 'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256']

    # 4. independent local audit; 5. strict global replay of this package's data
    run('audit-local', PKG / 'independent/audit_local.py', '--word', fw, '--main', root, '--output', work / 'AUDIT-LOCAL.json', portable=False)
    assert read(work / 'AUDIT-LOCAL.json')['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'
    out = run('strict', PKG / 'verify_global.py', '--main', root, '--local', local, '--work', work / 'global', portable=False)
    last = [l for l in out.splitlines() if l.startswith('PASS_GAUGE44')][-1]
    assert last.split()[1] == pins['kappa_decimal'], last
    res = dict(status='PASS_BALANCE_ARCFLOW_ON_CHECKED_SLOT_BASELINE', kappa_decimal=pins['kappa_decimal'], strict=last,
               baseline=str(bl), steps=steps)
    (work / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
    print(res['status'], pins['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

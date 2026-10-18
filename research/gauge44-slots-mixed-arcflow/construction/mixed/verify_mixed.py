#!/usr/bin/env python3
"""Two-provider layer on the seven-slot k8 word, with explicit, hash-checked reuse of a completed
research/gauge44-slots-arcflow replay (the pattern of research/gauge44-slots's verify_slots.py).

  1. parent manifest, then baseline: the completed research/gauge44-slots-arcflow verify_slots.py --work directory; its
     slot word must equal the recipes' base pin and its step receipt must be complete.
  2. apply: apply_mixed.py (standard library) builds both provider words from the slot word: gauge44r16 (sixteen restored
     entrances, ten deepened ends: research/gauge44-slots-deepen-arcflow's word) and gauge44r12 (twelve restored entrances,
     ten deepened ends); both outputs are pinned. Four mutants of the gauge44r12 recipe are built and each must be rejected
     by the independent audit_local.py (frame not monotone three times, paid-profile mismatch once).
  3. native locals of both words (the chain's steps); canonical/programs/Clifford pinned per provider.
  4. independent audit_local on both words.
  5. strict global replay (verify_global.py) of this package's two-provider data on the two locals.
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
    pins = read(HERE / 'MIXED-PINS-k8.json'); steps = []
    recipes = {pid: HERE / ('RECIPE-%s-k8.json' % pid[-3:].upper()) for pid in ('gauge44r16', 'gauge44r12')}
    r = {pid: read(p) for pid, p in recipes.items()}

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
    assert all(csha(bw) == r[pid]['base_sha256'] for pid in r) and csha(bw) == pins['base_sha256'], 'baseline slot word'
    print('PASS baseline', flush=True)

    # 2. apply both recipes; mutants of the gauge44r12 recipe must be rejected by the independent audit
    (work / 'word').mkdir(); fw = {}
    for pid, rec in recipes.items():
        fw[pid] = work / ('word/%s.json.gz' % pid)
        run('apply-' + pid, HERE / 'apply_mixed.py', bw, rec, fw[pid], portable=False)
        assert csha(fw[pid]) == r[pid]['expect_sha256'] == pins['providers'][pid]['word_sha256'], pid + ' word pin'
    for m in pins['mutants']:
        mw = work / ('word/mutant-%s.json.gz' % m)
        run('mutant-' + m, HERE / 'apply_mixed.py', bw, recipes['gauge44r12'], mw, '--mutant=' + m, portable=False)
        run('mutant-%s-audit' % m, parent_pkg / 'independent/audit_local.py', '--word', mw, '--main', root,
            '--output', work / ('MUTANT-%s.json' % m), portable=False, expect_fail=True)

    # 3. native locals of both words; 4. independent audits
    local = {}
    for pid in recipes:
        local[pid] = work / ('local-' + pid); pp = pins['providers'][pid]
        run('native-' + pid, up / 'code/hpe_audit_and_transport.py', '--raw', fw[pid], '--routing', routing, '--out', local[pid])
        assert csha(local[pid] / 'CANONICAL-WORD.json.gz') == pp['canonical_sha256']
        run('ledgers-' + pid, up / 'code/hpe_emit_local.py', local[pid])
        run('local-replay-' + pid, up / 'code/hpe_audit_local.py', local[pid])
        run('wrappers-' + pid, up / 'code/hpe_adapters_local.py', local[pid] / 'CANONICAL-WORD.json.gz', local[pid] / 'RESIDUAL-ADAPTERS.json', local[pid] / 'WRAPPER-CHECKS.json')
        chk = read(local[pid] / 'LOCAL-CHECKS.json')
        assert {o: chk[o]['sha256'] for o in ('forward', 'backward')} == pp['program_sha256']
        assert chk['forward']['paid_profile'] == r[pid]['expected_profile'], 'paid profile ' + pid
        run('phases-' + pid, base / 'code/phases_full.py', local[pid], par / 'complex-global/vendor531/vendor/clifford')
        assert fsha(local[pid] / 'CLIFFORD-RECIPES.json') == pp['clifford_recipes_sha256']
        run('audit-local-' + pid, PKG / 'independent/audit_local.py', '--word', fw[pid], '--main', root, '--output', work / ('AUDIT-LOCAL-%s.json' % pid), portable=False)
        assert read(work / ('AUDIT-LOCAL-%s.json' % pid))['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'

    # 5. strict global replay of this package's two-provider data
    out = run('strict', PKG / 'verify_global.py', '--main', root, '--local-r16', local['gauge44r16'], '--local-r12', local['gauge44r12'], '--work', work / 'global', portable=False)
    last = [l for l in out.splitlines() if l.startswith('PASS_GAUGE44')][-1]
    assert last.split()[1] == pins['kappa_decimal'], last
    res = dict(status='PASS_MIXED_TWO_PROVIDER_ARCFLOW_ON_CHECKED_SLOT_BASELINE', kappa_decimal=pins['kappa_decimal'], strict=last,
               baseline=str(bl), steps=steps)
    (work / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
    print(res['status'], pins['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

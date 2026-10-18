#!/usr/bin/env python3
"""Slot layer on research/gauge44-leaver8 with explicit, hash-checked reuse of a completed k8 chain replay.

Follows the repository's baseline-reuse pattern (cf. research/complex-t37-owners/verify.py --baseline799):
the completed k8 replay is rechecked against the parent package's pins, and only the new layer is rebuilt.

  1. parent manifest, then baseline: the completed reproduce_leaver_chain.py --id k8 output; its final word and its
     canonical/program/Clifford locals must equal CHAIN-PINS-k8 and the final frame recipe's output pin.
  2. slots: the reviewed construction/barch/build_tri.py (unchanged) with RECIPE-SLOTS-k8.json; output pinned.
     All per-slot controls (run_controls.py, unchanged) must reject exactly as pinned.
  3. native locals of the new word (the same steps as reproduce_leaver_chain step 9); canonical/programs/Clifford pinned.
  4. independent audit_local on the new word.
  5. strict global replay (verify_global.py) of this package's data on the new locals.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
MUTANTS = ('drop_restore', 'restore_full', 'drop_preread', 'donation_after')  # as reproduce_leaver_chain.py
# Complete step receipt of reproduce_leaver_chain.py --id k8 (unchanged driver of the parent package).
CHAIN_STEPS = ['pivot-swap', 'cold44-exact', 'lec-p6n', 'promotion', 'promo-controls', 'lec-promo', 'jx',
               'jx-control-C0_identity', 'jx-control-C1_741_only', 'jx-control-N3_plain_join_moved_reads', 'lec-jx',
               'hybrids', 'hybrid-controls', 'lec-hyb', 'frames', 'lec-frames',
               'native', 'ledgers', 'local-replay', 'wrappers', 'phases']


def read(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()
def csha(p): return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True, help='repository root')
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--baseline', type=Path, required=True,
                    help='completed research/gauge44-leaver8 reproduce_leaver_chain.py --id k8 --out directory')
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    root = a.main.resolve(); work = a.work.resolve(); assert not work.exists(); work.mkdir(parents=True)
    parent_pkg = root / 'research/gauge44-leaver8'
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = root / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; par = base / 'vendor/pr552'
    routing = par / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    env.pop('PYTHONOPTIMIZE', None)
    pins = read(HERE / 'SLOT-PINS-k8.json'); steps = []

    def run(label, script, *args, portable=True):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (work / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, cwd=root)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)
        return (work / (label + '.log')).read_text()

    # 1. parent package and baseline coverage
    run('parent-manifest', parent_pkg / 'verify_manifest.py', portable=False)
    cp = read(parent_pkg / 'construction/leaver/CHAIN-PINS-k8.json')
    fr = read(parent_pkg / 'construction/leaver/FRAME-RECIPE-LV-k8.json')
    bl = a.baseline.resolve(); bw = bl / 'frames/FULL-WORD.json.gz'; blocal = bl / 'local'
    bsteps = read(bl / 'STEPS.json')
    assert [s['step'] for s in bsteps] == CHAIN_STEPS and all(s['exit_code'] == 0 for s in bsteps), 'baseline is not a complete k8 chain replay'
    assert csha(bw) == fr['expected']['output_content_sha256'] == pins['base_sha256'], 'baseline final word'
    assert hashlib.sha256(gzip.decompress((blocal / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest() == cp['canonical_sha256'], 'baseline canonical'
    chk = read(blocal / 'LOCAL-CHECKS.json')
    assert {o: chk[o]['sha256'] for o in ('forward', 'backward')} == cp['program_sha256'], 'baseline programs'
    assert fsha(blocal / 'CLIFFORD-RECIPES.json') == cp['clifford_recipes_sha256'], 'baseline Clifford'
    for lab in ('lec-p6n', 'lec-promo', 'lec-jx', 'lec-hyb', 'lec-frames'):
        c = read(bl / lab / 'COLD-END-CONTROLS.json')
        assert c['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(c['rejected']) == cp[lab], 'baseline ' + lab
    print('PASS baseline', flush=True)

    # 2. slot layer with the reviewed builder and controls (unchanged files from research/gauge44-leaver8)
    barch = parent_pkg / 'construction/barch'; rec = HERE / 'RECIPE-SLOTS-k8.json'; r = read(rec)
    assert r['base_sha256'] == pins['base_sha256'] and r['expect_sha256'] == pins['word_sha256']
    (work / 'slots').mkdir(); fw = work / 'slots/FULL-WORD.json.gz'
    run('slots', barch / 'build_tri.py', bw, rec, fw, portable=False)
    assert csha(fw) == pins['word_sha256'], 'slot word'
    run('slot-controls', barch / 'run_controls.py', bw, rec, parent_pkg / 'independent/audit_local.py', work / 'slot-controls', portable=False)
    res = read(work / 'slot-controls/controls.json')
    want = ['C0_identity', 'recipe', *MUTANTS] + [m + '@' + str(v['X']) for v in r.get('variants', []) for m in MUTANTS]
    assert sorted(res) == sorted(want) == sorted(pins['slot_controls']) and all(x['ok'] for x in res.values()), res

    # 3. native locals of the new word
    local = work / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', fw, '--routing', routing, '--out', local)
    assert hashlib.sha256(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest() == pins['canonical_sha256']
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz', local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    chk = read(local / 'LOCAL-CHECKS.json')
    assert {o: chk[o]['sha256'] for o in ('forward', 'backward')} == pins['program_sha256']
    run('phases', base / 'code/phases_full.py', local, par / 'complex-global/vendor531/vendor/clifford')
    assert fsha(local / 'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256']

    # 4. independent local audit; 5. strict global replay of this package's data
    run('audit-local', PKG / 'independent/audit_local.py', '--word', fw, '--main', root, '--output', work / 'AUDIT-LOCAL.json', portable=False)
    assert read(work / 'AUDIT-LOCAL.json')['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'
    out = run('strict', PKG / 'verify_global.py', '--main', root, '--local', local, '--work', work / 'global', portable=False)
    last = [l for l in out.splitlines() if l.startswith('PASS_GAUGE44')][-1]
    assert last.split()[1] == pins['kappa_decimal'], last
    res = dict(status='PASS_SLOTS_ON_CHECKED_K8_BASELINE', kappa_decimal=pins['kappa_decimal'], strict=last,
               baseline=str(bl), steps=steps)
    (work / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
    print(res['status'], pins['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

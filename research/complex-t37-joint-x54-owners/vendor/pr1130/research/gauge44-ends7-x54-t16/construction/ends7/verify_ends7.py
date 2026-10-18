#!/usr/bin/env python3
"""Rebuild rank-seven ends574/575 AND the eighth triangle slot X54 on the checked seven-slot k8 baseline.

The completed baseline replay is hash-checked. Ends7 is rebuilt and its dual-auditor controls run on that intermediate
word. Then the pinned post-ends7 X54 recipe is applied with the unchanged triangle builder and all ten X54 controls
are checked. Native transport, ledgers, replay, wrappers, exact phases, independent audit and PR1049's full leaver
premise are checked against COMPOSITE pins. Strict T8 and T16 both run on the rebuilt composite locals and frozen data.
The CLI is retained for autoship dispatch, but the final marker explicitly identifies the eight-slot construction.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
FASTPATH = HERE / 'fastpath/phases_fast.py'  # PR1029 sparse exact evaluator driver (FastPhases)
BASE_STEPS = ['parent-manifest', 'slots', 'slot-controls', 'native', 'ledgers', 'local-replay', 'wrappers', 'phases',
              'audit-local', 'strict']


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
    ap.add_argument('--baseline', type=Path, required=True, help='completed verify_slots[_fast].py --work directory')
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--phases', choices=('sparse', 'reference'), default='sparse')
    ap.add_argument('--fastpath', type=Path, default=FASTPATH, help="FastPhases' fastpath/phases_fast.py (PR1029 driver)")
    ap.add_argument('--phase-jobs', type=int, default=4)
    a = ap.parse_args()
    root = a.main.resolve(); work = a.work.resolve(); assert not work.exists(); work.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = root / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; par = base / 'vendor/pr552'
    routing = par / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    env.pop('PYTHONOPTIMIZE', None)
    sp = read(PKG / 'construction/slots/SLOT-PINS-k8.json'); epins = read(HERE / 'ENDS7-PINS-k8.json')
    pins = read(HERE / 'x54/X54-PINS.json'); steps = []

    def run(label, script, *args, portable=True):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (work / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, cwd=root,
                                 creationflags=0x08000000 if os.name == 'nt' else 0)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)
        return (work / (label + '.log')).read_text()

    # 1. baseline: completed slot replay
    bl = a.baseline.resolve(); bw = bl / 'slots/FULL-WORD.json.gz'; blocal = bl / 'local'
    bsteps = read(bl / 'STEPS.json')
    assert [s['step'] for s in bsteps] == BASE_STEPS and all(s['exit_code'] == 0 for s in bsteps), 'baseline is not a complete slot replay'
    assert csha(bw) == sp['word_sha256'] == epins['base_sha256'], 'baseline slot word'
    assert csha(blocal / 'CANONICAL-WORD.json.gz') == sp['canonical_sha256'], 'baseline canonical'
    chk = read(blocal / 'LOCAL-CHECKS.json')
    assert {o: chk[o]['sha256'] for o in ('forward', 'backward')} == sp['program_sha256'], 'baseline programs'
    assert fsha(blocal / 'CLIFFORD-RECIPES.json') == sp['clifford_recipes_sha256'], 'baseline Clifford'
    assert read(bl / 'RESULT.json')['status'] == 'PASS_SLOTS_ON_CHECKED_K8_BASELINE'
    print('PASS baseline', flush=True)

    # 2. rank-seven ends and their controls
    rec = HERE / 'RECIPE-ENDS7-k8.json'; r = read(rec)
    assert r['input_sha256'] == epins['base_sha256'] and r['expected']['output_sha256'] == epins['word_sha256']
    assert [e[0] for e in r['ends']] == epins['helpers']
    (work / 'ends7').mkdir(); ew = work / 'ends7/FULL-WORD.json.gz'
    run('ends7', HERE / 'build_ends7.py', bw, rec, ew, portable=False)
    assert csha(ew) == epins['word_sha256'] == pins['base_sha256'], 'intermediate ends7 word'
    run('ends7-controls', HERE / 'end7_controls.py', bw, rec, PKG / 'independent/audit_local.py',
        up / 'code/hpe_audit_and_transport.py', src / 'code/run_portable.py', routing, work / 'ends7-controls', portable=False)
    c = read(work / 'ends7-controls/END7-CONTROLS.json')
    assert c['status'] == 'PASS_RANK7_END_CONTROLS' and c['rejections'] == epins['control_rejections'], c['status']

    # Explicit eighth slot; never pass the intermediate ends7 word as the final construction.
    xr = HERE / 'x54/RECIPE-X54-ends7.json'; recipe = read(xr)
    assert recipe['base_sha256'] == pins['base_sha256'] and recipe['expect_sha256'] == pins['word_sha256']
    assert recipe['variants'] == [{'X': 54, 'E': 589, 'hold': [335, 367]}]
    assert recipe['local_profile'] == pins['local_profile']
    (work / 'x54').mkdir(); fw = work / 'x54/FULL-WORD.json.gz'
    run('x54', HERE / 'x54/build_tri.py', ew, xr, fw, portable=False)
    assert csha(fw) == pins['word_sha256'], 'composite word'
    run('x54-controls', HERE / 'x54/run_controls.py', ew, xr, PKG / 'independent/audit_local.py',
        work / 'x54-controls', portable=False)
    xc = read(work / 'x54-controls/controls.json')
    assert len(xc) == pins['control_cases'] and all(case['ok'] for case in xc.values()), 'X54 controls'

    # 3. native locals of the new word
    local = work / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', fw, '--routing', routing, '--out', local)
    assert csha(local / 'CANONICAL-WORD.json.gz') == pins['canonical_sha256']
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz', local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    chk = read(local / 'LOCAL-CHECKS.json')
    assert {o: chk[o]['sha256'] for o in ('forward', 'backward')} == pins['program_sha256']
    if a.phases == 'reference':
        run('phases', base / 'code/phases_full.py', local, par / 'complex-global/vendor531/vendor/clifford')
    else:
        run('phases', a.fastpath.resolve(), local, par / 'complex-global/vendor531/vendor/clifford',
            root / 'research/clifford-state-performance/fast_state.py', max(1, a.phase_jobs))
    assert fsha(local / 'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256']

    # 4. independent local audit and PR1049's leaver premise on the new word
    run('audit-local', PKG / 'independent/audit_local.py', '--word', fw, '--main', root, '--output', work / 'AUDIT-LOCAL.json', portable=False)
    assert read(work / 'AUDIT-LOCAL.json')['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'
    out = run('leaver-premise', HERE / 'premise/premise_check.py', fw, portable=False)
    lp = json.loads(out.strip().splitlines()[-1])
    assert lp['status'] == 'PASS_LEAVER_PREMISE' and lp['cells'] == 8 and lp['paid_profile'] == pins['local_profile'], lp

    # 5. strict replay of this package's data on the new locals: T8 (verify_global.py) or, in a T16 package, verify_t16.py
    gpkg = PKG
    if (PKG / 'data/T8').is_dir():  # T16 package: strict T8 = research/gauge44-slots (#1018, the T8 admission code) with
        import shutil               # this package's frozen T8 data (data/T8 + data/SPEC-T8.json) swapped in
        gpkg = work / 't8-view'
        shutil.copytree(root / 'research/gauge44-slots', gpkg, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(PKG / 'construction', gpkg / 'construction', dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__'))
        for f in ('PLAN.json', 'OWNERS.json.gz'): shutil.copyfile(PKG / 'data/T8' / f, gpkg / 'data' / f)
        shutil.copyfile(PKG / 'data/SPEC-T8.json', gpkg / 'data/SPEC.json')
    out = run('strict', gpkg / 'verify_global.py', '--main', root, '--local', local, '--work', work / 'global', portable=False)
    last = [l for l in out.splitlines() if l.startswith('PASS_GAUGE44')][-1]
    assert last.split()[1] == pins['kappa_decimal'], last
    kd8 = pins['kappa_decimal']
    run('strict-t16', PKG / 'verify_t16.py', '--main', root, '--local', local,
        '--work', work / 't16', portable=False)
    t16 = read(work / 't16/REPLAY.json')
    assert t16['kappa_decimal'] == pins['kappa_t16_decimal'], 'composite T16 kappa'
    kd = pins['kappa_t16_decimal']
    res = dict(status='PASS_RANK7_ENDS_AND_X54_ON_CHECKED_SLOT_BASELINE', kappa_decimal=kd,
               kappa_t8_decimal=kd8, strict=last, word_sha256=pins['word_sha256'],
               baseline=str(bl), steps=steps)
    (work / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
    print(res['status'], kd, flush=True)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Rebuild the U10 word (two further triangle-hybrid B deliveries on PR869's U8 word) and its native locals.

Input: the U8 word written by the vendored PR870 driver (`native/barch/FULL-WORD.json.gz`, content 090fd574...).
Steps, each checked exactly:
  1. u10: NewBArch's unchanged standard-library builder `build_tri.py` applies RECIPE-U10.json (explicit B deletes and
     inserts with frames, two early-cleanup tails and two FULL-cleanup restores); base and result shas are checked.
  2. u10-controls: NewBArch's unchanged `run_controls.py` rebuilds C0 (identity), the recipe word (must PASS the
     independent audit_local.py) and the four mutants globally and per new slot (X = 444, 446); 14 outcomes, all required.
  3. layer-end-controls, native, ledgers, local-replay, wrappers, phases: PR635's native local programs, exactly as
     in the PR870 driver.
Apache-2.0.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
T21 = PKG.parents[1]/'research/complex-t21-owners'
BARCH = T21/'vendor/pr870/construction/barch'
P6 = T21/'vendor/pr870/construction/layers_p6n'
MUTANTS = ('drop_restore', 'restore_full', 'drop_preread', 'donation_after')


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--u8-word', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve()/'research/complex-571-cold14-st2'
    src = a.main.resolve()/'research/complex-k492-owner-repair/vendor/multicold'
    base = src/'vendor/pr558'; parent = base/'vendor/pr552'
    rfile = HERE/'RECIPE-U10.json'; rec = read(rfile); pins = read(HERE/'LOCAL-PINS-U10.json')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE'): env.pop(k, None)
    steps = []

    def run(label, script, *args, portable=True):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src/'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (out/(label+'.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic()-t, 3)))
        (out/'STEPS.json').write_text(json.dumps(steps, indent=2)+'\n')
        assert rc == 0, label
        print('PASS', label, flush=True)

    inp = a.u8_word.resolve()
    assert hashlib.sha256(gzip.decompress(inp.read_bytes())).hexdigest() == rec['base_sha256'], 'input must be the pinned U8 word'
    (out/'u10').mkdir(); word = out/'u10/FULL-WORD.json.gz'
    run('u10', BARCH/'build_tri.py', inp, rfile, word, portable=False)
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == rec['expect_sha256']
    run('u10-controls', BARCH/'run_controls.py', inp, rfile, T21/'vendor/pr870/independent/audit_local.py', out/'u10-controls', portable=False)
    res = read(out/'u10-controls/controls.json')
    want = ['C0_identity', 'recipe', *MUTANTS] + [m+'@'+str(v['X']) for v in rec['variants'] for m in MUTANTS]
    assert sorted(res) == sorted(want) == sorted(pins['u10_controls']) and all(x['ok'] for x in res.values()), res
    routing = parent/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up/'code')
    run('layer-end-controls', P6/'layer_end_controls.py', word, routing, out/'controls')
    env.pop('PR635_CODE')
    ctl = read(out/'controls/COLD-END-CONTROLS.json')
    assert ctl['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ctl['rejected']) == pins['layer_controls'], len(ctl['rejected'])
    local = out/'local'
    run('native', up/'code/hpe_audit_and_transport.py', '--raw', word, '--routing', routing, '--out', local)
    if pins.get('canonical_sha256'):
        assert hashlib.sha256(gzip.decompress((local/'CANONICAL-WORD.json.gz').read_bytes())).hexdigest() == pins['canonical_sha256'], 'canonical word'
    run('ledgers', up/'code/hpe_emit_local.py', local)
    run('local-replay', up/'code/hpe_audit_local.py', local)
    run('wrappers', up/'code/hpe_adapters_local.py', local/'CANONICAL-WORD.json.gz',
        local/'RESIDUAL-ADAPTERS.json', local/'WRAPPER-CHECKS.json')
    checks = read(local/'LOCAL-CHECKS.json')
    for o, s in pins.get('program_sha256', {}).items(): assert checks[o]['sha256'] == s, ('local program', o)
    run('phases', base/'code/phases_full.py', local, parent/'complex-global/vendor531/vendor/clifford')
    if pins.get('clifford_recipes_sha256'):
        assert hashlib.sha256((local/'CLIFFORD-RECIPES.json').read_bytes()).hexdigest() == pins['clifford_recipes_sha256'], 'clifford recipes'
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()

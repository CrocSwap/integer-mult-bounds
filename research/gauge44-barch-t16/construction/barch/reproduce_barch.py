#!/usr/bin/env python3
"""Rebuild the B0 word (NewBArch's width-neutral triangle-hybrid B-delivery rewrite on X4) and its native locals.

Input: a fresh `construction/jx/reproduce_jx.py` output directory; its X4 word (1e1d99ba...) is pinned there and by
RECIPE-B0.json (base_sha256). Steps, each checked exactly:
  1. barch: build_tri.py (standard library only; NewBArch) applies the recipe's explicit B deletes and inserts (with frames),
     re-chosen B frames, early-cleanup tails and FULL-cleanup restores; it checks the base and result shas (d9ba0942...).
  2. barch-controls: run_controls.py rebuilds C0 (identity, must reproduce the input), the recipe word (must PASS #645's
     independent audit_local.py) and four mutants (drop_restore, restore_full, drop_preread, donation_after), globally
     and for each recipe variant (NAME@X); each mutant must FAIL audit_local with its pinned message. Every outcome is
     required and the control set is pinned (LOCAL-PINS).
  3. layer-end-controls: ../layers_p6n/layer_end_controls.py (per-end variant) on the B0 word; count pinned.
  4. native, ledgers, local-replay, wrappers, phases: PR635's native local programs; canonical word, local programs and
     Clifford recipes pinned (LOCAL-PINS-barch-<id>.json).
Apache-2.0. Driver by ColdWitness around NewBArch's builder and controls.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
P6 = HERE.parent / 'layers_p6n'
MUTANTS = ('drop_restore', 'restore_full', 'drop_preread', 'donation_after')


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--jx-dir', type=Path, required=True, help='construction/jx/reproduce_jx.py output')
    ap.add_argument('--recipe', default='U8', help='RECIPE-<id>.json and LOCAL-PINS-barch-<id>.json')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'
    rfile = HERE / ('RECIPE-%s.json' % a.recipe); rec = read(rfile); pins = read(HERE / ('LOCAL-PINS-barch-%s.json' % a.recipe))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE'): env.pop(k, None)
    steps = []

    def run(label, script, *args, portable=True):
        t = time.monotonic()
        cmd = [sys.executable, '-B'] + ([str(src / 'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (out / (label + '.log')).open('w') as f:
            rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (out / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)

    inp = a.jx_dir.resolve() / 'jx/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(inp.read_bytes())).hexdigest() == rec['base_sha256'], 'input must be the pinned X4 word'
    (out / 'barch').mkdir(); word = out / 'barch/FULL-WORD.json.gz'
    run('barch', HERE / 'build_tri.py', inp, rfile, word, portable=False)
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == rec['expect_sha256']
    run('barch-controls', HERE / 'run_controls.py', inp, rfile, PKG / 'independent/audit_local.py', out / 'barch-controls', portable=False)
    res = read(out / 'barch-controls/controls.json')
    want = ['C0_identity', 'recipe', *MUTANTS] + [m + '@' + str(v['X']) for v in rec.get('variants', []) for m in MUTANTS]
    assert sorted(res) == sorted(want) == sorted(pins['barch_controls']) and all(x['ok'] for x in res.values()), res
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up / 'code')
    run('layer-end-controls', P6 / 'layer_end_controls.py', word, routing, out / 'controls')
    env.pop('PR635_CODE')
    ctl = read(out / 'controls/COLD-END-CONTROLS.json')
    assert ctl['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ctl['rejected']) == pins['layer_controls'], len(ctl['rejected'])
    local = out / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', word, '--routing', routing, '--out', local)
    assert hashlib.sha256(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest() == pins['canonical_sha256'], 'canonical word'
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    checks = read(local / 'LOCAL-CHECKS.json')
    for o, s in pins['program_sha256'].items(): assert checks[o]['sha256'] == s, ('local program', o)
    if not a.skip_phases:
        run('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')
        assert hashlib.sha256((local / 'CLIFFORD-RECIPES.json').read_bytes()).hexdigest() == pins['clifford_recipes_sha256'], 'clifford recipes'
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()

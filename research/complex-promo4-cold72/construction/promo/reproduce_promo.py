#!/usr/bin/env python3
"""Rebuild a promoted no-triangle layered word (entrance promotions E4 -> E5) and its native locals.

Input: a fresh `construction/layers_np/reproduce_np.py` output directory. That driver pins the layered no-triangle
word (a9de804f...). Recipe k: PROMO-RECIPE-k<k>.json (BlockInvert; data only) and LOCAL-PINS-k<k>.json. Steps, each
checked exactly:
  1. promotion: BlockInvert's build_promotion.py. It pins the input word and the recipe's output sha, profile and
     widths; every old frame must match the input; only frame annotations and start frames move (no scalar change).
  2. promo-controls: BlockInvert's promo_controls.py. The honest word must pass #645's independent audit_local.py,
     and its recipe- and word-level mutants must be rejected at their pinned sites (count pinned in LOCAL-PINS).
  3. layer-end-controls: ../layers/layer_end_controls.py (signed, unchanged) on the promoted word; the pinned count.
  4. native, ledgers, local-replay, wrappers, phases: PR635's native local programs; the canonical word, local
     programs and Clifford recipes are pinned (LOCAL-PINS).
Moving to another recipe k is a recipe and pins swap; this driver does not change.
Apache-2.0. Driver by ColdWitness around BlockInvert's constructor and controls.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
LAYERS = HERE.parent / 'layers'
NP_SHA = 'a9de804f194eeb39f52a4c6e54c14d93e881bec4b632694249733ed410b58113'


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--np-dir', type=Path, required=True, help='construction/layers_np/reproduce_np.py output')
    ap.add_argument('--k', default='3', help='recipe number (PROMO-RECIPE-k<k>.json)')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'
    recipe = HERE / ('PROMO-RECIPE-k%s.json' % a.k); pins = read(HERE / ('LOCAL-PINS-k%s.json' % a.k))
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

    inp = a.np_dir.resolve() / 'layers/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(inp.read_bytes())).hexdigest() == NP_SHA, 'input must be the pinned NP word'
    assert read(recipe)['input_content_sha256'] == NP_SHA
    run('promotion', HERE / 'build_promotion.py', '--input', inp, '--recipe', recipe, '--out', out / 'promo', portable=False)
    word = out / 'promo/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == read(recipe)['expected']['output_content_sha256']
    run('promo-controls', HERE / 'promo_controls.py', '--input', inp, '--recipe', recipe,
        '--audit', PKG / 'independent/audit_local.py', '--out', out / 'PROMO-CONTROLS.json', portable=False)
    pc = read(out / 'PROMO-CONTROLS.json'); assert pc['honest'] == 'PASS' and pc['rejected'] == pins['promo_controls'], pc['rejected']
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up / 'code')
    run('layer-end-controls', LAYERS / 'layer_end_controls.py', word, routing, out / 'controls')
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

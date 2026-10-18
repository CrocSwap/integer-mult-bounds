#!/usr/bin/env python3
"""Rebuild the layered gauge44 word (pivot swaps + entering ends + factored dim-8 cold ends) and its native locals.

Input: a fresh `construction/reproduce.py --until word` output directory (its regroup/ and cold44/ words are pinned
by reproduce.py itself). Steps, each checked exactly:
  1. pivot-swap: construction/layers/build_pivot_swap.py on regroup/FULL-WORD (six cost-neutral pivot-role swaps,
     exact zero-response replay, unchanged profile and width multiset, 30 negative controls);
  2. hpe: the inherited jp8 hyperplane-end changes (HYPERPLANE-END-S6.json) applied with PR635's build_hpe.apply;
  3. cold44-exact: #645's build_gauge_cold44.py on the swapped HPE word; its 44 rank-four cold ends, premix and tail
     must equal the unswapped cold44 construction's (the swaps touch no factory block);
  4. layers: PR635's unchanged build_cold_end.apply(HPE, COLD-LAYERS-RECIPE) - the cold44 recipe plus 8 entering ends
     (560/561/572/573 at U24, 597/599/537/549 at U30) and 10 factored dim-8 cold ends; output sha pinned;
  5. layer-end-controls: raw-word negative controls on the layered word (PR635 cold_end_controls adapted by
     LayerReviewer: lower->FULL pinned at 'cleanup on non-FULL end', entering ends from the recipe); 59 rejected;
  6. native, ledgers, local-replay, wrappers, phases: PR635's native local programs (as in reproduce.py).
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYERED_SHA = '0be48b1d8a6105059addf3f0d5e420c27ae3398b3a1186b6b11e9c4aa9e3f3d4'
LAYER_CONTROLS = 59


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--word-dir', type=Path, required=True, help='construction/reproduce.py --until word output')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-phases', action='store_true')
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    base = src / 'vendor/pr558'; parent = base / 'vendor/pr552'; gk = parent / 'complex-local/static44/gk'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    env.pop('PYTHONOPTIMIZE', None)
    steps = []

    def run(label, script, *args):
        t = time.monotonic()
        with (out / (label + '.log')).open('w') as f:
            rc = subprocess.call([sys.executable, '-B', str(src / 'code/run_portable.py'), str(script), *map(str, args)],
                                 env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 3)))
        (out / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        assert rc == 0, label
        print('PASS', label, flush=True)

    wd = a.word_dir.resolve()
    run('pivot-swap', HERE / 'build_pivot_swap.py', '--input', wd / 'regroup/FULL-WORD.json.gz',
        '--recipe', HERE / 'PIVOT-SWAP-S6.json', '--gk-dir', gk, '--out', out / 'swap')
    hpe = load('upstream_hpe', up / 'code/build_hpe.py')
    w = hpe.apply(read(out / 'swap/FULL-WORD.json.gz'), read(HERE / 'HYPERPLANE-END-S6.json')['changes'])
    (out / 'hpe').mkdir(); (out / 'hpe/FULL-WORD.json.gz').write_bytes(gzip.compress(enc(w), mtime=0))
    run('cold44-exact', HERE.parent / 'build_gauge_cold44.py', '--input', out / 'hpe/FULL-WORD.json.gz',
        '--out', out / 'cold44', '--hamming', wd / 'hamming', '--upstream-package', up)
    new, old = read(out / 'cold44/RECIPE.json.gz'), read(wd / 'cold44/RECIPE.json.gz')
    # The swaps touch no factory block: the 44 ends, their premix and their low tails are identical; only the FULL
    # inverse (rebuilt from the whole word) differs.
    for key in ('premix', 'early_cleanup', 'cold_ends'):
        assert new[key] == old[key], ('swapped cold44 differs from the pinned cold44 construction', key)
    tail = len(new['early_cleanup']); assert new['cleanup'][:tail] == old['cleanup'][:tail], 'low tails'
    bce = load('upstream_cold', up / 'code/build_cold_end.py')
    layered = bce.apply(w, read(HERE / 'COLD-LAYERS-RECIPE.json.gz'))
    raw = enc(layered); assert hashlib.sha256(raw).hexdigest() == LAYERED_SHA, 'layered word'
    rep = layered['report']
    assert rep['local_profile'] == {'1': 2542, '2': 414, '3': 434, '4': 154, '5': 56, '8': 8}, rep['local_profile']
    assert rep['width_inventory'] == {'4': 52, '5': 48, '7': 42, '8': 116, '9': 234}, rep['width_inventory']
    (out / 'layers').mkdir(); word = out / 'layers/FULL-WORD.json.gz'; word.write_bytes(gzip.compress(raw, mtime=0))
    print('PASS layered scalar word', word, flush=True)
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env['PR635_CODE'] = str(up / 'code')
    run('layer-end-controls', HERE / 'layer_end_controls.py', word, routing, out / 'controls')
    ctl = json.loads((out / 'controls/COLD-END-CONTROLS.json').read_text())
    assert ctl['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ctl['rejected']) == LAYER_CONTROLS, len(ctl['rejected'])
    local = out / 'local'
    run('native', up / 'code/hpe_audit_and_transport.py', '--raw', word,
        '--routing', routing, '--out', local)
    run('ledgers', up / 'code/hpe_emit_local.py', local)
    run('local-replay', up / 'code/hpe_audit_local.py', local)
    run('wrappers', up / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    if not a.skip_phases:
        run('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()

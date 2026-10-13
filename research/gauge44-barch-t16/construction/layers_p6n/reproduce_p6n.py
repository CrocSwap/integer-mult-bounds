#!/usr/bin/env python3
"""Rebuild the p6n word (NoTriReopen): the layered no-triangle word with p123's lane rebuilt as three factored dim-8 pairs.

Input: a fresh `construction/layers_np/reproduce_np.py` output directory. Its swapped HPE word (hpe/) and its
layered word a9de804f... are pinned there. Steps, each checked exactly:
  1. layers: PR635's unchanged build_cold_end.apply(swapped HPE word, COLD-LAYERS-RECIPE-P6N.json.gz). The recipe is
     NP's cold-layer recipe (cold44, s4, x30, b6, q4) plus the six cold ends of P6N-SPEC.json, built by NoTriReopen
     with JP8Ends' stackJ/stackE (the CarrierBypass premix-only factored construction): [512,513] at
     U(256,128,66,34,16,8,6,1), [311,510] at U(256,128,72,40,24,4,2,1), [522,327] at U(256,128,66,34,18,10,6,1).
     The output word sha (34b683fa...), profile and widths are pinned.
  2. layer-end-controls: layer_end_controls.py (Q6Reviewer-signed variant fc58c569..., which controls every dim-8
     cold end individually) on the p6n word; exactly 95 rejections at pinned reasons.
The promotion step (construction/promo/reproduce_promo.py --base p6n) builds the final word and its native locals.
Apache-2.0. Driver by ColdWitness after NoTriReopen's runspec.py.
"""
import argparse, gzip, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NP_SHA = 'a9de804f194eeb39f52a4c6e54c14d93e881bec4b632694249733ed410b58113'
P6N_SHA = '34b683fa08f0'   # prefix; full value is the recipe's output_content_sha256 (asserted equal below)
LAYER_CONTROLS = 95


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
    ap.add_argument('--np-dir', type=Path, required=True, help='construction/layers_np/reproduce_np.py output')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    up = a.pr635.resolve() / 'research/complex-571-cold14-st2'
    src = a.main.resolve() / 'research/complex-k492-owner-repair/vendor/multicold'
    parent = src / 'vendor/pr558/vendor/pr552'
    npd = a.np_dir.resolve()
    assert hashlib.sha256(enc(read(npd / 'layers/FULL-WORD.json.gz'))).hexdigest() == NP_SHA, 'np-dir must hold the pinned NP word'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src), PR635_CODE=str(up / 'code'))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET'): env.pop(k, None)
    bce = load('upstream_cold', up / 'code/build_cold_end.py')
    rec = read(HERE / 'COLD-LAYERS-RECIPE-P6N.json.gz')
    w = bce.apply(read(npd / 'hpe/FULL-WORD.json.gz'), rec)
    raw = enc(w); got = hashlib.sha256(raw).hexdigest()
    assert got == rec['output_content_sha256'] and got.startswith(P6N_SHA), ('p6n word', got)
    rep = w['report']
    assert rep['local_profile'] == {'1': 2540, '2': 358, '3': 446, '4': 178, '5': 56, '8': 8}, rep['local_profile']
    assert rep['width_inventory'] == {'4': 64, '5': 48, '7': 54, '8': 122, '9': 216}, rep['width_inventory']
    (out / 'p6n').mkdir(); word = out / 'p6n/FULL-WORD.json.gz'; word.write_bytes(gzip.compress(raw, mtime=0))
    print('PASS p6n word', got, flush=True)
    t = time.monotonic()
    with (out / 'layer-end-controls.log').open('w') as f:
        rc = subprocess.call([sys.executable, '-B', str(src / 'code/run_portable.py'), str(HERE / 'layer_end_controls.py'), str(word),
                              str(parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'), str(out / 'controls')],
                             env=env, stdout=f, stderr=subprocess.STDOUT)
    (out / 'STEPS.json').write_text(json.dumps([dict(step='layer-end-controls', exit_code=rc, seconds=round(time.monotonic() - t, 3))], indent=2) + '\n')
    assert rc == 0, 'layer-end-controls'
    ctl = read(out / 'controls/COLD-END-CONTROLS.json')
    assert ctl['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ctl['rejected']) == LAYER_CONTROLS, len(ctl['rejected'])
    print('PASS layer-end-controls', LAYER_CONTROLS, flush=True)
    print('DONE', word, flush=True)


if __name__ == '__main__':
    main()

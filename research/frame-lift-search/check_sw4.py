"""Frame-only optimality of the current selected complex word (#741, eight B-frame coalescences after SW4).

Input: PR699's SW4 word (content hash = complex-sw4-frame8/data/FRAME-RECIPE.json input_content_sha256), e.g.
<work>/sw4/sw4/FULL-WORD.json.gz from `bash research/complex-sw4-frame8/verify.sh <work>` or PR699's replay.
Applies #741's frame recipe, checks the pinned output hash, then solves the frame LP (linear and exact-root
weights at #741's complex root) on both the input and the #741 word.

usage: check_sw4.py --input SW4-FULL-WORD.json.gz --out RESULT-SW4.json
"""
import argparse, copy, gzip, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frame_lift as L
from frame_exact import interval
from check import chain_terms, chain_weight, lp_bound

RECIPE = HERE.parent / 'complex-sw4-frame8/data/FRAME-RECIPE.json'
ROOT741 = '1663966829367501881629/1000000000000000000000000'
enc = lambda w: json.dumps(w, sort_keys=True, separators=(',', ':')).encode()


def solve(word):
    ch, G, orig, lo = chain_terms(word)
    dom = [interval(l, g) for l, g in zip(lo, G)]
    out = {}
    for name, exact in (('linear', False), ('exact_root', True)):
        L.EXACT = exact
        w_in = chain_weight(ch, orig); bound, nv, nr = lp_bound(ch, dom)
        out[name] = dict(input_weight='%.9f' % w_in, lp_optimum='%.9f' % bound, gap='%.3e' % (w_in - bound))
    L.EXACT = False
    out['paid_profile'] = {str(k): n for k, n in sorted(L.profile(word).items())}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--input', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    L.A_STAR = float(__import__('fractions').Fraction(ROOT741))
    recipe = json.loads(RECIPE.read_text())
    w = json.loads(gzip.decompress(a.input.read_bytes()))
    assert hashlib.sha256(enc(w)).hexdigest() == recipe['input_content_sha256'], 'not the pinned PR699 SW4 word'
    z = copy.deepcopy(w)
    for part, i, before, after in recipe['gate_frames']:
        assert z[part][i][-1] == before; z[part][i][-1] = after
    p = L.profile(z); z['report']['local_profile'] = {str(k): n for k, n in sorted(p.items())}
    assert hashlib.sha256(enc(z)).hexdigest() == recipe['expected']['output_content_sha256'], 'recipe output hash'
    res = dict(input_sha256=recipe['input_content_sha256'], output_sha256=recipe['expected']['output_content_sha256'],
               exact_root=ROOT741, pr699_sw4=solve(w), pr741_frame8=solve(z))
    for k in ('linear', 'exact_root'):
        best = float(res['pr741_frame8'][k]['lp_optimum'])
        assert abs(float(res['pr699_sw4'][k]['lp_optimum']) - best) < 1e-6, 'frame optimum differs between input and #741'
        assert float(res['pr741_frame8'][k]['input_weight']) - best < 1e-3, '#741 is not frame-optimal'
    res['status'] = 'PASS_741_IS_FRAME_OPTIMAL_AND_EQUALS_THE_PR699_FRAME_OPTIMUM'
    res['scope'] = 'Same relaxation and LP as check.py (no cone caps, tail frames free); fixed SW4 gate sequence.'
    a.out.write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()

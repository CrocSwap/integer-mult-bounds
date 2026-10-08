#!/usr/bin/env python3
"""Exact certificate: PR #51 positive frames and paid clones on PR #53 skip-prefix graphs.

Inherits PR #53's research/skip-strips pipeline (data corners with exact fallback
recovery, copied centers, paid endpoint corrections, fixed I+J bases, complex
layer, balanced assembly). The two local axes are replaced by the pinned
profiles-{23,25}.json, which build.py reproduces from scratch.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse, importlib.util, json, sys
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts')); sys.path.insert(0, str(ROOT/'research/skip-strips'))
_s = importlib.util.spec_from_file_location('pr53_verify', ROOT/'research/skip-strips/verify.py')
base = importlib.util.module_from_spec(_s); _s.loader.exec_module(base)
from balanced_assembly import assembly, cutoffs
require, read, moment, js = base.require, base.read, base.moment, base.js
AB = Q(4548878290, 10**14)
KAPPA = Q(4548671376, 10**14)
PR53_KAPPA = Q(4498144, 10**11)
PR54_KAPPA = Q(141532521, 3125000000000)

def profile():
    a, b = 23, 25; m = a*b; N = comb(a, 3)*comb(b, 3)
    P = {h: read(HERE/f'profiles-{h}.json') for h in (a, b)}
    W = 2*N+sum(N//P[h]['v']*P[h]['R'] for h in (a, b)); L = sum(N//P[h]['v']*P[h]['loss'] for h in (a, b))
    data = base.data_corners(); good, bad = data['good'], data['fallback']
    require(bad == 0 and good == N, 'All data pairs recovered (PR #46/#53)')
    parts = {'data': Counter({1: 2*9*good, 21: 2*good, 17: 2*good, 481: 2*N}), 'paid_endpoint_copy': Counter({1: N})}
    for h in (a, b):
        f = P[h]
        require(f['h'] == h and f['v'] == comb(h, 3) and f['loss'] == h*(h-1) and f['rank_defects'] == 0, 'Axis profile')
        blocks = f['blocks'][:]; require(blocks[h] == h, 'Exactly h full center cleanup calls'); blocks[h] -= h; blocks[1] += h
        require(sum(t*n for t, n in enumerate(blocks)) == h*f['R']+f['loss'], 'Copied profile mass')
        rep = N//f['v']; bank = rep*f['R']
        parts[f'internal_{h}'] = Counter({t: n*rep for t, n in enumerate(blocks) if t and n})
        parts[f'exterior_{h}'] = Counter({h: bank, m-2*h: bank}); parts[f'data_growth_{h}'] = Counter({1: 2*N, h-2: 2*N})
    hist = sum(parts.values(), Counter()); s = sum(t*n for t, n in hist.items())
    require(s == W*m-N+L and (m, N, L) == (575, 4073300, 2226400), 'Complete rank mass')
    require(max(hist) == 529 and all(0 < t < m and n > 0 for t, n in hist.items()), 'Proper children')
    return dict(m=m, N=N, W=W, L=L, total_rank=s, deficit=W*m-s, maxchild=max(hist), child_multiplicities=dict(sorted(hist.items())), parts=parts)

def excluded(name):
    c = read(HERE/name); rows = {int(t): n for t, n in c['child_multiplicities'].items()}
    lower = moment(c['m'], c['W'], rows, AB)['lower']; require(lower > 1, name+' not excluded'); return lower

def run():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    p = profile(); exact = moment(p['m'], p['W'], p['child_multiplicities'], AB); require(exact['upper'] < 1, 'Bit characteristic failed')
    nxt = moment(p['m'], p['W'], p['child_multiplicities'], AB+Q(1, 10**14)); require(nxt['lower'] > 1, 'Next bit grid point certified')
    prior = base.baseline.certificate()
    bridge = base.baseline.finite_bridge(p, prior['complex']['counts'], [read(ROOT/'certificates/copied-centers-complex-input.json')]*2)
    final = assembly(bridge, AB, KAPPA, a_complex=base.AC); eventual = cutoffs(bridge, final)
    try: assembly(bridge, AB, KAPPA+Q(1, 10**14), a_complex=base.AC)
    except (AssertionError, ValueError): pass
    else: raise ValueError('Next kappa grid point accepted')
    controls = {n: excluded(n) for n in ('comparison-pr53.json', 'comparison-pr54.json')}
    require(KAPPA > PR54_KAPPA > PR53_KAPPA > Q(1, 2**15) and KAPPA < Q(1, 2**14), 'Comparison failed')
    own = sorted(HERE.glob('*.py'))+sorted(HERE.glob('*.uses'))+[HERE/f'profiles-{h}.json' for h in (23, 25)]+[HERE/'pins.json']
    return dict(status='Conditional exact arithmetic witness; inherited written proofs are dependencies', kappa=KAPPA,
                bit=dict(counts=p, **exact), next_bit_grid_lower=nxt['lower'], complex=prior['complex'], finite_bridge=bridge,
                assembly=final, eventual_bounds=eventual, exclusion_lower_moments=controls,
                comparison=dict(PR54=PR54_KAPPA, ratio_PR54=KAPPA/PR54_KAPPA, PR53=PR53_KAPPA, ratio_PR53=KAPPA/PR53_KAPPA),
                local_sha256={str(f.relative_to(ROOT)): sha256(f.read_bytes()).hexdigest() for f in own},
                scope='PR #53 skip-prefix graphs + PR #51 backward-positive labels and paid whole-chain clones + exact optimal matching; '
                      'fixed I+J profiles from tools/cprof.cpp (validated against certified PR #51 and PR #53 profiles); everything else PR #53.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', type=Path); a = ap.parse_args(); r = run()
    if a.output: a.output.write_text(json.dumps(js(r), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB))
    print('47 strict inequalities; seven margins; next grid points rejected; PR53 and PR54 networks excluded')

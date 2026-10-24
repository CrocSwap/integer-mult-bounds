"""Exact coarse savings in the seven-stage bridged word B_3 and PR #315's outer assembly.
Complex: (2K+1) x Sussman-format block histogram + 2v x B_3 idle climbs, UNSPLIT (38 | 16, 8, 22 | 32, 8, 6 at h = 9,
m = 63; max child 38: halving degree two, the admitted condition of DaysSky's PR #375), W = 6v + R, deficit 6v - 7 cst.
Bit (non-binding): #370's E8 bit word (as in #373) local histogram (our replay) x 7 + 2v x B_3 idle climbs at h = 8,
split at 27 (#373), m = 56, W = 6v + R, deficit 6v - 7 x 72. Both rational engines, 1e-16 fallback, adjacent grid
point excluded; kappa by outer.assembly (47 strict constraints, adjacent kappa rejected).
usage: kappa.py COMPLEX_CERT ORIGINAL_CERT BITWORD OUT.json"""
import sys, os, gzip, json
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8core import coarse, kappa, price_word, load_word, Q
from layout_bk import layout


def complex_b(c, K=3, split=False):
    h, v, R, cst = c['h'], c['v'], c['R'], c['cst']; Hinv = Counter()
    for w in c['blocks'].values():
        for r, n in w.items(): Hinv[int(r)] += n
    s = 2 * K + 1; m = s * h; lay = layout(K, h, split=(m - 1) // 2 if split else None)
    H = Counter({r: s * n for r, n in Hinv.items()})
    for r in lay['blocks']: H[r] += 2 * v
    W = 2 * K * v + R; assert m * W - sum(r * n for r, n in H.items()) == 2 * K * v - s * cst
    mx = max(H); t = 1
    while m ** t <= 2 * mx ** t: t += 1
    assert m <= 72 and t == (1 if split else 2)
    return coarse(H, m, W), mx, t, lay['per_pair']


def bit_c(word, K=3):
    p = price_word(word); h, v = 8, 120; s = 2 * K + 1; m = s * h
    assert p['T'] == 1; R = word['R']
    lay = layout(K, h, split=(m - 1) // 2)
    H = Counter({r: s * n for r, n in p['H'].items()})
    for r in lay['blocks']: H[r] += 2 * v
    W = 2 * K * v + R; assert m * W - sum(r * n for r, n in H.items()) == 2 * K * v - s * 72 and 2 * max(H) < m
    return coarse(H, m, W)


ours = json.load(gzip.open(sys.argv[1])); orig = json.load(gzip.open(sys.argv[2])); word = load_word(sys.argv[3])
c = bit_c(word); assert c == Q(968197503705007, 10**18), c
print('   bit side (non-binding): #370 E8 bit word in B_3 (split at 27, as #373): c = %s = %.15e (= #373)' % (c, float(c)))
out = dict(bit_coarse=str(c))
for name, cert in (('original', orig), ('ours', ours)):
    bs, _, _, _ = complex_b(cert, split=True)
    b, mx, t, idle = complex_b(cert)
    k, bd = kappa(c, b); assert bd == 'complex'
    print('   %-8s complex B_3 split b = %.15e | unsplit (max child %d, halving degree %d, idle %s) b = %s = %.15e | kappa = %s = %.15e (%s-bound)'
          % (name, float(bs), mx, t, idle, b, float(b), k, float(k), bd))
    out[name] = dict(b_split=str(bs), b_unsplit=str(b), kappa=str(k), kappa_float=float(k), binding=bd)
assert out['original']['b_split'] == '932783231884153/1000000000000000000'                 # #363
assert out['original']['kappa'] == '95424356568133/100000000000000000'                     # #375 reproduced
json.dump(out, open(sys.argv[4], 'w'), indent=1)

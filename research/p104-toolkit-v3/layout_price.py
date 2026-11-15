#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mask-layout pricer for rho = 2 callers (CALLEROPEN, an outside-session lane of Mason's / DreamingOfClouds) [C-param].
Standard library only.  PARAMETRIC: prices hypothetical caller layouts with hypothetical natives; no word is built.
 price a rho=2 mask layout from (i) role masks (stage sets), (ii) per-boundary
line caps.  Ledger [P]: T = sum_roles T[8 deg+1] (odd phase), idle incidences at stage k = |Z_k| - 2 (Lemma Det), thin = n+2-2L
QUERY P[1]; lines = intervals of consecutive stages, #lines at k = |Z_k|-2, #crossing k|k+1 <= cap_k.  Line lengths: at each
boundary continue the OLDEST lines up to min(m_k, m_k+1, cap_k) (most unequal arrangement for convex f) -> P[8 len].
Natives (three what-if readings of the #7546 native, 104 ports, 17 calls):
  'twins deleted'      the hosted X2/Y2 main moves removed from the paid histogram (a ceiling: assumes they vanish for free)
  'shadows'            the word with the hosted block dropped from the main set (its X2/Y2 registers priced as helpers)
  'shadows+2 relays'   'shadows' plus 2 relays per type-A port (T[9] += 2, P[8] += 2, P[1] += 2 per port)
Ratios printed are kappa(layout, native) / kappa(#7546)."""
import sys, copy, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); import pricekit as pk
from collections import Counter
W = pk.load(HERE / 'data' / 'base-7546-word.json.gz'); C7 = pk.load(HERE / 'data' / 'caller-7113.json.gz')
n0 = pk.native_from_word(W); base = pk.price(pk.invoice(pk.caller_invoice(C7), n0), 30); K = base['kappa']['lo']
W2 = copy.deepcopy(W); W2['hosted'] = {}; nt = pk.native_from_word(W2)
nm = dict(nt); P_ = Counter(n0['P'])
for c in ('X2', 'Y2'): P_.subtract(n0['main_moves'][c])
nm['P'] = +P_; nm['T'] = Counter(n0['T']); nm['source'] = 'param'
nr = dict(nt); nr['T'] = Counter(nt['T']); nr['P'] = Counter(nt['P']); nr['source'] = 'param'
nr['T'][9] += 2 * 96; nr['P'][1] += 96; nr['P'][8] += 2 * 96; nr['P'][1] += 96
NAT = (('twins deleted', nm), ('shadows', nt), ('shadows+2 relays', nr))
f = lambda r: r * math.log(r) if r > 1 else 0.0
def lines(m, cap):
    """m[k] lines needed at stage k (k=0..L-1); cap[k] max crossing k|k+1.  Returns Counter of line lengths."""
    alive = []   # start stages, oldest first
    out = Counter()
    for k in range(len(m)):
        if k > 0:
            keep = min(m[k - 1], m[k], cap[k - 1], len(alive))
            for s in alive[keep:]: out[k - s] += 1
            alive = alive[:keep]
        alive += [k] * (m[k] - len(alive))
    for s in alive: out[len(m) - s] += 1
    return out
def invoice(masks, L, cap, cov=2):
    """masks: list of role stage-sets; cap: list of L-1 caps."""
    Z = [sum(1 for ms in masks if k in ms) for k in range(L)]
    m = [z - cov for z in Z]; assert min(m) >= 0, Z
    T = Counter(8 * len(ms) + 1 for ms in masks)
    P = Counter({8 * l: v for l, v in lines(m, cap).items()})
    n = len(masks); thin = n + 2 - 2 * L; assert thin >= 0, (n, L)
    # thin QUERYs absorbed as IDLE_ODD into the shortest lines (as the built B does: 4 x r9)
    for _ in range(thin):
        r = min((r for r in P if r % 8 == 0 and P[r] > 0), default=None)
        if r is None: P[1] += 1; continue
        P[r] -= 1; P[r + 1] += 1
    return T, +P, Z
def price(T, P, lab, nJ=17, quiet=False):
    Ta = Counter({r: v * 104 for r, v in T.items()}); Pa = Counter({r: v * 104 for r, v in P.items()})
    res = []
    for nn, nat in NAT:
        pr = pk.price(pk.invoice(dict(T=Ta, P=Pa, nJ=nJ), nat), 30); k = pr['kappa']
        res.append(float(k['lo'] / K) if isinstance(k, dict) and k.get('lo') else 0.0)
    D = sum(v * f(r) for r, v in T.items()) - sum(v * f(r) for r, v in P.items())
    if not quiet:
        print('%-58s S/port %4d D0/port %7.1f header %3d | td %.4f  sh %.4f  rel %.4f' % (lab, pk.S_of(T, P), D, sum((r - 1) // 8 * v for r, v in T.items()), *res))
    return res
def two_arm(L=17, nl=8, hubs=2, grow=2, extra=0, deg1=True):
    """B-type: hubs on all stages; left arm stages 0..nl-1 (centre nl-1), right nl..L-1 (centre nl).  At left stage k (0-based)
    'grow' own roles enter (k>=1 or always), mask k..nl-1; 'extra' own roles enter at stage 0 additionally."""
    masks = [set(range(L)) for _ in range(hubs)]
    for k in range(nl):
        cnt = grow + (extra if k == 0 else 0)
        masks += [set(range(k, nl)) for _ in range(cnt)]
    for k in range(L - 1, nl - 1, -1):
        cnt = grow + (extra if k == L - 1 else 0)
        masks += [set(range(nl, k + 1)) for _ in range(cnt)]
    return masks
def caps_B(Z, L, nl, bonus=0):
    """interior caps |S|-4 ; centre boundary: S = hubs only -> crossing <= hubs-? use |S|-4 floored at 0; outer boundaries |S|-4+bonus."""
    cap = []
    for k in range(L - 1):
        S = Z[k] if k < nl - 1 else (Z[k + 1] if k >= nl else None)
        if S is None: cap.append(0); continue     # centre (thin block between): no line crosses (S = hubs, covered)
        c = S - 4
        if k == 0 or k == L - 2: c += bonus
        cap.append(max(c, 0))
    return cap
if __name__ == '__main__':
    print(pk.cite('control #7546 on #7113', base))
    Zof = lambda ms: [sum(1 for m in ms if k in m) for k in range(17)]
    ms = two_arm(); T, P, Z = invoice(ms, 17, caps_B(Zof(ms), 17, 8))
    print('model B: Z', Z, 'P', sorted(P.items()))
    price(T, P, 'model B (built B: 1.0950/1.0031/0.9773)')
    T, P, Z = invoice(ms, 17, caps_B(Zof(ms), 17, 8, bonus=2)); price(T, P, 'B + outer bonus (2 lines cross each outer boundary)')
    T, P, Z = invoice(ms, 17, caps_B(Zof(ms), 17, 8, bonus=1)); price(T, P, 'B + outer bonus 1')
    ms2 = two_arm(extra=-2); Z2 = Zof(ms2); print('tight Z', Z2, 'n', len(ms2))
    T, P, Z = invoice(ms2, 17, caps_B(Z2, 17, 8)); price(T, P, 'tight two-hub |Z_k|=2k (no own role at outer stages)')
    for nl in (7, 9):
        ms3 = two_arm(nl=nl); T, P, Z = invoice(ms3, 17, caps_B(Zof(ms3), 17, nl)); price(T, P, 'B with centre at %d|%d' % (nl, nl + 1))
    # uncapped ceiling (all lines run full) for reference
    T, P, Z = invoice(ms, 17, [99] * 16); price(T, P, 'B masks, NO caps (unreachable reference)')

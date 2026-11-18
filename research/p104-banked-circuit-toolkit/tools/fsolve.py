"""fast exact solve: target = sum c_x val_x.  sparse mod-p elimination selects the tokens, exact Fraction solve on them."""
from fractions import Fraction as Q
from collections import defaultdict
p = 33554393
def _m(c): return c.numerator % p * pow(c.denominator % p, -1, p) % p
def esolve(target, toks, EVt, n=None):
    if not target: return {}
    piv = {}   # col -> (vec dict, combo dict)
    for x in toks:
        v = {i: _m(c) for i, c in EVt[x].items()}; v = {i: c for i, c in v.items() if c}; cb = {x: 1}
        while v:
            col = min(v)
            if col not in piv: break
            pv, pc = piv[col]; f = v[col]
            for i, c in pv.items():
                w = (v.get(i, 0) - f * c) % p
                if w: v[i] = w
                else: v.pop(i, None)
            for i, c in pc.items():
                w = (cb.get(i, 0) - f * c) % p
                if w: cb[i] = w
                else: cb.pop(i, None)
        if v:
            col = min(v); inv = pow(v[col], -1, p)
            piv[col] = ({i: c * inv % p for i, c in v.items()}, {i: c * inv % p for i, c in cb.items()})
    y = {i: _m(c) for i, c in target.items()}; y = {i: c for i, c in y.items() if c}; cb = {}
    while y:
        col = min(y)
        if col not in piv: return None
        pv, pc = piv[col]; f = y[col]
        for i, c in pv.items():
            w = (y.get(i, 0) - f * c) % p
            if w: y[i] = w
            else: y.pop(i, None)
        for i, c in pc.items(): cb[i] = (cb.get(i, 0) + f * c) % p
    sel = [x for x, c in cb.items() if c]
    # exact solve over sel (least squares not needed: system consistent mod p; solve exactly)
    rows = defaultdict(dict)
    for j, x in enumerate(sel):
        for i, c in EVt[x].items(): rows[i][j] = c
    k = len(sel)
    R = [[rows[i].get(j, Q(0)) for j in range(k)] + [target.get(i, Q(0))] for i in set(rows) | set(target)]
    rr = 0; pc = []
    for c in range(k):
        i = next((i for i in range(rr, len(R)) if R[i][c]), None)
        if i is None: continue
        R[rr], R[i] = R[i], R[rr]; g = R[rr][c]; R[rr] = [v / g for v in R[rr]]
        for i2 in range(len(R)):
            if i2 != rr and R[i2][c]:
                h = R[i2][c]; R[i2] = [a - h * b for a, b in zip(R[i2], R[rr])]
        pc.append(c); rr += 1
    if any(R[i][k] for i in range(rr, len(R))): return None
    sol = {sel[c]: R[i][k] for i, c in enumerate(pc) if R[i][k]}
    chk = dict(target)
    for x, c in sol.items():
        for i, v in EVt[x].items():
            w = chk.get(i, 0) - c * v
            if w: chk[i] = w
            else: chk.pop(i, None)
    return sol if not chk else None

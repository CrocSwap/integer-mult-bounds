"""Shared-donor response kernel on a gcert/1 complex program (Sussman's format), via exterior gauges (rule E7/Q2).
Entry: pivot slot p, entrance E (a frame inside p's first frame and inside every donor's first frame), donors d with
rational coefficients c_d such that resp(p) + sum c_d resp(d) = 0, where resp(s) in Q^v = the column of slot s's
initial value in the y rows of the product (A, scatter, B). Transform: p starts at E (ext gauge [p, E]); at the start
of A each donor climbs to E and takes d += c_d p ('in' gate at E). Then Q2 holds for p.
Price (entrance-residual rule, as the bit side's #320/#329 lineage): W = 2Kv + sum_slots (h - dim ext)/h, deficit fixed.
usage: cxkernel.py CERT.json.gz GXDIR OUT.json.gz [K]"""
import sys, os, gzip, json, math, copy
from fractions import Fraction as Fr
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8core import coarse
from layout_bk import layout


def reduce(u, basis):
    for b in basis:
        if u >> (b.bit_length() - 1) & 1: u ^= b
    return u
def inside(a, b): return all(reduce(u, b) == 0 for u in a)
def echelon(vecs):
    """reduced echelon (descending pivots) of the F2 span of vecs"""
    B = []
    for u in vecs:
        u = reduce(u, B)
        if u:
            B = [b ^ u if b >> (u.bit_length() - 1) & 1 else b for b in B] + [u]
            B.sort(reverse=True)
    return B


def responses(c):
    v, R = c['v'], c['R']; n = 2 * v + R
    reg = [dict() for _ in range(n)]
    for r in range(2 * v, n): reg[r] = {r: Fr(1)}
    def axpy(t, src, co):
        d = reg[t]
        for k, u in src.items():
            w = d.get(k, 0) + co * u
            if w: d[k] = w
            else: d.pop(k, None)
    def run(gates):
        for g in gates:
            if g[0] == 'neg': reg[g[2]] = {k: -u for k, u in reg[g[2]].items()}
            elif g[0] == 'out':
                src = dict(reg[g[2]])
                for t, a, b in g[3]: axpy(t, src, Fr(a, b))
            else:
                for s, a, b in g[3]: axpy(g[2], reg[s], Fr(a, b))
    run(c['A'])
    tot = {k: dict(reg[s]) for k, s, _ in c['ret']}
    for t in range(v):
        for k, a, b in c['scat']['table'][t]: axpy(v + t, tot[k], Fr(a, b))
    run(c['B'])
    resp = {s: {} for s in range(2 * v, n)}
    for t in range(v):
        for s, co in reg[v + t].items(): resp[s][t] = co
    return resp


def first_frames(c):
    v, R = c['v'], c['R']; n = 2 * v + R; first = {}
    for ph in ('A', 'B'):
        for g in c[ph]:
            regs = [g[2]] + ([t for t, _, _ in g[3]] + list(g[4]) if g[0] == 'out' else [s for s, _, _ in g[3]] if g[0] == 'in' else [])
            for r in regs:
                if r >= 2 * v and r not in first and g[1] != 0: first[r] = g[1]
    return first


class QBasis:
    """incremental rational basis over Q^v with combination tracking (donor slots)"""
    def __init__(self): self.rows = []  # (pivot, vec dict, combo dict)
    def reduce(self, x):
        x = dict(x); cm = {}
        for p, vec, co in self.rows:
            if p in x:
                f = x[p] / vec[p]
                for k, u in vec.items():
                    w = x.get(k, 0) - f * u
                    if w: x[k] = w
                    else: x.pop(k, None)
                for k, u in co.items():
                    w = cm.get(k, 0) - f * u
                    if w: cm[k] = w
                    else: cm.pop(k, None)
        return x, cm
    def add(self, x, slot):
        r, cm = self.reduce(x)
        cm = {k: u for k, u in cm.items()}; cm[slot] = cm.get(slot, 0) + 1
        p = min(r); self.rows.append((p, r, cm))


def select(c, a, K=3):
    h, v, R = c['h'], c['v'], c['R']; m = (2 * K + 1) * h
    fr = [tuple(f) for f in c['frames']]; dim = [len(f) for f in fr]
    chi = lambda r: 0.0 if r <= 0 else r * (math.exp(a * math.log(m / r)) - 1)
    resp = responses(c); first = first_frames(c)
    ret = {s for _, s, _ in c['ret']}
    H = [s for s in range(2 * v, 2 * v + R) if s not in ret and s in first and c['start'][s] == 0]
    # candidate entrances: frames of the table inside some first frame, plus pairwise intersections not in table skipped
    fset = sorted(set(first[s] for s in H))
    cand = [E for E in range(2, len(fr)) if dim[E] > 0 and dim[E] < h and any(inside(fr[E], fr[f]) for f in fset)]
    ins = {}
    def isin(E, f):
        k = (E, f)
        if k not in ins: ins[k] = inside(fr[E], fr[f])
        return ins[k]
    groups = {E: [s for s in H if isin(E, first[s])] for E in cand}
    avail_p = set(H); avail_d = set(H); donor_at = {}
    def plan(E):
        e = dim[E]; G = groups[E]; mem = []
        for s in G:
            d1 = dim[first[s]]
            dc = (0.0 if donor_at.get(s) == E else (chi(e) + chi(d1 - e) - chi(d1)) if s in avail_d else None)
            if s in donor_at and donor_at[s] != E: dc = None
            pg = chi(d1) - chi(d1 - e) if s in avail_p else None
            if dc is None and pg is None: continue
            mem.append((s, dc, pg))
        mem.sort(key=lambda t: (t[1] if t[1] is not None else 1e9, t[2] if t[2] is not None else -1))
        B = QBasis(); slots = {}; piv = []
        for s, dc, pg in mem:
            r, cm = B.reduce(resp[s])
            if not r and pg is not None and pg > 0: piv.append((s, cm, pg))
            elif r and dc is not None: B.add(resp[s], s); slots[s] = dc
        if not piv: return None
        keep = list(piv)
        def users():
            u = Counter()
            for _, cm, _ in keep:
                for k in cm: u[k] += 1
            return u
        while keep:
            u = users(); best = None
            for i, (s, cm, pg) in enumerate(keep):
                freed = sum(slots[k] for k in cm if u[k] == 1)
                if freed > pg and (best is None or freed - pg > best[0]): best = (freed - pg, i)
            if best is None: break
            keep.pop(best[1])
        u = users(); gain = sum(pg for _, _, pg in keep) - sum(slots[k] for k in u)
        if gain <= 1e-15: return None
        # coefficients: resp(p) = sum cm_k resp(k)  -> donor gate d += (-cm_d) p
        return gain, [(s, {k: -x for k, x in cm.items()}) for s, cm, _ in keep]
    plans = {E: plan(E) for E in cand}
    chosen = []; total = 0.0
    while True:
        live = [(p[0], E) for E, p in plans.items() if p]
        if not live: break
        g, E = max(live); _, ents = plans[E]
        touched = set()
        for p, cm in ents:
            chosen.append((E, p, cm)); avail_p.discard(p); avail_d.discard(p); touched.add(p)
            for d in cm: donor_at[d] = E; avail_p.discard(d); avail_d.discard(d); touched.add(d)
        total += g
        for E2 in cand:
            if plans.get(E2) and any(s in touched for s in groups[E2]): plans[E2] = plan(E2)
        plans[E] = plan(E)
    return chosen, total


def apply(c, chosen):
    c = copy.deepcopy(c); head = []
    ext = []
    for E, p, cm in chosen:
        ext.append([p, E]); c['start'][p] = E
    byd = {}
    for E, p, cm in chosen:
        for d, co in cm.items(): byd.setdefault((d, E), []).append([p, co.numerator, co.denominator])
    for (d, E), lst in sorted(byd.items()): head.append(['in', E, d, sorted(lst)])
    c['A'] = head + c['A']; c['ext'] = sorted(ext)
    return c


def rehist(c):
    """recompute block histograms and N exactly as gx.check1 counts them (climbs per class, COPY ranks)"""
    v, R = c['v'], c['R']; n = 2 * v + R; dim = [len(f) for f in c['frames']]
    cls = lambda r: 'x' if r < v else 'y' if r < 2 * v else 's'
    cur = list(c['start']); H = {'x': Counter(), 'y': Counter(), 's': Counter(), 'c': Counter()}
    def climb(r, f):
        if cur[r] != f: H[cls(r)][dim[f] - dim[cur[r]]] += 1; cur[r] = f
    for ph in ('A', 'B'):
        if ph == 'B':
            for k, s_, f in c['ret']: H['c'][dim[f]] += 1
        for g in c[ph]:
            regs = [g[2]] + ([t for t, _, _ in g[3]] + list(g[4]) if g[0] == 'out' else [x for x, _, _ in g[3]] if g[0] == 'in' else [])
            for r in regs: climb(r, g[1])
    for r in range(n): climb(r, c['final'][r])
    c['blocks'] = {k: {str(r): x for r, x in sorted(w.items())} for k, w in H.items()}
    c['N'] = sum(r * x for w in H.values() for r, x in w.items())
    return c


def price(c, K):
    """returns b in B_K with the entrance-residual W"""
    h, v, R, cst = c['h'], c['v'], c['R'], c['cst']
    Hinv = Counter()
    for w in c['blocks'].values():
        for r, n in w.items(): Hinv[int(r)] += n
    s = 2 * K + 1; m = s * h; lay = layout(K, h, split=(m - 1) // 2 if K > 2 else None)
    tails = sum(len(c['frames'][f]) for _, f in c['ext'])
    T = 1 if tails % h == 0 else h
    H = Counter({r: T * s * n for r, n in Hinv.items()})
    for r in lay['blocks']: H[r] += T * 2 * v
    W = (2 * K * v + R) * T - tails * T // h; assert tails * T % h == 0
    assert m * W - sum(r * n for r, n in H.items()) == T * (2 * K * v - s * cst), 'deficit'
    assert 2 * max(H) < m
    return coarse(H, m, W)


if __name__ == '__main__':
    c = json.load(gzip.open(sys.argv[1])); sys.path.insert(0, sys.argv[2]); import gx, gxcore
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    b0 = price(c, K); print('start b(B_%d) =' % K, b0, float(b0))
    chosen, tot = select(c, float(b0), K)
    fr = c['frames']
    print('entries', len(chosen), 'chi %.5f' % tot, 'ranks', Counter(len(fr[E]) for E, _, _ in chosen),
          'donors', len({d for _, _, cm in chosen for d in cm}))
    w = rehist(apply(c, chosen)); w['derived_from'] = c['derived_from'] + ' + shared-donor kernel via exterior gauges'
    st = {}; gx.check1(w, scalar=True, stats=st); print('gx.check1 (E0-E7 incl. exact scalar E5 and Q2) PASS', st)
    for K2 in (2, 3, 4):
        b = price(w, K2); print('b(B_%d) =' % K2, b, float(b))
    json.dump(w, gzip.open(sys.argv[3], 'wt'))

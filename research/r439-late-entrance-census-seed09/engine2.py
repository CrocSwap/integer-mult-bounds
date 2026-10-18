# SPDX-License-Identifier: Apache-2.0
"""Engine 2: an independent recomputation (no code shared with census.py).

- register values are Python sets of dirty columns (XOR = symmetric difference);
- frame geometry uses rational annihilators (containment = every basis row is orthogonal to the annihilator);
- the closure L is built from annihilators of first-contact spaces;
- W_t (LC-fav) is computed at sigma by a kernel method: eliminate the x part of the generators with combination
  tracking, then take the dirt part of every x-free combination;
- W_t (A6) is computed per (target, register) pair by enumerating the change points of cur, next and value,
  instead of sweeping time.
Outputs use the same dirt-bit convention as Engine 1 (bit j = helper register 2v + j) for exact comparison.
"""
from fractions import Fraction
from itertools import combinations


def _eliminate(rows, width):
    """row-reduce rational rows; returns (independent reduced rows, pivot columns)."""
    m = [list(map(Fraction, r)) for r in rows]
    piv_cols, out, r0 = [], [], 0
    for c in range(width):
        k = next((i for i in range(r0, len(m)) if m[i][c]), None)
        if k is None:
            continue
        m[r0], m[k] = m[k], m[r0]
        lead = m[r0][c]
        m[r0] = [x / lead for x in m[r0]]
        for i in range(len(m)):
            if i != r0 and m[i][c]:
                q = m[i][c]
                m[i] = [a - q * b for a, b in zip(m[i], m[r0])]
        piv_cols.append(c)
        r0 += 1
    return [tuple(r) for r in m[:r0]], piv_cols


def annihilator(rows, width=8):
    red, piv = _eliminate(rows, width) if rows else ([], [])
    ann = []
    for free in range(width):
        if free in piv:
            continue
        vec = [Fraction(0)] * width
        vec[free] = Fraction(1)
        for row, pc in zip(red, piv):
            vec[pc] = -row[free]
        ann.append(tuple(vec))
    return ann


class Geometry:
    def __init__(self, w):
        self.lines = w['lines']
        self.rows = [[self.lines[i] for i in f] for f in w['frames']]
        self.ann = [annihilator(r) for r in self.rows]
        self.memo = {}

    def contained(self, a, b):
        key = (a, b)
        if key not in self.memo:
            self.memo[key] = all(sum(x * y for x, y in zip(u, z)) == 0 for u in self.rows[a] for z in self.ann[b])
        return self.memo[key]

    def closed(self, f, v):
        """the frame's label list is exactly the set of live labels in its span."""
        inside = [i for i in range(v) if all(sum(x * y for x, y in zip(self.lines[i], z)) == 0 for z in self.ann[f])]
        return inside


def replay_sets(w):
    v, R = w['v'], w['R']
    n = 2 * v + R
    val = [{r} for r in range(n)]
    cur = list(w['start'])
    versions = [[(0, frozenset(val[r]))] for r in range(n)]     # per register: (tau, value) from sigma on
    for f, d, ss in w['A']:
        for r in (d, *ss):
            cur[r] = f
        for s in ss:
            val[d] = val[d] ^ val[s]
    snaps = [frozenset(val[q]) for q in w['ret']]
    for t, row in enumerate(w['scatter']):
        for k in row:
            val[v + t] = val[v + t] ^ snaps[k]
    sigma_val = [frozenset(x) for x in val]
    sigma_cur = list(cur)
    versions = [[(0, sigma_val[r])] for r in range(n)]
    frames_hist = [[(0, sigma_cur[r])] for r in range(n)]
    for i, (f, d, ss) in enumerate(w['B']):
        for r in (d, *ss):
            if frames_hist[r][-1][1] != f:
                frames_hist[r].append((i + 1, f))
        for s in ss:
            val[d] = val[d] ^ val[s]
        versions[d].append((i + 1, frozenset(val[d])))
    K = []
    for t in range(v):
        y = val[v + t]
        if {c for c in y if c < 2 * v} != {t, v + t}:
            raise ValueError('raw word is not y -> y + x + K h')
        K.append(sum(1 << (c - 2 * v) for c in y if c >= 2 * v))
    return dict(snaps=snaps, sigma_val=sigma_val, sigma_cur=sigma_cur, versions=versions, frames_hist=frames_hist, K=K)


def first_contact(w):
    v = w['v']
    first = {}
    for f, d, ss in w['A'] + w['B']:
        for r in (d, *ss):
            if r >= 2 * v:
                first.setdefault(r, f)
    return first


def closure_classes(w, first):
    """{annihilator-key of V: sorted eligible registers} for L = distinct first spaces and their pairwise meets."""
    geo = Geometry(w)
    v = w['v']
    spaces = {}
    for r, f in first.items():
        red = tuple(_eliminate(geo.rows[f], 8)[0])
        spaces.setdefault(red, []).append(r)
    keys = list(spaces)
    members = set(keys)
    planes = [k for k in keys if len(k) == 2]
    for a, b in combinations(planes, 2):
        meet_ann = annihilator(list(a)) + annihilator(list(b))
        meet = annihilator(meet_ann)                 # the intersection = annihilator of the stacked annihilators
        if meet:
            members.add(tuple(_eliminate(meet, 8)[0]))

    def inside(V, F):
        za = annihilator(list(F))
        return all(sum(x * y for x, y in zip(u, z)) == 0 for u in V for z in za)
    return {V: sorted(r for key, regs in spaces.items() if inside(V, key) for r in regs) for V in members}


def _xfree_dirt(gens, v):
    """dirt parts (bitmask over helpers) of all F2 combinations of gens whose x part (< v) vanishes."""
    piv = {}                                   # pivot x-column -> (x set, dirt mask)
    free = []
    for g in gens:
        xs = {c for c in g if c < v}
        dm = sum(1 << (c - 2 * v) for c in g if c >= 2 * v)
        while xs:
            p = max(xs)
            if p in piv:
                xs = xs ^ piv[p][0]
                dm ^= piv[p][1]
            else:
                piv[p] = (xs, dm)
                break
        if not xs:
            free.append(dm)
    return free


def _basis(vectors):
    b = {}
    for x in vectors:
        while x:
            h = x.bit_length() - 1
            if h in b:
                x ^= b[h]
            else:
                b[h] = x
                break
    return list(b.values())


def W_fav(w, rep, geo):
    v, R = w['v'], w['R']
    n = 2 * v + R
    tperp = [w['final'][v + t] for t in range(v)]
    out = []
    for t in range(v):
        gens = list(rep['snaps']) + [rep['sigma_val'][r] for r in range(n)
                                      if r != v + t and geo.contained(rep['sigma_cur'][r], tperp[t])]
        out.append(_basis(_xfree_dirt(gens, v)))
    # x-free here; note the generators are full values (x, y, dirt); y is projected out (y-free variant)
    return out


def W_A6(w, rep, geo):
    """per pair (t, r): change points = 0 and every tau = i+1 with B[i] touching t or r."""
    v, R = w['v'], w['R']
    n = 2 * v + R
    B, C = w['B'], w['C']
    touch = [[] for _ in range(n)]
    for i, (f, d, ss) in enumerate(B + C):
        for r in (d, *ss):
            touch[r].append((i, f))

    def nxt(r, tau):
        for i, f in touch[r]:
            if i >= tau:
                return f
        return w['final'][r]

    def at(hist, tau):
        out = hist[0][1]
        for k, x in hist:
            if k <= tau:
                out = x
            else:
                break
        return out
    btouch = [{i + 1 for i, _ in touch[r] if i < len(B)} for r in range(n)]
    out = []
    for t in range(v):
        gens = list(rep['snaps'])
        for r in range(n):
            if r == v + t:
                continue
            for tau in sorted({0} | btouch[v + t] | btouch[r]):
                ct, cr = at(rep['frames_hist'][v + t], tau), at(rep['frames_hist'][r], tau)
                if geo.contained(cr, nxt(v + t, tau)) and geo.contained(ct, nxt(r, tau)):
                    gens.append(at(rep['versions'][r], tau))
        out.append(_basis(_xfree_dirt(gens, v)))
    return out


def same_span(a, b):
    ba, bb = _basis(a), _basis(b)
    return len(ba) == len(bb) == len(_basis(list(a) + list(b)))


def admitted(K, W, classes, v):
    sup = set()
    for I in classes.values():
        for k in range(1, len(I) + 1):
            for S in combinations(I, k):
                sup.add(S)
    out = []
    for S in sup:
        cm = sum(1 << (r - 2 * v) for r in S)
        T = [t for t in range(v) if bin(K[t] & cm).count('1') % 2]
        if all(any(bin(u & cm).count('1') % 2 for u in W[t]) for t in T):
            out.append((tuple(S), len(T)))
    return sorted(out, key=lambda a: (len(a[0]), a[0])), len(sup)

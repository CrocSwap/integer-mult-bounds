"""Independent re-implementation of the depth-one search (shares no code with reframe.py / search.py).

Differences from the primary implementation, chosen so that a shared mistake is unlikely:
  * frames are frozensets of line indices; spans use fraction-free integer elimination (no Fraction, no masks);
  * every legal insertion index is enumerated (not one representative per slot), within a section and across the
    scatter; indices are grouped by the prefix counts that fix every changed register sequence, which must reproduce
    the primary slot count exactly; moves are rebuilt from their descriptions by separate code;
  * D and C are kept in the replayed word (D at frame 0, C rebuilt as the literal reverse at the full frame) instead of
    being argued away;
  * free gates are grouped by any shared register (coarser than "consecutive on a register"), then each group is
    enumerated exhaustively over all closed frames between the bounds.
For each class the optimal paid profile is compared with the primary result file.

Usage: independent_check.py WORD.json.gz PRIMARY_DETAIL.json [--jobs N]
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import gzip
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from math import gcd
from multiprocessing import Pool


def int_rank_basis(vectors):
    """row echelon basis of integer vectors by fraction-free elimination (rows kept primitive)"""
    basis = []  # list of (pivot, row)
    for v in vectors:
        row = list(v)
        for piv, b in basis:
            if row[piv]:
                a, c = b[piv], row[piv]
                row = [a * x - c * y for x, y in zip(row, b)]
                g = 0
                for x in row:
                    g = gcd(g, x)
                if g > 1:
                    row = [x // g for x in row]
        piv = next((k for k, x in enumerate(row) if x), None)
        if piv is not None:
            basis.append((piv, row))
    return basis


def in_span(basis, v):
    row = list(v)
    for piv, b in basis:
        if row[piv]:
            a, c = b[piv], row[piv]
            row = [a * x - c * y for x, y in zip(row, b)]
    return not any(row)


class Geometry:
    def __init__(self, lines):
        self.lines = [tuple(l) for l in lines]
        self.memo = {}

    def closure(self, S):
        S = frozenset(S)
        if S in self.memo:
            return self.memo[S]
        basis = int_rank_basis([self.lines[i] for i in sorted(S)])
        C = frozenset(i for i in range(len(self.lines)) if i in S or (basis and in_span(basis, self.lines[i])))
        out = (C, len(basis))
        self.memo[S] = out
        self.memo[C] = out
        return out


def word_parts(w):
    V = w['v']
    N = 2 * V + w['R']
    fr = [frozenset(f) for f in w['frames']]
    full = frozenset(range(V))
    return V, N, fr, full


def ops_commute(a, b):
    (ta, sa), (tb, sb) = a, b
    return ta not in sb and tb not in sa


def variants_of(gate):
    """(source or None, moved op, remainder or None) for each summand of a gate, plus the whole multi-source gate"""
    f, t, ss = gate
    out = [(x, (t, (x,)), (t, tuple(y for y in ss if y != x)) if len(ss) > 1 else None) for x in ss]
    if len(ss) > 1:
        out.append((None, (t, tuple(ss)), None))
    return out


def without(L, i, rem):
    rest = [(g[1], tuple(g[2])) for g in L]
    del rest[i]
    if rem is not None:
        rest.insert(i, rem)
    return rest


def prefix_counts(seq, regs):
    pref = {r: [0] for r in regs}
    for t2, s2 in seq:
        for r in regs:
            pref[r].append(pref[r][-1] + (t2 == r or r in s2))
    return pref


def move_classes(L):
    """every insertion index of the same section reachable through commuting gates, grouped into classes.

    Moving op only changes the gate sequences of op's own registers (and, for a split, the gate key of the remainder,
    which does not depend on the index). After inserting op at index q of `rest`, register r's sequence is fixed by
    the number of gates of rest[:q] that touch r. So the tuple of those counts over op's registers is the class key.
    Returns (number of indices, list of (i, source or None, representative index))."""
    out = []
    n_idx = 0
    for i, gate in enumerate(L):
        for s, op, rem in variants_of(gate):
            rest = without(L, i, rem)
            regs = sorted({op[0], *op[1]})
            pref = prefix_counts(rest, regs)
            reach = {i}
            p = i
            while p > 0 and ops_commute(op, rest[p - 1]):
                p -= 1
                reach.add(p)
            p = i
            while p < len(rest) and ops_commute(op, rest[p]):
                p += 1
                reach.add(p)
            identity = tuple(pref[r][i] for r in regs) if (s is None or len(gate[2]) == 1) else None
            seen = {}
            for q in sorted(reach):
                n_idx += 1
                key = tuple(pref[r][q] for r in regs)
                if key != identity and key not in seen:
                    seen[key] = q
            out += [(i, s, q) for q in seen.values()]
    return n_idx, out


def cross_classes(w):
    """relocations into the other section. The scatter writes the targets and reads the retained totals, so an op
    commutes with it iff it does not write a retained total and reads no target; H3 further requires a phase-A gate
    (and so any gate that ends up in A, or comes from A) to write no target. The op must reach the end of A (from A)
    or the start of B (from B) through commuting gates; every index of the other section reachable from its near end
    is then grouped by prefix counts as above. Returns (number of indices, list of (section, i, source, index))."""
    V = w['v']
    targets = set(range(V, 2 * V))
    ret = set(w['ret'])
    out = []
    n_idx = 0
    for sec, other in (('A', 'B'), ('B', 'A')):
        L, M = w[sec], [(g[1], tuple(g[2])) for g in w[other]]
        for i, gate in enumerate(L):
            for s, op, rem in variants_of(gate):
                t, srcs = op
                if t in ret or t in targets or any(x in targets for x in srcs):
                    continue
                rest = without(L, i, rem)
                if sec == 'A' and not all(ops_commute(op, g) for g in rest[i:]):
                    continue
                if sec == 'B' and not all(ops_commute(op, g) for g in rest[:i]):
                    continue
                regs = sorted({t, *srcs})
                pref = prefix_counts(M, regs)
                if sec == 'A':
                    reach = [0]
                    while reach[-1] < len(M) and ops_commute(op, M[reach[-1]]):
                        reach.append(reach[-1] + 1)
                else:
                    reach = [len(M)]
                    while reach[-1] > 0 and ops_commute(op, M[reach[-1] - 1]):
                        reach.append(reach[-1] - 1)
                seen = {}
                for q in reach:
                    n_idx += 1
                    seen.setdefault(tuple(pref[r][q] for r in regs), q)
                out += [(sec, i, s, q) for q in seen.values()]
    return n_idx, out


def build(w, sec, i, s, dst, q):
    """the (A, B) gate lists of one move, rebuilt from its description"""
    L = w[sec]
    gate = L[i]
    s_, op, rem = next(v for v in variants_of(gate) if v[0] == s)
    rest = without(L, i, rem)
    other = 'B' if sec == 'A' else 'A'
    if dst == sec:
        new = rest[:q] + [op] + rest[q:]
        lists = {sec: new, other: [(g[1], tuple(g[2])) for g in w[other]]}
    else:
        M = [(g[1], tuple(g[2])) for g in w[other]]
        lists = {sec: rest, other: M[:q] + [op] + M[q:]}
    return lists['A'], lists['B']


class Problem:
    def __init__(self, w):
        self.w = w
        self.V, self.N, self.fr, self.full = word_parts(w)
        self.geo = Geometry(w['lines'])
        self.start = [self.fr[f] for f in w['start']]
        self.final = [self.fr[f] for f in w['final']]
        self.ret = w['ret']
        cur = list(self.start)
        for f, t, ss in w['D'] + w['A']:
            for r in [t, *ss]:
                cur[r] = self.fr[f]
        self.copy = {q: cur[q] for q in self.ret}
        self.D = [(t, tuple(ss)) for f, t, ss in w['D']]
        self.Dframes = [self.fr[f] for f, t, ss in w['D']]

    def optimum(self, A, B):
        """A, B: lists of (t, sources). Returns the optimal profile (dict) or None."""
        V, N = self.V, self.N
        C = [(t, ss) for t, ss in reversed(A + B) if t < V or t >= 2 * V]
        seq = [('D', g) for g in self.D] + [('A', g) for g in A] + [('S', None)] + [('B', g) for g in B] + \
              [('C', g) for g in C]
        n = len(seq)
        fixed = {}
        for k in range(len(self.D)):
            fixed[k] = self.Dframes[k]
        for k in range(n - len(C), n):
            fixed[k] = self.full
        geo = self.geo
        # forward least frames
        lo = [None] * n
        cur = list(self.start)
        for k, (sec, g) in enumerate(seq):
            if sec == 'S':
                for q in self.ret:
                    if not cur[q] <= self.copy[q]:
                        return None
                    cur[q] = self.copy[q]
                continue
            t, ss = g
            U = frozenset().union(*(cur[r] for r in (t, *ss)))
            m = geo.closure(U)[0]
            if k in fixed:
                if not m <= fixed[k]:
                    return None
                m = fixed[k]
            lo[k] = m
            for r in (t, *ss):
                cur[r] = m
        for r in range(N):
            if not cur[r] <= self.final[r]:
                return None
        # backward greatest frames
        hi = [None] * n
        ub = list(self.final)
        for k in range(n - 1, -1, -1):
            sec, g = seq[k]
            if sec == 'S':
                for q in self.ret:
                    if not self.copy[q] <= ub[q]:
                        return None
                    ub[q] = self.copy[q]
                for r in range(V, 2 * V):
                    ub[r] = frozenset()
                continue
            t, ss = g
            m = frozenset.intersection(*(ub[r] for r in (t, *ss)))
            if k in fixed:
                if not fixed[k] <= m:
                    return None
                m = fixed[k]
            hi[k] = m
            for r in (t, *ss):
                ub[r] = m
        for k in range(n):
            if lo[k] is not None and not lo[k] <= hi[k]:
                return None
        # options of free gates
        opts = {}
        for k in range(n):
            if lo[k] is None or lo[k] == hi[k]:
                continue
            found = {lo[k]}
            frontier = [lo[k]]
            while frontier:
                m = frontier.pop()
                for i in hi[k] - m:
                    c = geo.closure(m | {i})[0]
                    if c <= hi[k] and c not in found:
                        found.add(c)
                        frontier.append(c)
            opts[k] = sorted(found, key=lambda s: (len(s), sorted(s)))
        # register -> positions
        regpos = defaultdict(list)
        for k, (sec, g) in enumerate(seq):
            if sec != 'S':
                for r in (g[0], *g[1]):
                    regpos[r].append(k)
        scat = next(k for k, (sec, g) in enumerate(seq) if sec == 'S')
        frames = [lo[k] for k in range(n)]

        def climbs(r):
            H = Counter()
            c = self.start[r]
            checked = r not in self.copy
            for k in regpos[r]:
                if not checked and k > scat:
                    if c != self.copy[r]:
                        return None
                    checked = True
                m = frames[k]
                if m != c:
                    if not c <= m:
                        return None
                    H[geo.closure(m)[1] - geo.closure(c)[1]] += 1
                    c = m
            if not checked and c != self.copy[r]:
                return None
            if c != self.final[r]:
                if not c <= self.final[r]:
                    return None
                H[geo.closure(self.final[r])[1] - geo.closure(c)[1]] += 1
            return H

        # groups of free gates sharing any register
        regs_of = {k: {seq[k][1][0], *seq[k][1][1]} for k in opts}
        unseen = set(opts)
        groups = []
        while unseen:
            k0 = unseen.pop()
            grp, todo = [k0], [k0]
            while todo:
                k = todo.pop()
                for r in regs_of[k]:
                    for k2 in regpos[r]:
                        if k2 in unseen:
                            unseen.discard(k2)
                            grp.append(k2)
                            todo.append(k2)
            groups.append(sorted(grp))
        z = float(self.w.get('_z', 0.0017334))

        def cost(H):
            return sum(cnt * d * (64 / d) ** z for d, cnt in H.items())

        for grp in groups:
            regs = sorted(set().union(*(regs_of[k] for k in grp)))
            best = None
            for combo in itertools.product(*(opts[k] for k in grp)):
                for k, m in zip(grp, combo):
                    frames[k] = m
                H = Counter()
                ok = True
                for r in regs:
                    h = climbs(r)
                    if h is None:
                        ok = False
                        break
                    H.update(h)
                if ok:
                    key = (cost(H), [sorted(m) for m in combo])
                    if best is None or key < best:
                        best = (key[0], key[1], combo)
            if best is None:
                return None
            for k, m in zip(grp, best[2]):
                frames[k] = m
        H = Counter()
        for r in range(N):
            h = climbs(r)
            if h is None:
                return None
            H.update(h)
        for q in self.ret:
            H[geo.closure(self.copy[q])[1]] += 1
        return dict(sorted(H.items()))


_P = None


def _init(path, z):
    global _P
    w = json.load(gzip.open(path, 'rt'))
    w['_z'] = z
    _P = Problem(w)


def _job(moves):
    out = []
    for mv in moves:
        A, B = build(_P.w, *mv)
        out.append((mv, _P.optimum(A, B)))
    return out


def main():
    path, primary = sys.argv[1], sys.argv[2]
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else os.cpu_count()
    w = json.load(gzip.open(path, 'rt'))
    prim = json.load(open(primary))
    num, den = prim['c'].split('/') if '/' in prim['c'] else (prim['c'], '1')
    z = int(num) / int(den)
    V, N = w['v'], 2 * w['v'] + w['R']
    base_ops = {sec: [(t, tuple(ss)) for f, t, ss in w[sec]] for sec in 'AB'}
    # enumerate every insertion index and group it into classes (identity classes dropped as in the primary search)
    total_indices = 0
    reps = []
    for sec in 'AB':
        n_idx, cl = move_classes(w[sec])
        total_indices += n_idx
        reps += [(sec, i, s, sec, q) for i, s, q in cl]
    n_cross, cl = cross_classes(w)
    reps += [(sec, i, s, 'B' if sec == 'A' else 'A', q) for sec, i, s, q in cl]
    items = [reps[k:k + 32] for k in range(0, len(reps), 32)]
    with Pool(jobs, initializer=_init, initargs=(path, z)) as pool:
        results = [x for part in pool.imap(_job, items) for x in part]
    P = Problem(dict(w, _z=z))
    base = P.optimum(base_ops['A'], base_ops['B'])

    def cost(h):
        return sum(n * d * (64 / d) ** z for d, n in h.items())

    outcome = Counter('illegal' if h is None else 'same' if h == base else
                      'better' if cost(h) < cost(base) - 1e-9 else 'worse' for _, h in results)
    # per (section, gate, source) multiset of outcomes, compared with the primary detail rows
    mine = defaultdict(Counter)
    for (sec, i, s, dst, q), h in results:
        mine[(sec, i, s, dst)][None if h is None else tuple(sorted(h.items()))] += 1
    theirs = defaultdict(Counter)
    for row in prim['detail']:
        h = row['profile']
        theirs[(row['sec'], row['i'], row['s'], row['dst'])][None if h is None else
                                                             tuple(sorted((int(k), v) for k, v in h.items()))] += 1
    mismatches = sorted(str(k) for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
    print(json.dumps(dict(insertion_indices=total_indices, cross_scatter_indices=n_cross, classes=len(results), primary_candidates=len(prim['detail']),
                          base_profile=base, outcome=dict(outcome), mismatches_vs_primary=len(mismatches),
                          first_mismatches=mismatches[:5])))


if __name__ == '__main__':
    main()

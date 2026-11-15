#!/usr/bin/env python3
"""TOY4 checker: owned-set enumeration on F2^3 with births cuts, Charge Corollary, controls, 4-feeder replay, duality.

Own code (DreamingOfClouds with Claude Opus 5.5), standard library only.  Tags: [C] exact enumeration.
The lemmas themselves (Pin, time-cut basis, Down-set No-Loss (DNL), Charge Corollary, Duality) are proved in PROOF.md;
this script only enumerates and applies them.  The S2 proof is an outside-session lane of DreamingOfClouds'.

Checks (F2^3, 16 subspaces as frames, standard dot product)
  a. labels [1,2,4,7]: 8,261 owned multisets of ascending moves with total climb 3; 460 up-sets; 13 pass every births cut
     (for every up-set G: #moves a notin G, b in G >= #{ports j: <q_j> in G, q_j^perp notin G}).
  b. Charge Corollary blocks all 13 (port 7).  Labels [1,2,7], climb 2: exactly 1 cut-feasible set, blocked.
  c. Controls: 4 line feeders {0}->q pass the cuts and the corollary is silent; 0 owned fails the cuts.
     Climb 4: 2,074 cut-feasible sets; number blocked by the corollary is printed (asserted < 2,074, feeders not blocked).
  d. Exact Fraction replay of the real-time 4-feeder program: exact, owned climb 4.
  e. Duality O -> {(b^perp, a^perp)} permutes the 13 cut-feasible sets and preserves climb.
Prints PASS_TOY4_DECISION.
"""
import itertools, sys
from fractions import Fraction as Q


def fail(msg):
    print('FAIL:', msg); sys.exit(1)


def expect(name, got, want):
    ok = got == want
    print(('ok   ' if ok else 'FAIL ') + name + ': ' + str(got))
    if not ok:
        fail('%s: got %r want %r' % (name, got, want))


def span(vs):
    S = {0}
    for v in vs: S |= {x ^ v for x in S}
    return frozenset(S)


def subspaces(m):
    out = set()
    for k in range(m + 1):
        for B in itertools.combinations(range(1, 1 << m), k): out.add(span(B))
    return sorted(out, key=lambda s: (len(s), sorted(s)))


def dot(a, b): return bin(a & b).count('1') & 1


def setup(m):
    F = subspaces(m); return F, {f: i for i, f in enumerate(F)}


def down(F, g): return {i for i, f in enumerate(F) if f <= F[g]}


def dnl_fails(F, moves, g):
    if any(b == g for a, b in moves): return True
    D = down(F, g); ch = True
    while ch:
        ch = False
        for a, b in moves:
            if a in D and b not in D: D |= down(F, b); ch = True
    return any(F[g] < F[x] for x in D)


def analyse(m, labels, moves):
    """Charge Corollary.  Returns list of blocked port indices."""
    F, idx = setup(m); n = len(labels)
    cross = [[k for k, (a, b) in enumerate(moves) if q not in F[a] and q in F[b]] for q in labels]
    tight = [len(c) == 1 for c in cross]
    blocked = []
    for d in range(n):
        T = [s for s in range(n) if s != d and tight[s] and dot(labels[s], labels[d])]
        if not T: continue
        cand = [g for g, f in enumerate(F) if labels[d] in f and not any(labels[s] in f for s in T)]
        if not any(dnl_fails(F, moves, g) for g in cand): blocked.append(d)
    return blocked


class Enum:
    def __init__(self, m, labels):
        self.m, self.labels = m, labels
        F, idx = setup(m); self.F, self.idx = F, idx; nF = len(F)
        self.dimf = [len(f).bit_length() - 1 for f in F]
        up = [[j for j in range(nF) if F[i] <= F[j]] for i in range(nF)]
        line = [idx[span([q])] for q in labels]
        hyp = [idx[frozenset(x for x in range(1 << m) if dot(x, q) == 0)] for q in labels]
        self.ups = [M for M in range(1 << nF)
                    if all(all((M >> j) & 1 for j in up[i]) for i in range(nF) if (M >> i) & 1)]
        need = [(G, sum(1 for j in range(len(labels)) if (G >> line[j]) & 1 and not (G >> hyp[j]) & 1)) for G in self.ups]
        self.need = [(G, d) for G, d in need if d]
        self.mv = [(a, b, self.dimf[b] - self.dimf[a]) for a in range(nF) for b in range(nF) if a != b and F[a] <= F[b]]

    def cut_ok(self, ms):
        return all(sum(1 for a, b, _ in ms if not (G >> a) & 1 and (G >> b) & 1) >= d for G, d in self.need)

    def sets(self, climb):
        """(number of multisets of total climb == climb, list of cut-feasible ones)"""
        total = 0; sols = []
        mv = self.mv
        def rec(start, left, cur):
            nonlocal total
            if left == 0:
                total += 1
                if self.cut_ok(cur): sols.append([(a, b) for a, b, _ in cur])
                return
            for i in range(start, len(mv)):
                if mv[i][2] <= left: rec(i, left - mv[i][2], cur + [mv[i]])
        rec(0, climb, [])
        return total, sols


def perp_frame(m, f): return frozenset(x for x in range(1 << m) if all(dot(x, y) == 0 for y in f))


def dual(E, moves):
    F, idx = E.F, E.idx
    return sorted((idx[perp_frame(E.m, F[b])], idx[perp_frame(E.m, F[a])]) for a, b in moves)


def main():
    m = 3; L = [1, 2, 4, 7]
    E = Enum(m, L)
    expect('a. frames', len(E.F), 16)
    expect('a. up-sets of frame lattice', len(E.ups), 460)
    tot, sols = E.sets(3)
    expect('a. owned multisets with total climb 3', tot, 8261)
    expect('a. cut-feasible climb-3 sets', len(sols), 13)
    blk = [analyse(m, L, s) for s in sols]
    expect('b. Charge Corollary blocked sets (of 13)', sum(1 for b in blk if b), 13)
    expect('b. blocked port label(s) over all 13', sorted({L[d] for b in blk for d in b}), [7])
    E3 = Enum(m, [1, 2, 7]); t3, s3 = E3.sets(2)
    expect('b. labels [1,2,7] climb 2 cut-feasible sets', len(s3), 1)
    expect('b. labels [1,2,7] that set blocked', [bool(analyse(m, [1, 2, 7], s)) for s in s3], [True])
    # controls
    F, idx = E.F, E.idx; Z = idx[span([])]
    feed = [(Z, idx[span([q])]) for q in L]
    expect('c. 4 line feeders: cut-feasible', E.cut_ok([(a, b, 1) for a, b in feed]), True)
    expect('c. 4 line feeders: blocked ports', analyse(m, L, feed), [])
    expect('c. 0 owned: cut-feasible', E.cut_ok([]), False)
    t4, s4 = E.sets(4)
    print('     climb-4 multisets enumerated:', t4)
    expect('c. climb-4 cut-feasible sets', len(s4), 2074)
    nb4 = sum(1 for s in s4 if analyse(m, L, s))
    print('     Charge Corollary blocks %d of %d climb-4 cut-feasible sets' % (nb4, len(s4)))
    assert nb4 < 2074, 'corollary vacuous at climb 4'
    expect('c. 4-feeder set among climb-4 cut-feasible', sorted(feed) in [sorted(s) for s in s4], True)
    # d. exact replay (adapted from TOY4/control4.py)
    Vf = span([1, 2, 4]); Zf = span([])
    perp = lambda q: frozenset(x for x in range(8) if dot(x, q) == 0)
    dim = lambda f: len(f).bit_length() - 1
    regs = {}; cost = 0
    def new(name, frame, tok=None, owned=False): regs[name] = [frame, ({tok: Q(1)} if tok else {}), owned]
    def move(r, b):
        nonlocal cost
        a = regs[r][0]; assert a < b, ('not ascending', r)
        if regs[r][2]: cost += dim(b) - dim(a)
        regs[r][0] = b
    def add(r, s, c):
        assert regs[r][0] == regs[s][0], ('no common frame', r, s)
        R = regs[r][1]
        for k, v in regs[s][1].items():
            R[k] = R.get(k, 0) + Q(c) * v
            if R[k] == 0: del R[k]
    for s, q in enumerate(L):
        new('Y%d' % s, Zf, 'y%d' % s); new('T%d' % s, Zf, owned=True); new('X%d' % s, span([q]), 'x%d' % s)
        add('T%d' % s, 'Y%d' % s, 1); move('T%d' % s, span([q])); add('X%d' % s, 'T%d' % s, -1)
        l = next(x for x in sorted(perp(q)) if x)
        move('Y%d' % s, span([l])); move('Y%d' % s, perp(q))
        pl = span([q, next(x for x in range(1, 8) if x != q)]); move('X%d' % s, pl); move('X%d' % s, Vf)
    ok = all(regs['X%d' % s][1] == {'x%d' % s: 1, 'y%d' % s: -1} and regs['X%d' % s][0] == Vf and
             regs['Y%d' % s][1] == {'y%d' % s: 1} and regs['Y%d' % s][0] == perp(L[s]) for s in range(4))
    expect('d. 4-feeder replay exact', ok, True)
    expect('d. 4-feeder replay owned climb', cost, 4)
    # e. duality
    fam = sorted(sorted(s) for s in sols)
    img = sorted(dual(E, s) for s in sols)
    expect('e. dual image of the 13-set family = the family', img, fam)
    perm = [fam.index(dual(E, s)) for s in sols]
    expect('e. dual map is a permutation', sorted(perm), list(range(13)))
    clm = lambda s: sum(E.dimf[b] - E.dimf[a] for a, b in s)
    expect('e. climb preserved', all(clm(dual(E, s)) == 3 for s in sols), True)
    print('PASS_TOY4_DECISION')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""verify.py -- one shared call at three directions: two-term parts finish or remove, not both.

Standard library only, exact rational arithmetic. Reads no file and writes no file.

    python3 -B verify.py --part controls       the solver and the rule are not vacuous; modular arithmetic agrees
    python3 -B verify.py --part main           the complete table at 3 address bits and the rule that describes it
    python3 -B verify.py --part poststep       the parts that one more call and a free step after it can finish
    python3 -B verify.py --part symmetry       one first call and one shared call up to symmetry; a second shared
                                               call gives the same table
    python3 -B verify.py --part coefficients   other coefficients: kind A with -1, 2 and 1/2, kind B with -1 and 2
    python3 -B verify.py --part spare          the rule on a seeded sample with one spare address bit (4 bits)
    python3 -B verify.py --part full           (slow, not registered) every case one at a time, with no symmetry
                                               reduction; --quarter 0..3 runs one quarter of it

THE GAME (the frame game: the engine game with its Pauli part dropped; README section 3).
Labels are the vectors of F_2^(2m), written x | z << m, with the symplectic form <u, v> = x_u.z_v + z_u.x_v.
A term is an element g of Sp(2m, 2), stored as the images of the 2m basis labels; products act from right to left.
An array is a rational combination of terms. L is the set of labels with x = 0 (the raw frame). The FREE elements
are the g that map L to L (address maps and phases). A PAID call is a transvection t_u : v -> v + <v, u> u with u
outside L. Free steps multiply an array on the left by any rational combination of free elements, and add arrays.
A paid call multiplies one array on the left by one t_u. A free image of a term h is p.h with p free. The frame of
a term g is g^-1(L); two frames are adjacent when they meet in dimension m - 1. The level of g is
m - dim(g^-1(L) meet L), its distance from the raw frame.

THE QUESTION (README section 4). One input's part y of a shared array, after its first call D0 and the shared
call t_w. M = t_w.D0 is the plain middle term; the part has one extra term E, with coefficient c:
    kind A   y = t_w.(1 + c.gamma).D0     E = t_w.gamma.D0   (a free image of the first-call term went in too)
    kind B   y = t_w.(D0 + c.gamma)       E = t_w.gamma      (a free image of the raw input went in too)
with gamma free. The same input also has v = 1 (the raw input) and a = D0 (its first-call term).
    FINISHABLE BY THE CALL ALONE:  for some paid t that raises M to level 3, the term t.M is a free combination of
                 v, a, y plus t applied to a free combination of v, a, y. (No free combination is applied to the
                 output of t itself; --part poststep treats that.)
    REMOVABLE:   for some paid t, t.y is a free combination of v, a, y, plus t applied to free combinations of
                 v and a, plus other free images t.p.y (p free, p != 1) of the same call. A call t with t.t_w free
                 only undoes the shared call and is not tried. The program reports two counts: removable by a call
                 that could be a last call (t.t_w at level 2, so t can raise a middle term to level 3), and
                 removable by any call that is tried.
A case is "plain in disguise" and is set aside when y has one term or none, or E is a free image of v or of a.
"""
import argparse
import random
import sys
import time
from fractions import Fraction

PRIME = (1 << 61) - 1          # used only by a control; every result is computed in exact rational arithmetic


def parity(x):
    return bin(x).count("1") & 1


class Game:
    def __init__(self, m):
        self.m = m
        self.n = 1 << m
        self.mask = self.n - 1
        self.I = tuple(1 << j for j in range(2 * m))
        self.L = frozenset(z << m for z in range(self.n))
        self._free = None

    def form(self, u, v):
        m, k = self.m, self.mask
        return parity((u & k) & (v >> m)) ^ parity((u >> m) & (v & k))

    def apply(self, g, v):
        out, j = 0, 0
        while v:
            if v & 1:
                out ^= g[j]
            v >>= 1
            j += 1
        return out

    def mul(self, h, g):
        """h after g: the term g multiplied on the left by h"""
        ap = self.apply
        return tuple(ap(h, x) for x in g)

    def inv(self, g):
        tab = [0] * (1 << (2 * self.m))
        for v in range(1 << (2 * self.m)):
            tab[self.apply(g, v)] = v
        return tuple(tab[1 << j] for j in range(2 * self.m))

    def transv(self, u):
        return tuple((v ^ u) if self.form(v, u) else v for v in self.I)

    def is_symplectic(self, g):
        I = self.I
        return all(self.form(g[i], g[j]) == self.form(I[i], I[j]) for i in range(2 * self.m) for j in range(2 * self.m))

    def is_free(self, g):
        k = self.mask
        return all((g[j] & k) == 0 for j in range(self.m, 2 * self.m))

    def image_of_L(self, g):
        return frozenset(self.apply(g, x) for x in self.L)

    def frame(self, g):
        """g^-1(L)"""
        return self.image_of_L(self.inv(g))

    def level(self, g):
        """m - dim(g^-1(L) meet L)"""
        c = len(self.frame(g) & self.L)
        return self.m - (c.bit_length() - 1)

    def order(self, g):
        x, k = g, 1
        while x != self.I:
            x = self.mul(g, x)
            k += 1
        return k

    def free_generators(self):
        m = self.m
        gens = [self.transv(z << m) for z in range(1, self.n)]            # phases
        for i in range(m):
            for j in range(m):
                if i != j:                                                # address map: bit i added into bit j
                    g = list(self.I)
                    g[i] ^= 1 << j
                    g[m + j] ^= 1 << (m + i)
                    gens.append(tuple(g))
        for g in gens:
            assert self.is_symplectic(g) and self.is_free(g)
        return gens

    def free_group(self):
        if self._free is None:
            gens = self.free_generators()
            seen = {self.I}
            todo = [self.I]
            while todo:
                g = todo.pop()
                for h in gens:
                    x = self.mul(h, g)
                    if x not in seen:
                        seen.add(x)
                        todo.append(x)
            self._free = sorted(seen)
        return self._free

    def paid_calls(self):
        return [self.transv(u) for u in range(1, 1 << (2 * self.m)) if u & self.mask]


def left(G, h, arr):
    out = {}
    for g, c in arr.items():
        k = G.mul(h, g)
        c2 = out.get(k, 0) + c
        if c2:
            out[k] = c2
        else:
            out.pop(k, None)
    return out


def in_span(G, target, free_gens, paid_gens, prime=None, exclude=frozenset(), max_cols=3000):
    """Is the array `target` in   sum_R Q[P].R  +  sum_(t,R) t.Q[P].R   (P = the free elements)?

    free_gens: list of arrays R. paid_gens: list of (t, R). Arrays are dicts {term: integer coefficient}.
    exclude: set of (index into paid_gens, p) naming columns t.p.R that may not be used (R with two or more terms).
    Returns (answer, number of columns): answer True or False, or None if more than max_cols columns were needed.

    A generator with ONE term h gives every free image of h: every term g with g.h^-1 free (or t.g.h^-1 free for
    a paid generator) is such a column by itself, so those terms are dropped everywhere. For a generator with
    several terms, a column p.R or t.p.R can only help if one of its terms is a term that still has to be
    cancelled, and that fixes p; so the columns are found by following terms from the target, and the columns
    never reached share no term with it. The elimination is in exact rational arithmetic (prime=None), or
    modulo `prime` when one is given (a control only)."""
    mul, inv, is_free = G.mul, G.inv, G.is_free
    single = []          # (t or None, h^-1)
    multi = []           # (index in paid_gens or -1, t or None, R, [(h^-1, c)])
    for R in free_gens:
        if len(R) == 1:
            single.append((None, inv(next(iter(R)))))
        elif R:
            multi.append((-1, None, R, [inv(h) for h in R]))
    for i, (t, R) in enumerate(paid_gens):
        if len(R) == 1:
            single.append((t, inv(next(iter(R)))))
        elif R:
            multi.append((i, t, R, [inv(h) for h in R]))
    cache = {}

    def is_free_image(g):
        r = cache.get(g)
        if r is None:
            r = False
            for t, hi in single:
                x = mul(g, hi)
                if is_free(x if t is None else mul(t, x)):
                    r = True
                    break
            cache[g] = r
        return r

    if prime is None:
        def num(c):
            return Fraction(c)

        def recip(c):
            return 1 / c
    else:
        def num(c):
            return c % prime

        def recip(c):
            return pow(c, prime - 2, prime)

    def project(arr):
        return {g: num(c) for g, c in arr.items() if not is_free_image(g)}

    tvec = project(target)
    if not tvec:
        return True, 0
    cols = {}
    done = set()
    frontier = list(tvec)
    while frontier:
        nxt = []
        for g in frontier:
            if g in done:
                continue
            done.add(g)
            for gi, (pi, t, R, invs) in enumerate(multi):
                for hi in invs:
                    p = mul(g, hi) if t is None else mul(t, mul(g, hi))
                    if not is_free(p):
                        continue
                    key = (gi, p)
                    if key in cols or (pi, p) in exclude:
                        continue
                    col = left(G, p, R)
                    if t is not None:
                        col = left(G, t, col)
                    vec = project(col)
                    cols[key] = vec
                    nxt.extend(k for k in vec if k not in done)
                    if len(cols) > max_cols:
                        return None, len(cols)
        frontier = nxt
    pivots = {}
    basis = []

    def reduce(vec):
        while True:
            best = None
            for k in vec:
                i = pivots.get(k)
                if i is not None and (best is None or i < best):
                    best = i
            if best is None:
                return vec
            pk, bv = basis[best]
            f = vec[pk]
            for k, x in bv.items():
                nv = num(vec.get(k, 0) - f * x)
                if nv:
                    vec[k] = nv
                else:
                    vec.pop(k, None)

    for vec in cols.values():
        r = reduce(dict(vec))
        if r:
            pk = next(iter(r))
            f = recip(r[pk])
            pivots[pk] = len(basis)
            basis.append((pk, {k: num(x * f) for k, x in r.items()}))
    return (not reduce(dict(tvec))), len(cols)


class Setting:
    """a first call D0 = t_(X0), a shared call t_w, and everything fixed by them"""

    def __init__(self, m, w, prime=None):
        G = self.G = Game(m)
        self.w = w
        self.prime = prime
        self.D0 = G.transv(1)
        self.tw = G.transv(w)
        self.main = G.mul(self.tw, self.D0)
        assert G.level(self.D0) == 1 and G.level(self.main) == 2
        self.v = {G.I: 1}
        self.a = {self.D0: 1}
        self.paid = G.paid_calls()
        self.lifting = [t for t in self.paid if G.level(G.mul(t, self.main)) == 3]
        lev = [G.level(G.mul(t, self.tw)) for t in self.paid]
        self.undo = frozenset(i for i, x in enumerate(lev) if x == 0)       # t.t_w free: t undoes the shared call
        self.last = frozenset(i for i, x in enumerate(lev) if x == 2)       # t can raise a middle term to level 3
        assert len(self.undo) + len(self.last) + sum(1 for x in lev if x == 1) == len(self.paid)
        self.main_inv = G.inv(self.main)
        self.main_frame = G.frame(self.main)
        self.tests = 0

    def part(self, kind, gamma, coef=1):
        G = self.G
        second = G.mul(self.tw, G.mul(gamma, self.D0)) if kind == "A" else G.mul(self.tw, gamma)
        y = {self.main: 1}
        c = y.get(second, 0) + coef
        if c:
            y[second] = c
        else:
            y.pop(second, None)
        return y, second

    def skipped(self, y, second):
        """plain in disguise"""
        G = self.G
        return len(y) < 2 or G.is_free(second) or G.is_free(G.mul(second, self.D0))

    def finishable(self, y):
        """by the call alone"""
        G = self.G
        for t in self.lifting:
            self.tests += 1
            ans, _ = in_span(G, {G.mul(t, self.main): 1}, [self.v, self.a, y],
                             [(t, self.v), (t, self.a), (t, y)], self.prime)
            assert ans is not None
            if ans:
                return True
        return False

    def removing_calls(self, y):
        """the calls that pass the removal test, as indices into self.paid"""
        G = self.G
        assert len(y) >= 2                          # in_span ignores `exclude` for a generator with one term
        out = []
        for i, t in enumerate(self.paid):
            if i in self.undo:                      # a call that only undoes the shared call is not tried
                continue
            self.tests += 1
            ans, _ = in_span(G, left(G, t, y), [self.v, self.a, y], [(t, self.v), (t, self.a), (t, y)],
                             self.prime, exclude=frozenset({(2, G.I)}))
            assert ans is not None
            if ans:
                out.append(i)
        return out

    def answers(self, y):
        """(finishable by the call alone, removable by a possible last call, removable by any call tried,
        number of calls that remove)"""
        calls = self.removing_calls(y)
        return self.finishable(y), any(i in self.last for i in calls), bool(calls), len(calls)

    # ---- the rule
    def frames(self, kind, gamma):
        """how the frame of the extra term E sits to the frame of the plain middle term M:
        ('same', order of the free element g with E = g.M), ('adjacent', 0) or ('apart', 0)"""
        G = self.G
        second = G.mul(self.tw, G.mul(gamma, self.D0)) if kind == "A" else G.mul(self.tw, gamma)
        k = len(G.frame(second) & self.main_frame)
        if k == len(self.main_frame):
            g = G.mul(second, self.main_inv)
            assert G.is_free(g)
            return "same", G.order(g)
        return ("adjacent" if 2 * k == len(self.main_frame) else "apart"), 0

    def rule_A(self, gamma, coef=1):
        """(finishable by the call alone, removable by a possible last call, removable by any call tried)
        predicted for the kind A part t_w.(1 + coef.gamma).D0.
        On the same frame the part is (1 + coef.g).M with g free, and 1 + coef.g is invertible in the group
        algebra exactly when (-coef)^(order of g) is not 1."""
        k, o = self.frames("A", gamma)
        if k == "same":
            unit = (-Fraction(coef)) ** o != 1
            return (unit and o > 1), (not unit), (not unit)
        return False, False, (k == "adjacent" and abs(coef) == 1)

    def swapped(self, kind, gamma):
        """some paid call carries M onto the frame of E and E onto the frame of M"""
        G = self.G
        y, second = self.part(kind, gamma)
        inv2 = G.inv(second)
        return any(G.is_free(G.mul(G.mul(t, self.main), inv2)) and G.is_free(G.mul(G.mul(t, second), self.main_inv))
                   for t in self.paid)

    def symmetries(self):
        """the free s with s* = D0.s.D0 free. Right multiplication of every term by s* keeps the free images of
        v and of a, and maps the question for (t_w, gamma) onto the question for (t_(s^-1 w), gamma'), where
        gamma' = s^-1.gamma.s for kind A and gamma' = s^-1.gamma.s* for kind B   (README section 5)"""
        G = self.G
        return [s for s in G.free_group() if G.is_free(G.mul(self.D0, G.mul(s, self.D0)))]

    def centraliser(self):
        G = self.G
        return [s for s in G.free_group() if G.mul(s, self.D0) == G.mul(self.D0, s)
                and G.mul(s, self.tw) == G.mul(self.tw, s)]


def conjugacy_orbits(S):
    """orbits of gamma -> s^-1.gamma.s over the free s that commute with D0 and t_w. Such an s has s* = s, so
    right multiplication of every term by it maps the question for gamma onto the question for s^-1.gamma.s,
    for both kinds (README section 5)."""
    G = S.G
    C = S.centraliser()
    Cinv = [G.inv(s) for s in C]
    rep = {}
    orbits = {}
    for g in G.free_group():
        if g in rep:
            continue
        orb = {G.mul(si, G.mul(g, s)) for s, si in zip(C, Cinv)}
        r = min(orb)
        for x in orb:
            rep[x] = r
        orbits[r] = sorted(orb)
    return C, orbits


def counts(tab):
    """(tested, finishable by the call alone, removable by a possible last call, removable by any call, both)"""
    return (len(tab), sum(f for f, rl, ra, n in tab.values()), sum(rl for f, rl, ra, n in tab.values()),
            sum(ra for f, rl, ra, n in tab.values()), sum(f and ra for f, rl, ra, n in tab.values()))


def table(S, kind, orbits=None, show=True, coef=1):
    """the table for one kind of part: {gamma: answers} for every gamma that is not plain in disguise"""
    G = S.G
    out = {}
    skipped = 0
    items = orbits.items() if orbits is not None else ((g, [g]) for g in G.free_group())
    for r, orb in items:
        y, second = S.part(kind, r, coef)
        if S.skipped(y, second):
            for x in orb:
                y2, s2 = S.part(kind, x, coef)
                assert S.skipped(y2, s2)
            skipped += len(orb)
            continue
        res = S.answers(y)
        for x in orb:
            out[x] = res
    if show:
        n, f, rl, ra, both = counts(out)
        print(f"   kind {kind}  tested {n:5d}  plain in disguise {skipped:4d}  finishable by the call alone {f:4d}  "
              f"removable by a possible last call {rl:4d}, by any call {ra:5d}  both {both}")
    return out, skipped


# tested, plain in disguise, finishable by the call alone, removable by a possible last call, removable by any call
EXPECT = {"A": (9983, 769, 128, 639, 1407), "B": (9984, 768, 0, 128, 128)}


def check_tables(S, use_orbits):
    G = S.G
    P = G.free_group()
    assert len(P) == 10752 and len(S.paid) == 56 and len(S.lifting) == 32
    assert len(S.undo) == 4 and len(S.last) == 48
    orbits = None
    if use_orbits:
        C, orbits = conjugacy_orbits(S)
        print(f"   shared call t_w, w = {S.w}: {len(C)} free elements commute with both calls; "
              f"{len(orbits)} classes of gamma")
    by, orders = {}, {}
    for g in P:
        k, o = S.frames("A", g)
        key = k if k != "same" else ("same frame, E = M" if o == 1 else
                                     "same frame, odd order" if o % 2 else "same frame, even order")
        by[key] = by.get(key, 0) + 1
        if k == "same":
            orders[o] = orders.get(o, 0) + 1
    assert by == {"same frame, E = M": 1, "same frame, odd order": 128, "same frame, even order": 639,
                  "adjacent": 768, "apart": 9216}, by
    assert orders == {1: 1, 2: 127, 3: 128, 4: 384, 6: 128}, orders
    print(f"   kind A, frames of the two terms: {by}")
    print(f"   kind A, same frame: orders of g {dict(sorted(orders.items()))}")
    tabs = {}
    for kind in ("A", "B"):
        tab, skipped = table(S, kind, orbits)
        tabs[kind] = tab
        n, f, rl, ra, both = counts(tab)
        assert (n, skipped, f, rl, ra) == EXPECT[kind], (kind, n, skipped, f, rl, ra)
        assert both == 0, "a case is both finishable and removable"
    # the rule for kind A, exactly; and which calls remove
    for g, (f, rl, ra, n) in tabs["A"].items():
        assert (f, rl, ra) == S.rule_A(g)
        k = S.frames("A", g)[0]
        if ra:
            assert n == (52 if k == "same" else 4) and rl == (k == "same")
        assert S.swapped("A", g) == (k == "adjacent")
    for g in P:
        if g not in tabs["A"]:
            assert g == G.I or S.frames("A", g)[0] == "apart"
    print("   kind A: finishable by the call alone = same frame with g of odd order (128); removable by a possible"
          " last call = same frame with g of even order (639, by every one of the 52 calls tried); the 768"
          " adjacent-frame parts are removable only by the 4 calls with t.t_w at level 1, which cannot be a last"
          " call, and they are exactly the parts for which some call carries M onto the frame of E and E onto the"
          " frame of M; the rule matches all 9,983 cases; none is both")
    # kind B: what is known
    rel, rem = {}, {}
    for g, (f, rl, ra, n) in tabs["B"].items():
        k = S.frames("B", g)[0]
        rel[k] = rel.get(k, 0) + 1
        if ra:
            rem[k] = rem.get(k, 0) + 1
        assert rl == ra == S.swapped("B", g)
    assert rel == {"adjacent": 1536, "apart": 8448} and rem == {"adjacent": 128}, (rel, rem)
    print("   kind B: none finishable; 128 removable, each by a possible last call, all among the 1,536 cases with"
          " adjacent frames, and exactly the cases where some call carries M onto the frame of E and E onto the"
          " frame of M; none is both")
    print(f"   [{S.tests} span tests, exact rational arithmetic]")
    return tabs, orbits


def part_main():
    t0 = time.time()
    print("3 address bits: two-term parts of kinds A and B of one shared array (10,752 free gamma for each kind)")
    S = Setting(3, 2)
    tabs, orbits = check_tables(S, True)
    # the symmetry reduction, tested directly on cases that were not representatives
    rng = random.Random(1002)
    others = [g for r, orb in orbits.items() for g in orb if g != r]
    n = 0
    for kind in ("A", "B"):
        sample = [g for g in rng.sample(others, 60) if g in tabs[kind]][:40]
        for g in sample:
            y, _ = S.part(kind, g)
            assert S.answers(y) == tabs[kind][g]
            n += 1
    print(f"   the reduction to classes was tested directly on {n} cases that were not representatives "
          f"[{time.time() - t0:.0f} s]")
    print("PASS_COMPLEX_M3_SHARED_CALL_MAIN")


def part_poststep():
    """kind A parts finished by one more call followed by a free step on its output.
    If a call t raises M to level 3 and puts t.E among the free images of t.M (t.E = h.t.M with h free), then
    t.y = (1 + c.h).t.M, and when 1 + c.h is invertible, (1 + c.h)^-1 applied to the call's output is the single
    third-level term t.M. The inverse is sum_j (-c)^j h^j / (1 - (-c)^n) for h of order n."""
    t0 = time.time()
    S = Setting(3, 2)
    G = S.G
    print("3 address bits, kind A: parts finished by one more call and a free step applied to its output")
    expect = {1: 128, -1: 0, 2: 512, Fraction(1, 2): 512}
    for c in (1, -1, 2, Fraction(1, 2)):
        c = Fraction(c)
        found, orders = 0, {}
        for g in G.free_group():
            y, second = S.part("A", g, c)
            if S.skipped(y, second) or S.frames("A", g)[0] == "same":
                continue
            rel = G.mul(second, S.main_inv)                       # E.M^-1
            for t in S.lifting:
                h = G.mul(t, G.mul(rel, t))                       # t.E.(t.M)^-1
                if not G.is_free(h):
                    continue
                n = G.order(h)
                if (-c) ** n == 1:
                    continue
                out, hp, ty = {}, G.I, left(G, t, y)
                for j in range(n):
                    for term, x in left(G, hp, ty).items():
                        out[term] = out.get(term, 0) + (-c) ** j / (1 - (-c) ** n) * x
                    hp = G.mul(h, hp)
                assert {k: x for k, x in out.items() if x} == {G.mul(t, S.main): 1}
                # frames apart, and by the rule neither finishable by the call alone nor removable
                assert S.frames("A", g)[0] == "apart" and S.rule_A(g, c) == (False, False, False)
                found += 1
                orders[n] = orders.get(n, 0) + 1
                break
        assert found == expect[c], (c, found)
        assert c != 1 or set(orders) <= {3}
        print(f"   c = {c}: {found} parts with frames apart are finished by one call and one free step after it"
              f" (orders of h: {dict(sorted(orders.items()))})")
    print(f"   each identity (1 + c.h)^-1.(t.y) = t.M is checked term by term; by the rule checked in the other"
          f" parts, none of these parts is finishable by the call alone or removable [{time.time() - t0:.0f} s]")
    print("PASS_COMPLEX_M3_SHARED_CALL_POSTSTEP")


def part_full(quarters=(0, 1, 2, 3)):
    """every gamma one at a time: kind A against the rule (which fixes the whole kind A table), kind B counted"""
    t0 = time.time()
    S = Setting(3, 2)
    G = S.G
    P = G.free_group()
    print(f"3 address bits, no symmetry reduction: quarters {list(quarters)} (gamma number i is in quarter i mod 4)")
    tot = {"A": [0] * 5, "B": [0] * 5}        # tested, plain in disguise, finishable, removable (last), removable (any)
    for k in quarters:
        row = {"A": [0] * 5, "B": [0] * 5}
        for g in P[k::4]:
            for kind in ("A", "B"):
                y, second = S.part(kind, g)
                if S.skipped(y, second):
                    row[kind][1] += 1
                    continue
                f, rl, ra, n = S.answers(y)
                assert not (f and ra), "a case is both finishable and removable"
                if kind == "A":
                    assert (f, rl, ra) == S.rule_A(g)
                else:
                    assert not f and rl == ra and (not ra or S.frames("B", g)[0] == "adjacent")
                row[kind][0] += 1
                row[kind][2] += f
                row[kind][3] += rl
                row[kind][4] += ra
        for kind in ("A", "B"):
            r = row[kind]
            print(f"   quarter {k}: kind {kind}  tested {r[0]:5d}  plain in disguise {r[1]:4d}  finishable {r[2]:4d}  "
                  f"removable by a possible last call {r[3]:4d}, by any call {r[4]:5d}  both 0   "
                  f"[{time.time() - t0:.0f} s]")
            tot[kind] = [x + y for x, y in zip(tot[kind], r)]
    if tuple(quarters) == (0, 1, 2, 3):
        assert tuple(tot["A"]) == EXPECT["A"] and tuple(tot["B"]) == EXPECT["B"], tot
        print("   totals as in the main table; every kind A case matches the rule; none is both")
        print("PASS_COMPLEX_M3_SHARED_CALL_FULL")
    else:
        print("   every kind A case of these quarters matches the rule; none is both")
        print(f"PASS_COMPLEX_M3_SHARED_CALL_FULL_QUARTER_{'_'.join(str(k) for k in quarters)}")


def part_symmetry():
    t0 = time.time()
    G = Game(3)
    labels = [u for u in range(1, 1 << 6) if u & G.mask]
    # 1. the free elements move the first call to every other paid call
    orb, todo, gens = {1}, [1], G.free_generators()
    while todo:
        u = todo.pop()
        for h in gens:
            x = G.apply(h, u)
            if x not in orb:
                orb.add(x)
                todo.append(x)
    assert sorted(orb) == labels and len(labels) == 56
    print("   the free elements carry the first call to each of the 56 paid calls")
    # 2. the shared calls that give a level-2 term form one class under the symmetries of the question
    S = Setting(3, 2)
    mids = [w for w in labels if G.level(G.mul(G.transv(w), S.D0)) == 2]
    sym = S.symmetries()
    reach = {2}
    for s in sym:
        reach.add(G.apply(G.inv(s), 2))
    assert len(mids) == 48 and len(sym) == 768 and sorted(reach) == mids
    print("   48 shared calls give a level-2 term; the 768 symmetries carry w = 2 to each of them")
    # 3. a second shared call: the same counts and the same rule
    print("   the table again for the shared call w = 10:")
    S10 = Setting(3, 10)
    tabs10, _ = check_tables(S10, True)
    # 4. the symmetry itself, case by case: gamma at w = 2 against gamma' at w = 10
    cands = [s for s in sym if G.apply(G.inv(s), 2) == 10]
    s = next(s for s in cands if G.mul(s, S.D0) != G.mul(S.D0, s))       # one that does not commute with D0
    si = G.inv(s)
    sstar_inv = G.mul(S.D0, G.mul(si, S.D0))
    assert len(cands) == 16 and G.is_free(sstar_inv) and sstar_inv != si
    rng = random.Random(1010)
    n = 0
    for kind in ("A", "B"):
        keys = sorted(tabs10[kind])
        chosen = [g for g in keys if tabs10[kind][g][2]] if kind == "B" else []
        have = set(chosen)
        chosen += rng.sample([g for g in keys if g not in have], 120)
        for g10 in chosen:
            g2 = G.mul(s, G.mul(g10, si if kind == "A" else sstar_inv))
            y, second = S.part(kind, g2)
            assert not S.skipped(y, second)
            assert S.answers(y) == tabs10[kind][g10]
            n += 1
    print(f"   the symmetry was tested case by case on {n} distinct cases, among them all 128 removable kind B parts "
          f"[{time.time() - t0:.0f} s]")
    print("PASS_COMPLEX_M3_SHARED_CALL_SYMMETRY")


def part_coefficients():
    t0 = time.time()
    print("3 address bits, other coefficients c of the extra term")
    half = Fraction(1, 2)
    # finishable by the call alone, removable by a possible last call, removable by any call
    expect = {("A", -1): (0, 767, 1535), ("A", 2): (767, 0, 0), ("A", half): (767, 0, 0),
              ("B", -1): (0, 128, 128), ("B", 2): (0, 0, 0)}
    S = Setting(3, 2)
    C, orbits = conjugacy_orbits(S)
    for (kind, c), want in expect.items():
        print(f"   c = {c}:")
        tab, skipped = table(S, kind, orbits, coef=c)
        n, f, rl, ra, both = counts(tab)
        assert (n, skipped) == EXPECT[kind][:2] and (f, rl, ra) == want and both == 0, (kind, c, n, skipped, f, rl, ra)
        if kind == "A":
            assert all(res[:3] == S.rule_A(g, c) for g, res in tab.items())
        elif c == -1:
            # the same parts as for c = 1 (--part main checks that test for c = 1)
            assert all(res[2] == S.swapped("B", g) for g, res in tab.items())
    print("   kind A: the rule with a coefficient matches every case. c = -1: nothing is finishable, the 767"
          " same-frame cases are removable by a possible last call. c = 2 and c = 1/2: the 767 same-frame cases are"
          " finishable by the call alone and nothing is removable")
    print(f"   kind B: c = -1 as c = 1 (none finishable, the same 128 parts removable); c = 2: nothing either way;"
          f" none is both in any row [{time.time() - t0:.0f} s]")
    print("PASS_COMPLEX_M3_SHARED_CALL_COEFFICIENTS")


def part_spare(sizes=(20, 20, 20, 40), seed=2026):
    t0 = time.time()
    S = Setting(4, 2)
    G = S.G
    rng = random.Random(seed)
    gens = G.free_generators()
    names = ["same frame, even order", "adjacent frames", "same frame, odd order", "frames apart"]
    want = dict(zip(names, sizes))
    pool = {k: [] for k in names}
    seen = set()
    drawn = 0
    while any(len(pool[k]) < want[k] for k in names):
        g = G.I
        for _ in range(40):
            g = G.mul(rng.choice(gens), g)
        drawn += 1
        if g in seen or g == G.I:
            continue
        seen.add(g)
        y, second = S.part("A", g)
        if S.skipped(y, second):
            continue
        k, o = S.frames("A", g)
        name = ("same frame, even order" if o % 2 == 0 else "same frame, odd order") if k == "same" else \
            ("adjacent frames" if k == "adjacent" else "frames apart")
        if len(pool[name]) < want[name]:
            pool[name].append(g)
    print(f"4 address bits (one spare), kind A, shared call w = 2: {drawn} random free elements drawn, seed {seed}; "
          f"{len(S.paid)} paid calls, {len(S.lifting)} of them raise the plain middle term to level 3, "
          f"{len(S.last)} could be a last call")
    bad = 0
    for name in names:
        fin = reml = rema = 0
        for g in pool[name]:
            y, _ = S.part("A", g)
            f, rl, ra, n = S.answers(y)
            fin += f
            reml += rl
            rema += ra
            bad += (f, rl, ra) != S.rule_A(g) or (f and ra)
        print(f"   {name:24s} sampled {len(pool[name]):3d}  finishable by the call alone {fin:3d}  "
              f"removable by a possible last call {reml:3d}, by any call {rema:3d}")
    assert bad == 0, bad
    print(f"   the rule found at 3 address bits is right on all {sum(sizes)} sampled cases; none is both "
          f"[{S.tests} span tests, {time.time() - t0:.0f} s]")
    print("PASS_COMPLEX_M3_SHARED_CALL_SPARE")


def part_controls():
    t0 = time.time()
    S = Setting(3, 2)
    G = S.G
    P = G.free_group()
    # 1. the solver finds the plain last call and refuses a missing one
    plain = {S.main: 1}
    T = [G.mul(t, S.main) for t in S.lifting]
    assert all(in_span(G, {G.mul(t, S.main): 1}, [S.v, S.a, plain], [(t, S.v), (t, S.a), (t, plain)])[0]
               for t in S.lifting)
    assert not any(in_span(G, {x: 1}, [S.v, S.a], [(t, S.v), (t, S.a)])[0] for x in T[:8] for t in S.paid)
    print("   the solver finds the plain third call and refuses a target two calls away")
    # 2. arithmetic modulo a large prime gives the same answers on a seeded sample from every class
    rng = random.Random(7)
    S2 = Setting(3, 2, PRIME)
    groups = {}
    for g in P:
        k, o = S.frames("A", g)
        groups.setdefault((k, o % 2 if k == "same" else 0), []).append(g)
    n = 0
    for key in sorted(groups):
        for g in rng.sample(groups[key], min(12, len(groups[key]))):
            for kind in ("A", "B"):
                y, second = S.part(kind, g)
                if S.skipped(y, second):
                    continue
                r1 = S.answers(y)
                assert r1 == S2.answers(y)
                if kind == "A":
                    assert r1[:3] == S.rule_A(g)
                n += 1
    print(f"   exact arithmetic and arithmetic modulo 2^61 - 1 give the same answers on {n} seeded cases")
    # 3. the rule is not vacuous: each wrong variant fails on some sampled case
    cases = []
    for key in sorted(groups):
        for g in rng.sample(groups[key], min(6, len(groups[key]))):
            y, second = S.part("A", g)
            if not S.skipped(y, second):
                cases.append((g, S.answers(y)[:3]))

    def variant(name, g):
        k, o = S.frames("A", g)
        same = k == "same"
        odd, even = same and o % 2 == 1 and o > 1, same and o % 2 == 0
        if name == "parities swapped":
            return even, odd, odd or k == "adjacent"
        if name == "adjacent frames removable by a last call":
            return odd, even or k == "adjacent", even or k == "adjacent"
        if name == "frames apart removable":
            return odd, even, not odd
    for name in ("parities swapped", "adjacent frames removable by a last call", "frames apart removable"):
        assert any(variant(name, g) != res for g, res in cases), name
    assert all(S.rule_A(g) == res for g, res in cases)
    print(f"   three wrong variants of the rule are each rejected on {len(cases)} seeded cases")
    # 4. coefficient -1 never finishes (1 - g is never invertible), on a seeded sample of same-frame cases
    same = [g for g in P if S.frames("A", g)[0] == "same" and g != G.I]
    m = 0
    for g in rng.sample(same, 24):
        y, second = S.part("A", g, coef=-1)
        if not S.skipped(y, second):
            assert not S.finishable(y)
            m += 1
    print(f"   with coefficient -1 no same-frame part is finishable ({m} seeded cases) [{time.time() - t0:.0f} s]")
    print("PASS_COMPLEX_M3_SHARED_CALL_CONTROLS")


if __name__ == "__main__":
    if not __debug__:
        sys.exit("verify.py checks with assert statements: run it without -O")
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["controls", "main", "poststep", "symmetry", "coefficients", "spare", "full"],
                    required=True)
    ap.add_argument("--quarter", type=int, choices=[0, 1, 2, 3], help="full only: one quarter of the cases")
    args = ap.parse_args()
    if args.part == "full":
        part_full((0, 1, 2, 3) if args.quarter is None else (args.quarter,))
    else:
        {"controls": part_controls, "main": part_main, "poststep": part_poststep, "symmetry": part_symmetry,
         "coefficients": part_coefficients, "spare": part_spare}[args.part]()
    sys.exit(0)

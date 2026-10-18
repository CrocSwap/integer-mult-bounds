"""KB3j engine tests: every walk engine is validated against complete brute
force on the smallest instances before any F2^5 walk number is trusted.

Run: python3 -I -B research/f7-18point-av42-kb3j-b1/test_engine.py
Expected: Ran N tests ... OK
"""

import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import walk42  # noqa: E402


def brute_w(u, v, wsize, bits, allm, d1):
    """Complete brute force: all wsize-sets W of F2^bits passing (a),(b),(c)."""
    n = 1 << bits
    vd = walk42.sumset_g(v, d1, bits, allm)
    ud = walk42.sumset_g(u, d1, bits, allm)
    uv = walk42.sumset_g(u, v, bits, allm)
    out = set()
    for wc in combinations(range(n), wsize):
        w = sum(1 << c for c in wc)
        wd = walk42.sumset_g(w, d1, bits, allm)
        if (
            (walk42.sumset_g(u, w, bits, allm) | vd) == allm
            and (ud | walk42.sumset_g(v, w, bits, allm)) == allm
            and (uv | wd) == allm
        ):
            out.add(w)
    return out


def brute_w_full(u, v, wsize, bits, allm, d1):
    """Complete brute force: all wsize-sets W passing all four lines."""
    n = 1 << bits
    out = set()
    for wc in combinations(range(n), wsize):
        w = sum(1 << c for c in wc)
        ok, _ = walk42.lines42_g(u, v, w, d1, bits, allm)
        if ok:
            out.add(w)
    return out


class TestLines42(unittest.TestCase):
    def test_residual_symmetry(self):
        """lines42 is invariant under (u+a, v+b, w+a+b): the normalization
        0 in U, 0 in V used by the walk is a genuine symmetry."""
        rng = random.Random(20261016)
        for _ in range(300):
            u = rng.randrange(1 << 5)
            v = rng.randrange(1 << 5)
            w = rng.randrange(1 << 5)
            a = rng.randrange(1 << 5)
            b = rng.randrange(1 << 5)
            ok1, _ = walk42.lines42(u, v, w)
            ok2, _ = walk42.lines42(walk42.T5(u, a), walk42.T5(v, b), walk42.T5(w, a ^ b))
            self.assertEqual(ok1, ok2)

    def test_mirror_symmetry(self):
        rng = random.Random(7)
        for _ in range(300):
            u = rng.randrange(1 << 5)
            v = rng.randrange(1 << 5)
            w = rng.randrange(1 << 5)
            ok1, _ = walk42.lines42(u, v, w)
            ok2, _ = walk42.lines42(v, u, w)
            self.assertEqual(ok1, ok2)


class TestSolveW(unittest.TestCase):
    def test_solve_w42_fast_matches(self):
        """The walk hot path (solve_w42_fast) equals the reference solve_w42
        on sampled F2^5 pairs."""
        rng = random.Random(31)
        for _ in range(6):
            uc = rng.sample(range(1, 32), 5)
            u = 1 | walk42.tight.mask_of(uc)
            ue = (0,) + tuple(uc)
            TU = [0] * 32
            for r in range(32):
                m = 0
                for a in ue:
                    m |= walk42.X32[a][r]
                TU[r] = m
            v = 1 | sum(1 << c for c in rng.sample(range(1, 32), 5))
            vd = walk42.S5(v, walk42.D1M5)
            ud = walk42.S5(u, walk42.D1M5)
            a = set(walk42.solve_w42(u, v, 4))
            b = set(walk42.solve_w42_fast(u, v, 4, TU, vd, ud))
            self.assertEqual(a, b)

    def test_solve_equals_bruteforce_m5(self):
        """solve_w42 equals complete brute force over all C(32,4) W 4-sets on
        sampled F2^5 pairs."""
        rng = random.Random(11)
        seen = 0
        for t in range(5):
            u = 1 | sum(1 << c for c in rng.sample(range(1, 32), 5))
            v = 1 | sum(1 << c for c in rng.sample(range(1, 32), 5))
            ws = set(walk42.solve_w42(u, v, 4))
            ref = brute_w(u, v, 4, 5, walk42.ALL5, walk42.D1M5)
            self.assertEqual(ws, ref, "u=%r v=%r" % (u, v))
            seen += len(ws)
        # NOTE: on random F2^5 pairs both engines find ZERO W candidates - the
        # (5,1)-style pair-level kill shape.  Equality with brute force is the
        # tested contract; existence of covers is guarded at m=3 below.

    def test_solve_equals_bruteforce_m3(self):
        rng = random.Random(5)
        covers = 0
        for _ in range(30):
            u = 1 | sum(1 << c for c in rng.sample(range(1, 8), rng.randrange(1, 7)))
            v = 1 | sum(1 << c for c in rng.sample(range(1, 8), rng.randrange(1, 7)))
            for wsz in range(0, 9):
                ws = set(walk42.solve_w42_g(u, v, 3, 255, 0b11, wsz))
                ref = brute_w(u, v, wsz, 3, 255, 0b11)
                self.assertEqual(ws, ref, "u=%r v=%r wsize=%d" % (u, v, wsz))
                for w in ws:
                    ok, _ = walk42.lines42_g(u, v, w, 0b11, 3, 255)
                    covers += 1 if ok else 0
        self.assertGreater(covers, 0, "false-empty guard: expected covers at m=3")

    def test_full_line_check_matches(self):
        rng = random.Random(23)
        for _ in range(20):
            u = 1 | sum(1 << c for c in rng.sample(range(1, 8), rng.randrange(1, 7)))
            v = 1 | sum(1 << c for c in rng.sample(range(1, 8), rng.randrange(1, 7)))
            for wsz in range(0, 9):
                ws = walk42.solve_w42_g(u, v, 3, 255, 0b11, wsz)
                ref = brute_w_full(u, v, wsz, 3, 255, 0b11)
                got = set()
                for w in ws:
                    ok, _ = walk42.lines42_g(u, v, w, 0b11, 3, 255)
                    if ok:
                        got.add(w)
                self.assertEqual(got, ref, "u=%r v=%r wsize=%d" % (u, v, wsz))


class TestPairBacktrack(unittest.TestCase):
    def test_pair_backtrack42_equals_bruteforce(self):
        """pair_backtrack42 equals brute force over all normalized V at need
        24 and 27 on a sampled U (the excess monotonicity used by the walk)."""
        rng = random.Random(3)
        uc = rng.sample(range(1, 32), 5)
        u = 1 | walk42.tight.mask_of(uc)
        ue = (0,) + tuple(uc)
        TU = [0] * 32
        for r in range(32):
            m = 0
            for a in ue:
                m |= walk42.X32[a][r]
            TU[r] = m
        for need in (24, 27):
            got = set()
            for (vm, vl, uv, sv) in walk42.pair_backtrack42(u, need, TU):
                got.add(vm)
            ref = set()
            for vc in combinations(range(1, 32), 5):
                vm = 1 | walk42.tight.mask_of(vc)
                sup = 0
                for x in (0,) + vc:
                    sup |= TU[x]
                if sup.bit_count() >= need:
                    ref.add(vm)
            self.assertEqual(got, ref, "u=%r need=%d" % (u, need))


class TestCensus(unittest.TestCase):
    def test_k3_class_counts_match_direct(self):
        """Per-class cover counts from the solve machinery equal a direct
        (a)-(d) triple loop on all normalized pairs with |U|, |V| <= 2."""
        bits = 3
        allm = 255
        d1 = 0b11
        subs = list(range(256))
        norm = [m for m in subs if m & 1 and m.bit_count() <= 2]
        direct = {}
        mach = {}
        for u in norm:
            for v in norm:
                for w in subs:
                    key = (u.bit_count(), v.bit_count(), w.bit_count())
                    ok, _ = walk42.lines42_g(u, v, w, d1, bits, allm)
                    if ok:
                        direct[key] = direct.get(key, 0) + 1
                for wsz in range(0, 9):
                    key = (u.bit_count(), v.bit_count(), wsz)
                    for w in walk42.solve_w42_g(u, v, bits, allm, d1, wsz):
                        ok, _ = walk42.lines42_g(u, v, w, d1, bits, allm)
                        if ok:
                            mach[key] = mach.get(key, 0) + 1
        self.assertEqual(direct, mach)


class TestReduction(unittest.TestCase):
    def test_direct_vs_reduced_lines(self):
        """The reduced (4,2) lines with D1 = {0, delta} agree with direct
        A + D coverage in E = F2^4 on the halved F2^3 analogue, on every
        configuration (independent routes must agree exactly)."""
        bits = 3
        n = 1 << bits
        allm = (1 << n) - 1
        pts = 1 << 4
        H = [p for p in range(pts) if not (p & 1)]
        Hp = [p for p in range(pts) if p & 1]

        def sset(X, Y):
            return {a ^ b for a in X for b in Y}

        checked = 0
        for (k, x) in [(1, 1), (1, 2), (2, 1)]:
            for a0t in combinations(H, k):
                for a1t in combinations(Hp, k):
                    for d0t in combinations(H, x):
                        for d1t in combinations(Hp, 2):
                            A = list(a0t) + list(a1t)
                            D = list(d0t) + list(d1t)
                            direct = sset(A, D) == set(range(pts)) and (
                                sset(A, A) | sset(D, D) == set(range(pts))
                            )
                            a0 = sum(1 << (p >> 1) for p in a0t)
                            a1 = sum(1 << (p >> 1) for p in a1t)
                            d0 = sum(1 << (p >> 1) for p in d0t)
                            r1 = min(p >> 1 for p in d1t)
                            r2 = max(p >> 1 for p in d1t)
                            d1m = 1 | (1 << (r1 ^ r2))
                            u = walk42.trans_g(a0, r1, bits, allm)
                            v = walk42.trans_g(a1, r1, bits, allm)
                            w = walk42.trans_g(d0, r1, bits, allm)
                            ok, _ = walk42.lines42_g(u, v, w, d1m, bits, allm)
                            self.assertEqual(ok, direct, "case k=%d x=%d" % (k, x))
                            checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)

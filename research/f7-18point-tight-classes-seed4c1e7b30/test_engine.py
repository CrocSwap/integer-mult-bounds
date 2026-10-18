"""Unit and control tests for the KB3g tight-class engine.

All exact integer arithmetic.  Run:
  python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/test_engine.py
"""

import random
import sys
import unittest
from itertools import combinations

HERE = __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0]
sys.path.insert(0, HERE)

import tight  # noqa: E402


def naive_sumset(X, Y):
    return {x ^ y for x in X for y in Y}


class TestPrimitives(unittest.TestCase):
    def test_trans_and_sumset_vs_naive(self):
        rng = random.Random(1)
        for _ in range(300):
            X = rng.sample(range(32), rng.randrange(0, 9))
            Y = rng.sample(range(32), rng.randrange(0, 9))
            a = rng.randrange(32)
            self.assertEqual(
                tight.trans(tight.mask_of(X), a),
                tight.mask_of([x ^ a for x in X]),
            )
            self.assertEqual(
                tight.sumset_mask(tight.mask_of(X), tight.mask_of(Y)),
                tight.mask_of(naive_sumset(X, Y)),
            )

    def test_delta_mask(self):
        X = [0, 1, 3]
        self.assertEqual(tight.delta_mask(tight.mask_of(X)), tight.mask_of([1, 3, 2]))


class TestL7Reduction(unittest.TestCase):
    def test_m4_class71_analogue_direct_agreement(self):
        """End-to-end chain check: the four L3 lines vs a DIRECT S+S = F2^5
        cover test on every (7,1)-analogue configuration at m=4 (positive
        direction: 512 real covers are accepted by both routes)."""
        H = [x for x in range(16) if not (x & 1)]
        Hp = [x for x in range(16) if x & 1]

        def ss(X, Y):
            return {x ^ y for x in X for y in Y}

        def se(X):
            return {x ^ y for x in X for y in X}

        def l3(a0, a1, d0, d1):
            return (
                ss(a0, d0) | ss(a1, d1) == set(H)
                and ss(a0, d1) | ss(a1, d0) == set(Hp)
                and se(a0) | se(a1) | se(d0) | se(d1) == set(H)
                and ss(a0, a1) | ss(d0, d1) == set(Hp)
            )

        def direct(a0, a1, d0, d1):
            # E = F2^4 = even coset of F2^5 via parity extension; H = bit-4
            # half of the F2^4 coords; odd coset point p = 1 in F2^5.
            def phi(w):
                return w | ((w.bit_count() & 1) << 4)

            A = {phi(a) for a in a0} | {phi(a) for a in a1}
            B = {1 ^ phi(d) for d in d0} | {1 ^ phi(d) for d in d1}
            S = A | B
            cov = naive_sumset(S, S)
            return len(cov) == 32

        agree = 0
        covers = 0
        for a0t in combinations(H, 7):
            a0 = list(a0t)
            for a1 in Hp:
                for d0 in H:
                    for d1 in Hp:
                        v_l3 = l3(a0, [a1], [d0], [d1])
                        v_dir = direct(a0, [a1], [d0], [d1])
                        self.assertEqual(v_l3, v_dir, (a0, a1, d0, d1))
                        agree += 1
                        if v_l3:
                            covers += 1
        self.assertEqual(agree, 4096)
        self.assertEqual(covers, 512)

    def test_half_translation_invariance(self):
        """Random m=5 configurations: half-translations preserve the four
        L3 lines, and the translated class formulas are invariant in the
        free parameter (d1 for (7,1), w for (8,2))."""
        rng = random.Random(42)

        def l3_masks(a0m, a1m, d0m, d1m):
            H = set(range(32))
            ok_i = (tight.sumset_mask(a0m, d0m) | tight.sumset_mask(a1m, d1m)) == tight.ALL
            ok_ii = (tight.sumset_mask(a0m, d1m) | tight.sumset_mask(a1m, d0m)) == tight.ALL
            ok_iii = (
                tight.selfsum_mask(a0m)
                | tight.selfsum_mask(a1m)
                | tight.selfsum_mask(d0m)
                | tight.selfsum_mask(d1m)
            ) == tight.ALL
            ok_iv = (tight.sumset_mask(a0m, a1m) | tight.sumset_mask(d0m, d1m)) == tight.ALL
            return ok_i and ok_ii and ok_iii and ok_iv

        for _ in range(200):
            a0m = tight.mask_of(rng.sample(range(32), 5))
            a1m = tight.mask_of(rng.sample(range(32), 5))
            d0m = tight.mask_of(rng.sample(range(32), 7))
            d1m = tight.mask_of(rng.sample(range(32), 1))
            h = rng.randrange(32)
            hp = rng.randrange(32)
            v0 = l3_masks(a0m, a1m, d0m, d1m)
            v1 = l3_masks(
                tight.trans(a0m, h),
                tight.trans(a1m, hp),
                tight.trans(d0m, h),
                tight.trans(d1m, hp),
            )
            self.assertEqual(v0, v1)

    def test_class71_free_parameter_invariance(self):
        rng = random.Random(7)
        for _ in range(100):
            a0m = tight.mask_of(rng.sample(range(32), 5))
            a1m = tight.mask_of(rng.sample(range(32), 5))
            sums = tight.sumset_mask(a0m, a1m)
            tm = tight.ALL ^ sums
            d1 = rng.randrange(32)
            d0m = tight.trans(tm, d1)
            d1m = 1 << d1
            ok_direct = l3_any(a0m, a1m, d0m, d1m)
            ok_formula = (
                (tight.sumset_mask(a0m, tm) | a1m) == tight.ALL
                and (tight.sumset_mask(a1m, tm) | a0m) == tight.ALL
                and (tight.selfsum_mask(a0m) | tight.selfsum_mask(a1m) | tight.selfsum_mask(tm))
                == tight.ALL
            )
            self.assertEqual(ok_direct, ok_formula)


def l3_any(a0m, a1m, d0m, d1m):
    ok_i = (tight.sumset_mask(a0m, d0m) | tight.sumset_mask(a1m, d1m)) == tight.ALL
    ok_ii = (tight.sumset_mask(a0m, d1m) | tight.sumset_mask(a1m, d0m)) == tight.ALL
    ok_iii = (
        tight.selfsum_mask(a0m)
        | tight.selfsum_mask(a1m)
        | tight.selfsum_mask(d0m)
        | tight.selfsum_mask(d1m)
    ) == tight.ALL
    ok_iv = (tight.sumset_mask(a0m, a1m) | tight.sumset_mask(d0m, d1m)) == tight.ALL
    return ok_i and ok_ii and ok_iii and ok_iv


class TestFourier(unittest.TestCase):
    def test_71_contradiction_numbers(self):
        fid = tight.fourier_71_identity()
        self.assertTrue(fid["m5_k5"]["contradiction"])
        self.assertEqual(fid["m5_k5"]["need"], 175)
        self.assertEqual(fid["m5_k5"]["lower_bound"], 239)
        self.assertFalse(fid["m3_k2"]["contradiction"])
        self.assertFalse(fid["m3_analogue_71"]["contradiction"])
        self.assertEqual(fid["m3_analogue_71"]["need"], 7)
        self.assertEqual(fid["m3_analogue_71"]["lower_bound"], 7)

    def test_identity_odd_sides_numbers(self):
        r117 = tight.identity_odd_sides(11, 7)
        self.assertEqual(r117["excess"], 13)
        self.assertEqual(r117["sum_rho2_min"], 17)
        self.assertFalse(r117["contradiction"])
        r99 = tight.identity_odd_sides(9, 9)
        self.assertEqual(r99["excess"], 17)
        self.assertEqual(r99["sum_rho2_min"], 19)
        self.assertFalse(r99["contradiction"])

    def test_identity_soundness_on_f24_covers(self):
        """Every odd-odd-split cover of F2^4 satisfies the sum-rho^2 bound
        (positive validation of the identity on real covers)."""
        N = 16
        full = set(range(N))
        checked = 0
        for mask in range(1, 1 << N):
            S = [x for x in range(N) if (mask >> x) & 1]
            cov = {0}
            for i in range(len(S)):
                for j in range(i):
                    cov.add(S[i] ^ S[j])
            if cov != full:
                continue
            A = [x for x in S if x.bit_count() % 2 == 0]
            B = [x for x in S if x.bit_count() % 2 == 1]
            D = [1 ^ b for b in B]
            s, t = len(A), len(D)
            if s % 2 == 0 or t % 2 == 0:
                continue
            from collections import Counter

            def ecoord(x):
                # x in the even coset of F2^4: x = (w, parity(w)), w in F2^3
                return x >> 1

            cnt = Counter()
            for a in A:
                for d in D:
                    cnt[ecoord(a) ^ ecoord(d)] += 1
            excess = s * t - 8
            rho2 = sum((v - 1) ** 2 for v in cnt.values())
            self.assertEqual(sum(v - 1 for v in cnt.values()), excess)
            rec = tight.identity_odd_sides(s, t, m=3)
            self.assertGreaterEqual(rho2, rec["sum_rho2_min"], (S, rho2, rec))
            checked += 1
        self.assertGreater(checked, 0)


class TestRhoClassification(unittest.TestCase):
    def test_walsh_constraints(self):
        rng = random.Random(3)

        def rho_hat(rho_map, v):
            return sum(c * (1 - 2 * ((s & v).bit_count() & 1)) for s, c in rho_map)

        # 2+1+1: V22 sizes are 2^{5-r}-1, never 11
        seen = set()
        for _ in range(300):
            q = rng.randrange(32)
            p1 = rng.randrange(32)
            p2 = rng.randrange(32)
            if len({q, p1, p2}) != 3:
                continue
            rho_map = [(q, 2), (p1, 1), (p2, 1)]
            v22 = [
                v
                for v in range(1, 32)
                if abs(rho_hat(rho_map, v)) == 4
            ]
            seen.add(len(v22))
        self.assertTrue(seen <= {1, 3, 7, 15, 31}, seen)

        # 3+1: rho_hat attains +-2 for p != q (obstruction witness)
        witness = False
        for _ in range(200):
            q = rng.randrange(32)
            p = rng.randrange(32)
            if p == q:
                continue
            rho_map = [(q, 3), (p, 1)]
            vals = {abs(rho_hat(rho_map, v)) for v in range(1, 32)}
            if 2 in vals:
                witness = True
                break
        self.assertTrue(witness)

        # 2+2: |V22| = 15
        q1, q2 = 3, 5
        rho_map = [(q1, 2), (q2, 2)]
        v22 = [v for v in range(1, 32) if abs(rho_hat(rho_map, v)) == 4]
        self.assertEqual(len(v22), 15)

        # 1+1+1+1 on a rank-3 affine 2-flat: |V22| = 7
        p1, p2, p3 = 1, 2, 4
        flat = [p1, p2, p3, p1 ^ p2 ^ p3]
        rho_map = [(x, 1) for x in flat]
        v22 = [v for v in range(1, 32) if abs(rho_hat(rho_map, v)) == 4]
        self.assertEqual(len(v22), 7)

        # 4 delta_p: Parseval contradiction numbers
        cls = tight.rho_classification()
        dead = {t["rho"] for t in cls["types"] if t["verdict"] == "DEAD"}
        self.assertEqual(dead, {"4*delta_p", "3+1", "2+1+1"})
        self.assertEqual(set(cls["surviving"]), {"2+2", "1+1+1+1"})


class TestSearchEnumeration(unittest.TestCase):
    def test_sidon_backtracking_m4_matches_bruteforce(self):
        ALL16 = (1 << 16) - 1

        def trans16(mask, a):
            for i in range(4):
                if (a >> i) & 1:
                    b = 1 << i
                    lo = 0
                    for p in range(16):
                        if not (p & b):
                            lo |= 1 << p
                    hi = ALL16 ^ lo
                    mask = ((mask & lo) << b) | ((mask & hi) >> b)
            return mask

        def sumset16(mx, my):
            out = 0
            x = mx
            while x:
                lsb = x & -x
                out |= trans16(my, lsb.bit_length() - 1)
                x ^= lsb
            return out

        def delta16(mx):
            return sumset16(mx, mx) & ALL16 & ~1

        def mask_of(pts):
            m = 0
            for p in pts:
                m |= 1 << p
            return m

        bf = 0
        for c0 in combinations(range(1, 16), 2):
            x = mask_of((0,) + c0)
            for c1 in combinations(range(1, 16), 2):
                y = mask_of((0,) + c1)
                if sumset16(x, y).bit_count() == 9:
                    bf += 1
        bt = 0
        for c1 in combinations(range(1, 16), 2):
            a1m = 1 | mask_of(c1)
            forb = delta16(a1m)
            cand = [v for v in range(1, 16) if not (forb >> v) & 1]
            chosen = [0, 0, 0]

            def rec(depth, start):
                nonlocal bt
                if depth == 3:
                    bt += 1
                    return
                for i in range(start, len(cand)):
                    v = cand[i]
                    if v <= chosen[depth - 1]:
                        continue
                    ok = True
                    for j in range(1, depth):
                        if (forb >> (v ^ chosen[j])) & 1:
                            ok = False
                            break
                    if ok:
                        chosen[depth] = v
                        rec(depth + 1, i + 1)

            rec(1, 0)
        self.assertEqual(bf, 5040)
        self.assertEqual(bt, bf)

    def test_class71_pairs_empty(self):
        pairs = tight.class71_pairs()
        self.assertEqual(len(pairs), 0)

    def test_transversals6_positive_control_m3(self):
        """The walk machinery must FIND transversals when they exist: at m=3,
        pairs X (4-set), D (2-set) with X + D = F2^3 exist; the same
        branch-on-uncovered transversal search over the D-family recovers
        them (adapted small-dimension copy)."""
        N = 8
        found_pairs = []
        for xc in combinations(range(N), 4):
            xm = tight_mask(xc)
            for dc in combinations(range(N), 2):
                dmm = tight_mask(dc)
                if tight_sumset3(xm, dmm) == (1 << N) - 1:
                    found_pairs.append((xc, dc))
        self.assertGreater(len(found_pairs), 0)
        # transversal search (same branch-on-uncovered logic) on one such D
        xc, dc = found_pairs[0]
        dmm = tight_mask(dc)
        cov_by = [0] * N
        for v in range(N):
            m = 0
            for x in range(N):
                if (dmm >> (x ^ v)) & 1:
                    m |= 1 << x
            cov_by[v] = m
        out = set()
        cur = []

        def rec(uncov, vlo):
            if len(cur) == 4:
                if not uncov:
                    out.add(frozenset(cur))
                return
            if uncov.bit_count() > 2 * (4 - len(cur)):
                return
            if not uncov:
                for v in range(vlo, N):
                    if v in cur:
                        continue
                    cur.append(v)
                    rec(uncov, v + 1)
                    cur.pop()
                return
            i = (uncov & -uncov).bit_length() - 1
            target = 0
            for x in range(N):
                if (dmm >> (x ^ i)) & 1:
                    target |= 1 << x
            for v in range(N):
                if not (target >> v) & 1:
                    continue
                if v in cur:
                    continue
                cur.append(v)
                rec(uncov & ~cov_by[v], 0)
                cur.pop()

        rec((1 << N) - 1, 0)
        self.assertIn(frozenset(xc), out)

    def test_no_full_sumset_33_pair_f2_3(self):
        """Cross-check of the (6,0) phenomenon in miniature: no pair of
        3-sets X, D in F2^3 has X + D = F2^3 (all 3136 pairs scanned)."""
        N = 8
        full = (1 << N) - 1
        cnt = 0
        for xc in combinations(range(N), 3):
            xm = tight_mask(xc)
            for dc in combinations(range(N), 3):
                if tight_sumset3(xm, tight_mask(dc)) == full:
                    cnt += 1
        self.assertEqual(cnt, 0)


def tight_mask(pts):
    m = 0
    for p in pts:
        m |= 1 << p
    return m


def tight_sumset3(mx, my):
    out = 0
    x = mx
    while x:
        lsb = x & -x
        a = lsb.bit_length() - 1
        y = my
        while y:
            lsb2 = y & -y
            out |= 1 << (a ^ (lsb2.bit_length() - 1))
            y ^= lsb2
        x ^= lsb
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)

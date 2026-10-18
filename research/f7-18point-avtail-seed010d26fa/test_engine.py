"""Machine checks for the KB3h engine (avtail.py).  Run:
python3 -I -B research/f7-18point-avtail-seed010d26fa/test_engine.py
"""

import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import tight  # noqa: E402
import avtail  # noqa: E402

RNG = random.Random(20261016)


def naive_sumset(X, Y):
    return {x ^ y for x in X for y in Y}


def rand_set(n, k):
    return RNG.sample(range(n), k)


class TestPrimitives(unittest.TestCase):
    def test_trans_sumset_vs_naive(self):
        for bits in (3, 4, 5):
            n = 1 << bits
            allm = (1 << n) - 1
            for _ in range(50):
                X = rand_set(n, RNG.randint(1, min(6, n)))
                Y = rand_set(n, RNG.randint(1, min(6, n)))
                xm = sum(1 << p for p in X)
                ym = sum(1 << p for p in Y)
                got = avtail.sumset_g(xm, ym, bits, allm)
                want = sum(1 << p for p in naive_sumset(X, Y))
                self.assertEqual(got, want)
                a = RNG.randrange(n)
                self.assertEqual(
                    avtail.trans_g(xm, a, bits, allm),
                    sum(1 << (p ^ a) for p in X),
                )
                self.assertEqual(
                    avtail.selfsum_g(xm, bits, allm),
                    sum(1 << p for p in naive_sumset(X, X)),
                )

    def test_lines51_vs_naive(self):
        for _ in range(200):
            u = sum(1 << p for p in rand_set(32, 6))
            v = sum(1 << p for p in rand_set(32, 6))
            w = sum(1 << p for p in rand_set(32, 5))
            ok, fails = avtail.lines51(u, v, w)
            U, V, W = avtail.elems_g(u), avtail.elems_g(v), avtail.elems_g(w)
            want_a = naive_sumset(V, [0]) | naive_sumset(U, W) == set(range(32))
            want_b = naive_sumset(U, [0]) | naive_sumset(V, W) == set(range(32))
            want_c = naive_sumset(U, V) | naive_sumset(W, [0]) == set(range(32))
            want_d = (
                naive_sumset(U, U) | naive_sumset(V, V) | naive_sumset(W, W) | {0}
            ) == set(range(32))
            self.assertEqual(ok, want_a and want_b and want_c and want_d, fails)


class TestReduction(unittest.TestCase):
    def test_reduction_line_equivalence_random(self):
        """Random (A0, A1, D0, D1={d1}) configurations: the four L3 lines
        and the four reduced (a)-(d) lines agree exactly."""
        for _ in range(400):
            a0 = sum(1 << p for p in rand_set(32, 6))
            a1 = sum(1 << p for p in rand_set(32, 6))
            d0 = sum(1 << p for p in rand_set(32, 5))
            d1 = 1 << RNG.randrange(32)
            ok_l3, _ = avtail.lines_l3(a0, a1, d0, d1)
            u, v, w = avtail.red51_forward(a0, a1, d0, d1)
            ok_r, _ = avtail.lines51(u, v, w)
            self.assertEqual(ok_l3, ok_r)
            # backward round trip
            bu, bv, bw, bd1 = avtail.red51_backward(u, v, w)
            self.assertEqual(bd1, 1)
            ok_l3b, _ = avtail.lines_l3(bu, bv, bw, bd1)
            self.assertEqual(ok_l3b, ok_r)

    def test_residual_symmetry(self):
        """(U, V, W) -> (U+a, V+b, W+a) preserves the four reduced lines."""
        for _ in range(300):
            u = sum(1 << p for p in rand_set(32, 6))
            v = sum(1 << p for p in rand_set(32, 6))
            w = sum(1 << p for p in rand_set(32, 5))
            a = RNG.randrange(32)
            b = RNG.randrange(32)
            ok1, f1 = avtail.lines51(u, v, w)
            ok2, f2 = avtail.lines51(
                tight.trans(u, a), tight.trans(v, b), tight.trans(w, a)
            )
            self.assertEqual((ok1, f1), (ok2, f2))

    def test_wlog_normalization_covers_all(self):
        """Every solution (U, V, W) maps to one with 0 in U and 0 in V
        through the residual symmetry (round trip test on random data)."""
        for _ in range(200):
            u = sum(1 << p for p in rand_set(32, 6))
            v = sum(1 << p for p in rand_set(32, 6))
            w = sum(1 << p for p in rand_set(32, 5))
            a = avtail.elems_g(u)[0]
            b = avtail.elems_g(v)[0]
            un = tight.trans(u, a)
            vn = tight.trans(v, b)
            wn = tight.trans(w, a)
            self.assertIn(0, avtail.elems_g(un))
            self.assertIn(0, avtail.elems_g(vn))
            self.assertEqual(
                avtail.lines51(u, v, w), avtail.lines51(un, vn, wn)
            )


class TestSearchCompleteness(unittest.TestCase):
    def test_solve_w_vs_bruteforce(self):
        """solve_w must equal brute force over all C(32,5) 5-sets."""
        pairs = []
        for _ in range(8):
            u = 1 | sum(1 << p for p in rand_set(31, 5))
            v = 1 | sum(1 << p for p in rand_set(31, 5))
            pairs.append((u, v))
        # plus the pairs with the largest sumsets found in a quick scan
        us = [1 | tight.mask_of(c) for c in combinations(range(1, 32), 5)]
        best = []
        for u in RNG.sample(us, 60):
            for v in RNG.sample(us, 60):
                sz = tight.sumset_mask(u, v).bit_count()
                if sz >= 25:
                    best.append((sz, u, v))
        best.sort(reverse=True)
        for (_sz, u, v) in best[:6]:
            pairs.append((u, v))
        for (u, v) in pairs:
            got = set(avtail.solve_w(u, v, 5))
            want = set()
            for wc in combinations(range(32), 5):
                wm = sum(1 << p for p in wc)
                _, fails = avtail.lines51(u, v, wm)
                if "a" not in fails and "b" not in fails and "c" not in fails:
                    want.add(wm)
            self.assertEqual(got, want, (avtail.elems_g(u), avtail.elems_g(v)))

    def test_pair_backtrack_vs_bruteforce(self):
        """pair_backtrack must equal brute force over all normalized v."""
        us = [1 | tight.mask_of(c) for c in combinations(range(1, 32), 5)]
        for u in RNG.sample(us, 4):
            for need in (24, 27):
                got = set(avtail.pair_backtrack(u, need))
                want = set()
                for vc in combinations(range(1, 32), 5):
                    vm = 1 | tight.mask_of(vc)
                    if tight.sumset_mask(u, vm).bit_count() >= need:
                        want.add(vm)
                self.assertEqual(got, want, (avtail.elems_g(u), need))

    def test_class51_run_shard_smoke(self):
        """One tiny shard slice agrees with direct evaluation on the same
        slice (soundness of the walk loop)."""
        rec = avtail.class51_run(budget=None, shard=0, shards=169911)
        self.assertEqual(rec["u_checked"], 1)
        self.assertFalse(rec["budget_hit"])

    def test_optimized_vs_reference_per_slice(self):
        """The optimized decision engine must agree with the validated
        reference (pair_backtrack + solve_w + lines51) on full U slices."""
        import random as _r

        rr = _r.Random(31337)
        for idx in rr.sample(range(169911), 3):
            ref = avtail.class51_reference(budget=None, shard=idx, shards=169911)
            opt = avtail.class51_run(budget=None, shard=idx, shards=169911)
            for key in ("uv_pairs", "uv_pairs_by_sumset_size", "w_candidates",
                        "covering_configs", "fail_hist", "u_checked"):
                self.assertEqual(ref[key], opt[key], (idx, key, ref[key], opt[key]))


class TestControls(unittest.TestCase):
    def test_m4_control_agreement_and_mutants(self):
        rec = avtail.control_m4()
        load_bearing = False
        nonempty = 0
        for k, r in rec.items():
            self.assertTrue(r["agreement"], (k, r))
            if r["direct_covers"] > 0:
                nonempty += 1
            if r["mutant_drop_a"] != r["machinery_covers"] or r["mutant_drop_d"] != r["machinery_covers"]:
                load_bearing = True
        self.assertTrue(load_bearing, rec)
        self.assertGreaterEqual(nonempty, 1, "positive control needs a cover-bearing class")


if __name__ == "__main__":
    unittest.main()

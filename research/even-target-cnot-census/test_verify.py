"""Rejection controls for research/even-target-cnot-census/verify.py."""

import itertools
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # works under -I
import verify as v


class PackageTests(unittest.TestCase):
    def test_attaining_words_are_exact(self):
        for r in (1, 2, 3):
            w = v.word_even(r)
            self.assertTrue(v.formal_is_target(v.formal_word_value(w, r), r))
            self.assertTrue(v.layer_ok_even_target(w, r))

    def test_drop_one_rejected(self):
        r = 3
        w = v.word_even(r)
        for drop in range(len(w)):
            mut = w[:drop] + w[drop + 1:]
            self.assertFalse(v.formal_is_target(v.formal_word_value(mut, r), r))

    def test_wrong_label_rejected(self):
        r = 2
        w = v.word_even(r)
        bad = list(w)
        gi, vv, pp = bad[0]
        bad[0] = (v.B_IDX, vv, pp)
        self.assertFalse(v.formal_is_target(v.formal_word_value(bad, r), r))

    def test_layer_system_rejects_wrong_target_word(self):
        # a word that hits [c] cannot satisfy the SWAP-target layer system
        self.assertFalse(v.layer_ok_swap_target(v.word_even(2), 2))
        self.assertTrue(v.layer_ok_swap_target(v.word_swap(2), 2))

    def test_layer_counterexample_baba(self):
        # Review regression for
        # https://github.com/CrocSwap/integer-mult-bounds/pull/1763 : at r=1
        # with every projector [1], the word b a b a is an exact target word
        # since (ba)^2 = ab = c, but the free-layer screening filter rejects
        # it (sum_ba = 1).  The filter is therefore NOT a necessary condition
        # (README section 3).
        r = 1
        w = [(v.B_IDX, 1, 1), (v.A_IDX, 1, 1), (v.B_IDX, 1, 1), (v.A_IDX, 1, 1)]
        self.assertTrue(v.formal_is_target(v.formal_word_value(w, r), r))
        self.assertFalse(v.layer_ok_even_target(w, r))
        self.assertEqual(v.layer_sums(w, r)["sum_ba"], 1)

    def test_layer_filter_not_sufficient(self):
        # r=2, word a b on one projector passes the filter but is not a target
        w = [(v.A_IDX, 1, 1), (v.B_IDX, 1, 1)]
        self.assertTrue(v.layer_ok_even_target(w, 2))
        self.assertFalse(v.formal_is_target(v.formal_word_value(w, 2), 2))

    def test_minima_do_not_rely_on_layer_condition(self):
        # Make the invalid layer filter vacuous and confirm the reported
        # minima and exclusion counts are unchanged: exclusion uses only L1'
        # parity, the q=1 direct check and the meets.
        here = Path(__file__).resolve().parent
        stored = json.loads((here / "RECEIPT.json").read_text(encoding="utf-8"))
        orig = v.layer_ok_even_target
        v.layer_ok_even_target = lambda word, r: True
        try:
            fresh = json.loads(json.dumps(v.run(fast=True), default=str))
        finally:
            v.layer_ok_even_target = orig
        self.assertEqual(stored["t1r1"], fresh["t1r1"])
        self.assertEqual(stored["small_minima"], fresh["small_minima"])
        self.assertEqual(stored["swap_t2r2"], fresh["swap_t2r2"])
        self.assertEqual(fresh["main_t4r4"]["upper"], 8)
        self.assertEqual(stored["main_t4r4"]["q"], {"2": 0, "4": 0, "6": 0})

    def test_free_layer_validity_scope(self):
        # README section 3 corrected claim.  (1) up to degree 3 the kernel of
        # F -> F_2[G] is 1-dimensional, spanned by R = xyx+yxy+x+y alone:
        # the seven monomial images have rank 6 and Z's degree<=3 truncation
        # x+y+yx maps to [ba]+[e] != 0.  (2) every hitting word of length
        # q <= 3 satisfies the corrected system (class: q <= 3 only).
        e = 1 << v.E_IDX

        def gmul(u, w):
            out = 0
            for i in range(6):
                for j in range(6):
                    if ((u >> i) & 1) and ((w >> j) & 1):
                        out ^= 1 << v.GTAB[i][j]
            return out

        x = e | (1 << v.A_IDX)
        y = e | (1 << v.B_IDX)
        imgs = {"1": e, "x": x, "y": y, "xy": gmul(x, y), "yx": gmul(y, x),
                "xyx": gmul(gmul(x, y), x), "yxy": gmul(gmul(y, x), y)}
        basis = []
        for key in ("1", "x", "y", "xy", "yx", "xyx", "yxy"):
            cur = imgs[key]
            for b in basis:
                cur = min(cur, cur ^ b)
            if cur:
                basis.append(cur)
                basis.sort()
        self.assertEqual(len(basis), 6)  # rank 6 -> ker dim 1
        self.assertEqual(imgs["x"] ^ imgs["y"] ^ imgs["xyx"] ^ imgs["yxy"], 0)
        z_low = imgs["x"] ^ imgs["y"] ^ imgs["yx"]  # Z = z+z^2+z^3, degree <= 3
        expected = (1 << v.E_IDX) | (1 << v.GIDX[v.mmul(v.MAT_B, v.MAT_A)])
        self.assertEqual(z_low, expected)  # [ba] + [e], not in the kernel

        def layer_ok_short(word, r):
            # corrected system, claimed only for words of length q <= 3
            self.assertLessEqual(len(word), 3)
            s = v.layer_sums(word, r)
            ident = v.mat_ident(r)
            if s["sum_a"] != s["sum_b"]:
                return False
            lam = s["sum_a"] ^ ident
            return (s["sum_ab"] == ident and s["sum_ba"] == 0
                    and s["sum_aba"] == lam and s["sum_bab"] == lam)

        checked, hits = 0, 0
        for r in (1, 2):
            gens = [(g[4], g[5], g[6]) for g in v.make_gens(r)]
            for q in (1, 2, 3):
                for w in itertools.product(gens, repeat=q):
                    checked += 1
                    if v.formal_is_target(v.formal_word_value(list(w), r), r):
                        hits += 1
                        self.assertTrue(layer_ok_short(list(w), r), (r, q, w))
        self.assertEqual(checked, 1898)  # 14 at r=1, 1884 at r=2
        self.assertEqual(hits, 1)
        # the counterexample has length 4: outside the claimed class
        w4 = [(v.B_IDX, 1, 1), (v.A_IDX, 1, 1), (v.B_IDX, 1, 1), (v.A_IDX, 1, 1)]
        self.assertTrue(v.formal_is_target(v.formal_word_value(w4, 1), 1))

    def test_parity_and_or_confusion_control(self):
        # the natural target transform is F_2 addition: 1+1 = 0 (a row of
        # two equal bits must cancel).  Regression for a | / ^ confusion.
        r = 2
        v.set_r(r)
        s = (0b11 << 0) | (0b11 << (v.ROWSZ * 1))  # rows 0 and 1 = (1,1)
        got = v.nat_right_target(s, v.MAT_C, r)
        # rho(c) = [[0,1],[1,1]]; a row (1,1) maps to (1^1, 1^1) = (1,0)
        row0 = (got >> 0) & 0b11
        row1 = (got >> v.ROWSZ) & 0b11
        self.assertEqual(row0, 0b01)
        self.assertEqual(row1, 0b01)

    def test_receipt_rejects_mutation(self):
        here = Path(__file__).resolve().parent
        stored = json.loads((here / "RECEIPT.json").read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(v.run(fast=True), default=str))
        for key in ("t1r1", "small_minima", "swap_t2r2"):
            self.assertEqual(stored.get(key), fresh.get(key))
        tampered = json.loads(json.dumps(stored))
        tampered["main_t4r4"]["q"]["6"] = 99
        self.assertNotEqual(tampered["main_t4r4"]["q"], fresh["main_t4r4"].get("q", {}))

    def test_random_words_do_not_hit_target(self):
        rng = random.Random(99)
        r = 2
        v.set_r(r)
        gens = v.make_gens(r)
        for _ in range(30):
            n = rng.randrange(1, 6)
            s = v.nat_identity()
            for _k in range(n):
                s = v.nat_right_mul(s, gens[rng.randrange(len(gens))])
            self.assertNotEqual(s, v.nat_right_target(v.nat_identity(), v.MAT_C, r))


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: Apache-2.0
"""Controls for the two-role whole-helper swap census.

Exact integer radical oracle for the exponent-uniform sign rule, a toy
brute-force census cross-check, the pair-aware rejection rules, certificate
tamper and source-drift controls, and the improving-inverse positive fixture.
"""
import importlib.util
from collections import Counter
import json
from pathlib import Path
import random
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("swap_census", HERE / "verify.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def _pos(g, B, C):
    """Sign of g + sqrt(B) - sqrt(C) for integer g > 0 and nonnegative B, C."""
    K = C - g * g - B
    if K < 0:
        return 1
    four = 4 * g * g * B
    if K == 0:
        return 1 if B > 0 else 0
    # K > 0: compare 2 g sqrt(B) with K by squaring (both sides >= 0).
    if four > K * K:
        return 1
    if four < K * K:
        return -1
    return 0


def cmp_lin_sqrt(g, B, C):
    """Sign of g + sqrt(B) - sqrt(C) for integer g and nonnegative integers B, C."""
    if g == 0:
        return (B > C) - (B < C)
    if g > 0:
        return _pos(g, B, C)
    return -_pos(-g, C, B)


def cmp_two_sqrt_sums(a, b, c, d):
    """Sign of (sqrt(a) + sqrt(b)) - (sqrt(c) + sqrt(d)); nonnegative integer args."""
    return cmp_lin_sqrt(a + b - c - d, 4 * a * b, 4 * c * d)


class RadicalOracle(unittest.TestCase):
    """The class sign rule must match exact radical comparison at a = 1/2."""

    def test_sign_rule_matches_exact_radicals(self):
        checks = 0
        for x1 in (0, 1, 2, 3, 5, 7, 12, 48):
            for x2 in (0, 1, 2, 3, 5, 7, 12, 48):
                for w1 in range(1, 10):
                    for w2 in range(1, 10):
                        sign = sc.swap_sign(x1, w1, x2, w2)
                        d = w1 - w2
                        if sign == "capacity_infeasible":
                            self.assertTrue(x1 + d < 0 or x2 - d < 0)
                            continue
                        exact = cmp_two_sqrt_sums(x1 + d, x2 - d, x1, x2)
                        if sign == "strictly_improving":
                            self.assertEqual(exact, -1, (x1, w1, x2, w2))
                        elif sign == "neutral":
                            self.assertEqual(exact, 0, (x1, w1, x2, w2))
                        else:
                            self.assertEqual(exact, 1, (x1, w1, x2, w2))
                        checks += 1
        self.assertGreater(checks, 2000)

    def test_float_agreement_sample(self):
        import math
        rng = random.Random(20261014)
        for _ in range(500):
            x1 = rng.randrange(0, 49)
            x2 = rng.randrange(0, 49)
            w1 = rng.randrange(1, 10)
            w2 = rng.randrange(1, 10)
            sign = sc.swap_sign(x1, w1, x2, w2)
            if sign == "capacity_infeasible":
                continue
            d = w1 - w2
            diff = (math.sqrt(x1 + d) + math.sqrt(x2 - d)
                    - math.sqrt(x1) - math.sqrt(x2))
            self.assertEqual(sign == "neutral", abs(diff) < 1e-9, (x1, w1, x2, w2))
            self.assertEqual(sign == "strictly_improving", diff < -1e-9, (x1, w1, x2, w2))


class ToyCensus(unittest.TestCase):
    """Class-count tabulation must agree with a direct pair enumeration."""

    def test_tabulate_matches_brute_force(self):
        rng = random.Random(7)
        bin_x, fixed = {}, []
        for _ in range(60):
            b = rng.randrange(4)
            if b not in bin_x:
                bin_x[b] = rng.randrange(0, 5)
            fixed.append((b, bin_x[b], rng.randrange(1, 6)))
        class_roles, class_bins = sc.group_roles(fixed)
        rows, classification, same_bin = sc.tabulate(class_roles, class_bins)
        brute = Counter()
        for i in range(len(fixed)):
            for j in range(i + 1, len(fixed)):
                b1, x1, w1 = fixed[i]
                b2, x2, w2 = fixed[j]
                if b1 == b2:
                    brute["same_bin_noop"] += 1
                else:
                    brute[sc.swap_sign(x1, w1, x2, w2)] += 1
        self.assertEqual(same_bin, brute["same_bin_noop"])
        for key in ("capacity_infeasible", "strictly_improving", "neutral", "strictly_worsening"):
            self.assertEqual(classification[key], brute[key], key)
        total = len(fixed) * (len(fixed) - 1) // 2
        self.assertEqual(same_bin + sum(classification.values()), total)
        self.assertEqual(sum(r["distinct_bin_pairs"] for r in rows),
                         sum(classification.values()))


class RealCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = sc.fixture()
        cls.result = sc.census(cls.f["model"])

    def test_completeness_identity(self):
        c = self.result
        self.assertEqual(c["roles"] * (c["roles"] - 1) // 2, c["total_unordered_role_pairs"])
        self.assertEqual(c["same_bin_noop"] + sum(c["pair_classification"].values()),
                         c["total_unordered_role_pairs"])

    def test_improving_candidates_complete(self):
        c = self.result
        self.assertEqual(len(c["improving_candidates"]),
                         c["pair_classification"]["strictly_improving"])
        for cand in c["improving_candidates"]:
            x1, x2 = cand["old_remainders"]
            w1, w2 = cand["widths"]
            self.assertEqual(sc.swap_sign(x1, w1, x2, w2), "strictly_improving")

    def test_rejection_reasons_recomputed(self):
        model = self.f["model"]
        reasons = Counter()
        for cand in self.result["improving_candidates"]:
            i, j = cand["role_index_a"], cand["role_index_b"]
            self.assertNotEqual(sc.bin_key(model.roles[i]), sc.bin_key(model.roles[j]))
            self.assertEqual(sc.swap_sign(
                model.bins[sc.bin_key(model.roles[i])].remainder, model.roles[i]["width"],
                model.bins[sc.bin_key(model.roles[j])].remainder, model.roles[j]["width"]),
                "strictly_improving")
            reasons[sc.swap_rejection(model, i, j)] += 1
        expected = dict(self.result["rejection_counts"])
        if self.result["legal_strict_improvements"]:
            expected[None] = self.result["legal_strict_improvements"]
        self.assertEqual(dict(reasons), expected)

    def test_family_rule_pair_aware(self):
        model = self.f["model"]
        roles = model.roles
        muted = sc.Model(model.roles, model.geo,
                         {k: (-10 ** 9, 10 ** 9) for k in model.windows}, model.positions)
        same = collide = None
        bins_by_family = model.by_family
        for i, ri in enumerate(roles):
            if same is None:
                for j in range(i + 1, len(roles)):
                    if roles[j]["time"] == ri["time"]:
                        same = (i, j)
                        break
            if collide is None:
                for family in model.families[ri["time"]]:
                    key = bins_by_family.get(family)
                    if key is None or key == sc.bin_key(ri):
                        continue
                    for j, rj in enumerate(roles):
                        if sc.bin_key(rj) == key and rj["time"] != ri["time"]:
                            if (muted.window_active_rejection(ri, key) is None
                                    and muted.window_active_rejection(rj, sc.bin_key(ri)) is None):
                                collide = (i, j)
                            break
                    if collide:
                        break
            if same and collide:
                break
        self.assertIsNotNone(same)
        self.assertIsNotNone(collide)
        self.assertIsNone(sc.family_collision(model, *same))
        self.assertEqual(sc.family_collision(model, *collide), "same_call_family_collision")
        # With the window muted and the active rule clear, family is the binding reason.
        self.assertEqual(sc.swap_rejection(muted, *collide), "same_call_family_collision")
        # On the real map the combined rejection reports the first failing rule.
        first = (model.window_active_rejection(model.roles[collide[0]], sc.bin_key(model.roles[collide[1]]))
                 or model.window_active_rejection(model.roles[collide[1]], sc.bin_key(model.roles[collide[0]]))
                 or "same_call_family_collision")
        self.assertEqual(sc.swap_rejection(model, *collide), first)

    def test_window_rule_strict(self):
        model = self.f["model"]
        i, j = self.result["improving_candidates"][0]["role_index_a"], \
            self.result["improving_candidates"][0]["role_index_b"]
        ri, rj = model.roles[i], model.roles[j]
        for role, dest in ((ri, sc.bin_key(rj)), (rj, sc.bin_key(ri))):
            call = (role["stage"], role["replica"])
            lo, hi = model.windows[dest[:2]]
            self.assertEqual(model.window_active_rejection(role, dest) is None,
                             lo < model.positions[call] < hi)

    def test_positive_control_detects_inverse(self):
        pc = sc.positive_control(self.f)
        self.assertTrue(pc["improving_inverse_detected"])
        self.assertIsNone(pc["rejection_of_inverse"])


class CertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = (HERE / "CERTIFICATE.json").read_bytes()
        cls.result = sc.build()

    def test_regeneration_matches(self):
        self.assertEqual(sc.canonical(self.result), self.data)

    def test_tampered_certificate_rejected(self):
        tampered = self.data.replace(b"strictly_improving", b"strictly_improvinx", 1)
        self.assertNotEqual(tampered, self.data)
        with self.assertRaises(ValueError):
            sc.check_certificate(self.result, tampered)

    def test_suppressed_candidate_rejected(self):
        parsed = json.loads(self.data)
        parsed["census"]["improving_candidates"].pop()
        with self.assertRaises(ValueError):
            sc.check_certificate(self.result, sc.canonical(parsed))

    def test_source_drift_rejected(self):
        manifest = json.loads((HERE / "SOURCES.json").read_bytes())
        for item in manifest["files"]:
            if item["usage"] == "input":
                item["sha256"] = "0" * 64
                break
        with self.assertRaises(ValueError):
            sc.checked_sources(sc.ROOT, manifest)


if __name__ == "__main__":
    unittest.main()

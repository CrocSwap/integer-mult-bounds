"""Feasibility boundaries and fixed-exponent optimization, using exact arithmetic."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from tune_paired_parameters import (A, S, KAPPA, parameters, evaluate,
    capacity_polynomial, capacity_enclosure, supremum_enclosure, guard_checks,
    sufficient_role_budget, design_target, certificate)
from make_tuned_paired_patch import patched_files


class TunedPairedParameters(unittest.TestCase):
    def test_new_witness_exceeds_prior_supported_margin(self):
        new = evaluate(parameters())
        old = evaluate(parameters(beta=Q(999, 1000), epsilon=Q(199, 1000),
                                  delta=Q(1, 10000), kappa=Q(1, 2**59)))
        self.assertGreater(KAPPA, Q(old["minimum_margin"]))
        self.assertGreater(Q(new["minimum_margin"]), KAPPA)
        self.assertEqual(Q(new["minimum_margin"]), Q("1.7523184646864326407676563456e-18"))

    def test_margins_require_exact_arithmetic(self):
        p = parameters()
        self.assertEqual(float(p.lam), 1.0)
        self.assertLess(p.lam, p.lamp)
        self.assertLess(p.lamp, 1)
        self.assertGreater(p.lamp-(p.sigma+p.beta*(1-p.sigma)), 0)

    def test_old_delta_is_incompatible_with_new_dimension(self):
        with self.assertRaisesRegex(ValueError, "gaussian_cost"):
            evaluate(replace(parameters(), delta=Q(1, 10000)))

    def test_stopping_exponent_cannot_approach_one_arbitrarily(self):
        with self.assertRaisesRegex(ValueError, "leaf_cost"):
            evaluate(parameters(beta=1-Q(1, 10**10)))

    def test_old_guard_power_cannot_support_new_dimension(self):
        with self.assertRaisesRegex(ValueError, "guard_width"):
            evaluate(replace(parameters(), C1=20))

    def test_absorption_requires_strict_gap(self):
        p = parameters()
        minimum = Q(evaluate(p)["minimum_margin"])
        with self.assertRaisesRegex(ValueError, "absorption gap"):
            evaluate(replace(p, kappa=minimum))

    def test_stopped_guard_range_and_constants(self):
        for beta in (Q(9, 10), parameters().beta):
            checked = guard_checks(beta)
            self.assertLess(Q(checked["depth_with_piece_count_exponent"]), 2)
        with self.assertRaisesRegex(ValueError, "guard exponent"):
            guard_checks(Q(8, 10))

    def test_bisection_encloses_root_with_certified_signs(self):
        lo, hi = capacity_enclosure()
        self.assertGreaterEqual(capacity_polynomial(lo), 0)
        self.assertLessEqual(capacity_polynomial(hi), 0)
        self.assertEqual(hi-lo, A*A/2**160)
        self.assertLess(2*A*hi, S+A*A)

    def test_capacity_crossing_brackets_both_competing_bounds(self):
        lo, hi = capacity_enclosure()
        def packed(beta):
            return beta*A*A/(1-A+A*beta)
        beta_lo, beta_hi = 1-hi/S, 1-lo/S
        self.assertGreaterEqual(beta_lo, Q(9, 10))
        self.assertLess(packed(beta_lo), (1-beta_lo)*S)
        self.assertGreater(packed(beta_hi), (1-beta_hi)*S)

    def test_feasible_rational_family_approaches_supremum(self):
        lo, hi = capacity_enclosure()
        beta = 1-(lo+hi)/(2*S)
        limits = []
        for bits in (20, 40, 80):
            z = lo*(1-Q(1, 2**bits))
            delta = Q(1, 2**bits)
            c = z/A
            lamp = 1-z
            lam = (max(1-A, 1-S, (1-A)*(1+c/beta))+lamp)/2
            epsilon = (Q(1, 4)-delta)/(Q(5, 4)+z)
            p = parameters(beta=beta, epsilon=epsilon, delta=delta, kappa=epsilon*z/2)
            p = replace(p, c=c, lam=lam, lamp=lamp)
            checked = evaluate(p)
            limits.append(Q(checked["minimum_margin"]))
        glo, ghi = supremum_enclosure()
        self.assertLess(limits[0], limits[1])
        self.assertLess(limits[1], limits[2])
        self.assertLess(limits[2], ghi)
        self.assertGreater(limits[2]/glo, 1-Q(1, 10**20))

    def test_scoped_supremum_is_below_next_dyadic_target(self):
        lo, hi = supremum_enclosure()
        self.assertGreater(lo, KAPPA)
        self.assertLess(hi, Q(1, 2**58))
        self.assertGreater(KAPPA/hi, Q(99999996, 10**8))

    def test_supremum_balance_has_dimension_strictly_below_one_fifth(self):
        for z in capacity_enclosure():
            epsilon = 1/(5+4*z)
            self.assertLess(epsilon, Q(1, 5))
            self.assertEqual(epsilon*z, Q(1, 4)-Q(5, 4)*epsilon)
            self.assertGreater(A*(1-epsilon), 4*A/5)
            self.assertGreater(A*(1-epsilon), epsilon*z)
            self.assertGreater(Q(1, 3)-epsilon, Q(2, 15))

    def test_cost_factors_independently_imply_the_reported_margins(self):
        # Exponents of d, K, ell and alpha from eq:sizes and the tighter width.
        p = parameters()
        d, K, ell, alpha = p.epsilon, p.epsilon*p.c, 1-p.epsilon, (1+p.epsilon)/4
        powers = {"g1": d+K,                         # d*K
                  "g2": 1+(p.tau-1)*K,              # p*K^(tau-1)
                  "g3": ell+p.lamp*d,               # ell*d^(lambda-prime)
                  "g4": d+p.tau*ell,                # d*ell^tau dominates d
                  "g5": d+Q(1, 2)+p.delta+alpha,     # d*p^(1/2+delta)*alpha
                  "g6": d+p.delta,                  # d*p^delta
                  "g7": ell}                        # log(r*p)
        margins = evaluate(p)["margins"]
        self.assertEqual({k: 1-v for k, v in powers.items()},
                         {k: Q(v) for k, v in margins.items()})
        self.assertTrue(all(power < 1-p.kappa for power in powers.values()))

    def test_role_budget_is_strict_and_target_is_unachieved(self):
        from math import comb
        from tune_paired_parameters import LOG_BOUND
        v, h = comb(50, 3), 50
        a = Q(417, 10**11)
        budget = sufficient_role_budget(a)
        def deficit(R):
            return Q(v-6*h*h, 2*h**3*(v+R+h))
        self.assertGreater(deficit(budget), a*LOG_BOUND)
        self.assertLessEqual(deficit(budget+1), a*LOG_BOUND)
        target = design_target()
        self.assertEqual(budget, 356295)
        self.assertIn("UNACHIEVED", target["status"])

    def test_standalone_certificate_does_not_claim_circuit_validation(self):
        c = certificate()
        self.assertFalse(c["integration"]["paired_circuit_rechecked"])
        self.assertGreater(Q(c["comparison"]["relative_gain_over_previous_margin"]), Q(6, 1000))
        self.assertLess(Q(c["comparison"]["relative_gain_over_previous_margin"]), Q(61, 10000))

    def test_complete_integration_and_source_hashes(self):
        c = certificate(upstream=True)
        self.assertTrue(c["integration"]["paired_circuit_rechecked"])
        self.assertTrue(c["integration"]["all_parameter_slacks_and_margins_match"])
        self.assertEqual(c["integration"]["actual_side_roles"], 509194)
        self.assertEqual(c["integration"]["upstream_commit"], "adc7f1241b42e322a6451854ab7e4b4c146bf78a")

    def test_patch_retains_all_inherited_dependencies_and_updates_parameters(self):
        files = list(patched_files())
        self.assertEqual(len(files), 7)
        for name, old, new in files:
            if name.endswith(("main.tex", "00-introduction.tex")):
                self.assertIn(r"\kappa=\frac{17523184}{10^{25}}", new)
            elif name.endswith("08-assembly.tex"):
                for literal in (r"d^{10^{13}}\le b^{1999999999999}",
                                r"e^{10^{11}}<d^{99999912384}",
                                r"g_5=1/4-\delta-5\epsilon/4", r"\rho=G-\kappa", "184<2^8"):
                    self.assertIn(literal, new)
                for obsolete in (r"b^{199/1000}", r"d^{1000}\le b^{199}", r"p^{199/500}", "2^{-59}", "1597/2000"):
                    self.assertNotIn(obsolete, new)
            elif name.endswith("03-motifs.tex"):
                self.assertIn(r"\label{prop:paired-bit-interface}", new)
            elif name.endswith("05-layers.tex"):
                self.assertIn(r"\label{sec:stopped-guard}", new)

    def test_checks_survive_python_optimization(self):
        code = "from dataclasses import replace; from fractions import Fraction as Q; from tune_paired_parameters import evaluate,parameters; evaluate(replace(parameters(),delta=Q(1,10000)))"
        result = subprocess.run([sys.executable, "-O", "-c", code], cwd=ROOT/"scripts",
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gaussian_cost", result.stderr)


if __name__ == "__main__":
    unittest.main()

"""Coefficient dependency paths, compiled frames and alternate guard witness."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from experiments import assembly_breakthrough_guard as dg
from aligned_bit_network import parameters as aligned_parameters
from complex_network import guard as historical_guard


class DependencyPaths(unittest.TestCase):
    def test_parallel_work_is_not_one_dependency_chain(self):
        audit = dg.PathAudit([0, 0])
        audit.gate("left-rise", [0], 7)
        audit.gate("right-rise", [1], 7)
        audit.gate("left-fall", [0], 3)
        audit.gate("right-fall", [1], 3)
        audit.gate("join", [0, 1], 3)
        # Chronological edge-rank total is 22, but either chain costs 11.
        self.assertEqual(audit.rank, [11, 11])
        self.assertEqual(audit.loss, [4, 4])
        self.assertLess(max(audit.rank), 2 * (7 + 4))

    def test_partial_decreasing_edge_obeys_telescoping(self):
        audit = dg.PathAudit([2])
        audit.gate("rise", [0], 7)
        # Stop after two of a planned six downward child factors.
        audit.gate("partial-decrease", [0], 5)
        self.assertEqual(audit.rank[0], 7)
        self.assertEqual(audit.rank[0], 5 - 2 + 2 * audit.loss[0])
        audit.gate("finish-decrease", [0], 1)
        self.assertEqual(audit.rank[0], 11)
        self.assertEqual(audit.rank[0], 1 - 2 + 2 * audit.loss[0])

    def test_role_switch_can_accumulate_sequential_decreases(self):
        audit = dg.PathAudit([0, 0])
        audit.gate("first-rise", [0], 6)
        audit.gate("first-fall", [0], 2)
        audit.gate("switch-role", [0, 1], 2)
        audit.gate("second-rise", [1], 7)
        audit.gate("second-fall", [1], 1)
        # Taking only the largest individual descent (6) would be wrong.
        self.assertEqual(audit.loss[1], 4 + 6)
        self.assertEqual(audit.rank[1], 1 + 2 * (4 + 6))


class CompiledFrameControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = dg.ComplexSideCircuit(8)
        cls.code = dg.compile_roles(cls.c)
        labels = dg.Checks(cls.c)
        cls.dimensions = {node: labels.label(node).dim for node in cls.c.active}

    def test_all_three_actual_stage_schedules(self):
        for stage, inverse in ((1, False), (2, True), (3, False)):
            with self.subTest(stage=stage):
                got = dg.invocation(self.c, self.code, self.dimensions, stage, inverse)
                self.assertEqual(got["decreasing_edges"], 9)
                self.assertEqual(got["maximum_path_descent"], 8)
                self.assertEqual(got["maximum_path_rank"], 8 ** 3 + 16)

    def test_wrong_middle_labels_are_detected(self):
        dimensions = dict(self.dimensions)
        node = next(node for node, _, _ in self.code["gates"] if self.c.args[node])
        # A label larger than the ambient stage forces an unaccounted descent.
        dimensions[node] = self.c.h + 1
        with self.assertRaises(AssertionError):
            dg.invocation(self.c, self.code, dimensions, 1, False)


class GuardAndWitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = dg.complex_counts(dg.ComplexSideCircuit(25))
        cls.p = replace(aligned_parameters(), beta=Q(1, 1000), C1=Q(1001099, 10 ** 6))

    def test_integer_power_and_exact_unroll_controls(self):
        controls = dg.exact_recurrence_controls()
        self.assertEqual(controls["path_branching"], 15775)
        self.assertEqual(controls["finite_recurrence_comparisons"], 81)
        self.assertLess(15775 ** 1000, 15625 ** 1001)

    def test_old_constant_is_sufficient(self):
        new = dg.dependency_guard(self.n, self.p.beta)
        old = historical_guard(self.n, self.p.beta, dg.ZETA)
        self.assertEqual(new["C0"], old["C0"])
        self.assertTrue(all(x > 0 for x in new["constant_slacks"].values()))
        self.assertLess(new["C1"], old["C1"])
        self.assertLess(1 - self.p.epsilon * old["C1"], 0)
        self.assertGreater(1 - self.p.epsilon * new["C1"], 0)

    def test_too_small_path_exponent_is_rejected(self):
        with self.assertRaises(ValueError):
            dg.dependency_guard(self.n, self.p.beta, rho=Q(10001, 10000))

    def test_alternate_baseline_has_every_strict_margin(self):
        w = dg.research_witness(self.n, self.p)
        self.assertEqual(w["parameters"]["kappa"], Q(1624, 10 ** 12))
        self.assertEqual(w["limiting_margins"], ["g3"])
        self.assertEqual(w["minimum_margin"], Q(162446751, 10 ** 17))
        self.assertEqual(w["absorption_gap"], Q(46751, 10 ** 17))
        self.assertTrue(all(value > 0 for value in w["constraint_slacks"].values()))
        self.assertEqual(w["recurrence"]["internal"], self.p.tau)

    def test_guard_mismatch_and_bad_leaf_and_no_gap_are_rejected(self):
        with self.assertRaises(ValueError):
            dg.research_witness(self.n, replace(self.p, C1=2))
        beta = Q(9, 10)
        with self.assertRaises(ValueError):
            dg.research_witness(self.n, replace(
                self.p, beta=beta, C1=beta + (1 - beta) * dg.RHO + dg.ZETA))
        with self.assertRaises(ValueError):
            dg.research_witness(self.n, replace(self.p, kappa=Q(162446751, 10 ** 17)))

    def test_research_certificate_reproduces_full_size_controls(self):
        cert = json.loads((ROOT / "certificates/assembly-breakthrough-guard.json").read_text())
        full = next(control for control in cert["invocation_controls"] if control["h"] == 25)
        self.assertEqual(full["three_stage_path_rank_upper"], 15775)
        for invocation in full["invocations"]:
            self.assertEqual(invocation["maximum_path_descent"], 25)
        saved = cert["alternate_baseline_witness"]
        self.assertEqual(Q(saved["guard"]["C1"]), self.p.C1)
        self.assertEqual(Q(saved["parameters"]["kappa"]), self.p.kappa)
        self.assertEqual(Q(saved["minimum_margin"]), Q(162446751, 10 ** 17))


if __name__ == "__main__":
    unittest.main()

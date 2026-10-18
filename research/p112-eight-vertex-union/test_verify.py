"""Behavioral controls and separately implemented finite cross-checks."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import independent
import verify
from census import PROFILE, survives
from union import cost_masks, indices, score, union_maximum
from vendor.geometry import require


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (
            cls.result,
            cls.candidates,
            cls.costs,
            cls.vertices,
            cls.adjacency,
            cls.points,
        ) = verify.receipt()

    def test_committed_receipt(self):
        verify.check_receipt(
            self.result, json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        )

    def test_independent_graph_and_mixed_census(self):
        vertices, adjacency = independent.vertices_and_graph()
        self.assertEqual(vertices, self.vertices)
        self.assertEqual(adjacency, self.adjacency)
        ranks, bounds = independent.mixed_census(vertices, adjacency, self.points)
        self.assertEqual(ranks, self.result["mixed"]["rank_histogram"])
        self.assertEqual(bounds, self.result["mixed"]["support_histogram"])

    def test_independent_union_census_includes_repeated_flats(self):
        for j, expected in ((1, 104), (2, 108), (3, 108)):
            self.assertEqual(
                independent.union_maximum(
                    self.candidates[4][j], self.candidates[5][j], self.costs
                ),
                expected,
            )

    def test_original_profile_and_losing_relaxation(self):
        self.assertTrue(survives(PROFILE, 7))
        self.assertFalse(survives((6,) * 11, 7))
        rows = self.result["all_root"]["frame_bounds"]
        self.assertEqual(
            [r["live_cost"] - r["independent_flat_sum_cap"] for r in rows],
            [172, 156, 160, 160, 164],
        )
        spectrum = self.result["all_root"]["spectra"][1]
        costs = sorted(k for k, n in spectrum.items() for _ in range(n))
        self.assertEqual(sum(costs[:80]), 158)
        self.assertEqual([r["outside_lower"] for r in rows], [172, 162, 162, 162, 164])

    def test_one_extra_cut_loses_mixed_margin(self):
        witness = self.result["mixed"]["witness"]
        self.assertEqual(witness["lower_after_33_cuts"], 159)
        self.assertEqual(independent.integer_rank(witness["vertices_doubled"]), 7)

    def test_frame_coverage(self):
        root = self.result["all_root"]
        self.assertEqual(sum(root["frame_orbit_sizes"]), root["frames"])
        self.assertEqual(root["frames"], 2025)
        self.assertEqual(root["frame_search_nodes"], 27565)

    def test_flat_capacity_and_candidate_coverage(self):
        rows = self.result["all_root"]["flat_censuses"]
        self.assertEqual(sum(r["subspaces"] for r in rows), 6_619_494)
        self.assertEqual(
            [[len(self.candidates[d][j]) for j in (1, 2, 3)] for d in (4, 5)],
            [[101, 61, 45], [150, 86, 54]],
        )

    def test_planted_disjoint_union_reaches_failure_threshold(self):
        masks = (0, (1 << 32) - 1)
        a, b, c = (1 << 8) - 1, ((1 << 12) - 1) << 8, ((1 << 12) - 1) << 20
        self.assertEqual(union_maximum({a}, {b, c}, masks)["maximum_union_score"], 128)
        self.assertEqual(score(a | b | c, masks), 128)
        self.assertGreaterEqual(
            128, self.result["all_root"]["frame_bounds"][1]["failure_threshold"]
        )

    def test_altered_receipt_rejected(self):
        changed = copy.deepcopy(self.result)
        changed["application"]["margin"] = 0
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            verify.check_receipt(changed, self.result)

    def test_changed_pinned_source_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "package"
            shutil.copytree(verify.PACKAGE, destination)
            destination.chmod(0o755)
            (destination / "vendor").chmod(0o755)
            path = destination / "vendor/mixed.py"
            path.chmod(0o644)
            path.write_bytes(path.read_bytes() + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "changed retained source"):
                verify.bind_sources(destination)

    def test_changed_live_input_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "data.txt"
            path.write_bytes(verify.read_bytes(verify.ROOT / verify.DATA) + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112 data"):
                verify.bind_data(path, (), (), verify.bind_sources())

    def test_output_is_external_and_exclusive(self):
        with self.assertRaisesRegex(ValueError, "outside checkout"):
            verify.write_result({}, verify.PACKAGE / "forbidden.json")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            verify.write_result({"ok": True}, path)
            with self.assertRaises(FileExistsError):
                verify.write_result({}, path)
            self.assertEqual(json.loads(path.read_text()), {"ok": True})

    def test_invalid_domains_and_optimization_guards(self):
        for operation, args in (
            (indices, (-1, 120)),
            (cost_masks, ((1,) * 120,)),
            (survives, ((4, 6, 5), 7)),
            (require, (False, "active guard")),
        ):
            with self.assertRaises(ValueError):
                operation(*args)

    def test_linked_input_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "link"
            path.symlink_to(verify.ROOT / verify.DATA)
            with self.assertRaisesRegex(ValueError, "linked"):
                verify.read_bytes(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)

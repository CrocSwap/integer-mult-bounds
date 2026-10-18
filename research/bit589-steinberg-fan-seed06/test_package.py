#!/usr/bin/env python3
"""Mathematical and certificate admission controls; safe under Python -O.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""

import copy
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("steinberg_verifier", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
spec = importlib.util.spec_from_file_location("steinberg_independent", HERE / "independent.py")
I = importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)


class MathematicalControls(unittest.TestCase):
    def test_both_chain_orientations_on_all_boolean_inputs(self):
        for pair in [[(0, 1, 2), (0, 0, 1)], [(0, 0, 1), (0, 1, 2)]]:
            orders = V.expansion_orders(*pair)
            self.assertEqual(len(orders), 3)
            for order in orders:
                for value in range(8):
                    self.assertEqual(I.direct_map(order, [0, 1, 2], value),
                                     I.direct_map([(t, s) for _, t, s in pair], [0, 1, 2], value))

    def test_commuting_and_two_register_pairs_are_excluded(self):
        self.assertEqual(V.expansion_orders((0, 0, 1), (0, 0, 2)), [])
        self.assertEqual(V.expansion_orders((0, 0, 1), (0, 1, 0)), [])

    def test_rootless_intersection_is_counted(self):
        # No listed line is in both planes, but the actual intersection is Q(e0-e1).
        lines = [[1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0],
                 [1, 0, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
        geometry = V.Geometry(dict(lines=lines, frames=[[0, 1], [2, 3]]))
        expected = V.rref([[1, -1, 0, 0, 0, 0, 0, 0]])
        self.assertEqual(geometry.meet((0, 1)), expected)
        self.assertEqual(I.intersection_dimension([I.integer_basis(lines[:2], 8),
                                                  I.integer_basis(lines[2:], 8)]), 1)

    def test_improvement_outside_pinned_context_is_detected(self):
        # Explicit flag 0 <= Q e0 <= Q e0 <= Q(e0,e1).
        geometry = V.Geometry(dict(lines=[[1, 0, 0, 0, 0, 0, 0, 0],
                                          [0, 1, 0, 0, 0, 0, 0, 0]],
                                   frames=[[], [0], [0, 1]]))
        gates = [(0, 1), (0, 2), (1, 2)]
        self.assertEqual(V.flag(gates, {0: 0, 1: 0, 2: 1}, {0: 1, 1: 2, 2: 2}, geometry), [0, 1, 1, 2])
        result = V.controls()["positive_fixture"]
        self.assertEqual(result["concavity_slacks"], [-1, 0, 0, 0, 0, 0, 0, 0])

    def test_all_builtin_rejection_controls(self):
        self.assertEqual(len(V.controls()["rejected"]), 8)

    def test_nonintegral_or_negative_counts_rejected(self):
        for count in [-1, True, 1.5]:
            with self.assertRaisesRegex(ValueError, "invalid histogram count"):
                V.require_dominance([count] + [0] * 7, [0] * 8)

    def test_source_drift_rejected(self):
        pins = V.load_json(HERE / "SOURCES.json")
        row = next(row for row in pins["files"] if row["path"] == V.WORD)
        data = (V.ROOT / row["path"]).read_bytes()
        V.source_bytes(data, row)
        with self.assertRaisesRegex(ValueError, "source SHA256 mismatch"):
            V.source_bytes(data + b"corruption", row)

    def test_missing_scatter_read_rejects_full_dirty_endpoint(self):
        word = V.load_json(V.ROOT / V.WORD)
        target = next(i for i, sources in enumerate(word["scatter"]) if sources)
        word["scatter"][target].pop()
        with self.assertRaisesRegex(ValueError, "whole dirty-column endpoint failed"):
            V.whole_endpoint(word, V.elementary(word, "A"))

    def test_omitted_cleanup_rejects_full_dirty_endpoint(self):
        word = V.load_json(V.ROOT / V.WORD)
        stream = V.scalar_stream(word, V.elementary(word, "A"))
        self.assertEqual(stream[-1][0], "add")
        with self.assertRaisesRegex(ValueError, "whole dirty-column endpoint failed"):
            V.check_scalar_stream(word, stream[:-1])

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"coverage":316,"coverage":315}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                V.load_json(path)


class CertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = V.load_json(HERE / "CERTIFICATE.json.gz")

    def run_independent(self, certificate):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json.gz"
            path.write_bytes(gzip.compress(V.canonical(certificate), mtime=1))
            return subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "independent.py"), str(path)],
                                  text=True, capture_output=True, timeout=30)

    def rejects(self, mutate, expected_message):
        data = copy.deepcopy(self.certificate)
        mutate(data)
        self.assertNotEqual(data, self.certificate, "mutation control made no change")
        result = self.run_independent(data)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_message, result.stderr)

    def test_recompressed_certificate_accepted(self):
        result = self.run_independent(self.certificate)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_window_rejected(self):
        self.rejects(lambda d: d["windows"].pop(0), "window identity")

    def test_duplicate_corrective_order_rejected(self):
        self.rejects(lambda d: d["windows"][0]["variants"].__setitem__(0, d["windows"][0]["variants"][1]),
                     "variant coverage")

    def test_false_intersection_dimension_rejected(self):
        self.rejects(lambda d: d["windows"][0]["variants"][0]["flag_dimensions"].__setitem__(2, 8),
                     "independent flag dimension")

    def test_missing_rank_schedule_rejected(self):
        self.rejects(lambda d: d["windows"][0]["variants"][0]["schedules"].pop(), "rank domain")

    def test_same_mass_false_histogram_rejected(self):
        def mutate(data):
            for window in data["windows"]:
                for variant in window["variants"]:
                    for schedule in variant["schedules"]:
                        if schedule[3][1]:
                            schedule[3][1] -= 1
                            schedule[3][0] += 2
                            return
            self.fail("no rank-two test fixture")
        self.rejects(mutate, "schedule histogram or slack mismatch")

    def test_forged_concavity_slack_rejected(self):
        def mutate(data):
            slacks = data["windows"][0]["variants"][0]["schedules"][0][4]
            slacks[0] += 1
        self.rejects(mutate, "schedule histogram or slack mismatch")

    def test_false_coverage_total_rejected(self):
        self.rejects(lambda d: d["summary"].__setitem__("rational_rank_schedules", 1670),
                     "independent rank coverage")


if __name__ == "__main__":
    unittest.main(verbosity=2)

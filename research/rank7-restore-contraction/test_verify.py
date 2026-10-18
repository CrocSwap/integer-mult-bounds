# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the literal contraction, lower bound and invoice."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from itertools import product
from pathlib import Path
from unittest.mock import patch

import verify
from contract import NEW, OLD, START, operator, produce, projected_block
from frames import trace
from minimality import KINDS, exclude_two, symbolic_pair


def evaluate(gates, state, projection):
    state = [list(row) for row in state]
    for gate in gates:
        target = 0 if gate[1] == 22 else 1
        source = 1 - target
        scaled = [sum(a * b for a, b in zip(row, state[source], strict=True))
                  for row in projection]
        factor = Fraction(gate[3], gate[4])
        state[target] = [a + factor * b for a, b in
                         zip(state[target], scaled, strict=True)]
    return state


class ContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = verify.read(verify.PACKAGE / "vendor/WORD-base.json.gz")

    def test_real_both_provider_receipt(self):
        result = verify.audit()
        self.assertEqual(result["status"], "PASS_RANK7_RESTORE_CONTRACTION")
        self.assertEqual(result["bill"]["profile_delta"], {})
        for variant in ("base", "extra"):
            self.assertEqual(result["variants"][variant]["section_lengths"]["restore"],
                             [212, 211])
            self.assertEqual(result["variants"][variant]["private_buffers"], 91)

    def test_independent_dense_dirty_idempotent_substitutions(self):
        projections = (((1, 0), (0, 1)), ((1, 1), (0, 0)), ((0, 0), (0, 0)))
        for values in product((-2, Fraction(1, 2), 3), repeat=4):
            state = [values[:2], values[2:]]
            for projection in projections:
                self.assertEqual(evaluate(OLD, state, projection),
                                 evaluate(NEW, state, projection))
        self.assertEqual(evaluate(NEW, [[2, 3], [5, 7]], projections[0]),
                         [[-5, -7], [-3, -4]])

    def test_idempotence_is_a_real_hypothesis(self):
        state = [[2, 3], [5, 7]]
        nonprojection = ((2, 0), (0, 2))
        self.assertNotEqual(evaluate(OLD, state, nonprojection),
                            evaluate(NEW, state, nonprojection))

    def test_dropped_gate_rejected_by_dirty_operator(self):
        candidate = produce(self.parent)
        del candidate["restore"][START]
        with self.assertRaisesRegex(ValueError, "dirty restore"):
            verify.same_operator(self.parent["restore"], candidate["restore"])

    def test_wrong_dyadic_coefficient_rejected(self):
        candidate = produce(self.parent)
        candidate["restore"][START + 2][3] = 1
        with self.assertRaisesRegex(ValueError, "dirty restore"):
            verify.verify_pair(self.parent, candidate)

    def test_stale_inverse_cleanup_rejected(self):
        candidate = produce(self.parent)
        self.assertEqual(operator(candidate["cleanup"][33:36], (22, 934)),
                         {22: {22: -1, 934: 1}, 934: {22: -1}})
        candidate["cleanup"] = copy.deepcopy(self.parent["cleanup"])
        with self.assertRaisesRegex(ValueError, "inverse cleanup"):
            verify.verify_pair(self.parent, candidate)

    def test_frame_edit_rejected_even_though_scalar_identity_holds(self):
        candidate = produce(self.parent)
        candidate["restore"][START][-1] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        verify.same_operator(self.parent["restore"], candidate["restore"])
        with self.assertRaisesRegex(ValueError, "nonmonotone"):
            trace(candidate)
        bad = copy.deepcopy(NEW)
        bad[0][-1] = []
        with self.assertRaisesRegex(ValueError, "common frame"):
            projected_block(bad)

    def test_changed_endpoint_bill_rejected(self):
        candidate = produce(self.parent)
        candidate["helper_final"]["230"] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        with self.assertRaisesRegex(ValueError, "local profile"):
            verify.verify_pair(self.parent, candidate)

    def test_unlisted_program_edit_and_stale_report_rejected(self):
        candidate = produce(self.parent)
        candidate["A"][0][3] *= -1
        with self.assertRaisesRegex(ValueError, "only restore"):
            verify.verify_pair(self.parent, candidate)
        candidate = produce(self.parent)
        candidate["report"]["local_profile"]["1"] += 1
        with self.assertRaises(ValueError):
            verify.verify_pair(self.parent, candidate)

    def test_wrong_preimage_and_bad_scalar_inputs_rejected(self):
        parent = copy.deepcopy(self.parent)
        parent["restore"][START][3] *= -1
        with self.assertRaisesRegex(ValueError, "preimage"):
            produce(parent)
        for gate in (["add", 22, 22, 1, 1, []], ["add", 22, 230, 1, 0, []],
                     ["scale", 22, 0, 1, []]):
            with self.assertRaises(ValueError):
                operator([gate], (22, 230))

    def test_lower_bound_does_not_certify_easy_targets(self):
        self.assertEqual(len(exclude_two()), 16)
        for easy in (((1, 0), (0, 1)), ((1, 2), (0, 1)), ((2, 0), (0, 1))):
            with self.assertRaisesRegex(ValueError, "no universal obstruction"):
                exclude_two(easy)

    def test_symbolic_templates_match_independent_numeric_matrices(self):
        for kinds in product(KINDS, repeat=2):
            symbolic = symbolic_pair(kinds)
            for a, b in product(range(-2, 3), repeat=2):
                rows = [[1, 0], [0, 1]]
                for kind, coefficient in zip(kinds, (a, b), strict=True):
                    t = 0 if kind.endswith("x") else 1
                    if kind.startswith("scale"):
                        rows[t] = [coefficient * x for x in rows[t]]
                    else:
                        rows[t] = [x + coefficient * y for x, y in
                                   zip(rows[t], rows[1 - t], strict=True)]
                actual = [[p[0] + a * p[1] + b * p[2] + a * b * p[3] for p in row]
                          for row in symbolic]
                self.assertEqual(actual, rows)

    def test_source_corruption_and_missing_pin_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in verify.FILES | {"VENDOR.json", "SOURCES.json"}:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.PACKAGE / name, destination)
            verify.check_pins(root)
            word = root / "vendor/WORD-base.json.gz"
            word.write_bytes(word.read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "source digest"):
                verify.check_pins(root)
            records = json.loads((root / "VENDOR.json").read_text())
            records["files"].pop()
            (root / "VENDOR.json").write_text(json.dumps(records))
            with self.assertRaisesRegex(ValueError, "complete vendor"):
                verify.check_pins(root)
            profile = root / "vendor/PROFILE.json"
            counts = json.loads(profile.read_text())
            counts["1"] -= 1
            profile.write_text(json.dumps(counts))
            with (
                patch.object(verify, "PACKAGE", root),
                self.assertRaisesRegex(ValueError, "source complete profile"),
            ):
                verify.whole_bill()

    def test_real_cli_can_emit_the_verified_contraction(self):
        command = [sys.executable, "-W", "error", "-B", str(verify.PACKAGE / "verify.py"),
                   "--emit-word", "base"]
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
        self.assertEqual(json.loads(result.stdout), produce(self.parent))
        invalid = subprocess.run([*command[:-1], "unknown"], capture_output=True,
                                 text=True, check=False, timeout=30)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, "")


if __name__ == "__main__":
    unittest.main()

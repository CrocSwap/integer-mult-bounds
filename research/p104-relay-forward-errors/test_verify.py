#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the combined forward precision certificate."""

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p104_forward_errors", P / "verify.py")
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


class PrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core, cls.word = V.load_inputs()
        cls.gates, cls.schedule = V.compile_word(cls.core, cls.word)
        cls.expected = json.loads((P / "EXPECTED.json").read_text())

    def test_complete_receipt(self):
        self.assertEqual(V.audit(self.core, self.word), self.expected)

    def test_signed_suffix_fixture_and_copy_overwrite(self):
        # z <- z - (y+2x)/2: three private/scalar defects have gain -1/2,
        # and the final ADD defect has gain +1. Exact allocation/discard add none.
        gates = [V.Gate("zero", V.PRIVATE), V.Gate("add", 1, 0, Q(2)),
                 V.Gate("copy", V.PRIVATE, 1, Q(1)),
                 V.Gate("transport", V.PRIVATE),
                 V.Gate("add", 2, V.PRIVATE, Q(-1, 2)), V.Gate("erase", V.PRIVATE)]
        total, evidence = V.defect_witness(gates, 2)
        self.assertEqual(total, Q(5, 2))
        self.assertEqual(evidence["nonzero_defects"], 4)
        all_cut = V.error_certificate(gates)
        self.assertEqual(all_cut["max_error_l1"], "3")
        self.assertEqual(all_cut["witness"]["register"], "C")
        initial = [0] * V.N
        initial[:3] = [3, 5, 7]
        self.assertEqual(V.scalar_replay(gates, initial)[2], Q(3, 2))
        columns = [{0: Q(1)}, {1: Q(1)}, {2: Q(1)}] + [{} for _ in range(V.N - 2)]
        for gate in reversed(gates):
            V.pullback(columns, gate)
        self.assertEqual(columns[0], {0: Q(1), 1: Q(2), 2: Q(-1)})
        self.assertEqual(columns[1], {1: Q(1), 2: Q(-1, 2)})
        self.assertEqual(columns[V.PRIVATE], {})
        # A defect before an overwriting COPY cannot survive that COPY.
        reset = [V.Gate("zero", V.PRIVATE), V.Gate("transport", V.PRIVATE),
                 V.Gate("copy", V.PRIVATE, 0, Q(1)),
                 V.Gate("add", 1, V.PRIVATE, Q(1)), V.Gate("erase", V.PRIVATE)]
        self.assertEqual(V.scalar_replay(reset, [0] * V.N, {1: Q(7)})[1], 0)

    def test_dirty_compensation_and_core_omission_reject(self):
        bad = copy.deepcopy(self.word)
        bad["ops"][1][3] = "1"
        gates, _ = V.compile_word(self.core, bad)
        with self.assertRaisesRegex(ValueError, "complete forward endpoint"):
            V.prefix_certificate(gates)
        with self.assertRaisesRegex(ValueError, "complete forward endpoint"):
            V.prefix_certificate([g for g in self.gates if g.section == "relay"])

    def test_copy_binding_and_final_discard_reject(self):
        copy_at = next(i for i, g in enumerate(self.gates) if g.kind == "copy")
        bad = self.gates.copy()
        bad[copy_at] = replace(bad[copy_at], src=0)
        with self.assertRaisesRegex(ValueError, "complete forward endpoint"):
            V.prefix_certificate(bad)
        erase_at = max(i for i, g in enumerate(self.gates) if g.kind == "erase")
        bad = self.gates.copy()
        bad[erase_at] = replace(bad[erase_at], kind="transport")
        with self.assertRaisesRegex(ValueError, "private final discard"):
            V.prefix_certificate(bad)

    def test_chronology_rank_and_ownership_reject(self):
        bad = copy.deepcopy(self.word)
        contact = next(op for op in bad["ops"] if op[0] == "write" and op[-1] == 4058)
        contact[-1] = 0
        with self.assertRaisesRegex(ValueError, "relay common frame"):
            V.compile_word(self.core, bad)
        bad_core = copy.deepcopy(self.core)
        next(op for op in bad_core["program"] if op[0] == "transport")[4] += 1
        with self.assertRaisesRegex(ValueError, "core transport rank/entry"):
            V.compile_word(bad_core, self.word)
        bad = copy.deepcopy(self.word)
        next(op for op in bad["ops"] if op[0] == "move")[2] = []
        with self.assertRaisesRegex(ValueError, "relay monotone move"):
            V.compile_word(self.core, bad)
        bad_core = copy.deepcopy(self.core)
        next(op for op in bad_core["program"] if op[0] == "zero")[1] = "Q0"
        with self.assertRaisesRegex(ValueError, "private allocation ownership"):
            V.compile_word(bad_core, self.word)

    def test_equivalent_binary_bases(self):
        core, word = copy.deepcopy(self.core), copy.deepcopy(self.word)
        for group in (core["initial_frames"], core["final_frames"]):
            for basis in group.values():
                basis.reverse()
        for op in core["program"]:
            for value in op:
                if isinstance(value, list):
                    value.reverse()
        for op in word["ops"]:
            if op[0] == "move":
                op[2].reverse()
        self.assertEqual(V.compile_word(core, word), (self.gates, self.schedule))

    def test_endpoint_preserving_growth_and_error_change(self):
        at = self.expected["prefix"]["norm_witness"]["combined_event"] + 1
        dst = V.INDEX["Y67"]
        extra = [V.Gate("add", dst, 0, Q(4)), V.Gate("add", dst, 0, Q(-4))]
        bad = self.gates[:at] + extra + self.gates[at:]
        result = V.prefix_certificate(bad)  # All endpoint coefficients still pass.
        self.assertGreater(Q(result["max_row_l1"]), Q(self.expected["prefix"]["max_row_l1"]))
        old, _ = V.defect_witness(self.gates, dst)
        new, _ = V.defect_witness(bad, dst)
        self.assertEqual(new, old + 2)
        extra = [V.Gate("add", dst, 0, Q(1, 16)), V.Gate("add", dst, 0, Q(-1, 16))]
        result = V.prefix_certificate(self.gates[:at] + extra + self.gates[at:])
        self.assertEqual(result["largest_denominator"], 16)

    def test_export_pins_receipt_and_exclusive_output(self):
        # Replays from an export without Git, against the same exact inputs.
        with tempfile.TemporaryDirectory(prefix="p104-forward-test-") as directory:
            root = Path(directory)
            package = root / "research/p104-relay-forward-errors"
            shutil.copytree(P, package, ignore=shutil.ignore_patterns("__pycache__"))
            source = root / V.CORE_PATH
            source.parent.mkdir(parents=True)
            source.write_bytes((V.ROOT / V.CORE_PATH).read_bytes())
            files = [f for f in root.rglob("*") if f.is_file()]
            before = {str(f.relative_to(root)): f.read_bytes() for f in files}
            out = root / "result.json"
            command = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]

            def run(extra=()):
                return subprocess.run(command + list(extra), capture_output=True, text=True,
                                      timeout=30, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

            good = run(["--out", str(out)])
            self.assertEqual(good.returncode, 0, good.stderr[-1500:])
            self.assertEqual(json.loads(out.read_text()), self.expected)
            for f in files:
                self.assertEqual(f.read_bytes(), before[str(f.relative_to(root))])
            again = run(["--out", str(out)])
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("FileExistsError", again.stderr)
            receipt = package / "EXPECTED.json"
            drift = copy.deepcopy(self.expected)
            drift["suffix"]["unit_defect_final_bound"] = "1"
            receipt.write_text(json.dumps(drift))
            self.assertIn("receipt drift", run().stderr)
            source.write_bytes(source.read_bytes() + b"\n")
            self.assertIn("core source pin", run().stderr)
            source.write_bytes((V.ROOT / V.CORE_PATH).read_bytes())
            word = package / "inputs/WORD.json"
            word.write_bytes(word.read_bytes() + b"\n")
            self.assertIn("relay source pin", run().stderr)


if __name__ == "__main__":
    unittest.main()

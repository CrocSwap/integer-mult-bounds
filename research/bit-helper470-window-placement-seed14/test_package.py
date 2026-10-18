#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mathematical boundary and fault-injection tests for the scoped package."""
import copy
import gzip
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("placement", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Boundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = v.read_inputs()
        cls.word = json.loads(gzip.decompress(cls.inputs[v.WORD]))
        cls.geo = v.Geometry(cls.word)
        cls.record = json.loads(cls.inputs[v.RECORD])
        cls.slots = v.allocate(json.loads(cls.inputs[v.SELECTION])["bit"])
        cls.win = v.windows(v.schedule())
        cls.local = Counter({int(k): n for k, n in cls.record["word"]["local_histogram"].items()})
        cls.baseline = v.full_profile(cls.local, cls.slots, cls.win, set())
        cls.certificate = json.loads((HERE / "CERTIFICATE.json").read_text())

    def test_three_early_gates_are_necessary(self):
        for gate in range(3):
            with self.subTest(gate=gate), self.assertRaises(v.Reject):
                v.local_replay(self.word, self.geo, True, omit_early=gate)

    def test_last_touch_is_not_just_pair_inequality(self):
        # Stage zero and stage two both use pair zero, but only stage two is
        # after the intervening bridge touching rank-seven host pair one.
        self.assertEqual(self.win[1][2], (2,))
        events = copy.deepcopy(v.schedule())
        after = next(i for i, e in enumerate(events) if e.get("stage") == 2)
        events.insert(after + 1, {"kind": "bridge", "dst": 0, "src": 1, "coefficient": 1})
        self.assertEqual(v.windows(events)[1][2], ())

    def joint_slots(self, stages):
        replacements = {s: (6, 213, 7 * i, 7, s, v.HELPER) for i, s in enumerate(stages)}
        return [replacements.get(row[4], row) if row[5] == v.HELPER else row for row in self.slots]

    def test_shared_large_remainder_is_charged_jointly(self):
        for stages in ((3, 4), tuple(range(3, 9))):
            with self.subTest(stages=stages):
                slots = self.joint_slots(stages)
                literal = v.full_profile(self.local, slots, self.win, set(stages))
                expected = next(g for g in self.certificate["joint_rank42_subsets"] if g["stages"] == list(stages))
                delta = Counter({int(r): n * 32 for r, n in expected["profile_delta"].items() if n})
                self.assertEqual(v.difference(literal, self.baseline), delta)
                if len(stages) == 6:
                    self.assertEqual(delta[42], -32)
                    self.assertNotIn(0, delta)

    def test_partial_overlap_is_rejected(self):
        slots = [list(row) for row in self.joint_slots((3, 4))]
        at = next(i for i, row in enumerate(slots) if row[4:] == [4, v.HELPER])
        slots[at][2] = 6
        with self.assertRaisesRegex(v.Reject, "coordinate collision"):
            v.placement_audit(slots, self.win, {3, 4})

    def test_returned_and_consumed_rank_are_both_required(self):
        for old in (2, 4, 6):
            correct = v.single_delta(old, 7)
            self.assertEqual(sum(r * n for r, n in correct.items()), 0)
            self.assertEqual(sum(correct.values()), 0)
            self.assertLess(v.raw_cost(correct)[1], 0)
            no_return = Counter(correct)
            no_return[old + 8] -= 1
            no_return[old] += 1
            self.assertEqual(sum(r * n for r, n in no_return.items()), -8)

    def test_source_corruption_fails_before_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in self.inputs.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data + (b" " if name == v.SELECTION else b""))
            with self.assertRaisesRegex(v.Reject, "source SHA256"):
                v.read_inputs(root)

    def test_forged_receipt_rejected_under_optimization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for name in ("verify.py", "independent.py", "SOURCES.json"):
                shutil.copyfile(HERE / name, package / name)
            for name, data in self.inputs.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            forged = copy.deepcopy(self.certificate)
            forged["replacement_slots"][0][1] += 1
            (package / "CERTIFICATE.json").write_text(v.canonical(forged))
            for script in ("verify.py", "independent.py"):
                run = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script)],
                                     capture_output=True, text=True, timeout=30)
                self.assertNotEqual(run.returncode, 0, run.stdout)
                self.assertIn("certificate mismatch" if script == "verify.py" else "witness binding", run.stderr)


if __name__ == "__main__":
    unittest.main()

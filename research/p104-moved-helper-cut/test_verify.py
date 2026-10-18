# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the mathematical support/cut boundary."""
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("moved_helper_audit", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
cut_spec = importlib.util.spec_from_file_location("algebraic_cut", HERE / "check_cut.py")
c = importlib.util.module_from_spec(cut_spec)
cut_spec.loader.exec_module(c)


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = v.load()
        cls.g = v.geometry(cls.inputs)
        cls.base = v.incidence(cls.g)
        cls.matrix, cls.demands, _ = v.required_coefficients(cls.inputs["P104-FIXTURE.json"])

    def compare_tiny(self, network, expected, count, sources):
        actual, _ = v.propagate(network, count=count, target_count=len(expected))
        self.assertEqual(actual, expected)
        self.assertEqual(v.bfs_outputs(network, source_count=sources, count=count), expected)

    def test_fresh_read_can_cross_same_layer_chain(self):
        # Literal word: h0 += X0; h1 += h0; h2 += h1; Y0 += h2.
        network = ({1: [{0, 1}, {0, 1, 2}, {1, 2}]},
                   {1: [1, 0, 0]}, {1: [0, 0, 1]}, [0])
        self.compare_tiny(network, [1], 3, 1)

    def test_all_writers_and_direct_reads_accumulate(self):
        # Two disjoint helper outputs and an independent direct read of X2.
        network = ({1: [{0}, {1}]}, {1: [1, 2]}, {1: [1, 1]}, [4])
        self.compare_tiny(network, [7], 2, 3)
        swapped = ({1: [{0}, {1}]}, {1: [2, 1]}, {1: [1, 1]}, [4])
        self.compare_tiny(swapped, [7], 2, 3)

    def test_late_source_cannot_travel_backwards(self):
        network = ({1: [{0, 1}, {0, 1}], 2: [{0}, {1}]},
                   {1: [0, 0], 2: [1, 0]}, {1: [0, 1], 2: [0, 0]}, [0])
        self.compare_tiny(network, [0], 2, 1)

    def test_independent_dirt_has_no_source_coefficient(self):
        network = ({1: [{0, 1}, {0, 1}]}, {1: [0, 0]}, {1: [1, 1]}, [0])
        self.compare_tiny(network, [0], 2, 1)

    def test_nonnested_positive_control_is_illegal_but_effective(self):
        cut = v.cut_receipt(self.g, self.base, self.matrix, self.demands)
        flag = [v.span(b) for b in cut["nonnested_positive_control"]["flag_bases"]]
        with self.assertRaisesRegex(ValueError, "nested flag"):
            v.flag_profile(self.g, flag)
        profile = v.flag_profile(self.g, flag, require_nested=False)
        output, _ = v.propagate(v.constrain(self.base, profile))
        self.assertTrue(output[40] & (1 << 1))

    def test_changed_contact_or_coefficient_invalidates_cut(self):
        changed = copy.deepcopy(self.base)
        changed[0][4][91].add(2)
        changed[0][4][2].add(91)
        with self.assertRaisesRegex(ValueError, "contact boundary"):
            v.cut_receipt(self.g, changed, self.matrix, self.demands)
        matrix = copy.deepcopy(self.matrix)
        matrix[40][1] = 0
        with self.assertRaisesRegex(ValueError, "cut coefficient"):
            v.cut_receipt(self.g, self.base, matrix, self.demands)

    def test_equivalent_basis_and_incompatible_pairing(self):
        changed = copy.deepcopy(self.inputs)
        word = changed["LOWRANK-WITNESS.json"]
        for bank in (word["initial_frames"], word["final_frames"]):
            for name in bank:
                bank[name].reverse()
        for event in word["program"]:
            if event[0] == "transport":
                event[2].reverse()
                event[3].reverse()
        g = v.geometry(changed)
        self.assertEqual(g["frames"], self.g["frames"])
        self.assertEqual(g["paths"], self.g["paths"])
        changed["WITNESS.json"]["pairing"][13] = changed["WITNESS.json"]["pairing"][14]
        with self.assertRaisesRegex(ValueError, "perfect matching"):
            v.geometry(changed)

    def test_logical_channel_binds_port_order(self):
        receipt = v.source_response(self.inputs["LOWRANK-WITNESS.json"], self.matrix)
        self.assertEqual(receipt["target_coefficients"], 10816)
        wrong = copy.deepcopy(self.matrix)
        for row in wrong:
            row[0], row[1] = row[1], row[0]
        with self.assertRaisesRegex(ValueError, "Gram/channel port-order binding"):
            v.source_response(self.inputs["LOWRANK-WITNESS.json"], wrong)
        bad_word = copy.deepcopy(self.inputs["LOWRANK-WITNESS.json"])
        first = next(e for e in bad_word["program"] if e[0] == "add")
        first[4] = [1]
        with self.assertRaisesRegex(ValueError, "common-frame ADD"):
            v.source_response(bad_word, self.matrix)

    def test_interval_contact_formula_against_all_f2_cubed_spaces(self):
        # Pruning-free literal ground truth, unrelated to elimination ranks.
        spaces = set()
        for size in range(4):
            for generators in combinations(range(1, 8), size):
                space = {0}
                for generator in generators:
                    space |= {x ^ generator for x in space}
                spaces.add(frozenset(space))
        self.assertEqual(len(spaces), 16)
        intervals = [(a, b) for a in spaces for b in spaces if a <= b]
        self.assertEqual(len(intervals), 66)
        choices = {(a, b, d): {s for s in spaces if a <= s <= b and len(s) == 1 << d}
                   for a, b in intervals for d in range(4)}
        comparisons = 0
        for a, b in intervals:
            for x, y in intervals:
                for d in range(4):
                    literal = bool(choices[a, b, d] & choices[x, y, d])
                    algebraic = c.possible_contact((c.reduced(a), c.reduced(b)),
                                                   (c.reduced(x), c.reduced(y)), d)
                    self.assertEqual(algebraic, literal)
                    comparisons += 1
        self.assertEqual(comparisons, 17424)

    def test_separate_algebraic_cut_and_reverse_row(self):
        actual = c.derive(self.inputs)
        primary = v.cut_receipt(self.g, self.base, self.matrix, self.demands)
        self.assertEqual(actual, {key: primary[key] for key in actual})
        self.assertEqual(c.target_row(self.inputs["LOWRANK-WITNESS.json"]), self.matrix[40])

    def test_optimized_gitfree_export_and_corruption_rejection(self):
        with tempfile.TemporaryDirectory(prefix="p104-moved-cut-") as tmp:
            root = Path(tmp)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for name in ("verify.py", "check_cut.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(HERE / name, package / name)
            for row in v.read_json(HERE / "SOURCES.json")["files"]:
                if row["usage"] == "input":
                    destination = root / row["path"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / row["path"], destination)
            argv = [sys.executable, "-I", "-O", "-B", str(package / "verify.py"), "--cut-only"]
            # Isolated mode and no imported repository modules make old pyc irrelevant.
            def run():
                return subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=30)
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            valid = run()
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertIn("PASS_P104_MOVED_HELPER_SMALL_CUT", valid.stdout)
            independent = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "check_cut.py")],
                                         cwd=root, text=True, capture_output=True, timeout=30)
            self.assertEqual(independent.returncode, 0, independent.stderr)
            self.assertIn("PASS_P104_MOVED_HELPER_ALGEBRAIC_CUT", independent.stdout)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            receipt = v.read_json(package / "RESULT.json")
            receipt["cut"]["required_coefficient"] = "0"
            (package / "RESULT.json").write_text(json.dumps(receipt))
            invalid = run()
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("receipt equality", invalid.stderr)
            shutil.copyfile(HERE / "RESULT.json", package / "RESULT.json")
            source = root / "research/p104-alternating-cycle-neighborhood/WITNESS.json"
            source.write_bytes(source.read_bytes() + b"\n")
            invalid = run()
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("source hash:", invalid.stderr)


if __name__ == "__main__":
    unittest.main()

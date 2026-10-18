# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the matching certificate and both dependency algorithms."""

import copy
import itertools
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
V = runpy.run_path(str(PACKAGE / "verify.py"))
L = runpy.run_path(str(PACKAGE / "literal.py"))


def child(package, *args):
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-Werror",
            "-B",
            str(package / "verify.py"),
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=25,
        env=env,
        check=False,
    )


def export(root):
    package = root / "research/p104-coherent-support-witness"
    shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
    for name in V["INPUTS"]:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(V["ROOT"] / name, destination)
    return package


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = V["inputs"]()
        cls.paths = V["data_paths"](cls.inputs[1])
        cls.frames = V["cover_frames"](cls.inputs[0], cls.paths)
        cls.witness = V["read_json"](PACKAGE / "WITNESS.json")
        cls.control = V["control_pairing"]()

    def test_actual_clis_and_git_free_read_only_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = export(root)
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            for args in ((), ("--literal",)):
                result = child(package, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("required=4992 missing=0", result.stdout)
            self.assertEqual(list(root.rglob("*.pyc")), [])
            self.assertFalse((root / ".git").exists())

    def test_literal_contacts_and_separate_bfs_agree(self):
        edges = list(enumerate(self.witness["pairing"]))
        interval = V["interval_layers"](self.frames, edges, self.paths)
        literal = L["literal_layers"](self.frames, edges, self.paths)
        self.assertEqual(interval, literal)
        output, summary = L["independent_trace"](literal, self.paths)
        self.assertEqual(output, [(1 << 104) - 1] * 104)
        self.assertEqual((output, summary), V["trace"](interval, self.paths))

    def test_published_and_45_missing_controls(self):
        matrix = V["correction"](self.inputs[2])
        original = V["published_pairing"](self.inputs[0], self.frames[-1])
        for pairing, missing in ((original, 3095), (self.control, 45)):
            edges = list(enumerate(pairing))
            layers = V["interval_layers"](self.frames, edges, self.paths)
            report = V["report"](edges, layers, self.paths, matrix)
            self.assertEqual(report["unreachable_required_pairs"], missing)
            if missing == 45:
                masks = report["missing_source_masks_hex"]
                self.assertEqual([t for t, m in enumerate(masks) if int(m, 16)], [40])
                self.assertEqual(
                    int(report["target_source_masks_hex"][40], 16),
                    (1 << 8) | (1 << 41) | (1 << 45),
                )

    def test_cycle_schema_bijection_and_exact_edit(self):
        cases = []
        for field, value in (
            ("schema_version", True),
            ("cycle", [139] * 4),
            ("cycle", [139, 154, 182]),
            ("cycle", [True, 154, 182, 179]),
        ):
            value_copy = copy.deepcopy(self.witness)
            value_copy[field] = value
            cases.append(value_copy)
        for a, b in ((0, 0), (139, self.control[139])):
            value_copy = copy.deepcopy(self.witness)
            value_copy["pairing"][a] = b
            cases.append(value_copy)
        value_copy = copy.deepcopy(self.witness)
        value_copy["pairing"] = self.control
        cases.append(value_copy)
        for witness in cases:
            with self.assertRaises(ValueError):
                V["check_witness"](witness, self.control, self.frames[-1])
        self.assertEqual(
            V["check_witness"](self.witness, self.control, self.frames[-1]),
            [[139, 7, 186], [154, 186, 146], [179, 171, 7], [182, 146, 171]],
        )

    def test_new_bridge_uses_the_changed_arrival(self):
        _, departures, arrivals, _, _ = self.frames
        common = V["span"]([113, 288, 2, 424])
        self.assertEqual(V["dim"](common), 4)
        self.assertEqual(departures[139] & common, departures[139])
        self.assertEqual(departures[91] & common, departures[91])
        self.assertEqual(common & arrivals[186], common)
        self.assertEqual(common & arrivals[8], common)
        self.assertNotEqual(common & arrivals[7], common)
        self.assertFalse(
            V["contact"](
                (departures[139], arrivals[7]), (departures[91], arrivals[8]), 4
            )
        )
        self.assertTrue(
            V["contact"](
                (departures[139], arrivals[186]), (departures[91], arrivals[8]), 4
            )
        )

    def test_all_small_binary_interval_contacts(self):
        spaces = {1}
        for size in range(1, 4):
            for basis in itertools.combinations(range(1, 8), size):
                try:
                    spaces.add(V["span"](list(basis)))
                except ValueError:
                    continue  # Dependent tuples are not subspace bases.
        self.assertEqual(len(spaces), 16)
        intervals = [(a, b) for a in spaces for b in spaces if a & b == a]
        for dimension in range(4):
            choices = [
                {f for f in spaces if V["fits"](bounds, dimension, f)}
                for bounds in intervals
            ]
            for i, left in enumerate(intervals):
                for j, right in enumerate(intervals):
                    self.assertEqual(
                        V["contact"](left, right, dimension),
                        bool(choices[i] & choices[j]),
                    )

    def test_directed_relay_cannot_run_backwards(self):
        paths = {
            f"{kind}{i}": [1 << (i + offset)]
            for kind, offset in (("X", 1), ("Y", 200))
            for i in range(104)
        }
        for late, expected in ((False, 1), (True, 0)):
            layers = [([1, 2], [0, 0], [0, 0]) for _ in range(8)]
            layers[3 if late else 1][1][0] = 1
            layers[2][0][:] = [3, 3]
            layers[3][2][1] = 1
            primary = V["trace"](layers, paths)
            independent = L["independent_trace"](layers, paths)
            self.assertEqual(primary, independent)
            self.assertEqual(primary[0][0], expected)
            self.assertEqual(primary[0][1:], [0] * 103)

    def test_source_control_and_receipt_mutations_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = export(root)
            mutations = [root / V["INPUTS"][2], package / "CONTROL.json"]
            for path in mutations:
                raw = path.read_bytes()
                path.write_bytes(raw + b"\n")
                result = child(package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("SHA256", result.stderr)
                path.write_bytes(raw)
            path = package / "RESULT.json"
            value = json.loads(path.read_bytes())
            value["passing"]["required_pairs"] = True
            path.write_text(json.dumps(value))
            result = child(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exact typed receipt", result.stderr)

    def test_duplicate_keys_and_contact_dropping_mutant_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = export(Path(tmp))
            path = package / "WITNESS.json"
            raw = path.read_bytes()
            path.write_bytes(
                raw.replace(
                    b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'
                )
            )
            result = child(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate JSON key", result.stderr)
            path.write_bytes(raw)
            oracle = package / "literal.py"
            text = oracle.read_text()
            old = "adjacency[bit.bit_length() - 1] |= mask"
            self.assertEqual(text.count(old), 1)
            oracle.write_text(
                text.replace(old, "pass  # Deliberately omit relay contacts.")
            )
            result = child(package, "--literal")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FAIL_P104_COHERENT_SUPPORT:", result.stderr)


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the P104 matching-coherence certificate."""

import copy
import itertools
import json
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


def export(root):
    package = root / "research" / PACKAGE.name
    package.mkdir(parents=True)
    for name in (
        "verify.py",
        "literal.py",
        "SOURCES.json",
        "WITNESS.json",
        "RESULT.json",
    ):
        shutil.copyfile(PACKAGE / name, package / name)
    for name in V["INPUTS"]:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE.parents[1] / name, destination)
    return package


def run(package, *args):
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
        cwd=package,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


class CertificateTests(unittest.TestCase):
    def test_contact_criterion_on_every_small_subspace_interval(self):
        spaces = {1}
        for size in range(1, 4):
            for basis in itertools.combinations(range(1, 8), size):
                try:
                    spaces.add(V["span"](list(basis)))
                except ValueError:
                    pass  # Dependent lists do not specify new subspaces.
        self.assertEqual(len(spaces), 16)
        intervals = [(a, b) for a in spaces for b in spaces if a & b == a]
        checks = 0
        for left, right in itertools.product(intervals, repeat=2):
            for dimension in range(4):
                literal = any(
                    V["dim"](f) == dimension
                    and left[0] & f == left[0]
                    and f & left[1] == f
                    and right[0] & f == right[0]
                    and f & right[1] == f
                    for f in spaces
                )
                self.assertEqual(V["contact"](left, right, dimension), literal)
                checks += 1
        self.assertGreater(checks, 1000)
        a, b = V["span"]([1, 2]), V["span"]([4, 8])
        full = V["span"]([1, 2, 4, 8])
        self.assertFalse(V["contact"]((a, full), (b, full), 3))
        self.assertTrue(V["contact"]((a, full), (b, full), 4))

    def test_alternating_cycles_against_all_three_slot_graphs(self):
        accepted = 0
        for mask in range(1 << 9):
            graph = [[j for j in range(3) if mask >> (3 * i + j) & 1] for i in range(3)]
            matchings = [
                list(p)
                for p in itertools.permutations(range(3))
                if all(p[i] in graph[i] for i in range(3))
            ]
            if not matchings:
                continue
            try:
                result = V["matching_support"](graph, matchings[0])
            except ValueError as error:
                self.assertIn("strongly connected", str(error))
                continue
            supported = {(i, p[i]) for p in matchings for i in range(3)}
            self.assertEqual(result["supported_edges"], len(supported))
            self.assertEqual(len(supported), sum(map(len, graph)))
            accepted += 1
        self.assertGreater(accepted, 10)
        with self.assertRaisesRegex(ValueError, "strongly connected"):
            V["matching_support"]([[0], [0, 1]], [0, 1])

    def test_literal_quotient_census_and_cosets(self):
        quotients = L["quotient_spaces"]()
        self.assertEqual(list(map(len, quotients)), [1, 31, 155, 155, 31, 1])
        low, high = V["span"]([1, 2]), V["span"]([1, 2, 4, 8, 16, 32, 64])
        cosets = L["coset_masks"](low, high)
        self.assertEqual(len(set(cosets)), 32)
        self.assertTrue(all(c.bit_count() == 4 for c in cosets))
        self.assertEqual(sum(cosets), high)
        with self.assertRaisesRegex(ValueError, "dimension"):
            L["coset_masks"](low, low)

    def test_pairing_and_json_boundaries(self):
        graph = [[0, 1], [0, 1]]
        V["check_pairing"]([1, 0], graph)
        for bad in ([0, 0], [True, 0], [2, 0], [0]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                V["check_pairing"](bad, graph)
        with self.assertRaisesRegex(ValueError, "compatible"):
            V["check_pairing"]([1, 0], [[0], [1]])
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            json.loads('{"x":0,"x":1}', object_pairs_hook=V["unique"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversize.json"
            path.write_bytes(b" " * (V["LIMIT"] + 1))
            with self.assertRaisesRegex(ValueError, "size bound"):
                V["read_json"](path)

    def test_forward_flow_and_no_backward_acquisition(self):
        paths = {f"{kind}{i}": [] for kind in "XY" for i in range(104)}
        upward = [([1], [1], [0]), ([1], [0], [1])]
        backward = [([1], [0], [1]), ([1], [1], [0])]
        self.assertEqual(V["trace"](upward, paths)[0][0], 1)
        self.assertEqual(V["trace"](backward, paths)[0][0], 0)
        relay = [([3, 3], [1, 0], [0, 1])]
        self.assertEqual(V["trace"](relay, paths)[0][0], 1)

    def test_actual_clis_and_git_free_export(self):
        expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
        for args in (("--emit",), ("--literal", "--emit")):
            result = run(PACKAGE, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), expected)
        self.assertEqual(expected["published"]["unreachable_required_pairs"], 3095)
        self.assertEqual(expected["rematched"]["unreachable_required_pairs"], 45)
        self.assertEqual(expected["union"]["unreachable_required_pairs"], 0)
        self.assertEqual(
            {
                t
                for t, mask in enumerate(
                    expected["rematched"]["missing_source_masks_hex"]
                )
                if int(mask, 16)
            },
            {40},
        )
        with tempfile.TemporaryDirectory() as directory:
            result = run(export(Path(directory)), "--literal")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P104_MATCHING_COHERENCE", result.stdout)

    def test_cli_source_witness_and_oracle_faults(self):
        with tempfile.TemporaryDirectory() as directory:
            package = export(Path(directory))
            source = Path(directory) / V["INPUTS"][1]
            original_source = source.read_bytes()
            source.write_bytes(original_source + b" ")
            result = run(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input SHA256", result.stderr)
            source.write_bytes(original_source)
            witness = json.loads((package / "WITNESS.json").read_bytes())
            witness["pairing"][0] = witness["pairing"][1]
            (package / "WITNESS.json").write_text(json.dumps(witness))
            result = run(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("bijection", result.stderr)
            shutil.copyfile(PACKAGE / "WITNESS.json", package / "WITNESS.json")
            oracle = package / "literal.py"
            text = oracle.read_text()
            self.assertEqual(text.count("adjacency[bit.bit_length() - 1] |= mask"), 1)
            oracle.write_text(
                text.replace(
                    "adjacency[bit.bit_length() - 1] |= mask",
                    "adjacency[bit.bit_length() - 1] |= bit",
                )
            )
            result = run(package, "--literal")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exact typed receipt", result.stderr)

    def test_cli_receipt_type_and_relation_faults(self):
        with tempfile.TemporaryDirectory() as directory:
            package = export(Path(directory))
            expected = json.loads((package / "RESULT.json").read_bytes())
            for fault in ("type", "relation"):
                mutant = copy.deepcopy(expected)
                if fault == "type":
                    mutant["schema_version"] = True
                else:
                    mutant["rematched"]["missing_source_masks_hex"][40] = "0x0"
                (package / "RESULT.json").write_text(json.dumps(mutant))
                result = run(package, "--literal")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("exact typed receipt", result.stderr)


if __name__ == "__main__":
    unittest.main()

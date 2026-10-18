#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Mathematical regressions and rejection/portability controls."""
import gzip
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine
import independent


def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, "-I", "-O", "-S", "-B", str(script), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True, timeout=120)


class PackageTests(unittest.TestCase):
    def test_first_rank8_footprint_transition(self):
        records = [json.loads(row) for row in (HERE / "generated/CUTS.jsonl").read_text().splitlines()]
        summary = json.loads((HERE / "generated/CERTIFICATE.json").read_text())
        self.assertEqual(summary["arbitrary_suffix_rank8_from_cut"], 177)
        self.assertEqual(summary["arbitrary_suffix_excluded_cuts"], 4697)
        self.assertEqual(summary["first_rank8_footprint_event"], ["B", 88, "MOVE", 208, 0, 152])
        before, after = records[176:178]
        self.assertEqual((before["join_rank"], after["join_rank"]), (7, 8))
        self.assertEqual(before["restore_hex"], after["restore_hex"])
        self.assertEqual(before["dirt_hex"], after["dirt_hex"])
        self.assertTrue(int(after["dirt_hex"], 16) & (1 << 208))
        self.assertTrue(all(row["helper_rank"] == 8 or row.get("join_rank") == 8
                            for row in records[177:]))

    def test_all_binary_3_by_3_inverse_updates(self):
        invertible, updates = 0, 0
        for matrix in itertools.product(range(8), repeat=3):
            try:
                inverse = engine.invert(list(matrix))
            except ValueError:
                continue
            invertible += 1
            rows_as_sets = [set(engine.bits(row)) for row in matrix]
            self.assertEqual([set(engine.bits(row)) for row in inverse],
                             independent.inverse_sets(rows_as_sets))
            for target, source in itertools.permutations(range(3), 2):
                rows, current = list(matrix), inverse[:]
                engine.add(rows, current, target, source)
                self.assertEqual(current, engine.invert(rows))
                self.assertEqual([set(engine.bits(row)) for row in current],
                                 independent.inverse_sets([set(engine.bits(row)) for row in rows]))
                updates += 1
        self.assertEqual((invertible, updates), (168, 1008))

    def test_rational_frames_are_not_binary_frames(self):
        matrix = [[1, 1], [1, -1]]
        self.assertEqual(len(engine.rref(matrix)), 2)
        self.assertEqual(len(independent.integer_basis(matrix)), 2)
        self.assertEqual(independent.bareiss(matrix), -2)
        self.assertEqual(engine.determinant(matrix), -2)
        # Reducing the two rationally independent rows modulo two merges them.
        binary = [sum((x % 2) << i for i, x in enumerate(row)) for row in matrix]
        self.assertEqual(binary, [3, 3])

    def test_outside_frame_span_never_loses_a_vector(self):
        def span(values):
            result = {0}
            for value in values:
                result |= {x ^ value for x in result}
            return result
        cases = 0
        for rows in itertools.product(range(8), repeat=3):
            try:
                engine.invert(list(rows))
            except ValueError:
                continue
            for high in range(8):
                original = span(rows[i] for i in range(3) if high & (1 << i))
                for target, source in itertools.permutations(range(3), 2):
                    operands = (1 << target) | (1 << source)
                    for common_is_high in (False, True):
                        if not common_is_high and high & operands:
                            continue
                        after_high = high | operands if common_is_high else high
                        after = list(rows)
                        after[target] ^= after[source]
                        changed = span(after[i] for i in range(3) if after_high & (1 << i))
                        self.assertTrue(original <= changed)
                        cases += 1
        self.assertEqual(cases, 10080)

    def test_geometry_witness_and_target208_obstruction(self):
        word = json.loads(gzip.decompress((HERE / "inputs/PR589-WORD.json.gz").read_bytes()))
        receipt = json.loads((HERE / "generated/GEOMETRY.json").read_text())
        geometry = independent.Geometry(word, receipt)
        low = next(case for case in receipt["cases"] if case["rank"] == 7)
        self.assertFalse(geometry.join_contained_in_target(tuple(low["frames"]), 208))
        false_minor = json.loads(json.dumps(low))
        false_minor["minor_determinant"] = "0"
        with self.assertRaisesRegex(ValueError, "minor witness"):
            geometry.validate_case(false_minor)
        false_normal = json.loads(json.dumps(low))
        false_normal["annihilating_normal"] = [0]*8
        with self.assertRaisesRegex(ValueError, "upper-bound normal"):
            geometry.validate_case(false_normal)

    def test_both_replays_reject_source_mutation(self):
        with tempfile.TemporaryDirectory(prefix="r439-cut-source-") as root:
            copy = Path(root) / "package"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            with (copy / "inputs/PR589-WORD.json.gz").open("ab") as stream:
                stream.write(b" ")
            for script in ("verify.py", "independent.py"):
                result = run(copy / script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("archive drift", result.stderr)

    def test_both_replays_reject_omitted_cut(self):
        with tempfile.TemporaryDirectory(prefix="r439-cut-ledger-") as root:
            copy = Path(root) / "package"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            path = copy / "generated/CUTS.jsonl"
            rows = path.read_text().splitlines()
            rows.pop(176)
            path.write_text("\n".join(rows)+"\n")
            for script in ("verify.py", "independent.py"):
                result = run(copy / script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("REJECT_", result.stderr)

    def test_both_replays_reject_omitted_move(self):
        with tempfile.TemporaryDirectory(prefix="r439-cut-events-") as root:
            copy = Path(root) / "package"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            path = copy / "generated/EVENTS.json"
            events = json.loads(path.read_text())
            index = next(i for i, event in enumerate(events) if event[2] == "MOVE")
            events.pop(index)
            path.write_text(json.dumps(events, separators=(",", ":"))+"\n")
            for script in ("verify.py", "independent.py"):
                result = run(copy / script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("REJECT_", result.stderr)

    def test_writer_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory(prefix="r439-cut-existing-") as root:
            sentinel = Path(root) / "sentinel"
            sentinel.write_text("keep this")
            result = run(HERE / "verify.py", "--write-directory", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output directory already exists", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep this")

    def test_isolated_optimized_relocation(self):
        with tempfile.TemporaryDirectory(prefix="r439 cut export ") as root:
            copy = Path(root) / "package with spaces"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            before = {str(path.relative_to(copy)): path.read_bytes() for path in copy.rglob("*") if path.is_file()}
            for script, marker in (("verify.py", "PASS_R439_HELPER468_LATE_CUT"),
                                   ("independent.py", "PASS_INDEPENDENT_R439_HELPER468")):
                result = run(copy / script, cwd=root)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(marker, result.stdout)
            after = {str(path.relative_to(copy)): path.read_bytes() for path in copy.rglob("*") if path.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)

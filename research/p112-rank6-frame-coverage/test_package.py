#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Finite mathematical regressions and package rejection controls."""
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


def span(values):
    result = {0}
    for value in values:
        result |= {v ^ value for v in result}
    return result


def oracle_rank(values):
    return len(span(values)).bit_length()-1


def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(script), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True, timeout=240)


class PackageTests(unittest.TestCase):
    def test_joint_domination_all_binary_3_by_4_matrices(self):
        matrices, cases, codimension_one = 0, 0, 0
        for rows in itertools.product(range(16), repeat=3):
            matrices += 1
            r = oracle_rank(rows)
            self.assertEqual(r, len(engine.basis(rows)))
            if r == 0:
                continue
            columns = [sum(((rows[i] >> j) & 1) << i for i in range(3)) for j in range(4)]
            row_zero_sets = [7 ^ word for word in span(columns) if word]
            column_zero_sets = [15 ^ word for word in span(rows) if word]
            row_ranks = [oracle_rank(rows[i] for i in range(3) if s & (1 << i)) for s in range(8)]
            column_ranks = [oracle_rank(row & t for row in rows) for t in range(16)]
            for s in range(8):
                for t in range(16):
                    cases += 1
                    joint = oracle_rank(rows[i] & t for i in range(3) if s & (1 << i))
                    if row_ranks[s] == r and column_ranks[t] == r:
                        self.assertEqual(joint, r)
                    if joint != r-1:
                        continue
                    codimension_one += 1
                    self.assertTrue(row_ranks[s] == r-1 or column_ranks[t] == r-1)
                    row_extension = (row_ranks[s] == r-1 and any(
                        s & ~z == 0 and row_ranks[z] == r-1 for z in row_zero_sets))
                    column_extension = (column_ranks[t] == r-1 and any(
                        t & ~z == 0 and column_ranks[z] == r-1 for z in column_zero_sets))
                    self.assertTrue(row_extension or column_extension)
        self.assertEqual((matrices, cases), (4096, 524160))
        self.assertGreater(codimension_one, 0)

    def test_cover_exactly_and_diagonal_obstruction(self):
        data = engine.model()
        cover = json.loads((HERE / "COVERING.json").read_text())
        result = engine.check_cover(data, cover)
        self.assertEqual(result["copy_bill"], 60)
        self.assertEqual(result["hit_histogram"], {8: 376, 9: 648, 10: 236})
        with self.assertRaisesRegex(ValueError, "uncovered diagonal"):
            engine.check_diagonal_coverage(data, cover)
        _, n, support, frames = independent.independent_geometry(data)
        independent.check_cover(data, n, support, frames, cover)
        self.assertEqual(cover["diagonal_support_coverage"]["histogram"]["0"], 21)

    def test_invalid_copy_and_frame_witnesses_rejected(self):
        data = engine.model()
        cover = json.loads((HERE / "COVERING.json").read_text())
        zero_cut = json.loads(json.dumps(cover))
        zero_cut["terms"][0][2] = "0"
        with self.assertRaisesRegex(ValueError, "maximal-cut dictionary"):
            engine.check_cover(data, zero_cut)
        repeated = json.loads(json.dumps(cover))
        repeated["terms"] = [cover["terms"][0]] * 10
        with self.assertRaisesRegex(ValueError, "misses a frame"):
            engine.check_cover(data, repeated)

    def test_both_replays_reject_archive_mutation(self):
        with tempfile.TemporaryDirectory(prefix="p112-rank6-source-") as root:
            copy = Path(root) / "package"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            with (copy / "inputs/PR1323-MODEL.json").open("ab") as stream:
                stream.write(b" ")
            for script in ("verify.py", "independent.py"):
                result = run(copy / script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("REJECT_", result.stderr)

    def test_independent_rejects_wrong_roots(self):
        lines = engine.model()["lines"]
        lines[0] = [2*x for x in lines[0]]
        with self.assertRaisesRegex(ValueError, "Weyl root"):
            independent.check_roots(lines)

    def test_false_coverage_table_rejected(self):
        with tempfile.TemporaryDirectory(prefix="p112-rank6-table-") as root:
            copy = Path(root) / "package"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            path = copy / "generated/COVERAGE.jsonl"
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            rows[0][2] += 1
            path.write_bytes(engine.table_bytes(rows))
            result = run(copy / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("coverage table disagreement", result.stderr)

    def test_writer_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory(prefix="p112-rank6-write-") as root:
            sentinel = Path(root) / "sentinel"
            sentinel.write_text("preserve me")
            result = run(HERE / "verify.py", "--write-directory", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output directory already exists", result.stderr)
            self.assertEqual(sentinel.read_text(), "preserve me")

    def test_optimized_relocation_both_replays(self):
        with tempfile.TemporaryDirectory(prefix="p112 rank6 relocation ") as root:
            copy = Path(root) / "package with spaces"
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
            for script, marker in (("verify.py", "PASS_P112_RANK6_FRAME_COVERAGE"),
                                   ("independent.py", "PASS_INDEPENDENT_P112_RANK6_COVERAGE")):
                result = run(copy / script, cwd=root)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(marker, result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

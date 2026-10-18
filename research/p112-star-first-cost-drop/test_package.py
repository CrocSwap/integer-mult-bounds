#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Exhaustive small-matrix oracle plus exact failure and relocation controls."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("census_engine", HERE / "engine.py")
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {v ^ vector for v in tuple(values)}
    return values


def small_rank(vectors):
    return len(span(vectors)).bit_length()-1


class PackageTests(unittest.TestCase):
    def run_script(self, folder, name, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(folder / name), *args],
                              cwd=folder.parent, capture_output=True, text=True, timeout=180)

    def portable(self, temporary):
        folder = Path(temporary) / "portable package with spaces"
        shutil.copytree(HERE, folder, ignore=shutil.ignore_patterns("__pycache__"))
        return folder

    def test_every_binary_three_by_four_matrix_and_joint_cut(self):
        cases = 0
        for value in range(4096):
            rows = [(value >> (4*i)) & 15 for i in range(3)]
            rank = small_rank(rows)
            self.assertEqual(len(e.basis(rows)), rank)
            if rank == 0:
                continue
            columns = [sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(4)]
            row_code, col_code = span(columns)-{0}, span(rows)-{0}
            d = min(min(v.bit_count() for v in row_code), min(v.bit_count() for v in col_code))
            rw = [row.bit_count() for row in rows]
            cw = [col.bit_count() for col in columns]
            w = min(min(sum(rw[i] for i in range(3) if (v >> i) & 1) for v in row_code),
                    min(sum(cw[j] for j in range(4) if (v >> j) & 1) for v in col_code))
            row_ranks = [small_rank([r for i, r in enumerate(rows) if not (s >> i) & 1]) for s in range(8)]
            col_ranks = [small_rank([r & (15 ^ t) for r in rows]) for t in range(16)]
            brute_d, brute_w = 8, 13
            for s in range(8):
                for t in range(16):
                    kept = [r & (15 ^ t) for i, r in enumerate(rows) if not (s >> i) & 1]
                    joint = small_rank(kept)
                    self.assertEqual(joint == rank, row_ranks[s] == rank and col_ranks[t] == rank)
                    if joint < rank:
                        brute_d = min(brute_d, s.bit_count()+t.bit_count())
                        brute_w = min(brute_w, sum(rw)-sum(r.bit_count() for r in kept))
                    cases += 1
            self.assertEqual((d, w), (brute_d, brute_w))
        self.assertEqual(cases, 4095*128)

    def test_support_loss_is_not_a_rank_drop(self):
        rows = [3, 3]
        self.assertEqual(small_rank(rows), 1)
        self.assertEqual(small_rank(rows[1:]), 1)
        self.assertEqual(min(v.bit_count() for v in span([3])-{0}), 2)
        self.assertEqual(sum(r.bit_count() for r in rows), 4)

    def test_archive_corruption_rejected_by_both_engines(self):
        for name in ("verify.py", "independent.py"):
            with self.subTest(checker=name), tempfile.TemporaryDirectory() as temporary:
                folder = self.portable(temporary)
                source = folder / "inputs/PR1226-RESULTS.json"
                source.write_bytes(source.read_bytes()+b" ")
                result = self.run_script(folder, name)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source", result.stderr.lower())

    def test_model_corruption_rejected_by_weyl_engine(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = self.portable(temporary)
            path = folder / "generated/MODEL.json"
            data = json.loads(path.read_text())
            data["lines"][0][0] += 2
            path.write_text(json.dumps(data))
            result = self.run_script(folder, "independent.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Weyl root model disagreement", result.stderr)

    def test_false_threshold_table_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = self.portable(temporary)
            path = folder / "generated/THRESHOLDS.jsonl"
            lines = path.read_text().splitlines()
            row = json.loads(lines[0])
            row[2] = 19
            lines[0] = json.dumps(row)
            path.write_text("\n".join(lines)+"\n")
            result = self.run_script(folder, "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("threshold table changed", result.stderr)

    def test_existing_output_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "evidence"
            destination.mkdir()
            sentinel = destination / "retain.txt"
            sentinel.write_text("unchanged")
            result = self.run_script(HERE, "verify.py", "--write-directory", str(destination))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), "unchanged")
            self.assertEqual(list(destination.iterdir()), [sentinel])

    def test_relocated_optimized_both_engine_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = self.portable(temporary)
            for name in ("verify.py", "independent.py"):
                result = self.run_script(folder, name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("copy_drop=20 frame_change=4 even_loss=560", result.stdout)


if __name__ == "__main__":
    unittest.main()

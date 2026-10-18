#!/usr/bin/env python3
"""Behavioral, finite-oracle and real-CLI controls for the scoped result."""

import copy
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load_source(name):
    path = PACKAGE / (name + ".py")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


V = load_source("verify")
INDEPENDENT = load_source("independent")


def brute_full(rows, budget):
    """Literal pairs times all orders; no state-domain merging."""
    n = len(rows)
    choices = []
    for _p, q in rows:
        d = sum(1 << j for j in range(3) if q[j])
        local = []
        for a in range(1, 8):
            for b in range(1, 8):
                if b & ~d or (a & b).bit_count() % 2 == 0:
                    continue
                form_r = b == d or a == b and a in (1, 2, 4)
                if form_r or a == 7 and b in (1, 2, 4):
                    local.append((a, b, 0 if form_r else 1))
        choices.append(local)
    best = None
    for labels in itertools.product(*choices):
        price = sum(c for _a, _b, c in labels)
        if price > budget or best is not None and price >= best:
            continue
        for order in itertools.permutations(range(n)):
            valid = True
            for position, t in enumerate(order):
                for s in order[position + 1:]:
                    dot = sum(rows[t][0][j] * rows[s][1][j] for j in range(3))
                    if dot == 0 and (labels[t][0] & labels[s][1]).bit_count() % 2:
                        valid = False
            if valid:
                best = price
                break
    return best


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = V.decode(V.read_json(ROOT / V.SOURCE, 4096, V.SOURCE_SHA256))
        cls.receipt = V.read_json(PACKAGE / "RESULT.json")

    def test_exact_tiny_oracles(self):
        # Every three-line restriction, plus four representative four-line sets.
        domains = list(itertools.combinations(range(12), 3))
        domains += [(0, 1, 3, 6), (0, 3, 6, 9), (0, 1, 2, 11), (2, 5, 8, 10)]
        for indices in domains:
            rows = tuple(self.rows[t] for t in indices)
            for budget in (0, 1):
                with self.subTest(indices=indices, budget=budget):
                    answer = V.solve(rows, budget)["minimum"]
                    self.assertEqual(answer, brute_full(rows, budget))
            excluded, _counts = INDEPENDENT.reverse_exclusion(rows)
            self.assertEqual(excluded, V.solve(rows, 0)["minimum"] is None)

    def test_twelve_exact_obstructions_and_witnesses(self):
        actual = V.calculate(self.rows)
        self.assertEqual(actual, self.receipt)
        self.assertEqual([r["form_r_maximum"] for r in actual["records"]], [10] * 12)
        self.assertEqual([r["minimum_interior_for_eleven"] for r in actual["records"]],
                         [1] * 12)
        for record in actual["records"]:
            sub = tuple(self.rows[t] for t in record["indices"])
            self.assertEqual(INDEPENDENT.reverse_exclusion(sub)[0], True)
            INDEPENDENT.direct_replay(sub, record["extended"]["witness"], 1)

    def test_real_constraint_mutants(self):
        indices = self.receipt["records"][0]["indices"]
        rows = tuple(self.rows[t] for t in indices)
        original = V.advance
        try:
            # Actual weakened implementation ignores all future zero-arc obligations.
            def no_constraints(state, t, _a, _zeros):
                return tuple(0 if s == t else value for s, value in enumerate(state))
            V.advance = no_constraints
            self.assertEqual(V.solve(rows, 0)["minimum"], 0)
        finally:
            V.advance = original
        self.assertIsNone(V.solve(rows, 0)["minimum"])
        # Treating a new (111,e_c) label as old Form-R falsely admits eleven.
        original_pairs = V.local_pairs
        try:
            V.local_pairs = lambda q: tuple((a, b, 0) for a, b, _c in original_pairs(q))
            self.assertEqual(V.solve(rows, 0)["minimum"], 0)
        finally:
            V.local_pairs = original_pairs

    def test_invalid_witnesses(self):
        record = self.receipt["records"][0]
        rows = tuple(self.rows[t] for t in record["indices"])
        good = record["extended"]["witness"]
        INDEPENDENT.direct_replay(rows, good, 1)
        broken = []
        bad = copy.deepcopy(good)
        bad[0][1] = 0
        broken.append(bad)
        bad = copy.deepcopy(good)
        bad[0][2] = 7
        broken.append(bad)
        bad = copy.deepcopy(good)
        bad[0][0] = bad[1][0]
        broken.append(bad)
        broken.append(list(reversed(good)))
        for witness in broken:
            with self.assertRaises(ValueError):
                INDEPENDENT.direct_replay(rows, witness, 1)
        with self.assertRaises(ValueError):
            INDEPENDENT.direct_replay(rows, good, 0)

    def test_input_and_capacity_limits_fail_closed(self):
        for bad in ([], [[[True, 1, 1], [1, 1, 0]]], [[[1, 1, 1], [1, -1, 0]]],
                    [[[1, 1, 1], [1, 0, 0]]], [[[2, 1, 1], [1, 1, 0]]]):
            with self.assertRaises(ValueError):
                V.decode(bad)
        self.assertEqual(V.solve(self.rows[:3], 0)["minimum"], 0)
        with self.assertRaisesRegex(ValueError, "capacity exhausted"):
            V.solve(self.rows[:3], 0, capacity=1)
        for invalid in (-1, 2, True):
            with self.assertRaises(ValueError):
                V.solve(self.rows[:3], invalid)

    def run_cli(self, script, cwd, *arguments):
        return subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B",
                               str(script), *arguments], cwd=cwd, text=True,
                              capture_output=True, timeout=60, check=False)

    def test_real_cli_export_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research/fstar-one-interior-label"
            package.mkdir(parents=True)
            for name in ("verify.py", "independent.py", "RESULT.json"):
                shutil.copyfile(PACKAGE / name, package / name)
            source = root / V.SOURCE
            source.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / V.SOURCE, source)
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for script, marker in (("verify.py", "PASS_FSTAR_ONE_INTERIOR"),
                                   ("independent.py", "PASS_FSTAR_REVERSE_EXCLUSION")):
                run = self.run_cli(package / script, root)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn(marker, run.stdout)
            after = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            source.write_bytes(b"not JSON")
            run = self.run_cli(package / "verify.py", root)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source hash mismatch", run.stderr)
            source.write_bytes(before[source])
            result = package / "RESULT.json"
            bad = copy.deepcopy(self.receipt)
            bad["records"][0]["extended"]["minimum"] = True
            result.write_text(json.dumps(bad), encoding="utf-8")
            run = self.run_cli(package / "verify.py", root)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete receipt mismatch", run.stderr)
            result.write_text('{"schema_version":1,"schema_version":1}',
                              encoding="utf-8")
            run = self.run_cli(package / "verify.py", root)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("duplicate JSON key", run.stderr)

    def test_exclusive_output_and_json_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text("retained", encoding="utf-8")
            run = self.run_cli(PACKAGE / "verify.py", ROOT, "--write-result", str(path))
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(path.read_text(encoding="utf-8"), "retained")
            with self.assertRaisesRegex(ValueError, "size limit"):
                V.read_json(path, limit=1)
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonfinite"):
                V.read_json(path)


if __name__ == "__main__":
    unittest.main()

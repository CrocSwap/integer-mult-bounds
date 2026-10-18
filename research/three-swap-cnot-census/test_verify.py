"""Focused algebra, completeness-binding and isolated replay controls.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("three_swap_verify", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
independent = verify.load_independent()


def inverse(rows):
    work = [row | (1 << (3 + i)) for i, row in enumerate(rows)]
    for column in range(3):
        pivot = next(i for i in range(column, 3) if (work[i] >> column) & 1)
        work[column], work[pivot] = work[pivot], work[column]
        for i in range(3):
            if i != column and (work[i] >> column) & 1:
                work[i] ^= work[column]
    return tuple(row >> 3 for row in work)


class CensusTests(unittest.TestCase):
    def test_algebra_and_faithfulness(self):
        tables = verify.to_regular_tables()
        for g in range(6):
            for h in range(6):
                x, y = 1 << g, 1 << h  # (0,0) matrix entry only
                self.assertEqual(
                    verify.to_regular(verify.formal_product(x, y), tables),
                    independent.multiply(verify.to_regular(x, tables),
                                         verify.to_regular(y, tables)))
        for g in (verify.A, verify.B):
            for u, v in verify.PROJECTORS:
                f = verify.factor(g, u, v)
                self.assertEqual(verify.formal_product(f, f), verify.IDENTITY)
        images = {verify.to_regular(1 << bit, tables) for bit in range(54)}
        self.assertEqual(len(images), 54)
        self.assertNotIn(0, images)
        self.assertEqual(len(verify.controls(independent, tables)), 25)

    def test_scalar_normalization_inventory(self):
        all_n = {rows for rows, _, _ in independent.scalar_idempotents()}
        direct_n = {tuple(v if (u >> i) & 1 else 0 for i in range(3))
                    for u, v in verify.PROJECTORS}
        self.assertEqual(all_n, direct_n)
        gl = [rows for rows in itertools.product(range(8), repeat=3)
              if independent.rank(rows) == 3]
        self.assertEqual(len(gl), 168)
        checks = 0
        for basis in gl:
            inv = inverse(basis)
            self.assertEqual(independent.small_product(basis, inv), (1, 2, 4))
            for n in all_n:
                conjugate = independent.small_product(
                    independent.small_product(basis, n), inv)
                self.assertIn(conjugate, all_n)
                checks += 1
        self.assertEqual(checks, 4704)

    def test_optimized_formal_steps_on_complete_linear_basis(self):
        tables = verify.transition_tables()
        factors = [verify.factor(g, u, v) for g in (verify.A, verify.B)
                   for u, v in verify.PROJECTORS]
        checks = 0
        # Both maps are F2-linear in the current formal matrix; these 54
        # input vectors span every possible current matrix, including dirty ones.
        for bit in range(54):
            state = 1 << bit
            for table, factor in zip(tables, factors, strict=True):
                self.assertEqual(verify.apply_table(state, table),
                                 verify.formal_product(state, factor))
                checks += 1
        self.assertEqual(checks, 3024)
        for swaps in range(4):
            for bit in range(54):
                state = 1 << bit
                self.assertEqual(verify.right_target(state, swaps),
                                 verify.formal_product(state, verify.diagonal_target(swaps)))

    def test_full_state_set_guard(self):
        tables = verify.to_regular_tables()
        identity = verify.to_regular(verify.IDENTITY, tables)
        verify.same_states({verify.IDENTITY}, {identity}, tables)
        with self.assertRaisesRegex(ValueError, "cardinality"):
            verify.same_states({verify.IDENTITY}, set(), tables)
        with self.assertRaisesRegex(ValueError, "full state sets"):
            verify.same_states({verify.IDENTITY}, {identity ^ 1}, tables)

    def test_receipt_mutations(self):
        good = json.loads((PACKAGE / "EXPECTED.json").read_text())
        verify.compare_receipt(good, copy.deepcopy(good))
        for key in ("minimum_paid_calls", "registers", "exact_distance_layers",
                    "target_intersections_by_left_distance",
                    "formal_layer_sha256_7byte_little_endian", "semantic_controls"):
            bad = copy.deepcopy(good)
            del bad[key]
            with self.assertRaisesRegex(ValueError, "receipt differs"):
                verify.compare_receipt(good, bad)

    def test_live_source_rejection(self):
        manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
        inputs = [item for item in manifest["files"] if item["usage"] == "input"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for item in inputs:
                p = root / item["path"]
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((verify.ROOT / item["path"]).read_bytes())
            with patch.object(verify, "ROOT", root):
                verify.check_inputs()
                p = root / inputs[0]["path"]
                p.write_bytes(p.read_bytes() + b"\nchanged-source\n")
                with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                    verify.check_inputs()

    def test_isolated_optimized_readonly_replay_and_bad_receipt(self):
        manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for item in manifest["files"]:
                if item["usage"] == "input":
                    dest = root / item["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.ROOT / item["path"], dest)
            files = [p for p in root.rglob("*") if p.is_file()]
            directories = [p for p in root.rglob("*") if p.is_dir()]
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            try:
                for p in files:
                    p.chmod(0o444)
                for p in directories:
                    p.chmod(0o555)
                passed = subprocess.run(command, cwd=root, capture_output=True,
                                        text=True, timeout=120, check=False)
                self.assertEqual(passed.returncode, 0, passed.stderr)
                self.assertIn("minimum=9 registers=3", passed.stdout)
            finally:
                for p in directories:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)
            expected = package / "EXPECTED.json"
            corrupt = json.loads(expected.read_text())
            corrupt["minimum_paid_calls"] = 7
            expected.write_text(json.dumps(corrupt))
            rejected = subprocess.run(command, cwd=root, capture_output=True,
                                      text=True, timeout=120, check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("receipt differs", rejected.stderr)
            self.assertEqual(list(root.rglob("__pycache__")), [])


if __name__ == "__main__":
    unittest.main()

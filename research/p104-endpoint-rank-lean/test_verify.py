"""Semantic, source-binding, and read-only controls for the endpoint-rank lemma."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import permutations, product
from pathlib import Path

import verify as V


def literal_frame(vectors, n):
    """Separate row-based execution of the retained unsigned P/D/C definition."""
    if not vectors:
        return V.identity(2 * n)
    if len(vectors) == n:
        return V.identity(n) + tuple((1 << i) | (1 << (n + i)) for i in range(n))
    columns = list(vectors)
    for unit in V.identity(n):
        if V.binary_rank(columns + [unit]) > len(columns):
            columns.append(unit)
    rows = [
        sum(((column >> i) & 1) << j for j, column in enumerate(columns))
        | (1 << (n + i))
        for i in range(n)
    ]
    for bit in range(n):
        pivot = next(i for i in range(bit, n) if (rows[i] >> bit) & 1)
        rows[bit], rows[pivot] = rows[pivot], rows[bit]
        for i in range(n):
            if i != bit and (rows[i] >> bit) & 1:
                rows[i] ^= rows[bit]
    inverse_rows = tuple(row >> n for row in rows)
    inverse_columns = tuple(
        sum(((row >> j) & 1) << i for i, row in enumerate(inverse_rows))
        for j in range(n)
    )
    quadratic = tuple(
        (1 << i)
        ^ sum(((a & b).bit_count() % 2) << j for j, b in enumerate(inverse_columns))
        for i, a in enumerate(inverse_columns)
    )
    mask = (1 << n) - 1
    output = []
    for bit in range(2 * n):
        x, z = (1 << bit) & mask, (1 << bit) >> n
        # Adjoint chart: D^-1 then P^-1. Signs disappear only in binary action.
        z ^= sum(((row & x).bit_count() % 2) << i for i, row in enumerate(quadratic))
        x = sum(((row & x).bit_count() % 2) << i for i, row in enumerate(inverse_rows))
        z = sum(((column & z).bit_count() % 2) << i for i, column in enumerate(columns))
        x ^= z & ((1 << len(vectors)) - 1)
        # Forward chart: P then D.
        x = V.image(columns, x)
        z = sum(
            ((column & z).bit_count() % 2) << i
            for i, column in enumerate(inverse_columns)
        )
        z ^= sum(((row & x).bit_count() % 2) << i for i, row in enumerate(quadratic))
        output.append(x | (z << n))
    return tuple(output)


class EndpointRankTests(unittest.TestCase):
    def test_literal_gate_semantics(self):
        cases = 0
        for n in range(1, 4):
            for rank in range(n + 1):
                for vectors in permutations(range(1, 1 << n), rank):
                    if V.binary_rank(vectors) == rank:
                        self.assertEqual(V.frame(vectors, n), literal_frame(vectors, n))
                        cases += 1
        self.assertEqual(cases, 2 + 10 + 218)

    def test_all_consumed_frames(self):
        word = V.read_json(V.PACKAGE / "inputs/PR2586-WORD.json")
        runs = V.endpoint_runs(word)
        frames = {
            tuple(frame)
            for run in runs
            for index in run["events"]
            for frame in word["program"][index][2:4]
        }
        for frame in frames:
            self.assertEqual(V.frame(frame), literal_frame(frame, 9))
        self.assertEqual(len(frames), 338)

    def test_arbitrary_matrix_bound_and_cancellation(self):
        matrices = list(product(range(4), repeat=2))
        for left in matrices:
            for right in matrices:
                self.assertLessEqual(
                    V.mixing_rank(V.multiply(left, right), 1),
                    V.mixing_rank(left, 1) + V.mixing_rank(right, 1),
                )
        child = (1, 3)
        self.assertEqual(V.mixing_rank(child, 1), 1)
        self.assertEqual(V.multiply(child, child), (1, 2))
        self.assertEqual(V.mixing_rank(V.multiply(child, child), 1), 0)

    def test_source_read_barrier_and_invoice(self):
        word = V.read_json(V.PACKAGE / "inputs/PR2586-WORD.json")
        runs = V.endpoint_runs(word)
        y0 = next(r for r in runs if r["role"] == "Y0" and r["side"] == "entry")
        self.assertEqual(word["program"][y0["barrier"]][2], "Y0")
        self.assertEqual(len(y0["events"]), 1)
        pair = next(r for r in runs if len(r["events"]) == 2)
        bad = copy.deepcopy(word)
        bad["program"][pair["events"][1]][2] = []
        with self.assertRaisesRegex(ValueError, "run frame continuity"):
            V.endpoint_runs(bad)
        bad = copy.deepcopy(word)
        edge = next(i for i in pair["events"] if bad["program"][i][4] > 1)
        bad["program"][edge][4] = 1
        with self.assertRaisesRegex(ValueError, "individual child rank"):
            V.endpoint_runs(bad)

    def test_frame_boundaries(self):
        for n in range(1, 10):
            self.assertEqual(V.mixing_rank(V.frame((), n), n), 0)
            self.assertEqual(V.mixing_rank(V.frame(V.identity(n), n), n), n)
        for vectors in ((True,), (0,), (512,), (1, 1)):
            with self.assertRaises(ValueError):
                V.frame(vectors)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"rank":1,"rank":0}', object_pairs_hook=V.unique_object)

    def test_export_sources_receipt_and_output(self):
        with tempfile.TemporaryDirectory(prefix="endpoint-rank-export-") as directory:
            root = Path(directory)
            package = root / "research" / V.PACKAGE.name
            shutil.copytree(
                V.PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__")
            )
            for item in V.read_json(V.PACKAGE / "SOURCES.json")["files"]:
                if item["usage"] == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V.ROOT / item["path"], target)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=60, check=False
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("runs=416 rank_mass=928", result.stdout)
            self.assertEqual(
                before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            )
            self.check_export_faults(root, package, command)

    def check_export_faults(self, root, package, command):
        targets = (
            (
                root / "research/p104-native-channel/vendor/native_verify.py",
                "live source SHA256",
            ),
            (package / "inputs/PR2586-WORD.json", "predecessor SHA256"),
        )
        for path, message in targets:
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=60, check=False
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)
            path.write_bytes(original)
        receipt = package / "RESULT.json"
        bad = json.loads(receipt.read_text())
        bad["schema_version"] = True
        receipt.write_text(json.dumps(bad))
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=60, check=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("typed receipt", result.stderr)
        output = root / "exclusive.json"
        output.write_text("keep")
        result = subprocess.run(
            command + ["--out", str(output)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)
        self.assertEqual(output.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()

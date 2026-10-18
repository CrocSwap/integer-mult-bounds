"""Independent rational oracles and failure controls for the opt-in kernel."""
import copy
from fractions import Fraction
import gzip
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closure
import run


def rational_rank(rows):
    """Fraction Gauss-Jordan rank; no modular arithmetic or kernel imports."""
    if not rows:
        return 0
    matrix = [list(map(Fraction, row)) for row in rows]
    rank = 0
    for j in range(len(matrix[0])):
        candidates = [i for i in range(rank, len(matrix)) if matrix[i][j]]
        if not candidates:
            continue
        i = candidates[0]
        matrix[rank], matrix[i] = matrix[i], matrix[rank]
        divisor = matrix[rank][j]
        matrix[rank] = [x / divisor for x in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank:
                factor = matrix[i][j]
                matrix[i] = [x - factor*y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def oracle(lines, mask):
    if mask == 0:
        return (0, 0)
    selected = [row for i, row in enumerate(lines) if mask >> i & 1]
    rank = rational_rank(selected)
    closed = sum(1 << i for i, row in enumerate(lines)
                 if rational_rank(selected + [row]) == rank)
    return closed, rank


class ClosureTests(unittest.TestCase):
    def test_all_512_small_masks_against_rational_rank(self):
        lines = [(0, 0, 0), (2, 0, 0), (-1, 0, 0), (0, -3, 0),
                 (1, 1, 0), (0, 0, 2), (1, 0, 1), (0, 1, -1), (2, -2, 2)]
        cache = {}
        close = closure.make_close(lines, len(lines), cache)
        for mask in range(1 << len(lines)):
            self.assertEqual(close(mask), oracle(lines, mask), mask)
        self.assertEqual(len(cache), 512)

    def test_pivot_order_and_nonunit_coefficients(self):
        lines = [(0, 0, -2), (0, 3, 1), (-2, 1, 1), (2, -1, -1)]
        for ordering in itertools.permutations(lines):
            close = closure.make_close(ordering, len(ordering), {})
            for mask in range(16):
                self.assertEqual(close(mask), oracle(ordering, mask))

    def test_seed93_live_root_masks_against_rational_rank(self):
        word = json.loads(gzip.decompress((run.ROOT / run.TUNED).read_bytes()))
        lines = word["lines"]
        rng = random.Random(93)
        close = closure.make_close(lines, len(lines), {})
        masks = [1 << i for i in range(len(lines))]
        masks += [sum(1 << i for i in rng.sample(range(len(lines)), j % 11))
                  for j in range(93)]
        for mask in masks:
            self.assertEqual(close(mask), oracle(lines, mask), mask)

    def test_bad_domains_and_modular_alias_guard(self):
        bad = [([], 0, {}, "line count"), ([[1], [1, 2]], 2, {}, "rectangular"),
               ([[1.0]], 1, {}, "integer"), ([[1]], 2, {}, "line count"),
               ([[1]], 1, {0: (0, 0)}, "fresh"),
               ([[closure.PRIME, 0], [0, 1]], 2, {}, "Hadamard")]
        for lines, count, cache, error in bad:
            with self.assertRaisesRegex(ValueError, error):
                closure.make_close(lines, count, cache)
        close = closure.make_close([[1, 0], [0, 1]], 2, {})
        for mask in (-1, 4, 1.5):
            with self.assertRaisesRegex(ValueError, "line mask"):
                close(mask)
        self.assertEqual(rational_rank([[closure.PRIME, 0]]), 1)
        self.assertEqual(len(closure.echelon([[closure.PRIME, 0]], 2)), 0)

    def test_wrong_membership_and_lost_pivot_are_detected(self):
        lines = [(2, 0), (1, 0), (0, 1)]
        def compare(mask):
            actual = closure.make_close(lines, 3, {})(mask)
            closure.require(actual == oracle(lines, mask), "mathematical mismatch")
        for answer in (True, False):
            with patch.object(closure, "contains", return_value=answer):
                with self.assertRaisesRegex(ValueError, "mathematical mismatch"):
                    compare(1)
        original = closure.echelon
        with patch.object(closure, "echelon", side_effect=lambda rows, width: original(rows, width)[:-1]):
            with self.assertRaisesRegex(ValueError, "mathematical mismatch"):
                compare(5)

    def test_cache_is_word_local_and_coordinates_are_copied(self):
        lines = [[1, 0], [0, 1], [1, 0]]
        first = closure.make_close(lines, 3, {})
        lines[2][:] = [0, 1]
        second = closure.make_close(lines, 3, {})
        self.assertEqual(first(1), (5, 1))
        self.assertEqual(second(1), (1, 1))

    def test_all_input_pins_and_inventory_fail_closed(self):
        pins = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="closure-pins-") as temp:
            root = Path(temp)
            for path in run.INPUTS:
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((run.ROOT / path).read_bytes())
            run.check_sources(root, pins)
            for path in sorted(run.INPUTS):
                destination = root / path
                saved = destination.read_bytes()
                destination.write_bytes(saved + b"corruption")
                with self.assertRaisesRegex(ValueError, "source digest"):
                    run.check_sources(root, pins)
                destination.write_bytes(saved)
            destination.unlink()
            with self.assertRaisesRegex(ValueError, "missing input"):
                run.check_sources(root, pins)
        for mutation in ("missing", "duplicate"):
            bad = copy.deepcopy(pins)
            row = next(r for r in bad["files"] if r["usage"] == "input")
            if mutation == "missing":
                bad["files"].remove(row)
            else:
                bad["files"].append(row)
            with self.assertRaisesRegex(ValueError, "exact input inventory"):
                run.check_sources(pins=bad)

    def test_adapter_anchor_and_inherited_assertions(self):
        source = (run.ROOT / run.CHECKER).read_text()
        for changed in (source.replace("def close(m):", "def renamed(m):"),
                        source + "\ndef close(m): return (m, 0)\n"):
            with self.assertRaisesRegex(ValueError, "unique close function"):
                run.program(changed, "test.py", "basis")
        small = "L=[[1]]\nV=1\n_close={}\ndef close(m): return (m, m)\nassert False, 'retained assertion'\n"
        for engine in ("reference", "basis"):
            with self.assertRaisesRegex(AssertionError, "retained assertion"):
                exec(run.program(small, "test.py", engine), {"_make_close": closure.make_close})
        p = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "run.py")],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("inherited checker requires assertions", p.stderr)

    def test_benchmark_code_and_coverage_bindings(self):
        import verify
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        evidence = json.loads((HERE / "BENCHMARK.json").read_text())
        verify.check_benchmark(expected, evidence)
        for label in ("source", "receipt", "coverage", "median"):
            bad = copy.deepcopy(evidence)
            if label == "source":
                bad["implementation_sha256"]["closure.py"] = "0" * 64
            elif label == "receipt":
                bad["samples"][0]["engines"]["basis"]["cases"]["pr589"]["report_sha256"] = "0" * 64
            elif label == "coverage":
                del bad["samples"][0]["engines"]["basis"]["cases"]["degraded"]
            else:
                bad["median_suite_seconds"]["basis"] *= 2
            with self.assertRaisesRegex(ValueError, "benchmark"):
                verify.check_benchmark(expected, bad)


if __name__ == "__main__":
    unittest.main()

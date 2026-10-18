#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Small exact census controls using an independent dense-matrix oracle."""

from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
import io
from itertools import product
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load_module(name, source=None):
    module = types.ModuleType("compact_" + name + "_control")
    module.__file__ = str(HERE / (name + ".py"))
    body = (HERE / (name + ".py")).read_bytes() if source is None else source
    exec(compile(body, module.__file__, "exec"), module.__dict__)
    return module


def multiply(left, right):
    """Ordinary dense GF(2) multiplication, supplied as the kernel callback."""
    width = len(left)
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(width)) % 2
                       for j in range(width)) for i in range(width))


def pack(matrix):
    return sum(value << index for index, value in enumerate(
        entry for row in matrix for entry in row))


def triple(left, middle, right):
    """Direct three-factor formula, without invoking the callback above."""
    width = len(left)
    return tuple(tuple(sum(left[i][j] * middle[j][k] * right[k][ell]
                           for j in range(width) for k in range(width)) % 2
                       for ell in range(width)) for i in range(width))


def oracle(matrices):
    n = len(matrices)
    products = {word: triple(*(matrices[index] for index in word))
                for word in product(range(n), repeat=3)}
    multiplicities = Counter(products[word] for word in products
                             if word[0] != word[1] and word[1] != word[2])
    histogram = Counter(multiplicities.values())
    # Enumerate words directly, rather than reconstructing ordered pairs from
    # product classes. This independently checks reversal and cyclic filtering.
    relations = {word for word in product(range(n), repeat=6)
                 if all(word[i] != word[(i + 1) % 6] for i in range(6))
                 and products[word[:3]] == products[word[5:2:-1]]}
    return sum(multiplicities.values()), histogram, relations


IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
SWAP01 = ((0, 1, 0), (1, 0, 0), (0, 0, 1))
SWAP12 = ((1, 0, 0), (0, 0, 1), (0, 1, 0))
CYCLE = ((0, 1, 0), (0, 0, 1), (1, 0, 0))


class Controls(unittest.TestCase):
    def setUp(self):
        self.kernel = load_module("kernel")

    def census(self, matrices):
        actual = self.kernel.relation_census(matrices, multiply, pack)
        self.assertIsInstance(actual, tuple)
        self.assertIsInstance(actual[1], Counter)
        self.assertIsInstance(actual[2], set)
        self.assertEqual(actual, oracle(matrices))
        return actual

    def test_empty_and_single_matrix(self):
        for matrices in ([], [IDENTITY]):
            with self.subTest(length=len(matrices)):
                self.assertEqual(self.census(matrices), (0, Counter(), set()))

    def test_large_collision_class_and_all_orientations(self):
        total, histogram, relations = self.census([IDENTITY] * 3)
        self.assertEqual(total, 12)
        self.assertEqual(histogram, Counter({12: 1}))
        # Proper colorings of the six-cycle with three labels: 2^6 + 2.
        self.assertEqual(len(relations), 66)
        self.assertIn((0, 1, 0, 1, 0, 1), relations)
        self.assertIn((1, 0, 1, 0, 1, 0), relations)
        # Equal triple products alone do not permit a repeated cyclic endpoint.
        self.assertNotIn((0, 1, 0, 1, 2, 0), relations)
        self.assertNotIn((0, 1, 0, 0, 1, 0), relations)

    def test_distinct_noncommuting_involutions(self):
        self.assertNotEqual(multiply(SWAP01, SWAP12), multiply(SWAP12, SWAP01))
        self.census([IDENTITY, SWAP01, SWAP12])

    def test_duplicate_labels_in_multiple_product_classes(self):
        _, histogram, _ = self.census([IDENTITY, IDENTITY, SWAP01, SWAP12])
        self.assertGreater(sum(histogram.values()), 2)
        self.assertTrue(any(size >= 3 for size in histogram))

    def test_callback_order_without_involution_assumption(self):
        self.assertNotEqual(multiply(CYCLE, CYCLE), IDENTITY)
        self.census([IDENTITY, SWAP01, CYCLE, SWAP12])

    def test_word_code_domain_and_leading_zero_digits(self):
        for base in (1, 2, 5):
            for word in product(range(base), repeat=3):
                code = (word[0] * base + word[1]) * base + word[2]
                self.assertEqual(self.kernel.decode_word(code, base), word)
        for code, base in ((0, 0), (-1, 2), (8, 2), (0, -1), (True, 2)):
            with self.subTest(code=code, base=base), self.assertRaises(ValueError):
                self.kernel.decode_word(code, base)
        # Code zero is valid for the storage helper, but cannot occur among
        # reduced triples. This checks the actual helper boundary, not a
        # purported zero-code case in the canonical census.
        classes = self.kernel.CompactClasses(2)
        classes.add(7, 0)
        classes.add(7, 2)
        self.assertEqual(classes.classes[7], [0, 2])
        self.assertEqual(classes.finish(), (2, Counter({2: 1}), set()))

    def test_exact_matrix_keys_despite_equal_python_hashes(self):
        first, second = 7, 7 + sys.hash_info.modulus
        self.assertNotEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        classes = self.kernel.CompactClasses(2)
        for key, code in ((first, 0), (second, 1), (first, 2), (second, 3)):
            classes.add(key, code)
        self.assertEqual(classes.classes, {first: [0, 2], second: [1, 3]})
        self.assertEqual(classes.finish(), (4, Counter({2: 2}), set()))

    def test_dropped_first_collision_member_mutant_is_detected(self):
        source = (HERE / "kernel.py").read_text()
        target = "words = [previous, code]"
        self.assertEqual(source.count(target), 1)
        mutant = load_module("kernel", source.replace(target, "words = [code]"))
        matrices = [IDENTITY] * 3
        self.assertNotEqual(mutant.relation_census(matrices, multiply, pack), oracle(matrices))

    def test_word_code_alias_mutant_is_detected(self):
        source = (HERE / "kernel.py").read_text()
        target = "prefix + c"
        self.assertEqual(source.count(target), 1)
        mutant = load_module("kernel", source.replace(target, "(prefix + c) % (n * n)"))
        matrices = [IDENTITY] * 3
        actual = mutant.relation_census(matrices, multiply, pack)
        expected = oracle(matrices)
        self.assertEqual(actual[:2], expected[:2])
        self.assertNotEqual(actual[2], expected[2])

    def test_reference_source_authenticated_before_execution(self):
        worker = load_module("worker")
        inputs = [row for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]
                  if row["usage"] == "input"]
        target = worker.REFERENCE + "/verify.py"
        self.assertIn(target, [row["path"] for row in inputs])
        with tempfile.TemporaryDirectory(prefix="fano-source-control-") as directory:
            root = Path(directory)
            for row in inputs:
                path = root / row["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                original = HERE.parents[1] / row["path"]
                if row["path"] == target:
                    path.write_bytes(original.read_bytes() +
                                     b"\nraise RuntimeError('UNAUTHENTICATED_CODE_EXECUTED')\n")
                else:
                    path.symlink_to(original)
            with self.assertRaisesRegex(ValueError, "source hash: .*verify.py"):
                worker.load_reference(root)

    def test_full_receipt_mismatch_and_patch_restoration(self):
        worker = load_module("worker")
        reference = types.SimpleNamespace()
        original = lambda _matrices: (0, Counter(), set())
        reference.relation_census = original
        reference.canonical = lambda value: json.dumps(value, sort_keys=True).encode()

        def build():
            total, sizes, relations = reference.relation_census([])
            return {"reduced_triples": total, "class_size_histogram": dict(sizes),
                    "cyclic_length6_relation_words_with_symmetry": len(relations)}

        reference.build = build
        with self.assertRaisesRegex(ValueError, "complete canonical receipt mismatch"):
            worker.full_build(reference, b"wrong receipt", original)
        self.assertIs(reference.relation_census, original)
        expected = reference.canonical(build())
        self.assertEqual(worker.full_build(reference, expected, original)["receipt_bytes"], len(expected))
        self.assertIs(reference.relation_census, original)

    def test_optional_rowtable_composition(self):
        worker = load_module("worker")
        tables = worker.load_rowtables()
        matrices = [IDENTITY, IDENTITY, SWAP01, SWAP12]
        lifted = [tuple(sum(value << j for j, value in enumerate(row)) for row in matrix)
                  + tuple(1 << i for i in range(3, 17)) for matrix in matrices]
        expected = oracle(matrices)
        self.assertEqual(tables.relation_census(lifted), expected)
        self.assertEqual(worker.rowtable_compact(lifted, tables), expected)

    def test_optional_source_authenticated_before_execution(self):
        worker = load_module("worker")
        with tempfile.TemporaryDirectory(prefix="fano-rowtable-control-") as directory:
            path = Path(directory) / "tampered.py"
            path.write_bytes((HERE / "inputs/pr3219-kernel.py").read_bytes() +
                             b"\nraise RuntimeError('UNAUTHENTICATED_OPTIONAL_CODE_EXECUTED')\n")
            with self.assertRaisesRegex(ValueError, "optional row-table source hash"):
                worker.load_rowtables(path)

    def test_benchmark_balanced_order_and_complete_receipt(self):
        benchmark = load_module("benchmark")
        self.assertEqual(benchmark.mode_order(0), benchmark.MODES)
        self.assertEqual(benchmark.mode_order(1), tuple(reversed(benchmark.MODES)))
        self.assertEqual(benchmark.mode_order(2), benchmark.MODES)
        receipt = {"receipt_sha256": "a" * 64, "census_sha256": "b" * 64,
                   "receipt_bytes": 100, "reduced_triples": 12,
                   "class_size_histogram": {"12": 1}, "relation_words": 66}
        encoded = json.dumps({"mode": "compact", **receipt})
        self.assertEqual(benchmark.parse_receipt(encoded, "compact"), receipt)
        for bad in (json.dumps({"mode": "compact"}),
                    json.dumps({"mode": "compact", **receipt, "extra": 1}),
                    json.dumps({"mode": "compact", **receipt, "census_sha256": "bad"}),
                    encoded + "\nextra output"):
            with self.subTest(receipt=bad), self.assertRaises(ValueError):
                benchmark.parse_receipt(bad, "compact")
        with self.assertRaisesRegex(ValueError, "worker mode"):
            benchmark.parse_receipt(encoded, "baseline")

    def test_benchmark_timeout_kills_and_reaps_entire_worker_group(self):
        benchmark = load_module("benchmark")
        process = mock.Mock(pid=4321)
        process.communicate.side_effect = [benchmark.subprocess.TimeoutExpired(["worker"], 0.01),
                                           ("", "")]
        with mock.patch.object(benchmark.subprocess, "Popen", return_value=process) as launch, \
                mock.patch.object(benchmark.os, "killpg") as kill:
            with self.assertRaisesRegex(TimeoutError, "complete worker timed out"):
                benchmark.run_sample("compact", 0.01)
        self.assertTrue(launch.call_args.kwargs["start_new_session"])
        kill.assert_called_once_with(4321, benchmark.signal.SIGKILL)
        self.assertEqual(process.communicate.call_count, 2)

    def test_benchmark_rejects_cross_worker_census_change(self):
        benchmark = load_module("benchmark")
        samples = [{"mode": "baseline", "receipt": {"census_sha256": "a" * 64},
                    "elapsed_seconds": 1, "peak_rss_kib": 1},
                   {"mode": "compact", "receipt": {"census_sha256": "b" * 64},
                    "elapsed_seconds": 1, "peak_rss_kib": 1}]
        with mock.patch.object(benchmark, "source_hashes", return_value={}), \
                mock.patch.object(benchmark, "run_sample", side_effect=samples) as run, \
                mock.patch.object(benchmark, "TIME", types.SimpleNamespace(is_file=lambda: True)), \
                mock.patch.object(benchmark.platform, "system", return_value="Linux"), \
                mock.patch.object(benchmark.platform, "python_implementation", return_value="CPython"), \
                redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, "receipt or census differs"):
                benchmark.benchmark(repetitions=1)
        self.assertEqual(run.call_count, 2)

    def test_benchmark_refuses_existing_output_before_work(self):
        benchmark = load_module("benchmark")
        with tempfile.TemporaryDirectory(prefix="fano-output-control-") as directory:
            output = Path(directory) / "retained.json"
            output.write_bytes(b"retained evidence\n")
            with mock.patch.object(sys, "argv", ["benchmark.py", "--output", str(output)]), \
                    mock.patch.object(benchmark, "benchmark") as run, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as stopped:
                    benchmark.main()
            self.assertEqual(stopped.exception.code, 2)
            run.assert_not_called()
            self.assertEqual(output.read_bytes(), b"retained evidence\n")


if __name__ == "__main__":
    unittest.main()

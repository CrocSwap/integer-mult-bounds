"""Complete consumer conformance, produced by Nick Petalas. Apache-2.0."""

import hashlib
import io
import itertools
import json
from pathlib import Path
import runpy
import shutil
import tempfile
from types import SimpleNamespace
import unittest

adapter = SimpleNamespace(**runpy.run_path(str(Path(__file__).with_name("adapter.py"))))


def snapshot(matrix):
    return tuple(map(tuple, matrix))


def reached_conformance():
    counts = {"calls": 0, "old_products": 0, "new_products": 0}
    shapes = {}
    trace = hashlib.sha256()

    def observe(original):
        def checked(a, b):
            before = snapshot(a), snapshot(b)
            expected = original(a, b)
            actual = adapter.multiply(a, b)
            adapter.require(actual == expected, "reached product mismatch")
            adapter.require(before == (snapshot(a), snapshot(b)), "input was modified")
            shape = (len(a), len(b), len(b[0]))
            adapter.require(all(1 <= n <= 11 for n in shape), "unexpected caller size")
            key = "x".join(map(str, shape))
            shapes[key] = shapes.get(key, 0) + 1
            counts["calls"] += 1
            counts["old_products"] += len(a) * len(b) * len(b[0])
            counts["new_products"] += sum(bool(x) for row in a for x in row) * len(b[0])
            trace.update(adapter.canonical([a, b, actual]))
            return actual
        return checked

    result = adapter.scientific(observer=observe)
    adapter.require(counts == {"calls": 16294, "old_products": 562574,
                               "new_products": 307264}, "reached coverage changed")
    return {**counts, "shapes": shapes, "trace_sha256": trace.hexdigest(),
            "scientific_sha256": hashlib.sha256(adapter.canonical(result)).hexdigest()}


def finite_conformance():
    source = adapter.source_bytes()
    reference = adapter.load_module("check_dense", source).multiply
    matrices = [list(map(list, (values[:2], values[2:])))
                for values in itertools.product((-1, 0, 1), repeat=4)]
    count = 0
    for a in matrices:
        for b in matrices:
            before = snapshot(a), snapshot(b)
            adapter.require(adapter.multiply(a, b) == reference(a, b), "finite mismatch")
            adapter.require(before == (snapshot(a), snapshot(b)), "finite input changed")
            count += 1
    for rows, inner, columns in itertools.product(range(1, 5), repeat=3):
        a = [[(i + 2 * k) % 5 - 2 for k in range(inner)] for i in range(rows)]
        b = [[(3 * k - j) % 7 - 3 for j in range(columns)] for k in range(inner)]
        adapter.require(adapter.multiply(a, b) == reference(a, b), "rectangular mismatch")
        count += 1
    adapter.require(adapter.multiply([], [[1]]) == [], "empty-output boundary")
    return count + 1


def rejection_controls():
    rejected = 0
    sources = adapter.source_bytes()
    with tempfile.TemporaryDirectory(prefix="dirty-phase-source-") as name:
        root = Path(name)
        shutil.copytree(adapter.ROOT / adapter.SOURCE, root / adapter.SOURCE,
                        ignore=shutil.ignore_patterns("__pycache__"))
        for relative, original in sources.items():
            path = root / relative
            path.write_bytes(original + b"\nchanged\n")
            try:
                adapter.source_bytes(root)
            except ValueError as error:
                adapter.require("mismatch" in str(error), "wrong source rejection")
                rejected += 1
            else:
                raise ValueError("changed source accepted")
            path.write_bytes(original)
        (root / (adapter.SOURCE + "verify.py")).unlink()
        try:
            adapter.source_bytes(root)
        except FileNotFoundError:
            rejected += 1
        else:
            raise ValueError("missing source accepted")
    try:
        adapter.load_module("unknown", sources)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("unknown entry accepted")
    return rejected


def kernel_controls():
    # Each real arithmetic fault must disagree on a concrete supported input.
    fixtures = [([[-2]], [[3]]), ([[0, 1]], [[5], [7]]),
                ([[1, 2]], [[3, 4], [5, 6]]), ([[1]], [[-1]])]
    wrong = [lambda a, b: [[0]],
             lambda a, b: [[a[0][0] * b[0][0]]],
             lambda a, b: [[sum(a[0][k] * b[j][k] for k in range(2))
                             for j in range(2)]],
             lambda a, b: [[abs(a[0][0] * b[0][0])]]]
    for fault, (a, b) in zip(wrong, fixtures, strict=True):
        adapter.require(fault(a, b) != adapter.multiply(a, b), "kernel fault hidden")
    complete_faults = [
        lambda a, b: [[0 for _ in row] for row in adapter.multiply(a, b)],
        lambda a, b: [[-x for x in row] for row in adapter.multiply(a, b)],
        lambda a, b: adapter.multiply([[max(x, 0) for x in row] for row in a], b),
        lambda a, b: [row[::-1] for row in adapter.multiply(a, b)],
    ]
    for fault in complete_faults:
        try:
            adapter.scientific(observer=lambda original: fault)
        except ValueError as error:
            adapter.require("dense normal-form disagreement" in str(error),
                            "wrong complete-consumer rejection")
        else:
            raise ValueError("faulty complete consumer accepted")
    return len(wrong) + len(complete_faults)


def retained_tests():
    sources = adapter.source_bytes()
    module = adapter.load_module("test_package", sources)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    adapter.require(result.wasSuccessful() and result.testsRun == 6,
                    "retained package tests failed:\n" + stream.getvalue())
    return result.testsRun


def main():
    reached = reached_conformance()
    baseline = adapter.scientific(baseline=True)
    candidate = adapter.scientific()
    adapter.require(adapter.canonical(baseline) == adapter.canonical(candidate),
                    "complete scientific output differs")
    result = {"status": "PASS_DIRTY_PHASE_ROW_PRODUCTS", "reached": reached,
              "finite_cases": finite_conformance(),
              "source_rejections": rejection_controls(),
              "kernel_rejections": kernel_controls(), "retained_tests": retained_tests()}
    paths = sorted(adapter.HERE.iterdir())
    result["package_sha256"] = {p.name: hashlib.sha256(adapter.bounded_read(p)).hexdigest()
                                for p in paths if p.is_file()}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

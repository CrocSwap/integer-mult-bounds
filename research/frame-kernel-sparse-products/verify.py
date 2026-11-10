"""Check the new sparse adapter, its operation saving and source boundaries.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import contextlib
import hashlib
import io
import itertools
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def small_products():
    cases = 0
    for width in range(7):
        for row in itertools.product((0, 1), repeat=width):
            for vector in itertools.product((-1, 0, 1), repeat=width):
                expected = sum(x * y for x, y in zip(row, vector)) == 0
                replay.require(replay.kernel_ok([row], [vector]) == expected,
                               "small dot-product mismatch")
                cases += 1
    return cases


def trace_products(rows, vectors, counts):
    counts["calls"] += 1
    for row in rows:
        counts["row_scans"] += 1
        for vector in vectors:
            counts["dot_products"] += 1
            counts["dense_terms"] += len(row)
            counts["nonzero_terms"] += sum(value != 0 for value in row)
            if sum(x * y for x, y in zip(row, vector)) != 0:
                counts["false_calls"] += 1
                return False
    return True


def complete_conformance():
    module = replay.load_source()
    baseline = io.StringIO()
    with contextlib.redirect_stdout(baseline):
        module.main()
    reference = module.kernel_ok
    counts = dict.fromkeys(("calls", "row_scans", "dot_products", "dense_terms",
                            "nonzero_terms", "false_calls"), 0)
    calls = hashlib.sha256()

    def compared(rows, vectors):
        dense = reference(rows, vectors)
        sparse = replay.kernel_ok(rows, vectors)
        traced = trace_products(rows, vectors, counts)
        replay.require(dense == sparse == traced, "complete predicate mismatch")
        calls.update(json.dumps([rows, vectors, dense], separators=(",", ":"))
                     .encode("ascii"))
        return sparse

    module.kernel_ok = compared
    candidate = io.StringIO()
    with contextlib.redirect_stdout(candidate):
        module.main()
    replay.require(candidate.getvalue() == baseline.getvalue(),
                   "complete scientific stdout mismatch")
    replay.require("PASS_FULL_FAMILY_G_WITHOUT_D fixtures=2:" in baseline.getvalue(),
                   "complete scientific replay did not finish")
    replay.require(counts["dense_terms"] > counts["nonzero_terms"] > 0,
                   "no sparse operation saving")
    counts["zero_products_removed"] = counts["dense_terms"] - counts["nonzero_terms"]
    counts["unit_products_removed"] = counts["nonzero_terms"]
    counts["call_stream_sha256"] = calls.hexdigest()
    counts["scientific_stdout_sha256"] = hashlib.sha256(
        baseline.getvalue().encode("utf-8")).hexdigest()
    return counts


def controls():
    invalid = [([[2]], [[1]]), ([[-1]], [[1]]), ([[1, 0]], [[1]]),
               ([[0], [0, 1]], [[1]]), ([[True]], [[1]]),
               ([[0]], [[1.0]]), ([[0]] * 2026, [[0]]),
               ([[0] * 121], [[0] * 121]), ([[0]], [[0]] * 9)]
    for rows, vectors in invalid:
        rejects(replay.kernel_ok, rows, vectors)
    replay.require(replay.kernel_ok([], []) and replay.kernel_ok([[0]], []),
                   "empty-product identity failed")
    replay.require(not replay.kernel_ok([[1, 1]], [[1, 0]]),
                   "nonzero dot product was accepted")
    with tempfile.TemporaryDirectory(prefix="frame-kernel-control-") as name:
        path = Path(name) / "damaged.py"
        path.write_bytes(replay.authenticated_source() + b"\n")
        rejects(replay.authenticated_source, path)
        path.write_bytes(b"#" * 65537)
        rejects(replay.authenticated_source, path)
    module = replay.load_source()
    try:
        module.ip((1,), (1,))
    except AssertionError:
        pass
    else:
        raise ValueError("reference assertions were disabled")
    return len(invalid) + 5


def package_hashes():
    files = sorted(path for path in replay.HERE.iterdir() if path.is_file())
    replay.require(len(files) <= 12, "package inventory exceeds capacity")
    result = {}
    for path in files:
        with path.open("rb") as handle:
            data = handle.read(1048577)
        replay.require(len(data) <= 1048576, "package file exceeds capacity")
        result[path.name] = hashlib.sha256(data).hexdigest()
    return result


def main():
    small = small_products()
    counts = complete_conformance()
    negative = controls()
    print(json.dumps({"status": "PASS_FRAME_KERNEL_SPARSE_PRODUCTS",
                      "small_dot_cases": small, "controls": negative,
                      "complete_work": counts, "package_sha256": package_hashes()},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

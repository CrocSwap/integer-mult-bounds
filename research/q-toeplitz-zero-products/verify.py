"""Conformance, exact product counts, and meaningful failure controls."""

import contextlib
import hashlib
import io
import json
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path

from kernel import multiply
from replay import PACKAGE, ROOT, check_sources, load_source


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def complete_conformance() -> dict:
    source = load_source()
    dense = source.multiply
    counts = {"multiplications": 0, "dense_products": 0, "nonzero_products": 0, "entries": 0}
    transcript = hashlib.sha256()

    def compare(left, right):
        reference = dense(left, right)
        candidate = multiply(left, right)
        need(candidate == reference, "complete matrix mismatch")
        order = len(left)
        counts["multiplications"] += 1
        counts["dense_products"] += order ** 3
        counts["entries"] += order ** 2
        counts["nonzero_products"] += sum(
            bool(left[i][k]) and bool(right[k][j])
            for i in range(order) for j in range(order) for k in range(order)
        )
        transcript.update(repr((left, right, candidate)).encode("ascii"))
        return candidate

    output = io.StringIO()
    source.multiply = compare
    with contextlib.redirect_stdout(output):
        source.main()
    need(output.getvalue() == "PASS_Q_TOEPLITZ_FACTORIZATION matrices=30 no_new_kappa\n", "output changed")
    expected_nonzero = 5 * sum(
        n*(n+1)*(n+2)//6 + 5*n*(n+1)//2
        + 2*sum(k*k for k in range(1, n+1)) + n*n + n**3
        for n in range(1, 7)
    )
    need(counts == {"multiplications": 300, "dense_products": 22050,
                    "nonzero_products": expected_nonzero, "entries": 4550}, "coverage counts changed")
    counts["skipped_products"] = counts["dense_products"] - counts["nonzero_products"]
    return {**counts, "transcript_sha256": transcript.hexdigest(), "stdout": output.getvalue()}


def kernel_controls() -> dict:
    dense = load_source().multiply
    values = (Fraction(-1, 3), Fraction(0), Fraction(2, 5))
    matrices = [[list(entries[:2]), list(entries[2:])] for entries in product(values, repeat=4)]
    for left in matrices:
        for right in matrices:
            need(multiply(left, right) == dense(left, right), "rational kernel mismatch")
    for order in range(1, 7):
        left = [[Fraction((3*i + j) % 7 - 3, i+j+1) for j in range(order)] for i in range(order)]
        right = [[Fraction((i + 4*j) % 5 - 2, i+j+2) for j in range(order)] for i in range(order)]
        need(multiply(left, right) == dense(left, right), "dense boundary mismatch")
    rejected = 0
    for left, right in (([], []), ([[1]], []), ([[1, 0]], [[1]]), ([[0]*7]*7, [[0]*7]*7)):
        try:
            multiply(left, right)
        except ValueError:
            rejected += 1
    need(rejected == 4, "invalid shape admitted")
    tiny = Fraction(1, 2**1024)
    need(multiply([[tiny]], [[tiny]]) == [[tiny*tiny]], "small nonzero product lost")
    return {"exhaustive_rational_pairs": len(matrices)**2, "dense_orders": 6, "invalid_shapes": rejected}


def failure_controls() -> dict:
    corruptions = 0
    rows = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    inputs = [row["path"] for row in rows if row["usage"] == "input"]
    with tempfile.TemporaryDirectory(prefix="q-toeplitz-") as scratch:
        root = Path(scratch)
        for relative in inputs:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / relative).read_bytes())
        check_sources(root)
        for relative in inputs:
            path = root / relative
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            try:
                check_sources(root)
            except ValueError:
                corruptions += 1
            path.write_bytes(original)
        check_sources(root)
    need(corruptions == len(inputs), "changed source admitted")
    rejections = 0
    for bad in (lambda left, right: [[Fraction(0)] * len(left) for _ in left],
                lambda left, right: [row[::-1] for row in multiply(left, right)]):
        source = load_source()
        source.multiply = bad
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                source.main()
        except SystemExit:
            rejections += 1
    need(rejections == 2, "faulty multiplication admitted")
    return {"source_corruptions": corruptions, "faulty_kernel_rejections": rejections}


def main() -> None:
    result = {"complete": complete_conformance(), "kernel": kernel_controls(), "controls": failure_controls()}
    result["files_sha256"] = {
        name: hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()
        for name in ("BENCHMARK.json", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
                     "benchmark.py", "kernel.py", "replay.py", "verify.py")
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_Q_TOEPLITZ_ZERO_PRODUCTS")


if __name__ == "__main__":
    main()

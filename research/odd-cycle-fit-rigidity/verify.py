"""Bounded exact corroboration of odd-cycle fitting-matrix rigidity.

produced by Nick Petalas. Apache-2.0.
"""

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from linear import (  # noqa: E402
    block,
    canonical,
    check,
    diagonal,
    inverse2,
    matrix,
    multiply,
    normal_form,
    rank,
    scalar,
)


def binary_rank(data):
    """Independent column-bit elimination, used for the completion census."""
    pivots = {}
    for column in zip(*data, strict=True):
        value = sum(int(x) << i for i, x in enumerate(column))
        for _ in range(len(data)):
            if not value:
                break
            leading = value.bit_length() - 1
            if leading not in pivots:
                pivots[leading] = value
                break
            value ^= pivots[leading]
        else:
            check(value == 0, "binary elimination capacity")
    return len(pivots)


def conjugate(n, bases, prime):
    change = diagonal(bases)
    undo = diagonal(tuple(inverse2(basis, prime) for basis in bases))
    return multiply(multiply(change, matrix(canonical(n), prime), prime), undo, prime)


def local_consequences(data, prime):
    n = len(data) // 2
    zero = ((0, 0), (0, 0))
    identity = ((1, 0), (0, 1))
    for i in range(n):
        before, after = (i - 1) % n, (i + 1) % n
        left = multiply(block(data, i, before), block(data, before, i), prime)
        right = multiply(block(data, i, after), block(data, after, i), prime)
        check(rank(left, prime) == rank(right, prime) == 1, "projector rank")
        check(multiply(left, left, prime) == left, "left idempotent")
        check(multiply(right, right, prime) == right, "right idempotent")
        total = tuple(
            tuple(scalar(a + b, prime) for a, b in zip(x, y, strict=True))
            for x, y in zip(left, right, strict=True)
        )
        check(total == identity, "complementary projectors")
        check(multiply(left, right, prime) == zero, "projector disjointness")
        for direction in (-1, 1):
            j, k = (i + direction) % n, (i + 2 * direction) % n
            check(rank(block(data, i, j), prime) == 1, "ordered edge rank")
            check(
                multiply(block(data, i, j), block(data, j, k), prime) == zero,
                "two-edge product",
            )
    twice = tuple(tuple(scalar(2 * x, prime) for x in row) for row in data)
    check(multiply(data, data, prime) == twice, "quadratic identity")
    return n


def field_fixtures():
    count = 0
    for prime, n, seed in itertools.product(
        (0, 2, 3, 5, 101), (5, 7, 9, 11, 13), range(8)
    ):
        bases = []
        for i in range(n):
            a, b = (seed + 3 * i) % 7 - 3, (3 * seed + i) % 7 - 3
            s = (
                Fraction(seed % 4 + 1, i % 3 + 1)
                if not prime
                else seed % (prime - 1) + 1
            )
            scale = 1 / s if not prime else pow(s, -1, prime)
            bases.append(matrix(((s, s * a), (scale * b, scale * (1 + a * b))), prime))
        data = conjugate(n, bases, prime)
        normal_form(data, prime)
        local_consequences(data, prime)
        if prime == 2:
            check(binary_rank(data) == n, "independent fixture rank")
        count += 1
    return count


def binary_gauge_census():
    gauges = tuple(
        matrix((values[:2], values[2:]), 2)
        for values in itertools.product(range(2), repeat=4)
        if (values[0] * values[3] - values[1] * values[2]) % 2
    )
    check(len(gauges) == 6, "GL2(F2) order")
    digests = set()
    for bases in itertools.product(gauges, repeat=5):
        data = conjugate(5, bases, 2)
        normal_form(data, 2)
        check(binary_rank(data) == 5, "independent gauge rank")
        digests.add(bytes(x for row in data for x in row))
    check(len(digests) == 6**5, "distinct gauge matrices")
    return len(digests)


def completion_census():
    counts = []
    digest = hashlib.sha256()
    values = tuple(itertools.product(range(2), repeat=4))
    for n in (5, 7):
        slots = tuple((i, (i + step) % n) for i in range(n) for step in (-1, 1))
        tested = accepted = 0
        for first, second in itertools.combinations(slots, 2):
            for a, b in itertools.product(values, repeat=2):
                rows = [list(row) for row in canonical(n)]
                for (i, j), entries in ((first, a), (second, b)):
                    for x, y in itertools.product(range(2), repeat=2):
                        rows[2 * i + x][2 * j + y] = entries[2 * x + y]
                dimension = binary_rank(rows)
                tested += 1
                digest.update(bytes((n, dimension)))
                if dimension == n:
                    normal_form(rows, 2)
                    local_consequences(rows, 2)
                    accepted += 1
        counts.append({"n": n, "tested": tested, "minimum_rank": accepted})
    return counts, digest.hexdigest()


def rejected(function, *args):
    try:
        function(*args)
    except ValueError:
        return 1
    raise ValueError("negative control accepted")


def controls():
    count = 0
    for prime in (0, 2, 3, 5, 101):
        rows = [list(row) for row in canonical(5)]
        rows[1][2] = rows[2][1] = 0
        data = matrix(rows, prime)
        check(rank(data, prime) == 6, "rank-slack boundary")
        count += rejected(normal_form, data, prime)
        count += rejected(local_consequences, data, prime)
    for n in (6, 8):
        rows = [[int(i == j) for j in range(2 * n)] for i in range(2 * n)]
        for i in range(0, n, 2):
            for j in range(2):
                rows[2 * i + j][2 * (i + 1) + j] = 1
                rows[2 * (i + 1) + j][2 * i + j] = 1
        check(binary_rank(rows) == n, "even-cycle minimum-rank witness")
        count += rejected(normal_form, rows, 2)
        count += rejected(local_consequences, rows, 2)
    data = [list(row) for row in canonical(5)]
    data[0][4] = 1
    count += rejected(normal_form, data, 2)
    data = [list(row) for row in canonical(5)]
    data[0][0] = 0
    count += rejected(normal_form, data, 2)
    for bad in ([], [[1], [1, 0]], [[True]], [[Fraction(1, 2)]], [[2**257]]):
        count += rejected(matrix, bad, 2)
    count += rejected(matrix, [[1]], 4)
    return count


def receipt():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    root = PACKAGE.parent.parent
    inputs = {}
    for item in sources["files"]:
        if item["usage"] == "input":
            digest = hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
            check(digest == item["sha256"], "source drift: " + item["path"])
            inputs[item["path"]] = digest
    completions, digest = completion_census()
    evidence = {
        "field_fixtures": field_fixtures(),
        "binary_gauge_matrices": binary_gauge_census(),
        "two_block_completions": completions,
        "completion_digest": digest,
        "negative_controls": controls(),
    }
    files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.iterdir())
        if path.is_file() and path.name != "RESULT.json"
    }
    return {
        "schema_version": 1,
        "claim_type": "scoped proof with exact finite corroboration",
        "evidence": evidence,
        "package_sha256": files,
        "input_sha256": inputs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = receipt()
    if args.write_result:
        check(
            args.write_result.resolve().parent != PACKAGE,
            "write receipts outside the package",
        )
        args.write_result.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
    else:
        saved = json.loads((PACKAGE / "RESULT.json").read_text())
        check(
            json.dumps(result, sort_keys=True) == json.dumps(saved, sort_keys=True),
            "receipt mismatch",
        )
    print(json.dumps(result["evidence"], sort_keys=True))
    print("PASS_ODD_CYCLE_FIT_RIGIDITY")


if __name__ == "__main__":
    main()

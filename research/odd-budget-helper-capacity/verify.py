"""Independent finite corroboration of the new odd-budget boundary contract.

Produced by Nick Petalas. Apache-2.0. Writes only its computed stdout receipt.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import capacity as candidate


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def inverse(value: candidate.Matrix) -> candidate.Matrix:
    size = len(value)
    work = [list(row) + list(candidate.identity(size)[i]) for i, row in enumerate(value)]
    for column in range(size):
        pivot = next(i for i in range(column, size) if work[i][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row != column:
                scale = work[row][column]
                work[row] = [a - scale * b for a, b in zip(work[row], work[column], strict=True)]
    check(all(work[i][:size] == list(candidate.identity(size)[i]) for i in range(size)),
          "inverse elimination failed")
    return tuple(tuple(row[size:]) for row in work)


def chart(smith: tuple[int, ...], serial: int) -> tuple[candidate.Matrix, ...]:
    m, n = len(smith) + 1, len(smith) + 2
    changes = []
    for size in (m, n):
        work = [list(row) for row in candidate.identity(size)]
        for index in range(size - 1):
            coefficient = (serial + index) % 5 - 2
            work[index] = [a + coefficient * b
                           for a, b in zip(work[index], work[index + 1], strict=True)]
        work[-1] = [entry * Fraction(1, 2) for entry in work[-1]]
        changes.append(tuple(tuple(row) for row in work))
    u, v = changes
    diagonal = tuple(tuple(Fraction(smith[i] if i == j and i < len(smith) else 0)
                           for j in range(n)) for i in range(m))
    k = candidate.multiply(candidate.multiply(inverse(u), diagonal), inverse(v))
    return k, u, v


def witness_ok(k: candidate.Matrix, x: candidate.Matrix, y: candidate.Matrix,
               count: int, a: int, b: int) -> bool:
    if len(x) != count or len(y) != len(k[0]):
        return False
    if any(len(row) != len(k) for row in x) or any(len(row) != count for row in y):
        return False
    for rows, scale in ((x, a), (y, b)):
        for row in rows:
            for entry in row:
                denominator = (scale * entry).denominator
                if denominator & (denominator - 1):
                    return False
    for i in range(count):
        for j in range(count):
            entry = sum((x[i][s] * k[s][t] * y[t][j]
                         for s in range(len(k)) for t in range(len(k[0]))), Fraction(0))
            if entry != int(i == j):
                return False
    return True


def chart_cases() -> dict[str, int | list[int]]:
    profiles = [()]
    profiles.extend((a,) for a in (1, 3, 5))
    profiles.extend((a, a * b) for a in (1, 3, 5) for b in (1, 3, 5, 9))
    profiles.extend((a, a * b, a * b * c) for a in (1, 3, 5)
                    for b in (1, 3, 5, 9) for c in (1, 3, 5, 9))
    profiles.append((1, 27, 675))
    cases = 0
    obstructions = 0
    for serial, smith in enumerate(profiles):
        k, u, v = chart(smith, serial)
        for a, b in itertools.product((1, 3, 5, 9, 15, 25), repeat=2):
            x, y, count, obstruction = candidate.construct(k, u, v, smith, a, b)
            check(witness_ok(k, x, y, count, a, b), "non-diagonal boundary witness")
            if obstruction:
                prime, exponent = obstruction
                local_count = sum(h % (prime ** (exponent + 1)) != 0 for h in smith)
                check(local_count == count, "prime-local upper certificate")
                obstructions += 1
            else:
                check(count == len(smith), "rational-rank upper certificate")
            cases += 1
        for count in range(len(smith) + 1):
            q = candidate.common_denominator(smith, count)
            x, y, achieved, _ = candidate.construct(k, u, v, smith, q, q)
            check(achieved >= count and witness_ok(k, x, y, achieved, q, q),
                  "least common denominator attainer")
            if count:
                for prime, _ in candidate.factors(q):
                    _, _, fewer, _ = candidate.construct(k, u, v, smith, q // prime, q // prime)
                    check(fewer < count, "common denominator prime is indispensable")
        check(candidate.common_denominator(smith, len(smith) + 1) is None,
              "above-rank common denominator")
    minima = [candidate.common_denominator((1, 27, 675), t) for t in (1, 2, 3)]
    check(minima == [1, 9, 45], "prime-power example")
    return {"profiles": len(profiles), "budget_cases": cases,
            "prime_obstructions": obstructions, "example_minima": minima}


def factor_exists(k: tuple[tuple[int, int], tuple[int, int]], scalar: int,
                  width: int, modulus: int) -> tuple[bool, int, int]:
    """Brute-force every right factor, then every possible left row modulo 9."""
    right_count = 0
    row_count = 0
    targets = [tuple(scalar * int(i == j) % modulus for j in range(width))
               for i in range(width)]
    for flat in itertools.product(range(modulus), repeat=2 * width):
        right_count += 1
        right = (flat[:width], flat[width:])
        middle = tuple(tuple(sum(k[i][s] * right[s][j] for s in range(2)) % modulus
                             for j in range(width)) for i in range(2))
        image = set()
        for left in itertools.product(range(modulus), repeat=2):
            image.add(tuple(sum(left[s] * middle[s][j] for s in range(2)) % modulus
                            for j in range(width)))
            row_count += 1
        if all(target in image for target in targets):
            return True, right_count, row_count
    return False, right_count, row_count


def residue_cases() -> dict[str, int]:
    systems = 0
    right_count = 0
    row_count = 0
    for d0, d1 in itertools.combinations_with_replacement((1, 3, 9), 2):
        for changed in range(3):
            k = ((d0, changed * d0), ((changed + 1) * d0,
                                     (changed + 1) * changed * d0 + d1))
            for scalar in (1, 3):
                expected = sum(scalar % d == 0 for d in (d0, d1))
                for width in (1, 2):
                    exists, rights, rows = factor_exists(k, scalar, width, 9)
                    check(exists == (width <= expected), "independent residue-ring existence")
                    systems += 1
                    right_count += rights
                    row_count += rows
    check(not factor_exists(((1, 0), (0, 9)), 3, 2, 9)[0],
          "determinant-only false positive")
    return {"systems": systems, "right_factors_enumerated": right_count,
            "left_rows_enumerated": row_count, "determinant_control": 1}


def scalar_cases() -> dict[str, int]:
    cases = 0
    pairs = 0
    for prime in (3, 5):
        for power in range(5):
            for exponent in range(3):
                modulus = prime ** (exponent + 1)
                scalar = prime ** exponent
                found = False
                for left, right in itertools.product(range(modulus), repeat=2):
                    pairs += 1
                    if (left * prime ** power * right - scalar) % modulus == 0:
                        found = True
                check(found == (power <= exponent), "complete scalar prime-power search")
                cases += 1
    return {"systems": cases, "factor_pairs_enumerated": pairs}


def symmetric_cases() -> dict[str, int]:
    pairs = 0
    for factor in range(1, 256, 2):
        feasible = []
        for q in range(1, factor + 1, 2):
            if q * q % factor == 0:
                feasible.append(q)
            pairs += 1
        predicted = candidate.common_denominator((factor,), 1)
        check(predicted == min(feasible), "independent least common denominator")
        check(all(q % predicted == 0 for q in feasible), "all feasible denominators divide")
    largest = 1 << 255
    k = candidate.matrix([[largest]])
    u = candidate.matrix([[Fraction(1, largest)]])
    v = candidate.identity(1)
    x, y, count, _ = candidate.construct(k, u, v, (1,), candidate.MAX_ODD, candidate.MAX_ODD)
    check(witness_ok(k, x, y, count, candidate.MAX_ODD, candidate.MAX_ODD),
          "inclusive bit and budget capacities")
    k = tuple(tuple(Fraction(i == j and i < 1) for j in range(6)) for i in range(6))
    x, y, count, _ = candidate.construct(k, candidate.identity(6), candidate.identity(6),
                                        (1,), 1, 1)
    check(witness_ok(k, x, y, count, 1, 1), "inclusive dimension capacity")
    return {"odd_factors": 128, "denominator_candidates": pairs, "capacity_positives": 2}


def expect_rejection(function, *arguments) -> None:
    try:
        function(*arguments)
    except (ValueError, TypeError):
        return
    raise AssertionError("invalid contract accepted")


def controls() -> dict[str, int]:
    k, u, v = chart((1, 27, 675), 2)
    invalid_budgets = (0, -1, 2, True, (1 << 21) + 1)
    for value in invalid_budgets:
        expect_rejection(candidate.construct, k, u, v, (1, 27, 675), value, 1)
    for smith in ((3, 1), (0,), (2,), ((1 << 21) + 1,)):
        expect_rejection(candidate.construct, k, u, v, smith, 1, 1)
    altered = tuple(tuple(value + int(i == 0 and j == 0) for j, value in enumerate(row))
                    for i, row in enumerate(k))
    expect_rejection(candidate.construct, altered, u, v, (1, 27, 675), 1, 1)
    bad_u = tuple(tuple(value * (3 if i == 0 else 1) for value in row)
                  for i, row in enumerate(u))
    expect_rejection(candidate.construct, k, bad_u, v, (1, 27, 675), 1, 1)
    bad_matrices = ([[Fraction(1, 3)]], [[True]], [[1], [1, 2]], [], [[1 << 256]],
                    [[1] * 7], [[1]] * 7)
    for value in bad_matrices:
        expect_rejection(candidate.matrix, value)
    expect_rejection(candidate.common_denominator, (1,) * 7, 1)
    expect_rejection(candidate.common_denominator, (1,), -1)
    x, y, count, _ = candidate.construct(k, u, v, (1, 27, 675), 9, 75)
    check(witness_ok(k, x, y, count, 9, 75), "positive witness control")
    bad_x = tuple(tuple(value + int(i == 0 and j == 0) for j, value in enumerate(row))
                  for i, row in enumerate(x))
    check(not witness_ok(k, bad_x, y, count, 9, 75), "changed boundary coefficient")
    check(not witness_ok(k, x, y[:-1], count, 9, 75), "missing suffix row")
    check(not witness_ok(k, x, y, count, 1, 75), "undeclared left odd division")
    return {"rejections": len(invalid_budgets) + 4 + 2 + len(bad_matrices) + 2 + 3,
            "positive_witnesses": 1}


def authenticate() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    sources = json.loads((package / "SOURCES.json").read_text())
    hashes = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            check(digest == row["sha256"], "live predecessor proof drift")
            hashes[row["path"]] = digest
    names = ("README.md", "PROOF.md", "SAFETY.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "capacity.py", "verify.py")
    for name in names:
        hashes[name] = hashlib.sha256((package / name).read_bytes()).hexdigest()
    return hashes


def main() -> None:
    hashes = authenticate()
    receipt = {"status": "PASS_ODD_BUDGET_HELPER_CAPACITY", "source_sha256": hashes,
               "charts": chart_cases(), "residue_ring": residue_cases(),
               "scalar_prime_powers": scalar_cases(), "common_denominators": symmetric_cases(),
               "controls": controls(),
               "scope": "Scoped algebraic proof with finite corroboration; no supplier or kappa."}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Standalone exact finite corroboration; writes only a generated stdout receipt."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import sys

from bounds import certificate, comparison, cutoff, rational_boundary


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def determinant(matrix: list[list[F]]) -> F:
    """Literal signed permutation oracle, deliberately independent of the law."""
    n = len(matrix)
    require(1 <= n <= 5 and all(len(row) == n for row in matrix), "oracle dimensions")
    total = F(0)
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        term = F((-1) ** inversions)
        for i in range(n):
            term *= matrix[i][order[i]]
        total += term
    return total


def rank(matrix: list[list[F]]) -> int:
    """Independent rational elimination for the larger attaining witnesses."""
    n = len(matrix)
    require(1 <= n <= 32 and all(len(row) == n for row in matrix), "rank dimensions")
    rows = [row[:] for row in matrix]
    pivots = 0
    for col in range(n):
        candidates = [i for i in range(pivots, n) if rows[i][col]]
        if not candidates:
            continue
        pivot = candidates[0]
        rows[pivots], rows[pivot] = rows[pivot], rows[pivots]
        divisor = rows[pivots][col]
        rows[pivots] = [value / divisor for value in rows[pivots]]
        for i in range(pivots + 1, n):
            multiplier = rows[i][col]
            rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[pivots])]
        pivots += 1
    return pivots


def check_identities() -> int:
    count = 0
    for n, limit, error in product(range(1, 6), (F(1), F(3, 2), F(4)),
                                    (F(0), F(1, 256), F(1, 250), F(1, 7), F(1))):
        matrix = comparison(n, limit, error)
        weights, margin = certificate(n, limit, error)
        residual = [sum(a * b for a, b in zip(row, weights)) for row in matrix]
        require(residual == [margin] * n, "weighted identity")
        require(determinant(matrix) == margin, "literal determinant disagrees")
        count += 1
    return count


def check_vertices() -> int:
    """Every real sign vertex in the stated n=2,3 parameter boxes."""
    count = 0
    for n, limit in product((2, 3), (F(1), F(2))):
        error = cutoff(n, limit, 16)[0] / 2
        weights, margin = certificate(n, limit, error)
        require(margin > 0 and all(w > 0 for w in weights), "invalid positive certificate")
        for signs in product((-1, 1), repeat=n * n):
            matrix = [[F(i == j) + signs[i*n+j] * (limit if i < j else error)
                       for j in range(n)] for i in range(n)]
            require(determinant(matrix) != 0, "singular sign vertex below cutoff")
            count += 1
    return count


def check_boundaries() -> tuple[int, int]:
    count, broken = 0, 0
    for n, ratio in product(range(2, 17), (F(2), F(3), F(7, 2), F(16))):
        limit, error, weights = rational_boundary(n, ratio)
        matrix = comparison(n, limit, error)
        require(rank(matrix) == n - 1, "boundary rank")
        require(all(sum(a*b for a, b in zip(row, weights)) == 0 for row in matrix), "kernel")
        require(error * (1 + limit - error) ** n == limit, "boundary polynomial")
        require(limit / (1 + limit) ** n < error <= 1 / limit ** (n - 1), "growth sandwich")
        low, high = cutoff(n, limit, 40)
        require(low <= error <= high, "boundary outside cutoff interval")
        changed = [row[:] for row in matrix]
        changed[-1][0] += error
        require(rank(changed) == n, "missing wrap term was not detected")
        count += 1
        broken += 1
    return count, broken


def check_controls() -> list[str]:
    invalid = ((0, F(1), F(0)), (33, F(1), F(0)), (True, F(1), F(0)),
               (2, F(1, 2), F(0)), (2, F(1), F(-1)), (2, F(1), F(2)),
               (2, 1, F(0)), (2, F(1 << 4097), F(0)))
    for n, limit, error in invalid:
        try:
            certificate(n, limit, error)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    for bits in (0, 129, True):
        try:
            cutoff(2, F(1), bits)
        except ValueError:
            continue
        raise ValueError("invalid precision accepted")
    require(rank([[F(1), F(1)], [F(1), F(1)]]) == 1, "cyclic zero-error counterexample")
    limit, error, _ = rational_boundary(2, F(256))
    paid = comparison(2, limit, error)
    total = [row[:] for row in paid]
    total[0][1] += limit  # An off-mask summand can conceal paid-subtotal growth.
    require(rank(paid) == 1 and rank(total) == 2, "paid-subtotal control")
    require(max(abs(x) for row in total for x in row) < 1, "bounded final total")
    require(limit > 255, "large paid subtotal")
    require(certificate(8, F(1), F(1, 256))[1] > 0, "eight-line safe cutoff")
    require(certificate(8, F(1), F(1, 250))[1] < 0, "eight-line upper bracket")
    require(certificate(1, F(1), F(1))[1] == 0, "diagonal-error boundary")
    return ([f"invalid-domain-{i}" for i in range(len(invalid))]
            + [f"invalid-precision-{i}" for i in range(3)]
            + ["cyclic-zero-error", "paid-subtotal-vs-final-total",
               "eight-line-bracket", "diagonal-error-boundary"])


def receipt_files() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "bounds.py", "verify.py")
    result = {}
    for name in names:
        path = root / name
        require(path.stat().st_size <= 1024 * 1024, "receipt input too large")
        data = path.read_bytes()
        result[name] = sha256(data).hexdigest()
    return result


def main() -> None:
    require(len(sys.argv) == 1, "no CLI arguments are accepted")
    identities = check_identities()
    vertices = check_vertices()
    boundaries, omissions = check_boundaries()
    controls = check_controls()
    low, high = cutoff(8, F(1))
    result = {"claim_type": "scoped proof with exact finite corroboration", "new_kappa": False,
              "determinant_identities": identities, "sign_vertices": vertices,
              "rank_n_minus_one_witnesses": boundaries, "wrap_omissions_rejected": omissions,
              "controls": controls, "control_count": len(controls),
              "n8_L1_cutoff": [str(low), str(high)],
              "files_sha256": receipt_files()}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("PASS_ACYCLIC_BORDER_ERROR")


if __name__ == "__main__":
    main()

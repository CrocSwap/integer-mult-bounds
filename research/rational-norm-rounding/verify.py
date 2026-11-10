"""Exact finite corroboration. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
from math import isqrt, lcm
from pathlib import Path
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def norm2(vector):
    return sum(x * x for x in vector)


def validate(matrix):
    """The finite reference accepts exact rational orthogonal matrices, d<=4."""
    d = len(matrix)
    require(1 <= d <= 4, "dimension must be in 1..4")
    require(all(len(row) == d for row in matrix), "matrix must be square")
    require(all(type(x) in (int, F) for row in matrix for x in row), "exact rationals required")
    require(all(abs(x.numerator) <= 625 and x.denominator <= 625
                for row in matrix for x in map(F, row)), "coefficient bound")
    for i, j in product(range(d), repeat=2):
        require(sum(matrix[k][i] * matrix[k][j] for k in range(d)) == (i == j),
                "matrix must be orthogonal")


def column_data(matrix, j):
    validate(matrix)
    require(type(j) is int and 0 <= j < len(matrix), "column index")
    column = tuple(F(row[j]) for row in matrix)
    q = lcm(*(x.denominator for x in column))
    a = tuple(int(q * x) for x in column)
    require(norm2(a) == q * q, "column norm invariant")
    return q, a


def radial_certificate(q, a, n, y):
    """Return the literal error and its positive integral quantum."""
    require(type(q) is int and 2 <= q <= 625, "nonintegral column required")
    require(1 <= len(a) <= 4 and len(a) == len(y), "vector dimensions")
    require(all(type(x) is int for x in a + y), "integer vectors required")
    require(norm2(a) == q * q, "unit rational direction required")
    require(type(n) is int and 1 <= n <= 2**64, "input radius bound")
    require(any(n * x % q for x in a), "ideal output must be nonintegral")
    require(norm2(y) == n * n, "output must preserve the input norm")
    error = norm2(tuple(F(y[i]) - F(n * a[i], q) for i in range(len(a))))
    quantum = n * q - sum(a[i] * y[i] for i in range(len(a)))
    require(type(quantum) is int and quantum >= 1, "positive error quantum")
    require(error == F(2 * n * quantum, q), "radial error identity")
    return error, quantum


def sphere(d, n):
    """Complete integer sphere; at most 17**3 prefix trials per stream."""
    require(type(d) is int and 1 <= d <= 4, "sphere dimension")
    require(type(n) is int and 1 <= n <= 8, "sphere radius")
    for prefix in product(range(-n, n + 1), repeat=d - 1):
        remaining = n * n - norm2(prefix)
        if remaining < 0:
            continue
        last = isqrt(remaining)
        if last * last == remaining:
            yield prefix + (last,)
            if last:
                yield prefix + (-last,)


def cases():
    rotation = ((F(3, 5), F(-4, 5)), (F(4, 5), F(3, 5)))
    hadamard = tuple(tuple(F((-1) ** ((i & j).bit_count()), 2)
                           for j in range(4)) for i in range(4))
    r01 = ((F(3, 5), F(-4, 5), 0), (F(4, 5), F(3, 5), 0), (0, 0, 1))
    r12 = ((1, 0, 0), (0, F(3, 5), F(-4, 5)), (0, F(4, 5), F(3, 5)))
    composed = tuple(tuple(sum(r12[i][k] * r01[k][j] for k in range(3))
                           for j in range(3)) for i in range(3))
    return {"rotation5": rotation, "rotation5_with_spectator": r01,
            "two_plane_product25": composed, "four_coordinate_hadamard2": hadamard}


def check_spheres(matrices):
    count = 0
    streams = []
    for name, matrix in matrices.items():
        validate(matrix)
        for j in range(len(matrix)):
            q, a = column_data(matrix, j)
            if q == 1:
                continue
            for n in range(1, 9 if len(matrix) < 4 else 5):
                if n % q == 0:
                    continue
                errors = []
                for y in sphere(len(matrix), n):
                    error, quantum = radial_certificate(q, a, n, y)
                    require(error >= F(2 * n, q), "claimed lower bound")
                    errors.append((error, quantum))
                    count += 1
                require(errors, "sphere must contain the signed coordinate axes")
                streams.append([name, j, n, q, str(min(errors)[0]), len(errors)])
    return count, streams


def check_finite_contraction():
    domain = tuple(range(-3, 4))
    examined = 0
    contractive = 0
    for image in permutations(domain):
        examined += 1
        if all(y * y <= x * x for x, y in zip(domain, image)):
            require(all(y * y == x * x for x, y in zip(domain, image)), "finite norm preservation")
            contractive += 1
    require(examined == 5040 and contractive == 8, "complete permutation census")
    return {"permutations": examined, "contractive": contractive}


def check_dyadic(matrices):
    records = []
    for name, matrix in matrices.items():
        for j in range(len(matrix)):
            q, a = column_data(matrix, j)
            if q == 1:
                continue
            first = None
            for p in range(1, 65):
                N = 2**p
                n = N if N % q else N - 1
                require(1 <= n <= N and any(n * x % q for x in a), "nonintegral ball witness")
                bound = F(2 * n, q * N * N)
                require(bound >= F(2 * (N - 1), q * N * N), "physical bound")
                if bound > F(16, N * N) and first is None:
                    first = p
            require(first is not None, "C=4 must eventually be excluded")
            records.append([name, j, q, first])
    return records


def check_controls(matrices):
    r = matrices["rotation5"]
    q, a = column_data(r, 0)
    bad = (
        lambda: validate(((1, 1), (0, 1))),
        lambda: validate(((1, 0),)),
        lambda: validate(((1.0, 0), (0, 1))),
        lambda: column_data(r, 2),
        lambda: radial_certificate(q, a, 5, (3, 4)),
        lambda: radial_certificate(q, a, 1, (0, 0)),
        lambda: radial_certificate(q, a, 1, (0, 1, 0)),
        lambda: radial_certificate(1, (1, 0), 1, (1, 0)),
    )
    for f in bad:
        try:
            f()
        except ValueError:
            continue
        raise ValueError("malformed or out-of-scope certificate accepted")
    require(radial_certificate(q, a, 1, (0, 1)) == (F(2, 5), 1), "attaining quantum")
    signed = ((0, -1), (1, 0))
    validate(signed)
    for x in product(range(-4, 5), repeat=2):
        y = tuple(sum(signed[i][k] * x[k] for k in range(2)) for i in range(2))
        require(norm2(x) == norm2(y), "signed permutation positive control")
    require(norm2((0, 0)) < norm2((1, 0)), "noninjective contraction control")
    require(norm2(tuple(F(x, q) for x in a)) == 1, "finer-grid escape")
    nearest, ideal = (1, 1, 1, 1), (F(1, 2),) * 4
    require(norm2(nearest) > 1 and norm2(tuple(y-z for y,z in zip(nearest, ideal))) == 1,
            "outward nearest-grid control")
    return {"rejections": len(bad), "signed_permutation_inputs": 81,
            "attaining_quantum": True, "hypothesis_escape_controls": 3}


def main():
    require(len(sys.argv) == 1, "read-only verifier takes no arguments")
    matrices = cases()
    count, streams = check_spheres(matrices)
    report = {"status": "PASS_RATIONAL_NORM_ROUNDING", "claim_type": "scoped-proof",
              "matrix_fixtures": len(matrices), "literal_sphere_outputs": count,
              "sphere_streams": streams, "finite_contraction": check_finite_contraction(),
              "dyadic_column_certificates_64_precisions": check_dyadic(matrices),
              "controls": check_controls(matrices), "source_programs_executed": 0}
    package = Path(__file__).resolve().parent
    names = ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    report["file_sha256"] = {name: sha256((package/name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

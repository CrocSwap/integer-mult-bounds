"""Exact finite corroboration for the half-shift lower envelope.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable is imported. The universal theorem is in PROOF.md.
"""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform


MAX_N = 8
MAX_SPECTRAL_N = 32
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def kernel(n, q, endpoint):
    require(type(n) is int and 1 <= n <= MAX_N, "finite size domain")
    require(type(q) is F and 0 < q < 1, "Gaussian scale domain")
    require(q.numerator.bit_length() <= 20, "numerator capacity")
    require(q.denominator.bit_length() <= 20, "denominator capacity")
    require(type(endpoint) is int and endpoint in (-1, 0, 1), "shift domain")
    return [[q ** ((j - i) ** 2 - endpoint * (j - i))
             for j in range(n)] for i in range(n)]


def multiply(a, b):
    n = len(a)
    return [[sum((a[i][k] * b[k][j] for k in range(n)), F(0))
             for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    aug = [list(row) + unit for row, unit in zip(a, identity(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i][j]), None)
        require(pivot is not None, "singular matrix")
        aug[j], aug[pivot] = aug[pivot], aug[j]
        scale = aug[j][j]
        aug[j] = [x / scale for x in aug[j]]
        for i in range(n):
            if i != j:
                scale = aug[i][j]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[j])]
    result = [row[n:] for row in aug]
    require(multiply(a, result) == identity(n), "right inverse")
    require(multiply(result, a) == identity(n), "left inverse")
    return result


def checkerboard(a):
    n = len(a)
    return [[(-1) ** (i + j) * a[i][j] for j in range(n)] for i in range(n)]


def dominates_triangle(b, endpoint):
    n = len(b)
    for i in range(n):
        for j in range(n):
            triangle = i <= j if endpoint == 1 else j <= i
            require(b[i][j] >= int(triangle), "triangular domination")


def check_gaussians():
    cases = entries = strict = 0
    largest_bits = 0
    for q in (F(1, 8), F(1, 3), F(1, 2), F(2, 3), F(7, 8)):
        for n in range(1, MAX_N + 1):
            for endpoint in (-1, 1):
                a = kernel(n, q, endpoint)
                inv = inverse(a)
                b = checkerboard(inv)
                dominates_triangle(b, endpoint)
                require(all(x > 0 for row in b for x in row), "positive inverse")
                if n > 1:
                    require(b[-1][-1] > 1, "strict norm comparison witness")
                    strict += 1
                else:
                    require(b == [[F(1)]], "size-one equality")
                cases += 1
                entries += n * n
                for row in inv:
                    for x in row:
                        bits = max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                        largest_bits = max(largest_bits, bits)
                        require(bits <= 8192, "arithmetic capacity")
    return {"matrices": cases, "entries": entries, "strict_cases": strict,
            "largest_inverse_rational_bits": largest_bits}


def poly_step(poly, diagonal, previous):
    out = [0] * (len(poly) + 1)
    for i, value in enumerate(poly):
        out[i] -= diagonal * value
        out[i + 1] += value
    for i, value in enumerate(previous):
        out[i] -= value
    return out


def spectral_polynomial(n):
    previous, current = [0], [1]
    for size in range(1, n + 1):
        diagonal = 1 if size == n else 2
        previous, current = current, poly_step(current, diagonal, previous)
    return current


def laurent_substitution(coefficients):
    out = {}
    for coefficient in reversed(coefficients):
        following = {}
        for exponent, value in out.items():
            for delta, scale in ((-1, -1), (0, 2), (1, -1)):
                key = exponent + delta
                following[key] = following.get(key, 0) + scale * value
        following[0] = following.get(0, 0) + coefficient
        out = {key: value for key, value in following.items() if value}
    return out


def check_spectral_identity():
    for n in range(1, MAX_SPECTRAL_N + 1):
        poly = spectral_polynomial(n)
        actual = laurent_substitution(poly)
        expected = {j: (-1 if j % 2 else 1) for j in range(-n, n + 1)}
        require(actual == expected, "complete characteristic identity")
        if n <= MAX_N:
            u = [[F(i <= j) for j in range(n)] for i in range(n)]
            difference = [[F(i == j) - F(j == i + 1)
                           for j in range(n)] for i in range(n)]
            require(multiply(u, difference) == identity(n), "triangular inverse")
            require(multiply(difference, u) == identity(n), "reverse triangular inverse")
    return {"complete_laurent_identities": MAX_SPECTRAL_N,
            "triangular_inverse_pairs": MAX_N}


def check_limit():
    cases = 0
    for n in range(2, MAX_N + 1):
        previous = None
        for bits in (2, 4, 8, 16):
            b = checkerboard(inverse(kernel(n, F(1, 2 ** bits), 1)))
            error = sum((b[i][j] - int(i <= j)) ** 2
                        for i in range(n) for j in range(n))
            require(error > 0, "limit is not finite-scale equality")
            if previous is not None:
                require(error < previous, "finite approach-to-limit fixture")
            previous = error
            cases += 1
        require(previous < F(1, 10 ** 12), "small-scale limit fixture")
    return {"limit_matrices": cases, "decreasing_error_comparisons": 3 * (MAX_N - 1)}


def expect_rejection(n, q, endpoint):
    try:
        kernel(n, q, endpoint)
    except ValueError:
        return
    raise ValueError("invalid input accepted")


def check_controls():
    invalid = ((0, F(1, 2), 1), (9, F(1, 2), 1), (True, F(1, 2), 1),
               (2, F(0), 1), (2, F(1), 1), (2, F(-1), 1),
               (2, 0.5, 1), (2, F(1, 2), 2), (2, F(1, 2), True),
               (2, F(1, 2 ** 21), 1))
    for n, q, endpoint in invalid:
        expect_rejection(n, q, endpoint)
    a = kernel(3, F(1, 8), 1)
    inv = inverse(a)
    b = checkerboard(inv)
    require(b[1][0] < 1, "all-ones comparator must fail")
    require(inv[0][1] < 0, "checkerboard sign is essential")
    require(checkerboard(inverse(kernel(3, F(1, 8), -1)))[0][1] < 1,
            "transpose changes triangle")
    inv[0][0] += 1
    require(multiply(a, inv) != identity(3), "altered inverse control")
    interior = inverse(kernel(2, F(1, 4), 0))
    row_bound = max(sum(abs(x) for x in row) for row in interior)
    require(row_bound == F(4, 3) < F(3, 2), "interior norm upper bound")
    require(F(13, 5) > F(3, 2) ** 2, "triangle trial vector exceeds interior")
    return {"invalid_inputs_rejected": len(invalid), "semantic_controls": 5}


def package_hashes():
    root = Path(__file__).resolve().parent
    result = {}
    for name in PACKAGE_FILES:
        path = root / name
        require(path.stat().st_size <= 262144, "package hash read capacity")
        result[name] = sha256(path.read_bytes()).hexdigest()
    return result


def main():
    receipt = {"status": "PASS_GAUSSIAN_HALF_SHIFT_ENVELOPE",
               "claim_type": "scoped written proof with exact finite corroboration",
               "python": platform.python_version(),
               "gaussians": check_gaussians(),
               "spectral_identity": check_spectral_identity(),
               "limit": check_limit(), "controls": check_controls(),
               "source_sha256": package_hashes()}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

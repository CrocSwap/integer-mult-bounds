#!/usr/bin/env python3
"""Exact bounded corroboration of the transient-leakage theorem."""

from dataclasses import dataclass, replace
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path


Matrix = tuple[tuple[Q, ...], ...]
FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def matrix(rows) -> Matrix:
    require(1 <= len(rows) <= 64, "row capacity")
    width = len(rows[0])
    require(1 <= width <= 64, "column capacity")
    require(all(len(row) == width for row in rows), "rectangular matrix")
    return tuple(tuple(Q(x) for x in row) for row in rows)


def identity(n: int) -> Matrix:
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def transpose(a: Matrix) -> Matrix:
    return tuple(zip(*a))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    require(len(a[0]) == len(b), "matrix product shape")
    columns = transpose(b)
    return matrix([[sum((x * y for x, y in zip(row, col)), Q(0))
                    for col in columns] for row in a])


def scale(c: Q, a: Matrix) -> Matrix:
    return matrix([[c * x for x in row] for row in a])


def add(a: Matrix, b: Matrix, sign: int = 1) -> Matrix:
    require((len(a), len(a[0])) == (len(b), len(b[0])), "matrix sum shape")
    return matrix([[x + sign * y for x, y in zip(ar, br)]
                   for ar, br in zip(a, b)])


def kron(a: Matrix, b: Matrix) -> Matrix:
    return matrix([[x * y for x in ar for y in br] for ar in a for br in b])


def sandwich(a: Matrix, p: Matrix) -> Matrix:
    return multiply(transpose(a), multiply(p, a))


def psd(a: Matrix, strict: bool = False) -> bool:
    """Symmetric Schur elimination, including the zero-diagonal case."""
    require(len(a) == len(a[0]), "square PSD input")
    require(a == transpose(a), "symmetric PSD input")
    b = [list(row) for row in a]
    for i in range(len(b)):
        pivot = b[i][i]
        if pivot < 0 or (strict and pivot == 0):
            return False
        if pivot == 0:
            if any(b[i][j] != 0 for j in range(i + 1, len(b))):
                return False
            continue
        for j in range(i + 1, len(b)):
            for k in range(j, len(b)):
                value = b[j][k] - b[j][i] * b[i][k] / pivot
                b[j][k] = value
                b[k][j] = value
    return True


@dataclass(frozen=True)
class Certificate:
    local_dimension: int
    active: Matrix
    leakage: Matrix
    transient: Matrix
    active_metric: Matrix
    transient_metric: Matrix
    left: Matrix
    right: Matrix
    rho: Q
    delta: Q
    left_squared: Q = Q(1)
    right_squared: Q = Q(1)


def validate(c: Certificate) -> None:
    d = c.local_dimension
    a, b = len(c.active_metric), len(c.transient_metric)
    require(1 <= d <= 3 and 1 <= a <= 3 and 1 <= b <= 3, "certificate capacity")
    require(0 <= c.rho < 1 and c.delta >= 0, "rate domain")
    require(c.left_squared >= 0 and c.right_squared >= 0, "boundary domain")
    for value, rows, cols in ((c.active, d*a, d*a), (c.leakage, d*a, d*b),
                              (c.transient, d*b, d*b), (c.active_metric, a, a),
                              (c.transient_metric, b, b), (c.left, len(c.left), a),
                              (c.right, b, len(c.right[0]))):
        require(len(value) == rows and all(len(row) == cols for row in value), "certificate shape")
    require(len(c.left) <= 3 and len(c.right[0]) <= 3, "role capacity")
    require(psd(c.active_metric, True) and psd(c.transient_metric, True), "positive metrics")
    pa = kron(identity(d), c.active_metric)
    pb = kron(identity(d), c.transient_metric)
    require(psd(add(pa, sandwich(c.active, pa), -1)), "active contraction")
    require(psd(add(scale(c.rho**2, pb), sandwich(c.transient, pb), -1)), "transient contraction")
    require(psd(add(scale(c.delta**2, pb), sandwich(c.leakage, pa), -1)), "coherent leakage")
    require(psd(add(scale(c.left_squared, c.active_metric),
                    multiply(transpose(c.left), c.left), -1)), "complete left boundary")
    require(psd(add(scale(c.right_squared, identity(len(c.right[0]))),
                    sandwich(c.right, c.transient_metric), -1)), "complete right boundary")


def block(a: Matrix, y: int, x: int, rows: int, cols: int) -> Matrix:
    return matrix([row[x*cols:(x+1)*cols] for row in a[y*rows:(y+1)*rows]])


def transfer(c: Certificate, y: int, x: int) -> Matrix:
    a, b = len(c.active_metric), len(c.transient_metric)
    aa = block(c.active, y, x, a, a)
    cc = block(c.leakage, y, x, a, b)
    dd = block(c.transient, y, x, b, b)
    return matrix([aa[i] + cc[i] for i in range(a)] +
                  [(Q(0),)*a + dd[i] for i in range(b)])


def literal_endpoint(c: Certificate, width: int) -> Matrix:
    require(1 <= width <= 4, "literal width capacity")
    a, b = len(c.active_metric), len(c.transient_metric)
    words = tuple(product(range(c.local_dimension), repeat=width))
    p, q = len(c.left), len(c.right[0])
    result = [[Q(0)] * (q * len(words)) for _ in range(p * len(words))]
    for yi, ys in enumerate(words):
        for xi, xs in enumerate(words):
            value = identity(a+b)
            for y, x in zip(ys, xs):
                value = multiply(value, transfer(c, y, x))
            corner = matrix([row[a:] for row in value[:a]])
            endpoint = multiply(c.left, multiply(corner, c.right))
            for i in range(p):
                for j in range(q):
                    result[i*len(words)+yi][j*len(words)+xi] = endpoint[i][j]
    return matrix(result)


def bound(c: Certificate, width: int) -> Q:
    require(1 <= width <= 64, "bound width capacity")
    return c.delta * (1-c.rho**width) / (1-c.rho)


def sharp_certificate(rho: Q, delta: Q) -> Certificate:
    return Certificate(2, identity(2), matrix([[delta, 0], [0, -delta]]),
                       scale(rho, identity(2)), identity(1), identity(1),
                       identity(1), identity(1), rho, delta)


def coupled_certificate(weighted: bool) -> Certificate:
    a = matrix([[0, 1, 0, 0], [-1, 0, 0, 0],
                [0, 0, 1, 0], [0, 0, 0, -1]])
    d = matrix([[0, 0, 1, 0], [0, 0, 0, -1],
                [0, 1, 0, 0], [1, 0, 0, 0]])
    cc = matrix([[0, 0, 0, 1], [0, 0, 1, 0],
                 [0, 1, 0, 0], [1, 0, 0, 0]])
    sa = matrix([[2, 0], [0, 1]]) if weighted else identity(2)
    ia = matrix([[Q(1, 2), 0], [0, 1]]) if weighted else identity(2)
    sd = matrix([[1, 0], [0, 3]]) if weighted else identity(2)
    ii = matrix([[1, 0], [0, Q(1, 3)]]) if weighted else identity(2)
    return Certificate(2, multiply(kron(identity(2), ia), multiply(a, kron(identity(2), sa))),
                       scale(Q(1, 32), multiply(kron(identity(2), ia), multiply(cc, kron(identity(2), sd)))),
                       scale(Q(1, 2), multiply(kron(identity(2), ii), multiply(d, kron(identity(2), sd)))),
                       sandwich(sa, identity(2)), sandwich(sd, identity(2)),
                       sa, ii, Q(1, 2), Q(1, 32))


def determinant(a: Matrix) -> Q:
    n = len(a)
    require(n <= 3, "determinant oracle capacity")
    result = Q(0)
    for perm in permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i+1, n))
        term = Q((-1)**inversions)
        for i in range(n):
            term *= a[i][perm[i]]
        result += term
    return result


def principal_minor_oracle(a: Matrix) -> bool:
    for k in range(1, len(a)+1):
        for indices in combinations(range(len(a)), k):
            minor = matrix([[a[i][j] for j in indices] for i in indices])
            if determinant(minor) < 0:
                return False
    return True


def check_psd_oracle() -> int:
    count = 0
    for values in product((-1, 0, 1), repeat=6):
        x, y, z, u, v, w = values
        a = matrix([[x, y, z], [y, u, v], [z, v, w]])
        require(psd(a) == principal_minor_oracle(a), "independent PSD oracle")
        count += 1
    require(count == 729, "PSD domain completeness")
    return count


def check_sharp_words() -> dict[str, int]:
    counts = {"families": 0, "word_endpoints": 0, "width_norms": 0}
    for rho in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4)):
        for delta in (Q(1, 8), Q(1, 1024)):
            c = sharp_certificate(rho, delta)
            validate(c)
            counts["families"] += 1
            for width in range(1, 13):
                maximum = Q(0)
                for word in product((0, 1), repeat=width):
                    value = Q(0)
                    for bit in word:
                        value = rho*value + delta*(1-2*bit)
                    maximum = max(maximum, abs(value))
                    counts["word_endpoints"] += 1
                require(maximum == bound(c, width), "sharp full diagonal norm")
                counts["width_norms"] += 1
    return counts


def check_literal_operators() -> dict[str, int]:
    fixtures = [sharp_certificate(rho, Q(1, 8)) for rho in (Q(0), Q(1, 2), Q(3, 4))]
    fixtures.extend((coupled_certificate(False), coupled_certificate(True)))
    mixed = replace(sharp_certificate(Q(1, 2), Q(1, 8)),
                    active=matrix([[Q(3, 5), Q(4, 5)], [-Q(4, 5), Q(3, 5)]]),
                    leakage=matrix([[0, Q(1, 8)], [Q(1, 8), 0]]))
    fixtures.append(mixed)
    counts = {"certificates": len(fixtures), "complete_matrices": 0, "physical_entries": 0}
    for c in fixtures:
        validate(c)
        for width in range(1, 5):
            e = literal_endpoint(c, width)
            squared = c.left_squared*c.right_squared*bound(c, width)**2
            require(psd(add(scale(squared, identity(len(e[0]))),
                            multiply(transpose(e), e), -1)), "complete operator error")
            counts["complete_matrices"] += 1
            counts["physical_entries"] += len(e)*len(e[0])
    for width in range(1, 5):
        require(literal_endpoint(fixtures[3], width) == literal_endpoint(fixtures[4], width),
                "weighted similarity preserves every endpoint entry")
    aa = block(fixtures[3].active, 0, 0, 2, 2)
    bb = block(fixtures[3].active, 1, 1, 2, 2)
    require(multiply(aa, bb) != multiply(bb, aa), "noncommuting virtual fixture")
    return counts


def check_metric_obstruction() -> int:
    """Check the two forced null-row equations in an independent finite grid."""
    count = 0
    for rho in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4)):
        for delta in (Q(1, 8), Q(1, 1024)):
            for x in range(1, 5):
                z = Q(x)*delta/(1-rho)
                metric = matrix([[x, z], [z, 1+z*z/Q(x)]])
                plus = matrix([[1, delta], [0, rho]])
                minus = matrix([[1, -delta], [0, rho]])
                kp = add(metric, sandwich(plus, metric), -1)
                km = add(metric, sandwich(minus, metric), -1)
                require(psd(metric, True), "obstruction positive metric")
                require(kp[0][0] == km[0][0] == 0, "preserved active eigenvector")
                require(kp[0][1] == 0 and km[0][1] == 2*x*delta, "incompatible null rows")
                require(psd(kp), "first sign really is contractive in this metric")
                require(not psd(km), "second sign rejects first-sign metric")
                count += 1
    return count


def check_rejections() -> list[str]:
    good = sharp_certificate(Q(1, 2), Q(1, 8))
    cases = (
        ("rho-one", replace(good, rho=Q(1))),
        ("negative-rho", replace(good, rho=Q(-1, 2))),
        ("negative-delta", replace(good, delta=Q(-1))),
        ("singular-metric", replace(good, active_metric=matrix([[0]]))),
        ("indefinite-metric", replace(good, transient_metric=matrix([[-1]]))),
        ("active-growth", replace(good, active=scale(Q(2), identity(2)))),
        ("transient-growth", replace(good, rho=Q(1, 4))),
        ("understated-leakage", replace(good, delta=Q(1, 16))),
        ("coherent-cross-input", replace(good, leakage=matrix([[Q(1, 8), Q(1, 8)], [0, 0]]))),
        ("omitted-left-role", replace(good, left=matrix([[1], [1]]))),
        ("omitted-right-role", replace(good, right=matrix([[1, 1]]))),
        ("bad-shape", replace(good, leakage=identity(1))),
        ("capacity", replace(good, local_dimension=4)),
    )
    rejected = []
    for name, bad in cases:
        try:
            validate(bad)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted invalid certificate: " + name)
    require(len(rejected) == len(cases), "rejection inventory")
    return rejected


def source_bindings() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    inventory = tuple(root.iterdir())
    require(len(inventory) == len(FILES), "package inventory")
    require({p.name for p in inventory} == set(FILES), "package filenames")
    bindings = {}
    for name in FILES:
        path = root / name
        require(path.is_file() and not path.is_symlink(), "regular package file")
        require(path.stat().st_size <= 131072, "source size capacity")
        bindings[name] = sha256(path.read_bytes()).hexdigest()
    return bindings


def main() -> None:
    report = {"claim_type": "scoped proof with finite exact corroboration",
              "psd_oracle_matrices": check_psd_oracle(),
              "sharp_family": check_sharp_words(),
              "literal_operators": check_literal_operators(),
              "metric_obstruction_fixtures": check_metric_obstruction(),
              "rejected_certificates": check_rejections(),
              "uniform_example": {"rho": "1/2", "delta": "1/1024", "supremum_error": "1/512"},
              "source_sha256": source_bindings(),
              "status": "PASS_TRANSFER_TRANSIENT_LEAKAGE"}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

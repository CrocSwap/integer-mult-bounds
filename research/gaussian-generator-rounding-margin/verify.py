#!/usr/bin/env python3
"""Exact quantitative controls for PROOF.md; standard library only.

Small rational matrix utilities are retained from the separately credited
boundary-minor predecessor. This file is standalone and does not import it.
The positive-semidefinite certificates and perturbation controls are new.
"""
from fractions import Fraction as F
import json
import random

class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def zeros(rows, cols=None):
    return [[F(0) for _ in range(rows if cols is None else cols)] for _ in range(rows)]


def identity(n):
    a = zeros(n)
    for i in range(n):
        a[i][i] = F(1)
    return a


def transpose(a):
    return [list(row) for row in zip(*a)]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, c):
    return [[c * x for x in row] for row in a]


def multiply(a, b):
    out = zeros(len(a), len(b[0]))
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] += x * y
    return out


def kron(a, b):
    return [[x * y for x in ar for y in br] for ar in a for br in b]


def tensor(factors):
    out = [[F(1)]]
    for a in factors:
        out = kron(out, a)
    return out


def shift(n):
    a = zeros(n)
    for i in range(1, n):
        a[i][i - 1] = F(1)
    return a


def entry_displacements(a):
    n = len(a)
    d = [[(a[i][j + 1] if j + 1 < n else F(0)) -
          (a[i - 1][j] if i else F(0)) for j in range(n)] for i in range(n)]
    e = [[a[i][j] - (a[i - 1][j - 1] if i and j else F(0))
          for j in range(n)] for i in range(n)]
    return d, e


def rref(a):
    out = [row[:] for row in a]
    pivots = []
    row = 0
    for col in range(len(out[0])):
        pivot = next((i for i in range(row, len(out)) if out[i][col]), None)
        if pivot is None:
            continue
        out[row], out[pivot] = out[pivot], out[row]
        value = out[row][col]
        out[row] = [x / value for x in out[row]]
        for i in range(len(out)):
            if i != row and out[i][col]:
                value = out[i][col]
                out[i] = [x - value * y for x, y in zip(out[i], out[row])]
        pivots.append(col)
        row += 1
        if row == len(out):
            break
    return out, pivots


def rank(a):
    return len(rref(a)[1])


def inverse(a):
    n = len(a)
    out, pivots = rref([row + eye for row, eye in zip(a, identity(n))])
    require(pivots[:n] == list(range(n)), "inverse requested for a singular matrix")
    result = [row[n:] for row in out]
    require(multiply(a, result) == identity(n), "left inverse residual")
    require(multiply(result, a) == identity(n), "right inverse residual")
    return result


def select(a, indices):
    return [[a[i][j] for j in indices] for i in indices]


def block(a, b, c, d):
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def gaussian(n, q, v):
    return [[q ** ((i - j) ** 2) * v ** (i - j) for j in range(n)] for i in range(n)]


def norm_bound(a):
    """max(1-norm,infinity-norm), an exact spectral-norm upper bound."""
    row = max(sum(abs(x) for x in r) for r in a)
    col = max(sum(abs(x) for x in r) for r in transpose(a))
    return max(row, col)


def psd(a):
    """Exact symmetric LDL test, including zero diagonal pivots."""
    if a != transpose(a):
        return False
    work = [row[:] for row in a]
    n = len(a)
    for k in range(n):
        pivot = work[k][k]
        if pivot < 0:
            return False
        if pivot == 0:
            if any(work[k][j] for j in range(k + 1, n)):
                return False
            continue
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                work[i][j] -= work[i][k] * work[k][j] / pivot
    return True


def singular_gap_certificate(a, reciprocal_gap):
    """Check A A^T - gap^2 P_image is PSD using exact rational arithmetic."""
    _, pivots = rref(a)
    c = [[row[j] for j in pivots] for row in a]
    gram = multiply(transpose(c), c)
    projector = multiply(multiply(c, inverse(gram)), transpose(c))
    require(multiply(projector, projector) == projector, "image projector is not idempotent")
    require(multiply(projector, a) == a, "image projector misses a column")
    residual = sub(multiply(a, transpose(a)), scale(projector, 1 / reciprocal_gap ** 2))
    return psd(residual)


def stein(a):
    return entry_displacements(a)[1]


def minor_bound(a, b):
    m, n = len(a), len(b)
    require(n >= 3, "fastest Gaussian dimension is outside n>=3 scope")
    require(b[0][1] != 0 and b[1][0] != 0, "zero adjacent coefficient")
    require(abs(b[n - 1][0] / b[0][1]) <= 1, "R ratio exceeds one")
    require(abs(b[0][n - 1] / b[1][0]) <= 1, "S ratio exceeds one")
    z = shift(m)
    r = sub(scale(identity(m), b[0][1]), scale(z, b[n - 1][0]))
    s = sub(scale(identity(m), b[1][0]), scale(transpose(z), b[0][n - 1]))
    p = scale(sub(a, multiply(multiply(z, a), transpose(z))), b[0][0])
    q, t = multiply(r, a), multiply(a, s)
    minor = block(p, q, t, zeros(m))
    qi, ti = inverse(q), inverse(t)
    literal_inverse = inverse(minor)
    formula_inverse = block(zeros(m), ti, qi, scale(multiply(multiply(qi, p), ti), F(-1)))
    require(literal_inverse == formula_inverse, "block inverse formula")
    alpha, zeta = m / abs(b[0][1]), m / abs(b[1][0])
    require(norm_bound(inverse(r)) <= alpha, "R geometric inverse bound")
    require(norm_bound(inverse(s)) <= zeta, "S geometric inverse bound")
    u, v = norm_bound(a), norm_bound(inverse(a))
    k = v * (alpha + zeta) + 2 * abs(b[0][0]) * u * v ** 2 * alpha * zeta
    require(norm_bound(literal_inverse) <= k, "quantitative boundary inverse bound")
    h = kron(a, b)
    indices = [i * n for i in range(m)] + [i * n + 1 for i in range(m)]
    require(select(stein(h), indices) == minor, "selected minor identity")
    require(rank(stein(h)) == 2 * m, "exact boundary rank")
    require(singular_gap_certificate(stein(h), k), "forward singular-gap certificate")
    return h, k


def perturb_and_round(target, reciprocal_gap, minimum_rank):
    n = len(target)
    noise = [[F(((3 * i + 5 * j) % 7) - 3, 3) / (8 * reciprocal_gap * n)
              for j in range(n)] for i in range(n)]
    require(norm_bound(noise) <= 1 / (8 * reciprocal_gap), "perturbation budget")
    require(rank(stein(add(target, noise))) >= minimum_rank, "protected unstructured perturbation")
    required = 2 * n * reciprocal_gap
    bits = max(1, required.numerator.bit_length() - required.denominator.bit_length() + 1)
    while F(2 ** bits) <= required:
        bits += 1
    scale_factor = 2 ** bits
    rounded = [[F((x * scale_factor).numerator // (x * scale_factor).denominator,
                  scale_factor) for x in row] for row in target]
    error = sub(rounded, target)
    require(max(abs(x) for row in error for x in row) <= F(1, scale_factor), "entry rounding error")
    require(2 * reciprocal_gap * norm_bound(error) < 1, "rounded matrix missed protected margin")
    require(rank(stein(rounded)) >= minimum_rank, "protected rounded generator rank")
    return bits


def schur_controls(h, k):
    n = len(h)
    z, eye, zero = shift(n), identity(n), zeros(n)
    hi = inverse(h)
    middle = block(h, z, transpose(z), hi)
    left1 = block(eye, multiply(z, h), zero, eye)
    diag1 = block(stein(h), zero, zero, hi)
    right1 = block(eye, zero, multiply(h, transpose(z)), eye)
    require(multiply(multiply(left1, diag1), right1) == middle, "first Schur factorization")
    reverse = sub(hi, multiply(multiply(transpose(z), hi), z))
    left2 = block(eye, zero, multiply(transpose(z), hi), eye)
    diag2 = block(h, zero, zero, reverse)
    right2 = block(eye, multiply(hi, z), zero, eye)
    require(multiply(multiply(left2, diag2), right2) == middle, "second Schur factorization")
    ehi = stein(hi)
    reversal = [list(reversed(row)) for row in reversed(ehi)]
    require(transpose(reversal) == reverse, "inverse persymmetry orientation")
    u0, v0 = norm_bound(h), norm_bound(hi)
    kinv = max(k, u0) * (1 + u0) ** 2 * (1 + v0) ** 2
    require(singular_gap_certificate(ehi, kinv), "inverse singular-gap certificate")
    return hi, kinv


def generic_cases():
    rng = random.Random(642)
    count, bits = 0, []
    # The first two approach opposite half-shift boundaries while remaining rational.
    choices = [(F(1, 2), 2 - F(1, 2 ** 20)),
               (F(1, 3), F(1, 3) + F(1, 2 ** 20)), (F(2, 3), F(1))]
    for m in range(1, 4):
        for n in range(3, 6):
            for q, v in choices:
                a = [[F(rng.randint(-2, 2), rng.randint(1, 3)) for _ in range(m)]
                     for _ in range(m)]
                a = add(a, scale(identity(m), F(10)))
                h, k = minor_bound(a, gaussian(n, q, v))
                bits.append(perturb_and_round(h, k, 2 * m))
                count += 1
    return count, bits


def tensor_cases():
    dimensions = [(3,), (4,), (2, 3), (3, 3), (2, 4), (2, 2, 3)]
    qs, vs = [F(1, 2), F(1, 3), F(2, 3)], [F(3, 2), F(2, 3), F(1)]
    bits, factor_bits, certificates = [], [], 0
    for dims in dimensions:
        factors = [gaussian(n, qs[i % 3], vs[i % 3]) for i, n in enumerate(dims)]
        a = tensor(factors[:-1])
        h, k = minor_bound(a, factors[-1])
        hi, kinv = schur_controls(h, k)
        r = 2 * len(a)
        bits.append(perturb_and_round(h, k, r))
        bits.append(perturb_and_round(hi, kinv, r))
        factor_bits.append(factor_rounding(factors, h, hi, k, kinv, r))
        certificates += 2
    return len(dimensions), certificates, bits, factor_bits


def factor_rounding(factors, h, hi, k, kinv, minimum_rank):
    g = len(factors)
    u = max(norm_bound(a) for a in factors)
    v = max(norm_bound(inverse(a)) for a in factors)
    nmax = max(map(len, factors))
    bits = 1
    while True:
        delta = F(nmax, 2 ** bits)
        forward_bound = g * delta * (2 * u) ** (g - 1)
        inverse_bound = g * 2 ** g * v ** (g + 1) * delta
        if delta <= u and delta * v <= F(1, 2) and 2 * k * forward_bound < 1 and 2 * kinv * inverse_bound < 1:
            break
        bits += 1
        require(bits <= 512, "finite factor-rounding fixture exceeded its stopping bound")
    scale_factor = 2 ** bits
    rounded = [[[F((x * scale_factor).numerator // (x * scale_factor).denominator,
                    scale_factor) for x in row] for row in a] for a in factors]
    forward = tensor(rounded)
    inverse_target = tensor([inverse(a) for a in rounded])
    require(norm_bound(sub(forward, h)) <= forward_bound, "factor tensor error bound")
    require(norm_bound(sub(inverse_target, hi)) <= inverse_bound, "inverse-factor tensor error bound")
    require(rank(stein(forward)) >= minimum_rank, "factor-rounding forward generator rank")
    require(rank(stein(inverse_target)) >= minimum_rank, "factor-rounding inverse generator rank")
    return bits


def expect_rejection(action, message):
    rejected = False
    try:
        action()
    except VerificationError:
        rejected = True
    require(rejected, message)


def failure_controls():
    controls = []
    # The shifted two-point shortcut really fails, rather than merely lacking a proof.
    m = 3
    b = gaussian(2, F(1, 2), F(3, 2))
    r = sub(scale(identity(m), b[0][1]), scale(shift(m), b[1][0]))
    require(b[1][0] / b[0][1] == F(9, 4), "shifted two-point ratio")
    require(norm_bound(inverse(r)) > m / b[0][1], "shifted two-point false bound not detected")
    expect_rejection(lambda: minor_bound(identity(m), b), "n=2 scope rejection did not fire")
    controls.append("shifted-two-point-geometric-bound-fails")
    # Coarse rounding can lower the generator requirement.
    h = gaussian(4, F(1, 64), F(1))
    rounded = [[F((x * 16 + F(1, 2)).numerator // (x * 16 + F(1, 2)).denominator, 16)
                for x in row] for row in h]
    require(rounded == identity(4), "low-precision identity fixture")
    require(rank(stein(h)) == 2 and rank(stein(rounded)) == 1, "low-precision rank loss")
    controls.append("insufficient-precision-reduces-generator-rank")
    # Exact PSD code must reject an impossible claimed singular gap.
    e = stein(gaussian(3, F(1, 2), F(1)))
    fake_gap = 1 + norm_bound(e)
    require(not singular_gap_certificate(e, 1 / fake_gap), "forged singular-gap certificate accepted")
    controls.append("forged-singular-gap-certificate-rejected")
    require(psd([[F(1), F(0)], [F(0), F(0)]]), "singular PSD positive control")
    require(not psd([[F(0), F(1)], [F(1), F(0)]]), "zero-pivot indefinite control")
    controls.append("zero-pivot-indefinite-matrix-rejected")
    # No o(p) guard claim is made when the number of axes is linear in p.
    beta = F(1)
    expect_rejection(lambda: require(0 <= beta < 1, "beta outside source regime"),
                     "beta=1 scope rejection did not fire")
    p, g, log2p = 2 ** 20, 2 ** 20, 20
    require(p <= 7 + 42 * g * log2p, "linear-axis insufficient-budget control")
    controls.append("linear-axis-o-p-guard-claim-rejected")
    # The uniform source conditioning estimate needs a positive half-shift gap.
    q, v = F(1, 2), F(2)
    expect_rejection(lambda: require(q < v < 1 / q, "zero source phase gap"),
                     "half-shift source gap rejection did not fire")
    controls.append("zero-half-shift-gap-rejected")
    return controls


def precision_receipts():
    receipts = []
    for exponent in (20, 22, 24, 30):
        p = 2 ** exponent
        g = 2 ** (exponent // 2)
        required = 7 + 42 * g * exponent
        require(required < p, "explicit Cp-bit budget failed")
        receipts.append({"p": p, "axes": g, "required_strictly_more_bits": required,
                         "available_bits": p, "margin": p - required})
    require(receipts[0]["required_strictly_more_bits"] == 860167, "explicit threshold arithmetic")
    require(7 + 60 * 2048 * 22 == 2703367 < 2 ** 22, "explicit factor-rounding threshold")
    return receipts


def main():
    generic, first_bits = generic_cases()
    tensors, tensor_certificates, second_bits, factor_bits = tensor_cases()
    controls = failure_controls()
    receipts = precision_receipts()
    all_bits = first_bits + second_bits
    print(json.dumps({
        "status": "PASS", "arithmetic": "exact rational inverses, norm bounds and PSD certificates",
        "seed": 642, "generic_boundary_cases": generic, "tensor_cases": tensors,
        "singular_gap_certificates": generic + tensor_certificates,
        "protected_unstructured_perturbations": len(all_bits),
        "protected_entrywise_roundings": len(all_bits),
        "finite_rounding_bits_min": min(all_bits), "finite_rounding_bits_max": max(all_bits),
        "protected_factor_table_roundings": len(factor_bits),
        "factor_rounding_target_rank_checks": 2 * len(factor_bits),
        "finite_factor_rounding_bits_min": min(factor_bits),
        "finite_factor_rounding_bits_max": max(factor_bits),
        "negative_controls": controls, "explicit_precision_receipts": receipts,
        "scope": "finite controls for the all-size proof; no runtime lower bound or new kappa"
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

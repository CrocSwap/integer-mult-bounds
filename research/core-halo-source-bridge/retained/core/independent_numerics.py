"""Independent exact numerical/budget oracle for the complete current Core join.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is an observer, never an online payload producer. It imports no source
factor builder, rounded page solver, physical controller or author oracle.
The final target is formed by pivoting the original complete Q, not by
multiplying the producer's five factors. All failures survive python -O.
"""
from __future__ import annotations
from fractions import Fraction as Q
from hashlib import sha256
import json
from typing import Iterable, Sequence


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def pow2(exponent: int) -> Q:
    return Q(1 << exponent) if exponent >= 0 else Q(1, 1 << -exponent)


def ceil_log2(value: Q | int) -> int:
    value = Q(value)
    need(value > 0, "positive logarithm argument")
    k = value.numerator.bit_length() - value.denominator.bit_length()
    return k if pow2(k) >= value else k + 1


def ceil_div(a: int, b: int) -> int:
    need(type(a) is int and a >= 0 and type(b) is int and b > 0,
         "nonnegative numerator and positive divisor")
    return (a + b - 1) // b


def dyadic_at_least(value: Q | int) -> int:
    return 1 << max(0, ceil_log2(value))


def matrix(rows: Iterable[Iterable[Q | int]]) -> tuple[tuple[Q, ...], ...]:
    answer = tuple(tuple(map(Q, row)) for row in rows)
    need(bool(answer) and all(len(row) == len(answer[0]) for row in answer),
         "nonempty rectangular exact matrix")
    return answer


def identity(n: int) -> tuple[tuple[Q, ...], ...]:
    need(type(n) is int and n > 0, "positive identity dimension")
    return matrix((int(i == j) for j in range(n)) for i in range(n))


def multiply(left, right):
    need(len(left[0]) == len(right), "compatible exact matrix dimensions")
    return matrix((sum((a * right[k][j] for k, a in enumerate(row)), Q())
                   for j in range(len(right[0]))) for row in left)


def inverse(original):
    """Full pivoted Gauss-Jordan, independently of the source Schur/LU path."""
    n = len(original)
    need(n > 0 and all(len(row) == n for row in original), "square inverse target")
    eye = identity(n)
    a = [list(map(Q, row)) + list(eye[i]) for i, row in enumerate(original)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda i: abs(a[i][column]))
        need(a[pivot][column] != 0, "invertible original exact matrix")
        a[pivot], a[column] = a[column], a[pivot]
        scale = a[column][column]
        a[column] = [x / scale for x in a[column]]
        for row in range(n):
            if row != column:
                scale = a[row][column]
                if scale:
                    a[row] = [x - scale * y for x, y in zip(a[row], a[column])]
    need(tuple(tuple(row[:n]) for row in a) == eye, "independent inverse residual")
    result = tuple(tuple(row[n:]) for row in a)
    need(multiply(original, result) == eye, "original left inverse residual")
    return result


def row_norm(a) -> Q:
    return max(sum(map(abs, row), Q()) for row in a)


def column_norm(a) -> Q:
    return row_norm(tuple(zip(*a)))


def bandwidth(a) -> int:
    return max((abs(i - j) for i, row in enumerate(a)
                for j, value in enumerate(row) if value), default=0)


def five_factors(original, interior: Sequence[int], *, broad: bool = False):
    """Reconstruct factors for checking, never accept producer A/B/C/F pages."""
    q = matrix(original)
    n = len(q)
    need(all(len(row) == n for row in q), "complete square source Q")
    ids = tuple(interior)
    need(ids == tuple(sorted(set(ids))) and all(0 <= i < n for i in ids),
         "increasing original interior indices")
    boundary = tuple(i for i in range(n) if i not in ids)
    need(bool(boundary), "nonempty complete boundary")
    ai = inverse(tuple(tuple(q[i][j] for j in ids) for i in ids)) if ids else ()
    a = tuple(tuple(q[i][j] for j in ids) for i in ids)
    b = tuple(tuple(q[i][j] for j in boundary) for i in ids)
    c = tuple(tuple(q[i][j] for j in ids) for i in boundary)
    d = tuple(tuple(q[i][j] for j in boundary) for i in boundary)
    schur = matrix((q[i][j] - sum((q[i][u] * ai[u0][v0] * q[v][j]
                    for u0, u in enumerate(ids) for v0, v in enumerate(ids)), Q())
                    for j in boundary) for i in boundary)
    finv = None if broad else inverse(schur)
    plus = [list(row) for row in identity(n)]
    minus = [list(row) for row in identity(n)]
    for i0, i in enumerate(ids):
        for j0, j in enumerate(ids):
            plus[i][j], minus[i][j] = a[i0][j0], ai[i0][j0]
    upper = [list(row) for row in identity(n)]
    for i0, i in enumerate(ids):
        for j0, j in enumerate(boundary):
            upper[i][j] = (1 if broad else -1) * b[i0][j0]
    lower = [list(row) for row in identity(n)]
    if broad:
        for i0, i in enumerate(boundary):
            for j0, j in enumerate(ids):
                lower[i][j] = c[i0][j0]
            for j0, j in enumerate(boundary):
                lower[i][j] = schur[i0][j0]
        factors = (matrix(plus), matrix(upper), matrix(minus), matrix(lower), matrix(plus))
    else:
        for i0, i in enumerate(boundary):
            for j0, j in enumerate(ids):
                lower[i][j] = -sum((finv[i0][k] * c[k][j0]
                                    for k in range(len(boundary))), Q())
            for j0, j in enumerate(boundary):
                lower[i][j] = finv[i0][j0]
        factors = (matrix(minus), matrix(lower), matrix(plus), matrix(upper), matrix(minus))
    product = identity(n)
    for factor in factors:
        product = multiply(factor, product)
    target = q if broad else inverse(q)
    need(product == target, "five exact factors equal independently formed complete source target")
    exposed = tuple(i for i in range(n) if i in boundary or
                    any(q[i][j] or q[j][i] for j in boundary))
    return dict(factors=factors, target=target, I=ids, J=boundary, E=exposed,
                A=a, Ainv=ai, B=b, C=c, D=d, F=schur,
                h=dyadic_at_least(max(Q(1), *(max(row_norm(m), column_norm(m))
                                             for m in factors))))


def apply_matrix(a, values):
    need(len(a[0]) == len(values) and all(len(z) == 2 for z in values),
         "complete complex vector for exact matrix")
    return tuple(tuple(sum((coefficient * values[k][part]
                           for k, coefficient in enumerate(row)), Q())
                       for part in (0, 1)) for row in a)


def apply_axis(a, values, axis: int, axes: int):
    side = len(a)
    need(all(len(row) == side for row in a) and len(values) == side ** axes
         and 0 <= axis < axes, "complete tensor axis oracle")
    stride = side ** axis
    result = list(values)
    for block in range(0, len(values), stride * side):
        for offset in range(stride):
            positions = tuple(block + offset + k * stride for k in range(side))
            transformed = apply_matrix(a, tuple(values[i] for i in positions))
            for i, value in zip(positions, transformed):
                result[i] = value
    return tuple(result)


def exact_complete_target(source_contexts, values, *, broad=False):
    """Original Q or independently pivoted Q^-1 on every actual context/axis."""
    need(bool(source_contexts) and bool(source_contexts[0]), "nonempty complete source family")
    g, side = len(source_contexts[0]), len(source_contexts[0][0])
    volume = side ** g
    need(len(values) == len(source_contexts) * volume, "all contexts included in oracle")
    answer = []
    for c, sources in enumerate(source_contexts):
        need(len(sources) == g, "same complete axis count per context")
        state = tuple(values[c * volume:(c + 1) * volume])
        for axis, q in enumerate(sources):
            need(len(q) == side, "uniform actual complete-core side")
            state = apply_axis(matrix(q) if broad else inverse(q), state, axis, g)
        answer.extend(state)
    return tuple(answer)


def decode_pairs(values, precision: int):
    need(type(precision) is int and precision >= 0, "nonnegative encoded grid")
    need(all(len(z) == 2 and all(type(x) is int for x in z) for z in values),
         "integer complex-pair observer")
    return tuple(tuple(Q(x, 1 << precision) for x in z) for z in values)


def squared_norm(values) -> Q:
    return sum((x * x for z in values for x in z), Q())


def squared_error(left, right) -> Q:
    need(len(left) == len(right), "same complete output extent")
    return sum(((x - y) ** 2 for a, b in zip(left, right) for x, y in zip(a, b)), Q())


def fraction_digest(value: Q):
    value = Q(value)
    raw = (hex(value.numerator) + "/" + hex(value.denominator)).encode()
    return dict(numerator_bits=abs(value.numerator).bit_length(),
                denominator_bits=value.denominator.bit_length(), sha256=sha256(raw).hexdigest())


def check_complete_return(source_contexts, input_words, input_precision,
                          output_words, output_precision, target, *, broad=False):
    original = decode_pairs(input_words, input_precision)
    actual = decode_pairs(output_words, output_precision)
    wanted = exact_complete_target(source_contexts, original, broad=broad)
    error = squared_error(actual, wanted)
    need(error <= pow2(-2 * target), "complete original-Q target error")
    return dict(records=len(actual), contexts=len(source_contexts),
                axes=len(source_contexts[0]), mode="broad" if broad else "narrow",
                error_squared=fraction_digest(error), target_bits=target)


def budget(n: int, g: int, h: int, target: int, incoming: int,
           initial_radius_bits: int):
    need(all(type(x) is int for x in (n, g, h, target, incoming, initial_radius_bits))
         and n >= 1 and 1 <= g <= n and h >= 1 and h & (h - 1) == 0
         and target >= 1 and incoming >= 0 and initial_radius_bits >= 0,
         "complete dyadic numerical budget domain")
    H = h ** g
    td = target + ceil_log2(10 * H ** 4)
    R0 = 1 << initial_radius_bits
    R2 = dyadic_at_least((H + 1) ** 5 * (R0 + 1))
    Rstar = dyadic_at_least(2 * (h + 1) ** (g + 1) * (R2 + 1))
    V2 = 1 << ceil_div(n, 2)
    q = td + ceil_log2(V2 * g * h ** (g - 1))
    need(5 * H ** 4 * pow2(-td) <= pow2(-target - 1), "five exact suffix allowances")
    need(V2 * g * h ** (g - 1) * pow2(-q) <= pow2(-td), "complete-field sparse allowance")
    radius = Q(R0)
    for _ in range(5):
        need(radius <= R2, "actual input admitted to complete dense call")
        radius = H * radius + pow2(-td)
        need(radius <= R2, "actual output radius including local defect")
    partial = Q(R2)
    for _ in range(g + 1):
        need(2 * partial <= Rstar, "actual sparse partial input complex-l1 radius")
        partial = h * partial + 1
    need(2 * partial <= Rstar, "actual sparse final/micro-step radius")
    return dict(n=n, g=g, h=h, H=H, target=target, incoming=incoming,
                R0=R0, R2=R2, Rstar=Rstar, stage_target=td,
                local_target=q, V2=V2,
                broad_micro_target=q + ceil_log2(2 * (h + 1)))


def sparse_allocation(budget_row, *, pbar: int, sparsity: int, gamma: Q | int,
                      dense_minimum: int, descriptor: int = 1):
    """Exact sufficient source inequalities, not a finite-output fitted guard."""
    need(pbar >= 1 and sparsity >= 1 and Q(gamma) >= 0 and dense_minimum >= 1
         and descriptor >= 1, "positive sparse/source allocation inputs")
    q, radius = budget_row["local_target"], budget_row["Rstar"]
    inverse_grid = q + 45 + 16 * ceil_log2(pbar) + ceil_log2(radius)
    action_grid = q + ceil_log2(sparsity * radius + 6) + 1
    P = max(budget_row["incoming"], dense_minimum, inverse_grid, action_grid)
    wi = P + 52 + 16 * ceil_log2(pbar) + ceil_log2(radius)
    wa = P + 2 + ceil_log2(max(Q(1), Q(gamma)) * (radius + 1))
    width = max(wi, wa, descriptor.bit_length() + 2)
    need(P >= budget_row["incoming"], "exact upward common-grid lift")
    need(Q(2 ** 44 * pbar ** 16 * radius, 1 << P) <= pow2(-q - 1),
         "retained conservative inverse error with eta=2^(1-P)")
    need(Q(sparsity * radius + 6, 1 << P) <= pow2(-q - 1),
         "retained supplied-action allocation")
    need(2 ** 48 * pbar ** 16 * radius < (1 << (width - P - 1)),
         "conservative scalar state fits signed inverse carrier")
    need(max(Q(1), Q(gamma)) * radius < (1 << (width - P - 1)),
         "actual forward target/source states fit signed carrier")
    return dict(P=P, width=width, inverse_grid=inverse_grid, action_grid=action_grid)


def product_counts(a: int, j: int, m: int, b: int):
    need(a >= j >= 1 and m >= 1 and b >= 2 and b & (b - 1) == 0,
         "nonempty physical complete-line geometry")
    z = ceil_div(2 * m, b)
    inverse_calls = (2 * (2 * ceil_div(a, b) - 1)
                     + 2 * (2 * ceil_div(j, b) - 1)) * z
    action_calls = 2 * (2 * ceil_div(2 * a, b) - 1) * z
    ell = b.bit_length() - 1
    return dict(inverse_calls=inverse_calls, action_calls=action_calls,
                inverse_scalar_leaves=inverse_calls * 7 ** ell,
                action_scalar_leaves=action_calls * 7 ** ell,
                batches=z, block=b)


def signed_convert(integer: int, incoming: int, outgoing: int,
                   old_width: int, new_width: int) -> int:
    """Independent exact numeric specification for a physically paid converter."""
    need(all(type(x) is int for x in (integer, incoming, outgoing, old_width, new_width))
         and outgoing >= incoming >= 0 and old_width >= 2 and new_width >= 2,
         "upward grid and positive signed converter widths")
    need(-(1 << (old_width - 1)) <= integer < 1 << (old_width - 1),
         "source signed word fits")
    value = integer << (outgoing - incoming)
    need(-(1 << (new_width - 1)) <= value < 1 << (new_width - 1),
         "target signed word fits without discarding a value bit")
    need(Q(integer, 1 << incoming) == Q(value, 1 << outgoing),
         "signed conversion has zero numerical defect")
    return value


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

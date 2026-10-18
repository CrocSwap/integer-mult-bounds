#!/usr/bin/env python3
"""Independent finite algebra checks for the weighted exact-root-swap theorem.

Prepared by conorholds with substantial OpenAI Codex assistance.  Apache-2.0.
Credits: DreamingOfClouds/#1590 (two-total lemma), #2816/#2862 (root-swap
and carrier framework), and the retained E8/root-code predecessor lineage.

This file imports no primary checker or generated certificate.  Its fixtures
corroborate the written theorem; they do not enumerate all coefficient spaces.
The theorem concerns exact swaps.  Converting general weight-eight vectors to
swaps requires the package's separately stated geometric bridge hypotheses.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
import json


class CheckError(ValueError):
    """A mathematical or coverage condition failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


@dataclass(frozen=True)
class Gaussian:
    """An exact element of Q(i), also used for rational fixtures."""

    real: Fraction = Fraction(0)
    imag: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "real", Fraction(self.real))
        object.__setattr__(self, "imag", Fraction(self.imag))

    @staticmethod
    def of(value: object) -> Gaussian:
        if isinstance(value, Gaussian):
            return value
        return Gaussian(Fraction(value))

    def __add__(self, other: object) -> Gaussian:
        z = self.of(other)
        return Gaussian(self.real + z.real, self.imag + z.imag)

    __radd__ = __add__

    def __neg__(self) -> Gaussian:
        return Gaussian(-self.real, -self.imag)

    def __sub__(self, other: object) -> Gaussian:
        return self + (-self.of(other))

    def __rsub__(self, other: object) -> Gaussian:
        return self.of(other) - self

    def __mul__(self, other: object) -> Gaussian:
        z = self.of(other)
        return Gaussian(
            self.real * z.real - self.imag * z.imag,
            self.real * z.imag + self.imag * z.real,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> Gaussian:
        z = self.of(other)
        norm = z.real * z.real + z.imag * z.imag
        if not norm:
            raise ZeroDivisionError("division by zero in Q(i)")
        return self * Gaussian(z.real / norm, -z.imag / norm)

    def __bool__(self) -> bool:
        return bool(self.real or self.imag)


ZERO = Gaussian()
ONE = Gaussian(1)
I = Gaussian(0, 1)
Vector = tuple[Gaussian, ...]
Root = tuple[int, ...]  # doubled ordinary Euclidean E8 coordinates


def solve_columns(columns: list[Vector], target: Vector) -> tuple[Gaussian, ...] | None:
    """Solve the actual shared coefficient equations; free variables are zero."""
    require(all(len(c) == len(target) for c in columns), "column shape")
    width = len(columns)
    rows = [[c[r] for c in columns] + [target[r]] for r in range(len(target))]
    pivot_rows: list[tuple[int, int]] = []
    row = 0
    for col in range(width):
        pivot = next((r for r in range(row, len(rows)) if rows[r][col]), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        scale = rows[row][col]
        rows[row] = [x / scale for x in rows[row]]
        for r in range(len(rows)):
            if r != row and rows[r][col]:
                scale = rows[r][col]
                rows[r] = [x - scale * y for x, y in zip(rows[r], rows[row])]
        pivot_rows.append((row, col))
        row += 1
    if any(not any(r[:width]) and r[-1] for r in rows):
        return None
    answer = [ZERO] * width
    for r, col in pivot_rows:
        answer[col] = rows[r][-1]
    require(
        all(sum((answer[j] * columns[j][r] for j in range(width)), ZERO) == target[r]
            for r in range(len(target))),
        "coefficient reconstruction",
    )
    return tuple(answer)


def rational_rank(rows: list[tuple[int, ...]] | list[list[Fraction]]) -> int:
    if not rows:
        return 0
    a = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for col in range(len(a[0])):
        at = next((j for j in range(pivot, len(a)) if a[j][col]), None)
        if at is None:
            continue
        a[pivot], a[at] = a[at], a[pivot]
        scale = a[pivot][col]
        a[pivot] = [x / scale for x in a[pivot]]
        for j in range(pivot + 1, len(a)):
            scale = a[j][col]
            if scale:
                a[j] = [x - scale * y for x, y in zip(a[j], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def f2_rank(values: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in values:
        x = value
        while x:
            at = x.bit_length() - 1
            if at in pivots:
                x ^= pivots[at]
            else:
                pivots[at] = x
                break
    return len(pivots)


def in_f2_span(values: list[int], value: int) -> bool:
    return f2_rank(values + [value]) == f2_rank(values)


def determinant(matrix: list[list[int]]) -> int:
    """Fraction-free Bareiss determinant, including singular controls."""
    a = [row[:] for row in matrix]
    if not a:
        return 1
    sign, previous = 1, 1
    for col in range(len(a) - 1):
        at = next((j for j in range(col, len(a)) if a[j][col]), None)
        if at is None:
            return 0
        if at != col:
            a[col], a[at] = a[at], a[col]
            sign = -sign
        pivot = a[col][col]
        for r in range(col + 1, len(a)):
            for c in range(col + 1, len(a)):
                numerator = a[r][c] * pivot - a[r][col] * a[col][c]
                require(numerator % previous == 0, "Bareiss exact division")
                a[r][c] = numerator // previous
            a[r][col] = 0
        previous = pivot
    return sign * a[-1][-1]


def canonical(root: Root) -> Root:
    return root if next(x for x in root if x) > 0 else tuple(-x for x in root)


def e8_lines() -> tuple[Root, ...]:
    roots: set[Root] = set()
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=8):
        if sum(x < 0 for x in signs) % 2 == 0:
            roots.add(canonical(signs))
    require(len(roots) == 120, "E8 line inventory")
    return tuple(sorted(roots))


def inner(left: Root, right: Root) -> int:
    value = sum(x * y for x, y in zip(left, right))
    require(value % 4 == 0, "integral E8 inner product")
    return value // 4


def lattice_member(root: Root) -> bool:
    if all(x % 2 == 0 for x in root):
        return sum(root) % 4 == 0
    return all(x % 2 for x in root) and sum(root) % 4 == 0


class Geometry:
    def __init__(self) -> None:
        self.roots = e8_lines()
        self.index = {r: j for j, r in enumerate(self.roots)}
        # An independent D7 + half-root basis.  Its Gram determinant is one,
        # so inner products with it identify E8/2E8 without a coordinate solve.
        basis: list[Root] = [(1,) * 8]
        for j in range(1, 7):
            row = [0] * 8
            row[j], row[j + 1] = 2, -2
            basis.append(tuple(row))
        basis.append((0, 0, 0, 0, 0, 0, 2, 2))
        gram = [[inner(a, b) for b in basis] for a in basis]
        require(determinant(gram) == 1, "unimodular independent label basis")
        self.labels = tuple(
            1 | sum((inner(r, b) % 2) << (j + 1) for j, b in enumerate(basis))
            for r in self.roots
        )
        require(len(set(self.labels)) == 120, "distinct root labels")
        require(all(x & 1 for x in self.labels), "affine labels")
        require(f2_rank(list(self.labels)) == 9, "full label rank")
        self.gram = tuple(tuple(inner(a, b) for b in self.roots) for a in self.roots)
        self.frames = tuple(
            self.root_index(tuple(2 if i == 2 * j else 2 * sign if i == 2 * j + 1 else 0
                                  for i in range(8)))
            for j in range(4) for sign in (-1, 1)
        )
        require(all(self.gram[a][b] == 0 for a, b in combinations(self.frames, 2)),
                "orthogonal frame")

    def root_index(self, root: Root) -> int:
        return self.index[canonical(root)]

    def support(self, vector: Vector) -> set[int]:
        require(len(vector) == 120, "root vector shape")
        return {j for j, x in enumerate(vector) if x}

    def weight(self, vector: Vector) -> int:
        return f2_rank([self.labels[j] for j in self.support(vector)])

    def vector(self, entries: dict[int, object]) -> Vector:
        return tuple(Gaussian.of(entries.get(j, 0)) for j in range(120))

    def root_codeword(self, root: int) -> Vector:
        return tuple(Gaussian(x) for x in self.gram[root])


def combine(basis: list[Vector], coefficients: tuple[Gaussian, ...]) -> Vector:
    require(len(basis) == len(coefficients), "coefficient count")
    return tuple(sum((a * q[j] for a, q in zip(coefficients, basis)), ZERO)
                 for j in range(120))


def validate_swap(g: Geometry, root: int, tau: Vector) -> None:
    require(0 <= root < 120 and len(tau) == 120, "swap shape")
    require(tau[root] == ONE, "swap pivot must equal one")
    require(all(not tau[s] for s in range(120) if s != root and g.gram[root][s] == 0),
            "swap has orthogonal leakage")
    actual = tuple(x - 2 * y for x, y in zip(g.root_codeword(root), tau))
    require(g.weight(actual) <= 8, "literal corrected codeword is not weight eight")


def root_swap_witnesses(
    g: Geometry, basis: list[Vector]
) -> dict[int, tuple[tuple[Gaussian, ...], Vector]]:
    """Exact swaps for arbitrary supplied coefficient spaces, not support unions."""
    zero = (ZERO,) * 120
    for j, q in enumerate(basis):
        require(len(q) == 120, "basis vector shape")
        require(any(q), "zero basis vector")
        require(solve_columns(basis[:j], q) is None, "dependent basis")
    witnesses = {}
    for t in range(120):
        constrained = [t] + [s for s in range(120) if s != t and g.gram[t][s] == 0]
        columns = [tuple(q[s] for s in constrained) for q in basis]
        target = (ONE,) + (ZERO,) * (len(constrained) - 1)
        coefficients = solve_columns(columns, target)
        if coefficients is not None:
            tau = combine(basis, coefficients) if basis else zero
            validate_swap(g, t, tau)
            witnesses[t] = (coefficients, tau)
    return witnesses


def independent_roots(g: Geometry, candidates: list[int]) -> list[int]:
    chosen: list[int] = []
    for t in candidates:
        if rational_rank([g.roots[s] for s in chosen + [t]]) > len(chosen):
            chosen.append(t)
    return chosen


def binary_subrank(g: Geometry, rows: list[int], columns: list[int]) -> int:
    return f2_rank([
        sum((int(s == t or g.gram[s][t] == 0)) << j for j, t in enumerate(columns))
        for s in rows
    ])


def audit_two_total_fitting(
    pairing: list[list[int]], p: list[list[Gaussian]], q: list[list[Gaussian]],
    ratio_order: list[Gaussian] | None = None,
) -> dict[str, int]:
    """Check all intermediate Lemma A inequalities over Q(i), without ordering it."""
    size = len(pairing)
    require(all(len(row) == size for row in pairing), "pairing shape")
    require(all(x in (0, 1) for row in pairing for x in row)
            and all(pairing[t][t] == 1 for t in range(size)), "binary unit-diagonal pairing")
    require(len(p) == len(q) == size and all(len(x) == 2 for x in p + q), "two-total shape")
    matrix = [[sum((p[t][j] * q[s][j] for j in range(2)), ZERO)
               for s in range(size)] for t in range(size)]
    require(all(matrix[t][t] for t in range(size)), "zero fitting diagonal")
    require(all(not matrix[t][s] for t in range(size) for s in range(size)
                if t != s and pairing[t][s]), "fitting incidence is nonzero")
    rsets = [{t for t in range(size) if p[t][j]} for j in range(2)]
    asets = [{t for t in range(size) if q[t][j]} for j in range(2)]
    dsets = [rsets[j] & asets[j] for j in range(2)]
    shared = dsets[0] & dsets[1]
    require(dsets[0] | dsets[1] == set(range(size)), "uncovered diagonal")

    def subrank(rows: set[int], columns: set[int]) -> int:
        cs = sorted(columns)
        return f2_rank([sum(pairing[t][s] << j for j, s in enumerate(cs)) for t in sorted(rows)])

    ranks = [subrank(rsets[j], asets[j]) for j in range(2)]
    shared_rank = subrank(shared, shared)
    for j in range(2):
        require(ranks[j] >= len(dsets[j] - shared) + shared_rank, "private pivot inequality")
    alpha = {t: p[t][0] / p[t][1] for t in shared}
    beta = {t: -q[t][1] / q[t][0] for t in shared}
    values = list(dict.fromkeys(list(alpha.values()) + list(beta.values())))
    order = values if ratio_order is None else ratio_order
    require(len(order) == len(set(order)) and set(order) == set(values), "incomplete ratio order")
    positions = {v: j for j, v in enumerate(order)}
    less = {t for t in shared if positions[alpha[t]] < positions[beta[t]]}
    greater = shared - less
    require(all(alpha[t] != beta[t] for t in shared), "tied diagonal ratios")
    for subset, key, increasing in [(less, alpha, False), (greater, beta, True)]:
        for t in subset:
            for s in subset:
                if t != s and pairing[t][s]:
                    require((positions[key[s]] > positions[key[t]]) == increasing,
                            "finite-order triangular implication")
        require(subrank(subset, subset) == len(subset), "triangular block rank")
    require(shared_rank >= max(len(less), len(greater)), "shared rank inequality")
    require(sum(ranks) >= size, "two-total lower bound")
    return {"size": size, "shared": len(shared), "rank_sum": sum(ranks)}


def fitting_from_swaps(
    g: Geometry, basis: list[Vector], witnesses: dict[int, tuple[tuple[Gaussian, ...], Vector]]
) -> dict[str, int]:
    chosen = independent_roots(g, sorted(witnesses))
    require(len(basis) <= 2, "two-total fitting used outside scope")
    p = [[basis[j][s] if j < len(basis) else ZERO for j in range(2)] for s in chosen]
    q = [[witnesses[t][0][j] if j < len(basis) else ZERO for j in range(2)] for t in chosen]
    pairing = [[int(s == t or g.gram[s][t] == 0) for t in chosen] for s in chosen]
    result = audit_two_total_fitting(pairing, p, q)
    ranks = []
    for j in range(len(basis)):
        rows = [s for s in chosen if basis[j][s]]
        columns = [t for t in chosen if witnesses[t][0][j]]
        ranks.append(binary_subrank(g, rows, columns))
        require(ranks[-1] <= g.weight(basis[j]), "block exceeds actual basis weight")
    require(len(chosen) <= sum(ranks), "fitting root-rank consequence")
    return result


def low_partitions(total: int, maximum: int | None = None) -> list[tuple[int, ...]]:
    if total == 0:
        return [()]
    maximum = min(total, total if maximum is None else maximum)
    return [(head,) + tail for head in range(maximum, 0, -1)
            for tail in low_partitions(total - head, head)]


def check_profile_coverage(profiles: set[tuple[int, ...]]) -> None:
    needed = {p for cost in range(1, 8) for p in low_partitions(cost)
              if sum(w >= 3 for w in p) >= 2}
    require(needed == {(3, 3), (4, 3), (3, 3, 1)}, "low-cost partition derivation")
    require(profiles == needed, "incomplete exceptional-profile coverage")


def audit_fixture(g: Geometry, name: str, basis: list[Vector], expected_weights: tuple[int, ...],
                  expected_rank: int | None = None) -> dict[str, object]:
    weights = tuple(g.weight(q) for q in basis)
    require(weights == expected_weights, f"{name}: incorrect charged weights")
    witnesses = root_swap_witnesses(g, basis)
    rank = rational_rank([g.roots[t] for t in witnesses])
    cost = sum(weights)
    require(rank <= cost, f"{name}: weighted root-swap rank bound")
    if expected_rank is not None:
        require(rank == expected_rank, f"{name}: actual independent-root rank")
    overrank = [j for j, q in enumerate(basis)
                if rational_rank([g.roots[t] for t in g.support(q)]) > weights[j]]
    outside_count = 0
    if len(overrank) <= 1:
        ordinary = [t for j, q in enumerate(basis) if j not in overrank for t in g.support(q)]
        o_rank = rational_rank([g.roots[t] for t in ordinary])
        outside = [t for t in witnesses
                   if rational_rank([g.roots[s] for s in ordinary] + [g.roots[t]]) > o_rank]
        outside_count = len(outside)
        if overrank:
            exception = basis[overrank[0]]
            require(all(t in g.support(exception) for t in outside), "outside-O support binding")
            require(all(g.gram[s][t] != 0 for s, t in combinations(outside, 2)),
                    "outside-O roots not pairwise nonorthogonal")
            require(f2_rank([g.labels[t] for t in outside]) == len(outside),
                    "outside-O orthonormal label independence")
            require(len(outside) <= weights[overrank[0]], "one-exception rank allowance")
        else:
            require(not outside, "ordinary pieces generated an outside-O root")
    if len(basis) <= 2:
        fitting_from_swaps(g, basis, witnesses)
    if cost <= 7 and len(overrank) >= 2:
        require(tuple(sorted(weights, reverse=True)) in {(3, 3), (4, 3), (3, 3, 1)},
                "missing exceptional proof profile")
        if len(basis) == 3:
            a, b = (g.support(basis[j]) for j in overrank)
            require(len(a) == len(b) == 4, "three-piece exceptional support size")
            require(all(g.gram[s][t] == 0 for s, t in combinations(a, 2)), "first orthogonal quartet")
            require(all(g.gram[s][t] == 0 for s, t in combinations(b, 2)), "second orthogonal quartet")
            ordinary_j = next(j for j in range(3) if j not in overrank)
            unit = g.support(basis[ordinary_j])
            require(len(unit) == 1, "ordinary piece is not a unit")
            if len(a & b) <= 1:
                require(set(witnesses) <= unit, "uncancelled orthogonal quartet coordinate")
            else:
                require(len(a | b | unit) <= 7, "quartet union exceeds allowance")
    return {"name": name, "weights": list(weights), "cost": cost,
            "eligible": len(witnesses), "root_rank": rank, "overrank_pieces": len(overrank),
            "one_exception_outside_o": outside_count if len(overrank) == 1 else None}


def quartet_checks(g: Geometry) -> dict[str, int]:
    pairs: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for a, b in combinations(range(120), 2):
        pairs[g.labels[a] ^ g.labels[b]].append((a, b))
    quartets: set[tuple[int, ...]] = set()
    for group in pairs.values():
        for left, right in combinations(group, 2):
            if len(set(left + right)) == 4:
                quartets.add(tuple(sorted(left + right)))
    overrank, signed = 0, 0
    for ids in sorted(quartets):
        require(f2_rank([g.labels[j] for j in ids]) == 3, "dependent affine quartet rank")
        gram = [[g.gram[a][b] for b in ids] for a in ids]
        if determinant(gram):
            overrank += 1
            require(all(g.gram[a][b] == 0 for a, b in combinations(ids, 2)),
                    "overrank quartet is not orthogonal")
            for signs in product((-1, 1), repeat=4):
                summed = [sum(sign * g.roots[j][c] for sign, j in zip(signs, ids)) for c in range(8)]
                require(all(x % 2 == 0 for x in summed), "half-sum integer doubled coordinates")
                half = tuple(x // 2 for x in summed)
                require(lattice_member(half) and inner(half, half) == 2, "signed E8 half-sum")
                signed += 1
    require(overrank > 0 and len(quartets) > overrank, "quartet controls not exercised")
    return {"dependent_quartets": len(quartets), "overrank_orthogonal_quartets": overrank,
            "signed_half_sums": signed}


def kernel_sharpness_checks(g: Geometry) -> list[dict[str, int]]:
    """Literal cost-72 bases of C_E plus one through seven frame units.

    Restriction has exactly the P112 root-code space and kernel the displayed
    units.  The assertion that that code has no weight-at-most-seven vector
    uses the separately stated source/geometry theorem, not these fixtures.
    """
    code = [g.root_codeword(t) for t in g.frames]
    require(rational_rank([g.roots[t] for t in g.frames]) == 8, "frame code basis")
    restricted = [t for t in range(120) if t not in g.frames]
    reports = []
    for count in range(1, 8):
        units = [g.vector({t: 1}) for t in g.frames[:count]]
        changed = [tuple(x - 2 * y for x, y in zip(code[j], units[j]))
                   if j < count else code[j] for j in range(8)]
        basis = units + changed
        weights = [g.weight(q) for q in basis]
        require(weights == [1] * count + [8] * count + [9] * (8 - count),
                "literal kernel-sharpness profile")
        require(sum(weights) == 72, "literal kernel-sharpness invoice")
        require(all(not value.imag for q in basis for value in q), "rational sharpness basis")
        full_rank = rational_rank([[x.real for x in q] for q in basis])
        restricted_rank = rational_rank([[q[t].real for t in restricted] for q in basis])
        require(full_rank == 8 + count and restricted_rank == 8,
                "literal full/restricted basis dimensions")
        for j in range(8):
            recovered = tuple(x + 2 * y for x, y in zip(changed[j], units[j])) \
                if j < count else changed[j]
            require(recovered == code[j], "literal code containment")
            require(tuple(changed[j][t] for t in restricted)
                    == tuple(code[j][t] for t in restricted), "restriction is the root code")
        require(all(not q[t] for q in units for t in restricted), "unit kernel support")
        reports.append({"frame_units": count, "full_dimension": full_rank,
                        "restricted_dimension": restricted_rank,
                        "kernel_dimension": full_rank - restricted_rank, "basis_cost": sum(weights)})
    return reports


def run_checks() -> dict[str, object]:
    g = Geometry()
    require(I * I == Gaussian(-1), "Q(i) field control")
    fixtures: list[dict[str, object]] = []
    rejected = 0

    def reject(action, name: str) -> None:
        nonlocal rejected
        try:
            action()
        except CheckError:
            rejected += 1
        else:
            raise CheckError(f"negative control accepted: {name}")

    def root(a: int, b: int, sign: int = 1) -> int:
        v = [0] * 8
        v[a], v[b] = 2, 2 * sign
        return g.root_index(tuple(v))

    def indicator(ids: list[int] | tuple[int, ...], values: list[object] | None = None) -> Vector:
        return g.vector(dict(zip(ids, [1] * len(ids) if values is None else values)))

    first = [root(0, j) for j in (1, 2, 3)]
    second = [root(4, j) for j in (5, 6, 7)]
    unit = root(0, 4, -1)
    fixtures.append(audit_fixture(g, "sharp-3-3-1", [indicator(first), indicator(second), indicator([unit])],
                                  (3, 3, 1), 7))
    fixtures.append(audit_fixture(g, "complex-two-total-sharp", [indicator(first, [1, I, 1 + I]),
                                                                indicator(second[:2], [I, 2 - I])],
                                  (3, 2), 5))
    fixtures.append(audit_fixture(g, "two-overrank-3-3", [indicator(g.frames[:4]), indicator(g.frames[4:])],
                                  (3, 3), 0))
    fixtures.append(audit_fixture(g, "two-overrank-3-3-positive",
                                  [indicator(g.frames[:4]), indicator(g.frames[:4], [1, 1, 1, 2])],
                                  (3, 3), 1))
    # A full orthogonal frame has affine label rank four and real rank eight.
    fixtures.append(audit_fixture(g, "two-overrank-4-3", [indicator(g.frames), indicator(g.frames[:4], [1, 2, 3, 4])],
                                  (4, 3), 0))
    overlap_one = [
        root(0, 1, -1), root(4, 5, -1),
        g.root_index((1, 1, 1, 1, 1, 1, 1, 1)),
        g.root_index((1, 1, -1, -1, 1, 1, -1, -1)),
    ]
    quartet_pairs = {
        0: list(g.frames[4:]),
        1: overlap_one,
        2: list(g.frames[:2]) + list(g.frames[4:6]),
        4: list(g.frames[:4]),
    }
    for overlap, b in quartet_pairs.items():
        a = list(g.frames[:4])
        require(len(a) == len(b) == 4 and len(set(a) & set(b)) == overlap, "quartet fixture overlap")
        fixtures.append(audit_fixture(g, f"orthogonal-3-3-1-overlap-{overlap}",
                                      [indicator(a), indicator(b, [1, 2, 3, 4]), indicator([unit])],
                                      (3, 3, 1)))
    fixtures.append(audit_fixture(g, "one-exception-actual-space",
                                  [indicator(g.frames[:4])] + [indicator([j]) for j in g.frames[:3]],
                                  (3, 1, 1, 1), 4))
    independent = independent_roots(g, list(range(120)))
    fixtures.append(audit_fixture(g, "sharp-seven-units", [indicator([j]) for j in independent[:7]],
                                  (1,) * 7, 7))
    fixtures.append(audit_fixture(g, "cost-eight-ambient-bound", [indicator([j]) for j in g.frames],
                                  (1,) * 8, 8))

    old_roots = [
        (0, 0, 0, 0, 0, 2, -2, 0), (0, 0, 0, 0, 0, 2, 0, -2),
        (0, 0, 0, 2, 0, -2, 0, 0), (1, -1, -1, -1, -1, 1, -1, -1),
        (1, -1, 1, -1, 1, 1, -1, -1),
    ]
    old_ids = [g.root_index(r) for r in old_roots]
    frame = g.root_index((2, 2, 0, 0, 0, 0, 0, 0))
    q5 = indicator(old_ids)
    require(g.weight(q5) == 5 and rational_rank(old_roots) == 5, "old carrier actual cost/rank")
    require(all(g.gram[a][b] != 0 for a, b in combinations(old_ids, 2)), "old carrier clique")
    require(all(g.gram[t][frame] == 0 for t in old_ids), "old carrier frame orthogonality")
    xor = 0
    for t in old_ids:
        xor ^= g.labels[t]
    require(xor == g.labels[frame], "old carrier frame-label relation")
    restricted = [s for s in range(120) if s not in g.frames]

    def restricted_weight(v: Vector) -> int:
        return f2_rank([g.labels[s] for s in restricted if v[s]])

    restricted_vectors = [q5] + [tuple(x - 2 * y for x, y in zip(g.root_codeword(t), q5)) for t in old_ids]
    carriers = 0
    for vector in restricted_vectors:
        labels = [g.labels[s] for s in restricted if vector[s]]
        carriers += any(in_f2_span(labels, g.labels[f]) for f in g.frames)
    require([restricted_weight(v) for v in restricted_vectors] == [5] + [8] * 5,
            "old carrier literal restricted vectors")
    require(carriers == 6, "old carrier counterexample not reproduced")
    reject(lambda: require(carriers <= 5, "false old carrier count"), "carrier count shortcut")
    fixtures.append(audit_fixture(g, "old-carrier-full-rank-control", [q5, indicator([frame])], (5, 1), 6))

    # Non-orderable coefficient-field test with both private and shared lines.
    values = [ONE, I, 1 + I, 2 - I, -1 + I, 3 + 2 * I]
    p = [[ONE, ZERO], [ZERO, ONE]] + [[v, ONE] for v in values]
    q = [[ONE, ZERO], [ZERO, ONE]] + [[ONE, -values[(j + 1) % len(values)]] for j in range(len(values))]
    matrix = [[sum((p[t][j] * q[s][j] for j in range(2)), ZERO) for s in range(8)] for t in range(8)]
    pairing = [[int(t == s or not matrix[t][s]) for s in range(8)] for t in range(8)]
    complex_lemma = audit_two_total_fitting(pairing, p, q)
    audit_two_total_fitting(pairing, p, q, list(reversed(values)))
    reject(lambda: audit_two_total_fitting(pairing, p, q, values[:-1]), "incomplete finite order")
    wrong_pairing = [row[:] for row in pairing]
    row, col = next((t, s) for t in range(8) for s in range(8)
                    if t != s and matrix[t][s])
    wrong_pairing[row][col] = 1
    reject(lambda: audit_two_total_fitting(wrong_pairing, p, q), "nonzero fitting incidence")
    wrong_diagonal = [row[:] for row in pairing]
    wrong_diagonal[0][0] = 0
    reject(lambda: audit_two_total_fitting(wrong_diagonal, p, q), "missing pairing diagonal")

    single_quad = [indicator(g.frames[:4])]
    actual = root_swap_witnesses(g, single_quad)
    require(not actual, "orthogonal support shortcut control")
    reject(lambda: require(set(actual) == set(g.frames[:4]), "support is not a coefficient space"),
           "support-only eligibility")
    tau = indicator([first[0]])
    wrong = list(tau)
    orthogonal = next(s for s in range(120) if g.gram[first[0]][s] == 0)
    wrong[orthogonal] = ONE
    reject(lambda: validate_swap(g, first[0], tuple(wrong)), "orthogonal leakage")
    reject(lambda: validate_swap(g, first[0], (ZERO,) * 120), "missing swap pivot")
    reject(lambda: root_swap_witnesses(g, [q5, q5]), "dependent purported basis")
    reject(lambda: audit_fixture(g, "undercharge", [q5], (4,)), "undercharged basis weight")
    profiles = {(3, 3), (4, 3), (3, 3, 1)}
    check_profile_coverage(profiles)
    reject(lambda: check_profile_coverage(profiles - {(3, 3, 1)}), "incomplete profile list")
    quartets = quartet_checks(g)
    sharpness = kernel_sharpness_checks(g)
    return {
        "scope": "finite-independent-algebra-controls-not-an-exhaustion-of-L",
        "roots": 120, "coefficient_field": "Q(i)", "fixtures": fixtures,
        "eligible_witnesses": sum(int(f["eligible"]) for f in fixtures),
        "complex_two_total": complex_lemma, "old_carrier_count": carriers,
        "old_carrier_cost": 5, "exception_profiles": [list(p) for p in sorted(profiles)],
        "quartets": quartets, "rejected_controls": rejected,
        "kernel_sharpness": sharpness,
        "cost_ge_8": "root rank at most eight; no counterexample asserted",
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), sort_keys=True))
    print("PASS_E8_D0_INDEPENDENT_ALGEBRA")

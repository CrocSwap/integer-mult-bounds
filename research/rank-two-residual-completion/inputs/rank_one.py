"""Exact rank-one-residual completion in the original binary symplectic space.

Produced by Nick Petalas. Apache-2.0.
The reduction and lower bound build on Krzysztof Wojt, PR5097.
Vectors store e coordinates below f coordinates. No signed/phase API is implied.
"""

MAX_QUBITS = 16


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def pairing(x: int, y: int, n: int) -> int:
    mask = (1 << n) - 1
    return (((x & mask) & (y >> n)).bit_count()
            ^ ((y & mask) & (x >> n)).bit_count()) & 1


def turn(x: int, axis: int, n: int) -> int:
    return x ^ (axis if pairing(x, axis, n) else 0)


def apply_word(x: int, word: tuple[int, ...], n: int) -> int:
    for axis in word:
        x = turn(x, axis, n)
    return x


def linear_combination(rows: tuple[int, ...], coefficients: int) -> int:
    result = 0
    for i, row in enumerate(rows):
        if (coefficients >> i) & 1:
            result ^= row
    return result


def elimination(rows: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return independent input indices and a basis of coefficient relations."""
    pivots: dict[int, tuple[int, int]] = {}
    selected = []
    relations = []
    for i, original in enumerate(rows):
        row, coefficients = original, 1 << i
        for pivot in sorted(pivots, reverse=True):
            if (row >> pivot) & 1:
                other, relation = pivots[pivot]
                row ^= other
                coefficients ^= relation
        if row:
            pivots[row.bit_length() - 1] = (row, coefficients)
            selected.append(i)
        else:
            relations.append(coefficients)
    return tuple(selected), tuple(relations)


def validate(n: int, source: tuple[int, ...], image: tuple[int, ...]) -> None:
    require(type(n) is int and 1 <= n <= MAX_QUBITS, "unsupported dimension")
    require(type(source) is tuple and type(image) is tuple, "use immutable tuples")
    require(len(source) == len(image) <= 2 * n, "source/image lengths")
    limit = 1 << (2 * n)
    require(all(type(v) is int and 0 <= v < limit for v in source + image),
            "binary vector outside ambient space")
    require(len(elimination(source)[0]) == len(source), "dependent source basis")
    require(len(elimination(image)[0]) == len(image), "noninjective image")
    for i, x in enumerate(source):
        for j, y in enumerate(source):
            require(pairing(x, y, n) == pairing(image[i], image[j], n),
                    "partial map does not preserve pairings")


def residual(n: int, source: tuple[int, ...], image: tuple[int, ...]
             ) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    displacement = tuple(x ^ y for x, y in zip(source, image))
    indices, _ = elimination(displacement)
    basis = tuple(displacement[i] for i in indices)
    lifts = tuple(source[i] for i in indices)
    rows = tuple(sum(pairing(u, d, n) << j for j, d in enumerate(basis))
                 for u in lifts)
    return basis, lifts, rows


def solve_pairings(n: int, constraints: tuple[tuple[int, int], ...]) -> int:
    pivots: dict[int, tuple[int, int]] = {}
    mask = (1 << n) - 1
    for vector, value in constraints:
        row = ((vector & mask) << n) | (vector >> n)
        for pivot in sorted(pivots, reverse=True):
            if (row >> pivot) & 1:
                other, rhs = pivots[pivot]
                row ^= other
                value ^= rhs
        if row:
            pivots[row.bit_length() - 1] = (row, value)
        else:
            require(value == 0, "inconsistent pairing equations")
    result = 0
    for pivot in sorted(pivots):
        row, rhs = pivots[pivot]
        if rhs ^ ((row & result).bit_count() & 1):
            result |= 1 << pivot
    require(all(pairing(vector, result, n) == value
                for vector, value in constraints), "pairing solution failed")
    return result


def upper_correction(n: int, source: tuple[int, ...], image: tuple[int, ...]
                     ) -> tuple[int, ...]:
    """PR5097's at-most-two-per-displacement reduction, implemented locally."""
    correction = []
    initial_rank = len(residual(n, source, image)[0])
    for _ in range(initial_rank):
        displacement = tuple(x ^ y for x, y in zip(source, image))
        indices, relations = elimination(displacement)
        if not indices:
            break
        i = indices[0]
        u, p = source[i], displacement[i]
        if pairing(u, p, n):
            axes = (p,)
        else:
            fixed = tuple(linear_combination(source, relation) for relation in relations)
            constraints = tuple((k, 0) for k in fixed) + ((u, 1), (p, 0))
            a = solve_pairings(n, constraints)
            axes = (a, a ^ p)
        require(all(axes), "zero correction axis")
        image = tuple(apply_word(y, axes, n) for y in image)
        require(len(residual(n, source, image)[0]) < len(indices),
                "correction did not decrease displacement rank")
        correction.extend(axes)
    require(image == source, "upper correction did not finish")
    return tuple(correction)


def complete(n: int, source: tuple[int, ...], image: tuple[int, ...]
             ) -> tuple[int, ...]:
    """Attain the exact 2r-1 minimum, rejecting other residual-form ranks."""
    validate(n, source, image)
    basis, _, rows = residual(n, source, image)
    r = len(basis)
    require(len(elimination(rows)[0]) == 1, "residual form must have rank one")
    candidates = tuple(1 << i for i in range(r)) + tuple(
        (1 << i) | (1 << j) for i in range(r) for j in range(i))
    axis = None
    for coefficients in candidates:
        value = 0
        for i, row in enumerate(rows):
            if (coefficients >> i) & 1:
                value ^= (row & coefficients).bit_count() & 1
        if value:
            axis = linear_combination(basis, coefficients)
            break
    require(axis is not None and axis != 0, "missing anisotropic pivot")
    reduced = tuple(turn(y, axis, n) for y in image)
    reduced_basis, _, reduced_rows = residual(n, source, reduced)
    require(len(reduced_basis) == r - 1 and not any(reduced_rows),
            "rank-one pivot did not leave a zero form")
    correction = (axis,) + upper_correction(n, source, reduced)
    word = tuple(reversed(correction))
    require(len(word) == 2 * r - 1, "word length does not attain the lower bound")
    require(tuple(apply_word(x, word, n) for x in source) == image,
            "completion does not realize the partial contract")
    return word

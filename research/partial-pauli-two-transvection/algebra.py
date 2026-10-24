"""Low-length binary symplectic extensions, with bounded executable inputs."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def omega(v: int, w: int, n: int) -> int:
    mask = (1 << n) - 1
    return (((v & mask) & (w >> n)).bit_count()
            + ((v >> n) & (w & mask)).bit_count()) & 1


def span(basis: tuple[int, ...]) -> set[int]:
    require(len(basis) <= 18, "span capacity exceeded")
    result = {0}
    for vector in basis:
        result |= {x ^ vector for x in tuple(result)}
    return result


def turn_word(v: int, axes: tuple[int, ...], n: int) -> int:
    for axis in axes:
        if omega(v, axis, n):
            v ^= axis
    return v


def validate(n: int, source: tuple[int, ...], target: tuple[int, ...]) -> None:
    require(type(n) is int and 0 <= n <= 9, "expected integer 0 <= n <= 9")
    require(type(source) is tuple and type(target) is tuple, "expected tuples")
    require(len(source) == len(target) <= 2 * n, "invalid basis lengths")
    for basis in (source, target):
        require(all(type(v) is int and 0 < v < 1 << (2 * n) for v in basis),
                "invalid nonzero binary vector")
        require(len(span(basis)) == 1 << len(basis), "dependent basis")
    for v, image_v in zip(source, target):
        for w, image_w in zip(source, target):
            require(omega(v, w, n) == omega(image_v, image_w, n),
                    "map does not preserve the symplectic form")


def solve_pairings(n: int, vectors: tuple[int, ...], values: tuple[int, ...]) -> int:
    """Solve omega(vectors[j], answer) = values[j] by binary elimination."""
    require(len(vectors) == len(values) <= 19, "linear-system capacity exceeded")
    pivots: dict[int, tuple[int, int]] = {}
    mask = (1 << n) - 1
    for vector, value in zip(vectors, values):
        row = ((vector & mask) << n) | (vector >> n)
        rhs = value
        for column in range(2 * n):
            if (row >> column) & 1:
                if column not in pivots:
                    pivots[column] = (row, rhs)
                    break
                old_row, old_rhs = pivots[column]
                row ^= old_row
                rhs ^= old_rhs
        else:
            require(rhs == 0, "inconsistent pairing system")
    answer = 0
    for column in range(2 * n - 1, -1, -1):
        if column in pivots:
            row, rhs = pivots[column]
            if ((row & answer).bit_count() & 1) != rhs:
                answer |= 1 << column
    return answer


class Decision:
    __slots__ = ("residual_rank", "residual_form", "minimum", "lower_bound", "axes")

    def __init__(self, residual_rank: int, residual_form: tuple[tuple[int, ...], ...],
                 minimum: int | None, lower_bound: int, axes: tuple[int, ...] | None):
        self.residual_rank = residual_rank
        self.residual_form = residual_form
        self.minimum = minimum
        self.lower_bound = lower_bound
        self.axes = axes


def displacement_data(n: int, source: tuple[int, ...], target: tuple[int, ...]
                      ) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    images: tuple[int, ...] = ()
    preimages: tuple[int, ...] = ()
    for v, w in zip(source, target):
        if (v ^ w) not in span(images):
            images += (v ^ w,)
            preimages += (v,)
    form = tuple(tuple(omega(v, d, n) for d in images) for v in preimages)
    return images, form


def two_axes(images: tuple[int, ...], form: tuple[tuple[int, ...], ...]
             ) -> tuple[int, int]:
    """Diagonalize a nonsingular nonalternating two-dimensional residual form."""
    vectors = (images[0], images[1], images[0] ^ images[1])
    coordinates = ((1, 0), (0, 1), (1, 1))
    for i, left in enumerate(coordinates):
        norm = sum(left[j] * form[j][k] * left[k]
                   for j in range(2) for k in range(2)) & 1
        if norm:
            for h, right in enumerate(coordinates):
                pairing = sum(right[j] * form[j][k] * left[k]
                              for j in range(2) for k in range(2)) & 1
                if h != i and pairing == 0:
                    return vectors[i], vectors[h]
    raise ValueError("no triangular residual basis")


def low_length(n: int, source: tuple[int, ...], target: tuple[int, ...]) -> Decision:
    """Decide length <= 2, and the nonsingular alternating rank-two boundary.

    minimum=None supplies only lower_bound, never infeasibility. Axes are in
    execution order, followed by an optional Pauli sign correction.
    """
    validate(n, source, target)
    images, form = displacement_data(n, source, target)
    rank = len(images)
    axes: tuple[int, ...]
    if rank == 0:
        axes = ()
    elif rank == 1:
        d = images[0]
        if form[0][0]:
            axes = (d,)
        else:
            values = tuple(int(v != w) for v, w in zip(source, target)) + (0,)
            a = solve_pairings(n, source + (d,), values)
            axes = (a, a ^ d)
    elif rank == 2:
        determinant = (form[0][0] * form[1][1]) ^ (form[0][1] * form[1][0])
        if determinant == 0:
            return Decision(rank, form, None, 3, None)
        if form[0][0] == form[1][1] == 0:
            axes = (images[0], images[1], images[0] ^ images[1])
        else:
            axes = two_axes(images, form)
    else:
        return Decision(rank, form, None, rank, None)
    require(all(axis != 0 for axis in axes), "zero transvection axis")
    require(all(turn_word(v, axes, n) == w for v, w in zip(source, target)),
            "constructed word violates the contract")
    return Decision(rank, form, len(axes), len(axes), axes)

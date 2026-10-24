"""Binary partial symplectic completion, with explicit bounded linear algebra.

Krzysztof Wojt with OpenAI Codex assistance. Apache-2.0.
Vectors pack (x_0,...,x_{n-1},z_0,...,z_{n-1}) into low-to-high bits.
Words list axes in chronological application order. No predecessor code imported.
"""

MAX_QUBITS = 9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairing(left, right, n):
    mask = (1 << n) - 1
    return (((left & mask) & (right >> n)).bit_count()
            + ((right & mask) & (left >> n)).bit_count()) & 1


def turn(vector, axis, n):
    return vector ^ (axis if pairing(vector, axis, n) else 0)


def apply_word(vector, axes, n):
    for axis in axes:
        vector = turn(vector, axis, n)
    return vector


def linear_combination(columns, mask):
    result = 0
    for index, column in enumerate(columns):
        if (mask >> index) & 1:
            result ^= column
    return result


def echelon(columns):
    """Return pivot -> (value, original-column mask), and kernel masks."""
    pivots = {}
    kernel = []
    for index, column in enumerate(columns):
        value, coefficients = column, 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (value, coefficients)
                break
            old, old_coefficients = pivots[pivot]
            value ^= old
            coefficients ^= old_coefficients
        if not value:
            kernel.append(coefficients)
    return pivots, tuple(kernel)


def rank(columns):
    return len(echelon(columns)[0])


def validate(n, source, target):
    require(type(n) is int and 1 <= n <= MAX_QUBITS, "invalid dimension")
    require(isinstance(source, (tuple, list)), "source must be a sequence")
    require(isinstance(target, (tuple, list)), "target must be a sequence")
    require(len(source) == len(target) <= 2 * n, "invalid basis length")
    for vector in tuple(source) + tuple(target):
        require(type(vector) is int and 0 < vector < (1 << (2 * n)),
                "invalid basis vector")
    require(rank(source) == len(source), "dependent source basis")
    require(rank(target) == len(target), "noninjective target")
    for i, left in enumerate(source):
        for j, right in enumerate(source):
            require(pairing(left, right, n) == pairing(target[i], target[j], n),
                    "map does not preserve the symplectic pairing")


def residual_data(n, source, target):
    validate(n, source, target)
    difference = tuple(u ^ v for u, v in zip(source, target))
    pivots, kernel = echelon(difference)
    records = tuple(pivots[key] for key in sorted(pivots))
    displacement = tuple(value for value, _ in records)
    lifts = tuple(linear_combination(source, mask) for _, mask in records)
    form = tuple(sum(pairing(u, d, n) << j for j, d in enumerate(displacement))
                 for u in lifts)
    fixed = tuple(linear_combination(source, mask) for mask in kernel)
    return displacement, lifts, form, fixed


def solve_pairings(n, equations):
    """Solve omega(vector, a)=rhs; free variables are set to zero."""
    pivots = {}
    mask = (1 << n) - 1
    for vector, rhs in equations:
        row = (vector >> n) | ((vector & mask) << n)
        value = rhs
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (row, value)
                break
            old, old_value = pivots[pivot]
            row ^= old
            value ^= old_value
        require(row != 0 or value == 0, "inconsistent pairing equations")
    answer = 0
    for pivot in sorted(pivots):
        row, rhs = pivots[pivot]
        if ((row & answer).bit_count() & 1) != rhs:
            answer ^= 1 << pivot
    require(all(pairing(v, answer, n) == rhs for v, rhs in equations),
            "pairing solution check failed")
    return answer


def reduction_word(n, source, target):
    """Complete any valid partial map in at most twice its displacement rank."""
    validate(n, source, target)
    current = tuple(target)
    initial_rank = rank(tuple(u ^ v for u, v in zip(source, current)))
    corrections = []
    for _ in range(initial_rank):
        difference = tuple(u ^ v for u, v in zip(source, current))
        old_rank = rank(difference)
        if old_rank == 0:
            break
        _, kernel = echelon(difference)
        fixed = tuple(linear_combination(source, mask) for mask in kernel)
        index = next(i for i, value in enumerate(difference) if value)
        u, delta = source[index], difference[index]
        if pairing(u, delta, n):
            axes = (delta,)
        else:
            equations = tuple((k, 0) for k in fixed) + ((u, 1), (delta, 0))
            axis = solve_pairings(n, equations)
            axes = (axis, axis ^ delta)
        require(all(0 < a < (1 << (2 * n)) for a in axes), "invalid axis")
        require(all(apply_word(k, axes, n) == k for k in fixed), "fixed-space loss")
        current = tuple(apply_word(v, axes, n) for v in current)
        new_rank = rank(tuple(u ^ v for u, v in zip(source, current)))
        require(new_rank < old_rank, "rank did not decrease")
        corrections.extend(axes)
    require(current == tuple(source), "incomplete reduction")
    word = tuple(reversed(corrections))
    require(len(word) <= 2 * initial_rank, "completion bound exceeded")
    require(tuple(apply_word(u, word, n) for u in source) == tuple(target),
            "completion endpoint mismatch")
    return word


def exact_completion(n, source, target):
    """Solve zero residual forms at any rank, and rank-two rank-one forms.

    Other nonzero forms are deliberately outside this successor's exact API.
    The lower bound r + nullity(b) itself applies to every partial isometry.
    """
    displacement, _, form, _ = residual_data(n, source, target)
    r, form_rank = len(displacement), rank(form)
    minimum = 2 * r - form_rank
    if form_rank == 0:
        word = reduction_word(n, source, target)
    else:
        require(r == 2 and form_rank == 1, "outside exact classification")
        axis = 0
        for coefficients in (1, 2, 3):
            quadratic = (coefficients & linear_combination(form, coefficients)).bit_count() & 1
            if quadratic:
                axis = linear_combination(displacement, coefficients)
                break
        require(axis != 0, "missing anisotropic residual vector")
        reduced = tuple(turn(v, axis, n) for v in target)
        new_displacement, _, new_form, _ = residual_data(n, source, reduced)
        require(len(new_displacement) == 1 and rank(new_form) == 0,
                "singular Schur complement mismatch")
        word = reduction_word(n, source, reduced) + (axis,)
    require(len(word) == minimum, "sharp length mismatch")
    require(tuple(apply_word(u, word, n) for u in source) == tuple(target),
            "sharp endpoint mismatch")
    return {"displacement_rank": r, "form_rank": form_rank,
            "minimum": minimum, "axes": word}

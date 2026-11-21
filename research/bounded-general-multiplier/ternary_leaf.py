"""Lower a split rank-one address exchange over Z/3**w. Apache-2.0."""

from itertools import chain


def select_pivot(u, v):
    """Use only the low row of the cover and the two rank-one factors."""
    return next(i for i, (a, b) in enumerate(zip(u, v, strict=True)) if a % 3 and b % 3)


def ordered_chart(u, v, pivot, modulus):
    """Write P=b c^t in pivot order, with b[0]=1 and c[0] a unit."""
    order = list(range(len(u)))
    order[0], order[pivot] = order[pivot], order[0]
    unit = u[pivot] % modulus
    inverse = pow(unit, -1, modulus)
    b = [u[i] * inverse % modulus for i in order]
    c = [v[i] * unit % modulus for i in order]
    return order, b, c


def lower_slot(n, slot):
    """Return the target, source and chart index. All targets follow their source."""
    sweep, offset = divmod(slot, n - 1)
    i = offset + 1
    if sweep == 0:
        return i, 0, i
    if sweep == 1:
        return 2 * n - 1, n + offset, n - i
    if sweep == 2:
        return n + offset, 0, n - i
    if sweep == 3:
        return 2 * n - 1, i, i
    raise IndexError(slot)


def lower_coefficient(sweep, i, b, c, a0, ai, h_inverse, modulus):
    """A single coefficient reads at most two ancestral head weights."""
    if sweep == 0:
        return -ai * b[i] * pow(a0, -1, modulus) % modulus
    if sweep == 1:
        return c[i] * h_inverse % modulus
    if sweep == 2:
        return b[i] * pow(a0, -1, modulus) % modulus
    if sweep == 3:
        return -c[i] * h_inverse * pow(ai, -1, modulus) % modulus
    raise IndexError(sweep)


def pivot_pairs(n, pivot):
    if not pivot:
        return ()
    a, b, c, d = 0, pivot, 2 * n - 1, 2 * n - 1 - pivot
    return (a, c), (b, d), (a, d), (b, c)


def exchange(fields, head, tail, weights, modulus):
    """Execute one weighted reversed child with weights in head order."""
    left, right = fields[head], fields[tail]
    for j, weight in enumerate(weights):
        k = len(right) - 1 - j
        left[j], right[k] = weight * right[k] % modulus, pow(weight, -1, modulus) * left[j] % modulus


def run_leaf(u, v, weight_columns, head, tail, digits):
    """Run the physical program. The input satisfies v^t u=1 over Z/3**digits.

    Only this finite reference interpreter materializes the complete field arrays.
    The tape selector calls lower_coefficient once per aligned column and slot.
    Its inputs a0 and ai are in the new pivot order.
    """
    modulus = 3**digits
    n, width = len(u), len(weight_columns)
    order, b, c = ordered_chart(u, v, select_pivot(u, v), modulus)
    fields = [list(row) for row in chain(head, tail)]
    if not width:
        return fields, ()
    pairs = pivot_pairs(n, order[0])
    for left, right in pairs:
        exchange(fields, left, right, (1 for _ in range(width)), modulus)
    h_inverse = pow(c[0], -1, modulus)
    slots = range(4 * (n - 1))
    for undo in (False, True):
        if undo:
            exchange(fields, 0, 2 * n - 1, (column[order[0]] * c[0] for column in weight_columns), modulus)
        for slot in reversed(slots) if undo else slots:
            dst, src, i = lower_slot(n, slot)
            sweep = slot // (n - 1)
            for j, column in enumerate(weight_columns):
                coefficient = lower_coefficient(
                    sweep, i, b, c, column[order[0]], column[order[i]], h_inverse, modulus
                )
                x = j if src < n else width - 1 - j
                y = j if dst < n else width - 1 - j
                if undo:
                    coefficient = -coefficient
                fields[dst][y] = (fields[dst][y] + coefficient * fields[src][x]) % modulus
    for left, right in reversed(pairs):
        exchange(fields, left, right, (1 for _ in range(width)), modulus)
    return fields, (width,) * (1 + 2 * len(pairs))

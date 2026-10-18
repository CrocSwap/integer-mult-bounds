"""Independent integer-address specification of the residual grammar. Apache-2.0.

This checker model does not import the source trace, cursor or encoded arithmetic.
Its finite caller bounds dimension <= 64, columns <= 129 and commands <= 8.
The written theorem has no numerical-width bound.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def point(dimension, columns, field, column):
    return field * columns + (column if field < dimension else columns - 1 - column)


def request(
    kind,
    coordinate,
    reference=None,
    backward=False,
    child_kind="",
    field=0,
    reverse=False,
    negative=False,
    half=False,
):
    return (
        kind,
        coordinate,
        reference,
        backward,
        child_kind,
        field,
        reverse,
        negative,
        half,
    )


def event(
    kind,
    first,
    second=None,
    width=None,
    depth=None,
    child_kind="",
    field=0,
    reverse=False,
    code=0,
    half=False,
    coefficient=None,
):
    return (
        kind,
        first,
        second,
        width,
        depth,
        child_kind,
        field,
        reverse,
        code,
        half,
        coefficient,
    )


def child(first, second, width, depth, code, kind, field=0, reverse=False, half=False):
    """Specify complete boundaries and the eight literal elementary leaf steps."""
    need(0 < width <= 63 * 129 and first + width <= second, "oracle child geometry")
    boundary = event(
        "enter", first, second, width, depth + 1, kind, field, reverse, code, half
    )
    if width >= 64:
        return [boundary, ("invoke", *boundary[1:]), ("return", *boundary[1:])]
    result = [boundary]
    for coordinate in range(width):
        a, b = first + coordinate, second + width - 1 - coordinate
        for stage in range(8):
            if stage in (0, 2, 4, 6):
                result.append(event("atom_swap", a, b))
            elif stage == 7:
                result.append(event("sign", b))
            else:
                coefficient = request(
                    "child",
                    coordinate,
                    child_kind=kind,
                    field=field,
                    reverse=reverse,
                    negative=stage == 3,
                    half=half,
                )
                result.append(event("add", b, a, coefficient=coefficient))
    result.append(("return", *boundary[1:]))
    return result


def reference_key(reference):
    return (
        reference.kind,
        reference.index,
        reference.first,
        reference.second,
        reference.permutation,
        reference.sign,
    )


def sweep(plan, columns, command, backward=False):
    result = []
    for column in range(columns - 1, -1, -1) if backward else range(columns):
        target = point(plan.dimension, columns, command.target, column)
        if command.kind == "sign":
            result.append(event("sign", target))
        else:
            source = point(plan.dimension, columns, command.source, column)
            coefficient = request(
                "adapter", column, reference_key(command.reference), backward
            )
            result.append(event("add", target, source, coefficient=coefficient))
    return result


def good_expected(plan, columns, depth, code):
    """Column-major adapters surround one complete central good child."""
    result = []
    for backward in (False, True):
        if backward:
            result.extend(
                child(
                    0,
                    (2 * plan.dimension - plan.rank) * columns,
                    plan.rank * columns,
                    depth,
                    code,
                    "good",
                )
            )
        for column in range(columns - 1, -1, -1) if backward else range(columns):
            for command in reversed(plan.commands) if backward else plan.commands:
                a = point(plan.dimension, columns, command.target, column)
                b = point(plan.dimension, columns, command.source, column)
                coefficient = request(
                    "adapter", column, reference_key(command.reference), backward
                )
                result.append(event("add", a, b, coefficient=coefficient))
    return result


def expected(plan, columns, depth=9, code=23):
    """Whole source semantics for the finite grammar-check domain."""
    need(2 <= plan.dimension <= 64 and 1 <= columns <= 129, "oracle finite domain")
    need(
        1 <= plan.rank < plan.dimension and len(plan.commands) <= 8,
        "oracle plan domain",
    )
    if plan.good:
        return good_expected(plan, columns, depth, code)
    result = []
    for command in plan.commands:
        if command.kind != "child":
            result.extend(sweep(plan, columns, command))
            continue
        i, k = command.target, command.source
        half = columns // 2
        reset = []
        if (i < plan.dimension) == (k < plan.dimension) and half:
            reset = child(
                k * columns,
                (k + 1) * columns - half,
                half,
                depth,
                code,
                "unit",
                half=True,
            )
        result.extend(reset)
        kind = command.reference.kind
        result.extend(
            child(
                i * columns,
                k * columns,
                columns,
                depth,
                code,
                kind,
                i if kind == "pair" else 0,
                i >= plan.dimension if kind == "pair" else False,
            )
        )
        result.extend(reset)
    return result


def spectator_extents(n, before, gap, suffix, first, second, width):
    """Count actual spectator factors in the ordered physical product.

    Each ordinary atom contributes the formal factor A. The single original
    gap contributes G. Returning (B multiplier, G multiplier, S multiplier)
    as (coefficient, exponent) avoids any logarithmic approximation.
    """
    need(
        0 <= first < first + width <= second < second + width <= 2 * n,
        "ordered physical chunks",
    )
    need(
        all(
            end <= n or start >= n
            for start, end in ((first, first + width), (second, second + width))
        ),
        "unsplit gap",
    )
    factors = [
        (before, first),
        (1, second - first - width),
        (suffix, 2 * n - second - width),
    ]
    region = 0 if first >= n else 2 if second + width <= n else 1
    coefficient, exponent = factors[region]
    factors[region] = coefficient * gap, exponent
    return factors, region

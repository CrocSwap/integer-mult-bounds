"""Exact finite lattice oracle for a family of integer reflections.

For ``A_k(x, y) = (x + k*y, -y)``, this module computes the worst, over the
full denominator-m grid, of the minimum numerator error among integer outputs.
All arithmetic is integral. The finite search box follows from the feasible
output ``(0, 0)`` and is exhaustive for every candidate that could improve it.

Krzysztof Wojt with substantial OpenAI Codex assistance and Luna support.
Apache-2.0. Independently represented finite check, not a universal proof.
"""


def _require_integer(name, value):
    if type(value) is not int:
        raise TypeError(name + " must be an int")


def _ceil_div(numerator, denominator):
    """Return ceil(numerator / denominator) for a positive denominator."""
    return -((-numerator) // denominator)


def _validate_grid_parameters(k, m):
    _require_integer("k", k)
    _require_integer("m", m)
    if m < 2:
        raise ValueError("m must be at least 2")


def _validate_residues(m, p, q):
    _require_integer("p", p)
    _require_integer("q", q)
    if not 0 <= p < m:
        raise ValueError("p must satisfy 0 <= p < m")
    if not 0 <= q < m:
        raise ValueError("q must satisfy 0 <= q < m")


def minimum(k, m, p, q):
    """Return ``(cost, (a, b), candidate_count)`` for residue ``(p, q)``.

    The returned cost is the minimum numerator error

        max(|m*a-p|, |m*b-q|, |m*a-p+k*(m*b-q)|).

    The feasible output ``(a, b) = (0, 0)`` supplies an initial bound ``B``.
    Every output with cost at most ``B`` lies in the enumerated coordinate
    box. On the fixed axis ``q == 0``, only outputs with ``b == 0`` are
    enumerated.
    """
    _validate_grid_parameters(k, m)
    _validate_residues(m, p, q)

    # Cost of the feasible output (0, 0), with u = m*a-p and v = m*b-q.
    bound = max(p, q, abs(p + k * q))

    a_min = _ceil_div(p - bound, m)
    a_max = (p + bound) // m
    b_min = _ceil_div(q - bound, m)
    b_max = (q + bound) // m

    best_cost = None
    best_output = None
    candidate_count = 0

    for a in range(a_min, a_max + 1):
        if q == 0:
            b_values = (0,)
        else:
            b_values = range(b_min, b_max + 1)
        for b in b_values:
            candidate_count += 1
            u = m * a - p
            v = m * b - q
            cost = max(abs(u), abs(v), abs(u + k * v))
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_output = (a, b)

    if best_cost is None or best_output is None:
        raise RuntimeError("the feasible initial output was absent from the search box")

    return best_cost, best_output, candidate_count


def grid(k, m):
    """Exhaust the full residue grid and return its worst minimum and witness.

    ``witness`` is the maximizing residue pair ``(p, q)``. Ties use the first
    residue in lexicographic ``p, q`` order; ``minimum`` likewise keeps the
    first lexicographic output among tied minima.
    """
    _validate_grid_parameters(k, m)

    radius_numerator = -1
    witness = None
    output = None
    points = 0
    candidates = 0

    for p in range(m):
        for q in range(m):
            cost, minimizing_output, point_candidates = minimum(k, m, p, q)
            points += 1
            candidates += point_candidates
            if cost > radius_numerator:
                radius_numerator = cost
                witness = (p, q)
                output = minimizing_output

    if witness is None or output is None:
        raise RuntimeError("the residue grid was empty")

    return {
        "radius_numerator": radius_numerator,
        "witness": witness,
        "output": output,
        "points": points,
        "candidates": candidates,
    }


def _self_test():
    expected_minimum = (1, (0, 0), 4)
    if minimum(0, 2, 1, 1) != expected_minimum:
        raise RuntimeError("coordinate-reflection minimum self-test failed")

    expected_axis_minimum = (1, (0, 0), 2)
    if minimum(1, 2, 1, 0) != expected_axis_minimum:
        raise RuntimeError("fixed-axis minimum self-test failed")

    expected_grid = {
        "radius_numerator": 1,
        "witness": (0, 1),
        "output": (0, 0),
        "points": 4,
        "candidates": 9,
    }
    if grid(0, 2) != expected_grid:
        raise RuntimeError("full-grid self-test failed")

    invalid_inputs = (
        ((True, 2, 0, 0), TypeError),
        ((0, 1, 0, 0), ValueError),
        ((0, 2, -1, 0), ValueError),
        ((0, 2, 0, 2), ValueError),
    )
    for arguments, expected_exception in invalid_inputs:
        try:
            minimum(*arguments)
        except expected_exception:
            pass
        except Exception as error:
            raise RuntimeError("unexpected exception in validation self-test") from error
        else:
            raise RuntimeError("invalid input was accepted")

    print("PASS_LATTICE_ORACLE")


if __name__ == "__main__":
    _self_test()

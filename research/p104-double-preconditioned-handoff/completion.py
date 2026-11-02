"""Ordered dyadic preconditioners for the concrete helper handoff.

This contribution was produced by Nick Petalas. Apache-2.0.
CubeJerry PR6322 supplies the dual pairs and column-unit completion;
unpaidmoon PR6297 and Ali Romman PR5602/5611 supply the handoff lineage.
"""
from fractions import Fraction as Q

V = {592: Q(5, 16), 593: Q(5, 16), 594: Q(5, 8), 596: Q(3, 8)}
U = {592: Q(-1), 593: Q(1), 594: Q(1), 596: Q(1)}
B = {188: Q(-1), **U}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(a, b, pivot, frame):
    """Complete exactly the two credited dual pairs, with arbitrary inputs."""
    require(a == V and pivot == 596, "fixed functional and pivot")
    require((b == B and frame == 3) or (b == U and frame == 1053),
            "fixed direction and available boundary chart")
    events = [["ADD", 596, 594, "-5/8", frame]]
    if b == B:
        events.append(["ADD", 188, 596, "-1", frame])
    events.extend([
        ["ADD", 593, 596, "1", frame],
        ["ADD", 594, 596, "1", frame],
        ["ADD", 594, 592, "-1/2", frame],
        ["ADD", 592, 593, "-1", frame],
    ])
    return events


def inverse(events):
    require(len(events) <= 6, "bounded boundary program")
    return [[op, r, s, str(-Q(q)), frame]
            for op, r, s, q, frame in reversed(events)]


def allowance(events):
    require(len(events) <= 12, "bounded tariff input")
    total = 0
    for op, r, s, text, frame in events:
        q = Q(text)
        n, d = abs(q.numerator), q.denominator
        require(op == "ADD" and r != s and q != 0, "nonzero ADD")
        require(d & (d - 1) == 0 and abs(q) + 1 < 2**16,
                "retained dyadic coefficient contract")
        require(type(frame) is int and frame >= 0, "chart index")
        total += 2 * (3 + n.bit_length() - 1 + n.bit_count()
                      + d.bit_length() - 1)
    return total

"""Independent exact integer model of the proposed half-grid ring matching.

All half-grid points are represented by twice their coordinates (odd integers).
Gaussian integers are pairs of Python integers, never Python complex values.
This mathematical model makes no tape, runtime, or selected-caller claim.
"""

from __future__ import annotations

Point = tuple[int, int]
Pair = tuple[Point, Point]


def turn(z: Point, count: int = 1) -> Point:
    """Apply J(x,y)=(-y,x), reduced modulo four."""
    x, y = z
    for _ in range(count % 4):
        x, y = -y, x
    return x, y


def add(x: Point, y: Point) -> Point:
    return x[0] + y[0], x[1] + y[1]


def sub(x: Point, y: Point) -> Point:
    return x[0] - y[0], x[1] - y[1]


def norm2(z: Point) -> int:
    return z[0] * z[0] + z[1] * z[1]


def hadamard(z: Point) -> Point:
    return z[0] + z[1], z[0] - z[1]


def match(z: Point) -> Point:
    """M on (Z+1/2)^2, with input/output coordinates multiplied by two.

    The positive odd ring radius is 4m+1 (inner) or 4m+3 (outer).
    Four radial connectors are handled first. Every other point has one
    unique quarter-turn into the canonical top arc. Pair its index with
    index xor 1 and undo the quarter-turn.
    """
    x, y = z
    if x % 2 != 1 or y % 2 != 1:
        raise ValueError("both scaled half-grid coordinates must be odd")
    radius = max(abs(x), abs(y))
    inner = radius if radius % 4 == 1 else radius - 2
    outer = inner + 2
    for q in range(4):
        a = turn((inner, inner), q)
        b = turn((outer, inner), q)
        if z == a:
            return b
        if z == b:
            return a
    for q in range(4):
        xx, yy = turn(z, q)
        if radius == inner and yy == inner and -inner < xx < inner:
            index = (inner - 2 - xx) // 2
            mate = (xx - 2 if index % 2 == 0 else xx + 2, yy)
            return turn(mate, -q)
        if radius == outer and yy == outer and -inner < xx <= outer:
            index = (outer - xx) // 2
            mate = (xx - 2 if index % 2 == 0 else xx + 2, yy)
            return turn(mate, -q)
    raise ArithmeticError("uncovered half-grid ring point")


def forward(pair: Pair, matcher=match) -> Pair:
    """Exact-sum Gaussian rounding F, using nearest unit matching of d."""
    u, v = pair
    s, d = add(u, v), sub(u, v)
    if (s[0] - s[1]) % 2 == 0:
        image_d = turn(d)
    else:
        t2 = hadamard(turn(d))
        mt2 = matcher(t2)
        h = hadamard(mt2)
        if h[0] % 2 or h[1] % 2:
            raise ArithmeticError("nonintegral transformed difference")
        image_d = h[0] // 2, h[1] // 2
    plus, minus = add(s, image_d), sub(s, image_d)
    if any(a % 2 for a in plus + minus):
        raise ArithmeticError("nonintegral Gaussian output")
    return (plus[0] // 2, plus[1] // 2), (minus[0] // 2, minus[1] // 2)


def inverse(pair: Pair) -> Pair:
    """F^{-1}=swap o F, once the proved square identity holds."""
    a, b = forward(pair)
    return b, a

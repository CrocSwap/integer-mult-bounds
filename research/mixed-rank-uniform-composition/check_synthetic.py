"""Exact synthetic ring and C-to-H checks. No floating-point arithmetic."""

from itertools import product
from math import prod


def demand(value, label):
    if not value:
        raise ValueError(label)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def scale(x, n):
    return n * x[0], n * x[1]


def mul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def rotate(x, exponent):
    return mul(x, ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent % 4])


def mono(xs, exponent):
    """Multiply by y**exponent in Z[i][y]/(y**r+1)."""
    r = len(xs)
    vals = [(0, 0)] * r
    for i, x in enumerate(xs):
        wrap, out = divmod(i + exponent, r)
        vals[out] = scale(x, (-1) ** (wrap % 2))
    return tuple(vals)


def zip_add(x, y):
    return tuple(add(a, b) for a, b in zip(x, y))


def h_layer(array, active, slot):
    """Return H0 on these slots as integer numerator at denominator 2**len(active)."""
    out = dict(array)
    for axis in active:
        nxt = {}
        for pos in out:
            partner = list(pos)
            partner[axis] ^= 1 << slot
            b = (pos[axis] >> slot) & 1
            left, right = (out[tuple(partner)], out[pos]) if b else (out[pos], out[tuple(partner)])
            nxt[pos] = tuple(add(x, scale(y, (-1) ** b)) for x, y in zip(left, right))
        out = nxt
    return out


def c_bridge(array, active, slot):
    """Evaluate D C^h D b^h with C's numerator and b=(1-i)/2."""
    count = len(active)
    phase = lambda pos: sum((pos[j] >> slot) & 1 for j in active)
    out = {pos: tuple(rotate(v, phase(pos)) for v in xs) for pos, xs in array.items()}
    for axis in active:
        nxt = {}
        for pos, xs in out.items():
            partner = list(pos)
            partner[axis] ^= 1 << slot
            nxt[pos] = tuple(add(mul(x, (1, 1)), mul(y, (1, -1)))
                             for x, y in zip(xs, out[tuple(partner)]))
        out = nxt
    finish = (1, 0)
    for _ in range(count):
        finish = mul(finish, (1, -1))
    final = {}
    for pos, xs in out.items():
        entries = []
        for x in xs:
            z = mul(rotate(x, phase(pos)), finish)
            demand(all(v % (1 << count) == 0 for v in z), "H0 output grid")
            entries.append(tuple(v // (1 << count) for v in z))
        final[pos] = tuple(entries)
    demand(final == h_layer(array, active, slot), "C-to-H0 signed address convention")
    return final


def rounds(array, lengths, r, opposite=False):
    max_width = max(t.bit_length() - 1 for t in lengths)
    slots = range(max_width) if opposite else reversed(range(max_width))
    out = array
    for slot in slots:
        active = [j for j, t in enumerate(lengths) if 1 << slot < t]
        u = 2 << slot
        def twiddle(pos):
            return sum(-((2 * r) // u) * ((pos[j] >> slot) & 1)
                       * (pos[j] % (u // 2)) for j in active) % (2 * r)
        if opposite:
            out = {pos: mono(xs, -twiddle(pos)) for pos, xs in out.items()}
            out = c_bridge(out, active, slot)
        else:
            out = c_bridge(out, active, slot)
            out = {pos: mono(xs, twiddle(pos)) for pos, xs in out.items()}
    return out


def reverse(value, side):
    return int(format(value, "0" + str(side.bit_length() - 1) + "b")[::-1], 2)


def oracle(array, sides, r):
    spectrum = {}
    for freq in product(*(range(t) for t in sides)):
        total = ((0, 0),) * r
        for pos, poly in array.items():
            exponent = -sum(x * j * ((2 * r) // t) for x, j, t in zip(pos, freq, sides))
            total = zip_add(total, mono(poly, exponent))
        spectrum[tuple(reverse(j, t) for j, t in zip(freq, sides))] = total
    return spectrum


def experiment(sides, r):
    data = {}
    for n, p in enumerate(product(*(range(t) for t in sides))):
        data[p] = tuple(((n * n + k * n + 31 * k + 13) % 37 - 20,
                         (3 * n - k * k + 21 * k * n + 7) % 41 - 23)
                        for k in range(r))
    forward = rounds(data, sides, r)
    demand(forward == oracle(data, sides, r), "forward synthetic Fourier operator")
    returned = rounds(forward, sides, r, opposite=True)
    demand(all(poly == tuple(scale(v, prod(sides)) for v in data[pos])
               for pos, poly in returned.items()), "opposite/source-volume shift")
    # The represented denominator is prod(sides) on each pass.
    return prod(sides) * r


if __name__ == "__main__":
    fixtures = [((8, 4, 4), 8), ((4, 2, 2), 4), ((8,), 8)]
    print("Exact signed Gaussian/ring coordinates in three fixtures",
          sum(experiment(s, r) for s, r in fixtures))

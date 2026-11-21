"""Check the weighted chart transition at the issued projector and after its return."""

from functools import cache
from io import BytesIO
from math import prod

from check_module_atoms import expected_packet, payload
from factored_frames import Frame, inverse_word
from module_atoms import balanced_widths
from quotient_route import canonical_lows, representative
from receiver import Receiver


def before_and_after():
    core = Receiver(2, balanced_widths(1))
    lows = list(canonical_lows(2))
    frame = Frame(2, (("add", 0, 1, 1), ("swap", 0, 1), ("add", 1, 0, -1)), (0,))
    standard = Frame(2, (), (0,))
    change = frame.matcher_to(standard)
    dims = (2, core.low, 2, 3, 3, 2, 3, 3)
    data = payload(prod(dims))

    def weight(old, i):
        return 1 + ((old + i) & 1)

    @cache
    def factors(low):
        return frame.covered_line(representative(lows[low], 0, 2, 1), 1)

    def ideal(group, low, old, a, b, gap, c, d):
        u, v = factors(low)
        h, t = (a, b), (c, d)
        diff = sum(v[i] * (t[i] - pow(weight(old, i), -1, 3) * h[i]) for i in (0, 1))
        return (
            group,
            low,
            old,
            *((h[i] + weight(old, i) * u[i] * diff) % 3 for i in (0, 1)),
            gap,
            *((t[i] - u[i] * diff) % 3 for i in (0, 1)),
        )

    expected = expected_packet(data, dims, ideal)
    direct = BytesIO()
    first, acted, returned = BytesIO(), BytesIO(), BytesIO()
    with core.storage():
        core.serve_line(BytesIO(data), direct, frame, 1, 2, 2, 2, 4, weight)
        core.transition(BytesIO(data), first, change, 1, 2, 2, 2, 4, weight)
        first.seek(0)
        core.serve_line(first, acted, standard, 1, 2, 2, 2, 4, weight)
        acted.seek(0)
        core.transition(acted, returned, tuple(inverse_word(change)), 1, 2, 2, 2, 4, weight)
    assert direct.getvalue() == returned.getvalue() == expected
    assert first.getvalue() != data and acted.getvalue() != first.getvalue()
    print("full quotient matcher, changed projector and inverse", prod(dims), "independent records")


def positive_highs():
    # One old low, all its independent high charts, and a genuine nine-valued target field.
    from quotient_route import canonical_right, high_packet, positions, right_matrix
    from streaming_routes import cold_swap_tape

    core = Receiver(2, (0, 3, 1, 2))
    word = (("add", 0, 1, 1), ("swap", 0, 1), ("add", 0, 1, 2))
    matrix = right_matrix(2, word, 9)
    flat = (1, 2, 0, 1)
    low = (flat[:2], flat[2:])
    result_low, _ = canonical_right(low, matrix, 3)
    dims = (core.high, 9, 9, 9, 9)
    data = payload(prod(dims))

    @cache
    def image(h):
        g = representative(flat, h, 2, 2)
        image, lower = canonical_right(g, matrix, 9)
        label = 0
        for r, columns in zip(image, positions(result_low), strict=True):
            for col in columns:
                label = 3 * label + r[col] // 3
        return label, lower[1][0]

    def expected(h, a, b, c, d):
        label, k = image(h)
        return label, a, (b - 2 * k * a) % 9, c, (d - k * c) % 9

    output = BytesIO()
    with core.storage():

        def body(source, target, lower, piece):
            core.compensate(source, target, lower, 1, 1, 1, 4, lambda old, i: 1 + i)

        high_packet(
            BytesIO(data), output, low, result_low, matrix, 2, 4 * 9**4, cold_swap_tape, body
        )
    assert output.getvalue() == expected_packet(data, dims, expected)
    print("weighted high-lift payloads", prod(dims), "records", core.high, "genuine high matrices")


def subtrees():
    core = Receiver(2, balanced_widths(1), direct=True)
    for atoms, front, old, gap in [(3, 2, 3, 2), (4, 1, 1, 1)]:
        size = front * old * gap * 3 ** (2 * atoms)
        data = payload(size)
        dims = [front, old] + [3] * atoms + [gap] + [3] * atoms

        def ideal(owner, age, *body):
            h, g, t = body[:atoms], body[atoms], body[atoms + 1 :]
            weights = [1 + ((age + i) & 1) for i in range(atoms)]
            return (
                owner,
                age,
                *(w * y % 3 for w, y in zip(weights, t, strict=True)),
                g,
                *(w * x % 3 for w, x in zip(weights, h, strict=True)),
            )

        out = BytesIO()
        core.weighted(
            BytesIO(data),
            out,
            atoms=atoms,
            available=front,
            older=old,
            gap=gap,
            suffix=4,
            weight=lambda age, i: 1 + ((age + i) & 1),
        )
        assert out.getvalue() == expected_packet(data, dims, ideal)
        print("direct native subtree", atoms, "atoms", size, "records", core.last_storage)


if __name__ == "__main__":
    before_and_after()
    positive_highs()
    subtrees()

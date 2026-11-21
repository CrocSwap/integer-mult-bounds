"""Check every binary chart, owner, grade, trace and powered price from the literal source."""

from collections import Counter
from fractions import Fraction
from functools import cache
from math import isqrt, lcm

from factored_frames import inverse_word
from independent_binary_price import independent_prices
from strong_binary import caller, graph, native_word
from ternary_frames import frame_at_three, identity, projector, transpose
from vendor.cover import row_program


def run_registers(program, starts, ends, ports):
    """Record exact data-form coefficients for all arbitrary public inputs at once."""
    count = len(starts)
    frames = dict(enumerate(starts))
    values = {i: 1 << i for i in range(count)}
    dirty = 0
    for op, dest, *args in program:
        if op == "MOVE":
            before, after = args
            assert frames[dest] == before
            frames[dest] = after
        elif op == "ADD":
            read, site = args
            assert frames[dest] == frames[read] == site
            values[dest] ^= values[read]
        elif op == "SWAP":
            (read,) = args
            frames[dest], frames[read] = frames[read], frames[dest]
            values[dest], values[read] = values[read], values[dest]
        elif op == "INIT":
            assert dest >= count and dest not in frames
            frames[dest], values[dest] = args[0], 0
        elif op == "CLEAR":
            assert dest >= count and frames.pop(dest) == args[0]
            dirty += int(bool(values.pop(dest)))
        else:
            raise ValueError("Unknown graph instruction")
    assert frames == dict(enumerate(ends))
    assert len(values) == count == 630 and ports == 111
    for i in range(count):
        expected = 1 << i
        if ports <= i < 2 * ports:
            expected ^= 1 << (i - ports)
        assert values[i] == expected
    return dirty


def check_outer_word(root):
    """Evaluate all 38 role images in the group ring of the commuting axis swaps."""

    def shift(terms, mask):
        return {(role, exponent ^ mask) for role, exponent in terms}

    def stage_mask(stages):
        mask = 0
        for stage in stages:
            mask ^= 1 << stage
        return mask

    head = 1
    words = [{(i, 0)} for i in range(root["roles"])]
    for op, *args in root["events"]:
        if op == "LOCAL":
            stage, x, y = args
            body = stage_mask((stage,))
            first, second = words[x], words[y]
            words[x] = shift(first, body)
            words[y] = shift(first, body ^ head) ^ shift(second, body)
        elif op == "IDLE_ONE":
            x, stages = args
            words[x] = shift(words[x], stage_mask(stages))
        elif op == "QUERY":
            x, y = args
            words[x] ^= shift(words[y], head)
        elif op == "ADD":
            x, y = args
            words[x] ^= words[y]
        elif op == "SWAP":
            x, y = args
            words[x], words[y] = words[y], words[x]
        else:
            raise ValueError("Unknown caller instruction")
    for i, (answer, diag) in enumerate(zip(words, root["diagonal"], strict=True)):
        assert diag["q"] == 1
        assert answer == {(i, head ^ stage_mask(diag["stages"]))}


def matrix_product(a, b):
    cols = list(zip(*b, strict=True))
    return [[sum(x * y for x, y in zip(u, v, strict=True)) for v in cols] for u in a]


def integer_matrix(a):
    den = lcm(*(v.denominator for row in a for v in row))
    assert den % 3
    return den, [[int(v * den) for v in row] for row in a]


def rational_word(frame):
    word = row_program(frame, 3)
    back = tuple(inverse_word(word))
    for program, base, goal in [
        (word, identity(len(frame)), frame),
        (back, frame, identity(len(frame))),
    ]:
        rows = [list(row) for row in base]
        for op, i, *args in program:
            if op in ("scale", "add"):
                q = Fraction(args[-1])
                assert q.denominator % 3 and max(abs(q.numerator), q.denominator) <= 20
                if op == "scale":
                    assert q.numerator % 3
            for row in rows:
                if op == "scale":
                    row[i] *= q
                elif op == "add":
                    row[i] += row[args[0]] * q
                elif op == "swap":
                    j = args[0]
                    row[i], row[j] = row[j], row[i]
                else:
                    raise ValueError("Unknown frame instruction")
        assert rows == goal
    return len(word)


def check_charts(data, ports):
    frames, starts, ends = data["frames"], data["start"], data["final"]
    ops = data["program"]
    projectors, splits = [], []
    ident = identity(8)
    for i in range(len(frames)):
        spec = frames[str(i)]
        p = projector(transpose(spec["B"] + spec["A"]), spec["dim"])
        projectors.append(p)
        den, m = integer_matrix(p)
        assert matrix_product(m, m) == [[den * x for x in row] for row in m]
        splits.append((den, m))
    pairs = {tuple(row[2:]) for row in ops if row[0] == "MOVE"}
    pairs.update(zip(starts[2 * ports :], ends[2 * ports :], strict=True))
    pairs = {tuple(sorted(pair, key=lambda j: frames[str(j)]["dim"])) for pair in pairs}
    steps = 0
    for i, j in sorted(pairs):
        di, pi = splits[i]
        dj, pj = splits[j]
        lifted = [[dj * x for x in row] for row in pi]
        assert matrix_product(pi, pj) == matrix_product(pj, pi) == lifted
        delta = [
            [y - x for x, y in zip(a, b, strict=True)]
            for a, b in zip(projectors[i], projectors[j], strict=True)
        ]
        basis, rank = frame_at_three(delta)
        assert rank == frames[str(j)]["dim"] - frames[str(i)]["dim"]
        den, m = integer_matrix(delta)
        assert matrix_product(m, basis) == [
            [den * v if col < rank else 0 for col, v in enumerate(row)] for row in basis
        ]
        steps += rational_word(basis)
    for i in range(ports):
        head, body = projectors[starts[i]], projectors[ends[ports + i]]
        assert len(frames[str(starts[i])]["B"]) == 1
        assert projectors[ends[i]] == ident
        assert all(x == 0 for row in projectors[starts[ports + i]] for x in row)
        assert [
            [x + y for x, y in zip(a, b, strict=True)] for a, b in zip(head, body, strict=True)
        ] == ident
        basis = transpose(frames[str(starts[i])]["B"] + frames[str(ends[ports + i])]["B"])
        steps += rational_word(basis)
    return len(projectors), len(pairs), steps


GRID = 1 << 128


@cache
def power(rank, exponent):
    """Enclose a nonnegative dyadic power with integer square roots and products."""
    n, q = exponent.as_integer_ratio()
    assert n >= 0 and q & (q - 1) == 0
    a = b = rank * GRID
    for _ in range(q.bit_length() - 1):
        a, b = isqrt(a * GRID), isqrt(b * GRID) + 1
    lo = hi = GRID
    while n:
        if n & 1:
            lo, hi = lo * a // GRID, (hi * b + GRID - 1) // GRID
        n //= 2
        if n:
            a, b = a * a // GRID, (b * b + GRID - 1) // GRID
    return Fraction(lo, GRID), Fraction(hi, GRID)


def strict_surplus(word, saving, drop_tilt, caps, slack_bits, debit):
    k, r = (Counter(port.rank for port in ports) for ports in (word.targets, word.paid))
    assert (len(word.targets), len(word.paid), word.ambient, word.low_cut, word.high_cut) == (
        18906,
        104904,
        134,
        12,
        12,
    )
    assert (word.power, word.floor) in ((128, 16), (228, 15))
    assert max(k) == 127 and max(r) == 56
    assert sum(rank * count for rank, count in r.items()) == 285_600 < 12 * len(word.paid)
    assert 3 * len(word.paid) ** word.power < 2 ** (18 * word.power)
    assert 5**13 > 16 * 4**13
    t, z, w = 1 - saving, Fraction(19, 64), drop_tilt

    def mass(counter, e, side):
        return sum(count * power(rank, e)[side] for rank, count in counter.items())

    base = mass(k, t, 0)
    alpha = mass(r, t, 1) / base
    gamma = mass(r, t + z, 1) / (power(word.high_cut, z)[0] * base)
    lam = power(word.floor, w)[1] * mass(k, t - w, 1) / base
    # These three upward rounded bounds keep the powered test small.
    assert all(u < b for u, b in zip((alpha, gamma, lam), caps, strict=True))
    a, g, l = caps
    assert a**word.power + 2 * g**word.power + l**word.power < 1 - Fraction(1, 2**slack_bits)
    cutoff = 2 ** (slack_bits + 1)
    assert Fraction(32 * 2 * 16 * cutoff, 15 * (cutoff - 2)) < 72
    assert 0 < saving < Fraction(39, 10_000)
    base = 4 * (word.ambient * max(k)) ** word.power * cutoff
    assert 72**10_000 * base**39 < 2 ** (debit * 10_000)
    return caps


def main():
    data, root = graph(), caller()
    assert sum(r[0] == "LOCAL" for r in root["events"]) == 36
    dirty = run_registers(data["program"], data["start"], data["final"], root["ports"])
    check_outer_word(root)
    assert dirty == 3433
    frames, pairs, steps = check_charts(data, root["ports"])
    assert (frames, pairs, steps) == (636, 2352, 44825)
    prices = [
        strict_surplus(
            native_word(128),
            Fraction(2039, 2**19),
            Fraction(13, 32),
            (Fraction(999998604, 10**9), Fraction(907282, 10**6), Fraction(926012, 10**6)),
            14,
            14,
        ),
        strict_surplus(
            native_word(228),
            Fraction(17108907955, 2**42),
            Fraction(31, 64),
            (Fraction(999999999997229, 10**15), Fraction(907282, 10**6), Fraction(900019, 10**6)),
            34,
            19,
        ),
    ]
    print(
        "PASS_STRONG_BINARY",
        frames,
        "frames",
        pairs,
        "deltas",
        steps,
        "frame gates",
        dirty,
        "dirty private clears",
        "strict surplus > 2^-14 and 2^-34",
        prices,
    )
    print("PASS_INDEPENDENT_BINARY_SURPLUS_X_1E18", *independent_prices(data, root))


if __name__ == "__main__":
    main()

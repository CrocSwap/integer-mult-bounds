"""Independent checks of the exact physical CRT map and its Walsh wiring."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from itertools import product
from math import prod
from random import Random


from crt_route import inject, original_reshape, phase_signs, permute, restrict, route, shear
from fine_ring import Tape, Trace


def digits(index, radices):
    result = []
    for radix in radices:
        index, x = divmod(index, radix)
        result.append(x)
    return result


def flatten(digit, radices):
    return sum(x * prod(radices[:j]) for j, x in enumerate(digit))


def destination(k, moduli, *, prefix):
    units = [prod(moduli[:j] if prefix else moduli[j + 1:]) for j in range(len(moduli))]
    return flatten([(k * pow(u, -1, s)) % s for u, s in zip(units, moduli)], moduli)


def assert_equal(x, y, stage):
    if x != y:
        raise AssertionError(stage)


def run_shape(moduli, padded, batch):
    s = prod(moduli)
    field = [(i * 19 - 27, 83 - i * i) for i in range(s)]
    dest = [destination(i, moduli, prefix=False) for i in range(s)]
    old = [destination(i, moduli, prefix=True) for i in range(s)]
    assert_equal(sorted(dest), list(range(s)), "CRT must be a complete bijection")
    mismatched = sum(x != y for x, y in zip(dest, old))
    # Pairwise gcd hypotheses must imply no two binary coordinates collide.
    fwd = [None] * s
    for k, i in enumerate(dest):
        fwd[i] = field[k]
    inv = [field[i] for i in dest]
    trace = Trace()
    args = (29, batch, trace)
    actual = route(field, moduli, padded, False, *args)
    assert_equal(actual, fwd, "wrong forward destination")
    assert_equal(route(field, moduli, padded, True, *args), inv, "wrong inverse destination")
    assert_equal(route(actual, moduli, padded, True, *args), field, "round trip")
    assert_equal(trace.live, 0, "owned Walsh tape leak")
    print("CRT", moduli, padded, "batch", batch, "all", s, "columns; prefix mismatches", mismatched,
          "Walsh calls", trace.grouped_requests)


def arbitrary_permutations():
    random = Random(20261120)
    count = phases = 0
    for width in range(1, 9):
        for case in range(8):
            p = list(range(width))
            random.shuffle(p)
            pairs = list(zip(p[::2], p[1::2]))
            for x, sign in enumerate(phase_signs(width, pairs)):
                exponent = sum(((x >> a) & (x >> b) & 1) for a, b in pairs)
                assert_equal(sign, (-1) ** exponent, "odometer CZ")
                phases += 1
            v = [(23 - i, 31 * i - 7) for i in range(1 << width)]
            y = [None] * len(v)
            for i, z in enumerate(v):
                index = sum(((i >> b) & 1) << p[b] for b in range(width))
                y[index] = z
            trace = Trace()
            assert_equal(permute(v, p, 18, 1 + case % 5, trace), y, "full signed arbitrary permutation")
            assert_equal(trace.live, 0, "permutation ownership")
            count += 1
    print("signed complete address permutations", count, "quadratic phase signs", phases)


def padded_adversary():
    moduli = [3, 5, 7]
    padded = [4, 8, 8]
    size = prod(padded)
    # Shear stores tensor axis zero outermost, with final axis unit-stride.
    field = [(i, 77 - 13 * i) for i in range(size)]
    for axis, inverse in product(range(3), (False, True)):
        expect = [None] * size
        for k, z in enumerate(field):
            tmp = list(reversed(digits(k, list(reversed(padded)))))
            if all(x < s for x, s in zip(tmp[:axis + 1], moduli)):
                c = flatten(tmp[:axis], moduli[:axis]) * pow(prod(moduli[:axis]), -1, moduli[axis])
                tmp[axis] = (tmp[axis] + (-c if inverse else c)) % moduli[axis]
            j = flatten(list(reversed(tmp)), list(reversed(padded)))
            expect[j] = z
        assert_equal(shear(field, moduli, padded, axis, inverse), expect, "dirty padded shear")
    print("dirty padded shears", 6, "all", size, "columns")


def checked_fail(fn, message):
    try:
        fn()
    except (ArithmeticError, ValueError):
        return
    raise AssertionError(message)


def masks_and_restoration():
    size = dirty_holes = examples = 0
    for sides, targets in [((3,), (16,)), ((7,), (8,)), ((3, 5), (4, 8)),
                           ((5, 9, 7), (8, 16, 8)), ((2, 3), (8, 4))]:
        length = prod(sides)
        trace = Trace()
        borrowed = Tape(18, trace)
        x = [(i * 3, 11 - i) for i in range(length)]
        for z in x:
            borrowed.append(z)
        # This also checks restoration when the input head enters off origin.
        borrowed.seek(length // 2)
        old_bytes = borrowed.cells.copy()
        entered = trace.live
        head = borrowed.head
        targets_index = []
        for k in range(length):
            local = digits(k, sides)
            shape_position = [(2 * t * j + s) // (2 * s) for j, s, t in zip(local, sides, targets)]
            targets_index.append(flatten(shape_position, targets))
        expected = [(0, 0)] * prod(targets)
        for j, z in zip(targets_index, x):
            expected[j] = z
        scatter = original_reshape(borrowed, sides, targets, 22, trace, extract=False)
        assert_equal(scatter, expected, "incorrect nearest-image scatter")
        assert_equal(borrowed.cells, old_bytes, "modified borrowed input")
        assert_equal(borrowed.head, head, "borrowed original head not restored")
        assert_equal(trace.live, entered, "mask retained scratch")
        occupied = set(targets_index)
        for j in range(len(scatter)):
            if j not in occupied:
                scatter[j] = (73 - j, 901 + j)
                dirty_holes += 1
        result = original_reshape(scatter, sides, targets, 22, trace, extract=True)
        assert_equal(result, x, "dirty Gaussian holes reached the compact output")
        ordinary = inject(borrowed, sides, targets, trace=trace)
        assert_equal(restrict(ordinary, sides, targets, trace=trace), x, "misplaced compact ordinary rows")
        ordinary[-1] = (2, -3)
        checked_fail(lambda: restrict(ordinary, sides, targets, trace=trace), "nonzero CRT tail admitted")
        assert_equal(trace.live, entered, "failed crop leaked a tape")
        if len(sides) > 1 and all(s % 2 for s in sides):
            fwd = route(borrowed, sides, targets, False, 22, 2, trace)
            assert_equal(route(fwd, sides, targets, True, 22, 2, trace), x, "wrong CRT round trip")
            assert_equal(borrowed.head, head, "CRT mutated borrowed head")
            assert_equal(borrowed.cells, old_bytes, "CRT mutated borrowed cells")
        assert_equal(trace.live, entered, "CRT left final scratch")
        borrowed.release()
        assert_equal(trace.live, 0, "unrestored borrowed owner")
        if trace.reads <= 0 or trace.erased <= 0:
            raise AssertionError("missing physical trace")
        size += prod(targets)
        examples += 1
    print("original-coordinate maps", examples, "slots", size, "dirty Gaussian holes", dirty_holes,
          "rejected nonzero CRT tails and restored input heads")


def travel_check():
    sides, targets = (3,5,7), (4,8,8)
    volume = prod(targets)
    total = 0
    for axis, inverse in product(range(3), (False,True)):
        trace = Trace()
        words = [(-i, i) for i in range(volume)]
        shear(words, sides, targets, axis, inverse, word_bits=13, trace=trace)
        if trace.travel > 40 * 2 * 14 * volume or trace.live or trace.erased < 2 * 14 * 2 * volume:
            raise AssertionError("nonlinear scan movement or release exceeded its bound")
        total += trace.travel
    print("six measured physical shears", total, "bits of head travel")


if __name__ == "__main__":
    for args in [((7,), (8,), 2), ((3, 5), (4, 8), 1), ((5, 3), (8, 4), 7),
                 ((3, 5, 7), (4, 8, 8), 1), ((7, 3, 5), (8, 4, 8), 2),
                 ((5, 11, 7), (8, 16, 8), 3), ((9, 5, 7), (16, 8, 8), 4)]:
        run_shape(*args)
    arbitrary_permutations()
    padded_adversary()
    masks_and_restoration()
    travel_check()

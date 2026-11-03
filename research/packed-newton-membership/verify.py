"""Exact bounded checks for the new packed membership algorithm.

Produced by Nick Petalas. Apache-2.0.
"""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import packed
from support import checked_hash, need, replay_result, source_modules


def subset_coefficients(values):
    """Independent definition by subsets, with at most 512 masks/subsets."""
    rank = len(values).bit_length() - 1
    mask = (1 << ((rank + 1) // 2)) - 1
    result = []
    for target in range(len(values)):
        real = imag = 0
        for source in range(target + 1):
            if source & target == source:
                sign = -1 if (target.bit_count() - source.bit_count()) & 1 else 1
                real += sign * values[source][0]
                imag += sign * values[source][1]
        result.extend((real & mask, imag & mask))
    return bytes(result)


def compare(values, reference, full=False):
    before = list(values)
    actual = packed.obstruction(values)
    need(actual == reference.obstruction(values), "first-failure tuple changed")
    need(values == before, "input mutated")
    if full:
        rank = len(values).bit_length() - 1
        mask = (1 << ((rank + 1) // 2)) - 1
        word = packed._pack(values, mask)
        need(packed._transform(word, rank) == subset_coefficients(values),
             "packed coefficients differ from independent subset sums")


def lane_checks():
    count = 0
    for bits in range(1, 6):
        mask = (1 << bits) - 1
        for upper, lower in product(range(mask + 1), repeat=2):
            # Two simultaneous destination bytes expose cross-lane borrowing.
            values = upper | (upper << 8)
            sources = lower | (lower << 8)
            actual = ((values | 0x8080) - sources) & (mask | (mask << 8))
            expected = ((upper - lower) & mask) * 257
            need(actual == expected, "guarded subtraction failed")
            count += 1
    need((-0x0101 & 0x1F1F) != 0x1F1F, "unguarded borrow control")
    need(((0x8080 - 0x0101) & 0x1F1F) == 0x1F1F, "guard repair")
    return count


def finite_checks(reference):
    small = broad = 0
    for rank in (0, 1, 2):
        for raw in product(range(2), repeat=2 * (1 << rank)):
            compare(list(zip(raw[::2], raw[1::2])), reference, True)
            small += 1
    for raw in product(range(4), repeat=8):
        compare([(x, 0) for x in raw], reference)
        small += 1
    for rank in range(10):
        for seed in range(12):
            values = [((i * i * 7 + seed * 11) % 67 - 33,
                       (i * 13 + seed * 17) % 71 - 35) for i in range(1 << rank)]
            compare(values, reference, seed == 0)
            broad += 1
        for width in (1, 127, 1024, 8191):
            values = [(((-1) ** i) * ((1 << width) + i),
                       ((-1) ** (i // 2)) * ((1 << width) + 3 * i))
                      for i in range(1 << rank)]
            compare(values, reference)
            broad += 1
    return small, broad


def failure_checks():
    malformed = (None, (), [], [(0, 0)] * 3, [(0, 0)] * 1024,
                 [[0, 0]], [(True, 0)], [(0, 1.0)], [(0,)],
                 [(1 << 8192, 0)], [(0, -(1 << 8192))])
    count = 0
    for values in malformed:
        try:
            packed.obstruction(values)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid input accepted")
    try:
        checked_hash(HERE / "packed.py", "0" * 64)
    except ValueError:
        count += 1
    else:
        raise ValueError("source drift not rejected")
    need(packed.member([(0, 0)]) and packed.member([((1 << 8192) - 1, 0)]),
         "rank-zero or component-limit acceptance")
    plans = packed.PLANS
    # The fault changes the actual production transform, then is restored.
    packed.PLANS = tuple(tuple((u, l, 0, s) for u, l, g, s in stages)
                         for stages in plans)
    try:
        values = [(1, 0)] + [(0, 0)] * 7
        word = packed._pack(values, 3)
        need(packed._transform(word, 3) != subset_coefficients(values),
             "production guard-removal mutant survived")
        count += 1
    finally:
        packed.PLANS = plans
    return count


def main():
    reference, replay = source_modules()
    lanes = lane_checks()
    small, broad = finite_checks(reference)
    controls = failure_checks()
    complete = replay_result(replay, True)
    result = {"status": "PASS_PACKED_NEWTON_MEMBERSHIP", "lane_pairs": lanes,
              "small_arrays": small, "broad_arrays": broad,
              "rejection_controls": controls, "source_replay": complete,
              "rank9_packed_subtractions": 9,
              "rank9_reference_component_subtractions": 4608,
              "rank9_packed_bits": 8192}
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

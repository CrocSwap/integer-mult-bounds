"""Separate enumeration from receiver truth-table consistency."""

import hashlib
import itertools
import json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def local_tables():
    assignments = []
    for value in range(32):
        digits = tuple(int(c) for c in f"{value:05b}"[::-1])
        zero, one = 0, 0
        for receiver in range(5):
            neighbors = (digits[(receiver + 4) % 5],
                         digits[(receiver + 1) % 5])
            slot = 4 * receiver + neighbors[0] + 2 * neighbors[1]
            if digits[receiver]:
                one |= 1 << slot
            else:
                zero |= 1 << slot
        assignments.append((zero, one))
    return assignments


def class_inventory():
    assignments = local_tables()
    levels = [set() for _ in range(7)]
    levels[0].add(0)
    states = [(0, 0, 0)]
    for size in range(1, 7):
        following = []
        for members, zero, one in states:
            for value in range(members.bit_length(), 32):
                new_zero, new_one = assignments[value]
                if not (zero & new_one or one & new_zero):
                    mask = members | (1 << value)
                    levels[size].add(mask)
                    following.append((mask, zero | new_zero, one | new_one))
        states = following
    check(not states, "six-input truth-table fiber")
    return [sorted(level) for level in levels]


def packing_certificate(levels):
    fives, fours = levels[5], levels[4]
    check(len(fives) == 32 and len(fours) == 480, "inventory sizes")
    four_unions = []
    for count in (4, 5):
        for chosen in itertools.combinations(fives, count):
            union = 0
            for mask in chosen:
                if union & mask:
                    break
                union |= mask
            else:
                check(count == 4, "five disjoint maximal fibers")
                four_unions.append(union)
    check(len(four_unions) == 1600, "four-fiber inventory")
    pair_unions = set()
    for a, b in itertools.combinations(fours, 2):
        if not a & b:
            pair_unions.add(a | b)
    for union in four_unions:
        remaining = ((1 << 32) - 1) ^ union
        for a in fours:
            if a & remaining == a:
                check((remaining ^ a) not in pair_unions,
                      "complete seven-message decoder")
    return len(pair_unions)


def main():
    levels = class_inventory()
    check(tuple(map(len, levels)) == (1, 32, 256, 640, 480, 32, 0),
          "truth-table class counts")
    pairs = packing_certificate(levels)
    serialized = json.dumps(levels, separators=(",", ":")).encode()
    digest = hashlib.sha256(serialized).hexdigest()
    check(digest ==
          "a39ed8349b302d38efbdacb422c394044ec1c2042364c21f4d01ddda1a555c73",
          "complete truth-table inventory digest")
    print(json.dumps({"status": "PASS_NONLINEAR_CYCLE_TRUTH_TABLES",
                      "class_counts_by_size": list(map(len, levels)),
                      "inventory_sha256": digest,
                      "disjoint_four_pair_unions": pairs}, sort_keys=True))


if __name__ == "__main__":
    main()

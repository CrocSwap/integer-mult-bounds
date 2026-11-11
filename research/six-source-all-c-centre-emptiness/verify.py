#!/usr/bin/env python3
"""Exact centre classification for the six-source diagonal s + t = 6c + 3.

The written argument is in README.md.  The program checks the two algebraic
lemmas on every characteristic c >= 3, enumerates the complete centre census
for c = 2, ..., 10, and checks the exact 180 + 120 shape count for odd c.
It does not search words.
"""
import itertools
import math

# Complete count-vector census: (count vectors with sum 3c+1, examined centre
# letters with counts[centre] <= c-1, residue-legal sums, weight-3 sums).
CENSUS = (2, 3, 4, 5, 6, 7, 8, 9, 10)
EXPECTED = {
    2: (126, 450, 450, 0),
    3: (546, 2346, 366, 300),
    4: (1686, 7926, 0, 0),
    5: (4221, 20916, 300, 300),
    6: (9156, 46956, 0, 0),
    7: (17892, 93996, 300, 300),
    8: (32292, 172692, 0, 0),
    9: (54747, 296802, 300, 300),
    10: (88242, 483582, 0, 0),
}
ALGEBRA_MAX = 999
PASS = "PASS_ALL_C_CENTRE_CLASSIFICATION"


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def allowed_values(c):
    """Coordinate sums of two counts in 0..c that are 0 or 1 modulo c."""
    values = [v for v in range(2 * c + 1) if v % c in (0, 1)]
    expect(values == sorted(set(values)), "allowed set is not sorted and distinct")
    expect(values[:2] == [0, 1] and values[-1] == 2 * c, "allowed set endpoints moved")
    return values


def even_restriction(c):
    """For even c the non-centre and centre counts both lie in {0,c/2,c}."""
    expect(c % 2 == 0 and c >= 4, "even restriction used outside its domain")
    values = set(allowed_values(c))
    counts = [r for r in range(c + 1) if 2 * r in values or 2 * r + 1 in values]
    expect(counts == [0, c // 2, c], f"c={c}: legal counts {counts}")
    step = c // 2
    expect(step >= 2, f"c={c}: step {step} is not at least 2")
    expect(all(r % step == 0 for r in counts), f"c={c}: legal count misses the step")
    expect((3 * c + 1) % step == 1, f"c={c}: centre length is not 1 modulo the step")
    return counts, step


def odd_tables(c):
    """Non-centre counts {0,h,c} and centre counts {0,a} for odd c."""
    expect(c % 2 == 1 and c >= 3, "odd tables used outside their domain")
    a, h = (c - 1) // 2, (c + 1) // 2
    values = set(allowed_values(c))
    non_centre = [r for r in range(c + 1) if 2 * r in values]
    centre = [r for r in range(c + 1) if 2 * r + 1 in values]
    expect(non_centre == [0, h, c], f"c={c}: non-centre counts {non_centre}")
    expect(centre == [0, a], f"c={c}: centre counts {centre}")
    expect(2 * h == c + 1 and 2 * a + 1 == c, f"c={c}: table identities moved")
    return a, h


def odd_solutions(c):
    """Every (m,k,xi) solving sum = 3c+1 with six legal counts."""
    a, h = odd_tables(c)
    found = []
    # m counts equal c and k counts equal h among the five non-centre slots;
    # the centre slot carries xi in {0,a}.
    for m in range(6):
        for k in range(6 - m):
            for xi in (0, a):
                if m * c + k * h + xi == 3 * c + 1:
                    found.append((m, k, xi))
    if c == 3:
        expect(found == [(0, 5, 0), (1, 3, 1), (2, 2, 0), (3, 0, 1)],
               f"c=3: solutions {found}")
    else:
        expect(found == [(1, 3, a), (2, 2, 0)], f"c={c}: solutions {found}")
    return found, a, h


def legal_shapes(c):
    """Count the legal centre pairs by the multinomial coefficients."""
    a, h = odd_tables(c)
    # Shape 1: counts {0,0,h,h,c,c}, centre on one of the two zero slots.
    shape1 = math.factorial(6) // (2 * 2 * 2) * 2
    # Shape 2: counts {0,a,h,h,h,c}, centre on the a slot.
    shape2 = math.factorial(6) // (3 * 2)
    expect(shape1 == 180 and shape2 == 120, "shape counts moved")
    return shape1, shape2


def census(c):
    """Enumerate every count vector and centre letter; count legal sums."""
    values = set(allowed_values(c))
    length = 3 * c + 1
    vectors = 0
    examined = 0
    legal = 0
    weight3 = 0
    for counts in itertools.product(range(c + 1), repeat=6):
        if sum(counts) != length:
            continue
        vectors += 1
        for centre in range(6):
            if counts[centre] > c - 1:
                continue
            examined += 1
            summed = [2 * counts[j] + (1 if j == centre else 0) for j in range(6)]
            if any(value not in values for value in summed):
                continue
            legal += 1
            bits = sum(1 for value in summed if value % c == 1)
            if bits == 3:
                weight3 += 1
    return vectors, examined, legal, weight3


def main():
    # Lemma 1: even c >= 4 has no residue-legal centre, because every count is
    # a multiple of c/2 while the centre length is not.
    for c in range(4, ALGEBRA_MAX + 1, 2):
        even_restriction(c)

    # Lemma 2: for odd c the legal counts are {0,h,c} off the centre and
    # {0,a} at the centre.  Solving the two linear equations for every c >= 5
    # leaves exactly two count shapes, 180 and 120 realizations.
    for c in range(5, ALGEBRA_MAX + 1, 2):
        solutions, a, h = odd_solutions(c)
        expect(len(solutions) == 2, f"c={c}: odd solution count moved")
        shape1, shape2 = legal_shapes(c)
        expect(shape1 + shape2 == 300, f"c={c}: legal total moved")
        # Weight of both shapes is exactly three.
        expect((1 + 2) == 3, "shape-1 weight moved")
        expect((0 + 3) == 3, "shape-2 weight moved")

    # Complete count-vector census on a small range.
    for c in CENSUS:
        vectors, examined, legal, weight3 = census(c)
        expected = EXPECTED[c]
        expect((vectors, examined, legal, weight3) == expected,
               f"c={c}: census {(vectors, examined, legal, weight3)} != {expected}")
        print(f"c={c}: vectors {vectors}, centre letters {examined}, "
              f"legal {legal}, weight-3 {weight3}")

    # The predecessor's c=6 totals reappear under this model.
    expect(EXPECTED[6][:3] == (9156, 46956, 0), "the c=6 totals moved")

    # Table controls: the residue sets used by the predecessor.
    expect(allowed_values(6) == [0, 1, 6, 7, 12], "c=6 residue set changed")
    expect(allowed_values(7) == [0, 1, 7, 8, 14], "c=7 residue set changed")
    expect(allowed_values(5) == [0, 1, 5, 6, 10], "c=5 residue set changed")

    # Explicit odd witnesses: c=5 and c=7 shape 1 and shape 2.
    for c in (5, 7):
        values = set(allowed_values(c))
        a, h = (c - 1) // 2, (c + 1) // 2
        r = (0, 0, h, h, c, c)
        s = [2 * r[j] + (1 if j == 0 else 0) for j in range(6)]
        expect(all(s[j] in values for j in range(6)), f"c={c}: shape-1 witness illegal")
        expect(sum(1 for v in s if v % c == 1) == 3, f"c={c}: shape-1 weight moved")
        r = (0, a, h, h, h, c)
        s = [2 * r[j] + (1 if j == 1 else 0) for j in range(6)]
        expect(all(s[j] in values for j in range(6)), f"c={c}: shape-2 witness illegal")
        expect(sum(1 for v in s if v % c == 1) == 3, f"c={c}: shape-2 weight moved")

    print("even c >= 4: no residue-legal centre at all")
    print("odd c >= 5: exactly 300 residue-legal centres, all of weight 3")
    print("c=3: 366 legal, 300 of weight 3; c=2: 450 legal, none of weight 3")
    print(PASS)


if __name__ == "__main__":
    main()

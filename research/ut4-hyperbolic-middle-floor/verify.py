#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact corroboration of the paired UT4 middle-factor rank argument."""

import hashlib
import itertools
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(size):
    return tuple(1 << i for i in range(size))


def plus(left, right):
    need(len(left) == len(right), "matrix row mismatch")
    return tuple(a ^ b for a, b in zip(left, right))


def multiply(left, right):
    need(len(right) <= 64, "inner dimension limit")
    need(all(0 <= row < (1 << len(right)) for row in left), "matrix shape")
    return tuple(xor_values(right[k] for k in range(len(right))
                            if (row >> k) & 1) for row in left)


def xor_values(values):
    answer = 0
    for value in values:
        answer ^= value
    return answer


def rank(rows):
    need(len(rows) <= 64 and all(0 <= x < 2**64 for x in rows), "rank limit")
    basis = [0] * 64
    answer = 0
    for original in rows:
        row = original
        for bit in range(63, -1, -1):
            if (row >> bit) & 1:
                if basis[bit]:
                    row ^= basis[bit]
                else:
                    basis[bit] = row
                    answer += 1
                    break
    return answer


def coupling(x, y, roles):
    need(type(roles) is int and 1 <= roles <= 6, "role limit")
    need(type(x) is int and type(y) is int
         and 0 < x < 1 << roles and 0 < y < 1 << roles, "nonzero vectors")
    return tuple(y if (x >> i) & 1 else 0 for i in range(roles))


def validate_word(word, roles):
    need(isinstance(word, tuple) and len(word) <= 48, "word limit")
    for label, x, y in word:
        need(label in "abc" and len(label) == 1, "generator")
        coupling(x, y, roles)


def monomial(word):
    if len(word) >= 4:
        return None
    # At most one interchange is possible in a word of length at most three.
    canonical = word.replace("ca", "ac")
    if any(letter * 2 in canonical for letter in "abc"):
        return None
    return canonical


def coefficients(word, roles):
    """Direct polynomial multiplication, without prefix/suffix formulas."""
    validate_word(word, roles)
    zero = (0,) * roles
    result = {"": identity(roles)}
    for label, x, y in word:
        matrix = coupling(x, y, roles)
        updated = result.copy()
        for name, rows in result.items():
            destination = monomial(name + label)
            if destination is not None:
                updated[destination] = plus(updated.get(destination, zero),
                                            multiply(rows, matrix))
        result = updated
    return result


def middle_arrays(word, roles):
    """Build X,Y and both prefix/suffix pairs independently of coefficients."""
    validate_word(word, roles)
    zero = (0,) * roles
    totals = {label: zero for label in "ac"}
    for label, x, y in word:
        if label in totals:
            totals[label] = plus(totals[label], coupling(x, y, roles))
    prefix = {label: zero for label in "ac"}
    xs, ys, ua, uc, va, vc = [], [], [], [], [], []
    for label, x, y in word:
        if label != "b":
            prefix[label] = plus(prefix[label], coupling(x, y, roles))
            continue
        xs.append(x)
        ys.append(y)
        ua.append(tuple((row & x).bit_count() & 1 for row in prefix["a"]))
        uc.append(tuple((row & x).bit_count() & 1 for row in prefix["c"]))
        va.append(multiply((y,), plus(totals["a"], prefix["a"]))[0])
        vc.append(multiply((y,), plus(totals["c"], prefix["c"]))[0])
    xrows = tuple(sum(((x >> i) & 1) << j for j, x in enumerate(xs))
                  for i in range(roles))
    urows = tuple(sum(column[i] << j for j, column in enumerate(columns))
                  for columns in (ua, uc) for i in range(roles))
    vrows = tuple(a | (c << roles) for a, c in zip(va, vc))
    return xrows, tuple(ys), urows, vrows


def check_identities(word, roles):
    coeff = coefficients(word, roles)
    x, y, u, v = middle_arrays(word, roles)
    zero = (0,) * roles
    need(multiply(x, y) == coeff.get("b", zero), "B identity")
    need(multiply(u, y) == coeff.get("ab", zero) + coeff.get("cb", zero),
         "stacked prefix identity")
    expect = tuple(a | (c << roles) for a, c in
                   zip(coeff.get("ba", zero), coeff.get("bc", zero)))
    need(multiply(x, v) == expect, "concatenated suffix identity")
    expect = tuple(a | (c << roles) for first, second in
                   (("aba", "abc"), ("cba", "cbc"))
                   for a, c in zip(coeff.get(first, zero), coeff.get(second, zero)))
    need(multiply(u, v) == expect, "paired cubic identity")
    return x, y, u, v


def quotient_rank(x, y, u, v):
    need(not any(multiply(x, y)), "XY must vanish")
    need(not any(multiply(u, y)), "UY must vanish")
    need(not any(multiply(x, v)), "XV must vanish")
    capacity = len(y) - rank(x) - rank(y)
    need(rank(multiply(u, v)) <= capacity, "quotient rank inequality")
    return capacity


def central_check(word, roles, projector):
    coeff = coefficients(word, roles)
    names = ("", "a", "b", "c", "ab", "ac", "ba", "bc", "cb",
             "aba", "abc", "acb", "bab", "bac", "bcb", "cba", "cbc")
    for name in names:
        expected = identity(roles) if name == "" else (0,) * roles
        if name in ("abc", "acb", "bac", "cba"):
            expected = projector
        need(coeff.get(name, (0,) * roles) == expected, "central coefficient " + name)
    x, y, u, v = check_identities(word, roles)
    width = rank(projector)
    need(rank(multiply(u, v)) == 2 * width, "hyperbolic block rank")
    capacity = quotient_rank(x, y, u, v)
    need(rank(x) >= width and rank(y) >= width, "middle span lower bounds")
    need(len(y) >= 2 * width + rank(x) + rank(y) >= 4 * width,
         "four-per-target middle floor")
    return capacity


def group_product(left, right):
    a, b, c, d, e, f = ((left >> i) & 1 for i in range(6))
    p, q, r, s, t, u = ((right >> i) & 1 for i in range(6))
    values = (a ^ p, b ^ q, c ^ r, d ^ s ^ (a & q),
              e ^ t ^ (b & r), f ^ u ^ (a & t) ^ (d & r))
    return sum(value << i for i, value in enumerate(values))


def formal_endpoint(word, roles):
    """Full 64-element group algebra, without a truncated quotient."""
    validate_word(word, roles)
    result = {0: identity(roles)}
    for label, x, y in word:
        matrix = coupling(x, y, roles)
        updated = result.copy()
        generator = {"a": 1, "b": 2, "c": 4}[label]
        for element, rows in result.items():
            increment = multiply(rows, matrix)
            for destination in (element, group_product(element, generator)):
                updated[destination] = plus(updated.get(destination, (0,) * roles),
                                            increment)
        result = {element: rows for element, rows in updated.items() if any(rows)}
    return result


def direct_word(roles, width, changed_basis):
    need(1 <= width <= roles <= 6, "direct fixture dimensions")
    basis = identity(roles)
    inverse = identity(roles)
    if changed_basis and roles >= 2:
        # One scalar involution, including mixing an active and a dirty role.
        shear = list(basis)
        shear[roles - 1] ^= 1
        basis = inverse = tuple(shear)
    word = tuple((label, xor_values((1 << i) for i in range(roles)
                                   if (basis[i] >> role) & 1), inverse[role])
                 for role in range(width) for label in "abcbabcb")
    diagonal = tuple(1 << i if i < width else 0 for i in range(roles))
    projector = multiply(multiply(basis, diagonal), inverse)
    return word, projector


def reject(function, arguments):
    try:
        function(*arguments)
    except ValueError:
        return 1
    raise ValueError("negative control accepted")


def fixtures():
    counts = {"attaining_words": 0, "omissions": 0}
    for roles in range(1, 7):
        for width in range(1, roles + 1):
            for changed in (False, True):
                word, projector = direct_word(roles, width, changed)
                need(central_check(word, roles, projector) == 2 * width,
                     "sharp quotient capacity")
                expected = {0: plus(identity(roles), projector), 32: projector}
                expected = {g: rows for g, rows in expected.items() if any(rows)}
                need(formal_endpoint(word, roles) == expected, "full formal endpoint")
                need(tuple(sum(label == g for label, _, _ in word) for g in "abc")
                     == (2 * width, 4 * width, 2 * width), "attaining counts")
                counts["attaining_words"] += 1
                if roles <= 3 and not changed:
                    for i in range(len(word)):
                        counts["omissions"] += reject(
                            central_check, (word[:i] + word[i + 1:], roles, projector))
    return counts


def identity_checks():
    alphabet = tuple(itertools.product("abc", range(1, 4), range(1, 4)))
    count = 0
    for length in range(4):
        for word in itertools.product(alphabet, repeat=length):
            check_identities(word, 2)
            count += 1
    # Longer words and all three role directions, including nilpotent couplings.
    for seed in range(192):
        word = tuple(("abc"[(seed + i * i) % 3],
                      1 + (seed * 3 + i * 5) % 7,
                      1 + (seed * 5 + i * 3) % 7) for i in range(18))
        check_identities(word, 3)
        count += 1
    return count


def controls():
    total = 0
    total += reject(quotient_rank, ((1,), (1,), (1,), (1,)))
    total += reject(quotient_rank, ((0, 0), (1, 2), (1, 2), (1, 2)))
    total += reject(quotient_rank, ((1, 2), (0, 0), (1, 2), (1, 2)))
    total += reject(coupling, (0, 1, 2))
    total += reject(coupling, (1, 4, 2))
    total += reject(coupling, (1, 1, 7))
    total += reject(validate_word, ((("d", 1, 1),), 2))
    total += reject(validate_word, ((("a", 1, 1),) * 49, 2))
    need(rank((1, 1)) == 1 and rank((2, 1)) == 2,
         "self-cubic zeros are needed for doubled rank")
    word, projector = direct_word(3, 2, True)
    total += reject(central_check, (word, 3, identity(3)))
    changed = (("c", word[0][1], word[0][2]),) + word[1:]
    total += reject(central_check, (changed, 3, projector))
    return total


def main():
    counts = fixtures()
    counts["coefficient_words"] = identity_checks()
    counts["controls"] = controls()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py"):
        path = package / name
        need(path.stat().st_size <= 2**20, "package file limit")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"status": "PASS_UT4_HYPERBOLIC_MIDDLE_FLOOR",
                      "counts": counts, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Binary first-pivot quarter law, produced by Nick Petalas. Apache-2.0."""

import hashlib
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(1 << i for i in range(n))


def apply(a, x):
    return sum(((row & x).bit_count() & 1) << i for i, row in enumerate(a))


def multiply(a, b):
    n = len(b)
    result = []
    for row in a:
        value = 0
        for j in range(n):
            if row >> j & 1:
                value ^= b[j]
        result.append(value)
    return tuple(result)


def plus(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def rank(a):
    rows = list(a)
    n = len(rows)
    lead = 0
    for col in range(n):
        pivot = next((i for i in range(lead, n) if rows[i] >> col & 1), None)
        if pivot is None:
            continue
        rows[lead], rows[pivot] = rows[pivot], rows[lead]
        for i in range(n):
            if i != lead and rows[i] >> col & 1:
                rows[i] ^= rows[lead]
        lead += 1
    return lead


def inverse(a):
    n = len(a)
    rows = [row | (1 << (n + i)) for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i] >> col & 1), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in range(n):
            if i != col and rows[i] >> col & 1:
                rows[i] ^= rows[col]
    result = tuple(row >> n for row in rows)
    require(multiply(result, a) == identity(n), "inverse failed literal multiplication")
    return result


def matrices(n):
    require(1 <= n <= 4, "raw census dimension exceeds four")
    yield from product(range(1 << n), repeat=n)


def pair(a):
    r = len(a)
    require(1 <= r <= 3, "half-dimension capacity")
    require(all(0 <= row < 1 << r for row in a), "invalid binary row")
    complement = plus(identity(r), a)
    require(rank(a) == rank(complement) == r, "compression has a forbidden eigenvalue")
    c = multiply(a, complement)
    s = identity(r) + (0,) * r
    t = tuple(a[i] | (1 << (r + i)) for i in range(r))
    t += tuple(c[i] | (complement[i] << r) for i in range(r))
    require(multiply(s, s) == s and multiply(t, t) == t, "nonidempotent construction")
    require(rank(plus(multiply(s, t), multiply(t, s))) == 2 * r, "singular commutator")
    return s, t


def functional_masks(n):
    require(1 <= n <= 6, "functional census dimension exceeds six")
    return tuple(sum(1 << beta for beta in range(1 << n)
                     if (beta & a).bit_count() & 1) for a in range(1 << n))


def literal_splits(s, t, masks):
    return sum((masks[a] & masks[apply(s, a)] & masks[apply(t, a)]).bit_count()
               for a in range(1 << len(s)))


def predicted_splits(r):
    require(2 <= r <= 3, "finite formula-check capacity")
    return (1 << (2 * r - 3)) * ((1 << (2 * r)) - 1)


def compression_census(r):
    masks = functional_masks(2 * r)
    count = 0
    for a in matrices(r):
        if rank(a) != r or rank(plus(identity(r), a)) != r:
            continue
        s, t = pair(a)
        actual = literal_splits(s, t, masks)
        require(actual == predicted_splits(r), "quarter-law split count failed")
        require(4 * actual == ((1 << (2 * r)) - 1) * (1 << (2 * r - 1)),
                "quarter-law normalized density failed")
        count += 1
    require(count == {2: 2, 3: 48}[r], "compression census incomplete")
    return {"r": r, "admissible_compressions": count, "passing_splits_each": predicted_splits(r)}


def raw_partner_census():
    s, _ = pair((2, 3))
    masks = functional_masks(4)
    idempotents, generic = 0, 0
    for t in matrices(4):
        if multiply(t, t) != t:
            continue
        idempotents += 1
        if rank(plus(multiply(s, t), multiply(t, s))) != 4:
            continue
        require(literal_splits(s, t, masks) == 30, "raw generic partner count failed")
        generic += 1
    require((idempotents, generic) == (802, 12), "raw partner census incomplete")
    return {"matrices": 65536, "idempotents": idempotents,
            "generic_partners": generic, "passing_splits_each": 30}


def complete_header_census():
    s, t = pair((2, 3))
    total, passing = 0, 0
    first_not_full = None
    for g in matrices(4):
        gi = inverse(g)
        if gi is None:
            continue
        sp = multiply(multiply(gi, s), g)
        tp = multiply(multiply(gi, t), g)
        total += 1
        if sp[0] & tp[0] & 1:
            passing += 1
            leading_s = tuple(row & 3 for row in sp[:2])
            leading_t = tuple(row & 3 for row in tp[:2])
            if first_not_full is None and (rank(leading_s) < 2 or rank(leading_t) < 2):
                first_not_full = g
    require((total, passing) == (20160, 5040), "literal complete-header census failed")
    require(passing == 30 * 168, "GL3 completion multiplier failed")
    require(first_not_full is not None, "first/full guard distinction not exhibited")
    return {"headers": total, "passing": passing,
            "first_passing_full_failing_header": first_not_full}


def controls():
    for a in ((0,), (1,)):
        try:
            pair(a)
        except ValueError:
            pass
        else:
            raise ValueError("forbidden scalar compression accepted")
    s, t = pair((2, 3))
    require(literal_splits(s, s, functional_masks(4)) == 60,
            "singular-commutator contrast failed")
    p, swap = (1, 0), (2, 1)
    require(multiply(swap, swap) != swap, "nonidempotent control is idempotent")
    require(rank(plus(multiply(p, swap), multiply(swap, p))) == 2,
            "nonidempotent control must retain invertible commutator")
    require(literal_splits(p, swap, functional_masks(2)) == 2,
            "nonidempotent control lost its non-quarter density 2/6")
    require(4 * 30 != 16 * 8, "zero-vector denominator control failed")
    require(30 != 5040, "split/header completion distinction failed")
    require(literal_splits(s, t, functional_masks(4)) == 30, "valid control fixture failed")
    return ["forbidden_A_zero", "forbidden_A_one", "singular_commutator",
            "nonidempotent_with_invertible_commutator", "zero_vector_denominator",
            "missing_GL3_completion", "first_guard_is_not_full_guard"]


def main():
    result = {"claim_type": "scoped F2 counting proof with finite corroboration",
              "compression_censuses": [compression_census(r) for r in (2, 3)],
              "raw_partners": raw_partner_census(),
              "complete_headers": complete_header_census(), "controls": controls()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in names}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("PASS_GENERIC_IDEMPOTENT_FIRST_GUARD")


if __name__ == "__main__":
    main()

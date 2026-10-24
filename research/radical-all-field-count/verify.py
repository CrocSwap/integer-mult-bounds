#!/usr/bin/env python3
"""Exact finite-field corroboration of the radical target counting law.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is imported.
"""

from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


FIELDS = (2, 3, 4, 5, 7)
MAX_DIM = {2: 4, 3: 3, 4: 2, 5: 2, 7: 2}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    require(q in FIELDS, "unsupported field order")
    if q == 4:
        add = tuple(tuple(a ^ b for b in range(q)) for a in range(q))
        rows = []
        for a in range(q):
            row = []
            for b in range(q):
                c = (a & 1) * b ^ ((a >> 1) * b << 1)
                row.append(c ^ (7 if c & 4 else 0))
            rows.append(tuple(row))
        mul = tuple(rows)
    else:
        add = tuple(tuple((a + b) % q for b in range(q)) for a in range(q))
        mul = tuple(tuple(a * b % q for b in range(q)) for a in range(q))
    neg = tuple(next(b for b in range(q) if add[a][b] == 0) for a in range(q))
    for a in range(1, q):
        require(any(mul[a][b] == 1 for b in range(1, q)), "nonunit in field")
    for a, b, c in product(range(q), repeat=3):
        require(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]], "distributivity")
        require(mul[mul[a][b]][c] == mul[a][mul[b][c]], "associativity")
    return add, mul, neg


def determinant(a, add, mul, neg):
    return add[mul[a[0]][a[3]]][neg[mul[a[1]][a[2]]]]


def bilinear_masks(q, add, mul):
    lines = tuple((1, t) for t in range(q)) + ((0, 1),)
    masks = []
    for a in product(range(q), repeat=4):
        mask = 0
        for bit, (phi, v) in enumerate(product(lines, repeat=2)):
            av = (add[mul[a[0]][v[0]]][mul[a[1]][v[1]]],
                  add[mul[a[2]][v[0]]][mul[a[3]][v[1]]])
            value = add[mul[phi[0]][av[0]]][mul[phi[1]][av[1]]]
            if value == 0:
                mask |= 1 << bit
        masks.append(mask)
    require(len(masks) == q ** 4, "coefficient matrix inventory")
    return tuple(masks)


def direct_census(q, dim, masks):
    require(0 <= dim <= MAX_DIM[q], "census capacity")
    total = reachable = 0
    for entries in product(masks, repeat=dim):
        common = (1 << ((q + 1) ** 2)) - 1
        for mask in entries:
            common &= mask
        reachable += common != 0
        total += 1
    require(total == q ** (4 * dim), "target enumeration count")
    return total, reachable, total - reachable


def spaces(q, dim):
    """Yield each subspace once by its unique reduced row-echelon basis."""
    require(0 <= dim <= 4, "subspace capacity")
    for pivots in combinations(range(4), dim):
        slots = tuple((i, j) for i, p in enumerate(pivots)
                      for j in range(p + 1, 4) if j not in pivots)
        for values in product(range(q), repeat=len(slots)):
            rows = [[int(j == p) for j in range(4)] for p in pivots]
            for (i, j), value in zip(slots, values, strict=True):
                rows[i][j] = value
            yield tuple(tuple(row) for row in rows)


def avoids_rank_one(basis, q, add, mul, neg):
    for coeffs in product(range(q), repeat=len(basis)):
        if not any(coeffs):
            continue
        value = [0] * 4
        for c, row in zip(coeffs, basis, strict=True):
            for j in range(4):
                value[j] = add[value[j]][mul[c][row[j]]]
        if determinant(value, add, mul, neg) == 0:
            return False
    return True


def subspace_census(q, add, mul, neg):
    total, good = [], []
    for dim in range(5):
        seen = accepted = 0
        for basis in spaces(q, dim):
            accepted += avoids_rank_one(basis, q, add, mul, neg)
            seen += 1
        total.append(seen)
        good.append(accepted)
    expected = [1, q * (q * q - 1), q * q * (q - 1) ** 2 // 2, 0, 0]
    require(good == expected, "rank-one-free subspace formula")
    require(total[1] == (q ** 4 - 1) // (q - 1), "projective point count")
    require(total[2] == (q * q + 1) * (q * q + q + 1), "plane inventory")
    return {"all_by_dimension": total, "rank_one_free_by_dimension": good}


def full_rank_tuples(z, q, rank):
    result = 1
    for i in range(rank):
        result *= z - q ** i
    return result


def formula(q, dim):
    z = q ** dim
    terms = [full_rank_tuples(z, q, 4),
             q * (q * q - 1) * full_rank_tuples(z, q, 3),
             q * q * (q - 1) ** 2 // 2 * full_rank_tuples(z, q, 2)]
    unreachable = sum(terms)
    return z ** 4 - unreachable, unreachable


def irreducible_census(q, add, mul, neg):
    count = 0
    for a in product(range(q), repeat=4):
        has_eigenvalue = False
        for t in range(q):
            shifted = (add[a[0]][neg[t]], a[1], a[2], add[a[3]][neg[t]])
            has_eigenvalue |= determinant(shifted, add, mul, neg) == 0
        count += not has_eigenvalue
    require(2 * count == (q * q - q) ** 2, "irreducible matrix census")
    return count


def controls(data):
    add, mul, _ = field(3)
    masks = bilinear_masks(3, add, mul)
    # Lexicographic indices of I and [[0,2],[1,0]] among the 81 matrices.
    left, right = masks[28], masks[21]
    require(left != 0 and right != 0 and left & right == 0, "shared chart control")
    require(formula(3, 2)[1] == 864, "ternary two-coordinate control")
    rejected_mutants = 0
    for mutant, reference in (
            (19 * full_rank_tuples(9, 3, 2), data["3"]["target_censuses"][2]["unreachable"]),
            (18 * full_rank_tuples(27, 3, 2), data["3"]["target_censuses"][3]["unreachable"]),
            (6 * full_rank_tuples(16, 2, 3) + 2 * full_rank_tuples(16, 2, 2),
             data["2"]["target_censuses"][4]["unreachable"])):
        try:
            require(mutant == reference, "wrong plane coefficient or missing line term")
        except ValueError:
            rejected_mutants += 1
    require(rejected_mutants == 3, "count mutants must be rejected")
    a4, m4, _ = field(4)
    require(a4[1][1] == 0 and m4[2][2] == 3, "F4 is not Z/4Z")
    rejected = 0
    for bad_q in (1, 6, 9):
        try:
            field(bad_q)
        except ValueError:
            rejected += 1
    require(rejected == 3, "field boundary rejection")
    try:
        direct_census(3, 4, masks)
    except ValueError:
        return {"groups": ["shared chart", "wrong plane coefficient",
                           "missing line term", "missing zero-subspace term", "F4 field arithmetic",
                           "unsupported fields", "census capacity"],
                "rejected_count_mutants": rejected_mutants,
                "rejected_field_inputs": rejected}
    raise ValueError("census bound was not enforced")


def main():
    output = {"claim_type": "scoped counting proof with finite corroboration",
              "fields": {}, "no_new_kappa": True}
    for q in FIELDS:
        add, mul, neg = field(q)
        masks = bilinear_masks(q, add, mul)
        data = subspace_census(q, add, mul, neg)
        data["irreducible_matrices"] = irreducible_census(q, add, mul, neg)
        data["target_censuses"] = []
        for dim in range(MAX_DIM[q] + 1):
            total, reachable, unreachable = direct_census(q, dim, masks)
            require((reachable, unreachable) == formula(q, dim), "target formula")
            if q == 2:
                z = 2 ** dim
                require(reachable == 9*z**3 - 30*z*z + 42*z - 20, "binary overlap")
            data["target_censuses"].append({"dim": dim, "total": total,
                                            "reachable": reachable,
                                            "unreachable": unreachable})
        output["fields"][str(q)] = data
    output["controls"] = controls(output["fields"])
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    output["sha256"] = {name: sha256((package / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(output, sort_keys=True, indent=2))
    print("PASS_RADICAL_ALL_FIELD_COUNT")


if __name__ == "__main__":
    main()

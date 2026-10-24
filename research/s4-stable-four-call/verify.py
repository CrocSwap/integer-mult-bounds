"""Exact corroboration for the maximal-odd S4 alphabet; writes only stdout."""
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(r):
    return tuple(1 << i for i in range(r))


def add(a, b):
    need(len(a) == len(b), "matrix sizes differ")
    return tuple(x ^ y for x, y in zip(a, b))


def multiply(a, b):
    r = len(a)
    need(len(b) == r and 2 <= r <= 5, "matrix capacity")
    result = [0] * r
    for i in range(r):
        for j in range(r):
            if a[i] >> j & 1:
                result[i] ^= b[j]
    return tuple(result)


def rank(a):
    rows = list(a)
    r = len(a)
    pivot = 0
    for column in range(r):
        selected = next((i for i in range(pivot, r)
                         if rows[i] >> column & 1), None)
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for i in range(r):
            if i != pivot and rows[i] >> column & 1:
                rows[i] ^= rows[pivot]
        pivot += 1
    return pivot


def projectors(r):
    need(2 <= r <= 5, "projector capacity")
    result = []
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if (u & v).bit_count() % 2:
                n = tuple(v if u >> i & 1 else 0 for i in range(r))
                need(multiply(n, n) == n and rank(n) == 1,
                     "projector definition")
                result.append(n)
    need(len(set(result)) == len(result), "duplicate projector")
    return result


def group_data():
    elements = tuple(permutations(range(4)))
    index = {g: i for i, g in enumerate(elements)}
    table = tuple(tuple(index[tuple(g[h[i]] for i in range(4))]
                        for h in elements) for g in elements)
    parity = tuple(sum(g[i] > g[j] for i in range(4)
                       for j in range(i + 1, 4)) % 2 for g in elements)
    e = index[(0, 1, 2, 3)]
    odd = tuple(i for i in range(24) if parity[i])
    even = tuple(i for i in range(24) if not parity[i] and i != e)
    need(len(odd) == 12 and len(even) == 11, "S4 inventory")
    for g, h in product(range(24), repeat=2):
        need(parity[table[g][h]] == parity[g] ^ parity[h], "sign map")
    return elements, table, parity, e, odd, even


def insert(result, g, matrix):
    value = add(result.get(g, (0,) * len(matrix)), matrix)
    if any(value):
        result[g] = value
    elif g in result:
        del result[g]


def formal_product(a, b, table):
    need(len(a) <= 24 and len(b) <= 24, "formal support capacity")
    result = {}
    for g, x in a.items():
        for h, y in b.items():
            insert(result, table[g][h], multiply(x, y))
    return result


def factor(g, n, e):
    need(g != e and multiply(n, n) == n, "paid factor domain")
    result = {}
    insert(result, e, add(identity(len(n)), n))
    insert(result, g, n)
    return result


def endpoint(a, b, r, e):
    result = {}
    for i in range(r):
        matrix = tuple(1 << i if j == i else 0 for j in range(r))
        insert(result, (a, b)[i] if i < 2 else e, matrix)
    return result


def word_product(word, r, e, table):
    result = {e: identity(r)}
    for g, n in word:
        result = formal_product(result, factor(g, n, e), table)
    return result


def ring_multiply(a, b):
    # F2[C2], bit 0 is [e] and bit 1 is [z], with z*z=e.
    return (((a & 1) * (b & 1) ^ (a >> 1) * (b >> 1))
            | (((a & 1) * (b >> 1) ^ (a >> 1) * (b & 1)) << 1))


def quotient_determinant(n):
    r = len(n)
    need(2 <= r <= 5, "determinant capacity")
    result = 0
    for permutation in permutations(range(r)):
        term = 1
        for i, j in enumerate(permutation):
            bit = n[i] >> j & 1
            value = ((i == j) ^ bit) | (bit << 1)
            term = ring_multiply(term, value)
        result ^= term
    return result


def check_two_calls(table, parity, e, odd):
    checked = even_supported = 0
    for r in (2, 3):
        ps = projectors(r)
        for s, t, n, m in product(odd, odd, ps, ps):
            actual = formal_product(factor(s, n, e), factor(t, m, e), table)
            nm = multiply(n, m)
            expanded = {}
            insert(expanded, e, add(add(add(identity(r), n), m), nm))
            insert(expanded, s, add(n, nm))
            insert(expanded, t, add(m, nm))
            insert(expanded, table[s][t], nm)
            need(actual == expanded, "two-call expansion")
            mass = sum(rank(c) for g, c in actual.items()
                       if g != e and not parity[g])
            need(mass <= 1, "two-call even coefficient rank")
            if all(not parity[g] for g in actual):
                even_supported += 1
                need(n == m, "even support requires a common projector")
            checked += 1
    return {"two_call_words": checked, "even_supported_words": even_supported}


def regular_action(word, values, elements):
    # Independent literal permutation composition, with no group table.
    r = len(values)
    for g, n in reversed(word):
        source = 0
        first = next(i for i in range(r) if n[i])
        v = n[first]
        for j in range(r):
            if v >> j & 1:
                source ^= values[j]
        shifted = 0
        for h in range(24):
            if source >> h & 1:
                image = tuple(elements[g][elements[h][i]] for i in range(4))
                shifted ^= 1 << elements.index(image)
        delta = shifted ^ source
        values = tuple(value ^ (delta if n[i] else 0)
                       for i, value in enumerate(values))
    return values


def check_attainers(elements, table, parity, e, odd, even):
    t = elements.index((1, 0, 2, 3))
    endpoints = columns = omissions = four_cycle_uses = 0
    for r in (2, 3, 5):
        for a, b in product(even, repeat=2):
            word = []
            for i, target in enumerate((a, b)):
                n = tuple(1 << i if j == i else 0 for j in range(r))
                other = table[t][target]
                need(other in odd and table[t][other] == target, "odd factorization")
                word.extend(((t, n), (other, n)))
                four_cycle_uses += (table[other][other] != e)
            expected = endpoint(a, b, r, e)
            need(word_product(word, r, e, table) == expected, "four-call endpoint")
            need(sum(rank(c) for g, c in expected.items()
                     if g != e and not parity[g]) == 2, "target rank mass")
            endpoints += 1
            for role, h in product(range(r), range(24)):
                values = tuple(1 << h if j == role else 0 for j in range(r))
                actual = regular_action(word, values, elements)
                target = (a, b)[role] if role < 2 else e
                image = tuple(elements[target][elements[h][i]] for i in range(4))
                wanted = tuple(1 << elements.index(image) if j == role else 0
                               for j in range(r))
                need(actual == wanted, "literal dirty regular action")
                columns += 1
            if r == 3:
                for omitted in range(4):
                    mutant = word[:omitted] + word[omitted + 1:]
                    need(word_product(mutant, r, e, table) != expected,
                         "omitted call accepted")
                    omissions += 1
    need(four_cycle_uses > 0, "enlarged alphabet was unused")
    return {"four_call_endpoints": endpoints, "regular_basis_columns": columns,
            "omission_rejections": omissions, "four_cycle_uses": four_cycle_uses}


def check_scalar_covariance(table, e, odd):
    gl = tuple(a for a in product(range(4), repeat=2) if rank(a) == 2)
    checked = 0
    for g in gl:
        inverse = next(h for h in gl if multiply(g, h) == identity(2))
        for n, label in product(projectors(2), odd):
            conjugate = multiply(multiply(g, n), inverse)
            actual = formal_product(formal_product({e: g}, factor(label, n, e), table),
                                    {e: inverse}, table)
            need(actual == factor(label, conjugate, e), "free scalar covariance")
            checked += 1
    return checked


def check_hypothesis_controls(elements, table, e, odd, even):
    n, m = (1, 0), (0, 2)
    # Even paid labels reach the two-target endpoint in two calls.
    a, b = even[:2]
    need(word_product(((a, n), (b, m)), 2, e, table) == endpoint(a, b, 2, e),
         "even-label boundary control")
    # Scalar rank two reaches a repeated even target in two calls.
    s = elements.index((1, 0, 2, 3))
    t = elements.index((0, 2, 1, 3))
    a = table[s][t]
    need(word_product(((s, identity(2)), (t, identity(2))), 2, e, table)
         == endpoint(a, a, 2, e), "rank-two boundary control")
    # A four-cycle call is invertible, but is not an involution.
    c = next(g for g in odd if table[g][g] != e)
    inverse = next(g for g in odd if table[c][g] == e)
    need(word_product(((c, n), (c, n)), 2, e, table) != {e: identity(2)},
         "wrong involution shortcut")
    need(word_product(((c, n), (inverse, n)), 2, e, table) == {e: identity(2)},
         "four-cycle inverse control")
    # One even target is attained in two calls.
    need(word_product(((s, n), (t, n)), 2, e, table) == factor(a, n, e),
         "single-target control")
    return 5


def main():
    elements, table, parity, e, odd, even = group_data()
    determinants = 0
    for r in (2, 3, 4, 5):
        for n in projectors(r):
            need(quotient_determinant(n) == 2, "sign determinant")
            determinants += 1
    result = check_two_calls(table, parity, e, odd)
    result.update(check_attainers(elements, table, parity, e, odd, even))
    result["scalar_covariances"] = check_scalar_covariance(table, e, odd)
    result["hypothesis_controls"] = check_hypothesis_controls(elements, table, e, odd, even)
    result["sign_determinants"] = determinants
    result["ordered_even_target_pairs"] = len(tuple(product(even, repeat=2)))
    source_hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        raw = Path(__file__).with_name(name).read_bytes()
        need(len(raw) <= 262144, "source byte capacity")
        source_hashes[name] = sha256(raw).hexdigest()
    receipt = {"status": "PASS_S4_STABLE_FOUR_CALL", "counts": result,
               "python": sys.version.split()[0], "source_sha256": source_hashes}
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(canonical)
    print("PASS_S4_STABLE_FOUR_CALL receipt_sha256=" + sha256(canonical.encode()).hexdigest())


if __name__ == "__main__":
    main()

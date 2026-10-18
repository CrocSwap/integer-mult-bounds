#!/usr/bin/env python3
"""Independently check the complete finite two-product-mask certificate.

No generator, predecessor code, optimizer, floating point, or assert statements.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import base64
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALL = (1 << 32) - 1
STATE_COUNT = 65536
TARGET = 19
COORD = [sum(((x >> i) & 1) << x for x in range(32)) for i in range(5)]
PARITY = sum((x.bit_count() % 2) << x for x in range(32))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fraction_rank(rows):
    """Rational Gauss elimination, separate from the integer-row generator."""
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivot_row = 0
    for column in range(len(matrix[0]) if matrix else 0):
        choices = [i for i in range(pivot_row, len(matrix)) if matrix[i][column]]
        if not choices:
            continue
        index = choices[0]
        matrix[index], matrix[pivot_row] = matrix[pivot_row], matrix[index]
        divisor = matrix[pivot_row][column]
        normalized = [x / divisor for x in matrix[pivot_row][column:]]
        for i in range(pivot_row + 1, len(matrix)):
            multiplier = matrix[i][column]
            if multiplier:
                matrix[i][column:] = [a - multiplier * b for a, b in zip(matrix[i][column:], normalized)]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def character_gram():
    # G is the Gram of the 16 Walsh characters of degrees zero, one and two.
    characters = [0] + [1 << i for i in range(5)]
    characters += [(1 << i) | (1 << j) for i, j in combinations(range(5), 2)]
    vectors = [[1 - 2 * ((x & a).bit_count() % 2) for a in characters] for x in range(32)]
    return [[sum(a * b for a, b in zip(vectors[x], vectors[y])) for y in range(32)] for x in range(32)]


def canonical_basis(name):
    h = COORD[0] & COORD[1]
    if name == "disjoint":
        k = COORD[2] & COORD[3]
    elif name == "aligned":
        k = COORD[1] & COORD[2]
    elif name == "opposed":
        k = (ALL ^ COORD[1]) & COORD[2]
    else:
        raise ValueError("unknown orbit")
    return [ALL, PARITY, h, k]


def linear_combinations(basis):
    values = [0]
    for column in basis:
        values += [v ^ column for v in values]
    return values


def outer(a, b):
    # Build rows as bit slices rather than the generator's entrywise product.
    return sum(b << (4 * i) for i in range(4) if a & (1 << i))


def binary_rank(numbers):
    rows = list(numbers)
    rank = 0
    for bit in range(16):
        pivot = next((j for j in range(rank, len(rows)) if rows[j] & (1 << bit)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for j in range(rank + 1, len(rows)):
            if rows[j] & (1 << bit):
                rows[j] ^= rows[rank]
        rank += 1
    return rank


def check_domain(records, gram):
    require(isinstance(records, list) and len(records) == 720, "domain must contain 720 codes")
    expected = {(a, b, signs) for a, b in combinations(list(combinations(range(5), 2)), 2)
                for signs in product(range(2), repeat=4)}
    seen, code_spaces, counts = set(), set(), Counter()
    for row in records:
        a, b, signs = tuple(row["first"]), tuple(row["second"]), tuple(row["literal_flips"])
        key = (a, b, signs)
        require(key in expected and key not in seen, "omitted, repeated or foreign domain member")
        seen.add(key)
        literals = [COORD[i] ^ (ALL if sign else 0) for i, sign in zip(a + b, signs)]
        h, k = literals[0] & literals[1], literals[2] & literals[3]
        space = tuple(sorted(linear_combinations([ALL, PARITY, h, k])))
        require(len(set(space)) == 16 and space not in code_spaces, "dependent or duplicate code")
        code_spaces.add(space)
        axes, flips = row["transport_axes"], row["transport_flips"]
        require(sorted(axes) == list(range(5)), "transport is not a coordinate permutation")
        require(len(flips) == 5 and all(type(v) is int and v in (0, 1) for v in flips), "invalid transport flips")
        mapping = [sum((((x >> axis) & 1) ^ flip) << i for i, (axis, flip) in enumerate(zip(axes, flips)))
                   for x in range(32)]
        require(len(set(mapping)) == 32, "transport is not bijective")
        basis = canonical_basis(row["orbit"])
        for x, y in product(range(32), repeat=2):
            u, v = mapping[x], mapping[y]
            require(gram[x][y] == gram[u][v], "transport changes Gram pairing")
            require(((x ^ y).bit_count() % 2) == ((u ^ v).bit_count() % 2), "transport changes target decoder")
        for x, u in enumerate(mapping):
            require(((h >> x) & 1) == ((basis[2] >> u) & 1), "first mask does not transport")
            require(((k >> x) & 1) == ((basis[3] >> u) & 1), "second mask does not transport")
        counts[row["orbit"]] += 1
    require(seen == expected, "incomplete domain")
    require(dict(counts) == {"aligned": 240, "opposed": 240, "disjoint": 240}, "orbit count mismatch")
    return code_spaces


def exact_edges(name, gram, claimed):
    forms = linear_combinations(canonical_basis(name))
    require(len(set(forms)) == 16, "evaluation basis is not injective")
    require(isinstance(claimed, list) and len(claimed) == 225, "missing ordered dyad")
    edges = []
    for position, (a, b) in enumerate(product(range(1, 16), repeat=2)):
        readers = [x for x in range(32) if (forms[a] >> x) & 1]
        sources = [y for y in range(32) if (forms[b] >> y) & 1]
        weight = fraction_rank([[gram[x][y] for y in sources] for x in readers])
        require(type(claimed[position]) is int and claimed[position] == weight, "incorrect rational term rank")
        edges.append((outer(a, b), weight, a, b))
    return forms, edges


def check_word(word, cap, optimum, forms, gram):
    require(isinstance(word, list) and len(word) > 0, "empty attaining word")
    coefficient, total = 0, 0
    pairs, ranks = [], []
    for term in word:
        require(isinstance(term, list) and len(term) == 2, "invalid word term")
        a, b = term
        require(type(a) is int and type(b) is int and 1 <= a <= 15 and 1 <= b <= 15, "foreign factor")
        coefficient ^= outer(a, b)
        readers = [x for x in range(32) if (forms[a] >> x) & 1]
        sources = [y for y in range(32) if (forms[b] >> y) & 1]
        cost = fraction_rank([[gram[x][y] for y in sources] for x in readers])
        require(cost <= cap, "word violates rank cap")
        total += cost
        ranks.append(cost)
        pairs.append((forms[a], forms[b]))
    require(coefficient == TARGET, "word misses coefficient target")
    require(total == optimum, "word does not attain claimed cost")
    for x, y in product(range(32), repeat=2):
        decoded = sum(((f >> x) & 1) * ((g >> y) & 1) for f, g in pairs) % 2
        expected = 1 ^ (x.bit_count() % 2) ^ (y.bit_count() % 2)
        require(decoded == expected, "word fails literal source/target decoding")
    return ranks


def check_separator(separator, edges):
    require(type(separator) is int and 0 < separator < STATE_COUNT, "invalid separator")
    require((separator & TARGET).bit_count() % 2 == 1, "separator does not separate target")
    require(all((separator & delta).bit_count() % 2 == 0 for delta, _, _, _ in edges),
            "separator does not annihilate allowed dyads")


def check_potential(potential, optimum, edges):
    require(len(potential) == STATE_COUNT, "incomplete state potential")
    require(potential[0] == 0 and potential[TARGET] == optimum, "wrong potential endpoints")
    for delta, weight, _, _ in edges:
        bit = delta & -delta
        # Each edge is undirected. Check exactly one of its two orientations.
        for start in range(0, STATE_COUNT, bit * 2):
            for state in range(start, start + bit):
                require(abs(potential[state ^ delta] - potential[state]) <= weight,
                        "potential violates an allowed edge")
    return len(edges) * (STATE_COUNT // 2)


def check_caps(records, forms, edges, gram, table):
    expected_caps = sorted({0, *(weight for _, weight, _, _ in edges)})
    require([r["cap"] for r in records] == expected_caps, "missing, repeated or foreign rank-cap regime")
    checks, words, results = 0, [], {}
    for row in records:
        cap, optimum = row["cap"], row["optimum"]
        allowed = [e for e in edges if e[1] <= cap]
        require(row["span_dimension"] == binary_rank(e[0] for e in allowed), "dyad span dimension mismatch")
        if optimum is None:
            check_separator(row["separating_functional"], allowed)
        else:
            require(type(optimum) is int and 0 <= optimum < 256, "invalid optimum")
            ranks = check_word(row["attaining_word"], cap, optimum, forms, gram)
            potential = base64.b64decode(row["potential_u8_base64"], validate=True)
            checks += check_potential(potential, optimum, allowed)
            words.append({"cap": cap, "total": optimum, "ranks": ranks})
        results[cap] = optimum
    expanded = [results[max(c for c in expected_caps if c <= cap)] for cap in range(17)]
    require(table == expanded, "rank-cap table does not match certificates")
    return checks, words


def check_subcodes(records, forms, edges, gram, parent_cost):
    require([r["quotient_generator"] for r in records] == [4, 8, 12],
            "missing or foreign one-mask subcode")
    evidence, checks = [], 0
    for row in records:
        q = row["quotient_generator"]
        coefficients = set(range(1, 4)) | {q ^ u for u in range(4)}
        allowed = [e for e in edges if e[2] in coefficients and e[3] in coefficients and e[1] <= 14]
        require(row["cap"] == 14, "subcode comparison must use the same rank cap")
        require(row["span_dimension"] == binary_rank(e[0] for e in allowed), "subcode span mismatch")
        optimum = row["optimum"]
        if optimum is None:
            check_separator(row["separating_functional"], allowed)
            ranks = None
        else:
            require(type(optimum) is int and 0 <= optimum < 256, "invalid subcode optimum")
            require(all(a in coefficients and b in coefficients for a, b in row["attaining_word"]),
                    "word leaves claimed common one-mask subcode")
            ranks = check_word(row["attaining_word"], 14, optimum, forms, gram)
            checks += check_potential(base64.b64decode(row["potential_u8_base64"], validate=True), optimum, allowed)
        evidence.append({"quotient_generator": q, "optimum": optimum, "attaining_ranks": ranks})
    best = min(r["optimum"] for r in records if r["optimum"] is not None)
    require(best - parent_cost == 1, "the claimed one-rank improvement is not certified")
    return checks, {"cap": 14, "two_mask_minimum": parent_cost, "best_one_mask_subcode": best,
                    "subcodes": evidence}


def check_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for row in sources["files"]:
        if row["usage"] == "input":
            path = (ROOT / row["path"]).resolve()
            require(path.is_relative_to(ROOT.resolve()), "external input path")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "source hash mismatch")
            count += 1
    require(count == 2, "expected two inherited mathematical source pins")
    return count


def check_scope_control(gram, code_spaces):
    # Two GENERAL quadratic masks evade the rank-16 necessity below. This
    # fixture is deliberately outside the signed coordinate-product family.
    h = PARITY & COORD[0]
    k = (ALL ^ PARITY) & COORD[1]
    forms = linear_combinations([ALL, PARITY, h, k])
    require(tuple(sorted(forms)) not in code_spaces, "scope control accidentally belongs to the covered family")
    ranks = check_word([[1, 6], [1, 4], [11, 1], [8, 1]], 8, 32, forms, gram)
    require(ranks == [8, 8, 8, 8], "scope-control ranks changed")
    return {"basis_masks": [ALL, PARITY, h, k], "word": [[1, 6], [1, 4], [11, 1], [8, 1]], "ranks": ranks}


def rejection_controls(certificate, models, gram):
    def rejects(function, *args):
        try:
            function(*args)
        except (ValueError, KeyError, TypeError):
            return
        raise ValueError("negative control was incorrectly accepted")

    row = certificate["orbits"][0]
    forms, edges = models[row["name"]]
    good = next(r for r in row["certificates"] if r["optimum"] is not None)
    rejects(exact_edges, row["name"], gram, row["term_ranks"][:-1])
    altered = row["term_ranks"][:]
    altered[0] += 1
    rejects(exact_edges, row["name"], gram, altered)
    rejects(check_word, good["attaining_word"][:-1], good["cap"], good["optimum"], forms, gram)
    rejects(check_word, good["attaining_word"], good["cap"], good["optimum"] + 1, forms, gram)
    rejects(check_word, good["attaining_word"], 0, good["optimum"], forms, gram)
    rejects(check_separator, 0, edges)
    damaged = bytearray(base64.b64decode(good["potential_u8_base64"]))
    edge = next(e for e in edges if e[1] <= good["cap"] and e[0] != TARGET)
    damaged[edge[0]] = edge[1] + 1
    rejects(check_potential, damaged, good["optimum"], [edge])
    rejects(check_domain, certificate["domain"][:-1], gram)
    damaged_domain = [dict(x) for x in certificate["domain"]]
    damaged_domain[0]["transport_axes"] = [0, 0, 2, 3, 4]
    rejects(check_domain, damaged_domain, gram)
    rejects(check_caps, row["certificates"][:-1], forms, edges, gram, row["optimum_by_cap_0_to_16"])
    opposed = next(r for r in certificate["orbits"] if r["name"] == "opposed")
    ff, ee = models["opposed"]
    rejects(check_subcodes, opposed["one_mask_subcodes_at_cap14"][:-1], ff, ee, gram, 47)
    return 11


def verify(certificate, controls=True):
    require(certificate["schema_version"] == 1, "unknown certificate schema")
    require(certificate["state_bits"] == 16 and certificate["target_state"] == TARGET, "incorrect state space or target")
    gram = character_gram()
    require(fraction_rank(gram) == 16, "unexpected full Gram rank")
    code_spaces = check_domain(certificate["domain"], gram)
    orbits = certificate["orbits"]
    require(len(orbits) == 3 and {r["name"] for r in orbits} == {"aligned", "opposed", "disjoint"}, "incomplete orbit coverage")
    evidence, models, checks, subcode_evidence = [], {}, 0, None
    for row in orbits:
        name = row["name"]
        require(row["basis_masks"] == canonical_basis(name), "canonical mask mismatch")
        forms, edges = exact_edges(name, gram, row["term_ranks"])
        models[name] = (forms, edges)
        histogram = {str(k): v for k, v in sorted(Counter(e[1] for e in edges).items())}
        require(histogram == row["rank_histogram"], "rank histogram mismatch")
        count, words = check_caps(row["certificates"], forms, edges, gram, row["optimum_by_cap_0_to_16"])
        checks += count
        if name == "opposed":
            count, subcode_evidence = check_subcodes(row["one_mask_subcodes_at_cap14"], forms, edges, gram,
                                                    row["optimum_by_cap_0_to_16"][14])
            checks += count
        evidence.append({"orbit": name, "codes": 240, "optimum_by_cap_0_to_16": row["optimum_by_cap_0_to_16"], "attaining_ranks": words})
    scope = check_scope_control(gram, code_spaces)
    count = rejection_controls(certificate, models, gram) if controls else 0
    return {"status": "PASS_FIVE_CUBE_TWO_PRODUCT_MASKS", "codes": 720, "orbits": 3,
            "ordered_rational_ranks": 675, "undirected_edge_checks": checks,
            "transport_pair_checks": 720 * 1024, "controls": count,
            "results": evidence, "one_mask_comparison": subcode_evidence, "outside_family_control": scope,
            "scope": "All finite factorizations in the specified 720 codes; no physical supplier or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--receipt", type=Path, help="Write a NEW verified receipt; refuse to overwrite")
    args = parser.parse_args()
    if args.receipt and args.receipt.exists():
        raise ValueError("receipt already exists")
    pins = check_pins()
    receipt = verify(json.loads(args.certificate.read_text()))
    receipt["source_pins"] = pins
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"PASS_FIVE_CUBE_TWO_PRODUCT_MASKS codes=720 orbits=3 ranks=675 controls=11 pins={pins} no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit("FAIL_TWO_PRODUCT_MASKS: " + str(error))

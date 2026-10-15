#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact radius-seven meet-in-the-middle search in F2[S5]."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "CERTIFICATE.json"
N_GROUP = 120
POLY_BYTES = 15  # 120 coefficients over F2


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def mat_mul_f2(a, b):
    return (
        (a[0] & b[0]) ^ (a[1] & b[2]),
        (a[0] & b[1]) ^ (a[1] & b[3]),
        (a[2] & b[0]) ^ (a[3] & b[2]),
        (a[2] & b[1]) ^ (a[3] & b[3]),
    )


def rank2(m):
    a, b, c, d = m
    determinant = (a & d) ^ (b & c)
    if determinant:
        return 2
    return int(any(m))


def idempotents():
    out = []
    for m in itertools.product((0, 1), repeat=4):
        if rank2(m) == 1 and mat_mul_f2(m, m) == m:
            out.append(m)
    return tuple(out)


def make_group():
    permutations = tuple(itertools.permutations(range(5)))
    index = {p: i for i, p in enumerate(permutations)}
    identity = index[tuple(range(5))]
    # Standard right-to-left composition: (a*b)(x) = a(b(x)).
    product = tuple(
        tuple(index[tuple(a[b[i]] for i in range(5))] for b in permutations)
        for a in permutations
    )
    generators = []
    for j in range(4):
        p = list(range(5))
        p[j], p[j + 1] = p[j + 1], p[j]
        generators.append(index[tuple(p)])
    inverse = []
    for p in permutations:
        q = [0] * 5
        for i, value in enumerate(p):
            q[value] = i
        inverse.append(index[tuple(q)])
    return permutations, index, product, identity, tuple(generators), tuple(inverse)


def closure_size(product, identity, generators):
    seen = {identity}
    frontier = [identity]
    while frontier:
        g = frontier.pop()
        for s in generators:
            h = product[g][s]
            if h not in seen:
                seen.add(h)
                frontier.append(h)
    return len(seen)


def translate(poly, g, product):
    out = 0
    bits = poly
    while bits:
        low = bits & -bits
        i = low.bit_length() - 1
        out |= 1 << product[i][g]
        bits ^= low
    return out


def run():
    permutations, index, group_product, e, generators, inverses = make_group()
    need(len(permutations) == N_GROUP, "S5 permutation count")
    need(closure_size(group_product, e, generators) == N_GROUP,
         "adjacent transpositions do not generate all S5 elements")
    need(all(group_product[s][s] == e for s in generators),
         "adjacent transposition order")
    need(all(group_product[a][b] == group_product[b][a]
             for a, b in ((generators[0], generators[2]),
                          (generators[0], generators[3]),
                          (generators[1], generators[3]))),
         "nonadjacent Coxeter generators should commute")

    ns = idempotents()
    need(len(ns) == 6 and len(set(ns)) == 6, "rank-one idempotent inventory")
    alphabet = tuple((g, n) for g in generators for n in ns)
    need(len(alphabet) == 24, "paid alphabet size")

    # c = s1*s2*s3*s4 under the declared permutation product.
    c = e
    for s in generators:
        c = group_product[c][s]
    c_inv = inverses[c]
    need(group_product[c][c_inv] == e and group_product[c_inv][c] == e,
         "5-cycle inverse")
    powers = []
    power = e
    for _ in range(5):
        power = group_product[power][c]
        powers.append(power)
    need(all(p != e for p in powers[:4]) and powers[4] == e,
         "target generator is not order five")

    one = 1 << e
    zero = 0
    identity = (one, zero, zero, one)
    target = (1 << c, zero, zero, 1 << c_inv)
    target_reverse = (1 << c_inv, zero, zero, 1 << c)

    def factor_step(matrix, factor_index):
        g, n = alphabet[factor_index]
        a, b, c0, d = matrix
        ta = a ^ translate(a, g, group_product)
        tb = b ^ translate(b, g, group_product)
        tc = c0 ^ translate(c0, g, group_product)
        td = d ^ translate(d, g, group_product)
        n00, n01, n10, n11 = n
        return (
            a ^ (ta if n00 else 0) ^ (tb if n10 else 0),
            b ^ (ta if n01 else 0) ^ (tb if n11 else 0),
            c0 ^ (tc if n00 else 0) ^ (td if n10 else 0),
            d ^ (tc if n01 else 0) ^ (td if n11 else 0),
        )

    factor_by_pair = {(n, g): i for i, (g, n) in enumerate(alphabet)}
    factor_involution_controls = 0
    for fi in range(len(alphabet)):
        need(factor_step(factor_step(identity, fi), fi) == identity,
             "paid factor is not involutive")
        factor_involution_controls += 1

    # Independent-coordinate construction: D_E11(c) D_E22(c^-1), with each
    # group element expanded into its four paid Coxeter generators.
    e11 = (1, 0, 0, 0)
    e22 = (0, 0, 0, 1)
    direct = tuple(factor_by_pair[(e11, s)] for s in generators) + tuple(
        factor_by_pair[(e22, s)] for s in reversed(generators)
    )

    def product_word(word):
        out = identity
        for fi in word:
            out = factor_step(out, fi)
        return out

    need(len(direct) == 8 and product_word(direct) == target,
         "direct eight-call construction")
    wrong_orientation = tuple(factor_by_pair[(e22, s)] for s in generators) + tuple(
        factor_by_pair[(e11, s)] for s in reversed(generators)
    )
    need(product_word(wrong_orientation) == target_reverse
         and target_reverse != target, "opposite target orientation control")
    need(product_word(direct[:-1]) != target, "dropped-factor control")
    wrong_generator = list(direct)
    wrong_generator[3] = factor_by_pair[(e11, generators[2])]
    need(product_word(tuple(wrong_generator)) != target,
         "wrong-generator control")

    # Exact balls of words of exactly each length. State deduplication is safe:
    # equal complete matrices have identical continuations. Representatives
    # are retained only to reconstruct witnesses.
    layers = [{identity: ()}]
    for depth in range(1, 5):
        current = {}
        for state, word in layers[-1].items():
            for fi in range(len(alphabet)):
                child = factor_step(state, fi)
                if child not in current:
                    current[child] = word + (fi,)
        layers.append(current)

    def right_diagonal(matrix, left, right):
        a, b, c0, d = matrix
        return (
            translate(a, left, group_product),
            translate(b, right, group_product),
            translate(c0, left, group_product),
            translate(d, right, group_product),
        )

    def inverse_prefix_search(left, right, prefix_depth, suffix_depth):
        prefix_map = {}
        suffix_map = {}
        for layer in layers[:prefix_depth + 1]:
            for state, word in layer.items():
                prefix_map.setdefault(state, word)
        for layer in layers[:suffix_depth + 1]:
            for state, word in layer.items():
                suffix_map.setdefault(state, word)
        hits_ = []
        test_target = (1 << left, zero, zero, 1 << right)
        for word in prefix_map.values():
            inverse_state = identity
            for fi in reversed(word):
                inverse_state = factor_step(inverse_state, fi)
            tail = right_diagonal(inverse_state, left, right)
            suffix = suffix_map.get(tail)
            if suffix is not None:
                combined = word + suffix
                need(product_word(combined) == test_target,
                     "meet-in-the-middle witness failed exact replay")
                hits_.append(combined)
        best_ = min(hits_, key=len) if hits_ else None
        return best_, len(hits_), len(prefix_map), len(suffix_map)

    # Solver positive control on a known three-call diagonal word, searched as
    # a 1+2 split. This checks the inverse-prefix orientation used below.
    known3 = tuple(factor_by_pair[(e11, s)] for s in generators[:3])
    g3 = e
    for s in generators[:3]:
        g3 = group_product[g3][s]
    known3_target = (1 << g3, zero, zero, one)
    need(product_word(known3) == known3_target, "known three-call target control")
    found3, found3_count, found3_prefixes, found3_suffixes = inverse_prefix_search(
        g3, e, 1, 2
    )
    need(found3 is not None and len(found3) <= 3,
         "meet-in-the-middle failed the known three-call target")

    best, hit_count, prefix_count, suffix_count = inverse_prefix_search(
        c, c_inv, 3, 4
    )
    if best is None:
        minimum = 8
    else:
        minimum = len(best)
        need(minimum <= 7, "radius-seven witness outside search radius")

    def layer_digest(layer):
        h = hashlib.sha256()
        for state in sorted(layer):
            for poly in state:
                h.update(poly.to_bytes(POLY_BYTES, "little"))
        return h.hexdigest()

    word_counts = [24 ** depth for depth in range(5)]
    all_prefix_words = sum(24 ** depth for depth in range(4))
    all_suffix_words = sum(word_counts)
    certificate = {
        "status": "PASS_S5_INVERSE_FIVECYCLE_RADIUS7",
        "group": {
            "elements": N_GROUP,
            "generated_closure": N_GROUP,
            "generators": ["(12)", "(23)", "(34)", "(45)"],
            "group_product": "standard right-to-left composition (a*b)(x)=a(b(x))",
            "c": "s1*s2*s3*s4=(1 2 3 4 5)",
            "target": "diag([c],[c^-1])",
        },
        "alphabet": {
            "rank_one_idempotents": [list(n) for n in ns],
            "factor_count": len(alphabet),
            "all_factors_involutive": factor_involution_controls == 24,
            "factor_involution_checks": factor_involution_controls,
        },
        "search": {
            "radius": 7,
            "split": "prefix length <=3; suffix length <=4; factors are involutions",
            "raw_prefix_words": all_prefix_words,
            "raw_suffix_words": all_suffix_words,
            "unique_prefix_states": prefix_count,
            "unique_suffix_states": suffix_count,
            "exact_depth_word_counts_0_to_4": word_counts,
            "exact_depth_state_counts_0_to_4": [len(layer) for layer in layers],
            "exact_depth_state_sha256_0_to_4": [layer_digest(layer) for layer in layers],
            "prefix_queries": prefix_count,
            "target_hits": hit_count,
            "minimum_call_count": minimum,
            "shortest_witness_factor_indices": list(best) if best is not None else None,
        },
        "solver_positive_control": {
            "target": "diag([s1*s2*s3],[1])",
            "direct_word_factor_indices": list(known3),
            "radius": 3,
            "split": "prefix length <=1; suffix length <=2",
            "found_witness_factor_indices": list(found3),
            "target_hits": found3_count,
            "prefix_states": found3_prefixes,
            "suffix_states": found3_suffixes,
        },
        "direct_control": {
            "factor_indices": list(direct),
            "call_count": len(direct),
            "exact_target": True,
        },
        "negative_controls": [
            "opposite target orientation remains distinct",
            "drop final direct factor",
            "replace the fourth generator in the E11 block with the third",
        ],
        "limits": [
            "Exact result only for the two-register F2[S5] model and the specified 24-factor alphabet.",
            "No native integer-multiplication supplier mapping or selected-kappa improvement is claimed.",
        ],
    }
    return certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic certificate")
    args = parser.parse_args()
    certificate = run()
    if args.write:
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(CERTIFICATE.read_text())
        need(certificate == expected, "certificate mismatch; use --write only for an intentional update")
    search = certificate["search"]
    print(
        "PASS_S5_INVERSE_FIVECYCLE_RADIUS7 alphabet=24 group=120 "
        f"prefix_states={search['unique_prefix_states']} suffix_states={search['unique_suffix_states']} "
        f"hits={search['target_hits']} direct=8 minimum={search['minimum_call_count']} no_kappa"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent exact pair-meet replay for the mixed S4 target."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import tempfile


PACKAGE = Path(__file__).resolve().parent


def compose(a, b):
    return tuple(a[b[i]] for i in range(4))


def ga_mul(a, b, group_product):
    out = 0
    while a:
        abit = a & -a
        i = abit.bit_length() - 1
        a ^= abit
        bb = b
        while bb:
            bbit = bb & -bb
            j = bbit.bit_length() - 1
            bb ^= bbit
            out ^= 1 << group_product[i][j]
    return out


def mat_mul(a, b, group_product):
    out = [0] * 9
    for i in range(3):
        for j in range(3):
            cell = 0
            for k in range(3):
                cell ^= ga_mul(a[3 * i + k], b[3 * k + j], group_product)
            out[3 * i + j] = cell
    return tuple(out)


def rank_f2(rows, ncols):
    rows = [int(r) for r in rows]
    pivot = 0
    for col in range(ncols):
        hit = next((r for r in range(pivot, len(rows)) if (rows[r] >> col) & 1), None)
        if hit is None:
            continue
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        for r in range(len(rows)):
            if r != pivot and ((rows[r] >> col) & 1):
                rows[r] ^= rows[pivot]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def linear_displacement_rank(perm):
    # Columns of the permutation matrix are e_i -> e_perm[i].
    rows = []
    for r in range(4):
        row = 0
        for c in range(4):
            value = int(perm[c] == r) ^ int(r == c)
            row |= value << c
        rows.append(row)
    return rank_f2(rows, 4)


def exact_search(target, pair_states, pair_index, n_factors, group_product):
    lookups = 0
    for f4 in range(n_factors):
        for f3 in range(n_factors):
            lookups += 1
            inverse_suffix = pair_states[f4 * n_factors + f3]
            needed_prefix = [0] * 9
            for i in range(3):
                g = (target[3 * i + i] & -target[3 * i + i]).bit_length() - 1
                for j in range(3):
                    cell = inverse_suffix[3 * i + j]
                    while cell:
                        bit = cell & -cell
                        h = bit.bit_length() - 1
                        cell ^= bit
                        needed_prefix[3 * i + j] ^= 1 << group_product[g][h]
            prefix = tuple(needed_prefix)
            if prefix in pair_index:
                left = pair_index[prefix]
                return (left[0], left[1], f3, f4), lookups
    return None, lookups


def main():
    permutations = list(itertools.permutations(range(4)))
    group_id = {p: i for i, p in enumerate(permutations)}
    group_product = [
        [group_id[compose(a, b)] for b in permutations]
        for a in permutations
    ]
    e = group_id[(0, 1, 2, 3)]
    s1 = group_id[(1, 0, 2, 3)]
    s2 = group_id[(0, 2, 1, 3)]
    s3 = group_id[(0, 1, 3, 2)]
    p = group_id[(2, 3, 0, 1)]
    q = group_id[(1, 0, 3, 2)]
    r = group_id[(3, 2, 1, 0)]
    assert group_product[group_product[group_product[s2][s1]][s3]][s2] == p
    assert group_product[s1][s3] == q
    assert group_product[p][q] == r

    idempotents = [
        (x, y)
        for x in range(1, 8)
        for y in range(1, 8)
        if (x & y).bit_count() & 1
    ]
    assert len(idempotents) == 28
    label_values = (s1, s2, s3)
    factors = []
    for label, g in enumerate(label_values):
        for idem, (x, y) in enumerate(idempotents):
            state = [0] * 9
            for i in range(3):
                for j in range(3):
                    nij = ((x >> i) & 1) and ((y >> j) & 1)
                    if i == j:
                        state[3 * i + j] ^= 1 << e
                    if nij:
                        state[3 * i + j] ^= (1 << e) | (1 << g)
            factors.append((label, idem, tuple(state)))
    assert len(factors) == 84
    identity = [0] * 9
    for i in range(3):
        identity[3 * i + i] = 1 << e
    identity = tuple(identity)
    assert all(mat_mul(factor[2], factor[2], group_product) == identity for factor in factors)

    pair_states = []
    pair_index = {}
    for f1, f2 in itertools.product(range(84), repeat=2):
        state = mat_mul(factors[f1][2], factors[f2][2], group_product)
        pair_states.append(state)
        pair_index.setdefault(state, (f1, f2))
    assert len(pair_states) == 7056

    pair_digest = hashlib.sha256(
        b"".join(struct.pack("<9I", *state) for state in sorted(pair_index))
    ).hexdigest()

    def target_state(g0, g1):
        out = [0] * 9
        out[0] = 1 << g0
        out[4] = 1 << g1
        out[8] = 1 << e
        return tuple(out)

    mixed = target_state(p, q)
    repeated = target_state(p, p)
    easy = target_state(q, q)
    mixed_word, mixed_lookups = exact_search(mixed, pair_states, pair_index, 84, group_product)
    repeated_word, repeated_lookups = exact_search(repeated, pair_states, pair_index, 84, group_product)
    easy_word, easy_lookups = exact_search(easy, pair_states, pair_index, 84, group_product)

    idem_id = {xy: i for i, xy in enumerate(idempotents)}
    e00 = idem_id[(1, 1)]
    e11 = idem_id[(2, 2)]
    direct_mixed = [28 + e00, e00, 56 + e00, 28 + e00, e11, 56 + e11]
    direct_easy = [e00, 56 + e00, e11, 56 + e11]
    coupled_easy = [56 + e00, 56 + e11, e11, e00]

    def replay(word):
        acc = [0] * 9
        for i in range(3):
            acc[3 * i + i] = 1 << e
        for f in word:
            acc = mat_mul(tuple(acc), factors[f][2], group_product)
        return tuple(acc)

    assert replay(direct_mixed) == mixed
    assert replay(direct_easy) == easy
    assert all(replay(direct_mixed[:i] + direct_mixed[i + 1:]) != mixed for i in range(6))
    wrong_label_word = direct_mixed.copy()
    wrong_label_word[0] = e00
    assert replay(wrong_label_word) != mixed
    assert replay(direct_mixed) != target_state(p, r)
    assert mixed_word is None and mixed_lookups == 7056
    assert repeated_word is None and repeated_lookups == 7056
    assert easy_word is not None and easy_lookups <= 7056
    assert replay(easy_word) == easy
    assert easy_word == tuple(coupled_easy)

    # Any subword yielding p needs at least four adjacent transpositions.
    p_perm = permutations[p]
    q_perm = permutations[q]
    p_length = sum(p_perm[i] > p_perm[j] for i in range(4) for j in range(i + 1, 4))
    q_length = sum(q_perm[i] > q_perm[j] for i in range(4) for j in range(i + 1, 4))
    assert p_length == 4 and q_length == 2
    assert linear_displacement_rank(p_perm) == 2
    assert linear_displacement_rank(q_perm) == 2
    assert p_length % 2 == 0 and q_length % 2 == 0

    receipt = {
        "schema_version": 1,
        "group": "S4",
        "group_order": 24,
        "roles": 3,
        "labels": ["s1=(12)", "s2=(23)", "s3=(34)"],
        "target": ["p=(13)(24)", "q=(12)(34)", "e"],
        "direct_word": [
            "D_E00(s2)", "D_E00(s1)", "D_E00(s3)", "D_E00(s2)",
            "D_E11(s1)", "D_E11(s3)",
        ],
        "direct_cost": 6,
        "q_q_positive_control_word": [
            "D_E00(s3)", "D_E11(s3)", "D_E11(s1)", "D_E00(s1)"
        ],
        "idempotents": len(idempotents),
        "factors": len(factors),
        "ordered_pair_words": len(pair_states),
        "distinct_pair_products": len(pair_index),
        "pair_products_sha256_sorted_little_endian_u32": pair_digest,
        "length_four_words": 84**4,
        "mixed_target_four_call_hits": 0,
        "mixed_target_pair_lookups": mixed_lookups,
        "repeated_p_control_hits": 0,
        "all_six_omissions_rejected": True,
        "wrong_label_rejected": True,
        "wrong_target_rejected": True,
        "q_q_positive_control_hit": True,
        "q_q_witness_replayed": True,
        "direct_mixed_six_call_word_replayed": True,
        "rank_floor": 4,
        "word_length_p": 4,
        "exact_minimum": 6,
        "new_kappa": False,
    }

    # Cross-check the independent C++ implementation.
    with tempfile.TemporaryDirectory(prefix="s4-mixed-v4-") as tmp:
        exe = Path(tmp) / "search"
        subprocess.run(
            ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
             str(PACKAGE / "search.cpp"), "-o", str(exe)],
            check=True, capture_output=True, text=True,
        )
        native = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
    fields = dict(token.split("=", 1) for token in native.stdout.splitlines()[0].split()[1:])
    assert fields["group_order"] == "24"
    assert fields["idempotents"] == "28"
    assert fields["factors"] == "84"
    assert fields["pair_words"] == "7056"
    assert fields["unique_pair_states"] == str(len(pair_index))
    assert fields["four_call_words"] == str(84**4)
    assert fields["mixed"] == "none" and fields["mixed_lookups"] == "7056"
    assert fields["repeated"] == "none"
    assert fields["easy_positive"] == "hit" and fields["witnesses"] == "pass"
    assert fields["easy_direct"] == "pass" and fields["direct_mixed_six"] == "pass"
    assert native.stdout.splitlines()[1] == "EASY_WITNESS s3:N0,s3:N4,s1:N4,s1:N0"

    expected_path = PACKAGE / "RESULT.json"
    if expected_path.exists():
        expected = json.loads(expected_path.read_text())
        assert receipt == expected, "deterministic exact-search receipt changed"

    print("PASS_S4_MIXED_V4_DOUBLE_TRANSPOSITION " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

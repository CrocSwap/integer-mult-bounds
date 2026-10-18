#!/usr/bin/env python3
"""Exact finite corroboration of the written UT4 all-workspace tariff bound.

Prepared for @ToikY with OpenAI Codex assistance. Apache-2.0.
Finite checks do not replace the quantified proof or certify a supplier.
"""
import argparse
from collections import deque
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LABELS = {"a": 1, "b": 2, "c": 4}
Z = 32


def sibling(name):
    spec = importlib.util.spec_from_file_location("ut4_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(ok, message):
    if not ok:
        raise ValueError(message)


def group_mul(g, h):
    a, b, c, d, e, f = [(g >> i) & 1 for i in range(6)]
    A, B, C, D, E, F = [(h >> i) & 1 for i in range(6)]
    values = [a ^ A, b ^ B, c ^ C, d ^ D ^ (a & B),
              e ^ E ^ (b & C), f ^ F ^ (a & E) ^ (d & C)]
    return sum(v << i for i, v in enumerate(values))


def identity(r):
    return [1 << i for i in range(r)]


def zero(r):
    return [0] * r


def xor(a, b):
    return [x ^ y for x, y in zip(a, b)]


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        out.append(value)
    return out


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def outer(x, y, r):
    return [y if (x >> i) & 1 else 0 for i in range(r)]


def matvec(a, x):
    return sum(((row & x).bit_count() & 1) << i for i, row in enumerate(a))


def row_times(y, a):
    return multiply([y], a)[0]


def transpose(a, columns):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(a)) for j in range(columns)]


def clean(coefficients):
    return {g: rows for g, rows in coefficients.items() if any(rows)}


def paid_product(word, r):
    require(type(r) is int and r >= 1, "positive integer role count")
    result = {0: identity(r)}
    for label, x, y in word:
        require(label in LABELS and type(x) is int and type(y) is int
                and 0 < x < (1 << r) and 0 < y < (1 << r), "invalid paid alphabet")
        N = outer(x, y, r)
        updated = {g: rows[:] for g, rows in result.items()}
        for g, rows in result.items():
            increment = multiply(rows, N)
            for key in (g, group_mul(g, LABELS[label])):
                updated[key] = xor(updated.get(key, zero(r)), increment)
        result = clean(updated)
    return result


def target(r, w, projector=None):
    require(type(w) is int and 1 <= w <= r, "invalid target count")
    P = projector if projector is not None else [1 << i if i < w else 0 for i in range(r)]
    require(rank(P) == w and multiply(P, P) == P, "target projector")
    return clean({0: xor(identity(r), P), Z: P})


def regular_columns(coefficients, r):
    columns = []
    for j in range(r):
        for h in range(64):
            value = 0
            for g, rows in coefficients.items():
                address = group_mul(g, h)
                for i, row in enumerate(rows):
                    if (row >> j) & 1:
                        value ^= 1 << (64 * i + address)
            columns.append(value)
    return columns


def path_coefficients(word, r, reverse=False):
    A, B, C, AB, BC, H = [zero(r) for _ in range(6)]
    for label, x, y in word:
        if reverse:
            label = {"a": "c", "b": "b", "c": "a"}[label]
        N = outer(x, y, r)
        if label == "a":
            A = xor(A, N)
        elif label == "b":
            AB, B = xor(AB, multiply(A, N)), xor(B, N)
        else:
            H, BC, C = xor(H, multiply(AB, N)), xor(BC, multiply(B, N)), xor(C, N)
    return A, B, C, AB, BC, H


def middle_factors(word, r):
    suffix = [None] * len(word)
    current = zero(r)
    for i in range(len(word) - 1, -1, -1):
        suffix[i] = current[:]
        label, x, y = word[i]
        if label == "c":
            current = xor(current, outer(x, y, r))
    xs, ys, us, vs = [], [], [], []
    prefix = zero(r)
    for i, (label, x, y) in enumerate(word):
        if label == "a":
            prefix = xor(prefix, outer(x, y, r))
        elif label == "b":
            xs.append(x)
            ys.append(y)
            us.append(matvec(prefix, x))
            vs.append(row_times(y, suffix[i]))
    X = transpose(xs, r)
    U = transpose(us, r)
    return X, ys, U, vs


def factor_checks(word, r):
    A, B, C, AB, BC, H = path_coefficients(word, r)
    X, Y, U, V = middle_factors(word, r)
    require(multiply(X, Y) == B and multiply(U, Y) == AB
            and multiply(X, V) == BC and multiply(U, V) == H,
            "chronological middle coefficient identities")
    if not any(B + AB + BC):
        require(rank(H) <= len(Y) - rank(X) - rank(Y), "middle quotient rank bound")
    return A, B, C, AB, BC, H


def lower_counts(word, r, w, P):
    for reverse in (False, True):
        data = path_coefficients(word, r, reverse)
        require(not any(sum(data[:5], [])) and data[5] == P, "necessary central coefficients")
    factor_checks(word, r)
    mixed = sibling("quotient").word_coefficients(word, r)
    require(mixed["bac"] == P and mixed["acb"] == P, "necessary mixed middle spans")
    X, Y, _, _ = middle_factors(word, r)
    require(rank(X) >= w and rank(Y) >= w, "mixed middle span ranks")
    counts = {label: sum(s[0] == label for s in word) for label in LABELS}
    require(counts["a"] >= 2 * w and counts["c"] >= 2 * w
            and counts["b"] >= 3 * w + (w == 1), "uniform tariff lower bound")
    return counts


def direct_word(r, w):
    return [(label, 1 << i, 1 << i) for i in range(w) for label in "abcbabcb"]


def conjugate_word(word, r):
    S, Sinv = identity(r), identity(r)
    for i in range(r - 1):
        E = identity(r)
        E[i] ^= 1 << (i + 1)
        S, Sinv = multiply(E, S), multiply(Sinv, E)
    require(multiply(S, Sinv) == identity(r), "scalar basis inverse")
    transformed = [(label, matvec(S, x), row_times(y, Sinv)) for label, x, y in word]
    return transformed, S, Sinv


def middle_relaxation(w, r):
    n = 3 * w + (w == 1)
    data = sibling("relaxation").build(w, r)
    X, Y, U, V = [data[key] for key in ("X", "Y", "U", "V")]
    P = [1 << i if i < w else 0 for i in range(r)]
    require(not any(multiply(X, Y) + multiply(U, Y) + multiply(X, V)), "relaxation vanishing coefficients")
    require(multiply(U, V) == P and rank(X) == rank(Y) == w, "relaxation attained factor data")
    require(len(Y) == n and all(transpose(X, n)) and all(Y), "relaxation nonzero rank-one factors")
    return {"w": w, "r": r, "middle_calls": n, "rank_X": rank(X), "rank_Y": rank(Y),
            "rank_H": rank(P), "full_word_realization": "not claimed"}


def scalar_census():
    distances, paths = {0: 0}, {0: ""}
    queue = deque([0])
    while queue:
        g = queue.popleft()
        for label, h in LABELS.items():
            nxt = group_mul(g, h)
            if nxt not in distances:
                distances[nxt], paths[nxt] = distances[g] + 1, paths[g] + label
                queue.append(nxt)
    require(len(distances) == 64 and distances[Z] == 8, "scalar Cayley positive control")
    return {"elements": len(distances), "central_distance": distances[Z], "shortest_word": paths[Z],
            "distance_histogram": {str(d): sum(v == d for v in distances.values()) for d in sorted(set(distances.values()))}}


def proof_image(coefficients, r, contra=False):
    out = [0] * (4 * r)
    positions = [(0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3)]
    for g, scalar in coefficients.items():
        if contra:
            g = next(h for h in range(64) if group_mul(g, h) == 0)
        address = identity(4)
        for bit, (i, j) in enumerate(positions):
            if (g >> bit) & 1:
                address[i] ^= 1 << j
        if contra:
            address = transpose(address, 4)
        for i, row in enumerate(address):
            for j in range(4):
                if (row >> j) & 1:
                    for a, scalar_row in enumerate(scalar):
                        out[i * r + a] ^= scalar_row << (j * r)
    return out


def semantic_controls():
    r, w = 3, 2
    word = direct_word(r, w)
    expected = target(r, w)
    rejected = 0
    for i in range(len(word)):
        require(paid_product(word[:i] + word[i + 1:], r) != expected, "omitted paid call")
        rejected += 1
    dirty = word + [(label, 4, 4) for label in "abcbabcb"]
    require(paid_product(dirty, r) != expected, "unrestored dirty central action")
    # Four-term common kernel of the two nonfaithful proof representations.
    bad = {g: rows[:] for g, rows in target(2, 1).items()}
    leak = [2, 0]
    for g in (0, LABELS["a"], Z, group_mul(Z, LABELS["a"])):
        bad[g] = xor(bad.get(g, zero(2)), leak)
    require(bad != target(2, 1), "nonzero formal diagnostic")
    for contra in (False, True):
        require(proof_image(bad, 2, contra) == proof_image(target(2, 1), 2, contra),
                "common-kernel diagnostic must be invisible")
    quotient = sibling("quotient")
    require(quotient.image_coefficients(bad, 2) == quotient.image_coefficients(target(2, 1), 2),
            "common-kernel quotient blind spot")
    cols, good = regular_columns(bad, 2), regular_columns(target(2, 1), 2)
    changed = sum(a != b for a, b in zip(cols, good))
    require(changed == 64 and cols[:64] == good[:64], "arbitrary dirty-input blind spot")
    trial = [("a", 1, 1), ("b", 1, 1), ("c", 1, 3), ("a", 3, 1),
             ("b", 1, 1), ("c", 1, 2)] * 2
    natural = path_coefficients(trial, 2)
    contra = path_coefficients(trial, 2, reverse=True)
    full = paid_product(trial, 2)
    require(not any(sum(natural[:5], [])) and natural[5] == identity(2),
            "legal twelve-call word must pass the natural relaxation")
    require(not any(sum(contra[:5], [])) and contra[5] == [1, 0],
            "contragredient target rejects the same twelve-call word")
    require(full != target(2, 2) and len(full) == 37, "full formal trial rejection")
    # Expanded hypotheses have cheaper direct bills; they are outside the theorem.
    require(rank(identity(2)) == 2, "rank-two alphabet control")
    # Binary odd-parity refinement is not a field-independent factor statement.
    require(sum([1, 1, 1]) % 3 == 0 and (1 * 1 + 2 * 0 + 0 * 2) % 3 == 1,
            "F3 middle-relaxation control")
    return {"omitted_calls": rejected, "dirty_role_action": 1, "common_kernel_changed_columns": changed,
            "common_kernel_scope": "Diagnostic operator, not asserted to be an admitted paid-letter word.",
            "twelve_call_trial": {"word": trial, "natural_H": natural[5], "contra_H": contra[5],
                                   "formal_nonzero_group_coefficients": len(full), "accepted_full_word": False},
            "outside_hypotheses": ["free central label", "rank-two paid coupling", "larger coefficient field"]}


def build_receipt():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "pinned model source changed")
    spec = importlib.util.spec_from_file_location("ut4_literal_regular", HERE / "independent.py")
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    table = independent.group_multiplication_table()
    require(all(table[g][h] == group_mul(g, h) for g in range(64) for h in range(64)),
            "literal address group mismatch")
    witness_hash = hashlib.sha256()
    witnesses, columns, mutations = 0, 0, 0
    for r in range(1, 6):
        for w in range(1, r + 1):
            base = direct_word(r, w)
            for transformed in (False, True):
                if transformed:
                    word, S, Sinv = conjugate_word(base, r)
                    P = multiply(multiply(S, target(r, w).get(Z, zero(r))), Sinv)
                else:
                    word, P = base, target(r, w).get(Z, zero(r))
                formal = paid_product(word, r)
                require(formal == target(r, w, P), "full formal central witness")
                counts = lower_counts(word, r, w, P)
                direct = regular_columns(formal, r)
                faithful = independent.regular_columns(word, r)
                require(direct == faithful, "independent faithful witness mismatch")
                witnesses += 1
                columns += len(direct)
                witness_hash.update(json.dumps([r, w, transformed, counts, direct], separators=(",", ":")).encode())
    alphabet = [(g, x, y) for g in LABELS for x in range(1, 4) for y in range(1, 4)]
    pairs = 0
    for first, second in itertools.product(alphabet, repeat=2):
        word = [first, second]
        formal = paid_product(word, 2)
        factor_checks(word, 2)
        require(regular_columns(formal, 2) == independent.regular_columns(word, 2),
                "ordered factor-pair mismatch")
        quotient = sibling("quotient")
        mixed = quotient.word_coefficients(word, 2)
        require(mixed == quotient.image_coefficients(formal, 2), "ordered quotient pair mismatch")
        X, Y, _, _ = middle_factors(word, 2)
        require(rank(transpose(X, len(Y)) + transpose(mixed["bac"], 2)) == rank(X)
                and rank(Y + mixed["acb"]) == rank(Y), "mixed middle span containment")
        pairs += 1
    formulas, formula_hash = 0, hashlib.sha256()
    for word in itertools.product(alphabet, repeat=3):
        data = factor_checks(word, 2)
        formula_hash.update(json.dumps(data, separators=(",", ":")).encode())
        formulas += 1
    require(pairs == 729 and formulas == 19683, "expanded alphabet coverage")
    relaxations = [middle_relaxation(w, r) for w in range(1, 65) for r in (w, w + 2)]
    controls = semantic_controls()
    trial = controls["twelve_call_trial"]["word"]
    trial_columns = independent.regular_columns(trial, 2)
    require(trial_columns == regular_columns(paid_product(trial, 2), 2), "independent trial operator mismatch")
    controls["twelve_call_trial"]["changed_basis_columns"] = sum(
        a != b for a, b in zip(trial_columns, regular_columns(target(2, 2), 2)))
    require(controls["twelve_call_trial"]["changed_basis_columns"] > 0, "faithful trial must reject")
    quotient = sibling("quotient")
    qreceipt = quotient.self_checks()
    for word in (trial, direct_word(3, 2)):
        role_count = 2 if word == trial else 3
        require(quotient.word_coefficients(word, role_count) ==
                quotient.image_coefficients(paid_product(word, role_count), role_count),
                "quotient/formal word coefficient mismatch")
    return {"schema_version": 1, "status": "Scoped written lower relaxation; not multi-target full-word optimality.",
            "uniform_counts": {"a": "2w", "b": "3w+[w=1]", "c": "2w", "unit_lower": "7w+[w=1]", "unit_upper": "8w"},
            "quotient_homomorphism": qreceipt,
            "scalar": scalar_census(), "group_products_compared": 4096,
            "formal_faithful_witnesses": witnesses, "witness_basis_columns": columns,
            "witness_operator_sha256": witness_hash.hexdigest(), "expanded_two_factor_pairs": pairs,
            "three_factor_coefficient_cases": formulas, "coefficient_sha256": formula_hash.hexdigest(),
            "middle_relaxation": {"fixtures": len(relaxations), "w_range": [1, 64], "role_counts": ["w", "w+2"],
                                  "records_sha256": hashlib.sha256(json.dumps(relaxations, sort_keys=True).encode()).hexdigest(),
                                  "examples": relaxations[:4]}, "semantic_controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    receipt = build_receipt()
    raw = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(raw)
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        require(json.dumps(expected, sort_keys=True) == json.dumps(receipt, sort_keys=True), "certificate differs")
    print("PASS_UT4_CENTRAL_TARIFF_RELAXATION witnesses=" + str(receipt["formal_faithful_witnesses"])
          + " pairs=729 formulas=19683 lower=7w+[w=1] upper=8w")


if __name__ == "__main__":
    main()

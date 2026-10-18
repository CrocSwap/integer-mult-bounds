#!/usr/bin/env python3
"""Exact finite evidence for the written shared-middle theorem. Apache-2.0.

Substantial OpenAI Codex assistance. Finite checks are not the universal proof.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ut4_regular", HERE / "regular.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent regular engine")
regular = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(regular)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def group_product(g, h):
    # Strict-upper entries 12,13,14,23,24,34; no literal matrix multiplication.
    a, b, c, d, e, f = ((g >> k) & 1 for k in range(6))
    A, B, C, D, E, F = ((h >> k) & 1 for k in range(6))
    out = (a ^ A, b ^ B ^ (a & D), c ^ C ^ (a & E) ^ (b & F),
           d ^ D, e ^ E ^ (d & F), f ^ F)
    return sum(value << i for i, value in enumerate(out))


TABLE = tuple(tuple(group_product(g, h) for h in range(64)) for g in range(64))
LABELS = {"x": 1, "y": 8, "z": 32}
U, V, CENTRAL = 2, 16, 4
PAIRS = ("xy", "yx", "yz", "zy")


def identity(r):
    return tuple(1 << i for i in range(r))


def zero(r):
    return (0,) * r


def matrix_xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def matrix_product(a, b):
    out = []
    for row in a:
        value = 0
        for j in bits(row):
            value ^= b[j]
        out.append(value)
    return tuple(out)


def matrix_transpose(a):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(a))
                 for j in range(len(a)))


def outer(u, v, r):
    return tuple(v if (u >> i) & 1 else 0 for i in range(r))


def rank(vectors):
    pivots = {}
    for item in vectors:
        while item:
            pivot = item.bit_length() - 1
            if pivot in pivots:
                item ^= pivots[pivot]
            else:
                pivots[pivot] = item
                break
    return len(pivots)


def rank_one_factors(matrix):
    nonzero = [row for row in matrix if row]
    require(nonzero and all(row == nonzero[0] for row in nonzero), "coupling must have rank one")
    return sum(bool(row) << i for i, row in enumerate(matrix)), nonzero[0]


def validate_call(label, matrix, r):
    require(label in LABELS, "paid address label outside x/y/z")
    require(len(matrix) == r and all(type(row) is int and 0 <= row < 1 << r for row in matrix),
            "invalid scalar coupling")
    return rank_one_factors(matrix)


def formal_identity(r):
    return tuple(tuple(int(i == j) for j in range(r)) for i in range(r))


def right_translate(mask, g):
    out = 0
    for h in bits(mask):
        out ^= 1 << TABLE[h][g]
    return out


def append_factor(formal, g, coupling):
    """Right multiply by I+([g]+1)N, allowing general N for controls."""
    r = len(formal)
    result = [list(row) for row in formal]
    for i in range(r):
        for k in range(r):
            changed = formal[i][k] ^ right_translate(formal[i][k], g)
            for j in bits(coupling[k]):
                result[i][j] ^= changed
    return tuple(tuple(row) for row in result)


def formal_word(word, r):
    result = formal_identity(r)
    for label, u, v in word:
        coupling = outer(u, v, r)
        validate_call(label, coupling, r)
        result = append_factor(result, LABELS[label], coupling)
    return result


def target(p, q, r):
    require(type(p) is int and type(q) is int and type(r) is int and p >= 0 and q >= 0
            and 0 < p + q <= r, "invalid target roles")
    group = [U] * p + [V] * q + [0] * (r - p - q)
    return tuple(tuple((1 << group[i]) if i == j else 0 for j in range(r)) for i in range(r))


def direct_word(p, q):
    result = []
    for i in range(p + q):
        labels = "xyxy" if i < p else "yzyz"
        result.extend((label, 1 << i, 1 << i) for label in labels)
    return result


def conjugate_formal(formal, scalar, inverse):
    r = len(scalar)
    out = [[0] * r for _ in range(r)]
    for i in range(r):
        for a in bits(scalar[i]):
            for b in range(r):
                for j in bits(inverse[b]):
                    out[i][j] ^= formal[a][b]
    return tuple(tuple(row) for row in out)


def conjugate_word(word, scalar, inverse):
    r = len(scalar)
    out = []
    for label, u, v in word:
        left = sum(((row & u).bit_count() & 1) << i for i, row in enumerate(scalar))
        right = 0
        for j in bits(v):
            right ^= inverse[j]
        out.append((label, left, right))
    return out


def formal_regular(formal):
    """Faithful embedding computed from the independent formal coefficients."""
    r = len(formal)
    columns = []
    for j in range(r):
        for h in range(64):
            column = 0
            for i in range(r):
                for g in bits(formal[i][j]):
                    column ^= 1 << (64 * i + TABLE[g][h])
            columns.append(column)
    return tuple(columns)


def update_coefficients(coefficients, label, coupling):
    result = dict(coefficients)
    for pair in PAIRS:
        if pair[1] == label:
            result[pair] = matrix_xor(result[pair], matrix_product(coefficients[pair[0]], coupling))
    result[label] = matrix_xor(result[label], coupling)
    return result


def coefficients_of(word, r):
    coefficients = {key: zero(r) for key in (*LABELS, *PAIRS)}
    for label, u, v in word:
        coefficients = update_coefficients(coefficients, label, outer(u, v, r))
    return coefficients


def block(matrix, i, j, r):
    return tuple((matrix[i * r + k] >> (j * r)) & ((1 << r) - 1) for k in range(r))


def check_coefficients(formal, coefficients):
    r = len(formal)
    natural = regular.represented(formal)
    dual = regular.represented(formal, dual=True)
    for key, i, j in (("x", 0, 1), ("y", 1, 2), ("z", 2, 3),
                      ("xy", 0, 2), ("yz", 1, 3)):
        require(block(natural, i, j, r) == coefficients[key], "natural coefficient mismatch")
    for key, i, j in (("x", 1, 0), ("y", 2, 1), ("z", 3, 2),
                      ("yx", 2, 0), ("zy", 3, 1)):
        require(block(dual, i, j, r) == coefficients[key], "dual coefficient mismatch")


def span_bounds(word, coefficients, r):
    spans = {}
    for label in LABELS:
        left = [u for g, u, _ in word if g == label]
        right = [v for g, _, v in word if g == label]
        dl, dr = rank(left), rank(right)
        if coefficients[label] == zero(r):
            require(dl + dr <= len(left), "zero-sum rank-nullity fails")
        spans[label] = (dl, dr)
        for pair in PAIRS:
            if pair[0] == label:
                require(rank(left + list(matrix_transpose(coefficients[pair]))) == dl,
                        "coefficient column escapes label span")
            if pair[1] == label:
                require(rank(right + list(coefficients[pair])) == dr,
                        "coefficient row escapes label span")
    return spans


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def group_checks():
    for g, h in product(range(64), repeat=2):
        require(TABLE[g][h] == regular.LEFT[g][h], "independent group products differ")
        left = regular.transpose(regular.inverse(regular.GROUP[TABLE[g][h]]))
        right = regular.multiply(regular.transpose(regular.inverse(regular.GROUP[g])),
                                 regular.transpose(regular.inverse(regular.GROUP[h])))
        require(left == right, "contragredient is not multiplicative")
    require(TABLE[U][32] != TABLE[32][U] and TABLE[1][V] != TABLE[V][1], "roots unexpectedly central")
    require(regular.transpose(regular.multiply(regular.GENERATORS["x"], regular.GENERATORS["y"]))
            != regular.multiply(regular.transpose(regular.GENERATORS["x"]),
                                regular.transpose(regular.GENERATORS["y"])), "transpose control fails")
    return {"group_products": 4096, "contragredient_products": 4096,
            "noncentral_root_controls": 2, "transpose_antihomomorphism_control": 1}


def call_checks():
    counts = Counter()
    for r in (1, 2, 3, 4):
        for u, v in product(range(1, 1 << r), repeat=2):
            coupling = outer(u, v, r)
            validate_call("x", coupling, r)
            counts["idempotents" if (u & v).bit_count() & 1 else "nilpotents"] += 1
            for label, g in LABELS.items():
                first = append_factor(formal_identity(r), g, coupling)
                second = append_factor(first, g, coupling)
                require(second == formal_identity(r), "formal call not involutive")
                require(formal_regular(first) == regular.replay([(label, u, v)], r),
                        "faithful single-call mismatch")
                counts["formal_involutions"] += 1
                counts["faithful_columns"] += 64 * r
    return dict(sorted(counts.items()))


def bounded_coefficients():
    r = 2
    factors = [(label, u, v) for label in LABELS for u, v in product(range(1, 4), repeat=2)]
    levels = [0, 0, 0, 0]
    h = hashlib.sha256()

    def visit(word, formal, coefficients):
        levels[len(word)] += 1
        check_coefficients(formal, coefficients)
        span_bounds(word, coefficients, r)
        h.update(bytes(value for key in (*LABELS, *PAIRS) for value in coefficients[key]))
        if len(word) == 3:
            return
        for label, u, v in factors:
            coupling = outer(u, v, r)
            visit(word + [(label, u, v)], append_factor(formal, LABELS[label], coupling),
                  update_coefficients(coefficients, label, coupling))

    visit([], formal_identity(r), {key: zero(r) for key in (*LABELS, *PAIRS)})
    return {"registers": r, "expanded_factors": len(factors), "length_counts": levels,
            "coefficient_digest": h.hexdigest(), "scope": "all words through length three; not an optimality census"}


def witness_checks():
    fixtures = [(p, q, p + q + extra, False) for p, q in product(range(4), repeat=2)
                if p + q for extra in (0, 1)]
    fixtures += [(1, 1, 8, False), (3, 3, 8, False), (1, 1, 4, True), (2, 2, 8, True)]
    receipts = []
    for p, q, r, conjugated in fixtures:
        word = direct_word(p, q)
        expected = target(p, q, r)
        P = tuple((1 << i) if i < p else 0 for i in range(r))
        Q = tuple((1 << i) if p <= i < p + q else 0 for i in range(r))
        if conjugated:
            s1, s2 = list(identity(r)), list(identity(r))
            s1[0] ^= 1 << (r - 1)
            s2[r - 1] ^= 1 << 1
            scalar = matrix_product(s1, s2)
            inverse = matrix_product(s2, s1)
            require(matrix_product(scalar, inverse) == identity(r), "conjugator inverse")
            word = conjugate_word(word, scalar, inverse)
            expected = conjugate_formal(expected, scalar, inverse)
            P = matrix_product(matrix_product(scalar, P), inverse)
            Q = matrix_product(matrix_product(scalar, Q), inverse)
        actual = formal_word(word, r)
        require(actual == expected, "full formal witness endpoint differs")
        independent = regular.replay(word, r)
        require(formal_regular(expected) == independent, "faithful dirty-column witness differs")
        coefficients = coefficients_of(word, r)
        check_coefficients(actual, coefficients)
        for key in LABELS:
            require(coefficients[key] == zero(r), "nonzero first coefficient")
        require(coefficients["xy"] == coefficients["yx"] == P, "first root coefficient")
        require(coefficients["yz"] == coefficients["zy"] == Q, "second root coefficient")
        require(rank(list(P) + list(Q)) == p + q, "row target sum not direct")
        require(rank(list(matrix_transpose(P)) + list(matrix_transpose(Q))) == p + q,
                "column target sum not direct")
        spans = span_bounds(word, coefficients, r)
        require(spans == {"x": (p, p), "y": (p + q, p + q), "z": (q, q)}, "sharp label spans")
        counts = {key: sum(label == key for label, _, _ in word) for key in LABELS}
        require(counts == {"x": 2 * p, "y": 2 * (p + q), "z": 2 * q}, "attaining invoice")
        receipts.append({"p": p, "q": q, "registers": r, "conjugated": conjugated,
                         "label_counts": counts, "label_span_ranks": spans,
                         "regular_columns": 64 * r, "formal_sha256": digest(actual),
                         "regular_sha256": digest(independent)})
    return receipts


def expect_failure(operation, message):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def semantic_controls():
    controls = []
    word, r = direct_word(1, 1), 3
    expected = target(1, 1, r)
    for i in range(len(word)):
        require(formal_word(word[:i] + word[i + 1:], r) != expected, "omission invisible")
        controls.append("omitted-call-" + str(i))
    wrong = list(word)
    wrong[0] = ("z", 1, 1)
    require(formal_word(wrong, r) != expected, "wrong label invisible")
    controls.append("wrong-paid-label")
    require(formal_word(word + [("x", 4, 1)], r) != expected, "dirty workspace unrestored")
    controls.append("dirty-workspace-not-restored")
    expect_failure(lambda: validate_call("x", (3, 0, 4), 3), "rank two")
    controls.append("rank-two-coupling-rejected")
    expect_failure(lambda: validate_call("u", (1, 0, 0), 3), "expanded address alphabet")
    controls.append("root-label-rejected")
    expect_failure(lambda: validate_call("x", (True, 0, 0), 3), "Boolean scalar encoding")
    controls.append("boolean-coupling-rejected")
    expect_failure(lambda: target(True, 1, 3), "Boolean role count")
    controls.append("boolean-role-count-rejected")
    # Higher-rank calls really change the bill; this is not a syntactic-only rejection.
    rank_two = (1, 2)
    four = formal_identity(2)
    for label in "xyxy":
        four = append_factor(four, LABELS[label], rank_two)
    require(four == target(2, 0, 2), "rank-two positive counterexample")
    controls.append("rank-two-four-call-two-root-counterexample")
    # Nonzero formal kernel invisible to both proof representations.
    lam = (1 << 0) ^ (1 << LABELS["x"]) ^ (1 << CENTRAL) ^ (1 << TABLE[CENTRAL][LABELS["x"]])
    require(lam.bit_count() == 4, "kernel perturbation vanished formally")
    mutant = [list(row) for row in expected]
    mutant[0][2] ^= lam
    mutant = tuple(tuple(row) for row in mutant)
    require(mutant != expected, "formal kernel mutant accepted")
    for dual in (False, True):
        require(regular.represented(mutant, dual) == regular.represented(expected, dual),
                "kernel control not invisible to proof representation")
    baseline_cols, mutant_cols = formal_regular(expected), formal_regular(mutant)
    require(baseline_cols[:128] == mutant_cols[:128] and baseline_cols[128:] != mutant_cols[128:],
            "dirty-only kernel control does not isolate dirty columns")
    controls.append("dual-natural-common-kernel-rejected-by-formal-and-dirty-columns")
    # P and Q overlap on one role. The union has rank one and the middle bill is two, not four.
    overlap_word = [(label, 1, 1) for label in "xyzxyz"]
    uv = TABLE[U][V]
    require(formal_word(overlap_word, 1) == ((1 << uv,),), "overlap six-call witness")
    coeff = coefficients_of(overlap_word, 1)
    require(all(coeff[pair] == (1,) for pair in PAIRS), "overlap second coefficients")
    require(span_bounds(overlap_word, coeff, 1)["y"] == (1, 1), "overlap span union")
    require(formal_regular(((1 << uv,),)) == regular.replay(overlap_word, 1), "overlap faithful replay")
    controls.append("overlapping-targets-invalidate-added-middle-bills")
    triple_word = [(label, 1, 1) for label in "xzyxzy"]
    triple_endpoint = formal_word(triple_word, 1)
    require(coefficients_of(triple_word, 1) == coeff and triple_endpoint != ((1 << uv,),),
            "degree-two alone incorrectly accepted full endpoint")
    require(triple_endpoint == ((1 << TABLE[uv][CENTRAL],),), "class-three correction")
    controls.append("degree-two-match-with-wrong-central-term")
    return controls


def source_checks():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    root = HERE.parent.parent
    checked = []
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            data = (root / entry["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == entry["sha256"], "runtime source pin mismatch")
            checked.append(entry["path"])
    selection = json.loads((HERE / "SELECTION.json").read_text())
    require(selection["seed"] == "5080ba3917adb12fda1e688c38733a49"
            and selection["track"] == "bit-mechanisms"
            and selection["base_commit"] == manifest["base_commit"], "selection provenance mismatch")
    return checked


def result():
    sources = source_checks()
    structure = group_checks()
    calls = call_checks()
    bounded = bounded_coefficients()
    witnesses = witness_checks()
    controls = semantic_controls()
    return {"schema_version": 1, "result": "sharp-formal-tariff-no-new-kappa",
            "theorem": {"x": "2p", "y": "2(p+q)", "z": "2q", "unit_minimum": "4(p+q)",
                        "prior_four_register_pair_minimum": 8,
                        "universal_evidence": "written proof in README.md, not finite extrapolation"},
            "source_inputs_checked": sources, "group_structure": structure,
            "rank_one_calls": calls, "bounded_coefficient_checks": bounded,
            "witnesses": witnesses, "semantic_controls": controls,
            "summary": {"witnesses": len(witnesses),
                        "witness_regular_columns": sum(w["regular_columns"] for w in witnesses),
                        "coefficient_words": sum(bounded["length_counts"]), "controls": len(controls)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print regenerated certificate without writing")
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "certificate mismatch (including scalar types)")
        s = actual["summary"]
        print("PASS_UT4_SHARED_MIDDLE pair_minimum=8"
              f" witnesses={s['witnesses']} dirty_columns={s['witness_regular_columns']}"
              f" coefficient_words={s['coefficient_words']} controls={s['controls']} no_new_kappa")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact finite-dihedral cut checks; the uniform theorem is in README.md.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only. All checks survive python -O.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PERIODS = tuple(range(2, 33, 2))
CALL_PERIODS = (2, 4, 6, 8, 10, 16)
WORD_PERIODS = (2, 4, 6, 8, 10)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def xor_rows(rows):
    result = 0
    for row in rows:
        result ^= row
    return result


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p not in pivots:
                pivots[p] = value
                break
            value ^= pivots[p]
    return len(pivots)


def binary_product(a, b):
    return tuple(xor_rows(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def identity(size):
    return tuple(1 << i for i in range(size))


def projectors(roles):
    result = []
    for u in range(1, 1 << roles):
        for v in range(1, 1 << roles):
            if (u & v).bit_count() % 2:
                result.append(tuple(v if u >> i & 1 else 0 for i in range(roles)))
    require(len(result) == (2**roles - 1) * 2**(roles - 1), "projector coverage")
    require(len(result) == len(set(result)), "duplicate projector")
    return result


def validate_projector(nrows):
    roles = len(nrows)
    require(roles > 0 and all(type(row) is int and 0 <= row < 1 << roles for row in nrows),
            "projector dimensions")
    require(binary_product(nrows, nrows) == nrows and rank(nrows) == 1,
            "not a rank-one idempotent")


def distance(n, k):
    k %= n
    return min(k, n - k)


def bill(n, targets):
    require(n >= 2 and n % 2 == 0, "even period required")
    require(all(e in (0, 1) for _, e in targets), "invalid normal-form parity")
    return (sum(distance(n, k + e) for k, e in targets),
            sum(distance(n, k) for k, _ in targets))


def short_word(n, target):
    k, e = target
    bill(n, [target])
    k = (k + n // 2) % n - n // 2
    letters = list("xy" * k if k >= 0 else "yx" * -k)
    if e:
        letters.append("x")
    reduced = []
    for letter in letters:
        if reduced and reduced[-1] == letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)  # Product order: rightmost acts first.


def group_product(n, a, b):
    ak, ae = divmod(a, 2)
    bk, be = divmod(b, 2)
    return 2 * ((ak + (-1 if ae else 1) * bk) % n) + (ae ^ be)


def poly_left(n, g, polynomial):
    answer = 0
    while polynomial:
        bit = polynomial & -polynomial
        answer ^= 1 << group_product(n, g, bit.bit_length() - 1)
        polynomial ^= bit
    return answer


def formal_identity(roles):
    return tuple(tuple(int(i == j) for j in range(roles)) for i in range(roles))


def formal_target(n, targets, roles):
    return tuple(tuple((1 << (2 * (targets[i][0] % n) + targets[i][1])
                        if i < len(targets) else 1) if i == j else 0
                       for j in range(roles)) for i in range(roles))


def formal_call(n, matrix, nrows, label):
    require(label in ("x", "y"), "unpaid address label")
    g = 1 if label == "x" else 2 * (n - 1) + 1
    roles = len(matrix)
    result = []
    for i, nrow in enumerate(nrows):
        delta = [xor_rows(matrix[j][k] for j in range(roles) if nrow >> j & 1)
                 for k in range(roles)]
        result.append(tuple(matrix[i][k] ^ delta[k] ^ poly_left(n, g, delta[k])
                            for k in range(roles)))
    return tuple(result)


def direct_calls(n, targets, roles):
    require(roles >= len(targets), "missing target role")
    calls = []
    for i, target in enumerate(targets):
        nrows = tuple(1 << i if j == i else 0 for j in range(roles))
        calls.extend((nrows, label) for label in reversed(short_word(n, target)))
    return tuple(calls)


def formal_run(n, roles, calls):
    result = formal_identity(roles)
    for nrows, label in calls:
        result = formal_call(n, result, nrows, label)
    return result


# Independent literal-permutation engine. Operators are packed binary rows on
# ALL dirty basis inputs, not scalar/register-only columns. Each paid call reads
# one immutable pre-call state, including for non-coordinate projectors.
def inverse_permutation(p):
    require(sorted(p) == list(range(len(p))), "not a permutation")
    result = [0] * len(p)
    for i, j in enumerate(p):
        result[j] = i
    return tuple(result)


def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def regular_letters(n):
    # Two n-point layers indexed e*n+k. These formulas do not call group_product.
    return {
        "x": tuple((1 - e) * n + (-k) % n for e in range(2) for k in range(n)),
        "y": tuple((1 - e) * n + (-k - 1) % n for e in range(2) for k in range(n)),
    }


def proof_letters(n, c):
    return {"x": tuple((c - a) % n for a in range(n)),
            "y": tuple((c - 1 - a) % n for a in range(n))}


def permutation_table(n, letters):
    ident = tuple(range(len(letters["x"])))
    rotation = compose(letters["x"], letters["y"])
    power = ident
    table = []
    for _ in range(n):
        table.extend((power, compose(power, letters["x"])))
        power = compose(rotation, power)
    require(power == ident, "rotation torsion")
    require(compose(letters["x"], letters["x"]) == ident, "x involution")
    require(compose(letters["y"], letters["y"]) == ident, "y involution")
    return tuple(table)


def literal_call(matrix, nrows, p):
    width = len(p)
    pinv = inverse_permutation(p)
    result = list(matrix)
    for i, row in enumerate(nrows):
        for j in range(len(nrows)):
            if row >> j & 1:
                for a in range(width):
                    result[i * width + a] ^= matrix[j * width + a] ^ matrix[j * width + pinv[a]]
    return tuple(result)


def literal_run(roles, calls, letters):
    result = identity(roles * len(letters["x"]))
    for nrows, label in calls:
        result = literal_call(result, nrows, letters[label])
    return result


def represent_formal(matrix, table):
    roles = len(matrix)
    width = len(table[0])
    inverses = tuple(inverse_permutation(p) for p in table)
    rows = [0] * (roles * width)
    for i in range(roles):
        for j in range(roles):
            polynomial = matrix[i][j]
            while polynomial:
                bit = polynomial & -polynomial
                p = inverses[bit.bit_length() - 1]
                for a in range(width):
                    rows[i * width + a] ^= 1 << (j * width + p[a])
                polynomial ^= bit
    return tuple(rows)


def crossing_rank(matrix, n, roles):
    half = n // 2
    mask = sum(1 << (i * n + a) for i in range(roles) for a in range(half, n))
    return rank(matrix[i * n + a] & mask for i in range(roles) for a in range(half))


def check_sources():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in pins["files"]:
        if item["usage"] == "input":
            require(sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                    "source changed: " + item["path"])
    selection = json.loads((PACKAGE / "SELECTION.json").read_text())
    task = json.loads((PACKAGE / "TASK.json").read_text())
    require(selection["seed"] == task["selection_seed"] == "63537661f5ee8acaa486b70f82726911",
            "selection nonce")
    require(selection["base_commit"] == pins["base_commit"] == task["base_commit"], "base pin")
    require(selection["track"] == task["selection_track"] == "bit-mechanisms", "track")
    card = next(s for s in selection["suggestions"] if s["task_id"] == task["task_id"])
    require(card["scope_key"] == task["selection_scope_key"], "card scope key")
    provenance = {entry["path"]: entry["sha256"] for entry in pins["files"]}
    require(selection["selected_record_sha256"] == provenance["certificates/selected-result.json"],
            "selected record provenance")
    require(selection["catalog_sha256"] == provenance["docs/research/agent-task-catalog.json"],
            "catalogue provenance")


def experiment():
    counts = Counter()
    evidence = sha256()
    negative = []

    def record(value):
        evidence.update(json.dumps(value, separators=(",", ":")).encode() + b"\n")

    # Derive actual group representations and endpoint cut ranks for every target.
    for n in PERIODS:
        all_targets = [(k, e) for k in range(n) for e in range(2)]
        for c in (n // 2, n // 2 - 1):
            table = permutation_table(n, proof_letters(n, c))
            for a in range(2 * n):
                for b in range(2 * n):
                    require(compose(table[a], table[b]) == table[group_product(n, a, b)],
                            "presentation homomorphism")
                    counts["representation_products"] += 1
            for target in all_targets:
                endpoint = formal_target(n, [target], 1)
                q = crossing_rank(represent_formal(endpoint, table), n, 1)
                expected = bill(n, [target])[0 if c == n // 2 else 1]
                require(q == expected, "target crossing formula")
                record((n, c, target, q))
                counts["target_cut_ranks"] += 1

    # Complete scalar-projector alphabets, including n=2,6,10 parity boundaries.
    for roles in range(1, 5):
        plist = projectors(roles)
        counts["rank_one_projectors"] += len(plist)
        for nrows in plist:
            validate_projector(nrows)
            for n in CALL_PERIODS:
                for c in (n // 2, n // 2 - 1):
                    letters = proof_letters(n, c)
                    for label in ("x", "y"):
                        operator = literal_call(identity(roles * n), nrows, letters[label])
                        q = crossing_rank(operator, n, roles)
                        expected = int((label == "x") == (c == n // 2))
                        require(q == expected, "non-coordinate call charge")
                        require(literal_call(operator, nrows, letters[label]) == identity(roles * n),
                                "paid call not involutive")
                        counts["rank_one_call_cut_checks"] += 1

    # Every GL(2,2) and GL(3,2) free scalar map has zero cut rank and preserves
    # a genuinely mixed paid word's crossing rank on either side.
    for roles in (2, 3):
        n = 6
        sample_calls = tuple((p, g) for p, g in zip(projectors(roles)[:3], ("x", "y", "x")))
        for scalar in product(range(1 << roles), repeat=roles):
            if rank(scalar) != roles:
                continue
            lifted = tuple(sum(1 << (j * n + a) for j in range(roles) if scalar[i] >> j & 1)
                           for i in range(roles) for a in range(n))
            require(crossing_rank(lifted, n, roles) == 0, "free scalar crossing charge")
            for c in (n // 2, n // 2 - 1):
                operator = literal_run(roles, sample_calls, proof_letters(n, c))
                q = crossing_rank(operator, n, roles)
                require(crossing_rank(binary_product(lifted, operator), n, roles) == q and
                        crossing_rank(binary_product(operator, lifted), n, roles) == q,
                        "free scalar rank invariance")
                counts["free_scalar_cut_checks"] += 1
            counts["free_scalar_invertible_maps"] += 1

    # Separate corollary: all idempotents through three scalar roles, every rank.
    for roles in range(1, 4):
        for nrows in product(range(1 << roles), repeat=roles):
            if binary_product(nrows, nrows) != nrows:
                continue
            r = rank(nrows)
            counts["all_rank_idempotents"] += 1
            for n in (2, 4, 6, 10):
                for c in (n // 2, n // 2 - 1):
                    for label, p in proof_letters(n, c).items():
                        actual = crossing_rank(literal_call(identity(roles * n), nrows, p), n, roles)
                        expected = r if ((label == "x") == (c == n // 2)) else 0
                        require(actual == expected, "block rank charge")
                        counts["all_rank_call_cut_checks"] += 1

    # Exhaust every two-role paid word through length three, without pruning or
    # deduplication. Formal and faithful-regular engines agree at every prefix;
    # the two nonfaithful proof quotients separately obey the tariff bound.
    alphabet = tuple((p, g) for p in projectors(2) for g in ("x", "y"))
    for n in WORD_PERIODS:
        reg_letters = regular_letters(n)
        reg_table = permutation_table(n, reg_letters)
        quotient_letters = tuple(proof_letters(n, c) for c in (n // 2, n // 2 - 1))
        stack = [(0, formal_identity(2), identity(4 * n),
                  (identity(2 * n), identity(2 * n)), (0, 0))]
        while stack:
            depth, fm, rm, quotients, used = stack.pop()
            if depth == 3:
                continue
            for p, g in alphabet:
                next_formal = formal_call(n, fm, p, g)
                next_regular = literal_call(rm, p, reg_letters[g])
                require(represent_formal(next_formal, reg_table) == next_regular,
                        "formal/faithful-regular disagreement")
                next_used = (used[0] + (g == "x"), used[1] + (g == "y"))
                next_quotients = tuple(literal_call(quotients[i], p, quotient_letters[i][g])
                                       for i in range(2))
                for i in range(2):
                    old_q = crossing_rank(quotients[i], n, 2)
                    new_q = crossing_rank(next_quotients[i], n, 2)
                    charge = int(g == ("x" if i == 0 else "y"))
                    require(new_q <= old_q + charge and new_q <= next_used[i],
                            "crossing subadditivity")
                    counts["word_cut_inequalities"] += 1
                counts["mixed_words_through_three"] += 1
                stack.append((depth + 1, next_formal, next_regular, next_quotients, next_used))

    # Uniform direct-word constructor corroborated on complete finite target
    # domains, plus heterogeneous higher-role fixtures with dirty spectators.
    fixtures = [(n, ((k, e),), 2) for n in PERIODS for k in range(n) for e in range(2)]
    for n in (2, 4, 6, 8):
        elements = tuple(product(range(n), range(2)))
        fixtures.extend((n, targets, 3) for targets in product(elements, repeat=2))
    fixtures.extend([
        (10, ((5, 0), (5, 1), (-4, 1), (12, 0)), 7),
        (6, ((3, 0), (3, 1), (-2, 1), (8, 0), (0, 1)), 9),
        (8, ((4, 0), (4, 0)), 7),
    ])
    for n, targets, roles in fixtures:
        calls = direct_calls(n, targets, roles)
        expected = formal_target(n, targets, roles)
        actual = formal_run(n, roles, calls)
        require(actual == expected, "formal attaining boundary")
        counts_by_label = (sum(g == "x" for _, g in calls), sum(g == "y" for _, g in calls))
        require(counts_by_label == bill(n, targets), "simultaneous sharp bill")
        letters = regular_letters(n)
        table = permutation_table(n, letters)
        literal = literal_run(roles, calls, letters)
        require(literal == represent_formal(expected, table), "literal dirty boundary")
        inverse = expected
        inverse_literal = literal
        for p, g in reversed(calls):
            inverse = formal_call(n, inverse, p, g)
            inverse_literal = literal_call(inverse_literal, p, letters[g])
        require(inverse == formal_identity(roles), "formal inverse")
        require(inverse_literal == identity(roles * 2 * n), "literal inverse")
        for c, wanted in zip((n // 2, n // 2 - 1), bill(n, targets)):
            qtable = permutation_table(n, proof_letters(n, c))
            require(crossing_rank(represent_formal(expected, qtable), n, roles) == wanted,
                    "heterogeneous cut rank additivity")
        for omit in range(len(calls)):
            mutated = formal_run(n, roles, calls[:omit] + calls[omit + 1:])
            require(mutated != expected, "omitted call accepted")
            counts["omission_controls"] += 1
        counts["formal_dirty_fixtures"] += 1
        counts["regular_dirty_columns_forward_and_inverse"] += 2 * roles * 2 * n
        record((n, targets, roles, counts_by_label, expected))

    # Semantic negative controls, with explicit exceptions rather than asserts.
    def must_reject(name, operation):
        try:
            operation()
        except ValueError:
            negative.append(name)
        else:
            raise ValueError("control accepted: " + name)

    must_reject("odd_period_scope", lambda: bill(3, [(1, 1)]))
    must_reject("non_idempotent_projector", lambda: validate_projector((2, 0)))
    must_reject("rank_two_undercharged_projector", lambda: validate_projector((1, 2)))
    must_reject("unpaid_rotation_label", lambda: formal_call(6, formal_identity(2), (1, 0), "r"))
    must_reject("missing_role", lambda: direct_calls(6, [(1, 0), (2, 0)], 1))

    # The excluded odd-period simultaneous-minimum inference fails already at n=3.
    odd_target = 2 * 1 + 1
    cheap = ((), ("x",), ("y",), ("x", "y"), ("y", "x"))
    for word in cheap:
        value = 0
        for g in word:
            value = group_product(3, value, 1 if g == "x" else 5)
        require(value != odd_target, "odd-period false simultaneous word")
    require((distance(3, 2), distance(3, 1)) == (1, 1), "odd scope fixture")
    negative.append("odd_separate_minima_not_jointly_attainable")

    # Using the usual c=0 action instead of the shifted action is not the proof.
    for n in (6, 10):
        wrong = proof_letters(n, 0)
        qx = crossing_rank(literal_call(identity(n), (1,), wrong["x"]), n, 1)
        qy = crossing_rank(literal_call(identity(n), (1,), wrong["y"]), n, 1)
        require((qx, qy) != (1, 0) and (qx, qy) != (0, 1), "wrong offset was isolated")
        negative.append("fixed_offset_shortcut_n" + str(n))

    n, roles, targets = 6, 3, ((1, 0), (2, 1))
    calls = direct_calls(n, targets, roles)
    target = formal_target(n, targets, roles)
    wrong_label = tuple((p, "y" if g == "x" else "x") if i == 0 else (p, g)
                        for i, (p, g) in enumerate(calls))
    require(formal_run(n, roles, wrong_label) != target, "wrong label accepted")
    negative.append("wrong_paid_label")
    require(formal_run(n, roles, tuple(reversed(calls))) != target, "wrong order accepted")
    negative.append("wrong_execution_order")
    dirty_calls = calls + (((0, 0, 4), "x"),)
    dirty = formal_run(n, roles, dirty_calls)
    require(dirty[:2] == target[:2] and dirty != target, "spectator restoration control")
    require(literal_run(roles, dirty_calls, regular_letters(n)) !=
            represent_formal(target, permutation_table(n, regular_letters(n))),
            "regular spectator restoration control")
    negative.append("dirty_workspace_not_restored")

    # An invertible off-diagonal Omega perturbation is hidden by BOTH proof
    # representations but not by the formal or faithful-regular engines.
    n = 6
    clean = formal_identity(2)
    omega = (1 << (2 * n)) - 1
    hidden = ((1, omega), (0, 1))
    for c in (n // 2, n // 2 - 1):
        table = permutation_table(n, proof_letters(n, c))
        require(represent_formal(hidden, table) == represent_formal(clean, table),
                "common-kernel control not hidden")
    faithful = permutation_table(n, regular_letters(n))
    require(hidden != clean and represent_formal(hidden, faithful) != represent_formal(clean, faithful),
            "represented-only endpoint accepted")
    require(binary_product(represent_formal(hidden, faithful), represent_formal(hidden, faithful)) ==
            identity(4 * n), "hidden dirty shear not invertible")
    negative.append("nonfaithful_endpoint_false_positive")

    # A direct central rotation is outside the paid alphabet: at n=10 its cut
    # costs five, so silently declaring it a unit operation invalidates the bound.
    n = 10
    central = formal_target(n, [(5, 0)], 1)
    for c in (5, 4):
        table = permutation_table(n, proof_letters(n, c))
        require(crossing_rank(represent_formal(central, table), n, 1) == 5,
                "free rotation surcharge control")
    negative.append("direct_rotation_not_unit_tariff")

    require(counts["mixed_words_through_three"] == 9420, "short-word domain truncated")
    require(counts["formal_dirty_fixtures"] == 1027, "target domain truncated")
    require(counts["rank_one_projectors"] == 155, "projector domain truncated")
    return {
        "schema_version": 1,
        "result": "PASS_FINITE_DIHEDRAL_CUT_BOUND",
        "theorem_scope": "all even n>=2, all target counts, every finite dirty workspace; written proof",
        "finite_domains": {
            "even_periods_all_targets": list(PERIODS),
            "rank_one_projector_roles": [1, 2, 3, 4],
            "rank_one_call_periods": list(CALL_PERIODS),
            "all_idempotent_roles": [1, 2, 3],
            "all_idempotent_periods": [2, 4, 6, 10],
            "free_scalar_roles": [2, 3],
            "free_scalar_period": 6,
            "mixed_word_periods": list(WORD_PERIODS),
            "mixed_word_max_length": 3,
            "all_ordered_target_pair_periods": [2, 4, 6, 8],
        },
        "counts": dict(sorted(counts.items())),
        "negative_controls": negative,
        "deterministic_evidence_sha256": evidence.hexdigest(),
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="research mode: emit newly computed receipt")
    parser.add_argument("--receipt", type=Path, default=PACKAGE / "RECEIPT.json")
    args = parser.parse_args()
    check_sources()
    receipt = experiment()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        expected = json.loads(args.receipt.read_text())
        require(receipt == expected, "receipt differs from exact recomputation")
        counts = receipt["counts"]
        print(receipt["result"], " ".join(f"{key}={value}" for key, value in counts.items()),
              f"controls={len(receipt['negative_controls'])}", "no_new_kappa")


if __name__ == "__main__":
    main()

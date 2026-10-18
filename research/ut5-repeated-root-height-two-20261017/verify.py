#!/usr/bin/env python3
"""Exact three-call obstruction for one four-role target in F2[UT5(Z)]."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = "research/ut5-four-role-mixed-root-seede2a8/verify.py"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load_predecessor():
    path = ROOT / PREDECESSOR
    spec = importlib.util.spec_from_file_location("pinned_ut5_predecessor", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned UT5 arithmetic helpers")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = []
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        path = ROOT / item["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == item["sha256"], f"source pin mismatch: {item['path']}")
        checked.append(item["path"])
    require(PREDECESSOR in checked, "the imported predecessor verifier is not a pinned live input")
    return checked


def main():
    checked_sources = source_pins()
    m = load_predecessor()

    pos = [m.root(i, 1) for i in range(4)]
    neg = [m.root(i, -1) for i in range(4)]
    labels = [q for i in range(4) for q in (pos[i], neg[i])]
    label_names = [q for i in range(1, 5) for q in (f"g{i}", f"g{i}^-1")]
    require(len(labels) == 8 and all(m.chi(g) == 1 for g in labels),
            "signed simple-root character mismatch")
    require(all(m.group_mul(labels[2 * i], labels[2 * i + 1]) == m.ZERO for i in range(4)),
            "signed simple-root labels are not inverse pairs")
    require(m.group_mul(pos[0], pos[1]) != m.group_mul(pos[1], pos[0]),
            "UT5(Z) adjacent simple roots unexpectedly commute")

    # Exact endpoint: two g1 outputs, one g2 output, and one g1*g2 output.
    target = [pos[0], pos[0], pos[1], m.group_mul(pos[0], pos[1])]
    require(target[0] == target[1] and len(set(target)) == 3 and m.ZERO not in target,
            "endpoint is not the stated repeated-root mixed-height target")
    target_character = [m.chi(g) for g in target]
    require(target_character == [1, 1, 1, 0] and sum(target_character) % 2 == 1,
            "target determinant character is not z")

    idempotents = m.enumerate_idempotents()
    gates = m.gate_pairs(labels, idempotents)
    gate_count = len(gates)
    require(len(idempotents) == 120 and gate_count == 960,
            "complete four-role paid alphabet has unexpected size")
    idem_index = {(x, y): i for i, (x, y, _) in enumerate(idempotents)}

    # Five-call positive control: one factor per simple target and two for g1*g2.
    direct_word = [
        (0, idem_index[(1, 1)]),
        (0, idem_index[(2, 2)]),
        (2, idem_index[(4, 4)]),
        (0, idem_index[(8, 8)]),
        (2, idem_index[(8, 8)]),
    ]
    direct = [frozenset({m.ZERO}) if i == j else frozenset()
              for i in range(4) for j in range(4)]
    for gate in direct_word:
        direct = m.matrix_mul(direct, m.gate_matrix(gate, labels, idempotents))
    require(direct == m.target_matrix(target), "five-call direct word failed full formal replay")

    # The address letters are literal integer UT5(Z) matrices; each g-I is
    # exactly one signed matrix unit, hence rank one over Q.
    native_updates = []
    for name, label in zip(label_names, labels):
        nonzero = [(i, j, value) for (i, j), value in zip(m.POS, label) if value]
        require(len(nonzero) == 1 and abs(nonzero[0][2]) == 1,
                f"{name}: address difference is not a signed rank-one matrix unit")
        native_updates.append({"letter": name, "difference_entry": list(nonzero[0]),
                               "rank_over_Q": 1, "inverse_is_in_alphabet": True})

    # Exact finite support universe for every two-factor state and T*C^{-1} query.
    element_set = {m.ZERO, *labels, *target}
    for g in labels:
        for h in labels:
            element_set.add(m.group_mul(g, h))
    for t in target:
        for h in labels:
            element_set.add(m.group_mul(t, h))
    elements = sorted(element_set)
    require(len(elements) < 255, "exact support-key element ids exceed one byte")
    id_by_element = {g: i for i, g in enumerate(elements)}
    id_e = id_by_element[m.ZERO]
    lambda_masks = [(1 << id_e) ^ (1 << id_by_element[g]) for g in labels]
    lambda_products = []
    for g in labels:
        row = []
        for h in labels:
            gh = m.group_mul(g, h)
            row.append((1 << id_e) ^ (1 << id_by_element[g]) ^
                       (1 << id_by_element[h]) ^ (1 << id_by_element[gh]))
        lambda_products.append(row)

    # Build the exact product table for all 960^2 ordered pairs.
    pair_map = {}
    pair_hash = hashlib.sha256()
    for ai, a in enumerate(gates):
        for bi, b in enumerate(gates):
            masks = m.pair_product_masks(a, b, idempotents, lambda_masks,
                                         lambda_products, id_e)
            key = m.encode_masks(masks, id_by_element)
            pair_hash.update(ai.to_bytes(2, "big") + bi.to_bytes(2, "big") + key)
            pair_map.setdefault(key, ai * gate_count + bi)

    # Query every legal right factor C using AB = T*C^{-1}. Each query is also
    # checked by independent sparse matrix multiplication in the full group algebra.
    hits = []
    query_hash = hashlib.sha256()
    query_full_algebra_checks = 0
    for ci, c in enumerate(gates):
        query_masks = m.target_times_inverse_masks(target, c, labels, idempotents,
                                                   id_by_element)
        li, ni = c
        inverse_gate = (li ^ 1, ni)
        query_matrix = m.matrix_mul(m.target_matrix(target),
                                    m.gate_matrix(inverse_gate, labels, idempotents))
        require(query_masks == m.support_masks_for_matrix(query_matrix, id_by_element),
                "right-query formula disagrees with full-algebra multiplication")
        query_full_algebra_checks += 1
        key = m.encode_masks(query_masks, id_by_element)
        query_hash.update(ci.to_bytes(2, "big") + key)
        packed = pair_map.get(key)
        if packed is not None:
            ai, bi = divmod(packed, gate_count)
            witness = (gates[ai], gates[bi], c)
            replay = [frozenset({m.ZERO}) if i == j else frozenset()
                      for i in range(4) for j in range(4)]
            for gate in witness:
                replay = m.matrix_mul(replay, m.gate_matrix(gate, labels, idempotents))
            require(replay == m.target_matrix(target),
                    "meet-in-the-middle hit failed full formal replay")
            hits.append(witness)

    # Formula/key implementation control: all 16 pairs from a tiny four-gate
    # alphabet agree with independent full-algebra multiplication, and a known
    # two-factor diagonal endpoint is found positively.
    e11, e22 = idem_index[(1, 1)], idem_index[(2, 2)]
    tiny = [(0, e11), (2, e11), (0, e22), (2, e22)]
    tiny_target = [pos[0], pos[1], m.ZERO, m.ZERO]
    tiny_positive = False
    for a in tiny:
        for b in tiny:
            formula = m.pair_product_masks(a, b, idempotents, lambda_masks,
                                            lambda_products, id_e)
            formula_key = m.encode_masks(formula, id_by_element)
            brute = m.matrix_mul(m.gate_matrix(a, labels, idempotents),
                                 m.gate_matrix(b, labels, idempotents))
            brute_key = m.encode_masks(m.support_masks_for_matrix(brute, id_by_element),
                                       id_by_element)
            require(formula_key == brute_key,
                    "pair formula disagrees with full algebra on tiny control")
            if brute == m.target_matrix(tiny_target):
                tiny_positive = True
    require(tiny_positive, "known two-factor positive control did not replay")

    # A single factor has address support in {1,g}, while this target has
    # three distinct nonidentity addresses. Verify the finite control too.
    one_call_hits = sum(m.gate_matrix(gate, labels, idempotents) ==
                        m.target_matrix(target) for gate in gates)
    require(one_call_hits == 0, "one-call support obstruction control failed")
    require(not hits, "unexpected three-call realization; exact-minimum claim must be revised")

    result = {
        "schema_version": 1,
        "status": "PASS_UT5_REPEATED_ROOT_NO_THREE_CALLS",
        "task_id": "bit-new-register-model",
        "base_commit": "463113d675af7410ac91d53a4fed51ec6494eb9a",
        "source_pins_checked": checked_sources,
        "model": {
            "address_group": "UT5(Z), full formal group algebra over F2",
            "register_roles": 4,
            "all_input_roles_dirty": True,
            "simple_root_generators": [f"g{i}=I+E_{{{i},{i+1}}}" for i in range(1, 5)],
            "signed_address_letters": label_names,
            "rank_one_idempotents": len(idempotents),
            "paid_factor_alphabet_size": gate_count,
            "endpoint": ["g1", "g1", "g2", "g1*g2"],
            "address_difference_checks": native_updates,
        },
        "exact_minimum": {
            "paid_factors": 5,
            "direct_word": [
                {"letter": label_names[li], "x": idempotents[ni][0],
                 "y": idempotents[ni][1]} for li, ni in direct_word
            ],
            "lower_bound_components": [
                "determinant character forces odd length",
                "length zero is not the nonidentity endpoint",
                "one factor cannot support three distinct nonidentity group symbols",
                "complete exact join excludes every three-factor word",
            ],
        },
        "character": {
            "map": "sum of first-superdiagonal entries modulo 2",
            "signed_simple_roots_map_to": "z in C2",
            "target_diagonal_maps_to": ["z", "z", "z", "1"],
            "each_paid_factor_determinant": "z",
            "target_determinant": "z",
            "conclusion": "every realizing word has odd length",
        },
        "pricing": {
            "direct_and_exact_minimum_calls": 5,
            "three_call_saving_if_present": 2,
            "relative_saving_if_present": "2/5",
            "observed_saving": 0,
            "supplier_or_kappa_change": False,
        },
        "search": {
            "ordered_two_factor_states": gate_count ** 2,
            "unique_exact_pair_states": len(pair_map),
            "right_factor_queries": gate_count,
            "right_query_hits": len(hits),
            "right_queries_checked_against_full_algebra": query_full_algebra_checks,
            "ordered_pair_transcript_sha256": pair_hash.hexdigest(),
            "right_query_transcript_sha256": query_hash.hexdigest(),
        },
        "controls": {
            "five_factor_positive_control_full_formal_equality": "pass",
            "tiny_pair_formula_checks": 16,
            "tiny_two_factor_positive_control": "pass",
            "all_960_right_query_formulas_checked_by_full_algebra": query_full_algebra_checks,
            "all_120_idempotents_checked_by_predecessor_enumerator": "pass",
            "one_factor_negative_control_hits": one_call_hits,
            "all_signed_address_differences_have_Q_rank_one": len(native_updates),
            "three_factor_join_hits": len(hits),
        },
        "scope": "Exact minimum only for diag([g1],[g1],[g2],[g1*g2]) in the stated four-role alphabet over F2[UT5(Z)]. It implies no supplier transfer, selected-kappa change, or minimum for other targets or operation alphabets.",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    result_path = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write"]:
        result_path.write_text(rendered, encoding="utf-8")
    else:
        require(sys.argv[1:] == [], "usage: verify.py [--write]")
        require(result_path.read_text(encoding="utf-8") == rendered,
                "RESULT.json differs from exact replay")
    print("PASS_UT5_REPEATED_ROOT_NO_THREE_CALLS min_calls=5 alphabet=960 "
          f"pair_states={len(pair_map)} three_factor_hits={len(hits)} "
          f"right_query_checks={query_full_algebra_checks} no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print("FAIL:", exc)
        raise SystemExit(1)

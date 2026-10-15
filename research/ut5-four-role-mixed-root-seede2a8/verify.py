#!/usr/bin/env python3
"""Exact 3-call meet-in-the-middle in F_2[UT_5(Z)] for one four-role target."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 4
POS = [(i, j) for i in range(5) for j in range(i + 1, 5)]
POS_ID = {p: k for k, p in enumerate(POS)}
ZERO = (0,) * 10


def require(ok, why):
    if not ok:
        raise ValueError(why)


def group_mul(a, b):
    """Multiply I+A and I+B in UT_5(Z), storing the ten strict upper entries."""
    out = []
    for i, j in POS:
        z = a[POS_ID[i, j]] + b[POS_ID[i, j]]
        for k in range(i + 1, j):
            z += a[POS_ID[i, k]] * b[POS_ID[k, j]]
        out.append(z)
    return tuple(out)


def root(i, sign=1):
    z = [0] * 10
    z[POS_ID[i, i + 1]] = sign
    return tuple(z)


def chi(g):
    return sum(g[POS_ID[i, i + 1]] for i in range(4)) & 1


def enumerate_idempotents():
    out = []
    seen = set()
    for x in range(1, 16):
        for y in range(1, 16):
            if (x & y).bit_count() & 1:
                n = 0
                for r in range(4):
                    for c in range(4):
                        if ((x >> r) & 1) and ((y >> c) & 1):
                            n |= 1 << (4 * r + c)
                require(n not in seen, "duplicate rank-one idempotent")
                seen.add(n)
                out.append((x, y, n))
    require(len(out) == 120, "four-dimensional rank-one idempotent count changed")
    # Verify N^2=N and trace(N)=1 for every enumerated frame.
    for x, y, n in out:
        require((y & x).bit_count() & 1, "non-idempotent entered the paid alphabet")
        tr = sum((n >> (5 * r)) & 1 for r in range(4))  # diagonal bits are 0,5,10,15
        require(tr & 1, "rank-one idempotent has wrong trace")
        for r in range(4):
            for c in range(4):
                lhs = sum(((n >> (4 * r + k)) & 1) * ((n >> (4 * k + c)) & 1)
                          for k in range(4)) & 1
                rhs = (n >> (4 * r + c)) & 1
                require(lhs == rhs, "enumerated frame failed N^2=N")
    return out


def encode_masks(masks, id_by_element):
    """Canonical fixed-width byte key; each paired-call entry has at most four terms."""
    out = bytearray()
    for mask in masks:
        ids = []
        while mask:
            bit = mask & -mask
            ids.append(bit.bit_length() - 1)
            mask ^= bit
        require(len(ids) <= 4, "two-call entry exceeded four formal support terms")
        require(all(i < 255 for i in ids), "support-key element id does not fit one byte")
        out.append(len(ids))
        out.extend(ids)
        out.extend([255] * (4 - len(ids)))
    return bytes(out)


def gate_pairs(labels, idempotents):
    return [(li, ni) for li in range(len(labels)) for ni in range(len(idempotents))]


def pair_product_masks(a, b, idempotents, lambda_masks, lambda_products, id_e):
    """Use D_N(g)D_M(h)=I+lambda_g N+lambda_h M+lambda_g lambda_h NM."""
    la, na = a
    lb, nb = b
    x, y, _ = idempotents[na]
    u, v, _ = idempotents[nb]
    nm = (y & u).bit_count() & 1
    lg, lh = lambda_masks[la], lambda_masks[lb]
    lgh = lambda_products[la][lb]
    out = []
    for r in range(4):
        xr, ur = (x >> r) & 1, (u >> r) & 1
        for c in range(4):
            yc, vc = (y >> c) & 1, (v >> c) & 1
            z = (1 << id_e) if r == c else 0
            if xr and yc:
                z ^= lg
            if ur and vc:
                z ^= lh
            if nm and xr and vc:
                z ^= lgh
            out.append(z)
    return out


def make_pair_product(a, b, idempotents, lambda_masks, lambda_products, id_e):
    return pair_product_masks(a, b, idempotents, lambda_masks, lambda_products, id_e)


def target_times_inverse_masks(target, gate, labels, idempotents, id_by_element):
    li, ni = gate
    inv_li = li ^ 1  # labels are ordered g1,g1^-1,g2,g2^-1,...
    x, y, _ = idempotents[ni]
    inv_g = labels[inv_li]
    out = []
    for r in range(4):
        xr = target[r]
        for c in range(4):
            z = (1 << id_by_element[xr]) if r == c else 0
            if ((x >> r) & 1) and ((y >> c) & 1):
                z ^= 1 << id_by_element[xr]
                z ^= 1 << id_by_element[group_mul(xr, inv_g)]
            out.append(z)
    return out


def gate_matrix(gate, labels, idempotents):
    li, ni = gate
    g = labels[li]
    x, y, _ = idempotents[ni]
    out = []
    for r in range(4):
        for c in range(4):
            s = set()
            if r == c:
                s.add(ZERO)
            if ((x >> r) & 1) and ((y >> c) & 1):
                for q in (ZERO, g):
                    if q in s:
                        s.remove(q)
                    else:
                        s.add(q)
            out.append(frozenset(s))
    return out


def target_matrix(target):
    return [frozenset({target[r]}) if r == c else frozenset()
            for r in range(4) for c in range(4)]


def matrix_mul(a, b):
    """Independent sparse full-group-algebra matrix product over F_2."""
    out = []
    for i in range(4):
        for j in range(4):
            s = set()
            for k in range(4):
                for x in a[4 * i + k]:
                    for y in b[4 * k + j]:
                        z = group_mul(x, y)
                        if z in s:
                            s.remove(z)
                        else:
                            s.add(z)
            out.append(frozenset(s))
    return out


def support_masks_for_matrix(matrix, id_by_element):
    out = []
    for entry in matrix:
        mask = 0
        for g in entry:
            mask ^= 1 << id_by_element[g]
        out.append(mask)
    return out


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    checked_sources = []
    for item in sources["files"]:
        if item["usage"] == "input":
            actual = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            require(actual == item["sha256"], f"source pin mismatch: {item['path']}")
            checked_sources.append(item["path"])

    pos = [root(i, 1) for i in range(4)]
    neg = [root(i, -1) for i in range(4)]
    labels = [q for i in range(4) for q in (pos[i], neg[i])]
    label_names = [q for i in range(1, 5)
                   for q in (f"g{i}", f"g{i}^-1")]
    require(all(chi(g) == 1 for g in labels), "simple-root character mismatch")
    require(all(group_mul(labels[2 * i], labels[2 * i + 1]) == ZERO for i in range(4)),
            "signed simple-root labels are not inverse pairs")
    require(group_mul(pos[0], pos[1]) != group_mul(pos[1], pos[0]),
            "UT5(Z) model unexpectedly commutative")

    targets = [group_mul(pos[0], pos[1]), pos[1], pos[2], pos[3]]
    require(len(set(targets)) == 4 and ZERO not in targets, "target labels are not distinct nonidentity elements")
    require(chi(targets[0]) ^ chi(targets[1]) ^ chi(targets[2]) ^ chi(targets[3]) == 1,
            "target character is not odd")

    # A direct native invoice: the first output uses g1,g2; each other role uses one letter.
    idempotents = enumerate_idempotents()
    idem_index = {(x, y): i for i, (x, y, _) in enumerate(idempotents)}
    direct = [
        (0, idem_index[(1, 1)]), (2, idem_index[(1, 1)]),
        (2, idem_index[(2, 2)]), (4, idem_index[(4, 4)]), (6, idem_index[(8, 8)]),
    ]
    direct_matrix = [frozenset({ZERO}) if i == j else frozenset() for i in range(4) for j in range(4)]
    for g in direct:
        direct_matrix = matrix_mul(direct_matrix, gate_matrix(g, labels, idempotents))
    require(direct_matrix == target_matrix(targets), "five-call positive control failed full formal equality")

    # All eight signed address letters are one-entry rank-one updates over Q.
    native_updates = []
    for i, name in enumerate(label_names):
        entry = labels[i]
        nonzero = [(a, b, v) for (a, b), v in zip(POS, entry) if v]
        require(len(nonzero) == 1 and abs(nonzero[0][2]) == 1,
                f"{name}: address difference is not a single rational rank-one entry")
        native_updates.append({"letter": name, "nonzero_entry": [nonzero[0][0], nonzero[0][1], nonzero[0][2]],
                               "rank_over_Q": 1})

    # The finite support universe needed by every two-call product and T*C^{-1} query.
    elem_set = {ZERO, *labels, *targets}
    for g in labels:
        for h in labels:
            elem_set.add(group_mul(g, h))
    for t in targets:
        for h in labels:
            elem_set.add(group_mul(t, h))
    elements = sorted(elem_set)
    require(len(elements) < 255, "compact exact support ids overflow one byte")
    id_by_element = {g: i for i, g in enumerate(elements)}
    id_e = id_by_element[ZERO]
    lambda_masks = [(1 << id_e) ^ (1 << id_by_element[g]) for g in labels]
    lambda_products = []
    for g in labels:
        row = []
        for h in labels:
            gh = group_mul(g, h)
            row.append((1 << id_e) ^ (1 << id_by_element[g]) ^
                       (1 << id_by_element[h]) ^ (1 << id_by_element[gh]))
        lambda_products.append(row)

    gates = gate_pairs(labels, idempotents)
    gate_count = len(gates)
    require(gate_count == 960, "paid alphabet size changed")
    pair_map = {}
    pair_enumeration_hash = hashlib.sha256()
    for ai, a in enumerate(gates):
        for bi, b in enumerate(gates):
            masks = make_pair_product(a, b, idempotents, lambda_masks, lambda_products, id_e)
            key = encode_masks(masks, id_by_element)
            pair_enumeration_hash.update(ai.to_bytes(2, "big") + bi.to_bytes(2, "big") + key)
            if key not in pair_map:
                pair_map[key] = ai * gate_count + bi

    # Cross-check the pair formula/key on a tiny alphabet against brute full algebra.
    n1, n2 = idem_index[(1, 1)], idem_index[(2, 2)]
    tiny = [(0, n1), (2, n1), (0, n2), (2, n2)]
    tiny_target = [pos[0], pos[1], ZERO, ZERO]
    tiny_key = encode_masks(support_masks_for_matrix(target_matrix(tiny_target), id_by_element), id_by_element)
    tiny_join = False
    tiny_brute = False
    for a in tiny:
        for b in tiny:
            mk = make_pair_product(a, b, idempotents, lambda_masks, lambda_products, id_e)
            formula_key = encode_masks(mk, id_by_element)
            brute_matrix = matrix_mul(gate_matrix(a, labels, idempotents),
                                      gate_matrix(b, labels, idempotents))
            brute_key = encode_masks(support_masks_for_matrix(brute_matrix, id_by_element),
                                     id_by_element)
            require(formula_key == brute_key, "pair formula disagrees with full-algebra product")
            if encode_masks(mk, id_by_element) == tiny_key:
                tiny_join = True
            if brute_matrix == target_matrix(tiny_target):
                tiny_brute = True
    require(tiny_join and tiny_brute, "tiny positive pair-join control failed")

    # Query AB = T*C^{-1}; every C inverse is another one of the 960 legal gates.
    candidate = None
    hits = 0
    query_full_algebra_checks = 0
    query_scan_hash = hashlib.sha256()
    for ci, c in enumerate(gates):
        masks = target_times_inverse_masks(targets, c, labels, idempotents, id_by_element)
        li, ni = c
        inverse_gate = (li ^ 1, ni)
        query_matrix = matrix_mul(target_matrix(targets),
                                  gate_matrix(inverse_gate, labels, idempotents))
        require(masks == support_masks_for_matrix(query_matrix, id_by_element),
                "right-query formula disagrees with full-algebra product")
        query_full_algebra_checks += 1
        key = encode_masks(masks, id_by_element)
        query_scan_hash.update(ci.to_bytes(2, "big") + key)
        packed = pair_map.get(key)
        if packed is None:
            continue
        hits += 1
        ai, bi = divmod(packed, gate_count)
        witness = (gates[ai], gates[bi], c)
        product = matrix_mul(matrix_mul(gate_matrix(witness[0], labels, idempotents),
                                        gate_matrix(witness[1], labels, idempotents)),
                             gate_matrix(witness[2], labels, idempotents))
        require(product == target_matrix(targets), "meet-in-middle hit failed independent full-algebra replay")
        if candidate is None:
            candidate = witness

    # One call cannot have four distinct nonidentity address symbols in its support.
    one_call_hits = sum(gate_matrix(g, labels, idempotents) == target_matrix(targets) for g in gates)
    require(one_call_hits == 0, "one-call support control unexpectedly found the target")
    if candidate is None:
        minimum = 5  # odd parity; 1-call excluded; all 3-call words exhausted; direct word costs 5
        status = "PASS_UT5_FOUR_ROLE_NO_THREE_CALL"
    else:
        minimum = 3  # odd parity and one-call support obstruction
        status = "PASS_UT5_FOUR_ROLE_THREE_CALL_CONSTRUCTION"

    result = {
        "schema_version": 1,
        "status": status,
        "seed": "e2a8beab166c91810bbb606f6aca593f",
        "track": "bit-mechanisms",
        "task_id": "bit-new-register-model",
        "base_commit": "564148b82ae9df72163f22106f15e73efca8aff2",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "source_pins_checked": checked_sources,
        "model": {
            "address_group": "UT5(Z), full formal group algebra over F2",
            "address_dimension": 5,
            "scalar_registers": 4,
            "simple_roots": [f"g{i}=I+E_{{{i},{i+1}}}" for i in range(1, 5)],
            "signed_paid_letters": label_names,
            "rank_one_idempotents": len(idempotents),
            "paid_factor_alphabet_size": gate_count,
            "endpoint": ["g1*g2", "g2", "g3", "g4"],
            "all_roles_dirty": True,
            "native_address_differences_over_Q": native_updates,
        },
        "pricing": {
            "direct_calls": 5,
            "best_shorter_candidate_calls": 3,
            "saved_calls_if_found": 2,
            "relative_call_reduction_if_found": "2/5",
            "unpaid_setup_restoration_or_copy": 0,
            "supplier_or_kappa_claim": False,
        },
        "parity_obstruction": {
            "character": "sum of the four first-superdiagonal entries modulo 2",
            "each_signed_simple_root_maps_to": "z in C2",
            "each_paid_factor_determinant_after_character": "z",
            "target_determinant_after_character": "z",
            "conclusion": "every realization has odd call count; lengths 0,2,4 are excluded",
        },
        "search": {
            "ordered_length_three_words_covered": gate_count ** 3,
            "ordered_first_two_factors": gate_count ** 2,
            "right_factor_queries": gate_count,
            "unique_exact_pair_states": len(pair_map),
            "matching_right_queries": hits,
            "right_queries_checked_against_full_algebra": query_full_algebra_checks,
            "ordered_pair_transcript_sha256": pair_enumeration_hash.hexdigest(),
            "right_query_transcript_sha256": query_scan_hash.hexdigest(),
            "candidate_three_call_word": None if candidate is None else [
                {"letter": label_names[li], "x": idempotents[ni][0], "y": idempotents[ni][1]}
                for li, ni in candidate
            ],
            "one_call_hits": one_call_hits,
        },
        "controls": {
            "direct_five_call_full_formal_endpoint": "pass",
            "all_16_tiny_pair_formulas_match_full_algebra": "pass",
            "all_960_right_queries_match_full_algebra": query_full_algebra_checks,
            "all_120_projectors_are_idempotent_trace_one": "pass",
            "all_eight_address_letters_have_rank_one_Q_difference": "pass",
            "adjacent_simple_roots_do_not_commute": "pass",
            "one_call_negative_control_hits": one_call_hits,
        },
        "scope": "Exact minimum only for the stated four-role target in F2[UT5(Z)] with the eight signed simple-root letters and all binary rank-one idempotents. It does not establish a supplier transfer, conditional kappa change, or result for other targets or address alphabets.",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    result_path = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write"]:
        result_path.write_text(rendered)
    else:
        require(sys.argv[1:] == [], "usage: verify.py [--write]")
        require(result_path.read_text() == rendered, "RESULT.json differs from exact replay")
    print(status, "min_calls", minimum, "alphabet", gate_count,
          "pair_states", len(pair_map), "length3_hits", hits)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print("FAIL:", exc)
        raise SystemExit(1)

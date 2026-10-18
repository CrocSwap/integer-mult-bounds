#!/usr/bin/env python3
"""Independent exact checker for the two-shear historical complex center.

Standard library only; imports no repository implementation or certificate.
Prepared for Ross with substantial OpenAI Codex assistance. Apache-2.0.

The output map is checked with doubled target registers, avoiding fractions:
    (X, 2Y, C) -> (X, 2Y +/- (|S intersect T|-1) X, C).
All source, target and arbitrary dirty-center columns are independent symbols.
"""

import argparse
from itertools import combinations
import json
from math import comb


def need(condition, message):
    if not condition:
        raise ValueError(message)


def factors(h, original=False):
    need(type(h) is int and h >= 8 and h % 2 == 0, "invalid ground size")
    triples = tuple(combinations(range(h), 3))
    gather, scatter = [], []
    for triple in triples:
        membership = tuple(int(j in triple) for j in range(h))
        if original:
            v = (1,) + tuple(membership[j] - int(j in (1, 2)) for j in range(1, h))
            u = (sum(membership[:3]) - 1,) + tuple(
                membership[j] - membership[0] for j in range(1, h)
            )
        else:
            v = (1,) + membership[1:]
            u = (3 * membership[0] - 1,) + tuple(
                membership[j] - membership[0] for j in range(1, h)
            )
        gather.append(tuple((j, x) for j, x in enumerate(v) if x))
        scatter.append(u)
    return triples, tuple(gather), tuple(scatter)


def invoice(h):
    """Closed-form complete gather/scatter bill under the retained charges."""
    n, d, e = comb(h, 3), comb(h - 1, 2), comb(h - 2, 2)
    new_g = n + (h - 1) * d
    new_h = 2 * n - d + 4 * (h - 1) * e
    old_g = 3 * n + (h - 5) * d
    old_h = 2 * comb(h - 3, 3) + 6 * (h - 3) + 1 + 4 * (h - 1) * e
    saving = 2 * comb(h - 3, 3) - 3 * d + 6 * h - 17
    need(old_g + old_h - new_g - new_h == saving, "closed-form invoice mismatch")
    return {
        "triples": n,
        "old_gather": old_g,
        "old_scatter": old_h,
        "new_gather": new_g,
        "new_scatter": new_h,
        "old_total": old_g + old_h,
        "new_total": new_g + new_h,
        "saved_G_plus_H": saving,
        "saved_complete_scalar_charge": 6 * n * n * saving,
    }


def check_factor(h, triples, gather, scatter):
    n = comb(h, 3)
    need(triples == tuple(combinations(range(h), 3)), "wrong triple inventory")
    need(len(gather) == len(scatter) == n, "factor dimensions")
    for v in gather:
        need(len({j for j, _ in v}) == len(v), "duplicate gather coordinate")
        need(all(type(j) is int and 0 <= j < h and type(x) is int and x in (-1, 1)
                 for j, x in v), "gather charge alphabet")
    need(all(len(u) == h and all(type(x) is int and x in (-1, 0, 1, 2) for x in u)
             for u in scatter), "scatter charge alphabet")
    masks = tuple(sum(1 << j for j in triple) for triple in triples)
    for row_mask, u in zip(masks, scatter):
        for column_mask, v in zip(masks, gather):
            got = sum(u[j] * x for j, x in v)
            need(got == (row_mask & column_mask).bit_count() - 1,
                 "central product identity")
    return {
        "coefficients_checked": n * n,
        "gather": sum(len(v) for v in gather),
        "scatter": sum(1 if x == 2 else 2 for u in scatter for x in u if x),
    }


def add_scaled(target, source, coefficient):
    for column, value in source.items():
        value = target.get(column, 0) + coefficient * value
        if value:
            target[column] = value
        else:
            target.pop(column, None)


def check_dirty(h, triples, gather, scatter, inverse=False, omit_event=None):
    """Exact sparse symbolic replay; no random or numeric probe vectors.

    Process one target row at a time to avoid retaining a dense n-by-n map.
    Center snapshots are shared, but every target/source/dirty column is checked.
    """
    n = len(triples)
    centers = [{2 * n + j: 1} for j in range(h)]
    initial = [row.copy() for row in centers]
    operations = [("scatter", -1), ("gather", 1), ("scatter", 1), ("gather", -1)]
    if inverse:
        operations = [(tag, -sign) for tag, sign in reversed(operations)]
    scatters = []
    for event_index, (tag, sign) in enumerate(operations):
        if event_index == omit_event:
            continue
        if tag == "gather":
            for source, v in enumerate(gather):
                for j, weight in v:
                    add_scaled(centers[j], {source: 1}, sign * weight)
        else:
            scatters.append((sign, tuple(row.copy() for row in centers)))
    need(centers == initial, "arbitrary dirty centers not restored")
    masks = tuple(sum(1 << j for j in triple) for triple in triples)
    direction = -1 if inverse else 1
    for target, (mask, u) in enumerate(zip(masks, scatter)):
        row = {n + target: 2}
        for sign, state in scatters:
            for j, weight in enumerate(u):
                if weight:
                    add_scaled(row, state[j], sign * weight)
        expected = {n + target: 2}
        for source, source_mask in enumerate(masks):
            value = direction * ((mask & source_mask).bit_count() - 1)
            if value:
                expected[source] = value
        need(row == expected, "dirty central target map")
    return {"source_columns": n, "target_columns": n, "dirty_center_columns": h,
            "all_independent_columns": 2 * n + h, "inverse": inverse}


def check_shears(h, gather, scatter):
    """Derive the new factors by two commuting changes of basis, independently."""
    _, old_v, old_u = factors(h, original=True)
    transformed_v, transformed_u = [], []
    for sparse, old_row in zip(old_v, old_u):
        v = [0] * h
        for j, value in sparse:
            v[j] = value
        u = list(old_row)
        # V <- (I+E_i0)V, U <- U(I-E_i0).  No runtime gate is implied.
        for i in (1, 2):
            v[i] += v[0]
            u[0] -= u[i]
        transformed_v.append(tuple((j, value) for j, value in enumerate(v) if value))
        transformed_u.append(tuple(u))
    need(tuple(transformed_v) == gather, "two-shear gather mismatch")
    need(tuple(transformed_u) == scatter, "two-shear scatter mismatch")


def controls():
    triples, gather, scatter = factors(8)
    _, _, old_scatter = factors(8, original=True)
    cases = []

    def reject(name, expected_message, operation):
        try:
            operation()
        except ValueError as error:
            need(str(error) == expected_message, "control failed for wrong reason: " + name)
            cases.append(name)
        else:
            raise ValueError("control accepted: " + name)

    reject("missing_conjugate_scatter", "central product identity",
           lambda: check_factor(8, triples, gather, old_scatter))
    wrong_gather = list(gather)
    wrong_gather[0] = tuple((j, -x if j == 0 else x) for j, x in wrong_gather[0])
    reject("wrong_gather_sign", "central product identity",
           lambda: check_factor(8, triples, tuple(wrong_gather), scatter))
    wrong_scatter = list(scatter)
    wrong_scatter[0] = (3,) + wrong_scatter[0][1:]
    reject("unpriced_scatter_coefficient", "scatter charge alphabet",
           lambda: check_factor(8, triples, gather, tuple(wrong_scatter)))
    reject("missing_restoration_forward", "arbitrary dirty centers not restored",
           lambda: check_dirty(8, triples, gather, scatter, omit_event=3))
    reject("missing_restoration_inverse", "arbitrary dirty centers not restored",
           lambda: check_dirty(8, triples, gather, scatter, inverse=True, omit_event=2))
    reject("missing_dirty_compensation", "dirty central target map",
           lambda: check_dirty(8, triples, gather, scatter, omit_event=0))
    reject("missing_delivery", "dirty central target map",
           lambda: check_dirty(8, triples, gather, scatter, omit_event=2))
    reject("odd_ground_size", "invalid ground size", lambda: factors(9))
    return cases


def verify():
    result = {"method": "independent integer products and sparse symbolic dirty maps", "cases": []}
    for h in (8, 10, 26):
        triples, gather, scatter = factors(h)
        checked = check_factor(h, triples, gather, scatter)
        closed = invoice(h)
        need(checked["gather"] == closed["new_gather"], "gather invoice mismatch")
        need(checked["scatter"] == closed["new_scatter"], "scatter invoice mismatch")
        _, original_v, original_u = factors(h, original=True)
        need(sum(len(v) for v in original_v) == closed["old_gather"], "old gather invoice")
        need(sum(1 if x == 2 else 2 for u in original_u for x in u if x)
             == closed["old_scatter"], "old scatter invoice")
        check_shears(h, gather, scatter)
        symbolic = [check_dirty(h, triples, gather, scatter, inverse=inverse)
                    for inverse in (False, True)]
        result["cases"].append({"h": h, **checked, **closed, "symbolic": symbolic})
    result["negative_controls"] = controls()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = verify()
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        cases = receipt["cases"]
        print("PASS_INDEPENDENT_TWO_SHEAR sizes=" + ",".join(str(case["h"]) for case in cases)
              + " coefficients=" + str(sum(case["coefficients_checked"] for case in cases))
              + " dirty_columns=" + str(cases[-1]["symbolic"][0]["all_independent_columns"])
              + " directions=2 h26_G_plus_H=" + str(cases[-1]["new_total"])
              + " controls=" + str(len(receipt["negative_controls"])))

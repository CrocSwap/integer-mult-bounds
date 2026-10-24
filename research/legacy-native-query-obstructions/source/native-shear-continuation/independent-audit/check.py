"""Check the five-map family with direct group-algebra operations."""

from collections import Counter
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json
import struct
import time


HERE = Path(__file__).resolve().parent
I2 = (1, 0, 0, 1)
Z = (-1, 0, 0, -1)
ZERO = (0,) * 9
I3 = (1, 0, 0, 0, 1, 0, 0, 0, 1)
MAPS = {
    "R1": (-1, 0, 0, 1),
    "R2": (1, 0, 0, -1),
    "U": (2, -1, 1, 0),
    "V": (0, -1, 1, 2),
    "W": (1, 0, 4, 1),
}


def group_product(a, b):
    return (a[0] * b[0] + a[1] * b[2],
            a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2],
            a[2] * b[1] + a[3] * b[3])


def determinant(a):
    return a[0] * a[3] - a[1] * a[2]


def binary_product(a, b):
    return tuple(sum(a[3 * i + k] * b[3 * k + j]
                     for k in range(3)) % 2
                 for i in range(3) for j in range(3))


def binary_sum(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def rank(vectors):
    rows = [[vector[i] for vector in vectors] for i in range(3)]
    pivot_row = 0
    for column in range(len(vectors)):
        pivot = next((i for i in range(pivot_row, 3)
                      if rows[i][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for i in range(3):
            if i != pivot_row and rows[i][column]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == 3:
            break
    return pivot_row


def has_full_span_and_no_coloop(vectors):
    return rank(vectors) == 3 and all(
        rank(vectors[:i] + vectors[i + 1:]) == 3
        for i in range(len(vectors)))


def add_term(coefficients, address, value):
    if value == ZERO:
        return
    value = binary_sum(coefficients.get(address, ZERO), value)
    if value == ZERO:
        coefficients.pop(address, None)
    else:
        coefficients[address] = value


def replay(calls):
    coefficients = {I2: I3}
    for name, projector in calls:
        out = {}
        for address, value in coefficients.items():
            changed = binary_product(projector, value)
            add_term(out, address, binary_sum(value, changed))
            add_term(out, group_product(MAPS[name], address), changed)
        coefficients = out
    return coefficients


def subset_addresses(order):
    addresses = []
    for selection in product((False, True), repeat=len(order)):
        address = I2
        for name, selected in zip(order, selection):
            if selected:
                address = group_product(MAPS[name], address)
        addresses.append(address)
    return addresses


def mask(matrix):
    return sum(value << i for i, value in enumerate(matrix))


def main():
    start = time.monotonic()
    assert group_product(MAPS["R2"], MAPS["R1"]) == Z
    assert group_product(MAPS["W"], group_product(MAPS["V"], MAPS["U"])) == Z
    signs = {name: int(determinant(value) < 0) for name, value in MAPS.items()}
    assert signs == {"R1": 1, "R2": 1, "U": 0, "V": 0, "W": 0}
    assert all(value not in (I2, Z) for value in MAPS.values())

    vectors = [v for v in product((0, 1), repeat=3) if any(v)]
    pool = [(a, b, tuple(x * y for x in a for y in b))
            for a in vectors for b in vectors
            if sum(x * y for x, y in zip(a, b)) % 2]
    pool.sort(key=lambda item: tuple(sum(x << i for i, x in enumerate(v))
                                     for v in item[:2]))
    assert len(pool) == 28
    assert all(binary_product(n, n) == n for a, b, n in pool)
    e0 = (1, 0, 0)
    common = pool[0][2]
    triples = []
    for indices in product(range(len(pool)), repeat=3):
        selected = [pool[i] for i in indices]
        images = [e0, e0] + [p[0] for p in selected]
        covectors = [e0, e0] + [p[1] for p in selected]
        if (has_full_span_and_no_coloop(images)
                and has_full_span_and_no_coloop(covectors)):
            triples.append(indices)

    diagonal = [tuple(int(i == j == role) for i in range(3) for j in range(3))
                for role in range(3)]
    six_calls = [(name, diagonal[role])
                 for role in range(3) for name in ("R1", "R2")]
    assert replay(six_calls) == {Z: I3}
    omissions = []
    for omitted in range(6):
        role = omitted // 2
        remaining = "R2" if omitted % 2 == 0 else "R1"
        expected = {Z: binary_sum(I3, diagonal[role]),
                    MAPS[remaining]: diagonal[role]}
        actual = replay(six_calls[:omitted] + six_calls[omitted + 1:])
        assert actual == expected and actual != {Z: I3}
        omissions.append({"omitted": omitted, "role": role,
                          "remaining_map": remaining, "exact_expected_endpoint": True})
    assert replay([(name, diagonal[0]) for name in ("U", "V", "W")]) == {
        I2: binary_sum(I3, diagonal[0]), Z: diagonal[0]}
    assert replay([(name, diagonal[0]) for name in ("W", "V", "U")]) == {
        I2: binary_sum(I3, diagonal[0]), (-17, -4, -4, -1): diagonal[0]}

    digest = sha256()
    records = []
    hits = []
    best = None
    count = 0
    for order in permutations(MAPS):
        subsets = subset_addresses(order)
        addresses = sorted(set(subsets))
        target_count = subsets.count(Z)
        checked = 0
        if target_count >= 3:
            packing = struct.Struct("<" + "H" * len(addresses))
            for indices in triples:
                projectors = dict(zip(("U", "V", "W"),
                                      (pool[i][2] for i in indices)))
                projectors.update({"R1": common, "R2": common})
                coefficients = replay([(name, projectors[name]) for name in order])
                packed = [mask(coefficients.get(address, ZERO)) for address in addresses]
                digest.update(packing.pack(*packed))
                wrong = sum(sum(binary_sum(value, I3 if address == Z else ZERO))
                            for address, value in coefficients.items())
                if Z not in coefficients:
                    wrong += 3
                if best is None or wrong < best["wrong_binary_coefficients"]:
                    best = {"wrong_binary_coefficients": wrong,
                            "order": list(order), "positive_projector_indices": list(indices)}
                if coefficients == {Z: I3}:
                    hits.append({"order": list(order), "positive_projector_indices": list(indices)})
                checked += 1
                count += 1
        records.append({"order": list(order), "target_subsets": target_count,
                        "terminal_address_terms": len(addresses), "checked": checked})

    reference_path = HERE.parent / "RESULT.json"
    reference = json.loads(reference_path.read_text())
    original_log = json.loads((HERE.parent / "CHECK.log").read_text())
    comparisons = {
        "maps": reference["maps"] == {name: list(map(str, g)) for name, g in MAPS.items()},
        "pool": reference["projector_pool"] == [
            {"u": sum(x << i for i, x in enumerate(a)),
             "v": sum(x << i for i, x in enumerate(b)), "mask": mask(n)}
            for a, b, n in pool],
        "triples": reference["permitted_projector_triples"] == len(triples),
        "all_120_order_records": reference["orders"] == records,
        "checked_words": reference["checked_words"] == count,
        "hits": reference["hits"] == hits,
        "best_count": reference["best"]["wrong_binary_coefficients"] == best["wrong_binary_coefficients"],
        "best_order_and_projectors": (reference["best"]["order"] == best["order"]
                                      and reference["best"]["projectors"][2:] == best["positive_projector_indices"]),
        "original_check_log": all(reference[key] == value for key, value in original_log.items()),
        "terminal_coefficient_sha256": reference["terminal_coefficient_sha256"] == digest.hexdigest(),
        "source_hash": reference["script_sha256"] == sha256((HERE.parent / "search.py").read_bytes()).hexdigest(),
    }
    assert all(comparisons.values()), comparisons
    assert len(triples) == 492 and count == 9840 and not hits
    result = {
        "status": "INDEPENDENT_EXACT_REPLAY_MATCH",
        "method": "Direct dictionaries of exact integer group matrices and literal binary role matrices. No import of search.py.",
        "scope": "Each of R1, R2, U, V, W once; three complete roles; all orders and all normalized rank-one idempotents.",
        "sign_character": "det(g) < 0",
        "projectors": len(pool), "unfiltered_positive_triples": len(pool) ** 3,
        "permitted_positive_triples": len(triples), "orders": len(records),
        "target_subset_histogram": dict(sorted(Counter(r["target_subsets"] for r in records).items())),
        "eligible_orders": [r for r in records if r["checked"]],
        "checked_words": count, "hits": hits, "best": best,
        "terminal_coefficient_sha256": digest.hexdigest(), "reference_comparisons": comparisons,
        "controls": {"six_call_exact_endpoint": True, "six_single_call_omissions": omissions,
                     "noncommuting_forward_order": True, "noncommuting_reverse_order": True},
        "reference_result_sha256": sha256(reference_path.read_bytes()).hexdigest(),
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "elapsed_seconds": time.monotonic() - start,
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "status", "permitted_positive_triples", "target_subset_histogram", "checked_words",
        "hits", "terminal_coefficient_sha256", "reference_comparisons", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()

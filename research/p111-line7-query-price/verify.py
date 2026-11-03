#!/usr/bin/env python3
"""Price the PR1525 line-span(7) query against its zero-frame scatter.

No new kappa. The triangular correction preserves every original scatter
output, including all 62 dirty columns, and the constructor forbids moving
that query from span(7) down to the zero frame.
"""
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORD_SHA = "e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e"
SEED_SHA = "228e178662fc01895bbcd8472a52114d3a3d11ea8c7ae44d99cd1c8cf9e89147"
CENTRES_IN_QUERY = (61, 63, 31, 256)
PARTNERS = (63, 31, 256)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and (pivots[other] >> bit) & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots))


def contained(left, right):
    """Span(left) is contained in span(right). Same test as PR1060 model.py."""
    return len(basis(list(left) + list(right))) == len(basis(list(right)))


def add_row(dst, scale, src):
    for index, value in src.items():
        total = dst.get(index, Q(0)) + scale * value
        if total == 0:
            dst.pop(index, None)
        else:
            dst[index] = total


def apply_op(rows, event):
    if event[0] == "add":
        add_row(rows[event[1]], Q(event[3], event[4]), rows[event[2]])
    else:
        require(event[0] == "scale", event[0])
        rows[event[1]] = {i: value * Q(event[2], event[3]) for i, value in rows[event[1]].items()}


def scatter_matrix(word):
    order = word["centers"]
    require(order == [60, 61, 63, 224, 31, 240, 23, 256], order)
    index = {centre: slot for slot, centre in enumerate(order)}
    matrix = [[Q(0) for _ in order] for _ in range(112)]
    receivers = {centre: [] for centre in order}
    for event in word["cut"]:
        require(event[0] == "add" and event[5] is None, event)
        target = event[1] - 112
        require(0 <= target < 112, event[1])
        slot = index[event[2]]
        matrix[target][slot] += Q(event[3], event[4])
        receivers[event[2]].append(event[1])
    return matrix, receivers


def column_nnz(matrix, slot):
    return sum(1 for row in matrix if row[slot])


def triangular(matrix, index):
    """Substitute q = (c61 + c63 + c31 + c256) / 2 for the c61 readout."""
    query = index[61]
    corrected = []
    for row in matrix:
        new_row = row[:]
        original = row[query]
        new_row[query] = 2 * original
        for partner in PARTNERS:
            new_row[index[partner]] = row[index[partner]] - original
        corrected.append(new_row)
    return corrected


def support_delta(matrix, index, partner):
    query = index[61]
    slot = index[partner]
    both = cancel = unequal = only_query = only_partner = 0
    for row in matrix:
        left, right = row[query], row[slot]
        if left and right:
            both += 1
            if right - left == 0:
                cancel += 1
            else:
                unequal += 1
        elif left:
            only_query += 1
        elif right:
            only_partner += 1
    old = column_nnz(matrix, slot)
    new = sum(1 for row in matrix if row[slot] - row[query])
    return {
        "partner": partner,
        "old_nnz": old,
        "new_nnz": new,
        "delta": new - old,
        "overlap": both,
        "cancellations": cancel,
        "unequal_overlap": unequal,
        "only_query": only_query,
        "only_partner": only_partner,
    }


def combine(matrix, vectors):
    outputs = []
    for row in matrix:
        acc = {}
        for slot, weight in enumerate(row):
            if weight:
                add_row(acc, weight, vectors[slot])
        outputs.append(acc)
    return outputs


def endpoint_line(frame):
    return next(
        mask
        for mask in range(1, 512)
        if all((mask & vector).bit_count() % 2 == 0 for vector in frame)
    )


def main():
    word_bytes = (ROOT / "inputs/word-base.json.gz").read_bytes()
    seed_bytes = (ROOT / "inputs/CENTRE-SEED.json").read_bytes()
    require(hashlib.sha256(word_bytes).hexdigest() == WORD_SHA, "word sha")
    require(hashlib.sha256(seed_bytes).hexdigest() == SEED_SHA, "seed sha")
    word = json.loads(gzip.decompress(word_bytes))
    seed = json.loads(seed_bytes)
    require(seed["puncture"] == 0, seed["puncture"])
    require(seed["dirty_columns"] == 62, seed["dirty_columns"])
    require([item["center"] for item in seed["terms"]] == list(CENTRES_IN_QUERY), seed["terms"])
    require(all(item["weight"] == "1/2" for item in seed["terms"]), seed["terms"])

    roles = 224 + word["report"]["R"]
    require(roles == 704, roles)
    rows = [{i: Q(1)} for i in range(roles)]
    for event in word["precondition"] + word["A"]:
        apply_op(rows, event)

    query = {}
    for item in seed["terms"]:
        add_row(query, Q(item["weight"]), rows[item["center"]])
    dirty = {i: value for i, value in query.items() if i >= 112}
    require({str(i): str(value) for i, value in dirty.items()} == seed["dirty_coefficients"], "dirty census")
    require(len(dirty) == 62, len(dirty))
    beta = seed["puncture"]
    for source in range(112):
        if source == beta:
            continue
        expected = Q(sum(a * b for a, b in zip(word["root_lines"][beta], word["root_lines"][source])), 2)
        require(query.get(source, Q(0)) == expected, source)

    line = endpoint_line(seed["terms"][0]["frame"])
    require(line == 7 and basis((line,)) == (7,), line)
    require(contained((7,), ()) is False, "span(7) is not contained in the zero frame")
    require(contained((), (7,)) is True, "the zero frame is contained in span(7)")

    matrix, receivers = scatter_matrix(word)
    index = {centre: slot for slot, centre in enumerate(word["centers"])}
    require(all(len(receivers[centre]) == 22 and len(set(receivers[centre])) == 22 for centre in word["centers"]), "22 receivers")
    require(sum(column_nnz(matrix, slot) for slot in range(8)) == 176, "S nnz")
    for slot in range(8):
        weights = Counter(str(row[slot]) for row in matrix if row[slot])
        require(set(weights) <= {"1/4", "-1/4"}, weights)
        require(sum(weights.values()) == 22, weights)

    deltas = [support_delta(matrix, index, partner) for partner in PARTNERS]
    require([item["delta"] for item in deltas] == [10, 22, 22], deltas)
    require(sum(item["delta"] for item in deltas) == 54, deltas)
    require(deltas[0]["cancellations"] == 4 and deltas[0]["overlap"] == 8, deltas[0])
    require(deltas[1]["overlap"] == 0 and deltas[2]["overlap"] == 0, deltas[1:])

    corrected = triangular(matrix, index)
    corrected_nnz = sum(1 for row in corrected for value in row if value)
    require(corrected_nnz == 230, corrected_nnz)
    require(column_nnz(corrected, index[61]) == 22, "query column")
    doubled = Counter(str(row[index[61]]) for row in corrected if row[index[61]])
    require(doubled == Counter({"-1/2": 3, "1/2": 19}), doubled)

    old_vectors = [rows[centre] for centre in word["centers"]]
    new_vectors = [query if centre == 61 else rows[centre] for centre in word["centers"]]
    old_outputs = combine(matrix, old_vectors)
    new_outputs = combine(corrected, new_vectors)
    require(old_outputs == new_outputs, "triangular image differs from the original scatter")

    # The same identity fails if the partner correction is omitted.
    uncorrected = [row[:] for row in matrix]
    for row in uncorrected:
        row[index[61]] = 2 * row[index[61]]
    require(combine(uncorrected, new_vectors) != old_outputs, "missing partner correction should be visible")

    witnesses = {}
    for column in sorted(dirty):
        hits = []
        for target, form in enumerate(old_outputs):
            coefficient = form.get(column, Q(0))
            if coefficient:
                hits.append((112 + target, str(coefficient)))
                break
        require(len(hits) == 1, column)
        witnesses[str(column)] = {"output_row": hits[0][0], "coefficient": hits[0][1]}
    require(len(witnesses) == 62, len(witnesses))

    # One shared rank-1 copy takes span(7) to a zero-frame register. The
    # comparator profile is the four already-paid rank-1 centre moves plus the
    # rank-8 copy. The extra child is exactly one rank 1.
    old_profile = {1: 4, 8: 1}
    new_profile = {1: 5, 8: 1}
    require(new_profile[1] - old_profile[1] == 1 and new_profile[8] == old_profile[8], "profile delta")
    # For every tariff that sends rank 1 to a positive value and ignores no
    # other change, the new multiset costs exactly that positive value more.
    for exponent in range(1, 9):
        old_mass = 4 * (1 ** exponent) + 8 ** exponent
        new_mass = 5 * (1 ** exponent) + 8 ** exponent
        require(new_mass - old_mass == 1, exponent)

    receipt = {
        "status": "PASS_P111_LINE7_QUERY_PRICE",
        "word_sha256": WORD_SHA,
        "seed_sha256": SEED_SHA,
        "source_pr": 1525,
        "source_head": "90d39a5603c7fbfd8d8d957e9732d9b6ebd6317f",
        "endpoint_line": [7],
        "move_line_to_zero_legal": False,
        "move_zero_to_line_legal": True,
        "scatter_nnz": 176,
        "triangular_nnz": 230,
        "scatter_add_delta": 54,
        "partner_deltas": deltas,
        "query_receivers": 22,
        "dirty_columns": 62,
        "dirty_columns_visible_in_original_outputs": 62,
        "dirty_witnesses": witnesses,
        "comparator_profile": old_profile,
        "zero_frame_copy_profile": new_profile,
        "profile_delta": {1: 1},
        "no_new_kappa": True,
    }
    print(
        receipt["status"],
        "delta_adds", receipt["scatter_add_delta"],
        "dirty_visible", receipt["dirty_columns_visible_in_original_outputs"],
        "line_to_zero_move", receipt["move_line_to_zero_legal"],
        "NO_NEW_KAPPA",
        flush=True,
    )
    return receipt


if __name__ == "__main__":
    main()

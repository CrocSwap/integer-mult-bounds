"""Exact F2 replay and fully charged local budget for one clean connector."""

from collections import Counter
import json
from pathlib import Path

L = 16
MASKS = tuple(range(1, 1 << 5))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def permute(word, row_to_input):
    out = 0
    for row, col in enumerate(row_to_input):
        out |= ((word >> col) & 1) << row
    return out


def apply_a(word):
    out = 0
    for row in range(L):
        bit = 0
        for shift in range(13):
            bit ^= (word >> ((row + shift) % L)) & 1
        out |= bit << row
    return out


def gf2_rank(rows, width):
    pivots = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def a_rows():
    return [sum(1 << ((row + shift) % L) for shift in range(13)) for row in range(L)]


def make_maps():
    b_maps = [tuple((i + shift) % L for i in range(L)) for shift in range(5)]
    affine = [(a, b) for a in range(1, L, 2) for b in range(L)][:31]
    q_maps = [tuple((a * i + b) % L for i in range(L)) for a, b in affine]
    return b_maps, q_maps


B_MAPS, Q_MAPS = make_maps()

EXPECTED_INVOICE = {
    "shared_map_table_bits": 26112,
    "shared_row_cells": 592,
    "source_updates": 2560,
    "output_updates": 6448,
    "action_descriptors": 2483,
    "mask_control_descriptors": 403,
    "allocation_release_descriptors": 26,
    "fresh_row_cells": 16,
    "zero_writes": 16,
}


def invoice_valid(invoice):
    return invoice == EXPECTED_INVOICE


def apply_output_map(word, output_index):
    return apply_a(permute(word, Q_MAPS[output_index]))


def expected_deltas(sources):
    deltas = []
    for mask in MASKS:
        total = 0
        for j in range(5):
            if (mask >> j) & 1:
                total ^= permute(sources[j], B_MAPS[j])
        deltas.append(apply_output_map(total, mask - 1))
    return deltas


def execute(sources, dirty_connector, targets, fresh_connector, fault=None):
    """Execute the candidate; fault values are verifier negative controls."""
    connector = fresh_connector
    if fault != "omit-zeroing":
        connector = 0
    out = list(targets)
    for mask in MASKS:
        selected = [j for j in range(5) if (mask >> j) & 1]
        for j in selected:
            if fault == "omit-first-source" and mask == 1 and j == 0:
                continue
            connector ^= permute(sources[j], B_MAPS[j])
        target_index = mask - 1
        if fault == "wrong-target" and mask == 1:
            target_index = 1
        out[target_index] ^= apply_output_map(connector, mask - 1)
        if fault != "omit-reverse":
            for j in reversed(selected):
                connector ^= permute(sources[j], B_MAPS[j])
    return list(sources), dirty_connector, out, connector


def verify_basis():
    checked = 0
    # 80 source bits, 16 original-connector bits, 496 target bits, 16
    # arbitrary pre-allocation scratch bits (cleared by the paid zeroing pass).
    for column in range(38 * L):
        sources = [0] * 5
        dirty_connector = 0
        targets = [0] * 31
        fresh_connector = 0
        if column < 5 * L:
            row, bit = divmod(column, L)
            sources[row] = 1 << bit
        elif column < 6 * L:
            dirty_connector = 1 << (column - 5 * L)
        elif column < 37 * L:
            row, bit = divmod(column - 6 * L, L)
            targets[row] = 1 << bit
        else:
            fresh_connector = 1 << (column - 37 * L)
        result = execute(sources, dirty_connector, targets, fresh_connector)
        expected = [targets[i] ^ d for i, d in enumerate(expected_deltas(sources))]
        require(result[0] == sources, "source row changed on basis column %d" % column)
        require(result[1] == dirty_connector, "original dirty connector changed on basis column %d" % column)
        require(result[2] == expected, "target delta mismatch on basis column %d" % column)
        require(result[3] == 0, "fresh connector not restored on basis column %d" % column)
        checked += 1
    return checked


def mixed_word(seed):
    state = seed & 0xFFFFFFFF

    def next_word():
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return (state ^ (state >> 13)) & 0xFFFF

    sources = [next_word() for _ in range(5)]
    dirty_connector = next_word()
    targets = [next_word() for _ in MASKS]
    fresh_connector = next_word()
    return sources, dirty_connector, targets, fresh_connector


def valid_result(inputs, result):
    sources, dirty_connector, targets, _fresh = inputs
    expected = [targets[i] ^ d for i, d in enumerate(expected_deltas(sources))]
    return result == (sources, dirty_connector, expected, 0)


def verify_controls():
    inputs = mixed_word(0xC1EA_5EED)
    clean_inputs = (inputs[0], inputs[1], inputs[2], 0)
    positive = execute(*clean_inputs)
    require(valid_result(clean_inputs, positive), "mixed-state positive fixture failed")
    controls = [
        execute(*inputs, fault="omit-zeroing"),
        execute(*clean_inputs, fault="omit-reverse"),
        execute(*clean_inputs, fault="omit-first-source"),
        execute(*clean_inputs, fault="wrong-target"),
    ]
    require(all(not valid_result(inputs if i == 0 else clean_inputs, result)
                for i, result in enumerate(controls)), "a mutation control escaped")
    return len(controls)


def direct_schedule_counts():
    root = Path(__file__).resolve().parents[2]
    certificate = json.loads(
        (root / "research/universal-connector-boundary/CERTIFICATE.json").read_text()
    )
    word = certificate["schedules"]["five_extra_output"]["word"]
    counts = Counter(op for op, _index in word)
    outputs = Counter(index for op, index in word if op == "A")
    require(counts == Counter({"A": 64, "B": 10}), "pinned direct schedule call counts changed")
    require(outputs == Counter({i: (4 if i == 20 else 2) for i in range(31)}),
            "pinned direct schedule no longer has its single four-read output")
    return counts["B"], counts["A"]


def budget(direct_b, direct_a, candidate_b, candidate_a):
    a, b, d = 208, 16, 13
    map_table_bits = 31 * L * 13 * 4 + 5 * L * 4
    common_row_cells = 37 * L  # 5 sources, 1 original connector, 31 targets.
    common = map_table_bits + common_row_cells
    direct = common + direct_b * (b + d) + direct_a * (a + d)
    invoice = {
        "shared_map_table_bits": map_table_bits,
        "shared_row_cells": common_row_cells,
        "source_updates": candidate_b * b,
        "output_updates": candidate_a * a,
        "action_descriptors": (candidate_b + candidate_a) * d,
        "mask_control_descriptors": 31 * d,
        "allocation_release_descriptors": 2 * d,
        "fresh_row_cells": L,
        "zero_writes": L,
    }
    require(invoice_valid(invoice), "a candidate invoice line changed: %r" % invoice)
    candidate = sum(invoice.values())
    return common, direct, candidate, direct - candidate, invoice


def verify_bill_and_fixture():
    rows = a_rows()
    require(gf2_rank(rows, L) == L, "13-term cyclic convolution is not invertible")
    require(all(len(set(p)) == L for p in B_MAPS + Q_MAPS), "a fixture map is not a permutation")
    signatures = [tuple(apply_output_map(1 << i, q) for i in range(L)) for q in range(31)]
    require(len(set(signatures)) == 31, "output maps are not pairwise distinct")
    for q_map in Q_MAPS:
        for row in range(L):
            indices = [q_map[(row + shift) % L] for shift in range(13)]
            require(len(set(indices)) == 13, "an output-map row does not have 13 taps")
    direct_b, direct_a = direct_schedule_counts()
    candidate_b = 2 * sum(mask.bit_count() for mask in MASKS)
    candidate_a = len(MASKS)
    require((candidate_b, candidate_a) == (160, 31), "candidate action count changed")
    common, direct, candidate, saving, invoice = budget(direct_b, direct_a, candidate_b, candidate_a)
    require((common, direct, candidate, saving) == (26704, 41138, 38656, 2482),
            "complete bill changed: %r" % ((common, direct, candidate, saving),))
    require(33 * 208 - 150 * 16 - 150 * 13 - 2 * L == saving,
            "symbolic break-even difference mismatch")
    controls = 0
    for key in invoice:
        undercharged = dict(invoice)
        undercharged[key] = 0
        require(undercharged != invoice, "undercharge mutation did not change invoice")
        require(not invoice_valid(undercharged), "undercharge mutation escaped: " + key)
        controls += 1
    return common, direct, candidate, saving, controls


def main():
    basis = verify_basis()
    controls = verify_controls()
    common, direct, candidate, saving, invoice_controls = verify_bill_and_fixture()
    print("PASS_CLEAN_CONNECTOR_PER_MASK basis_columns=%d controls=%d masks=31 candidate_B=160 candidate_A=31 direct_B=10 direct_A=64 common=%d direct_cost=%d candidate_cost=%d saving=%d" %
          (basis, controls + invoice_controls, common, direct, candidate, saving))


if __name__ == "__main__":
    main()

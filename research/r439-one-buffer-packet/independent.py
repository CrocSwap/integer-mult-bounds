#!/usr/bin/env python3
"""Independent finite witness for the conditional one-buffer identity.

No predecessor or package verifier is imported. All three packets occupy
disjoint interleaved positions of ONE family; two additional cells are guards.
Integer masks are formal F2 linear expressions, not sampled payload values.
Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
"""

from collections import Counter
from itertools import permutations, product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(p):
    q = [0] * len(p)
    for old, new in enumerate(p):
        q[new] = old
    return tuple(q)


def route_in_place(bank, p):
    """Push old position k to p[k], using XOR swaps and no payload vector.

    Cycle traversal and its indices are control storage, excluded from the
    payload-bank assertion. This small interpreter is not a tape compiler.
    """
    require(sorted(p) == list(range(len(bank))), "route is not bijective")
    for anchor in range(len(bank)):
        cursor = p[anchor]
        while cursor > anchor:
            cursor = p[cursor]
        if cursor != anchor:
            continue
        cursor = p[anchor]
        while cursor != anchor:
            bank[anchor] ^= bank[cursor]
            bank[cursor] ^= bank[anchor]
            bank[anchor] ^= bank[cursor]
            cursor = p[cursor]


EVENTS = ((0, 1), (2, 3), (1, 0), (0, 3), (2, 1), (1, 2))


def exercise(charts, fault=None):
    p = len(charts[0])
    n = 3 * p + 2
    owned = tuple(tuple(range(1 + r, n - 1, 3)) for r in range(3))
    family = [1 << k for k in range(n)]
    snapshot = [1 << (n + k) for k in range(p)]
    bank = [1 << (n + p + k) for k in range(p)]
    original = tuple(family), tuple(snapshot), tuple(bank)
    expected = list(family)
    inv = tuple(inverse(a) for a in charts)
    meter = Counter()
    layout = "idle"

    def exchange(role, broken=False):
        # The physical family is traversed once forward, then both heads
        # return. All three elementary XORs are local at each selected pair.
        position_to_offset = {position: k for k, position in enumerate(owned[role])}
        for position in range(n):
            if position not in position_to_offset:
                continue
            k = position_to_offset[position]
            if broken:
                bank[k] ^= family[position]
            else:
                family[position] ^= bank[k]
                bank[k] ^= family[position]
                family[position] ^= bank[k]
        meter["exchanges"] += 1
        meter["xor_packet_units"] += 3
        meter["outer_head_steps"] += 2 * n + 2 * p

    def route(role, backward=False):
        nonlocal layout
        require(layout == ("common" if backward else role), "route prefix layout")
        parked = tuple(family), tuple(snapshot)
        route_in_place(bank, inv[role] if backward else charts[role])
        require(parked == (tuple(family), tuple(snapshot)), "route touched parked values")
        layout = role if backward else "common"
        meter["routes"] += 1

    def event(target, source, ordinal):
        nonlocal layout
        # Independent coordinate oracle: output at owner index k reads the
        # source at inv(source_chart)[target_chart[k]]. No packet routing.
        before = list(expected)
        for k, position in enumerate(owned[target]):
            increment = (snapshot[charts[target][k]] if source == 3 else
                         before[owned[source][inv[source][charts[target][k]]]])
            expected[position] ^= increment

        if source == 3:
            exchange(target)
            layout = target
            route(target)
            dirt = bank[0]
            if fault == "transient_snapshot_borrow" and ordinal == 1:
                snapshot[0] ^= dirt
            for k in range(p):
                bank[k] ^= snapshot[k]
            if fault == "transient_snapshot_borrow" and ordinal == 1:
                snapshot[0] ^= dirt
            meter["outer_head_steps"] += 4 * p
            route(target, backward=True)
            exchange(target)
        else:
            exchange(source, fault == "dirty_copy" and ordinal == 0)
            layout = source
            if fault == "reverse_relative_order" and ordinal == 0:
                # Deliberately ignore the invalid intermediate layout, so the
                # semantic coordinate oracle must detect noncommutativity.
                route_in_place(bank, inv[target])
                route_in_place(bank, charts[source])
                meter["routes"] += 2
                layout = target
            else:
                route(source)
                route(target, backward=True)
            for k, position in enumerate(owned[target]):
                family[position] ^= bank[k]
            if fault == "unowned_write" and ordinal == 0:
                family[0] ^= bank[0]
            meter["outer_head_steps"] += 2 * n + 2 * p
            if fault == "reverse_return_order" and ordinal == 0:
                route_in_place(bank, inv[source])
                route_in_place(bank, charts[target])
                meter["routes"] += 2
                layout = source
            else:
                route(target)
                route(source, backward=True)
            if not (fault == "omit_exchange_back" and ordinal == 0):
                exchange(source)
        layout = "idle"
        meter["xor_packet_units"] += 1
        meter["event_boundaries"] += 1
        require(tuple(snapshot) == original[1], "snapshot boundary")
        require(tuple(bank) == original[2], "dirty-bank boundary")
        require(family == expected, "all-family coordinate oracle")

    for ordinal, (target, source) in enumerate(EVENTS + tuple(reversed(EVENTS))):
        event(target, source, ordinal)
    require(tuple(family) == original[0], "forward/inverse family restoration")
    require(meter == Counter(routes=40, exchanges=24, xor_packet_units=84,
                             outer_head_steps=64 * n + 80 * p, event_boundaries=12),
            "independent tariff")
    return dict(meter)


def chronological_endpoint(charts, events):
    p = len(charts[0])
    values = [[1 << (r * p + k) for k in range(p)] for r in range(4)]
    inv = tuple(inverse(a) for a in charts)
    for target, source in events:
        for k in range(p):
            values[target][k] ^= (values[3][charts[target][k]] if source == 3 else
                                  values[source][inv[source][charts[target][k]]])
    return values


def main():
    charts = tuple(permutations(range(3)))
    checked = 0
    for triple in product(charts, repeat=3):
        meter = exercise(triple)
        checked += 1

    witness = ((1, 2, 0), (1, 0, 2), (2, 0, 1))
    expected_failures = {
        "dirty_copy": "dirty-bank boundary",
        "reverse_relative_order": "all-family coordinate oracle",
        "reverse_return_order": "all-family coordinate oracle",
        "omit_exchange_back": "dirty-bank boundary",
        "unowned_write": "all-family coordinate oracle",
        "transient_snapshot_borrow": "all-family coordinate oracle",
    }
    rejected = {}
    for fault, reason in expected_failures.items():
        try:
            exercise(witness, fault)
        except ValueError as error:
            require(str(error) == reason, "fault failed for wrong reason: " + fault + ": " + str(error))
            rejected[fault] = str(error)
        else:
            raise ValueError("ineffective fault: " + fault)

    moved = (EVENTS[3],) + EVENTS[:3] + EVENTS[4:]
    require(Counter(moved) == Counter(EVENTS), "tap-cut inventory")
    require(chronological_endpoint(witness, moved) != chronological_endpoint(witness, EVENTS),
            "ineffective chronological-cut fault")
    rejected["wrong_tap_cut_same_inventory"] = "distinct coordinate endpoint"
    result = {
        "status": "PASS_INDEPENDENT_ONE_BUFFER_PACKET",
        "packet_records": 3,
        "same_family_records": 11,
        "formal_input_records_per_chart_triple": 17,
        "all_S3_chart_triples": checked,
        "checked_event_boundaries": checked * meter["event_boundaries"],
        "per_triple_meter": meter,
        "rejected_controls": rejected,
        "source_window_replayed": False,
        "scope": "finite exact generic identity witness; written proof needed for all sizes; no tape/compiler/supplier claim",
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

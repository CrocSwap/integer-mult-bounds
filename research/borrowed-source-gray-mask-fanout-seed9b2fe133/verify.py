#!/usr/bin/env python3
"""Exact dirty-boundary replay for the borrowed-source Gray-mask circuit."""
import json
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))


def candidate_schedule():
    ops = [(1, 0)]                         # A <- A+B
    ops += [(0, 3 + i) for i in range(3)] # X_i <- X_i+A
    ops += [(2, 0)]                         # A <- A+B+C
    ops += [(0, 6 + i) for i in range(3)] # Y_i <- Y_i+A
    ops += [(1, 0)]                         # A <- A+C
    ops += [(0, 9 + i) for i in range(3)] # Z_i <- Z_i+A
    ops += [(2, 0)]                         # restore A
    return ops


def direct_schedule():
    ops = []
    for destination_start, sources in (
        (3, (0, 1)),
        (6, (0, 1, 2)),
        (9, (0, 2)),
    ):
        for i in range(3):
            ops.extend((source, destination_start + i) for source in sources)
    return ops


def apply(values, ops):
    out = list(values)
    for source, destination in ops:
        out[destination] ^= out[source]
    return tuple(out)


def transfer_rows(ops):
    rows = [1 << i for i in range(12)]
    for source, destination in ops:
        rows[destination] ^= rows[source]
    return tuple(rows)


def expected_rows():
    rows = [1 << i for i in range(12)]
    for i in range(3):
        rows[3 + i] ^= rows[0] ^ rows[1]
        rows[6 + i] ^= rows[0] ^ rows[1] ^ rows[2]
        rows[9 + i] ^= rows[0] ^ rows[2]
    return tuple(rows)


def expected_state(values):
    a, b, c = values[:3]
    out = list(values)
    for i in range(3):
        out[3 + i] ^= a ^ b
        out[6 + i] ^= a ^ b ^ c
        out[9 + i] ^= a ^ c
    return tuple(out)


def tour_length(order):
    state = 0
    length = 0
    for next_state in order:
        length += (state ^ next_state).bit_count()
        state = next_state
    length += state.bit_count()
    return length


def control_fails(ops):
    return transfer_rows(ops) != expected_rows()


def main():
    candidate = candidate_schedule()
    direct = direct_schedule()
    target = expected_rows()

    assert len(candidate) == 13
    assert len(direct) == 21
    assert transfer_rows(candidate) == target
    assert transfer_rows(direct) == target

    # The anchor walks through the three required nonempty masks in Gray order.
    masks = (1, 3, 2)
    tour_costs = [tour_length(order) for order in permutations(masks)]
    assert min(tour_costs) == 4
    assert tour_length(masks) == 4

    # Exhaust every arbitrary dirty one-bit input to all 12 rows.
    for word in range(1 << 12):
        initial = tuple((word >> i) & 1 for i in range(12))
        got = apply(initial, candidate)
        assert got == expected_state(initial)
        assert apply(got, reversed(candidate)) == initial
        assert apply(initial, direct) == got

    # Failure controls: source leakage, wrong parity transition, missing fanout,
    # and an incorrect restoration source.
    controls = []
    controls.append(candidate[:-1])
    controls.append(candidate[:4] + candidate[5:])
    controls.append(candidate[:10] + candidate[11:])
    controls.append(candidate[:-1] + [(1, 0)])
    assert all(control_fails(control) for control in controls)

    assert len(controls) == EXPECTED["negative_controls"]
    assert len(candidate) == EXPECTED["borrowed_adds"]
    assert len(direct) == EXPECTED["direct_adds"]
    assert EXPECTED["direct_adds"] - EXPECTED["borrowed_adds"] == EXPECTED["saving_adds"]
    assert EXPECTED["anchor_transition_adds"] + EXPECTED["target_write_adds"] == len(candidate)
    assert (1 << 12) == EXPECTED["scalar_boundary_states"]

    print(
        "PASS_GRAY_MASK_FANOUT width=1 source_rows=3 target_classes=3 targets_per_class=3 "
        "direct_adds=21 borrowed_adds=13 transitions=4 target_writes=9 saving=8 "
        "scalar_states=4096 min_tour=4 controls=4"
    )


if __name__ == "__main__":
    main()

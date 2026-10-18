#!/usr/bin/env python3
"""Exact dirty-state check for a shared linear readout with one residual."""

from __future__ import annotations

import json


# Rows are bit masks in output-coordinate order.  C is invertible, D has rank
# one, and A1=C+D is also invertible.
C = (0b11, 0b01)
D = (0b01, 0b00)
A1 = tuple(c ^ d for c, d in zip(C, D))
IDENTITY = (0b01, 0b10)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def matvec(rows: tuple[int, ...], vector: int) -> int:
    answer = 0
    for i, row in enumerate(rows):
        if (row & vector).bit_count() & 1:
            answer |= 1 << i
    return answer


def rank_f2(rows: tuple[int, ...]) -> int:
    pivots: dict[int, int] = {}
    for row in rows:
        value = row
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def separate_schedule(x: int, z: int, y0: int, y1: int, scratch: int):
    """At q=0 and q=1, evaluate C for y0 and C+D for y1."""
    current_z = z
    current_y0, current_y1 = y0, y1
    for _boundary in range(2):
        current_y0 ^= matvec(C, current_z)
        current_y1 ^= matvec(A1, current_z)
        current_z ^= matvec(IDENTITY, x)  # one B0 toggle; the second restores z
    return x, current_z, current_y0, current_y1, scratch


def broadcast_schedule(x: int, z: int, y0: int, y1: int, scratch: int):
    """Broadcast C at each prefix, then apply the ordinary D correction to y1."""
    current_z = z
    current_y0, current_y1 = y0, y1
    for _boundary in range(2):
        common = matvec(C, current_z)
        current_y0 ^= common
        current_y1 ^= common
        current_y1 ^= matvec(D, current_z)
        current_z ^= matvec(IDENTITY, x)
    return x, current_z, current_y0, current_y1, scratch


def controls() -> dict[str, bool]:
    # Each control must have a concrete dirty state on which it fails.
    x, z, y0, y1, scratch = 1, 2, 0, 0, 3

    # Missing the residual loses D*x on target 1.
    no_residual = y1
    for connector in (z, z ^ x):
        no_residual ^= matvec(C, connector)
    residual_rejected = no_residual != y1 ^ matvec(A1, x)

    # Omitting the second broadcast destination loses C*x on target 1.
    no_second_destination = y1
    connector = z
    for _ in range(2):
        no_second_destination ^= matvec(D, connector)
        connector ^= x
    destination_rejected = no_second_destination != y1 ^ matvec(A1, x)

    # A single prefix read leaves dirty-connector dependence in the output.
    one_boundary = y0 ^ matvec(C, z)
    one_boundary_rejected = one_boundary != y0 ^ matvec(C, x)

    # Omitting the final B0 toggle leaves the connector changed by x.
    missing_restore_rejected = (z ^ x) != z

    result = {
        "negative_missing_rank_one_residual": residual_rejected,
        "negative_missing_second_broadcast_target": destination_rejected,
        "negative_single_prefix_read": one_boundary_rejected,
        "negative_missing_source_restore": missing_restore_rejected,
        "positive_residual_is_nonzero_on_control_input": matvec(D, x) != 0,
    }
    need(all(result.values()), "a targeted negative control failed")
    return result


def main() -> None:
    need(rank_f2(C) == 2, "common map C is not full rank")
    need(rank_f2(D) == 1, "residual D is not rank one")
    need(rank_f2(A1) == 2, "changed output map C+D is not full rank")

    states = 0
    for x in range(4):
        for z in range(4):
            for y0 in range(4):
                for y1 in range(4):
                    for scratch in range(4):
                        base = separate_schedule(x, z, y0, y1, scratch)
                        candidate = broadcast_schedule(x, z, y0, y1, scratch)
                        expected = (
                            x,
                            z,
                            y0 ^ matvec(C, x),
                            y1 ^ matvec(A1, x),
                            scratch,
                        )
                        need(base == expected,
                             f"separate dirty schedule failed at {(x, z, y0, y1, scratch)}")
                        need(candidate == expected,
                             f"broadcast schedule failed at {(x, z, y0, y1, scratch)}")
                        states += 1

    # Complete illustrative invoice. Each c_* is a complete dirty-safe
    # one-target child including its target update, scratch restoration,
    # frame/precision, and recursive children. w and r are the additional
    # second-target update and broadcast routing/dispatch per broadcast.
    tariff = {
        "shared_setup_and_entry_exit": 3,
        "B_complete_call": 2,
        "C_complete_one_target_call": 4,
        "C_plus_D_complete_one_target_call": 4,
        "D_complete_one_target_call": 1,
        "extra_target_row_update_per_broadcast": 1,
        "extra_broadcast_route_dispatch": 1,
    }
    common = tariff["shared_setup_and_entry_exit"] + 2 * tariff["B_complete_call"]
    baseline = common + 2 * (
        tariff["C_complete_one_target_call"]
        + tariff["C_plus_D_complete_one_target_call"]
    )
    candidate = common + 2 * (
        tariff["C_complete_one_target_call"]
        + tariff["extra_target_row_update_per_broadcast"]
        + tariff["extra_broadcast_route_dispatch"]
        + tariff["D_complete_one_target_call"]
    )
    saving = baseline - candidate
    need((baseline, candidate, saving) == (23, 21, 2),
         "the explicitly charged fixture invoice changed")
    need(saving == 2 * (
        tariff["C_plus_D_complete_one_target_call"]
        - tariff["D_complete_one_target_call"]
        - tariff["extra_target_row_update_per_broadcast"]
        - tariff["extra_broadcast_route_dispatch"]
    ), "the two-boundary break-even identity failed")

    result = {
        "status": "PASS_LOWRANK_COMMON_READOUT",
        "matrices_f2_rows": {"C": list(C), "D": list(D), "C_plus_D": list(A1)},
        "ranks": {"C": rank_f2(C), "D": rank_f2(D), "C_plus_D": rank_f2(A1)},
        "dirty_states_checked": states,
        "controls": controls(),
        "cost_model": {
            "tariffs": tariff,
            "separate_schedule_total": baseline,
            "broadcast_schedule_total": candidate,
            "saving": saving,
            "scope": "declared complete-call tariff fixture; not a selected-supplier invoice",
        },
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

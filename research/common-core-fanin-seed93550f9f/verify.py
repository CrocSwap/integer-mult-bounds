#!/usr/bin/env python3
"""Exact dirty-state replay for a shared-core, rank-one-correction fan-in."""

from fractions import Fraction
import json
from pathlib import Path


N = 49
R = 48
SOURCES = 3
SELECTED_A = Fraction(836330098538459, 500000000000000000)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rank_f2(matrix):
    rows = [sum((value & 1) << col for col, value in enumerate(row))
            for row in matrix]
    ncols = len(matrix[0]) if matrix else 0
    pivot_row = 0
    for col in range(ncols):
        pivot = next((r for r in range(pivot_row, len(rows))
                      if (rows[r] >> col) & 1), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for r in range(len(rows)):
            if r != pivot_row and ((rows[r] >> col) & 1):
                rows[r] ^= rows[pivot_row]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def matvec(matrix, vector, mod2=False):
    out = [sum(coefficient * value
                for coefficient, value in zip(row, vector))
           for row in matrix]
    return [value & 1 for value in out] if mod2 else out


def add_scaled(target, source, scale=1, mod2=False):
    out = [left + scale * right for left, right in zip(target, source)]
    return [value & 1 for value in out] if mod2 else out


def make_maps():
    core = [[0] * N for _ in range(N)]
    for i in range(R):
        core[i][i] = 1

    deltas = []
    maps = []
    for extra_coordinate in (0, 1, 2):
        row = [0] * N
        row[extra_coordinate] = 1
        row[-1] = 1
        delta = [[0] * N for _ in range(N)]
        delta[-1] = row
        deltas.append(delta)
        maps.append([[core[i][j] + delta[i][j] for j in range(N)]
                     for i in range(N)])
    return core, deltas, maps


CORE, DELTAS, MAPS = make_maps()


def baseline(sources, target, mod2=False):
    out = target[:]
    for matrix, source in zip(MAPS, sources):
        out = add_scaled(out, matvec(matrix, source, mod2), mod2=mod2)
    return out


def factored(sources, target, scratch, omit_first_core=False,
             omit_delta=None, omit_restore_source=None,
             omit_gather_restore_source=None, mod2=False):
    out = target[:]
    temp = scratch[:]

    # The first core call cancels the unknown initial contents of temp.
    if not omit_first_core:
        out = add_scaled(out, matvec(CORE, temp, mod2), -1, mod2)

    # These are six complete rank-one row additions in the 3-source case.
    for index, source in enumerate(sources):
        if index != omit_gather_restore_source:
            temp = add_scaled(temp, source, mod2=mod2)
    out = add_scaled(out, matvec(CORE, temp, mod2), mod2=mod2)
    for index, source in enumerate(sources):
        if index != omit_restore_source and index != omit_gather_restore_source:
            temp = add_scaled(temp, source, -1, mod2)

    for index, (delta, source) in enumerate(zip(DELTAS, sources)):
        if index != omit_delta:
            out = add_scaled(out, matvec(delta, source, mod2), mod2=mod2)
    return out, temp


def basis_replay():
    # The complete map is linear in all 5 arbitrary rows. Equality on this
    # basis proves the identity for every F2 input and every dirty entry state.
    for role in range(5):
        for coordinate in range(N):
            sources = [[0] * N for _ in range(SOURCES)]
            target = [0] * N
            scratch = [0] * N
            if role < SOURCES:
                sources[role][coordinate] = 1
            elif role == SOURCES:
                target[coordinate] = 1
            else:
                scratch[coordinate] = 1
            expected = baseline(sources, target, mod2=True)
            actual, restored = factored(sources, target, scratch, mod2=True)
            require(actual == expected,
                    f"binary basis mismatch role={role} coordinate={coordinate}")
            require(restored == scratch,
                    f"scratch restoration mismatch role={role} coordinate={coordinate}")


def integer_replay():
    sources = [
        [((i * 17 + 3) % 11) - 5 for i in range(N)],
        [((i * 29 + 8) % 13) - 6 for i in range(N)],
        [((i * 31 + 1) % 17) - 8 for i in range(N)],
    ]
    target = [((i * 7 + 2) % 19) - 9 for i in range(N)]
    scratch = [((i * 23 + 5) % 21) - 10 for i in range(N)]
    initial_sources = [row[:] for row in sources]
    initial_scratch = scratch[:]
    actual, restored = factored(sources, target, scratch)
    require(actual == baseline(sources, target), "integer-valued map mismatch")
    require(restored == initial_scratch, "integer-valued scratch was not restored")
    require(sources == initial_sources, "a source row was modified")


def negative_controls():
    zero_sources = [[0] * N for _ in range(SOURCES)]
    zero_target = [0] * N
    dirty = [0] * N
    dirty[0] = 1
    correct, _ = factored(zero_sources, zero_target, dirty, mod2=True)
    require(correct == zero_target, "positive dirty scratch control failed")

    # A one-core-call shortcut appears valid with clean scratch but leaks B*t
    # for an arbitrary dirty scratch row.
    faulty_one_core = add_scaled(zero_target, matvec(CORE, dirty, mod2=True), mod2=True)
    require(faulty_one_core != correct,
            "dirty-scratch control failed to reject a one-core shortcut")

    source3 = [[0] * N for _ in range(SOURCES)]
    source3[2][-1] = 1
    expected = baseline(source3, zero_target, mod2=True)
    missing_delta, restored = factored(source3, zero_target, zero_target,
                                       omit_delta=2, mod2=True)
    require(missing_delta != expected,
            "omitted-correction control was not rejected")
    require(restored == zero_target,
            "omitted-correction control changed scratch")

    source2 = [[0] * N for _ in range(SOURCES)]
    source2[1][4] = 1
    expected = baseline(source2, zero_target, mod2=True)
    missing_source, restored = factored(
        source2, zero_target, zero_target,
        omit_gather_restore_source=1, mod2=True)
    require(missing_source != expected,
            "omitted-source control was not rejected")
    require(restored == zero_target,
            "omitted-source control changed scratch")

    leak_sources = [[0] * N for _ in range(SOURCES)]
    leak_sources[1][4] = 1
    dirty2 = [0] * N
    dirty2[3] = 1
    leaked_output, leaked_scratch = factored(
        leak_sources, zero_target, dirty2, omit_restore_source=1, mod2=True)
    require(leaked_scratch != dirty2,
            "omitted-restore control was not rejected")
    require(leaked_output == baseline(leak_sources, zero_target, mod2=True),
            "restore omission changed the computed target")


def cost_screen():
    a = SELECTED_A
    require(a < Fraction(1, 100), "selected exponent no longer fits the screen")
    require(49 ** 99 > 47 ** 100,
            "exact lower bound for 49^(0.99) > 47 failed")

    baseline_profile = {49: 3, 1: 3}  # 3 maps plus one dispatch unit each.
    factored_profile = {48: 2, 1: 20}  # 9 child ops plus 11 dispatch units.
    require(sum(r * n for r, n in baseline_profile.items()) == 150,
            "baseline rank-mass receipt changed")
    require(sum(r * n for r, n in factored_profile.items()) == 116,
            "factored rank-mass receipt changed")

    # With q=1-a, 49^q > 49^0.99 > 47 and 48^q < 48.
    # Hence old-new > 3*47 - 2*48 - 17 = 28.
    # H is every additional parent/interface cost in rank-one equivalents.
    return {
        "selected_a": str(a),
        "a_lt_1_over_100": True,
        "baseline_profile_including_dispatch": {str(k): v for k, v in baseline_profile.items()},
        "factored_profile_including_dispatch": {str(k): v for k, v in factored_profile.items()},
        "baseline_core_and_correction_calls": 3,
        "factored_core_calls": 2,
        "factored_rank_one_deviation_calls": 3,
        "factored_rank_one_gather_restore_calls": 6,
        "baseline_dispatch_units": 3,
        "factored_dispatch_units": 11,
        "extra_dirty_scratch_rows": 1,
        "scratch_coordinates": N,
        "integer_lift_guard_bits": 2,
        "lower_bound_saving_before_remaining_overhead": ">28 rank-one-equivalent units",
        "remaining_overhead_gate": "all extra interface, hosting, precision, and program costs must total < 28 units",
        "selected_supplier_or_kappa_claim": False,
    }


def main():
    root = Path(__file__).resolve().parents[2]
    selected = json.loads((root / "certificates/selected-result.json").read_text())
    require(selected["kappa"] == str(SELECTED_A),
            "selected-result exponent changed from the task pin")

    core_rank = rank_f2(CORE)
    delta_ranks = [rank_f2(delta) for delta in DELTAS]
    map_ranks = [rank_f2(matrix) for matrix in MAPS]
    require(core_rank == 48, f"core rank is {core_rank}, expected 48")
    require(delta_ranks == [1, 1, 1], f"deviation ranks changed: {delta_ranks}")
    require(map_ranks == [49, 49, 49], f"source-map ranks changed: {map_ranks}")
    require(len({tuple(delta[-1]) for delta in DELTAS}) == SOURCES,
            "source deviations must be distinct")

    basis_replay()
    integer_replay()
    negative_controls()
    cost = cost_screen()

    result = {
        "status": "PASS_COMMON_CORE_FANIN_DIRTY_BOUNDARY",
        "dimension": N,
        "sources": SOURCES,
        "core_rank": core_rank,
        "deviation_ranks": delta_ranks,
        "source_map_ranks": map_ranks,
        "basis_columns": 5 * N,
        "integer_replay": "PASS",
        "negative_controls": 4,
        "cost": cost,
        "scope": "Exact local connector construction only; no supplier realization or new kappa.",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

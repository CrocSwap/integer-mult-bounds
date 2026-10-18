#!/usr/bin/env python3
"""Exact dirty-state replay for a nine-source Johnson-path connector batch."""

from __future__ import annotations

from collections import Counter

N = 9
MASKS = (0x01F, 0x02F, 0x067, 0x0E3, 0x1E1)
SOURCE_WORD = (0, 1, 2, 3, 4, 4, 5, 3, 6, 2, 7, 1, 8, 0, 5, 6, 7, 8)
READOUT_BOUNDARIES = (5, 7, 9, 11, 13)
DIRTY_OUTPUTS = len(MASKS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parity_dot(source_values: int, support: int) -> int:
    return (source_values & support).bit_count() & 1


def prefix_masks() -> tuple[int, ...]:
    q = 0
    states = [q]
    for source in SOURCE_WORD:
        q ^= 1 << source
        states.append(q)
    return tuple(states)


def replay(source_values: int, dirty_connector: int, dirty_outputs: int) -> tuple[int, int]:
    """Execute the scheduled scalar F2 calls; return final z and output bits."""
    q = 0
    z = dirty_connector
    outputs = dirty_outputs

    # Each A_i is read once at the common zero prefix.
    for i in range(DIRTY_OUTPUTS):
        outputs ^= dirty_connector << i

    readout_at = {boundary: i for i, boundary in enumerate(READOUT_BOUNDARIES)}
    for boundary, source in enumerate(SOURCE_WORD, start=1):
        value = (source_values >> source) & 1
        z ^= value
        q ^= 1 << source
        if boundary in readout_at:
            output = readout_at[boundary]
            outputs ^= z << output

    require(q == 0, "source connector did not return to its entry parity")
    expected_z = dirty_connector
    require(z == expected_z, "dirty connector value was not restored")
    return z, outputs


def replay_row_stars(source_values: int, dirty_connector: int,
                     dirty_outputs: int) -> tuple[int, int]:
    """Independent per-output schedule used for the 60-call comparator."""
    z = dirty_connector
    outputs = dirty_outputs
    for i, support in enumerate(MASKS):
        outputs ^= z << i
        for source in range(N):
            if (support >> source) & 1:
                z ^= (source_values >> source) & 1
        outputs ^= z << i
        for source in range(N):
            if (support >> source) & 1:
                z ^= (source_values >> source) & 1
    return z, outputs


def verify_instance() -> tuple[int, int, tuple[int, ...]]:
    universe = (1 << N) - 1
    require(len(set(MASKS)) == DIRTY_OUTPUTS, "output supports must be distinct")
    require(all(mask.bit_count() == 5 for mask in MASKS), "each output must have weight five")
    require(set().union(*(set(j for j in range(N) if (mask >> j) & 1) for mask in MASKS)) == set(range(N)),
            "the output family must use all nine sources")
    common = universe
    for mask in MASKS:
        common &= mask
    require(common == 1, "only source 0 should be common to all five outputs")
    require(all((left ^ right).bit_count() == 2 for left, right in zip(MASKS, MASKS[1:])),
            "successive supports must differ by one exchange in J(9,5)")

    counts = Counter(SOURCE_WORD)
    require(counts == Counter({j: 2 for j in range(N)}), "every source must be toggled exactly twice")
    states = prefix_masks()
    require(tuple(states[b] for b in READOUT_BOUNDARIES) == MASKS,
            "the source word must visit all five requested supports")
    require(states[-1] == 0, "source path must end at zero")

    cases = 0
    for source_values in range(1 << N):
        for dirty_connector in (0, 1):
            for dirty_outputs in range(1 << DIRTY_OUTPUTS):
                final_z, actual_outputs = replay(source_values, dirty_connector, dirty_outputs)
                expected_outputs = dirty_outputs
                for i, support in enumerate(MASKS):
                    expected_outputs ^= parity_dot(source_values, support) << i
                require(final_z == dirty_connector, "connector restoration failed")
                require(actual_outputs == expected_outputs, "dirty-state output map mismatch")
                stars_z, stars_outputs = replay_row_stars(
                    source_values, dirty_connector, dirty_outputs)
                require(stars_z == dirty_connector and stars_outputs == expected_outputs,
                        "independent row-star control disagrees with the target map")
                cases += 1

    require(cases == (1 << N) * 2 * (1 << DIRTY_OUTPUTS), "dirty-state domain is incomplete")

    # Failure control 1: a lone A readout leaks arbitrary entry dirt.
    dirty_y, dirty_z, zero_sources = 0, 1, 0
    lone_read = dirty_y ^ dirty_z ^ parity_dot(zero_sources, 0)
    require(lone_read != dirty_y, "single-readout dirty-z control failed to expose leakage")

    # Failure control 2: reading output 0 at the S2 boundary instead of S1
    # returns source 4 even though source 4 is absent from its requested row.
    wrong_source_values = 1 << 4
    wrong_boundary_term = parity_dot(wrong_source_values, states[READOUT_BOUNDARIES[1]])
    correct_row_term = parity_dot(wrong_source_values, MASKS[0])
    require(wrong_boundary_term != correct_row_term, "wrong-boundary control failed")

    # Failure control 3: omit the final B8 call and set x8=1; the connector
    # then retains the source-8 coefficient instead of restoring to entry.
    without_last = SOURCE_WORD[:-1]
    q = 0
    for source in without_last:
        q ^= 1 << source
    omitted_restore_residual = parity_dot(1 << 8, q)
    require(omitted_restore_residual == 1, "missing-restoration control failed")

    # The exact call floor and the row-by-row comparator use the same complete
    # unit-call alphabet: 2 per active source, 2 per output; 2r+2 per row star.
    source_calls = len(SOURCE_WORD)
    readout_calls = 2 * DIRTY_OUTPUTS
    lower_floor = 2 * N + 2 * DIRTY_OUTPUTS
    row_stars = DIRTY_OUTPUTS * (2 * 5 + 2)
    require(source_calls == 2 * N and readout_calls == 2 * DIRTY_OUTPUTS,
            "schedule call counts do not meet the source/readout lower floor")
    require(source_calls + readout_calls == lower_floor == 28,
            "schedule did not attain the exact complete-call floor")
    require(row_stars == 60, "row-star baseline arithmetic changed")

    # Heterogeneous complete-call prices are charged by operator type. The
    # output-readout bill is identical in both schedules; B_j is used 2*d_j
    # times in separate stars and exactly twice in the shared path.
    degrees = tuple(sum((mask >> j) & 1 for mask in MASKS) for j in range(N))
    require(degrees == (5, 4, 3, 2, 1, 4, 3, 2, 1), "source incidence vector changed")
    source_prices = tuple(range(1, N + 1))
    target_prices = tuple(range(1, DIRTY_OUTPUTS + 1))
    shared_weighted = 2 * sum(source_prices) + 2 * sum(target_prices)
    stars_weighted = (2 * sum(degrees[j] * source_prices[j] for j in range(N))
                      + 2 * sum(target_prices))
    weighted_saving = 2 * sum((degrees[j] - 1) * source_prices[j] for j in range(N))
    require(stars_weighted - shared_weighted == weighted_saving == 120,
            "heterogeneous complete-call price accounting failed")
    require(weighted_saving > 0, "positive source call prices should yield a strict saving")
    return cases, weighted_saving, degrees


def main() -> None:
    cases, weighted_saving, degrees = verify_instance()
    print("PASS_NINE_SOURCE_WEIGHT_FIVE_JOHNSON_CHAIN")
    print(f"supports={','.join(f'{m:03x}' for m in MASKS)}")
    print("common_sources=0")
    print(f"source_word={','.join(str(j) for j in SOURCE_WORD)}")
    print("source_calls=18")
    print("readout_calls=10")
    print("total_complete_calls=28")
    print("independent_row_stars=60")
    print("saved_calls=32")
    print(f"source_incidence_counts={','.join(str(x) for x in degrees)}")
    print(f"weighted_price_control_saving={weighted_saving}")
    print(f"dirty_state_cases={cases}")
    print("controls=single-readout,wrong-boundary,missing-restoration")
    print("scope=singleton F2 connector; weighted formula assumes stable per-call prices; no supplier or kappa claim")


if __name__ == "__main__":
    main()

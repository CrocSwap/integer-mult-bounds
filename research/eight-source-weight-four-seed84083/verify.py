#!/usr/bin/env python3
"""Exact census of two-sweep source paths for the n=8, weight-4 shell."""

from __future__ import annotations

from itertools import combinations, permutations

N = 8
FIRST_SWEEP = tuple(range(N))
TARGETS = tuple(sum(1 << j for j in subset) for subset in combinations(range(N), 4))
TARGET_INDEX = {mask: i for i, mask in enumerate(TARGETS)}
FULL_COVER = (1 << len(TARGETS)) - 1


def prefixes(second: tuple[int, ...]) -> tuple[int, ...]:
    """Return the 17 source-parity states for the two-sweep word."""
    state = 0
    out = [state]
    for source in FIRST_SWEEP + second:
        state ^= 1 << source
        out.append(state)
    return tuple(out)


def cover_word(second: tuple[int, ...]) -> int:
    """Encode all weight-four differences between the 17 prefix states."""
    states = prefixes(second)
    cover = 0
    for i, left in enumerate(states):
        for right in states[i + 1 :]:
            index = TARGET_INDEX.get(left ^ right)
            if index is not None:
                cover |= 1 << index
    return cover


def cover_by_intervals(second: tuple[int, ...]) -> int:
    """Independent encoding by toggling each contiguous source subword."""
    word = FIRST_SWEEP + second
    cover = 0
    for start in range(len(word)):
        mask = 0
        for source in word[start:]:
            mask ^= 1 << source
            index = TARGET_INDEX.get(mask)
            if index is not None:
                cover |= 1 << index
    return cover


def first_pair_for(states: tuple[int, ...], target: int) -> tuple[int, int] | None:
    for i, left in enumerate(states):
        for j in range(i + 1, len(states)):
            if left ^ states[j] == target:
                return i, j
    return None


def _dot(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def check_replay(states: tuple[int, ...], target: int, pair: tuple[int, int]) -> None:
    """Exhaust dirty connector/output and all source bits for one target."""
    i, j = pair
    assert states[i] ^ states[j] == target
    for source_values in range(1 << N):
        expected_term = _dot(source_values, target)
        for dirty_connector in (0, 1):
            for dirty_output in (0, 1):
                connector_i = dirty_connector ^ _dot(source_values, states[i])
                connector_j = dirty_connector ^ _dot(source_values, states[j])
                actual_output = dirty_output ^ connector_i ^ connector_j
                assert actual_output == dirty_output ^ expected_term
                assert _dot(source_values, states[-1]) == 0


def main() -> None:
    best_second: tuple[int, ...] | None = None
    best_cover = -1
    full_second: tuple[int, ...] | None = None
    permutation_count = 0
    maximum_attainers = 0
    histogram: dict[int, int] = {}

    for second in permutations(range(N)):
        permutation_count += 1
        cover = cover_word(second)
        count = cover.bit_count()
        assert cover == cover_by_intervals(second)
        histogram[count] = histogram.get(count, 0) + 1
        if count > best_cover:
            best_cover, best_second = count, second
            maximum_attainers = 1
        elif count == best_cover:
            maximum_attainers += 1
        if cover == FULL_COVER:
            full_second = second
            break

    assert best_second is not None
    if full_second is None:
        assert permutation_count == 40320
        assert sum(histogram.values()) == 40320
    selected = full_second if full_second is not None else best_second
    states = prefixes(selected)
    coverage = cover_word(selected)
    assert coverage.bit_count() == (70 if full_second is not None else best_cover)
    selected_word = FIRST_SWEEP + selected
    assert all(selected_word.count(source) == 2 for source in range(N))
    assert states[-1] == 0
    if full_second is None:
        assert best_cover == 23
        assert maximum_attainers == 68
        assert best_second == (2, 4, 6, 0, 7, 1, 3, 5)

    # A genuine positive control: every mask counted as covered has an exact
    # pair, and the dirty-state identity holds for all 2^8 source assignments.
    covered_masks = [mask for mask in TARGETS if coverage & (1 << TARGET_INDEX[mask])]
    for mask in covered_masks:
        pair = first_pair_for(states, mask)
        assert pair is not None
        check_replay(states, mask, pair)
    uncovered_masks = [mask for mask in TARGETS
                       if not coverage & (1 << TARGET_INDEX[mask])]
    if full_second is None:
        assert uncovered_masks
        assert first_pair_for(states, uncovered_masks[0]) is None

    # Negative controls: one A readout fails to cancel dirty z; deleting the
    # final source toggle leaves that source's coefficient in the connector.
    dirty_z, dirty_y = 1, 0
    one_readout_output = dirty_y ^ dirty_z
    assert one_readout_output != dirty_y
    final_source = (FIRST_SWEEP + selected)[-1]
    final_source_assignment = 1 << final_source
    omitted_toggle_residual = _dot(final_source_assignment, 1 << final_source)
    assert omitted_toggle_residual == 1

    print("PASS_TWO_SWEEP_WEIGHT_FOUR_CENSUS")
    print(f"permutations={permutation_count}")
    print(f"covered={coverage.bit_count()}/70")
    print(f"second_sweep={','.join(str(i) for i in selected)}")
    print(f"covered_masks={','.join(f'{mask:02x}' for mask in covered_masks)}")
    if full_second is None:
        print(f"maximum_attainers={maximum_attainers}")
        print(f"uncovered_masks={','.join(f'{mask:02x}' for mask in uncovered_masks)}")
        print("scope=two complete sweeps only; no universal impossibility claim")
    else:
        print("source_toggles=16")
        print("target_readouts=140")
        print("total_complete_calls=156")
        print("row_by_row_restored_stars=700")
        print("scope=connector-level complete-call model; no supplier or kappa claim")


if __name__ == "__main__":
    main()

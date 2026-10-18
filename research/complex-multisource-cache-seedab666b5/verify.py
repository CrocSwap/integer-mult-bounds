#!/usr/bin/env python3
"""Exact endpoint and profile screen for a three-source clean cache."""
from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = Q(1, 10**12)
M = 73
FAMILIES = 896
STAGES = 9
BASE_CENTRE = 64
CANDIDATE_CENTRE = 65
MAX_GROUPS = BASE[2] // 6


def unit(n: int, i: int) -> list[int]:
    row = [0] * n
    row[i] = 1
    return row


def add(dst: list[int], src: list[int], sign: int = 1) -> list[int]:
    return [a + sign * b for a, b in zip(dst, src)]


def initial_state(groups: int, dirty_scratch: bool = False) -> tuple[list[list[int]], int]:
    """Return register rows and variable count; clean scratch is the zero row."""
    data_registers = 5 * groups
    variables = data_registers + int(dirty_scratch)
    state = [unit(variables, i) for i in range(data_registers)]
    scratch = unit(variables, data_registers) if dirty_scratch else [0] * variables
    state.append(scratch)
    return state, variables


def expected(groups: int, dirty_scratch: bool = False) -> list[list[int]]:
    state, variables = initial_state(groups, dirty_scratch)
    expected_state = [row[:] for row in state]
    for group in range(groups):
        sources = range(3 * group, 3 * group + 3)
        first_target = 3 * groups + 2 * group
        for target in (first_target, first_target + 1):
            row = expected_state[target]
            for source in sources:
                row = add(row, expected_state[source])
            expected_state[target] = row
    if dirty_scratch:
        # A dirty cache is not accepted as the clean-helper contract.
        expected_state[-1] = unit(variables, 5 * groups)
    else:
        expected_state[-1] = [0] * variables
    return expected_state


def run_cache(groups: int, *, dirty_scratch: bool = False,
              restore: bool = True, alias_outputs: bool = False) -> tuple[list[list[int]], int]:
    state, variables = initial_state(groups, dirty_scratch)
    scratch = 5 * groups
    source_touches = 0
    for group in range(groups):
        source_ids = range(3 * group, 3 * group + 3)
        # Load the coded line into the single clean scratch register.
        for source in source_ids:
            state[scratch] = add(state[scratch], state[source])
            source_touches += 1
        first_target = 3 * groups + 2 * group
        second_target = first_target if alias_outputs else first_target + 1
        state[first_target] = add(state[first_target], state[scratch])
        state[second_target] = add(state[second_target], state[scratch])
        if restore:
            for source in source_ids:
                state[scratch] = add(state[scratch], state[source], -1)
                source_touches += 1
    return state, source_touches


def candidate_profile(groups: int) -> dict[int, int]:
    if not 1 <= groups <= MAX_GROUPS:
        raise ValueError("group count outside the declared domain")
    profile = dict(BASE)
    profile[1] += 2 * groups       # Two rank-1 output channels per group.
    profile[2] -= 6 * groups       # Remove six direct rank-2 channels.
    profile[3] += 2 * groups       # Rank-3 load and exact restore.
    return profile


def verify_endpoints(groups: int) -> None:
    direct = expected(groups)
    cached, source_touches = run_cache(groups)
    assert cached == direct, f"cached endpoint differs from direct route for g={groups}"
    assert source_touches == 6 * groups, "source read count changed"
    # Each group's six source lines and all outputs are independent register rows.
    assert len(cached) == 5 * groups + 1
    assert cached[-1] == [0] * (5 * groups), "clean scratch was not restored"
    for source in range(3 * groups):
        assert cached[source] == unit(5 * groups, source), "source register was modified"


def verify_controls() -> None:
    clean = expected(1)
    dirty_result, _ = run_cache(1, dirty_scratch=True)
    assert dirty_result != clean, "dirty-scratch control should fail the clean endpoint"
    omitted_restore, _ = run_cache(1, restore=False)
    assert omitted_restore != clean, "omitted-restore control should fail"
    aliased, _ = run_cache(1, alias_outputs=True)
    assert aliased != clean, "aliased-output control should fail"


def ceiling(profile: dict[int, int], centre: int) -> tuple[Q, Q]:
    return C.ceiling(profile, M, FAMILIES, STAGES, centre, grid=GRID)


def main() -> None:
    verify_endpoints(1)
    verify_endpoints(MAX_GROUPS)
    verify_controls()

    baseline = ceiling(BASE, BASE_CENTRE)
    profile = candidate_profile(MAX_GROUPS)
    candidate = ceiling(profile, CANDIDATE_CENTRE)
    assert baseline == (Q(1690054109, 10**12), Q(169005411, 10**11))
    assert candidate == (Q(1721731989, 10**12), Q(172173199, 10**11))
    assert candidate[0] > baseline[1], "candidate does not beat the selected-word ceiling"
    assert candidate[1] < Q(1, 99), "candidate unexpectedly reaches the stronger-budget target"

    lower_alpha = candidate[0]
    g1_relax = C.relax(candidate_profile(1), M, FAMILIES, STAGES,
                       CANDIDATE_CENTRE, lower_alpha)
    gmax_relax = C.relax(profile, M, FAMILIES, STAGES,
                         CANDIDATE_CENTRE, lower_alpha)
    assert gmax_relax[1] < g1_relax[0], "profile gain is not increasing through g=69"

    delta_percent = (candidate[1] / baseline[1] - 1) * 100
    kappa_cap = candidate[1] / (1 + candidate[1])
    print(
        "PASS_THREE_SOURCE_CACHE "
        f"groups={MAX_GROUPS} profile={profile} centre={CANDIDATE_CENTRE} "
        f"rank_mass={sum(r*n for r,n in profile.items())} "
        f"baseline_alpha=[{baseline[0]},{baseline[1]}] "
        f"candidate_alpha=[{candidate[0]},{candidate[1]}] "
        f"cap_gain_percent={float(delta_percent):.9f} "
        f"conditional_kappa_cap={float(kappa_cap):.12f} "
        f"linear_adds_direct={6*MAX_GROUPS} linear_adds_cached={8*MAX_GROUPS} "
        "controls=dirty_scratch,omitted_restore,aliased_outputs"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact screen for chronological direct-sum packing of rank-2/3 children."""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import sys
import tarfile
from functools import lru_cache
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
EXPECTED_PROFILE = {
    1: 2412,
    2: 362,
    3: 123,
    4: 158,
    5: 87,
    6: 127,
    8: 9,
    9: 1,
    12: 4,
    15: 5,
    16: 3,
}
BASE_CEILING_HI = Q(1690054109089, 10**15)
CANDIDATE_CEILING = (Q(1764844128532, 10**15), Q(1764844128533, 10**15))
EXPECTED_MAX_SAVING_HI = Q(
    2517691243955728211484679689432964574968478486787216632584191406584661519947,
    115792089237316195423570985008687907853269984665640564039457584007913129639936,
)
EXPECTED_BEST_RELAX_LO = Q(
    103752514267675293995553180164777208990301975357240430776147835751897807186332125,
    103749711956635311099519602567784365436529906260413945379353995271090164157382656,
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def selected_programs() -> dict[str, list]:
    archive = ARCHIVE.read_bytes()
    require(hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA256, "selected replay archive pin")
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        members = [member for member in tar.getmembers() if member.name == MEMBER]
        require(len(members) == 1, "exactly one selected local-program member")
        raw = tar.extractfile(members[0]).read()
    require(hashlib.sha256(raw).hexdigest() == MEMBER_SHA256, "selected provider member pin")
    return json.loads(gzip.decompress(raw))


def paid_profile(events: list) -> dict[int, int]:
    profile = collections.Counter()
    for event in events:
        if event[0] == "climb":
            profile[event[5]] += 1
        elif event[0] == "center":
            profile[event[4]] += 1
    return dict(sorted(profile.items()))


def rank23_runs(events: list) -> list[list[tuple[int, int]]]:
    """Phase markers are free; every other non-rank-2/3 event breaks a run."""
    runs: list[list[tuple[int, int]]] = []
    current: list[tuple[int, int]] = []
    for index, event in enumerate(events):
        if event[0] == "phase":
            continue
        if event[0] == "climb" and event[5] in (2, 3):
            current.append((index, event[5]))
        else:
            if current:
                runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def direct_sum_matrices(block_sizes: tuple[int, ...], side: int = 16):
    """Return sparse symbolic A,B entries for a block-diagonal product."""
    require(sum(block_sizes) == side, "test blocks must fill the child side")
    a = [[[] for _ in range(side)] for _ in range(side)]
    b = [[[] for _ in range(side)] for _ in range(side)]
    block_of = {}
    start = 0
    for block, size in enumerate(block_sizes):
        for row in range(start, start + size):
            for col in range(start, start + size):
                a[row][col] = [("A", block, row - start, col - start)]
                b[row][col] = [("B", block, row - start, col - start)]
                block_of[row] = block
        start += size
    return a, b, block_of


def symbolic_product(a: list[list[list]], b: list[list[list]]) -> list[list[set[tuple]]]:
    side = len(a)
    out = [[set() for _ in range(side)] for _ in range(side)]
    for i in range(side):
        for j in range(side):
            for k in range(side):
                out[i][j].update((x, y) for x in a[i][k] for y in b[k][j])
    return out


def check_direct_sum_identity() -> None:
    sizes = (2, 2, 3, 3, 3, 3)
    a, b, block_of = direct_sum_matrices(sizes)
    product = symbolic_product(a, b)
    starts = []
    pos = 0
    for size in sizes:
        starts.append((pos, pos + size))
        pos += size
    for i in range(16):
        for j in range(16):
            expected = set()
            if block_of[i] == block_of[j]:
                lo, hi = starts[block_of[i]]
                expected = {
                    (("A", block_of[i], i - lo, k - lo), ("B", block_of[i], k - lo, j - lo))
                    for k in range(lo, hi)
                }
            require(product[i][j] == expected, f"block-diagonal product entry ({i},{j})")

    # Negative control: a cross-block input makes a cross-block output term.
    bad_a = [row[:] for row in a]
    bad_a[0][2] = [("A", "cross", 0, 0)]
    bad_product = symbolic_product(bad_a, b)
    require(bool(bad_product[0][2]), "off-block-support negative control")


@lru_cache(None)
def child_cost(rank: int, target: Q) -> tuple[Q, Q]:
    return C.child_cost(rank, 73, target)


def optimize_run(run: list[tuple[int, int]], target: Q):
    """Maximize certified saving bounds over disjoint intervals of total rank <=16."""
    n = len(run)
    best_lo, best_hi = [Q(0)] * (n + 1), [Q(0)] * (n + 1)
    path_lo, path_hi = [[] for _ in range(n + 1)], [[] for _ in range(n + 1)]
    interval_count = 0
    for end in range(1, n + 1):
        best_lo[end], path_lo[end] = best_lo[end - 1], path_lo[end - 1]
        best_hi[end], path_hi[end] = best_hi[end - 1], path_hi[end - 1]
        mass = 0
        before_lo = before_hi = Q(0)
        for start in range(end - 1, -1, -1):
            rank = run[start][1]
            mass += rank
            if mass > 16:
                break
            low, high = child_cost(rank, target)
            before_lo += low
            before_hi += high
            if end - start < 2:
                continue
            interval_count += 1
            group_lo, group_hi = child_cost(mass, target)
            saving_lo = before_lo - group_hi
            saving_hi = before_hi - group_lo
            value_lo, value_hi = best_lo[start] + saving_lo, best_hi[start] + saving_hi
            if value_lo > best_lo[end]:
                best_lo[end] = value_lo
                path_lo[end] = path_lo[start] + [(start, end, mass)]
            if value_hi > best_hi[end]:
                best_hi[end] = value_hi
                path_hi[end] = path_hi[start] + [(start, end, mass)]
    return best_lo[n], best_hi[n], path_lo[n], path_hi[n], interval_count


def evaluate_orientation(events: list, target: Q):
    runs = rank23_runs(events)
    savings_lo = savings_hi = Q(0)
    schedule = []
    intervals = 0
    for run in runs:
        lo, hi, chosen_lo, chosen_hi, count = optimize_run(run, target)
        savings_lo += lo
        savings_hi += hi
        intervals += count
        require(chosen_lo == chosen_hi, "certified low/high optimizer paths agree")
        for start, end, rank in chosen_lo:
            schedule.append(
                [run[start][0], run[end - 1][0], rank, [r for _, r in run[start:end]]]
            )
    schedule.sort(key=lambda item: item[0])
    profile = BASE_PROFILE.copy()
    for _, _, new_rank, old_ranks in schedule:
        for rank in old_ranks:
            profile[rank] -= 1
        profile[new_rank] = profile.get(new_rank, 0) + 1
    return runs, intervals, schedule, savings_lo, savings_hi, dict(sorted(profile.items()))


def check_break_control() -> None:
    a = ["climb", "test", 0, 1, 1, 2]
    b = ["climb", "test", 1, 2, 1, 2]
    events = [a, ["scalar", "break"], b]
    require(len(rank23_runs(events)) == 2, "non-phase event must break a packing run")
    events = [a, ["phase", "free-marker"], b]
    require(len(rank23_runs(events)) == 1, "phase marker does not break a packing run")


def check_mass_control(profile: dict[int, int]) -> None:
    mass = sum(rank * count for rank, count in profile.items())
    require(mass == 5586, "rank mass is conserved")
    bad = profile.copy()
    bad[2] -= 1
    require(sum(rank * count for rank, count in bad.items()) != 5586, "rank-mass negative control")


def main() -> None:
    programs = selected_programs()
    require(set(programs) == {"forward", "backward"}, "both selected orientations present")
    target = BASE_CEILING_HI * Q(105, 100)
    oriented = {}
    for name, events in programs.items():
        require(paid_profile(events) == BASE_PROFILE, f"{name} selected paid profile")
        result = evaluate_orientation(events, target)
        runs, intervals, schedule, savings_lo, savings_hi, profile = result
        require((len(runs), sum(map(len, runs)), intervals, len(schedule)) == (641, 850, 341, 162),
                f"{name} exact bounded search coverage")
        require(profile == EXPECTED_PROFILE, f"{name} optimized zero-charge profile")
        require(savings_hi == EXPECTED_MAX_SAVING_HI, f"{name} exact maximum saving enclosure")
        require(savings_lo <= savings_hi, f"{name} saving enclosure order")
        oriented[name] = result
    require(oriented["forward"] == oriented["backward"], "orientation schedules and profiles agree")

    base_relax = C.relax(BASE_PROFILE, 73, 896, 9, 64, target)
    best_possible_relax_lo = base_relax[0] - EXPECTED_MAX_SAVING_HI / Q(896, 9)
    require(best_possible_relax_lo == EXPECTED_BEST_RELAX_LO, "exact optimistic all-packing lower bound")
    require(best_possible_relax_lo > 1, "even maximum zero-charge saving misses the five-percent target")
    candidate_bracket = C.ceiling(EXPECTED_PROFILE, 73, 896, 9, 64, grid=Q(1, 10**15))
    require(candidate_bracket == CANDIDATE_CEILING, "optimized profile exact ceiling bracket")
    require(candidate_bracket[1] < target, "reconstructed profile misses five-percent gate")
    require(sum(r * n for r, n in EXPECTED_PROFILE.items()) == 5586, "optimized profile mass")

    check_direct_sum_identity()
    check_break_control()
    check_mass_control(EXPECTED_PROFILE)
    result = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    require(result["selected_profile"] == {str(k): v for k, v in EXPECTED_PROFILE.items()}, "RESULT profile")
    require(result["candidate_ceiling"] == [str(candidate_bracket[0]), str(candidate_bracket[1])], "RESULT ceiling")
    require(result["best_possible_relax_lower_at_target"] == str(best_possible_relax_lo), "RESULT global bound")
    require(result["best_possible_relax_gap_lower"] == str(best_possible_relax_lo - 1), "RESULT target margin")
    require(result["max_packing_saving_hi_at_target"] == str(EXPECTED_MAX_SAVING_HI), "RESULT optimizer bound")
    require(result["per_orientation"]["nontrivial_merge_intervals"] == 341, "RESULT candidate count")
    require(result["per_orientation"]["windows_including_singletons"] == 1191, "RESULT all-window count")
    gain = 100 * (candidate_bracket[1] / BASE_CEILING_HI - 1)
    gap = best_possible_relax_lo - 1
    print(
        "PASS_COMPLEX_MIXED_RANK_DIAGONAL_BLOCKS "
        f"runs=641 nontrivial_intervals=341 windows_with_singletons=1191 disjoint_blocks=162 rank_mass=5586 "
        f"best_profile_ceiling_hi={float(candidate_bracket[1]):.15f} "
        f"ceiling_gain_percent={float(gain):.6f} "
        f"best_possible_target_relax_gap={float(gap):.12g} "
        "five_percent_gate=missed controls=4"
    )


if __name__ == "__main__":
    main()

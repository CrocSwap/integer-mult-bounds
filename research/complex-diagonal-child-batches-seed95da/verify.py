#!/usr/bin/env python3
"""Replay the selected-word contiguous diagonal-batch screen with exact pins."""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import tarfile
import sys
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
EXPECTED_BATCHES = (
    (17006, 17021, 456, 471),
    (17106, 17121, 592, 607),
    (17122, 17137, 608, 623),
    (17138, 17153, 624, 639),
    (17154, 17169, 640, 655),
    (17170, 17185, 656, 671),
    (17186, 17201, 672, 687),
    (17202, 17217, 688, 703),
)
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
BASE_CEILING_HI = Q(1690054109089, 10**15)
CANDIDATE_PROFILE = {1: 2284, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8, 16: 8}
CANDIDATE_CEILING = (
    Q(1719107428153, 10**15),
    Q(1719107428154, 10**15),
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def selected_programs() -> dict[str, list]:
    archive = ARCHIVE.read_bytes()
    require(hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA256, "selected replay archive pin")
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.name == MEMBER]
        require(len(members) == 1, "exactly one selected gauge44 program member")
        raw = tar.extractfile(members[0]).read()
    require(hashlib.sha256(raw).hexdigest() == MEMBER_SHA256, "selected provider member pin")
    return json.loads(gzip.decompress(raw))


def rank_one_runs(events: list) -> list[list[tuple[int, list]]]:
    """Runs ignore phase markers only; every computational event breaks a run."""
    runs: list[list[tuple[int, list]]] = []
    current: list[tuple[int, list]] = []
    for index, event in enumerate(events):
        if event[0] == "phase":
            continue
        if event[0] == "climb" and event[5] == 1:
            current.append((index, event))
        else:
            if current:
                runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def admissible_batches(events: list) -> list[tuple[int, int, int, int]]:
    batches = []
    for run in rank_one_runs(events):
        for group in range(len(run) // 16):
            block = run[group * 16:(group + 1) * 16]
            indices = [i for i, _ in block]
            climbs = [e for _, e in block]
            columns = [e[2] for e in climbs]
            if len(set(columns)) != 16:
                continue
            batches.append((indices[0], indices[-1], columns[0], columns[-1]))
    return batches


def diagonal_product(a: list[list[int | None]], b: list[list[int | None]]) -> list[list[set[tuple[int, int]]]]:
    n = len(a)
    out = [[set() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if a[i][k] is not None and b[k][j] is not None:
                    out[i][j].add((a[i][k], b[k][j]))
    return out


def check_diagonal_identity() -> None:
    n = 16
    a = [[i if i == j else None for j in range(n)] for i in range(n)]
    b = [[i if i == j else None for j in range(n)] for i in range(n)]
    out = diagonal_product(a, b)
    for i in range(n):
        for j in range(n):
            expected = {(i, i)} if i == j else set()
            require(out[i][j] == expected, f"diagonal block product at ({i},{j})")

    # A nonzero off-diagonal entry invalidates the direct-sum premise.
    bad_a = [row[:] for row in a]
    bad_a[0][1] = 16
    bad = diagonal_product(bad_a, b)
    require(bool(bad[0][1]), "off-diagonal-support negative control")


def check_batch_controls(events: list, spec: tuple[int, int, int, int]) -> None:
    start, end, first_column, last_column = spec
    block = events[start:end + 1]
    require(len(block) == 16, "source block length")
    require(all(e[0] == "climb" and e[5] == 1 for e in block), "source block rank-one tags")
    require([e[2] for e in block] == list(range(first_column, last_column + 1)), "source destinations")

    wrong_rank = [e[:] for e in block]
    wrong_rank[0][5] = 2
    duplicate_column = [e[:] for e in block]
    duplicate_column[0][2] = duplicate_column[1][2]
    require(not all(e[0] == "climb" and e[5] == 1 for e in wrong_rank), "wrong-rank negative control")
    require(len({e[2] for e in duplicate_column}) != 16, "duplicate-destination negative control")


def main() -> None:
    programs = selected_programs()
    require(set(programs) == {"forward", "backward"}, "both selected orientations present")
    orientation_batches = {}
    for orientation, events in programs.items():
        profile = collections.Counter()
        for event in events:
            if event[0] == "climb":
                profile[event[5]] += 1
            elif event[0] == "center":
                profile[event[4]] += 1
        require(dict(sorted(profile.items())) == BASE_PROFILE, f"{orientation} paid profile")
        require(profile[1] == 2412, f"{orientation} rank-one count")
        runs = rank_one_runs(events)
        require(sum(len(run) // 16 for run in runs) == 8, f"{orientation} maximum run packing")
        found = admissible_batches(events)
        require(tuple(found) == EXPECTED_BATCHES, f"{orientation} exact batch windows")
        for spec in EXPECTED_BATCHES:
            check_batch_controls(events, spec)
        orientation_batches[orientation] = found
    require(orientation_batches["forward"] == orientation_batches["backward"], "orientation batch agreement")

    mass_before = sum(r * n for r, n in BASE_PROFILE.items())
    mass_after = sum(r * n for r, n in CANDIDATE_PROFILE.items())
    require(mass_before == mass_after == 5586, "rank mass preserved by eight batches")
    require(BASE_PROFILE[1] - CANDIDATE_PROFILE[1] == 128, "sixteen rank-one calls per batch")
    require(CANDIDATE_PROFILE[16] == 8, "one rank-sixteen child per batch")

    base_bracket = C.ceiling(BASE_PROFILE, 73, 896, 9, 64, grid=Q(1, 10**15))
    candidate_bracket = C.ceiling(CANDIDATE_PROFILE, 73, 896, 9, 64, grid=Q(1, 10**15))
    require(base_bracket[1] == BASE_CEILING_HI, "baseline ceiling pin")
    require(candidate_bracket == CANDIDATE_CEILING, "candidate exact ceiling bracket")
    target = BASE_CEILING_HI * Q(105, 100)
    require(candidate_bracket[1] < target, "zero-charge profile misses the five-percent gate")
    require(candidate_bracket[1] > BASE_CEILING_HI, "diagonal batching improves the ideal ceiling")

    check_diagonal_identity()
    gain = 100 * (candidate_bracket[1] / BASE_CEILING_HI - 1)
    print(
        "PASS_COMPLEX_DIAGONAL_CHILD_BATCH_SCREEN "
        f"groups=8 rank1_repacked=128 profile_mass={mass_after} "
        f"baseline_a_hi={float(BASE_CEILING_HI):.15f} "
        f"candidate_a_hi={float(candidate_bracket[1]):.15f} "
        f"gain_percent={float(gain):.6f} target_percent=5 controls=3"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact bounded screen for one-touch rank-1 pair retiming."""

from __future__ import annotations

import bisect
import collections
import gzip
import hashlib
import importlib.util
import io
import json
import tarfile
from fractions import Fraction as Q
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
GRID = Q(1, 10**15)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_program(compressed: bytes, expected_sha256: str) -> dict:
    require(sha256(compressed) == expected_sha256, "LOCAL-PROGRAMS member hash mismatch")
    return json.loads(gzip.decompress(compressed))


def source_program() -> dict:
    archive_bytes = ARCHIVE.read_bytes()
    require(sha256(archive_bytes) == ARCHIVE_SHA256, "selected replay archive hash mismatch")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        member = archive.extractfile(MEMBER)
        require(member is not None, "pinned local program is absent from archive")
        compressed = member.read()
    return decode_program(compressed, MEMBER_SHA256)


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    raw = path.read_bytes()
    require(sha256(raw) == CEILING_SHA256, "pinned ceiling engine hash mismatch")
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    require(spec is not None and spec.loader is not None, "cannot import pinned ceiling engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidate_edges(events: list) -> tuple[set[tuple[int, int]], dict[int, int]]:
    """Return (column, climb-position) edges for one-touch (1,1) climb pairs."""
    climbs: dict[int, list[tuple[int, int]]] = collections.defaultdict(list)
    touches: dict[int, list[tuple[int, str]]] = collections.defaultdict(list)
    for index, event in enumerate(events):
        require(isinstance(event, list) and event, "malformed local-program event")
        tag = event[0]
        if tag == "climb":
            require(len(event) >= 6, "malformed climb event")
            climbs[int(event[2])].append((index, int(event[5])))
        elif tag == "scalar":
            require(len(event) >= 2 and isinstance(event[1], list), "malformed scalar event")
            refs = set()
            for operand in event[1][1:]:
                if isinstance(operand, list) and len(operand) >= 2 and operand[0] == "L":
                    refs.add(int(operand[1]))
            for column in refs:
                touches[column].append((index, tag))
        elif tag in ("adapter", "residual_adapter"):
            require(len(event) >= 3, "malformed adapter event")
            touches[int(event[2])].append((index, tag))

    edges: set[tuple[int, int]] = set()
    sizes = {column: len(sequence) for column, sequence in climbs.items()}
    for column, sequence in climbs.items():
        column_touches = touches.get(column, [])
        positions = [index for index, _ in column_touches]
        for position, ((left, rank_left), (right, rank_right)) in enumerate(
            zip(sequence, sequence[1:])
        ):
            if rank_left != 1 or rank_right != 1:
                continue
            first = bisect.bisect_right(positions, left)
            last = bisect.bisect_left(positions, right)
            between = column_touches[first:last]
            if len(between) == 1 and between[0][1] == "scalar":
                edges.add((column, position))
    return edges, sizes


def greedy_matching(edges: set[tuple[int, int]], sizes: dict[int, int]) -> set[tuple[int, int]]:
    chosen = set()
    for column in sorted(sizes):
        last_used_vertex = -1
        for position in sorted(p for c, p in edges if c == column):
            if position > last_used_vertex:
                chosen.add((column, position))
                last_used_vertex = position + 1
    return chosen


def dynamic_matching_size(edges: set[tuple[int, int]], sizes: dict[int, int]) -> int:
    total = 0
    for column, nodes in sizes.items():
        edge_positions = {p for c, p in edges if c == column}
        dp = [0] * (nodes + 1)
        for prefix in range(1, nodes + 1):
            dp[prefix] = dp[prefix - 1]
            position = prefix - 2
            if position >= 0 and position in edge_positions:
                dp[prefix] = max(dp[prefix], dp[prefix - 2] + 1)
        total += dp[nodes]
    return total


def profile_after_fusions(count: int) -> dict[int, int]:
    require(0 <= count <= sum(BASE_PROFILE.values()) // 2, "invalid fusion count")
    profile = dict(BASE_PROFILE)
    profile[1] -= 2 * count
    profile[2] += count
    return {rank: n for rank, n in profile.items() if n}


def main() -> None:
    selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
    require(sha256(selected_bytes) == SELECTED_SHA256, "selected-record hash mismatch")
    selected = json.loads(selected_bytes)
    require(selected.get("kappa") == "836330098538459/500000000000000000",
            "selected result value changed")

    program = source_program()
    forward_edges, forward_sizes = candidate_edges(program["forward"])
    backward_edges, backward_sizes = candidate_edges(program["backward"])
    require(len(forward_edges) == 690, "forward one-touch candidate count changed")
    require(len(backward_edges) == 690, "backward one-touch candidate count changed")
    require(forward_edges == backward_edges, "forward/backward candidate sets differ")
    require(forward_sizes == backward_sizes, "forward/backward climb-path sizes differ")

    chosen = greedy_matching(forward_edges, forward_sizes)
    greedy_count = len(chosen)
    dp_count = dynamic_matching_size(forward_edges, forward_sizes)
    require(greedy_count == dp_count == 674, "maximum disjoint fusion count changed")

    # A path with consecutive eligible edges must not count an overlapping climb twice.
    synthetic_edges = {(7, 0), (7, 1), (7, 2)}
    synthetic_sizes = {7: 4}
    require(len(greedy_matching(synthetic_edges, synthetic_sizes)) == 2,
            "synthetic greedy matching control failed")
    require(dynamic_matching_size(synthetic_edges, synthetic_sizes) == 2,
            "synthetic DP matching control failed")

    # The source pin must reject changed compressed bytes before parsing them.
    try:
        decode_program(b"changed", MEMBER_SHA256)
    except ValueError:
        pass
    else:
        raise ValueError("source corruption control was accepted")

    ceiling = load_ceiling()
    base_lo, base_hi = ceiling.ceiling(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    require(base_lo == Q(52814190909, 31250000000000), "baseline lower ceiling endpoint changed")
    require(base_hi == Q(1690054109089, 10**15), "baseline upper ceiling endpoint changed")

    profile = profile_after_fusions(greedy_count)
    require(profile == {1: 1064, 2: 1092, 3: 432, 4: 142, 5: 82, 8: 8},
            "optimistic fused profile changed")
    require(sum(rank * count for rank, count in profile.items()) == 5586,
            "fusion profile must preserve local rank mass")
    model = ceiling.model(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE)
    require(model["idle_mass"] == 1646, "incumbent idle mass changed")
    require(model["R"] == 51, "incumbent idle rank cap changed")

    fused_lo, fused_hi = ceiling.ceiling(profile, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    require(fused_lo == Q(1768911117731, 10**15), "optimistic lower ceiling endpoint changed")
    require(fused_hi == Q(442227779433, 250_000_000_000_000),
            "optimistic upper ceiling endpoint changed")
    target = base_hi * Q(21, 20)
    require(target == Q(35491136290869, 20_000_000_000_000_000), "5% target changed")
    target_value = ceiling.relax(profile, M, FAMILIES, STAGES, CENTRE, target)
    require(target_value[0] > 1, "674 fusions unexpectedly meet the 5% target")
    require(fused_hi < target, "fused ceiling unexpectedly meets the 5% target")

    # Find the exact zero-overhead fusion threshold and check both adjacent cases.
    def passes(count: int) -> bool:
        return ceiling.relax(profile_after_fusions(count), M, FAMILIES, STAGES, CENTRE, target)[1] < 1

    low, high = 0, sum(BASE_PROFILE.values()) // 2
    while low < high:
        middle = (low + high) // 2
        if passes(middle):
            high = middle
        else:
            low = middle + 1
    require(low == 720, "zero-overhead threshold changed")
    require(ceiling.relax(profile_after_fusions(719), M, FAMILIES, STAGES, CENTRE, target)[0] > 1,
            "719-fusion failure control did not fail")
    require(passes(720), "720-fusion positive boundary control did not pass")

    gain_upper = fused_hi / base_lo - 1
    require(gain_upper < Q(46660, 1_000_000), "reported 4.6660% upper gain is not certified")
    print(
        "PASS_ONE_TOUCH_RANK2_RETIMING_SCREEN "
        f"candidates={len(forward_edges)} matched={greedy_count} "
        f"a_gain_pct<{float(gain_upper * 100):.6f} target_min={low}"
    )


if __name__ == "__main__":
    main()

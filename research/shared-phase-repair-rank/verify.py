#!/usr/bin/env python3
"""Exact rank and cost check for shared repairs of independent phase defects."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
PROOF_PATH = PACKAGE / "vendor/PR3220-PROOF.md"
PROOF_SHA256 = "dc796d5ef8adb5eb44ff953023b62efe74b3f41bd4eb411230e8c1611a097aac"
SCALE = 1_000_000
RANK_CAP = 51


def floor_scaled_power(rank: int) -> int:
    """Exact floor(SCALE * rank**(399/400)) using integer powers only."""
    target = SCALE**400 * rank**399
    lo, hi = 0, SCALE * rank + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**400 <= target:
            lo = mid
        else:
            hi = mid
    return lo


def exact_packing_optimum() -> tuple[int, list[int]]:
    """Independently solve the CP-SAT rank-count domain by exact DP."""
    # CP-SAT has one count variable per rank 1..51, each with domain 0..4.
    states: dict[int, tuple[int, list[int]]] = {0: (0, [])}
    for rank in range(1, RANK_CAP + 1):
        unit_cost = floor_scaled_power(rank)
        next_states: dict[int, tuple[int, list[int]]] = {}
        for old_rank, (old_cost, old_counts) in states.items():
            for count in range(5):
                total_rank = old_rank + count * rank
                total_cost = old_cost + count * unit_cost
                candidate = (total_cost, old_counts + [count])
                if (total_rank not in next_states
                        or total_cost < next_states[total_rank][0]):
                    next_states[total_rank] = candidate
        states = next_states
    best_rank, (best_cost, best_counts) = min(
        ((rank, item) for rank, item in states.items() if rank >= 4),
        key=lambda entry: entry[1][0],
    )
    partition = [rank for rank, count in enumerate(best_counts, start=1)
                 for _ in range(count)]
    assert sum(partition) == best_rank
    return best_cost, partition


def multiply(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    a, b = x
    c, d = y
    return a * c - b * d, a * d + b * c


def subtract(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] - y[0], x[1] - y[1]


def main() -> None:
    proof = PROOF_PATH.read_bytes()
    actual_sha256 = hashlib.sha256(proof).hexdigest()
    assert actual_sha256 == PROOF_SHA256, actual_sha256
    source = proof.decode("utf-8")
    for line in (
        "from it at exactly\n",
        "Delta[1,1] = -1-i,",
        "Delta[3,1] = -1-i,",
        "Delta[7,7] =  1-i.",
        "nonzero columns are 1 and 7.",
        "The submatrix on rows and columns `{1,7}` has determinant `-2`",
    ):
        assert line in source, line

    # Exact sparse 8x8 defect over Z[i]. The only nonzero columns are 1 and 7.
    delta = [[(0, 0) for _ in range(8)] for _ in range(8)]
    delta[1][1] = (-1, -1)
    delta[3][1] = (-1, -1)
    delta[7][7] = (1, -1)
    nonzero_columns = {j for j in range(8) if any(delta[i][j] != (0, 0) for i in range(8))}
    assert nonzero_columns == {1, 7}
    # The {1,7} principal minor is (-1-i)(1-i) = -2, so rank is at least 2.
    minor = subtract(multiply(delta[1][1], delta[7][7]), multiply(delta[1][7], delta[7][1]))
    assert minor == (-2, 0), minor
    defect_rank = 2

    # B(a) <= 20*a*51/e. On a <= 1/400 and e > 8/3,
    # B(a) < 51/(20*(8/3)) = 153/160.
    assert 51 * 3 * 160 == 153 * 20 * 8
    allowance_numerator, allowance_denominator = 153, 160
    assert allowance_numerator < allowance_denominator

    # For each repair child q <= 51 and 0 <= a <= 1/400:
    # q^(1-a) >= q*51^(-a) >= q*51^(-1/400) > q/2,
    # since 51 < 2^400. Total inserted rank is at least rank(Delta).
    rank_cap = 51
    assert rank_cap < 2**400

    # Check the CP-SAT lower-rounded receipt without importing OR-Tools.
    result = json.loads((PACKAGE / "ORTOOLS-RESULT.json").read_text())
    assert result["status"] == "OPTIMAL_TWO_GROUP_RELAXATION"
    assert result["groups"] == 2
    assert result["required_total_repair_rank"] == defect_rank * result["groups"] == 4
    assert result["rank_cap"] == rank_cap
    assert result["optimal_rank_partition"] == {"4": 1}
    assert result["total_rank_below_four_control"] == "INFEASIBLE"
    lower_cost_scaled = result["rounded_lower_cost_scaled"]
    objective_scale = result["objective_scale"]
    exact_optimum, exact_partition = exact_packing_optimum()
    assert lower_cost_scaled == exact_optimum == 3_986_161
    assert exact_partition == [4]
    assert objective_scale == SCALE
    assert lower_cost_scaled * allowance_denominator > (
        objective_scale * allowance_numerator * result["groups"]
    )

    # General G-copy conclusion: correction cost > G; allowance < 153G/160.
    assert allowance_denominator - allowance_numerator == 7
    print(
        "PASS_SHARED_PHASE_REPAIR_RANK_BOUND "
        f"source_rank={defect_rank} two_group_rank>=4 "
        f"exact_packing_floor={lower_cost_scaled}/{objective_scale} "
        "general_repair_cost_per_group>1 allowance_per_group<153/160"
    )


if __name__ == "__main__":
    main()

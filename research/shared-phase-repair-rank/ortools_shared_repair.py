#!/usr/bin/env python3
"""OR-Tools lower-cost screen for shared repair rank across two groups.

This deliberately grants any rank partition the ability to repair both
independent defects. Exact coefficient floors make the CP-SAT objective a lower
bound on the actual raw cost at a = 1/400.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model
import ortools

PACKAGE = Path(__file__).resolve().parent
SCALE = 1_000_000
GROUPS = 2
REQUIRED_RANK = 4
RANK_CAP = 51


def floor_scaled_power(rank: int) -> int:
    """Return floor(SCALE * rank^(399/400)) by exact integer comparisons."""
    target = SCALE**400 * rank**399
    lo, hi = 0, SCALE * rank + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**400 <= target:
            lo = mid
        else:
            hi = mid
    return lo


def solve() -> dict:
    model = cp_model.CpModel()
    count = {r: model.NewIntVar(0, REQUIRED_RANK, f"num_rank_{r}")
             for r in range(1, RANK_CAP + 1)}
    total_rank = sum(r * count[r] for r in count)
    lower_cost = sum(floor_scaled_power(r) * count[r] for r in count)
    model.Add(total_rank >= REQUIRED_RANK)
    model.Minimize(lower_cost)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        raise RuntimeError(f"two-group screen did not optimize: {solver.StatusName(status)}")
    partition = {str(r): solver.Value(count[r]) for r in count if solver.Value(count[r])}

    control = cp_model.CpModel()
    control_count = {r: control.NewIntVar(0, REQUIRED_RANK, f"control_num_rank_{r}")
                     for r in range(1, RANK_CAP + 1)}
    control.Add(sum(r * control_count[r] for r in control_count) >= REQUIRED_RANK)
    control.Add(sum(r * control_count[r] for r in control_count) <= REQUIRED_RANK - 1)
    control_solver = cp_model.CpSolver()
    control_solver.parameters.num_search_workers = 1
    control_solver.parameters.random_seed = 0
    control_status = control_solver.Solve(control)

    objective_value = solver.Value(lower_cost)
    return {
        "status": "OPTIMAL_TWO_GROUP_RELAXATION",
        "solver": "OR-Tools CP-SAT",
        "ortools_version": ortools.__version__,
        "python": sys.version.split()[0],
        "scope": "two independent direct-sum copies of PR3220's rank-two defect; arbitrary repair-rank partition; rank cap 51; exact correctability and routing granted for free",
        "groups": GROUPS,
        "rank_per_group": 2,
        "required_total_repair_rank": REQUIRED_RANK,
        "rank_cap": RANK_CAP,
        "a_endpoint": "1/400",
        "objective_scale": SCALE,
        "objective_coefficients": "floor(1000000 * r^(399/400)), certified by integer-power comparisons",
        "optimal_rank_partition": partition,
        "optimal_total_rank": sum(int(r) * n for r, n in partition.items()),
        "rounded_lower_cost_scaled": objective_value,
        "lower_rounded_raw_cost": objective_value / SCALE,
        "max_two_group_allowance": "306/160",
        "total_rank_below_four_control": control_solver.StatusName(control_status),
        "selected_frontier_changed": False,
        "new_kappa": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PACKAGE / "ORTOOLS-RESULT.json")
    args = parser.parse_args()
    result = solve()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in (
        "status", "groups", "required_total_repair_rank", "optimal_rank_partition",
        "lower_rounded_raw_cost", "max_two_group_allowance", "total_rank_below_four_control",
        "ortools_version",
    )} | {"output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()

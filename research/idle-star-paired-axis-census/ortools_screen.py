#!/usr/bin/env python3
"""Exploratory CP-SAT screen for net-rank-changing idle-axis reassignments.

This is a discovery tool, not part of the registered admission verifier. It
uses the latter only to prepare an authenticated port, then lets OR-Tools
optimize assignments of the four rank-48 children while preserving the exact
multiset of residual axes and all within-child orthogonality constraints.
Every nominated assignment is still checked by the exact replay.
"""

from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model
import ortools


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
VERIFY = PACKAGE / "verify.py"
CHILDREN = (8, 10, 12, 13)
CHARACTER_BITS = 73
MAX_CHILD_RANK = 51
SAVING = 0.00167546  # selected-result complex-side scale; ranking surrogate only
SCALE = 10**12
TIME_LIMIT = 45.0


def load_verifier():
    spec = importlib.util.spec_from_file_location("idle_axis_verify", VERIFY)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def prepare(v):
    v.authenticate()
    vendor = PACKAGE / "vendor"
    base = v.decode(v.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    journal = v.decode(v.read_bytes(vendor / "EXCHANGE.json"))
    rows_by_port = v.project_all_ports(base, v.journal_edits(base, journal))
    order_base = v.decode(v.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/ORDER.json"))
    order = [[stage, replica + 74 * copy] for stage, replica in order_base for copy in range(10)]
    dispatch_rows = v.decode(v.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/DISPATCH.json"))
    dispatch = {(stage, replica): tag for stage, replica, tag in dispatch_rows}
    providers = v.decode(v.read_bytes(vendor / "PROVIDERS.json"))
    plan = v.decode(v.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz"))
    template = v.decode(v.read_bytes(ROOT / "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz"))
    recipes = v.decode(v.read_bytes(ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"))["recipes"]
    contexts = [
        v.prepare_port(port, rows_by_port[port], order, dispatch, providers, plan, template, recipes)
        for port in range(len(recipes))
    ]
    return contexts, v.stage_blocks(template)


def optimize(context):
    def dot(left, right):
        return (left & right).bit_count() & 1

    model = cp_model.CpModel()
    tokens = [(source, axis) for source in CHILDREN for axis in context["residual"][source]]
    if len(tokens) != 192:
        raise ValueError(f"expected 192 residual-axis tokens, got {len(tokens)}")

    x = {}
    hosted = {child: context["hosted_axes"].get(child, []) for child in CHILDREN}
    for t, (source, axis) in enumerate(tokens):
        for child in CHILDREN:
            x[t, child] = model.NewBoolVar(f"x_{t}_{child}")
            if any(dot(axis, fixed) for fixed in hosted[child]):
                model.Add(x[t, child] == 0)
        model.AddExactlyOne(x[t, child] for child in CHILDREN)

    # A child's residual set must be an orthonormal basis with its fixed hosted
    # axes. Pairwise forbidden assignments encode this exact GF(2) Gram test.
    conflicts = 0
    for i, (_, left) in enumerate(tokens):
        for j in range(i + 1, len(tokens)):
            right = tokens[j][1]
            if dot(left, right):
                for child in CHILDREN:
                    model.Add(x[i, child] + x[j, child] <= 1)
                    conflicts += 1

    ranks = {}
    for child in CHILDREN:
        hosted_count = len(hosted[child])
        ranks[child] = model.NewIntVar(hosted_count, MAX_CHILD_RANK, f"rank_{child}")
        model.Add(ranks[child] == hosted_count + sum(x[t, child] for t in range(len(tokens))))
    high = model.NewIntVar(0, MAX_CHILD_RANK, "maximum_child_rank")
    model.AddMaxEquality(high, list(ranks.values()))
    model.Add(high >= 49)  # demand a nonzero rank imbalance from 48/48/48/48

    exponent = 1.0 - SAVING
    score_table = [round(SCALE * (rank ** exponent)) for rank in range(MAX_CHILD_RANK + 1)]
    scores = {}
    for child in CHILDREN:
        scores[child] = model.NewIntVar(0, max(score_table), f"score_{child}")
        model.AddElement(ranks[child], score_table, scores[child])
    total_score = model.NewIntVar(0, len(CHILDREN) * max(score_table), "total_rank_moment")
    model.Add(total_score == sum(scores.values()))
    model.Minimize(total_score)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_LIMIT
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    primary_status = solver.Solve(model)
    if primary_status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        status = primary_status
    else:
        best_moment = solver.Value(total_score)
        model.Add(total_score == best_moment)
        moved_count = sum(1 - x[t, source] for t, (source, _) in enumerate(tokens))
        model.Minimize(moved_count)
        secondary_solver = cp_model.CpSolver()
        secondary_solver.parameters.max_time_in_seconds = TIME_LIMIT
        secondary_solver.parameters.num_search_workers = 1
        secondary_solver.parameters.random_seed = 0
        status = secondary_solver.Solve(model)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            solver = secondary_solver
    result = {
        "solver": "OR-Tools CP-SAT",
        "ortools_version": ortools.__version__,
        "python": sys.version.split()[0],
        "status": solver.StatusName(status),
        "wall_seconds": solver.WallTime(),
        "primary_status": solver.StatusName(primary_status),
        "conflict_constraints": conflicts,
        "token_count": len(tokens),
        "hosted_counts": {str(c): len(hosted[c]) for c in CHILDREN},
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result, None

    destinations = [next(c for c in CHILDREN if solver.Value(x[t, c])) for t in range(len(tokens))]
    trial = {child: list(values) for child, values in context["residual"].items()}
    for child in CHILDREN:
        trial[child] = []
    for (source, axis), destination in zip(tokens, destinations):
        trial[destination].append(axis)

    rank_vector = {str(c): len(hosted[c]) + len(trial[c]) for c in CHILDREN}
    moved = [(source, destination, axis) for (source, axis), destination in zip(tokens, destinations) if source != destination]
    result.update({
        "rank_vector": rank_vector,
        "rank_moment_surrogate": solver.Value(total_score),
        "moves": len(moved),
        "moved_tokens": [[s, d, a] for s, d, a in moved],
        "baseline_rank_vector": {str(c): len(hosted[c]) + len(context["residual"][c]) for c in CHILDREN},
    })
    return result, trial


def replay_screen(v, context, blocks, trial):
    baseline = context["residual"]
    moved_axes = sorted({axis for child in CHILDREN for axis in set(baseline[child]) ^ set(trial[child])})
    chars = {1 << bit for bit in range(CHARACTER_BITS)}
    chars.update(moved_axes)
    chars.update(a ^ b for i, a in enumerate(moved_axes) for b in moved_axes[i + 1 :])
    chars.update((1 << bit) | (1 << (bit + 1)) for bit in range(CHARACTER_BITS - 1))
    failures = []
    checked = 0
    for character in sorted(chars):
        checked += 1
        before = v.replay(context, baseline, character, blocks)
        after = v.replay(context, trial, character, blocks)
        if before != after:
            failures.append({"character": character, "differences": v.matrix_differences(before, after)})
            break
    return {"characters_tested_before_first_mismatch": checked, "candidate_character_set_size": len(chars), "failures_seen": len(failures), "first_failures": failures}


def main():
    v = load_verifier()
    contexts, blocks = prepare(v)
    summaries = []
    representative_witnesses = {}
    for port, context in enumerate(contexts):
        result, trial = optimize(context)
        if trial is not None:
            result["exact_replay_screen"] = replay_screen(v, context, blocks, trial)
        moved_tokens = result.pop("moved_tokens", [])
        assignment_digest = hashlib.sha256(
            json.dumps(moved_tokens, separators=(",", ":")).encode("ascii")
        ).hexdigest()
        screen = result.pop("exact_replay_screen", None)
        first_mismatch = screen["first_failures"][0] if screen and screen["first_failures"] else None
        if first_mismatch is not None:
            character_key = str(first_mismatch["character"])
            if character_key not in representative_witnesses:
                representative_witnesses[character_key] = {
                    "port": port,
                    "character": first_mismatch["character"],
                    "moved_tokens": moved_tokens,
                    "differences": first_mismatch["differences"],
                }
        diff_bytes = json.dumps(first_mismatch["differences"], separators=(",", ":")).encode("ascii") if first_mismatch else b"[]"
        summary = {
            "port": port,
            "status": result["status"],
            "primary_status": result.get("primary_status"),
            "wall_seconds": result["wall_seconds"],
            "conflict_constraints": result["conflict_constraints"],
            "baseline_rank_vector": result.get("baseline_rank_vector"),
            "rank_vector": result.get("rank_vector"),
            "rank_moment_surrogate": result.get("rank_moment_surrogate"),
            "moves": result.get("moves"),
            "assignment_sha256": assignment_digest,
            "screen": {
                "candidate_character_set_size": screen["candidate_character_set_size"],
                "characters_tested_before_first_mismatch": screen["characters_tested_before_first_mismatch"],
                "first_mismatch_character": first_mismatch["character"] if first_mismatch else None,
                "matrix_difference_count": len(first_mismatch["differences"]) if first_mismatch else 0,
                "matrix_difference_sha256": hashlib.sha256(diff_bytes).hexdigest(),
            } if screen else None,
        }
        summaries.append(summary)
    p = 1.0 - SAVING
    baseline_moment = 4 * (48 ** p)
    optimum_moment = 3 * (51 ** p) + (39 ** p)
    aggregate = {
        "base_main": v.BASE_MAIN,
        "fill_payload_sha256": v.FILL_SHA256,
        "solver_environment": {"ortools": ortools.__version__, "python": sys.version.split()[0]},
        "model": {
            "children": list(CHILDREN),
            "tokens_per_port": 192,
            "rank_cap": MAX_CHILD_RANK,
            "objective": "minimize sum(rank ** (1 - saving))",
            "saving_scale": SAVING,
            "objective_scale": SCALE,
            "lexicographic_tiebreak": "minimum number of moved residual-axis tokens",
            "time_limit_seconds_per_stage": TIME_LIMIT,
            "threads": 1,
            "seed": 0,
        },
        "scope": "one CP-SAT optimum with minimum move count per port; exact replay screens the listed Fourier characters and stops at the first mismatch",
        "ports": len(summaries),
        "all_models_optimal": all(row["status"] == "OPTIMAL" for row in summaries),
        "rank_imbalances_found": sum(row["status"] in ("OPTIMAL", "FEASIBLE") for row in summaries),
        "screen_survivors": [row["port"] for row in summaries if row.get("screen") is None or row["screen"]["first_mismatch_character"] is None],
        "rank_moment_comparison_per_port": {
            "baseline_profile": [48, 48, 48, 48],
            "candidate_profile": [51, 51, 51, 39],
            "baseline_unscaled_moment": baseline_moment,
            "candidate_unscaled_moment": optimum_moment,
            "candidate_minus_baseline": optimum_moment - baseline_moment,
            "relative_change": optimum_moment / baseline_moment - 1.0,
            "note": "ranking surrogate only; the source-bound physical operator rejects every nominated assignment, so this is not a κ improvement",
        },
        "representative_witnesses_by_character": [representative_witnesses[key] for key in sorted(representative_witnesses, key=int)],
        "results": summaries,
    }
    print(json.dumps(aggregate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

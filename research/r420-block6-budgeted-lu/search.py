#!/usr/bin/env python3
"""Search a fixed R420 block-6 LU sample and rebuild the complete word.

The sampler is the pinned upstream randomized pivoted-LU construction. Unlike
its baseline selector, this replay retains candidates on the gate-count / exact
positive-norm Pareto frontier. It makes no claim about circuits outside the
sampled LU class.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD_PATH = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
PLAN_PATH = ROOT / "research/e8-bit-r420/data/plan-l3.json"
EXPECTED_PATH = ROOT / "research/e8-bit-r420/EXPECTED.json"
BLOCK_INDEX = 6
FRAME = 548
START = 417
STOP = 471
BASELINE_TRIALS = 2_000
SEARCH_TRIALS = 20_000

os.environ["NODEOPT"] = str(BASELINE_TRIALS)
sys.path[:0] = [
    str(ROOT / "research/e8-bit-r420/code"),
    str(ROOT / "research/e8-bit-carrier-skeleton/code/skeleton"),
]

import gen_l3  # noqa: E402
import nodeopt  # noqa: E402
from gen_l3 import Geom  # noqa: E402
from planio import load_plan  # noqa: E402


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pareto_realise(rows: list[int], rng: random.Random, trials: int, norm_cap: int):
    """Return the best sampled realization with fewer gates and no larger norm.

    This follows the upstream candidate generator exactly: shuffled wire order,
    randomized row pivots, then an LU factorization. The changed selector keeps
    the least gate count among candidates whose full literal-reverse norm does
    not exceed the baseline incumbent. Ties use the smaller norm and then the
    first occurrence in the fixed stream.
    """
    n = len(rows)
    best = None
    valid = 0
    frontier: dict[tuple[int, int], tuple[list[tuple[int, int]], list[int]]] = {}
    for _ in range(trials):
        order = list(range(n))
        rng.shuffle(order)
        perm = nodeopt.pivot_perm(rows, order, rng)
        if perm is None:
            continue
        output_rows = [0] * n
        for k in range(n):
            output_rows[perm[k]] = rows[k]
        relabeled = []
        for i in range(n):
            wire = order[i]
            value = output_rows[wire]
            reordered = 0
            for j in range(n):
                if value >> order[j] & 1:
                    reordered |= 1 << j
            relabeled.append(reordered)
        ops = nodeopt.lu_ops(relabeled, n)
        if ops is None:
            continue
        ops = [(order[a], order[b]) for a, b in ops]
        valid += 1
        gate_count = len(ops)
        positive_norm = nodeopt.cost(ops, n)
        key = (gate_count, positive_norm)
        frontier.setdefault(key, (ops, perm))
        if positive_norm <= norm_cap:
            score = (gate_count, positive_norm)
            if best is None or score < best[0]:
                current = nodeopt.apply(ops, n)
                if not all(current[perm[k]] == rows[k] for k in range(n)):
                    raise RuntimeError("sampled LU candidate misses a target row")
                best = (score, ops, perm)
    if best is None:
        raise RuntimeError("the fixed sample contains no candidate within the baseline norm cap")
    nondominated = sorted(
        pair for pair in frontier
        if not any(
            other != pair and other[0] <= pair[0] and other[1] <= pair[1]
            for other in frontier
        )
    )
    score, ops, perm = best
    return {
        "score": score,
        "operations": ops,
        "output_to_wire": perm,
        "valid_samples": valid,
        "nondominated_pairs": [list(pair) for pair in nondominated],
        "unique_pairs": len(frontier),
    }


def run_variant(candidate_trials: int | None = None, norm_cap: int | None = None):
    original_realise = gen_l3.realise
    calls = 0
    trace: dict[str, object] = {}

    def counted_realise(rows, rng, tries=3_000):
        nonlocal calls
        block = calls % 10
        calls += 1
        if block != BLOCK_INDEX or candidate_trials is None:
            result = original_realise(rows, rng, tries=tries)
        else:
            selected = pareto_realise(rows, rng, candidate_trials, int(norm_cap))
            result = (selected["score"][1], selected["operations"], selected["output_to_wire"])
            trace.update({
                "valid_samples": selected["valid_samples"],
                "unique_score_pairs": selected["unique_pairs"],
                "nondominated_pairs": selected["nondominated_pairs"],
            })
        if block == BLOCK_INDEX:
            cost, ops, output_to_wire = result
            trace.update({
                "target_rows": list(rows),
                "operations_local": [list(op) for op in ops],
                "output_to_wire": list(output_to_wire),
                "positive_cost": cost,
                "trials": candidate_trials if candidate_trials is not None else tries,
            })
        return result

    gen_l3.realise = counted_realise
    try:
        geom = Geom()
        plan = load_plan(str(PLAN_PATH))
        result, outer_retries = gen_l3.search(
            geom, plan, seed=0, fresh=False, host_order="last", node_seed=None
        )
    finally:
        gen_l3.realise = original_realise
    if result[0] in ("rank", "deficient"):
        raise RuntimeError(f"upstream frame plan failed: {result}")
    if calls != 10 or outer_retries != 0:
        raise RuntimeError(f"unexpected upstream search coverage: calls={calls}, retries={outer_retries}")
    return geom, plan, result[1], trace


def layout(geom, plan):
    freeline, _ = gen_l3.plan_thirds(geom, plan, random.Random(0))
    _, keepline, home, _, _ = gen_l3.derive(geom, plan, freeline)
    dualcells = set(home.values())
    branch: dict[tuple[int, tuple[int, ...]], int] = {}
    next_helper = 2 * gen_l3.V
    for source in range(gen_l3.V):
        for cell in geom.cells_of[source]:
            if cell == home[source]:
                branch[(source, cell)] = source
            else:
                branch[(source, cell)] = next_helper
                next_helper += 1
    keeper = {cell: branch[(keepline[cell], cell)] for cell in geom.cells}
    wires = [
        keeper[cell]
        for cell in geom.cells
        if cell in dualcells and geom.cblk[cell] == BLOCK_INDEX
    ]
    complement = geom.comp[BLOCK_INDEX]
    targets = [target for target in range(gen_l3.V) if geom.blk[target] == complement]
    if len(wires) != 12 or len(targets) != 12:
        raise RuntimeError("unexpected block-6 geometry")
    return wires, targets


def generate() -> tuple[dict, dict]:
    _, base_plan, baseline_word, base_trace = run_variant()
    candidate_geom, candidate_plan, candidate_word, candidate_trace = run_variant(
        SEARCH_TRIALS, int(base_trace["positive_cost"])
    )
    if base_plan != candidate_plan:
        raise RuntimeError("baseline and candidate plans differ")
    expected_base_hash = json.loads(EXPECTED_PATH.read_text())["word"]["content_sha256"]
    baseline_hash = sha256(canonical(baseline_word))
    if baseline_hash != expected_base_hash:
        raise RuntimeError(f"baseline does not reproduce pinned R420 word: {baseline_hash}")
    wires, targets = layout(candidate_geom, candidate_plan)
    physical_ops = [[FRAME, wires[a], [wires[b]]] for a, b in candidate_trace["operations_local"]]
    if not all(gate[0] == FRAME for gate in baseline_word["B"][START:STOP]):
        raise RuntimeError("pinned block-6 slice is not at frame 548")
    if candidate_word["B"][START:START + len(physical_ops)] != physical_ops:
        raise RuntimeError("candidate block-6 circuit does not match regenerated word")
    if not all(gate[0] == FRAME for gate in candidate_word["B"][START:START + len(physical_ops)]):
        raise RuntimeError("candidate block-6 slice is not at frame 548")
    if candidate_word["scatter"] != baseline_word["scatter"]:
        raise RuntimeError("the scatter ADD schedule changed")
    if candidate_word["D"] != baseline_word["D"] or candidate_word["A"] != baseline_word["A"]:
        raise RuntimeError("the D or A phase changed")
    if len(baseline_word["B"][START:STOP]) != 54:
        raise RuntimeError("unexpected block-6 baseline circuit length")
    if len(physical_ops) >= 54:
        raise RuntimeError("the fixed Pareto selector did not improve the gate count")
    if candidate_trace["target_rows"] != base_trace["target_rows"]:
        raise RuntimeError("the target transfer matrix changed")
    if int(candidate_trace["positive_cost"]) > int(base_trace["positive_cost"]):
        raise RuntimeError("the selected candidate exceeds the baseline positive norm")
    if int(candidate_trace["trials"]) != SEARCH_TRIALS:
        raise RuntimeError("the fixed block-6 search budget was not used")

    certificate = {
        "schema": "r420-block6-budgeted-lu-search/1",
        "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "assignment_seed": 6,
        "track": "bit supplier",
        "object": {
            "block_index": BLOCK_INDEX,
            "frame": FRAME,
            "baseline_B_interval": [START, STOP],
            "baseline_operations": STOP - START,
            "candidate_operations": len(physical_ops),
            "input_wires": wires,
            "target_order": targets,
            "positive_integer_ADDs_saved_including_cleanup": 2 * (STOP - START - len(physical_ops)),
        },
        "search": {
            "method": "upstream randomized pivoted-LU sample, selected by (gate count, cancellation-free positive norm)",
            "upstream_rng_seed": 7 * BLOCK_INDEX,
            "baseline_trials_per_block": BASELINE_TRIALS,
            "block6_trials": SEARCH_TRIALS,
            "valid_candidates": candidate_trace["valid_samples"],
            "unique_score_pairs": candidate_trace["unique_score_pairs"],
            "nondominated_pairs": candidate_trace["nondominated_pairs"],
            "positive_norm_cap": base_trace["positive_cost"],
            "other_blocks": "unchanged 2,000-trial generator budgets",
            "outer_plan_seed": 0,
            "outer_plan_retries": 0,
            "stopping_rule": "finish exactly 20,000 block-6 LU samples",
            "coverage_limit": "sampled optimizer class only; no optimality claim",
        },
        "baseline": {
            "canonical_word_sha256": baseline_hash,
            "target_rows": base_trace["target_rows"],
            "operations_local": base_trace["operations_local"],
            "output_to_wire": base_trace["output_to_wire"],
            "positive_cost": base_trace["positive_cost"],
        },
        "candidate": {
            "canonical_word_sha256": sha256(canonical(candidate_word)),
            **candidate_trace,
        },
    }
    return candidate_word, certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new output directory; it must not exist")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing path: {args.output}")
    word, certificate = generate()
    args.output.mkdir(parents=True)
    (args.output / "candidate-word.json.gz").write_bytes(gzip.compress(canonical(word), mtime=0))
    (args.output / "search-certificate.json").write_text(json.dumps(certificate, indent=2) + "\n")
    print("PASS_R420_BLOCK6_PARETO_LU_SEARCH", certificate["object"]["baseline_operations"], "->",
          certificate["object"]["candidate_operations"])
    print("CANDIDATE_SHA256", certificate["candidate"]["canonical_word_sha256"])


if __name__ == "__main__":
    main()

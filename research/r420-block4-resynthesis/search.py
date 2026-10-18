#!/usr/bin/env python3
"""Reproduce the fixed-budget R420 block-4 randomized-LU search.

The upstream generator and node optimizer are pinned in SOURCES.json.  The
assignment seed chooses block 4; its optimizer seed follows the generator's
existing rule, 7 * block_index = 28.  Only block 4 receives 20,000 samples;
all other blocks use the published 2,000-sample baseline.
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

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD_PATH = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
PLAN_PATH = ROOT / "research/e8-bit-r420/data/plan-l3.json"
EXPECTED_PATH = ROOT / "research/e8-bit-r420/EXPECTED.json"
BLOCK_INDEX = 4
FRAME = 546
START = 313
STOP = 371
BASELINE_TRIALS = 2_000
BLOCK4_TRIALS = 20_000

os.environ["NODEOPT"] = str(BASELINE_TRIALS)
sys.path[:0] = [
    str(ROOT / "research/e8-bit-r420/code"),
    str(ROOT / "research/e8-bit-carrier-skeleton/code/skeleton"),
]

import gen_l3  # noqa: E402
from gen_l3 import Geom  # noqa: E402
from planio import load_plan  # noqa: E402


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_variant(extra_trials: int):
    original_realise = gen_l3.realise
    calls = 0
    trace: dict[str, object] = {}

    def counted_realise(rows, rng, tries=3_000):
        nonlocal calls
        block = calls % 10
        calls += 1
        budget = extra_trials if block == BLOCK_INDEX else tries
        result = original_realise(rows, rng, tries=budget)
        if block == BLOCK_INDEX:
            cost, ops, output_to_wire = result
            trace.update({
                "target_rows": list(rows),
                "operations_local": [list(op) for op in ops],
                "output_to_wire": list(output_to_wire),
                "positive_cost": cost,
                "trials": budget,
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
        raise RuntimeError("unexpected block-4 geometry")
    return wires, targets


def generate() -> tuple[dict, dict]:
    base_geom, base_plan, baseline, base_trace = run_variant(BASELINE_TRIALS)
    candidate_geom, candidate_plan, candidate, candidate_trace = run_variant(BLOCK4_TRIALS)
    if base_plan != candidate_plan or len(base_geom.blocks) != len(candidate_geom.blocks):
        raise RuntimeError("baseline and candidate plans differ")
    baseline_word, candidate_word = baseline, candidate
    expected_base_hash = json.loads(EXPECTED_PATH.read_text())["word"]["content_sha256"]
    baseline_hash = sha256(canonical(baseline_word))
    if baseline_hash != expected_base_hash:
        raise RuntimeError(f"baseline does not reproduce pinned R420 word: {baseline_hash}")
    wires, targets = layout(candidate_geom, candidate_plan)
    physical_ops = [
        [FRAME, wires[a], [wires[b]]]
        for a, b in candidate_trace["operations_local"]
    ]
    if candidate_word["B"][START:START + len(physical_ops)] != physical_ops:
        raise RuntimeError("block-4 physical circuit does not match the generator output")
    if not all(gate[0] == FRAME for gate in baseline_word["B"][START:STOP]):
        raise RuntimeError("pinned block-4 slice is not at frame 546")
    if not all(gate[0] == FRAME for gate in candidate_word["B"][START:START + len(physical_ops)]):
        raise RuntimeError("candidate block-4 slice is not at frame 546")
    if candidate_word["B"][START + len(physical_ops):] == baseline_word["B"][STOP:]:
        raise RuntimeError("expected block-4 output reassignment was not propagated downstream")
    if len(baseline_word["B"][START:STOP]) != 58 or len(physical_ops) != 51:
        raise RuntimeError("unexpected block-4 circuit lengths")
    if candidate_trace["target_rows"] != base_trace["target_rows"]:
        raise RuntimeError("the target transfer matrix changed")
    if int(candidate_trace["trials"]) != BLOCK4_TRIALS:
        raise RuntimeError("the fixed block-4 search budget was not used")

    certificate = {
        "schema": "r420-block4-resynthesis-search/1",
        "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "assignment_seed": 4,
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
            "method": "upstream randomized pivoted LU synthesis; retain the minimum cancellation-free cost",
            "upstream_rng_seed": 7 * BLOCK_INDEX,
            "baseline_trials_per_block": BASELINE_TRIALS,
            "block4_trials": BLOCK4_TRIALS,
            "other_blocks": "unchanged 2,000-trial generator budgets",
            "outer_plan_seed": 0,
            "outer_plan_retries": 0,
            "stopping_rule": "finish exactly 20,000 block-4 LU samples",
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
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    word, certificate = generate()
    payload = canonical(word) + b"\n"
    (out / "candidate-word.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    (out / "search-certificate.json").write_text(json.dumps(certificate, indent=2) + "\n")
    print("PASS_R420_BLOCK4_SEARCH baseline=58 candidate=51 trials=20000 seed=28 saved_adds=14")
    print("CANDIDATE_SHA256", certificate["candidate"]["canonical_word_sha256"])


if __name__ == "__main__":
    main()

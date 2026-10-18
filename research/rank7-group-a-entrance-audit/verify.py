# SPDX-License-Identifier: Apache-2.0
"""Mixed-entrance group A native boundary, control and completed invoice."""

import json
import sys
import tempfile
from pathlib import Path

import invoice
import native
from common import HELPERS, PACKAGE, authenticate, data, decode, module, require

FRAMES = "research/rank7-joint-frame-audit/frames.py"
LOWERING = "research/rank7-joint-frame-audit/lowering.py"
ENDPOINTS = "research/rank7-v45-native-endpoint/endpoints.py"
PRIOR = "research/rank7-v45-native-cone-seed78/RESULT-"


def local_comparison(blobs):
    """Explicit reuse of Nick Petalas's independent PR2993 frame checker."""
    frames = module(blobs[FRAMES], "frames")
    lower = module(blobs[LOWERING], "group_a_retained_lowering")
    edits = data(blobs, "data/STAGE1-FRAME-EDITS.json")
    prices = data(blobs, "construction/STAGE-PRICES.json")
    weights = {int(r): n for r, n in prices["weights"]["c"].items()}
    guide = prices["weights"]["break_even"]
    result, final_profiles = {}, {}
    for tag in ("base", "extra"):
        parent, final = (data(blobs, f"data/{kind}-{tag}.json.gz") for kind in ("PARENT", "WORD"))
        baseline = frames.ledger(parent)
        variants = {"parent": parent, "joint": lower.apply_frames(parent, edits, ["A"]),
                    "single331": lower.apply_frames(parent, edits, ["A"], endpoints=[331])}
        rows = {}
        for name, word in variants.items():
            record = frames.ledger(word, check_report=(name == "parent"))
            delta = lower.difference(record["profile"], baseline["profile"])
            count = {"parent": 0, "joint": 5, "single331": 1}[name]
            price = sum(weights[r] * n for r, n in delta.items())
            rows[name] = {"profile": record["profile"], "delta": delta,
                          "width_inventory": record["widths"], "surrogate_price": price,
                          "guide_margin": -price - count * guide,
                          "cleanup": frames.cleanup_namespace(word)}
        require(rows["joint"]["delta"] == {1: -1, 2: 20, 3: -14, 4: 2, 5: -2}, "joint group delta")
        require(rows["single331"]["delta"] == {1: 3, 2: 20, 3: -14, 4: 2, 5: -2}, "single control delta")
        require(rows["joint"]["guide_margin"] == 42541 and rows["single331"]["guide_margin"] == -58943,
                "source surrogate comparison")
        final_profiles[tag] = frames.ledger(final)["profile"]
        rows["final_cleanup"] = frames.cleanup_namespace(final)
        result[tag] = rows
    return result, final_profiles


def endpoints(blobs, words):
    """Apply the credited generic reverse-covector engine to these ten outputs."""
    engine = module(blobs[ENDPOINTS], "group_a_retained_covectors")
    result = {}
    for tag, word in words.items():
        gates = engine.program(word)
        live = set(range(704)) - set(word["removed"])
        buffers = {704 + int(h) for h in word["helper_final"]}
        rows = {}
        for dual in (False, True):
            for h in HELPERS:
                for output in (h, h + 704):
                    row = engine.endpoint(gates, output, dual, live, buffers)
                    require(row == [(output, (), "1")], "normalized group/private identity")
                    rows[f'{"dual" if dual else "forward"}:{output}'] = row
        result[tag] = {"gates": len(gates), "original_inputs": len(live), "private_inputs": len(buffers),
                       "identity_rows": rows, "method": "retained PR3006 reverse-covector engine"}
    return result


def prior_coverage(blobs, native_results):
    """Inventory reported PR3038 coverage; do not call it a fresh replay."""
    result = {}
    for tag, current in native_results.items():
        prior = decode(blobs[PRIOR + tag + ".json"])
        require(prior["scientific_head"] == "be191346391661f4d35fc0d1508d0a6029572576"
                and prior["provider"] == tag, "PR3038 coverage source")
        rows = {}
        for orientation, previous in prior["orientations"].items():
            covered = set(previous["event_indices"])
            classes = [a["class"] for a in previous["native"]["associations"]]
            helpers = {}
            for h, binding in current["bindings"].items():
                row = binding[orientation]
                e, u = map(int, row["recipe_key"].split(":"))
                selected = set(row["direct_scalar_indices"])
                selected.update(c["index"] for c in row["climbs"])
                selected.update(i for i, _ in row["wrappers"] + row["buffers"])
                helpers[h] = {
                    "residual_class_in_prior_cone": ["wrapper", e, u] in classes,
                    "post_wrapper_in_prior_cone": row["wrappers"][1][0] in covered,
                    "direct_events": len(selected),
                    "direct_events_outside_prior_cone": sorted(selected - covered)}
            rows[orientation] = helpers
        result[tag] = rows
    return {"status": "Pinned PR3038 receipts inspected; full PR3038 audit not rerun",
            "providers": result}


def compute():
    blobs = authenticate()
    local, profiles = local_comparison(blobs)
    words = {tag: data(blobs, f"data/WORD-{tag}.json.gz") for tag in ("base", "extra")}
    native_results = {}
    for tag in words:
        with tempfile.TemporaryDirectory(prefix="group-a-native-") as work:
            native_results[tag] = native.audit(blobs, tag, Path(work))
    result = {"schema_version": 1, "status": "PASS_GROUP_A_ENTRANCE_NATIVE_INVOICE",
              "local_comparison": local, "native": native_results,
              "normalized_endpoints": endpoints(blobs, words),
              "invoice": invoice.audit(blobs, words, profiles)}
    names, widths = invoice.widths(words["base"])
    joins = {}
    for tag, record in native_results.items():
        joins[tag] = {}
        for h in HELPERS:
            binding = record["bindings"][str(h)]["forward"]
            key = binding["recipe_key"]
            rank = record["residuals"][key]["rank"]
            require(rank == widths[names.index(h)] and
                    binding["compact_helper"] == 224 + names.index(h), "native-to-owner width join")
            joins[tag][str(h)] = {"helper_index": names.index(h), "native_pair": key, "width": rank}
    result["native_to_owner_join"] = joins
    result["prior_coverage"] = prior_coverage(blobs, native_results)
    require(authenticate() == blobs, "source stability during replay")
    return decode(json.dumps(result).encode())


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = compute()
    if sys.argv[1:]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(decode((PACKAGE / "RESULT.json").read_bytes()) == result, "deterministic receipt")
        print(result["status"] + " providers=2 helpers=5 residual_widths=7,6,6,6,6 roles=271728 no_new_kappa")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact P104 scalar identity using eight actual source registers.

Run with Python 3.12+ and the standard library:
    python3 -I -B research/p104-interleaved-search/actual_queries.py

The four non-coordinate queries are punctured Y registers produced by the
reordered retained B prefix. Four old coordinate centres supply the other
queries. The verifier constructs frame-zero compensation and ordered FULL
restoration and checks all 704 initial columns. The intervening scalar scatter
is deliberately unframed: its direct source-to-live-Y additions violate the
native survivor frames. This is not a native word, COPY56 certificate, hosting
proof, cost certificate, or exponent improvement.

Sources and predecessor attribution are retained in this package's README.
New verifier prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module(name):
    spec = importlib.util.spec_from_file_location("p104_actual_" + name, HERE / (name + ".py"))
    if spec is None or spec.loader is None:
        raise ValueError("cannot load local verifier " + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(events):
    return hashlib.sha256(json.dumps(events, separators=(",", ":")).encode()).hexdigest()


def build():
    """Derive the fixed recipe once; failure controls never re-fit its repairs."""
    qc, scalar = load_module("query_construction"), load_module("scalar_surgery")
    require = qc.require
    inputs = qc.load_inputs()
    word, prototype = inputs["word"], inputs["coordinates"]
    v, n = word["v"], 2 * word["v"] + word["R"]
    selected, specs = qc.geometry(inputs)
    roots, terms = scalar.coordinate_data(word, prototype, inputs["fixture"])
    require(roots == selected, "source coordinate bindings disagree")
    pairs = scalar.DECODER_ROOT_PAIRS
    require(tuple(b for _, b in pairs[:4]) == qc.QUERY_ROOTS, "chosen non-coordinate query basis")
    order, availability, _, _ = qc.schedule(word, specs)
    B = [word["B"][j] for j in order]
    cut = max(availability.values())
    live = [i for i in range(v) if i not in qc.REMOVED]
    live_set = set(live)
    prefix = word["precondition"] + word["compensation"] + word["A"] + B[:cut]
    suffix = B[cut:] + word["tail"] + word["cleanup"]
    at_cut = qc.run(qc.identity(n), prefix)
    registers, scales, source_records = {}, {}, []
    for aa, bb in pairs:
        register = specs[bb]["register"] if bb in specs else word["centers"][bb]
        scale = -Q(1, 4) if bb in specs else Q(1, 2)
        raw = {i: Q(qc.dot(selected[i], prototype["root_lines"][bb])) for i in live
               if qc.dot(selected[i], prototype["root_lines"][bb])}
        clean = {i: x for i, x in at_cut[register].items() if i in live_set}
        dirt = {i: x for i, x in at_cut[register].items() if i not in live_set}
        require(clean == {i: scale * x for i, x in raw.items()}, f"actual query {bb} coefficients")
        require(all(i in qc.REMOVED or not word["frames"][word["start"][i]] for i in dirt),
                f"actual query {bb} nonzero-entrance dirt")
        require(not any(v <= i < 2*v and i-v in live_set for i in dirt), f"query {bb} live initial Y")
        registers[bb], scales[bb] = register, scale
        source_records.append({
            "a_root": aa, "b_root": bb, "register": register,
            "raw_query_coefficient": str(scale),
            "full_704_column_row_sha256": qc.row_digest(at_cut[register]),
        })
    require(len(set(registers.values())) == 8, "aliased source registers")

    # Invert the actual remaining live-Y transfer to obtain a scalar scatter
    # into current live-Y coordinates. This matrix solve does not assign frames.
    transfer = qc.run([{i-v: Q(1)} if v <= i < 2*v else {} for i in range(n)], B[cut:])
    decoder = [[Q(qc.dot(selected[t], a), 4*d) / scales[bb]
                for (a, b, label, d), (aa, bb) in zip(terms, pairs)] for t in live]
    scatter_matrix = scalar.solve(
        [[transfer[v+t].get(j, Q(0)) for j in live] for t in live], decoder)
    scatter = []
    for i, t in enumerate(live):
        for k, (aa, bb) in enumerate(pairs):
            coefficient = scatter_matrix[i][k]
            if coefficient:
                scatter.append(["add", v+t, registers[bb], coefficient.numerator, coefficient.denominator, None])
    require(all(e[1] not in registers.values() for e in scatter), "scatter overwrites source bank")

    def replay(compensation=(), restoration=(), scatter_override=None):
        events = (list(compensation) + prefix +
                  (scatter if scatter_override is None else scatter_override) + suffix + list(restoration))
        return qc.run(qc.identity(n), events)

    uncorrected = replay()
    compensation = []
    for t in live:
        row = uncorrected[v+t]
        require(all(row.get(i, Q(0)) == Q(i == t) for i in live), f"live-X identity before compensation at {t}")
        require(row.get(v+t) == 1, "live-Y diagonal before compensation")
        for i, coefficient in sorted(row.items()):
            if i in (t, v+t):
                continue
            require(i in qc.REMOVED or not word["frames"][word["start"][i]], "nonzero-entrance compensation source")
            require(not (v <= i < 2*v and i-v in live_set), "compensation reads another live Y")
            compensation.append(["add", v+t, i, -coefficient.numerator, coefficient.denominator, 0])
    compensated = replay(compensation)
    require(all(compensated[v+t] == {v+t: Q(1), t: Q(1)} for t in live), "compensated live-Y identity")
    removed_Y = {v+t for t in qc.REMOVED}
    require(all(compensated[r] == {r: Q(1)} for r in range(n)
                if r not in removed_Y and not (v <= r < 2*v and r-v in live_set)),
            "unrestored register outside punctured Y")

    # Restore the four natural query banks before the other four deleted Y
    # roles: the latter may still contain the former's initial dirty values.
    natural = [specs[q]["register"] for q in qc.QUERY_ROOTS]
    restoration_order = natural + sorted(removed_Y - set(natural))
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == 9)
    restoration, restoration_blocks = [], []
    for register in restoration_order:
        require(compensated[register].get(register) == 1, "restoration diagonal")
        block = []
        for i, coefficient in sorted(compensated[register].items()):
            if i == register:
                continue
            require(compensated[i] == {i: Q(1)}, "restoration reads an unrestored source")
            require(len(word["frames"][word["final"][i]]) == 9 or i in removed_Y,
                    "restoration source cannot use FULL without extra promotion")
            event = ["add", register, i, -coefficient.numerator, coefficient.denominator, full]
            block.append(event)
            qc.apply(event, compensated)
        require(compensated[register] == {register: Q(1)}, "restoration row")
        restoration.extend(block)
        restoration_blocks.append(block)
    require(not scalar.endpoint_failures(compensated, v, live), "constructed full-column endpoint identity")
    require(replay(compensation, restoration) == compensated, "fresh replay of fixed recipe")

    # Exhibit the missing native obligation: every direct source chart is too
    # large for the relevant live target's endpoint. None is a legal free ADD.
    frame_sets = list(map(qc.span, word["frames"]))
    current = list(word["start"])
    qc.native_run(prefix, current, frame_sets, word["frames"])
    violations = sum(not frame_sets[current[e[2]]] <= frame_sets[word["final"][e[1]]]
                     for e in scatter)
    require(violations == len(scatter), "unexpected direct-scatter native classification")
    require(all(len(word["frames"][word["final"][r]]) == 8 for r in removed_Y),
            "punctured-Y restoration boundary rank")
    return {
        "qc": qc, "scalar": scalar, "inputs": inputs, "word": word,
        "n": n, "v": v, "live": live, "prefix": prefix, "suffix": suffix,
        "scatter": scatter, "compensation": compensation, "restoration": restoration,
        "restoration_blocks": restoration_blocks, "restoration_order": restoration_order,
        "sources": source_records, "cut": cut, "B_order": order,
        "native_scatter_violations": violations, "replay": replay,
    }


def verify():
    recipe = build()
    qc, scalar, word = recipe["qc"], recipe["scalar"], recipe["word"]
    compensation, restoration, scatter = (recipe[name] for name in ("compensation", "restoration", "scatter"))
    replay = recipe["replay"]
    v, n, live = recipe["v"], recipe["n"], recipe["live"]
    controls = {}
    altered_scatter = [event.copy() for event in scatter]
    altered_scatter[0][3] += altered_scatter[0][4]
    experiments = {
        "changed_scatter_coefficient": (compensation, restoration, altered_scatter),
        "dropped_frame_zero_compensation": (compensation[1:], restoration, scatter),
        "dropped_FULL_restoration": (compensation, restoration[:-1], scatter),
        "reversed_restoration_block_order": (compensation,
            [event for block in reversed(recipe["restoration_blocks"]) for event in block], scatter),
    }
    for name, (comp, restore, additions) in experiments.items():
        failures = scalar.endpoint_failures(replay(comp, restore, additions), v, live)
        qc.require(bool(failures), "fixed-repair failure control was accepted: " + name)
        controls[name] = {"rejected": True, "incorrect_endpoint_registers": len(failures)}
    result = replay(compensation, restoration)
    qc.require(not scalar.endpoint_failures(result, v, live), "final fixed-recipe identity")
    input_frames = word["start"].copy()
    for t in qc.REMOVED:
        input_frames[t] = 0
    qc.require(all(not word["frames"][input_frames[r]] for e in compensation for r in e[1:3]),
               "compensation not in common initial frame zero")
    return {
        "status": "ACTUAL_QUERY_SCALAR_IDENTITY_NOT_NATIVE_DELIVERY",
        "source_sha256": {relative: expected for relative, expected in qc.INPUTS.values()},
        "physical_registers": n,
        "live_ports": len(live),
        "full_704_column_identity": True,
        "old_centre_cut_included": False,
        "actual_query_cut_before_reordered_B_event": recipe["cut"],
        "B_permutation_sha256": digest(recipe["B_order"]),
        "sources": recipe["sources"],
        "unframed_scalar_scatter": {
            "additions": len(scatter), "sha256": digest(scatter),
            "source_frame_not_subset_live_target_endpoint": recipe["native_scatter_violations"],
            "native_frame_certificate": False,
        },
        "initial_frame_zero_compensation": {
            "additions": len(compensation), "sha256": digest(compensation),
            "source_registers": sorted({e[2] for e in compensation}),
            "punctured_X_roles_start_at_frame_zero": list(qc.REMOVED),
        },
        "ordered_FULL_restoration": {
            "additions": len(restoration), "sha256": digest(restoration),
            "register_order": recipe["restoration_order"],
            "every_source_already_restored_when_read": True,
            "all_eight_punctured_Y_roles_must_reach_FULL": True,
            "required_H8_to_FULL_boundary_profile": {"1": 8},
            "boundary_cost_not_a_new_additional_invoice": "These boundaries are part of retaining the eight punctured Y roles; a complete native schedule still must charge them.",
        },
        "failure_controls_with_repairs_held_fixed": controls,
        "unproved_obligations": [
            "replace the unframed scalar scatter with legal delivery after query availability",
            "verify the complete native word and its actual transport profile",
            "host all public and private lifetimes and price the complete global supplier",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

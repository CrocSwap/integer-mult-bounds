# SPDX-License-Identifier: Apache-2.0
"""Bind literal coefficient recipes to their actual correlated native rows."""

import hashlib
from fractions import Fraction as Q

import integer
from vendor.lowering import lower
from vendor.native import format as native

POLICIES = lower.POLICIES
MAX_TEMPLATES = 32


def template(gate, policy):
    kind = gate[0]
    native.require(kind in ("add", "scale"), "ordinary scalar kind")
    a, b = gate[-2:]
    recipe = lower.certify(kind, a, b, policy=policy)
    rows = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(0), Q(0)))
    trace = []
    for instruction in recipe:
        rows = lower.execute([instruction], rows)
        target = instruction[1]
        trace.append((target, rows[target]))
    return recipe, trace


def substitute(weights, target, source):
    result = {atom: q * weights[0] for atom, q in target.items() if q * weights[0]}
    return native.add(result, source, weights[1])


def evaluate(recipe, trace, before, source, expected, rank, ledger, index):
    """Only the changed local row needs a new observation after each step."""
    native.require(len(trace) <= 32, "bounded primitive trace")
    rows = []
    for step, (port, weights) in enumerate(trace):
        row = substitute(weights, before, source)
        rows.append(row)
        native.require(
            integer.bounds(row, rank)
            == (
                native.depth(row) + native.exponent(rank, True),
                native.norm(row) * 2 ** native.exponent(rank, True),
            ),
            "independent grid/norm equality",
        )
        ledger.field(row, rank, index, f"recipe step {step} port {port}")
    return integer.check_rows(recipe, before, source, expected, rows)


def observe_scalar(
    event, record, source, index, frames, active, templates, ledgers, counts, digests
):
    before, expected = record[2], record[4]
    rank = len(frames[record[5]]) if active else 0
    gate = event[1]
    key = (gate[0], *gate[-2:])
    if key not in templates:
        native.require(len(templates) < MAX_TEMPLATES, "bounded recipe alphabet")
        templates[key] = {p: template(gate, p) for p in POLICIES}
    for policy, (recipe, trace) in templates[key].items():
        count = counts[policy]
        count["instructions"] += evaluate(
            recipe, trace, before, source, expected, rank, ledgers[policy], index
        )
        count["source_writes"] += sum(instruction[1] == 1 for instruction in recipe)
        count["scratch_macros"] += any(instruction[1] == 2 for instruction in recipe)
        digests[policy].update(native.canonical([index, recipe]))


def combined(baseline, ledger):
    result = native.Ledger(True, correlated=True)
    for grid, amplitude, witness in (
        (
            baseline["fractional_bits"],
            Q(baseline["symmetric_amplitude_in_input_L"]),
            "inherited conversion/endpoints",
        ),
        (ledger.grid, ledger.amplitude, "coefficient microstates"),
    ):
        result.observe(grid, amplitude, -1, witness)
    report = result.result(64)
    for precision in (3, 64, 128):
        native.capacity(report, precision, 7, precision + 20)
    return report


def report(direction, scalars, templates, baseline, ledgers, counts, digests):
    return {
        "direction": direction,
        "scalar_macros": scalars,
        "template_count": len(templates),
        "baseline": baseline,
        "policies": {
            p: {
                "capacity": combined(baseline, ledgers[p]),
                "microstates_only": ledgers[p].result(64),
                "single_component_instructions": counts[p]["instructions"],
                "source_writes": counts[p]["source_writes"],
                "scratch_macros": counts[p]["scratch_macros"],
                "recipe_sha256": digests[p].hexdigest(),
            }
            for p in POLICIES
        },
    }


def stage(events, word, direction):
    baseline = native.stage(events, word)["pair_first"]
    ledgers = {policy: native.Ledger(True, correlated=True) for policy in POLICIES}
    state = {("L", r): {(r, ()): Q(1)} for r in range(632)}
    current = {("L", r): f for r, f in enumerate(word["start"])}
    templates = {}
    counts = {
        p: dict.fromkeys(("instructions", "source_writes", "scratch_macros"), 0)
        for p in POLICIES
    }
    digests = {p: hashlib.sha256() for p in POLICIES}
    active = ended = False
    scalars = 0
    for index, event in enumerate(events):
        if event[0] == "phase":
            if event[1] == "A":
                active = True
            elif active:
                native.require(event[1] == "centers", "complete A endpoint")
                ended = True
                break
            continue
        if event[0] in ("adapter", "residual_adapter"):
            native.require(not active, "adapter endpoint hypothesis")
            continue
        source = (
            state[tuple(event[1][2])]
            if event[0] == "scalar" and event[1][0] == "add"
            else {}
        )
        record = native.apply_event(event, state, current, word["frames"], active)
        if event[0] != "scalar":
            continue
        scalars += 1
        observe_scalar(
            event,
            record,
            source,
            index,
            word["frames"],
            active,
            templates,
            ledgers,
            counts,
            digests,
        )
    native.require(ended and scalars == 9992, "complete prelude/A scalar workload")
    native.require(
        [counts[p]["instructions"] for p in POLICIES] == [32391, 28855, 28855]
        and counts["target_walk"]["source_writes"] == 0,
        "complete instruction saving and read-only source policy",
    )
    return report(direction, scalars, templates, baseline, ledgers, counts, digests)

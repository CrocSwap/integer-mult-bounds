# SPDX-License-Identifier: Apache-2.0
"""Substitute actual source rows into every literal scalar recipe prefix."""

import hashlib
from fractions import Fraction as Q

from vendor import lower
from vendor.format_source import format as f

MAX_STEPS = 40_000


def step(rows, instruction):
    """The caller supplies a recipe certified over independent input columns."""
    kind, target = instruction[:2]
    if kind == "copy":
        rows[target] = rows[instruction[2]].copy()
    elif kind == "add":
        rows[target] = f.add(rows[target], rows[instruction[2]], Q(instruction[3]))
    else:
        factor = {"half": Q(1, 2), "double": Q(2), "neg": Q(-1), "clear": Q(0)}[kind]
        rows[target] = {a: q * factor for a, q in rows[target].items() if q * factor}
    f.depth(rows[target])
    return target


def prefix_record(event, offset, target, row):
    terms = [
        [v, list(w), q.numerator, q.denominator] for (v, w), q in sorted(row.items())
    ]
    return [event, offset, target, terms]


def macro(before, source, after, recipe, rank, ledger, index, digest):
    rows = [before.copy(), source.copy(), {}]
    for row in rows[:2]:
        ledger.field(row, rank, index, "scalar recipe entrance")
    for offset, instruction in enumerate(recipe):
        target = step(rows, instruction)
        ledger.field(rows[target], rank, index, "scalar recipe prefix")
        digest.update(f.canonical(prefix_record(index, offset, target, rows[target])))
    f.require(
        rows == [after, source, {}], "literal endpoint/source/zero-scratch return"
    )


def literal_record(index, gate, frame, recipe):
    return {"event": index, "gate": gate, "frame": frame, "instructions": recipe}


def scalar_event(event, record, state, frames, active, policy, ledger, index, digest):
    target, source, before, _, after, old, _ = record
    gate = event[1]
    recipe = lower.certify(gate[0], gate[-2], gate[-1], policy=policy)
    rank = len(frames[old]) if active else 0
    macro(
        before,
        state[source] if source else {},
        after,
        recipe,
        rank,
        ledger,
        index,
        digest,
    )
    f.require(state[target] == after, "chronological macro output")
    return recipe


def stage(events, word, policy, output):
    f.require(
        policy in lower.POLICIES and len(events) <= f.MAX_EVENTS, "bounded stream"
    )
    frames = word["frames"]
    current = {("L", r): frame for r, frame in enumerate(word["start"])}
    f.require(len(current) == 632, "ordinary source inventory")
    state = {r: {(r[1], ()): Q(1)} for r in current}
    ledger = f.Ledger(True, correlated=True)
    digest, rows_digest, literal_digest = (hashlib.sha256() for _ in range(3))
    active = ended = False
    macros = instructions = source_writes = scratch_macros = 0
    recipe_digest = hashlib.sha256()
    for index, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            if event[1] == "A":
                f.require(not active, "single A phase")
                active = True
            elif active:
                f.require(event[1] == "centers", "stop immediately before centres")
                ended = True
                break
            continue
        if tag in ("adapter", "residual_adapter"):
            f.require(not active, "hypothesized adapters only before A")
            continue
        record = f.apply_event(event, state, current, frames, active)
        if tag == "scalar":
            recipe = scalar_event(
                event, record, state, frames, active, policy, ledger, index, digest
            )
            macros += 1
            instructions += len(recipe)
            source_writes += sum(item[1] == 1 for item in recipe)
            scratch_macros += any(item[1] == 2 for item in recipe)
            recipe_digest.update(f.canonical([index, recipe]))
            f.require(instructions <= MAX_STEPS, "bounded complete expansion")
            raw = f.canonical(literal_record(index, event[1], record[-2], recipe))
            f.require(
                output.write(raw + b"\n") == len(raw) + 1, "complete literal write"
            )
            literal_digest.update(raw + b"\n")
        if tag in ("scalar", "warp"):
            rows_digest.update(f.canonical(f.row_record(index, record[0], record[4])))
    f.require(ended and macros == 9992, "complete prelude and A scalar coverage")
    return {
        "macros": macros,
        "real_instruction_slots": 2 * instructions,
        "source_writes": source_writes,
        "scratch_macros": scratch_macros,
        "recipe_sha256": recipe_digest.hexdigest(),
        "envelope": ledger.result(64),
        "literal_sha256": literal_digest.hexdigest(),
        "microstate_sha256": digest.hexdigest(),
        "normalized_rows_sha256": rows_digest.hexdigest(),
        "end_event": index,
    }

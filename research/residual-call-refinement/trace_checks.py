"""Compare both retained event emitters with an independent address oracle."""

import hashlib
import json
from dataclasses import replace
from itertools import product

import specification as spec


def signature(event, page, observe):
    if event.kind in ("enter", "invoke", "return"):
        spec.need(
            event.parent_identity is page.parent_identity, "borrowed parent identity"
        )

    def value(word):
        return None if word is None else observe(word)

    coefficient = event.request
    if coefficient is not None:
        coefficient = spec.request(
            coefficient.kind,
            value(coefficient.coordinate),
            None
            if coefficient.reference is None
            else spec.reference_key(coefficient.reference),
            coefficient.reverse_adapter,
            coefficient.child_kind,
            coefficient.field,
            coefficient.reverse,
            coefficient.negative_inverse,
            coefficient.half,
        )
    return spec.event(
        event.kind,
        value(event.first),
        value(event.second),
        value(event.width),
        value(event.depth),
        event.child_kind,
        event.field,
        event.reverse,
        event.source_code,
        event.half,
        coefficient,
    )


def collect(iterator, page, observe):
    try:
        return [signature(event, page, observe) for event in iterator]
    finally:
        iterator.close()


def plans():
    from plan import Command, Plan, Reference

    for dimension in (2, 3, 64):
        for rank in sorted({1, dimension - 1, *(r for r in (7, 42) if r < dimension)}):
            commands = (
                Command("add", 1, 0, Reference("head", 2, 1, 0)),
                Command("add", dimension + 1, dimension, Reference("tail", 3, sign=-1)),
            )
            yield Plan(dimension, rank, True, commands)
        commands = (
            Command("child", 0, 1, Reference("pair")),
            Command("child", dimension, dimension + 1, Reference("pair")),
            Command("child", 0, dimension, Reference("unit")),
            Command("add", dimension + 1, 0, Reference("shear", 2)),
            Command("sign", 2 * dimension - 1, -1, Reference("fixed", sign=-1)),
        )
        yield Plan(dimension, 1, False, commands)


def check_case(plan, columns):
    from trace import execute

    from check_support import inspect_count
    from numeric import Geometry
    from residual_blocks import Cursor, events
    from words import Arena

    arena = Arena(20, 128)
    width, depth = arena.input(columns), arena.input(9)
    page = Geometry(plan, arena, width, depth, 23, object())
    retained = frozenset(arena.live)
    try:
        expected = spec.expected(plan, columns)
        source = collect(execute(page), page, inspect_count)
        spec.need(source == expected, "source trace disagrees with independent grammar")
        actual, blocks = [], []
        cursor = Cursor(plan)
        for _ in range(3 * max(1, len(plan.commands))):
            if cursor.done:
                break
            block = cursor.take()
            blocks.append(block)
            actual.extend(collect(events(page, block), page, inspect_count))
            spec.need(arena.live == retained, "block releases borrowed numerical words")
        spec.need(
            cursor.done and actual == expected,
            "compiled residual disagrees with grammar",
        )
        return actual, blocks
    finally:
        page.close()
        arena.free_many(width, depth)
        spec.need(not arena.live, "trace fixture releases words")


def run():
    digest = hashlib.sha256()
    counts = {
        "cases": 0,
        "events": 0,
        "blocks": 0,
        "internal_entries": 0,
        "leaf_entries": 0,
    }
    for plan, columns in product(plans(), (1, 2, 3, 9, 63, 64, 65, 127, 128, 129)):
        actual, blocks = check_case(plan, columns)
        counts["cases"] += 1
        counts["events"] += len(actual)
        counts["blocks"] += len(blocks)
        for row in actual:
            if row[0] == "enter":
                counts["internal_entries" if row[3] >= 64 else "leaf_entries"] += 1
        digest.update(json.dumps(actual, separators=(",", ":")).encode())
    counts["sha256"] = digest.hexdigest()
    return counts


def controls():
    """Demonstrate why endpoint cancellation cannot establish this relation."""
    from trace import Event
    from unittest.mock import patch

    import residual_blocks

    plan = next(p for p in plans() if not p.good and p.dimension == 2)
    original = residual_blocks.events
    labels = ("omit_first_reset", "duplicate_enter", "double_sign", "lose_half_flag")
    for label in labels:

        def mutated(page, block, label=label):
            iterator = original(page, block)
            try:
                for index, event in enumerate(iterator):
                    if block == ("pair", 0, 0):
                        if label == "omit_first_reset":
                            continue
                        if label == "duplicate_enter" and event.kind == "enter":
                            yield event
                        if label == "double_sign" and index == 0:
                            yield Event("sign", event.first)
                            yield Event("sign", event.first)
                        if label == "lose_half_flag" and event.kind == "enter":
                            event = replace(event, half=False)
                    yield event
            finally:
                iterator.close()

        with patch.object(residual_blocks, "events", mutated):
            try:
                check_case(plan, 129)
            except ValueError as error:
                spec.need(
                    str(error) == "compiled residual disagrees with grammar",
                    "trace control reaches intended relation",
                )
            else:
                raise ValueError("trace control escaped: " + label)
    # Two consecutive signs are the identity over every ring, but are observable
    # at intermediate cuts. They leave this tiny signed endpoint unchanged.
    for value in (-3, 0, 5):
        negated = -value
        spec.need(-negated == value, "double-sign endpoint identity")
    return sorted(labels)

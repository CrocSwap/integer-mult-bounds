"""Bind selected full-ring fields to the pinned PR2310 control interface.

New interface glue; producer algebra and iterative evaluation are reused and
credited. Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from dataclasses import dataclass
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "sources/pr2310"),
               str(HERE / "sources/pr2234"),
               str(HERE / "sources/pr2234/vendor")]

import control
import descriptor as d
import provider
from controlled_normalizer import Arithmetic
from expressions import Expression, BoundExpression, FrozenFields, FieldSpecification
from recursive_plan import residual_plan


def need(test, message):
    if not test:
        raise ValueError(message)


@dataclass(frozen=True)
class Event:
    """One actual descent. A unit reset still freezes one physical field."""
    kind: str
    request: object
    low: tuple
    field: int = 0
    reverse: bool = False
    half: bool = False


@dataclass(frozen=True)
class Compilation:
    program: object
    tables: tuple
    expression: object
    live_slots: tuple


def neutral_table(tag):
    # Unread entries have no mathematical coefficient role. The consumer's
    # fixed-size page format requires valid unit padding at every slot.
    return control.Table(tag, (1,) * 64, (1,) * 128, tuple(range(128)))


def prepare_table(header, kind, tag):
    """Use the FULL unweighted matrix, preserving the producer's row order."""
    modulus = header.q ** header.width
    p = d.projector(header.read(Arithmetic(modulus)), header.axes, modulus)
    need(p == header.direct_projector(), "actual chart/base projector binding")
    blank = neutral_table(tag)
    if kind == "good":
        pivots = d.good_pivots(p, header.request.base.rank, modulus)
        return control.Table(tag, pivots + (1,) * (64 - len(pivots)),
                             blank.diagonal, blank.permutation)
    need(kind == "pair", "coefficient-bearing descent")
    plan = d.elimination(d.residual(p, modulus), modulus)
    return control.Table(tag, blank.pivots, plan.diagonal, plan.permutation)


def compile_chain(q, width, root_size, root_unit, events, fields, catalogue):
    """Compile one chronological chain; reject wrong source specifications.

    Tags are local slot tokens, not source hashes. Source equality is checked
    on the full FieldSpecification before a table is produced. A caller must
    preserve this pair of outputs; arbitrary pre-made tables are not trusted.
    """
    need(len(fields.high_matrices) == len(events) == len(fields.specifications),
         "complete frozen field prefix")
    expression = Expression(q, width, root_size, root_unit)
    steps = []
    for slot, event in enumerate(events):
        need(event.request in catalogue.requests, "selected provider request")
        specification = FieldSpecification(q, width, event.request, event.low)
        need(fields.specifications[slot] == specification, "exact frozen source specification")
        need(event.kind in ("good", "pair", "unit"), "descent kind")
        need(event.kind == "unit" or not event.half, "halving only at unit reset")
        need(event.kind == "pair" or (event.field == 0 and not event.reverse),
             "pair-only field and orientation")
        tag = slot + 1
        steps.append(control.Step(event.kind, tag, event.request.base.rank,
                                  event.field, event.reverse, event.half))
        plan = residual_plan(expression, event.request, event.low, catalogue)
        if event.kind == "unit":
            f = expression.size // 64
            child = expression.unit_child(f // 2 if event.half else f)
            child_kind = "orientation" if event.half else "unit"
        else:
            child = expression.append(event.kind, event.request, event.low,
                                      slot, event.field, event.reverse)
            child_kind = event.kind
        need(any(c.kind == child_kind and c.expression == child for c in plan.children),
             "descent is present in the actual low-class macroplan")
        expression = child
    program = control.Program(q, width, root_size, root_unit, tuple(steps))
    sizes = program.extents()
    need(sizes[-1] == expression.size and expression.depth == len(events),
         "program and source expression extents")
    # A reset makes all earlier numerical coefficients irrelevant. Keep the
    # physical slots but do not read or prepare their high matrices.
    first_live = 1 + max((i for i, e in enumerate(events) if e.kind == "unit"), default=-1)
    tables = []
    for slot, event in enumerate(events):
        tag = slot + 1
        if slot < first_live:
            tables.append(neutral_table(tag))
            continue
        specification = FieldSpecification(q, width, event.request, event.low)
        high = fields.high(slot, specification)
        raw = provider.RawHeader(q, width, event.low, high, event.request.header_space)
        header = provider.GeneralHeader(raw, event.request, catalogue)
        tables.append(prepare_table(header, event.kind, tag))
    return Compilation(program, tuple(tables), expression,
                       tuple(range(first_live, len(events))))


def run(compilation, index):
    meter = control.Meter()
    tape = control.FrozenTape(compilation.tables,
                             compilation.program.q ** compilation.program.width, meter)
    original = tape.data
    value = control.evaluate(compilation.program, tape, index)
    need(tape.data == original and tape.head == 0, "readonly tables and restored head")
    need(set(meter.field_reads) <= set(compilation.live_slots), "only live global slots read")
    return value, meter


def bound_reference(compilation, fields, catalogue):
    """Attributed PR2234 oracle, not an independent algebra implementation."""
    return provider.build_weights(BoundExpression(compilation.expression, catalogue, fields))[0]

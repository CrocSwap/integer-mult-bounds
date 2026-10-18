"""Dimension-aware continuation of PR2310, using actual full-ring headers."""
from dataclasses import dataclass

from algebra import Header, fallback, good, need


@dataclass(frozen=True)
class Step:
    kind: str
    specification: tuple
    dimension: int
    size: int
    field: int = 0
    reverse: bool = False


@dataclass(frozen=True)
class Program:
    q: int
    width: int
    root_size: int
    unit: int = 1
    steps: tuple = ()

    @property
    def size(self): return self.steps[-1].size if self.steps else self.root_size
    @property
    def depth(self): return len(self.steps)

    def child(self, kind, header, size=None, field=0, reverse=False):
        need((header.q, header.width) == (self.q, self.width), "one recursive atom ring")
        f = self.size // header.dimension
        need(f >= 1 and kind in ("good", "pair", "unit"), "generated child kind")
        computed = len(header.axes) * f if kind == "good" else f
        if kind == "unit":
            need(size is not None and 0 < size <= f, "unit/orientation child extent")
            computed = size
        need(0 < computed < self.size, "proper child descent")
        step = Step(kind, header.specification, header.dimension, computed, field, reverse)
        return Program(self.q, self.width, self.root_size, self.unit, self.steps + (step,))


def value(program, history, index, stats, low_only=False):
    """No fresh row or current-header argument exists at this boundary."""
    need(len(history) == program.depth, "global frozen-field age")
    need(0 <= index < program.size, "weight coordinate extent")
    stats["control_evaluations"] += 1
    sizes = [program.root_size] + [step.size for step in program.steps]
    modulus = program.q**program.width
    pending, values = [("value", program.depth, index)], []
    while pending:
        stats["max_control_stack"] = max(stats["max_control_stack"], len(pending) + len(values))
        op = pending.pop()
        if op[0] == "constant":
            values.append(op[1])
        elif op[0] == "multiply":
            values[-1] = values[-1] * op[1] % modulus
        elif op[0] == "pair":
            denominator, numerator = values.pop(), values.pop()
            values.append(op[1] * numerator * pow(denominator, -1, modulus) % modulus)
        else:
            _, level, coordinate = op
            need(0 <= coordinate < sizes[level], "recursive weight index")
            if level == 0:
                values.append(program.unit % modulus)
                continue
            step = program.steps[level - 1]
            if step.kind == "unit":
                values.append(1)
                continue
            header = history[level - 1]
            need(header.specification == step.specification, "chronological full-header source binding")
            stats["field_table_reads"] += 1
            stats["max_frozen_slot"] = max(stats["max_frozen_slot"], level - 1)
            if low_only:
                header = Header(header.q, header.width, header.low, header.axes)
            m = step.dimension
            f = sizes[level - 1] // m
            if step.kind == "good":
                pivot = good(header).pivots[coordinate // f]
                pending.extend((("multiply", pivot), ("value", level - 1, coordinate)))
            else:
                plan = fallback(header)
                column = f - 1 - coordinate if step.reverse else coordinate
                def bank(row):
                    return ("value", level - 1, row * f + column) if row < m else ("constant", 1)
                pending.extend((("pair", plan.diagonal[step.field]), bank(step.field),
                                bank(plan.permutation[step.field])))
    need(len(values) == 1 and not pending, "completed control stack")
    return values.pop()

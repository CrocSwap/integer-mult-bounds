"""Defunctionalized residual itinerary at complete column-sweep boundaries.

The cursor contains only a fixed-source command label and a three-way stage.
Variable column loops finish inside a block; an internal child can suspend
only its finite return label. This module does not interpret payload blocks.
"""
import loader
loader.activate()
from plan import Request
from role_parking import FiniteFields
from trace import adapters, child, columns, primitive
from words import need


class Cursor:
    def __init__(self, plan, position=0, stage=0):
        self.plan, self.position, self.stage = plan, position, stage
        self.bound = 3 if plan.good else len(plan.commands)
        self.schema = FiniteFields((self.bound + 1, 3))
        need(0 <= position <= self.bound and 0 <= stage < 3,
             "finite residual cursor")
        need(stage == 0 or (not plan.good and position < self.bound and
                           plan.commands[position].kind == "child"),
             "pair stages belong to fallback child commands")

    @property
    def done(self):
        return self.position == self.bound

    def save(self, tape):
        self.schema.write(tape, (self.position, self.stage))

    @classmethod
    def restore(cls, plan, tape):
        schema = FiniteFields(((3 if plan.good else len(plan.commands)) + 1, 3))
        return cls(plan, *schema.read(tape))

    def take(self):
        """Advance before execution; the new cursor is the return continuation."""
        need(not self.done, "unfinished residual block")
        position, stage = self.position, self.stage
        if self.plan.good:
            self.position += 1
            return ("forward", "good", "backward")[position], position, 0
        command = self.plan.commands[position]
        if command.kind == "child":
            if stage < 2:
                self.stage += 1
            else:
                self.position += 1
                self.stage = 0
            return "pair", position, stage
        self.position += 1
        return "sweep", position, 0


def events(page, block):
    """Reference expansion of one block, using the pinned primitive events.

    A physical interpreter runs forward/backward/sweep and below-cutoff leaves
    to completion. For an internal good/pair child it prepares the capsule and
    parks the finite return cursor; this reference generator is not that stack.
    """
    kind, position, stage = block
    if kind in ("forward", "backward"):
        yield from adapters(page, kind == "backward")
    elif kind == "good":
        yield from child(page, page.index.zero(),
                         page.raw.times_small(page.columns, 2 * page.plan.dimension - page.plan.rank),
                         page.raw.times_small(page.columns, page.plan.rank), "good")
    elif kind == "sweep":
        command = page.plan.commands[position]
        need(command.kind in ("add", "sign"), "complete nonrecursive column sweep")
        for column in columns(page):
            target = page.point(command.target, column)
            if command.kind == "sign":
                yield from primitive("sign", target, None, None, page)
            else:
                source = page.point(command.source, column)
                request = Request("adapter", page.index.copy(column), command.reference)
                yield from primitive("add", target, source, request, page)
    else:
        need(kind == "pair", "closed residual block alphabet")
        command = page.plan.commands[position]
        i, k, dimension = command.target, command.source, page.plan.dimension
        need(i < k, "ordered fallback child fields")
        if stage != 1:
            if (i < dimension) != (k < dimension):
                return
            half, remainder = page.raw.divmod(page.columns, page.two)
            page.index.free(remainder)
            if half.zero():
                page.index.free(half)
                return
            after = page.raw.times_small(page.columns, k + 1)
            second = page.raw.subtract_exact(after, half)
            page.index.free(after)
            yield from child(page, page.raw.times_small(page.columns, k), second,
                             half, "unit", half=True)
        else:
            child_kind = command.reference.kind
            need(child_kind in ("unit", "pair"), "selected fallback child kind")
            yield from child(page, page.raw.times_small(page.columns, i),
                             page.raw.times_small(page.columns, k), page.index.copy(page.columns),
                             child_kind, i if child_kind == "pair" else 0,
                             i >= dimension if child_kind == "pair" else False)

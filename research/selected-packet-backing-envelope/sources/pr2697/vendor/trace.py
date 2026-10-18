"""One encoded-index trace for algebra observation and stream interpretation.

The iterator lends each emitted word until the next iteration. A child
extension always refers to the unchanged parent program and current raw slot.
"""
from dataclasses import dataclass, replace

from plan import Request
from words import need


@dataclass
class Event:
    kind: str
    first: object
    second: object = None
    request: object = None
    width: object = None
    depth: object = None
    child_kind: str = ""
    field: int = 0
    reverse: bool = False
    source_code: int = 0
    parent_identity: object = None
    half: bool = False


def columns(page, reverse=False):
    j = page.raw.subtract_exact(page.columns, page.one) if reverse else page.index.zero()
    try:
        while page.raw.compare(j, page.columns) < 0:
            yield j
            if reverse:
                if j.zero():
                    break
                previous = page.raw.subtract_exact(j, page.one)
                page.index.free(j)
                j = previous
            else:
                page.raw.increment_in_place(j)
    finally:
        page.index.free(j)


def primitive(kind, first, second, request, page):
    try:
        yield Event(kind, first, second, request)
    finally:
        page.index.free(first)
        if second is not None:
            page.index.free(second)
        if request is not None:
            page.index.free(request.coordinate)


def leaf(page, first, second, width, kind, field=0, reverse=False, half=False):
    need(not width.zero() and page.raw.compare(width, page.leaf_cutoff) < 0,
         "completed leaf child below selected cutoff")
    depth = page.plus(page.depth, page.one)
    boundary = Event("enter", first, second, width=width, depth=depth,
                     child_kind=kind, field=field, reverse=reverse,
                     source_code=page.source_code, parent_identity=page.parent_identity, half=half)
    try:
        yield boundary
        i = page.index.zero()
        try:
            while page.raw.compare(i, width) < 0:
                left = page.plus(first, i)
                last = page.raw.subtract_exact(width, page.one)
                tail = page.raw.subtract_exact(last, i)
                right = page.plus(second, tail)
                page.index.free_many(last, tail)
                try:
                    # A weighted leaf uses only complete atom swaps, later
                    # ADDs and one sign. No weighted-swap oracle appears.
                    for stage in range(8):
                        a, b = page.index.copy(left), page.index.copy(right)
                        if stage in (0, 2, 4, 6):
                            yield from primitive("atom_swap", a, b, None, page)
                        elif stage == 7:
                            page.index.free(a)
                            yield from primitive("sign", b, None, None, page)
                        else:
                            request = Request("child", page.index.copy(i), child_kind=kind,
                                              field=field, reverse=reverse, negative_inverse=stage == 3, half=half)
                            yield from primitive("add", b, a, request, page)
                finally:
                    page.index.free_many(left, right)
                page.raw.increment_in_place(i)
        finally:
            page.index.free(i)
        yield replace(boundary, kind="return")
    finally:
        page.index.free(depth)


def child(page, first, second, width, kind, field=0, reverse=False, half=False):
    try:
        need(page.raw.compare(first, second) < 0, "ordered child chunks")
        end = page.plus(first, width)
        need(page.raw.compare(end, second) <= 0, "disjoint child chunks")
        page.index.free(end)
        yield from leaf(page, first, second, width, kind, field, reverse, half)
    finally:
        page.index.free_many(first, second, width)


def pair_command(page, command):
    i, k, m = command.target, command.source, page.plan.dimension
    need(i < k, "ordered fallback child fields")
    same = (i < m) == (k < m)
    half, remainder = page.raw.divmod(page.columns, page.two)
    page.index.free(remainder)
    try:
        for stage in range(3):
            if stage != 1:
                if not same or half.zero():
                    continue
                first = page.raw.times_small(page.columns, k)
                after = page.raw.times_small(page.columns, k+1)
                second = page.raw.subtract_exact(after, half)
                page.index.free(after)
                yield from child(page, first, second, page.index.copy(half), "unit", half=True)
            else:
                first = page.raw.times_small(page.columns, i)
                second = page.raw.times_small(page.columns, k)
                kind = command.reference.kind
                need(kind in ("unit", "pair"), "selected fallback child kind")
                yield from child(page, first, second, page.index.copy(page.columns),
                                 kind, i if kind == "pair" else 0,
                                 i >= m if kind == "pair" else False)
    finally:
        page.index.free(half)


def adapters(page, reverse=False):
    # Recreate the finite command iterator for each encoded column.
    for j in columns(page, reverse):
        commands = reversed(page.plan.commands) if reverse else page.plan.commands
        for command in commands:
            target, source = page.point(command.target, j), page.point(command.source, j)
            request = Request("adapter", page.index.copy(j), command.reference, reverse)
            yield from primitive("add", target, source, request, page)


def execute(page):
    """Expand one complete residual whose children lie below the cutoff."""
    if page.plan.good:
        yield from adapters(page)
        first = page.index.zero()
        second = page.raw.times_small(page.columns, 2*page.plan.dimension-page.plan.rank)
        width = page.raw.times_small(page.columns, page.plan.rank)
        yield from child(page, first, second, width, "good")
        yield from adapters(page, True)
    else:
        for command in page.plan.commands:
            if command.kind == "child":
                yield from pair_command(page, command)
            else:
                for j in columns(page):
                    target = page.point(command.target, j)
                    if command.kind == "sign":
                        yield from primitive("sign", target, None, None, page)
                    else:
                        source = page.point(command.source, j)
                        request = Request("adapter", page.index.copy(j), command.reference)
                        yield from primitive("add", target, source, request, page)

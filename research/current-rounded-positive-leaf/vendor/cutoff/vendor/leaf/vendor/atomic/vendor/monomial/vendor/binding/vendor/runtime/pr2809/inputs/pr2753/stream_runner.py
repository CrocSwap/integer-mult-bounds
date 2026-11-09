"""Interpret the shared trace on a complete Boolean fibre for one prefix.

Coefficient requests remain symbolic until a pass reads its exact raw prefix.
All physical atom positions and spectator cardinalities remain binary.
"""
from bitstream import atom_swap
from linear_sign import sign_address
from cardinality import Natural, multiply_atom_power
from stream import add_pass, positive_extent
from trace import execute
from words import need


class Layout:
    def __init__(self, geometry, parent_size, ring, q, before, suffix):
        positive_extent(before)
        positive_extent(suffix)
        self.geometry, self.ring, self.q = geometry, ring, q
        self.before, self.suffix = before, suffix
        self.core = geometry.raw.times_small(geometry.columns, geometry.plan.dimension)
        unused = geometry.raw.subtract_exact(parent_size, self.core)
        self.extra = geometry.raw.times_small(unused, 2)
        geometry.index.free(unused)
        self.total = geometry.raw.times_small(parent_size, 2)

    def physical(self, position):
        if self.geometry.raw.compare(position, self.core) < 0:
            return self.geometry.index.copy(position)
        return self.geometry.plus(position, self.extra)

    def extents(self, first, second=None):
        g = self.geometry
        a = self.physical(first)
        b = self.physical(second) if second is not None else None
        if b is not None:
            need(g.raw.compare(a, b) < 0, "ordered stream atoms")
        pre, tail = Natural(self.before), Natural(self.suffix)
        multiply_atom_power(pre, a, self.ring, self.q)
        after = g.raw.subtract_exact(self.total, a if b is None else b)
        count = g.raw.subtract_exact(after, g.one)
        multiply_atom_power(tail, count, self.ring, self.q)
        g.index.free_many(after, count)
        values = [pre]
        if b is not None:
            distance = g.raw.subtract_exact(b, a)
            gap = g.raw.subtract_exact(distance, g.one)
            middle = Natural()
            multiply_atom_power(middle, gap, self.ring, self.q)
            values.append(middle)
            g.index.free_many(distance, gap, b)
        values.append(tail)
        g.index.free(a)
        result = [value.marginal() for value in values]
        for value in values:
            value.close()
        return result

    def close(self):
        self.geometry.index.free_many(self.core, self.extra, self.total)


def action(source, event, layout, coefficient, payload_factory=None):
    """One full primitive pass; split and merge each request a coefficient."""
    if event.kind == "add":
        extents = layout.extents(event.second, event.first)
    elif event.kind == "atom_swap":
        extents = layout.extents(event.first, event.second)
    else:
        need(event.kind == "sign", "stream primitive tag")
        extents = layout.extents(event.first)
    try:
        if event.kind == "add":
            kwargs = {} if payload_factory is None else {"payload_factory": payload_factory}
            output, _traffic = add_pass(source, layout.ring, *extents,
                                       lambda: coefficient(event.request), **kwargs)
            return output
        if event.kind == "atom_swap":
            return atom_swap(source, layout.ring, layout.q, *extents)
        return sign_address(source, layout.ring, layout.q, *extents)
    finally:
        for extent in extents:
            extent.close()


def run(source, geometry, parent_size, ring, q, before, suffix, coefficient,
        payload_factory=None):
    layout = Layout(geometry, parent_size, ring, q, before, suffix)
    current, active = source, None
    try:
        for event in execute(geometry):
            if event.kind == "enter":
                need(active is None and event.parent_identity is geometry.parent_identity,
                     "one complete child invocation")
                active = event
                continue
            if event.kind == "return":
                need(active is not None and active.parent_identity is event.parent_identity
                     and active.source_code == event.source_code and active.child_kind == event.child_kind
                     and active.half == event.half,
                     "same symbolic child return")
                for a, b in ((active.first, event.first), (active.second, event.second),
                             (active.width, event.width), (active.depth, event.depth)):
                    need(geometry.raw.compare(a, b) == 0, "restored encoded child context")
                active = None
                continue
            following = action(current, event, layout, coefficient, payload_factory)
            if current is not source:
                current.clear()
            current = following
        need(active is None, "closed stream child invocation")
        return current
    finally:
        layout.close()

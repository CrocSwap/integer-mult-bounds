"""Run the retained closed primitive blocks with the sequential radix swap."""
from bitstream import copy_bits
from cardinal_counts import Count, positive
from cardinality import multiply_atom_power
from compact_digits import atom_swap
import fresh_rows
from layout import Layout
from numeric import Geometry
from packet import read_prefix
import peel
from plan import Plan, Request
from residual_blocks import events as block_events
from routes import copy_rows
from stream import Counter
from stream_runner import action
from trace import child
from words import BLANK, Unsigned, need


def primitive(source, event, layout, coefficient, factory):
    if event.kind != "atom_swap":
        return action(source, event, layout, coefficient, factory)
    extents = layout.extents(event.first, event.second)
    try:
        return atom_swap(source, layout.ring, layout.q, *extents, factory)
    finally:
        for extent in extents:
            extent.close()


def run_packet(source, events, layout, directory, prefixes, field_count, coefficient, factory):
    """The parent suspends internal children before this closed-block executor."""
    current = source
    fibre = layout.fibre()
    labels = None
    boundary = []
    returned = False
    try:
        for event in events:
            if event.kind in ("enter", "return"):
                identity = (event.child_kind, event.field, event.reverse, event.half,
                            event.source_code, event.parent_identity)
                words = (event.first, event.second, event.width, event.depth)
                if event.kind == "enter":
                    need(labels is None and event.parent_identity is layout.geometry.parent_identity
                         and layout.geometry.raw.compare(event.width, layout.geometry.leaf_cutoff) < 0,
                         "one completed below-cutoff leaf")
                    labels = identity
                    boundary = [layout.geometry.index.copy(v) for v in words]
                else:
                    need(labels == identity and len(boundary) == 4, "matching leaf return")
                    for saved, actual in zip(boundary,words):
                        need(layout.geometry.raw.compare(saved, actual) == 0, "restored leaf geometry")
                    layout.geometry.index.free_many(*boundary)
                    labels, boundary = None, []
                continue
            need(event.kind in ("sign", "add", "atom_swap"), "closed primitive block")
            output, remaining = factory(), Counter(prefixes)
            directory.rewind()
            try:
                need(not remaining.finished, "nonempty complete prefix packet")
                while not remaining.finished:
                    fields = read_prefix(directory, field_count)
                    local, changed = factory(), None
                    try:
                        copy_bits(current, local, fibre)
                        local.rewind()
                        changed = primitive(local, event, layout, lambda r: coefficient(fields,r), factory)
                        copy_bits(changed, output, fibre)
                        need(changed.read() == BLANK, "complete changed prefix fibre")
                    finally:
                        if changed is not None and changed is not local:
                            changed.clear()
                        local.clear()
                        fields.clear()
                    remaining.decrement()
                need(current.read() == directory.read() == BLANK, "complete shared packet and directory")
                current.rewind()
                directory.rewind()
                if current is not source:
                    current.clear()
                output.rewind()
                current = output
            except ValueError:
                output.clear()
                raise
            finally:
                remaining.close()
        need(labels is None, "complete leaf lifetime")
        returned = True
        return current
    finally:
        if not returned and current is not source:
            current.clear()
        fibre.close()
        directory.rewind()
        source.rewind()
        if boundary:
            layout.geometry.index.free_many(*boundary)
        events.close()


def run_peel(source, context, indices, parent_size, depth, program, old_directory, old_count,
             fresh_rows, before, gap, suffix, incoming, factory):
    divisor = indices.literal(context.dimension)
    columns, remainder = Unsigned(indices).divmod(parent_size, divisor)
    indices.free_many(divisor, remainder)
    geometry = Geometry(Plan(context.dimension, 1, True, ()), indices, columns, depth, 0, program)
    leading = Count.product(fresh_rows, before)
    layout = Layout(geometry, parent_size, context.ring, context.q, leading, gap, suffix, embedded=False)
    try:
        return run_packet(source, peel.events(geometry,parent_size), layout, old_directory,
                          old_count, depth, incoming.coefficient, factory)
    finally:
        layout.close()
        leading.close()
        geometry.close()
        indices.free(columns)


class CompactNodeOperations:
    """These two source methods pass the owned payload factory into each closed block."""
    def node(self):
        divisor = self.indices.literal(self.context.dimension)
        columns, remainder = Unsigned(self.indices).divmod(self.size, divisor)
        valid = not columns.zero()
        self.indices.free_many(divisor, columns, remainder)
        need(valid, "complete internal node width")
        for label in ("old_count", "rows", "before", "gap", "suffix"):
            self.count(label).normalize()
            positive(self.count(label))
        # Preserve source ingress validation before the first payload operation.
        first = read_prefix(self.tape("old_directory"), self.depth)
        self.tape("old_directory").rewind()
        zero = self.indices.zero()
        incoming = self.binding.incoming(self)
        try:
            value = incoming.coefficient(first, Request("incoming", zero))
            self.arena.free(value)
        finally:
            first.clear()
            self.indices.free(zero)
        unused = fresh_rows.quotient(self.count("rows"), self.context, self.topology.families)
        self.save_count(unused, "unused")
        stock = Count(self.count("unused"))
        try:
            need(stock.divide_small(self.binding.stock_multiple) == 0, "compatible fresh stock factor")
        finally:
            stock.close()
        self.save_count(Count.product(self.count("unused"), self.count("before")), "leading")
        fibre = Count.product(self.count("leading"), self.count("gap"))
        total = Unsigned(self.indices).times_small(self.size, 2)
        multiply_atom_power(fibre, total, self.context.ring, self.context.q)
        self.indices.free(total)
        complete = Count.product(fibre, self.count("suffix"))
        fibre.close()
        self.save_count(complete, "fibre")
        peeled = run_peel(self.tape("source"), self.context, self.indices, self.size, self.depth,
                          self.program, self.tape("old_directory"), self.count("old_count"),
                          self.count("rows"), self.count("before"), self.count("gap"),
                          self.count("suffix"), incoming, self.pool.acquire)
        self.commit(peeled, "peeled")
        self.save_count(fresh_rows.family_rows(self.context), "family_rows")
        source = self.tape("peeled")
        outer = Counter(self.count("old_count"))
        try:
            while not outer.finished:
                for family in range(self.topology.families):
                    copy_rows(source, self.tape(("family", family)), self.count("family_rows"), self.count("fibre"))
                outer.decrement()
            need(source.read() == BLANK, "complete canonical fresh-row split")
        finally:
            outer.close()
            source.rewind()
            for family in range(self.topology.families):
                self.tape(("family", family)).rewind()

    def block(self, definition, block):
        grants = None
        with self.geometry(definition) as (page, layout, fields):
            if block[0] == "axis":
                axis = block[1]
                trace = child(page, page.raw.times_small(page.columns, axis),
                              page.raw.times_small(page.columns, 3 - axis),
                              self.indices.copy(page.columns), "good")
            else:
                trace = block_events(page, block)
            try:
                first = next(trace, None)
                if first is not None and first.kind == "enter" and page.raw.compare(first.width, page.leaf_cutoff) >= 0:
                    grants = self.prepare_child(definition, first, layout, fields)
                else:
                    def complete_events():
                        if first is not None:
                            yield first
                        yield from trace
                    result = run_packet(self.tape("current"), complete_events(), layout,
                                               self.tape("directory"), self.count("prefixes"), fields,
                                               lambda prefix, request: self.binding.coefficient(self, definition, prefix, request), self.pool.acquire)
                    self.commit(result, "current")
            finally:
                trace.close()
        if grants is not None:
            self.close_geometry()
            self.call(grants)
            return True
        return False

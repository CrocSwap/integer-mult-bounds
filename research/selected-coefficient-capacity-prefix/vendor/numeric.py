"""One numeric page for one exact raw prefix; never a packet-wide constant."""
from controller import Callback, finite_word
from forms import fallback_form, good_form
from matrices import Matrices
from words import Unsigned, need


class Geometry:
    def __init__(self, plan, index_arena, columns, depth, source_code, parent_identity):
        self.plan = plan
        self.index, self.raw = index_arena, Unsigned(index_arena)
        self.columns = columns
        self.depth, self.source_code, self.parent_identity = depth, source_code, parent_identity
        self.one, self.two = self.index.literal(1), self.index.literal(2)
        self.leaf_cutoff = self.index.literal(64)
        need(not columns.zero(), "positive residual columns")

    def plus(self, a, b):
        out, carry = self.raw.add(a, b)
        need(not carry, "residual address margin")
        return out

    def point(self, field, column):
        base = self.raw.times_small(self.columns, field)
        if field < self.plan.dimension:
            result = self.plus(base, column)
        else:
            last = self.raw.subtract_exact(self.columns, self.one)
            reverse = self.raw.subtract_exact(last, column)
            result = self.plus(base, reverse)
            self.index.free_many(last, reverse)
        self.index.free(base)
        return result

    def close(self):
        self.index.free_many(self.one, self.two, self.leaf_cutoff)


class Page(Geometry):
    def __init__(self, plan, form, ring, index_arena, columns, weight,
                 depth, source_code, parent_identity):
        super().__init__(plan, index_arena, columns, depth, source_code, parent_identity)
        self.form, self.ring, self.weight = form, ring, weight
        if plan.good:
            need((form.dimension, form.rank) == (plan.dimension, plan.rank), "good plan binding")
        else:
            signature = tuple((r.kind, r.target, r.source, r.permutation) for r in form.reductions)
            need(signature == plan.reductions and form.permutation == plan.permutation
                 and form.negative_sign == plan.negative_sign, "full/low fallback itinerary binding")

    def bank(self, row, column):
        if row >= self.plan.dimension:
            return self.ring.arena.copy(self.ring.one)
        base = self.raw.times_small(self.columns, row)
        position = self.plus(base, column)
        result = self.weight(position)
        self.index.free_many(base, position)
        return result

    def ratio(self, scalar, numerator, denominator):
        ring, arena = self.ring, self.ring.arena
        inverse = ring.inverse(denominator)
        need(inverse is not None, "generated adapter denominator unit")
        product = ring.multiply(scalar, numerator)
        result = ring.multiply(product, inverse)
        arena.free_many(numerator, denominator, inverse, product)
        return result

    def coefficient(self, reference, column, reverse=False):
        ring, arena, form = self.ring, self.ring.arena, self.form
        if reference.kind == "head":
            scalar = form.rows[reference.index][2]
        elif reference.kind == "tail":
            scalar = form.columns[reference.index][2]
        elif reference.kind == "cross":
            scalar = form.cross[reference.first][reference.second]
        else:
            need(reference.kind == "shear", "adapter coefficient reference")
            reduction = form.reductions[reference.index]
            need((reduction.target, reduction.source, reduction.permutation) ==
                 (reference.first, reference.second, reference.permutation), "original shear reference")
            scalar = reduction.scalar
        if scalar.zero():
            result = arena.zero()
        elif reference.kind == "tail":
            result = arena.copy(scalar)
        else:
            if reference.kind == "head":
                numerator, denominator = self.bank(reference.first, column), self.bank(reference.second, column)
            elif reference.kind == "cross":
                numerator, denominator = arena.copy(ring.one), self.bank(reference.second, column)
            else:
                numerator = self.bank(reference.permutation[reference.first], column)
                denominator = self.bank(reference.permutation[reference.second], column)
            result = self.ratio(scalar, numerator, denominator)
        if (reference.sign < 0) != reverse:
            opposite = ring.negate(result)
            arena.free(result)
            result = opposite
        return result

    def child_weight(self, kind, field, reverse, index):
        ring, arena = self.ring, self.ring.arena
        if kind == "unit":
            return arena.copy(ring.one)
        if kind == "good":
            quotient, remainder = self.raw.divmod(index, self.columns)
            k = finite_word(quotient, self.plan.rank)
            parent = self.weight(index)
            result = ring.multiply(parent, self.form.pivots[k])
            arena.free(parent)
            self.index.free_many(quotient, remainder)
            return result
        need(kind == "pair" and 0 <= field < 2*self.plan.dimension-1, "pair child field")
        if self.form.permutation[field] == field:
            return arena.copy(self.form.diagonal[field])
        if reverse:
            last = self.raw.subtract_exact(self.columns, self.one)
            column = self.raw.subtract_exact(last, index)
            self.index.free(last)
        else:
            column = self.index.copy(index)
        numerator = self.bank(self.form.permutation[field], column)
        denominator = self.bank(field, column)
        result = self.ratio(self.form.diagonal[field], numerator, denominator)
        self.index.free(column)
        return result

    def close(self):
        self.form.close(self.ring)
        super().close()

    def evaluate(self, request):
        if request.kind == "adapter":
            return self.coefficient(request.reference, request.coordinate, request.reverse_adapter)
        need(request.kind == "child", "symbolic coefficient request")
        value = self.child_weight(request.child_kind, request.field, request.reverse, request.coordinate)
        if request.negative_inverse:
            inverse = self.ring.inverse(value)
            need(inverse is not None, "completed leaf weight unit")
            result = self.ring.negate(inverse)
            self.ring.arena.free_many(value, inverse)
            return result
        return value


def selected_page(plan, ring, index_arena, program, fields, specifications, current_code):
    """Caller closes the returned page and incoming frame at the same prefix."""
    incoming = Callback(ring, index_arena, program, fields, specifications, current_code,
                        allow_fallback=True)
    columns, remainder = incoming.raw.divmod(incoming.final_size, incoming.sixty_four)
    index_arena.free(remainder)
    scope = incoming.plus(incoming.depth, incoming.one_index)
    projector = incoming.prepare(incoming.depth, current_code, scope)
    index_arena.free(scope)
    need(plan.good == specifications[current_code].good, "fixed selected branch")
    form = good_form(projector, plan.rank, ring) if plan.good else fallback_form(projector, ring)
    Matrices(ring).free(projector)
    page = Page(plan, form, ring, index_arena, columns, incoming.weight,
                incoming.depth, current_code, program)
    return page, incoming


def selected_coefficient(plan, ring, index_arena, program, fields, specifications,
                         current_code, request):
    """Closed per-prefix callback for a symbolic trace event, on each pass."""
    need(current_code in specifications and plan.dimension == 64 and
         plan.rank == specifications[current_code].template.rank and
         plan.good == specifications[current_code].good, "selected trace/source binding")
    if request.kind == "child":
        from children import coefficient
        return coefficient(ring, index_arena, program, fields, specifications, current_code, request)
    protected_residues, protected_indices = frozenset(ring.arena.live), frozenset(index_arena.live)
    incoming = None
    try:
        page, incoming = selected_page(plan, ring, index_arena, program, fields, specifications, current_code)
        result = page.evaluate(request)
        page.close()
        index_arena.free(page.columns)
        incoming.close()
        return result
    except ValueError:
        if incoming is not None:
            incoming.abort()
        ring.arena.rollback(protected_residues)
        index_arena.rollback(protected_indices)
        program.tape.rewind()
        fields.tape.rewind()
        raise

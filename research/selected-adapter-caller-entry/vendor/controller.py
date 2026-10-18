"""Encoded selected coefficient/offset callback, including descriptor indices.

Runtime residues, extents, coordinates and generation levels remain words.
Only finite operation/source/rank/row labels enter native control. The loop
refines the retained PR2310/2332 grammar and PR2405 raw-prefix interface.
"""
from matrices import Matrices
from records import BLANK, CONSTANT, MULTIPLY, PAIR, RETURN, VALUE, Stack, seek_record
from words import LEFT, ONE, RIGHT, ZERO, Unsigned, need

GOOD_KIND, PAIR_KIND, UNIT_KIND = range(3)


def finite_word(word, limit):
    """Decode only a provably finite row/pivot label, not a variable index."""
    need(0 < limit <= 128, "finite row-label range")
    word.msb()
    state = 0
    while word.read() != LEFT:
        bit = word.read()
        need(bit in (ZERO, ONE), "finite-selector bit")
        state = (state << 1) | bit
        need(state < limit, "finite-selector extent")
        word.step(-1)
    word.step(1)
    return state


class Callback:
    def __init__(self, ring, index_arena, program, fields, specifications, current_code,
                 allow_fallback=False, leaf=False):
        self.ring, self.residue = ring, ring.arena
        self.index, self.raw = index_arena, Unsigned(index_arena)
        self.program, self.fields, self.specifications = program, fields, specifications
        self.current_code = current_code
        self.leaf = leaf
        self.protected_residues, self.protected_indices = frozenset(self.residue.live), frozenset(self.index.live)
        need(current_code in specifications and (allow_fallback or specifications[current_code].good),
             "selected good current site")
        need(program.code_bits == fields.code_bits and
             all(code == spec.code and 0 <= code < 1 << program.code_bits for code, spec in specifications.items()),
             "one compiled source-code vocabulary")
        self.q = specifications[current_code].template.q
        need(all(spec.template.q == self.q for spec in specifications.values()), "one fixed source prime")
        self.index.template.rewind()
        large_enough = True
        for _ in range(8):
            if self.index.template.read() == RIGHT:
                large_enough = False
                break
            self.index.template.step(1)
        self.index.template.rewind()
        need(large_enough, "internal-site index context has eight bits")
        self.one_index, self.sixty_four = self.index.literal(1), self.index.literal(64)
        self.two_index = self.index.literal(2)
        self.matrices = Matrices(ring)
        self.pending, self.values = Stack(index_arena, self.residue), Stack(index_arena, self.residue)
        self.prepared_codes = set()  # Bounded finite-vocabulary checker observation.
        try:
            self._prime_power_context()
            self._validate_program()
        except ValueError:
            self.abort()
            raise

    def plus(self, a, b):
        value, carry = self.raw.add(a, b)
        need(not carry, "binary index margin")
        return value

    def _prime_power_context(self):
        qword = self.residue.literal(self.q)  # Fixed machine prime, not a runtime residue.
        self.high_cap, remainder = self.ring.raw.divmod(self.ring.modulus, qword)
        need(remainder.zero() and not self.high_cap.zero(), "positive prime-power field cap")
        self.residue.free(remainder)
        test = self.residue.copy(self.high_cap)
        while self.ring.raw.compare(test, self.ring.one) > 0:
            quotient, remainder = self.ring.raw.divmod(test, qword)
            need(remainder.zero(), "modulus is a power of the fixed prime")
            self.residue.free_many(test, remainder)
            test = quotient
        need(self.ring.raw.compare(test, self.ring.one) == 0, "complete prime-power reduction")
        self.residue.free_many(test, qword)

    def step(self, level):
        metadata, parent, child = self.program.step(level)
        kind, code, rank, field, reverse, half = metadata
        need(kind in (GOOD_KIND, PAIR_KIND, UNIT_KIND) and code in self.specifications,
             "selected finite step/source")
        spec = self.specifications[code]
        need(rank == spec.template.rank and 1 <= rank <= 42, "actual selected rank")
        need((kind == GOOD_KIND) == spec.good, "actual low-class branch")
        need(reverse in (0, 1) and half in (0, 1), "finite step flags")
        need(kind == UNIT_KIND or not half, "halving only at unit reset")
        need((kind == PAIR_KIND and field < 127 and reverse == (field >= 64)) or
             (kind != PAIR_KIND and field == 0 and reverse == 0), "physical pair field and reversal")
        f, remainder = self.raw.divmod(parent, self.sixty_four)
        self.index.free(remainder)
        need(not f.zero(), "internal parent extent")
        if kind == GOOD_KIND:
            expected = self.raw.times_small(f, rank)
        elif half:
            expected, remainder = self.raw.divmod(f, self.two_index)
            self.index.free(remainder)
        else:
            expected = self.index.copy(f)
        need(not child.zero() and self.raw.compare(child, expected) == 0 and self.raw.compare(child, parent) < 0,
             "exact proper generated child extent")
        self.index.free(expected)
        return metadata, parent, child, f

    def _validate_program(self):
        self.root_size, self.root_unit, self.depth = self.program.root()
        self.root_size.msb()
        top = self.root_size.read()
        self.root_size.step(-1)
        significant = self.root_size.read()
        self.root_size.rewind()
        need(top == ZERO and significant == ONE, "canonical root-index word extent")
        need(self.raw.compare(self.root_size, self.sixty_four) >= 0, "selected internal root")
        need(self.ring.raw.compare(self.root_unit, self.ring.modulus) < 0, "canonical root unit")
        inv = self.ring.inverse(self.root_unit)
        need(inv is not None, "root coefficient unit")
        self.residue.free(inv)
        current, count = self.index.copy(self.root_size), self.index.zero()
        while self.raw.compare(count, self.depth) < 0:
            level = self.plus(count, self.one_index)
            metadata, parent, child, f = self.step(level)
            need(self.raw.compare(parent, current) == 0, "chronological program extents")
            self.fields.check_code(count, metadata[1])
            self.index.free_many(parent, f, current, count)
            current, count = child, level
        self.index.free(count)
        self.final_size = current
        after = self.plus(self.depth, self.one_index)
        seek_record(self.program.tape, after)
        need(self.program.tape.read() == BLANK, "exact program depth")
        self.program.tape.rewind()
        if self.leaf:
            self.fields.end(self.depth)
        else:
            self.fields.check_code(self.depth, self.current_code)
            self.fields.end(after)
        self.index.free(after)

    def prepare(self, slot, code, scope):
        high = self.fields.read(slot, code, scope)
        for row in high:
            for digit in row:
                need(self.ring.raw.compare(digit, self.high_cap) < 0, "canonical high digit")
        spec = self.specifications[code]
        p = self.matrices.prepare(spec.low, high, self.q, spec.template.preparation, spec.template.rank)
        self.matrices.free(high)
        # Only the checker consumes this finite source-code trace.
        self.prepared_codes.add(code)
        return p

    def weight(self, index):
        need(self.raw.compare(index, self.final_size) < 0, "requested generated coordinate")
        need(self.pending.empty() and self.values.empty(), "empty binary continuation roles")
        self.pending.push(VALUE, self.depth, index)
        while not self.pending.empty():
            tag, operands = self.pending.pop()
            if tag == CONSTANT:
                coefficient, = operands
                self.values.push(RETURN, coefficient)
                self.residue.free(coefficient)
            elif tag == MULTIPLY:
                coefficient, = operands
                value_tag, values = self.values.pop()
                need(value_tag == RETURN, "value-stack tag")
                value, = values
                result = self.ring.multiply(value, coefficient)
                self.values.push(RETURN, result)
                self.residue.free_many(coefficient, value, result)
            elif tag == PAIR:
                coefficient, = operands
                den_tag, den_values = self.values.pop()
                num_tag, num_values = self.values.pop()
                need(den_tag == num_tag == RETURN, "ordered pair value tags")
                denominator, = den_values
                numerator, = num_values
                inv = self.ring.inverse(denominator)
                need(inv is not None, "generated pair denominator unit")
                product = self.ring.multiply(coefficient, numerator)
                result = self.ring.multiply(product, inv)
                self.values.push(RETURN, result)
                self.residue.free_many(coefficient, denominator, numerator, inv, product, result)
            else:
                need(tag == VALUE, "pending value request")
                level, coordinate = operands
                if level.zero():
                    need(self.raw.compare(coordinate, self.root_size) < 0, "root coordinate extent")
                    self.values.push(RETURN, self.root_unit)
                    self.index.free_many(level, coordinate)
                    continue
                metadata, parent, child, f = self.step(level)
                kind, code, rank, field, reverse, _half = metadata
                need(self.raw.compare(coordinate, child) < 0, "recursive coordinate extent")
                if kind == UNIT_KIND:
                    self.values.push(RETURN, self.ring.one)
                else:
                    slot = self.raw.subtract_exact(level, self.one_index)
                    p = self.prepare(slot, code, self.depth)
                    if kind == GOOD_KIND:
                        pivots = self.matrices.good_pivots(p, rank)
                        self.matrices.free(p)
                        quotient, remainder = self.raw.divmod(coordinate, f)
                        pivot = finite_word(quotient, rank)
                        self.pending.push(MULTIPLY, pivots[pivot])
                        self.pending.push(VALUE, slot, coordinate)
                        self.residue.free_many(*pivots)
                        self.index.free_many(quotient, remainder)
                    else:
                        diagonal, permutation = self.matrices.fallback(p)
                        self.matrices.free(p)
                        self.pending.push(PAIR, diagonal[field])
                        if reverse:
                            last = self.raw.subtract_exact(f, self.one_index)
                            column = self.raw.subtract_exact(last, coordinate)
                            self.index.free(last)
                        else:
                            column = self.index.copy(coordinate)
                        for row in (field, permutation[field]):
                            if row < 64:
                                first = self.raw.times_small(f, row)
                                position = self.plus(first, column)
                                self.pending.push(VALUE, slot, position)
                                self.index.free_many(first, position)
                            else:
                                self.pending.push(CONSTANT, self.ring.one)
                        self.residue.free_many(*diagonal)
                        self.index.free(column)
                    self.index.free(slot)
                self.index.free_many(level, coordinate, parent, child, f)
        tag, values = self.values.pop()
        need(tag == RETURN and self.pending.empty() and self.values.empty(), "closed generated evaluation")
        result, = values
        return result

    def coefficient(self, target_row, column, inverse=False):
        need(not self.leaf, "internal coefficient requires a current field")
        need(0 < target_row < 64 and isinstance(target_row, int), "fixed head target row")
        f, remainder = self.raw.divmod(self.final_size, self.sixty_four)
        self.index.free(remainder)
        need(not f.zero() and self.raw.compare(column, f) < 0, "current selected column")
        scope = self.plus(self.depth, self.one_index)
        p = self.prepare(self.depth, self.current_code, scope)
        self.index.free(scope)
        pinv = self.ring.inverse(p[0][0])
        need(pinv is not None, "selected good head pivot")
        ratio = self.ring.multiply(p[target_row][0], pinv)
        ell = self.ring.negate(ratio)
        self.residue.free_many(pinv, ratio)
        self.matrices.free(p)
        base = self.raw.times_small(f, target_row)
        index = self.plus(base, column)
        self.index.free_many(base, f)
        numerator, denominator = self.weight(index), self.weight(column)
        self.index.free(index)
        ainv = self.ring.inverse(denominator)
        need(ainv is not None, "incoming head coefficient unit")
        product = self.ring.multiply(ell, numerator)
        coefficient = self.ring.multiply(product, ainv)
        self.residue.free_many(ell, numerator, denominator, ainv, product)
        if inverse:
            opposite = self.ring.negate(coefficient)
            self.residue.free(coefficient)
            coefficient = opposite
        return coefficient

    def offset(self, target_row, column, source, inverse=False):
        need(self.ring.raw.compare(source, self.ring.modulus) < 0, "canonical source atom")
        coefficient = self.coefficient(target_row, column, inverse)
        result = self.ring.multiply(coefficient, source)
        self.residue.free(coefficient)
        return result

    def close(self):
        need(self.pending.empty() and self.values.empty(), "closed continuation interface")
        self.index.free_many(self.root_size, self.depth, self.final_size,
                             self.one_index, self.sixty_four, self.two_index)
        self.residue.free_many(self.root_unit, self.high_cap)

    def abort(self):
        self.residue.rollback(self.protected_residues)
        self.index.rollback(self.protected_indices)
        self.program.tape.rewind()
        self.fields.tape.rewind()
        for stack in (self.pending, self.values):
            stack.tape.clear()
            stack.reverse.clear()


def selected_offset(ring, index_arena, program, fields, specifications, current_code,
                    target_row, column, source, inverse=False):
    callback = Callback(ring, index_arena, program, fields, specifications, current_code)
    try:
        result = callback.offset(target_row, column, source, inverse)
        prepared = tuple(sorted(callback.prepared_codes))
        callback.close()
        return result, prepared
    except ValueError:
        callback.abort()
        raise

"""Encoded current-child CRT reconstruction and complete right-node update.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
Only finite symbols/carries and fixed register ownership enter host control.
"""

class Arithmetic:
    """New loose-width residue interface; the frozen Ring guard is unchanged."""
    def __init__(self, arena, words):
        self.arena, self.w = arena, words
        self.raw = words.Unsigned(arena)
        self.one = arena.literal(1)

    def admit(self, modulus):
        self.w.need(self.raw.compare(modulus, self.one) > 0, 'CRT modulus exceeds one')
        modulus.msb(); high = modulus.read(); modulus.rewind()
        self.w.need(high == self.w.ZERO, 'CRT modulus high-bit margin')

    def remainder(self, value, modulus):
        quotient, rest = self.raw.divmod(value, modulus)
        self.arena.free(quotient)
        return rest

    def add(self, left, right, modulus):
        total, carry = self.raw.add(left, right)
        self.w.need(not carry, 'modular addition margin')
        if self.raw.compare(total, modulus) >= 0:
            reduced = self.raw.subtract_exact(total, modulus)
            self.arena.free(total); total = reduced
        return total

    def subtract(self, left, right, modulus):
        if self.raw.compare(left, right) >= 0:
            return self.raw.subtract_exact(left, right)
        larger, carry = self.raw.add(left, modulus)
        self.w.need(not carry, 'modular subtraction margin')
        result = self.raw.subtract_exact(larger, right)
        self.arena.free(larger)
        return result

    def multiply(self, left, right, modulus):
        scan, result = self.arena.copy(right), self.arena.zero()
        scan.msb()
        while scan.read() != self.w.LEFT:
            doubled = self.add(result, result, modulus)
            self.arena.free(result); result = doubled
            if scan.read() == self.w.ONE:
                added = self.add(result, left, modulus)
                self.arena.free(result); result = added
            scan.step(-1)
        scan.step(1); self.arena.free(scan)
        return result

    def inverse(self, value, modulus):
        r0, r1 = self.arena.copy(modulus), self.arena.copy(value)
        t0, t1 = self.arena.zero(), self.arena.copy(self.one)
        while not r1.zero():
            quotient, r2 = self.raw.divmod(r0, r1)
            qmod = self.remainder(quotient, modulus)
            product = self.multiply(qmod, t1, modulus)
            t2 = self.subtract(t0, product, modulus)
            self.arena.free_many(quotient, qmod, product, r0, t0)
            r0, r1, t0, t1 = r1, r2, t1, t2
        unit = self.raw.compare(r0, self.one) == 0
        self.arena.free_many(r0, r1, t1)
        if unit: return t0
        self.arena.free(t0)
        return None

    def product(self, left, right):
        scan, result = self.arena.copy(right), self.arena.zero()
        scan.msb()
        while scan.read() != self.w.LEFT:
            doubled, carry = self.raw.add(result, result)
            self.w.need(not carry, 'CRT product word capacity')
            self.arena.free(result); result = doubled
            if scan.read() == self.w.ONE:
                added, carry = self.raw.add(result, left)
                self.w.need(not carry, 'CRT product word capacity')
                self.arena.free(result); result = added
            scan.step(-1)
        scan.step(1); self.arena.free(scan)
        result.msb(); high = result.read(); result.rewind()
        self.w.need(high == self.w.ZERO, 'CRT complete product high-bit margin')
        return result


def produce(arena, left, right, words, records, *, fault=None):
    """Both borrowed streams contain ROOT + two fixed-width words + RECORD_END.

    LEFT is unique at cell zero, RIGHT terminates the stream; heads enter at one.
    Return owned lower/product words and (offset,new-value) records. The right
    prefix includes all preceding right moduli, exactly as source balanced().
    """
    w = words
    w.need(left is not right, 'distinct CRT descriptor roles')
    protected = set(arena.live)
    w.need(arena.capacity == 64 and arena.bits >= 4 and len(protected) <= 8,
           'fixed CRT numerical entry inventory')
    output = records.Tape(); keep = set(); succeeded = False

    def pair(stream):
        w.need(stream.read() == records.ROOT, 'CRT paired descriptor tag')
        stream.step(1)
        modulus = records.read_word(stream, arena)
        value = records.read_word(stream, arena)
        w.need(stream.read() == records.RECORD_END, 'CRT paired descriptor end')
        stream.step(1)
        return modulus, value

    try:
        a = Arithmetic(arena, words)
        lower, prefix = arena.zero(), arena.copy(a.one)
        valid, seen_left = True, False
        while left.read() != w.RIGHT:
            seen_left = True
            modulus, value = pair(left); a.admit(modulus)
            valid = valid and a.raw.compare(value, modulus) < 0
            base = a.remainder(prefix, modulus)
            inverse = a.inverse(base, modulus)
            w.need(inverse is not None, 'pairwise coprime CRT prefix')
            local = a.remainder(lower, modulus)
            scaled = a.multiply(local, inverse, modulus)
            digit = a.remainder(value, modulus)
            adjustment = arena.copy(digit) if fault == 'treat_current_as_original' else a.subtract(digit, scaled, modulus)
            term = a.product(prefix, adjustment)
            updated, carry = a.raw.add(lower, term)
            w.need(not carry, 'CRT reconstruction capacity')
            total = a.product(prefix, modulus)
            arena.free_many(modulus, value, base, inverse, local, scaled, digit,
                            adjustment, term, lower, prefix)
            lower, prefix = updated, total
        w.need(seen_left, 'nonempty current CRT left group')
        if not valid:
            arena.free(lower); lower = arena.zero()
        left_product = arena.copy(prefix)
        seen_right = False
        while right.read() != w.RIGHT:
            seen_right = True
            modulus, value = pair(right); a.admit(modulus)
            base = a.remainder(prefix, modulus)
            inverse = a.inverse(base, modulus)
            w.need(inverse is not None, 'pairwise coprime CRT right prefix')
            local = a.remainder(lower, modulus)
            offset = a.multiply(local, inverse, modulus)
            if fault == 'omit_right_prefix':
                arena.free(offset)
                original_base = a.remainder(left_product, modulus)
                original_inverse = a.inverse(original_base, modulus)
                offset = a.multiply(local, original_inverse, modulus)
                arena.free_many(original_base, original_inverse)
            if a.raw.compare(value, modulus) < 0 or fault == 'rotate_padding':
                canonical = a.remainder(value, modulus)
                updated = a.add(canonical, offset, modulus)
                arena.free(canonical)
            else: updated = arena.copy(value)
            output.append(records.ROOT)
            records.append_word(output, offset); records.append_word(output, updated)
            output.append(records.RECORD_END)
            total = a.product(prefix, modulus)
            arena.free_many(modulus, value, base, inverse, local, offset, updated, prefix)
            prefix = total
        w.need(seen_right, 'nonempty current CRT right group')
        output.append(w.RIGHT); output.rewind()
        keep = {lower.slot, left_product.slot}; succeeded = True
        return dict(lower=lower, product=left_product, stream=output, left_valid=valid)
    finally:
        left.rewind(); right.rewind()
        for slot in tuple(arena.live):
            if slot not in protected and slot not in keep:
                arena.free(arena.words[slot])
        if not succeeded: output.clear()

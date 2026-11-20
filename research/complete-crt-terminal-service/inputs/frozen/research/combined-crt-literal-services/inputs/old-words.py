"""Binary word tapes; unbounded numerical values stay in tape cells.

Only zero/one carry states and fixed register/operation tags enter Python
control. Fixture loading/inspection methods are outside measured execution.
The arena bounds the tape inventory by a compile-time register capacity.
"""
ZERO, ONE, LEFT, RIGHT, BLANK = range(5)


def need(test, message):
    if not test:
        raise ValueError(message)


class Meter:
    __slots__ = ("reads", "writes", "moves", "peak_live", "allocations")

    def __init__(self):
        self.reads = self.writes = self.moves = self.peak_live = self.allocations = 0

    def record(self):
        return {name: getattr(self, name) for name in self.__slots__}


class Word:
    __slots__ = ("arena", "slot", "cells", "head")

    def __init__(self, arena, slot):
        self.arena, self.slot = arena, slot
        self.cells = bytearray([LEFT] + [BLANK]*(arena.bits+1))
        self.head = 1

    def read(self):
        self.arena.meter.reads += 1
        return self.cells[self.head]

    def write(self, symbol):
        need(symbol in (ZERO, ONE, RIGHT, BLANK), "word tape alphabet")
        self.arena.meter.writes += 1
        self.cells[self.head] = symbol

    def step(self, direction):
        need(direction in (-1, 1), "unit word-head movement")
        self.head += direction
        need(0 <= self.head < len(self.cells), "local word boundary")
        self.arena.meter.moves += 1

    def rewind(self):
        self.step(-1)
        while self.read() != LEFT:
            self.step(-1)
        self.step(1)

    def msb(self):
        self.rewind()
        while self.read() != RIGHT:
            self.step(1)
        self.step(-1)

    def zero(self):
        self.rewind()
        nonzero = False
        while True:
            bit = self.read()
            if bit == RIGHT:
                break
            need(bit in (ZERO, ONE), "complete binary word")
            nonzero = nonzero or bit == ONE
            self.step(1)
        self.rewind()
        return not nonzero

    def erase(self):
        self.rewind()
        while self.read() != RIGHT:
            self.write(BLANK)
            self.step(1)
        self.write(BLANK)
        self.rewind()

    def inspect(self):
        """Checker-only decoding; arithmetic code must not call this."""
        need(self.head == 1 and self.cells[-1] == RIGHT, "inspect a restored word")
        return sum(bit << i for i, bit in enumerate(self.cells[1:-1]))


class Arena:
    def __init__(self, bits, capacity=65536):
        need(bits >= 2 and capacity > 0, "fixed word context")
        self.bits, self.capacity = bits, capacity
        self.meter = Meter()
        self.words, self.available, self.live = [], [], set()
        self.template = Word(self, -1)
        self.template.cells[1:-1] = bytes([ZERO])*bits
        self.template.cells[-1] = RIGHT

    def zero(self):
        if self.available:
            slot = self.available.pop()
            out = self.words[slot]
        else:
            slot = len(self.words)
            need(slot < self.capacity, "fixed register inventory")
            out = Word(self, slot)
            self.words.append(out)
        need(slot not in self.live, "fresh numerical register")
        self.live.add(slot)
        self.meter.allocations += 1
        self.meter.peak_live = max(self.meter.peak_live, len(self.live))
        source = self.template
        source.rewind()
        while source.read() != RIGHT:
            need(out.read() == BLANK, "erased register before reuse")
            out.write(ZERO)
            out.step(1)
            source.step(1)
        need(out.read() == BLANK, "erased right delimiter cell")
        out.write(RIGHT)
        out.rewind()
        source.rewind()
        return out

    def literal(self, value):
        """Compile-time literal only; never decode a runtime word here."""
        need(isinstance(value, int) and value >= 0, "unsigned literal")
        out = self.zero()
        for bit in tuple((value >> i) & 1 for i in range(value.bit_length())):
            need(out.read() != RIGHT, "literal fits the fixed word")
            out.write(bit)
            out.step(1)
        out.rewind()
        return out

    def input(self, value):
        """Fixture-only loading of an encoded input word."""
        return self.literal(value)

    def copy(self, source):
        need(source.arena is self, "one word extent")
        out = self.zero()
        source.rewind()
        while source.read() != RIGHT:
            out.write(source.read())
            source.step(1)
            out.step(1)
        out.rewind()
        source.rewind()
        return out

    def free(self, word):
        need(word.arena is self and word.slot in self.live, "owned numerical register")
        word.erase()
        self.live.remove(word.slot)
        self.available.append(word.slot)

    def free_many(self, *words):
        for word in words:
            self.free(word)

    def rollback(self, protected):
        """Erase owned temporary roles on a rejecting path; capacity is fixed."""
        for slot in tuple(self.live):
            if slot not in protected:
                self.free(self.words[slot])
        for slot in protected:
            self.words[slot].rewind()


class Unsigned:
    def __init__(self, arena):
        self.arena = arena

    def compare(self, a, b):
        need(a.arena is b.arena is self.arena, "comparison word context")
        if a is b:
            return 0
        a.rewind()
        b.rewind()
        state = 0
        while a.read() != RIGHT:
            x, y = a.read(), b.read()
            need(x in (ZERO, ONE) and y in (ZERO, ONE), "comparison binary digits")
            if x != y:
                state = 1 if x == ONE else -1
            a.step(1)
            b.step(1)
        need(b.read() == RIGHT, "equal comparison extents")
        a.rewind()
        b.rewind()
        return state

    def add(self, a, b):
        out = self.arena.zero()
        a.rewind()
        b.rewind()
        carry = 0
        while a.read() != RIGHT:
            x, y = a.read(), b.read()
            total = x+y+carry  # Four finite carry states, not word arithmetic.
            out.write(total & 1)
            carry = total >> 1
            a.step(1)
            if b is not a:
                b.step(1)
            out.step(1)
        need(b.read() == RIGHT, "equal addition extents")
        a.rewind()
        b.rewind()
        out.rewind()
        return out, carry

    def subtract(self, a, b):
        out = self.arena.zero()
        a.rewind()
        b.rewind()
        borrow = 0
        while a.read() != RIGHT:
            x, y = a.read(), b.read()
            digit = x-y-borrow  # One finite borrow bit.
            out.write(digit & 1)
            borrow = int(digit < 0)
            a.step(1)
            if b is not a:
                b.step(1)
            out.step(1)
        need(b.read() == RIGHT, "equal subtraction extents")
        a.rewind()
        b.rewind()
        out.rewind()
        return out, borrow

    def subtract_exact(self, a, b):
        out, borrow = self.subtract(a, b)
        need(not borrow, "unsigned subtraction precondition")
        return out

    def shift_add_bit(self, a, bit):
        need(bit in (ZERO, ONE), "one incoming bit")
        out = self.arena.zero()
        a.rewind()
        carry = bit
        while a.read() != RIGHT:
            previous = a.read()
            out.write(carry)
            carry = previous
            a.step(1)
            out.step(1)
        a.rewind()
        out.rewind()
        need(not carry, "reserved high-bit margin")
        return out

    def divmod(self, numerator, denominator):
        need(not denominator.zero(), "nonzero binary divisor")
        # A zero high bit leaves room for 2*remainder+bit.
        denominator.msb()
        margin = denominator.read()
        denominator.rewind()
        need(margin == ZERO, "binary divisor has the high-bit margin")
        scan = self.arena.copy(numerator)
        quotient, remainder = self.arena.zero(), self.arena.zero()
        scan.msb()
        quotient.msb()
        while scan.read() != LEFT:
            shifted = self.shift_add_bit(remainder, scan.read())
            self.arena.free(remainder)
            if self.compare(shifted, denominator) >= 0:
                remainder = self.subtract_exact(shifted, denominator)
                self.arena.free(shifted)
                quotient.write(ONE)
            else:
                remainder = shifted
                quotient.write(ZERO)
            scan.step(-1)
            quotient.step(-1)
        scan.step(1)
        quotient.step(1)
        self.arena.free(scan)
        return quotient, remainder

    def times_small(self, a, constant):
        """Multiply by a fixed finite matrix/rank label; preserve the word margin."""
        need(0 <= constant <= 128, "finite index multiplier")
        result = self.arena.zero()
        for bit in tuple((constant >> i) & 1 for i in range(constant.bit_length()-1, -1, -1)):
            doubled, carry = self.add(result, result)
            need(not carry, "index multiplication margin")
            self.arena.free(result)
            if bit:
                result, carry = self.add(doubled, a)
                need(not carry, "index multiplication extent")
                self.arena.free(doubled)
            else:
                result = doubled
        return result

    def increment_in_place(self, word):
        """Ripple increment for a bounded address counter; restore its head."""
        word.rewind()
        while word.read() == ONE:
            word.write(ZERO)
            word.step(1)
        need(word.read() == ZERO, "ripple increment has space")
        word.write(ONE)
        word.rewind()


class Ring:
    """Canonical residues modulo an encoded M>1 with one leading zero bit."""
    def __init__(self, modulus):
        self.modulus, self.arena = modulus, modulus.arena
        self.raw = Unsigned(self.arena)
        self.one = self.arena.literal(1)
        try:
            need(self.raw.compare(modulus, self.one) > 0, "modulus exceeds one")
            modulus.msb()
            margin = modulus.read()
            modulus.step(-1)
            significant = modulus.read()
            modulus.rewind()
            need(margin == ZERO and significant == ONE, "canonical modulus word with one high-bit margin")
        except ValueError:
            self.arena.free(self.one)
            raise

    def close(self):
        self.arena.free(self.one)

    def add(self, a, b):
        total, carry = self.raw.add(a, b)
        need(not carry, "canonical modular addition margin")
        if self.raw.compare(total, self.modulus) >= 0:
            out = self.raw.subtract_exact(total, self.modulus)
            self.arena.free(total)
            return out
        return total

    def subtract(self, a, b):
        if self.raw.compare(a, b) >= 0:
            return self.raw.subtract_exact(a, b)
        larger, carry = self.raw.add(a, self.modulus)
        need(not carry, "canonical modular subtraction margin")
        out = self.raw.subtract_exact(larger, b)
        self.arena.free(larger)
        return out

    def negate(self, a):
        zero = self.arena.zero()
        out = self.subtract(zero, a)
        self.arena.free(zero)
        return out

    def multiply(self, a, b):
        if a.zero() or b.zero():
            return self.arena.zero()
        if self.raw.compare(a, self.one) == 0:
            return self.arena.copy(b)
        if self.raw.compare(b, self.one) == 0:
            return self.arena.copy(a)
        scan = self.arena.copy(b)
        result = self.arena.zero()
        scan.msb()
        while scan.read() != LEFT:
            doubled = self.add(result, result)
            self.arena.free(result)
            if scan.read() == ONE:
                result = self.add(doubled, a)
                self.arena.free(doubled)
            else:
                result = doubled
            scan.step(-1)
        scan.step(1)
        self.arena.free(scan)
        return result

    def inverse(self, a):
        """Euclid, with Bezout coefficients reduced modulo M; None for nonunits."""
        r0, r1 = self.arena.copy(self.modulus), self.arena.copy(a)
        t0, t1 = self.arena.zero(), self.arena.copy(self.one)
        while not r1.zero():
            quotient, r2 = self.raw.divmod(r0, r1)
            if self.raw.compare(quotient, self.modulus) >= 0:
                reduced = self.raw.subtract_exact(quotient, self.modulus)
                self.arena.free(quotient)
                quotient = reduced
            product = self.multiply(quotient, t1)
            t2 = self.subtract(t0, product)
            self.arena.free_many(quotient, product, r0, t0)
            r0, r1, t0, t1 = r1, r2, t1, t2
        unit = self.raw.compare(r0, self.one) == 0
        self.arena.free_many(r0, r1, t1)
        if unit:
            return t0
        self.arena.free(t0)
        return None

    def literal(self, constant):
        """Compile a fixed signed integer through binary modular operations."""
        negative = constant < 0
        magnitude = abs(constant)
        result = self.arena.zero()
        instructions = tuple((magnitude >> i) & 1 for i in range(magnitude.bit_length()-1, -1, -1))
        for bit in instructions:
            doubled = self.add(result, result)
            self.arena.free(result)
            if bit:
                result = self.add(doubled, self.one)
                self.arena.free(doubled)
            else:
                result = doubled
        if negative:
            out = self.negate(result)
            self.arena.free(result)
            result = out
        return result

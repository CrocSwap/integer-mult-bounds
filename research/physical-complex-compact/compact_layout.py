"""A fixed field schema with encoded widths, extents and address states."""
import native_sources
native_sources.activate()
from compact_counts import power_two
from cardinal_counts import Count, positive
from encoded import compare, divide, subtract
from words import need


class Layout:
    def __init__(self, names, widths, record_bits):
        # The field count/order is compiled, not an input-dependent collection.
        need(type(names) is tuple and len(names) == len(set(names)) and len(names) == len(widths),
             "fixed unique field vocabulary")
        self.names, self.widths, self.record_bits = names, widths, record_bits
        positive(record_bits)
        self.bits = Count.literal(0)
        self.radices = {}
        for name, width in zip(names, widths):
            need(isinstance(width,Count), "encoded field width")
            self.bits.add(width)
            self.radices[name] = power_two(width)
        self.records = power_two(self.bits)
        self.row_bits = Count.product(self.records, record_bits)

    def width(self, name):
        return self.widths[self.names.index(name)]

    def sum_widths(self, names):
        result = Count.literal(0)
        for name in names:
            result.add(self.width(name))
        return result

    def decode(self, address):
        need(compare(address, self.records) < 0, "complete local-row address")
        current, state = Count(address), {}
        try:
            for name in reversed(self.names):
                following, state[name] = divide(current, self.radices[name])
                current.close()
                current = following
            need(current.zero(), "complete fixed-field decomposition")
            return state
        except BaseException:
            self.close_state(state)
            raise
        finally:
            current.close()

    def encode(self, state):
        result = Count.literal(0)
        try:
            for name in self.names:
                need(compare(state[name], self.radices[name]) < 0, "canonical encoded field")
                following = Count.product(result, self.radices[name])
                result.close()
                result = following
                result.add(state[name])
            return result
        except BaseException:
            result.close()
            raise

    def prefix_state(self, prefix, target):
        before = self.names[:self.names.index(target)]
        current, state = Count(prefix), {}
        try:
            for name in reversed(before):
                following, state[name] = divide(current, self.radices[name])
                current.close()
                current = following
            need(current.zero(), "complete rotation prefix")
            for name in self.names[len(before):]:
                state[name] = Count.literal(0)
            return state
        except BaseException:
            self.close_state(state)
            raise
        finally:
            current.close()

    @staticmethod
    def close_state(state):
        for value in state.values():
            value.close()

    def single_extents(self, field):
        at = self.names.index(field)
        before_bits = self.sum_widths(self.names[:at])
        after_bits = self.sum_widths(self.names[at+1:])
        before, after = power_two(before_bits), power_two(after_bits)
        try:
            return before, Count.product(after, self.record_bits)
        finally:
            before_bits.close()
            after_bits.close()
            after.close()

    def paired_extents(self, first, second):
        i, j = sorted((self.names.index(first), self.names.index(second)))
        need(i != j, "distinct ordinary compact fields")
        before_bits = self.sum_widths(self.names[:i])
        middle_bits = self.sum_widths(self.names[i+1:j])
        after_bits = self.sum_widths(self.names[j+1:])
        before, middle, after = power_two(before_bits), power_two(middle_bits), power_two(after_bits)
        try:
            return before, middle, Count.product(after, self.record_bits)
        finally:
            before_bits.close()
            middle_bits.close()
            after_bits.close()
            after.close()

    def bit_position(self, field, low_bit):
        """An encoded position counted from the left of the complete address."""
        need(compare(low_bit, self.width(field)) < 0, "selected field bit exists")
        ending = self.sum_widths(self.names[:self.names.index(field)+1])
        one = Count.literal(1)
        try:
            rest = subtract(ending, low_bit)
            try:
                return subtract(rest, one)
            finally:
                rest.close()
        finally:
            ending.close()
            one.close()

    def close(self):
        for value in (*self.radices.values(), self.bits, self.records, self.row_bits):
            value.close()

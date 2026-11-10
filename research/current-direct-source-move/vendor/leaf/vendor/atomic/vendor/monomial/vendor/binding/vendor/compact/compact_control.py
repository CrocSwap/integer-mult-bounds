"""Encoded modular offsets, inverse states and the retained compact guard."""
import native_sources
_source, reference = native_sources.activate()
from compact_counts import (add_mod, bit_at, bit_slice, bit_xor, negate_mod,
                           power_two, reduced, shifted)
from cardinal_counts import Count, positive
from encoded import compare, subtract
from stream import Counter
from words import need


class Control:
    def __init__(self, n, K, G, rho, source, target, late=False):
        self.n, self.K, self.G, self.rho = n, K, G, rho
        self.source, self.target, self.late = source, target, late
        # Only names/order flags enter this fixed compiler. The dummy numerical
        # constants are unused by the authenticated operations() method.
        self.operations = reference.Compact(1,1,1,0,source,target,late).operations()

    def validate(self, layout):
        for value in (self.n,self.K,self.G):
            positive(value)
        need(compare(self.rho,self.K) < 0, "selected residue lies in each wide chunk")
        need(self.target not in ("u","t","b") and self.source not in ("u","t","b",self.target),
             "distinct wide source/target and compact fields")
        axes = Count(self.n)
        axes.increment()
        wide, compact = Count.product(axes,self.K), Count.product(self.n,self.G)
        try:
            need(compare(layout.width(self.target),wide) == 0, "complete wide target")
            need(all(compare(layout.width(name),compact) == 0 for name in ("u","t","b")),
                 "three complete equal compact fields")
            at = layout.names.index(self.target)
            need(layout.names.index("u") < at and layout.names.index("t") < at < layout.names.index("b"),
                 "front/back compact placement")
            if self.source is None:
                need(not self.late, "constant toggle uses the early word")
            else:
                need(compare(layout.width(self.source),wide) == 0 and
                     ((layout.names.index(self.source) > at) == self.late), "declared wide source order")
            for operation in self.operations:
                if operation[0] == "rotate":
                    target, controls = operation[1:3]
                    need(all(layout.names.index(name) < layout.names.index(target) for name in controls),
                         "rotation reads only its preceding fields")
        finally:
            axes.close()
            wide.close()
            compact.close()

    def selected(self, value):
        """Pack the low n selected bits into the low bit of each G-bit digit."""
        result, position, weight = Count.literal(0), Count(self.rho), Count.literal(1)
        remaining = Counter(self.n)
        try:
            while not remaining.finished:
                if bit_at(value,position):
                    result.add(weight)
                position.add(self.K)
                following = shifted(weight,self.G)
                weight.close()
                weight = following
                remaining.decrement()
            return result
        except BaseException:
            result.close()
            raise
        finally:
            position.close()
            weight.close()
            remaining.close()

    def mask(self, state, compact=False, highest=False):
        source = "u" if compact else self.source
        source_position = Count.literal(0) if compact else Count(self.rho)
        weight = power_two(self.rho)
        result, axes = Count.literal(0), Count(self.n)
        if highest:
            axes.increment()
        remaining = Counter(axes)
        axes.close()
        try:
            while not remaining.finished:
                if source is None or bit_at(state[source],source_position):
                    result.add(weight)
                source_position.add(self.G if compact else self.K)
                following = shifted(weight,self.K)
                weight.close()
                weight = following
                remaining.decrement()
            return result
        except BaseException:
            result.close()
            raise
        finally:
            source_position.close()
            weight.close()
            remaining.close()

    def offset(self, state, operation, layout):
        _tag,target,_controls,kind,sign = operation
        modulus = layout.radices[target]
        result = None
        if kind in ("selected_x","selected_y"):
            result = self.selected(state[self.source if kind == "selected_x" else self.target])
        elif kind.startswith("original"):
            mask = self.mask(state,kind.endswith("compact"))
            original = bit_xor(state[self.target],mask)
            mask.close()
            try:
                result = self.selected(original)
            finally:
                original.close()
        else:
            need(kind.startswith("first") or kind.startswith("second"), "compiled compact rotation kind")
            compact = kind.endswith("compact")
            source = "u" if compact else self.source
            source_position = Count.literal(0) if compact else Count(self.rho)
            compact_position, wide_position = Count.literal(0), Count(self.rho)
            remaining, result = Counter(self.n), Count.literal(0)
            one = Count.literal(1)
            try:
                while not remaining.finished:
                    if source is None or bit_at(state[source],source_position):
                        digit = bit_slice(state["t"],compact_position,self.G)
                        negative = kind.startswith("second") and not digit.zero()
                        if kind.startswith("first"):
                            term = Count(digit)
                            term.multiply_small(2)
                        elif digit.zero():
                            term = Count.literal(1)
                        else:
                            twice = Count(digit)
                            twice.multiply_small(2)
                            term = subtract(twice,one)
                            twice.close()
                        digit.close()
                        following = shifted(term,wide_position)
                        term.close()
                        term = reduced(following,modulus)
                        following.close()
                        if negative:
                            following = negate_mod(term,modulus)
                            term.close()
                            term = following
                        following = add_mod(result,term,modulus)
                        result.close()
                        term.close()
                        result = following
                    source_position.add(self.G if compact else self.K)
                    compact_position.add(self.G)
                    wide_position.add(self.K)
                    remaining.decrement()
            except BaseException:
                result.close()
                raise
            finally:
                for value in (source_position,compact_position,wide_position,remaining,one):
                    value.close()
        try:
            canonical = reduced(result,modulus)
        finally:
            result.close()
        if sign < 0:
            result = negate_mod(canonical,modulus)
            canonical.close()
            canonical = result
        return canonical

    def execute_state(self, state, layout, inverse=False):
        """Mutate a fixed tuple of encoded fields, with current inverse controls."""
        for operation in reversed(self.operations) if inverse else self.operations:
            if operation[0] == "swap":
                first,second = operation[1:]
                state[first],state[second] = state[second],state[first]
                continue
            target = operation[1]
            offset = self.offset(state,operation,layout)
            try:
                if inverse:
                    following = negate_mod(offset,layout.radices[target])
                    offset.close()
                    offset = following
                following = add_mod(state[target],offset,layout.radices[target])
            finally:
                offset.close()
            state[target].close()
            state[target] = following

    def ideal_state(self, state, highest=False):
        mask = self.mask(state,highest=highest)
        try:
            following = bit_xor(state[self.target],mask)
        finally:
            mask.close()
        state[self.target].close()
        state[self.target] = following

    def bad(self, state):
        one = Count.literal(1)
        guard_width = subtract(self.K,one)
        base, guard_radix = power_two(self.G), power_two(guard_width)
        maximum = subtract(base,one)
        lower, twice_lower = Count(base), Count(base)
        lower.multiply_small(2)
        twice_lower.multiply_small(4)
        upper = compact_position = wide_position = remaining = None
        try:
            if compare(guard_radix,twice_lower) <= 0:
                return True
            upper = subtract(guard_radix,lower)
            compact_position, wide_position = Count.literal(0), Count(self.rho)
            wide_position.increment()
            remaining = Counter(self.n)
            while not remaining.finished:
                for name in (("t","u") if self.late else ("t",)):
                    digit = bit_slice(state[name],compact_position,self.G)
                    saturated = compare(digit,maximum) == 0
                    digit.close()
                    if saturated:
                        return True
                guard = bit_slice(state[self.target],wide_position,guard_width)
                outside = compare(guard,lower) < 0 or compare(guard,upper) >= 0
                guard.close()
                if outside:
                    return True
                compact_position.add(self.G)
                wide_position.add(self.K)
                remaining.decrement()
            return False
        finally:
            for value in (one,guard_width,base,guard_radix,maximum,lower,twice_lower,
                          upper,compact_position,wide_position,remaining):
                if value is not None:
                    value.close()

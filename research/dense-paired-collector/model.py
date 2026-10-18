"""Finite complete-array model; the fast tape tariff is a written construction.

This model invokes the frozen PR3109 direct semantic oracle. It does not emit
or benchmark the selected all-size backend or a reversible machine trace.
"""
from sources import load, need

SOURCE = load()
CORE, OLD = SOURCE["core"], SOURCE["old"]


class Executor:
    def __init__(self, n, width, d=2, spacing=2, suffix=1, outer=3):
        need(all(type(x) is int for x in (n, width, d, spacing, suffix, outer)), "integer finite parameters")
        need(1 <= n <= 10 and width >= 8 and d >= 1 and spacing >= 1 and 0 <= suffix <= n and outer >= 1,
             "bounded finite macro domain")
        self.n, self.width = n, width
        self.d, self.spacing, self.suffix, self.outer = d, spacing, suffix, outer
        self.counts = dict(fast_lifts=0, inner_oracles=0, dense_linear_oracles=0, address_oracles=0, address_gates=0, outer_blocks=0)

    def split_axes(self, axes):
        need(axes and tuple(axes) == tuple(range(axes[0], axes[-1]+1)) and 0 <= axes[0] <= axes[-1] < self.n,
             "one contiguous active interval")
        first, stop = max(axes[0], self.suffix), axes[-1]+1
        first = min(first, stop)
        chunks = (stop-first)//self.spacing
        blocks = []
        for base in range(0, chunks, self.d):
            height = min(self.d, chunks-base)
            for offset in range(self.spacing):
                blocks.append(tuple(first+(base+j)*self.spacing+offset for j in range(height)))
        direct = tuple(range(first+chunks*self.spacing, stop))+tuple(axis for axis in axes if axis < self.suffix)
        need(sorted([axis for block in blocks for axis in block]+list(direct)) == list(axes), "offset plan partitions actual interval")
        return tuple(blocks), direct

    def fast_lift(self, values, axes, inverse=False):
        """PR3109 construction, with an explicit active-field offset."""
        need(len(values) == 1 << self.n, "complete ambient batch")
        self.counts["fast_lifts"] += 1
        blocks, direct = self.split_axes(axes)
        result, oracle = list(values), CORE.DirectOracle()
        if inverse:
            result = CORE.lifted(result, direct, True)
        for block in reversed(blocks) if inverse else blocks:
            result = CORE.inplace_block(result, block, self.width, oracle, inverse)
        if not inverse:
            result = CORE.lifted(result, direct)
        self.counts["inner_oracles"] += len(oracle.calls)
        return result

    def dense_linear(self, source, target, axes, width, inverse=False):
        """Exact 2**g U on arbitrary integers, using only period inputs."""
        self.counts["dense_linear_oracles"] += 1
        g = len(axes)//2+1
        fine = shift(source, g)
        sent = self.fast_lift(fine, axes, inverse)
        result = CORE.xor_words(target, CORE.encode(sent, width))
        returned = self.fast_lift(sent, axes, not inverse)
        need(returned == fine, "period backend restores fine source")
        need(CORE.xor_words(CORE.encode(returned, self.width), CORE.encode(fine, self.width)) == [(0, 0)]*len(source),
             "period source uncopy")
        return result

    def original_lift(self, values, axes, inverse=False):
        blocks = tuple(tuple(axes[i:i+self.outer]) for i in range(0, len(axes), self.outer))
        executor = self
        class DenseOracle:
            def apply(self, source, target, block, width, inverse=False):
                return executor.dense_linear(source, target, block, width, inverse)
        oracle = DenseOracle()
        result = list(values)
        for block in reversed(blocks) if inverse else blocks:
            result = CORE.inplace_block(result, block, self.width, oracle, inverse)
            self.counts["outer_blocks"] += 1
        return result

    def address_word(self, values, target_axes, control_axes=None, inverse=False):
        if control_axes is None:
            result = self.fast_lift(values, target_axes, inverse)
            return self.fast_lift(result, target_axes, inverse)
        if inverse:
            result = character(values, control_axes, negative=True)
            result = self.fast_lift(result, target_axes, True)
            result = character(result, control_axes, target_axes)
            result = self.fast_lift(result, target_axes)
            return character(result, control_axes, target_axes)
        result = character(values, control_axes, target_axes)
        result = self.fast_lift(result, target_axes, True)
        result = character(result, control_axes, target_axes)
        result = self.fast_lift(result, target_axes)
        return character(result, control_axes)

    def address_oracle(self, source, target, target_axes, control_axes=None, omit_phase=False, guard=None):
        self.counts["address_oracles"] += 1
        need(control_axes is None or (len(control_axes) == len(target_axes) and not set(control_axes)&set(target_axes)),
             "disjoint matched address fields")
        g = len(target_axes)//2+1
        reserve = 2*g if guard is None else guard
        fine = shift(source, reserve)
        sent = self.address_word(fine, target_axes, control_axes)
        if omit_phase and control_axes is not None:
            sent = character(sent, control_axes, negative=True)
        extracted = shift(sent, -reserve)
        result = CORE.xor_words(target, CORE.encode(extracted, self.width))
        returned = self.address_word(sent, target_axes, control_axes, True)
        need(returned == fine, "literal dense address inverse restores fine bank")
        need(CORE.xor_words(CORE.encode(returned, self.width), CORE.encode(fine, self.width)) == [(0, 0)]*len(source),
             "dense address source uncopy")
        return result

    def address_gate(self, values, target_axes, control_axes=None):
        zero = [(0, 0)]*len(values)
        result = self.address_oracle(values, zero, target_axes, control_axes)
        original = self.address_oracle(CORE.decode(result, self.width), CORE.encode(values, self.width), target_axes, control_axes)
        need(original == zero, "involutive address oracle clears old bank")
        self.counts["address_gates"] += 1
        return CORE.decode(result, self.width)

    def monomial(self, values, recipe, multiplicity=1, inverse=False):
        m = len(recipe["matrix_rows"])
        need(m*multiplicity == self.n, "dense field-major monomial domain")
        word = SOURCE["binary_word"](recipe)
        result = list(values)
        if not inverse:
            result = recipe_phase(result, recipe, multiplicity)
        for op, target, source in reversed(word) if inverse else word:
            target_axes = tuple(range(target*multiplicity, (target+1)*multiplicity))
            source_axes = None if op == "flip" else tuple(range(source*multiplicity, (source+1)*multiplicity))
            result = self.address_gate(result, target_axes, source_axes)
        if inverse:
            result = recipe_phase(result, recipe, multiplicity, True)
        return result

    def native(self, values, recipe, multiplicity=1, inverse=False):
        axes = tuple(range(recipe["rank"]*multiplicity))
        if inverse:
            result = self.monomial(values, recipe["left"], multiplicity, True)
            result = self.original_lift(result, axes, True)
            return self.monomial(result, recipe["right"], multiplicity, True)
        result = self.monomial(values, recipe["right"], multiplicity)
        result = self.original_lift(result, axes)
        return self.monomial(result, recipe["left"], multiplicity)


def shift(values, bits):
    if bits >= 0:
        return [(a << bits, b << bits) for a, b in values]
    divisor = 1 << -bits
    need(all(value % divisor == 0 for pair in values for value in pair), "exact guarded output shift")
    return [(a//divisor, b//divisor) for a, b in values]


def character(values, controls, targets=None, negative=False):
    result = []
    for index, value in enumerate(values):
        phase = sum((index >> axis)&1 for axis in controls) if targets is None else \
                2*sum(((index >> c)&1)*((index >> t)&1) for c, t in zip(controls, targets, strict=True))
        result.append(OLD["rot"](value, -phase if negative else phase))
    return result


def recipe_phase(values, recipe, multiplicity, inverse=False):
    result = []
    m = len(recipe["matrix_rows"])
    for index, value in enumerate(values):
        phase = multiplicity*recipe["phase"]
        for column in range(multiplicity):
            bits = [(index >> (i*multiplicity+column))&1 for i in range(m)]
            phase += sum(bits[i]*recipe["linear_Z4"][i] for i in range(m))
            phase += 2*sum(bits[i]*bits[j]*((recipe["quadratic_rows"][i] >> j)&1)
                           for i in range(m) for j in range(i+1, m))
        result.append(OLD["rot"](value, -phase if inverse else phase))
    return result


def collector(executor, sources, query, f, beta, recipe, multiplicity=1):
    need(len(sources) == 5 and all(len(source) == len(query) == 1 << executor.n for source in sources), "actual five-source collector shape")
    need(type(f) is type(beta) is int and f >= 0 and beta >= 0, "nonnegative collector grid and accuracy")
    total = [(0, 0)]*len(query)
    for source in sources:
        total = [(a+c, b+d) for (a, b), (c, d) in zip(total, source, strict=True)]
    maximum = max(abs(value) for pair in total for value in pair)
    rank = recipe["rank"]*multiplicity
    gamma = (rank-1).bit_length()+executor.n//2
    grid = f if maximum == 0 else max(f, beta+1+gamma-(maximum.bit_length()-1-f))
    fine = shift(total, grid-f)
    sent = executor.native(fine, recipe, multiplicity)
    promoted = shift(query, grid-f)
    updated = [(a+c, b+d) for (a, b), (c, d) in zip(promoted, sent, strict=True)]
    returned = executor.native(sent, recipe, multiplicity, True)
    need(returned == fine, "paired actual native return")
    restored = shift(returned, f-grid)
    private = list(restored)
    for source in reversed(sources):
        private = [(a-c, b-d) for (a, b), (c, d) in zip(private, source, strict=True)]
    need(private == [(0, 0)]*len(query), "literal collector zero after ungather")
    return dict(query=updated, grid=grid, private=private, sent=sent, returned=returned, entrance=total)

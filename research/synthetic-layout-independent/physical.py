"""Literal prefix moves, chunk swaps, and physical synthetic-transform rounds.

All arithmetic is integral. Omit each butterfly's factor 1/2 and return
M times the normalized transform; one axis contributes a_i butterflies.
No source implementation, direct Fourier formula, or reference oracle is used.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plan(ell, width, long_axes):
    require(isinstance(ell, int) and ell >= 2, 'ell must be at least two')
    require(isinstance(width, int) and 1 <= width < ell, 'invalid chunk width')
    require(long_axes and all(type(x) is bool for x in long_axes), 'invalid axes')
    lengths = [ell if long else ell - 1 for long in long_axes]
    original = [(i, h) for i, a in enumerate(lengths) for h in range(a - 1, -1, -1)]
    slots = original.copy()
    remainder = (ell - 1) % width
    prefix = [(i, ell - 1) for i, long in enumerate(long_axes) if long]
    prefix += [(i, h) for h in range(remainder - 1, -1, -1) for i in range(len(lengths))]
    operations = []
    for target, slot in enumerate(prefix):
        source = slots.index(slot)
        if source != target:
            slots.insert(target, slots.pop(source))
            operations.append(('move', source, target, 1))
    start = len(prefix)
    chunks = [slots[j:j + width] for j in range(start, len(slots), width)]
    q = (ell - 1) // width
    desired = [chunks[i * q + j] for j in range(q) for i in range(len(lengths))]
    swaps = 0
    for target in range(len(chunks) - 1):
        source = chunks.index(desired[target])
        if source != target:
            chunks[source], chunks[target] = chunks[target], chunks[source]
            operations.append(('swap', start + source * width, start + target * width, width))
            swaps += 1
    slots = prefix + [slot for chunk in chunks for slot in chunk]
    require(swaps <= len(lengths) * q - 1, 'chunk swap count exceeded')
    return {'ell': ell, 'width': width, 'long_axes': tuple(long_axes),
            'lengths': lengths, 'original': original, 'slots': slots,
            'operations': operations, 'prefix_length': start, 'swaps': swaps,
            'prefix_moves': sum(op[0] == 'move' for op in operations)}


def move_address(index, bits, operation):
    """One literal move or chunk exchange, positions counted from the MSB."""
    kind, source, target, width = operation
    if kind == 'swap':
        low_source, low_target = bits - source - width, bits - target - width
        mask = (1 << width) - 1
        difference = ((index >> low_source) ^ (index >> low_target)) & mask
        return index ^ (difference << low_source) ^ (difference << low_target)
    require(kind == 'move' and width == 1, 'unknown layout operation')
    source_low, target_low = bits - 1 - source, bits - 1 - target
    selected = (index >> source_low) & 1
    # Remove the source bit and insert it at its destination in the shorter word.
    removed = (index & ((1 << source_low) - 1)) | ((index >> (source_low + 1)) << source_low)
    return ((removed & ((1 << target_low) - 1)) | (selected << target_low)
            | ((removed >> target_low) << (target_low + 1)))


def inverse_operations(operations):
    return [(kind, target, source, width) for kind, source, target, width in reversed(operations)]


def layout_address(index, schedule, inverse=False):
    bits = len(schedule['slots'])
    operations = schedule['operations']
    if inverse:
        operations = inverse_operations(operations)
    for operation in operations:
        index = move_address(index, bits, operation)
    return index


def relocate(data, schedule, inverse=False):
    """Execute every charged movement, preserving each whole polynomial record."""
    out = [row.copy() for row in data]
    operations = schedule['operations']
    if inverse:
        operations = inverse_operations(operations)
    for operation in operations:
        moved = [None] * len(out)
        for index, row in enumerate(out):
            moved[move_address(index, len(schedule['slots']), operation)] = row
        out = moved
    return out


def monomial(coefficients, exponent, unsigned=False):
    """The source's two-piece signed rotation, including negative exponents."""
    r = len(coefficients)
    quotient, remainder = divmod(exponent, r)
    sign = -1 if quotient % 2 else 1
    if unsigned:
        sign = 1
    if remainder == 0:
        return [sign * value for value in coefficients]
    head, tail = coefficients[:-remainder], coefficients[-remainder:]
    return [(-sign if not unsigned else sign) * x for x in tail] + [sign * x for x in head]


def execute(data, schedule, opposite=False, fault=None):
    """Return M times LB F- or F+ B^-1 L^-1 (exact integers)."""
    r = 1 << schedule['ell']
    lengths = schedule['lengths']
    bits = len(schedule['slots'])
    require(len(data) == 1 << bits and all(len(row) == r for row in data), 'wrong array shape')
    masks = {slot: 1 << (bits - 1 - position) for position, slot in enumerate(schedule['slots'])}
    out = [row.copy() for row in data] if opposite else relocate(data, schedule)
    rounds = range(schedule['ell']) if opposite else range(schedule['ell'] - 1, -1, -1)
    for h in rounds:
        axes = [i for i, a in enumerate(lengths) if h < a]
        if fault == 'omit_long_round' and h == schedule['ell'] - 1:
            continue
        if not axes:
            continue

        def butterfly():
            for i in axes:
                mask = masks[i, h]
                for address in range(len(out)):
                    if not address & mask:
                        other = address | mask
                        left, right = out[address], out[other]
                        out[address] = [x + y for x, y in zip(left, right)]
                        out[other] = [x - y for x, y in zip(left, right)]

        def twiddle():
            for address in range(len(out)):
                exponent = 0
                for i in axes:
                    branch = bool(address & masks[i, h])
                    low = sum((1 << v) for v in range(h) if address & masks[i, v])
                    if fault == 'include_branch_in_k':
                        low += (1 << h) * branch
                    if fault == 'physical_low_bits':
                        low = address & ((1 << h) - 1)
                    exponent -= (2 * r // (1 << (h + 1))) * branch * low
                if opposite and fault != 'wrong_inverse_sign':
                    exponent = -exponent
                out[address] = monomial(out[address], exponent, unsigned=fault == 'cyclic_instead_of_negacyclic')

        if opposite and fault != 'inverse_twiddle_after_butterfly':
            twiddle()
            butterfly()
        else:
            butterfly()
            twiddle()
    if opposite and fault != 'omit_layout_restoration':
        out = relocate(out, schedule, inverse=True)
    return out

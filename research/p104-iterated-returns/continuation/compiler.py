"""Finite rational lowering with the original 24-bit primitives and four streams."""

from collections import Counter
from fractions import Fraction
from functools import cache
from math import prod


LIMIT = 2**24 - 1
RADIX = 2**23
DONOR, PRODUCT, QUOTIENT, ACCUMULATOR = range(4)


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def width(coefficient):
    return max(abs(coefficient.numerator).bit_length(), coefficient.denominator.bit_length())


@cache
def bounded_factors(integer):
    """Pack exact factors, rejecting any factor outside the bounded primitive."""
    need(integer > 0, 'positive exact denominator')
    if integer == 1:
        return ()
    if integer <= LIMIT:
        return (integer,)
    x, divisor, factors = integer, 2, []
    while divisor * divisor <= x and divisor <= LIMIT:
        while x % divisor == 0:
            factors.append(divisor)
            x //= divisor
        divisor += 1 if divisor == 2 else 2
    need(x <= LIMIT, f'denominator has a factor above 24 bits: {x}')
    if x > 1:
        factors.append(x)
    packed = []
    for factor in reversed(factors):
        for i, current in enumerate(packed):
            if current * factor <= LIMIT:
                packed[i] *= factor
                break
        else:
            packed.append(factor)
    need(prod(packed) == integer, 'factor product')
    return tuple(packed)


@cache
def compile_scalar(coefficient):
    """Return (instructions, result stream). Narrow literals keep the retained path."""
    need(coefficient != 0, 'nonzero coefficient')
    if width(coefficient) <= 24:
        return (), QUOTIENT

    a = abs(coefficient.numerator)
    sign = 1 if coefficient > 0 else -1
    digits = []
    while a:
        a, digit = divmod(a, RADIX)
        digits.append(sign * digit)
    donor, spare, partial = DONOR, QUOTIENT, PRODUCT
    operations = []
    for factor in bounded_factors(coefficient.denominator):
        operations.append(('DIV', spare, donor, factor))
        donor, spare = spare, donor
    operations.append(('MUL', partial, donor, digits.pop()))
    for digit in reversed(digits):
        operations.append(('MUL', spare, partial, RADIX))
        if digit:
            operations.append(('MUL', partial, donor, digit))
            operations.append(('ADD', spare, spare, partial))
        partial, spare = spare, partial

    # Symbolic linear check uses no bit transducer or graph evaluator.
    formal = {DONOR: Fraction(1)}
    for op, out, source, arg in operations:
        need(out != ACCUMULATOR and source != ACCUMULATOR, 'do not borrow running row accumulator')
        if op == 'ADD':
            need(out == source != arg and arg in formal, 'owned ripple-add operands')
            need(formal[source] * formal[arg] > 0, 'one-sign radix accumulation')
            formal[out] = formal[source] + formal[arg]
        else:
            need(out != source and 0 < abs(arg) <= LIMIT, 'short disjoint scalar primitive')
            formal[out] = formal[source] * (Fraction(1, arg) if op == 'DIV' else arg)
        need(abs(formal[out]) <= max(1, abs(coefficient)), 'uniform intermediate magnitude envelope')
    need(formal[partial] == coefficient, 'compiled scalar identity')
    return tuple(operations), partial


def ripple_sum(left, right, signed_width):
    """Reference an owned in-place same-sign magnitude traversal."""
    need((left < 0) == (right < 0) or left == 0 or right == 0, 'mixed Horner signs')
    u, v = abs(left), abs(right)
    need(max(u, v).bit_length() < signed_width, 'input width')
    carry = magnitude = 0
    for j in range(signed_width + 26):
        carry += ((u >> j) & 1) + ((v >> j) & 1)
        magnitude |= (carry & 1) << j
        carry >>= 1
    need(carry == 0 and magnitude.bit_length() < signed_width, 'installed scalar overflow')
    return -magnitude if left < 0 or right < 0 else magnitude


def execute(plan, value, signed_width=None, scalar_service=None, dirty=None):
    """Execute the overwrite plan in the existing donor/product/quotient streams."""
    operations, result = plan
    registers = [value, None, None] if dirty is None else [value, *dirty]
    peak = abs(value)
    if signed_width is not None:
        need(peak.bit_length() < signed_width, 'input width')
    for op, out, source, arg in operations:
        x = registers[source]
        if op != 'ADD':
            need(out != source, 'source must survive full destination clear')
            registers[out] = None
        if op == 'ADD':
            y = x + registers[arg] if signed_width is None else ripple_sum(x, registers[arg], signed_width)
        elif scalar_service is not None:
            q = Fraction(1, arg) if op == 'DIV' else Fraction(arg)
            y = scalar_service(x, q, signed_width)
        elif op == 'DIV':
            y, remainder = divmod(x, arg)
            need(remainder == 0, 'physical remainder')
        else:
            y = x * arg
        peak = max(peak, abs(y))
        if signed_width is not None:
            need(abs(y).bit_length() < signed_width, 'installed scalar overflow')
        registers[out] = y
    output = registers[result]
    registers[:] = [None, None, None]
    return output, peak


def overwrite_count(instructions):
    live, count = {DONOR}, 0
    for op, out, _, _ in instructions:
        if op != 'ADD':
            count += out in live
            live.add(out)
    return count


def scalar_summary(physical, rows, caller, scales):
    """Charge every expanded incidence and test its short bit transducers."""
    counts = Counter(q for row in rows.values() for _, q in row)
    fixed = {Fraction(event[-1]) for event in caller['events']
             if event[0] != 'J' and event[1] in ('ADD', 'SCALE')}
    fixed.update((Fraction(-1), Fraction(1), Fraction(-1, 2), Fraction(1, 2)))
    for scale in scales:
        fixed.update((Fraction(scale), Fraction(1, scale), Fraction(-1, scale)))
    need(all(width(q) <= 24 for q in fixed), 'retained fixed-caller and conversion width')
    narrow = {q for q in counts if width(q) <= 24}
    check = physical.scalar_cases([{0: tuple(enumerate(narrow))}], caller, scales)
    wide = {q: compile_scalar(q) for q in counts if width(q) > 24}
    checked = 0
    for coefficient, plan in wide.items():
        a, b = coefficient.numerator, coefficient.denominator
        small_width = max(abs(a).bit_length(), b.bit_length()) + 2
        for w in (small_width, max(96, small_width + 8)):
            limit = (2**(w - 1) - 1) // max(abs(a), b)
            for k in (0, -1, 1, min(17, limit), -limit, limit):
                x, y = k*b, k*a
                observed, peak = execute(plan, x, w, physical.scalar_service, (317, -101))
                need(observed == y and peak == max(abs(x), abs(y)), 'expanded signed bit-stream replay')
                checked += 1
    histogram, overwrites = Counter(), 0
    for q, (instructions, _) in wide.items():
        overwrites += counts[q] * overwrite_count(instructions)
        for op, _, _, _ in instructions:
            histogram[op] += counts[q]
    # Retain the old allowance per source term. Charge all new primitives
    # again and reserve three extra whole-stream cleanup services per expansion.
    extra = sum(histogram.values()) + overwrites + 3 * sum(counts[q] for q in wide)
    return dict(**check, max_literal_bits=max(map(width, counts)), max_short_primitive_bits=24,
                expanded_terms=sum(counts[q] for q in wide), expanded_coefficient_count=len(wide),
                expanded_signed_fixtures=checked, extra_component_pass_allowance_per_native=extra,
                expanded_primitive_histogram=dict(histogram), overwrite_clears=overwrites, extra_scratch_streams=0,
                local_plans=[dict(coefficient=str(q), occurrences=counts[q], instructions=plan[0],
                                  result_stream=plan[1]) for q, plan in sorted(wide.items())])


def apply_expanded(native, signed, guard, coefficients, conversion, physical,
                   claim, tested, lower, upper, bit_cap):
    """Reprice finite ordinary work under the same signed and outer gates."""
    from mixed_application import ordinary_for_batch
    from supplier_gate import gate

    weights = {}
    for key, field, fixed in (('T', 'positive_helper_ranks', 'fixed_root_targets'),
                              ('P', 'paid_native_ranks', 'fixed_caller_paid')):
        total = Counter({int(r): signed['calls'] * n for r, n in native[field].items()})
        total.update({int(r): n for r, n in signed[fixed].items()})
        weights[key] = total
    scalar = conversion['scalar_cases']
    bits = max(scalar['coefficient_bits'], *(width(c) for c in coefficients))
    need(bits <= 24, 'padded scalar component width')
    for c in coefficients:
        for k in (-127, -1, 0, 1, 19, 2**68 + 1):
            x, y = k*c.denominator, k*c.numerator
            w = max(abs(x).bit_length(), abs(y).bit_length()) + 3
            need(physical.scalar_service(x, c, w) == y, 'ordinary signed caller scalar service')
    ordinary = ordinary_for_batch(native, signed, bits)
    incidences = ordinary['raw_scalar_incidence_allowance_before_factor_32']
    incidences['additional_odd_factor_steps'] = (len(conversion['odd_factors']) - 1)*ordinary['odd_conversions']
    extra = signed['calls'] * scalar['extra_component_pass_allowance_per_native']
    if extra:
        incidences['expanded_scalar_primitives_and_stream_clears'] = extra
        # The radix consumes a 24-bit multiplication constant even if all
        # narrow source incidences happen to have fewer bits.
        ordinary['scalar_step_rate'] = 2**max(20, scalar['max_short_primitive_bits']+8)
    ordinary['scalar_services'] = 32 * sum(incidences.values())
    need(sum(weights['T'].values()) == ordinary['raw_productive_targets'] and
         sum(weights['P'].values()) == ordinary['raw_paid_positions'], 'complete physical invoice')
    compiler = gate(weights, claim, tested, lower, upper, bit_cap)
    root = physical.root_envelope({'candidate': native}, guard)
    depth = physical.check_depth_guard(root, int(compiler['H']))
    return dict(invoice={'targets': dict(weights['T']), 'paid': dict(weights['P'])}, ordinary=ordinary,
                compiler=compiler, common_root=root, depth_guard=depth, claim=claim, bracket=[lower, upper])

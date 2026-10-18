"""Guarded in-place monomial refinement. Tekalign/Codex, Apache-2.0.

This is a semantic adapter, not a physical tape or memory-allocation benchmark.
The supplied lift must implement its stated reversible endpoint and clean up
its own private work. No predecessor executable is imported by this module.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rotate(value, phase):
    real, imag = value
    if phase & 1:
        real, imag = -imag, real
    if phase & 2:
        real, imag = -real, -imag
    return real, imag


def validate_word(recipe, word):
    """Check the compiled affine word symbolically, including its offset."""
    need(set(recipe) == {"matrix_rows", "offset", "linear_Z4", "quadratic_rows", "phase"},
         "recipe schema")
    size = len(recipe["matrix_rows"])
    need(1 <= size <= 73, "recipe dimension")
    for field, limit in (("matrix_rows", 1 << size), ("quadratic_rows", 1 << size), ("linear_Z4", 4)):
        need(len(recipe[field]) == size and
             all(type(x) is int and 0 <= x < limit for x in recipe[field]), "recipe field: " + field)
    need(type(recipe["phase"]) is int and 0 <= recipe["phase"] < 4, "global phase")
    need(type(recipe["offset"]) is int and 0 <= recipe["offset"] < 1 << size, "affine offset")
    rows, offsets = [1 << i for i in range(size)], [0] * size
    for kind, target, source in word:
        need(type(target) is int and 0 <= target < size, "target field")
        if kind == "flip":
            need(type(source) is int and source == -1, "toggle source sentinel")
            offsets[target] ^= 1
        else:
            need(kind == "add" and type(source) is int and 0 <= source < size and source != target,
                 "CNOT fields")
            rows[target] ^= rows[source]
            offsets[target] ^= offsets[source]
    need(rows == recipe["matrix_rows"] and sum(x << i for i, x in enumerate(offsets)) == recipe["offset"],
         "compiled affine endpoint")


def phase_pass(values, recipe, multiplicity, inverse=False):
    """Strict-upper Z4 convention; inverse is evaluated at recovered addresses."""
    size = len(recipe["matrix_rows"])
    output = []
    for address, value in enumerate(values):
        exponent = multiplicity * recipe["phase"]
        for column in range(multiplicity):
            bits = [(address >> (i * multiplicity + column)) & 1 for i in range(size)]
            exponent += sum(bit * coeff for bit, coeff in zip(bits, recipe["linear_Z4"], strict=True))
            exponent += 2 * sum(bits[i] * bits[j] * ((recipe["quadratic_rows"][i] >> j) & 1)
                                for i in range(size) for j in range(i + 1, size))
        output.append(rotate(value, (-exponent if inverse else exponent) % 4))
    return output


def character(values, controls, targets=None, inverse=False):
    output = []
    for address, value in enumerate(values):
        exponent = (sum((address >> c) & 1 for c in controls) if targets is None else
                    2 * sum(((address >> c) & 1) * ((address >> t) & 1)
                            for c, t in zip(controls, targets, strict=True)))
        output.append(rotate(value, (-exponent if inverse else exponent) % 4))
    return output


def guarded_gate(values, targets, controls, lift, inverse=False):
    """Literal R or R^-1; callers must establish the input lattice contract."""
    if controls is None:
        return lift(lift(values, targets, inverse), targets, inverse)
    if inverse:
        values = character(values, controls, inverse=True)
        values = lift(values, targets, True)
        values = character(values, controls, targets)
        values = lift(values, targets, False)
        return character(values, controls, targets)
    values = character(values, controls, targets)
    values = lift(values, targets, True)
    values = character(values, controls, targets)
    values = lift(values, targets, False)
    return character(values, controls)


def signed_capacity(values, width):
    need(type(width) is int and width >= 2, "signed capacity")
    limit = 1 << (width - 1)
    need(all(type(x) is int and -limit <= x < limit for pair in values for x in pair), "signed overflow")


def split_zero_guards(values, guard):
    """Return the data and the actual low-bit bank; never discard nonzero bits."""
    need(type(guard) is int and guard >= 0, "nonnegative guard")
    divisor = 1 << guard
    low = [(a % divisor, b % divisor) for a, b in values]
    need(all(a == b == 0 for a, b in low), "nonzero guard bank")
    return [(a // divisor, b // divisor) for a, b in values], low


def embed_bits(bits, guard, high):
    """Logical bit permutation plus sign CNOTs; returns the actual widened word.

    These bit arrays check the boundary representation, not physical routing.
    """
    need(len(bits) >= 2 and all(type(x) is int and x in (0, 1) for x in bits), "signed input bits")
    need(type(guard) is type(high) is int and guard >= 0 and high >= 1, "bit reserve")
    width = len(bits)
    bank = list(bits) + [0] * (guard + high)
    for at in range(width, width + high):
        bank[at] ^= bank[width - 1]
    # Rotate the zero suffix into the low end, a permutation of actual bits.
    if guard:
        bank = bank[-guard:] + bank[:-guard]
    return bank


def contract_bits(bank, width, guard):
    """Reverse the boundary operations, using the *current* output sign."""
    need(type(width) is type(guard) is int and width >= 2 and guard >= 0 and len(bank) > width + guard,
         "bit contraction domain")
    need(all(type(x) is int and x in (0, 1) for x in bank), "signed output bits")
    need(not any(bank[:guard]), "dirty low bits")
    moved = list(bank[guard:]) + list(bank[:guard])
    high = len(bank) - width - guard
    sign = moved[width - 1]
    need(all(x == sign for x in moved[width:width + high]), "output sign extension or capacity")
    for at in range(width, width + high):
        moved[at] ^= sign
    return moved[:width], moved[width:]


def execute(values, recipe, word, multiplicity, lift, width, inverse=False, meter=None):
    """One embedding and one exact contraction for the entire monomial word.

    A lift callback receives (bank, active_axes, inverse), returns the complete
    bank, and owes its own source, width, private-history and cleanup contract.
    Python list lifetimes do not represent the physical workspace proof.
    """
    need(type(multiplicity) is int and multiplicity >= 1 and type(inverse) is bool, "tensor parameters")
    validate_word(recipe, word)
    dimension = len(recipe["matrix_rows"]) * multiplicity
    need(len(values) == 1 << dimension and all(len(pair) == 2 for pair in values), "complete dense field layout")
    signed_capacity(values, width)
    guard = 2 * (multiplicity // 2 + 1)
    bank = [(a << guard, b << guard) for a, b in values]
    signed_capacity(bank, width)
    stats = dict(field_gates=0, inner_lifts=0, embeddings=1, contractions=1,
                 zero_guard_components=2 * len(values), guard_bits_per_component=guard)

    def checked_lift(data, axes, backwards):
        signed_capacity(data, width)
        result = lift(data, axes, backwards)
        need(len(result) == len(data), "complete lift result")
        signed_capacity(result, width)
        stats["inner_lifts"] += 1
        return result

    if not inverse:
        bank = phase_pass(bank, recipe, multiplicity)
    for kind, target, source in reversed(word) if inverse else word:
        targets = tuple(range(target * multiplicity, (target + 1) * multiplicity))
        controls = None if kind == "flip" else tuple(range(source * multiplicity, (source + 1) * multiplicity))
        bank = guarded_gate(bank, targets, controls, checked_lift, inverse)
        # Boundary check makes the compositional invariant observable.
        split_zero_guards(bank, guard)
        signed_capacity(bank, width)
        stats["field_gates"] += 1
    if inverse:
        bank = phase_pass(bank, recipe, multiplicity, True)
    result, low_bank = split_zero_guards(bank, guard)
    signed_capacity(result, width)
    if meter is not None:
        meter.append(stats)
    return result, low_bank

"""Independent host-integer oracle for the binary word implementation."""
from math import gcd

from words import Arena, BLANK, LEFT, Ring, Unsigned, need


def audit(arena, expected):
    need(arena.live == {word.slot for word in expected}, "exact live numerical registers")
    for word in arena.words:
        need(word.head == 1, "numerical head restoration")
        if word.slot not in arena.live:
            need(word.cells[0] == LEFT and all(x == BLANK for x in word.cells[1:]),
                 "erased numerical scratch before reuse")
    need(arena.template.head == 1, "extent-template head restoration")


def ring_cases(moduli=(2, 3, 4, 5, 7, 8, 9, 16, 25, 27)):
    rows = []
    for modulus in moduli:
        arena = Arena(modulus.bit_length()+1, capacity=64)
        m = arena.input(modulus)
        ring = Ring(m)
        pairs, inverse_cases = 0, 0
        for a in range(modulus):
            x = arena.input(a)
            inv = ring.inverse(x)
            if gcd(a, modulus) == 1:
                need(inv is not None and inv.inspect() == pow(a, -1, modulus), "binary modular inverse")
                arena.free(inv)
            else:
                need(inv is None, "binary nonunit rejection")
            need(x.inspect() == a and m.inspect() == modulus, "inverse preserves encoded inputs")
            audit(arena, (m, ring.one, x))
            inverse_cases += 1
            for b in range(modulus):
                y = arena.input(b)
                for operation, expected in ((ring.add, (a+b) % modulus),
                                            (ring.subtract, (a-b) % modulus),
                                            (ring.multiply, a*b % modulus)):
                    out = operation(x, y)
                    need(out.inspect() == expected, "binary modular operation")
                    need(x.inspect() == a and y.inspect() == b, "modular input preservation")
                    arena.free(out)
                    audit(arena, (m, ring.one, x, y))
                arena.free(y)
                pairs += 1
            # Alias the input register, as modular doubling and squaring do.
            doubled, squared = ring.add(x, x), ring.multiply(x, x)
            need(doubled.inspect() == 2*a % modulus and squared.inspect() == a*a % modulus,
                 "aliased read-only operands")
            arena.free_many(doubled, squared, x)
        ring.close()
        arena.free(m)
        audit(arena, ())
        rows.append({"modulus": modulus, "pairs": pairs, "inverses_and_nonunits": inverse_cases,
                     "word_bits": arena.bits, "operations": arena.meter.record()})
    return rows


def unsigned_cases():
    arena = Arena(6, capacity=32)
    machine = Unsigned(arena)
    count = 0
    for n in range(64):
        numerator = arena.input(n)
        for d in range(1, 32):
            denominator = arena.input(d)
            quotient, remainder = machine.divmod(numerator, denominator)
            need((quotient.inspect(), remainder.inspect()) == divmod(n, d), "restoring binary division")
            need(numerator.inspect() == n and denominator.inspect() == d, "division preserves inputs")
            arena.free_many(quotient, remainder, denominator)
            audit(arena, (numerator,))
            count += 1
        arena.free(numerator)
    zero = arena.input(0)
    try:
        machine.divmod(zero, zero)
    except ValueError as error:
        need(str(error) == "nonzero binary divisor", "division-zero rejection")
    else:
        raise ValueError("division by zero accepted")
    arena.free(zero)
    audit(arena, ())
    return {"division_cases": count, "operations": arena.meter.record()}


def carry_cases():
    arena = Arena(4, capacity=16)
    machine = Unsigned(arena)
    count = 0
    for a in range(16):
        x = arena.input(a)
        for b in range(16):
            y = arena.input(b)
            total, carry = machine.add(x, y)
            difference, borrow = machine.subtract(x, y)
            need((total.inspect(), carry) == ((a+b) % 16, (a+b)//16), "last carry bit")
            need((difference.inspect(), borrow) == ((a-b) % 16, int(a < b)), "last borrow bit")
            need(machine.compare(x, y) == ((a > b)-(a < b)), "binary magnitude comparison")
            arena.free_many(total, difference, y)
            audit(arena, (x,))
            count += 1
        arena.free(x)
    audit(arena, ())
    return {"carry_borrow_cases": count, "operations": arena.meter.record()}


def run():
    return {"rings": ring_cases(), "division": unsigned_cases(), "carry": carry_cases()}

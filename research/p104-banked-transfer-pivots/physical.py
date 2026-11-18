"""Price the finite bank program and exercise its exact scalar and reset services."""
from fractions import Fraction
from network import need


def scalar_bits(x, factor):
    a, b = abs(factor.numerator), factor.denominator
    magnitude = abs(x)
    carry = 0
    bits = []
    for j in range(max(1, magnitude.bit_length()) + a.bit_length() + 1):
        carry += a * ((magnitude >> j) & 1)
        bits.append(carry & 1)
        carry >>= 1
    need(carry == 0, "product width")
    quotient = remainder = 0
    for bit in reversed(bits):
        trial = 2 * remainder + bit
        next_bit = int(trial >= b)
        remainder = trial - next_bit * b
        quotient = 2 * quotient + next_bit
    need(remainder == 0, "physical grid remainder")
    return -quotient if (x < 0) != (factor.numerator < 0) else quotient


def overwrite(guide, bank, clear):
    need(guide is not bank and guide[0] == ("left", "") and guide[-1] == ("right", ""), "typed guide")
    pos = 1
    steps = 1
    while guide[pos][0] == "cell":
        bank[pos] = "_" if clear else guide[pos][1]
        pos += 1
        steps += 1
    need(guide[pos][0] == "right", "guide terminator")
    pos -= 1
    steps += 1
    while guide[pos][0] == "cell":
        pos -= 1
        steps += 1
    need(pos == 0, "head return")
    return steps + 1


def services(factors):
    cases = 0
    for factor in factors:
        for k in (0, -127, -1, 1, 19, (1 << 68) + 1):
            value = k * factor.denominator
            need(scalar_bits(value, factor) == k * factor.numerator, "finite scalar service")
            cases += 1
    try:
        scalar_bits(1, Fraction(1, 2))
    except ValueError as exc:
        need(str(exc) == "physical grid remainder", "odd-tick reason")
    else:
        raise ValueError("odd last tick escaped")
    for payload in ("", "0:0|_", ("0" * 19 + ":" + "0" * 19 + "|_") * 32):
        guide = [("left", "")] + [("cell", c) for c in payload] + [("right", "")]
        bank = ["left guard"] + ["_" if i % 2 else "#" for i in range(len(payload))] + ["right guard"]
        for clear in (False, True):
            expected = "_" * len(payload) if clear else payload
            need(overwrite(guide, bank, clear) == 2 * len(payload) + 3, "two-head cost")
            need(bank == ["left guard", *expected, "right guard"], "guard or extent")
    return cases


def budget(net, caller, raw, audit, paid, targets, signed):
    n, k, terms = raw["public"], raw["slots"], raw["terms"]
    calls, roots = audit["calls"], audit["root_owners"]
    uses = audit["uses"]
    factors = {Fraction(c) for row in net.forms.values() for c in row.values()}
    factors.update(Fraction(e[-1]) for e in caller["events"] if e[0] != "J" and e[1] in ("SCALE", "ADD"))
    for scale in (raw["odd"], audit["odd_scale"], 2):
        factors.update((Fraction(scale), Fraction(1, scale), Fraction(-1, scale)))
    bits = max(max(abs(c.numerator).bit_length(), c.denominator.bit_length()) for c in factors)
    cases = services(factors)
    conversions = 2 * (roots + calls * n)
    homes = 2 * n + 2 * k + 4
    resets = calls * (2 * homes + 4 * (terms + k + n))
    scalar_count = 32 * (calls * (terms + 4 * (k + n) + 2 * n + homes) + sum(uses.values()) + conversions)
    maps = (2 * sum(paid.values()) + 2 * sum(targets.values()) + 2 * calls * raw["mains"]
            + 2 * (uses["IDLE_ODD"] + uses["IDLE_ONE"]) + 3 * uses["QUERY"] + uses["LAMBDA"] + uses["IDLE_ODD"])
    height = raw["dyadic_height"] + audit["dyadic_height"]
    mass = Fraction(raw["peak_scaled_mass"]) * Fraction(audit["peak_scaled_mass"])
    mass_bits = ((mass.numerator + mass.denominator - 1) // mass.denominator).bit_length()
    c = 2 * max(height, mass_bits)
    h = int(signed["H"])
    depth = 1920 * 153**1920 * (h + 1)**2
    need((c * depth).bit_length() < h, "root exactness guard")
    return dict(odd_conversions=conversions, coefficient_bits=bits, scalar_test_cases=cases,
                raw_private_homes=calls * homes, homes_per_native=homes, reset_services_upper=resets,
                scalar_services_upper=scalar_count, scalar_steps_per_bit_upper=2**max(20, bits + 8),
                monomial_slots_upper=maps, elementary_records_upper=maps * 4 * 154**2,
                dyadic_height=height, context_mass_upper=str(mass), context_mass_bits=mass_bits,
                context_c=c, depth_guard_bits=(c * depth).bit_length(), H=h)

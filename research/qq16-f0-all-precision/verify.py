"""A symbolic all-precision extension of the credited PR3067 F0 witness."""

import argparse
import hashlib
import json
import types
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = "research/qq16-f0-physical-rounding/verify.py"
INPUTS = {
    "research/community-frontier1042-audit/selected-replay.tar.gz",
    "research/joint-query/certificate.json.gz",
    "research/qq16-f0-physical-rounding/README.md",
    "research/qq16-f0-physical-rounding/SOURCES.json",
    "research/qq16-f0-physical-rounding/vendor/pr3017/native.py",
    PREDECESSOR,
}
MIN_PRECISION = 8
OFFSET = 12


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load(root=ROOT):
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    entries = sources["files"]
    need(len(entries) == 8, "exact source inventory size")
    need(
        {row["path"] for row in entries if row["usage"] == "input"} == INPUTS,
        "exact live input inventory",
    )
    for entry in entries:
        if entry["usage"] == "input":
            with (root / entry["path"]).open("rb") as stream:
                raw = stream.read(32_000_001)
            need(len(raw) <= 32_000_000, "bounded scientific input")
            need(
                hashlib.sha256(raw).hexdigest() == entry["sha256"],
                "source pin: " + entry["path"],
            )
    source = root / PREDECESSOR
    module = types.ModuleType("credited_f0_reference")
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    packet, _, recipes, residuals = module.load(root)
    context = {
        "packet": packet,
        "children": {(r["old"], r["new"]): r for r in recipes["children"]},
        "adapters": {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]},
        "residuals": residuals,
    }
    return module, module.expand(packet), context


def power(exponent):
    return Q(2**exponent) if exponent >= 0 else Q(1, 2 ** (-exponent))


def floor_log(value):
    need(value > 0, "positive logarithm argument")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    return exponent - int(value < power(exponent))


def nearest_integer(value):
    quotient, remainder = divmod(value.numerator, value.denominator)
    if 2 * remainder > value.denominator or (
        2 * remainder == value.denominator and quotient % 2
    ):
        quotient += 1
    return quotient


@lru_cache(maxsize=65536)
def rounded_affine(a, b, minimum=MIN_PRECISION):
    """Certify RN_p(2^(p+12)*a+b) for every p >= minimum.

    Returns the unchanged leading coefficient and the new constant term.
    The two endpoint binade checks prove the exponent for the entire ray.
    An even integral leading-grid index makes tie parity independent of p.
    """
    need(type(minimum) is int and 2 <= minimum <= 256, "minimum precision bound")
    need(
        all(x.denominator & (x.denominator - 1) == 0 for x in (a, b)),
        "dyadic affine coefficients",
    )
    if not a:
        need(
            abs(b.numerator).bit_length() <= minimum,
            "constant significand exceeds minimum",
        )
        return a, b
    leading = a * power(minimum + OFFSET)
    initial = leading + b
    need(initial * leading > 0, "dominant sign is not stable")
    exponent = floor_log(abs(initial))
    lower, upper = power(exponent), power(exponent + 1)
    need(lower <= abs(leading) <= upper, "dominant binade differs")
    need(
        abs(leading) != upper or a * b < 0,
        "upper endpoint must be approached from below",
    )
    quantum = power(exponent - minimum + 1)
    index = leading / quantum
    need(
        index.denominator == 1 and index.numerator % 2 == 0,
        "leading tie parity not stable",
    )
    return a, quantum * nearest_integer(b / quantum)


def components(value):
    denominator = 2 ** value[2]
    return [Q(x, denominator) for row in value[:2] for x in row]


def vector_from_components(native, values):
    need(len(values) == 1024, "bounded complex component count")
    exponent = max(x.denominator.bit_length() - 1 for x in values)
    need(
        all(x.denominator == 2 ** (x.denominator.bit_length() - 1) for x in values),
        "dyadic values",
    )
    integers = [x.numerator * (2**exponent // x.denominator) for x in values]
    return native.vector(integers[:512], integers[512:], exponent)


def round_vector(native, leading, constant, minimum, observations):
    if leading == native.ZERO:
        # This branch still checks every distinct constant significand.
        values = components(constant)
        for b in set(values):
            rounded_affine(Q(0), b, minimum)
        observations["constant_vectors"] += 1
        return constant
    aa, bb = components(leading), components(constant)
    result = []
    for a, b in zip(aa, bb, strict=True):
        _, c = rounded_affine(a, b, minimum)
        result.append(c)
    observations["mixed_or_leading_vectors"] += 1
    return vector_from_components(native, result)


def physical_event(module, context, state, event):
    """Literal exact native dispatch, following PR3067 without changing its bytes."""
    native = module.N
    kind = event[0]
    if kind == "climb":
        _, _, dst, old, new, rank = event
        recipe = context["children"][old, new]
        need(recipe["rank"] == rank, "literal child rank")
        if state[dst] != native.ZERO:
            state[dst] = native.recipe(state[dst], recipe)
    elif kind == "adapter":
        _, direction, dst, _ = event
        if direction == "old_to_new" and dst < 112:
            key = native.monomial_key(context["adapters"]["source", dst]["left"])
            state[dst] = native.mono(state[dst], key)
        elif direction == "new_to_old" and 112 <= dst < 224:
            key = native.monomial_key(context["adapters"]["target", dst - 112]["left"])
            state[dst] = native.mono(state[dst], key, True)
        else:
            need(direction in ("old_to_new", "new_to_old"), "adapter direction")
    elif kind == "residual_adapter":
        direction, dst, a = event[1:4]
        b = event[4] if len(event) == 5 else 1
        need(direction in ("pre", "post"), "residual direction")
        key = str(a) if b == 1 else f"{a}:{b}"
        part = "right" if direction == "pre" else "left"
        record = context["residuals"]["recipes"][key][part]
        state[dst] = native.mono(state[dst], native.monomial_key(record), True)
    elif kind == "native_line":
        dst = module.reg(event[1])
        recipe = context["packet"]["native_line_recipes"][event[2]]["recipe"]
        state[dst] = native.recipe(state[dst], recipe)
    else:
        need(kind == "phase", "known physical event")


def scalar_event(module, event, states, minimum, observations, round_adds):
    native = module.N
    leading, constant = states
    gate = event[1]
    dst = module.reg(gate[1])
    if gate[0] == "clear":
        need(dst >= 704, "only owned private clear")
        leading[dst] = constant[dst] = native.ZERO
        return native.ZERO
    if gate[0] == "scale":
        coefficient = Q(gate[2], gate[3])
        n = abs(coefficient.numerator)
        need(n > 0 and n & (n - 1) == 0, "exact binary scale")
        leading[dst] = native.scaled(leading[dst], coefficient)
        constant[dst] = native.scaled(constant[dst], coefficient)
        return native.ZERO
    need(gate[0] == "add", "known scalar gate")
    src = module.reg(gate[2])
    need(src != dst, "distinct add operands")
    coefficient = Q(gate[3], gate[4])
    products = [native.scaled(state[src], coefficient) for state in states]
    if round_adds:
        product_round = round_vector(native, *products, minimum, observations)
        need(
            product_round == products[1],
            "coefficient product not exact for all precisions",
        )
    leading[dst] = native.plus(leading[dst], products[0])
    exact = native.plus(constant[dst], products[1])
    actual = (
        round_vector(native, leading[dst], exact, minimum, observations)
        if round_adds
        else exact
    )
    constant[dst] = actual
    return native.plus(actual, native.scaled(exact, Q(-1)))


def symbolic(module, events, context, minimum=MIN_PRECISION, round_adds=True):
    native = module.N
    leading, constant = [native.ZERO] * 712, [native.ZERO] * 712
    leading[224], constant[112] = native.ONE, native.ONE
    observations, faults = Counter(), []
    for index, event in enumerate(events):
        if event[0] == "scalar":
            delta = scalar_event(
                module, event, (leading, constant), minimum, observations, round_adds
            )
            if delta != native.ZERO:
                faults.append({"event": index, "delta": module.component_hist(delta)})
        else:
            physical_event(module, context, leading, event)
            physical_event(module, context, constant, event)
    return leading, constant, faults, dict(observations)


def audit(root=ROOT, minimum=MIN_PRECISION):
    module, events, context = load(root)
    native = module.N
    leading, constant, faults, observations = symbolic(module, events, context, minimum)
    expected_leading = [native.ZERO] * 712
    expected_leading[224] = native.ONE
    entry_constant = [native.ZERO] * 712
    entry_constant[112] = native.ONE
    expected_constant = module.expected(entry_constant)
    need(
        leading == expected_leading and constant == expected_constant,
        "complete symbolic endpoint",
    )
    ideal_a, ideal_b, ideal_faults, _ = symbolic(
        module, events, context, minimum, False
    )
    need(
        ideal_a == expected_leading and ideal_b == entry_constant and not ideal_faults,
        "complete ideal endpoint",
    )
    need(
        [x["event"] for x in faults] == [3887, 4060],
        "exactly the predecessor two faults",
    )
    need(
        all(x["delta"] == {"real": {"-1/2": 512}, "imag": {"0": 512}} for x in faults),
        "fault amplitudes",
    )
    return {
        "schema_version": 1,
        "status": "PASS_QQ16_F0_ALL_PRECISION",
        "minimum_precision": minimum,
        "quantifier": "every integer p >= minimum_precision",
        "dirty_amplitude": "2^(p+12)",
        "events": len(events),
        "event_sha256": module.digest(events),
        "faults": faults,
        "observations": observations,
        "endpoint_affine_sha256": module.digest([leading, constant]),
        "ideal_affine_sha256": module.digest([ideal_a, ideal_b]),
        "helper_return": "all 480 physical helper fields equal their entry values",
        "private_return": "all eight private fields zero",
        "error_fields": {
            "112": "-1",
            "114": "-1/2",
            "137": "-1/2",
            "190": "-1/2",
            "211": "-1/2",
        },
        "relative_error": "1",
        "native_internals": "exact, not rounded",
        "new_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(
            canonical(json.loads((HERE / "RESULT.json").read_bytes()))
            == canonical(result),
            "receipt mismatch",
        )
    print(result["status"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Source-bound finite F0 collision. Nick Petalas. Apache-2.0.

Native event dispatch follows Sricharan Vagvala's rounded F0 evaluator;
Gaussian vector primitives retain Tekalign/PR3017's attribution.
"""
import argparse
import hashlib
import json
import runpy
import sys
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIM = 512
FIELDS = 712
PREFIX = [
    ["phase", "zero_frame_precondition"],
    ["scalar", ["scale", ["L", 119], -1, 2], 0],
    ["scalar", ["add", ["L", 119], ["L", 169], 1, 2], 0],
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(len(pins["files"]) == 7, "Exactly seven declared source pins")
    for pin in pins["files"]:
        if pin["usage"] == "input":
            path = ROOT / pin["path"]
            need(path.stat().st_size <= 32 * 1024**2, "Source input size limit")
            raw = path.read_bytes()
            need(hashlib.sha256(raw).hexdigest() == pin["sha256"],
                 "Scientific source hash: " + pin["path"])
    path = ROOT / "research/qq16-native-rounded-components/verify.py"
    # run_path reads .py source directly, not a preexisting bytecode cache.
    module = types.SimpleNamespace(**runpy.run_path(str(path)))
    data = module.load()
    need(len(data[0]) == 26099 and data[0][:3] == PREFIX,
         "Literal F0 prefix or event inventory changed")
    return module, data


def round_fraction(value, bits):
    """Nearest-even binary rounding, using a rational-binade oracle."""
    need(2 <= bits <= 113, "Precision outside the checked domain")
    if not value:
        return Fraction(0)
    sign = -1 if value < 0 else 1
    value = abs(value)
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    power = Fraction(2) ** exponent
    if value < power:
        exponent -= 1
    quantum = Fraction(2) ** (exponent - bits + 1)
    scaled = value / quantum
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    if 2 * remainder > scaled.denominator or (
            2 * remainder == scaled.denominator and quotient % 2):
        quotient += 1
    return sign * quotient * quantum


def oracle_prefix(sign, bits):
    source = Fraction(2) ** (bits + 1)
    target = round_fraction(Fraction(-sign, 2), bits)
    term = round_fraction(source / 2, bits)
    return round_fraction(target + term, bits)


def initial(module, signs, bits):
    need(len(signs) == DIM and all(s in (-1, 1) for s in signs),
         "Exactly 512 independent signs required")
    state = [module.N.ZERO] * FIELDS
    state[119] = module.N.vector(list(signs), [0] * DIM, 0)
    state[169] = module.N.scaled(module.N.ONE, Fraction(2) ** (bits + 1))
    return state


def apply_event(module, engine, state, event, maps):
    """The frozen lowering's actual event dispatcher, with arbitrary input."""
    children, adapters, residuals, packet = maps
    kind = event[0]
    if kind == "scalar":
        gate = event[1]
        dst = module.reg(gate[1])
        if gate[0] == "clear":
            need(dst >= 704, "CLEAR must own its private destination")
            state[dst] = engine.zero
        elif gate[0] == "scale":
            state[dst] = engine.scalar(state[dst], *gate[2:], "scalar-scale")
        else:
            need(gate[0] == "add", "Unknown scalar operation")
            term = engine.scalar(state[module.reg(gate[2])], *gate[3:],
                                 "scalar-multiply")
            state[dst] = engine.add(state[dst], term)
    elif kind == "climb":
        _, _, dst, old, new, _ = event
        if state[dst] != engine.zero:
            state[dst] = engine.recipe(state[dst], children[old, new])
    elif kind == "adapter":
        _, direction, dst, _ = event
        if direction == "old_to_new" and dst < 112:
            key = module.N.monomial_key(adapters["source", dst]["left"])
            state[dst] = engine.mono(state[dst], key)
        elif direction == "new_to_old" and 112 <= dst < 224:
            key = module.N.monomial_key(adapters["target", dst-112]["left"])
            state[dst] = engine.mono(state[dst], key, True)
    elif kind == "residual_adapter":
        direction, dst, a = event[1:4]
        b = event[4] if len(event) == 5 else 1
        key = str(a) if b == 1 else f"{a}:{b}"
        part = "right" if direction == "pre" else "left"
        key = module.N.monomial_key(residuals["recipes"][key][part])
        state[dst] = engine.mono(state[dst], key, True)
    elif kind == "native_line":
        dst = module.reg(event[1])
        state[dst] = engine.recipe(
            state[dst], packet["native_line_recipes"][event[2]]["recipe"])
    else:
        need(kind == "phase", "Unknown physical event")


def maps_for(data):
    _, packet, _, recipes, residuals = data
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    return children, adapters, residuals, packet


def prefix(module, data, signs, bits=53):
    engine = module.Dyadic(bits)
    state = initial(module, signs, 53)
    maps = maps_for(data)
    for index, event in enumerate(data[0][:3]):
        engine.event = index
        apply_event(module, engine, state, event, maps)
    return state, engine.report()


def finish(module, data, merged, engine):
    if isinstance(engine, module.Binary64):
        state = [(tuple(float(Fraction(x, 1 << e)) for x in re),
                  tuple(float(Fraction(x, 1 << e)) for x in im))
                 for re, im, e in merged]
    else:
        state = merged.copy()
    maps = maps_for(data)
    trace = []
    for index in range(3, len(data[0])):
        engine.event = index
        event = data[0][index]
        apply_event(module, engine, state, event, maps)
        if event[0] != "phase":
            dst = (module.reg(event[1][1]) if event[0] == "scalar" else
                   module.reg(event[1]) if event[0] == "native_line" else event[2])
            trace.append(digest(engine.canonical(state[dst])))
    return [engine.canonical(x) for x in state], digest(trace)


def check_cut(module, data):
    patterns = [(-1,) * DIM, (1,) * DIM,
                tuple(1 if i % 2 else -1 for i in range(DIM))]
    outputs = [prefix(module, data, signs) for signs in patterns]
    merged = outputs[0][0]
    need(all(out == outputs[0] for out in outputs), "Whole-state coalescence")
    expected = [module.N.ZERO] * FIELDS
    expected[119] = module.N.scaled(module.N.ONE, Fraction(2) ** 53)
    expected[169] = module.N.scaled(module.N.ONE, Fraction(2) ** 54)
    need(merged == expected, "Explicit whole cut state")
    need(outputs[0][1] == [{"event": 2, "stage": "scalar-add",
                           "rounded_components": DIM, "max_component_error": "1/2"}],
         "Sign-independent rounding-count summary")
    for bits in (2, 3, 8, 24, 53, 65, 113):
        for sign in (-1, 1):
            need(oracle_prefix(sign, bits) == 2**bits, "Rational prefix oracle")
    hardware = [float(-s) * 0.5 + 0.5 * float(2**54) for s in (-1, 1)]
    need(hardware == [float(2**53)] * 2, "Actual binary64 prefix")
    for bits in (55, None):
        left, _ = prefix(module, data, patterns[0], bits)
        right, _ = prefix(module, data, patterns[1], bits)
        need(left != right, "Exact or wider-grid escape must distinguish")
    return merged, outputs[0][1]


def audit():
    need(sys.float_info.radix == 2 and sys.float_info.mant_dig == 53
         and sys.float_info.max_exp == 1024 and sys.float_info.rounds == 1,
         "IEEE binary64 nearest-rounding environment required")
    module, data = load()
    merged, faults = check_cut(module, data)
    exact, exact_trace = finish(module, data, merged, module.Dyadic(53))
    binary, binary_trace = finish(module, data, merged, module.Binary64())
    need(exact == binary and exact_trace == binary_trace,
         "Actual complete native suffix disagrees with binary64")
    endpoint = [module.N.ZERO] * FIELDS
    endpoint[169] = module.N.scaled(module.N.ONE, Fraction(2) ** 54)
    need(exact == endpoint, "Explicit common endpoint including every helper")
    ideal_controls = {}
    for sign in (-1, 1):
        cut, _ = prefix(module, data, (sign,) * DIM, None)
        ideal, _ = finish(module, data, cut, module.Dyadic(None))
        need(ideal == initial(module, (sign,) * DIM, 53),
             "Exact full native word preserves the constant-sign input")
        ideal_controls[str(sign)] = digest(ideal)
    counts = Counter(e[0] for e in data[0])
    return {
        "status": "PASS_QQ16_F0_WHOLE_STATE_COLLISION",
        "scope": "Finite local 512-complex-coordinate F0, p=53 pair-first lowering",
        "events": len(data[0]), "event_counts": dict(sorted(counts.items())),
        "event_sha256": digest(data[0]), "merge_after_zero_based_event": 2,
        "independent_original_data_signs": DIM, "minimum_exact_recovery_bits": DIM,
        "family_cardinality": "2^512", "shared_initial_source": "2^54",
        "borrowed_helpers_and_private_inputs": "all zero and identical",
        "merge_state_sha256": digest(merged), "prefix_rounding": faults,
        "endpoint_sha256": digest(exact), "suffix_cut_trace_sha256": exact_trace,
        "ideal_constant_sign_controls": ideal_controls,
        "all_480_zero_helpers_and_eight_private_fields_return_zero": True,
        "binary64_every_changed_suffix_cut_agrees": True,
        "full_state_equality_includes_all_712_fields": True,
        "physical_caller_or_supplier_admitted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Create an absent receipt")
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()),
             "Result receipt mismatch")
    print(result["status"])


if __name__ == "__main__":
    main()

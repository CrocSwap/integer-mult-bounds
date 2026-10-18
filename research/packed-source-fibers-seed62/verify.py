#!/usr/bin/env python3
"""Exact source-conditioned audit of the retained eight-rotation bit gadget.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
The source operations are OpenAI's; PR773's carry-state argument is credited
in README.md. No PR773 implementation is imported. This is finite evidence
for the written proof, not a formal multiplication theorem.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "49b3157d1d89adcef16df8be98445451672be5ba"
SEED = 62
INPUTS = {"upstream/build/sections/05-layers.tex",
          "tests/test_finite_identities.py", "upstream/LICENSE"}
STATES = (0, 5, 10, 80, 160)
SIGNS = (-1, -1, 1, 1, 1, 1, -1, -1)
TARGETS = (0, 1, 0, 1, 1, 0, 1, 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def source_check():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "wrong source base")
    rows = [r for r in pins["files"] if r["usage"] == "input"]
    require(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
            "incomplete input inventory")
    for row in rows:
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source SHA256 drift: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob drift: " + row["path"])
    spec = importlib.util.spec_from_file_location(
        "retained_finite_identities", ROOT / "tests/test_finite_identities.py")
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source.packed_steps


def digit(state, c, u, w, radix, unwrapped=False):
    """Eight explicit assignments, with signed incoming carries at each gate."""
    outgoing = 0
    trace = [(u, w)]

    def reduce(value, gate):
        nonlocal outgoing
        if unwrapped:
            return value
        carry, residue = divmod(value, radix)
        require(carry in (0, SIGNS[gate]), "invalid carry direction")
        outgoing |= bool(carry) << gate
        return residue

    u = reduce(u - c * (w % 2 == 0) - ((state >> 0) & 1), 0)
    trace.append((u, w))
    w = reduce(w - c * (u % 2 == 0) - ((state >> 1) & 1), 1)
    trace.append((u, w))
    u = reduce(u + c * (w % 2 == 0) + ((state >> 2) & 1), 2)
    trace.append((u, w))
    w = reduce(w + c * (u % 2 == 0) + ((state >> 3) & 1), 3)
    trace.append((u, w))
    w = reduce(w + c * (u % 2 == 1) + ((state >> 4) & 1), 4)
    trace.append((u, w))
    u = reduce(u + c * (w % 2 == 1) + ((state >> 5) & 1), 5)
    trace.append((u, w))
    w = reduce(w - c * (u % 2 == 1) - ((state >> 6) & 1), 6)
    trace.append((u, w))
    u = reduce(u - c * (w % 2 == 1) - ((state >> 7) & 1), 7)
    trace.append((u, w))
    return (outgoing, u, w), trace


def predicted_transition(state, c, u, w, radix):
    """Disjoint boundary conditions from the proof, without gate execution."""
    if state and c:
        return None
    if not c:
        if not state:
            return 0
        at_boundary = {5: u == 0, 10: w == 0,
                       80: w == radix - 1, 160: u == radix - 1}[state]
        return state if at_boundary else 0
    conditions = ((5, u == 0 and w % 2 == 0),
                  (10, w == 0 and u % 2 == 1),
                  (80, w == radix - 1 and u % 2 == 1),
                  (160, u == radix - 2 and w % 2 == 1))
    hits = [s for s, ok in conditions if ok]
    require(len(hits) <= 1, "overlapping boundary clauses")
    return hits[0] if hits else 0


def table(radix):
    b = radix
    return {
        0: {0: {0: b*b}, **{s: {0: b*(b-1), s: b} for s in STATES[1:]}},
        1: {0: {0: b*(b-2), **{s: b//2 for s in STATES[1:]}},
            **{s: {} for s in STATES[1:]}},
    }


def agreement(bits, radix):
    require(all(bit in (0, 1) for bit in bits), "nonbinary source pattern")
    ones = [i for i, bit in enumerate(bits) if bit]
    out = Q(1)
    for left, right in zip(ones, ones[1:]):
        out *= 1 - Q(2, radix ** (right - left))
    return out


def recurrence(bits, radix):
    """Five-state integer counting, distinct from the source-gap product."""
    counts = {0: 1}
    transitions = table(radix)
    for c in bits:
        following = Counter()
        for state, multiplicity in counts.items():
            for dest, choices in transitions[c][state].items():
                following[dest] += multiplicity * choices
        counts = following
    return Q(sum(counts.values()), radix ** (2 * len(bits)))


def failure_extrema(length, weight, radix):
    if weight <= 1:
        return Q(0), Q(0)
    gaps = weight - 1
    short, longer = divmod(length - 1, gaps)
    minimum = 1 - ((1 - Q(2, radix**short)) ** (gaps - longer)
                   * (1 - Q(2, radix**(short+1))) ** longer)
    maximum = 1 - (1 - Q(2, radix)) ** gaps
    return minimum, maximum


def word_model(x, y, z, k, f, rho):
    """Process digit columns then the inactive suffix; no full-word addition."""
    radix = 1 << k
    low = (1 << rho) - 1
    out = [y & low, z & low]
    state = 0
    for i in range(f - 1):
        shift = rho + k*i
        (state, a, b), _ = digit(state, (x >> shift) & 1,
                                (y >> shift) & (radix-1),
                                (z >> shift) & (radix-1), radix)
        out[0] |= a << shift
        out[1] |= b << shift
    shift = rho + k*(f-1)
    for target, initial in enumerate((y, z)):
        carry = sum(SIGNS[i] * ((state >> i) & 1)
                    for i in range(8) if TARGETS[i] == target)
        suffix = ((initial >> shift) + carry) % (1 << (k-rho))
        out[target] |= suffix << shift
    return x, *out


def ideal(x, y, z, k, f, rho, include_top=False):
    mask = sum(((x >> (rho+k*i)) & 1) << (rho+k*i)
               for i in range(f if include_top else f-1))
    return x, y ^ mask, z


def symbolic_checks():
    deltas = {}
    cases = 0
    for state, c, a, b in product(STATES, (0, 1), (0, 1), (0, 1)):
        (_, u, w), trace = digit(state, c, a, b, 64, unwrapped=True)
        require(all(-2 <= v <= 3 for pair in trace for v in pair), "parity range")
        error = (u - (a ^ c), w-b)
        if state and c:
            require(abs(error[1]) == 1, "incoming carry must corrupt dirty z")
            deltas[f"{state}:{a}{b}"] = list(error)
        else:
            require(error == (0, 0), "symbolic final scalar map")
        cases += 1
    for state in STATES:
        for target in (0, 1):
            require(sum(SIGNS[i]*((state >> i) & 1)
                        for i in range(8) if TARGETS[i] == target) == 0,
                    "matching-prefix suffix restoration")
    return {"parity_cases": cases, "dirty_error_table": deltas}


def digit_checks():
    cases = 0
    for k in range(2, 9):
        b = 1 << k
        expected = table(b)
        for state, c in product(STATES, (0, 1)):
            observed = Counter()
            for u, w in product(range(b), repeat=2):
                (dest, got_u, got_w), _ = digit(state, c, u, w, b)
                matches = (got_u, got_w) == (u ^ c, w)
                predicted = predicted_transition(state, c, u, w, b)
                require(matches == (predicted is not None), "boundary agreement")
                if matches:
                    require(dest == predicted, "boundary carry type")
                    observed[dest] += 1
                cases += 1
            require(dict(observed) == expected[c][state], "conditional count table")
    return cases


def pattern_checks():
    patterns = extrema = 0
    for b in (4, 8, 64, 128):
        for length in range(11):
            by_weight = {}
            total = Q(0)
            for bits in product((0, 1), repeat=length):
                got = recurrence(bits, b)
                require(got == agreement(bits, b), "source-gap product formula")
                total += got
                weight = sum(bits)
                by_weight.setdefault(weight, []).append(1-got)
                patterns += 1
            average = Q(1) if length == 0 else (1-Q(1, 2*b)) ** (length-1)
            require(total / (1 << length) == average, "PR773 complete-rectangle marginal")
            for weight, failures in by_weight.items():
                require((min(failures), max(failures)) == failure_extrema(length, weight, b),
                        "sharp fixed-weight extrema")
                extrema += 1
    return {"patterns": patterns, "weight_classes": extrema, "max_used_segments": 10}


def full_fiber_checks(source):
    cases = repair_records = 0
    fibers = []
    # Exhaust complete y,z fibers at a diagnostic radix, including all suffix
    # values. The written theorem retains the source domain K >= 6.
    for f in (1, 2, 3, 4):
        k, rho, b = 2, 0, 4
        modulus = 1 << (k*f)
        for bits in product((0, 1), repeat=f-1):
            x = sum(c << (k*i) for i, c in enumerate(bits))
            x |= ((SEED + sum(bits)) % 2) << (k*(f-1))
            mismatches = 0
            forward, target = [], []
            for y, z in product(range(modulus), repeat=2):
                actual = source(x, y, z, k, f, rho)
                wanted = ideal(x, y, z, k, f, rho)
                require(actual == word_model(x, y, z, k, f, rho), "whole-word digit model")
                mismatches += actual != wanted
                completed = (x, actual[1] ^ (x & (1 << (k*(f-1)))), actual[2])
                require((completed == ideal(x, y, z, k, f, rho, True)) == (actual == wanted),
                        "highest XOR agreement equivalence")
                if f == 3:
                    forward.append(actual[1]*modulus + actual[2])
                    target.append(wanted[1]*modulus + wanted[2])
                cases += 1
            count = modulus*modulus
            require(Q(mismatches, count) == 1-agreement(bits, b), "whole-fiber density")
            fibers.append({"bits_low_first": list(bits), "f": f,
                           "failures": mismatches, "total": count})
            if f == 3:
                require(len(set(forward)) == count, "source-fiber bijection")
                inverse = [0] * count
                for original, current in enumerate(forward):
                    inverse[current] = original
                repair = [target[inverse[current]] for current in range(count)]
                support = {q for q, dest in enumerate(repair) if q != dest}
                bad_original = {p for p, dest in enumerate(forward) if dest != target[p]}
                require(support == {forward[p] for p in bad_original}, "D_x = S0(F_x)")
                require(len(support) == mismatches, "fiberwise repair count")
                require({repair[q] for q in support} == support, "repair support invariance")
                records = list(inverse)
                extracted = sorted((repair[q], records[q]) for q in support)
                holes = sorted(support)
                require([dest for dest, _ in extracted] == holes, "destination keys equal holes")
                for dest, payload in extracted:
                    records[dest] = payload
                require(all(records[target[p]] == p for p in range(count)), "sorted payload repair")
                repair_records += count
    return {"states": cases, "fibers": fibers, "payload_repair_records": repair_records}


def source_domain_checks(source):
    rng = random.Random(SEED)
    cases = 0
    # Realize each incoming state by an actual first source segment, then
    # exhaust every second source-domain digit at the seed-selected offset.
    b, k, rho = 64, 6, SEED % 6
    prefixes = {0: (0, 0, 0), 5: (1, 0, 0), 10: (1, 1, 0),
                80: (1, 1, b-1), 160: (1, b-2, 1)}
    for state, (first_c, first_y, first_z) in prefixes.items():
        (got_state, got_y, got_z), _ = digit(0, first_c, first_y, first_z, b)
        require((got_state, got_y, got_z) == (state, first_y ^ first_c, first_z),
                "reachable prefix witness")
        for c, y, z in product((0, 1), range(b), range(b)):
            x = (first_c << rho) | (c << (rho+k)) | (1 << (rho+2*k))
            yy = 1 | (first_y << rho) | (y << (rho+k)) | (3 << (rho+2*k))
            zz = 2 | (first_z << rho) | (z << (rho+k)) | (5 << (rho+2*k))
            actual = source(x, yy, zz, k, 3, rho)
            require(actual == word_model(x, yy, zz, k, 3, rho), "source-domain prefix replay")
            (_, a, d), _ = digit(state, c, y, z, b)
            require((actual == ideal(x, yy, zz, k, 3, rho)) == ((a, d) == (y ^ c, z)),
                    "source-domain matching-prefix criterion")
            cases += 1
    prefix_cases = cases
    for k in (6, 7, 10):
        for f, rho in product((1, 2, 3, 4, 7, 11), range(k)):
            modulus, b = 1 << (k*f), 1 << k
            for sample in range(64):
                x, y, z = (rng.randrange(modulus) for _ in range(3))
                if sample % 2:
                    y, z = (sum(rng.choice((0, 1, b-2, b-1)) << (k*i)
                                for i in range(f)) for _ in range(2))
                actual = source(x, y, z, k, f, rho)
                require(actual == word_model(x, y, z, k, f, rho), "source-domain random/boundary replay")
                require(source(*actual, k, f, rho, inverse=True) == (x, y, z), "source inverse")
                cases += 1
    return {"prefix_comparisons": prefix_cases, "sample_comparisons": cases-prefix_cases,
            "sample_seed": SEED, "source_K": [6, 7, 10], "all_offsets": True}


def negative_controls(source):
    fiber, averaged = 1-agreement((1, 1), 64), Q(1, 128)
    require(fiber == Q(1, 32) and fiber > averaged, "average-as-upper-bound control")
    adjacent = 1-agreement((1, 1, 0), 64)
    separated = 1-agreement((1, 0, 1), 64)
    require(adjacent == Q(1, 32) and separated == Q(1, 2048), "weight-only control")
    require(separated != 1-agreement((1, 1), 64), "zero-gap attenuation control")
    q = (65, 65, 0)
    actual = source(*q, 6, 3, 0)
    wanted = ideal(*q, 6, 3, 0)
    require(actual[1] == wanted[1] and actual[2] != wanted[2], "target-only false acceptance")
    require(actual == (65, 0, 262080), "pinned dirty-target counterexample")
    good_carry = (1, 0, 0)
    require(digit(0, 1, 0, 0, 64)[0][0] != 0, "nonzero intermediate carry fixture")
    require(source(*good_carry, 6, 2, 0) == ideal(*good_carry, 6, 2, 0),
            "all-carries-are-failures control")
    q_top = (1, 0, 0)
    require(source(*q_top, 6, 1, 0) != ideal(*q_top, 6, 1, 0, True),
            "omitted highest XOR control")
    return {"controls": 6, "uniform_average": str(averaged), "worst_two_bit_fiber": str(fiber),
            "adjacent_density": str(adjacent), "separated_density": str(separated),
            "target_only_false_acceptance": {"input": list(q), "actual": list(actual),
                                              "ideal": list(wanted)}}


def run():
    source = source_check()
    return {"status": "PASS_PACKED_SOURCE_FIBERS", "base_commit": BASE,
            "scope": "Exact source-conditioned address-map audit; no new kappa or physical compiler claim.",
            "symbolic": symbolic_checks(), "digit_cases": digit_checks(),
            "patterns": pattern_checks(), "whole_fibers": full_fiber_checks(source),
            "source_domain": source_domain_checks(source),
            "negative_controls": negative_controls(source)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; refuses to overwrite")
    args = parser.parse_args()
    if args.write is not None:
        require(not args.write.exists(), "refusing to overwrite receipt")
    result = run()
    if args.write is None:
        require(result == json.loads((HERE / "EXPECTED.json").read_text()), "receipt mismatch")
    else:
        with args.write.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(f"{result['status']} digit_cases={result['digit_cases']} "
          f"full_fiber_states={result['whole_fibers']['states']} "
          f"source_cases={sum(result['source_domain'][n] for n in ('prefix_comparisons', 'sample_comparisons'))} "
          f"controls={result['negative_controls']['controls']} no_new_kappa")


if __name__ == "__main__":
    main()

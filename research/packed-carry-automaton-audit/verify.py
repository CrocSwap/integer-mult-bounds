#!/usr/bin/env python3
"""Exact carry-state count and sparse-support audit for packed selected bits.

New code: Apache-2.0. Precious (@Kyu), with substantial OpenAI Codex
assistance. The eight updates are from OpenAI's manuscript; see SOURCE.json
and its pinned Apache-2.0 license. PR735's guard envelope is credited in README.
This is executable finite evidence, not a proof-assistant theorem.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 70
# (target: 0=y, 1=z; sign; tested parity of the other chunk).
OPS = ((0, -1, 0), (1, -1, 0), (0, 1, 0), (1, 1, 0),
       (1, 1, 1), (0, 1, 1), (1, -1, 1), (0, -1, 1))
STATES = (0, 5, 10, 80, 160)  # no carry; gate pairs 1/3, 2/4, 5/7, 6/8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar_trace(c, u, w):
    """Unrolled integer implementation, independent of OPS and packed masks."""
    states = [(u, w)]
    u -= c * (w % 2 == 0)
    states.append((u, w))
    w -= c * (u % 2 == 0)
    states.append((u, w))
    u += c * (w % 2 == 0)
    states.append((u, w))
    w += c * (u % 2 == 0)
    states.append((u, w))
    w += c * (u % 2 == 1)
    states.append((u, w))
    u += c * (w % 2 == 1)
    states.append((u, w))
    w -= c * (u % 2 == 1)
    states.append((u, w))
    u -= c * (w % 2 == 1)
    states.append((u, w))
    return states


def local_safe(c, u, w, base):
    """The proposed ideal-XOR-invariant, no-crossing region."""
    if not c:
        return True
    n = base // 2
    g, h = u // 2, w // 2
    return (g > 0 and h > 0) if w % 2 == 0 else (g < n - 1 and h < n - 1)


def trace_safe(c, u, w, base):
    return all(0 <= a < base and 0 <= b < base
               for a, b in scalar_trace(c, u, w))


def positions(k, f, rho):
    return range(rho, rho + k * (f - 1), k)


def ideal(x, y, z, k, f, rho, include_top=False):
    count = f if include_top else f - 1
    mask = sum(((x >> j) & 1) << j for j in range(rho, rho + k * count, k))
    return y ^ mask, z


def good(x, y, z, k, f, rho, predicate=local_safe):
    base = 1 << k
    return all(predicate((x >> j) & 1, (y >> j) & (base - 1),
                         (z >> j) & (base - 1), base)
               for j in positions(k, f, rho))


def original_good(x, y, z, k, f, rho):
    del x
    n = 1 << (k - 1)
    return all(10 <= ((v >> (j + 1)) & (n - 1)) <= n - 11
               for v in (y, z) for j in positions(k, f, rho))


def packed(x, y, z, k, f, rho, inverse=False, ops=OPS):
    """Full integer shifts, reduced modulo the complete chunk width."""
    values = [y, z]
    modulus = 1 << (k * f)
    for target, sign, parity in (reversed(ops) if inverse else ops):
        other = values[1 - target]
        offset = sum(1 << j for j in positions(k, f, rho)
                     if ((x >> j) & 1) and ((other >> j) & 1) == parity)
        values[target] = (values[target] + (-sign if inverse else sign) * offset) % modulus
    return tuple(values)


def ripple(x, y, z, k, f, rho):
    """Independent signed digit/carry implementation; no full-word addition.

    The lower rho bits are spectators. There are f-1 active radix-2^k
    digits and a final radix-2^(k-rho) suffix. Each gate computes all
    predicates from the unchanged source digits, then propagates its carry.
    """
    base = 1 << k
    suffix_base = 1 << (k - rho)
    js = list(positions(k, f, rho))
    controls = [(x >> j) & 1 for j in js]
    low_mask = (1 << rho) - 1
    low = [y & low_mask, z & low_mask]
    digits = [[(v >> j) & (base - 1) for j in js] for v in (y, z)]
    suffix = [v >> (rho + k * (f - 1)) for v in (y, z)]
    carries = []
    for target, sign, parity in OPS:
        carry = 0
        for i, c in enumerate(controls):
            increment = sign * c * (digits[1 - target][i] % 2 == parity)
            carry, digits[target][i] = divmod(digits[target][i] + increment + carry, base)
            carries.append(carry)
        suffix[target] = (suffix[target] + carry) % suffix_base
    values = tuple(low[t] + sum(d << j for d, j in zip(digits[t], js))
                   + (suffix[t] << (rho + k * (f - 1))) for t in (0, 1))
    return values, carries


def correct(x, y, z, k, f, rho, predicate=local_safe):
    if good(x, y, z, k, f, rho, predicate):
        return y, z
    pre_y, pre_z = packed(x, y, z, k, f, rho, inverse=True)
    return ideal(x, pre_y, pre_z, k, f, rho)


def correction_map(x, y, z, k, f, rho):
    """R = T0 S0^-1 at a CURRENT address, without a guard prefilter."""
    pre_y, pre_z = packed(x, y, z, k, f, rho, inverse=True)
    return ideal(x, pre_y, pre_z, k, f, rho)


def digit_transition(state, c, u, w, base):
    """One column of the chronological carry circuit, by integer divmod."""
    values = [u, w]
    outgoing = 0
    for i, (target, sign, parity) in enumerate(OPS):
        delta = sign * (c * (values[1 - target] % 2 == parity) + ((state >> i) & 1))
        carry, values[target] = divmod(values[target] + delta, base)
        require(carry in (0, sign), "carry direction")
        if carry:
            outgoing |= 1 << i
    return outgoing, values == [u ^ c, w]


def polynomial_product(a, b):
    out = [0, 0, 0]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def symbolic_matrix():
    """Universal parity/guard partition; coefficients are in N = B/2.

    For every one of 40 (incoming state, c, a, b) cases, the unwrapped
    normalized coordinates stay in [-2,3]. For K>=6, guard classes
    0, [1,N-2], N-1 therefore determine every quotient exactly, with
    multiplicities 1, N-2, 1. This is an exhaustive symbolic partition,
    not interpolation from a few numerical radices.
    """
    weights = ((1, 0), (-2, 1), (1, 0))
    rows = {}
    parity_cases = 0
    for state in STATES:
        row = {}
        for c, a, b in product(range(2), repeat=3):
            values = [a, b]
            trace = [tuple(values)]
            for i, (target, sign, parity) in enumerate(OPS):
                values[target] += sign * (c * (values[1 - target] % 2 == parity)
                                          + ((state >> i) & 1))
                trace.append(tuple(values))
            parity_cases += 1
            require(all(-2 <= v <= 3 for pair in trace for v in pair), "symbolic range")
            if values != [a ^ c, b]:
                # The terminal difference has magnitude < B, so it cannot
                # disappear modulo B in the stated K>=6 domain.
                continue
            for y_class, z_class in product(range(3), repeat=2):
                classes = (y_class, z_class)

                def quotient(v, which):
                    if which == 0:
                        return -int(v < 0)
                    if which == 1:
                        return 0
                    return int(v >= 2)

                outgoing = 0
                for i, (target, sign, _) in enumerate(OPS):
                    carry = (quotient(trace[i + 1][target], classes[target])
                             - quotient(trace[i][target], classes[target]))
                    require(carry in (0, sign), "symbolic carry direction")
                    if carry:
                        outgoing |= 1 << i
                require(outgoing in STATES, "matching-prefix states are closed")
                term = polynomial_product(weights[y_class], weights[z_class])
                previous = row.setdefault(outgoing, [0, 0, 0])
                for i in range(3):
                    previous[i] += term[i]
        rows[state] = row
    expected = {0: {0: [0, -4, 8], **{s: [0, 1, 0] for s in STATES[1:]}}}
    expected.update({s: {0: [0, -2, 4], s: [0, 2, 0]} for s in STATES[1:]})
    require(rows == expected, "symbolic transition polynomial table")
    for state in STATES:
        require(all(sum(sign * ((state >> i) & 1)
                        for i, (t, sign, _) in enumerate(OPS) if t == target) == 0
                    for target in (0, 1)), "top suffix must be restored")
    return rows, parity_cases


def evaluate_matrix(polynomials, base):
    n = base // 2
    return {s: {t: sum(a * n ** i for i, a in enumerate(p)) for t, p in row.items()}
            for s, row in polynomials.items()}


def failure_fraction(k, f):
    return 1 - (1 - Fraction(1, 2 << k)) ** max(f - 2, 0)


def automaton_audit():
    polynomials, parity_cases = symbolic_matrix()
    counts = []
    for k in range(2, 9):
        base = 1 << k
        actual = {}
        for state in STATES:
            row = Counter()
            for c, u, w in product(range(2), range(base), range(base)):
                outgoing, matches = digit_transition(state, c, u, w, base)
                if matches:
                    row[outgoing] += 1
            actual[state] = dict(row)
        require(actual == evaluate_matrix(polynomials, base), "literal transition table")
        counts.append({"K": k, "digit_cases": 5 * 2 * base * base, "matrix": actual})
    recurrence = []
    for k in (6, 7, 10):
        base = 1 << k
        matrix = evaluate_matrix(polynomials, base)
        dp = {0: 1}
        for m in range(65):
            total = (2 * base * base) ** m
            agreeing = sum(dp.values())
            expected = 1 if m == 0 else 2 * base * base * (2 * base * base - base) ** (m - 1)
            require(agreeing == expected, "closed-form matching-prefix count")
            require(Fraction(total - agreeing, total) == failure_fraction(k, m + 1), "failure fraction")
            if m in (0, 1, 2, 3, 7, 31, 64):
                recurrence.append({"K": k, "f": m + 1, "alphabet_words": total,
                                   "agreeing_words": agreeing,
                                   "failure_fraction": str(Fraction(total - agreeing, total))})
            next_dp = Counter()
            for s, multiplicity in dp.items():
                for t, weight in matrix[s].items():
                    next_dp[t] += multiplicity * weight
            dp = dict(next_dp)
    return {"symbolic_parity_cases": parity_cases, "polynomials_in_N": polynomials,
            "literal_digit_enumerations": counts, "recurrence_checks": recurrence}


def prior_simulator_audit():
    """Compare every source-minimum digit input with the pinned older engine.

    A preceding segment realizes each of the five carry states. No code
    from that earlier simulator is changed or copied into this verifier.
    """
    spec = importlib.util.spec_from_file_location(
        "packed_guard_prior", ROOT / "tests/test_finite_identities.py")
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    base, k, f, rho = 64, 6, 3, SEED % 6
    witnesses = {}
    for c, u, w in product(range(2), range(base), range(base)):
        outgoing, matches = digit_transition(0, c, u, w, base)
        if matches and outgoing not in witnesses:
            witnesses[outgoing] = (c, u, w)
    require(set(witnesses) == set(STATES), "incoming-state witnesses")
    rows = []
    for state in STATES:
        lower_c, lower_u, lower_w = witnesses[state]
        agreeing = 0
        for c, u, w in product(range(2), range(base), range(base)):
            x = (lower_c + base * c) << rho
            y = (lower_u + base * u) << rho
            z = (lower_w + base * w) << rho
            previous = prior.packed_steps(x, y, z, k, f, rho)
            require(previous == (x, *packed(x, y, z, k, f, rho)), "pinned simulator disagreement")
            agreeing += previous[1:] == ideal(x, y, z, k, f, rho)
        expected = 2 * base * base if state == 0 else base * base
        require(agreeing == expected, "source-simulator incoming-state count")
        rows.append({"incoming_state": state, "lower_witness_cuw": witnesses[state],
                     "K": k, "f": f, "rho": rho, "cases": 2 * base * base,
                     "agreeing": agreeing})
    return rows


def finite_repair_audit():
    """Exhaust full y,z arrays in small radices, including real payload movement.

    K<6 is a diagnostic extension of the integer identity, not a source-lemma
    instance. x's unused bits never enter any predicate; every selected-bit
    assignment is represented, including the separately applied top XOR.
    """
    rows = []
    for k, f in ((2, 3), (3, 2), (2, 1)):
        modulus = 1 << (k * f)
        for rho in range(k):
            total_bad = total_disagreements = support_count = 0
            for control_word in range(1 << f):
                x = sum(((control_word >> i) & 1) << (rho + i * k) for i in range(f))
                at_destination = [None] * (modulus * modulus)
                for y, z in product(range(modulus), repeat=2):
                    out_y, out_z = packed(x, y, z, k, f, rho)
                    dest = out_y * modulus + out_z
                    require(at_destination[dest] is None, "S0 is a bijection")
                    at_destination[dest] = y * modulus + z  # immutable payload
                    require(packed(x, out_y, out_z, k, f, rho, inverse=True) == (y, z), "inverse")
                    admitted = good(x, y, z, k, f, rho)
                    require(admitted == good(x, out_y, out_z, k, f, rho), "global invariance")
                    expected = ideal(x, y, z, k, f, rho)
                    require(not admitted or (out_y, out_z) == expected, "agreement off B")
                    total_bad += not admitted
                    total_disagreements += (out_y, out_z) != expected
                # Extract exactly the support of R on CURRENT addresses.
                holes, extracted = [], []
                for rank, payload in enumerate(at_destination):
                    y, z = divmod(rank, modulus)
                    cy, cz = correction_map(x, y, z, k, f, rho)
                    if (cy, cz) != (y, z):
                        holes.append(rank)
                        extracted.append((cy * modulus + cz, payload))
                        support_count += 1
                extracted.sort()
                require([rank for rank, _ in extracted] == holes, "repair keys equal marked holes")
                for rank, (_, payload) in zip(holes, extracted):
                    at_destination[rank] = payload
                for rank, payload in enumerate(at_destination):
                    y, z = divmod(payload, modulus)
                    current_y, current_z = divmod(rank, modulus)
                    final = (current_y ^ (((x >> (rho + k * (f - 1))) & 1)
                                         << (rho + k * (f - 1))), current_z)
                    require(final == ideal(x, y, z, k, f, rho, include_top=True), "reinserted payload")
            total = (1 << f) * modulus * modulus
            q = Fraction(2, 1 << k) - Fraction(2, 1 << (2 * k))
            require(Fraction(total_bad, total) == 1 - (1 - q) ** (f - 1), "product cardinality")
            require(support_count == total_disagreements, "failure/support bijection")
            require(Fraction(support_count, total) == failure_fraction(k, f), "automaton versus whole words")
            rows.append({"K": k, "f": f, "rho": rho, "states": total,
                         "guard_envelope_states": total_bad, "exact_support_states": support_count,
                         "unrepaired_disagreements": total_disagreements})
    return rows


def source_domain_audit():
    rng = random.Random(SEED)
    rows = []
    for k, f in ((6, 1), (6, 2), (6, 3), (6, 7), (7, 4), (10, 5), (16, 3)):
        modulus = 1 << (k * f)
        offsets = [SEED % k] + [rho for rho in range(k) if rho != SEED % k]
        for rho in offsets:
            good_count = bad_count = disagreements = 0
            # Uniform full chunks and boundary-heavy chunks; a fixed 1024 of each.
            for case in range(2048):
                x, y, z = (rng.randrange(modulus) for _ in range(3))
                if case >= 1024:
                    ds = (0, 1, 2, 3, (1 << k) - 3, (1 << k) - 2, (1 << k) - 1)
                    mask = sum(((1 << k) - 1) << j for j in positions(k, f, rho))
                    y = (y & ~mask) | sum(rng.choice(ds) << j for j in positions(k, f, rho))
                    z = (z & ~mask) | sum(rng.choice(ds) << j for j in positions(k, f, rho))
                out = packed(x, y, z, k, f, rho)
                digit_out, carries = ripple(x, y, z, k, f, rho)
                require(out == digit_out, "independent signed carry replay")
                require(packed(x, *out, k, f, rho, inverse=True) == (y, z), "packed inverse")
                admitted = good(x, y, z, k, f, rho)
                require(admitted == good(x, *out, k, f, rho), "packed invariant region")
                require(not original_good(x, y, z, k, f, rho) or admitted, "retained region inclusion")
                if admitted:
                    require(not any(carries), "admitted trace crosses a segment boundary")
                    require(out == ideal(x, y, z, k, f, rho), "admitted output")
                    good_count += 1
                else:
                    bad_count += 1
                require(correct(x, *out, k, f, rho) == ideal(x, y, z, k, f, rho), "sparse correction")
                require(correction_map(x, *out, k, f, rho) == ideal(x, y, z, k, f, rho), "exact support correction")
                disagreements += out != ideal(x, y, z, k, f, rho)
            rows.append({"K": k, "f": f, "rho": rho, "states": 2048,
                         "good": good_count, "bad": bad_count, "unrepaired_disagreements": disagreements})
    require(sum(r["unrepaired_disagreements"] for r in rows) > 0, "boundary coverage")
    return rows


def negative_controls():
    controls = []
    # Current q is raw-no-crossing, yet T0 S0^-1(q) != q. A sparse repair that
    # marks only raw crossing states silently leaves the wrong payload here.
    for rho in (0, SEED % 6):
        k, f = 6, 3
        x, y, z = (v << rho for v in (65, 0, 127))
        require(good(x, y, z, k, f, rho, trace_safe), "naive counterexample admission")
        require(not good(x, y, z, k, f, rho), "invariant closure must reject q")
        pre = packed(x, y, z, k, f, rho, inverse=True)
        expected = ideal(x, *pre, k, f, rho)
        require(packed(x, *pre, k, f, rho) == (y, z), "counterexample preimage")
        require(expected != (y, z), "omitting repair must fail")
        require(correct(x, y, z, k, f, rho, trace_safe) != expected, "naive repair must fail")
        require(packed(x, y, z, k, f, rho) == ideal(x, y, z, k, f, rho), "q must pass forward-failure test")
        require(correct(x, y, z, k, f, rho) == expected, "closed repair must pass")
        controls.append({"name": "forward_failure_test_at_current_address_is_wrong", "K": k, "f": f, "rho": rho,
                         "current_q": [x, y, z], "preimage_yz": pre, "required_destination_yz": expected})
    # Every excluded end in the invariant local characterization is needed
    # for at least one of the two ideal-XOR-related parity states.
    for label, u, w in (("lower_y", 0, 2), ("lower_z", 3, 0),
                        ("upper_y", 62, 3), ("upper_z", 3, 63)):
        require(not local_safe(1, u, w, 64), "forbidden endpoint")
        require(not trace_safe(1, u, w, 64), "endpoint must cross")
        controls.append({"name": label, "c": 1, "u": u, "w": w,
                         "trace": scalar_trace(1, u, w)})
    # Alter a real primitive sign, and verify that the endpoint oracle detects it.
    mutant = list(OPS)
    mutant[5] = (0, -1, 1)
    args = (1, 2, 2, 6, 2, 0)
    require(good(*args), "interior mutant input")
    require(packed(*args, ops=mutant) != ideal(*args), "wrong-sign primitive was undetected")
    controls.append({"name": "gate6_wrong_sign", "arguments": args,
                     "actual_yz": packed(*args, ops=mutant), "expected_yz": ideal(*args)})
    args = (16, 0, 63, 6, 1, 4)
    require(packed(*args) != ideal(*args, include_top=True), "omitted top XOR was undetected")
    controls.append({"name": "omit_top_selected_bit", "arguments": args,
                     "actual_yz": packed(*args), "expected_yz": ideal(*args, include_top=True)})
    return controls


def verify_sources():
    source = json.loads((HERE / "SOURCE.json").read_text())
    for path, expected in source["files"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        require(actual == expected, "source drift: " + path)
    return source


def run():
    source = verify_sources()
    automaton = automaton_audit()
    previous = prior_simulator_audit()
    finite = finite_repair_audit()
    sampled = source_domain_audit()
    controls = negative_controls()
    return {"schema": "packed-carry-automaton-audit-v1", "seed": SEED, "source": source,
            "scope": "Written universal carry argument plus finite exact replay; no new kappa or tape theorem.",
            "automaton": automaton, "exhaustive_small_radix_repair": finite,
            "pinned_prior_simulator": previous,
            "sampled_source_domain": sampled, "negative_controls": controls,
            "totals": {"digit_cases": sum(r["digit_cases"] for r in automaton["literal_digit_enumerations"]),
                       "prior_simulator_cases": sum(r["cases"] for r in previous),
                       "repair_states": sum(r["states"] for r in finite),
                       "source_domain_samples": sum(r["states"] for r in sampled),
                       "negative_controls": len(controls)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", type=Path, help="write a deterministic receipt instead of checking it")
    group.add_argument("--check", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = run()
    # Normalize tuples in both evidence and loaded JSON.
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(encoded)
    else:
        require(json.loads(encoded) == json.loads(args.check.read_text()), "receipt mismatch")
    counts = result["totals"]
    print("PASS_PACKED_CARRY_AUTOMATON " + " ".join(f"{name}={value}" for name, value in counts.items()))


if __name__ == "__main__":
    main()

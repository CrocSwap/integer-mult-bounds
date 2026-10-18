#!/usr/bin/env python3
"""Exact audit of an invariant guard envelope for the eight packed additions.

Aryan Sudhir (AryanSudhirDev), with substantial OpenAI Codex assistance.
Apache-2.0. Independent integer implementation; no repository engine imports.
The finite checks corroborate README.md's proof, not the multiplication theorem.
"""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 62
# (target: 0=y or 1=z, sign, tested parity of the other coordinate).
LINES = ((0, -1, 0), (1, -1, 0), (0, 1, 0), (1, 1, 0),
         (1, 1, 1), (0, 1, 1), (1, -1, 1), (0, -1, 1))
TERMS = ("y_low", "z_low", "y_high", "z_high")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_trace(a, b, c=1):
    """Unbounded signed-integer trajectory, including the input."""
    v = [a, b]
    trace = [tuple(v)]
    for dst, sign, parity in LINES:
        v[dst] += c * sign * (v[1 - dst] % 2 == parity)
        trace.append(tuple(v))
    return trace


def positions(K, f, rho):
    require(K >= 1 and f >= 1 and 0 <= rho < K, "invalid layout")
    return tuple(rho + i * K for i in range(f - 1))


def packed(x, y, z, K, f, rho, inverse=False, lines=LINES):
    """Whole-slot modular rotations, with predicates recomputed each step."""
    places = positions(K, f, rho)
    mask = (1 << (K * f)) - 1
    v = [y, z]
    program = reversed(lines) if inverse else lines
    for dst, sign, parity in program:
        other = v[1 - dst]
        shift = 0
        for j in places:
            if ((x >> j) & 1) and ((other >> j) & 1) == parity:
                shift |= 1 << j
        v[dst] = (v[dst] + (-sign if inverse else sign) * shift) & mask
    return x, v[0], v[1]


def ideal(x, y, z, K, f, rho):
    mask = sum((x & (1 << j)) for j in positions(K, f, rho))
    return x, y ^ mask, z


def guard_terms(x, y, z, K, f, rho):
    G = 1 << (K - 1)
    found = set()
    for j in positions(K, f, rho):
        if not (x >> j) & 1:
            continue
        g = (y >> (j + 1)) & (G - 1)
        h = (z >> (j + 1)) & (G - 1)
        b = (z >> j) & 1
        if b == 0:
            if g == 0:
                found.add("y_low")
            if h == 0:
                found.add("z_low")
        else:
            if g == G - 1:
                found.add("y_high")
            if h == G - 1:
                found.add("z_high")
    return found


def bad(x, y, z, K, f, rho):
    return bool(guard_terms(x, y, z, K, f, rho))


def density(K, f):
    B = 1 << K
    return 1 - (1 - Fraction(2, B) + Fraction(2, B * B)) ** (f - 1)


def audit_one(x, y, z, K, f, rho):
    original = (x, y, z)
    out = packed(*original, K, f, rho)
    target = ideal(*original, K, f, rho)
    exceptional = bad(*original, K, f, rho)
    require(bad(*target, K, f, rho) == exceptional, "ideal changes bad-set membership")
    output_exceptional = bad(*out, K, f, rho)
    require(output_exceptional == exceptional, "packed map changes bad-set membership")
    preimage = packed(*out, K, f, rho, inverse=True)
    require(preimage == original, "modular inverse does not recover all three slots")
    repaired = ideal(*preimage, K, f, rho) if output_exceptional else out
    require(repaired == target, "repair did not implement the ideal permutation")
    if not exceptional:
        require(out == target, "a good address needs repair")
    return exceptional, out != target


def scalar_audit():
    expected = {
        (0, 0): ((-1, 1), (0, 1)),
        (0, 1): ((0, 2), (0, 1)),
        (1, 0): ((0, 1), (-1, 0)),
        (1, 1): ((0, 1), (1, 2)),
    }
    traces = []
    for (a, b), extrema in expected.items():
        trace = local_trace(a, b)
        actual = tuple((min(v[j] for v in trace), max(v[j] for v in trace)) for j in (0, 1))
        require(actual == extrema, "parity trajectory extrema changed")
        require(trace[-1] == (1 - a, b), "scalar identity failed")
        traces.append({"a": a, "b": b, "trace": trace, "extrema": actual})

    # For each quotient class, test BOTH y parities. This is exactly the
    # T0-invariant, no-segment-escape guard class in the written maximality claim.
    classes = []
    for K in range(1, 8):
        B = 1 << K
        G = B // 2
        good = 0
        for c, b, g, h in product(range(2), range(2), range(G), range(G)):
            all_inside = all(
                0 <= u < B and 0 <= w < B
                for a in range(2) for u, w in local_trace(2 * g + a, 2 * h + b, c)
            )
            envelope_good = c == 0 or (g > 0 and h > 0 if b == 0 else g < G - 1 and h < G - 1)
            require(all_inside == envelope_good, "guard condition is not equivalent to both-parity no-escape")
            good += all_inside
        total = 4 * G * G
        require(Fraction(total - good, total) == density(K, 2), "local density mismatch")
        classes.append({"K": K, "quotient_classes": total, "good": good, "bad": total - good})
    return {"parity_traces": traces, "quotient_class_checks": classes}


def exhaustive_audit():
    reports = []
    for K, f in ((1, 3), (2, 3), (3, 2), (4, 2)):
        M = 1 << (K * f)
        for rho in range(K):
            cases = exceptional = failures = 0
            for control in range(1 << (f - 1)):
                x = sum(((control >> i) & 1) << j for i, j in enumerate(positions(K, f, rho)))
                fiber_exceptional = 0
                fiber_failures = 0
                for y, z in product(range(M), repeat=2):
                    is_bad, differs = audit_one(x, y, z, K, f, rho)
                    cases += 1
                    exceptional += is_bad
                    failures += differs
                    fiber_exceptional += is_bad
                    fiber_failures += differs
                active = bin(control).count("1")
                G = 1 << (K - 1)
                fiber_density = 1 - Fraction(G - 1, G) ** (2 * active)
                require(Fraction(fiber_exceptional, M * M) == fiber_density,
                        "fixed-control fiber density mismatch")
                require(active > 1 or fiber_failures == 0,
                        "at most one active control must need no repair")
            require(Fraction(exceptional, cases) == density(K, f), "global exact density mismatch")
            reports.append({"K": K, "f": f, "rho": rho, "cases": cases,
                            "envelope_addresses": exceptional, "actual_disagreements": failures,
                            "envelope_fraction": str(density(K, f))})
    return reports


def large_guard_audit():
    rng = random.Random(SEED)
    cases = exceptional = failures = 0
    # This includes the original lemma's K>=6 domain, f=1, and extreme offsets.
    for K in (6, 7, 10, 16):
        B = 1 << K
        boundary_values = (0, 1, 2, 3, B - 4, B - 3, B - 2, B - 1)
        for rho in (0, K - 1):
            for u0, u1, w0, w1 in product(boundary_values, repeat=4):
                x = (1 | (1 << K)) << rho
                y = (u0 | (u1 << K)) << rho
                z = (w0 | (w1 << K)) << rho
                is_bad, differs = audit_one(x, y, z, K, 3, rho)
                cases += 1
                exceptional += is_bad
                failures += differs
        for f in (1, 2, 3, 5):
            for rho in range(K):
                for _ in range(32):
                    xyz = [rng.getrandbits(K * f) for _ in range(3)]
                    is_bad, differs = audit_one(*xyz, K, f, rho)
                    cases += 1
                    exceptional += is_bad
                    failures += differs
    return {"seed": SEED, "cases": cases, "envelope_addresses": exceptional,
            "actual_disagreements": failures,
            "boundary_domain": "K=6,7,10,16; f=3; rho=0,K-1; two active controls; each used segment in {0,1,2,3,B-4,B-3,B-2,B-1}",
            "sample_domain": "K=6,7,10,16; f=1,2,3,5; every rho; 32 full-width triples per layout"}


def negative_controls():
    # Deliberately weaken each boundary condition. Search a fixed, fully
    # enumerated boundary domain inside the ORIGINAL K>=6 regime.
    K, f, rho = 6, 3, 0
    B = 1 << K
    values = (0, 1, 2, 3, B - 4, B - 3, B - 2, B - 1)
    x = B + 1
    found = {}
    wrong_order = None
    for u0, u1, w0, w1 in product(values, repeat=4):
        original = (x, u0 + B * u1, w0 + B * w1)
        triggers = guard_terms(*original, K, f, rho)
        out = packed(*original, K, f, rho)
        target = ideal(*original, K, f, rho)
        if out != target and len(triggers) == 1:
            term = next(iter(triggers))
            if term not in found:
                found[term] = {"removed_guard": term, "input": original, "actual": out, "ideal": target}
        if wrong_order is None and triggers:
            wrong = packed(*ideal(*out, K, f, rho), K, f, rho, inverse=True)
            if wrong != target:
                wrong_order = {"input": original, "packed_output": out, "wrong_repair": wrong, "ideal": target}
    require(set(found) == set(TERMS), "a removed guard has no failure witness")
    require(wrong_order is not None, "wrong repair order has no failure witness")

    # Two changes to the operations themselves must fail even on good inputs.
    original = (x, 2 + 2 * B, 2 + 2 * B)
    require(not bad(*original, K, f, rho), "mutation input must be good")
    operation_mutations = []
    for label, mutated in (
        ("negate_line_7", LINES[:6] + ((1, 1, 1),) + LINES[7:]),
        ("omit_line_1", LINES[1:]),
    ):
        out = packed(*original, K, f, rho, lines=mutated)
        target = ideal(*original, K, f, rho)
        require(out != target, "operation mutation was not detected: " + label)
        operation_mutations.append({"mutation": label, "input": original, "actual": out, "ideal": target})
    return {"layout": {"K": K, "f": f, "rho": rho},
            "removed_guards": [found[name] for name in TERMS],
            "wrong_repair_order": wrong_order, "operation_mutations": operation_mutations}


def source_pins():
    claim = json.loads((HERE / "CLAIM.json").read_text())
    for relative, digest in claim["source_sha256"].items():
        require(sha256((ROOT / relative).read_bytes()).hexdigest() == digest,
                "pinned source changed: " + relative)
    return {"base_commit": claim["base_commit"], "source_sha256": claim["source_sha256"]}


def build_report():
    return {
        "status": "PASS_PACKED_GUARD_ENVELOPE_AUDIT",
        "scope": "Exact finite audit plus a written all-K guard-envelope proof; no new kappa, machine-time implementation, or full multiplication proof.",
        "source": source_pins(),
        "scalar": scalar_audit(),
        "exhaustive": exhaustive_audit(),
        "large_guard": large_guard_audit(),
        "negative_controls": negative_controls(),
        "density_examples": [{"K": K, "f": f, "exact": str(density(K, f)),
                              "new_union_bound": str(min(Fraction(1), Fraction(2 * (f - 1), 1 << K))),
                              "old_union_bound": str(min(Fraction(1), Fraction(80 * (f - 1), 1 << K)))}
                             for K, f in ((6, 2), (6, 3), (10, 5), (16, 32))],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write RESULT.json instead of comparing it")
    args = parser.parse_args()
    # JSON round-trip canonicalizes tuples; receipts contain no elapsed times.
    report = json.loads(json.dumps(build_report()))
    receipt = HERE / "RESULT.json"
    if args.write:
        receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        require(report == json.loads(receipt.read_text()), "recomputed result differs from RESULT.json")
    total = sum(row["cases"] for row in report["exhaustive"])
    print(report["status"])
    print(f"{total} exhaustive packed states; {report['large_guard']['cases']} boundary/seeded states; 7 negative controls")
    print("delta = 1 - (1 - 2/2^K + 2/2^(2K))^(f-1) <= min(1, 2(f-1)/2^K)")
    print("No new kappa; RESULT.json matches the declared finite coverage.")


if __name__ == "__main__":
    main()

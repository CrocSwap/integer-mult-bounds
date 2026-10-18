#!/usr/bin/env python3
"""Exact replay. Hanson Sun with substantial OpenAI Codex assistance; Apache-2.0."""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m


def primitive_map(word, registers):
    rows = {r: [Q(int(i == j)) for j in range(len(registers))]
            for i, r in enumerate(registers)}
    for op in word:
        tag, target = op[:2]
        if tag in ("add", "subtract"):
            sign = 1 if tag == "add" else -1
            rows[target] = [a + sign * b for a, b in zip(rows[target], rows[op[2]])]
        elif tag == "copy":
            rows[target] = rows[op[2]].copy()
        elif tag == "clear":
            rows[target] = [Q(0)] * len(registers)
        else:
            m.require(tag in ("double", "halve", "negate"), "primitive matrix opcode")
            factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            rows[target] = [factor * a for a in rows[target]]
    return rows


def check_macro(z, word=None):
    registers = [(name, c) for name in ("T", "S", "W") for c in range(2)]
    word = m.lower_gaussian(z) if word is None else word
    rows = primitive_map(word, registers)
    expected = {
        ("T", 0): [1, 0, z[0], -z[1], 0, 0],
        ("T", 1): [0, 1, z[1], z[0], 0, 0],
        ("S", 0): [0, 0, 1, 0, 0, 0],
        ("S", 1): [0, 0, 0, 1, 0, 0],
        ("W", 0): [0] * 6, ("W", 1): [0] * 6,
    }
    m.require(rows == expected, "six-column dirty Gaussian macro")
    m.require(len(word) == m.gaussian_add_cost(z), "macro cost")


def check_boundary(a, odd, forward=None, backward=None):
    honest_f, honest_b = m.boundary_word(a, odd)
    forward = honest_f if forward is None else forward
    backward = honest_b if backward is None else backward
    registers = [("X", 0), ("X", 1)]
    z = m.gauge(a, odd)
    expected = {registers[0]: [z[0], -z[1]], registers[1]: [z[1], z[0]]}
    m.require(primitive_map(forward, registers) == expected, "boundary forward map")
    m.require(primitive_map(forward + backward, registers) ==
              {registers[0]: [1, 0], registers[1]: [0, 1]}, "boundary restoration")


def total_gauge_cost(events, assignments):
    """Complete scalar cost, with phase-zero optimal boundary circuits."""
    factors = {("L", h): m.gauge(a, odd) for h, (a, odd) in assignments.items()}
    cost = sum(2 * abs(2 * a + 1) + 4 if odd else 4 * abs(a)
               for a, odd in assignments.values())
    for ev in events:
        if ev[0] != "scalar":
            continue
        g = ev[1]
        if g[0] == "add":
            z = m.mul((Q(g[3], g[4]), Q(0)),
                      m.mul(factors.get(tuple(g[1]), m.ONE),
                            m.inv(factors.get(tuple(g[2]), m.ONE))))
            cost += m.gaussian_add_cost(z)
        elif g[0] == "scale":
            q = Q(g[2], g[3])
            p, e = m.parts(q)
            m.require(p == 1, "original dyadic SCALE")
            cost += 2 * (abs(e) + int(q < 0))
        else:
            m.require(g[0] in ("copy", "clear"), "full invoice opcode")
            cost += 2
    return cost


def rounding_checks(events, helpers):
    results = []
    for pattern in range(4):
        assignments = {h: ((h * (pattern + 1) + 24) % 9 - 4,
                           int((h + pattern) % (pattern + 2) == 0)) for h in helpers}
        odd_count = sum(b for a, b in assignments.values())
        gaussian = total_gauge_cost(events, assignments)
        low = total_gauge_cost(events, {h: (a, 0) for h, (a, b) in assignments.items()})
        high = total_gauge_cost(events, {h: (a + b, 0) for h, (a, b) in assignments.items()})
        gap_twice = 2 * gaussian - low - high
        m.require(gap_twice >= 8 * odd_count, "common rounding dominance")
        results.append({"pattern": pattern, "odd_helpers": odd_count,
                        "gaussian_cost": gaussian, "low_cost": low, "high_cost": high,
                        "twice_gap_above_average": gap_twice})
    return results


def reject(label, fn, expected):
    try:
        fn()
    except ValueError as exc:
        m.require(expected in str(exc), "wrong rejection for " + label + ": " + str(exc))
        return label
    raise ValueError("control unexpectedly accepted: " + label)


def controls():
    result = []
    def add(label, fn, reason):
        result.append(reject(label, fn, reason))
    mixed = (Q(3, 2), Q(3, 2))
    word = m.lower_gaussian(mixed)
    second = next(i for i, g in enumerate(word) if g[:2] == ("add", ("T", 1)))
    add("missing_shared_target", lambda: check_macro(mixed, word[:second] + word[second + 1:]), "six-column")
    wrong = list(word)
    wrong[second] = ("subtract", *wrong[second][1:])
    add("wrong_cross_channel_sign", lambda: check_macro(mixed, wrong), "six-column")
    add("missing_product_initialization", lambda: check_macro(mixed, word[1:]), "six-column")
    unit_word = m.lower_gaussian((Q(1), Q(1)))
    add("dirty_work_not_cleared", lambda: check_macro((Q(1), Q(1)), unit_word[:-1]), "six-column")
    f, b = m.boundary_word(-3, 1)
    add("missing_inverse_boundary", lambda: check_boundary(-3, 1, f, []), "boundary restoration")
    broken = list(f)
    broken[0] = ("double", *broken[0][1:])
    add("wrong_boundary_shift", lambda: check_boundary(-3, 1, broken, b), "boundary forward")
    add("operand_alias", lambda: m.lower_gaussian(mixed, ("T",), ("T",)), "distinct complex")
    add("outside_gaussian_support", lambda: m.lower_gaussian((Q(1), Q(2))), "Gaussian support")
    add("nondyadic_coefficient", lambda: m.c(Q(1, 3)), "nonzero dyadic")
    add("gaussian_nonunit", lambda: m.unit_coordinates((Q(2), Q(1))), "unit diagonal")
    add("zero_factor", lambda: m.unit_coordinates(m.ZERO), "nonzero Gaussian unit")
    add("false_one_step_lipschitz", lambda: m.require(m.c(2) <= m.c(1) + 1, "unit discount jump"), "unit discount")
    # Ten repeated edges disprove independent rather than common rounding.
    gaussian_toy = 10 * 2 * m.c(1) + 12
    independent_mean = 10 * (4 * m.c(1) + 2 * m.c(2) + 2 * m.c(Q(1, 2))) // 4 + 4
    add("false_independent_rounding", lambda: m.require(gaussian_toy >= independent_mean, "rounding must be common"), "common")
    manifest = json.loads((m.HERE / "SOURCES.json").read_bytes())
    missing = copy.deepcopy(manifest)
    missing["files"] = [r for r in missing["files"] if r["path"] != m.LOWER]
    add("removed_source_pin", lambda: m.check_sources(missing), "source inventory")
    altered = copy.deepcopy(manifest)
    altered["base_commit"] = "0" * 40
    add("wrong_base", lambda: m.check_sources(altered), "base commit")
    add("modified_lowerer", lambda: m.check_sources(reader=lambda p:
        (m.ROOT / p).read_bytes() + (b"\n# changed\n" if p == m.LOWER else b"")), "source SHA256")
    return result


def compute():
    word, programs, bindings, _, _ = m.load()
    helpers = m.domain(word, programs)
    m.require(len(helpers) == 237, "eligible helper count")
    census = {}
    result = {"status": "PASS_GAUSSIAN_UNIT_COMMON_ROUNDING",
              "base_commit": m.BASE, "assignment_seed": 24,
              "eligible_helpers": helpers, "seed_selected_probe_helper": helpers[24],
              "source_members": bindings, "orientations": {}}
    coefficients = set()
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        rows = m.census(events, helpers)
        census[orientation] = rows
        entry = {"census_rows": len(rows),
                 "integer_breakpoint_evaluations": sum(len(r["real_candidates"]) + len(r["odd_candidates"]) for r in rows),
                 "rounding_fixtures": rounding_checks(events, helpers)}
        variants = [("baseline", {})]
        for name in ("real", "odd"):
            key = name + "_best"
            winner = min(rows, key=lambda r: (r[key][1], r["helper"], abs(r[key][0]), r[key][0]))
            a, delta = winner[key]
            entry[name + "_winner"] = {"helper": winner["helper"], "a": a, "delta": delta,
                                       "incident_adds": winner["incident_adds"]}
            variants.append((name, {winner["helper"]: (a, int(name == "odd"))}))
        prices = {}
        for name, assignments in variants:
            stream = m.transformed(events, assignments)
            m.require([e for e in stream if e[0] != "scalar"] ==
                      [e for e in events if e[0] != "scalar"], "non-scalar stream unchanged")
            endpoint = m.replay(stream, assignments, orientation)
            price = m.invoice(stream, assignments)
            m.require(price["complex_scalar_primitives"] == total_gauge_cost(events, assignments),
                      "formula versus emitted complete invoice")
            for ev in stream:
                if ev[0] == "scalar" and ev[1][0] == "add":
                    coefficients.add((Q(*ev[1][3]), Q(*ev[1][4])))
            prices[name] = {"endpoint": endpoint, "invoice": price,
                            "gaussian_macro_stream_sha256": m.sha(m.canonical(stream)),
                            "assignments": {str(h): [a, b] for h, (a, b) in assignments.items()}}
        before = prices["baseline"]["invoice"]
        m.require(before["complex_scalar_primitives"] == (149002 if orientation == "forward" else 149018), "retained baseline invoice")
        for name in ("real", "odd"):
            after = prices[name]["invoice"]
            m.require(after["paid_profile"] == before["paid_profile"], "paid profile unchanged")
            m.require(after["complex_scalar_primitives"] - before["complex_scalar_primitives"] ==
                      entry[name + "_winner"]["delta"], "census versus materialized winner")
        entry["programs"] = prices
        result["orientations"][orientation] = entry
    for e in (-16, -3, -1, 0, 1, 2, 16):
        for p in (1, 3, 5, 7):
            for phase in range(4):
                coefficients.add(m.mul((p * m.power(e), p * m.power(e)), m.gauge(0, 0, phase)))
    for z in sorted(coefficients):
        check_macro(z)
    for a in range(-16, 17):
        for odd in (0, 1):
            check_boundary(a, odd)
    result["local_primitive_checks"] = {"distinct_gaussian_macros": len(coefficients),
                                        "formal_columns_per_macro": 6,
                                        "boundary_pairs": 66}
    result["rejection_controls"] = controls()
    result["census_payload_sha256"] = m.sha(m.canonical(census))
    result["scope"] = "Written common-rounding theorem for the specified macro-local lowering and separate two-register boundaries; finite exact k8 evidence. No native hosting, new paid profile, kappa or full multiplication theorem."
    return result, census


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this package's own certificates")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result, census = compute()
    if args.write:
        (m.HERE / "CERTIFICATE.json").write_text(json.dumps(result, indent=2) + "\n")
        (m.HERE / "CENSUS.json.gz").write_bytes(gzip.compress(m.canonical(census), mtime=0))
    else:
        m.require(m.canonical(result) == m.canonical(json.loads((m.HERE / "CERTIFICATE.json").read_bytes())), "certificate mismatch")
        m.require(m.canonical(census) == m.canonical(json.loads(gzip.decompress((m.HERE / "CENSUS.json.gz").read_bytes()))), "census mismatch")
    print(json.dumps(result, indent=2) if args.json else
          "PASS_GAUSSIAN_UNIT_COMMON_ROUNDING helpers=237 orientations=2 real_saving=332 odd_saving=58 controls=" + str(len(result["rejection_controls"])))


if __name__ == "__main__":
    main()

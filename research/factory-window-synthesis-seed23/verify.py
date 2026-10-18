#!/usr/bin/env python3
"""Exact, bounded factory-window synthesis; no new kappa.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
Factory and lowering credits are retained in README.md and SOURCES.json.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/complex-factory-scale-frontier27/sources/PR924-COMPOSITION.json"
REFERENCE = "research/complex-factory5-resynthesis/CIRCUIT.json"
LOWERING = "research/complex-dyadic-lowering/lower.py"
INVOICE = "research/complex-k492-owner-repair/code/assemble.py"
SEED = 23
FRAME = [390, 74, 44, 30]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # Unlike Python equality, this distinguishes true from 1 and 1.0 from 1.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_sources():
    pins = read(HERE / "SOURCES.json")
    require(set(pins["files"]) == {SOURCE, REFERENCE, LOWERING, INVOICE}, "source inventory")
    for name, expected in pins["files"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                "source pin: " + name)
    return pins


def identity(n):
    # All entries share denominator 2**state[-1]; normalize after each gate.
    return tuple(int(i == j) for i in range(n) for j in range(n)) + (0,)


def apply(state, gate, n):
    kind, target, source, sign, exponent = gate
    depth, old = state[-1], state[:-1]
    out = list(old)
    if exponent < 0:
        out = [x << -exponent for x in out]
        depth -= exponent
    shift = max(exponent, 0)
    for j in range(n):
        pos = target * n + j
        if kind == "add":
            out[pos] += sign * (old[source * n + j] << shift)
        else:
            out[pos] = sign * (old[pos] << shift)
    while depth and all(x % 2 == 0 for x in out):
        out = [x // 2 for x in out]
        depth -= 1
    return tuple(out) + (depth,)


def execute(word, n):
    state = identity(n)
    for gate in word:
        state = apply(state, gate, n)
    return state


def inverse(gate):
    kind, t, s, sign, exponent = gate
    return (kind, t, s, -sign, exponent) if kind == "add" else (
        kind, t, s, sign, -exponent)


def variants(word):
    inv = [inverse(g) for g in reversed(word)]

    def transpose(g):
        return (g[0], g[2], g[1], g[3], g[4]) if g[0] == "add" else g
    return {
        "forward": word,
        "inverse": inv,
        "transpose": [transpose(g) for g in reversed(word)],
        "inverse_transpose": [transpose(g) for g in reversed(inv)],
    }


def cost(gate):
    if gate[0] == "add":
        return 2 if gate[4] == 0 else 3 + abs(gate[4])
    return abs(gate[4]) + int(gate[3] < 0)


def alphabet(n):
    gates = []
    for kind in ("add", "scale"):
        for target in range(n):
            for source in (range(n) if kind == "add" else (-1,)):
                for sign in (-1, 1):
                    for exponent in (-1, 0, 1):
                        if kind == "add" and source == target:
                            continue
                        if kind == "scale" and (sign, exponent) == (1, 0):
                            continue
                        gates.append((kind, target, source, sign, exponent))
    require(len(gates) == 6 * n * n - n, "alphabet incomplete")
    return gates


def parse(op, wires):
    require(isinstance(op, list) and op and op[0] in ("add", "scale"), "gate kind")
    require(len(op) == (6 if op[0] == "add" else 5), "gate shape")
    require(canonical(op[-1]) == canonical(FRAME), "frame mismatch")
    require(all(type(x) is int for x in op[1:-1]), "integer fields required")
    if op[0] == "add":
        kind, t, s, numerator, denominator, _ = op
        require(t != s, "source aliases target")
    else:
        kind, t, numerator, denominator, _ = op
        s = -1
    require(denominator != 0, "zero denominator")
    q = Fraction(numerator, denominator)
    require(q in map(Fraction, ("-2", "-1", "-1/2", "1/2", "1", "2")),
            "coefficient outside declared alphabet")
    exponent = abs(q.numerator).bit_length() - q.denominator.bit_length()
    g = (kind, wires.index(t), wires.index(s) if kind == "add" else -1,
         1 if q > 0 else -1, exponent)
    require(g in alphabet(len(wires)), "gate outside declared alphabet")
    return g


def short_frontier(n, gates=None):
    gates = alphabet(n) if gates is None else gates
    unit = identity(n)
    states = {unit: (0, 0, ())}
    singles = [apply(unit, gate, n) for gate in gates]
    for a, gate in enumerate(gates):
        nominations = [(singles[a], (1, cost(gate), (a,)))]
        nominations.extend((apply(singles[a], other, n),
                            (2, cost(gate) + cost(other), (a, b)))
                           for b, other in enumerate(gates))
        for matrix, price in nominations:
            if matrix not in states or price < states[matrix]:
                states[matrix] = price
    return gates, states


def solve(target, n, frontier):
    gates, states = frontier
    best = states.get(target)
    probes = 1
    for b, last in enumerate(gates):
        intermediate = apply(target, inverse(last), n)
        suffixes = [(intermediate, (b,), cost(last))]
        suffixes.extend((apply(intermediate, inverse(previous), n), (a, b),
                         cost(previous) + cost(last))
                        for a, previous in enumerate(gates))
        for residual, suffix, suffix_cost in suffixes:
            probes += 1
            if residual in states:
                p = states[residual]
                offer = (p[0] + len(suffix), p[1] + suffix_cost, p[2] + suffix)
                if best is None or offer < best:
                    best = offer
    require(probes == 1 + len(gates) + len(gates) ** 2, "incomplete suffix search")
    return best, probes


def windows(word):
    out = []
    for width in (4, 5, 6):
        for start in range(len(word) - width + 1):
            block = word[start:start + width]
            wires = sorted({r for op in block for r in (
                op[1:3] if op[0] == "add" else op[1:2])})
            if len(wires) <= 4:
                out.append((start, width, wires, [parse(op, wires) for op in block]))
    return out


def source_lowering():
    spec = importlib.util.spec_from_file_location("pinned_pr696", ROOT / LOWERING)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def primitive_word(word, lower):
    out = []
    for kind, t, s, sign, exponent in word:
        q = sign * Fraction(2) ** exponent
        fields = ["add", ("D", t), ("D", s), q.numerator, q.denominator] if kind == "add" else [
            "scale", ("D", t), q.numerator, q.denominator]
        out.extend(lower(fields))
    return out


def primitive_matrix(ops, n):
    labels = [("D", i) for i in range(n)] + [("W", 0)]
    rows = {label: [Fraction(i == j) for j in range(n + 1)]
            for i, label in enumerate(labels)}
    for op in ops:
        kind, t = op[:2]
        if kind == "clear":
            rows[t] = [Fraction(0)] * (n + 1)
        elif kind == "copy":
            rows[t] = rows[op[2]].copy()
        elif kind in ("add", "subtract"):
            sign = 1 if kind == "add" else -1
            rows[t] = [x + sign * y for x, y in zip(rows[t], rows[op[2]])]
        else:
            q = {"double": Fraction(2), "halve": Fraction(1, 2), "negate": Fraction(-1)}[kind]
            rows[t] = [q * x for x in rows[t]]
    return [rows[label] for label in labels]


def check_primitive_boundary(word, n, lower, supplied=None):
    ops = primitive_word(word, lower) if supplied is None else supplied
    require(len(ops) == sum(map(cost, word)), "primitive charge mismatch")
    actual = primitive_matrix(ops, n)
    state = execute(word, n)
    expected = [[Fraction(state[i * n + j], 1 << state[-1]) for j in range(n)] + [Fraction(0)]
                for i in range(n)]
    # All windows and nominated equal-map witnesses contain an ADD.
    require(any(g[0] == "add" for g in word), "expected clearing ADD")
    expected.append([Fraction(0)] * (n + 1))
    require(actual == expected, "arbitrary-input/private-work boundary")


def controls(lower):
    passed = []
    n = 3
    frontier = short_frontier(n)
    a = ("add", 1, 2, 1, 0)
    b = ("add", 0, 1, 1, 0)
    c = ("add", 0, 2, -1, 0)
    reducible = [a, b, c]
    answer, _ = solve(execute(reducible, n), n, frontier)
    require(answer[:2] == (2, 4), "planted Steinberg contraction not found")
    passed.append("planted_three_to_two_contraction")
    answer, _ = solve(identity(n), n, frontier)
    require(answer[:2] == (0, 0), "empty word omitted")
    passed.append("empty_identity_word")
    answer, _ = solve(execute([a, b], n), n, frontier)
    require(answer[:2] == (2, 4), "noncommuting two-gate target lost")
    require(execute([a, b], n) != execute([b, a], n), "bad noncommuting control")
    passed.append("noncommuting_order")
    for name, word, mutate in [
        ("nonunit_initial_copy", [("add", 0, 1, 1, -1)], lambda x: x[1:]),
        ("nonunit_final_clear", [("add", 0, 1, 1, -1)], lambda x: x[:-1]),
        ("unit_dirty_work_clear", [("add", 0, 1, 1, 0)], lambda x: x[:-1]),
        ("wrong_sign", [("add", 0, 1, 1, 0)],
         lambda x: [("subtract", x[0][1], x[0][2])] + x[1:]),
        ("wrong_scale_direction", [("scale", 0, -1, 1, -1), a],
         lambda x: [("double", x[0][1])] + x[1:]),
    ]:
        original_ops = primitive_word(word, lower)
        mutated_ops = mutate(original_ops)
        require(primitive_matrix(mutated_ops, n) != primitive_matrix(original_ops, n),
                "mutation did not change the complete dirty-input map: " + name)
        try:
            check_primitive_boundary(word, n, lower, mutated_ops)
        except ValueError:
            passed.append(name)
        else:
            raise ValueError("accepted mathematical mutation: " + name)
    for name, op in [
        ("nondyadic_coefficient", ["add", 0, 1, 1, 3, FRAME]),
        ("source_alias", ["add", 0, 0, 1, 1, FRAME]),
        ("boolean_index", ["add", False, 1, 1, 1, FRAME]),
        ("foreign_frame", ["add", 0, 1, 1, 1, [1]]),
    ]:
        try:
            parse(op, list(range(n)))
        except ValueError:
            passed.append(name)
        else:
            raise ValueError("accepted admission mutation: " + name)
    return passed


def generate():
    check_sources()
    source = read(ROOT / SOURCE)["replacement"]
    require(len(source) == 32, "source gate count")
    full = [parse(op, list(range(8))) for op in source]
    matrix = execute(full, 8)
    reference = read(ROOT / REFERENCE)["matrix"]
    exact = [[str(Fraction(matrix[i * 8 + j], 1 << matrix[-1])) for j in range(8)] for i in range(8)]
    require(exact == reference, "full eight-wire PR681 boundary")
    require(sum(map(cost, full)) == 73, "baseline price")
    lower = source_lowering()
    for n in (2, 3, 4):
        for gate in alphabet(n):
            require(len(primitive_word([gate], lower)) == cost(gate), "PR696 price mismatch")
    items = windows(source)
    require(len(items) == 32, "window inventory")
    items = items[SEED:] + items[:SEED]
    frontiers = {n: short_frontier(n) for n in (2, 3, 4)}
    records = []
    for start, width, wires, block in items:
        row = {"start": start, "stop": start + width, "wires": wires,
               "original_macros": width, "original_primitives": sum(map(cost, block)),
               "orientations": {}}
        for label, word in variants(block).items():
            n = len(wires)
            target = execute(word, n)
            answer, probes = solve(target, n, frontiers[n])
            check_primitive_boundary(word, n, lower)
            value = {"suffix_probes": probes, "target_sha256": digest(target), "best": None}
            if answer is not None:
                candidate = [frontiers[n][0][i] for i in answer[2]]
                require(execute(candidate, n) == target, "nominated boundary mismatch")
                check_primitive_boundary(candidate, n, lower)
                value["best"] = {"macros": answer[0], "primitives": answer[1],
                                 "gate_indices": list(answer[2])}
            row["orientations"][label] = value
        optimum = row["orientations"]["forward"]["best"]
        row["macro_lower_bound"] = 5 if optimum is None else optimum["macros"]
        row["macro_upper_bound"] = width if optimum is None else min(width, optimum["macros"])
        row["primitive_minimum_at_minimum_length"] = None if optimum is None else optimum["primitives"]
        records.append(row)
    records.sort(key=lambda r: (r["original_macros"], r["start"]))
    return {
        "format": "factory-window-synthesis-seed23-v1", "seed": SEED,
        "source_word_sha256": digest(source), "full_eight_wire_map_sha256": digest(exact),
        "baseline_macros": len(source), "baseline_primitives": sum(map(cost, full)),
        "fixed_invoice": {"compiler": 64 * 74 ** 3,
                          "marginal_emitted_macro_charge": 16 * 64 * 74 ** 3,
                          "scope": "retained local formula with unchanged outside costs; no global invoice replay"},
        "domain": {"lengths": [4, 5, 6], "max_wires": 4, "replacement_max_length": 4,
                   "add_coefficients": ["-2", "-1", "-1/2", "1/2", "1", "2"],
                   "scale_coefficients": ["-2", "-1", "-1/2", "1/2", "2"]},
        "frontiers": {str(n): {"alphabet_size": len(g), "prefix_words": 1 + len(g) + len(g) ** 2,
                                "distinct_prefix_matrices": len(d),
                                "frontier_sha256": digest(sorted((list(m), list(p[:2])) for m, p in d.items()))}
                      for n, (g, d) in frontiers.items()},
        "window_counts": dict(sorted(Counter(str(r["original_macros"]) for r in records).items())),
        "orientation_cases": len(records) * 4, "windows": records,
        "controls": controls(lower), "new_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new development receipt; refuses overwrites")
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), "output already exists")
    result = generate()
    if args.write:
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
        print("WROTE_FACTORY_WINDOW_RECEIPT", args.write)
    else:
        require(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "receipt mismatch")
        print("PASS_FACTORY_WINDOW_SYNTHESIS windows=32 orientations=128 macro_minima=27 four_gate_optima=18 "
              "five_gate_exclusions=9 six_gate_exclusions=5 controls=12 no_new_kappa")


if __name__ == "__main__":
    main()

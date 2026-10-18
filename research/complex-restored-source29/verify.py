"""Source-bound CK coefficient census and complete scalar-projection replay.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
Predecessor algorithms are imported only after checking exact source pins.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import search

PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck"
WORK = ("W", 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def read(path):
    return json.loads(payload(path))


def pin_check():
    pins = read(HERE / "SOURCES.json")
    for name, entry in pins["files"].items():
        path = ROOT / name
        need(entry["representation"] == ("gzip-payload" if path.suffix == ".gz" else "exact-bytes"),
             "incorrect hash representation")
        need(hashlib.sha256(payload(path)).hexdigest() == entry["sha256"], "source pin: " + name)
    return pins


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sources():
    pins = pin_check()
    reference = module("source29_reference", ROOT / "research/complex-dyadic-lowering/lower.py")
    horner = module("source29_horner", ROOT / "research/dyadic-horner-direction/lower.py")
    grid = module("source29_grid", ROOT / "research/jp8-grid-bounded-synthesis/synth.py")
    accumulation = module("source29_accumulation", HERE / "vendor/pr999_lower.py")
    programs = read(ROOT / PROVIDER / "LOCAL-PROGRAMS.json.gz")
    spec = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")
    need(hashlib.sha256(payload(ROOT / PROVIDER / "LOCAL-PROGRAMS.json.gz")).hexdigest() ==
         spec["providers"]["ck"]["artifact_semantic_sha256"]["LOCAL-PROGRAMS.json.gz"],
         "program does not match the historical provider SPEC")
    return pins, reference, horner, grid, accumulation, programs, spec


def coefficient_inventory(programs):
    inventories = {}
    for orientation in ("forward", "backward"):
        counts = Counter()
        for event in programs[orientation]:
            if event[0] == "scalar" and event[1][0] == "add":
                counts[abs(Q(event[1][3], event[1][4]))] += 1
        inventories[orientation] = counts
    need(set(inventories["forward"]) == set(inventories["backward"]), "coefficient domains differ")
    return inventories


def comparator_words(q, reference, horner, grid, accumulation):
    op = ["add", ["T", 0], ["S", 0], q.numerator, q.denominator]
    choices = {"pr696": reference.lower(op)}
    choices.update({"pr837_" + name: word for name, word in horner.candidates(op).items()})
    # Reuse the published PR882 graph method on eligible CK coefficients.
    # This is an explicit transfer of its local algebraic method, not a claim
    # that PR882's original 49-coefficient JP8 certificate covers CK.
    if q != 1 and q.numerator <= 127 and q.denominator <= 16:
        entry = grid.solve(q.numerator, q.denominator)
        w = [("copy", WORK, ("S", 0))]
        for tag in entry["operations"]:
            w.append((tag, WORK, ("S", 0)) if tag in ("add", "subtract") else (tag, WORK))
        w += [("add" if entry["end_sign"] > 0 else "subtract", ("T", 0), WORK), ("clear", WORK)]
        choices["pr882_method_on_ck"] = w
    _, abstract = accumulation.addition(q)
    names = {"T": ("T", 0), "S": ("S", 0), "W": WORK}
    choices["pr999"] = [(p[0], *(names[r] for r in p[1:])) for p in abstract]
    return choices


def step(rows, instruction):
    """Sparse Fraction interpreter, including every arbitrary input column."""
    tag, target = instruction[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = dict(rows[instruction[2]])
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {column: factor * value for column, value in rows[target].items()}
    elif tag in ("add", "subtract"):
        for column, value in list(rows[instruction[2]].items()):
            value = rows[target].get(column, 0) + (value if tag == "add" else -value)
            if value:
                rows[target][column] = value
            else:
                rows[target].pop(column, None)
    else:
        raise ValueError("unknown primitive")


def local_check(q, word):
    t, s = ("T", 0), ("S", 0)
    rows = {t: {0: Q(1)}, s: {1: Q(1)}, WORK: {2: Q(1)}}
    for primitive in word:
        step(rows, primitive)
    need(rows == {t: {0: Q(1), 1: q}, s: {1: Q(1)}, WORK: {}},
         "local shear or source restoration or private clearing")


def two_register_word(gates, negative=False):
    out = []
    for name in gates:
        index = search.GATES.index(name)
        # Conjugation by diag(1,-1) relabels addition signs without gates.
        if negative and index < 4:
            index ^= 1
        if index < 4:
            target, source = (("T", 0), ("S", 0)) if index < 2 else (("S", 0), ("T", 0))
            out.append(("add" if index % 2 == 0 else "subtract", target, source))
        else:
            tag, target = (("double", "T"), ("halve", "T"), ("double", "S"),
                           ("halve", "S"), ("negate", "T"), ("negate", "S"))[index - 4]
            out.append((tag, (target, 0)))
    return out + [("clear", WORK)]


def shortcut(op, reference):
    if op[0] == "add":
        q = Q(op[3], op[4])
        if abs(q) in (2, 3):
            # Validate all inherited alias/coefficient restrictions as well.
            reference.lower(op)
            return [("add" if q > 0 else "subtract", tuple(op[1]), tuple(op[2]))] * abs(q.numerator) + [("clear", WORK)]
    return reference.lower(op)


def scalar_replay(events, reference, use_shortcut, orientation):
    registers = set()
    paid = Counter()
    for event in events:
        if event[0] == "scalar":
            op = event[1]
            registers.add(tuple(op[1]))
            if op[0] in ("copy", "add"):
                registers.add(tuple(op[2]))
        elif event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
        else:
            need(event[0] in ("phase", "adapter", "residual_adapter"), "unknown non-scalar event")
    registers.add(WORK)
    for i in range(716):
        registers.add(("L", i))
    rows = {r: {r: Q(1)} for r in registers}
    magnitude = {r: Q(1) for r in registers}
    peak = Q(1)
    positive_peak = Q(1)
    denominator_bits = 0
    word_hash = hashlib.sha256()
    operations = Counter()
    macros = changed = 0
    for event in events:
        if event[0] != "scalar":
            continue
        op, frame = event[1:]
        macros += 1
        old = reference.lower(op)
        word = shortcut(op, reference) if use_shortcut else old
        changed += word != old
        for instruction in word:
            operations[instruction[0]] += 1
            word_hash.update((canonical([instruction, frame]) + "\n").encode())
            step(rows, instruction)
            target = instruction[1]
            tag = instruction[0]
            if tag == "clear":
                magnitude[target] = Q(0)
            elif tag == "copy":
                magnitude[target] = magnitude[instruction[2]]
            elif tag in ("double", "halve"):
                magnitude[target] *= Q(2) if tag == "double" else Q(1, 2)
            elif tag in ("add", "subtract"):
                magnitude[target] += magnitude[instruction[2]]
            positive_peak = max(positive_peak, magnitude[target])
            row = rows[target]
            peak = max(peak, sum(map(abs, row.values()), Q(0)))
            denominator_bits = max(denominator_bits, max((x.denominator.bit_length() - 1 for x in row.values()), default=0))
        if op[0] == "add":
            need(not rows[WORK], "dirty coefficient work escaped a macro")
    for i in range(716):
        expected = {("L", i): Q(1)}
        if orientation == "forward" and 112 <= i < 224:
            expected[("L", i - 112)] = Q(1)
        elif orientation == "backward" and i < 112:
            expected[("L", i + 112)] = Q(-1)
        need(rows[("L", i)] == expected, "full CK endpoint at native row " + str(i))
    row_data = [[list(r), [[list(c), str(v)] for c, v in sorted(rows[r].items())]] for r in sorted(rows)]
    return {
        "input_columns": len(registers), "native_columns": 716,
        "scalar_macros": macros, "replaced_macros": changed,
        "real_component_primitives": 2 * sum(operations.values()),
        "one_component_operations": dict(sorted(operations.items())),
        "exact_row_l1_peak": str(peak), "exact_denominator_bits": denominator_bits,
        "cancellation_free_peak": str(positive_peak),
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "primitive_stream_sha256": word_hash.hexdigest(),
        "endpoint_sha256": hashlib.sha256(canonical(row_data).encode()).hexdigest(),
        "endpoint_private_cells_cleared": all(not row for reg, row in rows.items() if reg[0] != "L"),
        "endpoint_native_helpers_restored": all(rows[("L", i)] == {("L", i): Q(1)} for i in range(224, 716)),
    }


def controls(reference):
    t, s = ("T", 0), ("S", 0)
    valid = [("add", t, s)] * 3 + [("clear", WORK)]
    cases = {
        "missing_source_read": valid[1:],
        "wrong_sign": [("subtract", t, s)] + valid[1:],
        "dirty_work_not_cleared": valid[:-1],
        "source_not_restored": [("double", s)] + valid,
        "target_dirt_lost": [("clear", t)] + valid,
        "work_dirt_used_as_source": [("add", t, WORK)] + valid,
    }
    rejected = []
    for name, word in cases.items():
        try:
            local_check(Q(3), word)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted control: " + name)
    for label, op in {
        "source_target_alias": ["add", list(t), list(t), 2, 1],
        "source_work_alias": ["add", list(t), list(WORK), 3, 1],
        "nondyadic": ["add", list(t), list(s), 1, 3],
    }.items():
        try:
            shortcut(op, reference)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("accepted invalid macro: " + label)
    # Neither a restricted alphabet nor a smaller ball is accepted as coverage.
    try:
        search.ball(order=search.ORDER[:-1])
    except ValueError:
        rejected.append("missing_gate_from_alphabet")
    else:
        raise ValueError("accepted incomplete alphabet")
    return rejected


def build():
    pins, reference, horner, grid, accumulation, programs, spec = sources()
    inventory = coefficient_inventory(programs)
    coefficients = sorted(inventory["forward"])
    need(len(coefficients) == 103, "CK coefficient inventory drift")
    words, layers = search.ball()
    result = search.metric(coefficients, words)
    strict = []
    for entry, q in zip(result, coefficients):
        choices = comparator_words(q, reference, horner, grid, accumulation)
        for word in choices.values():
            local_check(q, word)
        prices = {name: len(word) for name, word in choices.items()}
        best = min(prices.values())
        # Any strict improvement pays a clear, so at most best-2 group gates.
        need(best - 2 <= 2 * search.RADIUS, "search cutoff cannot decide improvement")
        minimum = entry["two_register_minimum"]
        improved = minimum is not None and minimum + 1 < best
        if minimum is not None:
            local_check(q, two_register_word(entry["word"]))
            local_check(-q, two_register_word(entry["word"], negative=True))
        if improved:
            strict.append(str(q))
        entry.update({
            "occurrences": {orientation: inventory[orientation][q] for orientation in inventory},
            "comparator_costs": prices, "best_comparator_cost": best,
            "minimum_complete_cost": minimum + 1 if minimum is not None else None,
            "complete_cost_lower_bound": entry["two_register_lower_bound"] + 1,
            "strict_improvement": improved,
        })
    need(strict == ["2", "3"], "unexpected improvement set; inspect mathematical result")
    replays = {}
    for orientation in ("forward", "backward"):
        old = scalar_replay(programs[orientation], reference, False, orientation)
        new = scalar_replay(programs[orientation], reference, True, orientation)
        need(old["endpoint_sha256"] == new["endpoint_sha256"], "full arbitrary-input endpoint changed")
        need(old["paid_profile"] == new["paid_profile"] ==
             {str(k): v for k, v in spec["providers"]["ck"]["expected_profile"].items()}, "paid profile changed")
        need(old["exact_denominator_bits"] == new["exact_denominator_bits"], "fractional grid changed")
        need(Q(new["exact_row_l1_peak"]) <= Q(old["exact_row_l1_peak"]), "prefix grew")
        need(Q(new["cancellation_free_peak"]) <= Q(old["cancellation_free_peak"]), "positive envelope grew")
        need(new["endpoint_private_cells_cleared"] and new["endpoint_native_helpers_restored"], "endpoint lifecycle failure")
        replays[orientation] = {"pr696": old, "direct_shortcuts": new,
                                "saved_real_primitives": old["real_component_primitives"] - new["real_component_primitives"]}
    return {
        "schema": "restored-two-register-ck/1", "seed": search.SEED,
        "base_commit": pins["base_commit"], "provider": "historical PR626 CK",
        "radius": search.RADIUS, "covered_word_length": 2 * search.RADIUS,
        "alphabet": list(search.GATES), "layer_sizes": layers,
        "ball_states": len(words), "distance_sha256": search.distance_digest(words),
        "coefficient_count": len(coefficients),
        "exact_minima": sum(row["two_register_minimum"] is not None for row in result),
        "strict_improvement_coefficients": strict,
        "coefficients": result, "scalar_replays": replays,
        "negative_controls": controls(reference),
        "kappa_claim": "none; selected frontier unchanged",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write a fresh certificate; refuse overwrite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "refusing to overwrite an existing certificate")
    receipt = build()
    if args.write:
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2) + "\n")
    else:
        need(canonical(receipt) == canonical(read(HERE / "EXPECTED.json")), "complete certificate mismatch")
    if args.json:
        print(json.dumps(receipt, indent=2))
    print("PASS_RESTORED_SOURCE_CK coefficients=103 exact_minima=77 improvements=2,3 "
          "saved_real=3124,3124 no_new_kappa")


if __name__ == "__main__":
    main()

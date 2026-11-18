#!/usr/bin/env python3
"""Replay the parent and split's complete scheduled physical bank maps over two primes."""

from collections import defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import runpy


HERE = Path(__file__).resolve().parent
SOURCE_HEAD = "1b4a4d6f9370b8c93b3f769a6229a9111ef3940e"
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CANDIDATE = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
PINS = {
    "data/PARENT-GRAPH.json.gz": "8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970",
    "data/CANDIDATE-GRAPH.json.gz": "789c51223158f816b4046321e28449e1db540d20b75ce57e0699a20706bc3510",
    "data/CALLER-LAYOUT.json": "622c6f458eba2dab0fdfd6050303cbc16ad684ab8b834c7df568264e4cf01db6",
    "EDIT.json": "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf",
    "native_support/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "native_support/PR7682-PHASE-RESULT.json": "50b05bdc2805d709761ce5c4b42e7ec352141366f5cc6031df9f8779e8872735",
    "native_support/PR7682-BANK-RECIPES.json.gz": "06dbe8d913627dbfef6cfe6599fd8eaa7fd82daddf72253b1f9bc5cb5a4eb0e9",
    "dense_support/field_interpreter.py": "e76bc78b132607890b2d9ea234d3a52e608e0e919bdc48308cc0727a2a07c73e",
}
SAMPLES = {1000000009: (4171, 8663), 998244353: (5147, 9631)}
WIDTH = 512
OLD_ROLES = 1501
CUT_ROLE = 281
FRESH = 1501
INJECTION_SLOT = 102698
PREFIX_SLOT = 95743
NAMES = ("injection_coefficient_sign", "prefix_return_quarter_phase")


def need(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pinned_inputs():
    files = {name: (HERE / name).read_bytes() for name in PINS}
    for name, raw in files.items():
        need(sha256(raw).hexdigest() == PINS[name], f"frozen input {name}")
    return files


def graph(raw, pin, public):
    blob = gzip.decompress(raw)
    need(sha256(blob).hexdigest() == pin, "decoded graph custody")
    word = json.loads(blob)
    need(canonical(word) == blob, "canonical banked word")
    initial, final, first = word["initial"], word["final"], word["first_output"]
    moves = {key: (a, b) for key, a, b in word["moves"]}
    forms = dict(word["forms"])
    schedule = word["schedule"]
    need(len(initial) == len(final) == public and first == 150522, "public owner inventory")
    need(len(word["moves"]) == len(moves) == 6142, "full paid bank inventory")
    need(len(word["forms"]) == len(forms) == len(schedule) == 6142 + public
         and set(schedule) == forms.keys() == moves.keys() | set(range(first, first + public)),
         "complete literal scheduled banks")
    available_charts = {~r: a for r, a in enumerate(initial)}
    for key in schedule:
        row = forms[key]
        a, b = moves[key] if key in moves else (final[key - first], None)
        need(len({donor for donor, _ in row}) == len(row)
             and all(available_charts.get(donor) == a for donor, _ in row),
             f"ordered cocharted donors for scheduled bank {key}")
        if b is not None:
            available_charts[key] = b
    return word, moves, forms


def paid_recipes(files, moves, frames):
    phase = json.loads(files["native_support/PR7682-PHASE-RESULT.json"])
    name = "native_support/PR7682-BANK-RECIPES.json.gz"
    need(phase["graph_pins"]["candidate"] == PARENT and phase["caller_sha256"] == CALLER
         and phase["status"] == "PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS"
         and phase["artifact_sha256"]["BANK-RECIPES.json.gz"] == PINS[name],
         "exact parent compiled recipe archive")
    keys = defaultdict(list)
    for slot, pair in sorted(moves.items()):
        keys[pair].append(slot)
    recipes = {}
    for row in json.loads(gzip.decompress(files[name])):
        pair = tuple(row["pair"])
        if pair in keys:
            a, b = pair
            recipe = row["recipe"]
            need(pair not in recipes and row["in_forward_union"]
                 and row["candidate_moves"] == keys[pair]
                 and row["compared_signed_pauli_and_absolute_phase"]
                 and recipe["rank"] == abs(len(frames[b]) - len(frames[a])) > 0,
                 f"bound archived physical body for paid pair {pair}")
            recipes[pair] = recipe
    need(recipes.keys() == keys.keys() and len(recipes) == 2977,
         "physical bodies for all 6,142 paid banks")
    return recipes


def direct_outputs(word, layout, inputs, raw, add, factor, scalar):
    """Use the signed public block formulas and direct ordered chart maps."""
    hosted = layout["hosted"]
    live, x2, y2, dport = layout["live"], hosted["X2"], hosted["Y2"], set(hosted["Dports"])
    need(len(live) == 104 and len(x2) == len(y2) == len(dport) == 96,
         "actual 104/96 paired main blocks")
    rows = [None] * OLD_ROLES

    def mapped(target, donor):
        return raw(word["initial"][donor], word["final"][target], inputs[donor])

    def block(x, y, alpha, beta):
        need(rows[x] is None and rows[y] is None, "distinct main roles")
        rows[x] = add(mapped(x, x), scalar(alpha), mapped(x, y))
        rows[y] = add(factor(scalar(beta), mapped(y, x)), scalar(1 + alpha * beta), mapped(y, y))

    alpha, beta, alpha2, beta2 = (Fraction(hosted[key]) for key in ("alpha", "beta", "alpha2", "beta2"))
    for j, x in enumerate(live):
        a, b = (0, 1) if j in dport else (alpha, beta)
        block(x, x + 112, a, b)
    for x, y in zip(x2, y2, strict=True):
        block(x, y, alpha2, beta2)
    mains = {r for r, row in enumerate(rows) if row is not None}
    need(len(mains) == 400 and CUT_ROLE not in mains, "complete main and helper separation")
    for role in range(OLD_ROLES):
        if role not in mains:
            rows[role] = mapped(role, role)
    return rows, mains


def descendants(word, forms, slot):
    reached = {slot}
    for key in word["schedule"]:
        if any(donor in reached for donor, _ in forms[key]):
            reached.add(key)
    first = word["first_output"]
    return {key - first for key in reached if key >= first}


def test_field(specification, parent, candidate, layout, recipes, prime, seeds):
    source, moves, _ = parent
    target, _, target_forms = candidate
    frames = source["frames"]
    interpreter, checker = specification
    field = interpreter["GateInterpreter"](prime, need)
    digest = interpreter["digest"]

    @cache
    def chart(a):
        return checker["frame"](frames[a], 9)

    @cache
    def raw_gates(a, b):
        return () if a == b else checker["adjoint"](chart(a)) + chart(b)

    @cache
    def lowered(a, b):
        return checker["recipe"](recipes[a, b])

    @cache
    def prepared(circuit):
        return tuple(field.gate(gate) for gate in circuit)

    def raw(a, b, value):
        return field.apply(prepared(raw_gates(a, b)), value)

    scalar = cache(field.coefficient)

    def add(dst, q, src):
        if q == 1:
            return [(a + b) % prime for a, b in zip(dst, src, strict=True)]
        return [(a + q*b) % prime for a, b in zip(dst, src, strict=True)]

    def factor(q, src):
        return [q*a % prime for a in src]

    exact_columns = []
    for a, b in ((3, 595), (595, 127)):
        compiled, ideal = lowered(a, b), raw_gates(a, b)
        for direction in ("forward", "adjoint"):
            for col in (0, 17, 511):
                unit = [0] * WIDTH
                unit[col] = 1
                actual = field.apply(prepared(compiled), unit)
                expected = field.column_residue(checker["state"](ideal, col))
                need(actual == expected, "finite physical orientation against exact Gaussian column")
                exact_columns.append([a, b, direction, col])
            compiled, ideal = checker["adjoint"](compiled), checker["adjoint"](ideal)

    def replay(bundle, inputs, fault=None):
        word, word_moves, forms = bundle
        first = word["first_output"]
        borrowed = digest(inputs)
        bars = {~key: value for key, value in enumerate(inputs)}
        sources, returns, terminals = {}, {}, {}
        changes = 0
        for key in word["schedule"]:
            value = [0] * WIDTH
            for donor, coefficient in forms[key]:
                q = scalar(coefficient)
                if fault == NAMES[0] and key == INJECTION_SLOT and donor == ~FRESH:
                    q = -q
                    changes += 1
                value = add(value, q, bars[donor])
            sources[key] = value
            if key in word_moves:
                returned = field.apply(prepared(lowered(*word_moves[key])), value)
                if fault == NAMES[1] and key == PREFIX_SLOT:
                    returned = factor(field.i, returned)
                    changes += 1
                bars[key] = returns[key] = returned
            else:
                terminals[key - first] = value
        need(changes == int(fault is not None), "one actual fault occurrence per mutation")
        need(len(returns) == 6142 and terminals.keys() == set(range(len(inputs))),
             "full actual paid returns and terminal arrays")
        held = [*inputs, *sources.values(), *returns.values()]
        need(len({id(row) for row in held}) == len(held) == 12284 + 2*len(inputs),
             "distinct actually held entry, source, returned and terminal arrays")
        need(digest(inputs) == borrowed, "borrowed public arrays remain intact")
        rows = [terminals[role] for role in range(len(inputs))]
        return rows, {"scheduled_banks": len(sources), "paid_slots": len(returns),
                      "local_scalar_terms": sum(map(len, forms.values())),
                      "terminal_rows": len(rows), "held_arrays": len(held),
                      "terminal_sha256": digest(rows), "returned_sha256": digest(returns[k] for k in sorted(returns))}, {
                          k: returns[k] for k in (PREFIX_SLOT, INJECTION_SLOT)
                      }

    cases = []
    for seed in seeds:
        random = Random(seed)
        entries = [[random.randrange(prime) for _ in range(WIDTH)] for _ in range(OLD_ROLES + 1)]
        need(any(entries[CUT_ROLE]) and any(entries[FRESH]) and entries[CUT_ROLE] != entries[FRESH],
             "nontrivial separate cut and fresh owner input banks")
        expected_old, mains = direct_outputs(source, layout, entries, raw, add, factor, scalar)
        expected = expected_old.copy()
        expected[CUT_ROLE] = raw(3, 595, entries[CUT_ROLE])
        expected.append(raw(595, 127, entries[FRESH]))
        old, old_report, _ = replay(parent, entries[:OLD_ROLES])
        actual, report, cut_slots = replay(candidate, entries)
        bad_old = [r for r, row in enumerate(old) if row != expected_old[r]]
        bad_new = [r for r, row in enumerate(actual) if row != expected[r]]
        need(not bad_old and not bad_new, f"whole-word physical oracle mismatch: source {bad_old[:8]}, candidate {bad_new[:8]}")
        changed = [r for r, row in enumerate(old) if row != actual[r]]
        need(changed == [CUT_ROLE] and raw(127, 595, old[CUT_ROLE]) == actual[CUT_ROLE],
             "shared digits preserve every old endpoint except the exact typed chart-595 return")

        controls = {}
        if prime == next(iter(SAMPLES)) and seed == seeds[0]:
            for name, slot in zip(NAMES, (INJECTION_SLOT, PREFIX_SLOT), strict=True):
                faulty, fault_report, fault_slots = replay(candidate, entries, name)
                mismatches = {r for r, row in enumerate(faulty) if row != expected[r]}
                reachable = descendants(target, target_forms, slot)
                need(mismatches and mismatches <= reachable, "actual physical fault is detected inside its descendants")
                if name == NAMES[0]:
                    q = scalar(dict(target_forms[slot])[~FRESH])
                    delta = factor(-2*q, raw(*moves[slot], entries[FRESH]))
                    need(FRESH in mismatches and CUT_ROLE not in mismatches,
                         "unsigned earlier return survives while the cold injected owner fails")
                else:
                    delta = factor(field.i - 1, cut_slots[slot])
                    need(CUT_ROLE in mismatches, "prefix MOVE phase fault reaches the chart-595 return")
                need(fault_slots[slot] == add(cut_slots[slot], 1, delta), "isolated actual paid return fault delta")
                controls[name] = {"slot": slot, "pair": list(moves[slot]),
                                  "changed_roles": sorted(mismatches), "reachable_roles": len(reachable),
                                  "changed_main_roles": len(mismatches & mains),
                                  "faulty_terminal_sha256": fault_report["terminal_sha256"],
                                  "one_actual_mutation_verified": True}
        cases.append({"seed": seed, "input_sha256": digest(entries),
                      "shared_external_inputs_sha256": digest(entries[:OLD_ROLES]),
                      "independent_parent_oracle_sha256": digest(expected_old),
                      "independent_candidate_oracle_sha256": digest(expected),
                      "changed_shared_roles_before_chart_typing": changed,
                      "all_shared_roles_match_after_chart_typing": True,
                      "changed_role_chart595_sha256": digest([actual[CUT_ROLE]]),
                      "fresh_input_sha256": digest([entries[FRESH]]),
                      "fresh_output_sha256": digest([actual[FRESH]]),
                      "parent": old_report, "candidate": report, "actual_negative_controls": controls})
    need(cases[0]["fresh_input_sha256"] != cases[1]["fresh_input_sha256"]
         and cases[0]["fresh_output_sha256"] != cases[1]["fresh_output_sha256"],
         "fresh coordinate remains variable across independent held arrays")
    return {"prime": prime, "imaginary_root": field.i, "literal_modular_column_links": exact_columns, "cases": cases}


def main():
    files = pinned_inputs()
    parent = graph(files["data/PARENT-GRAPH.json.gz"], PARENT, OLD_ROLES)
    candidate = graph(files["data/CANDIDATE-GRAPH.json.gz"], CANDIDATE, OLD_ROLES + 1)
    source, moves, _ = parent
    target, target_moves, target_forms = candidate
    edit = json.loads(files["EDIT.json"])
    layout = json.loads(files["data/CALLER-LAYOUT.json"])
    need(target["metadata"]["source_bank_graph_sha256"] == edit["source_graph_sha256"] == PARENT
         and target["metadata"]["source_pr_head"] == edit["source_head"] == SOURCE_HEAD
         and source["metadata"]["caller_sha256"] == target["metadata"]["caller_sha256"] == CALLER
         and source["metadata"]["source_word_sha256"] == layout["source_word_sha256"],
         "exact common source lineage and caller role layout")
    new_final = source["final"].copy()
    new_final[CUT_ROLE] = 595
    need(target["frames"] == source["frames"] and target_moves == moves
         and target["initial"] == source["initial"] + [595] and target["final"] == new_final + [127]
         and (source["initial"][CUT_ROLE], source["final"][CUT_ROLE]) == (3, 127),
         "exact typed endpoints and unchanged 6,142 physical MOVE bodies")
    need(moves[INJECTION_SLOT] == (595, 127) and moves[PREFIX_SLOT] == (3, 595)
         and dict(target_forms[INJECTION_SLOT])[~FRESH] == dict(edit["injection"])[INJECTION_SLOT] == "8/21"
         and dict(edit["prefix"])[PREFIX_SLOT] == "1", "actual single-site injection and phase controls")
    recipes = paid_recipes(files, moves, source["frames"])
    specification = tuple(runpy.run_path(str(HERE / name)) for name in (
        "dense_support/field_interpreter.py", "native_support/native_verify.py"
    ))
    fields = [test_field(specification, parent, candidate, layout, recipes, prime, seeds)
              for prime, seeds in SAMPLES.items()]
    pinned_inputs()
    print(canonical({
        "status": "PASS_P104_CHART595_DENSE_HELD_ARRAYS",
        "scope": "Full compiled forward paid-bank replay and independent direct ordered public boundaries on held finite fields.",
        "source_pr": 7682, "source_head": SOURCE_HEAD, "caller_sha256": CALLER,
        "graph_pins": {"parent": PARENT, "candidate": CANDIDATE}, "field_width": WIDTH,
        "packed_inputs_sha256": PINS,
        "main_outputs": 400, "candidate_helper_outputs": 1102,
        "candidate_split_boundaries": {str(CUT_ROLE): [3, 595], str(FRESH): [595, 127]},
        "paid_ordered_bodies": len(recipes), "paid_slots_per_word": len(moves), "fields": fields,
    }).decode(), flush=True)


if __name__ == "__main__":
    main()

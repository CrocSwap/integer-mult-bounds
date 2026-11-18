#!/usr/bin/env python3
"""Replay both #7700 banked graphs and inherited CLEAR observations in two prime fields."""

from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
HEAD = "7d84799a447867d36137d12ef7ca5646154d763c"
WORD = "ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
PARENT = "72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f"
CANDIDATE = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
RECIPES = "native_support/RECIPES.json.gz"
RECIPES_DECODED = "be33fd04af74312d297f01e1d8a374a72034e7e6f902bbd0c671df2597d1c828"
PINS = {
    "data/WORD.json.gz": "50c1facfc5626c060560e2f354b71bd92d0bb1c1e853b2aad72abcbaaa5328a5",
    "data/CERTS.json": "39ef28b708cd8bf1166b111d656809407b370dd11cd81a8e43820779f995aca3",
    "data/CALLER.json.gz": "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a",
    "data/PARENT-GRAPH.json.gz": "c86288cddb4b80af3c8128c9a0d2f7a1e82bae64c5152a0d96a19d166afaab1d",
    "data/CANDIDATE-GRAPH.json.gz": "0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc",
    "dense_support/field_interpreter.py": "e76bc78b132607890b2d9ea234d3a52e608e0e919bdc48308cc0727a2a07c73e",
    "native_support/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "native_support/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    RECIPES: "cf5dc6a35d3c8f6efbe4fc663853b2134234720c9cc8da16ee49aa1a0d98822f",
}
CASES = {1000000009: (17011, 34141), 998244353: (19181, 38303)}
WIDTH = 512
PUBLIC = 1501
OWNED = 68
FIRST = 154768
ROLE = 1256
REMOVED, RETAINED = 95828, 104442
ROUTES = ((476, 878), (878, 127), (476, 127))


def need(condition, label):
    if not condition:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def inputs():
    return {name: pinned(name) for name in PINS}


def pinned(name):
    raw = (HERE / name).read_bytes()
    need(digest(raw) == PINS[name], f"frozen bytes of {name}")
    return raw


def decoded(packed, pin, require_canonical=True):
    raw = gzip.decompress(packed)
    need(digest(raw) == pin, "exact decoded input digest")
    value = json.loads(raw)
    need(not require_canonical or canonical(value) == raw, "canonical decoded input")
    return value


def module(name, path):
    pinned(path)
    loader = importlib.util.spec_from_file_location(name, HERE / path)
    value = importlib.util.module_from_spec(loader)
    sys.modules[name] = value
    loader.loader.exec_module(value)
    return value


def graph(data, word, paid):
    metadata = data["metadata"]
    need(metadata["schema"] == "p104-exact-banked-dag/v1" and metadata["source_pr"] == 7700
         and metadata["source_pr_head"] == HEAD and metadata["source_word_sha256"] == WORD
         and metadata["caller_sha256"] == CALLER and metadata["source_clear_certificates_sha256"] == PINS["data/CERTS.json"],
         "source word, caller and CLEAR bindings")
    need(data["initial"] == word["initial"] and data["final"] == word["final"]
         and data["frames"] == word["frames"] and data["first_output"] == FIRST,
         "same typed public arrays and event clock")
    moves = {key: (a, b) for key, a, b in data["moves"]}
    forms = {key: {donor: Fraction(q) for donor, q in row} for key, row in data["forms"]}
    schedule = data["schedule"]
    need(len(moves) == len(data["moves"]) == paid and len(forms) == len(data["forms"]) == paid + PUBLIC
         and len(schedule) == len(forms) and set(schedule) == forms.keys() == moves.keys() | set(range(FIRST, FIRST+PUBLIC)),
         "complete unique paid and terminal schedule")
    chart_of = {~role: chart for role, chart in enumerate(data["initial"])}
    for key in schedule:
        a, b = moves[key] if key in moves else (data["final"][key-FIRST], None)
        need(all(chart_of.get(donor) == a and coefficient for donor, coefficient in forms[key].items()),
             f"earlier cocharted donors for bank {key}")
        if b is not None:
            chart_of[key] = b
    return moves, forms, schedule


def add_sparse(dst, src, scale):
    for donor, value in src.items():
        q = dst.get(donor, 0) + scale * value
        if q:
            dst[donor] = q
        else:
            dst.pop(donor, None)


def literal_clear_monitors(word, certificates, parent):
    """Recover cocharted observations with a chronological scalar shadow of the supplied tape."""
    moves, forms, _ = parent
    rows = [{~role: Fraction(1)} for role in range(PUBLIC)] + [None]*OWNED
    charts = word["initial"] + [None]*OWNED
    checked_moves, observations = set(), []
    for clock, (op, role, *args) in enumerate(word["program"]):
        if op == "INIT":
            need(role >= PUBLIC and rows[role] is None, f"fresh owned field {clock}")
            rows[role], charts[role] = {}, args[0]
            continue
        row = rows[role]
        need(row is not None, f"live field at {clock}")
        if op == "MOVE":
            a, b, owned = args
            need(charts[role] == a and owned == (role >= PUBLIC) and moves[clock] == (a, b)
                 and forms[clock] == row, f"literal source bank at {clock}")
            checked_moves.add(clock)
            rows[role], charts[role] = {clock: Fraction(1)}, b
            continue
        need(charts[role] == args[-1], f"literal operation chart at {clock}")
        if op == "CLEAR":
            need(role >= PUBLIC and clock in certificates, f"certified owned CLEAR at {clock}")
            right = defaultdict(dict)
            for donor, q in certificates[clock].items():
                need(donor != role and rows[donor] is not None and q, f"other live witness donor at {clock}")
                add_sparse(right[charts[donor]], rows[donor], q)
            need(REMOVED not in row and all(REMOVED not in value for value in right.values()),
                 f"the removed MOVE never supplies a certified CLEAR side at {clock}")
            observations.append((clock, role, charts[role], row, dict(right)))
            rows[role], charts[role] = None, None
        elif op == "SCALE":
            q = Fraction(args[0])
            rows[role] = {donor: value*q for donor, value in row.items()}
        else:
            donor, q, _ = args
            need(op == "ADD" and donor != role and charts[donor] == charts[role], f"cocharted literal ADD at {clock}")
            add_sparse(row, rows[donor], Fraction(q))
    need(checked_moves == moves.keys() and {row[0] for row in observations} == certificates.keys()
         and len(observations) == 235 and all(row is None for row in rows[PUBLIC:])
         and charts[:PUBLIC] == word["final"] and all(rows[r] == forms[FIRST+r] for r in range(PUBLIC)),
         "complete literal bank fold, public endpoints and private closure")
    return observations


def physical_bodies(word, parent, child, catalogue, compiler, checker):
    frames = word["frames"]
    need(catalogue["parent_graph_sha256"] == PARENT and catalogue["candidate_graph_sha256"] == CANDIDATE,
         "recipe catalogue covers the two frozen graphs")

    def occurrences(program):
        result = defaultdict(list)
        for slot, pair in sorted(program[0].items()):
            result[pair].append(slot)
        return result

    old_keys, new_keys = occurrences(parent), occurrences(child)
    wanted = old_keys.keys() | new_keys.keys()
    bodies = {}
    for entry in catalogue["pairs"]:
        pair = tuple(entry["pair"])
        if pair not in wanted:
            continue
        a, b = pair
        recipe = entry["recipe"]
        need(pair not in bodies and entry["ordered_bases"] == [frames[a], frames[b]]
             and entry["parent_moves"] == old_keys.get(pair, []) and entry["candidate_moves"] == new_keys.get(pair, [])
             and recipe["rank"] == abs(len(frames[a])-len(frames[b])) > 0,
             f"exact stored paid recipe and occurrence binding for {a}->{b}")
        bodies[pair] = checker.recipe(recipe)
    need(bodies.keys() == wanted and len(bodies) == 2979, "all actual paid ordered bodies")

    pair = ROUTES[-1]
    a, b = (compiler.canonical_frame(9, tuple(frames[i])) for i in pair)
    recipe, _ = compiler.lower_child(a.adjoint().then(b))
    need(recipe["rank"] == 6, "fresh direct role-1256 body rank")
    direct = checker.recipe(recipe)
    checker.equal(direct, bodies[pair], "fresh paid body and bound catalogue")
    checker.equal(direct, bodies[ROUTES[0]] + bodies[ROUTES[1]], "retained direct body and predecessor relay")
    bodies[pair] = direct
    return bodies


def replay_field(word, parent, child, certificates, monitors, bodies, field_engine, checker, prime, seeds):
    field = field_engine.GateInterpreter(prime, need)
    digest_rows = field_engine.digest
    scalar = cache(field.coefficient)
    zero = [0]*WIDTH

    @cache
    def chart(a):
        return checker.frame(word["frames"][a], 9)

    @cache
    def oracle_gates(a, b):
        return () if a == b else checker.adjoint(chart(a)) + chart(b)

    @cache
    def prepared(circuit):
        return tuple(field.gate(gate) for gate in circuit)

    def oracle(a, b, value):
        return field.apply(prepared(oracle_gates(a, b)), value)

    def paid(a, b, value):
        return field.apply(prepared(bodies[a,b]), value)

    def add(left, q, right):
        if q == 1:
            return [(x+y) % prime for x, y in zip(left, right, strict=True)]
        return [(x + q*y) % prime for x, y in zip(left, right, strict=True)]

    def scale(q, value):
        return [q*x % prime for x in value]

    def linear(terms, values):
        result = zero.copy()
        for donor, q in terms.items():
            result = add(result, scalar(q), values[donor])
        return result

    def direct_public(entries):
        layout = word["hosted"]
        dports = set(layout["Dports"])
        rows = [None]*PUBLIC

        def entry(target, donor):
            return oracle(word["initial"][donor], word["final"][target], entries[donor])

        def block(x, y, alpha, beta):
            need(rows[x] is None and rows[y] is None, "disjoint typed main blocks")
            rows[x] = add(entry(x, x), scalar(alpha), entry(x, y))
            rows[y] = add(scale(scalar(beta), entry(y, x)), scalar(1 + alpha*beta), entry(y, y))

        al, be, al2, be2 = (Fraction(layout[key]) for key in ("alpha", "beta", "alpha2", "beta2"))
        need(len(word["live"]) == 104 and len(layout["X2"]) == len(layout["Y2"]) == len(dports) == 96,
             "actual 104/96 typed main blocks")
        for position, x in enumerate(word["live"]):
            a, b = (0, 1) if position in dports else (al, be)
            block(x, x+112, a, b)
        for x, y in zip(layout["X2"], layout["Y2"], strict=True):
            block(x, y, al2, be2)
        mains = {role for role, row in enumerate(rows) if row is not None}
        need(len(mains) == 400 and ROLE not in mains, "400 main and 1,101 helper boundary oracles")
        for role in set(range(PUBLIC)) - mains:
            rows[role] = entry(role, role)
        return rows, mains

    links = []
    for a, b in ROUTES:
        cooked, ideal = bodies[a,b], oracle_gates(a,b)
        for direction in ("forward", "adjoint"):
            for column in (0, 17, 511):
                value = [0]*WIDTH
                value[column] = 1
                need(field.apply(prepared(cooked), value) == field.column_residue(checker.state(ideal, column)),
                     f"modular ordered physical map for {a}->{b} {direction} column {column}")
                links.append([a,b,direction,column])
            cooked, ideal = checker.adjoint(cooked), checker.adjoint(ideal)

    def literal(entries, seed):
        # Give every owned home unrelated dirty digits before its first INIT.
        poison = Random(27183 + seed)
        homes = [[poison.randrange(1, prime) for _ in range(WIDTH)] for _ in range(OWNED)]
        values = entries.copy() + homes
        charts = word["initial"] + [None]*OWNED
        initial_digest = digest_rows(entries)
        used_homes = {event[1] for event in word["program"] if event[0] == "INIT"}
        unused_homes = sorted(set(range(PUBLIC, PUBLIC+OWNED)) - used_homes)
        unused_digest = digest_rows(values[role] for role in unused_homes)
        need(len(used_homes) == 53 and len(unused_homes) == 15, "literal active and reserved owned-home inventory")
        physical_relays = {}
        observed = []
        initialized = cleared = nonzero = dirty_first_init = paid_count = 0
        for clock, (op, role, *args) in enumerate(word["program"]):
            row = values[role]
            if op == "INIT":
                need(role >= PUBLIC and charts[role] is None, f"literal owned INIT {clock}")
                dirty_first_init += any(row)
                row[:] = zero
                need(not any(row), f"complete initialized array at {clock}")
                charts[role] = args[0]
                initialized += 1
                continue
            need(charts[role] is not None, f"live literal array at {clock}")
            if op == "MOVE":
                a, b, owned = args
                need(charts[role] == a and owned == (role >= PUBLIC), f"literal MOVE owner/chart at {clock}")
                updated = paid(a,b,row)
                charts[role] = b
                paid_count += 1
                if clock in (REMOVED, RETAINED):
                    physical_relays[clock] = (row, updated)
            elif op == "CLEAR":
                need(role >= PUBLIC and charts[role] == args[0], f"literal CLEAR owner/chart at {clock}")
                expected = zero.copy()
                for donor, q in certificates[clock].items():
                    need(charts[donor] is not None and donor != role, f"other active CLEAR witness at {clock}")
                    expected = add(expected, scalar(q), oracle(charts[donor], charts[role], values[donor]))
                need(row == expected, f"literal live cross-chart CLEAR witness at {clock}")
                observed.append(row.copy())
                nonzero += any(row)
                row[:] = zero
                need(not any(row), f"complete restored array at {clock}")
                charts[role] = None
                cleared += 1
                continue
            elif op == "SCALE":
                updated = scale(scalar(args[0]), row)
            else:
                updated = add(row, scalar(args[1]), values[args[0]])
            if role >= PUBLIC:
                row[:] = updated
            else:
                values[role] = updated
        need(charts[:PUBLIC] == word["final"] and all(a is None for a in charts[PUBLIC:])
             and all(not any(values[r]) for r in used_homes)
             and digest_rows(values[role] for role in unused_homes) == unused_digest
             and all(values[PUBLIC+r] is home for r, home in enumerate(homes)),
             "literal terminal charts, restored active homes and intact reserved homes")
        need(initialized == cleared == 235 and nonzero == 193 and paid_count == 6144
             and dirty_first_init == len(used_homes) and digest_rows(entries) == initial_digest,
             "complete raw owned reset, CLEAR and borrowed-input scopes")
        return values[:PUBLIC], physical_relays, {"moves": paid_count, "initialized": initialized, "cleared": cleared,
                                                  "nonzero_clear": nonzero, "dirty_homes_initialized": dirty_first_init,
                                                  "restored_owned_homes": len(used_homes), "reserved_owned_homes": len(unused_homes),
                                                  "clear_sha256": digest_rows(observed)}

    def banked(program, entries, fault=False):
        moves, forms, schedule = program
        inputs_sha = digest_rows(entries)
        bars = {~role: row for role, row in enumerate(entries)}
        sources, returns, terminal = {}, {}, {}
        mutations = 0
        for slot in schedule:
            value = sources[slot] = linear(forms[slot], bars)
            if slot in moves:
                result = paid(*moves[slot], value)
                if fault and slot == RETAINED:
                    result = scale(field.i, result)
                    mutations += 1
                returns[slot] = bars[slot] = result
            else:
                terminal[slot-FIRST] = value
        need(mutations == int(fault), "one actual phase mutation at the retained event")
        held = [*entries, *sources.values(), *returns.values()]
        need(len({id(row) for row in held}) == len(held) == 2*(PUBLIC+len(moves))
             and digest_rows(entries) == inputs_sha, "distinct held banks and intact external input arrays")
        need(terminal.keys() == set(range(PUBLIC)) and returns.keys() == moves.keys(), "all public owners and paid returns")
        cleared, anomalies = [], []
        for clock, _, chart_at_clear, left, right in monitors:
            actual = linear(left, bars)
            expected = zero.copy()
            for chart_of_donors, terms in right.items():
                expected = add(expected, 1, oracle(chart_of_donors, chart_at_clear, linear(terms, bars)))
            if actual != expected:
                anomalies.append(clock)
            cleared.append(actual)
        need(fault or (not anomalies and sum(any(row) for row in cleared) == 193), "complete inherited CLEAR observations")
        outputs = [terminal[r] for r in range(PUBLIC)]
        snapshots = {slot: (sources[slot], returns[slot]) for slot in (REMOVED, RETAINED) if slot in moves}
        return outputs, snapshots, {"paid_moves": len(returns), "held_arrays": len(held), "terminal_arrays": len(outputs),
                                    "terminal_sha256": digest_rows(outputs),
                                    "paid_returns_sha256": digest_rows(returns[k] for k in sorted(returns)),
                                    "clear_observations": len(cleared), "clear_sha256": digest_rows(cleared),
                                    "clear_relation_failures": anomalies}

    results = []
    for seed in seeds:
        random = Random(seed)
        entries = [[random.randrange(prime) for _ in range(WIDTH)] for _ in range(PUBLIC)]
        need(any(entries[ROLE]), "nonzero arbitrary helper-1256 input")
        expected, mains = direct_public(entries)
        report = {"seed": seed, "inputs_sha256": digest_rows(entries), "oracle_sha256": digest_rows(expected)}
        old, old_relays, report["parent"] = banked(parent, entries)
        new, new_relays, report["candidate"] = banked(child, entries)
        need(old == expected == new, "every entry of all 1,501 typed public outputs")
        pre, mid = old_relays[REMOVED]
        post = old_relays[RETAINED][1]
        need(old_relays[RETAINED][0] == mid and new_relays[RETAINED] == (pre, post)
             and post == oracle(*ROUTES[-1], pre) and any(post), "same actual relay input and independently typed returned array")
        need(report["parent"]["clear_sha256"] == report["candidate"]["clear_sha256"], "all individual CLEAR arrays retained")
        report["role1256_relay"] = {"input_sha256": digest_rows([pre]), "old_midpoint_sha256": digest_rows([mid]),
                                    "returned_sha256": digest_rows([post]), "public_terminal_sha256": digest_rows([new[ROLE]])}
        if seed == seeds[0]:
            original, raw_relays, report["literal"] = literal(entries, seed)
            need(original == expected and raw_relays == old_relays
                 and report["literal"]["clear_sha256"] == report["parent"]["clear_sha256"],
                 "literal chronological output, relay and all CLEAR arrays agree with folded parent")
        if prime == 1000000009 and seed == seeds[0]:
            altered, altered_relay, faulty = banked(child, entries, fault=True)
            mismatches = [role for role in range(PUBLIC) if altered[role] != expected[role]]
            need(mismatches and altered_relay[RETAINED] == (pre, scale(field.i, post)),
                 "one retained physical MOVE quarter-phase mutation reaches a real public output")
            report["actual_phase_fault"] = {"slot": RETAINED, "pair": ROUTES[-1], "imaginary_root": field.i,
                                             "mismatched_roles": mismatches, "changed_main_roles": sorted(mains.intersection(mismatches)),
                                             "role1256_changed": ROLE in mismatches, "faulted_terminal_sha256": faulty["terminal_sha256"],
                                             "clear_relation_failures": faulty["clear_relation_failures"]}
        results.append(report)
        print(f"PASS_CF6A_DENSE_FIELD_CASE {prime} {seed}", flush=True)
    return {"prime": prime, "imaginary_root": field.i, "exact_column_links": links, "cases": results}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    files = inputs()
    word = decoded(files["data/WORD.json.gz"], WORD)
    caller = decoded(files["data/CALLER.json.gz"], CALLER, require_canonical=False)
    need(word["public"] == PUBLIC and word["owned_fields"] == OWNED and len(word["program"]) == FIRST
         and caller["stages"] == 16 and caller["ambient_rank"] == 137, "complete source and signed caller geometry")
    cert = json.loads(files["data/CERTS.json"])
    need(cert["candidate_canonical_sha256"] == WORD and len(cert["clear_event_index"]) == 235,
         "exact literal CLEAR certificate denominator")
    certificates = {int(clock): {int(role): Fraction(q) for role, q in item.items()}
                    for clock, item in cert["clear_event_index"].items()}
    before, after = (decoded(files[f"data/{name}-GRAPH.json.gz"], pin)
                     for name, pin in (("PARENT", PARENT), ("CANDIDATE", CANDIDATE)))
    need(before["metadata"]["kind"] == "parent" and after["metadata"]["kind"] == "candidate"
         and after["metadata"]["source_banked_graph_sha256"] == PARENT, "exact graph lineage")
    parent, child = graph(before, word, 6144), graph(after, word, 6143)
    p_moves, p_forms, _ = parent
    c_moves, c_forms, _ = child
    expected_moves, expected_forms = p_moves.copy(), p_forms.copy()
    expected_forms[RETAINED] = expected_forms.pop(REMOVED)
    del expected_moves[REMOVED]
    expected_moves[RETAINED] = ROUTES[-1]
    need(p_moves[REMOVED] == ROUTES[0] and p_moves[RETAINED] == ROUTES[1]
         and p_forms[RETAINED] == {REMOVED: Fraction(1)}
         and [key for key, row in p_forms.items() if REMOVED in row] == [RETAINED]
         and c_moves == expected_moves and c_forms == expected_forms
         and word["program"][REMOVED] == ["MOVE",ROLE,*ROUTES[0],False]
         and word["program"][RETAINED] == ["MOVE",ROLE,*ROUTES[1],False], "only the literal role-1256 relay changed")
    monitors = literal_clear_monitors(word, certificates, parent)
    compiler = module("_dense_cf6a_compiler", "native_support/clifford_exact.py")
    checker = module("_dense_cf6a_checker", "native_support/native_verify.py")
    field_engine = module("_dense_cf6a_field", "dense_support/field_interpreter.py")
    catalogue = decoded(files[RECIPES], RECIPES_DECODED)
    bodies = physical_bodies(word, parent, child, catalogue, compiler, checker)
    print(f"CF6A_BOUND_ACTUAL_PAID_BODIES {len(bodies)}", flush=True)
    fields = [replay_field(word, parent, child, certificates, monitors, bodies, field_engine, checker, prime, seeds)
              for prime, seeds in CASES.items()]
    inputs()
    result = {"status": "PASS_CF6A_ROLE1256_DENSE_HELD_ARRAYS", "source_head": HEAD,
              "source_word_sha256": WORD, "caller_sha256": CALLER, "graphs": {"parent": PARENT, "candidate": CANDIDATE},
              "inputs_sha256": PINS, "field_width": WIDTH, "public_outputs": PUBLIC, "main_outputs": 400,
              "helper_outputs": 1101, "paired_physical_paid_bodies": len(bodies), "clear_monitors": len(monitors),
              "recipe_catalogue_decoded_sha256": RECIPES_DECODED, "fresh_direct_lowering": list(ROUTES[-1]),
              "relay": {"role": ROLE, "removed": REMOVED, "retained": RETAINED, "routes": ROUTES, "ranks": [3,3,6]},
              "scope": "All materialized public arrays and exact certified live CLEAR observations in the tested finite fields.",
              "fields": fields}
    raw = canonical(result) + b"\n"
    with args.out.open("xb") as out:
        out.write(raw)
    print(result["status"], digest(raw), flush=True)


if __name__ == "__main__":
    main()

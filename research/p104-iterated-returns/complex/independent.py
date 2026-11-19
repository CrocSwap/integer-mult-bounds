#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check a literal rational P104 successor against the submitted #7781 supplier.

The frozen #7781 checker provides sparse rational replays and the signed-caller
readback. This driver derives all changes from the pinned words and layouts.
Nomination journals and receipts do not participate in the calculation.
"""

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DEFAULT_STATE = HERE.parent.parent / "STATE.json"
BASE_HEAD = "913fb6febe28cc3ccad1c16de8e45b8bce0da063"
BASE_WORD = "03ef8f6cc9ebb7394b5c7f8da70d44df965659ae4ff361bbc8d32c7a12121445"
BASE_LAYOUT = "37c04b0a349c1b7f7ada22533d3e4e6bacb42e4c6549f4257f4cbcae189a0275"
BASE_BINARY = "861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff"
BASE_UPPER = "0.00386981257853"
TARGET = "0.00387981257853"
REFERENCE_REPLAY = "0b428bc6fac4dc6ec014114bf4119782553fbb58d92b2a632b51629f4abe563b"
SOURCE_LOADER = "c70c3be6e48717c6a9a561ef2294d23437a60d7dbcbbddc1305a6fc54001bb3d"
SOURCE_LOCK = "4fad450ab3a7e237784d2d4b173ca6b33501b1c7f25241765d5bc7a597966093"
BASE_APPLICATION = "2ec405d37c8af8e85824601b6b0bfe4317dd908f8bed1e5381f895f397167615"
BASE_BINARY_FINITE = "32823f87b9edaa18869d8a1b401c8c1424e39784e08a9260e486f90b9faa37a5"
TICKS = 10**14
CHECKER_SHA = sha256(Path(__file__).read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def file_sha(path):
    return sha256(path.read_bytes()).hexdigest()


def load_module(name, path):
    spec = spec_from_file_location(name, path)
    need(spec and spec.loader, f"load pinned source {path}")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def diff(before, after):
    return {k: after.get(k, 0) - before.get(k, 0) for k in sorted(before.keys() | after.keys())
            if before.get(k, 0) != after.get(k, 0)}


def build_context(args):
    state_path = args.state
    if not state_path and not (args.cache or args.package or args.sources) and DEFAULT_STATE.exists():
        state_path = DEFAULT_STATE
    state = json.loads(state_path.read_bytes()) if state_path else {}
    if state:
        pin = state["recipient"]
        need((pin["head"], pin["word_sha256"], pin["layout_sha256"], pin["native_calls"]) ==
             (BASE_HEAD, BASE_WORD, BASE_LAYOUT, 48), "exact #7781 recipient")
    paths = state.get("source_paths", {})

    def resolve(path, cache_path, state_field):
        value = path or cache_path or paths.get(state_field)
        need(value, f"supply explicit path for {state_field}")
        return Path(value).resolve()

    public = resolve(args.package, args.cache / "parent" if args.cache else None, "public_package")
    locked = resolve(args.sources, args.cache, "locked_external_sources")
    base_path = resolve(args.base_graph, None, "complex_word")
    layout_path = resolve(args.base_layout, None, "complex_layout")
    reader_path = public / "complex/independent.py"
    need(file_sha(reader_path) == REFERENCE_REPLAY and file_sha(public / "SOURCE-LOCK.json") == SOURCE_LOCK and
         file_sha(public / "prepare_sources.py") == SOURCE_LOADER,
         "pin sparse replay and all external source manifests")
    reader = load_module("_p7781_literal_checker", reader_path)
    verify_sources = load_module("_p7781_source_lock", public / "prepare_sources.py")
    file_count = verify_sources.sources(locked)
    power_path = locked / "source/scripts/evaluate_recursive_power.py"
    need(file_sha(power_path) == reader.ORACLE, "pin interval engine")
    power = load_module("_p7781_power_bounds", power_path)
    source = locked / "source"
    peer = load_module("_p7774_grid_audit", locked / "peer/qualification.py")
    supplier = source / "research/p104-dual-supplier-lift"
    app_path = public / "evidence/application.json"
    need(file_sha(app_path) == BASE_APPLICATION, "pin #7781 complete archived invoice")
    prior = json.loads(app_path.read_bytes())
    need(prior["native_sha256"] == BASE_WORD and prior["layout_sha256"] == BASE_LAYOUT and
         prior["complex_crossing"][1] == BASE_UPPER, "archived comparator is the #7781 submitted word")
    return public, supplier, reader, power, peer, file_count, prior, base_path, layout_path


def read_case(reader, graph_path, layout_path, graph_sha, layout_sha):
    raw, word_pin = reader.read(graph_path, graph_sha)
    layout, layout_pin = reader.read(layout_path, layout_sha)
    graph = reader.Graph.parse(raw)
    spans = [reader.span(frame) for frame in graph.frames]
    expected, mains = reader.public_operator(graph, layout, spans)
    paid, targets = reader.ranks(graph, mains, spans)
    pins = {**word_pin, "word_file_sha256": file_sha(graph_path), "layout_sha256": layout_pin["content_sha256"],
            "layout_file_sha256": file_sha(layout_path)}
    return raw, graph, layout, spans, expected, mains, (paid, targets), pins


def endpoint_address(graph, layout, node):
    address = node - graph.first
    return {"node": node, "address": address, "owner_label": layout["source_labels"][address]}


def boundary_changes(base, layout0, other, layout1, mains):
    need(base.size <= other.size and base.first == other.first and
         layout1["source_labels"][:base.size] == layout0["source_labels"],
         "all inherited owner labels and address bindings retained")
    need(other.frames[:len(base.frames)] == base.frames and
         all(layout0[key] == layout1[key] for key in ("ports", "live", "hosted")),
         "unchanged chart definitions, main bindings and signed port coefficients")
    changed, fresh = [], []
    for i, charts in enumerate(zip(other.initial, other.final, strict=True)):
        record = {**endpoint_address(other, layout1, other.first + i), "charts": charts}
        if i >= base.size:
            fresh.append(record)
        elif (base.initial[i], base.final[i]) != charts:
            need(i not in mains, f"main owner boundary changed at address {i}")
            changed.append({**record, "before": (base.initial[i], base.final[i])})
    return changed, fresh


def move_changes(base, candidate):
    retired = sorted(base.moves.keys() - candidate.moves.keys())
    inserted = sorted(candidate.moves.keys() - base.moves.keys())
    common = base.moves.keys() & candidate.moves.keys()
    recharted = sorted(k for k in common if base.moves[k] != candidate.moves[k])
    changed = sorted(k for k in common if dict(base.forms[k]) != dict(candidate.forms[k]))
    return {
        "retired": {k: base.moves[k] for k in retired},
        "inserted": {k: candidate.moves[k] for k in inserted},
        "recharted": {k: {"before": base.moves[k], "after": candidate.moves[k]} for k in recharted},
        "retained_changed_form_keys": changed,
    }


def watched_replay(reader, graph, expected, own_ranks, pin, paid_watch, donor_watch):
    rows, inputs = reader.forward(graph, paid_watch | donor_watch)
    columns, outputs = reader.adjoint(graph, paid_watch)
    correct = reader.transpose(expected)
    need(rows == expected and columns == correct, "complete exact forward and independent adjoint identities")
    return reader.overview(graph, pin, rows, columns, own_ranks), rows, inputs, outputs


def held_replay(reader, graph, layout, expected, sold=(), inserted=()):
    """Exercise real normalized sender cells and dirty reinstallation of owner homes."""
    s = "sender"
    sources = {~i for i in range(graph.size)}
    homes = sources | set(graph.order) | {s}
    bank = reader.GuardedBank(homes)
    guards = bank.guard
    width = reader.COMPONENTS
    dirty = (11, -23, 37, -41)
    sample = {~i: tuple((-1)**(i+j) * (31*i + 7*j + 1) for j in range(width))
              for i in range(graph.size)}
    for k in homes:
        bank.install(k, reader.Held(k, -1, dirty))
    # Probe a real target/returned home with a missing physical address in its CLEAR.
    first = ~0
    bank.clear(first, width - 1)
    reader.reject(lambda: bank.install(first, reader.Held(first, graph.initial[0], sample[first])),
                  "install in occupied or dirty home")
    for k in homes:
        bank.clear(k)
    for k, cells in sample.items():
        bank.install(k, reader.Held(k, graph.initial[~k], cells))
    sold, inserted = set(sold), set(inserted)
    controls = {}
    for node in graph.order:
        chart = graph.source_chart(node)
        addends = [(q, bank.load(donor, donor, chart)) for donor, q in graph.forms[node]]
        cells = tuple(sum(q * values[j] for q, values in addends) for j in range(width))
        if node in graph.moves:
            before = reader.Held(node, chart, cells)
            bank.install(s, before)
            moved = bank.load(s, node, chart)
            if node in sold | inserted:
                reader.reject(lambda: bank.install(s, before), "install in occupied or dirty home")
                residue = cells[-1]
                if residue:
                    bank.clear(s, width - 1)
                    reader.reject(lambda: bank.install(s, before), "install in occupied or dirty home")
                controls[node] = {
                    "role": "retired_paid" if node in sold else "introduced_or_recharted_paid",
                    "chart": chart, "source_row_last_sample": str(residue),
                    "live_sender_alias_rejected": True, "partial_clear_rejected": bool(residue),
                }
            bank.install(node, reader.Held(node, graph.moves[node][1], moved))
            bank.clear(s)
        else:
            bank.install(node, reader.Held(node, chart, cells))
    need(all(bank.load(k, k, graph.initial[~k]) == cells for k, cells in sample.items()),
         "preserved arbitrary independent entry homes until terminal installation")
    for i, row in enumerate(expected):
        home, terminal = ~i, graph.first + i
        staged = bank.load(terminal, terminal, graph.final[i])
        want = tuple(sum(q * sample[~j][k] for j, q in row.items()) for k in range(width))
        bank.clear(home)
        bank.install(home, reader.Held(home, graph.final[i], staged))
        need(bank.load(home, home, graph.final[i]) == want,
             f"same original owner {layout['source_labels'][i]} reinstalled at final chart")
    for k in homes:
        bank.clear(k)
    need(bank.guard is guards and all(slot == reader.EMPTY for slot in bank.slots.values()),
         "complete guarded retirement")
    return {"scope": "four addressed normalized rational components", "distinct_homes": len(homes),
            "addressed_overwrites_including_controls": bank.count, "same_owner_installs": graph.size,
            "dirty_entry_tail_rejected": True, "controls_on_literal_sender_rows": controls,
            "guards_preserved": True}


def source_column(graph, source):
    """Evaluate a single exact unit input on the actual modified tape."""
    values = {~source: Fraction(1)}
    terminals = {}
    for node in graph.order:
        value = sum(q * values[d] for d, q in graph.forms[node] if d in values)
        if value:
            if node in graph.moves:
                values[node] = value
            else:
                terminals[node - graph.first] = value
    return terminals


def terminal_row(graph, terminal):
    """Pull a single exact terminal covector through the actual modified tape."""
    pending = {graph.first + terminal: Fraction(1)}
    for node in reversed(graph.order):
        value = pending.pop(node, 0)
        if value:
            for donor, q in graph.forms[node]:
                pending[donor] = pending.get(donor, 0) + q * value
    return {~node: value for node, value in pending.items() if value}


def axis_digest(reader, vector):
    return reader.digest([[i, str(v)] for i, v in sorted(vector.items())])


def coefficient_fault(reader, graph, layout, expected, node, donor, input_row, pulse, scoped):
    """Delete one actual nonzero literal and test its exact rank-one defect."""
    form = dict(graph.forms[node])
    need(donor in form and input_row and pulse, f"nontrivial control at {node}:{donor}")
    coefficient = form.pop(donor)
    faulty = replace(graph, forms={**graph.forms, node: tuple(form.items())})
    faulty.validate_causality()
    terminal, source = min(pulse), min(input_row)
    control = {}
    if scoped:
        old_col = {i: row[source] for i, row in enumerate(expected) if source in row}
        old_row = expected[terminal]
        new_col, new_row = old_col.copy(), old_row.copy()
        for i, q in pulse.items():
            new_col[i] = new_col.get(i, 0) - coefficient * q * input_row[source]
        for i, q in input_row.items():
            new_row[i] = new_row.get(i, 0) - coefficient * pulse[terminal] * q
        new_col = {i: q for i, q in new_col.items() if q}
        new_row = {i: q for i, q in new_row.items() if q}
        actual_col, actual_row = source_column(faulty, source), terminal_row(faulty, terminal)
        need(actual_col == new_col and actual_row == new_row and new_col != old_col and new_row != old_row,
             f"modified tape gives the exact defect on the witnessed column and covector {node}:{donor}")
        coefficient_after = actual_col.get(terminal, 0)
        control = {"scope": "one exact source column and one exact terminal adjoint covector on modified word",
                   "entries_per_orientation": graph.size, "mutated_source_column_sha256": axis_digest(reader, actual_col),
                   "mutated_terminal_covector_sha256": axis_digest(reader, actual_row)}
    else:
        predicted = [row.copy() for row in expected]
        for i, sensitivity in pulse.items():
            for j, gain in input_row.items():
                out = predicted[i]
                value = out.get(j, 0) - coefficient * sensitivity * gain
                if value:
                    out[j] = value
                else:
                    out.pop(j, None)
        observed, _ = reader.forward(faulty)
        columns, _ = reader.adjoint(faulty)
        need(observed != expected and observed == predicted and columns == reader.transpose(predicted),
             f"removed actual rational contact gives the predicted defect in both directions {node}:{donor}")
        coefficient_after = observed[terminal].get(source, 0)
        control = {"scope": "all exact forward rows and adjoint columns on modified word",
                   "faulty_forward_sha256": reader.row_digest(observed),
                   "faulty_adjoint_sha256": reader.row_digest(columns)}
    return {"node": node, "donor": donor, "removed_coefficient": str(coefficient),
            "affected_terminal_address": terminal, "affected_terminal_label": layout["source_labels"][terminal],
            "source_address": source, "source_label": layout["source_labels"][source],
            "normal_coefficient": str(expected[terminal].get(source, 0)),
            "faulty_coefficient": str(coefficient_after), **control}


def fresh_input_fault(reader, graph, layout, expected, address, scoped):
    """Remove a fresh independent entrance at every actual incidence."""
    changes = {k: tuple((d, q) for d, q in form if d != ~address)
               for k, form in graph.forms.items() if any(d == ~address for d, _ in form)}
    need(changes, f"visible independent fresh input {address}")
    faulty = replace(graph, forms={**graph.forms, **changes})
    record = {"source_address": address, "source_label": layout["source_labels"][address],
              "omitted_at_live_nodes": sorted(changes)}
    need(expected[address] == {address: 1}, "original fresh identity")
    if scoped:
        column, row = source_column(faulty, address), terminal_row(faulty, address)
        need(not column and not row, f"loss of fresh source {address} erases its own independent return")
        return {**record, "scope": "exact source column and terminal covector of the omitted fresh field",
                "entries_per_orientation": graph.size, "mutated_source_column_sha256": axis_digest(reader, column),
                "mutated_terminal_covector_sha256": axis_digest(reader, row)}
    rows, _ = reader.forward(faulty)
    columns, _ = reader.adjoint(faulty)
    want = expected.copy()
    want[address] = {}
    need(rows == want and columns == reader.transpose(want),
         f"loss of fresh source {address} erases its own return exactly")
    return {**record, "scope": "all exact forward rows and adjoint columns on modified word",
            "mutated_forward_sha256": reader.row_digest(rows), "mutated_adjoint_sha256": reader.row_digest(columns)}


def raw_bracket(reader, invoice, powers):
    def price(tick):
        return reader.interval(*invoice, powers, Fraction(tick, TICKS))

    left, right = 1, 690000000000
    need(price(left)[0] > 0 and price(right)[1] < 0, "raw crossing inside the finite compiler range")
    while left + 1 < right:
        mid = (left + right) // 2
        lo, hi = price(mid)
        need(lo > 0 or hi < 0, "directed midpoint sign")
        if lo > 0:
            left = mid
        else:
            right = mid
    return [tick_text(left), tick_text(right)], [reader.decimal_bounds(price(t)) for t in (left, right)]


def tick_text(tick):
    return f"{tick // TICKS}.{tick % TICKS:014d}"


def signed_invoices(reader, base, candidate, fixed, powers, price_point):
    before, after = reader.invoice(base, fixed), reader.invoice(candidate, fixed)
    signs = ("paid", "targets")

    def entries(invoice):
        return {k: [[r, n] for r, n in sorted(h.items())] for k, h in zip(signs, invoice, strict=True)}

    def record(invoice):
        payload = {"native_calls": 48, "caller_sha256": reader.PUBLIC_STREAM, "tariff": "rank^(1-kappa)",
                   "rank_histograms": entries(invoice)}
        return {**payload, "sha256": reader.digest(payload),
                "totals": {k: sum(n for _, n in h) for k, h in entries(invoice).items()}}

    a, b = (reader.interval(*invoice, powers, price_point) for invoice in (before, after))
    old_raw, old_margins = raw_bracket(reader, before, powers)
    need(old_raw[1] == BASE_UPPER, "independently confirmed directed #7781 upper endpoint")
    raw, margins = raw_bracket(reader, after, powers)
    base_record, candidate_record = record(before), record(after)
    paid, targets = map(Counter, after)
    tariff_rank = min(paid)
    paid[tariff_rank] -= 1
    changed = record((paid, targets))
    reader.reject(lambda: need(changed["sha256"] == candidate_record["sha256"],
                               "signed invoice content mismatch"), "signed invoice content mismatch")
    wrong_margin = reader.interval(paid, targets, powers, price_point)
    need(wrong_margin[0] > b[1], "omitted paid entry creates false apparent savings")
    return before, after, {
        "base": base_record, "candidate": candidate_record,
        "paid_delta": diff(before[0], after[0]), "target_delta": diff(before[1], after[1]),
        "target_kappa": str(price_point), "base_margin": reader.decimal_bounds(a),
        "candidate_margin": reader.decimal_bounds(b),
        "saving": reader.decimal_bounds((b[0] - a[1], b[1] - a[0])),
        "base_raw_bracket": old_raw, "base_raw_endpoint_margins": old_margins,
        "raw_bracket": raw, "raw_endpoint_margins": margins,
        "omitted_paid_entry_control": {"rank": tariff_rank, "rejected": True,
                                       "tampered_sha256": changed["sha256"],
                                       "wrong_margin": reader.decimal_bounds(wrong_margin)},
    }


def ordinary_case(reader, peer, supplier_path, raw, graph, layout, mains, expected_invoice, bracket, bit_cap):
    import supplier
    import supplier_gate
    from closed_application import apply, verify_caller

    need(Path(supplier.__file__).resolve() == (supplier_path / "complex/supplier.py").resolve(),
         "physical provider comes from the locked source tree")
    caller = supplier.read(supplier.SOURCE / "data/CALLER.json.gz")
    moves, rows = peer.graph_inputs(raw)
    physical = supplier.physical
    native = physical.graph_bounds(raw, moves, rows, mains)
    h = layout["hosted"]
    owners = mains, set(h["Dports"]), list(zip(h["X2"], h["Y2"], strict=True))
    conversion = peer.native_replay(supplier, raw, layout, owners, moves, rows, native, caller)
    signed, guard, proof, coefficients = verify_caller(
        caller, raw, layout, supplier.read(supplier.SOURCE / "data/CALLER-PHASE-BASES.json"))
    need(proof["readback"]["event_stream_sha256"] == reader.PUBLIC_STREAM and
         signed["finite_binding"]["stage_helper_owners"] == 48 * (graph.size - len(mains)),
         "full physical caller and stock bind all per-call owners")
    lo, hi = bracket
    ticks = min(int(Fraction(lo)*TICKS), int(bit_cap*TICKS))
    claim, tested = tick_text(ticks - 8), tick_text(ticks - 1)
    original = supplier_gate.BIT_PIN
    try:
        supplier_gate.BIT_PIN = str(bit_cap)
        application = apply(native, signed, guard, coefficients, conversion, physical, claim, tested, lo, hi, bit_cap)
    finally:
        supplier_gate.BIT_PIN = original
    need((application["invoice"]["paid"], application["invoice"]["targets"]) == expected_invoice,
         "ordinary and independent signed invoice agree entry by entry")
    return {"native": native, "conversion": conversion, "caller": signed, "caller_proof": proof,
            "caller_guard": guard, "application": application, "ordinary_binary_cap": str(bit_cap),
            "conditional_joint_lower": claim}


def chart_controls(reader, supplier, graph, changes, births, paid):
    """Read the relative maps at all changed chart boundaries independently."""
    sys.path.insert(0, str(supplier.parent / "shared-wire-split-composition/frozen"))
    import clifford_exact as producer
    import native_verify as checker

    @cache
    def physical_chart(index):
        return producer.canonical_frame(9, tuple(graph.frames[index]))

    @cache
    def reference_chart(index):
        return checker.frame(graph.frames[index], 9)

    paid_routes = set(paid["inserted"].values()) | {row["after"] for row in paid["recharted"].values()}
    productive_routes = {row["charts"] for row in (*changes, *births)}
    receipts = []
    for a, b in sorted(paid_routes | productive_routes):
        record, _ = producer.lower_child(physical_chart(a).adjoint().then(physical_chart(b)))
        rank = abs(len(graph.frames[a]) - len(graph.frames[b]))
        need(record["rank"] == rank > 0, f"charged physical rank of chart map {a}→{b}")
        compare = checker.adjoint(reference_chart(a)) + reference_chart(b)
        actual = checker.recipe(record)
        checker.equal(actual, compare, "signed Clifford action and absolute phase")
        for op, reference in ((actual, compare), (checker.adjoint(actual), checker.adjoint(compare))):
            need(all(checker.state(op, i) == checker.state(reference, i) for i in range(512)),
                 f"all exact physical forward and adjoint columns on chart pair {a}→{b}")
        corrupt = deepcopy(record)
        corrupt["left"]["phase"] = (corrupt["left"]["phase"] + 1) % 4
        reader.reject(lambda: checker.equal(checker.recipe(corrupt), compare, "mutated physical phase"),
                      "mutated physical phase: exact global phase")
        receipts.append({"charts": (a, b), "paid": (a, b) in paid_routes,
                         "productive": (a, b) in productive_routes,
                         "rank": rank, "recipe_sha256": reader.digest(record),
                         "forward_and_adjoint_columns": 1024, "global_phase_fault_rejected": True})
    return receipts


def fault_spec(value):
    try:
        if value.count(":") == 1:
            return tuple(map(int, value.split(":")))
        return int(value), None
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use a paid or terminal node, optionally node:donor") from exc


def verify(args):
    public, supplier, r, power, peer, file_count, prior, base_path, base_layout_path = build_context(args)
    c_path, l_path = args.candidate or base_path, args.layout or base_layout_path
    base_raw, base, layout0, spans0, expected0, mains0, ranks0, pin0 = read_case(
        r, base_path, base_layout_path, BASE_WORD, BASE_LAYOUT)
    new_raw, new, layout1, spans1, expected1, mains1, ranks1, pin1 = read_case(
        r, c_path, l_path, args.sha or BASE_WORD, args.layout_sha or BASE_LAYOUT)
    del base_raw, spans0, spans1
    need(base.size == 1279 and len(base.moves) == 5714 and mains0 == mains1, "submitted native census")
    pairs, births = boundary_changes(base, layout0, new, layout1, mains0)
    need(expected1[:base.size] == expected0 and
         all(expected1[i] == {i: Fraction(1)} for i in range(base.size, new.size)),
         "all old independent owner operators plus distinct fresh identity rows")
    paid = move_changes(base, new)
    comparison, comparison_layout, compared_expected, compared_ranks, control_pin = (
        base, layout0, expected0, ranks0, pin0)
    if args.control_word:
        _, comparison, comparison_layout, _, compared_expected, cmains, compared_ranks, control_pin = read_case(
            r, args.control_word, args.control_layout, args.control_sha, args.control_layout_sha)
        need(cmains == mains0 and comparison.size >= base.size and compared_expected[:base.size] == expected0,
             "incremental predecessor preserves the inherited owner operator")
        boundary_changes(base, layout0, comparison, comparison_layout, mains0)
    comparison_pairs, comparison_births = boundary_changes(comparison, comparison_layout, new, layout1, mains0)
    comparison_paid = move_changes(comparison, new)
    changed_forms = [k for k in new.terminals if dict(base.forms.get(k, ())) != dict(new.forms[k])]
    altered_forms = {k for k in new.terminals if dict(comparison.forms.get(k, ())) != dict(new.forms[k])}
    changed_terminals = altered_forms | {row["node"] for row in (*comparison_pairs, *comparison_births)}
    paid_watch = set(comparison_paid["inserted"]) | set(comparison_paid["recharted"]) | set(
        comparison_paid["retained_changed_form_keys"])
    direct = set(args.fault) | {(k, None) for k in comparison_paid["inserted"]}
    direct.update((row["node"], None) for row in (*comparison_pairs, *comparison_births))
    if changed_terminals and not direct:
        direct.add((min(changed_terminals), None))
    for k, donor in direct:
        need(k in new.forms and (k in paid_watch or k in changed_terminals),
             f"fault at an actual changed literal row {k}")
        if k in new.moves:
            paid_watch.add(k)
    donor_watch = {d for k, _ in direct for d, _ in new.forms[k]}
    print("Replaying all submitted and nominated rational rows and adjoints.", flush=True)
    old, old_rows, _, _ = watched_replay(r, base, expected0, ranks0, pin0, set(), set())
    candidate, new_rows, inputs, outputs = watched_replay(
        r, new, expected1, ranks1, pin1, paid_watch, donor_watch)
    need(new_rows[:base.size] == old_rows, "same original source-address operator")
    defects = []
    for k, picked in sorted(direct, key=lambda a: (a[0], a[1] is None, a[1] or 0)):
        # Omit a changed donor where possible. A replaced terminal namespace has
        # no prior row, so its literal input is a valid additional witness.
        donor_old = dict(comparison.forms.get(k, ()))
        viable = [d for d, q in new.forms[k] if inputs[d] and donor_old.get(d) != q]
        if picked is None:
            if any(n == k and d is not None for n, d in direct):
                continue
            viable = viable or [d for d, _ in new.forms[k] if inputs[d]]
            need(viable, f"observable nonzero contact on changed row {k}")
            picked = viable[0]
        pulse = outputs[k] if k in new.moves else {k - new.first: Fraction(1)}
        defects.append(coefficient_fault(r, new, layout1, expected1, k, picked, inputs[picked], pulse,
                                         args.scoped_faults))
    fresh_controls = [fresh_input_fault(r, new, layout1, expected1, d["address"], args.scoped_faults)
                      for d in comparison_births]
    print("Checking held-home clearing and unchanged signed caller.", flush=True)
    held0 = held_replay(r, base, layout0, expected0, sold=paid["retired"])
    held1 = held_replay(r, new, layout1, expected1, inserted=set(paid["inserted"]) | set(paid["recharted"]))
    held_comparison = None
    if args.control_word:
        held_comparison = held_replay(r, comparison, comparison_layout, compared_expected,
                                      sold=comparison_paid["retired"])
    labels = {**layout1, "source_labels": layout1["source_labels"].copy()}
    labels["source_labels"][-1] = labels["source_labels"][0]
    r.reject(lambda: r.public_operator(new, labels, [r.span(frame) for frame in new.frames]),
             "duplicate public owner label")
    p0, t0, caller0 = r.signed_caller(supplier, base, layout0)
    p1, t1, caller1 = r.signed_caller(supplier, new, layout1)
    need((p0, t0) == (p1, t1) and caller0["readback"] == caller1["readback"],
         "fixed signed caller census and original emitted instructions")
    print("Regenerating both complete signed rank histograms.", flush=True)
    powers = cache(power.power_bounds)
    before, after, invoice = signed_invoices(
        r, ranks0, ranks1, (p1, t1), powers, args.target)
    archived_invoice = prior["application"]["invoice"]
    need(before == tuple({int(k): v for k, v in archived_invoice[key].items()} for key in ("paid", "targets")),
         "submitted full invoice agrees with independent literal regeneration")
    receipt = {
        "schema": "p104-7781-independent-successor/v2", "reviewer_sha256": CHECKER_SHA,
        "source_lock_sha256": SOURCE_LOCK,
        "locked_source_files_verified": file_count, "base_public_head": BASE_HEAD,
        "base": old, "candidate": candidate,
        "changed_owner_boundaries": pairs, "fresh_independent_owners": births,
        "paid_changes": paid, "changed_terminal_forms": [endpoint_address(new, layout1, k) for k in changed_forms],
        "controls": {"literal_coefficient_removals": defects, "fresh_source_omissions": fresh_controls,
                     "duplicate_public_owner_rejected": True,
                     "base_cleanup": held0, "candidate_cleanup": held1},
        "caller": {"base": caller0, "candidate": caller1, "paid": p1, "targets": t1},
        "full_invoice": invoice,
    }
    if args.control_word:
        intermediate = r.invoice(compared_ranks, (p1, t1))
        prior_band, prior_endpoints = raw_bracket(r, intermediate, powers)
        margin0, margin1 = (r.interval(*histograms, powers, args.target) for histograms in (intermediate, after))
        receipt["incremental_comparison"] = {
            "source": control_pin, "changed_owner_boundaries": comparison_pairs,
            "fresh_independent_owners": comparison_births, "paid_changes": comparison_paid,
            "changed_terminal_forms": [endpoint_address(new, layout1, k) for k in sorted(altered_forms)],
            "cleanup_before_change": held_comparison,
            "prior_raw_bracket": prior_band, "prior_raw_endpoint_margins": prior_endpoints,
            "paid_delta": diff(intermediate[0], after[0]), "target_delta": diff(intermediate[1], after[1]),
            "directed_saving_at_target": r.decimal_bounds((margin1[0] - margin0[1], margin1[1] - margin0[0])),
        }
    if args.ordinary:
        print("Recomputing complete ordinary, compiler and precision-tape charges.", flush=True)
        bit_path = args.binary_finite or public / "binary/FINITE.json"
        bit_normal = not args.binary_finite
        expected_hash = BASE_BINARY_FINITE if bit_normal else args.binary_finite_sha
        need(expected_hash and file_sha(bit_path) == expected_hash, "pin separate ordinary binary receipt")
        bit = json.loads(bit_path.read_bytes())
        need(bit.get("word_sha256") == (BASE_BINARY if bit_normal else args.binary_word),
             "separate binary word bound to its ordinary receipt")
        bit_cap = Fraction(bit["ordinary_admitted"])
        physical = ordinary_case(r, peer, supplier, new_raw, new, layout1, mains1, after,
                                 invoice["raw_bracket"], bit_cap)
        from physical import check_depth_guard, root_envelope
        common = root_envelope({"base": prior["native"], "candidate": physical["native"]}, physical["caller_guard"])
        physical.update(common_root=common, common_depth_guards={
            "base": check_depth_guard(common, int(prior["application"]["compiler"]["H"])),
            "candidate": check_depth_guard(common, int(physical["application"]["compiler"]["H"])),
        }, binary_finite_file_sha256=expected_hash, binary_word_sha256=bit["word_sha256"],
            directed_gain_above_base_upper=str(Fraction(physical["conditional_joint_lower"]) - Fraction(BASE_UPPER)),
            remaining_to_target=str(max(Fraction(0), Fraction(args.target) -
                                        Fraction(physical["conditional_joint_lower"]))))
        receipt["ordinary_and_compiler"] = physical
    if args.charts:
        print("Checking signed maps and phase faults at changed chart boundaries.", flush=True)
        receipt["changed_chart_adapters"] = chart_controls(r, supplier, new, pairs, births, paid)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path)
    for option in ("cache", "package", "sources", "base-graph", "base-layout", "candidate", "layout",
                   "control-word", "control-layout", "binary-finite", "out"):
        parser.add_argument(f"--{option}", type=Path, required=option == "out")
    for option in ("sha", "layout-sha", "control-sha", "control-layout-sha", "binary-finite-sha", "binary-word"):
        parser.add_argument(f"--{option}")
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--fault", type=fault_spec, action="append", default=[])
    parser.add_argument("--ordinary", action="store_true")
    parser.add_argument("--charts", action="store_true")
    parser.add_argument("--scoped-faults", action="store_true",
                        help="test each modified word in one complete exact source column and terminal covector")
    args = parser.parse_args()
    need(__debug__, "run with assertions enabled")
    need(bool(args.candidate) == bool(args.sha) and bool(args.layout) == bool(args.layout_sha),
         "each explicit candidate path requires its content pin")
    controls = (args.control_word, args.control_layout, args.control_sha, args.control_layout_sha)
    need(all(controls) or not any(controls), "supply both paths and both hashes for an immediate predecessor")
    args.out.write_text(json.dumps(verify(args), indent=2, sort_keys=True) + "\n")
    print(f"Saved {args.out}", flush=True)


if __name__ == "__main__":
    main()

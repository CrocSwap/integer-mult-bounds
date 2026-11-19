#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently replay a frozen subdivided P104 word and its 48-call invoice.

The rational-graph representation follows PR #7774. No builder, subdivision
journal evaluator, or native bound calculator participates in this check.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
from hashlib import sha256
from itertools import chain
from math import gcd, lcm
from pathlib import Path
import gzip
import json
import sys


BASE_NATIVE = "934b7d4d792a5771bbcd28053d7797a9938f6b23faddaafe46451158eec81849"
BASE_LAYOUT = "d233f9ba1fc39c4be51685a45da1940fe43dc3a3fd7699a8b27339e1e063b489"
PUBLIC_STREAM = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
HOMOGENEOUS = "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a"
MIXED = "80009663da460229a57f09bde90e35294329a210ae7fc7ef6d1f05b61ffccbf4"
ORACLE = "52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad"
NATIVE_CALLS = 48
TARGET = "0.00386380485468"
COMPARATOR_PLUS_GAIN = "0.00386896184248"
ADMITTED_BINARY = "0.00386969950"
COMPONENTS = 4
CHECKER_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(encoded(value)).hexdigest()


def read(path, expected):
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw
    value = json.loads(payload)
    actual = digest(value)
    need(actual == expected, f"canonical content mismatch for {path.name}")
    return value, {"content_sha256": actual}


def span(frame):
    points = {0}
    for axis in frame:
        need(type(axis) is int and 0 < axis < 512 and axis not in points, "independent native chart axes")
        points |= {x ^ axis for x in points}
    return frozenset(points)


@dataclass(frozen=True)
class Graph:
    frames: list
    initial: tuple
    final: tuple
    first: int
    moves: dict
    forms: dict
    order: tuple

    @property
    def size(self):
        return len(self.initial)

    @property
    def terminals(self):
        return range(self.first, self.first + self.size)

    def source_chart(self, node):
        return self.moves[node][0] if node in self.moves else self.final[node - self.first]

    @classmethod
    def parse(cls, raw):
        frames = raw["frames"]
        initial, final = tuple(raw["initial"]), tuple(raw["final"])
        first = raw["first_output"]

        def valid_chart(chart):
            return type(chart) is int and 0 <= chart < len(frames)

        need(len(initial) == len(final) and type(first) is int and first > 0, "public graph census")
        need(all(map(valid_chart, chain(initial, final))), "all public chart IDs")
        moves = {}
        for k, a, b in raw["moves"]:
            need(type(k) is int and 0 <= k < first and k not in moves and valid_chart(a) and valid_chart(b),
                 "unique paid route with valid directed charts")
            moves[k] = a, b
        forms = {}
        for node, terms in raw["forms"]:
            need(type(node) is int and node not in forms and terms, "unique nonempty rational form")
            parsed = {}
            for donor, text in terms:
                need(type(donor) is int and donor not in parsed and type(text) is str, "unique literal donor")
                coefficient = Fraction(text)
                need(coefficient and str(coefficient) == text, "canonical nonzero rational literal")
                parsed[donor] = coefficient
            forms[node] = tuple(parsed.items())
        order = tuple(raw["schedule"])
        need(forms.keys() == moves.keys() | set(range(first, first + len(initial))),
             "every paid arrival and terminal has an actual form")
        need(len(order) == len(forms) and set(order) == forms.keys(), "complete literal chronology")
        graph = cls(frames, initial, final, first, moves, forms, order)
        graph.validate_causality()
        return graph

    def validate_causality(self):
        available = {~i: c for i, c in enumerate(self.initial)}
        for node in self.order:
            source = self.source_chart(node)
            for donor, _ in self.forms[node]:
                need(donor in available, f"use before completed arrival at {node} from {donor}")
                need(available[donor] == source, f"wrong source chart at {node} from {donor}")
            if node in self.moves:
                available[node] = self.moves[node][1]


def public_operator(graph, layout, spans):
    labels, h = layout["source_labels"], layout["hosted"]
    need(layout["frames"] == graph.frames and layout["public"] == graph.size == len(labels),
         "layout and graph public chart inventory")
    need(len(set(labels)) == len(labels), "duplicate public owner label")
    need(tuple(Fraction(h[k]) for k in ("alpha", "beta", "alpha2", "beta2")) ==
         (-1, Fraction(1, 2), -1, 0), "signed port constants")
    secondary = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    live, axes = layout["live"], layout["ports"]
    need(len(live) == len(axes) == len(set(axes)) == 104 and
         len(secondary) == 96 and secondary.keys() <= set(range(104)), "physical 96 A and 8 B ports")
    ports, endpoints = {}, [{i: Fraction(1)} for i in range(graph.size)]
    for p, (x, head) in enumerate(zip(live, axes, strict=True)):
        y = x + 112
        group = (x, y) + secondary.get(p, ())
        need(all(type(i) is int and 0 <= i < graph.size for i in group), "physical port address range")
        need(graph.frames[graph.initial[x]] == [head] and graph.frames[graph.initial[y]] == [] and
             spans[graph.final[x]] == frozenset(range(512)) and
             spans[graph.final[y]] == frozenset(v for v in range(512) if (v & head).bit_count() % 2 == 0),
             f"absolute primary port boundary {p}")
        if p in secondary:
            u, v = secondary[p]
            need(all(d[a] == d[b] for d in (graph.initial, graph.final)
                     for a, b in ((u, x), (v, y))), f"absolute secondary port boundary {p}")
            endpoints[y][x] = Fraction(1)
            endpoints[u][v] = Fraction(-1)
        else:
            endpoints[x][y] = Fraction(-1)
            endpoints[y] = {x: Fraction(1, 2), y: Fraction(1, 2)}
        ports[p] = group
    mains = {i for group in ports.values() for i in group}
    need(len(mains) == sum(map(len, ports.values())) == 400, "400 distinct main owners")
    return endpoints, mains


def rational_sum(terms):
    """One exact integer denominator per stored sparse forward row."""
    nonzero = [(row, q.numerator, denominator * q.denominator)
               for (denominator, row), q in terms if row]
    denominator = lcm(*(d for _, _, d in nonzero))
    numerators = defaultdict(int)
    for row, n, d in nonzero:
        multiplier = n * (denominator // d)
        for address, value in row.items():
            numerators[address] += multiplier * value
    result = {k: v for k, v in numerators.items() if v}
    common = gcd(denominator, *result.values())
    return denominator // common, {k: v // common for k, v in result.items()}


def unpack(row):
    denominator, values = row
    return {k: Fraction(v, denominator) for k, v in values.items()}


def forward(graph, watch=()):
    rows = {~i: (1, {i: 1}) for i in range(graph.size)}
    outputs = [None] * graph.size
    for node in graph.order:
        row = rational_sum((rows[donor], q) for donor, q in graph.forms[node])
        if node in graph.moves:
            rows[node] = row
        else:
            outputs[node - graph.first] = unpack(row)
    return outputs, {key: unpack(rows[key]) for key in watch}


def adjoint(graph, watch=()):
    """Pull each terminal covector backward through the literal directed tape."""
    pending = {node: [((1, {i: 1}), Fraction(1))] for i, node in enumerate(graph.terminals)}
    watched = {}
    for node in reversed(graph.order):
        influence = rational_sum(pending.pop(node, ()))
        if node in watch:
            watched[node] = unpack(influence)
        if influence[1]:
            for donor, coefficient in graph.forms[node]:
                pending.setdefault(donor, []).append((influence, coefficient))
    return [unpack(rational_sum(pending.pop(~i, ()))) for i in range(graph.size)], watched


def transpose(rows):
    columns = [{} for _ in rows]
    for output, row in enumerate(rows):
        for donor, coefficient in row.items():
            columns[donor][output] = coefficient
    return columns


def row_digest(rows):
    return digest([[[j, str(v)] for j, v in sorted(row.items())] for row in rows])


def ranks(graph, mains, spans):
    paid, productive = Counter(), Counter()
    for source, destination in graph.moves.values():
        need(spans[source] < spans[destination] or spans[destination] < spans[source],
             "every paid route has strictly nested charts")
        paid[abs(len(graph.frames[source]) - len(graph.frames[destination]))] += 1
    for owner, (source, destination) in enumerate(zip(graph.initial, graph.final, strict=True)):
        if owner not in mains:
            need(spans[source] < spans[destination], "every productive helper is a strict positive owner return")
            productive[len(graph.frames[destination]) - len(graph.frames[source])] += 1
    return paid, productive


def public_boundaries(base, base_layout, candidate, layout, mains, spans):
    need(candidate.size > base.size and candidate.first == base.first, "new owners use the original terminal namespace")
    need(layout["source_labels"][:base.size] == base_layout["source_labels"], "all original public labels retained")
    changed = {}
    for owner in range(base.size):
        a, b = base.initial[owner], base.final[owner]
        x, y = candidate.initial[owner], candidate.final[owner]
        if (a, b) != (x, y):
            need(owner not in mains and ((x == a) != (y == b)), "exactly one changed endpoint on an original helper")
            center = y if x == a else x
            need(spans[a] < spans[center] < spans[b], "strictly interior original retirement/entrance")
            daughter = (center, b) if x == a else (a, center)
            changed[owner] = (a, b), (x, y), daughter
    remaining = set(range(base.size, candidate.size))
    need(len(remaining) == len(changed), "one fresh helper per split original")
    records = []
    for owner, (old, kept, expected) in changed.items():
        candidates = [i for i in sorted(remaining) if (candidate.initial[i], candidate.final[i]) == expected]
        need(bool(candidates), "complementary new independent owner charts")
        fresh = candidates[0]
        remaining.remove(fresh)
        records.append({
            "original_address": owner,
            "original_label": layout["source_labels"][owner],
            "fresh_address": fresh,
            "fresh_label": layout["source_labels"][fresh],
            "old_charts": old,
            "original_charts": kept,
            "fresh_charts": expected,
            "matching_chart_pairs_remaining": len(candidates),
            "ranks": [len(base.frames[b]) - len(base.frames[a]) for a, b in (old, kept, expected)],
        })
    return records


def paid_boundaries(base, candidate, spans, productive_interiors):
    unmatched = set(candidate.moves) - set(base.moves)
    changed = [k for k, charts in base.moves.items() if k in candidate.moves and candidate.moves[k] != charts]
    records = []
    remaining_interiors = productive_interiors.copy()
    for key in sorted(changed):
        a, b = base.moves[key]
        x, y = candidate.moves[key]
        if (x == a) == (y == b):
            continue
        middle = y if x == a else x
        if not ((spans[a] < spans[middle] < spans[b]) or (spans[b] < spans[middle] < spans[a])):
            continue
        if not remaining_interiors[middle]:
            continue
        other = (middle, b) if x == a else (a, middle)
        matches = [k for k in sorted(unmatched) if candidate.moves[k] == other]
        if not matches:
            continue
        new = matches[0]
        unmatched.remove(new)
        remaining_interiors[middle] -= 1
        records.append({"old_paid_key": key, "new_paid_key": new, "old_charts": (a, b),
                        "retained_leg_charts": (x, y), "new_leg_charts": other,
                        "interior_chart": middle, "matching_chart_pairs_remaining": len(matches),
                        "ranks": [abs(len(base.frames[i]) - len(base.frames[j]))
                                  for i, j in ((a, b), (x, y), other)]})
    need(not +remaining_interiors, "all productive birth interiors carry a paid subdivision")
    retimed = set(changed) - {r["old_paid_key"] for r in records}
    return records, {
        "other_retired_keys": {k: base.moves[k] for k in sorted(base.moves.keys() - candidate.moves.keys())},
        "other_new_keys": {k: candidate.moves[k] for k in sorted(unmatched)},
        "other_recharted_keys": {k: [base.moves[k], candidate.moves[k]] for k in sorted(retimed)},
        "same_chart_changed_form_keys": [k for k in sorted(base.moves.keys() & candidate.moves.keys())
                                         if k not in changed and base.forms[k] != candidate.forms[k]],
    }


def reject(operation, reason):
    try:
        operation()
    except ValueError as error:
        need(str(error).startswith(reason), f"control rejected for wrong reason: {error}")
    else:
        raise ValueError(f"counterfactual accepted: {reason}")


def fault_paid(candidate, records, other_paid, expected, inputs, outputs):
    """A one-node sign change has exact endpoint difference -2*output*input."""
    split = {key for r in records for key in (r["new_paid_key"], r["old_paid_key"])}
    other_new = set(other_paid["other_new_keys"])
    faults, zero_impulse = [], []
    for key in sorted(inputs):
        input_row, output_column = inputs[key], outputs[key]
        if not input_row or not output_column:
            need(key not in split | other_new, "the new or subdivided paid leg has an observable public pulse")
            zero_impulse.append(key)
            continue
        source, terminal = min(input_row), min(output_column)
        old = expected[terminal].get(source, 0)
        delta = -2 * output_column[terminal] * input_row[source]
        need(delta, "nonzero exact paid sign defect")
        faults.append({"paid_key": key, "first_changed_terminal": terminal, "source_address": source,
                       "original_coefficient": str(old), "faulty_coefficient": str(old + delta),
                       "paid_input_coefficient": str(input_row[source]),
                       "terminal_pulse_coefficient": str(output_column[terminal])})
    direct = []
    for key in [records[0]["new_paid_key"], *sorted(other_new)]:
        replaced = tuple((donor, -coefficient) for donor, coefficient in candidate.forms[key])
        faulty = replace(candidate, forms={**candidate.forms, key: replaced})
        faulty.validate_causality()
        actual, _ = forward(faulty)
        actual_t, _ = adjoint(faulty)
        predicted = [row.copy() for row in expected]
        for terminal, influence in outputs[key].items():
            for source, coefficient in inputs[key].items():
                row = predicted[terminal]
                value = row.get(source, 0) - 2 * influence * coefficient
                if value:
                    row[source] = value
                else:
                    row.pop(source, None)
        need(actual == predicted and actual != expected and actual_t == transpose(predicted),
             "actual mutated forward and adjoint match the exact signed pulse")
        direct.append({"paid_key": key, "mutated_forward_sha256": row_digest(actual),
                       "mutated_adjoint_sha256": row_digest(actual_t)})
    return {"nonzero_rank_one_witnesses": faults,
            "recharted_paid_keys_with_zero_public_impulse": zero_impulse,
            "all_rows_directly_replayed_after_sign_mutations": direct}


def fault_free(candidate, records, expected):
    """Remove the observed original return, the fresh return, and its input pulse."""
    cases = []
    for event in records:
        original, fresh = event["original_address"], event["fresh_address"]
        for operation in ("original_projection", "fresh_projection", "fresh_input_pulse"):
            erased = original if operation == "original_projection" else fresh
            if operation == "fresh_input_pulse":
                updates = {
                    key: tuple((donor, coefficient) for donor, coefficient in form if donor != ~fresh)
                    for key, form in candidate.forms.items()
                    if any(donor == ~fresh for donor, _ in form)
                }
                need(updates, "literal independent fresh input pulse is present")
            else:
                updates = {candidate.first + erased: ()}
            faulty = replace(candidate, forms={**candidate.forms, **updates})
            faulty.validate_causality()
            claimed = expected.copy()
            claimed[erased] = {}
            rows, _ = forward(faulty)
            columns, _ = adjoint(faulty)
            need(expected[erased] == {erased: 1} and rows == claimed and columns == transpose(claimed),
                 f"removing {operation} erases exactly one independent unit terminal")
            cases.append({"operation": operation, "changed_form_keys": sorted(updates),
                          "source_address": erased, "terminal_address": erased,
                          "normal_coefficient": "1", "mutated_coefficient": "0",
                          "mutated_forward_sha256": row_digest(rows),
                          "mutated_adjoint_sha256": row_digest(columns)})
    return cases


def free_parent(args, candidate, records):
    if not records:
        need(not args.free_parent and not args.free_parent_sha, "a free-parent pin needs a declared free split")
        return None, None
    need(args.free_parent and args.free_parent_sha, "supply exact predecessor for a productive-only split")
    payload, pin = read(args.free_parent, args.free_parent_sha)
    earlier = Graph.parse(payload)
    originals = {r["original_address"]: r for r in records}
    fresh = {r["fresh_address"] for r in records}
    need(earlier.frames == candidate.frames and earlier.first == candidate.first
         and fresh == set(range(earlier.size, candidate.size)), "all and only declared free helpers appended")
    for i in range(earlier.size):
        prior = earlier.initial[i], earlier.final[i]
        if i in originals:
            need(prior == originals[i]["old_charts"], "the final split shortens this exact predecessor owner")
        else:
            need(prior == (candidate.initial[i], candidate.final[i]), "every other predecessor boundary preserved")
    need(earlier.moves == candidate.moves, "literal paid chart keys and endpoints preserved across free split")
    result = {
        "predecessor": pin,
        "common_paid_moves_sha256": digest([[key, *earlier.moves[key]] for key in sorted(earlier.moves)]),
        "common_paid_move_count": len(earlier.moves),
        "literal_paid_delta": {},
        "literal_coefficient_count_delta":
            sum(map(len, candidate.forms.values())) - sum(map(len, earlier.forms.values())),
        "owners": records,
    }
    return earlier, result


@dataclass(frozen=True)
class Held:
    owner: int | None
    chart: int | None
    values: tuple


EMPTY = Held(None, None, (0,) * COMPONENTS)


class GuardedBank:
    def __init__(self, distinct_homes):
        self.slots = {k: EMPTY for k in distinct_homes}
        self.count = 0
        self.guard = (object(), object())

    def load(self, key, owner, chart):
        state = self.slots[key]
        need((state.owner, state.chart) == (owner, chart), "held source owner and chart")
        return state.values

    def install(self, key, item):
        need(self.slots[key] == EMPTY, "install in occupied or dirty home")
        self.slots[key] = item

    def clear(self, key, cells=COMPONENTS):
        old = self.slots[key].values
        self.slots[key] = Held(None, None, (0,) * cells + old[cells:])
        self.count += cells


def held_control(graph, expected, subdivisions, other_paid):
    """Exercise preserved source values, a live split sender, and exact clearing."""
    source_keys = {~i for i in range(graph.size)}
    bank = GuardedBank(source_keys | set(graph.order) | {"sender"})
    guards = bank.guard
    samples = {
        ~i: tuple((-1) ** (i + j) * (31 * i + 7 * j + 1) for j in range(COMPONENTS))
        for i in range(graph.size)
    }
    for key, value in samples.items():
        bank.install(key, Held(key, graph.initial[~key], value))
    partial, alias = [], []
    new_keys = {record["new_paid_key"] for record in subdivisions} | set(other_paid["other_new_keys"])
    for node in graph.order:
        chart = graph.source_chart(node)
        addends = [(coefficient, bank.load(donor, donor, chart))
                   for donor, coefficient in graph.forms[node]]
        cells = tuple(sum(coefficient * values[j] for coefficient, values in addends)
                      for j in range(COMPONENTS))
        if node in graph.moves:
            bank.install("sender", Held(node, chart, cells))
            returned = bank.load("sender", node, chart)
            if node in new_keys:
                reject(lambda: bank.install("sender", Held(-1, chart, cells)), "install in occupied or dirty home")
                alias.append(node)
                if cells[-1]:
                    bank.clear("sender", COMPONENTS - 1)
                    reject(lambda: bank.install("sender", Held(node, chart, cells)),
                           "install in occupied or dirty home")
                    partial.append(node)
            bank.install(node, Held(node, graph.moves[node][1], returned))
            bank.clear("sender")
        else:
            bank.install(node, Held(node, chart, cells))
    need(all(bank.load(k, k, graph.initial[~k]) == v for k, v in samples.items()),
         "old and added independent inputs preserved until public return")
    for i, row in enumerate(expected):
        want = tuple(sum(coefficient * samples[~j][k] for j, coefficient in row.items())
                     for k in range(COMPONENTS))
        staged = bank.load(graph.first + i, graph.first + i, graph.final[i])
        bank.clear(~i)
        bank.install(~i, Held(~i, graph.final[i], staged))
        need(bank.load(~i, ~i, graph.final[i]) == want,
             f"install the same independent public owner {i} in the declared terminal chart")
    for key in bank.slots:
        bank.clear(key)
    need(bank.guard is guards and all(item == EMPTY for item in bank.slots.values()),
         "complete addressed clearing and guard preservation")
    need(alias and partial, "live-candidate dirty-tail and occupied sender controls")
    return {"scope": "normalized rational held-home fixture, four independent components",
            "homes": len(bank.slots), "addressed_cells_cleared": bank.count,
            "same_owner_returns": graph.size, "guards_preserved": True,
            "occupied_sender_rejected_at": alias, "partially_cleared_sender_rejected_at": partial}


def signed_caller(supplier, graph, layout):
    source = supplier / "complex"
    retained = source / "retained"
    sys.path[:0] = [str(source), str(retained), str(retained / "vendor")]
    from closed_application import readback
    from closed_caller import placement, templates
    from mixed_caller import layout_bindings
    from mixed_grid import census, exact

    caller_data = (retained / "data/CALLER.json.gz").read_bytes()
    mixed_data = (retained / "data/CONJUGATE-CALLER.json.gz").read_bytes()
    need(sha256(caller_data).hexdigest() == HOMOGENEOUS and sha256(mixed_data).hexdigest() == MIXED,
         "pinned canonical caller inputs")
    caller = json.loads(gzip.decompress(caller_data))
    words = templates(caller)
    roots = placement(caller)
    bindings, offsets, census_record = layout_bindings(words, roots, layout, NATIVE_CALLS)
    need(census_record["template_roots"] == {"A": 120, "rotated": 192} and
         census_record["stage_helper_owners"] == NATIVE_CALLS * (graph.size - 400),
         "all independent main roots and every new per-call helper included")
    tape = readback(words, roots, bindings, offsets)
    need(tape["event_stream_sha256"] == PUBLIC_STREAM and tape["events"] == 840912,
         "independent native helper births preserve the signed caller word")
    paid, productive, grids = Counter(), Counter(), {}
    for kind, (events, targets) in words.items():
        grams = exact(events, targets, 2025 << 9)
        grids[kind] = grams
        t, p, *_ = census(events, targets)
        count = census_record["template_roots"][kind]
        paid.update({rank: count * n for rank, n in p.items()})
        productive.update({rank: count * n for rank, n in t.items()})
    return paid, productive, {"finite_binding": census_record, "readback": tape,
                              "exact_local_operators": grids}


def invoice(graph_ranks, closed_ranks):
    return tuple(Counter({rank: NATIVE_CALLS * n for rank, n in native.items()}) + caller
                 for native, caller in zip(graph_ranks, closed_ranks, strict=True))


def interval(paid, productive, bounds, kappa=TARGET):
    lower = upper = Fraction(0)
    exponent = 1 - Fraction(kappa)
    for rank in sorted(paid.keys() | productive.keys()):
        n = productive[rank] - paid[rank]
        a, b = bounds(rank, exponent, 256)
        lower += n * (a if n >= 0 else b)
        upper += n * (b if n >= 0 else a)
    return lower, upper


def decimal_bounds(values):
    out = []
    for value, rounding in zip(values, (ROUND_FLOOR, ROUND_CEILING), strict=True):
        with localcontext() as ctx:
            ctx.prec = 58
            ctx.rounding = rounding
            out.append(str(Decimal(value.numerator) / Decimal(value.denominator)))
    return out


def overview(graph, ids, rows, columns, own_ranks):
    paid, productive = own_ranks
    return {**ids, "public": graph.size, "main": 400, "helpers": graph.size - 400,
            "forms": len(graph.forms), "paid_moves": len(graph.moves),
            "rational_literals": sum(map(len, graph.forms.values())),
            "forward_rows": len(rows), "adjoint_rows": len(columns),
            "forward_sha256": row_digest(rows), "adjoint_sha256": row_digest(columns),
            "native_paid": dict(paid), "native_productive": dict(productive)}


def verify(args):
    base_data, base_id = read(args.base_graph, BASE_NATIVE)
    base_layout, base_layout_id = read(args.base_layout, BASE_LAYOUT)
    new_data, new_id = read(args.candidate, args.sha)
    new_layout, layout_id = read(args.layout, args.layout_sha)
    base, candidate = Graph.parse(base_data), Graph.parse(new_data)
    need(base.size == 1264 and len(base.moves) == 5701, "literal #7776 graph census")
    need(base.frames == candidate.frames and all(base_layout[k] == new_layout[k] for k in ("ports", "live", "hosted")),
         "all original charts, port addresses and native coefficients")
    spans = [span(frame) for frame in base.frames]
    expected_base, base_main = public_operator(base, base_layout, spans)
    expected, mains = public_operator(candidate, new_layout, spans)
    need(base_main == mains and expected[:base.size] == expected_base and
         all(row == {i: 1} for i, row in enumerate(expected[base.size:], start=base.size)),
         "all original operator rows and one fresh independent unit row per added owner")
    changed_owners = public_boundaries(base, base_layout, candidate, new_layout, mains, spans)
    declared_free = set(args.free_split)
    free_records = [r for r in changed_owners if (r["original_address"], r["fresh_address"]) in declared_free]
    need(len(free_records) == len(declared_free), "every declared free split pairs the exact original and fresh address")
    paid_births = [r for r in changed_owners if r not in free_records]
    interiors = Counter(next(c for c in r["original_charts"] if c not in r["old_charts"]) for r in paid_births)
    changed_paid, other_paid = paid_boundaries(base, candidate, spans, interiors)
    need(len(paid_births) == len(changed_paid) > 0, "complete paid and productive subdivision counts")
    need(Counter(r["interior_chart"] for r in changed_paid) == interiors,
         "every paid interior chart supports a productive birth")
    earlier, free_result = free_parent(args, candidate, free_records)
    print("Checking all exact rational public rows and independent adjoints.", flush=True)
    old_rows, _ = forward(base)
    old_cols, _ = adjoint(base)
    watch = ({key for record in changed_paid for key in (record["new_paid_key"], record["old_paid_key"])}
             | set(other_paid["other_new_keys"]) | set(other_paid["other_recharted_keys"]))
    rows, inputs = forward(candidate, watch)
    columns, outputs = adjoint(candidate, watch)
    expected_t = transpose(expected)
    need(old_rows == expected_base and old_cols == transpose(expected_base), "pinned source orientations")
    need(rows == expected and columns == expected_t, "complete independent candidate orientations")
    need([dict((j, q) for j, q in col.items() if j < base.size) for col in columns[:base.size]] == old_cols and
         all(columns[i] == {i: 1} for i in range(base.size, candidate.size)),
         "no arbitrary fresh input perturbs an original terminal")
    print("Checking subdivided paid signs, address aliasing, and live partial CLEAR.", flush=True)
    faulty_layout = {**new_layout, "source_labels": new_layout["source_labels"].copy()}
    first = changed_owners[0]
    faulty_layout["source_labels"][first["fresh_address"]] = first["original_label"]
    reject(lambda: public_operator(candidate, faulty_layout, spans), "duplicate public owner label")
    faults = fault_paid(candidate, changed_paid, other_paid, expected, inputs, outputs)
    held = held_control(candidate, expected, changed_paid, other_paid)
    if free_records:
        print("Checking the free retirement, fresh terminal projection, and independent input pulse.", flush=True)
        free_result["removal_controls"] = fault_free(candidate, free_records, expected)
    base_ranks = ranks(base, mains, spans)
    new_ranks = ranks(candidate, mains, spans)
    print("Checking the 48-call signed caller and directed recursive price.", flush=True)
    caller_paid, caller_productive, caller = signed_caller(args.supplier.resolve(), candidate, new_layout)
    paid0, target0 = invoice(base_ranks, (caller_paid, caller_productive))
    paid1, target1 = invoice(new_ranks, (caller_paid, caller_productive))
    scripts = args.upstream.resolve() / "scripts"
    need(sha256((scripts / "evaluate_recursive_power.py").read_bytes()).hexdigest() == ORACLE,
         "pinned directed power checker")
    sys.path.insert(0, str(scripts))
    from evaluate_recursive_power import power_bounds
    original = interval(paid0, target0, power_bounds)
    updated = interval(paid1, target1, power_bounds)
    credit = updated[0] - original[1], updated[1] - original[0]
    if free_records:
        paid_earlier, target_earlier = invoice(ranks(earlier, mains, spans), (caller_paid, caller_productive))
        need(paid_earlier == paid1, "free target split has zero complete paid rank delta")
        delta = Counter()
        for event in free_records:
            old, first, second = event["ranks"]
            delta[old] -= NATIVE_CALLS
            delta[first] += NATIVE_CALLS
            delta[second] += NATIVE_CALLS
        observed = {r: target1[r] - target_earlier[r] for r in target1.keys() | target_earlier.keys()
                    if target1[r] != target_earlier[r]}
        need(observed == {r: amount for r, amount in delta.items() if amount},
             "the only productive change is both exact daughters against their retired original target")
        a, b = interval(paid_earlier, target_earlier, power_bounds)
        free_result["full_signed_credit"] = decimal_bounds((updated[0] - b, updated[1] - a))
        free_result["complete_target_delta"] = {r: n for r, n in delta.items() if n}
        need(updated[0] - b > 0, "directed positive paid-null productive split")
    need(original[1] < 0 < updated[0], "full candidate signed invoice clears the target")
    return {
        "schema": "p104-subdivided-independent-rational-replay/v1",
        "checker_sha256": CHECKER_SHA256,
        "target": TARGET,
        "base": overview(base, base_id, old_rows, old_cols, base_ranks),
        "candidate": overview(candidate, new_id, rows, columns, new_ranks),
        "base_layout": base_layout_id,
        "candidate_layout": layout_id,
        "original_and_fresh_owners": changed_owners,
        "paid_subdivisions": changed_paid,
        "free_productive_subdivision": free_result,
        "other_paid_changes": other_paid,
        "held_owner_clear": held,
        "fault_controls": {"occupied_public_owner_label_rejected": True, "changed_paid_signs": faults},
        "closed_caller": {**caller, "fixed_paid": dict(caller_paid), "fixed_targets": dict(caller_productive)},
        "full_invoice": {"base": {"paid": dict(paid0), "targets": dict(target0)},
                         "candidate": {"paid": dict(paid1), "targets": dict(target1)},
                         "paid_delta": {r: paid1[r] - paid0[r] for r in sorted(paid0.keys() | paid1.keys())
                                        if paid1[r] != paid0[r]},
                         "target_delta": {r: target1[r] - target0[r] for r in sorted(target0.keys() | target1.keys())
                                          if target1[r] != target0[r]},
                         "base_margin": decimal_bounds(original), "candidate_margin": decimal_bounds(updated),
                         "additional_candidate_margins": {
                             k: decimal_bounds(interval(paid1, target1, power_bounds, k))
                             for k in (COMPARATOR_PLUS_GAIN, ADMITTED_BINARY)
                         },
                         "saving": decimal_bounds(credit)},
    }


def main():
    def free_pair(value):
        try:
            a, b = map(int, value.split(":"))
        except ValueError as error:
            raise argparse.ArgumentTypeError("use original-address:fresh-address") from error
        if not 0 <= a < b:
            raise argparse.ArgumentTypeError("the fresh address follows the original address")
        return a, b

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-graph", "base-layout", "candidate", "layout", "supplier", "upstream", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--layout-sha", required=True)
    parser.add_argument("--free-split", type=free_pair, action="append", default=[])
    parser.add_argument("--free-parent", type=Path)
    parser.add_argument("--free-parent-sha")
    args = parser.parse_args()
    report = verify(args)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("Independent signed margin:", *report["full_invoice"]["candidate_margin"], flush=True)


if __name__ == "__main__":
    main()

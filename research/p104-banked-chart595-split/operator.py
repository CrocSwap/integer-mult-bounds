#!/usr/bin/env python3
"""Independently replay the two complete normalized chart-595 operators."""

from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_HEAD = "1b4a4d6f9370b8c93b3f769a6229a9111ef3940e"
PARENT_SHA = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CANDIDATE_SHA = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
EDIT_SHA = "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf"
PORTS_SHA = "622c6f458eba2dab0fdfd6050303cbc16ad684ab8b834c7df568264e4cf01db6"
PIVOTS_SHA = "fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85"
UNIT = Fraction(1)
EMPTY = (1, {})
OLD_ROLE = 281
FRESH = 1501
A, C, B = 3, 595, 127


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_pinned(path, digest, packed=False):
    raw = path.read_bytes()
    data = gzip.decompress(raw) if packed else raw
    require(sha256(data).hexdigest() == digest, f"exact input bytes for {path.name}")
    result = json.loads(data)
    if packed:
        require(canonical(result) == data, f"canonical graph serialization for {path.name}")
    return result


@cache
def scalar(text):
    result = Fraction(text)
    require(bool(result) and str(result) == text, "nonzero canonical rational coefficient")
    return result


def parsed_terms(entries):
    terms = {token: scalar(q) for token, q in entries}
    require(len(terms) == len(entries) and all(type(token) is int for token in terms), "unique typed coefficient keys")
    return terms


@dataclass(frozen=True)
class Graph:
    frames: list
    initial: list
    final: list
    start: int
    moves: dict
    forms: dict
    order: list
    metadata: dict

    @property
    def width(self):
        return len(self.initial)

    @property
    def terminals(self):
        return range(self.start, self.start + self.width)


def graph_from(raw, size):
    moves = {key: (source, target) for key, source, target in raw["moves"]}
    forms = {key: parsed_terms(row) for key, row in raw["forms"]}
    require(len(moves) == len(raw["moves"]) == 6142, "complete unique paid MOVE inventory")
    require(len(forms) == len(raw["forms"]) == 6142 + size, "complete unique saved and terminal inventory")
    require(raw["first_output"] == 150522 and len(raw["initial"]) == len(raw["final"]) == size,
            "explicit stable terminal namespace and public role denominator")
    graph = Graph(raw["frames"], raw["initial"], raw["final"], raw["first_output"], moves, forms,
                  raw["schedule"], raw["metadata"])
    schedule(graph)
    return graph


def schedule(graph):
    terminals = set(graph.terminals)
    require(not terminals & graph.moves.keys() and set(graph.forms) == terminals | graph.moves.keys(),
            "explicit complete terminal inventory")
    require(len(graph.order) == len(graph.forms) and set(graph.order) == set(graph.forms),
            "each paid and terminal row is scheduled once")
    available = {~role: chart for role, chart in enumerate(graph.initial)}
    require(len(graph.frames) == 1097 and all(type(chart) is int and 0 <= chart < len(graph.frames)
                                               for chart in [*graph.initial, *graph.final]), "typed public chart endpoints")
    for key in graph.order:
        if key in graph.moves:
            source, target = graph.moves[key]
            require(0 <= source < len(graph.frames) and 0 <= target < len(graph.frames), "typed paid chart endpoints")
        else:
            source = graph.final[key - graph.start]
        for token in graph.forms[key]:
            require(token in available, f"early, absent or terminal donor at stable key {key}")
            require(available[token] == source, f"noncoframed donor at stable key {key}")
        if key in graph.moves:
            available[key] = target
    require(len(available) == graph.width + len(graph.moves), "distinct preserved snapshots and public origins")
    return available


def coordinate(i):
    return 1, {i: 1}


def linear(terms):
    """Return an exact sparse row with its own reduced common denominator."""
    active = [(q, denominator, values) for q, (denominator, values) in terms if q and values]
    denominator = lcm(*(q.denominator * d for q, d, _ in active))
    result = {}
    for coefficient, divisor, vector in active:
        multiplier = coefficient.numerator * (denominator // (divisor * coefficient.denominator))
        for i, basis_coefficient in vector.items():
            result[i] = result.get(i, 0) + multiplier * basis_coefficient
    result = {i: value for i, value in result.items() if value}
    content = gcd(denominator, *result.values())
    return denominator // content, {i: value // content for i, value in result.items()}


def weighted(terms, rows):
    return linear((q, rows[token]) for token, q in terms.items())


def numerator_items(row):
    denominator, values = row
    return ((i, Fraction(value, denominator)) for i, value in values.items())


def forward(graph):
    rows = {~role: coordinate(role) for role in range(graph.width)}
    products = 0
    for token in graph.order:
        terms = graph.forms[token]
        products += sum(len(rows[donor][1]) for donor in terms)
        rows[token] = weighted(terms, rows)
    return rows, products


def reverse_columns(graph):
    """Propagate unit output labels along reversed scalar incidences."""
    downstream = defaultdict(list)
    for consumer, terms in graph.forms.items():
        for donor, q in terms.items():
            downstream[donor].append((consumer, q))
    columns = {token: coordinate(i) for i, token in enumerate(graph.terminals)}
    products = 0
    reverse_order = [token for token in reversed(graph.order) if token in graph.moves]
    reverse_order.extend(~role for role in range(graph.width))
    for token in reverse_order:
        terms = downstream[token]
        products += sum(len(columns[consumer][1]) for consumer, _ in terms)
        columns[token] = linear((q, columns[consumer]) for consumer, q in terms)
    return [columns[~i] for i in range(graph.width)], products


def transpose_rows(rows):
    columns = [[] for _ in rows]
    for i, row in enumerate(rows):
        for j, value in numerator_items(row):
            columns[j].append((value, coordinate(i)))
    return [linear(column) for column in columns]


def reference_ports(layout):
    require(layout["public"] == 1501 and len(layout["live"]) == len(layout["ports"]) == 104,
            "all original P104 boundary ports")
    hosted = layout["hosted"]
    a_ports = set(hosted["Dports"])
    require(len(a_ports) == len(hosted["X2"]) == len(hosted["Y2"]) == 96, "96 paired A and eight B ports")
    rows = [coordinate(role) for role in range(layout["public"])]
    mains = set()
    for port, x in enumerate(layout["live"]):
        y = x + 112
        mains.update((x, y))
        if port in a_ports:
            rows[y] = 1, {x: 1, y: 1}
        else:
            rows[x] = 1, {x: 1, y: -1}
            rows[y] = 2, {x: 1, y: 1}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        rows[x] = 1, {x: 1, y: -1}
        mains.update((x, y))
    require(len(mains) == 400, "all distinct original main input/output roles")
    return rows, mains


def checked_endpoints(graph, rows, expected):
    require(len(expected) == graph.width, "one separate independent target for each public input")
    for i, key in enumerate(graph.terminals):
        require(rows[key] == expected[i], f"normalized external row {i}")


def impulse_response(graph, injections):
    """Evaluate the baseline graph on zero inputs with a unit correction parameter."""
    result = {}
    for token in graph.order:
        response = injections.get(token, 0)
        for donor, q in graph.forms[token].items():
            if donor in result:
                response += q * result[donor]
        if response:
            result[token] = response
    return result


def codec(group, functional, direction):
    require(OLD_ROLE in group and functional.keys() <= group and direction.keys() <= group,
            "both exact codec factors live in the retained 615-field block")
    require(sum((q * direction.get(i, 0) for i, q in functional.items()), Fraction()) == 1,
            "exact normalized pairing between the prefix and suffix")
    pivot = functional[OLD_ROLE]
    encoder = {i: coordinate(i) for i in range(FRESH)}
    encoder[OLD_ROLE] = linear([(-q / pivot, coordinate(i)) for i, q in functional.items() if i != OLD_ROLE]
                               + [(direction.get(OLD_ROLE, 0), coordinate(OLD_ROLE))])
    for i in group - {OLD_ROLE}:
        encoder[i] = linear(((UNIT, coordinate(i)), (direction.get(i, 0), coordinate(OLD_ROLE))))
    require(weighted(functional, encoder) == coordinate(OLD_ROLE), "group encoder recovers arbitrary first coordinate")
    for i in group - {OLD_ROLE}:
        retained = linear(((UNIT, encoder[i]), (-direction.get(i, 0), coordinate(OLD_ROLE))))
        require(retained == coordinate(i), f"group encoder does not consume retained owner {i}")
    return encoder


def composition(row, encoder, response):
    terms = [(q, encoder[i]) for i, q in numerator_items(row)]
    if response:
        terms.append((response, (1, {OLD_ROLE: -1, FRESH: 1})))
    return linear(terms)


def add_coefficient(form, donor, coefficient):
    coefficient += form.get(donor, 0)
    if coefficient:
        form[donor] = coefficient
    else:
        form.pop(donor, None)


def check_literal_paid_forms(parent, child, encoded, prefix, suffix):
    borrowed_inputs = {~i: {~j: q for j, q in numerator_items(row)} for i, row in encoded.items()}
    rewritten = []
    for key in parent.moves:
        old = parent.forms[key]
        form = {}
        for donor, q in old.items():
            if donor < 0:
                for replacement, factor in borrowed_inputs[donor].items():
                    add_coefficient(form, replacement, q * factor)
            else:
                add_coefficient(form, donor, q)
        if form != old:
            rewritten.append(key)
        pulse = suffix.get(key)
        if pulse:
            add_coefficient(form, ~FRESH, pulse)
            for node, q in prefix.items():
                add_coefficient(form, node, -pulse * q)
        require(form == child.forms[key], f"literal paid row equals codec plus specified departure pulse at {key}")
    require(len(rewritten) == 340 and not set(rewritten) & suffix.keys(), "full disjoint 340 ingress and ten departure rows")
    return len(rewritten)


def check_pivot_observations(pivots, parent, child, old_rows, new_rows, encoded, response):
    require(len(pivots) == 15 and sum(row["direction"] == "forward" for row in pivots) == 7,
            "all seven forward and eight transposed published pivot scopes")
    result = []
    for index, record in enumerate(pivots):
        groups = {name: parsed_terms(record[name]) for name in ("sender", "receiver", "combination")}
        groups["lead"] = {record["pivot"]: UNIT}
        groups["drop"] = {record["remove"]: UNIT}
        presences = {}
        for name, terms in groups.items():
            old_terms, new_terms = [], []
            live, retired, inputs = 0, 0, 0
            for token, q in terms.items():
                if token < 0:
                    require(record["direction"] == "forward" and ~token in encoded,
                            "public donor is named in the original forward ingress coordinates")
                    reference = encoded[~token]
                    # A virtual old input is the literal coframe encoder on the current
                    # physical inputs, never the independent fresh chart-595 field.
                    actual = linear((c, new_rows[~j]) for j, c in numerator_items(reference))
                    inputs += 1
                elif token in parent.moves:
                    require(token in child.moves and not response.get(token),
                            f"prior observed token unchanged by the suffix at witness {index}, key {token}")
                    reference = composition(old_rows[token], encoded, 0)
                    actual = new_rows[token]
                    live += 1
                else:
                    require(token not in child.forms, f"previously removed observation still absent at key {token}")
                    retired += 1
                    continue
                require(actual == reference and FRESH not in actual[1],
                        f"observed codec pullback independent of fresh input at pivot {index}, {name}, {token}")
                old_terms.append((q, reference))
                new_terms.append((q, actual))
            require(linear(old_terms) == linear(new_terms), f"every still-observable term of pivot {index}, {name}")
            presences[name] = {"paid_observations": live, "encoded_public_input_observations": inputs, "previously_absent": retired}
        result.append({"pivot_index": index, "direction": record["direction"], "groups": presences})
    return result


def check_original_boundary_recovery(parent, child, grouping, functional, direction, encoded, parent_rows, child_rows):
    left = linear((q, coordinate(i)) for i, q in functional.items())
    old_input_bridge = {i: coordinate(i) for i in range(FRESH)}
    old_input_bridge[OLD_ROLE] = old_input_bridge[FRESH] = left
    for role in grouping - {OLD_ROLE}:
        old_input_bridge[role] = linear(((UNIT, coordinate(role)), (-direction.get(role, 0), left)))
    observable = {i: composition(child_rows[child.start + i], old_input_bridge, 0) for i in range(FRESH + 1)}
    require(observable[OLD_ROLE] == observable[FRESH] == left, "original coordinate is recovered at both old-chart projections")
    old_output_bridge = dict(observable)
    old_output_bridge[OLD_ROLE] = observable[FRESH]
    for role in range(FRESH):
        recovered = composition(encoded[role], old_output_bridge, 0) if role in grouping else observable[role]
        require(recovered == parent_rows[parent.start + role], f"original external map recovered at role {role}")
    return FRESH


def verify_split(parent, child, edit, baseline_rows, candidate_rows, mains, pivots):
    require(edit["source_head"] == SOURCE_HEAD and edit["source_graph_sha256"] == PARENT_SHA,
            "exact role split on the named parent")
    require(parent.frames == child.frames and parent.moves == child.moves, "every ordered frame and paid route is literally held")
    require([key for key in child.order if key in child.moves] == [key for key in parent.order if key in parent.moves],
            "every retained paid slot keeps its relative chronological position")
    require(edit["charts"] == [A, C, B] and edit["ranks"] == [1, 8], "declared two physical helper boundaries")
    require((edit["retired_role"], edit["fresh_role"]) == (OLD_ROLE, FRESH), "two named distinct productive roles")
    require(child.initial == [*parent.initial, C] and parent.final[OLD_ROLE] == B
            and child.final == [C if i == OLD_ROLE else chart for i, chart in enumerate(parent.final)] + [B],
            "only the old rank-nine boundary changes, with one independent entry and output at role 1501")
    require(len({~OLD_ROLE, ~FRESH, child.start + OLD_ROLE, child.start + FRESH}) == 4,
            "distinct old and fresh input and output tokens")
    group = set(edit["group_roles"])
    expected_group = {i for i, pair in enumerate(zip(parent.initial, parent.final, strict=True))
                      if pair == (A, B) and i not in mains}
    require(group == expected_group and len(group) == len(edit["group_roles"]) == 615,
            "complete independent original 3→127 helper block")
    helpers = edit["fixed_special_helpers"]
    require(helpers == [325, 1087] and not (set(helpers) & (group | mains)),
            "special helpers remain outside the split and main domains")
    require(all((child.initial[i], child.final[i]) == (3, 237) and candidate_rows[child.start + i] == coordinate(i)
                for i in helpers), "both protected special helpers retain exact same-owner operators")

    functional, direction = parsed_terms(edit["functional"]), parsed_terms(edit["return_direction"])
    prefix, suffix = parsed_terms(edit["prefix"]), parsed_terms(edit["injection"])
    require(len(prefix) == 8 and len(suffix) == 10, "complete literal prefix and departure witness")
    require(all(parent.moves[key][1] == C for key in prefix) and all(parent.moves[key][0] == C for key in suffix),
            "prefix arrivals and suffix departures are both in ordered chart 595")
    old_positions = {key: i for i, key in enumerate(parent.order)}
    prefix_end = max(old_positions[key] for key in prefix)
    suffix_start = min(old_positions[key] for key in suffix)
    require([prefix_end, suffix_start] == edit["reference_cut"] == [995, 1473], "exact published prefix and departure cut")
    child_positions = {key: i for i, key in enumerate(child.order)}
    close_prefix = max(child_positions[key] for key in prefix)
    require(child_positions[child.start + OLD_ROLE] == close_prefix + 1 < min(child_positions[key] for key in suffix),
            "retired-coordinate output is captured at the chart-595 cut before any injection")
    require(weighted(prefix, baseline_rows) == linear((q, coordinate(i)) for i, q in functional.items()),
            "eight literal arrivals recover the old arbitrary left functional")
    encoded = codec(group, functional, direction)
    response = impulse_response(parent, suffix)
    require(all(not response.get(key) for key in prefix), "ten departures have no feedback into prefix snapshots")
    require(all(response.get(parent.start + i, 0) == direction.get(i, 0) for i in range(FRESH)),
            "literal downstream response agrees at all 1,501 original exits")
    protected = set(edit["protected_slots"])
    require(len(protected) == 33 and not set(suffix) & protected and all(not response.get(key) for key in protected),
            "fixed prior pivot and role-230 slots remain uninjected and unaffected by suffix")
    require(all(key in parent.moves for key in protected if key in parent.forms), "retained protected slots are saved MOVE rows")
    require(all(key not in child.forms for key in protected if key not in parent.forms), "deleted prior pivot slots remain absent")
    for key in sorted(protected & parent.moves.keys()):
        require(candidate_rows[key] == composition(baseline_rows[key], encoded, 0)
                and FRESH not in candidate_rows[key][1], f"protected encoded observation independent of the fresh owner at {key}")
    require({key for key in protected & parent.moves.keys() if parent.forms[key] != child.forms[key]} == {94756, 97405},
            "both re-expressed protected leads change only under the input codec")
    ingress_count = check_literal_paid_forms(parent, child, encoded, prefix, suffix)
    prior_observations = check_pivot_observations(pivots, parent, child, baseline_rows, candidate_rows, encoded, response)

    for key in parent.moves:
        modeled = composition(baseline_rows[key], encoded, response.get(key, 0))
        require(candidate_rows[key] == modeled, f"composed exact paid row including all later reads at {key}")
    require(weighted(prefix, candidate_rows) == coordinate(OLD_ROLE)
            and candidate_rows[child.start + OLD_ROLE] == coordinate(OLD_ROLE), "old 281 returns only its own input at chart 595")
    recovered_b = {i: composition(baseline_rows[parent.start + i], encoded, response.get(parent.start + i, 0))
                   for i in group}
    require(weighted(functional, recovered_b) == coordinate(FRESH)
            and candidate_rows[child.start + FRESH] == coordinate(FRESH), "chart 127 independently recovers only fresh input 1501")
    for role in group - {OLD_ROLE}:
        row = linear(((UNIT, recovered_b[role]), (-direction.get(role, 0), coordinate(FRESH))))
        require(row == candidate_rows[child.start + role] == coordinate(role), f"later chart-127 owner restoration at {role}")
    recovered_original = check_original_boundary_recovery(parent, child, group, functional, direction,
                                                          encoded, baseline_rows, candidate_rows)
    return {
        "prefix_count": len(prefix), "departures_count": len(suffix), "parent_cut": [prefix_end, suffix_start],
        "protected_slots": len(protected), "retained_protected_slots": len(protected & parent.moves.keys()),
        "protected_codec_only_form_changes": [94756, 97405],
        "main_roles": len(mains), "fixed_special_helpers": helpers, "group_width": len(group),
        "retained_chart127_group_rows": len(group) - 1, "independent_split_roles": [OLD_ROLE, FRESH],
        "all_paid_rows_exact_model": len(parent.moves), "nonzero_suffix_response_rows": len(response),
        "paid_ingress_forms_checked": ingress_count, "original_boundary_recovered": recovered_original,
        "archived_pivot_observations": prior_observations,
    }


def controls(child, expected):
    slot = 93859
    mutated = child.forms.copy()
    row = child.forms[slot].copy()
    require(row[~FRESH].denominator == 7, "essential equal-price denominator-7 witness")
    row[~FRESH] = -row[~FRESH]
    mutated[slot] = row
    bad = replace(child, forms=mutated)
    schedule(bad)
    rows, _ = forward(bad)
    first_bad = next((i for i, key in enumerate(child.terminals) if rows[key] != expected[i]), None)
    require(first_bad is not None, "equal-price wrong injection must change a public normalized row")

    terminal = child.start + FRESH
    omitted = replace(child, forms={k: row for k, row in child.forms.items() if k != terminal},
                      order=[k for k in child.order if k != terminal])
    try:
        schedule(omitted)
    except ValueError as exc:
        require(str(exc) == "explicit complete terminal inventory", "missing target rejected at the actual boundary")
    else:
        raise ValueError("omitting the independently productive fresh target escaped the inventory check")
    return {"wrong_denominator_7_injection": {"slot": slot, "first_wrong_public_role": first_bad, "paid_routes_held": True},
            "omitted_new_target": {"terminal_key": terminal, "rejected_by": "explicit complete terminal inventory"}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE)
    args = parser.parse_args()
    data = args.root / "data"
    require(CANDIDATE_SHA is not None, "the literal changed graph must be frozen first")
    original = graph_from(read_pinned(data / "PARENT-GRAPH.json.gz", PARENT_SHA, packed=True), FRESH)
    candidate = graph_from(read_pinned(data / "CANDIDATE-GRAPH.json.gz", CANDIDATE_SHA, packed=True), FRESH + 1)
    edit = read_pinned(args.root / "EDIT.json", EDIT_SHA)
    ports = read_pinned(data / "CALLER-LAYOUT.json", PORTS_SHA)
    pivots = read_pinned(data / "PARENT-PIVOTS.json", PIVOTS_SHA)
    require(ports["source_word_sha256"] == original.metadata["source_word_sha256"], "explicit original port source")
    require(original.metadata["fixed_pivot_sha256"] == PIVOTS_SHA, "historical manifest bound to the parent graph")
    expected, mains = reference_ports(ports)
    expanded_expected = [*expected, coordinate(FRESH)]
    baseline_rows, baseline_products = forward(original)
    candidate_rows, candidate_products = forward(candidate)
    checked_endpoints(original, baseline_rows, expected)
    checked_endpoints(candidate, candidate_rows, expanded_expected)
    old_columns, old_reverse_count = reverse_columns(original)
    new_columns, new_reverse_count = reverse_columns(candidate)
    require(old_columns == transpose_rows(expected), "exact full original transposed operator")
    require(new_columns == transpose_rows(expanded_expected), "exact full transformed transposed operator")
    split = verify_split(original, candidate, edit, baseline_rows, candidate_rows, mains, pivots)
    result = {
        "status": "PASS_CHART595_EXACT_NORMALIZED_OPERATOR", "source_head": SOURCE_HEAD,
        "parent_graph_sha256": PARENT_SHA, "candidate_graph_sha256": CANDIDATE_SHA,
        "edit_sha256": EDIT_SHA, "port_layout_sha256": PORTS_SHA, "parent_pivots_sha256": PIVOTS_SHA,
        "operator_sizes": {"original": original.width, "candidate": candidate.width},
        "all_normalized_forward_and_adjoint_coefficients_exact": True,
        "original_forward_products": baseline_products, "candidate_forward_products": candidate_products,
        "original_adjoint_products": old_reverse_count, "candidate_adjoint_products": new_reverse_count,
        "literal_causal_codec_and_boundary": split, "controls": controls(candidate, expanded_expected),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

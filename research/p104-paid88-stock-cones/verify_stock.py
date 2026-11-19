#!/usr/bin/env python3
"""Replay the six named causal paid-pair exclusions against the pinned source archive."""

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
HEAD = "89a67c404226d51028e135de2b9169e9020d57af"
WORD = "c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
WORD_ARCHIVE = "fde0f7eaa3749d0934a9fc0d6320074f021cd722ed6753f3a59a62fb5b221949"
LAYOUT_ARCHIVE = "b0f3ebc5710e469f3e8fc5ce159cbba048b563944182b50993431ef94f4fedbf"
DONOR, RELAY, RECEIVER = 278, 288, 127
IN, OUT, TERMINAL = 95914, 88, 155442
PAIRS = (
    (94953, 98148), (95493, 95987), (88919, 95502),
    (88952, 95503), (95982, 98175), (95982, 98182),
)
INPUT = {~674: Fraction(1), ~722: Fraction(1), ~1288: Fraction(-1, 845660160)}


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def read_pinned(path, expected_archive_digest, expected_payload_digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == expected_archive_digest, f"bad compressed pin at {path.name}")
    payload = gzip.decompress(raw)
    require(sha256(payload).hexdigest() == expected_payload_digest, f"bad payload pin at {path.name}")
    return json.loads(payload)


def add_scaled(dst, row, coefficient):
    for index, value in row.items():
        updated = dst.get(index, 0) + coefficient * value
        if updated:
            dst[index] = updated
        else:
            dst.pop(index, None)


def dot(row, values):
    return sum(q * values.get(i, 0) for i, q in row.items())


def encoded(row):
    return [[key, str(row[key])] for key in sorted(row) if row[key]]


class NativeGraph:
    def __init__(self, word, layout):
        self.word = word
        self.schedule = word["schedule"]
        self.order = {key: clock for clock, key in enumerate(self.schedule)}
        self.routes = {key: (start, end) for key, start, end in word["moves"]}
        self.forms = {
            key: {symbol: Fraction(value) for symbol, value in row}
            for key, row in word["forms"]
        }
        self.terminals = {
            word["first_output"] + i: chart for i, chart in enumerate(word["final"])
        }
        self.primary = defaultdict(list)
        for i, chart in enumerate(word["initial"]):
            self.primary[chart].append(~i)
        self.arrivals = defaultdict(list)
        for key, (_, chart) in self.routes.items():
            self.arrivals[chart].append(key)

        require(layout["frames"] == word["frames"], "word and layout charts")
        require(layout["public"] == len(word["initial"]) == len(self.terminals) == 1289,
                "1289 arbitrary inputs and outputs")
        require(len(self.routes) == len(word["moves"]) == 5709, "complete MOVE roster")
        require(len(self.order) == len(self.schedule) == len(self.forms) == len(word["forms"])
                == 6998, "complete ordered form roster")
        require(set(self.order) == self.routes.keys() | self.terminals.keys() == self.forms.keys()
                and self.routes.keys().isdisjoint(self.terminals), "each form is one send or terminal")
        for key in self.schedule:
            owner = self.routes[key][0] if key in self.routes else self.terminals[key]
            local_stock = set(self.stock(owner, key))
            require(self.forms[key].keys() <= local_stock, f"noncausal or nonlocal source at {key}")

    def stock(self, chart, before):
        previous = [key for key in self.arrivals[chart] if self.order[key] < self.order[before]]
        return sorted(self.primary[chart] + previous)

    def readers(self, symbol):
        return sorted(key for key, row in self.forms.items() if symbol in row)

    def evaluate(self, public, overrides=None):
        values = {~i: public.get(~i, 0) for i in range(len(self.word["initial"]))}
        overrides = overrides or {}
        for key in self.schedule:
            values[key] = dot(overrides.get(key, self.forms[key]), values)
        return values

    def pulse_columns(self, keys):
        responses = {}
        for key in self.schedule:
            row = {key: Fraction(1)} if key in keys else {}
            for symbol, q in self.forms[key].items():
                if symbol in responses:
                    add_scaled(row, responses[symbol], q)
            if row:
                responses[key] = row
        return responses

    @cache
    def expand(self, key):
        if key < 0:
            return {key: Fraction(1)}
        row = {}
        for symbol, q in self.forms[key].items():
            add_scaled(row, self.expand(symbol), q)
        return row


def row_elimination(rows):
    """Track each reduced row as a combination of the supplied stock atoms."""
    pivots = {}
    relations = []
    for key, row in rows.items():
        residue = row.copy()
        combination = {key: Fraction(1)}
        while residue:
            column = min(residue)
            if column not in pivots:
                pivots[column] = (residue, combination)
                break
            prior, prior_combination = pivots[column]
            factor = -residue[column] / prior[column]
            add_scaled(residue, prior, factor)
            add_scaled(combination, prior_combination, factor)
        if not residue:
            relations.append(combination)
    return pivots, relations


def controls_for_active_pair(graph, early, late, columns, ratio, observe, original, early_stock,
                             late_rows, late_dependence, direct_stock, relations):
    """Realize a nonzero legal recoding for the two pairs that lack a stock annihilator."""
    for combination in relations:
        common = {}
        for key, coefficient in combination.items():
            add_scaled(common, late_rows[key], coefficient)
        divisor = ratio - dot(combination, late_dependence)
        if divisor and dot(common, INPUT):
            break
    else:
        raise ValueError(f"no nonzero causal recoding control for {early}/{late}")

    require(common.keys() <= set(early_stock), "early form uses its initial stock")
    increment = {key: q / divisor for key, q in common.items()}
    new_early = graph.forms[early].copy()
    new_late = graph.forms[late].copy()
    add_scaled(new_early, increment, 1)
    add_scaled(new_late, combination, 1)
    recoded = {early: new_early, late: new_late}
    replay = graph.evaluate(INPUT, recoded)
    delta = dot(increment, INPUT)
    require(delta and replay[early] - original[early] == delta, "real nonzero early change")
    require(all(replay[key] - original[key] == columns.get(key, 0) * delta
                for key in graph.schedule), "serial causal recoding matches pulse addition")
    require(all(replay[key] == original[key] for key in observe), "genuine two-row preservation")
    require(all(not replay[key] for key in direct_stock), "all possible direct sender inputs vanish")
    failed = graph.evaluate(INPUT, recoded | {IN: {}, OUT: {key: Fraction(1) for key in direct_stock}})
    require(not failed[OUT] and not failed[TERMINAL] and original[TERMINAL] == 1,
            "collapse after a genuine compatible recoding loses terminal 155442")
    return {
        "earlier_increment_form": encoded(increment),
        "later_increment_in_its_changed_stock": encoded(combination),
        "earlier_change_at_witness": str(delta),
        "local_later_increment_at_witness": str(ratio * delta),
        "changed_collapsed_outlet_at_witness": str(failed[OUT]),
        "changed_collapsed_terminal_at_witness": str(failed[TERMINAL]),
    }


def pair_certificate(graph, early, late, responses, exterior, arrivals, original, direct_stock):
    require(graph.order[early] < graph.order[late], "ordered pair")
    require({early, late}.isdisjoint({IN, OUT}) and early in graph.routes and late in graph.routes,
            "two other paid slots")
    observe = exterior | arrivals
    first = {key: row[early] for key, row in responses.items() if early in row}
    second = {key: row[late] for key, row in responses.items() if late in row}
    diagnostic = next((key for key in sorted(observe) if first.get(key)), None)
    require(diagnostic is not None and second.get(diagnostic), "nonzero observed paid pulses")
    ratio = -first[diagnostic] / second[diagnostic]
    combined = first.copy()
    add_scaled(combined, second, ratio)
    require(combined.keys().isdisjoint(observe), "match all 1,288 protected coordinates")
    require(first[diagnostic] + second[diagnostic] * (-ratio),
            "reversing the second correction fails at a protected coordinate")

    early_stock = graph.stock(graph.routes[early][0], early)
    late_stock = graph.stock(graph.routes[late][0], late)
    require(all(key < 0 for key in early_stock), "early producer has coordinate stock")
    late_rows = {key: graph.expand(key) for key in late_stock}
    late_basis, _ = row_elimination(late_rows)
    require(len(late_basis) == len(late_rows), "full rank of original later causal stock")
    outside = {
        key: {symbol: q for symbol, q in row.items() if symbol not in early_stock}
        for key, row in late_rows.items()
    }
    projected, relations = row_elimination(outside)
    dependence = {key: first[key] for key in late_stock if key in first}
    require(dependence, "the earlier edit reaches the later producer's stock")
    direct_delta = {key: combined[key] for key in direct_stock if key in combined}
    result = {
        "chronological_slots": [early, late],
        "schedule_indices_zero_based": [graph.order[early], graph.order[late]],
        "routes": [list(graph.routes[early]), list(graph.routes[late])],
        "nonzero_early_pulse_counts": {
            "387_exterior_terminals": sum(key in first for key in exterior),
            "901_receiver_arrivals": sum(key in first for key in arrivals),
        },
        "later_increment_per_earlier_increment": str(ratio),
        "omitted_and_wrong_sign_control": {
            "first_disagreeing_protected_coordinate": diagnostic,
            "with_later_omitted": str(first[diagnostic]),
            "with_later_sign_reversed": str(2 * first[diagnostic]),
        },
        "earlier_stock_rank": len(early_stock),
        "later_stock": late_stock,
        "later_stock_rank": len(late_basis),
        "later_stock_minor_public_columns": sorted(~key for key in late_basis),
        "original_stock_intersection_rank": len(late_basis) - len(projected),
        "later_stock_nonzero_values_at_witness": encoded({key: original[key] for key in late_stock}),
        "early_pulse_into_later_causal_stock": encoded(dependence),
        "early_pulse_at_later_original_paid_row": str(first.get(late, 0)),
        "combined_pulse_at_direct_sender_stock": encoded(direct_delta),
    }
    if direct_delta:
        require(all(not original[key] for key in late_stock), "later original stock annihilates witness")
        result["exclusion"] = "Independence forces the earlier increment into the later original stock span."
    else:
        result["exclusion"] = "Preservation cancels the increments on every possible direct sender input."
        result["nonzero_causal_recoding_control"] = controls_for_active_pair(
            graph, early, late, combined, ratio, observe, original, early_stock,
            late_rows, dependence, direct_stock, relations,
        )
    return result


def replay(source):
    word = read_pinned(source / "WORD.json.gz", WORD_ARCHIVE, WORD)
    layout = read_pinned(source / "LAYOUT.json.gz", LAYOUT_ARCHIVE, LAYOUT)
    graph = NativeGraph(word, layout)
    require(graph.routes[IN] == (DONOR, RELAY) and graph.routes[OUT] == (RELAY, RECEIVER),
            "literal paid path at slots 95914 and 88")
    require(graph.readers(IN) == [OUT], "95914 exclusively feeds 88")
    outlet_readers = graph.readers(OUT)
    require(outlet_readers == [155442, 155490]
            and all(graph.terminals[key] == RECEIVER for key in outlet_readers), "88 has sink-only reads")
    require(not graph.primary[RECEIVER] and all(start != RECEIVER for start, _ in graph.routes.values()),
            "chart 127 is a terminal sink without an initial coordinate")
    exterior = {key for key, chart in graph.terminals.items() if chart != RECEIVER}
    arrivals = set(graph.arrivals[RECEIVER]) - {OUT}
    require(len(exterior) == 387 and len(arrivals) == 901, "protected frontier census")
    require(not graph.primary[DONOR] and len(graph.arrivals[DONOR]) == 10, "direct source stock")
    direct_stock = graph.stock(DONOR, OUT)
    require(set(direct_stock) == set(graph.arrivals[DONOR]), "all donor stock precedes the outlet")
    grades = [len(word["frames"][chart]) for chart in (DONOR, RELAY, RECEIVER)]
    require([abs(grades[0] - grades[1]), abs(grades[1] - grades[2]),
             abs(grades[0] - grades[2])] == [2, 5, 7], "proposed grade-preserving geometry")

    original = graph.evaluate(INPUT)
    require(all(not original[key] for key in direct_stock + list(arrivals)),
            "witness annihilates every direct sender input and retained receiver arrival")
    require(original[OUT] == original[TERMINAL] == 1, "literal required terminal equals one")
    wrong_input = graph.evaluate({key: value for key, value in INPUT.items() if key != ~1288})
    altered_stock = {key: wrong_input[key] for key in direct_stock if wrong_input[key]}
    require(altered_stock, "the third arbitrary input coordinate is detected")
    responses = graph.pulse_columns({key for pair in PAIRS for key in pair})
    pairs = [pair_certificate(graph, early, late, responses, exterior, arrivals, original, direct_stock)
             for early, late in PAIRS]
    return {
        "status": "PASS_SIX_SCOPED_CAUSAL_PAID_PAIR_EXCLUSIONS",
        "source": {"pr": 7786, "head": HEAD, "word_sha256": WORD, "layout_sha256": LAYOUT},
        "counts": {"arbitrary_coordinates": 1289, "protected_exterior": len(exterior),
                   "protected_arrivals": len(arrivals)},
        "public_witness": [[~key, str(INPUT[key])] for key in sorted(INPUT, reverse=True)],
        "altered_witness_nonzero_donor_stock_after_omitting_coordinate_1288": encoded(altered_stock),
        "direct_sender_stock": direct_stock,
        "old_path_grades_and_new_grade": [2, 5, 7],
        "removed_path_slots": [IN, OUT],
        "old_outlet_readers": outlet_readers,
        "old_outlet_at_witness": str(original[OUT]),
        "old_terminal_at_witness": [TERMINAL, str(original[TERMINAL])],
        "pairs": pairs,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true", help="print the complete exact result")
    args = parser.parse_args()
    result = replay(HERE / "sources")
    encoded_result = json.dumps(result, indent=2, sort_keys=True) + "\n"
    require(encoded_result.encode() == (HERE / "STOCK.json").read_bytes(), "exact stock receipt mismatch")
    if args.emit_result:
        print(encoded_result, end="")
    else:
        print(result["status"])

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent forward replay of the #7830 public-only chart-282 cut."""

from collections import Counter, defaultdict
from functools import cache
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import canonical, enclose, margin

HEAD = "14c74c6a67108f675ac1196a5f2415ead0920e71"
WORD = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
PACKED_WORD = "1b1b3294e86979f1f41076fb056f3c0a08ace6df7bf80f2886bc579a22962f4b"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
APPLICATION = "1b2d87e93ae023f5ffd464546af53281b6cb4963dfd76ae4742e0a5540b752fa"
AUTHOR_RESULT = "1a2e0344eb9a6be657120acb92b87b5aeb62b0912700b71e0d5e60b54d435c8f"
TARGET = "0.003889928046155"
DROPPED, PUBLIC_INPUT_SEND, RETURN, OUTLET, EXTRA = 95914, 94019, 90369, 88, 156057
CHANNELS = frozenset((88959, 88960, 90605, 90604))
RELEASED = (89198, 91110, 98703, 91131, 94251)
DEMANDS = (155823, 155993, 156006, 154930, 154938)
S12_DEMANDS = (155823, 155993, 156006, 154930, 154935)


def pinned_json(path, digest, blob=None, unpacked=None):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == digest, path
    if blob:
        header = f"blob {len(data)}\0".encode()
        assert sha1(header + data).hexdigest() == blob, path
    if unpacked:
        data = gzip.decompress(data)
        assert sha256(data).hexdigest() == unpacked, path
    return json.loads(data)


class Program:
    def __init__(self, schedule, routes, forms, initial, final, frames):
        self.schedule = schedule
        self.routes = routes
        self.forms = forms
        self.initial = initial
        self.final = final
        self.frames = frames
        assert len(schedule) == len(set(schedule))
        assert set(schedule) == set(forms) == routes.keys() | final.keys()
        assert routes.keys().isdisjoint(final)
        residents = initial.copy()
        self.chart = {}
        for slot in schedule:
            sender = routes[slot][0] if slot in routes else final[slot]
            self.chart[slot] = sender
            assert all(weight and residents.get(key) == sender
                       for key, weight in forms[slot].items()), (slot, sender)
            if slot in routes:
                residents[slot] = routes[slot][1]

    @cache
    def frame(self, label):
        span = {0}
        for row in self.frames[label]:
            assert row not in span, label
            span.update([value ^ row for value in span])
        return span

    @cache
    def route_grade(self, source, receiver, productive=False):
        left, right = self.frame(source), self.frame(receiver)
        assert left < right or (right < left and not productive), (source, receiver)
        return abs(len(self.frames[source]) - len(self.frames[receiver]))

    def paid_grades(self):
        return Counter(self.route_grade(a, b) for a, b in self.routes.values())

    def eval(self, public, forced=None):
        values = public.copy()
        forced = forced or {}
        for slot in self.schedule:
            values[slot] = forced[slot] if slot in forced else sum(
                weight * values.get(key, 0) for key, weight in self.forms[slot].items())
        return values

    def all_rows(self):
        """Forward-compose exact public coefficients for every native row."""
        public = {key: (1, {-key - 1: 1}) for key in self.initial}
        for slot in self.schedule:
            terms = []
            for key, weight in self.forms[slot].items():
                den, nums = public[key]
                terms.append((den * weight.denominator, weight.numerator, nums))
            denominator = lcm(*(den for den, _, _ in terms))
            sums = defaultdict(int)
            for den, numerator, nums in terms:
                factor = numerator * (denominator // den)
                for axis, n in nums.items():
                    sums[axis] += factor * n
            row = {axis: n for axis, n in sums.items() if n}
            common = gcd(denominator, *row.values())
            public[slot] = (denominator // common, {axis: n // common for axis, n in row.items()})
        return public


def read_program(word):
    forms = {}
    for slot, terms in word["forms"]:
        form = {i: Fraction(q) for i, q in terms}
        assert len(form) == len(terms)
        forms[slot] = form
    routes = {slot: (a, b) for slot, a, b in word["moves"]}
    assert len(routes) == len(word["moves"]) == 5707
    assert len(forms) == len(word["forms"])
    assert len(word["initial"]) == len(word["final"]) == 1289
    initial = {-i - 1: chart for i, chart in enumerate(word["initial"])}
    final = dict(enumerate(word["final"], word["first_output"]))
    return Program(word["schedule"], routes, forms, initial, final, word["frames"])


def changed_tape(base, fifth):
    assert [base.routes[i] for i in (DROPPED, PUBLIC_INPUT_SEND, RETURN, OUTLET)] == [
        (278, 288), (3, 304), (3, 282), (288, 127)]
    assert [i for i in base.schedule if base.chart[i] == 282] == list(RELEASED)
    assert not any(chart == 282 for chart in base.initial.values())
    assert {i for i, (_, bank) in base.routes.items() if bank == 282} == CHANNELS | {RETURN}
    assert base.forms[OUTLET][DROPPED] == 1
    routes = base.routes | {PUBLIC_INPUT_SEND: (3, 278), RETURN: (3, 304), OUTLET: (278, 127)}
    del routes[DROPPED]
    forms = {}
    schedule = []
    for slot in base.schedule:
        if slot == DROPPED:
            continue
        schedule.append(slot)
        if slot == PUBLIC_INPUT_SEND:
            forms[slot] = {-1289: Fraction(1)}
        elif slot == RETURN:
            forms[slot] = base.forms[PUBLIC_INPUT_SEND]
        elif slot == OUTLET:
            forms[slot] = base.forms[DROPPED] | {PUBLIC_INPUT_SEND: Fraction(-845660160)}
        else:
            form = {}
            for key, q in base.forms[slot].items():
                if key == RETURN:
                    assert base.chart[slot] == 282
                    if fifth:
                        form[EXTRA] = q
                else:
                    form[RETURN if key == PUBLIC_INPUT_SEND else key] = q
            forms[slot] = form
        if fifth and slot == RETURN:
            assert EXTRA not in base.forms
            schedule.append(EXTRA)
            routes[EXTRA] = base.routes[RETURN]
            forms[EXTRA] = base.forms[RETURN]
    return Program(schedule, routes, forms, base.initial, base.final, base.frames)


def observed_boundaries(tape):
    """Propagate the union of early stock through each possible changing send."""
    fixed_stock = defaultdict(set)
    channels = defaultdict(set)
    internal = defaultdict(set)
    dirty = set()
    first_receipt = {}
    observations = {}
    for key, chart in tape.initial.items():
        fixed_stock[chart].add(key)
    for slot in tape.schedule:
        source = tape.chart[slot]
        free = slot in CHANNELS
        mutable = free or bool(channels[source])
        if mutable:
            dirty.add(slot)
        if slot in tape.final:
            if mutable:
                observations[slot] = (
                    fixed_stock[source].copy(), channels[source].copy(), internal[source].copy())
            continue
        dest = tape.routes[slot][1]
        if free:
            channels[dest].add(slot)
        elif mutable:
            fixed_stock[dest].update(fixed_stock[source])
            channels[dest].update(channels[source])
            internal[dest].update(internal[source])
            internal[dest].add(slot)
        else:
            fixed_stock[dest].add(slot)
        if mutable:
            first_receipt.setdefault(dest, slot)
    return dirty, first_receipt, observations


def key_from_event(row):
    return row["slot"] if "slot" in row else -1 - row["input_axis"]


def rank_trace(rows, stock, demands):
    """Exact rational row elimination with the highest public axis as pivot."""
    pivots = {}
    trace = []
    for index, slot in enumerate([*stock, *demands]):
        # The common denominator scales the row without changing its rank.
        row = {axis: Fraction(n) for axis, n in rows[slot][1].items()}
        while row:
            axis = max(row)
            coeff = row[axis]
            if axis not in pivots:
                pivots[axis] = {col: value / coeff for col, value in row.items()}
                break
            for col, value in pivots[axis].items():
                new = row.get(col, 0) - coeff * value
                if new:
                    row[col] = new
                else:
                    row.pop(col, None)
        if index >= len(stock) - 1:
            trace.append(len(pivots))
    return trace


def verify_cut(base, four, rows, certificate):
    dirty, first, boundaries = observed_boundaries(four)
    assert first == {int(chart): slot for chart, slot in certificate["first_mutable_receipt_by_chart"].items()}
    assert len(first) == certificate["chronologically_reached_charts"] == 256
    assert len(dirty & four.routes.keys()) == certificate["mutable_paid_count_including_four_ingresses"] == 773
    assert len(boundaries) == certificate["mutable_public_terminal_count"] == 1139
    assert {i for i in dirty & four.routes.keys() if four.routes[i][1] == 282} == CHANNELS
    assert set(first).isdisjoint({3, 273, 276, 278, 304})
    assert set(RELEASED).issubset(dirty)
    assert {PUBLIC_INPUT_SEND, RETURN, OUTLET, 89187}.isdisjoint(dirty)
    assert tuple(item["slot"] for item in certificate["witness_demands"]) == DEMANDS

    clock = {slot: index for index, slot in enumerate(base.schedule)}
    assert [item["slot"] for item in certificate["fixed_retargets"]] == [PUBLIC_INPUT_SEND, RETURN, OUTLET]
    for item in certificate["fixed_retargets"]:
        slot = item["slot"]
        assert item["native_clock"] == clock[slot] and tuple(item["route"]) == four.routes[slot]
    assert certificate["held_side_reader"]["old_operands"] == sorted(base.forms[89187])
    for item, demand in zip(certificate["witness_demands"], DEMANDS, strict=True):
        assert (item["native_clock"], item["terminal_chart"]) == (clock[demand], base.final[demand])
    for item, demand in zip(certificate["witness_cones"], DEMANDS, strict=True):
        fixed, funded, internal = boundaries[demand]
        assert item["demand"] == demand
        assert funded == set(item["funded_ingresses"])
        assert fixed == set(item["fixed_stock_ids"])
        assert internal == set(item["mutable_ancestor_paid_slots"])

    focused = set.union(*(boundaries[d][0] for d in DEMANDS))
    assert focused == {key_from_event(event) for event in certificate["witness_exterior_stock"]}
    assert len(focused) == certificate["witness_exterior_stock_count"] == 136
    for item in certificate["witness_exterior_stock"]:
        key = key_from_event(item)
        if key < 0:
            assert item["chart"] == base.initial[key]
        else:
            assert item["native_clock"] == clock[key] and tuple(item["route"]) == base.routes[key]
    assert set.union(*(boundaries[d][1] for d in DEMANDS)) == CHANNELS
    assert focused.isdisjoint(dirty)

    # Validate the frozen full exterior inventory separately from its rank.
    full = set.union(*(fixed for fixed, _, _ in boundaries.values()))
    assert full == set(certificate["full_exterior_stock_ids"])
    assert len(full) == certificate["full_exterior_stock_count"] == 1581
    assert len(set.union(*(internal for _, _, internal in boundaries.values()))) == (
        certificate["full_exterior_paid_ancestor_count_excluding_four_ingresses"]
    )
    focused_rank = rank_trace(rows, sorted(focused), DEMANDS)
    assert focused_rank == certificate["witness_exact_rank_trace"] == list(range(127, 133))
    s12 = set.union(*(boundaries[d][0] for d in S12_DEMANDS))
    s12_rank = rank_trace(rows, sorted(s12), S12_DEMANDS)
    assert len(s12) == 189 and s12_rank == list(range(165, 171))
    assert certificate["s12_original_exterior_terminals_control"] == {
        "demand_order": list(S12_DEMANDS), "boundary_row_count": len(s12), "exact_rank_trace": s12_rank}
    return focused, full, {
        "reached_charts": len(first),
        "mutable_paid_rows": len(dirty & four.routes.keys()),
        "mutable_terminal_rows": len(boundaries),
        "fixed_exterior_counts_by_demand": [len(boundaries[d][0]) for d in DEMANDS],
        "fixed_exterior_union": len(focused),
        "pooled_public_demand_rank_trace": focused_rank,
        "full_exterior_inventory_count": len(full),
        "s12_terminal_choice_rank_trace": s12_rank,
        "demands": list(DEMANDS),
        "channels": sorted(CHANNELS),
    }


def verify_controls(base, four, five, original, stock, full, certificate):
    restored = five.all_rows()
    assert restored[EXTRA] == original[RETURN]
    assert restored[RETURN] == original[PUBLIC_INPUT_SEND]
    survivors = (base.routes.keys() - {DROPPED, PUBLIC_INPUT_SEND, RETURN}) | base.final.keys()
    assert all(restored[i] == original[i] for i in survivors)
    assert len(survivors & base.final.keys()) == 1289
    assert len(survivors & base.routes.keys()) == 5704
    assert all(four.forms[i] == five.forms[i] for i in full if i >= 0)
    # The retained rows themselves, including retarget outputs in the pool,
    # must retain their original public value in the four-channel tape.
    four_rows = four.all_rows()
    assert all(four_rows[i] == original[i] for i in full | {OUTLET, 89187, 94034, 156055})

    pulses = certificate["verified_separating_pulses"]
    assert len(pulses) == len(DEMANDS)
    incumbent_matrix = []
    four_matrix = []
    for index, item in enumerate(pulses):
        vector = {-axis - 1: Fraction(q) for axis, q in item["input_axis_values"]}
        assert len(vector) == len(item["input_axis_values"]) and vector.keys() <= base.initial.keys()
        public = {i: vector.get(i, Fraction(0)) for i in base.initial}
        old = base.eval(public)
        assert item["exterior_stock_all_zero"] is True and not any(old[i] for i in stock)
        target = [int(i == index) for i in range(len(DEMANDS))]
        observed = [old[d] for d in DEMANDS]
        assert observed == item["incumbent_demand_values"] == target
        incumbent_matrix.append(target)
        four_values = four.eval(public, {88959: old[88959] + old[RETURN] / 2})
        assert not any(four_values[i] for i in stock)
        assert all(four_values[i] == old[i] for i in (89198, 91110, 94251))
        response = [str(four_values[d]) for d in DEMANDS]
        assert response == item["four_channel_trial_demand_values"]
        four_matrix.append(response)
        five_values = five.eval(public)
        assert all(five_values[i] == old[i] for i in survivors)
        assert item["five_channel_public_output_mismatches"] == 0
    assert four_matrix[3] == ["0", "0", "0", "0", "-1"]
    repair = certificate["added_fifth_channel_control"]
    grade = five.route_grade(*five.routes[EXTRA])
    assert grade == repair["new_grade"] == 3
    assert list(five.routes[EXTRA]) == repair["new_route"] == [3, 282]
    assert repair["new_slot"] == EXTRA and repair["shadowed_original_slot"] == RETURN
    assert five.schedule.index(EXTRA) == five.schedule.index(RETURN) + 1
    assert repair["public_terminals_checked_per_pulse"] == len(survivors & base.final.keys())
    assert repair["paid_payloads_checked_per_pulse"] == len(survivors & base.routes.keys())
    return {
        "original_pulse_response_matrix": incumbent_matrix,
        "four_channel_control_response_matrix": four_matrix,
        "extra_slot": EXTRA,
        "extra_route": list(five.routes[EXTRA]),
        "extra_grade": grade,
        "retained_paid_payloads_symbolically_equal": 5704,
        "terminal_rows_symbolically_equal": 1289,
        "public_input_axes_compared": 1289,
    }


def histogram(mapping):
    return Counter({int(key): value for key, value in mapping.items()})


def check_price(base, four, five, layout, app, certificate):
    assert layout["frames"] == base.frames and layout["public"] == len(base.initial)
    assert app["word_sha256"] == WORD and app["layout_sha256"] == LAYOUT and app["caller"] == CALLER
    calls = app["caller_census"]["calls"]
    assert calls == certificate["native_calls"] == 48 and certificate["target"] == TARGET
    owners = set(layout["live"]) | {i + 112 for i in layout["live"]}
    owners.update(layout["hosted"]["X2"], layout["hosted"]["Y2"])
    assert len(owners) == 400
    native_targets = Counter(base.route_grade(source, dest, productive=True) for i, (source, dest) in
                             enumerate(zip(base.initial.values(), base.final.values(), strict=True)) if i not in owners)
    assert native_targets == histogram(app["native"]["positive_helper_ranks"])
    assert base.paid_grades() == histogram(app["native"]["paid_native_ranks"])

    fixed_paid = histogram(app["caller_census"]["fixed_caller_paid"])
    fixed_targets = histogram(app["caller_census"]["fixed_root_targets"])

    def scaled(census):
        return Counter({g: n * calls for g, n in census.items()})

    paid = scaled(base.paid_grades()) + fixed_paid
    targets = scaled(native_targets) + fixed_targets
    assert paid == histogram(app["application"]["invoice"]["paid"])
    assert paid == histogram(certificate["complete_published_baseline_paid"])
    assert targets == histogram(app["application"]["invoice"]["targets"])
    assert targets == histogram(certificate["complete_published_baseline_targets"])

    rerouted = scaled(four.paid_grades()) + fixed_paid
    repaired = scaled(five.paid_grades()) + fixed_paid
    paid_delta = rerouted.copy()
    paid_delta.subtract(paid)
    paid_delta = {g: n for g, n in paid_delta.items() if n}
    assert paid_delta == histogram(certificate["nominal_paid_delta"]) == {3: -48, 5: -48, 7: 48}
    assert repaired - rerouted == {3: calls} and not (rerouted - repaired)
    assert certificate["nominal_productive_delta"] == {} and certificate["earned_signed_credit"] == 0
    baseline = margin(targets, paid, TARGET)
    nominal = margin(rerouted, paid, TARGET)
    extra_one = margin(rerouted + Counter({1: calls}), paid, TARGET)
    shortfall = margin(targets, rerouted + Counter({1: calls}), TARGET)
    fifth = margin(repaired, paid, TARGET)
    for key, bounds in (
        ("baseline_deficit", baseline), ("nominal_credit", nominal),
        ("nominal_credit_after_one_extra_p1_per_call", extra_one),
        ("remaining_shortfall_after_one_extra_p1_per_call", shortfall),
        ("signed_saving_of_restored_five_channel_control", fifth),
    ):
        lo, hi = map(Fraction, certificate[key])
        assert lo <= bounds[0] <= bounds[1] <= hi, key
    assert fifth[1] < 0 < extra_one[1] < baseline[0] < nominal[0]
    return {
        "target_kappa": TARGET,
        "native_calls": calls,
        "complete_baseline_paid": paid,
        "complete_productive_targets": targets,
        "nominal_paid_delta": paid_delta,
        "fifth_channel_paid_delta_from_baseline": {
            g: repaired[g] - paid[g] for g in paid.keys() | repaired.keys() if repaired[g] != paid[g]},
        "baseline_deficit": enclose(baseline),
        "nominal_credit": enclose(nominal),
        "credit_after_one_extra_grade_one_per_call": enclose(extra_one),
        "remaining_deficit_after_one_extra_grade_one_per_call": enclose(shortfall),
        "grade_three_fifth_channel_signed_credit": enclose(fifth),
        "grade_three_fifth_channel_total_deficit": enclose(margin(targets, repaired, TARGET)),
        "earned_signed_credit": 0,
    }


def main():
    assert not sys.flags.optimize, "Run with assertions enabled"
    inputs = HERE.parent / "inputs"
    word = pinned_json(inputs / "DOUBLE-CANDIDATE.json.gz", PACKED_WORD,
                       "51ac72e499cdf6efac62cbd34a9f217d6d135b14", WORD)
    app = pinned_json(inputs / "DOUBLE-APPLICATION.json", APPLICATION,
                      "714f7b48a2a70bb2cc9f7cd4206b2a8701bbb062")
    layout = pinned_json(inputs / "LAYOUT.json.gz",
                         "b0f3ebc5710e469f3e8fc5ce159cbba048b563944182b50993431ef94f4fedbf",
                         "35af1c9e36953cd223eadfca734e122792703de8", LAYOUT)
    assert sha256(canonical(word)).hexdigest() == WORD
    author = pinned_json(HERE / "S14-RESULT.json", AUTHOR_RESULT)
    assert author["source"]["commit"] == HEAD and author["source"]["word_sha256"] == WORD
    assert author["source"]["gzip_sha256"] == PACKED_WORD and author["source"]["application_sha256"] == APPLICATION
    base = read_program(word)
    four = changed_tape(base, fifth=False)
    five = changed_tape(base, fifth=True)
    assert all(base.route_grade(*base.routes[i]) == 1 for i in CHANNELS)
    original = base.all_rows()
    stock, full, checked_cut = verify_cut(base, four, original, author["cut"])
    checked_control = verify_controls(base, four, five, original, stock, full, author["cut"])
    checked_price = check_price(base, four, five, layout, app, author["signed_price"])
    result = {
        "status": "verified_five_public_rows_versus_four_scalar_arrivals",
        "scope": author["scope"],
        "source": author["source"],
        "author_result_sha256": AUTHOR_RESULT,
        "cut": checked_cut,
        "controls": checked_control,
        "signed_price": checked_price,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

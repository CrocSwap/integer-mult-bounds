#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact public-terminal cut after the two funded #7795 retargets on #7830.

Literal replay, compensated routes, and directed tariff functions are adapted
from the Clear1nsight and Codex S12 rational-neighbor certificate.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path


HEAD = "14c74c6a67108f675ac1196a5f2415ead0920e71"
WORD = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
PACKED = "1b1b3294e86979f1f41076fb056f3c0a08ace6df7bf80f2886bc579a22962f4b"
APPLICATION = "1b2d87e93ae023f5ffd464546af53281b6cb4963dfd76ae4742e0a5540b752fa"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
GOAL = "goal-c9b923e487624c27b9078b5182fc7dee"
STEP = "s14-rational-all-outputs"
BINDING = "progress.goal-c9b923e487624c27b9078b5182fc7dee.00000231"
TRIAL = "0.003889928046155"
FUNDED = (88959, 88960, 90605, 90604)
CHART_288 = (89198, 91110, 94251)
CHART_282_OUTLETS = (89198, 91110, 98703, 91131, 94251)
DEMANDS = (155823, 155993, 156006, 154930, 154938)
S12_TERMINALS = (154930, 154935)
FULL_DEMANDS = (154779, 154785, 154789, 154798, 154903)
RETIRED, RETARGET, OBSERVER, OUTLET = 95914, 94019, 90369, 88
SIDE = 89187


def without_zeros(row):
    return {i: q for i, q in row.items() if q}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read_source(path, expected):
    data = path.read_bytes()
    require(sha256(data).hexdigest() == expected, f"unexpected SHA-256 for {path}")
    return data


class Literal:
    def __init__(self, draws, forms, routes, terminals, inputs, frames):
        self.schedule = list(draws)
        self.clock = {slot: clock for clock, slot in enumerate(self.schedule)}
        self.forms = forms
        self.routes = routes
        self.terminals = terminals
        self.inputs = inputs
        self.frames = frames
        self.stock = defaultdict(list)
        resident = dict(inputs)
        for key, chart in resident.items():
            self.stock[chart].append(key)
        require(set(self.schedule) == set(routes) | set(terminals) == set(forms)
                and len(self.schedule) == len(set(self.schedule)), "literal inventory")
        for slot in self.schedule:
            source = self.source(slot)
            require(all(q and resident.get(i) == source for i, q in forms[slot].items()),
                    f"nonlocal or late operand at {slot}")
            if slot in routes:
                dest = routes[slot][1]
                self.stock[dest].append(slot)
                resident[slot] = dest

    def source(self, slot):
        return self.routes[slot][0] if slot in self.routes else self.terminals[slot]

    def readers(self, slot):
        return [i for i in self.schedule if slot in self.forms[i]]

    def before(self, slot):
        return [i for i in self.stock[self.source(slot)]
                if i < 0 or self.clock[i] < self.clock[slot]]

    @lru_cache(None)
    def pullback(self, slot):
        working = {slot: Q(1)}
        for row in reversed(self.schedule):
            weight = working.pop(row, 0)
            if weight:
                for operand, factor in self.forms[row].items():
                    working[operand] = working.get(operand, 0) + weight * factor
        return {~i: q for i, q in working.items() if q}

    def evaluate(self, pulse, override=None):
        # Independent forward evaluation of the sparse pulse.
        override = override or {}
        value = {~i: q for i, q in pulse.items()}
        for row in self.schedule:
            if row in override:
                value[row] = override[row]
            else:
                value[row] = sum(q * value.get(i, 0) for i, q in self.forms[row].items()
                                 if value.get(i, 0))
        return value

    def grade(self, route):
        lower, upper = sorted((self.frames[c] for c in route), key=len)
        span = {0}
        for axis in upper:
            span |= {axis ^ x for x in span}
        require(set(lower) <= span and len(span) == 2**len(upper) and len(lower) < len(upper),
                f"non-nested paid route {route}")
        return len(upper) - len(lower)


def load_word(path):
    raw = gzip.decompress(read_source(path, PACKED))
    require(sha256(raw).hexdigest() == WORD, "unexpected uncompressed word SHA-256")
    word = json.loads(raw)
    graph = Literal(
        word["schedule"], {slot: {i: Q(q) for i, q in row} for slot, row in word["forms"]},
        {slot: (a, b) for slot, a, b in word["moves"]},
        {word["first_output"] + i: chart for i, chart in enumerate(word["final"])},
        {~i: chart for i, chart in enumerate(word["initial"])}, word["frames"],
    )
    require(len(graph.routes) == 5707 and len(graph.inputs) == len(graph.terminals) == 1289,
            "published native inventory")
    return graph


def compensated(graph, shadow=False):
    """Replay actual retargets with an optional fifth chart-282 input control."""
    require(graph.readers(RETIRED) == [OUTLET], "retired observation has one original use")
    require(graph.readers(RETARGET) == [94034, 156055], "restore all old 304 demands")
    require(graph.readers(OBSERVER) == [91110, 98703, 94251], "all withdrawn 282 uses")
    require(graph.readers(FUNDED[0]) == [91110, 98703, 91131, 94251]
            and graph.readers(FUNDED[1]) == [89198, 91110, 98703, 91131, 94251],
            "both recoded donor slots feed only chart-282 rows")
    require(SIDE not in graph.readers(FUNDED[1]), "side reader is a separate source-side output")
    new = graph.pullback(RETIRED).copy()
    new[1288] = new.get(1288, 0) - 845660160
    require(without_zeros(new) == graph.pullback(OUTLET), "old 88 identity")

    draws = [i for i in graph.schedule if i != RETIRED]
    routes = graph.routes.copy()
    forms = graph.forms.copy()
    del routes[RETIRED], forms[RETIRED]
    routes.update({RETARGET: (3, 278), OBSERVER: (3, 304), OUTLET: (278, 127)})
    forms[RETARGET] = {~1288: Q(1)}
    forms[OBSERVER] = graph.forms[RETARGET].copy()
    forms[OUTLET] = {**graph.forms[RETIRED], RETARGET: Q(-845660160)}
    for reader in graph.readers(RETARGET):
        old = forms[reader].copy()
        old[OBSERVER] = old.pop(RETARGET)
        forms[reader] = old

    if shadow:
        extra = max(draws) + 1
        draws.insert(draws.index(OBSERVER) + 1, extra)
        routes[extra] = graph.routes[OBSERVER]
        forms[extra] = graph.forms[OBSERVER]
        for reader in graph.readers(OBSERVER):
            old = forms[reader].copy()
            old[extra] = old.pop(OBSERVER)
            forms[reader] = old
    else:
        # A four-input positive control for chart 288. Grant the 88959
        # channel the old 88959 plus half the old withdrawn observation.
        # The four-channel replay supplies that override externally.
        for reader in graph.readers(OBSERVER):
            old = forms[reader].copy()
            del old[OBSERVER]
            forms[reader] = old
    return Literal(draws, forms, routes, graph.terminals, graph.inputs, graph.frames)


def ordinal(graph, slot):
    return (0, ~slot) if slot < 0 else (1, graph.clock[slot])


class Equations:
    """Sparse rational echelon equations in the original public axes."""
    def __init__(self):
        self.rows = {}

    def add(self, row, right=()):
        row = row.copy()
        while row:
            axis = min(row)
            coefficient = row[axis]
            if axis not in self.rows:
                self.rows[axis] = ({i: q / coefficient for i, q in row.items()},
                                   tuple(q / coefficient for q in right))
                return True
            previous, values = self.rows[axis]
            for i, q in previous.items():
                value = row.get(i, 0) - coefficient * q
                if value:
                    row[i] = value
                else:
                    row.pop(i, None)
            right = tuple(a - coefficient * b for a, b in zip(right, values))
        require(not any(right), "dependent equation with inconsistent pulse values")
        return False

    def inputs_for_right_sides(self, count):
        result = [dict() for _ in range(count)]
        for axis in sorted(self.rows, reverse=True):
            row, values = self.rows[axis]
            for pulse, q in zip(result, values):
                value = q - sum(a * pulse.get(i, 0) for i, a in row.items())
                if value:
                    pulse[axis] = value
        return result


def rank(graph, slots):
    eq = Equations()
    for i in slots:
        eq.add(graph.pullback(i))
    return len(eq.rows)


def event(graph, slot):
    if slot < 0:
        return {"input_axis": ~slot, "chart": graph.inputs[slot]}
    return {
        "slot": slot,
        "native_clock": graph.clock[slot],
        "route": graph.routes.get(slot),
        "terminal_chart": graph.terminals.get(slot),
    }


def physical_cone(graph):
    """Find every paid send and terminal after a chart first sees a free row."""
    dirty, first_arrival = set(), {}
    for slot in graph.schedule:
        if slot in FUNDED or graph.source(slot) in first_arrival:
            dirty.add(slot)
            if slot in graph.routes:
                first_arrival.setdefault(graph.routes[slot][1], slot)
    return dirty, first_arrival


def boundary(graph, dirty, demands):
    """Walk all earlier physical stock, ending at a free channel or an outside row."""
    active = list(demands)
    seen, fixed, channels = set(), set(), set()
    while active:
        row = active.pop()
        if row in seen:
            continue
        seen.add(row)
        for slot in graph.before(row):
            if slot in FUNDED:
                channels.add(slot)
            elif slot in dirty:
                active.append(slot)
            else:
                fixed.add(slot)
    return fixed, channels, seen - set(demands)


def stock_ids(base, stock):
    return sorted(stock, key=lambda i: ordinal(base, i))


def physical_path(graph, dirty, start, demand):
    """Return one time-valid path of available operands from a changed receipt."""
    path = {start: [start]}
    for slot in graph.schedule[graph.clock[start] + 1:graph.clock[demand] + 1]:
        if slot not in dirty:
            continue
        predecessor = next((i for i in graph.before(slot) if i in path), None)
        if predecessor is not None:
            path[slot] = path[predecessor] + [slot]
    return path.get(demand)


def separating_pulses(base, fixed, demands):
    equations = Equations()
    zero = (Q(0),) * len(demands)
    basis = [slot for slot in stock_ids(base, fixed)
             if equations.add(base.pullback(slot), zero)]
    trace = [len(equations.rows)]
    for index, slot in enumerate(demands):
        unit = tuple(Q(j == index) for j in range(len(demands)))
        require(equations.add(base.pullback(slot), unit), f"dependent public demand {slot}")
        trace.append(len(equations.rows))
    return trace, basis, equations.inputs_for_right_sides(len(demands))


def all_public_rows(word):
    """Compute row numerators with one common denominator per slot."""
    rows = {slot: (1, {~slot: 1}) for slot in word.inputs}
    for slot in word.schedule:
        terms = []
        for operand, coefficient in word.forms[slot].items():
            denominator, numerators = rows[operand]
            terms.append((coefficient.numerator, denominator * coefficient.denominator,
                          numerators))
        denominator = lcm(*(d for _, d, _ in terms))
        values = defaultdict(int)
        for numerator, d, term in terms:
            scale = numerator * (denominator // d)
            for axis, value in term.items():
                values[axis] += scale * value
        values = {i: v for i, v in values.items() if v}
        common = gcd(denominator, *values.values())
        rows[slot] = (denominator // common, {i: v // common for i, v in values.items()})
    return rows


def primitive(values):
    common = gcd(*values.values())
    return {i: v // common for i, v in values.items()} if common > 1 else values


class IntegerElimination:
    """Normalize integer numerators as rows are canceled over Q."""

    def __init__(self, axis_priority):
        self.rows = {}
        self.axis_priority = axis_priority

    def add(self, values):
        values = primitive(values.copy())
        while values:
            axis = min(values, key=self.axis_priority.__getitem__)
            if axis not in self.rows:
                self.rows[axis] = values
                return True
            prior = self.rows[axis]
            coefficient = values.pop(axis)
            if len(prior) == 1:
                continue
            pivot = prior[axis]
            divisor = gcd(coefficient, pivot)
            a, b = pivot // divisor, coefficient // divisor
            if a != 1:
                values = {i: v * a for i, v in values.items()}
            for i, value in prior.items():
                if i == axis:
                    continue
                new = values.get(i, 0) - b * value
                if new:
                    values[i] = new
                else:
                    values.pop(i, None)
            values = primitive(values)
        return False


def complete_rank_trace(base, fixed):
    vectors = all_public_rows(base)
    frequencies = Counter(axis for slot in fixed for axis in vectors[slot][1])
    order = sorted(range(len(base.inputs)), key=lambda axis: (frequencies[axis], axis))
    rank = IntegerElimination({axis: index for index, axis in enumerate(order)})
    for slot in sorted(fixed, key=lambda slot: (len(vectors[slot][1]), slot)):
        rank.add(vectors[slot][1])
    trace = [len(rank.rows)]
    for slot in FULL_DEMANDS:
        require(rank.add(vectors[slot][1]), f"dependent full-cut terminal {slot}")
        trace.append(len(rank.rows))
    require(trace == list(range(1134, 1140)), "complete rational rank trace")
    return trace


def check_compensation(base, four, five, dirty):
    """Prove exact outside stock and complete operator restoration by substitution."""
    shadow = max(five.schedule)
    require(five.pullback(shadow) == base.pullback(OBSERVER)
            and five.pullback(OBSERVER) == base.pullback(RETARGET)
            and five.pullback(OUTLET) == base.pullback(OUTLET), "equal replacement payloads")
    aliases = {shadow: OBSERVER, OBSERVER: RETARGET}
    replaced = {RETIRED, RETARGET, OBSERVER, OUTLET}
    surviving = set(base.schedule) - replaced
    require(all({aliases.get(i, i): q for i, q in five.forms[slot].items()} == base.forms[slot]
                for slot in surviving), "complete five-channel operator by local substitution")
    require(all(four.forms[slot] == five.forms[slot] for slot in set(four.schedule) - dirty),
            "every fixed exterior formula survives without the fifth channel")
    require(all(not dirty.intersection(four.forms[slot]) for slot in set(four.schedule) - dirty),
            "no fixed exterior formula sees a physically mutable receipt")
    require(all(four.pullback(slot) == base.pullback(slot)
                for slot in (OUTLET, SIDE, 94034, 156055)), "protected retarget and side readers")
    return {
        "new_slot": shadow,
        "new_route": five.routes[shadow],
        "new_grade": five.grade(five.routes[shadow]),
        "shadowed_original_slot": OBSERVER,
        "symbolically_preserved_rows_by_substitution": len(surviving),
        "paid_payloads_checked_per_pulse": len(base.routes) - 3,
        "public_terminals_checked_per_pulse": len(base.terminals),
    }


def certify(base):
    require(base.stock[282] == [OBSERVER, *FUNDED], "original chart-282 stock")
    require(tuple(i for i in base.schedule if base.source(i) == 282) == CHART_282_OUTLETS,
            "complete chart-282 sender inventory")
    require(all(base.grade(base.routes[slot]) == 1 for slot in FUNDED), "four grade-one channels")
    four, five = compensated(base), compensated(base, shadow=True)
    dirty, earliest = physical_cone(four)
    require(len(earliest) == 256
            and len(dirty.intersection(four.routes)) == 773
            and len(dirty.intersection(four.terminals)) == 1139, "full chronological cone")
    require(all(slot in dirty for slot in CHART_282_OUTLETS + DEMANDS), "all outlets and demands mutable")
    require(not {3, 273, 276, 278, 304}.intersection(earliest)
            and {slot for slot in dirty.intersection(four.routes) if four.routes[slot][1] == 282}
            == set(FUNDED), "no new chart-282 input, no retarget or donor reach")
    require(not {RETARGET, OBSERVER, OUTLET, SIDE}.intersection(dirty), "fixed compensated routes and side row")
    control = check_compensation(base, four, five, dirty)
    full_public = [slot for slot in four.schedule if slot in dirty and slot in four.terminals]
    full_fixed, full_channels, full_paid = boundary(four, dirty, full_public)
    require(len(full_fixed) == 1581 and full_channels == set(FUNDED), "complete exterior inventory")
    require(full_paid <= dirty.intersection(four.routes) - set(FUNDED),
            "full backward cone descends only through mutable paid sends")
    require(set(FULL_DEMANDS) <= set(full_public), "all full-cut demands lie in the reached cone")
    full_trace = complete_rank_trace(base, full_fixed)

    fixed, channels, internal = boundary(four, dirty, DEMANDS)
    require(len(fixed) == 136 and channels == set(FUNDED)
            and fixed <= full_fixed, "focused five-terminal exterior inventory")
    trace, basis, pulses = separating_pulses(base, fixed, DEMANDS)
    require(trace == [127, 128, 129, 130, 131, 132], "five rational quotient dimensions")

    # Also preserve the previous stage's two outer public demands to test the
    # same question under its original choice of receivers.
    s12_choice = DEMANDS[:3] + S12_TERMINALS
    s12_fixed, s12_channels, _ = boundary(four, dirty, s12_choice)
    s12_trace, _, s12_pulses = separating_pulses(base, s12_fixed, s12_choice)
    require(len(s12_fixed) == 189 and s12_channels == set(FUNDED)
            and s12_trace == [165, 166, 167, 168, 169, 170], "previous terminal choice still works")
    for index, pulse in enumerate(s12_pulses):
        old = base.evaluate(pulse)
        require(not any(old.get(slot, 0) for slot in s12_fixed)
                and tuple(old[slot] for slot in s12_choice) ==
                tuple(int(j == index) for j in range(len(s12_choice))),
                "forward check for continuity with the previous terminal choice")

    pulse_receipts = []
    for index, pulse in enumerate(pulses):
        old = base.evaluate(pulse)
        want = tuple(int(j == index) for j in range(len(DEMANDS)))
        require(not any(old.get(slot, 0) for slot in fixed), "zero fixed observations on all pulses")
        require(tuple(old[slot] for slot in DEMANDS) == want, "forward terminal responses form identity")
        new = five.evaluate(pulse)
        require(all(old[slot] == new[slot] for slot in base.terminals),
                "fifth-channel control preserves every public output")
        require(all(old[slot] == new[slot] for slot in base.routes
                    if slot not in {RETIRED, RETARGET, OBSERVER}),
                "fifth-channel control preserves every retained paid payload")
        trial = four.evaluate(pulse, {88959: old[88959] + old[OBSERVER] / 2})
        require(not any(trial.get(slot, 0) for slot in fixed)
                and all(old[slot] == trial[slot] for slot in CHART_288),
                "four-channel trial retains the chart-288 receipts")
        pulse_receipts.append({
            "input_axis_values": [[i, str(q)] for i, q in sorted(pulse.items())],
            "exterior_stock_all_zero": True,
            "incumbent_demand_values": want,
            "four_channel_trial_demand_values": [str(trial[slot]) for slot in DEMANDS],
            "five_channel_public_output_mismatches": 0,
        })
    require(any(tuple(Q(x) for x in row["four_channel_trial_demand_values"]) != row["incumbent_demand_values"]
                for row in pulse_receipts), "four-channel trial fails a public terminal")

    individual = []
    for demand in DEMANDS:
        outside, ingresses, inter = boundary(four, dirty, (demand,))
        individual.append({
            "demand": demand,
            "fixed_stock_ids": stock_ids(base, outside),
            "funded_ingresses": sorted(ingresses, key=base.clock.get),
            "mutable_ancestor_paid_slots": sorted(inter, key=base.clock.get),
        })
    paths = []
    for start in CHART_282_OUTLETS:
        for end in DEMANDS:
            path = physical_path(four, dirty, start, end)
            if path is not None:
                paths.append({"slots": path, "native_clocks": [base.clock[i] for i in path]})
    require(any(p["slots"][0] in CHART_288 and p["slots"][-1] == 154930 for p in paths),
            "cross-branch availability to the 846 demand")

    chart_stock = four.stock[288]
    chart_288_outputs = [slot for slot in four.schedule if four.source(slot) == 288]
    branches = {}
    for row in CHART_282_OUTLETS:
        receiver = four.routes[row][1]
        impulse = base.evaluate({}, {row: Q(1)})
        branches[str(row)] = {
            "outlet": event(base, row),
            "receiver": receiver,
            "receiver_paid_outputs": [event(base, slot) for slot in four.schedule
                                      if four.source(slot) == receiver and slot in four.routes],
            "receiver_public_terminals": [event(base, slot) for slot in four.schedule
                                          if four.source(slot) == receiver and slot in four.terminals],
            "original_direct_readers": [event(base, slot) for slot in base.readers(row)],
            "original_impulse_response_at_witness": [str(impulse[slot]) for slot in DEMANDS],
        }
    contaminated = {slot for slot in internal.intersection(four.routes)
                    if slot not in FUNDED and earliest[four.routes[slot][1]] != slot}
    outside_s12, _, _ = boundary(four, physical_cone_with_held_receipts(four), s12_choice[-2:])
    formerly_fixed = [slot for slot in stock_ids(base, outside_s12.intersection(dirty))]
    return {
        "source_chart": 282,
        "free_ingresses": [event(base, slot) for slot in FUNDED],
        "released_outlets": [event(base, slot) for slot in CHART_282_OUTLETS],
        "receiver_branches": branches,
        "chart_288_causal_stock_after_retargets": [event(base, slot) for slot in chart_stock],
        "chart_288_unchanged_early_rows": [event(base, slot) for slot in chart_288_outputs if slot not in dirty],
        "chart_288_mutable_rows_and_public_terminals": [event(base, slot) for slot in chart_288_outputs if slot in dirty],
        "held_side_reader": {**event(base, SIDE), "old_operands": sorted(base.forms[SIDE])},
        "fixed_retargets": [event(four, slot) | {"native_clock": base.clock[slot]}
                            for slot in (RETARGET, OBSERVER, OUTLET)],
        "retired_slot": event(base, RETIRED),
        "chronologically_reached_charts": len(earliest),
        "first_mutable_receipt_by_chart": earliest,
        "mutable_paid_count_including_four_ingresses": len(dirty.intersection(four.routes)),
        "mutable_public_terminal_count": len(full_public),
        "full_exterior_stock_count": len(full_fixed),
        "full_exterior_stock_ids": stock_ids(base, full_fixed),
        "full_exterior_paid_ancestor_count_excluding_four_ingresses": len(full_paid),
        "full_exterior_rank_demands": [event(base, slot) for slot in FULL_DEMANDS],
        "full_exterior_exact_rank_trace": full_trace,
        "witness_demands": [event(base, slot) for slot in DEMANDS],
        "witness_cones": individual,
        "witness_physical_paths_from_released_outlets": paths,
        "witness_late_mutable_arrivals_into_already_affected_charts": sorted(contaminated, key=base.clock.get),
        "formerly_fixed_s12_outside_rows_now_mutable": [event(base, slot) for slot in formerly_fixed],
        "witness_exterior_stock_count": len(fixed),
        "witness_exterior_stock": [event(base, slot) for slot in stock_ids(base, fixed)],
        "witness_exterior_basis_slots": basis,
        "witness_exact_rank_trace": trace,
        "required_quotient_directions": trace[-1] - trace[0],
        "available_scalar_channels": len(channels),
        "s12_original_exterior_terminals_control": {
            "demand_order": s12_choice,
            "boundary_row_count": len(s12_fixed),
            "exact_rank_trace": s12_trace,
        },
        "verified_separating_pulses": pulse_receipts,
        "added_fifth_channel_control": control,
        "stock_id_encoding": "Transfers are numbered by native slot. Public input axis i is encoded as -1-i.",
    }


def physical_cone_with_held_receipts(graph):
    """Recreate the earlier three-held-receipts envelope for the contamination audit."""
    dirty, reached = set(), set()
    for slot in graph.schedule:
        if slot in CHART_288:
            continue
        if slot in FUNDED or graph.source(slot) in reached:
            dirty.add(slot)
            if slot in graph.routes:
                reached.add(graph.routes[slot][1])
    return dirty


# Directed tariff enclosure adapted from the Clear1nsight and Codex S11 replay.
def tariff_interval(grade):
    # Direct rational log series and alternating exp(-k log(g)).
    def log_series(value):
        z = (value - 1) / (value + 1)
        term, result = z, Q(0)
        for k in range(48):
            result += 2 * term / (2 * k + 1)
            term *= z * z
        return result, result + 2 * term / (97 * (1 - z * z))

    def expansion(x, n):
        term = total = Q(1)
        for k in range(1, n + 1):
            term *= -x / k
            total += term
        return total

    power = grade.bit_length() - 1
    ln2 = log_series(Q(2))
    scaled = log_series(Q(grade, 2**power))
    lower, upper = (Q(TRIAL) * (power * a + b) for a, b in zip(ln2, scaled))
    require(0 <= lower <= upper < 1, "alternating series range")
    return grade * expansion(upper, 25), grade * expansion(lower, 24)


def decimal_enclosure(low, high):
    grid = 10**25
    lo = int(low * grid // 1)
    hi = -int(-high * grid // 1)

    def number(n):
        whole, fraction = divmod(abs(n), grid)
        return f"{'-' if n < 0 else ''}{whole}.{fraction:025d}"

    return [number(lo), number(hi)]


def load_application(path):
    packed = path.read_bytes()
    require(sha256(packed).hexdigest() == APPLICATION, "application SHA-256")
    app = json.loads(packed)
    require(app["word_sha256"] == WORD and app["layout_sha256"] == LAYOUT and app["caller"] == CALLER,
          "word, layout, and caller application anchors")
    require(app["caller_census"]["calls"] == 48, "native application call count")
    return app


def directed_cost(counts, tariffs):
    low, high = Q(0), Q(0)
    for grade, count in counts.items():
        lower_tariff, upper_tariff = tariffs[grade]
        if count < 0:
            lower_tariff, upper_tariff = upper_tariff, lower_tariff
        low += count * lower_tariff
        high += count * upper_tariff
    return low, high


def pricing(graph, app):
    calls = app["caller_census"]["calls"]
    invoice = app["application"]["invoice"]
    paid = Counter({int(g): n for g, n in invoice["paid"].items()})
    targets = Counter({int(g): n for g, n in invoice["targets"].items()})
    native_paid = Counter(graph.grade(route) for route in graph.routes.values())
    require(native_paid == {int(g): n for g, n in app["native"]["paid_native_ranks"].items()},
          "literal grade histogram agrees with the published native census")
    for name, macro_name, native, billed in (
        ("paid", "fixed_caller_paid", native_paid, paid),
        ("target", "fixed_root_targets", app["native"]["positive_helper_ranks"], targets),
    ):
        fixed = Counter({int(g): n for g, n in app["caller_census"][macro_name].items()})
        total = Counter({int(g): calls * n for g, n in native.items()}) + fixed
        require(total == billed, f"complete {name} bill reconstructed")

    old = Counter(graph.grade(graph.routes[i]) for i in (RETIRED, RETARGET, OUTLET, OBSERVER))
    new = Counter(graph.grade(route) for route in ((3, 278), (278, 127), (3, 304)))
    paid_delta = {g: calls * (new[g] - old[g]) for g in old.keys() | new.keys() if new[g] != old[g]}
    require(paid_delta == {3: -48, 5: -48, 7: 48}, "nominal two-retarget paid delta")
    tariffs = {}
    for grade in paid.keys() | targets.keys() | paid_delta.keys():
        lo, hi = tariff_interval(grade)
        # Keep a shared denominator for the full signed sum.
        grid = 10**46
        tariffs[grade] = (Q(lo * grid // 1, grid), Q(-(-hi * grid // 1), grid))
    deficit = directed_cost({g: paid[g] - targets[g] for g in paid.keys() | targets.keys()}, tariffs)
    saving = directed_cost({g: -n for g, n in paid_delta.items()}, tariffs)
    with_extra = tuple(q - calls for q in saving)
    grade = graph.grade(graph.routes[OBSERVER])
    added_low, added_high = directed_cost({grade: calls}, tariffs)
    restored = (saving[0] - added_high, saving[1] - added_low)
    require(0 < with_extra[1] < deficit[0] < saving[0], "an extra P1 per call fails the full invoice")
    require(restored[1] < 0, "the demonstrated grade-three repair loses signed credit")
    return {
        "target": TRIAL,
        "native_calls": calls,
        "complete_published_baseline_paid": paid,
        "complete_published_baseline_targets": targets,
        "baseline_deficit": decimal_enclosure(*deficit),
        "nominal_paid_delta": paid_delta,
        "nominal_productive_delta": {},
        "nominal_credit": decimal_enclosure(*saving),
        "nominal_credit_after_one_extra_p1_per_call": decimal_enclosure(*with_extra),
        "remaining_shortfall_after_one_extra_p1_per_call": decimal_enclosure(
            deficit[0] - with_extra[1], deficit[1] - with_extra[0]),
        "signed_saving_of_restored_five_channel_control": decimal_enclosure(*restored),
        "earned_signed_credit": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("word", type=Path)
    parser.add_argument("application", type=Path)
    args = parser.parse_args()
    base = load_word(args.word)
    app = load_application(args.application)
    price = pricing(base, app)
    print(json.dumps({
        "status": "excluded_by_exact_public_terminal_rank_cut",
        "goal": GOAL,
        "step": STEP,
        "turn_binding_receipt": BINDING,
        "source": {
            "repository": "CrocSwap/integer-mult-bounds",
            "pr": 7830,
            "commit": HEAD,
            "historical_retarget_origin_pr": 7795,
            "word_sha256": WORD,
            "gzip_sha256": PACKED,
            "layout_sha256": LAYOUT,
            "caller_sha256": CALLER,
            "application_sha256": APPLICATION,
        },
        "scope": "Fixed #7830 native chronology and paid topology after the two funded retargets, with four arbitrarily recodable arrivals at chart 282, all five former chart-282 payloads and their causal descendants freely recodable, and all 1289 public outputs prescribed.",
        "cut": certify(base),
        "signed_price": price,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the two-retarget chart-282 reader cut on the exact #7830 rational word."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path


HEAD = "14c74c6a67108f675ac1196a5f2415ead0920e71"
WORD = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
PACKED = "1b1b3294e86979f1f41076fb056f3c0a08ace6df7bf80f2886bc579a22962f4b"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
TRIAL = "0.003889928046155"
PROBE = {~674: Fraction(1), ~722: Fraction(1), ~1288: Fraction(-1, 845660160)}
CUT = (88960, 90369)


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def load_word(path):
    packed = path.read_bytes()
    check(sha256(packed).hexdigest() == PACKED, "compressed word SHA-256")
    raw = gzip.decompress(packed)
    check(sha256(raw).hexdigest() == WORD, "word SHA-256")
    return json.loads(raw)


class Literal:
    def __init__(self, word):
        self.schedule = word["schedule"]
        self.clock = {slot: i for i, slot in enumerate(self.schedule)}
        self.route = {slot: (src, dst) for slot, src, dst in word["moves"]}
        self.terminal = {word["first_output"] + i: c for i, c in enumerate(word["final"])}
        self.in_chart = {~i: c for i, c in enumerate(word["initial"])}
        self.coeffs = {slot: {s: Fraction(v) for s, v in row} for slot, row in word["forms"]}
        self.frames = word["frames"]
        inventory = set(self.route) | set(self.terminal)
        check(len(self.in_chart) == len(self.terminal) == 1289, "public row count")
        check(len(self.route) == 5707 and len(inventory) == len(self.schedule) == 6996,
              "paid and terminal inventory")
        check(inventory == set(self.schedule) == set(self.coeffs), "complete literal schedule")
        resident = dict(self.in_chart)
        for slot in self.schedule:
            source = self.source(slot)
            check(all(q and resident.get(i) == source for i, q in self.coeffs[slot].items()),
                  f"off-chart or late operand at slot {slot}")
            if slot in self.route:
                resident[slot] = self.route[slot][1]

    def source(self, slot):
        return self.route[slot][0] if slot in self.route else self.terminal[slot]

    def readers(self, slots):
        return [i for i in self.schedule if any(s in self.coeffs[i] for s in slots)]

    def stock(self, chart, before=None, skip=()):
        inputs = [i for i, c in self.in_chart.items() if c == chart]
        arrivals = [i for i in self.schedule if i in self.route and self.route[i][1] == chart
                    and i not in skip and (before is None or self.clock[i] < self.clock[before])]
        return inputs + arrivals

    def pullback(self, seed):
        # Pull a linear functional back to the 1,289 public input axes.
        working = dict(seed)
        for slot in reversed(self.schedule):
            weight = working.pop(slot, 0)
            if weight:
                for operand, factor in self.coeffs[slot].items():
                    working[operand] = working.get(operand, 0) + weight * factor
        return {~i: q for i, q in working.items() if q}

    def evaluate(self, initial, omit=()):
        values = dict(initial)
        for i in self.schedule:
            if i not in omit:
                values[i] = sum((factor * values[s] for s, factor in self.coeffs[i].items()
                                 if values.get(s)), Fraction(0))
        return values

    def grade(self, route):
        lower, upper = sorted((self.frames[c] for c in route), key=len)
        span = {0}
        for axis in upper:
            span |= {axis ^ x for x in span}
        check(len(span) == 2 ** len(upper) and set(lower) <= span and len(upper) > len(lower),
              f"non-nested charged route {route}")
        return len(upper) - len(lower)


def row_rank(rows):
    """Exact column elimination on the tested family of public-input row forms."""
    columns = sorted(set().union(*(row.keys() for row in rows)))
    work = [row.copy() for row in rows]
    pivot_row = 0
    for col in columns:
        pivot = next((j for j in range(pivot_row, len(work)) if work[j].get(col)), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        basis = work[pivot_row]
        for row in work[pivot_row + 1:]:
            if row.get(col):
                scale = row[col] / basis[col]
                for j, q in basis.items():
                    row[j] = row.get(j, 0) - scale * q
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def signature(row):
    encoded = [[i, str(q)] for i, q in sorted(row.items())]
    return sha256(json.dumps(encoded, separators=(",", ":")).encode()).hexdigest()


def observer(graph):
    check(graph.route[90369] == (3, 282) and graph.clock[90369] == 297, "observer port and clock")
    check(graph.readers((90369,)) == [91110, 98703, 94251], "three direct observer readers")
    check(graph.readers((95914,)) == [88], "sole old 95914 reader")
    check(graph.route[95914] == (278, 288) and graph.route[88] == (288, 127), "old outlet")
    old_88 = graph.pullback({88: Fraction(1)})
    check(graph.pullback({156056: Fraction(1)}) == {1288: Fraction(1)}, "terminal 156056 identity")
    check(not graph.pullback({88: 1, 95914: -1, ~1288: 845660160}), "old88 all-column identity")
    check(graph.pullback({88: 1, 95914: -1, ~1288: 845660159}) == {1288: -1},
          "perturbed old88 identity must fail")

    held_outlet = graph.stock(127, skip=(88,))
    deposits = [slot for slot in held_outlet if slot >= 0]
    old_sources = graph.stock(278, before=88)
    probe = graph.evaluate(PROBE)
    check(len(deposits) == 901 and len(old_sources) == 10, "frozen #7795 stock counts")
    check(not any(probe[i] for i in deposits + old_sources), "probe annihilates held stock")
    check(probe[88] == probe[155442] == probe[155490] == 1 and probe[90369] == Fraction(1865, 148),
          "published probe response")
    keys = (88, 90369, 155442, 155490, 156056)
    return {"three_coordinate_input": {~i: str(q) for i, q in PROBE.items()},
            "probe_values": {i: str(probe[i]) for i in keys}, "zero_retained_127_arrivals": len(deposits),
            "zero_chart_278_source_atoms": old_sources, "observer_port": [3, 282, 297],
            "observer_readers": graph.readers((90369,)), "old_88_row_sha256": signature(old_88),
            "operator_mutation": {"change_coefficient_by": 1, "nonzero_identity_residual": [[1288, "-1"]]}}


def cut_witness(graph):
    arrivals = graph.stock(282)
    hold = graph.stock(282, skip=CUT)
    demands = graph.readers(CUT)
    check(arrivals == [90369, 88959, 88960, 90605, 90604], "chart-282 full arrival list")
    check(hold == [88959, 90605, 90604], "chart-282 surviving stock")
    check(demands == [89198, 91110, 98703, 91131, 94251], "five protected obligations")
    check(all(graph.source(i) == 282 and graph.stock(282, before=i, skip=CUT) == hold for i in demands),
          "all three surviving forms arrive strictly before every reader")
    rows = {i: graph.pullback({i: Fraction(1)}) for i in arrivals + demands}
    unchanged = [rows[i] for i in hold]
    rank_trace = [row_rank(unchanged + [rows[i] for i in demands[:k]]) for k in range(len(demands) + 1)]
    check(rank_trace == [3, 4, 5, 5, 5, 5], "reader rank trace")
    check(all(row_rank(unchanged + [rows[i]] + [rows[d] for d in demands]) == 5
              and row_rank(unchanged + [rows[i]]) == 4 for i in CUT), "either single ingress still falls short")
    restored = unchanged + [rows[i] for i in CUT]
    check(row_rank(restored + [rows[i] for i in demands]) == row_rank(restored) == 5,
          "restoring both old ingresses supplies the readers")

    # Suppression on the original probe distinguishes the actual literal observers.
    before = graph.evaluate(PROBE)
    after = graph.evaluate(PROBE, omit=CUT)
    check(any(before[i] != after[i] for i in demands), "literal omission must disturb a protected reader")
    return {
        "withdrawn": list(CUT), "surviving_arrivals": [[i, graph.clock[i]] for i in hold],
        "row_provenance_sha256": {i: signature(row) for i, row in rows.items()},
        "protected": [{"slot": i, "clock": graph.clock[i], "route": graph.route[i],
                       "literal_terms": {j: str(q) for j, q in graph.coeffs[i].items()}} for i in demands],
        "rank_trace": rank_trace, "independent_readers": [89198, 91110], "required_added_directions": 2,
        "supplied_by_arbitrary_single_scalar": 1,
        "original_probe_reader_values": {i: str(before[i]) for i in demands},
        "omission_probe_reader_values": {i: str(after[i]) for i in demands},
    }


def tariff_interval(grade):
    # Direct rational log series and alternating exp(-k log(g)).
    def log_series(value):
        z = (value - 1) / (value + 1)
        term, result = z, Fraction(0)
        for k in range(48):
            result += 2 * term / (2 * k + 1)
            term *= z * z
        return result, result + 2 * term / (97 * (1 - z * z))

    def expansion(x, n):
        term = total = Fraction(1)
        for k in range(1, n + 1):
            term *= -x / k
            total += term
        return total

    power = grade.bit_length() - 1
    ln2 = log_series(Fraction(2))
    scaled = log_series(Fraction(grade, 2**power))
    lower, upper = (Fraction(TRIAL) * (power * a + b) for a, b in zip(ln2, scaled))
    check(0 <= lower <= upper < 1, "alternating series range")
    return grade * expansion(upper, 25), grade * expansion(lower, 24)


def decimal_enclosure(low, high):
    grid = 10**25
    lo = int(low * grid // 1)
    hi = -int(-high * grid // 1)

    def number(n):
        whole, fraction = divmod(abs(n), grid)
        return f"{'-' if n < 0 else ''}{whole}.{fraction:025d}"

    return [number(lo), number(hi)]


def pricing(graph):
    original = {i: graph.route[i] for i in (95914, 94019, 88, 90369)}
    proposed = {94019: (3, 278), 88: (278, 127), 90369: (3, 304)}
    old = Counter(graph.grade(route) for route in original.values())
    new = Counter(graph.grade(route) for route in proposed.values())
    held = [88908, 88955, 88960]
    check(all(a in graph.coeffs[b] and graph.clock[a] < graph.clock[b]
              for a, b in zip(held, held[1:])), "held-charge three-leg upstream chain")
    held_chain = [[i, *graph.route[i], graph.grade(graph.route[i])] for i in held]
    check(graph.route[94019] == (3, 304) and graph.readers((94019,)) == [94034, 156055],
          "two abandoned chart-304 readers")
    check(all(graph.source(reader) == 304 and graph.clock[90369] < graph.clock[reader]
              for reader in graph.readers((94019,))), "retargeted 90369 can arrive for both readers")
    check(set(graph.coeffs[94019]) <= set(graph.stock(3, before=90369)), "all causal operands for new 90369")
    stock_278 = set(graph.stock(278, before=88))
    check(graph.in_chart[~1288] == 3 and graph.clock[94019] < graph.clock[88]
          and set(graph.coeffs[95914]) <= stock_278, "all causal operands for new 88")
    check(old == {2: 1, 3: 2, 5: 1} and new == {2: 1, 3: 1, 7: 1}, "frozen grade changes")
    calls = 48
    a, b, c = (tariff_interval(g) for g in (3, 5, 7))
    low = calls * (a[0] + b[0] - c[1])
    high = calls * (a[1] + b[1] - c[0])
    return {"price_target": TRIAL, "inherited_rational_calls": calls,
            "withdrawn_original_routes": {i: [*route, graph.grade(route)] for i, route in original.items()},
            "proposed_routes": {i: [*route, graph.grade(route)] for i, route in proposed.items()},
            "held_chain_slot_ports_and_grades": held_chain,
            "paid_delta_all_calls": {3: -calls, 5: -calls, 7: calls}, "productive_delta": {},
            "gross_saving_polynomial": "48*(P3 + P5 - P7)",
            "gross_nominal_saving": decimal_enclosure(low, high),
            "nominal_saving_after_one_extra_P1_per_call": decimal_enclosure(low - calls, high - calls),
            "earned_signed_credit": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("word", type=Path)
    args = parser.parse_args()
    graph = Literal(load_word(args.word))
    result = {
        "status": "fixed_stock_one_scalar_repair_excluded",
        "source": {"pr": 7830, "head": HEAD, "word_sha256": WORD, "gzip_sha256": PACKED,
                   "reported_layout_sha256": LAYOUT, "reported_caller_sha256": CALLER},
        "observer": observer(graph), "cut": cut_witness(graph), "signed_price": pricing(graph),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

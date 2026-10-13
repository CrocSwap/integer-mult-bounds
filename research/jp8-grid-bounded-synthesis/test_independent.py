"""Bounded differential arithmetic and graph-certificate mutation tests.

Prepared for Philipp (@mightyOil) with substantial OpenAI Codex assistance.
Apache-2.0. Python 3.11+, standard library only; no files are written.

The replay implementation intentionally does not import Fraction.  Here that
different representation checks its common-denominator arithmetic, including
all denominator depths 0..27 observed in the complete scalar projections.
These are helper tests; the main verifier supplies full source/trace coverage.
"""
from copy import deepcopy
from collections import Counter
from fractions import Fraction
import gzip
import heapq
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import crosscheck
import integer_replay
import synth


def fractions(power, coefficients):
    return {column: Fraction(value, 1 << power)
            for column, value in coefficients.items() if value}


def add_fractions(left, right, sign):
    result = {column: left.get(column, Fraction(0)) + sign * right.get(column, Fraction(0))
              for column in left.keys() | right.keys()}
    return {column: value for column, value in result.items() if value}


def corpus():
    """Negative, odd, even, mixed, cancelled-zero and depth-dependent numerators."""
    for power in range(28):
        for coefficients in ({0: -12, 1: 4, 2: 0}, {0: 1, 1: -1}, {2: 0},
                             {0: -(1 << power), 2: 7}, {0: 8, 1: -24, 3: 16}):
            yield power, coefficients


class IndependentTests(unittest.TestCase):
    def assert_row(self, actual, expected):
        power, coefficients = actual
        self.assertIs(type(power), int)
        self.assertTrue(all(type(value) is int and value != 0 for value in coefficients.values()))
        self.assertEqual(fractions(power, coefficients), expected)
        canonical_power = max((value.denominator.bit_length() - 1 for value in expected.values()),
                              default=0)
        self.assertEqual(power, canonical_power)
        if not expected:
            self.assertEqual(actual, (0, {}))

    def test_row_normalization_and_signed_multipliers(self):
        checked = 0
        for power, coefficients in corpus():
            original = deepcopy(coefficients)
            value = integer_replay.row(power, coefficients)
            expected = fractions(power, coefficients)
            self.assert_row(value, expected)
            self.assertEqual(coefficients, original)
            saved = deepcopy(value)
            for numerator in (-127, -16, -3, -1, 0, 1, 2, 3, 16, 127):
                for divisor_power in range(5):
                    scaled = integer_replay.row_multiple(value, numerator, divisor_power)
                    factor = Fraction(numerator, 1 << divisor_power)
                    answer = {column: coefficient * factor for column, coefficient in expected.items()
                              if coefficient * factor}
                    self.assert_row(scaled, answer)
                    checked += 1
            self.assertEqual(value, saved, "row multiplication mutated its input")
        self.assertEqual(checked, 7000)

    def test_all_corpus_row_sums_and_cancellation(self):
        values = [(integer_replay.row(power, coefficients), fractions(power, coefficients))
                  for power, coefficients in corpus()]
        checked = 0
        for left, left_expected in values:
            for right, right_expected in values:
                saved_left, saved_right = deepcopy(left), deepcopy(right)
                for sign in (-1, 1):
                    self.assert_row(integer_replay.row_sum(left, right, sign),
                                    add_fractions(left_expected, right_expected, sign))
                    checked += 1
                self.assertEqual(left, saved_left, "row addition mutated its left input")
                self.assertEqual(right, saved_right, "row addition mutated its right input")
        self.assertEqual(checked, 39200)

    def test_primitive_intermediate_states_and_copy_independence(self):
        t, s, w = ("T", 0), ("S", 0), ("W", 0)
        word = [("copy", w, s), ("double", s), ("halve", w), ("add", t, w),
                ("subtract", t, s), ("negate", w), ("halve", t),
                ("clear", s), ("add", s, w), ("clear", w)]
        for power, coefficients in corpus():
            initial = {t: integer_replay.row(power, coefficients),
                       s: integer_replay.row((power + 3) % 28, {0: -3, 2: 5}),
                       w: integer_replay.row(1, {3: -7})}
            rows = deepcopy(initial)
            expected = {register: fractions(*value) for register, value in initial.items()}
            for instruction in word:
                tag, target = instruction[:2]
                if tag == "copy":
                    expected[target] = expected[instruction[2]].copy()
                elif tag == "clear":
                    expected[target] = {}
                elif tag in ("add", "subtract"):
                    expected[target] = add_fractions(expected[target], expected[instruction[2]],
                                                     1 if tag == "add" else -1)
                else:
                    factor = {"double": Fraction(2), "halve": Fraction(1, 2),
                              "negate": Fraction(-1)}[tag]
                    expected[target] = {column: value * factor
                                        for column, value in expected[target].items()}
                integer_replay.primitive(rows, instruction)
                for register in rows:
                    self.assert_row(rows[register], expected[register])
        self.assertEqual(integer_replay.ZERO, (0, {}), "shared zero row was mutated")

    def test_comparator_formulas_over_entire_supported_coefficient_domain(self):
        checked = 0
        for denominator in (1, 2, 4, 8, 16):
            for numerator in range(1, 128):
                if denominator > 1 and numerator % 2 == 0:
                    continue
                entry = {"numerator": numerator, "denominator": denominator}
                self.assertEqual(integer_replay.comparator_lengths(
                    numerator, denominator.bit_length() - 1), synth.comparisons(entry), entry)
                checked += 1
        self.assertEqual(checked, 383)

    def test_complete_potential_obligations_reject_local_mutations(self):
        numerator, denominator = 7, 4
        potential = crosscheck.bellman_potential(numerator, denominator)["distances"]
        self.assertEqual(len(potential), 57)
        for position, value in enumerate(potential):
            for delta in (-1, 1):
                corrupted = potential.copy()
                corrupted[position] = value + delta
                with self.assertRaises(crosscheck.CertificateError):
                    crosscheck.validate_potential(numerator, denominator, corrupted)
        for corrupted in (potential[:-1], potential + [0]):
            with self.assertRaisesRegex(crosscheck.CertificateError, "every vertex"):
                crosscheck.validate_potential(numerator, denominator, corrupted)
        entry = synth.solve(numerator, denominator)
        for position in range(len(entry["operations"])):
            corrupted = deepcopy(entry)
            corrupted["operations"].pop(position)
            corrupted["preparation_steps"] -= 1
            with self.assertRaises(crosscheck.CertificateError):
                crosscheck.verify_entry(corrupted)

    def test_weighted_dijkstra_against_pareto_receipt(self):
        """490 independent scalar-weight searches, plus aggregate and tie checks."""
        root = HERE.parents[1]
        source = root / ('research/community-k492-audit/pr626/replay/mixed-global/'
                         'base/providers/jp8/LOCAL-PROGRAMS.json.gz')
        programs = json.loads(gzip.decompress(source.read_bytes()))
        counts = {name: Counter(abs(Fraction(e[1][3], e[1][4])) for e in events
                               if e[0] == 'scalar' and e[1][0] == 'add')
                  for name, events in programs.items()}
        self.assertEqual(set(counts), {'forward', 'backward'})
        coefficients = {q for counter in counts.values() for q in counter
                        if q != 1 and q.numerator <= 127
                        and q.denominator in (1, 2, 4, 8, 16)}
        receipt = json.loads((HERE / 'EXPECTED.json').read_text())['source_read_pareto']
        claimed = {Fraction(r['coefficient']): [tuple(p) for p in r['macro_frontier']]
                   for r in receipt['graphs']}
        selected = {Fraction(r['coefficient']) for r in receipt['selected_frontiers']}
        self.assertEqual(coefficients, set(claimed))
        self.assertEqual((len(coefficients), len(selected)), (49, 7))

        def shortest(q, price):
            # Each positive scalar edge weight is instructions + price*reads.
            # Keep differently priced parallel edges, notably double vs add.
            n, d = q.numerator, q.denominator
            bound = n*d
            numerator, denominator = price.numerator, price.denominator
            distances, queue = {d: (0, 0, 0)}, [(0, 0, 0, d)]
            while queue:
                cost, reads, steps, state = heapq.heappop(queue)
                if distances.get(state) != (cost, reads, steps):
                    continue
                edges = [(state+d, 1), (state-d, 1), (-state, 0), (2*state, 0)]
                if state % 2 == 0:
                    edges.append((state//2, 0))
                for target, increment in edges:
                    if abs(target) > bound:
                        continue
                    candidate = (cost+denominator+numerator*increment,
                                 reads+increment, steps+1)
                    if target not in distances or candidate < distances[target]:
                        distances[target] = candidate
                        heapq.heappush(queue, (*candidate, target))
            cost, reads, steps = min(distances[n], distances[-n])
            self.assertEqual(cost, denominator*steps+numerator*reads)
            return steps+3, reads+1  # Paid copy, accumulation, clear; copy reads S.

        prices = list(map(Fraction, ('0', '1/6', '1/3', '2/3', '1',
                                    '26/23', '3/2', '2', '3', '10')))
        intervals = receipt['hypothetical_sensitivity']['intervals']
        self.assertEqual(receipt['hypothetical_sensitivity']['breakpoints'], ['1/3', '1', '2'])
        checked = 0
        for price in prices:
            choices = {}
            for q in coefficients:
                choices[q] = shortest(q, price)
                expected = min(claimed[q], key=lambda p: (p[0]+price*p[1], p[1], p[0]))
                self.assertEqual(choices[q], expected, (q, price))
                checked += 1
            deltas = {name: [0, 0] for name in counts}
            for q in selected:
                tail = bin(q.numerator)[3:]
                old = (3+len(tail)+tail.count('1')+q.denominator.bit_length()-1,
                       1+tail.count('1'))
                for name, counter in counts.items():
                    for coordinate in (0, 1):
                        deltas[name][coordinate] += 2*counter[q]*(choices[q][coordinate]-old[coordinate])
            applicable = [r for r in intervals if Fraction(r['lower']) <= price
                          and (r['upper'] is None or price <= Fraction(r['upper']))]
            self.assertTrue(applicable)
            for interval in applicable:  # Both adjacent costs must agree at ties.
                for name, delta in deltas.items():
                    declared = interval['delta_instructions_source_reads_vs_696'][name]
                    self.assertEqual(delta[0]+price*delta[1], declared[0]+price*declared[1])
                    if price > Fraction(interval['lower']) and (interval['upper'] is None
                                                                or price < Fraction(interval['upper'])):
                        self.assertEqual(delta, declared)
            if price == 0:
                for delta in deltas.values():
                    self.assertEqual(delta, [-104, 92])
                    self.assertEqual(Fraction(-delta[0], delta[1]), Fraction(26, 23))
        self.assertEqual(checked, 490)


if __name__ == "__main__":
    unittest.main()

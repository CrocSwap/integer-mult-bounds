# SPDX-License-Identifier: Apache-2.0
"""Behavioral oracles and failure controls for the finite proof replay."""

import copy
import itertools
import json
import shutil
import tempfile
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

from costs import certificate, compare, log_interval
from eliminate import projected_factor, solve_component
from graph import Graph, bounds, build, components
from spaces import ZERO, domain, rank, span
from verify import PACKAGE, load_words, run, solve


def chain():
    line, top = span([1]), span([1, 2])
    return Graph([('A', 0), ('restore', 0)], [line, line],
                 [(0, -1, ZERO, 0, line), (0, 0, line, 1, line),
                  (0, 1, line, -1, top)], Counter(), Counter())


def triangle():
    top = span([1, 2, 4])
    gates = [(0, 1), (1, 2), (0, 2), (0, 1)]
    traces = [[-1] for _ in range(3)]
    for i, operands in enumerate(gates):
        for r in operands:
            traces[r].append(i)
    edges = [(r, a, ZERO if a == -1 else top, b, top)
             for r, events in enumerate(traces)
             for a, b in zip(events, [*events[1:], -1], strict=True)]
    return Graph([('A', i) for i in range(4)], [top] * 4, edges,
                 Counter(), Counter())


def brute_force(graph, choices):
    """Independent tiny oracle with a literal strictly concave integer tariff."""
    best, optimal, feasible = None, 0, 0
    for assignment in itertools.product(choices, repeat=len(graph.frames)):
        bill = 0
        for _, a, before, b, after in graph.edges:
            before = assignment[a] if a >= 0 else before
            after = assignment[b] if b >= 0 else after
            if not before <= after:
                break
            difference = (len(after).bit_length() - 1) - (len(before).bit_length() - 1)
            bill += difference * (10 - difference)
        else:
            feasible += 1
            if best is None or bill < best:
                best, optimal = bill, 1
            elif bill == best:
                optimal += 1
    return best, optimal, feasible


class JointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = load_words()

    def test_improvable_coupled_prefix_restore(self):
        graph = chain()
        lower, upper = bounds(graph)
        groups = components(graph, lower, upper)
        self.assertEqual(groups, [(0, 1)])
        result, _ = solve_component(groups[0], graph.edges, lower, upper)
        self.assertEqual(result['source_profile'], (1, 2, 0, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(result['optimum_profile'], (2, 0, 1, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual((result['feasible'], result['optimal'], result['source_comparison']),
                         (12, 3, 1))
        self.assertEqual(brute_force(graph, domain(ZERO, span([1, 2]))), (16, 3, 12))

    def test_three_register_exhaustive_oracle(self):
        graph = triangle()
        lower, upper = bounds(graph)
        result, _ = solve_component((0, 1, 2, 3), graph.edges, lower, upper)
        oracle = brute_force(graph, domain(ZERO, span([1, 2, 4])))
        self.assertEqual(oracle[0], 63)
        self.assertEqual((result['optimal'], result['feasible']), oracle[1:])
        self.assertEqual(result['source_comparison'], 0)
        self.assertEqual(result['optimum_profile'][3], 3)

    def test_rotated_subspaces_are_included(self):
        choices = domain(ZERO, span([1, 2]))
        self.assertEqual(set(choices), {ZERO, span([1]), span([2]), span([3]), span([1, 2])})
        self.assertEqual(Counter(map(rank, domain(ZERO, span([1, 2, 4])))),
                         {0: 1, 1: 7, 2: 7, 3: 1})

    def test_wrong_axis_same_rank_rejected(self):
        graph = chain()
        graph.frames[0] = span([4])
        graph.edges[0] = (0, -1, ZERO, 0, span([4]))
        graph.edges[1] = (0, 0, span([4]), 1, span([1]))
        with self.assertRaisesRegex(ValueError, 'source in propagated'):
            bounds(graph)

    def test_disconnected_counts_multiply(self):
        graph = chain()
        line, top = span([1]), span([1, 2])
        graph.labels.append(('B', 0))
        graph.frames.append(line)
        graph.edges.extend([(1, -1, ZERO, 2, line), (1, 2, line, -1, top)])
        lower, upper = bounds(graph)
        results = [solve_component(c, graph.edges, lower, upper)[0]
                   for c in components(graph, lower, upper)]
        self.assertEqual([r['feasible'] for r in results], [12, 5])
        self.assertEqual([r['optimal'] for r in results], [3, 2])

    def test_uniform_concavity_comparison(self):
        split = (0, 2, 0, 0, 0, 0, 0, 0, 0, 0)
        whole = (0, 0, 1, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(compare(split, whole), 1)
        self.assertEqual(compare(whole, split), -1)
        self.assertEqual(compare(whole, whole), 0)

    def test_uniform_taylor_comparison(self):
        delta = (-2, 7, -5, -3, 3, 0, 0, 0, 0, 0)
        kind, lower = certificate(delta)
        self.assertEqual(kind, 'taylor')
        self.assertGreater(lower, Fraction(182917, 10**6))
        self.assertIsNone(certificate(tuple(-x for x in delta)))

    def test_a_crossing_comparison_cannot_be_certified(self):
        # 8*(3H1-H3)-19*(2H1-H2) changes sign inside (0,.01].
        left = (3, 0, 19, 0, 0, 0, 0, 0, 0, 0)
        right = (0, 14, 0, 8, 0, 0, 0, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, 'unresolved tariff'):
            compare(left, right)

    def test_logarithm_intervals(self):
        lo, hi = log_interval(2)
        self.assertGreater(lo, Fraction(6931471805599453094, 10**19))
        self.assertLess(hi, Fraction(6931471805599453095, 10**19))
        self.assertEqual(log_interval(1), (0, 0))
        with self.assertRaises(ValueError):
            log_interval(10)

    def test_capacity_and_mass_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'quotient'):
            domain(ZERO, span([1, 2, 4, 8]))
        with self.assertRaisesRegex(ValueError, 'component capacity'):
            solve_component(tuple(range(129)), [], [], [])
        with self.assertRaisesRegex(ValueError, 'rank mass'):
            certificate((0, 1, 0, 0, 0, 0, 0, 0, 0, 0))
        with self.assertRaisesRegex(ValueError, '4096 elimination candidates'):
            projected_factor(0, set(range(1, 7)), [],
                             {i: [ZERO] * 4 for i in range(7)}, set())

    def test_source_profile_and_inventory_controls(self):
        for section, key in [('local_profile', '1'), ('width_inventory', '9')]:
            with self.subTest(section=section):
                mutant = copy.deepcopy(self.words['base'])
                mutant['report'][section][key] += 1
                with self.assertRaisesRegex(ValueError, 'source profile|helper widths'):
                    solve(mutant)
        mutant = copy.deepcopy(self.words['base'])
        mutant['helper_final'].pop(next(iter(mutant['helper_final'])))
        with self.assertRaises(ValueError):
            solve(mutant)

    def test_actual_prefix_and_warp_controls(self):
        mutant = copy.deepcopy(self.words['base'])
        mutant['B'][0][-1] = [51]
        with self.assertRaisesRegex(ValueError, 'source monotone'):
            build(mutant)
        mutant = copy.deepcopy(self.words['base'])
        mutant['warps'][0][3] = [1]
        with self.assertRaisesRegex(ValueError, 'fixed anchor'):
            build(mutant)
        mutant = copy.deepcopy(self.words['base'])
        mutant['A'][0][-1] = [512]
        with self.assertRaisesRegex(ValueError, 'nine-bit'):
            build(mutant)

    def test_frozen_source_bytes_rejected(self):
        with tempfile.TemporaryDirectory(prefix='joint-frame-test-') as directory:
            package = Path(directory)
            shutil.copy(PACKAGE / 'SOURCES.json', package)
            shutil.copytree(PACKAGE / 'inputs', package / 'inputs')
            path = package / 'inputs/base.json.gz'
            path.write_bytes(path.read_bytes() + b'x')
            with self.assertRaisesRegex(ValueError, 'frozen input bytes'):
                load_words(package)

    def test_complete_source_replay(self):
        result = run()
        self.assertEqual(result['status'], 'PASS_JOINT_FRAME_OPTIMUM')
        common = result['common_problem']
        self.assertEqual((common['scalar_events'], common['variables'], common['components']),
                         (6141, 743, 210))
        self.assertEqual((common['max_bucket'], common['attempts'], common['projected_states']),
                         (2560, 57681, 9776))
        self.assertEqual(common['comparisons']['methods'],
                         {'equal': 1, 'concavity': 41, 'taylor': 15})
        expected = json.loads((PACKAGE / 'RESULT.json').read_text(encoding='utf-8'))
        self.assertEqual(json.loads(json.dumps(result)), expected)


if __name__ == '__main__':
    unittest.main()

"""Independent literal-state oracle for the historical routing screen."""
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_cyclic_topology import routing_state_search


def literal_search(width, depth_cap, scalar_only=False):
    """Dense F2 rows and literal sets of permutations, with no packed states.

    scalar_only deliberately implements an invalid state merge for a control.
    """
    perms = list(permutations(range(width)))
    identity = tuple(tuple(int(i == j) for j in range(width))
                     for i in range(width))
    initial = identity, frozenset([tuple(range(width))])
    seen = {initial}
    frontier = {initial}
    layers = []
    saturated = 0
    survivors = []
    for depth in range(depth_cap + 1):
        serialized = []
        terminals = 0
        for matrix, routes in frontier:
            rows = tuple(sum(x << j for j, x in enumerate(row)) for row in matrix)
            route_bits = sum(1 << j for j, p in enumerate(perms) if p in routes)
            serialized.append((rows, route_bits))
            if all(sum(row) == 1 for row in matrix):
                terminals += 1
                scalar_route = tuple(row.index(1) for row in matrix)
                if scalar_route not in routes:
                    survivors.append(dict(depth=depth, scalar_rows=list(rows),
                                          routing_set=route_bits))
        digest = sha256(''.join(repr(s) + '\n' for s in sorted(serialized)).encode())
        layers.append(dict(depth=depth, new_states=len(frontier),
                           permutation_states=terminals,
                           frontier_sha256=digest.hexdigest()))
        if survivors or not frontier or depth == depth_cap:
            break
        following = set()
        scalar_seen = {matrix for matrix, _ in seen}
        for matrix, routes in sorted(frontier, key=repr):
            for target in range(width):
                for source in range(width):
                    if target == source:
                        continue
                    extended = set(routes)
                    for p in routes:
                        q = list(p)
                        q[target], q[source] = q[source], q[target]
                        extended.add(tuple(q))
                    if len(extended) == len(perms):
                        saturated += 1
                        continue
                    changed = list(matrix)
                    changed[target] = tuple((x + y) % 2 for x, y in
                                            zip(matrix[target], matrix[source]))
                    state = tuple(changed), frozenset(extended)
                    if state not in seen:
                        if not scalar_only or state[0] not in scalar_seen:
                            following.add(state)
                            scalar_seen.add(state[0])
        seen.update(following)
        frontier = following
    return dict(layers=layers, distinct_joint_states=len(seen),
                saturated_transitions_discarded=saturated,
                frontier_closed=not frontier,
                all_lengths_excluded=not frontier and not survivors,
                all_words_through_depth_excluded=not survivors,
                survivors=sorted(survivors, key=lambda s: (s['depth'], s['scalar_rows'], s['routing_set'])))


class CyclicRoutingPackedTest(unittest.TestCase):
    def test_complete_frozen_frontiers_and_receipts(self):
        frozen = json.loads((ROOT / 'certificates/cyclic-topology-audit.json').read_text())
        for expected in frozen['word_searches']:
            with self.subTest(width=expected['W']):
                self.assertEqual(routing_state_search(expected['W'], 7), expected)

    def test_dense_scalar_and_literal_routing_oracle(self):
        for width, cap in [(2, 7), (3, 7), (4, 7)]:
            for depth in range(cap + 1):
                with self.subTest(width=width, depth=depth):
                    expected = literal_search(width, depth)
                    actual = routing_state_search(width, depth)
                    self.assertEqual({key: actual[key] for key in expected}, expected)

    def test_scalar_only_merge_loses_coverage_without_finding_a_survivor(self):
        correct = routing_state_search(3, 4)
        broken = literal_search(3, 4, scalar_only=True)
        self.assertEqual(correct['survivors'], broken['survivors'])
        self.assertTrue(broken['all_words_through_depth_excluded'])
        self.assertLess(broken['distinct_joint_states'], correct['distinct_joint_states'])
        self.assertNotEqual(broken['layers'], correct['layers'])

    def test_depth_cutoff_is_not_closure(self):
        before_closure = routing_state_search(3, 6)
        closed = routing_state_search(3, 7)
        self.assertTrue(before_closure['all_words_through_depth_excluded'])
        self.assertFalse(before_closure['all_lengths_excluded'])
        self.assertTrue(closed['all_lengths_excluded'])
        self.assertEqual(before_closure['distinct_joint_states'], closed['distinct_joint_states'])

    def test_invalid_widths_and_depths_still_raise(self):
        for width in (0, 1, 5):
            with self.subTest(width=width), self.assertRaises(ValueError):
                routing_state_search(width, 3)
        for depth in (-1, 8, 1.5, True):
            with self.subTest(depth=depth), self.assertRaises(ValueError):
                routing_state_search(3, depth)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Differential and independent graph checks for the opt-in frame adapter.

Run directly, including under ``python3 -O``. Arbitrary-DAG cases exercise
``frame_data``'s graph contract, not the stronger cancellation-free circuit
contract checked by ``DisjointTensor.verify``.
"""
from collections import deque
from pathlib import Path
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))

from accelerator import frame_data
from experiments.disjoint_tensor import DisjointTensor
import test_disjoint_tensor

ORIGINAL = DisjointTensor.frame_data
SEED = 88


def explicit_graph_oracle(circuit):
    """Use separate per-node breadth-first searches, with no union recurrence."""
    users = {node: [] for node in circuit.active}
    for node in circuit.active:
        for parent in circuit.args[node] or ():
            users[parent].append(node)
    targets = sorted(circuit.outputs)
    descendants, source_union, target_union = {}, {}, {}
    for start in sorted(circuit.active):
        pending = deque([start])
        reachable = set()
        while pending:
            node = pending.popleft()
            if node in reachable:
                continue
            reachable.add(node)
            pending.extend(users[node])
        target_bits = 0
        target_mask = 0
        for i, target in enumerate(targets):
            if circuit.outputs[target] in reachable:
                target_bits |= 1 << i
                target_mask |= target
        descendants[start] = target_bits
        target_union[start] = target_mask

        pending = deque([start])
        ancestors = set()
        source_mask = 0
        while pending:
            node = pending.popleft()
            if node in ancestors:
                continue
            ancestors.add(node)
            if circuit.args[node]:
                pending.extend(circuit.args[node])
            else:
                source_mask |= circuit.inputs[node - 1]
        source_union[start] = source_mask
    return descendants, source_union, target_union


def graph(inputs, additions, outputs, extra_active=()):
    """Create just the state consumed by frame_data; node zero is unused."""
    args = [None] * (len(inputs) + 1) + list(additions)
    active = set(extra_active)
    pending = list(outputs.values())
    while pending:
        node = pending.pop()
        if node in active:
            continue
        active.add(node)
        pending.extend(args[node] or ())
    return SimpleNamespace(inputs=list(inputs), args=args,
                           outputs=dict(outputs), active=active)


class FrameUnionChecks(unittest.TestCase):
    def compare_maps(self, circuit):
        original = ORIGINAL(circuit)
        optimized = frame_data(circuit)
        self.assertEqual(optimized, original)
        self.assertEqual([list(result.items()) for result in optimized],
                         [list(result.items()) for result in original])
        self.assertEqual(optimized, explicit_graph_oracle(circuit))
        self.assertEqual(len(optimized), 3)
        for result in optimized:
            self.assertEqual(set(result), circuit.active)

    def test_seeded_arbitrary_topological_dags(self):
        rng = random.Random(SEED)
        for case in range(88):
            count = rng.randint(1, 8)
            inputs = [1 << i for i in range(count)]
            additions = []
            for _ in range(rng.randint(0, 24)):
                last = count + len(additions)
                additions.append((rng.randint(1, last), rng.randint(1, last)))
            # An actual repeated child tests OR idempotence explicitly.
            last = count + len(additions)
            additions.append((last, last))
            last += 1
            outputs = {1 << count: last, 1 << (count + 1): last}
            for target in range(2, rng.randint(3, 7)):
                # Include multi-coordinate targets without conflating labels
                # with their positions in the sorted reachable-target bitset.
                mask = (1 << (count + target)) | (1 << count)
                outputs[mask] = rng.randint(1, last)
            with self.subTest(case=case):
                circuit = graph(inputs, additions, outputs)
                self.compare_maps(circuit)
                expected = frame_data(circuit)
                items = list(outputs.items())
                rng.shuffle(items)
                circuit.outputs = dict(items)
                self.assertEqual(frame_data(circuit), expected)
                self.compare_maps(circuit)

    def test_explicit_aliased_outputs_and_target_masks(self):
        circuit = graph([1, 2], [(1, 2), (3, 3)],
                        {0b1100: 4, 0b10100: 4, 0b100000: 1})
        self.compare_maps(circuit)
        descendants, sources, targets = frame_data(circuit)
        self.assertEqual(descendants[1], 0b111)
        self.assertEqual(descendants[4], 0b011)
        self.assertEqual(sources[4], 0b11)
        self.assertEqual(targets[4], 0b11100)
        self.assertEqual(targets[1], 0b111100)

    def test_empty_graph(self):
        self.compare_maps(graph([], [], {}))

    def test_gapped_active_nodes_preserve_map_item_order(self):
        inputs = [1 << i for i in range(300)]
        circuit = graph(inputs, [(1, 256), (2, 301), (257, 302)],
                        {1 << 300: 303, 1 << 301: 299})
        self.compare_maps(circuit)

    def test_overlap_and_unreachable_guards_are_preserved(self):
        cases = {
            'source_target_overlap': graph([1, 2], [(1, 2)], {1: 3}),
            'zero_target_union': graph([1], [], {0: 1}),
            'active_without_output_path': graph([1, 2], [], {4: 1}, (2,)),
            'alias_introduces_overlap': graph([1, 2], [(1, 2)], {4: 3, 1: 3}),
        }
        for name, circuit in cases.items():
            for method in (ORIGINAL, frame_data):
                with self.subTest(case=name, method=method.__module__):
                    with self.assertRaisesRegex(ValueError, 'not a disjoint rectangle'):
                        method(circuit)

    def test_generated_small_circuits_and_both_frame_orientations(self):
        for h, k in ((4, 1), (6, 2), (8, 3), (10, 3)):
            with self.subTest(h=h, k=k):
                circuit = DisjointTensor(h, k)
                self.compare_maps(circuit)
                if k == 3:
                    expected = circuit.verify_frames(exact_bases=True)
                    with patch.object(DisjointTensor, 'frame_data', frame_data):
                        self.assertEqual(circuit.verify_frames(exact_bases=True), expected)
                    self.assertIs(DisjointTensor.frame_data, ORIGINAL)

    def test_h26_all_maps_and_both_frame_orientations(self):
        circuit = DisjointTensor(26)
        # The separate BFS oracle is deliberately confined to small graphs;
        # h=26 compares every entry of every map against the historical scan.
        optimized, original = frame_data(circuit), ORIGINAL(circuit)
        self.assertEqual(optimized, original)
        self.assertEqual([list(result.items()) for result in optimized],
                         [list(result.items()) for result in original])
        expected = circuit.verify_frames()
        self.assertEqual(expected['orientations'], 2)
        with patch.object(DisjointTensor, 'frame_data', frame_data):
            self.assertEqual(circuit.verify_frames(), expected)
        self.assertIs(DisjointTensor.frame_data, ORIGINAL)

    def test_five_historical_tests_with_scoped_adapter(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(
            test_disjoint_tensor.TensorDisjointness)
        self.assertEqual(suite.countTestCases(), 5)
        result = unittest.TestResult()
        with patch.object(DisjointTensor, 'frame_data', frame_data):
            suite.run(result)
        self.assertIs(DisjointTensor.frame_data, ORIGINAL)
        self.assertEqual(result.testsRun, 5)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertEqual(result.skipped, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Differential semantic faults, cache collisions, and admission controls.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from support import (HERE, ROOT, Trace, compare_traces, expected_controls,
                     observed_reference, verify_loaded_sources, verify_sources)

verify_sources()
sys.path.insert(0, str(ROOT / 'scripts'))
from experiments import ternary_side as reference
from audit_joint_frames import matrix, rank, sub
from frame_cache import FrameCache
import fast


class CacheSemantics(unittest.TestCase):
    def test_all_two_by_two_binary_matrix_pairs(self):
        matrices = [matrix((xs[:2], xs[2:])) for xs in itertools.product((0, 1), repeat=4)]
        cache = FrameCache(rank, sub)
        for old, new in itertools.product(matrices, repeat=2):
            expected = (rank(sub(new, old)), rank(new) - rank(old))
            self.assertEqual(cache.transition(old, new), expected)
            self.assertEqual(cache.transition(old, new), expected)
        self.assertEqual(cache.statistics()['ordered_pairs'], 256)
        self.assertEqual(cache.statistics()['hits'], 256)

    def test_seeded_rational_pairs_and_equal_copies(self):
        rng = random.Random(93)
        cache = FrameCache(rank, sub)
        for _ in range(200):
            old, new = [matrix([[Q(rng.randrange(-3, 4), rng.randrange(1, 6))
                                 for _ in range(3)] for _ in range(3)]) for _ in range(2)]
            expected = (rank(sub(new, old)), rank(new) - rank(old))
            self.assertEqual(cache.transition(old, new), expected)
            copies = [tuple(tuple(Q(x.numerator, x.denominator) for x in row)
                            for row in m) for m in (old, new)]
            before = cache.statistics()['ordered_pairs']
            self.assertEqual(cache.transition(*copies), expected)
            self.assertEqual(cache.statistics()['ordered_pairs'], before)

    def test_same_rank_is_not_same_frame(self):
        left = matrix(((1, 0), (0, 0)))
        right = matrix(((0, 0), (0, 1)))
        cache = FrameCache(rank, sub)
        self.assertEqual(cache.transition(left, left), (0, 0))
        self.assertEqual(cache.transition(left, right), (2, 0))
        self.assertNotEqual(cache.intern(left), cache.intern(right))

    def test_direction_controls_signed_dimension_change(self):
        zero = matrix(((0, 0), (0, 0)))
        line = matrix(((1, 0), (0, 0)))
        cache = FrameCache(rank, sub)
        self.assertEqual(cache.transition(zero, line), (1, 1))
        self.assertEqual(cache.transition(line, zero), (1, -1))

    def test_hash_collision_uses_exact_equality(self):
        modulus = sys.hash_info.modulus
        zero, nonzero = matrix(((0,),)), matrix(((modulus,),))
        self.assertEqual(hash(zero), hash(nonzero))
        cache = FrameCache(rank, sub)
        self.assertNotEqual(cache.intern(zero), cache.intern(nonzero))
        self.assertEqual(cache.transition(zero, zero), (0, 0))
        self.assertEqual(cache.transition(zero, nonzero), (1, 1))

    def test_identity_entries_hold_strong_references(self):
        cache = FrameCache(rank, sub)
        for i in range(200):
            value = matrix(((i % 3,),))
            cache.intern(value)
        self.assertEqual(len(cache.frames), 3)
        self.assertEqual(len(cache.by_identity), 200)
        for identity, (value, index) in cache.by_identity.items():
            self.assertEqual(id(value), identity)
            self.assertEqual(value, cache.frames[index])


class CheckerControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = reference.build(8, retain_graph=True)

    def reject_both(self, graph, message):
        for checker in (reference.verify_invocation_frames, fast.verify_invocation_frames):
            with self.subTest(checker=checker.__module__):
                with self.assertRaisesRegex(ValueError, message):
                    checker(graph)

    def test_complete_h8_ordered_trace(self):
        original, cached = Trace(), Trace()
        first = observed_reference(reference, original)(self.graph)
        second = fast.verify_invocation_frames(self.graph, observe=cached)
        self.assertEqual(first, expected_controls()[8]['frames'])
        self.assertEqual(first, second)
        compare_traces(original.payload(), cached.payload())
        self.assertEqual(len(original.edges), 9464)

    def test_missing_common_pair(self):
        bad = copy.deepcopy(self.graph)
        bad['_graph']['common'][1] = 0
        self.reject_both(bad, 'Missing common-pair positivity witness')

    def test_singular_input_gram(self):
        bad = copy.deepcopy(self.graph)
        bad['_graph']['labels'][0] = 0
        self.reject_both(bad, 'Singular Gram matrix')

    def test_wrong_role_count(self):
        bad = copy.deepcopy(self.graph)
        bad['side_roles'] += 1
        self.reject_both(bad, 'Reversible role count failed')

    def test_wrong_target_frame(self):
        bad = copy.deepcopy(self.graph)
        bad['_graph']['targets'][0] = (bad['_graph']['targets'][0] + 1) % bad['n']
        self.reject_both(bad, 'A physical edge has a non-nested rank charge')

    def test_changed_graph_after_success_is_rechecked(self):
        graph = copy.deepcopy(self.graph)
        self.assertEqual(fast.verify_invocation_frames(graph), expected_controls()[8]['frames'])
        graph['_graph']['common'][1] = 0
        with self.assertRaisesRegex(ValueError, 'Missing common-pair positivity witness'):
            fast.verify_invocation_frames(graph)

    def test_non_idempotent_projection(self):
        import audit_joint_frames as algebra
        original = algebra.product

        def corrupt(left, right):
            answer = original(left, right)
            # Corrupt exactly the P*P idempotence comparison; all dimensions and
            # input labels remain valid, so this must reach its semantic guard.
            if left is right:
                rows = [list(row) for row in answer]
                rows[0][0] += 1
                return matrix(rows)
            return answer

        with patch.object(algebra, 'product', corrupt):
            self.reject_both(self.graph, 'Non-idempotent frame')


class AdmissionControls(unittest.TestCase):
    def test_each_pinned_dependency_invalidates(self):
        pins = verify_sources()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in pins['files']:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            verify_sources(root)
            for relative in pins['files']:
                with self.subTest(source=relative):
                    path = root / relative
                    raw = path.read_bytes()
                    path.write_bytes(raw + b'\n# deliberate source mutation\n')
                    with self.assertRaisesRegex(ValueError, 'Pinned source changed'):
                        verify_sources(root)
                    path.write_bytes(raw)
            verify_sources(root)

    def test_disabled_assertions_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / 'out'
            result = subprocess.run([sys.executable, '-O', '-B', str(HERE / 'run.py'),
                                     '--out', str(out)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Assertions must remain enabled', result.stderr)
            self.assertFalse(out.exists())

    def test_output_reuse_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, '-B', str(HERE / 'run.py'),
                                     '--out', temporary], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Use a fresh output directory', result.stderr)

    def test_transcript_rejects_omission_duplication_order_and_matrix_faults(self):
        trace = Trace()
        observed_reference(reference, trace)(reference.build(8, retain_graph=True))
        payload = trace.payload()
        mutations = []
        missing = copy.deepcopy(payload); missing['edges'].pop(); mutations.append(missing)
        duplicate = copy.deepcopy(payload); duplicate['edges'].append(duplicate['edges'][0]); mutations.append(duplicate)
        reordered = copy.deepcopy(payload); reordered['edges'][0:2] = reordered['edges'][1::-1]; mutations.append(reordered)
        changed = copy.deepcopy(payload); changed['matrices'][0][0][0][0] += 1; mutations.append(changed)
        reversed_edge = copy.deepcopy(payload); reversed_edge['edges'][0][0] ^= 1; mutations.append(reversed_edge)
        wrong_slot = copy.deepcopy(payload); wrong_slot['edges'][0][1] += 1; mutations.append(wrong_slot)
        for i, mutation in enumerate(mutations):
            with self.subTest(mutation=i):
                with self.assertRaisesRegex(ValueError, 'Complete ordered rational edge transcript differs'):
                    compare_traces(payload, mutation)

    def test_loaded_dependency_closure(self):
        verify_loaded_sources()


if __name__ == '__main__':
    unittest.main(verbosity=2)

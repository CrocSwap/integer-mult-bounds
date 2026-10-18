#!/usr/bin/env python3
"""Behavioral controls for the exact local native noise witness. Apache-2.0."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent


def module(name):
    path = HERE / (name + '.py')
    result = types.ModuleType(name)
    result.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), result.__dict__)
    return result


V, D = module('verify'), module('independent')


class NativeNoiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.N, cls.packet, cls.word, cls.recipes, cls.residuals = V.load()
        cls.events = V.expand(cls.packet)
        cls.state, cls.report, cls.cut = V.native_channel(
            cls.N, cls.events, cls.word, cls.recipes, cls.residuals)

    def run_channel(self, events=None, recipes=None, **kwargs):
        return V.native_channel(self.N, self.events if events is None else events,
                                self.word, self.recipes if recipes is None else recipes,
                                self.residuals, **kwargs)

    def test_completed_event_grid_and_endpoint(self):
        self.assertEqual(self.cut, self.N.scaled(self.N.ONE, Q(-81921, 262144)))
        self.assertEqual(self.report['guard'], 18)
        self.assertEqual(self.report['first_attainment'], [26472, 93])
        self.assertEqual(self.state[75], self.N.scaled(self.N.ONE, Q(-1, 2)))
        self.assertEqual(self.state[93], self.N.scaled(self.N.ONE, Q(1, 2)))
        self.assertEqual([i for i in range(224, 704) if self.state[i] != self.N.ZERO],
                         [337, 338, 339, 341, 343, 346])
        self.assertTrue(all(v == self.N.ZERO for v in self.state[704:]))
        self.assertEqual((V.EXPECTED * 2**17).denominator, 2)
        self.assertEqual((V.EXPECTED * 2**18).denominator, 1)

    def test_zero_and_signed_dyadic_scaling(self):
        state, report, cut = self.run_channel(injection=self.N.ZERO)
        self.assertTrue(all(v == self.N.ZERO for v in state))
        self.assertEqual(report['guard'], 0)
        self.assertEqual(cut, self.N.ZERO)
        source = self.N.frame(self.word['frames'][236])
        state, report, cut = self.run_channel(injection=self.N.scaled(source, Q(-1, 8)))
        self.assertEqual(state, [self.N.scaled(v, Q(-1, 8)) for v in self.state])
        self.assertEqual(cut, self.N.scaled(self.cut, Q(-1, 8)))
        self.assertEqual(report['guard'], 21)

    def test_child_global_phase_is_material(self):
        recipes = deepcopy(self.recipes)
        entry = next(r for r in recipes['children'] if (r['old'], r['new']) == (236, 240))
        entry['left']['phase'] = (entry['left']['phase'] + 1) % 4
        _, _, bad_cut = self.run_channel(recipes=recipes, stop=V.TARGET)
        self.assertNotEqual(bad_cut, self.cut)

    def test_injection_frame_and_timing_are_material(self):
        _, _, bad_frame = self.run_channel(injection=self.N.ONE, stop=V.TARGET)
        _, _, bad_time = self.run_channel(origin=V.ORIGIN-1, stop=V.TARGET)
        self.assertNotEqual(bad_frame, self.cut)
        self.assertNotEqual(bad_time, self.cut)

    def test_residual_orientation_is_material(self):
        events = deepcopy(self.events)
        self.assertEqual(events[26796][0:3], ['residual_adapter', 'post', 337])
        events[26796][1] = 'pre'
        state, _, cut = self.run_channel(events=events)
        self.assertEqual(cut, self.cut)
        self.assertNotEqual(state[337], self.state[337])

    def test_attaining_scalar_sign_is_material(self):
        events = deepcopy(self.events)
        events[V.TARGET][1][3] *= -1
        _, _, bad_cut = self.run_channel(events=events, stop=V.TARGET)
        self.assertNotEqual(bad_cut, self.cut)
        _, _, bad_trace, independent_cut = D.full_forward(
            events, self.recipes, self.residuals, self.report['injection'])
        self.assertNotEqual(bad_trace, self.report['changed_field_trace_sha256'])
        self.assertNotEqual(independent_cut, {x: (V.EXPECTED, Q(0)) for x in range(512)})

    def test_source_and_site_bindings_fail_closed(self):
        # Only corrupt local disposable bytes; the real immutable input is never edited.
        with tempfile.TemporaryDirectory(prefix='noise-pin-', dir=HERE) as tmp:
            root = Path(tmp)
            path = root / 'research/community-frontier1042-audit/selected-replay.tar.gz'
            path.parent.mkdir(parents=True)
            path.write_bytes(b'corrupt archive control')
            with self.assertRaisesRegex(ValueError, 'source pin'):
                V.load(root)
        packet = deepcopy(self.packet)
        packet['core_words']['backward'][V.ORIGIN-1864][2] = 345
        with self.assertRaisesRegex(ValueError, 'injection child'):
            V.expand(packet)
        packet = deepcopy(self.packet)
        packet['core_words']['backward'][-1] = ['unrecognized']
        with self.assertRaisesRegex(ValueError, 'suffix'):
            V.expand(packet)

    def test_json_controls(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            V.decode(b'{"x": 1, "x": 2}')
        self.assertNotEqual(V.canonical({'x': 1}), V.canonical({'x': True}))
        self.assertNotEqual(V.canonical({'x': 1}), V.canonical({'x': '1'}))

    def test_independent_adjoint_identity(self):
        a = {0: (Q(1, 8), Q(-2)), 37: (Q(3), Q(1, 4)), 511: (Q(-1), Q(0))}
        b = {i: (Q(i % 7 - 3), Q(i % 5 - 2)) for i in range(512)}
        recipe = next(r for r in self.recipes['children'] if (r['old'], r['new']) == (236, 240))
        def dense(v):
            return self.N.vector([int(v.get(i, (0, 0))[0]*8) for i in range(512)],
                                 [int(v.get(i, (0, 0))[1]*8) for i in range(512)], 3)
        av = self.N.recipe(dense(a), recipe)
        aw = {'real': av[0], 'imag': av[1], 'exponent': av[2]}
        aa = dense(a)
        source = {'real': aa[0], 'imag': aa[1], 'exponent': aa[2]}
        result = D.inner(b, aw)
        self.assertNotEqual(result, (0, 0))
        self.assertEqual(result, D.inner(D.native_adjoint(b, recipe), source))


if __name__ == '__main__':
    unittest.main()

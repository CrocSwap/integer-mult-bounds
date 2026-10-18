"""Behavioral controls for the hybrid physical-rounding witness. Apache-2.0."""
import copy
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
# Execute source bytes; no stale local bytecode can replace the verifier.
import types
V = types.ModuleType('physical_rounding_checks')
V.__file__ = str(HERE / 'verify.py')
exec(compile((HERE / 'verify.py').read_bytes(), V.__file__, 'exec'), V.__dict__)
N = V.N


class PhysicalRounding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.word, cls.recipes, cls.residuals = V.load()
        cls.events = V.expand(cls.packet)

    def execute(self, entry, bits=53, events=None, round_at=None):
        return V.execute(self.events if events is None else events, self.packet,
                         self.recipes, self.residuals, entry, bits, round_at)

    def test_independent_nearest_number_oracle(self):
        # Enumerate representable signed integers, then minimize exact distance.
        # This uses neither quotient/remainder rounding nor native vector code.
        checks = 0
        for bits in range(2, 7):
            representable = [0]
            for n in range(1, 4097):
                odd = n // (n & -n)
                if odd.bit_length() <= bits:
                    representable.extend((n, -n))
            for value in range(-257, 258):
                distance = min(abs(value-c) for c in representable)
                ties = [c for c in representable if abs(value-c) == distance]
                if len(ties) == 1:
                    want = ties[0]
                else:
                    step = abs(ties[1]-ties[0])
                    want = next(c for c in ties if (abs(c)//step) % 2 == 0)
                self.assertEqual(V.rn_integer(value, bits), want)
                checks += 1
        self.assertEqual(checks, 2575)
        for bits in (8, 24, 53, 113):
            n = (1 << (bits+12)) + 3
            self.assertEqual(V.rn_integer(n, bits), 1 << (bits+12))
            self.assertEqual(V.rn_integer(-n, bits), -(1 << (bits+12)))

    def test_native_primitive_conventions(self):
        # Pairwise direct complex-Fraction formula, independent of the retained
        # integer vector evaluator, including both line signs and imaginary data.
        re = [((i*11) % 19)-9 for i in range(512)]
        im = [((i*7) % 17)-8 for i in range(512)]
        vector = N.vector(re, im, 3)
        for axis, sign in ((1, 1), (37, -1), (256, 1)):
            out = N.line(vector, axis, sign)
            for i in range(512):
                a, b, c, d = (Q(re[i], 8), Q(im[i], 8),
                              Q(re[i^axis], 8), Q(im[i^axis], 8))
                self.assertEqual(Q(out[0][i], 2**out[2]), (a-sign*b+c+sign*d)/2)
                self.assertEqual(Q(out[1][i], 2**out[2]), (b+sign*a+d-sign*c)/2)
        rows = tuple(1 << i for i in range(9))
        key = rows, (0,)*9, (0,)*9, 0, 1
        out = N.mono(vector, key)
        self.assertEqual(out, N.vector([-x for x in im], re, 3))
        self.assertEqual(N.mono(out, key, True), vector)

    def test_finite_frame_rounding_intertwiner(self):
        frames = [N.frame(axes) for axes in self.word['frames']]
        self.assertEqual(len(frames), 1004)
        for frame in frames:
            self.assertEqual(frame[2], 0)
            self.assertTrue(set(frame[0]+frame[1]) <= {0, -2, -1, 1, 2})
            # Scalar sample covers both signs and a nontrivial tie. The written
            # homogeneity lemma, rather than this sample, quantifies the identity.
            a = Q(33, 8)
            lhs = V.rounded(N.scaled(frame, a), 4)
            rounded_a = Q(V.rn_integer(33, 4), 8)
            self.assertEqual(lhs, N.scaled(frame, rounded_a))
        for i in (3887, 4060):
            self.assertEqual(self.events[i][2], 0)
            self.assertEqual(frames[0], N.ONE)

    def test_wider_same_dirty_and_clean_controls(self):
        entry = V.initial(53)
        actual, faults = self.execute(entry, 65)
        self.assertEqual(actual, entry)
        self.assertEqual(faults, [])
        clean = V.initial(53, dirty=False)
        actual, faults = self.execute(clean)
        self.assertEqual(actual, clean)
        self.assertEqual(faults, [])

    def test_each_rounding_site_matters(self):
        entry = V.initial(53)
        expected_support = {3887: {112: Q(-1, 2), 114: Q(-1, 2), 137: Q(-1, 2), 139: Q(-1, 2)},
                            4060: {112: Q(-1, 2), 139: Q(1, 2), 190: Q(-1, 2), 211: Q(-1, 2)}}
        for site in (3887, 4060):
            actual, faults = self.execute(entry, round_at={site})
            self.assertEqual([x['event'] for x in faults], [site])
            want = list(entry)
            for reg, delta in expected_support[site].items():
                want[reg] = N.plus(want[reg], N.scaled(N.ONE, delta))
            self.assertEqual(actual, want)
            self.assertNotEqual(actual, V.expected(entry))

    def test_dyadic_scale_sign_and_hilbert_bound(self):
        signal = Q(-1, 32)
        entry = V.initial(53, signal)
        actual, faults = self.execute(entry)
        self.assertEqual(actual, V.expected(entry, signal))
        self.assertEqual([x['event'] for x in faults], [3887, 4060])
        error = N.plus(actual[112], N.scaled(entry[112], Q(-1)))
        self.assertEqual(V.squared_norm(entry[112]), Q(1, 2))
        self.assertEqual(V.squared_norm(error), Q(1, 2))

    def test_occupied_exit_adapter_semantics(self):
        # Removing an occupied, nonconstant target exit adapter must affect
        # amplitudes, even though a source adapter on zero input might not.
        events = copy.deepcopy(self.events)
        index = 17721
        self.assertEqual(events[index][:3], ['adapter', 'new_to_old', 114])
        events[index] = ['phase', 'test_omitted_occupied_adapter']
        actual, faults = self.execute(V.initial(53), events=events)
        self.assertEqual([x['event'] for x in faults], [3887, 4060])
        self.assertNotEqual(actual, V.expected(V.initial(53)))
        self.assertEqual(actual[224:], V.initial(53)[224:])

    def test_source_and_receipt_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / 'research/joint-query/certificate.json.gz'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'wrong')
            # Inventory order may check the archive first: both live inputs
            # are present, so the failure tests bytes rather than absence.
            archive = root / 'research/community-frontier1042-audit/selected-replay.tar.gz'
            archive.parent.mkdir(parents=True)
            archive.write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError, 'source pin'):
                V.load(root)
        with self.assertRaises(ValueError):
            V.unique([('x', 1), ('x', 2)])
        with tempfile.TemporaryDirectory() as temp:
            receipt = Path(temp) / 'receipt.json'
            receipt.write_text('{"value":true}')
            with self.assertRaisesRegex(ValueError, 'receipt mismatch'):
                V.verify_receipt(receipt, {'value': 1})
            receipt.write_text('{"value":1,"value":2}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                V.verify_receipt(receipt, {'value': 1})
        with self.assertRaises(ValueError):
            V.rn_integer(1, 1)


if __name__ == '__main__':
    unittest.main()

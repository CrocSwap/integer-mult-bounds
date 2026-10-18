#!/usr/bin/env python3
"""Source, semantic and receipt controls for the P104 max-flow audit.

Each corruption must be rejected for the stated reason, and an equivalent
frame-basis presentation must reproduce the identical receipt.  Prepared for
Michael Yee with substantial Claude (Anthropic) assistance.  Apache-2.0.
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify  # noqa: E402


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (verify.ROOT / verify.WITNESS).read_bytes()
        cls.witness = verify.load_witness()
        cls.receipt = verify.audit(cls.witness)

    def mutated(self):
        return copy.deepcopy(self.witness)

    def first(self, kind, w, pred=lambda e: True):
        return next(i for i, e in enumerate(w['program']) if e[0] == kind and pred(e))

    def test_receipt_is_committed(self):
        self.assertEqual(verify.RESULT.read_text(encoding='utf-8'), verify.canonical(self.receipt))

    def test_modified_source_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'w.json'
            p.write_bytes(self.raw.replace(b'"-1/4"', b'"-1/2"', 1))
            with self.assertRaisesRegex(verify.AuditError, 'PR1972 pin'):
                verify.load_witness(p)

    def test_transport_rank_mutation_rejected(self):
        w = self.mutated()
        i = self.first('transport', w)
        w['program'][i][4] += 1
        with self.assertRaisesRegex(verify.AuditError, 'rank mismatch'):
            verify.chronology(w)

    def test_add_outside_common_chart_rejected(self):
        w = self.mutated()
        i = self.first('add', w, lambda e: len(e[4]) > 0)
        w['program'][i][4] = []
        with self.assertRaisesRegex(verify.AuditError, 'common chart'):
            verify.chronology(w)

    def test_non_nested_transport_rejected(self):
        w = self.mutated()
        i = self.first('transport', w, lambda e: len(verify.frame(e[2])) == 1)
        (q,) = verify.frame(w['program'][i][2])
        w['program'][i][3] = [1 if q != 1 else 2]
        with self.assertRaisesRegex(verify.AuditError, 'not nested'):
            verify.chronology(w)

    def test_scalar_attainment_check_is_live(self):
        w = self.mutated()
        i = self.first('add', w)
        w['program'][i][3] = str(2 * verify.Fraction(w['program'][i][3]))
        verify.chronology(w)  # frames stay legal: only the scalar data changes
        with self.assertRaises(verify.AuditError):
            verify.audit(w)

    def test_equivalent_basis_presentation_is_invariant(self):
        w = self.mutated()
        for e in w['program']:
            if e[0] == 'transport' and len(e[3]) >= 2:
                head, *rest = e[3]
                e[3] = [head] + [v ^ head for v in rest]
                e[3].reverse()
        self.assertEqual(verify.canonical(verify.audit(w)), verify.canonical(self.receipt))

    def test_corrupted_receipt_rejected(self):
        text = verify.canonical(self.receipt).replace('"max_flow_arrays": 8', '"max_flow_arrays": 9')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'RESULT.json'
            p.write_text(text, encoding='utf-8')
            with self.assertRaisesRegex(verify.AuditError, 'differs'):
                verify.main(['--result', str(p)])

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'exists.json'
            p.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(verify.AuditError, 'overwrite'):
                verify.main(['--write', str(p)])
            self.assertEqual(json.loads(p.read_text(encoding='utf-8')), {})


if __name__ == '__main__':
    unittest.main()

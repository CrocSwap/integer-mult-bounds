#!/usr/bin/env python3
"""Behavior and mathematical boundary controls; no expensive search repetition."""
import gzip
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify
from algebra import (baseline, check_fit, dot, escape_controls, pairing,
                     rank, roots_e8, scalar_gram)


class Controls(unittest.TestCase):
    def test_authenticate_before_parsing_both_inputs(self):
        original = verify.HERE
        for name in verify.PINS:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp)
                shutil.copytree(original/'inputs', copied/'inputs')
                raw = b'{invalid JSON'
                (copied/'inputs'/name).write_bytes(gzip.compress(raw) if name.endswith('.gz') else raw)
                verify.HERE = copied
                try:
                    with self.assertRaisesRegex(ValueError, 'source authentication'):
                        verify.sources()
                finally:
                    verify.HERE = original

    def test_recompression_preserves_the_scientific_source(self):
        original = verify.HERE
        expected = verify.sources()
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp)
            shutil.copytree(original/'inputs', copied/'inputs')
            path = copied/'inputs/DATA-PHASES.json.gz'
            path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=1234))
            verify.HERE = copied
            try:
                self.assertEqual(verify.sources(), expected)
            finally:
                verify.HERE = original

    def test_both_plane_dimensions_and_scalar_mask(self):
        _, all_planes = verify.sources()
        planes = [all_planes[i] for i in (13, 23, 35, 16, 34)]
        rows = baseline(planes)
        self.assertEqual(sum(check_fit(rows, planes)), 20)
        bad = [r[:] for r in rows]
        bad[4] = bad[0][:]
        with self.assertRaisesRegex(ValueError, 'scalar mask'):
            check_fit(bad, planes)
        # Each axis touches two orthogonal full planes, with pairing rank four.
        self.assertEqual(pairing(planes[0]+planes[1], planes[0]+planes[1]), 4)
        self.assertEqual(pairing([planes[0][0], planes[1][0]], [planes[0][0], planes[1][0]]), 2)

    def test_quarter_and_signed_half_are_actual_escapes(self):
        self.assertEqual(escape_controls(), {'quarter_positive_cost': 72,
                          'signed_half_cost': 81, 'line_ports': 120,
                          'binary_quotient_dimension': 9})
        roots = roots_e8()
        gram = scalar_gram(roots)
        binary = [[1 ^ ((x//2) % 2) for x in row] for row in gram]
        bad = [r[:] for r in roots]
        bad[8][1] *= -1
        modified = scalar_gram(bad)
        self.assertTrue(any(modified[i][j] != 0 for i in range(120) for j in range(120)
                            if i != j and binary[i][j]))

    def test_orthogonal_degenerate_sums_share_a_radical(self):
        # B=diag(1,1,0); H1=<e1,e3>, H2=<e2,e3> are orthogonal,
        # intersect nontrivially, yet their bilinear ranks add.
        def gram_rank(vectors):
            return rank([sum(dot(x & 3, y & 3) << j for j, y in enumerate(vectors)) for x in vectors])
        self.assertEqual(gram_rank([1, 4]), 1)
        self.assertEqual(gram_rank([2, 4]), 1)
        self.assertEqual(gram_rank([1, 4, 2, 4]), 2)
        self.assertEqual(rank([1, 4, 2, 4]), 3)

    def test_frozen_receipt_has_typed_complete_coverage(self):
        result = json.loads((verify.HERE/'RESULT.json').read_text())
        self.assertIs(type(result['minimum_cost_each_cycle']), int)
        self.assertEqual(result['minimum_cost_each_cycle'], 20)
        self.assertEqual(len(result['cycles']), 23)
        self.assertEqual(len(result['cost_classes']), 16)
        self.assertEqual(sum(len(c['members']) for c in result['cost_classes']), 23)
        self.assertTrue(all(type(s['found']) is bool and not s['found'] and s['witness'] is None
                            for c in result['cost_classes'] for s in c['searches']))
        original = json.dumps(result, sort_keys=True)
        result['minimum_cost_each_cycle'] = '20'
        self.assertNotEqual(original, json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    unittest.main()

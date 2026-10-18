#!/usr/bin/env python3
"""Obligation tests for the exact coefficient and Newton-polygon audit."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('newton_audit', HERE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
c = audit.cyclotomic


def dense_remainder(poly, divisor):
    poly = list(poly)
    while len(poly) >= len(divisor):
        shift = len(poly) - len(divisor)
        scale = poly[-1]  # divisor is monic
        for j, value in enumerate(divisor):
            poly[j + shift] -= scale * value
        poly.pop()
    return tuple(poly + [0] * (len(divisor) - 1 - len(poly)))


def dense_tail_coefficients(p, a, t):
    r, q = p ** a, p ** (a - 1)
    divisor = [int(i % q == 0) for i in range((p - 1) * q + 1)]
    result = []
    # Deliberately rebuild each product, with ordinary polynomial multiplication
    # and monic long division; no cyclic shifts or cyclotomic shortcut.
    for j in range(r):
        poly = (1,)
        for s in range(j + 1, r):
            factor = [0] * (t * s + 1)
            factor[0], factor[-1] = 1, -1
            product = [0] * (len(poly) + len(factor) - 1)
            for x, u in enumerate(poly):
                for y, v in enumerate(factor):
                    product[x + y] += u * v
            poly = dense_remainder(product, divisor)
        result.append(dense_remainder(poly, divisor))
    return result


class Obligations(unittest.TestCase):
    def test_all_domain_eisenstein(self):
        for p, a, r in audit.domain():
            poly = c.cyclotomic_pi_polynomial(p, a)
            self.assertEqual(len(poly), (p - 1) * p ** (a - 1) + 1)
            self.assertEqual(poly[0], p)
            self.assertEqual(abs(poly[-1]), 1)
            self.assertTrue(all(x % p == 0 for x in poly[:-1]))
            self.assertNotEqual(poly[0] % (p * p), 0)

    def test_dense_polynomial_reference(self):
        for p, a in [(2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (5, 1)]:
            r = p ** a
            for t in range(1, r):
                if t % p:
                    self.assertEqual(c.tail_coefficients(p, a, t, basis='u'), dense_tail_coefficients(p, a, t))

    def test_radix_four_literal_coefficients(self):
        # u=i, pi=1-i: [4,2+2i,1+i,1] in the u basis.
        self.assertEqual(c.tail_coefficients(2, 2, 1, basis='u'), [(4, 0), (2, 2), (1, 1), (1, 0)])
        self.assertEqual(c.tail_coefficients(2, 2, 1), [(4, 0), (4, -2), (2, -1), (1, 0)])
        self.assertEqual(c.tail_valuations(2, 2, 1), [4, 3, 1, 0])

    def test_signed_primitive_choices(self):
        for p, a in [(2, 3), (3, 2), (5, 1)]:
            r = p ** a
            self.assertEqual(c.tail_coefficients(p, a, -1), c.tail_coefficients(p, a, r - 1))
            self.assertEqual(c.tail_coefficients(p, a, r + 1), c.tail_coefficients(p, a, 1))

    def test_strict_input_admission(self):
        for args in [(True, 1, 1), (2, True, 1), (2, 1, True), (2.0, 1, 1),
                     (1, 2, 1), (6, 1, 1), (2, -1, 1), (3, 2, 0), (3, 2, 3)]:
            with self.assertRaises((ValueError, TypeError)):
                c.tail_valuations(*args)
        with self.assertRaises(ValueError):
            c.tail_coefficients(2, 2, 1, basis='unknown')

    def test_controls_and_extra_contacts(self):
        self.assertEqual(len(audit.controls()), 9)
        vals = audit.counting_valuations(3, 2)
        self.assertEqual(audit.lower_hull(vals), [(0, 12), (6, 2), (8, 0)])
        record = audit.polygon_record(vals, 3, 2)
        self.assertEqual(record['segments'][0]['contacts'], [0, 3, 6])
        self.assertEqual(record['segments'][1]['contacts'], [6, 7, 8])

    def test_receipt_types_are_not_coerced(self):
        self.assertNotEqual(audit.canonical({'x': 1}), audit.canonical({'x': True}))
        self.assertNotEqual(audit.canonical({'x': 1}), audit.canonical({'x': 1.0}))

    def test_source_drift_fails_and_relocation_works(self):
        manifest = json.loads((HERE / 'SOURCE.json').read_text())
        original = audit.HERE
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            relocated = root / 'research' / HERE.name
            relocated.mkdir(parents=True)
            shutil.copyfile(HERE / 'SOURCE.json', relocated / 'SOURCE.json')
            for name in manifest['sha256']:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parent.parent / name, target)
            try:
                audit.HERE = relocated
                self.assertEqual(audit.check_sources(), manifest['base_commit'])
                changed = root / 'research/prime-power-cyclic-inverse/PROOF.md'
                changed.write_bytes(changed.read_bytes() + b'\ncorrupted source\n')
                with self.assertRaisesRegex(ValueError, 'source drift'):
                    audit.check_sources()
            finally:
                audit.HERE = original


if __name__ == '__main__':
    unittest.main()

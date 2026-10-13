#!/usr/bin/env python3
"""Failure controls and offline-closure checks for the receiver census.
Prepared for ToikY with substantial OpenAI Codex assistance; Apache-2.0.
"""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True  # Preserve hash-inventoried predecessor packages.
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('receiver_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = v.Model()

    def test_block_lower_bounds_and_attainment(self):
        rows = {b: [self.model.local(b, m) for m in itertools.product((1, 2, 3),
                    repeat=len(self.model.groups[b]))] for b in range(10)}
        minima = {b: min(t['cost'] for t in ts) for b, ts in rows.items()}
        self.assertEqual(minima, {0: 3, 1: 1, 2: 0, 3: 2, 4: 0, 5: 4, 6: 0, 7: 0, 8: 0, 9: 0})
        multiplicity = 1
        for b, ts in rows.items():
            multiplicity *= sum(t['cost'] == minima[b] for t in ts)
        self.assertEqual(multiplicity, 2646)
        self.assertEqual(429 + sum(minima.values()), 439)

    def test_failed_write_must_not_change_donor_contents(self):
        text = (HERE / 'verify.py').read_text()
        anchor = 'missing |= remainder  # A failed predecessor write is skipped.'
        self.assertEqual(text.count(anchor), 1)
        mutant = types.ModuleType('failed_write_mutant')
        mutant.__file__ = str(HERE / 'verify.py')
        exec(compile(text.replace(anchor, 'missing |= remainder; content[destination] = wanted'),
                     mutant.__file__, 'exec'), mutant.__dict__)
        bad = mutant.Model().local(0, (2, 1, 1))
        good = self.model.local(0, (2, 1, 1))
        self.assertEqual(good['extras'], [48, 49, 50, 57])
        self.assertEqual(bad['extras'], [49, 50, 57])
        self.assertEqual((good['cost'], bad['cost']), (4, 3))

    def test_extra_reuse_and_junk_are_both_priced(self):
        row = self.model.local(0, (3, 1, 1))
        self.assertEqual((row['target_count'], row['rank'], row['reusable_extras']), (9, 8, 3))
        self.assertEqual(row['junk'], 0)
        self.assertEqual(v.junk_count(9, 8, 0), 1)
        # Synthetic deficient transfer: two demanded equal rows need one independent
        # dirty direction. One eligible carrier supplies it but is still paid once.
        self.assertEqual(len(v.echelon([1, 1])), 1)
        self.assertEqual(v.junk_count(2, 1, 0), 1)
        self.assertEqual(1 + v.junk_count(2, 1, 1), 1)

    def test_punctured_keeper_is_zero(self):
        model = v.Model()
        wire = model.fk[(53, 62)]
        self.assertEqual(wire, 462)
        self.assertEqual(model.initial[wire], 0)
        good = model.local(5, (1, 1))
        model.initial[wire] = 1 << 111
        try:
            bad = model.local(5, (1, 1))
        except ValueError:
            return
        self.assertNotEqual(v.canonical(good), v.canonical(bad))
        self.assertIn(111, bad['extras'])

    def test_receiver_domain_rejects_invalid_values(self):
        for masks in ((0, 1, 1), (4, 1, 1), (True, 1, 1), (1, 1)):
            with self.subTest(masks=masks), self.assertRaises(ValueError):
                self.model.local(0, masks)

    def test_echelon_against_explicit_span(self):
        vectors = [0b10101, 0b11000, 0b01101, 0b00011]
        span = {0}
        for x in vectors:
            span |= {s ^ x for s in tuple(span)}
        self.assertEqual(1 << len(v.echelon(vectors)), len(span))
        for x in range(32):
            self.assertEqual(v.residual(x, vectors) == 0, x in span)

    def test_minimal_offline_copy_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix='p111 receiver closure ') as tmp:
            root = Path(tmp)
            package = root / 'research/p111-receiver-census'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for name in v.REQUIRED:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / name, target)
            def snapshot():
                return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob('*') if p.is_file()}
            def run(name='verify.py', flags=(), ok=True):
                proc = subprocess.run([sys.executable, '-I', '-B', *flags, str(package / name)],
                                      cwd=tmp, capture_output=True, text=True, timeout=90)
                self.assertEqual(proc.returncode == 0, ok, proc.stdout + proc.stderr)
                return proc.stdout + proc.stderr
            before = snapshot()
            self.assertIn('PASS_P111_RECEIVER_CENSUS', run())
            self.assertIn('PASS', run('independent.py'))
            self.assertEqual(before, snapshot(), 'verification changed its input closure')
            self.assertIn('ordinary Python', run(flags=('-O',), ok=False))
            expected = package / 'EXPECTED.json'
            saved = expected.read_bytes()
            value = json.loads(saved); value['minimum_R'] = 439.0
            expected.write_text(json.dumps(value))
            self.assertIn('receipt mismatch', run(ok=False))
            expected.write_bytes(saved)
            pins = package / 'SOURCES.json'; saved = pins.read_bytes()
            value = json.loads(saved); value['files'].pop()
            pins.write_text(json.dumps(value))
            self.assertIn('source pin', run(ok=False))
            pins.write_bytes(saved)
            source = root / v.REQUIRED[0]
            source.write_bytes(source.read_bytes() + b'\n# corruption control\n')
            self.assertIn('source SHA256', run(ok=False))


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('ordinary Python required: pinned predecessor setup uses assertions; omit -O')
    unittest.main()

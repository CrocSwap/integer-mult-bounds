"""Integration boundaries for the new endpoint/phase composition."""
from dataclasses import replace
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'research/translated-partial'
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('translated_partial_verify',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class TranslatedPartialIntegration(unittest.TestCase):
    def test_actual_relocated_rank_mass_and_recorded_producers(self):
        n,rows=v.bit_counts()
        self.assertEqual(n['W']*n['m']-sum(w*c for w,c in rows.items()),2*n['N']-2*n['L'])
        self.assertEqual(rows[32729],n['B2'])
        self.assertNotIn(575,rows)
        self.assertNotIn(31625,rows)
        v.validate_producer(HERE/'producer-certificate.json')

    def test_correct_complex_schedule_and_guard_are_bound_to_assembly(self):
        import complex_source
        c=complex_source.run();a=v.assembly()
        self.assertEqual(c['a_c'],1-a['parameters']['sigma'])
        self.assertEqual(c['guard']['C1'],a['parameters']['C1'])
        self.assertGreater(c['guard']['q'],22120)
        self.assertEqual(c['guard']['M'],21924)
        self.assertGreater(v.KAPPA,Q(1,2**18))
        self.assertLess(v.KAPPA,Q(1,2**17))

    def test_wrong_headline_or_missing_complex_headroom_is_rejected(self):
        with self.assertRaises(AssertionError):v.assembly(replace(v.parameters(),kappa=Q(1,2**17)))
        with self.assertRaises(AssertionError):v.assembly(replace(v.parameters(),sigma=1-Q(417,10**8)))
        with self.assertRaises(ValueError):v.bit_certificate(Q(12,10**6))

    def test_pinned_dependency_and_active_theorem_have_separate_sources(self):
        v.validate_retained_sources()
        note=(ROOT/'notes/translated-partial-note.tex').read_text()
        self.assertIn('notes/translated-partial-bit.tex',note)
        self.assertIn('notes/translated-partial-complex.tex',note)
        self.assertIn('notes/translated-partial-assembly.tex',note)
        self.assertNotIn(r'\input{notes/partial-swap-assembly.tex}',note)
        self.assertIn(r'\frac{5499}{10^9}',(ROOT/'notes/translated-partial-assembly.tex').read_text())

if __name__=='__main__':unittest.main()

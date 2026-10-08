"""New-interface integration and pinned-source boundaries for the -20 patch."""
import importlib.util
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'research/nested-source'
spec = importlib.util.spec_from_file_location('nested_source_patch', FOLDER/'make_patch.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NestedSourceIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = module.patched_files()
        cls.sources = module.all_sources(cls.files)
        cls.previous = {n:t for n,o,t in module.previous.patched_files()}

    def test_full_label_reference_and_pinned_base_audit(self):
        result = module.audit(self.files)
        self.assertEqual(result['missing_references'],0)
        self.assertEqual(result['files'],8)
        self.assertGreater(result['unique_labels'],120)

    def test_historical_proofs_retained_and_new_consumers(self):
        for section in ('04-swap.tex','05-layers.tex'):
            name='build/sections/'+section
            self.assertTrue(self.sources[name].startswith(self.previous[name]))
        for section in ('06-transforms.tex','07-resampling.tex','08-assembly.tex'):
            text=self.sources['build/sections/'+section]
            self.assertNotIn('lem:batched-chunk-swap',text)
            self.assertNotIn('prop:batched-simultaneous-layer',text)
        self.assertIn('prop:nested-simultaneous-layer',self.sources['build/sections/06-transforms.tex'])
        self.assertIn('lem:nested-chunk-swap',self.sources['build/sections/08-assembly.tex'])

    def test_separate_arities_and_all_extension_proofs(self):
        bit=self.sources['build/sections/04-swap.tex']
        layer=self.sources['build/sections/05-layers.tex']
        self.assertIn((ROOT/'notes/nested-bit.tex').read_text(),bit)
        self.assertIn((ROOT/'notes/nested-complex.tex').read_text(),layer)
        active=layer[layer.index(r'\begin{proposition}[Nested-source simultaneous'):]
        self.assertIn(r'm_{\rm b}=32768',active)
        self.assertIn(r'm_{\rm c}=21952',active)
        self.assertIn(r'C_1=3/2-\beta/2+\zeta',active)
        self.assertNotIn('two selected classes',active)
        self.assertNotIn('three selected classes',active)
        self.assertIn('sec:nested-complex-guard',active)

    def test_final_parameters_and_guard_are_the_certificate_values(self):
        w=module.verify.assembly();p=w['parameters']
        text=self.sources['build/sections/08-assembly.tex']
        self.assertIn(r'\kappa='+module.texq(p['kappa'])+r'>2^{-20}',text)
        self.assertIn('G_*-\\kappa='+module.texq(w['absorption_gap']),text)
        self.assertIn(r'\epsilon C_1='+module.texq(p['epsilon']*p['C1']),text)
        self.assertIn('d^{'+str(p['epsilon'].denominator)+r'}\le b^{'+str(p['epsilon'].numerator)+'}',text)
        self.assertIn(r'$F=2^{\lceil1.14\alpha^2\rceil}',self.sources['build/sections/07-resampling.tex'])

    def test_audit_rejects_duplicate_labels_and_stale_consumers(self):
        files=list(self.files)
        name,old,text=files[0]
        files[0]=(name,old,text+r'\label{lem:nested-chunk-swap}')
        with self.assertRaisesRegex(ValueError,'Duplicate labels'):module.audit(tuple(files))
        files=list(self.files)
        index=next(i for i,(n,o,t) in enumerate(files) if n.endswith('06-transforms.tex'))
        n,o,t=files[index];files[index]=(n,o,t.replace('prop:nested-simultaneous-layer','prop:batched-simultaneous-layer'))
        with self.assertRaisesRegex(ValueError,'Stale active layer'):module.audit(tuple(files))


if __name__=='__main__':unittest.main()

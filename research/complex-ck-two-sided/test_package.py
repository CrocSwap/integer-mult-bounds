"""Focused provenance, pricing and corruption controls for the finite package.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import experiment as e
import independent


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word,cls.programs,cls.checks=e.load()
        cls.panel,cls.recipe=e.construct(cls.word)

    def source_closure(self, root):
        for item in e.read(e.HERE/'SOURCES.json')['files']:
            source=e.ROOT/item['path'];dest=root/item['path']
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)

    def test_recompression_keeps_mathematical_input(self):
        with tempfile.TemporaryDirectory(prefix='ck closure ') as tmp:
            root=Path(tmp);self.source_closure(root)
            path=root/e.PROVIDER/'CANONICAL-WORD.json.gz'
            path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()),compresslevel=1,mtime=1234567))
            with patch.object(e,'ROOT',root):
                self.assertEqual(e.load()[0],self.word)

    def test_changed_and_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.source_closure(root)
            path=root/e.PROVIDER/'CANONICAL-WORD.json.gz'
            changed=copy.deepcopy(self.word);changed['compensation'][0][3]*=-1
            path.write_bytes(gzip.compress(e.canonical(changed)))
            with patch.object(e,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'source pin'):
                    e.load()
                path.unlink()
                with self.assertRaises(FileNotFoundError):
                    e.load()

    def test_all_emitted_coefficients_exact_with_dirty_work(self):
        coefficients=set()
        for programs in (self.programs,e.replace_programs(self.word,self.programs,self.panel)):
            for events in programs.values():
                for event in events:
                    if event[0]=='scalar' and event[1][0]=='add':
                        coefficients.add(Q(event[1][3],event[1][4]))
        for q in sorted(coefficients):
            result=independent.replay(e.lower(['add',['L',1],['L',0],q.numerator,q.denominator]),n=2,centers=0)
            expected={'denominator_power':q.denominator.bit_length()-1,
                      'terms':[[0,q.numerator],[1,q.denominator]]}
            self.assertEqual(result['endpoint']['L'][1],expected)
            self.assertEqual(result['endpoint']['L'][0],{'denominator_power':0,'terms':[[0,1]]})
            self.assertEqual(result['endpoint']['W'][0],{'denominator_power':0,'terms':[]})
            cost=3+len(bin(abs(q.numerator)))-3+bin(abs(q.numerator)).count('1')+q.denominator.bit_length()-1
            self.assertEqual(result['primitive_count'],cost)
        self.assertGreater(len(coefficients),100)

    def test_non_scalar_and_other_scalar_segments_unchanged(self):
        changed=e.replace_programs(self.word,self.programs,self.panel)
        begin=1+len(self.word['precondition']);end=begin+len(self.word['compensation'])
        for name,original in self.programs.items():
            self.assertEqual(changed[name][:begin],original[:begin])
            self.assertEqual(changed[name][begin+len(self.panel):],original[end:])
            self.assertEqual([x for x in changed[name] if x[0]!='scalar'],[x for x in original if x[0]!='scalar'])

    def test_repeated_helpers_fail_independent_recipe(self):
        bad=copy.deepcopy(self.recipe);bad['helper_pairs'].append(bad['helper_pairs'][0])
        with self.assertRaisesRegex(independent.ReplayError,'helper pair collision'):
            independent.check_recipe(self.word,bad)

    def test_tampered_cost_fails_independent_recipe(self):
        bad=copy.deepcopy(self.recipe);bad['two_sided_panel_price']-=1
        with self.assertRaisesRegex(independent.ReplayError,'complete panel price'):
            independent.check_recipe(self.word,bad)

    def test_typed_json_comparison_distinguishes_bool(self):
        # JSON object equality alone treats True as 1; committed receipts use bytes.
        self.assertNotEqual(e.canonical({'price':1}),e.canonical({'price':True}))


if __name__=='__main__':
    unittest.main()

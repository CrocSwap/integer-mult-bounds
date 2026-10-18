#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mathematical and read-only packaging controls; work under Python -O."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('uniform_audit', HERE/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class MathematicalControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = audit.path_word(audit.PATH_FOUR)
        cls.result = audit.build_result()

    def test_finite_dependencies(self):
        self.assertEqual(self.result['nine_points']['count'],2600)
        self.assertEqual(self.result['nine_points']['max_coverage'],29)
        self.assertEqual(self.result['pairings']['count'],945)
        self.assertEqual(self.result['pairings']['max_coverage'],31)
        self.assertEqual(self.result['source_projections']['identity_by_length'],[1,0,20,0])

    def test_five_positive_maps_and_literal_inverses(self):
        for record in self.result['witnesses'].values():
            word = record['root_word']
            audit.replay(list(reversed(word)))
            leaves,_ = audit.lower(word)
            audit.replay(word,True,list(reversed(leaves)))

    def test_odd_readout_retains_dirt(self):
        word = self.word.copy()
        del word[next(i for i,g in enumerate(word) if g[0]=='R')]
        with self.assertRaisesRegex(ValueError,'dirty-input'):
            audit.replay(word)

    def test_missing_source_uncompute(self):
        word = self.word.copy()
        del word[next(i for i,g in enumerate(word) if g[0]=='X')]
        with self.assertRaisesRegex(ValueError,'dirty-input'):
            audit.replay(word)

    def test_missing_query(self):
        word = self.word.copy()
        del word[next(i for i,g in enumerate(word) if g[0]=='Q')]
        with self.assertRaisesRegex(ValueError,'dirty-input'):
            audit.replay(word)

    def test_heterogeneous_B_breaks_the_shear_identity(self):
        state = [{((),i)} for i in range(37)]
        for gate in self.word:
            if gate[0]=='Q': audit.apply_leaf(state,gate[1],5,('B'+str(gate[1]),))
            elif gate[0]=='R': audit.apply_leaf(state,5,5+gate[1],('A'+str(gate[1]),))
            else: audit.apply_leaf(state,gate[1],gate[2],())
        target = [{((),i)} for i in range(37)]
        for m in range(1,32):
            for j in range(5):
                if (m>>j)&1: target[5+m].add((('A'+str(m),'B'+str(j)),j))
        self.assertNotEqual(state,target)

    def test_omitted_recursive_leaf(self):
        leaves,_ = audit.lower(self.word)
        with self.assertRaisesRegex(ValueError,'dirty-input'):
            audit.replay(self.word,True,leaves[:7]+leaves[8:])

    def test_noncommuting_factor_order(self):
        leaves,_ = audit.lower(self.word)
        bad = []
        for source,target,operator in leaves:
            changed = tuple({'B.0':'B.1','B.1':'B.0'}.get(v,v) for v in operator)
            bad.append((source,target,changed))
        with self.assertRaisesRegex(ValueError,'dirty-input'):
            audit.replay(self.word,True,bad)

    def test_private_scratch_alias(self):
        leaves,_ = audit.lower(self.word)
        bad = [(5 if s==37 else s,5 if t==37 else t,op) for s,t,op in leaves]
        with self.assertRaises(ValueError): audit.replay(self.word,True,bad)

    def test_closed_point_count_and_capacity(self):
        self.assertEqual(len(set(audit.PATH_FOUR)),10)
        self.assertEqual(len(audit.PATH_FOUR),11)
        self.assertEqual(audit.differences((0,1,0)),{0,1})
        self.assertEqual(min(t+audit.minimum_reads(t) for t in range(9)),76)
        # Treating closing zero as a new point would give the spurious 62-read
        # bound for t=8; the actual capacity bound is 68.
        self.assertEqual(audit.minimum_reads(8),68)
        self.assertNotEqual(audit.minimum_reads(8),124-2*min(31,9*8//2))
        self.assertEqual(self.result['arithmetic']['at_most_72_survivors'],[[10,62]])

    def test_sharp_odd_query_midpoint(self):
        word = audit.path_word(audit.PATH_TWO)
        self.assertEqual(audit.tally(word),(11,62,2))
        audit.replay(word)
        audit.replay(word,expanded=True)
        self.assertEqual(audit.witness_receipt(word)['unit_tariff'],2778)
        self.assertEqual(2778*2,2744+2812)
        self.assertEqual(73+2*Fraction(1,2),74)

    def test_tariff_domains_switch_and_midpoint(self):
        for c in (Fraction(1,7),1,38,Fraction(103,11)):
            for ratio in (Fraction(1,100),Fraction(1,2),Fraction(7,8),100):
                x = c*ratio
                expected = 72*c+4*x if ratio<=Fraction(1,2) else 74*c
                self.assertEqual(audit.best_price(c,x),expected)
                self.assertGreaterEqual(73*c+2*x,expected)
        for c,x in ((0,1),(1,0),(-1,2),(True,1),(1,True),(1.0,1)):
            with self.assertRaises(ValueError): audit.best_price(c,x)
        self.assertEqual(audit.best_price(38,2),2744)
        # Exact cost-plane identity, independently of the odd-query control above.
        self.assertEqual([2*73,2*2],[72+74,4+0])

    def test_unpaid_xor_and_dispatch_receipts(self):
        for delta in (4,8):
            changed = copy.deepcopy(self.result)
            changed['witnesses']['four_x']['unit_tariff'] -= delta
            with self.assertRaisesRegex(ValueError,'mismatch'):
                audit.same(changed,self.result,'unpaid bill')

    def test_changed_histogram_rejected(self):
        changed = copy.deepcopy(self.result)
        changed['nine_points']['max_coverage'] = 32
        with self.assertRaises(ValueError): audit.same(changed,self.result,'false cover')

    def test_generator_side_failures_before_receipt_comparison(self):
        old_lower = audit.lower
        old_witness = audit.witness_receipt
        old_projection = audit.source_projection
        old_reads = audit.minimum_reads
        old_retained = audit.retained_word
        pairing_records = list(audit.pairing_words())
        changed_path = list(audit.PATH_FOUR); changed_path[5] ^= 1

        def wrong_nodes(word):
            leaves,nodes = old_lower(word)
            return leaves,nodes-1

        def unpaid(word,field):
            result = old_witness(word)
            result['unit_tariff'] -= result[field]
            return result

        def omitted_readout(schedule):
            word = old_retained(schedule)
            del word[next(i for i,g in enumerate(word) if g[0]=='R')]
            return word

        mutants = [
            ('lower',wrong_nodes,'recursive invoice'),
            ('witness_receipt',lambda word:unpaid(word,'source_xors'),'fixture prices'),
            ('witness_receipt',lambda word:unpaid(word,'root_instructions'),'fixture prices'),
            ('pairing_words',lambda:iter(pairing_records[1:]),'pairing histogram'),
            ('source_projection',lambda word:old_projection(word[:-1]) if word else old_projection(word),'source-restoration census'),
            ('minimum_reads',lambda t:old_reads(t+1),'small-query capacity'),
            ('PATH_FOUR',tuple(changed_path),'missing paired-readout mask'),
            ('retained_word',omitted_readout,'dirty-input map'),
        ]
        for attribute,changed,error in mutants:
            with self.subTest(attribute=attribute,error=error):
                with mock.patch.object(audit,attribute,changed):
                    # No RESULT.json comparison is invoked here: production
                    # mathematical/billing invariants must themselves reject.
                    with self.assertRaisesRegex(ValueError,error):
                        audit.build_result()

    def test_legal_longer_words_restore_and_are_fully_paid(self):
        original = audit.witness_receipt(self.word)
        for gate,cost in ((('Q',0),76),(('R',1),76),(('X',0,1),4)):
            with self.subTest(gate=gate):
                result = audit.witness_receipt(self.word+[gate,gate])
                self.assertEqual(result['unit_tariff']-original['unit_tariff'],cost)

    def test_no_inherited_invoice_consumption(self):
        data = audit.load_input()
        data['lowered'] = {}
        data['five_source_comparators'] = {'column_stars':-1,'row_stars':-1}
        # Deliberately in-memory seam only; normal load_input still enforces
        # the hash on all certificate bytes, including unused predecessor data.
        with mock.patch.object(audit,'load_input',lambda package=HERE:data):
            audit.same(audit.build_result(),self.result,'root-word-only dependency')

    def test_gate_domain_rejections(self):
        for gate in (('DUO',0,1),('X',1,1),('X',1,5),('R',0),('Q',True),('Q',5)):
            with self.assertRaises(ValueError): audit.tally([gate])
        with self.assertRaises(ValueError): audit.path_word((0,1,0))
        with self.assertRaises(ValueError): audit.path_word((0,1,2))

    def test_json_duplicate_and_type_controls(self):
        for data in ('{"a":1,"a":1}','{"a":NaN}','{"x":{"a":0,"a":1}}'):
            with self.assertRaises(ValueError): audit.read_json(data)
        for changed in (True,1.0):
            with self.assertRaises(ValueError): audit.same({'x':1},{'x':changed},'typed receipt')


class ExportControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'export'
        self.package = self.root/'research/mutable-source-uniform-tariff'
        self.package.mkdir(parents=True)
        for name in ('verify.py','RESULT.json'):
            shutil.copyfile(HERE/name,self.package/name)
        source = self.root/audit.INPUT_PATH
        source.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(HERE.parent.parent/audit.INPUT_PATH,source)

    def run_cli(self,*args,ok=True):
        before = hashes(self.root)
        run = subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*map(str,args)],
                             cwd=self.tmp.name,timeout=30,capture_output=True,text=True)
        if ok:
            self.assertEqual(run.returncode,0,run.stderr)
        else:
            self.assertNotEqual(run.returncode,0,run.stdout)
        self.assertEqual(hashes(self.root),before,'CLI modified source export')
        return run

    def test_clean_read_only_optimized_export(self):
        self.run_cli()

    def test_input_corruption_and_missing(self):
        path = self.root/audit.INPUT_PATH
        original = path.read_bytes()
        path.write_bytes(original+b' ')
        self.run_cli(ok=False)
        path.unlink()
        self.run_cli(ok=False)

    def test_input_symlink(self):
        path = self.root/audit.INPUT_PATH
        external = Path(self.tmp.name)/'same.json'
        shutil.move(path,external)
        path.symlink_to(external)
        self.run_cli(ok=False)

    def test_stale_missing_duplicate_and_typed_receipts(self):
        path = self.package/'RESULT.json'
        original = audit.read_json(path.read_bytes())
        for field,value in (('schema_version',True),('schema_version',1.0),('theorem','wrong')):
            bad = copy.deepcopy(original); bad[field]=value
            path.write_text(json.dumps(bad))
            self.run_cli(ok=False)
        path.write_text('{"schema_version":1,"schema_version":1}')
        self.run_cli(ok=False)
        path.unlink()
        self.run_cli(ok=False)

    def test_explicit_regeneration_and_internal_destination(self):
        output = Path(self.tmp.name)/'fresh.json'
        self.run_cli('--write-receipt',output)
        self.assertEqual(output.read_bytes(),(HERE/'RESULT.json').read_bytes())
        self.run_cli('--write-receipt',self.package/'RESULT.json',ok=False)
        self.run_cli('--write-receipt',self.root/'elsewhere.json',ok=False)


if __name__ == '__main__':
    unittest.main(verbosity=2)

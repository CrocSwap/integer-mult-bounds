#!/usr/bin/env python3
"""Targeted preparation/ledger tests. No all-column scalar replay is invoked."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import source_loader
import raw_ledger

HERE=Path(__file__).resolve().parent
PR210=HERE/'source_inputs/pr210'
BASE=HERE/'source_inputs/base_bit'

class IntegrityControls(unittest.TestCase):
    def test_all_public_input_hashes(self):
        _,_,pins=source_loader.check_sources(PR210,BASE)
        self.assertEqual(sum(map(len,pins.values())),22)
    def test_corrupt_input_rejected_before_import(self):
        target=(PR210/source_loader.PR210_PACKAGE/'frames/opframe-bases.json').resolve()
        original=Path.read_bytes
        def corrupt(path):
            data=original(path)
            return data+b'\n' if path.resolve()==target else data
        with patch.object(Path,'read_bytes',corrupt):
            with self.assertRaisesRegex(ValueError,'source hash mismatch'):
                source_loader.check_sources(PR210,BASE)
    def test_missing_input_rejected(self):
        target=(PR210/source_loader.PR210_PACKAGE/'newg/schedule.json').resolve()
        original=Path.read_bytes
        def missing(path):
            if path.resolve()==target:raise FileNotFoundError(str(path))
            return original(path)
        with patch.object(Path,'read_bytes',missing):
            with self.assertRaises(FileNotFoundError):source_loader.check_sources(PR210,BASE)
    def test_optimized_execution_rejected(self):
        proc=subprocess.run([sys.executable,'-O','-B',str(HERE/'source_loader.py'),'--help'],capture_output=True,text=True)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing optimized',proc.stderr)

class SemanticControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=source_loader.prepare(PR210,BASE)
        cls.fingerprint=source_loader.semantic_fingerprint(cls.context)
        cls.expected=json.loads((HERE/'expected_semantics.json').read_text())
        cls.ledger=raw_ledger.reconstruct(cls.context)
    def test_exact_semantic_fixture(self):
        self.assertEqual(self.fingerprint,self.expected)
    def test_no_scalar_replay_loaded(self):
        self.assertNotIn('replay',self.context)
        self.assertIn('SOURCE_TEXT',self.context)
    def test_wrong_gauge_order_detected(self):
        w=self.context['W'];before=w.order[:]
        try:
            w.order[0],w.order[1]=w.order[1],w.order[0]
            self.assertNotEqual(source_loader.semantic_fingerprint(self.context)['hashes']['gauge_read_order'],self.expected['hashes']['gauge_read_order'])
        finally:w.order[:]=before
    def test_wrong_partner_delivery_detected(self):
        e=self.context['W'].k['entries'][0];before=e['deliver_after_root']
        try:
            e['deliver_after_root']=before+1
            changed=source_loader.semantic_fingerprint(self.context)['hashes']
            self.assertNotEqual(changed['partner_chronology'],self.expected['hashes']['partner_chronology'])
            self.assertNotEqual(changed['partner_lookup'],self.expected['hashes']['partner_lookup'])
        finally:e['deliver_after_root']=before
    def test_raw_ledger_fixture(self):
        expected=json.loads((HERE/'expected_ledger.json').read_text())
        for key,value in expected.items():self.assertEqual(self.ledger[key],value,key)
    def test_all_center_and_completion_calls_paid(self):
        self.assertEqual(self.ledger['paid_center_copy_histogram'],{'22':24})
        profile=self.ledger['five_stage_profile']
        self.assertEqual((profile['calls'],profile['rank_mass'],profile['deficit'],profile['maxchild']),(495304,2837560,4400,100))
        self.assertEqual({r:profile['histogram'][r] for r in ['60','65','90','100']},{'60':18,'65':48,'90':13,'100':2200})

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr210-root',type=Path,default=PR210)
    parser.add_argument('--base-bit-root',type=Path,default=BASE)
    parser.add_argument('--pins-only',action='store_true')
    args=parser.parse_args();PR210=args.pr210_root;BASE=args.base_bit_root
    suite=unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrityControls))
    if not args.pins_only:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SemanticControls))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())

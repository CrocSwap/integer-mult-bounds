"""Reject incomplete X4 phase/admission/price evidence after valid ancestry."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
from unittest.mock import patch
import unittest
from test_frontier741_bindings import Composition as ParentComposition

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify_frontier799_bindings as binding

class X4Composition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ParentComposition.setUpClass()
        cls.parent=ParentComposition
        cls.root=cls.parent.root
        cls.ancestor=cls.root/'ancestor';cls.ancestor.mkdir()
        (cls.ancestor/'bit').symlink_to(cls.parent.bit,target_is_directory=True)
        (cls.ancestor/'complex').symlink_to(cls.parent.complex,target_is_directory=True)
        with tarfile.open(ROOT/'research/community-frontier799-audit/pr799-replay.tar.gz') as archive:
            for member in archive:
                dest=(cls.root/member.name).resolve()
                if not member.isfile() or not dest.is_relative_to(cls.root):raise ValueError('Invalid replay member')
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(archive.extractfile(member).read())
        cls.native=cls.root/'pr799-native-fresh';cls.global_dir=cls.root/'pr799-global-fresh'
        cls.evidence=ROOT/'research/community-frontier799-audit/logs'
    @classmethod
    def tearDownClass(cls):cls.parent.tearDownClass()
    def check(self):
        return binding.check(self.ancestor,self.native,self.global_dir,
                             self.evidence/'pr799-independent-local.json',self.evidence/'pr799-independent-price.json')
    def test_complete_bound_replay(self):
        self.assertEqual(self.check()['kappa'],binding.KAPPA)
    def test_incomplete_or_changed_evidence(self):
        cases=[
            (self.native/'STEPS.json',lambda x:x.pop(),'Complete X4 native stages'),
            (self.native/'controls/COLD-END-CONTROLS.json',lambda x:x['rejected'].pop(),'Endpoint controls'),
            (self.native/'local/CLIFFORD-REVIEW.json',lambda x:x.update(all_child_equalities_include_global_phase=False),'Complete phase check'),
            (self.global_dir/'ADMISSION-CONTROLS.json',lambda x:x['rejected_controls'].pop(),'Admission controls'),
            (self.global_dir/'ASSEMBLY.json',lambda x:x.update(kappa='1/100'),'Selected X4 kappa'),
            (self.global_dir/'ASSEMBLY.json',lambda x:x['outer'].update({next(iter(x['outer'])):'0'}),'Strict outer constraints'),
            (self.evidence/'pr799-independent-price.json',lambda x:x['prices']['native']['outer_with_bit'].update(kappa='1/100'),'Independent price'),
        ]
        original=binding.read
        for path,mutate,reason in cases:
            value=deepcopy(original(path));mutate(value)
            def reader(p):return value if p==path else original(p)
            with self.subTest(reason=reason),patch.object(binding,'read',reader):
                with self.assertRaisesRegex(ValueError,reason):self.check()

if __name__=='__main__':unittest.main()

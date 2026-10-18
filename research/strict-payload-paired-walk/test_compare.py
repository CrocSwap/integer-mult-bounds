#!/usr/bin/env python3
"""Retain predecessor controls and test the adapter boundary. Apache-2.0.

ywz65, with substantial OpenAI Codex assistance.
"""
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('paired_verifier',HERE/'verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
fast,retained=verify.setup()
oldtests=verify.module(verify.ROOT/verify.OLD/'test_compare.py',{'compare':fast,'verify':retained})
# Their CLI fixture now exercises this adapter, while source checks retain their
# original bound-input function and root. No predecessor source is rewritten.
oldtests.HERE=HERE
ComparisonControls=oldtests.ComparisonControls


class AdapterControls(unittest.TestCase):
    def test_source_change_invalidates_before_execution(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);path=root/fast.SOURCE;path.parent.mkdir(parents=True)
            shutil.copyfile(verify.ROOT/fast.SOURCE,path)
            fast.load_source(root)
            path.write_bytes(path.read_bytes()+b'\nraise RuntimeError("must not execute")\n')
            with self.assertRaisesRegex(ValueError,'SHA256 differs'):
                fast.load_source(root)

    def test_success_does_not_build_tagged_trees(self):
        oldtree=fast.source.tree
        def forbidden(*args,**kwargs):
            raise AssertionError('positive traversal allocated tagged tree')
        fast.source.tree=forbidden
        try:
            self.assertEqual(fast.classify('a.json',b'{"v":[1,true,1.00]}',b' {"v":[1,true,1e0]}'),{'cls':'json-format'})
            ra,rb=fast.Roots([('W','/a')]),fast.Roots([('W','/b')])
            self.assertEqual(fast.classify('a.json',b'{"/a/f":1}',b'{"/b/f":1}',ra,rb),{'cls':'json-relocated'})
            self.assertEqual(fast.classify('a.json',b'{"t":1}',b'{"t":2.0}',timing_paths=[('t',)]),{'cls':'json-diff','verdict':'declared-timing'})
        finally:
            fast.source.tree=oldtree

    def test_negative_result_uses_original_diagnostics(self):
        args=('a.json',b'{"unknown":{"values":[0,1]}}',b'{"unknown":{"values":[0,true]}}')
        self.assertEqual(fast.classify(*args),fast.original_classify(*args))
        self.assertEqual(fast.classify(*args)['first_difference']['path'],[['string','unknown'],['string','values'],1])

    def test_masks_use_both_original_key_paths(self):
        ra,rb=fast.Roots([('W','/a')]),fast.Roots([('W','/b')])
        a=fast.read_json(b'{"/a":1,"/b":2}')
        b=fast.read_json(b'{"/b":3,"/a":2}')
        # The '/a' mask exists on both inputs but denotes different normalized
        # keys. It cannot erase the different path-tagged value on only one side.
        self.assertFalse(fast.paired(a,b,ra,rb,frozenset({('/a',)}),frozenset({('/a',)})))
        self.assertFalse(fast.accepted(fast.classify('a.json',b'{"/a":1,"/b":2}',b'{"/b":3,"/a":2}',ra,rb,[('/a',)])))

    def test_full_result_differential_detects_python_equality_mutant(self):
        previous=fast.paired
        fast.paired=lambda a,b,*args: a==b
        try:
            args=('a.json',b'{"x":true}',b'{"x":1}')
            self.assertNotEqual(fast.classify(*args),fast.original_classify(*args))
        finally:
            fast.paired=previous

    def test_timing_validation_still_rejects_identical_invalid_data(self):
        for value in (b'true',b'-1',b'"1"',b'null'):
            raw=b'{"t":'+value+b'}'
            self.assertEqual(fast.classify('a.json',raw,raw,timing_paths=[('t',)])['cls'],'invalid')


if __name__=='__main__':
    unittest.main(verbosity=2)

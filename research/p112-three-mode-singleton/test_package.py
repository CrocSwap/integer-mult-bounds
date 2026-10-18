#!/usr/bin/env python3
"""Positive replay and external corruption controls, active under Python -O.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]


class CorruptionControls(unittest.TestCase):
    def execute(self, script, *args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(script),*map(str,args)],
                              text=True,capture_output=True,timeout=120)

    def test_positive_independent_replay(self):
        result=self.execute(PACKAGE/'independent_check.py')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS_INDEPENDENT_SINGLETON_THREE_MODE',result.stdout)

    def corrupted_certificate(self, mutate, reason):
        receipt=json.loads((PACKAGE/'CERTIFICATE.json').read_text())
        mutate(receipt)
        with tempfile.TemporaryDirectory(prefix='singleton-control-') as tmp:
            path=Path(tmp)/'bad.json';path.write_text(json.dumps(receipt))
            result=self.execute(PACKAGE/'independent_check.py','--certificate',path)
        self.assertNotEqual(result.returncode,0,'corrupt receipt was accepted')
        self.assertIn(reason,result.stderr)

    def test_missing_stratum(self):
        self.corrupted_certificate(lambda r:r['strata'].pop(),'support coverage')

    def test_wrong_support_representative(self):
        self.corrupted_certificate(lambda r:r['strata'][0].update(coefficient=[0,0,0]),
                                   'coefficient-to-support binding')

    def test_changed_pair_rank(self):
        def mutate(r):
            row=r['strata'][0]['survivor_pair_ranks'][0]
            r['strata'][0]['survivor_pair_ranks'][0]='6'+row[1:]
        self.corrupted_certificate(mutate,'full survivor pairing table')

    def test_false_copy_floor(self):
        self.corrupted_certificate(lambda r:r['summary'].update(sharp_whole_copy_sum=63),'claimed floor')

    def test_invalid_transport(self):
        self.corrupted_certificate(lambda r:r['transports'][0].update(permutation=[0]*8),
                                   'coordinate permutation')

    def corrupted_source(self, missing_pin):
        with tempfile.TemporaryDirectory(prefix='singleton-source-') as tmp:
            root=Path(tmp);package=root/'research'/'p112-three-mode-singleton'
            package.mkdir(parents=True)
            shutil.copy2(PACKAGE/'verify.py',package/'verify.py')
            pins=json.loads((PACKAGE/'SOURCES.json').read_text())
            for row in pins['files']:
                if row['usage']=='input':
                    dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(ROOT/row['path'],dest)
            geometry='research/p112-single-lift/geometry.py'
            if missing_pin:
                pins['files']=[r for r in pins['files'] if r['path']!=geometry]
            else:
                with (root/geometry).open('a') as f:f.write('\n# deliberate corruption\n')
            (package/'SOURCES.json').write_text(json.dumps(pins))
            result=self.execute(package/'verify.py')
        self.assertNotEqual(result.returncode,0,'corrupt source accepted')
        self.assertIn('incomplete live source inventory' if missing_pin else 'source SHA256',result.stderr)

    def test_missing_geometry_pin(self):
        self.corrupted_source(True)

    def test_changed_geometry_bytes(self):
        self.corrupted_source(False)


if __name__=='__main__': unittest.main()

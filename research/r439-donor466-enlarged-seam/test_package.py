#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""Premise, semantic-payload and source-binding rejection controls."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


def module(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


V=module('verify')
O=module('oracle')


class EnlargedSeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=V.pins()
        cls.word=cls.inputs[V.WORD]
        cls.certificate=json.loads((HERE/'CERTIFICATE.json').read_text())
        cls.actual=V.compute(cls.word,cls.inputs[V.PRIOR])

    def test_positive_certificate(self):
        V.validate_certificate(self.certificate,self.actual)
        self.assertTrue(O.audit(self.certificate,self.word))

    def test_rank_preserving_inverse_support_corruption(self):
        bad=copy.deepcopy(self.certificate)
        bad['wires'][0]['inverse_source_outputs'].remove(97)
        # It still has rank four: checking rank alone would miss this wrong coefficient.
        self.assertEqual(O.integer_rank([self.word['lines'][i] for i in bad['wires'][0]['inverse_source_outputs']]),4)
        with self.assertRaisesRegex(ValueError,'certificate mismatch'):
            V.validate_certificate(bad,self.actual)
        with self.assertRaisesRegex(ValueError,'source-only witness record'):
            O.audit(bad,self.word,atlas=False)

    def test_dependent_witness_corruption(self):
        bad=copy.deepcopy(self.certificate)
        bad['wires'][0]['source_only_witness'][-1]=19
        self.assertEqual(O.integer_rank([self.word['lines'][i] for i in bad['wires'][0]['source_only_witness']]),3)
        with self.assertRaises(ValueError):
            V.validate_certificate(bad,self.actual)
        with self.assertRaises(ValueError):
            O.audit(bad,self.word,atlas=False)

    def test_underpriced_enlarged_invoice(self):
        bad=copy.deepcopy(self.certificate)
        # Reusing the old B508-only bill omits the newly included A promotions.
        bad['minimum_eleven_wire_profile']={'2':6,'3':2}
        bad['minimum_eleven_wire_rank_mass']=18
        with self.assertRaises(ValueError):
            V.validate_certificate(bad,self.actual)
        with self.assertRaisesRegex(ValueError,'minimum invoice'):
            O.audit(bad,self.word,atlas=False)

    def test_complete_cut_coverage(self):
        bad=copy.deepcopy(self.certificate)
        bad['earlier_cut_atlas']['cuts']=1991
        bad['earlier_cut_atlas']['wire_cut_checks']=21901
        with self.assertRaises(ValueError):
            V.validate_certificate(bad,self.actual)
        with self.assertRaisesRegex(ValueError,'complete cut atlas'):
            O.audit(bad,self.word)

    def test_copy_scatter_is_not_omitted(self):
        changed=copy.deepcopy(self.word)
        i=next(i for i,ss in enumerate(changed['scatter']) if ss)
        changed['scatter'][i].pop()
        # The source/helper restriction is unchanged, but the all-wire boundary is wrong.
        actual=V.compute(changed,self.inputs[V.PRIOR])
        self.assertEqual(actual['wires'],self.certificate['wires'])
        self.assertNotEqual(actual['full_endpoint_rows_sha256'],self.certificate['full_endpoint_rows_sha256'])
        with self.assertRaises(ValueError):
            V.validate_certificate(self.certificate,actual)
        with self.assertRaisesRegex(ValueError,'forward endpoint'):
            O.audit(self.certificate,changed,atlas=False)

    def test_contract_changes_reject(self):
        for kind in ('source_write','target_feedback'):
            changed=copy.deepcopy(self.word)
            if kind=='source_write':
                changed['A'][0][1]=19
            else:
                changed['A'][0][2]=[111]
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    V.validate_contract(changed)
                with self.assertRaises(ValueError):
                    O.audit(self.certificate,changed,atlas=False)

    def test_source_bytes_reject(self):
        with tempfile.TemporaryDirectory(prefix='pin-control-',dir=HERE) as tmp:
            root=Path(tmp)
            path=root/V.WORD
            path.parent.mkdir(parents=True)
            path.write_bytes((V.ROOT/V.WORD).read_bytes()+b'\0')
            with self.assertRaisesRegex(ValueError,'source SHA256'):
                V.pins(root)

    def test_forward_only_misses_exception(self):
        entry=self.certificate['wires'][0]
        self.assertEqual(O.integer_rank([self.word['lines'][i] for i in entry['forward_sources']]),1)
        self.assertEqual(O.integer_rank([self.word['lines'][i] for i in entry['inverse_source_outputs']]),4)

    def test_source_preserving_nonlinear_prefix_and_dirty_auxiliary(self):
        # Two sources x0,x1, one helper h. All 16 source-controlled helper flips
        # preserve both source coordinates. B(x0,x1,h)=(x0+h,x1+h,h).
        # All 256 source/helper-controlled dirty-auxiliary flips are allowed.
        checks=0
        for preparation in range(16):
            for garbage in range(256):
                outputs=set()
                for word in range(16):
                    x0,x1,h,a=((word>>i)&1 for i in range(4))
                    prepared=h^((preparation>>(x0+2*x1))&1)
                    y0,y1,yh=x0^prepared,x1^prepared,prepared
                    ya=a^((garbage>>(word&7))&1)
                    outputs.add(y0+2*y1+4*yh+8*ya)
                    self.assertEqual((y0^yh,y1^yh),(x0,x1))
                    checks+=1
                self.assertEqual(len(outputs),16)
        self.assertEqual(checks,65536)
        # A prefix that writes a source destroys the claimed source-row identity.
        x0,x1,h=0,0,1
        changed_x0=x0^h
        y0,yh=changed_x0^h,h
        self.assertNotEqual(y0^yh,x0)


if __name__=='__main__':
    unittest.main()

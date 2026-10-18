"""Exact native phase, owner-action and typed-receipt regressions."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent

class NativeTests(unittest.TestCase):
    def test_native_phase_and_owner_controls(self):
        p=subprocess.run([sys.executable,'-I','-O','-B',str(HERE/'verify.py'),'--controls'],
                         capture_output=True,text=True,encoding='utf-8',timeout=30)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertIn('PASS_QUARTER_NATIVE_CONTROLS',p.stdout)

    def test_native_kernel_witness_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix='.receipt-',dir=HERE) as tmp:
            path=Path(tmp)/'receipt.json'
            args=[sys.executable,'-I','-O','-B',str(HERE/'verify.py')]
            p=subprocess.run(args+['--write',str(path)],capture_output=True,
                             text=True,encoding='utf-8',timeout=300)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            d=json.loads(path.read_bytes())
            self.assertEqual(d['native_witness']['all_forward_centre_inputs_zero'],True)
            self.assertEqual(d['native_witness']['all_forward_centre_outputs_zero'],True)
            self.assertEqual(d['native_witness']['backward_pre_channel0'],['1/4','0'])
            self.assertIn('native_controls',d)
            self.assertIn('cover_invariant_kernel_positive',d['native_controls'])
            self.assertIn('backward_transport_phase_rejected',d['native_controls'])
            self.assertIn('wrong_owner_location_rejected',d['native_controls'])
            for wrong in (['0','0'],[0.25,0]):
                d['native_witness']['backward_pre_channel0']=wrong
                path.write_text(json.dumps(d),encoding='utf-8')
                p=subprocess.run(args+['--receipt',str(path)],capture_output=True,
                                 text=True,encoding='utf-8',timeout=300)
                self.assertNotEqual(p.returncode,0)
                self.assertIn('receipt mismatch',p.stdout+p.stderr)

if __name__=='__main__':
    unittest.main()

"""Controls catch incomplete joining, serial-vs-simultaneous families, and receipts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from runpy import run_path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class CycleTests(unittest.TestCase):
    def test_deadline_rejects_all_blocked_and_empty_censuses(self):
        api=run_path(str(HERE/'verify.py'))
        clock=[0]
        model=api['toy']()
        def closed_landing(role,destination):
            clock[0]=301
            return 'outside_strict_source_event_window'
        model.window_active_rejection=closed_landing
        with patch.object(api['time'],'monotonic',side_effect=lambda:clock[0]):
            with self.assertRaisesRegex(ValueError,'time budget exceeded; census incomplete'):
                api['enumerate_cycles'](model,seconds=300)
        model=api['toy']()
        model.roles=[]
        ticks=iter((0,301))
        with patch.object(api['time'],'monotonic',side_effect=lambda:next(ticks,301)):
            with self.assertRaisesRegex(ValueError,'time budget exceeded; census incomplete'):
                api['enumerate_cycles'](model,seconds=300)

    def test_rank_key_roundtrip_keeps_value_types(self):
        canonical=run_path(str(HERE/'verify.py'))['canonical']
        result={'profile':{1:3,7:2,48:1}}
        self.assertEqual(canonical(result),canonical(json.loads(json.dumps(result))))
        self.assertNotEqual(canonical({'count':1}),canonical({'count':1.0}))
        self.assertNotEqual(canonical({'count':1}),canonical({'count':True}))

    def test_exact_toy_cycle_and_simultaneous_family_controls(self):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE/'verify.py'),
                                 '--controls'], text=True, encoding='utf-8',
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn('PASS_CROSSCALL_CYCLE_CONTROLS', result.stdout)

    def test_complete_census_and_type_strict_receipt_rejection(self):
        with tempfile.TemporaryDirectory(prefix='.control-',dir=HERE) as temp:
            path = Path(temp)/'new.json'
            args = [sys.executable,'-I','-O','-B',str(HERE/'verify.py')]
            result = subprocess.run(args+['--write',str(path)],text=True,encoding='utf-8',
                                    capture_output=True,timeout=180)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            data = json.loads(path.read_bytes())
            self.assertEqual(data['census']['cross_call_arithmetic_candidates'],21886)
            self.assertEqual(data['census']['window_joined'],0)
            self.assertEqual(data['independent_direct']['candidates'],21886)
            self.assertIn('constant_window_blocks',data)
            self.assertEqual([p['rejected_cycles'] for p in data['constant_window_blocks']],
                             [17567,4319])
            self.assertEqual(data['constant_window_blocks'][0]['blocked_role'],[1,15,226])
            self.assertEqual(data['constant_window_blocks'][1]['blocked_role'],[7,14,296])
            for wrong in (21885,21886.0):
                with self.subTest(wrong=wrong):
                    data['census']['cross_call_arithmetic_candidates'] = wrong
                    path.write_text(json.dumps(data),encoding='utf-8')
                    result = subprocess.run(args+['--receipt',str(path)],text=True,
                        encoding='utf-8',capture_output=True,timeout=180)
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn('receipt mismatch',result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()

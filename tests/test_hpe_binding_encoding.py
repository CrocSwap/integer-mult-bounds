"""The emitted-recipe CLI must decode its frozen Lean literals as UTF-8."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/verify_hpe_lean_binding.py'


class HPEEncodingTests(unittest.TestCase):
    def test_actual_cli_under_cp1252_keeps_recipe_failure_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture, receipt = Path(directory) / 'run', Path(directory) / 'receipt.json'
            fixture.mkdir()
            # Build a declared 38-helper/three-pair fixture through the UTF-8
            # positive control. This tests decoding/binding, not a physical word.
            build = '''import gzip,json,sys
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import verify_hpe_lean_binding as h
pairs = list(h.literal_pairs().items()); frames=[]; recipes={}
for i, ((entrance,terminal), recipe) in enumerate(pairs):
 frames.extend([entrance,terminal]); recipes[f'{2*i}:{2*i+1}']={**recipe,'rank':7}
word={'frames':frames,'start':[2*(i%3) for i in range(38)],
      'final':[2*(i%3)+1 for i in range(38)],
      'tail':[['add',i,38,-1,1,2*(i%3)+1] for i in range(38)]}
out=Path(sys.argv[2]);(out/'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(json.dumps(word).encode()))
(out/'RESIDUAL-ADAPTERS.json').write_text(json.dumps({'recipes':recipes}),encoding='utf-8')
'''
            setup = subprocess.run([sys.executable, '-c', build, str(ROOT / 'scripts'), str(fixture)],
                                   env={**os.environ, 'PYTHONUTF8': '1'}, capture_output=True, timeout=30)
            self.assertEqual(setup.returncode, 0, setup.stderr)
            # Force the same default even on a UTF-8 host; explicit encodings
            # survive. runpy executes the real CLI entry point and main checks.
            driver = '''import io,runpy,sys
from unittest.mock import patch
original=io.open
def legacy(file,mode='r',buffering=-1,encoding=None,*args,**kwargs):
 if 'b' not in mode and encoding is None: encoding='cp1252'
 return original(file,mode,buffering,encoding,*args,**kwargs)
sys.argv=sys.argv[1:]
with patch('io.open',side_effect=legacy): runpy.run_path(sys.argv[0],run_name='__main__')
'''
            argv = [sys.executable, '-c', driver, str(SCRIPT), str(fixture), '--out', str(receipt)]
            result = subprocess.run(argv, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(receipt.read_bytes())
            self.assertEqual(report['instances'][0]['helpers'], 38)
            self.assertEqual(report['instances'][0]['pairs'], 3)
            self.assertEqual(report['instances'][0]['rejected'], ['left_phase', 'right_phase'])
            if os.name == 'nt':
                # Also exercise the native Windows locale with no I/O patch.
                native = subprocess.run([sys.executable, str(SCRIPT), str(fixture), '--out', str(receipt)],
                                        env={**os.environ, 'PYTHONUTF8': '0'}, capture_output=True, timeout=30)
                self.assertEqual(native.returncode, 0, native.stderr)
            adapters = fixture / 'RESIDUAL-ADAPTERS.json'
            data = json.loads(adapters.read_bytes())
            next(iter(data['recipes'].values()))['left']['phase'] ^= 1
            adapters.write_text(json.dumps(data), encoding='utf-8')
            bad = subprocess.run(argv, capture_output=True, timeout=30)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn(b'Emitted recipe differs from Lean', bad.stderr)


if __name__ == '__main__':
    unittest.main()

import subprocess
import sys
import unittest
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

class SemanticTests(unittest.TestCase):
    def test_smallest_and_mixed_cold_hyperplanes(self):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE/'verify.py'), '--probe'],
            text=True, encoding='utf-8', capture_output=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn('PASS_COLD_HYPERPLANE_PROBE normals=1,511', result.stdout)

    def test_omitted_hyperplane_or_unsafe_radix_receipt_is_rejected(self):
        original = json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(prefix='.control-', dir=HERE) as temp:
            for field, wrong in [('hyperplanes',510), ('packed_radix',2),
                                 ('hyperplanes',511.0), ('normal_range',[True,511])]:
                with self.subTest(field=field):
                    data = json.loads(json.dumps(original)); data[field] = wrong
                    path = Path(temp)/f'{field}.json'
                    path.write_text(json.dumps(data),encoding='utf-8')
                    result = subprocess.run([sys.executable,'-I','-O','-B',str(HERE/'verify.py'),'--result',str(path)],
                        text=True,encoding='utf-8',capture_output=True,timeout=180)
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn('result receipt mismatch',result.stdout+result.stderr)

if __name__ == '__main__':
    unittest.main()

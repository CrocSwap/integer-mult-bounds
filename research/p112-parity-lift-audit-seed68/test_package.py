"""Receipt and source-binding controls for the P112 audit. Apache-2.0."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def replay(script, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *map(str, args)],
                          cwd=script.parent, text=True, capture_output=True, check=False)


class PackageTests(unittest.TestCase):
    def test_relocated_receipt_and_corruptions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / 'research' / HERE.name
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json', 'CERTIFICATE.json'):
                shutil.copyfile(HERE / name, package / name)
            source = Path(json.loads((package / 'SOURCES.json').read_text())['geometry'])
            (root / source).parent.mkdir(parents=True)
            shutil.copyfile(ROOT / source, root / source)
            script = package / 'verify.py'

            valid = replay(script)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertIn('records=4194304 minimum=64', valid.stdout)

            certificate = json.loads((package / 'CERTIFICATE.json').read_text())
            certificate['copy_cost_histogram']['64'] += 1
            (package / 'corrupted.json').write_text(json.dumps(certificate))
            rejected = replay(script, '--certificate', package / 'corrupted.json')
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('saved certificate differs', rejected.stderr)

            pins_path = package / 'SOURCES.json'
            original_pins = pins_path.read_bytes()
            pins = json.loads(original_pins)
            pins['inputs'][str(source)]['git_blob'] = '0' * 40
            pins_path.write_text(json.dumps(pins))
            rejected = replay(script)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('source Git blob', rejected.stderr)

            pins_path.write_bytes(original_pins)
            with (root / source).open('ab') as handle:
                handle.write(b'\n')
            rejected = replay(script)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('source SHA256', rejected.stderr)


if __name__ == '__main__':
    unittest.main()

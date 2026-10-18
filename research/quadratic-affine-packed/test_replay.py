"""Fail-closed source and CLI controls for the optional audit adapter."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay import ROOT, check_sources


class ReplayGuards(unittest.TestCase):
    def test_all_pins_and_source_mutations(self):
        manifest = check_sources()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in manifest['files']:
                dest = root / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, dest)
            self.assertEqual(check_sources(root), manifest)
            for relative in ('scripts/experiments/quadratic_affine.py',
                             'scripts/experiments/quadratic_affine_witnesses.json',
                             'certificates/quadratic-affine-vectors.json',
                             'upstream/manifest.json'):
                path = root / relative
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with self.assertRaisesRegex(ValueError, 'Pinned input changed'):
                    check_sources(root)
                path.write_bytes(original)

    def test_optimized_python_is_refused(self):
        p = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'replay.py')],
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Assertions must remain enabled', p.stderr)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'existing.json'
            out.write_bytes(b'preserve this output')
            for script in ('replay.py', 'benchmark.py'):
                p = subprocess.run([sys.executable, '-I', '-B', str(HERE / script), '--out', str(out)],
                                   capture_output=True, text=True)
                self.assertNotEqual(p.returncode, 0)
                self.assertEqual(out.read_bytes(), b'preserve this output')


if __name__ == '__main__':
    unittest.main()

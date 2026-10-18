"""Fault-injection checks for the independent audit's evidence boundary."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('counter_audit', HERE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditFailures(unittest.TestCase):
    def test_literal_width_zero_and_full_wrap(self):
        self.assertEqual(audit.literal(0, 0, 0, ('S', 'B', 1)), (0, 1, 2))
        self.assertEqual(audit.literal(4, 15, 1, ('B', 0, 1)), (0, 1, 10))

    def test_omitted_return_steps_rejected(self):
        bad = {(4, 15, 1): (0, 1, 5)}
        with self.assertRaisesRegex(ValueError, 'one-call potential identity'):
            audit.summarize(4, 15, (1,), bad)

    def test_suppressed_wrap_flag_rejected(self):
        bad = {(4, 15, 1): (0, 0, 10)}
        with self.assertRaisesRegex(ValueError, 'one-call potential identity'):
            audit.summarize(4, 15, (1,), bad)

    def test_incorrect_endpoint_rejected(self):
        bad = {(4, 15, 1): (1, 1, 10)}
        with self.assertRaisesRegex(ValueError, 'one-call potential identity'):
            audit.summarize(4, 15, (1,), bad)

    def test_empty_sequence(self):
        for width in (0, 1, 4):
            row = audit.summarize(width, 0, (), {})
            self.assertEqual((row['steps'], row['runs'], row['wrap_runs']), (0, 0, 0))

    def test_source_drift_rejected_under_optimized_python(self):
        # Stage only the immutable inputs, preserving repository-relative layout.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'research/counter-reversal-audit'
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json'):
                (package / name).write_bytes((HERE / name).read_bytes())
            pins = json.loads((HERE / 'SOURCES.json').read_text())
            for source in pins['files']:
                dest = root / source
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((audit.ROOT / source).read_bytes())
            source = root / next(iter(pins['files']))
            source.write_bytes(source.read_bytes()+b'\n-- mutation control\n')
            result = subprocess.run([sys.executable, '-I', '-B', '-O', str(package/'verify.py')],
                                    capture_output=True, text=True, cwd=tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source drift:', result.stderr)


if __name__ == '__main__':
    unittest.main()

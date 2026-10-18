"""Entry-point controls for exact receipts and source-bound reuse.

Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify


def exported(temporary):
    root = Path(temporary) / 'repo';package = root / 'research' / HERE.name
    shutil.copytree(HERE, package, copy_function=shutil.copyfile)
    for item in verify.read(HERE / 'SOURCES.json')['files']:
        if item['usage'] == 'input':
            out = root / item['path'];out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parents[1] / item['path'], out)
    for p in root.rglob('*'):
        if p.is_dir():p.chmod(0o755)
    return root, package


class Controls(unittest.TestCase):
    def test_changed_receipt_at_actual_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            data = verify.read(package / 'RESULT.json');data['warm']['trace_sha256'] = '0' * 64
            (package / 'RESULT.json').write_text(json.dumps(data))
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                 cwd=tmp, capture_output=True, text=True, timeout=120)
            self.assertNotEqual(run.returncode, 0);self.assertIn('complete typed receipt differs', run.stderr)

    def test_missing_timed_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            data = verify.read(package / 'BENCHMARK.json')
            data['interleaved_pairs'][1]['evidence']['event_counts']['model'] -= 1
            (package / 'BENCHMARK.json').write_text(json.dumps(data))
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'check_benchmark.py')],
                                 cwd=tmp, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(run.returncode, 0);self.assertIn('complete timed evidence differs', run.stderr)

    def test_changed_source_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, package = exported(tmp)
            source = root / 'research/complex-local-word-ceiling/ceiling.py';source.write_bytes(source.read_bytes() + b'\n')
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                 cwd=tmp, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(run.returncode, 0);self.assertIn('source changed: engine', run.stderr)

    def test_strict_json_and_exact_trace_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            for text in ['{"x":1,"x":1}', '{"x":NaN}', '{"x":Infinity}']:
                path.write_text(text)
                with self.assertRaises(ValueError):verify.read(path)
        self.assertNotEqual(verify.freeze(1), verify.freeze(True))
        self.assertNotEqual(verify.freeze(verify.Q(0)), verify.freeze(0.0))

    def test_existing_outputs_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'keep.json';out.write_bytes(b'preserve evidence\n')
            for name, flag in [('verify.py', '--emit-result'), ('benchmark.py', '--out')]:
                run = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / name), flag, str(out)],
                                     capture_output=True, text=True, timeout=20)
                self.assertNotEqual(run.returncode, 0);self.assertIn('output already exists', run.stderr)
                self.assertEqual(out.read_bytes(), b'preserve evidence\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)

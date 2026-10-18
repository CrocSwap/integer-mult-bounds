#!/usr/bin/env python3
"""Behavioral controls for the exact consumer binding; stdlib only."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def module():
    spec = importlib.util.spec_from_file_location('consumer', HERE/'verify.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def snapshot(root):
    pins = json.loads((HERE/'SOURCES.json').read_text())['files']
    paths = {ROOT/p['path'] for p in pins if p['usage'] == 'input'}
    paths.update(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for p in paths:
        dst = root/p.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dst)


def execute(root):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(root/REL/'verify.py')],
                          cwd=root, text=True, capture_output=True, timeout=120)


class Contracts(unittest.TestCase):
    def test_source_fault_real_entry(self):
        with tempfile.TemporaryDirectory(prefix='r439-copy-contract-test-') as tmp:
            root=Path(tmp); snapshot(root)
            p=root/'research/pr589-five-helper-hosting/PROOF.md'
            p.write_bytes(p.read_bytes()+b'\nchanged premise\n')
            result=execute(root)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source SHA256',result.stderr)

    def test_missing_witness_real_entry(self):
        with tempfile.TemporaryDirectory(prefix='r439-copy-contract-test-') as tmp:
            root=Path(tmp); snapshot(root)
            (root/REL/'inputs/pr2407/WITNESS.json').unlink()
            result=execute(root)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('WITNESS.json',result.stderr)

    def test_receipt_fault_real_entry(self):
        with tempfile.TemporaryDirectory(prefix='r439-copy-contract-test-') as tmp:
            root=Path(tmp); snapshot(root)
            p=root/REL/'RESULT.json'; d=json.loads(p.read_text())
            d['copy_window']['interior_address_children']=1
            p.write_text(json.dumps(d))
            result=execute(root)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('stale result receipt',result.stderr)

    def test_guard_removal_is_detected(self):
        source=(HERE/'verify.py').read_text()
        guard="need(new['local_hash'] == expected, 'stale call program hash')"
        self.assertEqual(source.count(guard),1)
        mutant=types.ModuleType('binding_guard_removed')
        mutant.__file__=str(HERE/'verify.py')
        exec(compile(source.replace(guard,'pass  # deliberate guard-removal control'),
                     mutant.__file__,'exec'),mutant.__dict__)
        with self.assertRaisesRegex(ValueError,'control accepted: stale selected local program'):
            mutant.run()

    def test_git_free_read_only_replay(self):
        with tempfile.TemporaryDirectory(prefix='r439-copy-contract-test-') as tmp:
            root=Path(tmp); snapshot(root)
            before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            dirs=[root]+[p for p in root.rglob('*') if p.is_dir()]
            try:
                for p in root.rglob('*'):
                    if p.is_file():p.chmod(0o444)
                for p in dirs:p.chmod(0o555)
                result=execute(root)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('PASS_R439_INTERLEAVED_COPY_CONTRACT',result.stdout)
                after={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(before,after)
                self.assertFalse((root/'.git').exists())
            finally:
                for p in dirs:p.chmod(0o755)
                for p in root.rglob('*'):
                    if p.is_file():p.chmod(0o644)

    def test_restored_snapshot_countermodel(self):
        r=module().alias_control()
        self.assertEqual(r['failing_inputs'],4)
        self.assertEqual(r['witness']['final_private'],0)
        self.assertNotEqual(r['witness']['actual'],r['witness']['expected'])


if __name__ == '__main__':
    unittest.main()

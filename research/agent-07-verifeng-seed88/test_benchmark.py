"""Maintainer regression: nondeterminism cannot excuse changed receipts."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('benchmark_under_test', Path(__file__).with_name('benchmark.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class BenchmarkAcceptance(unittest.TestCase):
    def run_case(self, changed):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'tests').mkdir()
            path = root/'tests/test_example.py'
            path.touch()
            output = root/'receipt.json'
            runner = types.SimpleNamespace(module_command=lambda *a: ['unused'],
                run_modules=lambda *a, **k: [(path,0,b'changed\n' if changed else b'good\n',b'Ran 1 test in 0.002s\n')])
            runs = iter([subprocess.CompletedProcess([],0,b'good\n',b'Ran 1 test in 0.001s\n'),
                         subprocess.CompletedProcess([],0,b'random A\n',b'Ran 1 test in 0.003s\n'),
                         subprocess.CompletedProcess([],0,b'random B\n',b'Ran 1 test in 0.004s\n')])
            with patch.object(b,'ROOT',root), patch.object(b,'load_runner',return_value=runner), \
                 patch.object(b.subprocess,'run',side_effect=lambda *a,**k: next(runs)), \
                 patch.object(sys,'argv',['benchmark','--output',str(output)]), contextlib.redirect_stdout(io.StringIO()):
                if changed:
                    with self.assertRaises(SystemExit): b.main()
                else: b.main()
            self.assertTrue(output.is_file())

    def test_different_receipts_fail_even_when_same_mode_is_nondeterministic(self):
        self.run_case(True)

    def test_unittest_elapsed_time_alone_is_allowed(self):
        self.run_case(False)

if __name__ == '__main__': unittest.main()

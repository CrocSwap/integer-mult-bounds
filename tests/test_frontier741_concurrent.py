"""Concurrent supplier replay for the PR589 + PR741 ancestry.

The driver must run exactly the commands of scripts/verify_frontier741.py; only
their schedule differs. These tests tie the command lines and environment to that
script's source, and check overlap and fail-fast behaviour of the scheduler.
"""
import ast
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_frontier741_concurrent as conc

ORIGINAL = ROOT / 'scripts/verify_frontier741.py'
PY = sys.executable


def original_runs():
    """name -> command expression of every run(...) call in verify_frontier741.py."""
    main = next(n for n in ast.parse(ORIGINAL.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == 'main')
    return {call.args[0].value: call.args[1] for call in ast.walk(main)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'run'
            and call.args and isinstance(call.args[0], ast.Constant)}


def original_command(expr, work):
    return list(map(str, eval(compile(ast.Expression(expr), 'verify_frontier741.py', 'eval'),
                              {'ROOT': ROOT, 'work': work, 'sys': sys})))


class SameCommandsAsOriginal(unittest.TestCase):
    def setUp(self):
        self.work = Path('/replay/work')
        self.runs = original_runs()

    def test_original_stage_names_and_order(self):
        self.assertEqual(list(self.runs), ['bit589', 'complex741', 'bindings'])

    def test_supplier_commands_equal_original(self):
        for name, command in conc.supplier_commands(self.work):
            self.assertEqual(list(map(str, command)), original_command(self.runs[name], self.work), name)

    def test_binding_command_equals_original(self):
        self.assertEqual(list(map(str, conc.binding_command(self.work))),
                         original_command(self.runs['bindings'], self.work))

    def test_environment_matches_original(self):
        main = next(n for n in ast.parse(ORIGINAL.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'main')
        popped = next(ast.literal_eval(n.iter) for n in ast.walk(main)
                      if isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple))
        self.assertEqual(set(popped), {'PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'SW4_PIN'})
        with mock.patch.dict(os.environ, {name: '1' for name in popped}):
            env = conc.supplier_env()
        self.assertFalse(set(popped) & set(env))
        self.assertEqual(env['PYTHON'], sys.executable)
        self.assertEqual(env['PYTHONDONTWRITEBYTECODE'], '1')
        self.assertEqual(env['SW4_FRAME8_PYTHON'], sys.executable)
        assigned = next(n.value for n in ast.walk(main) if isinstance(n, ast.Assign) and
                        isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'env')
        self.assertEqual({k.arg for k in assigned.keywords},
                         {'PYTHON', 'PYTHONDONTWRITEBYTECODE', 'SW4_FRAME8_PYTHON'})

    def test_complex_jobs_uses_parallel_scheduler_only_for_complex(self):
        commands = dict(conc.supplier_commands(self.work, complex_jobs=3))
        self.assertEqual(list(map(str, commands['bit589'])),
                         original_command(self.runs['bit589'], self.work))
        self.assertEqual(Path(commands['complex741'][2]).name, 'verify_complex741_parallel.py')
        self.assertEqual(list(map(str, commands['complex741']))[-2:], ['--jobs', '3'])


class Scheduler(unittest.TestCase):
    def run_jobs(self, jobs):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            start = time.monotonic()
            try:
                records = conc.run_concurrent(jobs, work, conc.supplier_env())
                error = None
            except RuntimeError as exc:
                records, error = exc.args[1], exc
            return records, error, time.monotonic() - start, json.loads((work / 'CONCURRENCY.json').read_text()), \
                {n: (work / (n + '.log')).read_text() for n, _ in jobs}

    def test_independent_jobs_overlap_and_keep_order(self):
        sleep = [PY, '-c', 'import time;time.sleep(1.5);print("done")']
        records, error, wall, summary, logs = self.run_jobs([('a', sleep), ('b', sleep)])
        self.assertIsNone(error)
        self.assertEqual([r['name'] for r in records], ['a', 'b'])
        self.assertEqual([r['exit_code'] for r in records], [0, 0])
        self.assertLess(wall, 2.8)
        self.assertLess(summary['wall_seconds'], 0.75 * summary['sequential_seconds'])
        self.assertEqual(logs['a'], 'done\n')
        self.assertEqual(len(records[0]['log_sha256']), 64)

    def test_failure_stops_the_other_job_and_names_the_failure(self):
        fail = [PY, '-c', 'import sys;print("bad");sys.exit(3)']
        hang = [PY, '-c', 'import time;time.sleep(120)']
        records, error, wall, _, logs = self.run_jobs([('hang', hang), ('fail', fail)])
        self.assertIsInstance(error, RuntimeError)
        self.assertIn('fail failed', error.args[0])
        self.assertLess(wall, 30)
        by_name = {r['name']: r for r in records}
        self.assertEqual(by_name['fail']['exit_code'], 3)
        self.assertNotEqual(by_name['hang']['exit_code'], 0)
        self.assertEqual(logs['fail'], 'bad\n')

    def test_success_of_one_job_does_not_stop_the_other(self):
        quick = [PY, '-c', 'print(1)']
        slow = [PY, '-c', 'import time;time.sleep(1);print(2)']
        records, error, _, _, logs = self.run_jobs([('quick', quick), ('slow', slow)])
        self.assertIsNone(error)
        self.assertEqual([r['exit_code'] for r in records], [0, 0])
        self.assertEqual(logs['slow'], '2\n')


if __name__ == '__main__':
    unittest.main()

"""Solver regressions; requires OR-Tools. No historical ceiling claim is tested here."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from collections import Counter


class AllocatorTests(unittest.TestCase):
    def invoke(self, script, widths, seconds, output_exists=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / 'plan.json'
            plan.write_text(json.dumps({
                'order': [[stage, replica] for stage in range(9) for replica in range(8)],
                'windows': {'0,0': [8, list(range(72))]},
            }))
            output = root / 'allocation.json'
            if output_exists:
                output.write_text('previous receipt\n')
            command = [sys.executable, '-O', str(Path(__file__).with_name(script)),
                       str(plan), json.dumps(widths), str(output), str(seconds)]
            if script == 'loop.py':
                command.append('1')
            result = subprocess.run(command, text=True, capture_output=True, timeout=60)
            payload = output.read_text() if output.exists() else None
            return result, payload

    def test_failed_solves_do_not_export_or_overwrite(self):
        for script in ('aggregate_milp.py', 'loop.py'):
            for widths, seconds, status in (({'8': 1}, 0, 'UNKNOWN'),
                                            ({'9': 1}, 5, 'INFEASIBLE')):
                for existing in (False, True):
                    with self.subTest(script=script, status=status, existing=existing):
                        result, payload = self.invoke(script, widths, seconds, existing)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(status, result.stderr)
                        self.assertEqual(payload, 'previous receipt\n' if existing else None)

    def test_zero_width_rejected_before_pattern_enumeration(self):
        for script in ('aggregate_milp.py', 'loop.py'):
            with self.subTest(script=script):
                result, payload = self.invoke(script, {'0': 1}, 5)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Widths must be positive', result.stderr)
                self.assertIsNone(payload)

    def test_feasible_allocation_conserves_every_call_and_port(self):
        for script in ('aggregate_milp.py', 'loop.py'):
            with self.subTest(script=script):
                result, payload = self.invoke(script, {'8': 1}, 10)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                allocation = json.loads(payload)
                self.assertIn(allocation['status'], ('FEASIBLE', 'OPTIMAL'))
                calls = Counter()
                for time, child, owner, width, count in allocation['x']:
                    self.assertEqual((child, owner, width), (0, 0, 8))
                    self.assertGreater(count, 0)
                    calls[time] += count
                self.assertEqual(calls, Counter({time: 1 for time in range(72)}))
                ports = mass = 0
                remainders = Counter()
                for child, owner, pattern, count in allocation['y']:
                    self.assertEqual((child, owner), (0, 0))
                    self.assertIn(pattern, ([], [8]))
                    ports += count
                    mass += sum(pattern) * count
                    if sum(pattern) < 8:
                        remainders[str(8 - sum(pattern))] += count
                self.assertEqual(ports, 120)
                self.assertEqual(mass, 72 * 8)
                self.assertEqual(remainders, {'8': 48})
                self.assertEqual(allocation['remainders'], dict(remainders))
                if script == 'loop.py':
                    self.assertEqual(allocation['fails'], [])
                    literal = allocation['assign']['0,0']
                    self.assertEqual(len(literal), 72)
                    self.assertEqual({time for time, width, port in literal}, set(range(72)))
                    self.assertEqual({width for time, width, port in literal}, {8})
                    self.assertEqual(len({port for time, width, port in literal}), 72)
                    self.assertTrue(all(0 <= port < 120 for time, width, port in literal))


if __name__ == '__main__':
    unittest.main(verbosity=2)

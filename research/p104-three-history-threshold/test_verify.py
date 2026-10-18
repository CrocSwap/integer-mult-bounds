# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the bounded changed-history cost screen."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import verify as v


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = v.sources()
        cls.endpoint = v.read_json(
            v.ROOT / 'research/p104-endpoint-geometric-budget/RESULT.json')
        cls.curve = v.endpoint_curve(cls.endpoint)
        cls.forced = [4656, 4656, 4672, 4680, 4672, 4656, 4656]

    def test_actual_fusion_profile_and_constraints(self):
        result = v.check_screen((232, 180, 11), self.curve, self.forced)
        self.assertEqual(result['local_profile'], {
            '1': 3235, '2': 69, '3': 86, '4': 104,
            '5': 48, '6': 24, '7': 240, '8': 8})
        self.assertEqual(result['cut_capacities'],
                         [12456, 12104, 12104, 12456, 12456, 12456, 12456])
        self.assertEqual(result['endpoint_dimension_totals'], [1569, 1569])
        self.assertEqual((result['local_rank_mass'], result['idle_rank_mass']),
                         (6175, 537))
        self.assertEqual(v.history(v.MERGED), ([64, 32, 32, 64, 64, 64, 64], 7, 7))

    def test_minimum_fusions_and_independent_prices(self):
        ten = v.independent_moment(232, 181, 10, v.SELECTED)
        eleven = v.independent_moment(232, 180, 11, v.SELECTED)
        self.assertGreater(ten[0], 1)
        self.assertLess(eleven[1], 1)
        self.assertEqual(v.outward(eleven), [
            '999999737314689/1000000000000000', '99999973731469/100000000000000'])
        self.assertEqual(v.independent_moment(232, 180, 11, Q(0)),
                         (Q(7551, 7592), Q(7551, 7592)))

    def test_independent_binomial_has_exact_power_oracles(self):
        for rank in (1, 2, 8, 51, 73):
            with self.subTest(rank=rank):
                low, high = v.INDEPENDENT.child(rank, Q(1, 100))
                exact_power = Q(rank, 73) ** 99
                self.assertLessEqual(low ** 100, exact_power)
                self.assertGreaterEqual(high ** 100, exact_power)
        with self.assertRaisesRegex(ValueError, 'independent saving'):
            v.INDEPENDENT.child(1, Q(1, 2))
        with self.assertRaisesRegex(ValueError, 'independent helper counts'):
            v.independent_moment(483, 0, 0, v.SELECTED)
        with self.assertRaisesRegex(ValueError, 'independent rational bit bound'):
            v.INDEPENDENT.child(1, Q(1, 1 << 200))

    def test_independent_checker_rejects_a_wrong_primary_price(self):
        value = v.checked_moment(self.engine, (232, 180, 11))
        self.assertEqual(value['primary'], [
            '999999737314689/1000000000000000', '99999973731469/100000000000000'])
        with patch.object(self.engine, 'relax', return_value=(Q(0), Q(0))):
            with self.assertRaisesRegex(ValueError, 'independent binomial enclosure'):
                v.checked_moment(self.engine, (232, 180, 11))

    def test_endpoint_curve_against_independent_integer_dp(self):
        best = [0]
        for demand, capacity, multiplicity in self.endpoint['geometry']['arrival'][
                'endpoint_types']:
            for _ in range(multiplicity):
                next_best = [-1] * (len(best) + 2)
                for used, covered in enumerate(best):
                    for extra, gain in enumerate((0, capacity, demand)):
                        next_best[used + extra] = max(next_best[used + extra],
                                                       covered + gain)
                best = next_best
        self.assertEqual([4656 - n for n in best], self.curve)
        self.assertEqual(self.curve[191], 219)
        broken = copy.deepcopy(self.endpoint)
        broken['geometry']['arrival']['endpoint_types'][0][1] += 1
        with self.assertRaisesRegex(ValueError, 'inherited endpoint curve'):
            v.endpoint_curve(broken)

    def test_threshold_with_independent_affine_enclosures(self):
        constant = v.independent_moment(0, 0, 0, v.SELECTED)
        c = v.independent_moment(1, 0, 0, v.SELECTED)
        m = v.independent_moment(0, 0, 1, v.SELECTED)
        dc = c[0] - constant[1], c[1] - constant[0]
        dm = m[0] - constant[1], m[1] - constant[0]
        for floor, expected in ((435, (245, 190)), (436, (246, 190))):
            # Deliberately include nonminimal cheap counts, unlike the primary.
            rows = []
            for merged in range(483):
                low = max(self.curve[min(merged, 208)], floor - merged, 0)
                for cheap in range(low, 483 - merged):
                    rows.append((constant[0] + cheap * dc[0] + merged * dm[0],
                                 constant[1] + cheap * dc[1] + merged * dm[1],
                                 (cheap, merged)))
            winner = min(rows, key=lambda row: row[1])
            self.assertEqual(winner[2], expected)
            self.assertTrue(all(a > winner[1] for a, _, pair in rows
                                if pair != winner[2]))
            if floor == 435:
                self.assertLess(winner[1], 1)
            else:
                self.assertGreater(winner[0], 1)

    def test_reject_bad_histories_counts_and_acceptance_premises(self):
        for jumps in ((1, 0, 8), (True, 8), (1, 7), (10,), (1,) * 10):
            with self.subTest(jumps=jumps), self.assertRaises(ValueError):
                v.history(jumps)
        for counts in ((True, 0, 0), (-1, 0, 0), (483, 0, 0), (1, 2)):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                v.profile(counts)
        with self.assertRaisesRegex(ValueError, 'saturated endpoint demands'):
            v.check_screen((218, 180, 11), self.curve, self.forced)
        with self.assertRaisesRegex(ValueError, 'coupled cut demands'):
            v.check_screen((232, 180, 11), self.curve,
                           [4656, 12105, 4672, 4680, 4672, 4656, 4656])
        with patch.object(v, 'MERGED', (1, 1, 2, 1, 1, 1, 2)):
            with self.assertRaisesRegex(ValueError, 'endpoint signatures'):
                v.compute()


def export_tree(destination):
    package = destination / 'research/p104-three-history-threshold'
    shutil.copytree(v.PACKAGE, package,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    manifest = v.read_json(v.PACKAGE / 'SOURCES.json')
    for record in manifest['files']:
        if record['usage'] == 'input':
            target = destination / record['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(v.ROOT / record['path'], target)
    return package


def cli(package):
    environment = os.environ.copy()
    environment.pop('PYTHONOPTIMIZE', None)
    command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
    return subprocess.run(command, cwd=package, env=environment, capture_output=True,
                          text=True, check=False, timeout=90)


class PublicCommandTests(unittest.TestCase):
    def test_git_free_isolated_command_and_source_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            package = export_tree(Path(directory))
            result = cli(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'PASS_P104_THREE_HISTORY_THRESHOLD '
                             'minimum_fusions=11 two_history_floor=423 '
                             'three_history_floor=436 no_new_kappa\n')
            engine = Path(directory) / 'research/complex-local-word-ceiling/ceiling.py'
            with engine.open('a', encoding='utf-8') as stream:
                stream.write('\nraise RuntimeError("must not execute")\n')
            result = cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source hash:', result.stderr)
            self.assertNotIn('RuntimeError: must not execute', result.stderr)

    def test_retained_predecessor_and_full_receipt_corruption(self):
        for filename, message in (('inputs/PR2924-RESULT.json', 'source hash:'),
                                  ('RESULT.json', 'complete typed receipt')):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as root:
                package = export_tree(Path(root))
                path = package / filename
                data = json.loads(path.read_text(encoding='utf-8'))
                data['invented_field'] = True
                path.write_text(json.dumps(data), encoding='utf-8')
                result = cli(package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_duplicate_keys_reject(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'duplicate.json'
            path.write_text('{"x":1,"x":2}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                v.read_json(path)


if __name__ == '__main__':
    unittest.main()

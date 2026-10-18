#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Semantic corruption tests: each must fail for the intended reason."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('owner_floor_under_test', P/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class CorruptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = V.load()

    def run_mutant(self, mutate, reason):
        data = deepcopy(self.original)
        mutate(data)
        saved = V.load
        try:
            V.load = lambda: data
            with self.assertRaisesRegex(ValueError, reason):
                V.build()
        finally:
            V.load = saved

    def test_missing_scatter(self):
        def mutate(data):
            events = data['programs']['forward']
            at = next(i for i, e in enumerate(events) if e[0] == 'scalar' and
                      e[1][0] == 'add' and e[1][2][0] == 'C')
            events.pop(at)
        self.run_mutant(mutate, 'complete first scalar endpoint')

    def test_owner_route_collapse(self):
        def mutate(data):
            data['phases']['recipes'][1] = data['phases']['recipes'][0]
        self.run_mutant(mutate, '112 distinct owner routes')

    def test_intervening_operation(self):
        def mutate(data):
            data['template']['execution_schedule'][2]['kind'] = 'bridge'
        self.run_mutant(mutate, 'intervening nonlocal event')

    def test_wrong_owner_boundary(self):
        def mutate(data):
            data['template']['calls'][4]['owners'][0][1][1] = 0
        self.run_mutant(mutate, 'owner/chart boundary')


if __name__ == '__main__':
    unittest.main()

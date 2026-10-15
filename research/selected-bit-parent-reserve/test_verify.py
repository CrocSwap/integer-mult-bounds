#!/usr/bin/env python3
"""Semantic/source controls, also required under python -O. Apache-2.0."""
from __future__ import annotations

import copy
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('parent_reserve', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ReserveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.inputs()
        cls.assembly, cls.bit, cls.m = v.bind_sources(cls.data)
        cls.values = v.parameters(cls.bit, cls.m)
        cls.stage = v.cutoff(cls.assembly, cls.values['parent_sigma'])

    def test_selected_dimension_not_complex_or_historical(self):
        for m in (73, 120):
            with self.subTest(m=m), self.assertRaisesRegex(v.Rejected, 'ordinary dimension'):
                v.parameters(self.bit, m)

    def test_all_physical_work_roles_are_charged(self):
        mutant = copy.deepcopy(self.bit)
        mutant['nine']['bit']['physical'] -= 9
        with self.assertRaisesRegex(v.Rejected, 'nine additional roles'):
            v.parameters(mutant, self.m)

    def test_one_level_halving_is_false(self):
        self.assertEqual(42 * (128 // 64), 84)
        self.assertGreater(84, 128 // 2)
        mutant = copy.deepcopy(self.bit)
        mutant['nine']['bit']['halving_depth'] = 1
        with self.assertRaisesRegex(v.Rejected, 'halving degree'):
            v.parameters(mutant, self.m)

    def test_uncharged_larger_child_is_rejected(self):
        mutant = copy.deepcopy(self.bit)
        mutant['nine']['profile']['46'] = mutant['nine']['profile'].pop('42')
        with self.assertRaisesRegex(v.Rejected, 'maximum child'):
            v.parameters(mutant, self.m)
        self.assertGreater(2 * 46 ** 2, 64 ** 2)

    def test_high_matrix_fibers_do_not_cancel_from_stock(self):
        actual = 2 * v.gl_size(3, 2, 2)
        omitted_fibers = 2 * v.gl_size(3, 2, 1)
        self.assertEqual(actual, omitted_fibers * 3 ** 4)
        with self.assertRaisesRegex(v.Rejected, 'divisible descendant stock'):
            v.require_stock(omitted_fibers, actual, 1)

    def test_role_factor_is_not_free(self):
        group = v.gl_size(3, 2, 2)
        with self.assertRaisesRegex(v.Rejected, 'divisible descendant stock'):
            v.require_stock(group, 2 * group, 1)

    def test_one_missing_nested_packet_is_rejected(self):
        v.require_stock(27, 3, 3)
        with self.assertRaisesRegex(v.Rejected, 'divisible descendant stock'):
            v.require_stock(9, 3, 3)

    def test_sequential_calls_reuse_but_do_not_erase_leaf_obligation(self):
        self.assertEqual(v.row_smoke()['rows'], 27)
        with self.assertRaisesRegex(v.Rejected, 'divisible descendant stock'):
            v.require_stock(27, 3, 3, external_leaf=3)

    def test_arbitrary_dirty_row_requires_every_restoration(self):
        for failed_depth in (1, 2, 3):
            with self.subTest(depth=failed_depth):
                outputs = [v.row_program(row, 3, 3, failed_depth) for row in range(27)]
                self.assertNotEqual(outputs, list(range(27)))

    def test_existing_sufficient_guard_rejects_next_headroom_bit(self):
        row = self.stage
        v.fit_guard(row['cutoff_log2'], v.Q(row['gap']), v.Q(row['s']),
                    row['guard_headroom'])
        with self.assertRaisesRegex(v.Rejected, 'stock-fit guard'):
            v.fit_guard(row['cutoff_log2'], v.Q(row['gap']), v.Q(row['s']),
                        row['guard_headroom'] + 1)
        self.assertEqual(row['sigma'], 8194)
        self.assertEqual(row['required_log2_8sigma'], 17)

    def test_recorded_stage_cannot_be_rebound(self):
        mutant = copy.deepcopy(self.assembly)
        mutant['bootstrap'][0]['cutoff_log2'] = str(self.stage['cutoff_log2'] - 1)
        with self.assertRaisesRegex(v.Rejected, 'cutoff reconstruction'):
            v.cutoff(mutant, 8194)

    def test_source_tamper_is_rejected_before_semantic_read(self):
        pins = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
        pin = next(p for p in pins if p['path'] == v.BIT)
        with self.assertRaisesRegex(v.Rejected, 'source SHA256'):
            v.authenticate(self.data[v.BIT] + b' ', pin)

    def test_archive_member_pin_is_not_just_container_success(self):
        member = v.archive_member(self.data, 'code/assemble.py') + b'\n# mutation\n'
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w:gz') as archive:
            info = tarfile.TarInfo('code/assemble.py')
            info.size = len(member)
            archive.addfile(info, io.BytesIO(member))
        mutant = dict(self.data)
        mutant[v.ARCHIVE] = output.getvalue()
        with self.assertRaisesRegex(v.Rejected, 'archive member SHA256'):
            v.archive_member(mutant, 'code/assemble.py')

    def test_small_local_ring_census_is_not_float_arithmetic(self):
        self.assertEqual([row['invertible'] for row in v.local_ring_smoke()], [48, 3888, 480])


if __name__ == '__main__':
    unittest.main(verbosity=2)

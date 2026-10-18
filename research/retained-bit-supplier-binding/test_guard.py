#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Semantic faults and source/CLI controls; checks also run under -I -O."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('guard_under_test', HERE / 'guard.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = g.context()
        cls.assembly = json.loads((g.ROOT / g.ASSEMBLIES[-1]).read_bytes())
        cls.record = cls.ctx['record']
        import gzip
        cls.word = json.loads(gzip.decompress((g.ROOT / g.RETAINED_ROOT /
                                              cls.record['word']['file']).read_bytes()))

    def test_all_four_published_assemblies(self):
        for name in g.ASSEMBLIES:
            with self.subTest(name=name):
                self.assertEqual(g.check_assembly(json.loads((g.ROOT / name).read_bytes()), self.ctx), 10272)
        result = json.loads((g.ROOT / g.BIT_RESULT).read_bytes())
        self.assertTrue(g.check_bit_result(result, self.ctx))

    def test_false_provenance_with_identical_priced_numbers(self):
        # Mirrors PR1277's false-source fixture, then covers each identity field.
        replacements = dict(pr=555, repository='another/repository', commit='0' * 40,
                            merged_as='0' * 40, path=g.SOURCE_ROOT + '/tune/EXPECTED.json',
                            git_blob_sha1='0' * 40)
        for name, value in replacements.items():
            with self.subTest(name=name):
                a = copy.deepcopy(self.assembly)
                a['bit_supplier'][name] = value
                self.assertEqual(a['bit_lower'], self.assembly['bit_lower'])
                self.assertEqual(a['kappa'], self.assembly['kappa'])
                with self.assertRaisesRegex(ValueError, 'bit_supplier.' + name):
                    g.check_assembly(a, self.ctx)

    def test_same_record_at_another_real_commit_is_not_the_cited_head(self):
        a = copy.deepcopy(self.assembly)
        a['bit_supplier']['commit'] = self.ctx['base_commit']
        raw = g.git(g.ROOT, 'show', self.ctx['base_commit'] + ':' + a['bit_supplier']['path'])
        self.assertEqual(g.blob_id(raw), a['bit_supplier']['git_blob_sha1'])
        with self.assertRaisesRegex(ValueError, 'bit_supplier.commit'):
            g.check_assembly(a, self.ctx)

    def test_compensating_copy_rank_fault_preserves_scalar_deficit(self):
        a = copy.deepcopy(self.assembly)
        a['bit_supplier']['word']['copy_ranks'][:2] = [6, 8]
        self.assertEqual(sum(a['bit_supplier']['word']['copy_ranks']), 63)
        with self.assertRaisesRegex(ValueError, 'bit_supplier.word'):
            g.check_assembly(a, self.ctx)

    def test_source_frame_change_is_measured_not_read_from_record(self):
        w = copy.deepcopy(self.word)
        total = w['ret'][0]
        self.assertEqual(g.copy_ranks(w), [7] * 9)
        # A final full-frame gate really changes the COPY rank to eight.
        full = next(i for i, frame in enumerate(w['frames'])
                    if g.rank([w['lines'][j] for j in frame]) == 8)
        w['A'].append([full, total, [0]])
        self.assertEqual(g.copy_ranks(w)[0], 8)
        with self.assertRaisesRegex(ValueError, 'word record: decoder_constant'):
            g.derive(self.record, w)

    def test_profile_mass_fault_and_boolean_count(self):
        for value in (self.record['nine']['profile']['1'] + 1, True):
            r = copy.deepcopy(self.record)
            r['nine']['profile']['1'] = value
            with self.assertRaises(ValueError):
                g.derive(r, self.word)

    def test_endpoint_digest_surcharge_and_deficit_faults(self):
        faults = [('endpoint', lambda a: a.update(bit_lower='1/2')),
                  ('digest', lambda a: a['input_sha256'].update({'package:inputs/PR589-EXPECTED.json': '0' * 64})),
                  ('surcharge', lambda a: a['surcharge_model'].update(bit=1)),
                  ('deficit', lambda a: a['bit_supplier'].update(derived_deficit=9984)),
                  ('formula', lambda a: a['bit_supplier'].update(deficit_formula='unpunctured'))]
        for name, change in faults:
            with self.subTest(name=name):
                a = copy.deepcopy(self.assembly)
                change(a)
                with self.assertRaises(ValueError):
                    g.check_assembly(a, self.ctx)

    def test_priced_bit_result_faults(self):
        positive = json.loads((g.ROOT / g.BIT_RESULT).read_bytes())
        for field, value in [('R', 438), ('replicas', 31), ('stages', 11), ('bit_lower', '1/2')]:
            result = copy.deepcopy(positive)
            result[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                g.check_bit_result(result, self.ctx)
        result = copy.deepcopy(positive)
        # Preserve rank mass by exchanging two H1 calls for one H2 call.
        result['bit_profile']['1'] -= 2
        result['bit_profile']['2'] += 1
        self.assertEqual(sum(int(k) * v for k, v in result['bit_profile'].items()), 1808352)
        with self.assertRaisesRegex(ValueError, 'bit result: bit_profile'):
            g.check_bit_result(result, self.ctx)

    def test_cli_rejects_unchanged_numerics_with_zeroed_source(self):
        with tempfile.TemporaryDirectory(prefix='.guard-test-', dir=HERE) as folder:
            path = Path(folder) / 'assembly.json'
            a = copy.deepcopy(self.assembly)
            a['bit_supplier'].update(commit='0' * 40, git_blob_sha1='0' * 40)
            path.write_text(json.dumps(a), encoding='utf-8')
            p = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'),
                                '--assembly', str(path)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('bit_supplier.commit', p.stderr)

    def test_relocated_inputs_and_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix='.guard-test-', dir=HERE) as folder:
            root = Path(folder)
            # Reuse only the object database; every live input is physically relocated.
            gitdir = g.git(g.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip()
            (root / '.git').write_text('gitdir: ' + gitdir + '\n', encoding='utf-8')
            sources = json.loads((HERE / 'SOURCES.json').read_bytes())
            for item in sources['files']:
                if item['usage'] == 'input':
                    target = root / item['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(g.ROOT / item['path'], target)
            self.assertEqual(g.context(root)['supplier'], self.ctx['supplier'])
            target = root / g.RETAINED_ROOT / 'tune/EXPECTED.json'
            target.write_bytes(target.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'live source pin'):
                g.context(root)


if __name__ == '__main__':
    unittest.main()

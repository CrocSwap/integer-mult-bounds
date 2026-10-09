#!/usr/bin/env python3
"""Corruption controls for the exact local-word/cover composition.

Prepared for eumemic with OpenAI Codex assistance; Apache-2.0.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Negative controls require assertions')
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import certificate
from verify import (ROOT, LOCAL, PACKAGE, BIT_MANIFEST, LOCAL_FILES,
                    check_sources, compare_json, digest, safe_file)


class CoverControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = check_sources(ROOT)

    def local_change(self, name, change, callback=certificate.cover_profile):
        with tempfile.TemporaryDirectory(prefix='cover-local-control-') as directory:
            local = Path(directory)
            for filename in LOCAL_FILES:
                out = local / filename
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / LOCAL / filename, out)
            path = local / name
            value = json.loads(path.read_text())
            change(value)
            path.write_text(json.dumps(value))
            with patch.object(certificate, 'LOCAL', local):
                with self.assertRaises((AssertionError, ValueError)):
                    callback()

    def test_frozen_exact_certificate_recomputed(self):
        actual = certificate.js(certificate.exact())
        self.assertEqual(actual, json.loads((ROOT / PACKAGE / 'certificate.json').read_text()))

    def test_local_cover_telescoping(self):
        p = certificate.cover_profile()
        self.assertEqual(p['roles_per_vertex'] * p['m'] - p['rank_per_vertex'], 2392)
        self.assertEqual(sum(int(r) * n for r, n in p['child_multiplicities'].items()), p['rank_per_vertex'])
        self.assertEqual(p['R'] + p['reused_roles'], p['virtual_R'])

    def test_omitted_reused_role_rejected(self):
        self.local_change('complex-profile.json', lambda p: p.update(reused_roles=p['reused_roles']-1))

    def test_omitted_endpoint_or_move_rejected(self):
        self.local_change('complex-profile.json', lambda p: p['child_multiplicities'].__setitem__('1', p['child_multiplicities']['1']-1))

    def test_unbound_source_inventory_rejected(self):
        self.local_change('reflection-audit.json', lambda p: p.update(completed_core_source_inventory_bound=False))

    def test_omitted_dirty_compensation_rejected(self):
        self.local_change('reflection-audit.json', lambda p: p.update(exact_arbitrary_dirty_cancellation_by_dependency_cut=False))

    def test_missing_reflected_frame_check_rejected(self):
        self.local_change('reflection-audit.json', lambda p: p.update(reflected_core_active_frames_complement_source=False))

    def test_wrong_source_hash_rejected(self):
        self.local_change('reflection-audit.json', lambda p: p.update(source_sha256='0'*64))

    def test_scalar_guard_below_literal_audit_rejected(self):
        self.local_change('reflection-audit.json',
                          lambda p: p.update(expanded_scalar_operations_per_stage=p['conservative_local_G']+1),
                          certificate.exact)

    def test_missing_dynamic_local_producer_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['files'][LOCAL + '/producer.py']
        with self.assertRaisesRegex(ValueError, 'source dependency closure'):
            check_sources(ROOT, changed)

    def test_missing_inherited_bit_source_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['files'][str(Path(BIT_MANIFEST).parent / 'deferred_23.json.gz')]
        with self.assertRaisesRegex(ValueError, 'source dependency closure'):
            check_sources(ROOT, changed)

    def test_altered_dag_rejected_even_after_outer_rehash(self):
        with tempfile.TemporaryDirectory(prefix='cover-repinned-dag-') as directory:
            root = Path(directory)
            for name in self.manifest['files']:
                out = root / name
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, out)
            name = LOCAL + '/inputs/complex-dag.json.gz'
            path = root / name
            path.write_bytes(path.read_bytes() + b'corrupted')
            changed = copy.deepcopy(self.manifest)
            changed['files'][name] = digest(path)
            with self.assertRaisesRegex(ValueError, 'scalar-DAG provenance'):
                check_sources(root, changed)

    def test_hash_bound_formatting_change_rejected(self):
        with tempfile.TemporaryDirectory(prefix='cover-formatting-') as directory:
            expected = ROOT / LOCAL / 'reflection-audit.json'
            actual = Path(directory) / expected.name
            actual.write_text(json.dumps(json.loads(expected.read_text())))
            with self.assertRaisesRegex(ValueError, 'generated byte mismatch'):
                compare_json(actual, expected)

    def test_noncanonical_reflection_receipt_rejected(self):
        path = ROOT / LOCAL / 'reflection-audit.json'
        expected = json.dumps(json.loads(path.read_text()), indent=2, sort_keys=True) + '\n'
        self.assertEqual(path.read_bytes(), expected.encode())

    def test_parent_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsafe source path'):
            safe_file(ROOT, '../certificate.json')

    def test_optimized_verifier_rejected_before_regeneration(self):
        result = subprocess.run([sys.executable, '-O', str(ROOT / PACKAGE / 'verify.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('optimized Python is forbidden', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)

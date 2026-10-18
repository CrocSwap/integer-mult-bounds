#!/usr/bin/env python3
"""Focused tests for the independent audit, not the inherited supplier checker."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('selected_identity_audit', HERE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def test_independent_encoder_known_bytes(self):
        value = {'z': [None, True, False, 1, -2], 'a': '\"\\\n\t\x7f\u00e9\U0001f642'}
        expected = b'{"a":"\\\"\\\\\\n\\t\\u007f\\u00e9\\ud83d\\ude42","z":[null,true,false,1,-2]}'
        self.assertEqual(b''.join(audit.encode(value)), expected)
        self.assertNotEqual(audit.identity(True), audit.identity(1))
        with self.assertRaisesRegex(ValueError, 'outside audited scalar domain'):
            audit.identity(1.0)

    def test_tree_includes_containers_keys_and_indices(self):
        value = {'empty': {}, 'list': [[], True]}
        self.assertEqual(audit.tree(value)['nodes'], 5)
        self.assertNotEqual(audit.tree(value), audit.tree({'empty': [], 'list': [[], True]}))
        self.assertNotEqual(audit.tree(value), audit.tree({'empty': {}, 'list': [True, []]}))
        self.assertNotEqual(audit.tree(value), audit.tree({'other': {}, 'list': [[], True]}))
        self.assertNotEqual(audit.tree(value), audit.tree({'empty': {}, 'list': [[], 1]}))

    def test_immutable_container_header_drift_rejects(self):
        with tempfile.TemporaryDirectory(prefix='identity-source-control-') as temporary:
            root = Path(temporary)
            for name in audit.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((audit.ROOT / name).read_bytes())
            archive = root / audit.ARCHIVE
            raw = bytearray(archive.read_bytes())
            self.assertEqual(raw[:2], b'\x1f\x8b')
            raw[4] ^= 1  # Gzip MTIME only; immutable source identity is still strict.
            archive.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'immutable source pin: ' + audit.ARCHIVE):
                audit.bind_sources(root)

    def test_independent_tree_oracle_detects_missing_phase_field(self):
        original_loader = audit.runpy.run_path

        def altered_loader(path):
            source = original_loader(path)
            original_phase = source['phase_value']

            def omit_field(*args, **kwargs):
                value = original_phase(*args, **kwargs)
                del value['all_child_equalities_include_global_phase']
                return value
            source['phase_value'] = omit_field
            return source

        with mock.patch.object(audit.runpy, 'run_path', side_effect=altered_loader):
            with self.assertRaisesRegex(ValueError, 'typed-path projection coverage: CLIFFORD-REVIEW.json'):
                audit.audit()

    def test_strict_fixture_parser_rejects_ambiguous_json(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                audit.load(raw)


if __name__ == '__main__':
    unittest.main()

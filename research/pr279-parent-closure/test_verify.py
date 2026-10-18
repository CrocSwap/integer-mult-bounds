#!/usr/bin/env python3
"""Offline parent-inventory controls. Adam Gall; OpenAI Codex; Apache-2.0."""
import base64
import copy
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('parent_closure', Path(__file__).with_name('verify.py'))
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class ParentClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs, cls.retained = V.load_inputs()

    def reject(self, index, mutate, message):
        values = list(self.inputs)
        value = copy.deepcopy(values[index])
        replacement = mutate(value)
        values[index] = value if replacement is None else replacement
        with self.assertRaisesRegex(ValueError, message):
            V.audit(*values)

    def test_positive_complete_parent(self):
        report = V.audit(*self.inputs)
        self.assertEqual(report['parent_paths'], 116)
        self.assertEqual(report['repository_changes'], {'added': 2, 'modified': 10})
        self.assertFalse(self.retained['fresh_execution'])
        self.assertEqual(len(self.retained['retained_stages']), 9)

    def test_changed_retained_blob(self):
        self.reject(1, lambda files: files.__setitem__('bank_template.py', b'changed'), 'wrong blob')

    def test_changed_companion_blob(self):
        self.reject(1, lambda files: files.__setitem__('target_transform.py', b'changed'), 'wrong blob')

    def test_omitted_retained_file(self):
        def omit(files):
            del files['bank_template.py']
        self.reject(1, omit, 'incomplete or additional file coverage')

    def test_extra_candidate_file(self):
        self.reject(1, lambda files: files.__setitem__('unlisted.py', b''), 'incomplete or additional')

    def test_current_bytes_cannot_replace_reviewed_base(self):
        self.reject(2, lambda files: files.__setitem__('verify.py', self.inputs[1]['verify.py']),
                    'Reviewed package: wrong blob')

    def test_changed_workflow(self):
        self.reject(3, lambda data: data + b'\n', 'Workflow: wrong blob')

    def test_wrong_matched_blob_with_unchanged_count(self):
        def change(comparison):
            comparison['matched'][0]['blob'] = comparison['matched'][1]['blob']
        self.reject(4, change, 'Parent inventory blob mismatch')

    def test_duplicate_parent_path_with_unchanged_count(self):
        def duplicate(comparison):
            comparison['matched'][0] = comparison['matched'][1].copy()
        self.reject(4, duplicate, 'Duplicate parent inventory path')

    def test_omitted_parent_path_with_unchanged_count(self):
        def replace(comparison):
            comparison['matched'][0]['path'] = 'not-in-pinned-parent'
        self.reject(4, replace, 'Parent inventory path omission')

    def test_swapped_coverage_partition(self):
        def swap(comparison):
            comparison['matched'][0], comparison['unresolved'][0] = (
                comparison['unresolved'][0], comparison['matched'][0])
        self.reject(4, swap, 'Wrong unresolved partition')

    def test_wrong_update_kind(self):
        def change(source):
            source['changes'][0]['status'] = 'added'
        self.reject(5, change, 'Incorrect update attribution')

    def test_missing_update_with_unchanged_count(self):
        def change(source):
            source['changes'][0]['path'] = 'not-in-commit.py'
        self.reject(5, change, 'Source update misses a repository change')

    def test_forged_commit_payload(self):
        def change(document):
            raw = base64.b64decode(document['commits'][V.CANDIDATE]) + b'\n'
            document['commits'][V.CANDIDATE] = base64.b64encode(raw).decode()
        self.reject(0, change, 'Git object hash mismatch')

    def test_substituted_commit_identity(self):
        def change(document):
            raw = document['commits'].pop(V.CANDIDATE)
            document['commits']['0' * 40] = raw
        self.reject(0, change, 'Wrong commit inventory')

    def test_forged_tree_payload(self):
        def change(document):
            oid = next(iter(document['trees']))
            raw = base64.b64decode(document['trees'][oid]) + b'\0'
            document['trees'][oid] = base64.b64encode(raw).decode()
        self.reject(0, change, 'Git object hash mismatch')

    def test_missing_root_tree(self):
        def change(document):
            proof = V.Proof(document)
            del document['trees'][proof.root(V.CANDIDATE)]
        self.reject(0, change, 'Missing tree proof')

    def test_unrelated_authentic_tree(self):
        def change(document):
            document['trees'][V.object_id('tree', b'')] = ''
        self.reject(0, change, 'Unused tree proof objects')


if __name__ == '__main__':
    unittest.main(verbosity=2)

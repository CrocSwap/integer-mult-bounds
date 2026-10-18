#!/usr/bin/env python3
"""Semantic and transport corruptions for the PR116 reconciliation capsule."""
import base64
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pr116_checker', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
DATA = v.json_read((HERE / 'CERTIFICATE.json').read_bytes())
RECEIPT_OID = 'dd37ce890b13e9548fb102044188f199007ad54a'
RECEIPT = v.json_read(base64.b64decode(DATA['objects'][RECEIPT_OID]['base64']))


class Capsule(unittest.TestCase):
    def test_complete_certificate_and_result(self):
        self.assertEqual(v.check(DATA), v.json_read((HERE / 'RESULT.json').read_bytes()))

    def test_duplicate_json_field(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            v.json_read('{"schema":1,"schema":1}')

    def test_wrong_head_anchor(self):
        bad = deepcopy(DATA)
        bad['commits']['current'] = v.OLD
        with self.assertRaisesRegex(ValueError, 'commit anchors'):
            v.check(bad)

    def test_missing_tree(self):
        bad = deepcopy(DATA)
        tree = next(k for k, obj in bad['objects'].items() if obj['type'] == 'tree')
        del bad['objects'][tree]
        with self.assertRaisesRegex(ValueError, 'missing object'):
            v.check(bad)

    def test_changed_blob_with_refreshed_sha256(self):
        bad = deepcopy(DATA)
        obj = bad['objects'][RECEIPT_OID]
        raw = base64.b64decode(obj['base64']).replace(b'"verification": "passed"', b'"verification": "failed"')
        obj['base64'] = base64.b64encode(raw).decode()
        obj['sha256'] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, 'Git object digest'):
            v.check(bad)

    def test_extra_valid_git_object(self):
        bad = deepcopy(DATA)
        raw = b'unrelated evidence'
        oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        bad['objects'][oid] = dict(type='blob', base64=base64.b64encode(raw).decode(), sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(ValueError, 'unreferenced'):
            v.check(bad)

    def test_object_type_confusion(self):
        bad = deepcopy(DATA)
        bad['objects'][v.NEW]['type'] = 'blob'
        with self.assertRaisesRegex(ValueError, 'Git object digest'):
            v.check(bad)

    def test_changed_sha256(self):
        bad = deepcopy(DATA)
        bad['objects'][v.NEW]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'object SHA256'):
            v.check(bad)


class TreeParser(unittest.TestCase):
    @staticmethod
    def entry(name, mode=b'100644'):
        return mode + b' ' + name + b'\0' + b'\x01' * 20

    def test_valid_git_directory_order(self):
        raw = self.entry(b'a.c') + self.entry(b'a', b'40000') + self.entry(b'b')
        self.assertEqual(list(v.parse_tree(raw)), ['a.c', 'a', 'b'])

    def test_duplicate_name(self):
        with self.assertRaisesRegex(ValueError, 'duplicate tree name'):
            v.parse_tree(self.entry(b'a') * 2)

    def test_truncated_object_id(self):
        with self.assertRaisesRegex(ValueError, 'truncated tree entry'):
            v.parse_tree(self.entry(b'a')[:-1])

    def test_wrong_order(self):
        with self.assertRaisesRegex(ValueError, 'tree order'):
            v.parse_tree(self.entry(b'b') + self.entry(b'a'))

    def test_escaping_name(self):
        with self.assertRaisesRegex(ValueError, 'tree name'):
            v.parse_tree(self.entry(b'../a'))

    def test_invalid_mode(self):
        with self.assertRaisesRegex(ValueError, 'tree mode'):
            v.parse_tree(self.entry(b'a', b'100666'))


class Evidence(unittest.TestCase):
    def setUp(self):
        self.ci = deepcopy(DATA['ci'])
        self.receipt = deepcopy(RECEIPT)

    def rejects(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            v.check_ci(self.receipt, self.ci)

    def test_missing_check(self):
        self.ci['checks'].pop()
        self.rejects('CI count')

    def test_duplicate_check(self):
        self.ci['checks'][1] = deepcopy(self.ci['checks'][0])
        self.rejects('duplicate check id')

    def test_check_associated_with_wrong_head(self):
        self.ci['checks'][0]['head_sha'] = v.NEW
        self.rejects('observed CI head')

    def test_failed_check(self):
        self.ci['checks'][0]['conclusion'] = 'failure'
        self.rejects('CI outcome')

    def test_truncated_receipt_check_inventory(self):
        self.receipt['research_head_ci']['checks'].pop()
        self.rejects('receipt check count')

    def test_name_mismatch(self):
        self.ci['checks'][0]['name'] = 'some other test'
        self.rejects('CI field: name')

    def test_missing_matrix_job(self):
        self.ci['cube_jobs']['jobs'].pop()
        self.rejects('focused job count')

    def test_duplicate_matrix_job(self):
        self.ci['cube_jobs']['jobs'][1] = deepcopy(self.ci['cube_jobs']['jobs'][0])
        self.rejects('duplicate focused job')

    def test_skipped_verifier_step(self):
        for step in self.ci['cube_jobs']['jobs'][0]['steps']:
            if step['name'] == 'Run python3 research/cube-deferred/verify.py':
                step['conclusion'] = 'skipped'
        self.rejects('required focused step')

    def test_wrong_checkout_despite_associated_head(self):
        for key, lines in self.ci['log_excerpts'].items():
            self.ci['log_excerpts'][key] = [s.replace(v.MERGE, v.OLD) for s in lines]
        self.rejects('actual checkout')

    def test_missing_control_summary(self):
        key = next(iter(self.ci['log_excerpts']))
        self.ci['log_excerpts'][key] = [s for s in self.ci['log_excerpts'][key] if 'Ran 14 tests in ' not in s]
        self.rejects('package controls not logged')

    def test_missing_package_pass(self):
        key = next(iter(self.ci['log_excerpts']))
        self.ci['log_excerpts'][key] = [s for s in self.ci['log_excerpts'][key] if 'PASS read-only' not in s]
        self.rejects('package pass not logged')

    def test_logs_swapped_between_jobs(self):
        self.ci['log_excerpts']['focused (3.11)'] = self.ci['log_excerpts']['focused (3.13)']
        self.rejects('log job association')

    def test_wrong_run_event(self):
        self.ci['cube_run']['event'] = 'push'
        self.rejects('focused run provenance')


if __name__ == '__main__':
    unittest.main()

"""Literal-data tests of the selected replay binding; no supplier is executed."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/check_selected_replay.py'
spec = importlib.util.spec_from_file_location('selected_replay_binding', SCRIPT)
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)


def leaves(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from leaves(child, path + (index,))
    else:
        yield path, value


def put(value, path, replacement):
    for key in path[:-1]:
        value = value[key]
    value[path[-1]] = replacement


class SelectedReplay(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.record = json.loads((ROOT / 'certificates/selected-result.json').read_text())
        self.frozen_bytes = (ROOT / self.record['certificate']).read_bytes()
        self.frozen = json.loads(self.frozen_bytes)
        self.manifest_bytes = (ROOT / self.record['source_manifest']).read_bytes()
        # Historical literal receipt is a binding fixture, not a fresh replay.
        self.receipt = json.loads((ROOT / 'research/community-pr279-audit/verification.json').read_text())
        self.record_path = self.root / 'record.json'
        self.fresh_path = self.root / 'replay/certificate.json'
        self.receipt_path = self.root / 'replay/verification.json'
        self.write_bytes(self.record['certificate'], self.frozen_bytes)
        self.write_bytes(self.record['source_manifest'], self.manifest_bytes)
        self.write_json(self.record_path, self.record)
        self.write_json(self.fresh_path, self.frozen)
        self.write_json(self.receipt_path, self.receipt)

    def write_bytes(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + '\n')

    def check(self):
        return binding.check(self.record_path, self.fresh_path, self.receipt_path, self.root)

    def republish(self, certificate):
        path = self.root / self.record['certificate']
        self.write_json(path, certificate)
        self.record['certificate_sha256'] = sha256(path.read_bytes()).hexdigest()
        self.write_json(self.record_path, self.record)

    def test_literal_selected_certificate_and_manifest(self):
        self.assertEqual(self.check(), Fraction(self.record['kappa']))

    def test_key_order_and_equivalent_rationals(self):
        fresh = deepcopy(dict(reversed(list(self.frozen.items()))))
        for path in [('kappa',), ('bit_coarse',), ('assembly', 'absorption_gap')]:
            value = fresh
            for key in path:
                value = value[key]
            q = Fraction(value)
            put(fresh, path, str(2*q.numerator) + '/' + str(2*q.denominator))
        self.write_json(self.fresh_path, fresh)
        self.check()

    def test_only_named_receipt_timings_can_vary(self):
        self.receipt['seconds'] = 987.25
        self.receipt['timings'] = {stage: 12.5 for stage in binding.STAGES}
        self.write_json(self.receipt_path, self.receipt)
        self.check()

    def test_every_certificate_leaf_is_bound(self):
        for path, value in leaves(self.frozen):
            with self.subTest(field=path):
                fresh = deepcopy(self.frozen)
                if type(value) is bool:
                    changed = not value
                elif type(value) is int:
                    changed = value + 1
                else:
                    try:
                        changed = str(Fraction(value) + 1)
                    except ValueError:
                        changed = value + ' changed'
                put(fresh, path, changed)
                self.write_json(self.fresh_path, fresh)
                with self.assertRaises(ValueError):
                    self.check()

    def test_exact_fraction_delta_below_display_precision_rejected(self):
        fresh = deepcopy(self.frozen)
        fresh['bit_moment_interval'][0] = str(Fraction(fresh['bit_moment_interval'][0])
                                               + Fraction(1, 10**200))
        self.write_json(self.fresh_path, fresh)
        with self.assertRaisesRegex(ValueError, 'certificate/bit_moment_interval/0'):
            self.check()

    def test_deleted_fields_added_metadata_and_list_order_rejected(self):
        for key in self.frozen:
            fresh = deepcopy(self.frozen)
            del fresh[key]
            self.write_json(self.fresh_path, fresh)
            with self.subTest(deleted=key), self.assertRaises(ValueError):
                self.check()
        mutations = []
        fresh = deepcopy(self.frozen)
        fresh['seconds'] = 10
        mutations.append(fresh)
        fresh = deepcopy(self.frozen)
        del fresh['assembly']['margins']
        mutations.append(fresh)
        fresh = deepcopy(self.frozen)
        fresh['ordinary_bootstrap_chain'].reverse()
        mutations.append(fresh)
        fresh = deepcopy(self.frozen)
        fresh['bit_profile']['W'] = str(fresh['bit_profile']['W'])
        mutations.append(fresh)
        fresh = deepcopy(self.frozen)
        fresh['independent_base_two_pass'] = 1
        mutations.append(fresh)
        for fresh in mutations:
            self.write_json(self.fresh_path, fresh)
            with self.assertRaises(ValueError):
                self.check()

    def test_coordinated_publication_and_frozen_kappa_change_rejected(self):
        self.record.update(kappa='1/1000', decimal='0.001')
        frozen = deepcopy(self.frozen)
        frozen.update(kappa='1/1000', kappa_decimal='0.001', kappa_scientific='1e-3')
        self.republish(frozen)  # Includes the changed certificate's correct digest.
        with self.assertRaisesRegex(ValueError, 'certificate/kappa'):
            self.check()

    def test_coordinated_frozen_profile_change_rejected(self):
        frozen = deepcopy(self.frozen)
        frozen['bit_profile']['rank_mass'] += 1
        self.republish(frozen)
        with self.assertRaisesRegex(ValueError, 'certificate/bit_profile/rank_mass'):
            self.check()

    def test_publication_only_change_and_wrong_digest_rejected(self):
        for field, value in [('kappa', '1/1000'), ('decimal', '0.001'),
                             ('certificate_sha256', '0'*64)]:
            record = dict(self.record, **{field: value})
            self.write_json(self.record_path, record)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()

    def test_changed_selected_manifest_rejected(self):
        self.record['source_manifest'] = 'different-manifest.json'
        self.write_bytes('different-manifest.json', b'{"files":{"other.py":"changed"}}')
        self.write_json(self.record_path, self.record)
        with self.assertRaisesRegex(ValueError, 'source manifest differs'):
            self.check()

    def test_receipt_proof_fields_are_bound(self):
        changes = {'status': 'FAIL', 'inputs_unchanged': False, 'files': True,
                   'manifest_sha256': '0'*64, 'kappa': '1/1000',
                   'kappa_scientific': '1e-3', 'fresh_stages': [], 'negative_controls': [],
                   'seconds': -1, 'timings': {'unknown_math_field': 1}}
        for key, value in changes.items():
            receipt = dict(self.receipt, **{key: value})
            self.write_json(self.receipt_path, receipt)
            with self.subTest(field=key), self.assertRaises(ValueError):
                self.check()
        self.write_json(self.receipt_path, dict(self.receipt, mathematical_claim=True))
        with self.assertRaisesRegex(ValueError, 'receipt fields'):
            self.check()

    def test_duplicate_json_keys_and_nonfinite_numbers_rejected(self):
        self.fresh_path.write_text('{"kappa":"1/2",' + json.dumps(self.frozen)[1:])
        with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
            self.check()
        self.write_json(self.fresh_path, self.frozen)
        self.write_json(self.receipt_path, dict(self.receipt, seconds=float('nan')))
        with self.assertRaisesRegex(ValueError, 'Non-finite JSON number'):
            self.check()

    def test_float_math_rejected_even_if_both_certificates_agree(self):
        frozen = deepcopy(self.frozen)
        frozen['bit_coarse'] = 0.125
        self.republish(frozen)
        self.write_json(self.fresh_path, frozen)
        with self.assertRaisesRegex(ValueError, 'Inexact or unsupported'):
            self.check()

    def test_cli_binding_checks_remain_active_under_optimization(self):
        command = [sys.executable, '-B', '-O', str(SCRIPT),
                   '--certificate', str(self.fresh_path), '--verification',
                   str(ROOT / 'research/community-pr279-audit/verification.json')]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        fresh = deepcopy(self.frozen)
        fresh['bit_profile']['W'] += 1
        self.write_json(self.fresh_path, fresh)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate/bit_profile/W', result.stderr)


if __name__ == '__main__':
    unittest.main()

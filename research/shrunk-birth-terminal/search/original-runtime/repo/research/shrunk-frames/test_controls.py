#!/usr/bin/env python3
"""Negative controls for the shrunk-frame deferred finite witness.

These controls target source omissions, altered inputs, paid rank accounting,
noncontracting children and invalid exact arithmetic. They do not substitute
for the full producer and literal reflection checks. Prepared for eumemic with
OpenAI Codex assistance; Apache-2.0, inherited notices retained.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Negative controls require assertions')

import argparse
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from verify import check_sources, compare_json, digest, safe_file, validate_profile

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]


class FrozenControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = check_sources(HERE, REPOSITORY)
        cls.profiles = {label: json.loads((HERE / (label + '-profile.json')).read_text())
                        for label in ('bit', 'complex')}
        sys.path.insert(0, str(REPOSITORY / 'scripts'))
        spec = importlib.util.spec_from_file_location('checked_cyclic_certificate', HERE / 'certificate.py')
        cls.certificate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.certificate)
        cls.certificate.ROOT = REPOSITORY

    def test_all_frozen_profiles_satisfy_physical_ledgers(self):
        for label, profile in self.profiles.items():
            validate_profile(profile, label)

    def test_frozen_exact_certificate_recomputed(self):
        expected = json.loads((HERE / 'certificate.json').read_text())
        actual = self.certificate.js(self.certificate.exact())
        self.assertEqual(actual, expected)

    def test_omitted_endpoint_charge_rejected(self):
        for label, original in self.profiles.items():
            changed = copy.deepcopy(original)
            changed['child_multiplicities']['1'] -= changed['N']
            with self.assertRaisesRegex(ValueError, 'rank mass'):
                validate_profile(changed, label)

    def test_nonshrinking_recursive_child_rejected(self):
        for label, original in self.profiles.items():
            changed = copy.deepcopy(original)
            changed['child_multiplicities'][str(changed['m'])] = 1
            with self.assertRaisesRegex(ValueError, 'recursive child'):
                validate_profile(changed, label)

    def test_understated_role_count_rejected(self):
        changed = copy.deepcopy(self.profiles['complex'])
        changed['R'] -= 1
        with self.assertRaisesRegex(ValueError, 'physical ledger'):
            validate_profile(changed, 'complex')

    def test_overstated_matching_rejected(self):
        changed = copy.deepcopy(self.profiles['complex'])
        changed['links'] += 1
        with self.assertRaisesRegex(ValueError, 'matching role ledger'):
            validate_profile(changed, 'complex')

    def test_missing_transitive_dependency_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['repository_files']['scripts/exclusion_circuit.py']
        with self.assertRaisesRegex(ValueError, 'dependency closure'):
            check_sources(HERE, REPOSITORY, changed)

    def test_omitted_physical_input_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['package_files']['inputs/deferred_23.json.gz']
        with self.assertRaisesRegex(ValueError, 'finite-input closure'):
            check_sources(HERE, REPOSITORY, changed)

    def test_changed_input_digest_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed['package_files']['inputs/witness_23.json.gz'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            check_sources(HERE, REPOSITORY, changed)

    def test_omitted_pinned_complex_dag_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['package_files']['inputs/complex-dag.json.gz']
        with self.assertRaisesRegex(ValueError, 'finite-input closure'):
            check_sources(HERE, REPOSITORY, changed)

    def test_changed_complex_dag_digest_rejected(self):
        with tempfile.TemporaryDirectory(prefix='shrunk-frames-altered-dag-') as directory:
            package = Path(directory)
            for name in self.manifest['package_files']:
                target = package / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE / name, target)
            name = 'inputs/complex-dag.json.gz'
            path = package / name
            graph = json.loads(gzip.decompress(path.read_bytes()))
            graph['args'][0] = graph['args'][1]
            path.write_bytes(gzip.compress(json.dumps(graph).encode(), mtime=0))
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                check_sources(package, REPOSITORY, self.manifest)
            # Rehashing a substituted DAG must not erase its immutable provenance.
            changed = copy.deepcopy(self.manifest)
            changed['package_files'][name] = digest(path)
            with self.assertRaisesRegex(ValueError, 'scalar-DAG provenance digest mismatch'):
                check_sources(package, REPOSITORY, changed)

    def test_replayed_complex_dag_rejects_duplicated_operand(self):
        from replayed_producer import build
        with tempfile.TemporaryDirectory(prefix='shrunk-frames-invalid-dag-') as directory:
            graph = json.loads(gzip.decompress((HERE / 'inputs/complex-dag.json.gz').read_bytes()))
            graph['args'][0] = graph['args'][1]
            path = Path(directory) / 'invalid.json.gz'
            path.write_bytes(gzip.compress(json.dumps(graph).encode(), mtime=0))
            with self.assertRaisesRegex(AssertionError, 'cancellation-free'):
                build(path, Path(directory) / 'invalid-producer')

    def test_manifest_parent_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe manifest path'):
            safe_file(HERE, '../certificate.json')

    def test_changed_regenerated_profile_rejected(self):
        with tempfile.TemporaryDirectory(prefix='shrunk-frames-negative-') as directory:
            changed = copy.deepcopy(self.profiles['complex'])
            changed['child_multiplicities']['1'] += 1
            path = Path(directory) / 'changed.json'
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'Frozen generated record mismatch'):
                compare_json(path, HERE / 'complex-profile.json')

    def test_next_bit_and_complex_grid_points_rejected(self):
        from fractions import Fraction as Q
        module = self.certificate
        self.assertFalse(module.contracts(module.profile('bit-profile.json'), module.COARSE + Q(1, 10**10)))
        self.assertFalse(module.contracts(module.profile('complex-profile.json'), module.COMPLEX + Q(1, 10**12)))

    def test_unshrunk_pr114_profile_rejects_new_complex_saving(self):
        module = self.certificate
        previous = json.loads((HERE / 'controls/pr114-complex-profile.json').read_text())
        previous['child_multiplicities'] = {int(t): c for t, c in previous['child_multiplicities'].items()}
        self.assertEqual((previous['R'], previous['deferred_roles']), (28705, 4706))
        self.assertTrue(module.contracts(previous, module.Q(109305097, 10**12)))
        self.assertFalse(module.contracts(previous, module.COMPLEX))
        self.assertTrue(module.contracts(module.profile('complex-profile.json'), module.COMPLEX))

    def test_optimized_verifier_rejected_before_any_regeneration(self):
        result = subprocess.run([sys.executable, '-O', str(HERE / 'verify.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('optimized Python is forbidden', result.stderr)


def main():
    global REPOSITORY
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, default=REPOSITORY)
    args = parser.parse_args()
    REPOSITORY = args.repository_root.resolve()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FrozenControls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Negative controls for the cyclic/deferred frozen finite witness.

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

from verify import (check_completed_core_audit, check_sources, compare_json,
                    digest, safe_file, validate_profile, validate_shared_composition,
                    validate_bit_composition)

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]


class FrozenControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = check_sources(HERE, REPOSITORY)
        cls.profiles = {label: json.loads((HERE / (label + '-profile.json')).read_text())
                        for label in ('bit', 'shared-bit', 'complex', 'shared-complex')}
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

    def test_shared_profile_reconstructed_from_paid_local_cores(self):
        validate_shared_composition(HERE)
        validate_bit_composition(HERE, json.loads((HERE / 'certificate.json').read_text()))

    def test_wrong_shared_width_rejected(self):
        changed = copy.deepcopy(self.profiles['shared-complex'])
        changed['W'] += 2 * changed['R']
        with self.assertRaisesRegex(ValueError, 'physical ledger'):
            validate_profile(changed, 'shared-complex')

    def test_missing_shared_exterior_rejected(self):
        changed = copy.deepcopy(self.profiles['shared-complex'])
        changed['child_multiplicities']['384'] -= 2 * changed['R']
        with self.assertRaisesRegex(ValueError, 'rank mass'):
            validate_profile(changed, 'shared-complex')

    def test_nonorthogonal_partition_rejected(self):
        from itertools import combinations
        partition = json.loads((HERE / 'inputs/shared-partition.json').read_text())
        masks = [sum(1 << j for j in triple) for triple in combinations(range(24), 3)]
        groups = partition['groups']
        i, j = next((i, j) for i in range(1, len(groups)) for j, t in enumerate(groups[i])
                    if any((masks[t] & masks[u]).bit_count() & 1 for u in groups[0][1:]))
        groups[0][0], groups[i][j] = groups[i][j], groups[0][0]
        with tempfile.TemporaryDirectory(prefix='shared-core-nonorthogonal-') as directory:
            path = Path(directory)
            shutil.copyfile(HERE / 'phase_check.py', path / 'phase_check.py')
            (path / 'partition.json').write_text(json.dumps(partition))
            result = subprocess.run([sys.executable, '-B', str(path / 'phase_check.py'),
                                     str(path / 'partition.json')], cwd=path,
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('non-orthonormal completed group basis', result.stderr)

    def test_understated_scalar_guard_and_unbound_core_source_rejected(self):
        audit = json.loads((HERE / 'reflection-audit.json').read_text())
        certificate = json.loads((HERE / 'certificate.json').read_text())
        local = self.profiles['complex']
        check_completed_core_audit(audit, local, certificate)
        changed = copy.deepcopy(certificate)
        changed['finite_bridge']['complex']['scalar_group_upper'] = audit['literal_global_scalar_groups'] - 1
        with self.assertRaisesRegex(ValueError, 'scalar charge exceeds'):
            check_completed_core_audit(audit, local, changed)
        changed = copy.deepcopy(certificate)
        account = changed['finite_bridge']['complex']
        account['scalar_group_upper'] -= account['shared_basis_phase_group_upper']
        account['shared_basis_phase_group_upper'] = 0
        with self.assertRaisesRegex(ValueError, 'Missing paid shared basis'):
            check_completed_core_audit(audit, local, changed)
        changed = copy.deepcopy(audit)
        changed['completed_core_source_inventory_bound'] = False
        with self.assertRaisesRegex(ValueError, 'bound source'):
            check_completed_core_audit(changed, local, certificate)

    def test_resurrected_role_and_duplicate_source_frame_rejected(self):
        from gauge_phase import validate_inventory
        local = self.profiles['complex']
        inventory = copy.deepcopy(local['physical_auxiliary_source_frames'])
        inventory[0]['count'] += 1
        with self.assertRaisesRegex(AssertionError, 'role count'):
            validate_inventory(inventory, local['R'], local['h'])
        inventory = copy.deepcopy(local['physical_auxiliary_source_frames'])
        inventory.append(copy.deepcopy(inventory[0]))
        with self.assertRaisesRegex(AssertionError, 'distinct source inventory'):
            validate_inventory(inventory, local['R'], local['h'])

    def test_ungauged_old_exterior_inventory_rejected(self):
        from sharing import profile
        local = copy.deepcopy(self.profiles['complex'])
        local['child_multiplicities'] = {r: n for r, n in local['child_multiplicities'].items() if int(r) < 552}
        local['child_multiplicities']['552'] = 2 * local['v'] * local['R']
        partition = json.loads((HERE / 'inputs/shared-partition.json').read_text())
        phase = json.loads((HERE / 'phase_check.json').read_text())
        gauge = json.loads((HERE / 'gauge-phase-audit.json').read_text())
        with self.assertRaisesRegex(AssertionError, 'auxiliary exterior inventory'):
            profile(local, partition, phase, gauge)

    def test_missing_grouped_gauge_complement_rejected(self):
        from sharing import profile
        partition = json.loads((HERE / 'inputs/shared-partition.json').read_text())
        phase = json.loads((HERE / 'phase_check.json').read_text())
        gauge = json.loads((HERE / 'gauge-phase-audit.json').read_text())
        width = next(iter(gauge['grouped_exterior_histogram']))
        gauge['grouped_exterior_histogram'][width] -= 2
        with self.assertRaisesRegex(AssertionError, 'gauge complement profile'):
            profile(self.profiles['complex'], partition, phase, gauge)

    def test_one_stage_bit_loss_rejected(self):
        changed = copy.deepcopy(self.profiles['shared-bit'])
        changed['L'] //= 2
        with self.assertRaisesRegex(ValueError, 'physical ledger'):
            validate_profile(changed, 'shared-bit')

    def test_omitted_paid_bit_adapter_calls_rejected(self):
        changed = json.loads((HERE / 'certificate.json').read_text())
        changed['finite_bridge']['bit_coarse']['paid_projector_adapter_calls'] -= 1
        with self.assertRaisesRegex(ValueError, 'paid adapter call binding'):
            validate_bit_composition(HERE, changed)

    def test_omitted_reuse_role_charge_rejected(self):
        changed = copy.deepcopy(self.profiles['complex'])
        changed['reused_roles'] -= 1
        with self.assertRaisesRegex(ValueError, 'matching role ledger'):
            validate_profile(changed, 'complex')

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

    def test_omitted_pinned_partition_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['package_files']['inputs/shared-partition.json']
        with self.assertRaisesRegex(ValueError, 'finite-input closure'):
            check_sources(HERE, REPOSITORY, changed)

    def test_omitted_nested_bit_dependency_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['package_files']['bit-sharing/profile161.json']
        with self.assertRaisesRegex(ValueError, 'nested bit-package closure'):
            check_sources(HERE, REPOSITORY, changed)

    def test_changed_nested_bit_input_and_rehashed_manifest_rejected(self):
        from bit_adapter import MINIMAL_V_PATH, package_inventory
        with tempfile.TemporaryDirectory(prefix='dual-core-altered-bit-') as directory:
            package = Path(directory)
            shutil.copytree(HERE / 'bit-sharing', package / 'bit-sharing')
            path = package / 'bit-sharing' / MINIMAL_V_PATH
            path.write_bytes(path.read_bytes() + b'corrupted')
            with self.assertRaisesRegex(ValueError, 'Nested bit source hash mismatch'):
                package_inventory(package)
            manifest_path = package / 'bit-sharing/MANIFEST.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['sha256'][MINIMAL_V_PATH] = digest(path)
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Immutable bit-package manifest digest mismatch'):
                package_inventory(package)

    def test_changed_partition_rejected_even_when_rehashed(self):
        with tempfile.TemporaryDirectory(prefix='shared-core-altered-partition-') as directory:
            package = Path(directory)
            for name in self.manifest['package_files']:
                target = package / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE / name, target)
            name = 'inputs/shared-partition.json'
            path = package / name
            partition = json.loads(path.read_text())
            partition['groups'][0][0] = partition['groups'][0][1]
            path.write_text(json.dumps(partition))
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                check_sources(package, REPOSITORY, self.manifest)
            changed = copy.deepcopy(self.manifest)
            changed['package_files'][name] = digest(path)
            with self.assertRaisesRegex(ValueError, 'partition provenance digest mismatch'):
                check_sources(package, REPOSITORY, changed)

    def test_changed_complex_dag_digest_rejected(self):
        with tempfile.TemporaryDirectory(prefix='cyclic-deferred-altered-dag-') as directory:
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
        with tempfile.TemporaryDirectory(prefix='cyclic-deferred-invalid-dag-') as directory:
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
        with tempfile.TemporaryDirectory(prefix='cyclic-deferred-negative-') as directory:
            changed = copy.deepcopy(self.profiles['complex'])
            changed['child_multiplicities']['1'] += 1
            path = Path(directory) / 'changed.json'
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'Frozen generated record mismatch'):
                compare_json(path, HERE / 'complex-profile.json')

    def test_next_bit_and_complex_grid_points_rejected(self):
        from fractions import Fraction as Q
        module = self.certificate
        bit = module.profile('shared-bit-profile.json')
        self.assertTrue(module.contracts(bit, module.COARSE))
        self.assertFalse(module.contracts(bit, module.COARSE + Q(1, 10**12)))
        shared = module.profile('shared-complex-profile.json')
        self.assertTrue(module.contracts(shared, module.COMPLEX))
        self.assertFalse(module.contracts(shared, module.COMPLEX + Q(1, 10**12)))

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

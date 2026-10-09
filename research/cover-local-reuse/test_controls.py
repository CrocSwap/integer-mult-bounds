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
from collections import Counter
from fractions import Fraction as Q
import gzip
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
        cls.result = certificate.exact()

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
        actual = certificate.js(self.result)
        self.assertEqual(actual, json.loads((ROOT / PACKAGE / 'certificate.json').read_text()))

    def test_completed_adapters_included_in_semantic_budget(self):
        c = self.result['complex']
        bridge = self.result['finite_bridge']
        b, semantic = bridge['complex'], bridge['semantic']
        self.assertEqual(b['coefficient_denominator_divides'], 38)
        self.assertEqual(semantic['fixed_odd_divisor'], 19)
        # Three stage banks have V/3 cells each. Every physical source gets
        # an adapter, including zero-width tails; both data banks finish.
        adapters = c['vertices_per_stage'] * (self.result['profile']['R'] + 2*self.result['profile']['v'])
        paid = 32*(c['m']+1)**3*adapters
        self.assertEqual(b['completed_adapter_group_upper'], paid)
        local = json.loads((ROOT / LOCAL / 'complex-profile.json').read_text())
        self.assertEqual(b['actual_M_operations'], 76778)
        self.assertEqual(b['guarded_M_operations'], 85577)
        row = dict(h=22, v=1540, R=local['virtual_R'], c=local['additions'],
                   q=local['roots'], total_M_operations=b['guarded_M_operations'])
        old = certificate.inherited.finite_bridge(c, row)
        self.assertEqual(b['scalar_group_upper'] - old['complex']['scalar_group_upper'], paid)
        self.assertGreater(semantic['E'], old['semantic']['E'])
        self.assertGreater(semantic['literal_charge'], old['semantic']['literal_charge'])
        self.assertEqual(semantic['strict_literal_gap'], semantic['E'] - semantic['literal_charge'])

    def test_bit_padding_and_omitted_zero_tails_match_physical_word(self):
        row = json.loads((ROOT / 'certificates/three-stage-cover-bit-input.json').read_text())
        b = self.result['bit']
        local = Counter()
        for histogram in row['local_rank_histograms'].values():
            local.update({int(r): 9*n for r, n in histogram.items()})
        tails = Counter()
        for nullity, count in row['exit_nullity_histogram'].items():
            width = b['m'] - 3*int(nullity)
            if width:
                tails[width] += 3*count
        self.assertEqual(b['local_copies_per_cell'], 9)
        self.assertEqual(b['zero_width_exteriors_omitted'], 3*row['exit_nullity_histogram']['23'])
        self.assertEqual(b['data_finish_child_multiplicities'], {2: 6*row['v']})
        local.update(tails)
        local.update({2: 6*row['v']})
        self.assertEqual(b['ideal_child_multiplicities'], dict(local))
        self.assertEqual(b['roles_per_cell']*b['m'] - sum(r*n for r, n in local.items()), 6072)

    def test_bit_full_fallback_and_atom_conversion_paid(self):
        b = self.result['bit']
        self.assertTrue(b['full_local_ring_fallback_charged'])
        self.assertTrue(b['fresh_group_roles_independent_of_inherited_weights'])
        self.assertEqual(b['coset_conditioning_factor'], 3)
        self.assertEqual(b['prime_bad_bound'], Q(6*b['m']**3, 2**80))
        self.assertLess(b['prime_bad_bound'], b['bad_fraction'])
        self.assertEqual(b['fallback_children_per_edge'], 32*b['m']**2)
        edges = sum(b['ideal_child_multiplicities'].values())
        self.assertEqual(b['edge_count_per_cell'], edges)
        self.assertGreater(b['added_bad_moment_upper'], 0)
        self.assertEqual(b['rank_mass_upper_per_cell'] - b['ideal_rank_mass_per_cell'],
                         b['bad_fraction']*b['fallback_children_per_edge']*edges)
        self.assertEqual(b['strict_gap'], 1-b['good_moment_upper']-b['added_bad_moment_upper'])
        self.assertEqual(b['effective_saving'],
                         (1-b['atom_exponent'])*b['coarse_saving'] +
                         b['atom_exponent']*b['ordinary_leaf_saving'])

    def test_bit_changed_source_nullity_rejected(self):
        import bit_padded
        row = copy.deepcopy(bit_padded.reconstruct())
        row['exit_nullity_histogram']['23'] -= 1
        with patch.object(bit_padded, 'reconstruct', return_value=row):
            with self.assertRaises(AssertionError):
                bit_padded.certificate()

    def test_local_cover_telescoping(self):
        p = certificate.cover_profile()
        self.assertEqual(p['h'], 22)
        self.assertEqual(p['v'], 1540)
        self.assertEqual(p['roles_per_cell'] * p['m'] - p['rank_per_cell'], 5082)
        self.assertEqual(sum(int(r) * n for r, n in p['child_multiplicities'].items()), p['rank_per_cell'])
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

    def test_missing_generalized_frame_binding_rejected(self):
        for name in ('complex-profile.json', 'reflection-audit.json'):
            self.local_change(name, lambda p: p.update(generalized_lagrangian_frames=False))

    def test_unfixed_reuse_handoff_rejected(self):
        self.local_change('complex-profile.json',
                          lambda p: p['arbitrary_frame_stats'].update(source_root_gauge_and_reuse_handoffs_fixed=False))

    def test_missing_generalized_source_gauge_binding_rejected(self):
        for name in ('complex-profile.json', 'reflection-audit.json'):
            self.local_change(name, lambda p: p.update(generalized_source_gauges=False))

    def test_changed_gauge_reuse_mapping_rejected(self):
        self.local_change('complex-profile.json',
                          lambda p: p['gauge_frame_stats'].update(reuse_mapping_fixed=False))

    def test_moved_source_injection_or_root_rejected(self):
        self.local_change('complex-profile.json',
                          lambda p: p['gauge_frame_stats'].update(source_injection_and_root_frames_fixed=False))

    def test_padded_profile_keeps_all_nine_local_copies(self):
        from padded_checks import profile
        independent = profile(json.loads((ROOT / LOCAL / 'complex-profile.json').read_text()))
        p = certificate.cover_profile()
        self.assertEqual(independent['child_multiplicities'], p['child_multiplicities'])
        self.assertEqual(independent['local_copies_per_cell'], 9)
        self.assertEqual(independent['local_cell_child_multiplicities'],
                         {r: 9*n for r, n in independent['local_child_multiplicities'].items()})
        self.assertEqual(independent['data_finish_cell_child_multiplicities'], {2: 6*independent['v']})

    def test_missing_padded_geometry_claim_rejected(self):
        original_loads = json.loads
        for flag in ('order_three_orthogonal_permutation', 'right_cosets_have_three_vertices',
                     'all_three_active_spaces_disjoint', 'all_local_histograms_retained_nine_times',
                     'completed_offsets_cancel', 'reversed_residual_is_forward_inverse',
                     'both_data_bank_finishes_paid', 'all_stage_tail_ranks_three_times_source_dimension',
                     'zero_rank_exteriors_are_rank_zero_adapters'):
            def changed(text, *args, **kwargs):
                record = original_loads(text, *args, **kwargs)
                if isinstance(record, dict) and 'exact_tail_definition' in record:
                    record[flag] = False
                return record
            with patch.object(certificate.json, 'loads', side_effect=changed):
                with self.assertRaises(AssertionError):
                    certificate.cover_profile()

    def test_padded_geometry_source_hash_mismatch_rejected(self):
        original_loads = json.loads
        def changed(text, *args, **kwargs):
            record = original_loads(text, *args, **kwargs)
            if isinstance(record, dict) and 'exact_tail_definition' in record:
                record['source_sha256'][LOCAL + '/reflection-audit.json'] = '0'*64
            return record
        with patch.object(certificate.json, 'loads', side_effect=changed):
            with self.assertRaises(AssertionError):
                certificate.cover_profile()

    def test_padded_geometry_omitted_source_hash_rejected(self):
        original_loads = json.loads
        def changed(text, *args, **kwargs):
            record = original_loads(text, *args, **kwargs)
            if isinstance(record, dict) and 'exact_tail_definition' in record:
                del record['source_sha256'][LOCAL + '/reflection-audit.json']
            return record
        with patch.object(certificate.json, 'loads', side_effect=changed):
            with self.assertRaises(AssertionError):
                certificate.cover_profile()

    def test_degenerate_frame_is_valid_under_generalized_contract(self):
        sys.path.insert(0, str(ROOT / LOCAL))
        from arbitrary_frames import general_frame
        # (1,1) is isotropic for the binary dot form, but its full L_U is Lagrangian.
        self.assertTrue(general_frame((3,), 2))

    def test_outside_ambient_frame_rejected(self):
        sys.path.insert(0, str(ROOT / LOCAL))
        from arbitrary_frames import general_frame
        with self.assertRaisesRegex(AssertionError, 'Lagrangian dimension'):
            general_frame((1 << 24,), 24)

    def test_noncontained_physical_gate_rejected(self):
        sys.path.insert(0, str(ROOT / LOCAL))
        from arbitrary_frames import optimize
        data = dict(ops=[('add', 0, 1)], h=2, R=2, op_frames={0: (1,)},
                    placed={0: (2,)}, reuse_pairs=[], last={}, root_frame={})
        with self.assertRaises(AssertionError):
            optimize(data)

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

    def test_missing_padded_bit_proof_rejected(self):
        changed = copy.deepcopy(self.manifest)
        del changed['files'][PACKAGE + '/BIT-PADDED.md']
        with self.assertRaisesRegex(ValueError, 'source dependency closure'):
            check_sources(ROOT, changed)

    def test_missing_restriction_dependency_rejected(self):
        for filename in ('restrict_dag.py', 'restriction-audit.json', 'inputs/restricted-dag.json.gz'):
            with self.subTest(filename=filename):
                changed = copy.deepcopy(self.manifest)
                del changed['files'][LOCAL + '/' + filename]
                with self.assertRaisesRegex(ValueError, 'source dependency closure'):
                    check_sources(ROOT, changed)

    def test_different_coordinate_restriction_rejected(self):
        sys.path.insert(0, str(ROOT / LOCAL))
        from restrict_dag import restrict_record
        original = json.loads(gzip.decompress((ROOT / LOCAL / 'inputs/complex-dag.json.gz').read_bytes()))
        with self.assertRaisesRegex(AssertionError, 'Only the certified first22 restriction'):
            restrict_record(original, (21, 23))

    def test_corrupted_restricted_dag_rejected(self):
        sys.path.insert(0, str(ROOT / LOCAL))
        import restrict_dag
        with tempfile.TemporaryDirectory(prefix='cover-restricted-control-') as directory:
            local = Path(directory)
            (local / 'inputs').mkdir()
            shutil.copyfile(ROOT / LOCAL / 'inputs/complex-dag.json.gz', local / 'inputs/complex-dag.json.gz')
            record = json.loads(gzip.decompress((ROOT / LOCAL / 'inputs/restricted-dag.json.gz').read_bytes()))
            record['D'][0] = record['D'][1]
            (local / 'inputs/restricted-dag.json.gz').write_bytes(gzip.compress(json.dumps(record).encode()))
            with patch.object(restrict_dag, 'HERE', local):
                with self.assertRaisesRegex(AssertionError, 'Frozen restricted DAG differs'):
                    restrict_dag.checked_record()

    def test_wrong_restricted_root_support_rejected(self):
        sys.path.insert(0, str(ROOT / LOCAL))
        from restrict_dag import restrict_record
        original = json.loads(gzip.decompress((ROOT / LOCAL / 'inputs/complex-dag.json.gz').read_bytes()))
        original['D'][0] = original['D'][1]
        with self.assertRaises(AssertionError):
            restrict_record(original)

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

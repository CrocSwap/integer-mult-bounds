"""Independent exact controls for the one-shear center circuit.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance; predecessor attribution
is retained in the package proof note and original source files.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import circuit
from independent import (closed_cost_formula, coefficient_check, dirty_basis_check,
                         factor_entries, mutation_controls, orbit_census)


def dense_source(h, changed=False):
    """Adapt the independent closed entries to the primary sparse interface."""
    dense = factor_entries(h, changed)
    return dict(h=h, triples=list(dense['triples']),
                gather=[tuple((i, x) for i, x in enumerate(column) if x)
                        for column in dense['V_columns']], scatter=list(dense['U_rows']))


class CenterCircuit(unittest.TestCase):
    def test_shear_matches_independent_entries_and_inverse_restores_input(self):
        for h in (8, 10, 12, 26):
            original = dense_source(h)
            snapshot = deepcopy(original)
            changed = circuit.shear(original, 1, 2, -1)
            with self.subTest(h=h):
                self.assertEqual(changed, dense_source(h, changed=True))
                self.assertEqual(circuit.shear(changed, 1, 2, 1), original)
                self.assertEqual(original, snapshot)
                self.assertEqual(len(changed['gather']), len(original['gather']))
                self.assertEqual(changed['h'], original['h'])

    def test_small_complete_products_and_digests_use_independent_contraction(self):
        for h in (8, 10):
            actual = circuit.verify_product(circuit.shear(dense_source(h), 1, 2, -1))
            independent = coefficient_check(h)
            with self.subTest(h=h):
                self.assertEqual(actual['coefficients_checked'], independent['coefficients_checked'])
                self.assertEqual(actual['coefficient_sha256'], independent['coefficient_sha256'])

    def test_product_mutations_pass_alphabet_but_fail_exact_identity(self):
        original = dense_source(8)
        changed = circuit.shear(original, 1, 2, -1)
        gather_only = deepcopy(changed)
        gather_only['scatter'] = original['scatter']
        wrong_sign = deepcopy(changed)
        position = next(i for i, row in enumerate(wrong_sign['scatter']) if row[2] == -2)
        row = list(wrong_sign['scatter'][position])
        row[2] = 2
        wrong_sign['scatter'][position] = tuple(row)
        for mutation in (gather_only, wrong_sign):
            circuit.validate(mutation)
            with self.assertRaisesRegex(ValueError, 'Central product coefficient mismatch'):
                circuit.verify_product(mutation)

    def test_invalid_moves_shapes_and_alphabets_are_rejected(self):
        original = dense_source(8)
        for move in ((1, 1, -1), (-1, 2, -1), (1, 8, -1), (1, 2, 0),
                     (True, 2, -1), (1, 2, True), (0, 1, -1)):
            with self.subTest(move=move), self.assertRaises(ValueError):
                circuit.shear(original, *move)
        mutations = []
        wrong = deepcopy(original)
        wrong['gather'][0] += ((0, 1),)
        mutations.append(wrong)
        wrong = deepcopy(original)
        wrong['gather'][0] = ((0, 2),)
        mutations.append(wrong)
        wrong = deepcopy(original)
        wrong['scatter'][0] = (3,) + wrong['scatter'][0][1:]
        mutations.append(wrong)
        wrong = deepcopy(original)
        wrong['scatter'][0] = (1.0,) + wrong['scatter'][0][1:]
        mutations.append(wrong)
        wrong = deepcopy(original)
        wrong['triples'] = wrong['triples'][::-1]
        mutations.append(wrong)
        for mutation in mutations:
            with self.assertRaises(ValueError):
                circuit.validate(mutation)

    def test_independent_orbit_census_matches_individual_moves(self):
        for h in (8, 10, 12, 26):
            individual = circuit.census(dense_source(h), seed=20)
            orbits = orbit_census(h)
            with self.subTest(h=h):
                self.assertEqual(orbits['orbits'], 16)
                self.assertEqual(sum(row['multiplicity'] for row in orbits['orbit_records']), 2*h*(h-1))
                for key in ('candidate_moves', 'admissible_moves', 'rejected_moves',
                            'delta_histogram', 'minimum_delta'):
                    self.assertEqual(orbits[key], individual[key])
                self.assertEqual(sum(row['multiplicity'] for row in orbits['minimizing_move_categories']),
                                 len(individual['minimizers']))
        self.assertEqual(orbits['admissible_moves'], 650)
        self.assertEqual(orbits['minimum_delta'], -1472)

    def test_negative_two_is_one_signed_update_and_saving_changes_sign(self):
        expected_saving = {8: -10, 10: 0, 26: 1472}
        for h, expected in expected_saving.items():
            before = circuit.charge(dense_source(h))
            after = circuit.charge(dense_source(h, changed=True))
            formula = closed_cost_formula(h)
            with self.subTest(h=h):
                self.assertEqual(before['G_plus_H'] - after['G_plus_H'], expected)
                self.assertEqual(circuit.closed_saving(h), expected)
                self.assertEqual(formula['saving_gather_plus_scatter'], expected)
                self.assertEqual(after['H'], formula['changed_scatter'])
        changed = dense_source(26, changed=True)
        # The new -2 entries are exactly triples containing 0 and two of the
        # 23 outside coordinates, so this tests the signed-unit price on 253
        # actual occurrences through the independently derived total below.
        self.assertEqual(sum(row.count(-2) for row in changed['scatter']), 23*22//2)
        self.assertEqual(circuit.charge(changed), dict(G=12352, H=31557, G_plus_H=43909))

    def test_dirty_center_basis_controls_and_missing_operations(self):
        controls = [dirty_basis_check(h) for h in (4, 6, 8)]
        self.assertEqual(sum(row['invocations_checked'] for row in controls), 356)
        self.assertTrue(all(row['all_dirty_center_inputs_restored'] for row in controls))
        mutations = mutation_controls()
        self.assertTrue(mutations['omitted_inverse_gather_rejected'])
        self.assertTrue(mutations['omitted_initial_dirty_scatter_rejected'])
        for key in ('gather_changed_without_inverse_scatter_change',
                    'negative_two_numerator_flipped_positive'):
            self.assertNotEqual(mutations[key]['actual_numerator'], mutations[key]['expected_numerator'])

    def test_source_pin_mutation_and_missing_input_fail(self):
        from verify import verify_pins
        with tempfile.TemporaryDirectory(prefix='center-shear-pin-control-') as directory:
            root = Path(directory)
            path = root / 'fixture.py'
            content = b'# exact input\n'
            path.write_bytes(content)
            manifest = dict(base_commit='test-only', sha256={'fixture.py': sha256(content).hexdigest()})
            self.assertEqual(verify_pins(root, manifest)['pinned_inputs'], 1)
            path.write_bytes(content + b'# altered\n')
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch: fixture.py'):
                verify_pins(root, manifest)
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                verify_pins(root, manifest)


if __name__ == '__main__':
    unittest.main(verbosity=2)

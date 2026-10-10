"""Relabelled supports, dirty scratch, and the aligned paired witness."""
from fractions import Fraction as Q
from dataclasses import replace
from itertools import combinations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from dag_network import exact_invocation, shared_scalar_model
from paired_exclusion_circuit import PairedExclusionCircuit
from shared_point_circuit import SharedPointCircuit
from aligned_paired_network import certificate, circuit, parameters, KAPPA
from certify import certify_parameters
from make_aligned_paired_patch import patched_files


class AlignedPairedNetwork(unittest.TestCase):
    def aligned(self, h):
        orders = [[j for j in range(h) if j not in (i, i ^ 1)] + [i ^ 1]
                  for i in range(h)]
        return SharedPointCircuit(h, PairedExclusionCircuit(h - 1), point_orders=orders)

    def test_relabelled_supports_independently_and_both_frames(self):
        for h in (6, 8, 10, 12):
            c = self.aligned(h)
            support = [0] * len(c.args)
            for node in sorted(c.active):
                if c.args[node]:
                    a, b = c.args[node]
                    self.assertFalse(support[a] & support[b])
                    support[node] = support[a] | support[b]
                else:
                    support[node] = 1 << (node - 1)
            for (common, target), node in c.outputs.items():
                expected = sum(1 << i for i, triple in enumerate(c.inputs)
                               if set(triple) & set(target) == {common})
                self.assertEqual(support[node], expected)
            self.assertTrue(c.verify()['all_partial_outputs_exact'])
            self.assertTrue(c.verify_frames()['reverse_complement_frames_nested'])

    def test_every_dirty_input_basis_vector_and_three_stage_exchange(self):
        for h in (6, 8):
            code = self.aligned(h).program()
            for inverse in (False, True):
                self.assertTrue(exact_invocation(h, inverse, code)['exact_linear_map'])
        code = self.aligned(6).program()
        for seed in (1, 109):
            result = shared_scalar_model(6, seed, code)
            self.assertTrue(result['bank_exchange'] and result['all_scratch_restored'])

    def test_full_size_supports_from_the_actual_global_dag(self):
        c = circuit()
        active = sorted(c.active)
        stars = [0] * c.h
        pair_stars = {p: 0 for p in combinations(range(c.h), 2)}
        for index, triple in enumerate(c.inputs):
            bit = 1 << index
            for point in triple:
                stars[point] |= bit
            for pair in combinations(triple, 2):
                pair_stars[pair] |= bit
        outputs = []
        for (common, target), node in c.outputs.items():
            a, b = [point for point in target if point != common]
            excluded = (pair_stars[tuple(sorted((common, a)))] |
                        pair_stars[tuple(sorted((common, b)))])
            outputs.append((node, stars[common] & ~excluded))

        # Bound memory while expanding every coefficient, without provenance.
        width = 1024
        chunk_mask = (1 << width) - 1
        for offset in range(0, len(c.inputs), width):
            support = [0] * len(c.args)
            for node in active:
                if c.args[node] is None:
                    index = node - 1 - offset
                    if 0 <= index < width:
                        support[node] = 1 << index
                else:
                    a, b = c.args[node]
                    if support[a] & support[b]:
                        self.fail(f'overlapping supports at offset {offset}, node {node}')
                    support[node] = support[a] | support[b]
            for node, expected in outputs:
                if support[node] != (expected >> offset) & chunk_mask:
                    self.fail(f'wrong output at offset {offset}, node {node}')

    def test_point_orders_must_be_permutations_of_the_other_points(self):
        orders = [[j for j in range(6) if j != i] for i in range(6)]
        orders[0][-1] = 0
        with self.assertRaises(AssertionError):
            SharedPointCircuit(6, PairedExclusionCircuit(5), point_orders=orders)

    def test_full_size_counts_and_strict_parameter_margin(self):
        c = certificate()
        self.assertEqual(c['global_circuit']['additions'], 435450)
        self.assertEqual(c['global_circuit']['merged_additions'], 55200)
        self.assertEqual(int(c['bit_counts']['side_roles_per_invocation']), 494250)
        self.assertEqual(int(c['bit_counts']['W']), 394839648000000)
        self.assertEqual(int(c['bit_counts']['s']), 49354954232864000000)
        self.assertEqual(int(c['bit_counts']['D']), 1767136000000)
        self.assertEqual(Q(c['bit_counts']['eta']), Q(23, 642375000))
        margin = Q(739738521, 400000000000000000000000000)
        self.assertEqual(Q(c['witness']['minimum_margin']), margin)
        self.assertGreater(margin, KAPPA)
        self.assertEqual(KAPPA / Q(1, 2**59), Q(17, 16))
        self.assertTrue(all(Q(x) > 0 for x in c['witness']['constraint_slacks'].values()))
        self.assertLess(Q(c['fixed_network_ceiling']['value']), Q(1, 2**58))
        with self.assertRaises(ValueError):
            certify_parameters(replace(parameters(), kappa=margin),
                               generalized_beta=True, strict_margin=True,
                               layout_model='nonadjacent', guard_model='stopping',
                               assembly_model='tight-gaussian')

    def test_patch_updates_the_relabelled_graph_and_all_bit_dependencies(self):
        files = list(patched_files())
        self.assertEqual(len(files), 7)
        for name, old, new in files:
            self.assertNotIn('296/10', new)
            self.assertNotIn('{296}', new)
            self.assertNotIn(r'\kappa=2^{-59}', new)
            if name.endswith('03-motifs.tex'):
                self.assertIn('Relabel the local inputs and outputs', new)
                for number in ('435450', '494250', '55200', '394839648000000',
                               '49354954232864000000', '642375000'):
                    self.assertIn(number, new)
            elif name.endswith('04-swap.tex'):
                self.assertIn(r'\frac{305}{10^{11}}', new)
            elif name.endswith('05-layers.tex'):
                self.assertIn(r'\tau=1-\frac{305}{10^{11}}', new)
                self.assertIn('46184298777878576000000', new)
            elif name.endswith('08-assembly.tex'):
                self.assertIn(r'\kappa=17\cdot2^{-63}', new)
                self.assertIn(r'\frac{739738521}{400000000000000000000000000}', new)
                for retained in (r'(32db)^{1/4}', r'd^{1000}\le b^{199}',
                                 r'g_5=1/4-\delta-5\epsilon/4', r'b\ge2^{40}'):
                    self.assertIn(retained, new)


if __name__ == '__main__':
    unittest.main()

"""Independent rank masses, assembly boundaries, and shifted-error controls."""
from dataclasses import replace
from fractions import Fraction as Q
from math import comb, isqrt
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import batched_stream_network as network


def independent_bit_moment(a, roles, batch_corner=True):
    h = 28
    v, m = comb(h, 5), h**3
    N, copies = v**3, v*v*roles
    width = 2*v*v*(v+roles)
    decreasing = 3*v*v*comb(h, 2)*(h-2)
    rank_sum = width*m-N+2*decreasing
    chunks = [m-4*h, m-2*h*h, m-2*h*h-2*h+2]
    multiplicities = [copies, copies, 2*N]
    logarithms = [Q(9997, 1000), Q(512, 10**5), Q(7411, 10**5), Q(768, 10**4)]
    if batch_corner:
        chunks.append(h*h)
        multiplicities.append(copies)
        logarithms.append(Q(33323, 10**4))
    singleton = rank_sum-sum(c*r for c, r in zip(multiplicities, chunks))
    masses = [singleton]+[c*r for c, r in zip(multiplicities, chunks)]
    upper = sum((Q(mass, width*m)/(1-a*log)
                 for mass, log in zip(masses, logarithms)), Q(0))
    return dict(width=width, rank_sum=rank_sum, singleton=singleton,
                masses=masses, m=m, upper=upper)


class BatchedStreamNetwork(unittest.TestCase):
    def test_independent_five_class_mass_accounting(self):
        expected = independent_bit_moment(network.BIT_SAVING, network.ROLES)
        actual = network.bit_certificate()
        self.assertEqual(expected['width'], 171343663010956800)
        self.assertEqual(expected['rank_sum'], 3761335710703551052800)
        self.assertEqual(expected['singleton'], 78990496465220121600)
        self.assertEqual(sum(expected['masses']), expected['rank_sum'])
        self.assertEqual(actual['counts']['W'], expected['width'])
        self.assertEqual(actual['counts']['original_rank_sum'], expected['rank_sum'])
        self.assertEqual(actual['moment_upper'], expected['upper'])
        self.assertEqual(actual['rank_mass_weights'],
                         [Q(mass, expected['width']*expected['m'])
                          for mass in expected['masses']])
        self.assertGreater(actual['strict_gap'], 0)

    def test_next_bit_saving_and_predecessor_width_are_rejected(self):
        larger = network.BIT_SAVING+Q(1, 10**12)
        self.assertGreater(independent_bit_moment(larger, network.ROLES)['upper'], 1)
        with self.assertRaises(AssertionError):
            network.bit_certificate(a=larger)
        with self.assertRaises(AssertionError):
            network.assembly(roles=11840940)

    def test_controlled_corner_is_required_at_the_selected_exponent(self):
        without_corner = independent_bit_moment(network.BIT_SAVING, network.ROLES,
                                                batch_corner=False)
        self.assertGreater(without_corner['upper'], 1)
        self.assertGreater(without_corner['singleton'], network.bit_certificate()['counts']['singleton_calls'])

    def test_independent_complex_moment_and_negative_exponent_control(self):
        h, v, roles = 28, comb(28, 3), 93838
        m = h**3
        width = 2*v*v*(v+roles+h+1)
        copies = v*v*(roles+h+1)
        rank_sum = width*m-2*v**3+6*v*v*h*(h+1)
        ranks = [m-2*h, m-h*h]
        masses = [rank_sum-copies*sum(ranks)]+[copies*r for r in ranks]
        logs = [Q(9997, 1000), Q(2555, 10**6), Q(36368, 10**6)]
        expected = sum((Q(mass, width*m)/(1-network.COMPLEX_SAVING*ell)
                        for mass, ell in zip(masses, logs)), Q(0))
        actual = network.complex_certificate()
        self.assertEqual(actual['moment_upper'], expected)
        self.assertLess(expected, 1)
        with self.assertRaises(ValueError):
            network.complex_certificate(a=10*network.COMPLEX_SAVING)

    def test_all_assembly_constraints_and_independent_seven_margins(self):
        p = network.parameters()
        actual = network.assembly()
        expected = dict(g1=1-p.epsilon*(1+p.c),
                        g2=p.epsilon*p.c*(1-p.tau),
                        g3=p.epsilon*(1-p.lamp),
                        g4=(1-p.epsilon)*(1-p.tau),
                        g5=1-p.delta-2*p.epsilon,
                        g6=1-p.delta-p.epsilon, g7=p.epsilon)
        self.assertEqual(actual['margins'], expected)
        self.assertEqual(len(actual['constraints']), 29)
        self.assertTrue(all(x > 0 for x in actual['constraints'].values()))
        self.assertEqual(actual['minimum_margin'], Q(824432362644205083, 5*10**24))
        self.assertEqual(actual['absorption_gap'], Q(2362644205083, 5*10**24))
        self.assertEqual(actual['factor_over_aligned'], Q(82443, 812))
        self.assertGreater(actual['factor_over_aligned'], 100)
        with self.assertRaisesRegex(ValueError, 'absorption gap'):
            network.assembly(replace(p, kappa=actual['minimum_margin']))
        # PR #10's epsilon caps the prefix margin at 1.25e-7.
        with self.assertRaisesRegex(ValueError, 'absorption gap'):
            network.assembly(replace(p, epsilon=Q(7999999, 16000000)))
        with self.assertRaisesRegex(ValueError, 'gaussian_cost'):
            network.assembly(replace(p, delta=1-2*p.epsilon))
        with self.assertRaisesRegex(ValueError, 'Bulk guard mismatch'):
            network.assembly(replace(p, C1=Q(6, 5)))

    def test_grid_selection_and_bilateral_width_negative_control(self):
        result=network.grid_selection()
        self.assertGreater(result['next_bit_moment'],1)
        self.assertEqual([row['epsilon'] for row in result['epsilon_candidates']],
                         [Q(499999917,10**9),Q(499999918,10**9)])
        self.assertEqual(max(row['margin_upper'] for row in result['epsilon_candidates']),
                         network.assembly()['minimum_margin'])
        # The source-only checkpoint cannot support the bilateral exponent.
        with self.assertRaises(AssertionError):
            network.assembly(roles=8791733)

    def test_cached_construction_rejects_changed_sources_and_artifacts(self):
        from experiments.ternary_stream_certify import (
            CONSTRUCTION_FILES,CONSTRUCTION_ARTIFACTS,cached_construction)
        from experiments.ternary_target_certify import file_hash
        data=json.loads((ROOT/'certificates/ternary-stream-producer.json').read_text())
        data['proof_sha256'].update({name:file_hash(ROOT/name) for name in CONSTRUCTION_FILES})
        with tempfile.TemporaryDirectory(prefix='test-construction-binding-') as folder:
            folder=Path(folder)
            for name,filename in CONSTRUCTION_ARTIFACTS.items():
                path=folder/filename
                path.write_bytes(name.encode())
                data['artifact_sha256'][name]=file_hash(path)
            saved=folder/'producer.json'
            saved.write_text(json.dumps(data))
            self.assertEqual(cached_construction(folder,saved)['top_split'],[16,12])
            (folder/CONSTRUCTION_ARTIFACTS['rewritten_dag']).write_bytes(b'changed graph')
            with self.assertRaisesRegex(ValueError,'artifact: rewritten_dag'):
                cached_construction(folder,saved)
            data['proof_sha256'][CONSTRUCTION_FILES[0]]='0'*64
            saved.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'construction dependency'):
                cached_construction(folder,saved)

    def test_bilateral_certificate_covers_strict_dual_frames(self):
        data=json.loads((ROOT/'certificates/ternary-stream-producer.json').read_text())
        self.assertEqual(data['global_roles']['current'],8771396)
        self.assertEqual(data['stream']['dual_frame_links'],20337)
        self.assertEqual(data['stream']['physical_rank_sum_each_orientation'],250925864)
        control=data['strict_dual_control']
        self.assertEqual(control['dual_frame_dimensions'],[24,27])
        self.assertEqual((control['original_roles'],control['new_roles']),(7,6))
        self.assertEqual(control['dirty_wrapper']['all_basis_symbols'],22)
        self.assertTrue(control['dirty_wrapper']['dirty_wrapper_restores_every_scratch'])
        self.assertTrue(control['dirty_wrapper']['forward_inverse_exact'])
        self.assertFalse(control['dirty_wrapper']['intended_map_is_identity'])
        for frame in control['frames']:
            self.assertEqual((frame['total_rank'],frame['loss']),(600,0))

    def test_bulk_guard_covers_every_path_case(self):
        guard = network.assembly()['guard']
        self.assertEqual(guard['q'], 22120)
        self.assertEqual(guard['C1'], Q(11999, 10000))
        self.assertTrue(all(2*rank > guard['q'] for rank in guard['selected_ranks']))
        self.assertEqual(guard['path_moment_upper'],
                         {'no_bulk': Q(553, 4000),
                          'rank_21896': Q(47817969, 47897500),
                          'rank_21168': Q(1213697, 1260000)})
        self.assertTrue(all(x < Q(999, 1000) for x in guard['path_moment_upper'].values()))
        self.assertGreaterEqual(guard['dependency_constant']*(1-guard['theta_upper']), guard['E'])

    def test_shifted_error_requires_larger_F_but_same_precision(self):
        # A legal alpha=100 shows why exact chirp magnitude cannot stand in
        # for the absolute generator error after its B-bit shift.
        alpha, B = 100, 11400
        old_enclosure_shortfall_bits = B-Q(355, 113)*alpha**2/(4*Q(693, 1000))
        self.assertGreater(old_enclosure_shortfall_bits, 60)
        # Include near-cutoff p, perfect squares, and length/power boundaries.
        for p in list(range(101, 401))+[1024, 10000, 20000]:
            for alpha in range(2, isqrt(p-1)+1):
                B = (114*alpha*alpha+99)//100
                # Exact ceil(sqrt(p)/(2 alpha)), including square p.
                window = isqrt(p-1)//(2*alpha)+1
                length = 3*window+1
                required = p+29*p+B+(length-1).bit_length()+11
                self.assertLessEqual(length, p)
                self.assertLess(required, 34*p)
        p = network.parameters()
        self.assertGreater(1-2*p.epsilon, 0)
        self.assertGreater(1-p.delta-2*p.epsilon, p.kappa)


if __name__ == '__main__':
    unittest.main()

"""Mathematical and source-binding controls for the standalone refinement."""
import copy
import json
import unittest
import verify as V


class PrecisionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read = lambda name: json.loads((V.HERE/'inputs'/name).read_bytes())
        cls.complex = read('paired-cube-sinks-input.json')
        cls.bit = read('paired-cube-bit-physical-input.json')
        cls.scalar = read('paired-cube-complex-input.json')

    def test_recomputed_certificate(self):
        self.assertEqual(V.regenerate(), json.loads((V.HERE/'certificate.json').read_bytes()))

    def test_supplier_successors_fail_characteristic(self):
        result = V.arithmetic(self.complex, self.bit, self.scalar)
        for side in ('complex', 'bit'):
            self.assertGreaterEqual(V.Q(result['supplier_successors'][side]['total_lower']), 1)

    def test_headline_successor_fails_compact_layer(self):
        bridge = V.A.reconstruct_bridge(self.scalar, self.complex)
        effective = (1-V.ATOM)*V.COARSE+V.ATOM*V.M.OLD
        with self.assertRaisesRegex(ValueError, 'compact_phase_layer_above_kappa'):
            V.A.balanced_assembly(bridge, effective, V.COMPLEX, V.KAPPA+V.Q(1,V.GRID),
                eta=V.ETA,beta=V.BETA,phase_gap=V.PHASE_GAP)

    def test_omit_paid_child(self):
        row = copy.deepcopy(self.bit)
        rank = next(k for k,n in row['local_histogram'].items() if int(k)>0 and n>0)
        row['local_histogram'][rank] -= 1
        with self.assertRaisesRegex(ValueError, 'Paid child reconstruction'):
            V.paid_profile(row)

    def test_wrong_positive_router_charge(self):
        bridge = V.A.reconstruct_bridge(self.scalar, self.complex)
        bridge['literal_charge'] = bridge['E']+1
        effective = (1-V.ATOM)*V.COARSE+V.ATOM*V.M.OLD
        with self.assertRaisesRegex(ValueError, 'literal_scalar_guard'):
            V.A.balanced_assembly(bridge,effective,V.COMPLEX,V.KAPPA,
                eta=V.ETA,beta=V.BETA,phase_gap=V.PHASE_GAP)

    def test_duplicate_rank_and_bool_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate normalized child rank'):
            V.M.normalize_children({'2':1,2:1},72)
        with self.assertRaisesRegex(ValueError, 'invalid child rank/count'):
            V.M.normalize_children({'2':True},72)

    def test_wrong_revision_label(self):
        manifest = json.loads((V.HERE/'SOURCE.json').read_bytes())
        manifest['upstream_commit'] = '0'*40
        with self.assertRaisesRegex(ValueError, 'Wrong upstream revision label'):
            V.check_source_manifest(manifest,lambda name:(V.HERE/name).read_bytes())

    def test_modified_raw_input(self):
        manifest = json.loads((V.HERE/'SOURCE.json').read_bytes())
        def modified(name):
            data=(V.HERE/name).read_bytes()
            return data+b' ' if name.startswith('inputs/') else data
        with self.assertRaisesRegex(ValueError, 'Source byte mismatch: inputs/'):
            V.check_source_manifest(manifest,modified)


if __name__ == '__main__':
    unittest.main()

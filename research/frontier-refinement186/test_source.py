"""Binding controls for all imported bundle bytes, cores and new own sources."""
import copy,json,unittest
import source_binding as S
class SourceControls(unittest.TestCase):
    def manifest(self):return json.loads((S.HERE/'SOURCE.json').read_bytes())
    def test_complete_actual_sources(self):S.check_sources()
    def test_wrong_revision(self):
        data=self.manifest();data['upstream_commit']='0'*40
        with self.assertRaisesRegex(ValueError,'wrong source revision'):S.check_manifest(data)
    def test_omitted_dependency(self):
        data=self.manifest();data['dependency_sha256'].pop(next(iter(data['dependency_sha256'])))
        with self.assertRaisesRegex(ValueError,'wrong frozen dependency closure'):S.check_manifest(data)
    def test_rebound_core_hash(self):
        data=self.manifest();data['dependency_sha256']['research/paired-cube-scalar-audit/independent_sinks.py']='0'*64
        with self.assertRaisesRegex(ValueError,'wrong frozen dependency closure'):S.check_manifest(data)
    def test_changed_raw_witness(self):
        data=self.manifest();target='research/coordinated-frames-and-entrance-banks/selected/complex/physical-pairs.json.gz'
        with self.assertRaisesRegex(ValueError,'dependency bytes changed'):S.check_manifest(data,lambda p:(S.ROOT/p).read_bytes()+(b' ' if p==target else b''))
    def test_missing_own_tests_or_wrapper(self):
        for name in S.OWN_FILES:
            data=self.manifest();del data['source_sha256'][name]
            with self.assertRaisesRegex(ValueError,'incomplete own source closure'):S.check_manifest(data)
    def test_changed_derived_input(self):
        data=self.manifest()
        with self.assertRaisesRegex(ValueError,'own source bytes changed'):S.check_manifest(data,read_owned=lambda p:(S.HERE/p).read_bytes()+(b' ' if p=='inputs/physical-sinks.json' else b''))
    def test_sparse_scalar_raw_joint_binding(self):
        import scalar
        values=scalar.raw_inputs();self.assertEqual(len(values),6);self.assertEqual(len(values[-1]),46)
if __name__=='__main__':unittest.main()

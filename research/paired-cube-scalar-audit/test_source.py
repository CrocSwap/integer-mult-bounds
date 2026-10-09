"""Source-binding controls separate from the mathematical scalar controls."""
import copy
import json
import unittest
import verify as V

class SourceControls(unittest.TestCase):
    def manifest(self):
        return json.loads((V.HERE/'SOURCE.json').read_bytes())
    def check(self,data,read=None):
        return V.check_source_manifest(data,read or (lambda p:(V.ROOT/p).read_bytes()),
                                      lambda p:(V.HERE/p).read_bytes())
    def test_full_raw_source_closure(self):
        self.check(self.manifest())
    def test_wrong_revision_label(self):
        data=self.manifest();data['upstream_commit']='0'*40
        with self.assertRaisesRegex(ValueError,'wrong upstream revision'):self.check(data)
    def test_input_manifest_cannot_relabel_modified_sources(self):
        data=self.manifest();name=next(iter(data['upstream_sha256']))
        data['upstream_sha256'][name]='0'*64
        with self.assertRaisesRegex(ValueError,'wrong frozen input closure'):self.check(data)
    def test_changed_raw_input_rejected(self):
        with self.assertRaisesRegex(ValueError,'upstream source changed'):
            self.check(self.manifest(),lambda p:(V.ROOT/p).read_bytes()+b' ')
    def test_rebound_checker_rejected(self):
        data=self.manifest();data['audit_sha256']['independent_bit.py']='0'*64
        with self.assertRaisesRegex(ValueError,'wrong reviewed checker pin'):self.check(data)
    def test_omitted_wrapper_or_source_test_rejected(self):
        for name in ('verify.py','test_source.py'):
            data=self.manifest();del data['audit_sha256'][name]
            with self.assertRaisesRegex(ValueError,'incomplete audit source closure'):self.check(data)

if __name__=='__main__':unittest.main()

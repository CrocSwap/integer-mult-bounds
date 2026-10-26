"""Own evidence-omission tests; never imports or runs verify.py mathematics.

Prepared for Artus's Tintagel campaign with OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('owned_pr647_integrity', ROOT/'integrity.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
authenticate = module.authenticate
IntegrityError = module.IntegrityError
REQUIRED_FILES = module.REQUIRED_FILES
REQUIRED_SOURCE_PROOFS = module.REQUIRED_SOURCE_PROOFS

def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()

def repin(root, name):
    manifest = json.loads((root/'SHA256SUMS.json').read_bytes())
    manifest[name] = sha256((root/name).read_bytes()).hexdigest()
    (root/'SHA256SUMS.json').write_bytes(encoded(manifest))

class IntegrityCoverage(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)/'package'
        shutil.copytree(ROOT, root)
        return root

    def test_pristine_retains_original_authentication_receipt(self):
        expected = json.loads((ROOT/'RESULTS.json').read_bytes())['checks']['source_byte_authentication']
        self.assertEqual(authenticate(ROOT), expected)
        self.assertEqual(set(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()), REQUIRED_FILES)

    def test_each_required_file_missing(self):
        for name in sorted(REQUIRED_FILES):
            with self.subTest(file=name):
                root=self.fixture();(root/name).unlink()
                with self.assertRaises(IntegrityError): authenticate(root)

    def test_each_consistently_omitted_file_and_manifest_entry(self):
        for name in sorted(REQUIRED_FILES-{'SHA256SUMS.json'}):
            with self.subTest(file=name):
                root=self.fixture();(root/name).unlink()
                manifest=json.loads((root/'SHA256SUMS.json').read_bytes());del manifest[name]
                (root/'SHA256SUMS.json').write_bytes(encoded(manifest))
                with self.assertRaises(IntegrityError):authenticate(root)

    def test_each_source_proof_row_omitted_with_rehashed_source(self):
        for name in REQUIRED_SOURCE_PROOFS:
            with self.subTest(proof=name):
                root=self.fixture();source=json.loads((root/'SOURCE.json').read_bytes())
                source['included_proof_sources']=[r for r in source['included_proof_sources'] if r['file']!=name]
                (root/'SOURCE.json').write_bytes(encoded(source));repin(root,'SOURCE.json')
                with self.assertRaises(IntegrityError):authenticate(root)

    def test_original_provider_omission_with_both_lists_rewritten(self):
        root=self.fixture();(root/'PROVIDER-PROOF.md').unlink()
        source=json.loads((root/'SOURCE.json').read_bytes())
        source['included_proof_sources']=[r for r in source['included_proof_sources'] if r['file']!='PROVIDER-PROOF.md']
        (root/'SOURCE.json').write_bytes(encoded(source))
        manifest=json.loads((root/'SHA256SUMS.json').read_bytes());del manifest['PROVIDER-PROOF.md']
        manifest['SOURCE.json']=sha256((root/'SOURCE.json').read_bytes()).hexdigest()
        (root/'SHA256SUMS.json').write_bytes(encoded(manifest))
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_notice_and_optional_manifest_cannot_disappear(self):
        root=self.fixture();(root/'NOTICE.md').unlink();(root/'SHA256SUMS.json').unlink()
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_empty_or_extra_manifest_coverage(self):
        for manifest in ({},dict(json.loads((ROOT/'SHA256SUMS.json').read_bytes()),extra='0'*64)):
            root=self.fixture();(root/'SHA256SUMS.json').write_bytes(encoded(manifest))
            with self.assertRaises(IntegrityError):authenticate(root)

    def test_each_retained_proof_corrupted_with_consistent_digest_rewrites(self):
        for name in ('PROVIDER-PROOF.md','CYCLIC-COROLLARY.md',*REQUIRED_SOURCE_PROOFS[1:]):
            with self.subTest(proof=name):
                root=self.fixture();(root/name).write_bytes(b'NO PROOF\n');repin(root,name)
                if name in REQUIRED_SOURCE_PROOFS:
                    source=json.loads((root/'SOURCE.json').read_bytes())
                    for row in source['included_proof_sources']:
                        if row['file']==name:row['sha256']=sha256((root/name).read_bytes()).hexdigest()
                    (root/'SOURCE.json').write_bytes(encoded(source));repin(root,'SOURCE.json')
                with self.assertRaises(IntegrityError):authenticate(root)

    def test_attribution_corrupted_with_consistent_manifest_rewrite(self):
        root=self.fixture();(root/'NOTICE.md').write_bytes(b'NO ATTRIBUTION\n');repin(root,'NOTICE.md')
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_self_declared_duplicate_proof_inventory_rehashed(self):
        root=self.fixture();source=json.loads((root/'SOURCE.json').read_bytes())
        source['included_proof_sources'].append(source['included_proof_sources'][0])
        (root/'SOURCE.json').write_bytes(encoded(source));repin(root,'SOURCE.json')
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_duplicate_json_keys_rejected(self):
        root=self.fixture();raw=(root/'SHA256SUMS.json').read_bytes()
        digest=json.loads(raw)['README.md'];(root/'SHA256SUMS.json').write_bytes(raw[:-2]+b',"README.md":"'+digest.encode()+b'"}\n')
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_extra_file_even_if_listed_and_hashed(self):
        root=self.fixture();(root/'unexpected.txt').write_bytes(b'extra\n');repin(root,'unexpected.txt')
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_symlink_rejected_before_reading_target(self):
        root=self.fixture();saved=(root/'NOTICE.md').read_bytes();(root/'NOTICE.md').unlink()
        target=root.parent/'notice-outside-package';target.write_bytes(saved)
        (root/'NOTICE.md').symlink_to(target)
        with self.assertRaises(IntegrityError):authenticate(root)

    def test_explicit_whole_release_authenticity_boundary(self):
        # Self-consistency is not an externally approved release signature.
        # Intentional mutable-file edits need an external revision/archive pin.
        root=self.fixture();(root/'README.md').write_bytes((root/'README.md').read_bytes()+b'\nUnreviewed fixture addition.\n')
        repin(root,'README.md')
        self.assertEqual(authenticate(root),authenticate(ROOT))

if __name__=='__main__':
    unittest.main(verbosity=2)

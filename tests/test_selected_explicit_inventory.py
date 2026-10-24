"""Closed-export provenance tests; no scientific replay.

Douglas Colkitt, with substantial OpenAI assistance. Apache-2.0.
"""
import json
from pathlib import Path
import tempfile
import unittest
from test_selected_proof_binding import checker, fixture


class ExplicitInventory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = fixture(self.root)
        self.manifest = self.root / self.record['source_manifest']
        self.data = json.loads(self.manifest.read_text())
        self.data['format'] = 'repository-files-sha256-v1'
        del self.data['package_roots']
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.data))

    def test_closed_export_binds_bytes_not_unexported_neighbors(self):
        checker.check(self.record, self.root)
        (self.root / 'supplier/unused.py').write_text('not exported')
        checker.check(self.record, self.root)
        (self.root / 'supplier/PROOF.md').write_text('changed proof')
        with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
            checker.check(self.record, self.root)

    def test_rejects_aliases_and_traversal(self):
        digest = self.data['files']['supplier/PROOF.md']
        for name in ['../PROOF.md', '/supplier/PROOF.md', 'supplier//PROOF.md',
                     './supplier/PROOF.md', 'supplier/../supplier/PROOF.md',
                     'supplier\\PROOF.md']:
            with self.subTest(name=name):
                self.data['files'] = {name: digest}
                self.save()
                with self.assertRaisesRegex(ValueError, 'Noncanonical'):
                    checker.check(self.record, self.root)

    def test_rejects_file_and_directory_symlinks_even_inside_root(self):
        proof = self.root / 'supplier/PROOF.md'
        proof.rename(self.root / 'original.md')
        proof.symlink_to(self.root / 'original.md')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            checker.check(self.record, self.root)
        proof.unlink()
        (self.root / 'original.md').rename(proof)
        (self.root / 'supplier').rename(self.root / 'real-supplier')
        (self.root / 'supplier').symlink_to(self.root / 'real-supplier', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            checker.check(self.record, self.root)

    def test_primary_proof_cannot_point_to_unexported_neighbor(self):
        self.record['proof'] = 'decoy.md'
        with self.assertRaisesRegex(ValueError, 'not covered'):
            checker.check(self.record, self.root)


if __name__ == '__main__':
    unittest.main()

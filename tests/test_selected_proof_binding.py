"""Primary-proof provenance regressions; synthetic files, not theorem checks.

Mihir Srivastava, with substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'selected_proof_checker', ROOT / 'scripts/verify_selected_result.py')
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def fixture(root, modern=True):
    """Two inventory key spaces with an independently mutable review receipt."""
    package = root / 'supplier'
    package.mkdir()
    (package / 'PROOF.md').write_bytes(b'frozen primary proof\n')
    (root / 'supplement.md').write_bytes(b'frozen supplement\n')
    (root / 'review.md').write_bytes(b'publication status may change\n')
    (root / 'validation.json').write_text('{}', encoding='utf-8')
    (root / 'certificate.json').write_text('{"kappa":"1/1000"}', encoding='utf-8')
    (root / 'decoy.md').write_bytes(b'NO PROOF\n')
    proof_hash = sha256((package / 'PROOF.md').read_bytes()).hexdigest()
    if modern:
        manifest_path = root / 'manifest.json'
        manifest = {'format': 'repository-packages-sha256-v1',
                    'package_roots': ['supplier'],
                    'files': {'supplier/PROOF.md': proof_hash}}
    else:
        manifest_path = package / 'MANIFEST.json'
        manifest = {'files': {'PROOF.md': proof_hash}}
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return dict(kappa='1/1000', decimal='0.001', certificate='certificate.json',
                certificate_sha256=sha256((root / 'certificate.json').read_bytes()).hexdigest(),
                source_manifest=manifest_path.relative_to(root).as_posix(),
                proof='supplier/PROOF.md', review='review.md', validation='validation.json',
                proof_supplements={'supplement.md': sha256((root / 'supplement.md').read_bytes()).hexdigest()})


class SelectedProofBinding(unittest.TestCase):
    def each_layout(self, run):
        for modern in (False, True):
            with self.subTest(modern=modern), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                run(root, fixture(root, modern))

    def test_inventory_proof_in_both_layouts(self):
        self.each_layout(lambda root, record:
                         self.assertEqual(checker.check(record, root), Fraction(1, 1000)))

    def test_supplement_only_proof_in_both_layouts(self):
        def run(root, record):
            record['proof'] = 'supplement.md'
            self.assertEqual(checker.check(record, root), Fraction(1, 1000))
        self.each_layout(run)

    def test_reject_unpinned_primary_proof(self):
        def run(root, record):
            # Keep all certificate, source, supplement and arithmetic bytes fixed.
            for target in ('decoy.md', 'review.md', 'validation.json', 'certificate.json'):
                changed = dict(record, proof=target)
                with self.subTest(target=target), self.assertRaisesRegex(
                        ValueError, 'primary proof is not covered'):
                    checker.check(changed, root)
        self.each_layout(run)

    def test_reject_same_bytes_at_unpinned_path(self):
        def run(root, record):
            (root / 'copy.md').write_bytes((root / record['proof']).read_bytes())
            record['proof'] = 'copy.md'
            with self.assertRaisesRegex(ValueError, 'primary proof is not covered'):
                checker.check(record, root)
        self.each_layout(run)

    def test_legacy_relative_key_is_not_repository_relative(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            record = fixture(root, modern=False)
            (root / 'PROOF.md').write_bytes((root / 'supplier/PROOF.md').read_bytes())
            record['proof'] = 'PROOF.md'
            with self.assertRaisesRegex(ValueError, 'primary proof is not covered'):
                checker.check(record, root)

    def test_normalized_proof_path(self):
        def run(root, record):
            record['proof'] = 'supplier/../supplier/./PROOF.md'
            self.assertEqual(checker.check(record, root), Fraction(1, 1000))
        self.each_layout(run)

    def test_receipts_remain_mutable(self):
        def run(root, record):
            (root / record['review']).write_bytes(b'new publication status\n')
            (root / record['validation']).write_text('{"published":true}', encoding='utf-8')
            self.assertEqual(checker.check(record, root), Fraction(1, 1000))
        self.each_layout(run)

    def test_old_digest_and_arithmetic_guards_remain(self):
        def run(root, record):
            for key, value in (('kappa', '1/2'), ('decimal', '0.5'),
                               ('certificate_sha256', '0' * 64), ('proof_supplements', {})):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    checker.check(dict(record, **{key: value}), root)
            changed = deepcopy(record)
            changed['proof_supplements']['supplement.md'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'proof supplement changed'):
                checker.check(changed, root)
            (root / record['proof']).write_bytes(b'changed primary proof\n')
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(record, root)
        self.each_layout(run)

    def test_source_membership_cannot_be_added_without_inventory_match(self):
        def run(root, record):
            manifest_path = root / record['source_manifest']
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['files']['../decoy.md'] = sha256((root / 'decoy.md').read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(dict(record, proof='decoy.md'), root)
        self.each_layout(run)

    def test_missing_and_outside_proofs_rejected(self):
        def run(root, record):
            with tempfile.TemporaryDirectory() as outside:
                target = Path(outside) / 'outside.md'
                target.write_bytes(b'outside\n')
                for name in ('missing.md', str(target)):
                    with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Invalid selected file'):
                        checker.check(dict(record, proof=name), root)
        self.each_layout(run)

    def test_resolved_aliases_preserve_existing_path_semantics(self):
        def run(root, record):
            alias = root / 'alias.md'
            try:
                alias.symlink_to(root / record['proof'])
            except (OSError, NotImplementedError) as exc:
                self.skipTest('symlinks unavailable: ' + str(exc))
            self.assertEqual(checker.check(dict(record, proof='alias.md'), root), Fraction(1, 1000))
            alias.unlink()
            alias.symlink_to(root / 'decoy.md')
            with self.assertRaisesRegex(ValueError, 'primary proof is not covered'):
                checker.check(dict(record, proof='alias.md'), root)
        self.each_layout(run)

    def test_optimized_cli_still_fails_closed(self):
        result = subprocess.run([sys.executable, '-I', '-B', '-O',
                                 str(ROOT / 'scripts/verify_selected_result.py')],
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Assertions must remain enabled', result.stderr)


if __name__ == '__main__':
    unittest.main()

"""Reject publication metadata that is detached from its reviewed certificate."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest
import tempfile
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_result_check', ROOT / 'scripts/verify_selected_result.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SelectedResult(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'certificates/selected-result.json').read_text())

    def test_current_selection(self):
        checker.check(self.record)

    def test_reject_detached_claim_or_proof(self):
        mutations = [
            ('kappa', '1/1000'), ('decimal', '0.001'),
            ('certificate_sha256', '0' * 64), ('proof_supplements', {}),
        ]
        for key, value in mutations:
            with self.subTest(field=key):
                record = deepcopy(self.record)
                record[key] = value
                with self.assertRaises(ValueError):
                    checker.check(record)

    def test_reject_changed_supplement(self):
        record = deepcopy(self.record)
        name = next(iter(record['proof_supplements']))
        record['proof_supplements'][name] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'proof supplement changed'):
            checker.check(record)

    def test_historical_hpe_context_is_explicit_and_both_versions_are_bound(self):
        relative = 'scripts/verify_hpe_lean_binding.py'
        original = (ROOT / 'scripts/historical-ci-inputs/verify_hpe_lean_binding.py').read_bytes()
        live = (ROOT / relative).read_bytes()
        digest = sha256(original).hexdigest()
        self.assertEqual(checker.supplement_bytes(ROOT, relative, digest), live)
        self.assertEqual(checker.supplement_bytes(ROOT, relative, digest, True), original)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'scripts/historical-ci-inputs').mkdir(parents=True)
            source = root / relative
            source.write_bytes(live)
            archived = root / 'scripts/historical-ci-inputs/verify_hpe_lean_binding.py'
            archived.write_bytes(original + b'corruption')
            with self.assertRaisesRegex(ValueError, 'Historical HPE supplement changed'):
                checker.supplement_bytes(root, relative, digest, True)
            archived.write_bytes(original)
            source.write_bytes(live + b'unknown successor')
            self.assertNotEqual(sha256(checker.supplement_bytes(root, relative, digest, True)).hexdigest(), digest)
        checkpoint = json.loads((ROOT / 'certificates/checkpoints/frontier1042.json').read_bytes())
        with self.assertRaisesRegex(ValueError, 'Selected proof supplement changed'):
            checker.check(checkpoint)
        checker.check(checkpoint, historical=True)
        checker.check(self.record)

    def test_optimized_interpreter_fails_closed(self):
        result = subprocess.run([sys.executable, '-O', str(ROOT / 'scripts/verify_selected_result.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Assertions must remain enabled', result.stderr)

    def test_repository_package_inventory_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = root / 'supplier'
            package.mkdir()
            source = package / 'proof.md'
            source.write_text('frozen proof\n')
            digest = sha256(source.read_bytes()).hexdigest()
            cert = root / 'certificate.json'
            cert.write_text('{"kappa":"1/1000"}')
            manifest = root / 'manifest.json'
            inventory = {'format': 'repository-packages-sha256-v1',
                         'package_roots': ['supplier'],
                         'files': {'supplier/proof.md': digest}}
            manifest.write_text(json.dumps(inventory))
            record = dict(kappa='1/1000', decimal='0.001', certificate='certificate.json',
                          certificate_sha256=sha256(cert.read_bytes()).hexdigest(),
                          source_manifest='manifest.json', proof='supplier/proof.md',
                          review='supplier/proof.md', validation='certificate.json',
                          proof_supplements={'supplier/proof.md': digest})
            checker.check(record, root)
            source.write_text('changed\n')
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(record, root)
            source.write_text('frozen proof\n')
            extra = package / 'unreviewed.py'
            extra.write_text('extra\n')
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(record, root)
            extra.unlink()
            for roots in (['..'], ['.'], ['supplier', 'supplier']):
                inventory['package_roots'] = roots
                manifest.write_text(json.dumps(inventory))
                with self.subTest(roots=roots), self.assertRaises(ValueError):
                    checker.check(record, root)


if __name__ == '__main__':
    unittest.main()

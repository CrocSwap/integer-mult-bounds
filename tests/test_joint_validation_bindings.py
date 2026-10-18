"""Reject unknown receipt/certificate bytes during the derived-binding repair."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('joint_bindings', ROOT / 'scripts/refresh_joint_validation_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BindingRepair(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        (root / 'certificates').mkdir()
        for name, _old, _certificate, _new in module.CASES:
            for suffix in ('-kappa.json', '-validation.json'):
                relative = 'certificates/' + name + suffix
                (root / relative).write_bytes((ROOT / relative).read_bytes())
        for relative in (module.PAIR_PATH, module.PAIR_SOURCE):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
        return root

    def test_current_exact_bindings_and_idempotence(self):
        module.refresh()
        with tempfile.TemporaryDirectory() as td:
            root = self.fixture(td)
            before = {p: p.read_bytes() for p in root.rglob('*.json')}
            module.refresh(root, write=True)
            module.refresh(root)
            self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_original_stale_receipts_refresh_to_exact_current_bytes(self):
        old_bindings = {
            'joint-dual': 'cd820c5f75f2de6b8bf1068e7c9a58010d2cf50062954f7e19ebea97a258be6d',
            'skip-frame': '9f57831c261dfb6b3bfbe94be75bfa5a3faa05768b7d500281e7398623ad115a',
        }
        with tempfile.TemporaryDirectory() as td:
            root = self.fixture(td)
            expected = {}
            for name, old_receipt, certificate, new_receipt in module.CASES:
                target = root / ('certificates/' + name + '-validation.json')
                expected[target] = target.read_bytes()
                stale = expected[target].replace(certificate.encode(), old_bindings[name].encode())
                self.assertEqual(sha256(stale).hexdigest(), old_receipt)
                target.write_bytes(stale)
            with self.assertRaisesRegex(ValueError, 'Stale derived binding'):
                module.refresh(root)
            module.refresh(root, write=True)
            self.assertEqual({p: p.read_bytes() for p in expected}, expected)

    def test_pair_original_binding_and_unknown_source_or_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.fixture(td)
            target = root / module.PAIR_PATH
            expected = target.read_bytes()
            stale = expected.replace(module.PAIR_SOURCE_SHA256.encode(), module.PAIR_OLD_SOURCE.encode())
            self.assertEqual(sha256(stale).hexdigest(), module.PAIR_OLD_RECEIPT)
            target.write_bytes(stale)
            with self.assertRaisesRegex(ValueError, 'Stale pair-frame binding'):
                module.refresh(root)
            module.refresh(root, write=True)
            self.assertEqual(target.read_bytes(), expected)
            for relative in (module.PAIR_PATH, module.PAIR_SOURCE):
                changed = root / relative
                original = changed.read_bytes()
                changed.write_bytes(original + b'corrupt')
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(ValueError, 'Unrecognized pair'):
                    module.refresh(root, write=True)
                self.assertEqual({p: p.read_bytes() for p in before}, before)
                changed.write_bytes(original)

    def test_unknown_receipt_or_certificate_rejects_without_partial_writes(self):
        for suffix in ('-kappa.json', '-validation.json'):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as td:
                root = self.fixture(td)
                target = root / ('certificates/skip-frame' + suffix)
                target.write_bytes(target.read_bytes() + b' ')
                before = {p: p.read_bytes() for p in root.rglob('*.json')}
                with self.assertRaisesRegex(ValueError, 'Unrecognized'):
                    module.refresh(root, write=True)
                self.assertEqual({p: p.read_bytes() for p in before}, before)


if __name__ == '__main__':
    unittest.main()

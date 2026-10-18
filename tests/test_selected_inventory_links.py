"""Source-inventory closure on a stable filesystem; no supplier code is run.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'selected_inventory_checker', ROOT / 'scripts/verify_selected_result.py')
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

# OS assignment 69 rotates the exhaustive domain; no random coverage claim.
LINK_CASES = ('directory_inside', 'directory_outside', 'cycle', 'dangling')
LINK_CASES = LINK_CASES[69 % len(LINK_CASES):] + LINK_CASES[:69 % len(LINK_CASES)]


def fixture(root, modern):
    """Minimal valid record for each of the two supported inventory layouts."""
    package = root / 'supplier'
    (package / 'nested').mkdir(parents=True)
    proof = package / 'nested/proof.txt'
    proof.write_bytes(b'frozen fixture; not a mathematical proof\n')
    certificate = root / 'certificate.json'
    certificate.write_text('{"kappa":"1/1000"}', encoding='utf-8')
    manifest = root / 'manifest.json' if modern else package / 'MANIFEST.json'
    prefix = 'supplier/' if modern else ''
    inventory = {'files': {prefix + 'nested/proof.txt': sha256(proof.read_bytes()).hexdigest()}}
    if modern:
        inventory.update(format='repository-packages-sha256-v1', package_roots=['supplier'])
    manifest.write_text(json.dumps(inventory), encoding='utf-8')
    return dict(kappa='1/1000', decimal='0.001', certificate='certificate.json',
                certificate_sha256=sha256(certificate.read_bytes()).hexdigest(),
                source_manifest=manifest.relative_to(root).as_posix(),
                proof='supplier/nested/proof.txt', review='supplier/nested/proof.txt',
                validation='certificate.json',
                proof_supplements={'supplier/nested/proof.txt': sha256(proof.read_bytes()).hexdigest()})


def add_link(root, case):
    package = root / 'supplier'
    link = package / 'linked'
    if case == 'directory_inside':
        link.symlink_to('nested', target_is_directory=True)
    elif case == 'directory_outside':
        outside = root / 'unlisted'
        outside.mkdir()
        (outside / 'extra.py').write_bytes(b'UNREVIEWED = 69\n')
        link.symlink_to('../unlisted', target_is_directory=True)
    elif case == 'cycle':
        link.symlink_to('.', target_is_directory=True)
    elif case == 'dangling':
        link.symlink_to('missing')
    else:
        raise ValueError(case)
    return link


class SelectedInventoryLinks(unittest.TestCase):
    def each_layout(self, run):
        for modern in (False, True):
            with self.subTest(modern=modern), tempfile.TemporaryDirectory() as td:
                root = Path(td).resolve()
                run(root, fixture(root, modern), modern)

    def make_symlink(self, link, target):
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('symlinks unavailable: ' + str(exc))

    def test_ordinary_nested_inventory(self):
        self.each_layout(lambda root, record, modern:
                         self.assertEqual(checker.check(record, root), Fraction(1, 1000)))

    def test_reject_unenumerated_links(self):
        def run(root, record, modern):
            for case in LINK_CASES:
                with self.subTest(case=case):
                    try:
                        link = add_link(root, case)
                    except (OSError, NotImplementedError) as exc:
                        self.skipTest('symlinks unavailable: ' + str(exc))
                    try:
                        # Direct filesystem witnesses, independent of the walk.
                        if case == 'directory_outside':
                            self.assertEqual((link / 'extra.py').read_bytes(), b'UNREVIEWED = 69\n')
                        elif case == 'directory_inside':
                            self.assertTrue((link / 'proof.txt').is_file())
                        elif case == 'cycle':
                            self.assertTrue((link / 'nested/proof.txt').is_file())
                        else:
                            self.assertFalse(link.exists())
                            self.assertTrue(link.is_symlink())
                        with self.assertRaisesRegex(ValueError, 'Package symlink is not a regular file'):
                            checker.check(record, root)
                    finally:
                        link.unlink()
        self.each_layout(run)

    def test_pinned_contained_file_alias(self):
        def run(root, record, modern):
            alias = root / 'supplier/alias.txt'
            self.make_symlink(alias, 'nested/proof.txt')
            manifest = root / record['source_manifest']
            inventory = json.loads(manifest.read_text())
            key = 'supplier/alias.txt' if modern else 'alias.txt'
            inventory['files'][key] = sha256(alias.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(inventory), encoding='utf-8')
            self.assertEqual(checker.check(record, root), Fraction(1, 1000))
            # Coverage remains byte-sensitive even through a supported alias.
            alias.write_bytes(b'changed pinned bytes\n')
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(record, root)
        self.each_layout(run)

    def test_reject_unlisted_contained_file_alias(self):
        def run(root, record, modern):
            self.make_symlink(root / 'supplier/alias.txt', 'nested/proof.txt')
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(record, root)
        self.each_layout(run)

    def test_reject_pinned_escaping_file_alias(self):
        def run(root, record, modern):
            outside = root / 'outside.txt'
            outside.write_bytes(b'outside supplier\n')
            alias = root / 'supplier/alias.txt'
            self.make_symlink(alias, '../outside.txt')
            manifest = root / record['source_manifest']
            inventory = json.loads(manifest.read_text())
            inventory['files']['supplier/alias.txt' if modern else 'alias.txt'] = sha256(outside.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(inventory), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Package symlink escapes root'):
                checker.check(record, root)
        self.each_layout(run)


    def test_reject_nested_directory_links(self):
        def run(root, record, modern):
            outside = root / 'unlisted'
            outside.mkdir()
            (outside / 'extra.txt').write_bytes(b'unlisted nested target\n')
            link = root / 'supplier/nested/linked'
            for target in ('../nested', '../../unlisted'):
                with self.subTest(target=target):
                    self.make_symlink(link, target)
                    try:
                        self.assertTrue(link.is_dir())
                        with self.assertRaisesRegex(ValueError, 'Package symlink is not a regular file'):
                            checker.check(record, root)
                    finally:
                        link.unlink()
        self.each_layout(run)

    def test_reject_self_and_two_link_cycles(self):
        def run(root, record, modern):
            link = root / 'supplier/loop'
            peer = root / 'supplier/peer'
            for target in ('loop', 'peer'):
                with self.subTest(target=target):
                    self.make_symlink(link, target)
                    try:
                        if target == 'peer':
                            self.make_symlink(peer, 'loop')
                        with self.assertRaisesRegex(ValueError, 'Package symlink is not a regular file'):
                            checker.check(record, root)
                    finally:
                        link.unlink()
                        if peer.is_symlink():
                            peer.unlink()
        self.each_layout(run)

    def test_reject_wrong_alias_digest(self):
        def run(root, record, modern):
            alias = root / 'supplier/alias.txt'
            self.make_symlink(alias, 'nested/proof.txt')
            before = alias.read_bytes()
            manifest = root / record['source_manifest']
            inventory = json.loads(manifest.read_text())
            key = 'supplier/alias.txt' if modern else 'alias.txt'
            inventory['files'][key] = '0' * 64
            manifest.write_text(json.dumps(inventory), encoding='utf-8')
            # The target's original digest and bytes are still correct. Only
            # the alias's independent inventory entry has an incorrect digest.
            self.assertEqual(alias.read_bytes(), before)
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                checker.check(record, root)
        self.each_layout(run)


if __name__ == '__main__':
    unittest.main()

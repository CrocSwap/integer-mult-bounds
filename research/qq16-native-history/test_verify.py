# SPDX-License-Identifier: Apache-2.0
"""Source and receipt boundary controls for the native-history package.

Chris R with substantial OpenAI Codex assistance. Adapted from #4167's export
controls. These checks exercise transport and authentication failure modes;
the ordinary/optimised scientific replays are separate registered evidence.
"""
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def snapshot(root):
    """Reading may alter atime; all other recorded filesystem state is fixed."""
    result = {}
    for path in sorted(root.rglob('*')):
        stat = path.stat()
        result[str(path.relative_to(root))] = (
            stat.st_mode, stat.st_mtime_ns, stat.st_ino,
            digest(path.read_bytes()) if path.is_file() else None,
        )
    return result


def raw_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def alias_mutation(value):
    """Produce a Python-equal, JSON-type-distinct bool/integer replacement."""
    if isinstance(value, bool):
        return int(value), True
    if isinstance(value, int) and value in (0, 1):
        return bool(value), True
    if isinstance(value, dict):
        for key, child in value.items():
            changed, found = alias_mutation(child)
            if found:
                result = copy.deepcopy(value)
                result[key] = changed
                return result, True
    if isinstance(value, list):
        for index, child in enumerate(value):
            changed, found = alias_mutation(child)
            if found:
                result = copy.deepcopy(value)
                result[index] = changed
                return result, True
    return value, False


class Boundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='qq16-history-export-')
        self.root = Path(self.tmp.name) / 'checkout'
        self.package = self.root / 'research' / HERE.name
        self.addCleanup(self.remove_export)
        shutil.copytree(HERE, self.package,
                        ignore=shutil.ignore_patterns('__pycache__'))
        registration = json.loads((HERE / 'VERIFY.json').read_bytes())
        for rel in registration['inputs']:
            path = Path(rel)
            self.assertFalse(path.is_absolute())
            self.assertNotIn('..', path.parts)
            source, target = ROOT / path, self.root / path
            self.assertTrue(source.is_file(), rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def remove_export(self):
        if self.root.exists():
            self.root.chmod(0o755)
            for path in self.root.rglob('*'):
                if path.is_dir():
                    path.chmod(0o755)
        self.tmp.cleanup()

    def replay(self, *args, optimized=True, ok=True, needle=None):
        result = subprocess.run(
            [sys.executable, '-I', '-Werror', '-B',
             *(['-O'] if optimized else []),
             str(self.package / 'verify.py'), *args],
            cwd=self.root,
            env=dict(os.environ, PATH='/nonexistent-qq16-git-free'),
            capture_output=True, text=True, timeout=60,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode == 0, ok, output)
        if needle is not None:
            self.assertIn(needle, output)
        if ok:
            self.assertFalse(result.stderr, output)
        return output

    def test_normal_and_optimized_readonly_check_only_export(self):
        """Fast transport check, explicitly not the fitted scientific replay."""
        for path in self.root.rglob('*'):
            path.chmod(0o555 if path.is_dir() else 0o444)
        self.root.chmod(0o555)
        before = snapshot(self.root)
        for optimized in (False, True):
            self.replay('--check-only', optimized=optimized,
                        needle='PASS_QQ16_NATIVE_HISTORY_CHECK_ONLY')
            self.assertEqual(before, snapshot(self.root))
        self.assertFalse((self.root / '.git').exists())

    def test_authentication_precedes_inherited_and_local_execution(self):
        source = self.root / 'research/physical-complex-controller/machine.py'
        raw = source.read_bytes()
        source.write_bytes(b"raise RuntimeError('INHERITED_POISON_EXECUTED')\n" + raw)
        fixture = self.package / 'fitted_fixture.py'
        fixture_raw = fixture.read_bytes()
        fixture.write_bytes(b"raise RuntimeError('LOCAL_POISON_EXECUTED')\n" + fixture_raw)
        # Default entry point, not check-only: rejected before fitted execution.
        output = self.replay(ok=False, needle='canonical input integrity')
        self.assertNotIn('INHERITED_POISON_EXECUTED', output)
        self.assertNotIn('LOCAL_POISON_EXECUTED', output)
        source.write_bytes(raw)
        output = self.replay(ok=False, needle='local module integrity')
        self.assertNotIn('LOCAL_POISON_EXECUTED', output)

    def test_outer_archive_and_manifest_seals(self):
        for name, message in (
            ('inputs/PR4167-MANIFEST.json', 'retained manifest integrity'),
            ('inputs/PR4167.tar', 'retained archive integrity'),
        ):
            with self.subTest(name=name):
                path = self.package / name
                raw = path.read_bytes()
                path.write_bytes(raw + b' ')
                self.replay('--check-only', ok=False, needle=message)
                path.write_bytes(raw)

    def test_retained_members_below_outer_seal(self):
        """Test-only resealing reaches inner validation; no inherited execution."""
        archive_path = self.package / 'inputs/PR4167.tar'
        manifest_path = self.package / 'inputs/PR4167-MANIFEST.json'
        original_archive = archive_path.read_bytes()
        original_manifest = manifest_path.read_bytes()
        members = []
        with tarfile.open(fileobj=io.BytesIO(original_archive), mode='r:') as src:
            for member in src:
                if member.isfile():
                    with src.extractfile(member) as stream:
                        members.append((copy.copy(member), stream.read()))
        self.assertTrue(members)
        for mutation, message in (
            ('content', 'retained content integrity'),
            ('duplicate', 'retained member kind/path'),
            ('link', 'retained member kind/path'),
            ('missing', 'missing retained member'),
        ):
            with self.subTest(mutation=mutation):
                out = io.BytesIO()
                with tarfile.open(fileobj=out, mode='w:') as dst:
                    selected = members[:-1] if mutation == 'missing' else members
                    for index, (member, raw) in enumerate(selected):
                        member = copy.copy(member)
                        if index == 0 and mutation == 'content':
                            raw = b'X' + raw
                            member.size = len(raw)
                        if index == 0 and mutation == 'link':
                            member.type = tarfile.SYMTYPE
                            member.linkname = '/outside-export'
                            member.size = 0
                            dst.addfile(member)
                        else:
                            dst.addfile(member, io.BytesIO(raw))
                    if mutation == 'duplicate':
                        member, raw = members[0]
                        dst.addfile(copy.copy(member), io.BytesIO(raw))
                archive = out.getvalue()
                manifest = json.loads(original_manifest)
                manifest['archive_sha256'] = digest(archive)
                manifest_bytes = json.dumps(manifest).encode()
                archive_path.write_bytes(archive)
                manifest_path.write_bytes(manifest_bytes)
                loader = raw_module('qq16_history_member_loader', self.package / 'runtime.py')
                loader.MANIFEST_SHA = digest(manifest_bytes)
                with self.assertRaisesRegex(ValueError, message):
                    loader.authenticated_inputs()
        archive_path.write_bytes(original_archive)
        manifest_path.write_bytes(original_manifest)

    def test_generation_refuses_to_overwrite_receipts(self):
        before = snapshot(self.root)
        self.replay('--write', ok=False, needle='refuse receipt overwrite')
        self.assertEqual(before, snapshot(self.root))

    def test_whole_typed_receipts_and_duplicate_keys(self):
        # Test the production transport comparator against a saved expected
        # result. Separate full replays independently regenerate that result.
        saved_path = list(sys.path)
        saved_runtime = sys.modules.pop('runtime', None)
        self.addCleanup(lambda: setattr(sys, 'path', saved_path))
        def restore_runtime():
            sys.modules.pop('runtime', None)
            if saved_runtime is not None:
                sys.modules['runtime'] = saved_runtime
        self.addCleanup(restore_runtime)
        sys.path.insert(0, str(self.package))
        verifier = raw_module('qq16_history_export_verifier', self.package / 'verify.py')
        typed_mutations = 0
        for name in verifier.NAMES:
            path = self.package / name
            raw = path.read_bytes()
            expected = json.loads(raw)
            verifier.check_receipt(name, expected, self.package)
            mutations = [dict(expected, unexpected_receipt_field=True),
                         {k: v for index, (k, v) in enumerate(expected.items()) if index != 0}]
            changed, found = alias_mutation(expected)
            if found:
                self.assertEqual(changed, expected)
                typed_mutations += 1
                mutations.append(changed)
            for changed in mutations:
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'whole typed receipt mismatch:'):
                    verifier.check_receipt(name, expected, self.package)
            path.write_bytes(raw)
            key = next(iter(expected))
            duplicate = b'{' + json.dumps(key).encode() + b':false,' + raw.lstrip()[1:]
            path.write_bytes(duplicate)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                verifier.check_receipt(name, expected, self.package)
            path.write_bytes(raw)
        self.assertGreater(typed_mutations, 0, 'no concrete bool/integer alias exercised')


if __name__ == '__main__':
    unittest.main()

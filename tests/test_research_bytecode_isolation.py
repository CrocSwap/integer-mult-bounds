"""Source-authenticated imports must not execute preexisting bytecode caches.

Run --p104-probe for the slower retained-source reproduction. Ordinary test
discovery uses small independent fixtures, including real timestamp/hash caches.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("research_package_cache_test", ROOT / "scripts/research_package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def cache_fixture(source, mode, optimize=0, prefix=None):
    """Compile changed scratch bytes, then restore exact source bytes and time."""
    raw, stat = source.read_bytes(), source.stat()
    fault = b"raise RuntimeError('UNVERIFIED_BYTECODE_SENTINEL')\n"
    if len(raw) < len(fault):
        raise ValueError("fixture source must be long enough for a same-size edit")
    saved_prefix = sys.pycache_prefix
    try:
        sys.pycache_prefix = None if prefix is None else str(prefix)
        target = Path(importlib.util.cache_from_source(str(source), optimization=str(optimize) if optimize else ""))
    finally:
        sys.pycache_prefix = saved_prefix
    source.write_bytes(fault + b" " * (len(raw) - len(fault)))
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    try:
        py_compile.compile(str(source), cfile=str(target), doraise=True,
                           optimize=optimize, invalidation_mode=mode)
    finally:
        source.write_bytes(raw)
        os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    return target


class BytecodeIsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="research-cache-test-")
        self.root = Path(self.temp.name)
        self.source = self.root / "pinned.py"
        self.source.write_text("VALUE = 'SOURCE'\n#" + "." * 500 + "\n", encoding="utf8")
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.output = self.root / "receipt.json"
        self.script = self.root / "fixture.py"
        self.script.write_text(
            "import hashlib, importlib.util, json, sys\nfrom pathlib import Path\n"
            f"source = Path({str(self.source)!r})\n"
            f"if hashlib.sha256(source.read_bytes()).hexdigest() != {self.digest!r}: raise ValueError('source drift')\n"
            "spec = importlib.util.spec_from_file_location('pinned_fixture', source)\n"
            "module = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(module)\n"
            "receipt = {'value': module.VALUE, 'prefix': sys.pycache_prefix, 'optimize': sys.flags.optimize, "
            "'debug': __debug__, 'argv': sys.argv[1:]}\n"
            f"Path({str(self.output)!r}).write_text(json.dumps(receipt))\n", encoding="utf8")

    def tearDown(self):
        self.temp.cleanup()

    def direct(self, argv):
        return subprocess.run(argv, cwd=self.root, capture_output=True, text=True, timeout=15)

    def checked_receipt(self, optimize=0, arguments=()):
        receipt = json.loads(self.output.read_text())
        self.assertEqual(receipt['value'], 'SOURCE')
        self.assertEqual(receipt['optimize'], optimize)
        self.assertEqual(receipt['debug'], optimize == 0)
        self.assertEqual(receipt['argv'], list(arguments))
        self.assertTrue(receipt['prefix'])
        self.assertFalse(Path(receipt['prefix']).exists(), 'private namespace was not cleaned')
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.digest)
        return receipt

    def test_timestamp_and_unchecked_hash_caches_cannot_replace_source(self):
        for mode in (py_compile.PycInvalidationMode.TIMESTAMP, py_compile.PycInvalidationMode.UNCHECKED_HASH):
            for optimize, flags in ((0, ['-B']), (1, ['-I', '-O', '-B']), (2, ['-I', '-OO', '-B'])):
                with self.subTest(mode=mode.name, optimize=optimize):
                    cache_fixture(self.source, mode, optimize)
                    argv = [sys.executable, *flags, str(self.script)]
                    bad = self.direct(argv)
                    self.assertNotEqual(bad.returncode, 0)
                    self.assertIn('UNVERIFIED_BYTECODE_SENTINEL', bad.stderr)
                    package.run_python_replay(argv, self.root, 15)
                    self.checked_receipt(optimize)

    def test_checked_hash_mismatch_is_already_rejected_by_python(self):
        cache_fixture(self.source, py_compile.PycInvalidationMode.CHECKED_HASH)
        result = self.direct([sys.executable, '-B', str(self.script)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text())['value'], 'SOURCE')

    def test_existing_prefix_options_are_overridden_before_entry_point(self):
        hostile = self.root / 'configured-cache'
        cache_fixture(self.source, py_compile.PycInvalidationMode.TIMESTAMP, 1, hostile)
        argument = 'pycache_prefix=' + str(hostile)
        receipts = []
        for flags in (['-I', '-O', '-B', '-X', argument], ['-IOB', '-X' + argument],
                      ['-OB', '-IX', argument],
                      ['-O', '-B', '-W', 'ignore', '--check-hash-based-pycs', 'always', '-X', argument]):
            with self.subTest(flags=flags):
                argv = [sys.executable, *flags, str(self.script), '-X', 'script argument unchanged']
                bad = self.direct(argv)
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn('UNVERIFIED_BYTECODE_SENTINEL', bad.stderr)
                package.run_python_replay(argv, self.root, 15)
                receipts.append(self.checked_receipt(1, ['-X', 'script argument unchanged'])['prefix'])
        self.assertEqual(len(set(receipts)), 4)
        self.assertTrue(hostile.exists(), 'preexisting cache was modified or removed')

    def test_environment_prefix_is_overridden_without_changing_parent(self):
        hostile = self.root / 'environment-cache'
        cache_fixture(self.source, py_compile.PycInvalidationMode.TIMESTAMP, 0, hostile)
        argv = [sys.executable, '-B', str(self.script)]
        with patch.dict(os.environ, {'PYTHONPYCACHEPREFIX': str(hostile)}):
            self.assertIn('UNVERIFIED_BYTECODE_SENTINEL', self.direct(argv).stderr)
            package.run_python_replay(argv, self.root, 15)
            self.checked_receipt()
            self.assertEqual(os.environ['PYTHONPYCACHEPREFIX'], str(hostile))

    def test_command_module_and_attached_command_entry_points(self):
        source = self.script.read_text()
        forms = [([sys.executable, '-B', '-c', source, 'payload'], ['payload']),
                 ([sys.executable, '-B', '-c' + source, 'payload'], ['payload']),
                 ([sys.executable, '-B', '-m', 'fixture', 'payload'], ['payload']),
                 ([sys.executable, '-B', '-mfixture', 'payload'], ['payload']),
                 ([sys.executable, '-B', '--', str(self.script), 'payload'], ['payload'])]
        for argv, args in forms:
            with self.subTest(entry=argv[2][:12]):
                package.run_python_replay(argv, self.root, 15)
                self.checked_receipt(arguments=args)

    def test_source_drift_still_fails_with_a_private_cache(self):
        self.source.write_text("VALUE = 'CHANGED'\n", encoding='utf8')
        with self.assertRaisesRegex(ValueError, 'exited 1'):
            package.run_python_replay([sys.executable, '-I', '-B', str(self.script)], self.root, 15)
        self.assertFalse(self.output.exists())

    def test_private_namespace_cleanup_on_failure_and_timeout(self):
        marker = self.root / 'namespace.txt'
        prefix = f"import sys; from pathlib import Path; Path({str(marker)!r}).write_text(sys.pycache_prefix); "
        for tail, timeout, error in [('raise SystemExit(7)', 15, 'exited 7'),
                                     ('import time; time.sleep(30)', 2, 'timed out')]:
            with self.subTest(error=error):
                with self.assertRaisesRegex(ValueError, error):
                    package.run_python_replay([sys.executable, '-I', '-B', '-c', prefix + tail], self.root, timeout)
                self.assertFalse(Path(marker.read_text()).exists())
                marker.unlink()

    def test_non_python_commands_and_missing_option_values_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'registered Python'):
            package.isolated_python_argv(['some-other-command', '-c', 'arg'], self.root)
        for option in ('-X', '-W', '--check-hash-based-pycs'):
            with self.subTest(option=option), self.assertRaisesRegex(ValueError, 'missing Python'):
                package.isolated_python_argv([sys.executable, option], self.root)


def p104_probe():
    """Reproduce on the actual retained native verifier without changing it."""
    source = ROOT / 'research/p104-native-channel'
    with tempfile.TemporaryDirectory(prefix='p104-source-cache-') as td:
        copied = Path(td) / 'p104-native-channel'
        shutil.copytree(source, copied, ignore=shutil.ignore_patterns('__pycache__'))
        vendor = copied / 'vendor/native_verify.py'
        hashes = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in copied.rglob('*') if p.is_file()}
        if hashes['vendor/native_verify.py'] != '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38':
            raise ValueError('P104 pinned interpreter changed')
        argv = [sys.executable, '-I', '-O', '-B', str(copied / 'verify.py')]
        clean = subprocess.run(argv, cwd=td, capture_output=True, text=True, timeout=300)
        if clean.returncode:
            raise ValueError(clean.stderr)
        cache_fixture(vendor, py_compile.PycInvalidationMode.TIMESTAMP, 1)
        contaminated = subprocess.run(argv, cwd=td, capture_output=True, text=True, timeout=300)
        if contaminated.returncode == 0 or 'UNVERIFIED_BYTECODE_SENTINEL' not in contaminated.stderr:
            raise ValueError('original bytecode-loading control did not trigger')
        with tempfile.TemporaryDirectory(prefix='p104-private-cache-') as private:
            fixed = subprocess.run(package.isolated_python_argv(argv, private), cwd=td,
                                   capture_output=True, text=True, timeout=300)
            if fixed.returncode or fixed.stdout != clean.stdout:
                raise ValueError('isolated full P104 receipt changed: ' + fixed.stderr)
            if list(Path(private).rglob('*.pyc')):
                raise ValueError('-B isolated replay unexpectedly wrote bytecode')
        for name, digest in hashes.items():
            if hashlib.sha256((copied / name).read_bytes()).hexdigest() != digest:
                raise ValueError('retained source bytes changed: ' + name)
        print(json.dumps({'status': 'PASS_P104_BYTECODE_SOURCE_ISOLATION', 'runtime': sys.version,
                          'baseline_exit': clean.returncode, 'stale_cache_exit': contaminated.returncode,
                          'isolated_exit': fixed.returncode, 'full_receipt_equal': True,
                          'retained_hashes': hashes,
                          'receipt_sha256': hashlib.sha256(clean.stdout.encode()).hexdigest()}, indent=2))


if __name__ == '__main__':
    if sys.argv[1:] == ['--p104-probe']:
        p104_probe()
    else:
        unittest.main()

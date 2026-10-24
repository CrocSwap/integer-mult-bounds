"""Real historical-child cache differentials and complete Git-free replay.

All numeric changes occur only in disposable copies; source bytes are restored
before execution. No mathematical check or source pin is weakened.
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

HERE = Path(__file__).resolve().parent


def load(package):
    spec = importlib.util.spec_from_file_location('containment_replay', package / 'replay.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export(root):
    target = root / 'research/rational-containment-child-isolation'
    shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__'))
    return target


def stale_numeric(path, mode):
    raw, before = path.read_bytes(), path.stat()
    old = raw.replace(b'return 9*sum', b'return 8*sum')
    if old == raw or len(old) != len(raw):
        raise ValueError('exact numeric cache anchor')
    path.write_bytes(old)
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    cache = path.parent / '__pycache__' / (path.stem + '.' + sys.implementation.cache_tag + '.pyc')
    py_compile.compile(str(path), cfile=str(cache), doraise=True,
                       invalidation_mode=mode, optimize=0)
    path.write_bytes(raw)
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    return cache, raw, before.st_mtime_ns


class Controls(unittest.TestCase):
    def test_actual_child_cache_differential(self):
        for mode in py_compile.PycInvalidationMode:
            with self.subTest(mode=mode.name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp).resolve()
                package = export(root)
                r = load(package)
                source = r.RETAINED / 'scripts/rational_span_frames.py'
                cache, raw, mtime = stale_numeric(source, mode)
                cached = cache.read_bytes()
                r.authenticate()  # Original sources are all exact, including this helper.
                trace = root / 'trace'
                trace.mkdir()
                env = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / 'ignored-env-prefix'))
                for kind in ('original', 'isolated', 'removed'):
                    output = root / (kind + '.json')
                    command = [sys.executable, '-I', '-B', str(r.PACKAGE / 'adapter.py'),
                               '--engine', 'reference', '--output', str(output)]
                    if kind == 'removed':
                        self.assertEqual(cache.read_bytes(), cached)
                        cache.unlink()
                    with tempfile.TemporaryDirectory(prefix='containment-test-cache-') as fresh:
                        if kind == 'isolated':
                            command = r.child_command(command, Path(fresh), trace)
                        result = subprocess.run(command, cwd=r.RETAINED, env=env,
                                                capture_output=True, text=True, timeout=30)
                    self.assertFalse(Path(fresh).exists())
                    stale = kind == 'original' and mode != py_compile.PycInvalidationMode.CHECKED_HASH
                    if stale:
                        self.assertEqual(result.returncode, 1)
                        self.assertIn('A forbidden source-to-target path exists', result.stderr)
                        self.assertNotIn('Changed pinned input', result.stderr)
                        self.assertFalse(output.exists())
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        receipt = json.loads(output.read_text())
                        self.assertEqual(receipt['result_sha256'], r.EXPECTED_PAYLOAD)
                    self.assertEqual(source.read_bytes(), raw)
                    self.assertEqual(source.stat().st_mtime_ns, mtime)
                    if kind != 'removed':
                        self.assertEqual(cache.read_bytes(), cached)

    def test_exact_grammar_and_original_mutants(self):
        r = load(HERE)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp).resolve()
            for flags in (['-I', '-B'], ['-I', '-B', '-O']):
                argv = [sys.executable, *flags, str(r.PACKAGE / 'adapter.py'), '--engine', 'reference']
                result = r.child_command(argv, folder / 'cache', folder)
                self.assertEqual(result[1:1 + len(flags)], flags)
                self.assertEqual(result[-3:], ['--', '--engine', 'reference'])
            for target, flags in ((r.PACKAGE / 'kernel.py', ['-I', '-B']),
                                  (r.PACKAGE / 'adapter.py', ['-B']),
                                  (r.PACKAGE / 'adapter.py', ['-I', '-B', '-X', 'foo'])):
                with self.assertRaises(ValueError):
                    r.child_target([sys.executable, *flags, str(target)])
            script = folder / 'test_kernel.py'
            script.write_bytes((r.PACKAGE / script.name).read_bytes())
            source = (r.PACKAGE / 'kernel.py').read_text()
            for before, after in r.MUTATIONS:
                (folder / 'kernel.py').write_text(source.replace(before, after))
                self.assertEqual(r.child_target([sys.executable, '-I', '-B', str(script)])[1], script)
            (folder / 'kernel.py').write_text(source + '\n# not an original mutant\n')
            with self.assertRaisesRegex(ValueError, 'original arithmetic mutant kernel'):
                r.child_target([sys.executable, '-I', '-B', str(script)])

    def test_all_retained_source_mutations_reject(self):
        with tempfile.TemporaryDirectory() as temp:
            package = export(Path(temp))
            r = load(package)
            rows = r.authenticate()
            self.assertEqual(len(rows), 17)
            for row in rows:
                path = r.RETAINED / row['path']
                raw = path.read_bytes()
                try:
                    path.write_bytes(raw + b'\n# altered retained source\n')
                    with self.assertRaisesRegex(ValueError, 'retained source SHA256'):
                        r.authenticate()
                finally:
                    path.write_bytes(raw)
            self.assertEqual(r.authenticate(), rows)

    def test_complete_optimized_git_free_export_with_stale_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            package = export(root)
            r = load(package)
            cache, raw, mtime = stale_numeric(r.RETAINED / 'scripts/rational_span_frames.py',
                                             py_compile.PycInvalidationMode.UNCHECKED_HASH)
            cached = cache.read_bytes()
            original = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in package.rglob('*') if p.is_file()}
            env = dict(os.environ, PATH='', PYTHONOPTIMIZE='2')
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'replay.py')],
                                    cwd=root, env=env, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt, json.loads((HERE / 'RESULT.json').read_text()))
            self.assertEqual(cache.read_bytes(), cached)
            self.assertEqual({str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in package.rglob('*') if p.is_file()}, original)
            self.assertEqual(receipt['child_calls'], 13)
            self.assertEqual(receipt['expected_child_rejections'], 6)
            self.assertTrue(receipt['all_caches_removed'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

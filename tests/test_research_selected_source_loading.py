"""Current selected preflights must execute checker source, not old bytecode.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Uses Mihir Srivastava's complete productive-helper selected fixture.
"""
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

from test_research_selected_baseline import selected_fixture

ROOT = Path(__file__).resolve().parents[1]
CI_DRIVER = '''import json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / 'scripts'))
import check_selected_ci_inputs
failures, files = check_selected_ci_inputs.check_records(['certificates/selected-result.json'], root)
print(json.dumps({'record_failures': failures, 'files': sorted(files)}))
sys.exit(bool(failures))
'''


def fixture(root):
    root.mkdir()
    selected_fixture(root)
    shutil.copyfile(ROOT / 'scripts/check_selected_ci_inputs.py',
                    root / 'scripts/check_selected_ci_inputs.py')
    return root / 'scripts/verify_selected_result.py'


def stale_checker(helper, mode, optimize):
    """Compile one disabled inventory guard, then restore exact source and time."""
    original, stat = helper.read_bytes(), helper.stat()
    condition = b"actual == manifest['files']"
    if original.count(condition) != 1:
        raise ValueError('one unchanged checker inventory equality required')
    changed = original.replace(condition, b'True' + b' ' * (len(condition) - 4))
    previous = sys.pycache_prefix
    try:
        sys.pycache_prefix = None
        cache = Path(importlib.util.cache_from_source(str(helper),
                     optimization='1' if optimize else ''))
    finally:
        sys.pycache_prefix = previous
    try:
        helper.write_bytes(changed)
        os.utime(helper, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        py_compile.compile(str(helper), cfile=str(cache), doraise=True,
                           optimize=optimize, invalidation_mode=mode)
    finally:
        helper.write_bytes(original)
        os.utime(helper, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    return cache


def execute(root, entry, optimize):
    env = os.environ.copy()
    # These controls deliberately expose the default adjacent cache even when
    # the containing unittest itself uses a private inherited namespace.
    for name in ('PYTHONPYCACHEPREFIX', 'PYTHONOPTIMIZE', 'PYTHONPATH'):
        env.pop(name, None)
    flags = ['-O'] if optimize else []
    command = [sys.executable, *flags, '-B']
    command += ([str(root / 'scripts/research_selected_baseline.py')]
                if entry == 'orientation' else ['-c', CI_DRIVER, str(root)])
    return subprocess.run(command, cwd=root, env=env, capture_output=True,
                          text=True, encoding='utf-8', timeout=20)


class SelectedSourceLoadingTests(unittest.TestCase):
    def cases(self, entry, corrupt):
        for mode in (py_compile.PycInvalidationMode.TIMESTAMP,
                     py_compile.PycInvalidationMode.UNCHECKED_HASH):
            for optimize in (0, 1):
                with self.subTest(entry=entry, mode=mode.name, optimize=optimize), \
                        tempfile.TemporaryDirectory(prefix='selected-source-loading-') as tmp:
                    root = Path(tmp) / 'repository'
                    helper = fixture(root)
                    cache = stale_checker(helper, mode, optimize)
                    original = (helper.read_bytes(), helper.stat().st_mtime_ns, cache.read_bytes())
                    if corrupt:
                        (root / 'research/fixture/native-input.txt').write_bytes(b'changed frozen input\n')
                    result = execute(root, entry, optimize)
                    self.assertEqual((helper.read_bytes(), helper.stat().st_mtime_ns, cache.read_bytes()),
                                     original, 'checker source/time and pre-existing cache must remain untouched')
                    if corrupt:
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        if entry == 'orientation':
                            self.assertEqual(result.stdout, '')
                            error = json.loads(result.stderr)
                            self.assertEqual(error['status'], 'FAIL_RESEARCH_BASELINE')
                            self.assertEqual(error['error'], 'Selected package inventory or bytes changed')
                        else:
                            self.assertEqual(json.loads(result.stdout)['record_failures'],
                                {'certificates/selected-result.json': 'Selected package inventory or bytes changed'})
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        if entry == 'orientation':
                            self.assertEqual(json.loads(result.stdout)['status'],
                                             'PASS_RESEARCH_BASELINE_BINDINGS_ONLY')
                        else:
                            self.assertEqual(json.loads(result.stdout)['record_failures'], {})

    def test_orientation_rejects_drift_despite_real_stale_checker_caches(self):
        self.cases('orientation', corrupt=True)

    def test_named_record_loader_rejects_drift_despite_real_stale_checker_caches(self):
        self.cases('named-records', corrupt=True)

    def test_valid_orientation_still_passes_and_preserves_preexisting_caches(self):
        self.cases('orientation', corrupt=False)

    def test_valid_named_records_still_pass_and_preserve_preexisting_caches(self):
        self.cases('named-records', corrupt=False)

    def test_checker_file_root_and_module_name_are_preserved(self):
        for entry, name in [('orientation', 'verify_selected_result'),
                            ('named-records', 'ci_inputs_selected_result')]:
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / 'repository'
                helper = fixture(root)
                with helper.open('a', encoding='utf-8') as out:
                    out.write("\nPath(ROOT / 'checker-namespace.json').write_text(json.dumps({"
                              "'file': __file__, 'root': str(ROOT), 'name': __name__}))\n")
                result = execute(root, entry, 0)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads((root / 'checker-namespace.json').read_text()),
                                 {'file': str(helper.resolve() if entry == 'orientation' else helper.absolute()),
                                  'root': str(root.resolve()), 'name': name})

    def test_invalid_current_source_cannot_fall_back_to_unchecked_hash_cache(self):
        for entry in ('orientation', 'named-records'):
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / 'repository'
                helper = fixture(root)
                cache = stale_checker(helper, py_compile.PycInvalidationMode.UNCHECKED_HASH, 0)
                cached = cache.read_bytes()
                helper.write_text('def broken(:\n', encoding='utf-8')
                result = execute(root, entry, 0)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('SyntaxError', result.stderr)
                self.assertEqual(cache.read_bytes(), cached)


if __name__ == '__main__':
    unittest.main()

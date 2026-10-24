"""Run the public isolated-test CLI against disposable stale numeric caches."""
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_isolated_tests.py"


class IsolatedBytecodeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="test-isolated-bytecode-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.scripts = self.root / "scripts"
        self.tests = self.root / "tests"
        self.owned = self.root / "owned"
        for directory in (self.scripts, self.tests, self.owned):
            directory.mkdir()
        shutil.copyfile(RUNNER, self.scripts / RUNNER.name)
        shutil.copyfile(ROOT / "scripts/research_package.py", self.scripts / "research_package.py")

    def environment(self, additions=None):
        env = os.environ.copy()
        for key in ("PYTHONPYCACHEPREFIX", "PYTHONOPTIMIZE", "PYTHONPATH", "PYTHONHOME"):
            env.pop(key, None)
        env.update(TMPDIR=str(self.owned), TMP=str(self.owned), TEMP=str(self.owned),
                   PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        env.update(additions or {})
        return env

    def run_cli(self, additions=None):
        return subprocess.run(
            [sys.executable, "-B", str(self.scripts / RUNNER.name), "--workers", "2"],
            cwd=self.root, env=self.environment(additions), capture_output=True,
            text=True, encoding="utf-8", timeout=30)

    def numeric_test(self, name="test_value.py", expected=2):
        path = self.tests / name
        path.write_text(
            "import unittest\nfrom numeric_value import VALUE\n"
            "class NumericTest(unittest.TestCase):\n"
            f" def test_current_source(self): self.assertEqual(VALUE, {expected})\n",
            encoding="utf-8")
        return path

    def stale_cache(self, source, cached, current, mode, prefix=None):
        source.write_text(f"VALUE = {cached}\n", encoding="utf-8")
        stamp = source.stat().st_mtime_ns
        if prefix is None:
            cache = source.parent / "__pycache__" / (
                source.stem + "." + sys.implementation.cache_tag + ".pyc")
        else:
            result = subprocess.run(
                [sys.executable, "-B", "-X", "pycache_prefix=" + str(prefix), "-c",
                 "import importlib.util,sys; print(importlib.util.cache_from_source(sys.argv[1]))",
                 str(source)], env=self.environment(), capture_output=True,
                text=True, encoding="utf-8", check=True, timeout=30)
            cache = Path(result.stdout.strip())
        cache.parent.mkdir(parents=True, exist_ok=True)
        py_compile.compile(str(source), cfile=str(cache), doraise=True,
                           optimize=0, invalidation_mode=mode)
        source.write_text(f"VALUE = {current}\n", encoding="utf-8")
        os.utime(source, ns=(stamp, stamp))
        return source, source.read_bytes(), source.stat().st_mtime_ns, cache, cache.read_bytes()

    def unchanged(self, snapshot):
        source, content, stamp, cache, bytecode = snapshot
        self.assertEqual(source.read_bytes(), content)
        self.assertEqual(source.stat().st_mtime_ns, stamp)
        self.assertEqual(cache.read_bytes(), bytecode)

    def check_stale_rejection(self, mode, prefix=None):
        self.numeric_test()
        snapshot = self.stale_cache(self.tests / "numeric_value.py", 2, 1, mode, prefix)
        additions = {"PYTHONPYCACHEPREFIX": str(prefix)} if prefix is not None else None
        result = self.run_cli(additions)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("AssertionError: 1 != 2", result.stderr)
        self.assertIn("Failed modules: test_value.py", result.stderr)
        self.assertNotIn("PASS all", result.stdout)
        self.unchanged(snapshot)

    def test_timestamp_cache_cannot_hide_current_failure(self):
        self.check_stale_rejection(py_compile.PycInvalidationMode.TIMESTAMP)

    def test_unchecked_hash_cache_cannot_hide_current_failure(self):
        self.check_stale_rejection(py_compile.PycInvalidationMode.UNCHECKED_HASH)

    def test_checked_hash_cache_already_invalidates(self):
        self.numeric_test()
        snapshot = self.stale_cache(self.tests / "numeric_value.py", 1, 2,
                                    py_compile.PycInvalidationMode.CHECKED_HASH)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS all 1 test modules", result.stdout)
        self.unchanged(snapshot)

    def test_inherited_external_cache_cannot_hide_current_failure(self):
        self.check_stale_rejection(py_compile.PycInvalidationMode.TIMESTAMP,
                                   self.root / "external-cache")

    def check_private_namespaces(self, failing):
        observations = self.root / "observations"
        observations.mkdir()
        external = self.root / "external-cache"
        body = '''import json
import os
from pathlib import Path
import sys
import time
import unittest
class NamespaceTest(unittest.TestCase):
 def test_namespace(self):
  self.assertIsNotNone(sys.pycache_prefix)
  prefix = Path(sys.pycache_prefix)
  self.assertEqual(sys._xoptions.get('pycache_prefix'), str(prefix))
  inherited = Path(os.environ['PYTHONPYCACHEPREFIX'])
  self.assertNotEqual(str(inherited), os.environ['EXTERNAL_PREFIX'])
  self.assertEqual(inherited.parent, prefix.parent)
  self.assertEqual(os.environ['PYTHONDONTWRITEBYTECODE'], '1')
  inherited.mkdir(parents=True, exist_ok=True)
  (inherited / 'owned-marker').write_text('owned', encoding='utf-8')
  prefix.mkdir(parents=True, exist_ok=True)
  (prefix / 'owned-marker').write_text('owned', encoding='utf-8')
  observed = Path(os.environ['OBSERVATIONS'])
  (observed / (Path(__file__).stem + '.json')).write_text(json.dumps([str(prefix), str(inherited)]), encoding='utf-8')
  for attempt in range(200):
   if len(list(observed.glob('*.json'))) == 2:
    break
   time.sleep(0.01)
  self.assertEqual(len(list(observed.glob('*.json'))), 2)
  self.assertEqual(FAILURE, 0)
'''
        for index in range(2):
            (self.tests / f"test_namespace_{index}.py").write_text(
                body.replace("FAILURE", str(index if failing else 0)), encoding="utf-8")
        result = self.run_cli({"OBSERVATIONS": str(observations),
                               "EXTERNAL_PREFIX": str(external),
                               "PYTHONPYCACHEPREFIX": str(external)})
        self.assertEqual(result.returncode, int(failing), result.stdout + result.stderr)
        paths = sorted(observations.glob("*.json"))
        self.assertEqual(len(paths), 2, result.stdout + result.stderr)
        pairs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        prefixes = [Path(prefix) for pair in pairs for prefix in pair]
        self.assertEqual(len(set(prefixes)), 4)
        for prefix in prefixes:
            self.assertTrue(prefix.is_relative_to(self.owned))
            self.assertFalse(prefix.exists(), "owned namespace survived CLI completion")
        if failing:
            self.assertIn("AssertionError: 1 != 0", result.stderr)
            self.assertIn("Failed modules: test_namespace_1.py", result.stderr)
        else:
            self.assertIn("PASS all 2 test modules", result.stdout)

    def test_concurrent_namespaces_are_private_and_removed_on_success(self):
        self.check_private_namespaces(failing=False)

    def test_concurrent_namespaces_are_removed_after_suite_failure(self):
        self.check_private_namespaces(failing=True)

    def descendant_test(self, depth=1, isolated=False):
        (self.tests / "probe.py").write_text(
            "from pathlib import Path\nimport json, os, sys\nimport numeric_value\n"
            "if os.environ.get('CACHE_OBSERVATION'):\n"
            " Path(os.environ['CACHE_OBSERVATION']).write_text(json.dumps({"
            "'cache_exists': Path(numeric_value.__cached__).exists(), "
            "'dont_write': sys.dont_write_bytecode, 'prefix': sys.pycache_prefix}), encoding='utf-8')\n"
            "print(numeric_value.VALUE)\n", encoding="utf-8")
        target = "probe.py"
        if depth == 2:
            (self.tests / "relay.py").write_text(
                "from pathlib import Path\nimport subprocess, sys\n"
                "raise SystemExit(subprocess.run([sys.executable, "
                "str(Path(__file__).with_name('probe.py'))]).returncode)\n", encoding="utf-8")
            target = "relay.py"
        flags = "'-I', '-B', " if isolated else ""
        (self.tests / "test_descendant.py").write_text(
            "from pathlib import Path\nimport subprocess, sys, unittest\n"
            "class DescendantTest(unittest.TestCase):\n"
            " def test_numeric_child(self):\n"
            f"  child = subprocess.run([sys.executable, {flags}"
            f"str(Path(__file__).with_name('{target}'))], "
            "capture_output=True, text=True, timeout=10)\n"
            "  self.assertEqual(child.returncode, 0, child.stderr)\n"
            "  self.assertEqual(int(child.stdout), 2)\n", encoding="utf-8")

    def test_descendants_and_grandchildren_reject_stale_numeric_cache(self):
        for depth in (1, 2):
            for mode in (py_compile.PycInvalidationMode.TIMESTAMP,
                         py_compile.PycInvalidationMode.UNCHECKED_HASH):
                with self.subTest(depth=depth, mode=mode):
                    self.descendant_test(depth)
                    snapshot = self.stale_cache(self.tests / "numeric_value.py", 2, 1, mode)
                    result = self.run_cli()
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn("AssertionError: 1 != 2", result.stderr)
                    self.assertNotIn("PASS all", result.stdout)
                    self.unchanged(snapshot)

    def test_descendant_ignores_inherited_stale_prefix(self):
        self.descendant_test()
        prefix = self.root / "external-cache"
        snapshot = self.stale_cache(self.tests / "numeric_value.py", 2, 1,
                                    py_compile.PycInvalidationMode.UNCHECKED_HASH, prefix)
        result = self.run_cli({"PYTHONPYCACHEPREFIX": str(prefix)})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("AssertionError: 1 != 2", result.stderr)
        self.unchanged(snapshot)

    def test_descendant_current_source_passes_without_writing_cache(self):
        self.descendant_test(depth=2)
        helper = self.tests / "numeric_value.py"
        helper.write_text("VALUE = 2\n", encoding="utf-8")
        observation = self.root / "child-cache.json"
        result = self.run_cli({"PYTHONDONTWRITEBYTECODE": "",
                               "CACHE_OBSERVATION": str(observation)})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS all 1 test modules", result.stdout)
        child = json.loads(observation.read_text(encoding="utf-8"))
        self.assertFalse(child['cache_exists'])
        self.assertTrue(child['dont_write'])
        self.assertTrue(Path(child['prefix']).is_relative_to(self.owned))
        self.assertFalse(Path(child['prefix']).exists())
        self.assertEqual(list(self.root.rglob("*.pyc")), [])

    def test_explicit_isolated_descendant_retains_its_own_policy(self):
        # -I ignores PYTHONPYCACHEPREFIX. Make that documented limit observable.
        self.descendant_test(isolated=True)
        snapshot = self.stale_cache(self.tests / "numeric_value.py", 2, 1,
                                    py_compile.PycInvalidationMode.TIMESTAMP)
        # -I also omits the script directory, so explicitly name the import path.
        probe = self.tests / "probe.py"
        probe.write_text("from pathlib import Path\nimport sys\n"
                         "sys.path.insert(0, str(Path(__file__).parent))\n"
                         "from numeric_value import VALUE\nprint(VALUE)\n", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS all 1 test modules", result.stdout)
        self.unchanged(snapshot)
        snapshot[3].unlink()
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("AssertionError: 1 != 2", result.stderr)

    def test_historical_wrapper_and_unittest_child_read_current_source(self):
        self.numeric_test("test_skip_clones.py", expected=1)
        child = self.stale_cache(self.tests / "numeric_value.py", 2, 1,
                                 py_compile.PycInvalidationMode.TIMESTAMP)
        wrapper = self.stale_cache(self.scripts / "wrapper_value.py", 2, 1,
                                   py_compile.PycInvalidationMode.UNCHECKED_HASH)
        manifest = self.root / "research/skip-clones/SOURCE.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("{}", encoding="utf-8")
        (self.scripts / "replay_historical_check.py").write_text('''import argparse
from pathlib import Path
import subprocess
import sys
from wrapper_value import VALUE
from run_isolated_tests import module_command
parser = argparse.ArgumentParser()
parser.add_argument('route')
parser.add_argument('--completion-receipt', type=Path, required=True)
args = parser.parse_args()
assert VALUE == 1, f'wrapper value {VALUE} differs from current source 1'
print('WRAPPER_VALUE', VALUE, flush=True)
root = Path(__file__).resolve().parents[1]
subprocess.run(module_command(sys.executable, root / 'tests', 'test_skip_clones.py',
                              args.completion_receipt), cwd=root, check=True)
''', encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WRAPPER_VALUE 1", result.stdout)
        self.assertIn("test_current_source", result.stderr)
        self.assertIn("PASS all 1 test modules", result.stdout)
        self.unchanged(child)
        self.unchanged(wrapper)


if __name__ == "__main__":
    unittest.main()

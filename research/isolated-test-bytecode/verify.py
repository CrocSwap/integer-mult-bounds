#!/usr/bin/env python3
"""Reproduce stale-cache false greens through both real isolated-runner CLIs."""
from hashlib import sha256
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
STAMP = 1_700_000_000_000_000_000
TEST = """import unittest
from observed_value import VALUE
class T(unittest.TestCase):
    def test_current_source(self):
        self.assertEqual(VALUE, 2)
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def original_runner():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    row, = [r for r in sources["files"] if r["path"] == "scripts/run_isolated_tests.py"]
    result = subprocess.run(
        ["git", "show", sources["base_commit"] + ":" + row["path"]],
        cwd=ROOT, capture_output=True, check=True, timeout=30)
    require(sha256(result.stdout).hexdigest() == row["sha256"], "baseline source drift")
    return result.stdout


def invoke(runner, root, expected):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for name in ("PYTHONPYCACHEPREFIX", "PYTHONOPTIMIZE"):
        env.pop(name, None)
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(runner), "--workers", "1"],
        cwd=root, env=env, capture_output=True, timeout=30)
    require(result.returncode == expected, "unexpected CLI verdict: " + repr(result.stderr))
    require(b"Ran 1 test" in result.stderr, "discovery did not execute the test")
    if expected:
        require(b"AssertionError: 1 != 2" in result.stderr, "wrong failure mechanism")
        require(b"PASS all" not in result.stdout, "failed test reported success")
    else:
        require(b"PASS all 1 test modules" in result.stdout, "missing completion summary")


def exercise(source, fixed, mode):
    with tempfile.TemporaryDirectory(prefix="isolated-bytecode-proof-") as temporary:
        root = Path(temporary)
        (root / "scripts").mkdir()
        runner = root / "scripts/run_isolated_tests.py"
        runner.write_bytes(source)
        (root / "tests").mkdir()
        helper = root / "tests/observed_value.py"
        (root / "tests/test_value.py").write_text(TEST, encoding="utf-8")
        helper.write_bytes(b"VALUE = 2\n")
        os.utime(helper, ns=(STAMP, STAMP))
        invoke(runner, root, 0)
        cache = helper.parent / "__pycache__" / (
            "observed_value." + sys.implementation.cache_tag + ".pyc")
        py_compile.compile(str(helper), cfile=str(cache), doraise=True,
                           optimize=0, invalidation_mode=mode)
        helper.write_bytes(b"VALUE = 1\n")
        os.utime(helper, ns=(STAMP, STAMP))
        cache_bytes = cache.read_bytes()
        invoke(runner, root, 1 if fixed else 0)
        require(helper.read_bytes() == b"VALUE = 1\n" and
                helper.stat().st_mtime_ns == STAMP and cache.read_bytes() == cache_bytes,
                "runner changed source or preexisting bytecode")
        cache.unlink()
        invoke(runner, root, 1)
    return {"clean_current_2": "pass", "current_1_with_stale_2": "fail" if fixed else "pass",
            "same_current_1_without_cache": "fail", "source_and_cache_unchanged": True}


def main():
    baseline = original_runner()
    candidate = (ROOT / "scripts/run_isolated_tests.py").read_bytes()
    observations = {}
    for mode in (py_compile.PycInvalidationMode.TIMESTAMP,
                 py_compile.PycInvalidationMode.UNCHECKED_HASH):
        observations[mode.name] = {
            "baseline": exercise(baseline, False, mode),
            "candidate": exercise(candidate, True, mode)}
    print(json.dumps({"baseline_sha256": sha256(baseline).hexdigest(),
                      "candidate_sha256": sha256(candidate).hexdigest(),
                      "observations": observations}, indent=2))
    print("PASS_ISOLATED_TEST_BYTECODE_DIFFERENTIAL")


if __name__ == "__main__":
    main()

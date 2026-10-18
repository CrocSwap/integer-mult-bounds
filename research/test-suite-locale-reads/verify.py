#!/usr/bin/env python3
"""Locale-independence check for the repository's document-reading tests.

Scope: tests/test_research_current_status.py reads docs/research/current-status.md.
On a legacy-locale host (cp1252 on Windows, the C locale elsewhere) a bare text
read of that document raises UnicodeDecodeError because it contains byte 0x9d
(in U+201D). Controls:
  - failure control 1: the document must still be undecodable as cp1252,
  - failure control 2: a bare locale read in a legacy-locale child must fail,
  - positive: the repaired module passes in a legacy-locale child and in the
    default environment, and the whole documented suite passes by default.

Not checked: the ~100 remaining locale-dependent text calls in tests/ and the
one-off scripts/ generators; frozen pins, replays and the selected record.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
STATUS = ROOT / "docs/research/current-status.md"
MODULE = "tests.test_research_current_status"


def fail(message):
    raise SystemExit("FAIL_TEST_SUITE_LOCALE_READS " + message)


def legacy_env():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "0"
    env.pop("PYTHONLEGACYWINDOWSUTF8", None)
    if os.name != "nt":
        env["PYTHONCOERCECLOCALE"] = "0"
        env["LC_ALL"] = "C"
        env["LANG"] = "C"
    return env


# Failure control 1: the fixture is load-bearing (byte 0x9d, undefined in cp1252).
try:
    STATUS.read_text(encoding="cp1252")
except UnicodeDecodeError:
    pass
else:
    fail("document decodes as cp1252; the legacy-locale fixture is not load-bearing")

# Failure control 2: a bare locale read fails under the forced legacy codec.
probe = "from pathlib import Path; Path('docs/research/current-status.md').read_text()"
bare = subprocess.run([sys.executable, "-c", probe], env=legacy_env(),
                      capture_output=True, text=True)
if bare.returncode == 0 or "UnicodeDecodeError" not in bare.stderr:
    fail("host cannot exhibit a legacy-codec read failure: " + bare.stderr[-200:])

# Positive: the repaired module passes under the forced legacy codec.
legacy = subprocess.run([sys.executable, "-B", "-m", "unittest", MODULE],
                        env=legacy_env(), capture_output=True, text=True)
if legacy.returncode != 0:
    fail("legacy-locale unittest run failed:\n" + legacy.stderr[-2000:])

# Positive: the module passes in the default environment.
default = subprocess.run([sys.executable, "-B", "-m", "unittest", MODULE],
                         capture_output=True, text=True)
if default.returncode != 0:
    fail("default-environment unittest run failed:\n" + default.stderr[-2000:])

# Positive: the documented suite command passes in the default environment.
suite = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover",
                        "-s", "tests", "-p", "test_research_*.py"],
                       capture_output=True, text=True)
if suite.returncode != 0:
    fail("documented suite command failed:\n" + suite.stderr[-2000:])

print("PASS_TEST_SUITE_LOCALE_READS legacy-locale reads repaired in tests/test_research_current_status.py")

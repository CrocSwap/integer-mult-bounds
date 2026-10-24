"""Check wrapper child and grandchild flags without a mathematical replay."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--package", type=Path, required=True)
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
assert __debug__ and sys.flags.isolated == 1
assert os.environ.get("PYTHONOPTIMIZE") == "1"
assert not args.work.exists() and not args.out.exists()
wrapper = args.package.resolve() / "verify.py"
original_run = subprocess.run
records = []
child_probe = """
import json, os, subprocess, sys
assert __debug__ and sys.flags.optimize == 0
assert 'PYTHONOPTIMIZE' not in os.environ
code = 'import json,sys; assert __debug__; print(json.dumps({"optimize":sys.flags.optimize,"debug":__debug__}))'
r = subprocess.run([sys.executable, '-B', '-c', code], text=True, capture_output=True, check=True)
print(json.dumps({'optimize':sys.flags.optimize,'debug':__debug__,'grandchild':json.loads(r.stdout)}))
"""


def inspect_child(command, **kwargs):
    assert command[:2] == [sys.executable, "-B"]
    assert "PYTHONOPTIMIZE" not in kwargs["env"]
    probe = original_run([sys.executable, "-B", "-c", child_probe], **kwargs)
    assert probe.returncode == 0, probe.stderr
    flags = json.loads(probe.stdout)
    assert flags["optimize"] == flags["grandchild"]["optimize"] == 0
    records.append({"intercepted_command": command, "flags": flags})
    return probe


sys.argv = [str(wrapper), "--work", str(args.work.resolve())]
captured = io.StringIO()
with patch("subprocess.run", inspect_child), contextlib.redirect_stdout(captured):
    runpy.run_path(str(wrapper), run_name="__main__")
assert len(records) == 5
result = {
    "status": "PASS_CHILD_AND_GRANDCHILD_ASSERTION_FLAGS",
    "scope": "Environment instrumentation only. Mathematical children were replaced by flag probes.",
    "wrapper_sha256": hashlib.sha256(wrapper.read_bytes()).hexdigest(),
    "parent_flags": {"optimize": sys.flags.optimize, "isolated": sys.flags.isolated},
    "inherited_PYTHONOPTIMIZE": "1",
    "children": records,
}
args.out.write_text(json.dumps(result, indent=2) + "\n")
print(result["status"])

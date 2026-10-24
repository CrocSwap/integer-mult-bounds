"""Check the wrapper environment without running the mathematical checks.

This test replaces each child script with a small assertion-state probe.
It keeps the wrapper's actual command options and environment. The negative
control removes only the environment cleanup from a copy of the wrapper
source held in memory. No package file is changed.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys


parser = argparse.ArgumentParser()
parser.add_argument("package", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--omit-cleanup", action="store_true")
args = parser.parse_args()
package = args.package.resolve()
output = args.output.resolve()
if not __debug__ or not sys.flags.isolated:
    raise RuntimeError("The parent must have assertions and isolated mode")
if os.environ.get("PYTHONOPTIMIZE") != "1":
    raise RuntimeError("The test requires PYTHONOPTIMIZE=1 in the parent environment")

wrapper = package / "verify.py"
source = wrapper.read_text()
tree = ast.parse(source, filename=str(wrapper))
cleanup = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "pop"
            and node.value.args
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value == "PYTHONOPTIMIZE"):
        cleanup.append(node)
if len(cleanup) != 1:
    raise RuntimeError("Expected one PYTHONOPTIMIZE cleanup statement")
if args.omit_cleanup:
    lines = source.splitlines(keepends=True)
    node = cleanup[0]
    for index in range(node.lineno - 1, node.end_lineno):
        lines[index] = "\n"
    source = "".join(lines)

probe = """import json, os, sys
print(json.dumps({'assertions_enabled': __debug__, 'optimize': sys.flags.optimize,
                  'PYTHONOPTIMIZE': os.environ.get('PYTHONOPTIMIZE')}))
if not __debug__ or sys.flags.optimize != 0:
    raise RuntimeError('ASSERTIONS_DISABLED')
"""
original_run = subprocess.run
calls = []


def instrumented_run(command, **kwargs):
    if command[:2] != [sys.executable, "-B"]:
        raise RuntimeError("Unexpected child command")
    if not isinstance(kwargs.get("env"), dict):
        raise RuntimeError("The wrapper must pass its child environment")
    result = original_run(command[:2] + ["-c", probe], **kwargs)
    calls.append({"original_command": command,
                  "cleanup_present": "PYTHONOPTIMIZE" not in kwargs["env"],
                  "returncode": result.returncode,
                  "stdout": result.stdout,
                  "stderr": result.stderr})
    return result


subprocess.run = instrumented_run
sys.argv = [str(wrapper), "--work", str(output)]
failure = None
try:
    exec(compile(source, str(wrapper), "exec"),
         {"__name__": "__main__", "__file__": str(wrapper)})
except RuntimeError as error:
    failure = str(error)
finally:
    subprocess.run = original_run

if args.omit_cleanup:
    if (len(calls) != 1 or calls[0]["returncode"] == 0
            or "ASSERTIONS_DISABLED" not in calls[0]["stderr"]
            or failure is None or not failure.startswith("CHECK_FAILED ")):
        raise RuntimeError("The missing-cleanup control did not fail as required")
else:
    if failure or len(calls) != 6 or any(call["returncode"] for call in calls):
        raise RuntimeError("The assertion-state probes did not pass")

receipt = {"status": "PASS_WRAPPER_ASSERTION_CONTROL",
           "scope": "Instrumented child assertion probes, not mathematical replay",
           "parent_isolated": bool(sys.flags.isolated),
           "parent_assertions_enabled": __debug__,
           "parent_PYTHONOPTIMIZE": os.environ["PYTHONOPTIMIZE"],
           "omitted_cleanup_control": args.omit_cleanup,
           "wrapper_failure": failure, "calls": calls}
output.with_suffix(".json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({key: receipt[key] for key in
                  ("status", "scope", "omitted_cleanup_control")}))

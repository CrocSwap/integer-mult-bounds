#!/usr/bin/env python3
"""One-command, offline reproduction of the standalone X4 pair package."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def run(script, *args):
    command = [sys.executable, "-B", "-I"]
    if sys.flags.optimize:
        command.append("-O")
    result = subprocess.run(command + [str(HERE / script), *map(str, args)],
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(script + " failed:\n" + result.stdout + result.stderr)
    return result


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for relative, expected in sources["immutable_input_sha256"].items():
        if hashlib.sha256((HERE.parents[1] / relative).read_bytes()).hexdigest() != expected:
            raise ValueError("source binding differs: " + relative)
    print(run("verify.py", "--check", HERE / "RESULT.json").stdout.strip(), flush=True)
    independent = json.loads(run("independent_checker.py").stdout)
    if independent != json.loads((HERE / "INDEPENDENT.json").read_text()):
        raise ValueError("independent certificate differs")
    print("PASS independent pair proof: minima=4/4 words=11111 gatewise=6/6", flush=True)
    result = run("test_verify.py")
    print(result.stderr.strip(), flush=True)
    print("PASS_X4_PRECONDITION_PACKAGE no_new_kappa", flush=True)


if __name__ == "__main__":
    main()

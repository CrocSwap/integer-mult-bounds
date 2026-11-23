#!/usr/bin/env python3
"""Replay frozen author evidence and a separately implemented exact oracle.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Fresh bytecode directories are used even under optimized Python.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def invoke(script, arguments, optimized=False):
    with tempfile.TemporaryDirectory(prefix="native-grid-cache-") as cache:
        command = [sys.executable, "-X", "pycache_prefix=" + cache]
        if optimized:
            command.append("-O")
        command += ["-B", str(ROOT / script), *map(str, arguments)]
        return subprocess.run(command, cwd=ROOT, capture_output=True,
                              text=True, timeout=90, check=False)


def replay(mode):
    frozen = json.loads((ROOT / "FROZEN.json").read_text())
    for relative, expected in frozen["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        require(actual == expected, "author frozen bytes differ: " + relative)
    for optimized in (False, True):
        suffix = "-OPTIMIZED" if optimized else ""
        if mode == "author":
            script, arguments = "check.py", []
            evidence = ROOT / ("EVIDENCE" + suffix + ".json")
        else:
            script, arguments = "review/independent.py", [ROOT / "retained/tensor_word.py"]
            evidence = ROOT / "review" / ("EVIDENCE" + suffix + ".json")
        completed = invoke(script, arguments, optimized)
        require(completed.returncode == 0, completed.stderr + completed.stdout)
        require(json.loads(completed.stdout) == json.loads(evidence.read_text()),
                "fresh evidence differs: " + str(evidence))
        if mode == "independent":
            with tempfile.TemporaryDirectory(prefix="native-grid-control-") as scratch:
                altered = Path(scratch) / "altered_source.py"
                altered.write_bytes((ROOT / "retained/tensor_word.py").read_bytes()
                                    + b"\n# independent source-corruption control\n")
                rejected = invoke(script, [altered], optimized)
                require(rejected.returncode != 0 and "literal raw-H source hash" in rejected.stderr,
                        "altered-source control did not fail at source authentication")
    print("PASS_NATIVE_GRID_" + mode.upper() + "_NORMAL_OPTIMIZED_FRESH_CACHE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("author", "independent"))
    replay(parser.parse_args().mode)

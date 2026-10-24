"""Independent bounded checks for the returned-register package."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(sys.argv[1]).resolve()
BUILD = Path(sys.argv[2]).resolve()
RESULT = Path(sys.argv[3]).resolve()
checks = []

def require(value, label):
    if not value:
        raise RuntimeError(label)
    checks.append(label)

def run_reject(command, message):
    result = subprocess.run(command, capture_output=True, text=True)
    require(result.returncode != 0 and message in result.stdout + result.stderr, message)

with tempfile.TemporaryDirectory(prefix="returned-register-controls-") as temp:
    tmp = Path(temp)
    run_reject([sys.executable, "-O", "-B", str(PACKAGE / "verify.py"), "--build", str(tmp / "optimized")], "Run this verifier without -O")
    require(not (tmp / "optimized").exists(), "optimized mode rejects before creating output")
    occupied = tmp / "occupied"
    occupied.mkdir()
    (occupied / "sentinel").write_bytes(b"retained")
    run_reject([sys.executable, "-B", str(PACKAGE / "verify.py"), "--build", str(occupied)], "FileExistsError")
    require((occupied / "sentinel").read_bytes() == b"retained", "occupied output is unchanged")
    copy = tmp / "package"
    copy.mkdir()
    for item in PACKAGE.iterdir():
        if item.is_file():
            shutil.copy2(item, copy / item.name)
    with (copy / "PROOF.txt").open("ab") as out:
        out.write(b"\nmutation\n")
    run_reject([sys.executable, "-B", str(copy / "verify.py"), "--build", str(tmp / "mutated")], "Source hash: PROOF.txt")
    require(not (tmp / "mutated").exists(), "source mutation rejects before creating output")
    bad = tmp / "bad.bin"
    bad.write_bytes(b"x")
    run_reject([str(BUILD / "rational"), str(bad), str(tmp / "rational"), "dirty"], "Invalid input length")
    run_reject([str(BUILD / "field101"), str(bad), str(tmp / "field.jsonl")], "Input size is not divisible by 18")

# Propagate each input column through actual address shifts. This does not
# use either collision engine or its formal matrix expansion.
ZERO = (0,) * 9
TARGETS = [(1,0,0,2,3,0,4,5,7), (2,0,0,-1,5,0,6,4,3), (3,0,0,7,2,0,-2,9,5)]
word = []
for role, target in enumerate(TARGETS):
    for column in range(3):
        frame = tuple(target[3*i+j] if j == column else 0 for i in range(3) for j in range(3))
        word.append((role, frame))

def endpoint(calls):
    columns = []
    for source in range(4):
        state = [{ZERO} if i == source else set() for i in range(4)]
        for role, frame in calls:
            state[role] = {tuple(a+b for a,b in zip(exponent, frame)) for exponent in state[role]}
        columns.append(state)
    return columns

expected = [[{TARGETS[i] if i < 3 else ZERO} if i == j else set() for i in range(4)] for j in range(4)]
require(endpoint(word) == expected, "nine calls realize three different lower triangular targets and all four input columns")
for omitted in range(9):
    require(endpoint(word[:omitted] + word[omitted+1:]) != expected, "omitted call " + str(omitted) + " changes the endpoint")
wrong_dirty = [row.copy() for row in expected]
wrong_dirty[3][3] = {TARGETS[0]}
require(endpoint(word) != wrong_dirty, "changed returned-role endpoint is rejected")

RESULT.write_text(json.dumps({"status": "PASS_BOUNDED_INDEPENDENT_CONTROLS", "checks": checks}, indent=2) + "\n")
print(len(checks), "controls passed")

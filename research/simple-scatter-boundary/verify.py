#!/usr/bin/env python3
"""Exact boundary replay. Arham Tahir with OpenAI Codex; Apache-2.0."""

import argparse
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
PREDECESSOR = "research/scatter-export-parity-audit/RESULT.json"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inputs():
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    result = {}
    for row in pins:
        if row["usage"] == "input":
            body = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(body).hexdigest() == row["sha256"], row["path"])
            result[row["path"]] = body
    selected = json.loads(result[SELECTED])["files"]
    scripts = runpy.run_path(str(PACKAGE / "boundary.py"))["SCRIPTS"]
    for path in (WORD, *scripts.values()):
        require(hashlib.sha256(result[path]).hexdigest() == selected[path], "selected binding")
    return result


def run(command):
    return subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)


def cli(mode, word, output=None):
    command = [sys.executable, "-I", "-B", str(PACKAGE / "boundary.py"), mode, str(word)]
    return run(command + ([] if output is None else [str(output)]))


def columns(raw, word):
    """Separate F2 interpreter, retaining arbitrary dirty input coordinates."""
    n = 2 * word["v"] + word["R"]
    require(len(raw) % 24 == 0, "aligned records")
    values, owner = [1 << i for i in range(n)] + [0], None
    for op, a, b, coefficient, _frame, _phase in struct.iter_unpack("<6i", raw):
        if op == 0:
            continue
        require(0 <= a <= n and 0 <= b <= n, "record registers")
        if op == 1:
            require(a < n and (b < n or owner is not None), "ADD temporary")
            if coefficient % 2:
                values[a] ^= values[b]
        elif op == 2:
            require(owner is None and a < n and b == n and values[n] == 0, "fresh COPY")
            values[n], owner = values[a], a
        elif op == 3:
            require(owner == a and b == n and values[n] == values[a], "bound ERASE")
            values[n], owner = 0, None
        else:
            raise ValueError("record opcode")
    require(owner is None and values[n] == 0, "closed temporary")
    expected = [1 << i for i in range(n)]
    for t in range(word["v"]):
        expected[word["v"] + t] ^= 1 << t
    return values[:-1], expected


def support_enumeration(validate):
    """Every ordered row of length <=5 on three indices: 364 cases."""
    accepted, rejected = 0, 0
    for length in range(6):
        for row in itertools.product(range(3), repeat=length):
            word = {"v": 1, "ret": [10, 11, 12], "scatter": [list(row)]}
            counts = [sum(k == j for k in row) for j in range(3)]
            simple = all(m <= 1 for m in counts)
            try:
                validate(word)
            except ValueError:
                require(not simple, "valid support rejected")
                rejected += 1
                continue
            require(simple, "multiplicity accepted")
            for values in itertools.product((0, 1), repeat=3):
                literal = sum(values[k] for k in row) % 2
                membership = sum(values[k] for k in range(3) if k in row) % 2
                require(literal == membership, "scatter coefficient mismatch")
            accepted += 1
    return {"rows": accepted + rejected, "accepted": accepted, "rejected": rejected}


def audit(directory):
    data = inputs()
    boundary = runpy.run_path(str(PACKAGE / "boundary.py"))
    word = json.loads(gzip.decompress(data[WORD]))
    fixture = directory / "word.json.gz"
    fixture.write_bytes(data[WORD])
    original, successor = directory / "original", directory / "successor"
    script = directory / "original-export.py"
    script.write_bytes(data[boundary["SCRIPTS"]["export"]])
    old = run([sys.executable, "-I", "-B", str(script), str(fixture), str(original)])
    require(old.returncode == 0, old.stderr)
    for mode, output in (("check", None), ("export", successor)):
        result = cli(mode, fixture, output)
        require(result.returncode == 0, result.stdout + result.stderr)
    digests = {}
    for name in ARTIFACTS:
        body = (original / name).read_bytes()
        require(body == (successor / name).read_bytes(), "artifact identity: " + name)
        digests[name] = hashlib.sha256(body).hexdigest()
    raw = (successor / ARTIFACTS[0]).read_bytes()
    actual, expected = columns(raw, word)
    require(actual == expected and len(actual) == 661, "all dirty columns")
    predecessor = json.loads(data[PREDECESSOR])
    require(digests[ARTIFACTS[0]] == predecessor["baseline"]["records_sha256"], "predecessor baseline")
    paired = copy.deepcopy(word)
    paired["scatter"][0].extend([0, 0])
    fixture.write_bytes(gzip.compress(json.dumps(paired).encode(), mtime=0))
    checker = directory / "original-check.py"
    checker.write_bytes(data[boundary["SCRIPTS"]["check"]])
    old_check = run([sys.executable, "-I", "-B", str(checker), str(fixture)])
    require(old_check.returncode == 0, "predecessor paired symbolic acceptance")
    original_bad = directory / "original-mutant"
    old = run([sys.executable, "-I", "-B", str(script), str(fixture), str(original_bad)])
    require(old.returncode == 0, "predecessor mutant exported")
    old_raw = (original_bad / ARTIFACTS[0]).read_bytes()
    require(hashlib.sha256(old_raw).hexdigest() == predecessor["mutant"]["records_sha256"], "same counterexample")
    actual_bad, _ = columns(old_raw, paired)
    require([i for i in range(661) if actual_bad[i] != expected[i]] == [111], "one changed target")
    require(actual_bad[111] >> 472 & 1, "dirty-input witness")
    rejected = directory / "rejected"
    for mode, output in (("check", None), ("export", rejected)):
        result = cli(mode, fixture, output)
        require(result.returncode == 2 and "duplicate index 0" in result.stderr, "entry guard")
    require(not rejected.exists(), "reject before output creation")
    return {"schema": boundary["SCHEMA"], "columns": 661, "records": len(raw) // 24,
            "artifacts_sha256": digests, "paired_mutant_rejected_modes": ["check", "export"],
            "predecessor_paired_symbolic_accepts": True,
            "enumeration": support_enumeration(boundary["validate_scatter"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="scatter-boundary-verify-") as temporary:
        result = audit(Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), "typed receipt")
        print("PASS_SIMPLE_SCATTER_BOUNDARY columns=661 artifacts=3 rows=364 modes=2 no_new_kappa")


if __name__ == "__main__":
    main()

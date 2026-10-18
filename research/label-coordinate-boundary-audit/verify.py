#!/usr/bin/env python3
"""Source-bound label coercion audit. OpenAI Codex assistance; Apache-2.0."""

import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
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
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")
boundary = runpy.run_path(str(PACKAGE / "boundary.py"))
require = boundary["require"]


def inputs():
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    data = {row["path"]: boundary["source_bytes"](row["path"])
            for row in pins if row["usage"] == "input"}
    selected = json.loads(data[SELECTED])["files"]
    for path in (WORD, *boundary["SCRIPTS"].values()):
        require(hashlib.sha256(data[path]).hexdigest() == selected[path], "selected binding: " + path)
    return data


def run(command):
    return subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)


def cli(mode, word, output=None, predecessor=False):
    script = ROOT / boundary["PREDECESSOR"] if predecessor else PACKAGE / "boundary.py"
    command = [sys.executable, "-I", "-B", str(script), mode, str(word)]
    return run(command + ([] if output is None else [str(output)]))


def rank(rows):
    """Independent exact row rank, including the dyadic mutant's raw values."""
    pivots = {}
    for values in rows:
        row = list(map(Fraction, values))
        for col, pivot in sorted(pivots.items()):
            scale = row[col]
            row = [a - scale * b for a, b in zip(row, pivot)]
        col = next((i for i, value in enumerate(row) if value), None)
        if col is not None:
            pivots[col] = [value / row[col] for value in row]
    return len(pivots)


def scalar_columns(raw, word):
    """Boolean projection only: frame metadata is deliberately not certified."""
    n = 2 * word["v"] + word["R"]
    require(len(raw) % 24 == 0, "record alignment")
    values = [1 << i for i in range(n)] + [0]
    owner = None
    for op, a, b, coefficient, _frame, _phase in struct.iter_unpack("<6i", raw):
        if op == 0:
            continue
        require(0 <= a < n and 0 <= b <= n, "record registers")
        if op == 1:
            require(b < n or owner is not None, "live temporary")
            if coefficient % 2:
                values[a] ^= values[b]
        elif op == 2:
            require(owner is None and b == n and values[n] == 0, "fresh COPY")
            values[n], owner = values[a], a
        elif op == 3:
            require(owner == a and b == n and values[n] == values[a], "bound ERASE")
            values[n], owner = 0, None
        else:
            raise ValueError("record opcode")
    expected = [1 << i for i in range(n)] + [0]
    for i in range(word["v"]):
        expected[word["v"] + i] ^= 1 << i
    require(owner is None and values == expected, "scalar endpoint/cleanup")
    return n


def audit(directory):
    data = inputs()
    word = json.loads(gzip.decompress(data[WORD]))
    mutant = copy.deepcopy(word)
    require(word["lines"][0] == [2, 0, 0, 0, 0, 0, 0, 0], "source witness")
    mutant["lines"][0][1] = 0.5
    normalized = [[int(a) for a in row] for row in mutant["lines"]]
    require(normalized == word["lines"], "checker sees original labels")
    norm = sum(Fraction(a) ** 2 for a in mutant["lines"][0]) / 2
    require(norm == Fraction(17, 8), "raw label fails norm two")
    outputs, digests = {}, {}
    for name, fixture in (("baseline", word), ("mutant", mutant)):
        path = directory / (name + ".json")
        path.write_text(json.dumps(fixture), encoding="utf-8")
        check = cli("check", path, predecessor=True)
        require(check.returncode == 0 and "PASS interleaved interface lemma" in check.stdout,
                name + " full predecessor acceptance: " + check.stdout + check.stderr)
        output = directory / name
        exported = cli("export", path, output, predecessor=True)
        require(exported.returncode == 0, exported.stdout + exported.stderr)
        outputs[name] = {file: (output / file).read_bytes() for file in ARTIFACTS}
        digests[name] = {file: hashlib.sha256(body).hexdigest() for file, body in outputs[name].items()}
        require(scalar_columns(outputs[name][ARTIFACTS[0]], fixture) == 661, "661 scalar columns")
        for mode in ("check", "export"):
            destination = directory / ("guard-" + name) if mode == "export" else None
            guarded = cli(mode, path, destination)
            require(guarded.returncode == (0 if name == "baseline" else 2),
                    "new boundary: " + guarded.stdout + guarded.stderr)
            if name == "mutant":
                require("coordinate 1 must be an exact integer" in guarded.stderr, "label diagnostic")
                require(destination is None or not destination.exists(), "no rejected outputs")
        if name == "baseline":
            for file in ARTIFACTS:
                require((directory / "guard-baseline" / file).read_bytes() == outputs[name][file],
                        "valid artifact identity: " + file)
    frames = {name: json.loads(output["frames.json"])["frames"] for name, output in outputs.items()}
    for name, fixture in (("baseline", word), ("mutant", mutant)):
        for k, frame in enumerate(fixture["frames"]):
            require(rank([fixture["lines"][i] for i in frame]) == frames[name][str(k)]["dim"],
                    f"independent raw frame rank: {name} {k}")
    changed = [k for k in frames["baseline"] if frames["baseline"][k] != frames["mutant"][k]]
    changed_dims = [k for k in changed if frames["baseline"][k]["dim"] != frames["mutant"][k]["dim"]]
    require((len(changed), len(changed_dims)) == (119, 77), "geometry delta")
    records = {name: list(struct.iter_unpack("<6i", output[ARTIFACTS[0]])) for name, output in outputs.items()}
    require(len(records["baseline"]) == len(records["mutant"]) == 27234, "record counts")
    deltas = [(a, b) for a, b in zip(records["baseline"], records["mutant"]) if a != b]
    require(deltas and all(a[:4] == b[:4] and
            ((a[0] == 0 and a[5] == b[5]) or (a[0] == 2 and a[4] == b[4]))
            for a, b in deltas), "only MOVE/COPY rank fields change")
    require(outputs["baseline"]["249-states.json"] == outputs["mutant"]["249-states.json"], "same states")
    integer = copy.deepcopy(word)
    integer["lines"][0][1] = 1
    path = directory / "integer-control.json"
    path.write_text(json.dumps(integer), encoding="utf-8")
    control = cli("check", path)
    require(control.returncode == 1 and "REJECT" in control.stdout, "full checker still rejects changed geometry")
    require(frames["baseline"]["267"]["dim"] == 4 and frames["mutant"]["267"]["dim"] == 5, "frame 267 witness")
    return {"mutation": {"path": "lines[0][1]", "before": 0, "after": "1/2"},
            "raw_mutant_norm": str(norm), "predecessor_accepts_modes": ["check", "export"],
            "guard_rejects_modes": ["check", "export"], "scalar_columns_each": 661,
            "records_each": 27234, "frames_each": 636, "changed_frames": len(changed),
            "changed_frame_dimensions": len(changed_dims), "frame_267_dimensions": [4, 5],
            "changed_records": len(deltas), "first_changed_record": [list(x) for x in deltas[0]],
            "changed_copy_records": sum(a[0] == 2 for a, _ in deltas),
            "integer_geometry_control_rejected": True, "artifacts_sha256": digests}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="label-audit-") as temporary:
        result = audit(Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(json.dumps(result, sort_keys=True) == json.dumps(json.loads((PACKAGE / "RESULT.json").read_bytes()), sort_keys=True),
                "typed receipt mismatch")
        print("PASS_LABEL_COORDINATE_BOUNDARY frames=636 changed=119 dimensions=77 columns=661 modes=2 no_new_kappa")


if __name__ == "__main__":
    main()

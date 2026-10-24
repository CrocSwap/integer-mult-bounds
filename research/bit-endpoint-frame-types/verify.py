#!/usr/bin/env python3
"""Actual checked export plus the retained C++ terminal predicate, not full native replay.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
import boundary as B

WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
NATIVE = "research/e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp"
HEADER = "research/e8-bit-carrier-skeleton/code/bit/checkers/json.hpp"
STAGER = "research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")


def sha(body):
    return hashlib.sha256(body).hexdigest()


def authenticate():
    bodies = {}
    for row in json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            B.require(sha(raw) == row["sha256"], "source pin: " + row["path"])
            bodies[row["path"]] = raw
    B.require('if(state[s]!=st["final"][to_string(s)])throw runtime_error("final frame")'
              in bodies[NATIVE].decode(), "actual native terminal comparison")
    B.require('int(v) for k, v in st[\'initial\'].items()' in bodies[STAGER].decode(),
              "actual initial-frame staging conversion")
    return bodies


def write_word(directory, name, word):
    path = directory / (name + ".json.gz")
    path.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
    return path


def run(command, expected=0):
    result = subprocess.run(command, capture_output=True, timeout=90, check=False)
    B.require(result.returncode == expected, "unexpected command result: " + repr(command) +
              "\n" + result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace"))
    return result.stdout.decode().strip()


def cli(mode, word, output=None, optimized=False):
    command = [sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
    command += [str(PACKAGE / "boundary.py"), mode, str(word)]
    if output is not None:
        command.append(str(output))
    return command


def hashes(output):
    return {name: sha((output / name).read_bytes()) for name in ARTIFACTS}


def audit():
    bodies = authenticate()
    word = json.loads(gzip.decompress(bodies[WORD]))
    B.require((word["v"], word["R"], len(word["frames"])) == (111, 439, 636), "source shape")
    B.require(type(word["start"][240]) is int and word["start"][240] == 0 and
              type(word["final"][0]) is int and word["final"][0] == 1, "witness locations")
    compiler = shutil.which("g++")
    B.require(compiler is not None, "g++ (C++17) is required for the actual JSON predicate probe")
    with tempfile.TemporaryDirectory(prefix="endpoint-frame-audit-") as temporary:
        directory = Path(temporary)
        private = directory / "sources"
        for path, body in bodies.items():
            target = private / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        predecessor = B.module(bodies[B.PREDECESSOR], private / B.PREDECESSOR)
        executable = directory / ("predicate.exe" if sys.platform == "win32" else "predicate")
        run([compiler, "-std=c++17", "-O0", "-I", str((private / HEADER).parent),
             str(PACKAGE / "json_endpoint_probe.cpp"), "-o", str(executable)])
        base_word = write_word(directory, "baseline", word)
        baseline = directory / "baseline-export"
        base_receipt = predecessor["execute"]("export", base_word, baseline, root=private)
        reference = hashes(baseline)
        B.require(base_receipt["export"]["records"] == 27234, "baseline record count")
        B.require(reference["249-records.bin"] ==
                  "ea44aa047a2a9cf034de8b56b2166c49cf2dbdf9cd9ed6a20299a4f2b05ef09a",
                  "credited predecessor baseline digest")
        rows = []
        for name, change_start, change_final in (
            ("baseline", False, False), ("start_false", True, False),
            ("final_true", False, True), ("both", True, True),
        ):
            candidate = deepcopy(word)
            if change_start:
                candidate["start"][240] = False
            if change_final:
                candidate["final"][0] = True
            path = write_word(directory, name, candidate)
            output = baseline if name == "baseline" else directory / (name + "-export")
            receipt = base_receipt if name == "baseline" else predecessor["execute"](
                "export", path, output, root=private)
            observed = hashes(output)
            B.require(observed["249-records.bin"] == reference["249-records.bin"] and
                      observed["frames.json"] == reference["frames.json"], "unchanged action/geometry")
            staged_in, staged_out = directory / (name + "-in"), directory / (name + "-out")
            run([sys.executable, "-I", "-B", str(private / STAGER), str(baseline),
                 str(output), str(staged_in), str(staged_out)])
            initial = json.loads((staged_out / "COHORT249-INITIAL.json").read_bytes())
            B.require(type(initial["240"]) is int and initial["240"] == 0,
                      "staging canonicalizes initial Boolean")
            native_result = run([str(executable), str(baseline / "249-states.json"),
                                 str(staged_in / "249-states.json")], int(change_final))
            B.require(native_result == ("REJECT_FINAL_FRAME role=0" if change_final else
                                        "PASS_FINAL_FRAME_PREDICATE roles=661"), "terminal verdict")
            new_output = directory / (name + "-guarded")
            if change_start or change_final:
                run(cli("export", path, new_output), 2)
                run(cli("check", path, optimized=True), 2)
                B.require(not new_output.exists(), "invalid endpoint published output")
                guarded = "reject_before_delegation"
            else:
                run(cli("export", path, new_output))
                B.require(hashes(new_output) == reference, "all three baseline artifacts unchanged")
                guarded = "accept_identical_export"
            rows.append({"case": name, "predecessor": receipt["schema"],
                         "predecessor_accepts": True, "artifacts": observed,
                         "native_terminal_predicate": native_result, "guarded": guarded})
        pairs = deepcopy(word)
        pairs["scatter"][0] += [0, 0]
        pair_path = write_word(directory, "cancelled_pair", pairs)
        pair_output = directory / "pair-guarded"
        pair_receipt = json.loads(run(cli("export", pair_path, pair_output, optimized=True)))
        B.require(hashes(pair_output) == reference, "XOR normalization retained")
        B.require(pair_receipt["input_occurrences"] == 529 and
                  pair_receipt["normalized_scatter_terms"] == 527, "XOR invoice retained")
        controls = []
        for name, field, value in (("fractional_label", "label", 0.5),
                                   ("wrong_integer_geometry", "label", 1),
                                   ("wrong_integer_final", "final", 0)):
            bad = deepcopy(word)
            if field == "label":
                bad["lines"][0][1] = value
            else:
                bad["final"][0] = value
            B.validate_endpoints(bad)
            path = write_word(directory, name, bad)
            output = directory / (name + "-guarded")
            run(cli("export", path, output, optimized=True), 2)
            B.require(not output.exists(), "semantic rejection published output")
            controls.append(name)
        return {"status": "PASS_BIT_ENDPOINT_FRAME_TYPES", "roles": 661, "frames": 636,
                "cases": rows, "xor_pair": "all_three_artifacts_identical",
                "semantic_controls_rejected": controls,
                "native_scope": "Actual staged JSON and exact compiled terminal predicate only; full native replay unrun."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        B.require(result == json.loads((PACKAGE / "RESULT.json").read_bytes()), "receipt mismatch")
        print(result["status"], "cases=4", "semantic_rejections=3", "no_new_kappa")


if __name__ == "__main__":
    main()

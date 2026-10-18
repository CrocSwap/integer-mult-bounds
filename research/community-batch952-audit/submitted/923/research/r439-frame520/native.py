#!/usr/bin/env python3
"""Replay the R439 frame-520 candidate with the unchanged native source checkers.

Adapted by Ross, with substantial OpenAI Codex assistance, from Ali Romman's
PR688 native harness and Alluri's supplier-circuit-consolidation follow-up.
Exporter and C++ checker authors include Dylan Crow and DaysSky; their source
notices are retained unchanged. Apache-2.0. This is finite circuit verification,
not a proof of the multiplication theorem or a new conditional exponent.

Requires Python 3.11+, a C++17 compiler and Boost headers. No NumPy/SciPy/SymPy.
Example: BOOST_INCLUDE=/path/to/boost python3 -B native.py --word candidate.json.gz
         --out /tmp/r439-native
"""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import struct
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINFILE = HERE / "native-source-pins.json"
BASELINE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
LEGALITY = "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE"
FIVE = "PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
BRIDGED = "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_word(path):
    with (gzip.open(path, "rt") if str(path).endswith(".gz") else path.open()) as stream:
        return json.load(stream)


def content_sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def additions(word):
    return sum(len(gate[2]) for section in "DABC" for gate in word[section]) + sum(map(len, word["scatter"]))


def record_structure(path):
    """Compare the ordered moves of each role, allowing independent interleaving."""
    raw = path.read_bytes()
    require(len(raw) % 24 == 0, "Unaligned source-exported records")
    moves = defaultdict(list)
    copy_erase = []
    for event in struct.iter_unpack("<6i", raw):
        op, role, *rest = event
        if op == 0:
            moves[str(role)].append(rest)
        elif op in (2, 3):
            copy_erase.append(list(event))
    return dict(moves), copy_erase


def run(root, out, baseline=None, candidate=None, expected_saving=None):
    """Write full native logs/receipts under out/native; return deterministic data.

    The normal parent invocation supplies out/baseline.json.gz and
    out/replacement.json.gz. Standalone use defaults baseline to the pinned PR589
    word. Existing native outputs are refused to prevent stale receipt reuse.
    """
    require(not sys.flags.optimize, "Run without -O: inherited exporter uses assertions")
    root, out = Path(root).resolve(), Path(out).resolve()
    if baseline is None:
        baseline = out / "baseline.json.gz"
        if not baseline.exists():
            baseline = root / BASELINE
    else:
        baseline = Path(baseline).resolve()
    require(baseline.is_file(), "Missing baseline word")
    candidate = Path(candidate).resolve() if candidate else out / "replacement.json.gz"
    require(candidate.is_file(), "Missing replacement word")
    pins = json.loads(PINFILE.read_text())
    for relative, expected in pins["sha256"].items():
        require(digest(root / relative) == expected, "Source pin mismatch: " + relative)
    words = {"baseline": load_word(baseline), "replacement": load_word(candidate)}
    require(content_sha(words["baseline"]) == pins["baseline_content_sha256"],
            "Baseline differs from the decoded pinned PR589 word")
    for name, word in words.items():
        require((word["h"], word["v"], word["R"], len(word["ret"])) == (8, 111, 439, 9),
                name + " has unexpected circuit dimensions")
    # Only B and its matching literal C reverse may change in this scoped rewrite.
    require({k: v for k, v in words["baseline"].items() if k not in ("B", "C")} ==
            {k: v for k, v in words["replacement"].items() if k not in ("B", "C")},
            "Candidate changes metadata or phases outside B/C")
    before, after = words["baseline"], words["replacement"]
    suffix_length = len(before["B"]) - 283
    require(after["B"][:242] == before["B"][:242] and
            after["B"][-suffix_length:] == before["B"][283:], "Candidate changes another B block")
    wires = set(before["frames"][520])
    require(all(f == 520 and d in wires and all(s in wires for s in ss)
                for f, d, ss in after["B"][242:-suffix_length]), "Candidate block uses other wires/frames")
    full_frame = next(i for i, f in enumerate(after["frames"]) if len(f) == after["v"])
    expected_c = [[full_frame, d, ss] for _, d, ss in reversed(after["A"] + after["B"])
                  if not after["v"] <= d < 2 * after["v"]]
    require(after["C"] == expected_c, "Candidate C is not the literal source/helper reverse")
    saving = additions(words["baseline"]) - additions(words["replacement"])
    if expected_saving is not None:
        require(saving == expected_saving, "Candidate scalar saving differs from expectation")

    native = out / "native"
    native.mkdir(parents=True, exist_ok=False)
    bindir = native / "bin"
    bindir.mkdir()
    package = root / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    include = Path(os.environ.get("BOOST_INCLUDE", "/usr/include")).resolve()
    require((include / "boost/multiprecision/cpp_int.hpp").is_file(),
            "Boost headers missing; set BOOST_INCLUDE to their parent directory")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + str(include)]
    commands = []

    def call(name, command):
        command = list(map(str, command))
        commands.append({"name": name, "argv": command})
        (native / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        with (native / (name + ".log")).open("w") as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)

    call("compiler-version", compiler + ["--version"])
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "compiler": (native / "compiler-version.log").read_text(),
        "boost_include": str(include),
        "boost_version_header_sha256": digest(include / "boost/version.hpp"),
        "boost_cpp_int_header_sha256": digest(include / "boost/multiprecision/cpp_int.hpp"),
        "boost_version_defines": [line for line in (include / "boost/version.hpp").read_text().splitlines()
                                  if line.startswith(("#define BOOST_VERSION ", "#define BOOST_LIB_VERSION "))],
    }
    (native / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    call("compile-legality", compiler + flags + ["-o", bindir / "legality", checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             bindir / ("columns" + str(pairs)), checkers / "columns_k.cpp"])

    results, structures, frames, states = {}, {}, {}, {}
    for name, path in (("baseline", baseline), ("replacement", candidate)):
        records, cin, cout = (native / name / item for item in ("records", "cin", "cout"))
        call(name + "-export", [sys.executable, "-I", "-B", bit / "export_records.py", path, records])
        call(name + "-cohort", [sys.executable, "-I", "-B", bit / "regression/stage_cohort.py", records, records, cin, cout])
        frames[name] = json.loads((records / "frames.json").read_text())
        states[name] = json.loads((records / "249-states.json").read_text())
        structures[name] = record_structure(records / "249-records.bin")
        call(name + "-legality", [bindir / "legality", cin, cout, cout / "legality.json"])
        legality = json.loads((cout / "legality.json").read_text())
        require(legality["status"] == LEGALITY, "Legality did not pass")
        require(legality["copies"] == legality["erasures"] == 9, "Wrong COPY/ERASE count")
        require(legality["rank_mass"] == 8 * 439 + 63 + 14 * 111 == 5129, "Wrong rank mass")
        require(legality["common_frame_ADDs"] == additions(words[name]), "Exporter scalar bill differs from word")
        results[name] = {"word_content_sha256": content_sha(words[name]), "legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            receipt = cout / ("columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [bindir / ("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", receipt])
            data = json.loads(receipt.read_text())
            require(data["status"] == (FIVE if pairs == 2 else BRIDGED), "Formal columns did not pass")
            count, stages = 6 * (pairs - 1), 2 * pairs + 1
            require(data["negative_controls"] == [{"omit_bridge": i, "rejected": True} for i in range(count)],
                    "Bridge controls must reject every omitted bridge exactly once")
            require(data["formal_columns_checked"] == 222 * pairs + 439, "Wrong formal column count")
            require(data["bridge_additions"] == count * 111, "Wrong bridge additions")
            require(len(data["stages"]) == stages and [x["stage"] for x in data["stages"]] == list(range(stages)),
                    "Missing or duplicate stage")
            require(data["local_scalar_additions"] == additions(words[name]), "Native scalar bill differs from word")
            require(data["fresh_center_copies"] == stages * 9 and data["reverse_fresh_center_copies"] == pairs * 9,
                    "Wrong forward/reverse copied-centre counts")
            for i, stage in enumerate(data["stages"]):
                require(stage == {"stage": i, "signed_inverse": bool(i % 2), "fresh_copies": 9,
                                  "scalar_additions": additions(words[name])}, "Stage bill or direction differs")
            prefix = data["signed_lift_prefix"]
            require(len(prefix) == 2 and [x["reverse"] for x in prefix] == [False, True], "Prefix orientations differ")
            fwd, rev = [int(x["cancellation_free_signed_row_l1_upper"]) for x in prefix]
            payload = 64 * fwd ** 3 * rev ** 2
            require(payload == int(data["payload_prefix_upper"]) < 2 ** 104, "Incorrect or excessive payload bound")
            require(data["payload_prefix_bits"] == payload.bit_length(), "Payload bit count differs")
            require([x["bits"] for x in prefix] == [fwd.bit_length(), rev.bit_length()], "Prefix bit counts differ")
            # Raw receipts retain timings and absolute source paths; this mathematical subsection does not.
            results[name]["stages"][str(stages)] = {key: value for key, value in data.items()
                                                   if key not in ("seconds", "local_scalar_stream")}

    require(frames["baseline"] == frames["replacement"], "Decoded frame geometry differs")
    require(states["baseline"] == states["replacement"], "Decoded initial/final state differs")
    require(structures["baseline"] == structures["replacement"],
            "Per-role ordered MOVE sequence or COPY/ERASE sequence differs")
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("baseline", "replacement"))
        require(old["local_raw_H"] == new["local_raw_H"], "Paid profile differs")
        require(old["local_scalar_additions"] - new["local_scalar_additions"] == saving, "Native saving differs")
    result = {
        "status": "PASS_R439_FRAME520_NATIVE_REPLAY",
        "source_pins_sha256": digest(PINFILE),
        "mathematical": {
            "baseline": results["baseline"], "replacement": results["replacement"],
            "comparison": {
                "saved_local_scalar_additions": saving,
                "decoded_frames_identical": True, "decoded_states_identical": True,
                "ordered_moves_identical_per_role": True, "copy_erase_sequence_identical": True,
                "roles_with_moves": len(structures["baseline"][0]),
                "per_role_moves_sha256": content_sha(structures["baseline"][0]),
                "copy_erase_sha256": content_sha(structures["baseline"][1]),
                "decoded_frames_sha256": content_sha(frames["baseline"]),
                "raw_H_identical": True,
            },
        },
        "scope": "Finite legality, all independent F2 columns at 5/9/11 stages, omitted-bridge controls and signed prefix accounting. No global hosting replay or exponent claim.",
    }
    (native / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    (native / "NATIVE.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected-saving", type=int)
    args = parser.parse_args()
    result = run(ROOT, args.out, args.baseline, args.word, args.expected_saving)
    print(result["status"] + " saved=" + str(result["mathematical"]["comparison"]["saved_local_scalar_additions"]))


if __name__ == "__main__":
    main()

"""Export and audit the finite R420 candidate at the native record boundary.

Only the Python standard library is required. The upstream exporter is run
unchanged; optional upstream C++ checkers need a compiler and Boost headers.
The Python bridged replay is a separately identified fallback, not a claim that
the official C++ checkers ran. No pricing or asymptotic improvement is inferred.
Its schedule and prefix formula follow the Apache-2.0 columns_k.cpp checker by
Dylan Crow and DaysSky (with Claude assistance); it is a port of that check,
not an independent derivation of the bridged composition theorem.

Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
SKELETON = RESEARCH / "e8-bit-carrier-skeleton"
BIT = SKELETON / "code/bit"
BASELINE = RESEARCH / "e8-bit-r420/data/bitE8mut-r420.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_word(path):
    with (gzip.open(path, "rt") if str(path).endswith(".gz") else open(path)) as handle:
        return json.load(handle)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def run_logged(command, logfile):
    completed = subprocess.run(list(map(str, command)), capture_output=True, text=True)
    logfile.write_text("$ " + " ".join(map(str, command)) + "\n" + completed.stdout + completed.stderr)
    return completed.returncode


def export(word, out):
    records = out / "records"
    records.mkdir(parents=True, exist_ok=True)
    require(run_logged([sys.executable, "-I", "-B", BIT / "export_records.py", word, records],
                       out / "export.log") == 0, "unchanged native export failed")
    raw = (records / "249-records.bin").read_bytes()
    require(len(raw) % 24 == 0, "native record alignment")
    rows = list(struct.iter_unpack("<6i", raw))
    state = json.loads((records / "249-states.json").read_text())
    frames = json.loads((records / "frames.json").read_text())["frames"]
    return rows, state, frames


def record_legality(rows, state, frames):
    """Exact integer geometry/lifecycle audit, with no owner selection present."""
    n = state["n"]
    frame = {int(k): v for k, v in frames.items()}
    current = [state["initial"][str(i)] for i in range(n)] + [state["ZERO"]]
    opened = None
    containment = {}
    paid = Counter()
    counts = Counter()
    for index, (op, a, b, c, f, z) in enumerate(rows):
        require(0 <= a <= n and (op == 0 or 0 <= b <= n), "record role range")
        counts[op] += 1
        if op == 0:
            require(a != n or opened is not None, "MOVE inactive temporary")
            key = (b, c)
            if key not in containment:
                containment[key] = frame[b]["dim"] <= frame[c]["dim"] and all(
                    sum(x * y for x, y in zip(row, ann)) == 0
                    for row in frame[b]["B"] for ann in frame[c]["A"])
            require(current[a] == b and containment[key] and frame[c]["dim"] - frame[b]["dim"] == f,
                    "illegal/mispriced MOVE at %d" % index)
            current[a] = c
            if f:
                paid[f] += 1
        elif op == 1:
            require(current[a] == current[b] == f and a != b, "ADD common frame or self ADD")
            require(n not in (a, b) or opened is not None, "ADD inactive temporary")
            require(opened is None or a not in (opened, n), "copied source or temporary mutated")
        elif op == 2:
            require(opened is None and b == n and current[a] == c, "COPY lifecycle")
            require(z == frame[c]["dim"], "COPY rank")
            opened = a
            current[n] = f
            paid[z] += 1
        elif op == 3:
            require(opened is not None and a == opened and b == n and current[a] == c and current[n] == f,
                    "ERASE lifecycle")
            opened = None
        else:
            raise ValueError("unknown native opcode")
    require(opened is None and counts[2] == counts[3] == 9, "copy endpoint")
    require(current[:n] == [state["final"][str(i)] for i in range(n)], "native final frames")
    return {"status": "PASS_PYTHON_NATIVE_RECORD_LEGALITY", "records": len(rows),
            "moves": counts[0], "binary_ADDs": counts[1], "copies": counts[2], "erasures": counts[3],
            "paid_histogram": dict(sorted(paid.items())), "rank_mass": sum(k * v for k, v in paid.items()),
            "binary_ADDs_by_phase": dict(sorted(Counter(row[5] for row in rows if row[0] == 1).items())),
            "containment_pairs_checked": len(containment)}


def scalar_stream(rows, n):
    stream = []
    for op, a, b, c, f, z in rows:
        if op == 1:
            stream.append((0, a, b, c))
        elif op == 2:
            stream.append((1, n, a, 0))
        elif op == 3:
            stream.append((2, n, a, 0))
    return stream


def prefix_bounds(stream, n):
    result = []
    for reverse in (False, True):
        values = [1] * (n + 1)
        largest = 1
        opened = False
        for kind, dst, src, coefficient in (reversed(stream) if reverse else stream):
            if reverse and kind:
                kind = 3 - kind
            if kind == 0:
                values[dst] += abs(coefficient) * values[src]
                largest = max(largest, values[dst])
            elif kind == 1:
                require(not opened, "prefix COPY nesting")
                values[n] = values[src]
                opened = True
            else:
                require(opened, "prefix ERASE without COPY")
                values[n] = 0
                opened = False
        require(not opened, "prefix copy closure")
        result.append({"reverse": reverse, "cancellation_free_signed_row_l1_upper": str(largest),
                       "bits": largest.bit_length()})
    forward, backward = [int(item["cancellation_free_signed_row_l1_upper"]) for item in result]
    payload = 64 * forward ** 3 * backward ** 2
    return {"signed_lift_prefix": result, "payload_prefix_upper": str(payload),
            "payload_prefix_bits": payload.bit_length(), "payload_under_2_power_104": payload < 2 ** 104}


def schedule(k):
    stages = 2 * k + 1
    active = []
    reverse = []
    bridges = [[] for _ in range(stages)]
    for stage in range(stages):
        pair = 1 if stage < 3 else (stage + 1) // 2
        backward = stage == 1 or (stage >= 3 and stage % 2 == 1)
        x, y = 2 * (pair - 1), 2 * (pair - 1) + 1
        active.append((y, x) if backward else (x, y))
        reverse.append(backward)
    for pair in range(2, k + 1):
        x, y = 2 * (pair - 1), 2 * (pair - 1) + 1
        bridges[2 * pair - 3].extend(((x - 2, x), (y, y - 2)))
        bridges[2 * pair - 2].extend(((y, y - 2), (x - 2, x)))
    for pair in range(k, 1, -1):
        x, y = 2 * (pair - 1), 2 * (pair - 1) + 1
        bridges[-1].extend(((y - 2, y), (x, x - 2)))
    return active, reverse, bridges


def bridged_replay(stream, state, k):
    """Python-integer bitsets carry every independent input column at once."""
    v, r, n = state["v"], state["R"], state["n"]
    live = 2 * k * v + r
    values = [1 << i for i in range(live)] + [0]
    active, backward, bridges = schedule(k)
    for stage, (xb, yb) in enumerate(active):
        mapping = [xb * v + i for i in range(v)] + [yb * v + i for i in range(v)] + list(range(2 * k * v, live + 1))
        opened = False
        copies = 0
        for kind, dst, src, coefficient in (reversed(stream) if backward[stage] else stream):
            if backward[stage] and kind:
                kind = 3 - kind
            d, s = mapping[dst], mapping[src]
            if kind == 0:
                if coefficient % 2:
                    values[d] ^= values[s]
            elif kind == 1:
                require(not opened, "physical COPY nesting")
                values[live] = values[s]
                opened = True
                copies += 1
            else:
                require(opened, "physical ERASE without COPY")
                values[live] = 0
                opened = False
        require(not opened and copies == 9, "stage COPY count")
        if stage == 0:
            require(all(values[i] == ((1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0))
                        for i in range(live)), "local defining decoder on all physical columns")
        for dst, src in bridges[stage]:
            for i in range(v):
                values[dst * v + i] ^= values[src * v + i]
    for bank in range(0, 2 * k, 2):
        for i in range(v):
            a, b = bank * v + i, (bank + 1) * v + i
            values[a], values[b] = values[b], values[a]
    require(values[live] == 0 and all(values[i] == 1 << i for i in range(live)), "bridged endpoint")
    bridge_count = sum(map(len, bridges))
    controls = []
    for omit in range(bridge_count):
        banks = [1 << i for i in range(2 * k)]
        number = 0
        for stage, (xb, yb) in enumerate(active):
            banks[yb] ^= banks[xb]
            for dst, src in bridges[stage]:
                if number != omit:
                    banks[dst] ^= banks[src]
                number += 1
        for bank in range(0, 2 * k, 2):
            banks[bank], banks[bank + 1] = banks[bank + 1], banks[bank]
        rejected = any(banks[i] != 1 << i for i in range(2 * k))
        require(rejected, "vacuous omitted bridge negative control")
        controls.append({"omit_bridge": omit, "rejected": True})
    return {"status": "PASS_PYTHON_NATIVE_ALL_PHYSICAL_COLUMNS", "stages": 2 * k + 1,
            "formal_columns_checked": live, "bridge_additions": bridge_count * v,
            "fresh_center_copies": (2 * k + 1) * 9, "negative_controls": controls}


def cpp_missing_d_control(out, binaries):
    """Run the unchanged C++ checkers on one malformed native ADD stream."""
    folder = out / "candidate"
    rows = list(struct.iter_unpack("<6i", (folder / "records/249-records.bin").read_bytes()))
    index = next(i for i, row in enumerate(rows) if row[0] == 1 and row[5] == 1)
    mutant = rows[:index] + rows[index + 1:]
    mutant_path = out / "missing-D-ADD.bin"
    mutant_path.write_bytes(b"".join(struct.pack("<6i", *row) for row in mutant))
    cout = out / "missing-D-cout"
    shutil.copytree(folder / "cout", cout, dirs_exist_ok=True)
    shutil.copyfile(mutant_path, cout / "COHORT249-RECORDS.bin")
    require(run_logged([binaries / "legality", folder / "cin", cout, cout / "legality.json"],
                       out / "missing-D-legality.log") == 0, "missing-D control changed native legality")
    rejections = []
    for stages in (5, 9, 11):
        log = out / ("missing-D-columns%d.log" % stages)
        code = run_logged([binaries / ("columns%d" % stages), mutant_path,
                           out / ("missing-D-columns%d.json" % stages)], log)
        require(code != 0 and "local defining-decoder full formal column" in log.read_text(),
                "C++ missing-D control accepted or rejected for wrong reason")
        rejections.append({"stages": stages, "rejected": True, "returncode": code,
                           "reason": "local defining-decoder full formal column"})
    return {"status": "PASS_CPP_MISSING_D_ADD_NEGATIVE_CONTROL", "record_index": index,
            "removed_record": list(rows[index]), "legality_passed": True,
            "native_all_column_rejections": rejections}


def compare_cpp_python(receipts, python_reports):
    for name, cpp in receipts.items():
        py = python_reports[name]
        legality = py["legality"]
        hist = {int(k): value for k, value in legality["paid_histogram"].items()}
        for cpp_key, py_key in (("records", "records"), ("common_frame_ADDs", "binary_ADDs"),
                               ("nested_MOVEs", "moves"), ("copies", "copies"),
                               ("erasures", "erasures"), ("rank_mass", "rank_mass")):
            require(cpp["legality"][cpp_key] == legality[py_key], "C++/Python legality mismatch")
        require(dict(cpp["legality"]["paid_histogram"]) == hist, "C++/Python paid histogram mismatch")
        for stage, physical in zip((5, 9, 11), py["physical_columns"]):
            receipt = cpp["columns%d" % stage]
            for key in ("signed_lift_prefix", "payload_prefix_upper", "payload_prefix_bits"):
                require(receipt[key] == py["prefix"][key], "C++/Python exact prefix mismatch")
            require(receipt["local_scalar_additions"] == legality["binary_ADDs"], "C++/Python ADD mismatch")
            require(dict(receipt["local_raw_H"]) == hist, "C++/Python column profile mismatch")
            for key in ("formal_columns_checked", "bridge_additions", "fresh_center_copies", "negative_controls"):
                require(receipt[key] == physical[key], "C++/Python physical column receipt mismatch")
    return {"status": "PASS_CPP_PYTHON_EXACT_RECEIPT_COMPARISON", "datasets": sorted(receipts),
            "checks": ["legality counts", "paid histogram and rank mass", "binary ADD counts",
                       "exact forward and reverse prefix bounds", "payload and bit lengths",
                       "5/9/11 column counts and omitted-bridge controls"]}


def cpp_checks(out, datasets, boost_include, cxx, python_reports=None):
    compiler = shutil.which(cxx)
    paths = ([Path(boost_include)] if boost_include else []) + [
        Path(os.environ.get("BOOST_INCLUDE", "/usr/include")),
        Path("/opt/homebrew/include"), Path("/usr/local/include")]
    boost = next((p for p in paths if (p / "boost/multiprecision/cpp_int.hpp").is_file()), None)
    availability = {"compiler_available": compiler is not None, "boost_headers_available": boost is not None}
    if compiler is None or boost is None:
        availability["status"] = ("NOT_RUN_MISSING_COMPILER_AND_BOOST_HEADERS" if compiler is None and boost is None
                                  else "NOT_RUN_MISSING_COMPILER" if compiler is None
                                  else "NOT_RUN_MISSING_BOOST_HEADERS")
        return availability
    binaries = out / "bin"
    binaries.mkdir(exist_ok=True)
    checks = BIT / "checkers"
    common = [compiler, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=420",
              "-I" + str(SKELETON / "portable-include"), "-I" + str(checks), "-I" + str(boost)]
    builds = [("legality", "legality_h.cpp", []), ("columns5", "columns_h.cpp", []),
              ("columns9", "columns_k.cpp", ["-DKPAIRS=4"]),
              ("columns11", "columns_k.cpp", ["-DKPAIRS=5"])]
    for name, source, options in builds:
        require(run_logged(common + options + ["-o", binaries / name, checks / source],
                           out / (name + "-compile.log")) == 0, "C++ compilation failed: " + name)
    result = {}
    for name in datasets:
        folder = out / name
        require(run_logged([sys.executable, "-I", "-B", BIT / "regression/stage_cohort.py",
                            folder / "records", folder / "records", folder / "cin", folder / "cout"],
                           folder / "stage.log") == 0, "cohort staging failed")
        result[name] = {}
        for binary, _, _ in builds:
            receipt = folder / (binary + ".json")
            args = [folder / "cin", folder / "cout", receipt] if binary == "legality" else [
                folder / "cout/COHORT249-RECORDS.bin", receipt]
            require(run_logged([binaries / binary] + args, folder / (binary + ".log")) == 0,
                    "official C++ checker failed: " + name + "/" + binary)
            result[name][binary] = {key: value for key, value in json.loads(receipt.read_text()).items()
                                    if key not in ("seconds", "local_scalar_stream")}
    negative = cpp_missing_d_control(out, binaries)
    comparison = compare_cpp_python(result, python_reports) if python_reports is not None else None
    return dict(availability, status="PASS_UNCHANGED_CPP_5_9_11_STAGE_CHECKERS", receipts=result,
                missing_D_negative_control=negative, python_receipt_comparison=comparison)


def missing_d_control(rows, state, frames, out):
    index = next(i for i, row in enumerate(rows) if row[0] == 1 and row[5] == 1)
    mutant = rows[:index] + rows[index + 1:]
    (out / "missing-D-ADD.bin").write_bytes(b"".join(struct.pack("<6i", *row) for row in mutant))
    legality = record_legality(mutant, state, frames)
    stream = scalar_stream(mutant, state["n"])
    rejections = []
    for k in (2, 4, 5):
        try:
            bridged_replay(stream, state, k)
        except ValueError as error:
            require(str(error) == "local defining decoder on all physical columns", "wrong mutation rejection")
            rejections.append({"stages": 2 * k + 1, "rejected": True, "reason": str(error)})
        else:
            raise ValueError("missing-D ADD corruption accepted at %d stages" % (2 * k + 1))
    return {"status": "PASS_MISSING_D_ADD_NEGATIVE_CONTROL", "record_index": index,
            "removed_record": list(rows[index]), "legality_status": legality["status"],
            "native_all_column_rejections": rejections}


def run(candidate_path, out, baseline=BASELINE, boost_include=None, cxx="c++"):
    """Write native audit artifacts to out and return the path-free result dict."""
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    result = {"status": "IN_PROGRESS", "exporter_sha256": digest((BIT / "export_records.py").read_bytes()),
              "upstream_columns_k_sha256": digest((BIT / "checkers/columns_k.cpp").read_bytes()),
              "python_replay_provenance": "Python port of the upstream columns_k schedule and prefix formula; not an official C++ run or an independent theorem proof.",
              "scope": "Finite native geometry, paid paths, ADD counts, exact F2 columns and positive prefix bounds. No new price or kappa."}
    datasets = {}
    for name, word in (("baseline", Path(baseline)), ("candidate", Path(candidate_path))):
        rows, state, frames = export(word.resolve(), out / name)
        datasets[name] = (rows, state, frames)
        stream = scalar_stream(rows, state["n"])
        result[name] = {"input_sha256": digest(word.read_bytes()), "legality": record_legality(rows, state, frames),
                        "prefix": prefix_bounds(stream, state["n"]),
                        "physical_columns": [bridged_replay(stream, state, k) for k in (2, 4, 5)]}
        require(result[name]["prefix"]["payload_under_2_power_104"], "positive prefix exceeds inherited cutoff")
    base, candidate = datasets["baseline"], datasets["candidate"]
    paths = [[row for row in data[0] if row[0] != 1] for data in (base, candidate)]
    require(paths[0] == paths[1], "MOVE/COPY/ERASE paths changed")
    for filename in ("frames.json", "249-states.json"):
        require((out / "baseline/records" / filename).read_bytes() ==
                (out / "candidate/records" / filename).read_bytes(), filename + " changed")
    bleg, cleg = [result[name]["legality"] for name in ("baseline", "candidate")]
    require(bleg["paid_histogram"] == cleg["paid_histogram"] and bleg["rank_mass"] == cleg["rank_mass"],
            "paid profile changed")
    result["comparison"] = {"exact_MOVE_COPY_ERASE_paths_equal": True, "frames_bytes_equal": True,
                            "states_bytes_equal": True, "paid_histogram_equal": True,
                            "paid_rank_mass_equal": True, "non_ADD_records": len(paths[0]),
                            "non_ADD_stream_sha256": digest(b"".join(struct.pack("<6i", *row) for row in paths[0])),
                            "binary_ADDs_saved": bleg["binary_ADDs"] - cleg["binary_ADDs"]}
    result["native_missing_D_negative_control"] = missing_d_control(*candidate, out)
    result["official_cpp"] = cpp_checks(out, datasets, boost_include, cxx, result)
    result["status"] = "PASS_NATIVE_PYTHON_AUDIT"
    write_json(out / "RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", type=Path, default=HERE / "output/candidate.json")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--out", type=Path, default=HERE / "output/native")
    parser.add_argument("--boost-include")
    parser.add_argument("--cxx", default=os.environ.get("CXX", "c++"))
    args = parser.parse_args()
    result = run(args.candidate, args.out, args.baseline, args.boost_include, args.cxx)
    print(json.dumps({"status": result["status"], "comparison": result["comparison"],
                      "official_cpp": result["official_cpp"]["status"],
                      "receipt": str(args.out.resolve() / "RESULT.json")}, indent=2))


if __name__ == "__main__":
    main()

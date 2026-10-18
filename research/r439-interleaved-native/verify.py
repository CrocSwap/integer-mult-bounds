#!/usr/bin/env python3
"""Source-bound replay of Ross Richardson's PR2407, without changing its engines.

Native staging/build adapted from Gareth Davidson's PR2373/980/926 harness,
following Sagar Thakrar's PR837 and Sricharan Vagvala's PR967 harnesses.
Prepared for starship-s with substantial OpenAI Codex assistance. Apache-2.0.

Default: compare REPLAY.json (Python evidence only). --native also builds the
unchanged C++17 engines (g++ and Boost headers via BOOST_INCLUDE) and compares
NATIVE.json. --write explicitly replaces the requested receipts after success.
Temporary files follow tempfile defaults, including TMPDIR when set.
Each subprocess has a bounded process group.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import resource
import runpy
import shlex
import signal
import struct
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HUB = "research/e8-bit-carrier-skeleton"
PARENT = "research/r439-single-copy-interleaving"
HEAD = "4944211cee666eb8631b990cb0f33cfa68666485"
INPUTS = {
    HUB + "/" + name for name in (
        "LICENSE", "NOTICE.md", "code/bit/export_records.py",
        "code/bit/regression/stage_cohort.py", "portable-include/bits/stdc++.h",
        "code/bit/checkers/legality_h.cpp", "code/bit/checkers/columns_k.cpp",
        "code/bit/checkers/json.hpp")
} | {"research/e8-bit-p111-tuned/code/xcheck_p.py",
     "research/r439-bsection-stars-seed01/candidate.json.gz"}
PYTHON = [sys.executable, "-I", "-B"]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def same(actual, expected, message):
    need(canonical(actual) == canonical(expected), message)


def execute(args, *, cwd=None, timeout=120, failure=None):
    args = [str(x) for x in args]
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    with subprocess.Popen(args, cwd=cwd, env=env, start_new_session=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except BaseException:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            raise
    if failure is None:
        need(proc.returncode == 0, f"command failed ({proc.returncode}): {args}\n"
             + stderr.decode(errors="replace") + stdout.decode(errors="replace"))
        return stdout
    need(proc.returncode != 0 and failure in stderr.decode(errors="replace"),
         f"wrong native rejection: {args}\n{stderr!r}")
    return {"returncode": proc.returncode, "diagnostic": failure}


def check_pin(raw, pin):
    need(sha(raw) == pin["sha256"], "source SHA256 mismatch: " + pin["path"])
    need(hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == pin["git_blob"],
         "source Git blob mismatch: " + pin["path"])


def safe_path(name):
    path = PurePosixPath(name)
    need(not path.is_absolute() and ".." not in path.parts and str(path) == name,
         "noncanonical source path: " + name)
    return name


def stage_sources(root):
    """Validate the entire inventory before any archived executable is loaded."""
    sources, predecessor = load(HERE / "SOURCES.json"), load(HERE / "PREDECESSOR.json")
    need(predecessor["head"] == HEAD and predecessor["pr"] == 2407, "PR2407 head")
    blobs = {}
    for pin in sources["files"]:
        path = safe_path(pin["path"])
        need(path not in blobs, "duplicate source path")
        if pin["usage"] == "input":
            raw = (ROOT / path).read_bytes()
        else:
            need(pin["usage"] == "provenance", "unsupported source usage")
            raw = execute(["git", "show", sources["base_commit"] + ":" + path], cwd=ROOT)
        check_pin(raw, pin)
        blobs[path] = raw
    need({p["path"] for p in sources["files"] if p["usage"] == "input"} == INPUTS,
         "complete native input inventory")
    archive = (HERE / safe_path(predecessor["archive"])).read_bytes()
    need(sha(archive) == predecessor["sha256"], "source archive SHA256 mismatch")
    pins = {pin["path"]: pin for pin in predecessor["members"]}
    need(len(pins) == len(predecessor["members"]) == 4 and set(pins) == {
        PARENT + "/" + name for name in ("verify.py", "SOURCES.json", "RESULT.json", "WITNESS.json")},
        "complete predecessor inventory")
    archived = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar.getmembers():
            path = safe_path(member.name)
            if member.isdir():
                need(any(p.startswith(path + "/") for p in pins), "unexpected archive directory")
                continue
            need(member.isfile() and path in pins and path not in archived,
                 "unsupported or duplicate archive member: " + path)
            raw = tar.extractfile(member).read()
            check_pin(raw, pins[path])
            archived[path] = raw
    need(set(archived) == set(pins), "missing archive member")
    parent_sources = json.loads(archived[PARENT + "/SOURCES.json"])
    same(parent_sources["base_commit"], sources["base_commit"], "predecessor base")
    for pin in parent_sources["files"]:
        need(pin in sources["files"], "unpinned predecessor input: " + pin["path"])
    for path, raw in {**blobs, **archived}.items():
        dest = root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    return {"pr2407_head": HEAD, "archive_sha256": sha(archive),
            "sources_sha256": sha((HERE / "SOURCES.json").read_bytes()),
            "predecessor_sha256": sha((HERE / "PREDECESSOR.json").read_bytes()),
            "consumed_sha256": {path: sha(raw) for path, raw in sorted({**blobs, **archived}.items())}}


def packed(rows):
    return b"".join(struct.pack("<6i", *row) for row in rows)


def record_binding(raw, expected):
    need(sha(raw) == expected, "full RAW6 record binding mismatch")


def rejects(fn, fragment):
    try:
        fn()
    except ValueError as exc:
        need(fragment in str(exc), "unexpected rejection: " + str(exc))
        return str(exc)
    raise ValueError("failure control accepted: " + fragment)


def mutations(rows, w, witness):
    center = w["ret"][witness["column"]]
    opening = next(i for i, r in enumerate(rows) if r[0] == 2 and r[1] == center)
    closing = next(i for i in range(opening + 1, len(rows)) if rows[i][0] == 3)
    undo = [i for i in range(opening + 1, closing) if rows[i][0] == 1 and rows[i][5] == 4]
    taps = [i for i in range(opening + 1, closing) if rows[i][0] == 1 and rows[i][5] == 3]
    need(len(undo) == 303 and len(taps) == 10 and closing - opening == 314,
         "column-0 COPY window")
    cuts = [[sum(u < t for u in undo), rows[t][1] - w["v"]] for t in taps]
    same(cuts, witness["taps"], "exact chronological tap cuts")
    last = next(t for t in reversed(taps) if any(u < t for u in undo))
    reordered = rows.copy()
    reordered.insert(opening + 1, reordered.pop(last))
    missing = rows[:undo[0]] + rows[undo[0] + 1:]
    erased = rows.copy()
    erased.insert(opening + 1, erased.pop(closing))
    relabeled = rows.copy()
    a, b = taps[0], undo[0]
    relabeled[a] = rows[a][:5] + (rows[b][5],)
    relabeled[b] = rows[b][:5] + (rows[a][5],)
    for name, changed in (("reorder", reordered), ("phase exchange", relabeled)):
        same(sorted(Counter((r[0], r[5]) for r in changed).items()),
             sorted(Counter((r[0], r[5]) for r in rows).items()), name + " opcode/phase counts")
        same([r for r in changed if r[0] != 1], [r for r in rows if r[0] != 1],
             name + " ordered MOVE/COPY/ERASE profile")
        same([[i, r] for i, r in enumerate(changed) if r[0] in (2, 3)],
             [[i, r] for i, r in enumerate(rows) if r[0] in (2, 3)], name + " COPY lifetime")
    same([r[:5] for r in relabeled], [r[:5] for r in rows], "phase-only exchange")
    return {"reordered_tap": reordered, "missing_undo": missing,
            "premature_erase": erased, "phase_exchange": relabeled}, {
        "opening_record": opening, "closing_record": closing, "copied_source": center,
        "temporary": rows[opening][2], "target_only_undo_ADDs": len(undo), "taps": cuts,
        "reordered_record": last, "reordered_cut": cuts[-1][0],
        "missing_undo_record": undo[0], "phase_exchange_records": [a, b]}


def stage(root, folder, raw, metadata):
    records, cin, cout = (folder / name for name in ("records", "cin", "cout"))
    records.mkdir(parents=True)
    (records / "249-records.bin").write_bytes(raw)
    for name, data in metadata.items():
        (records / name).write_bytes(data)
    execute(PYTHON + [root / HUB / "code/bit/regression/stage_cohort.py", records, records, cin, cout])
    need((cout / "COHORT249-RECORDS.bin").read_bytes() == raw, "native staging changed RAW6")
    states, frames = (json.loads(metadata[n]) for n in ("249-states.json", "frames.json"))
    expected = {
        "cin/249-states.json": states, "cin/frames.json": frames,
        "cin/249-DONOR-OWNERSHIP.json": {"donor_keys": []},
        "cout/COHORT249-INITIAL.json": states["initial"],
        "cout/COHORT249-FRAMES.json": {}, "cout/COHORT249-SELECTION.json": []}
    for path, value in expected.items():
        same(load(folder / path), value, "staged metadata: " + path)
    return {"record_sha256": sha(raw), "records": len(raw) // 24,
            "exported_metadata_sha256": {n: sha(canonical(json.loads(b))) for n, b in metadata.items()},
            "staged_metadata_sha256": {n: sha(canonical(load(folder / n))) for n in expected}}


def replay(root):
    bindings = stage_sources(root)
    predecessor = root / PARENT / "verify.py"
    # Execute its original CLI, including all inherited controls, before using its stream.
    execute(PYTHON + [predecessor, "--output", root / "original-replay"], cwd=root)
    expected = load(root / PARENT / "RESULT.json")
    same(load(root / "original-replay/RESULT.json"), expected, "pinned predecessor RESULT")
    p = runpy.run_path(str(predecessor))
    data = p["inputs"]()
    w = json.loads(gzip.decompress(data[p["WORD"]]))
    witness = load(root / PARENT / "WITNESS.json")
    split, rest, P, algebra = p["decompose"](w, witness)
    same(algebra, expected["algebra"], "predecessor algebra")
    fixed, frames = p["export"](split, data, root / "split-export")
    same(frames, load(root / "original-replay/frames.json"), "complete exported frames")
    candidate = p["interleave"](fixed, w, rest, P, witness)
    need(packed(candidate) == (root / "original-replay/records.bin").read_bytes(),
         "candidate differs from original verifier output")
    metadata = {name: (root / "split-export/out" / name).read_bytes()
                for name in ("249-states.json", "frames.json")}
    cases = {"split94": fixed, "interleaved88": candidate}
    schedules = {}
    for name, rows in cases.items():
        record_binding(packed(rows), expected["schedules"][name]["record_sha256"])
        p["boundary"](rows, w)
        p["boundary"](rows, w, True)
        schedules[name] = p["invoice"](rows, w, frames)
        same(schedules[name], expected["schedules"][name], "complete finite invoice: " + name)
    same([r for r in fixed if r[0] == 0], [r for r in candidate if r[0] == 0], "ordered MOVEs")
    bad, window = mutations(candidate, w, witness)
    controls = {}
    for name, rows in bad.items():
        controls[name] = {"full_record_binding": rejects(
            lambda: record_binding(packed(rows), schedules["interleaved88"]["record_sha256"]),
            "full RAW6 record binding mismatch")}
        if name == "phase_exchange":
            p["boundary"](rows, w)
            p["boundary"](rows, w, True)
            bill = p["invoice"](rows, w, frames)
            same({k: v for k, v in bill.items() if k != "record_sha256"},
                 {k: v for k, v in schedules["interleaved88"].items() if k != "record_sha256"},
                 "phase exchange finite invoice")
            controls[name]["python_boundary"] = "passes both orientations; labels are not semantics"
        else:
            controls[name]["python_boundary"] = rejects(lambda: p["boundary"](rows, w), "dirty boundary")
    cases.update(bad)
    stages = {name: stage(root, root / name, packed(rows), metadata) for name, rows in cases.items()}
    report = {"status": "PASS_R439_INTERLEAVED_PYTHON_REPLAY", "native_checks_executed": False,
              "bindings": bindings, "predecessor_result": expected, "schedules": schedules,
              "column0_window": window, "staging": stages, "controls": controls,
              "coverage": "Full RAW6 and metadata binding; inherited finite boundary/invoice in both orientations. Not native or supplier evidence."}
    return report


def native(root, replay_report):
    checker = root / HUB / "code/bit/checkers"
    build = root / "build"
    build.mkdir()
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9"]
    compiler = shlex.split(os.environ.get("CXX", "g++"))
    includes = ["-I" + str(root / HUB / "portable-include"), "-I" + str(checker),
                "-I" + os.environ.get("BOOST_INCLUDE", "/usr/include")]
    print("Compiling unchanged native legality and k=2,4,5 columns engines", flush=True)
    execute(compiler + flags + includes + ["-o", build / "legality", checker / "legality_h.cpp"], timeout=180)
    for k in (2, 4, 5):
        execute(compiler + flags + includes + ["-DVPORTS=111", "-DRHELP=439", f"-DKPAIRS={k}",
                "-o", build / f"columns-{k}", checker / "columns_k.cpp"], timeout=180)
    results = {}
    for name, binding in replay_report["staging"].items():
        print("Native replay:", name, flush=True)
        folder = root / name
        cin, cout = folder / "cin", folder / "cout"
        raw = cout / "COHORT249-RECORDS.bin"
        record_binding(raw.read_bytes(), binding["record_sha256"])
        args = [build / "legality", cin, cout, cout / "legality.json"]
        if name == "premature_erase":
            legality = execute(args, failure="ADD inactive temporary")
        else:
            execute(args)
            legality = load(cout / "legality.json")
            need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
                 "native legality status")
        columns = {}
        for k in (2, 4, 5):
            args = [build / f"columns-{k}", raw, cout / f"columns-{k}.json"]
            if name in ("reordered_tap", "missing_undo", "premature_erase"):
                diagnostic = ("temp not open" if name == "premature_erase"
                              else "local defining-decoder full formal column")
                columns[str(k)] = execute(args, failure=diagnostic)
                continue
            execute(args)
            col = load(cout / f"columns-{k}.json")
            need(col.pop("local_scalar_stream") == str(raw), "native consumed stream path")
            col.pop("seconds")  # Only location and elapsed time are excluded from exact comparison.
            col["local_scalar_stream_sha256"] = binding["record_sha256"]
            bill = replay_report["schedules"]["split94" if name == "split94" else "interleaved88"]
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if k == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            need(col["status"] == expected_status, "native column status")
            need(col["formal_columns_checked"] == 2 * k * 111 + 439
                 and len(col["stages"]) == 2 * k + 1, "native column/stage coverage")
            need(col["bridge_additions"] == 6 * (k - 1) * 111
                 and col["fresh_center_copies"] == 9 * (2 * k + 1)
                 and col["reverse_fresh_center_copies"] == 9 * k, "native bridge/COPY bill")
            key = "five_stage_additions" if k == 2 else "stage_additions"
            need(col[key] == (2 * k + 1) * bill["ADDs"]
                 and col["local_scalar_additions"] == legality["common_frame_ADDs"] == bill["ADDs"],
                 "native scalar ADD bill")
            same([int(x["cancellation_free_signed_row_l1_upper"]) for x in col["signed_lift_prefix"]],
                 [bill["F"], bill["B"]], "native signed positive envelopes")
            need(col["payload_prefix_bits"] == bill["local_bits"] <= 104
                 and int(col["payload_prefix_upper"]) == 64 * bill["F"] ** 3 * bill["B"] ** 2,
                 "native exact local precision bill")
            same(col["negative_controls"], [{"omit_bridge": i, "rejected": True} for i in range(6 * (k - 1))],
                 "every inherited omitted-bridge control")
            columns[str(k)] = col
        results[name] = {"record_sha256": binding["record_sha256"], "legality": legality, "columns": columns}
    for name in ("split94", "interleaved88"):
        leg, bill = results[name]["legality"], replay_report["schedules"][name]
        need(leg["records"] == replay_report["staging"][name]["records"]
             and leg["nested_MOVEs"] == bill["MOVEs"] and leg["rank_mass"] == bill["paid_rank_mass"]
             and leg["copies"] == leg["erasures"] == 9, "native lifetime/paid profile")
        same(dict(leg["paid_histogram"]), {int(k): v for k, v in bill["paid_profile"].items()}, "native ranks")
    same(results["phase_exchange"]["legality"], results["interleaved88"]["legality"], "native ignores phases: legality")
    for k in ("2", "4", "5"):
        same({a: b for a, b in results["phase_exchange"]["columns"][k].items() if a != "local_scalar_stream_sha256"},
             {a: b for a, b in results["interleaved88"]["columns"][k].items() if a != "local_scalar_stream_sha256"},
             "native ignores phases: columns")
    return {"status": "PASS_R439_INTERLEAVED_NATIVE", "replay_sha256": sha(canonical(replay_report)),
            "compile_flags": flags, "column_defines": {"VPORTS": 111, "RHELP": 439, "KPAIRS": [2, 4, 5]},
            "results": results,
            "coverage_boundary": "Phase-label exchange passes unchanged native engines; full expected RAW6 binding rejects it. Finite evidence only; no supplier admission."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--native", action="store_true")
    ap.add_argument("--write", action="store_true", help="explicitly replace REPLAY.json and, with --native, NATIVE.json")
    args = ap.parse_args()
    # Expected uncaught C++ lifetime rejection must not leave a core dump.
    resource.setrlimit(resource.RLIMIT_CORE, (0, resource.getrlimit(resource.RLIMIT_CORE)[1]))
    expected = {} if args.write else {"REPLAY.json": load(HERE / "REPLAY.json")}
    if args.native and not args.write:
        expected["NATIVE.json"] = load(HERE / "NATIVE.json")
    with tempfile.TemporaryDirectory(prefix="r439-native-") as tmp:
        root = Path(tmp)
        report = replay(root)
        reports = {"REPLAY.json": report}
        if not args.write:
            same(report, expected["REPLAY.json"], "REPLAY.json receipt mismatch")
        if args.native:
            reports["NATIVE.json"] = native(root, report)
        for name, result in reports.items():
            if args.write:
                (HERE / name).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
            else:
                same(result, expected[name], name + " receipt mismatch")
    print("PASS_R439_INTERLEAVED_" + ("NATIVE" if args.native else "PYTHON_ONLY")
          + " split94=11067 interleaved88=11061 controls=4 "
          + ("receipts_written" if args.write else "receipts_match"), flush=True)


if __name__ == "__main__":
    main()

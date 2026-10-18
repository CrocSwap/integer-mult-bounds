#!/usr/bin/env python3
"""Exact PR2115 phase transfer and opt-in native replay.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. Predecessor construction and reused checkers are credited in README.
"""
import argparse
import copy
import hashlib
import os
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
HERE, ROOT = C["HERE"], C["ROOT"]
need, same, load, write, digest = (C[k] for k in ("need", "same", "load", "write", "digest"))
L = runpy.run_path(str(HERE / "literal.py"))
BASE_WORD = "research/r439-gl5-shortest/candidate.json.gz"
CANDIDATE = HERE / "vendor/pr2115/candidate-1188.json.gz"
PROFILE = {"1": 1323, "2": 1342, "3": 79, "4": 44, "5": 102, "6": 11, "7": 19}


def phase_bill(word):
    return {str(i + 1): sum(map(len, word[phase])) if phase == "scatter"
            else sum(len(g[2]) for g in word[phase])
            for i, phase in enumerate(("D", "A", "scatter", "B", "C"))}


def rebuild(base):
    """Reconstruct the exact full deferral; do not import PR2115's generator."""
    v = base["v"]
    runs = []
    for i, gate in enumerate(base["D"]):
        frame, dst, srcs = gate
        need(frame == 0, "D zero frame")
        ty = "yy" if v <= dst < 2*v and all(v <= s < 2*v for s in srcs) else "other"
        if not runs or runs[-1][0] != ty:
            runs.append([ty, []])
        runs[-1][1].append(i)
    same([(t, len(indices)) for t, indices in runs],
         [("other", 236), ("yy", 306), ("other", 111), ("yy", 306), ("other", 236)],
         "pinned D block pattern")
    prep = [base["D"][i] for i in runs[1][1]]
    undo = [base["D"][i] for i in runs[3][1]]
    same(undo, list(reversed(prep)), "literal target undo")
    rows = [set(r) for r in base["scatter"]]
    for _, dst, srcs in prep:
        for src in srcs:
            rows[dst-v].symmetric_difference_update(rows[src-v])
    result = copy.deepcopy(base)
    removed = set(runs[3][1])
    result["D"] = [g for i, g in enumerate(base["D"]) if i not in removed]
    result["B"] = copy.deepcopy(undo + base["B"])
    result["scatter"] = [sorted(row) for row in rows]
    return result, undo


def rejected(action, label, expected=None):
    try:
        action()
    except ValueError as exc:
        if expected is not None:
            need(expected in str(exc), label + ": wrong failure: " + str(exc))
        return label
    raise ValueError("control accepted: " + label)


def finite():
    sources = C["pins"]()
    base, candidate = load(ROOT / BASE_WORD), load(CANDIDATE)
    rebuilt, undo = rebuild(base)
    same(rebuilt, candidate, "complete reconstructed candidate payload")
    prices = {label: L["literal_price"](word) for label, word in (("0", base), ("1", candidate))}
    for price in prices.values():
        L["require_admission"](price)
    same([prices[k]["ADDs"] for k in ("0", "1")], [10492, 10062], "complete ADDs")
    same([prices[k]["F"] for k in ("0", "1")], [13667, 13667], "F")
    same([prices[k]["B"] for k in ("0", "1")], [3758418, 2825146], "B")
    old, new = phase_bill(base), phase_bill(candidate)
    same({k: new[k]-old[k] for k in old}, {"1": -306, "2": 0, "3": -430, "4": 306, "5": 0},
         "phase transfer invoice")
    owner = runpy.run_path(str(ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"))
    flags = {}
    for key, word in (("0", base), ("1", candidate)):
        _, _, fl, h, c, _ = owner["check"](word)
        flags[key] = sorted(k for k, v in dict(h, **c).items() if not v)
        need(fl["columns"] == 661, "owner column domain")
    same(flags["0"], ["H2_D_frame0_targets_from_helpers", "K_equals_D"], "baseline flags")
    same(flags["1"], ["H2_D_frame0_targets_from_helpers", "H5_V_identity", "K_equals_D"], "deferred flags")
    controls = []
    dropped = copy.deepcopy(candidate)
    del dropped["B"][0]
    controls.append(rejected(lambda: L["execute"](dropped), "missing undo gate", "dirty full-word boundary"))
    wrong = copy.deepcopy(candidate)
    wrong["scatter"] = copy.deepcopy(base["scatter"])
    controls.append(rejected(lambda: L["execute"](wrong), "old scatter", "dirty full-word boundary"))
    reversed_undo = copy.deepcopy(candidate)
    reversed_undo["B"][:306] = list(reversed(undo))
    controls.append(rejected(lambda: L["execute"](reversed_undo), "wrong undo order", "dirty full-word boundary"))
    late = copy.deepcopy(candidate)
    late["B"] = [candidate["B"][306]] + undo + candidate["B"][307:]
    try:
        owner["check"](late)
    except owner["Reject"] as exc:
        need("climb" in str(exc), "late undo wrong failure")
        controls.append("undo after first target climb")
    else:
        raise ValueError("late undo accepted by frame checker")
    C["pins"]()
    result = dict(status="PASS_R439_DEFERRED_FINITE", payloads={"0": digest(base), "1": digest(candidate)},
                  prices=prices, phase_ADDs={"0": old, "1": new}, undo_gates=len(undo),
                  all_dirty_columns=661, directions=2, owner_false=flags, controls=controls,
                  sources=sources, new_kappa_claim=False)
    return result, {"0": base, "1": candidate}


def records(path):
    raw = path.read_bytes()
    need(len(raw) % 24 == 0, "record alignment")
    return list(struct.iter_unpack("<6i", raw))


def phase_binding(rows, expected):
    observed = {str(i): 0 for i in range(1, 6)}
    for row in rows:
        if row[0] == 1:
            need(str(row[5]) in observed, "unknown ADD phase")
            observed[str(row[5])] += 1
    same(observed, expected, "exported ADD phases")
    return observed


def record_binding(rows, expected_sha256):
    raw = b"".join(struct.pack("<6i", *row) for row in rows)
    actual = hashlib.sha256(raw).hexdigest()
    same(actual, expected_sha256, "complete exported record binding")
    return actual


def full(finite_result, words, output):
    output.mkdir(parents=True, exist_ok=False)
    inputs = output / "words"
    inputs.mkdir()
    for label, word in words.items():
        write(inputs / (label + ".json.gz"), word)
    N = runpy.run_path(str(HERE / "native.py"))
    native = output / "native"
    report = N["run"](ROOT, inputs, finite_result["prices"], native)
    # Neither unchanged C++ engine uses the ADD phase label in its semantic
    # calculation. Bind phases separately; do not infer an H5 theorem.
    phase_reports, record_hashes = {}, {}
    expected_records = load(HERE / "vendor/pr2115/EXPECTED.json")["census"]["PR1188"]["exporter"]
    for label in ("0", "1"):
        rows = records(native / label / "records/249-records.bin")
        phase_reports[label] = phase_binding(rows, finite_result["phase_ADDs"][label])
        record_hashes[label] = record_binding(rows, expected_records["base" if label == "0" else "deferred"]["record_sha256"])
        same(dict(report[label]["paid_histogram"]), {int(k): v for k, v in PROFILE.items()}, "native profile")
        need(report[label]["rank_mass"] == 5129, "native rank mass")
    control_root = output / "controls"
    control_root.mkdir()
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    results = []

    def execute(args, log, expect=None):
        with log.open("x") as stream:
            done = subprocess.run([str(x) for x in args], stdout=stream, stderr=subprocess.STDOUT, env=env)
        text = log.read_text()
        if expect:
            need(done.returncode != 0 and expect in text, "native control failed for wrong reason: " + str(log))
        else:
            need(done.returncode == 0, "native positive failed: " + str(log))
        return done.returncode

    hub = ROOT / C["HUB"]
    for name in ("missing-undo", "old-scatter", "late-undo"):
        word = copy.deepcopy(words["1"])
        if name == "missing-undo":
            del word["B"][0]
        elif name == "old-scatter":
            word["scatter"] = copy.deepcopy(words["0"]["scatter"])
        else:
            word["B"] = [word["B"][306]] + word["B"][:306] + word["B"][307:]
        folder = control_root / name
        folder.mkdir()
        path = folder / "word.json.gz"
        write(path, word)
        lowered, cin, cout = (folder / x for x in ("records", "cin", "cout"))
        execute([sys.executable, "-I", "-B", hub / "code/bit/export_records.py", path, lowered], folder / "export.log")
        execute([sys.executable, "-I", "-B", hub / "code/bit/regression/stage_cohort.py", lowered, lowered, cin, cout],
                folder / "stage.log")
        if name == "late-undo":
            rc = execute([native / "legality", cin, cout, folder / "legality.json"], folder / "reject.log",
                         "illegal or mispriced MOVE")
            reason = "illegal or mispriced MOVE"
        else:
            reason = "local defining-decoder full formal column"
            rc = execute([native / "columns-4", cout / "COHORT249-RECORDS.bin", folder / "columns.json"],
                         folder / "reject.log", reason)
        results.append(dict(control=name, rejected=True, reason=reason, returncode=rc))

    # Both native mathematical engines accept changing only 306 phase labels.
    # The explicit phase binding must reject it. This names their coverage limit.
    folder = control_root / "phase-label-only"
    folder.mkdir()
    rows = records(native / "1/cout/COHORT249-RECORDS.bin")
    seen = 0
    changed = []
    for row in rows:
        if row[0] == 1 and row[5] == 4 and seen < 306:
            row = row[:5] + (1,)
            seen += 1
        changed.append(row)
    need(seen == 306, "phase-only mutation count")
    source = native / "1/cout"
    for path in source.iterdir():
        if path.name.startswith("COHORT249-"):
            (folder / path.name).write_bytes(path.read_bytes())
    raw = folder / "COHORT249-RECORDS.bin"
    raw.write_bytes(b"".join(struct.pack("<6i", *r) for r in changed))
    execute([native / "legality", native / "1/cin", folder, folder / "legality.json"], folder / "legality.log")
    execute([native / "columns-4", raw, folder / "columns.json"], folder / "columns.log")
    rejected(lambda: phase_binding(changed, finite_result["phase_ADDs"]["1"]), "phase-only relabel", "exported ADD phases")
    rejected(lambda: record_binding(changed, record_hashes["1"]), "phase-only trace", "complete exported record binding")
    results.append(dict(control="phase-label-only", native_engines_accept=True, phase_binding_rejects=True, labels_changed=seen))
    # Even preserving all phase counts does not establish the literal trace.
    changed = list(rows)
    first = next(i for i, r in enumerate(rows) if r[0] == 1 and r[5] == 1)
    fourth = next(i for i, r in enumerate(rows) if r[0] == 1 and r[5] == 4)
    changed[first] = rows[first][:5] + (4,)
    changed[fourth] = rows[fourth][:5] + (1,)
    phase_binding(changed, finite_result["phase_ADDs"]["1"])
    rejected(lambda: record_binding(changed, record_hashes["1"]), "count-preserving phase exchange",
             "complete exported record binding")
    results.append(dict(control="count-preserving-phase-exchange", phase_counts_accept=True, record_binding_rejects=True))
    C["pins"]()
    result = dict(status="PASS_R439_DEFERRED_NATIVE", finite_payloads=finite_result["payloads"],
                  finite_result_sha256=digest(finite_result), native=report,
                  exported_phase_ADDs=phase_reports, record_sha256=record_hashes, native_controls=results,
                  native_omitted_bridge_controls=96, new_kappa_claim=False)
    write(output / "RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write", action="store_true", help="Explicitly regenerate the appropriate committed receipt")
    args = parser.parse_args()
    result, words = finite()
    target = HERE / "FINITE.json"
    if args.write and not args.native:
        target.unlink(missing_ok=True)
        write(target, result)
    else:
        same(load(target), result, "finite receipt")
    if args.native:
        if args.output:
            native_result = full(result, words, args.output.resolve())
        else:
            with tempfile.TemporaryDirectory(prefix="r439-deferred-") as tmp:
                native_result = full(result, words, Path(tmp) / "replay")
        target = HERE / "NATIVE.json"
        if args.write:
            target.unlink(missing_ok=True)
            write(target, native_result)
        else:
            same(load(target), native_result, "native receipt")
        print("PASS_R439_DEFERRED_NATIVE words=2 stages=5,9,11 controls=96+5 no_new_kappa")
    else:
        need(args.output is None, "--output requires --native")
        print("PASS_R439_DEFERRED_FINITE columns=661 directions=2 phase_transfer=306 saving=430 no_new_kappa")


if __name__ == "__main__":
    main()

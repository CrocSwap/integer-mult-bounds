#!/usr/bin/env python3
"""Independent admission checks plus unchanged full/native replay. Apache-2.0.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
No nomination or macro-bound implementation is imported into these checks.
"""
import argparse
import copy
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def same(a, b, message):
    need(C["canonical"](a) == C["canonical"](b), message)


def validate_ops(ops):
    need(type(ops) is list and ops, "nonempty operation list")
    for op in ops:
        need(type(op) is list and len(op) == 2, "operation pair")
        d, s = op
        need(type(d) is int and type(s) is int and 0 <= d < 6 and 0 <= s < 6 and d != s,
             "elementary transvection")


def act(ops, value, positive=False):
    result = list(value)
    for d, s in ops:
        if positive:
            result[d] += result[s]
        else:
            result[d] ^= result[s]
    return result


def local_check(old, new):
    validate_ops(old)
    validate_ops(new)
    for x in range(64):
        values = [(x >> i) & 1 for i in range(6)]
        need(act(old, values) == act(new, values), "local Boolean map")
    growth = [0, 0]
    for reverse in (False, True):
        a, b = (old[::-1], new[::-1]) if reverse else (old, new)
        for col in range(6):
            values = [int(i == col) for i in range(6)]
            before, after = act(a, values, True), act(b, values, True)
            growth[int(reverse)] += sum(y > x for x, y in zip(before, after))
    return growth


def cleanup(word):
    v = word["v"]
    z = [g for phase in ("A", "B") for g in word[phase] if not v <= g[1] < 2 * v]
    word["C"] = [[1, d, list(ss)] for _, d, ss in z[::-1]]


def splice(parent, blocks, replacements):
    # Independent reconstruction from certified complete source intervals.
    result = copy.deepcopy(parent)
    a, cursor = [], 0
    for item in blocks:
        frame, start, end, wires = (item[k] for k in ("frame", "start", "end", "wires"))
        a.extend(copy.deepcopy(parent["A"][cursor:start]))
        if frame in replacements:
            a.extend([[frame, wires[d], [wires[s]]] for d, s in replacements[frame]])
        else:
            a.extend(copy.deepcopy(parent["A"][start:end]))
        cursor = end
    a.extend(copy.deepcopy(parent["A"][cursor:]))
    result["A"] = a
    cleanup(result)
    return result


def check_certificate(parent, candidate, cert):
    need(cert["format"] == "r439-global-prefix/1", "certificate version")
    same(cert["seed"], 3, "assignment seed")
    same(cert["nomination_seed_from_pr952"], 19, "inherited nomination seed")
    same(cert["nomination_priorities"], [[1, 2, 3, 4, 5, 0], [0, 5, 4, 3, 2, 1]], "unchanged priorities")
    same(cert["max_nominees_per_block"], 32, "bounded stopping rule")
    need(cert["parent_sha256"] == C["digest"](parent), "parent digest")
    need(cert["candidate_sha256"] == C["digest"](candidate), "candidate digest")
    same(cert["strict_repeat"], {"trials": 172800, "selected": 0, "saved_A": 0}, "same-input strict repeat")
    need(len(cert["blocks"]) == 60, "sixty-block domain")
    same([r["frame"] for r in cert["blocks"]], list(range(266, 326)), "frame domain")
    order = list(range(266, 326))
    random.Random(3).shuffle(order)
    same(cert["block_order"], order, "one seed-three block order")
    cursor = 0
    for item in cert["blocks"]:
        frame, start, end = (item[k] for k in ("frame", "start", "end"))
        need(all(type(i) is int for i in (frame, start, end)), "integer frame/range")
        indices = [i for i, g in enumerate(parent["A"]) if g[0] == frame]
        need(indices == list(range(start, end)) and cursor <= start < end, "complete source block")
        gates = parent["A"][start:end]
        wires = sorted({x for _, d, ss in gates for x in [d, *ss]})
        same(wires, item["wires"], "physical wires")
        need(len(wires) == 6 and all(r < parent["v"] or r >= 2 * parent["v"] for r in wires), "six z wires")
        old = [[wires.index(d), wires.index(s)] for _, d, ss in gates for s in ss]
        same(old, item["old"], "source operations")
        validate_ops(old)
        need(all(type(item[k]) is int for k in ("trials", "distinct_programs", "shorter_programs", "retained_nominees")),
             "integer domain accounting")
        need(item["trials"] == 2880 and 0 <= item["shorter_programs"] <= item["distinct_programs"] <= 2880,
             "nomination counts")
        need(item["retained_nominees"] == min(32, item["shorter_programs"]), "retention count")
        cursor = end
    by_frame = {r["frame"]: r for r in cert["blocks"]}
    # Every first nominee passes in this recorded construction. Regeneration
    # separately verifies the actual Gaussian menu and strict-repeat certificate.
    same(cert["attempts"], cert["selected"], "all attempts admitted")
    same([r["frame"] for r in cert["attempts"]], [f for f in order if by_frame[f]["retained_nominees"]],
         "priced order covers each nonempty block once")
    reports, replacements = [], {}
    for row in cert["attempts"]:
        same(row["rank"], 0, "first nominee admission")
        same(row["bill"]["admitted"], True, "actual admitted decision")
        frame, new = row["frame"], row["program"]
        old = by_frame[frame]["old"]
        growth = local_check(old, new)
        need(any(growth), "old local guard really rejects")
        need({r for op in new for r in op} == set(range(6)), "all six frame paths retained")
        need(len(new) < len(old), "shorter cost")
        replacements[frame] = new
        reports.append({"frame": frame, "before": len(old), "after": len(new), "growing_positive_entries": growth})
    same(splice(parent, cert["blocks"], replacements), candidate, "exact splice with literal cleanup")
    saved = sum(r["before"] - r["after"] for r in reports)
    need(len(reports) == 42 and saved == 120, "new construction summary")
    return {"selected": 42, "saved_A": saved, "saved_complete": 2 * saved,
            "Boolean_inputs": 64 * len(reports), "positive_column_pairs": 12 * len(reports),
            "forward_growth_blocks": sum(bool(r["growing_positive_entries"][0]) for r in reports),
            "reverse_growth_blocks": sum(bool(r["growing_positive_entries"][1]) for r in reports),
            "both_growth_blocks": sum(all(r["growing_positive_entries"]) for r in reports), "blocks": reports}


def price(scalar):
    f, b = scalar["F"], scalar["B"]
    local, nine = 64 * f ** 3 * b ** 2, (1 << 18) * f ** 5 * b ** 4
    return {"ADDs": scalar["ADDs"], "F": f, "B": b, "local_bits": local.bit_length(),
            "nine_bits": nine.bit_length(), "local_upper": str(local), "nine_upper": str(nine),
            "admitted": local < 1 << 104 and nine < 1 << 192}


def check_price(scalar, recorded):
    same(price(scalar), recorded, "literal complete-word price")


def trial_checks(parent, cert, independent):
    replacements, reports = {}, []
    for row in cert["attempts"]:
        replacements[row["frame"]] = row["program"]
        word = splice(parent, cert["blocks"], replacements)
        scalar = independent["word_checks"](word)
        check_price(scalar, row["bill"])
        reports.append({"frame": row["frame"], "scalar": scalar})
    return reports


def raw_literal_bounds(word, independent):
    # For invalid-budget controls only: retain literal COPY/ERASE and measure
    # both bounds even when word_checks deliberately raises at its cap check.
    program = independent["instructions"](word)
    n = 2 * word["v"] + word["R"]
    bounds = []
    for reverse in (False, True):
        ops = [("erase" if k == "copy" else "copy" if k == "erase" else k, d, s)
               for k, d, s in program[::-1]] if reverse else program
        state, peak = [1] * n + [0], 1
        for kind, d, s in ops:
            if kind == "add":
                state[d] += state[s]
            elif kind == "copy":
                state[d] = state[s]
            else:
                state[d] = 0
            peak = max(peak, state[d])
        bounds.append(peak)
    return {"F": bounds[0], "B": bounds[1], "ADDs": sum(k == "add" for k, _, _ in program)}


def controls(parent, candidate, cert, checker, independent):
    rejected = []

    def reject(name, function, reason):
        try:
            function()
        except (ValueError, checker.Reject) as error:
            need(reason in str(error), "unexpected rejection: " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise ValueError("accepted negative control: " + name)

    frame = cert["selected"][0]["frame"]
    index = next(i for i, r in enumerate(cert["blocks"]) if r["frame"] == frame)
    old, program = cert["blocks"][index]["old"], cert["selected"][0]["program"]
    bad = copy.deepcopy(program)
    bad.pop()
    reject("dropped Boolean gate", lambda: local_check(old, bad), "local Boolean map")
    bad_bool = copy.deepcopy(program)
    bad_bool[0][0] = True
    reject("boolean gate coordinate", lambda: local_check(old, bad_bool), "elementary transvection")
    bad_self = copy.deepcopy(program)
    bad_self[0][0] = bad_self[0][1]
    reject("self addition", lambda: local_check(old, bad_self), "elementary transvection")
    for name, field, value, reason in (
        ("wrong physical participant", "wires", [111] + cert["blocks"][index]["wires"][1:], "physical wires"),
        ("partial block boundary", "end", cert["blocks"][index]["end"] - 1, "complete source block"),
        ("noninteger frame", "frame", float(frame), "frame domain")):
        modified = copy.deepcopy(cert)
        modified["blocks"][index][field] = value
        reject(name, lambda m=modified: check_certificate(parent, candidate, m), reason)
    scalar = independent["word_checks"](candidate)
    for name, field, value in (("undercharged full cost", "ADDs", 23432), ("stale forward bound", "F", 1),
                               ("unpaid nine-stage bound", "nine_upper", "1")):
        modified = dict(cert["candidate_bill"])
        modified[field] = value
        reject(name, lambda m=modified: check_price(scalar, m), "literal complete-word price")
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(parent["C"])
    w = checker.Word(stale)
    w.full()
    h, conclusions, _ = w.interface()
    need(h["H4_C_literal_reverse_at_full"] is False and all(conclusions.values()), "stale cleanup premise")
    rejected.append("semantically equal but unpaired literal cleanup")
    reject("stale cleanup exact splice",
           lambda: check_certificate(parent, stale, dict(cert, candidate_sha256=C["digest"](stale))), "exact splice")
    broken = copy.deepcopy(candidate)
    del broken["A"][0]
    reject("dropped physical gate", lambda: independent["word_checks"](broken), "endpoint")
    altered = copy.deepcopy(candidate)
    altered["stats"]["junk_wires"] += 1
    reject("unrelated payload edit with rebound digest",
           lambda: check_certificate(parent, altered, dict(cert, candidate_sha256=C["digest"](altered))), "exact splice")
    reject("boolean receipt field", lambda: same({"n": 1}, {"n": True}, "strict receipt"), "strict receipt")
    # A repeated transvection pair is Boolean identity, with a growing positive
    # lift. These two fixed controls isolate the nine-stage cap and then exceed
    # the local cap. Full dirty-state replay must reach the cap rejection.
    wires = cert["blocks"][index]["wires"]
    d, s = wires[:2]
    loop = [[frame, d, [s]], [frame, d, [s]]]
    end = max(i for i, g in enumerate(candidate["A"]) if g[0] == frame) + 1
    failures = {}
    for repeat in (320, 1024):
        grown = copy.deepcopy(candidate)
        grown["A"][end:end] = copy.deepcopy(loop * repeat)
        cleanup(grown)
        measured = price(raw_literal_bounds(grown, independent))
        label = ("nine-stage-only precision overflow" if measured["local_bits"] <= 104 and measured["nine_bits"] > 192
                 else "local precision overflow" if measured["local_bits"] > 104 else None)
        if label and label not in failures:
            reject(label, lambda w=grown: independent["word_checks"](w), "precision cap")
            failures[label] = {"identity_loops": repeat, "bill": measured}
        if len(failures) == 2:
            break
    need(len(failures) == 2, "both independent precision controls found")
    return {"rejected": rejected, "precision_failures": failures}


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    baseline = C["load"](root / C["WORD"])
    parent_path = root / C["PARENT"] / "candidate.json.gz"
    parent = C["load"](parent_path)
    candidate = C["load"](C["HERE"] / "candidate.json.gz")
    cert = C["load"](C["HERE"] / "CERTIFICATE.json")
    print("reproduce strict comparison and complete-word admission", flush=True)
    regenerated = output / "regenerated"
    with (output / "search.log").open("x") as log:
        subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "build.py", "--source-root", root,
                        "--out", regenerated], check=True, stdout=log, stderr=subprocess.STDOUT)
    same(C["load"](regenerated / "candidate.json.gz"), candidate, "candidate regeneration")
    same(C["load"](regenerated / "CERTIFICATE.json"), cert, "complete search certificate regeneration")
    local = check_certificate(parent, candidate, cert)
    independent = runpy.run_path(str(root / C["PARENT"] / "verify.py"))
    print("literal ADD/COPY/ERASE replay of all 42 accumulated trials", flush=True)
    trials = trial_checks(parent, cert, independent)
    words = {"baseline": baseline, "parent952": parent, "candidate": candidate}
    scalar = {name: independent["word_checks"](word) for name, word in words.items()}
    check_price(scalar["parent952"], cert["baseline_bill"])
    check_price(scalar["candidate"], cert["candidate_bill"])
    need([scalar[k]["ADDs"] for k in words] == [24305, 23673, 23433], "full ADD accounting")
    source_prefix = independent["prefix_binding"](root)
    print("unchanged E8 geometry, 661 symbolic columns and original H1-H5", flush=True)
    checker, source = independent["source_checks"](root, words)
    negatives = controls(parent, candidate, cert, checker, independent)
    print("fresh native legality and 5/9/11 stages on all three words", flush=True)
    native = C["module"]("global_prefix_native", C["HERE"] / "native.py").run(
        root, root / C["WORD"], parent_path, C["HERE"] / "candidate.json.gz", output / "native")
    for label in words:
        need(native[label]["common_frame_ADDs"] == scalar[label]["ADDs"], "literal/native ADD agreement")
        staged = native[label]["staged"]["5"]
        need(staged["payload_prefix_bits"] == scalar[label]["local_payload_bits"], "literal/native payload agreement")
        need([int(row["cancellation_free_signed_row_l1_upper"]) for row in staged["signed_lift_prefix"]]
             == [scalar[label]["F"], scalar[label]["B"]], "literal/native positive bound agreement")
        need(int(staged["payload_prefix_upper"]) == int(price(scalar[label])["local_upper"]), "exact payload agreement")
    return {"status": "PASS_R439_GLOBAL_PREFIX_ADMISSION", "sources": manifest,
            "word_sha256": {name: C["digest"](word) for name, word in words.items()},
            "certificate_sha256": C["digest"](cert), "local": local, "trials": trials, "scalar": scalar,
            "prefix_source": source_prefix, "source_checks": source, "native": native, "controls": negatives}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expected", type=Path, default=C["HERE"] / "EXPECTED.json")
    args = parser.parse_args()
    if args.output:
        need(not args.output.exists(), "output already exists")
    if args.receipt:
        need(not args.receipt.exists(), "receipt already exists")
    expected = C["load"](args.expected)
    with tempfile.TemporaryDirectory(prefix="r439-global-prefix-") as tmp:
        result = run(args.source_root, args.output or Path(tmp) / "run")
        same(result, expected, "receipt differs from EXPECTED.json")
        if args.receipt:
            C["write"](args.receipt, result)
    print("PASS_R439_GLOBAL_PREFIX_ADMISSION: 42 blocks; 240 further ADDs; 872 versus PR589; "
          "H1-H5; 104/192-bit caps; 5/9/11 stages; no new kappa")


if __name__ == "__main__":
    main()

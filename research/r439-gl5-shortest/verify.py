#!/usr/bin/env python3
"""Regenerate and independently check exact GL5 windows and complete words.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance. Apache-2.0.
Set-valued full-word replay is retained from PR1122; the truth-table/domain/DP
checks below do not invoke the search's matrix or interval implementations.
"""
import argparse
import bisect
import collections
import copy
import hashlib
from pathlib import Path
import runpy
import subprocess
import tempfile

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need, same = C["need"], C["same"]
L = runpy.run_path(str(Path(__file__).with_name("literal.py")))


def boolean_program(program, value):
    bits = [(value >> i) & 1 for i in range(5)]
    for d, s in program:
        need(type(d) is int and type(s) is int and 0 <= d < 5 and 0 <= s < 5 and d != s,
             "Boolean generator")
        bits[d] = bits[d] != bits[s]
    return sum(int(v) << i for i, v in enumerate(bits))


def verify_windows(parent, rows, tables):
    a = [(f, d, s) for f, d, ss in parent["A"] for s in ss]
    need(all(not parent["v"] <= d < 2 * parent["v"] for _, d, _ in a), "A destinations all cleaned")
    expected = set()
    # Independently enumerate backwards from each endpoint.
    for end in range(1, len(a) + 1):
        wires = set()
        frame = a[end - 1][0]
        for begin in range(end - 1, max(-1, end - 13), -1):
            f, d, s = a[begin]
            if f != frame:
                break
            wires.update((d, s))
            if len(wires) > 5:
                break
            if len(wires) == 5:
                expected.add((begin, end))
    actual = [(r["begin"], r["end"]) for r in rows]
    need(len(actual) == len(set(actual)) and set(actual) == expected, "complete window domain")
    need(actual == sorted(actual), "window order")
    truth_cases = 0
    for row in rows:
        begin, end = row["begin"], row["end"]
        wires = sorted({v for _, d, s in a[begin:end] for v in (d, s)})
        same(wires, row["wires"], "window physical wires")
        same(row["frame"], a[begin][0], "window frame")
        same(row["old"], [[wires.index(d), wires.index(s)] for _, d, s in a[begin:end]], "literal old window")
        outputs = []
        for value in range(32):
            old = boolean_program(row["old"], value)
            need(old == boolean_program(row["new"], value), "window Boolean map")
            outputs.append(old)
            truth_cases += 1
        packed = sum(((outputs[1 << s] >> d) & 1) << (5 * d + s)
                     for d in range(5) for s in range(5))
        same(packed, row["matrix"], "truth table matrix encoding")
        need(tables[packed] == row["distance"] == len(row["new"]), "certified shortest length")
        same(row["gain"], end - begin - len(row["new"]), "window saving")
        same(row["full_participation"], {v for g in row["new"] for v in g} == set(range(5)),
             "complete wire participation")
    return dict(windows=len(rows), Boolean_inputs=truth_cases,
                exact_maps=len({r["matrix"] for r in rows}))


def independent_interval(rows, chosen, claimed, ceiling=12):
    eligible = [r for r in rows if r["gain"] > 0 and r["full_participation"] and r["distance"] <= ceiling]
    ordered = sorted(eligible, key=lambda r: (r["end"], r["begin"]))
    ends, best = [], [0]
    for row in ordered:
        previous = bisect.bisect_right(ends, row["begin"])
        best.append(max(best[-1], best[previous] + row["gain"]))
        ends.append(row["end"])
    total, previous = 0, 0
    for index in chosen:
        need(type(index) is int and 0 <= index < len(rows), "interval index")
        row = rows[index]
        need(row["gain"] > 0 and row["full_participation"] and row["distance"] <= ceiling,
             "ineligible interval")
        need(row["begin"] >= previous, "overlapping interval")
        total += row["gain"]
        previous = row["end"]
    need(total == best[-1] == claimed, "maximum interval saving")
    return best[-1]


def reconstruct(parent, rows, accepted):
    a = [(f, d, s) for f, d, ss in parent["A"] for s in ss]
    schedule = {rows[i]["begin"]: rows[i] for i in accepted}
    need(len(schedule) == len(accepted), "duplicate interval")
    out, pos = [], 0
    while pos < len(a):
        row = schedule.get(pos)
        if row is None:
            f, d, s = a[pos]
            out.append([f, d, [s]])
            pos += 1
        else:
            out.extend([row["frame"], row["wires"][d], [row["wires"][s]]] for d, s in row["new"])
            pos = row["end"]
    word = copy.deepcopy(parent)
    word["A"] = out
    full = [i for i, frame in enumerate(word["frames"]) if sorted(frame) == list(range(word["v"]))]
    need(len(full) == 1, "unique full frame")
    word["C"] = []
    for phase in ("B", "A"):
        for _, d, donors in word[phase][::-1]:
            if d < word["v"] or d >= 2 * word["v"]:
                word["C"].append([full[0], d, list(donors)])
    return word


def literal_bounds(word):
    n = 2 * word["v"] + word["R"]
    stream = L["instructions"](word)
    bounds = []
    for reverse in (False, True):
        values, peak, opened = [1] * n + [0], 1, False
        for kind, d, s in reversed(stream) if reverse else stream:
            if reverse and kind != "add":
                kind = "erase" if kind == "copy" else "copy"
            if kind == "add":
                need(s != n or opened, "positive COPY read outside lifetime")
                values[d] += values[s]
            elif kind == "copy":
                need(not opened and values[d] == 0, "positive dirty COPY")
                values[d], opened = values[s], True
            else:
                need(opened, "positive ERASE outside lifetime")
                values[d], opened = 0, False
            peak = max(peak, values[d])
        need(not opened, "positive unclosed COPY")
        bounds.append(peak)
    f, b = bounds
    local, nine = 2**6 * f * f * f * b * b, 2**18 * f**5 * b**4
    sections = {p: sum(map(lambda g: len(g[2]), word[p])) for p in "ABCD"}
    sections["scatter"] = sum(map(len, word["scatter"]))
    return dict(ADDs=sum(kind == "add" for kind, _, _ in stream), sections=sections,
                F=f, B=b, local_upper=str(local), nine_upper=str(nine), local_bits=local.bit_length(),
                nine_bits=nine.bit_length(), admitted=local < 2**104 and nine < 2**192)


def admission(parent, candidate, rows, certificate):
    accepted = []
    need([r["window"] for r in certificate["trials"]] == certificate["chosen"], "complete admission order")
    for trial in certificate["trials"]:
        word = reconstruct(parent, rows, accepted + [trial["window"]])
        price = literal_bounds(word)
        same(price, trial["price"], "full admission price")
        if price["admitted"]:
            accepted.append(trial["window"])
    same(accepted, certificate["accepted"], "accepted intervals")
    same(reconstruct(parent, rows, accepted), candidate, "literal candidate reconstruction")
    for label, word in (("0", parent), ("1", candidate)):
        L["literal_cleanup"](word)
        price = literal_bounds(word)
        same(price, certificate["prices"][label], "final price")
        L["require_admission"](price)
        for reverse, key in ((False, "F"), (True, "B")):
            full = L["execute"](word, reverse)
            need(full["bound"] == price[key] and full["ADDs"] == price["ADDs"], "set replay bill")
    need(certificate["prices"]["0"]["ADDs"] - certificate["prices"]["1"]["ADDs"]
         == 2 * sum(rows[i]["gain"] for i in accepted), "cleanup saving paid twice")
    return dict(trials=len(certificate["trials"]), accepted=len(accepted),
                full_words=2, formal_columns=661, directions=2)


def owner(root, parent, candidate):
    original = C["load"](root / C["WORD"])
    for word in (parent, candidate):
        same(sorted(original), sorted(word), "payload keys")
        for key in original:
            if key not in "ABCD":
                same(original[key], word[key], "owning geometry " + key)
    for key in parent:
        if key not in ("A", "C"):
            same(parent[key], candidate[key], "untouched section " + key)
    check = C["module"]("gl5_source_owner", root / C["CHECKER"])
    frozen = check.Word(original)
    labels = frozen.labels()
    result = {}
    for label, word in (("0", parent), ("1", candidate)):
        current = copy.copy(frozen)
        current.w = word
        full, totals = current.full(), current.totals()
        hypotheses, conclusions, _ = current.interface()
        for k, v in hypotheses.items():
            need(v is (k != "H2_D_frame0_targets_from_helpers"), "inherited H2 boundary: " + k)
        for k, v in conclusions.items():
            need(v is (k != "K_equals_D"), "inherited K boundary: " + k)
        need(full["columns"] == 661 and [x["rank"] for x in totals] == [7] * 9, "owning coverage")
        need(all(x["hyperplane_of_punctured_line"] for x in totals), "punctured total geometry")
        result[label] = dict(full=full, totals=totals, hypotheses=hypotheses, conclusions=conclusions)
    return dict(labels=labels, words=result), frozen


def controls(parent, candidate, rows, cert, owning, metric_dir):
    rejected = []

    def reject(label, action, message):
        try:
            action()
        except ValueError as error:
            need(message in str(error), "wrong failure: " + label + ": " + str(error))
            rejected.append(label)
        else:
            raise ValueError("control accepted: " + label)

    row = rows[cert["accepted"][0]]
    bad = copy.deepcopy(row["new"])
    del bad[0]
    reject("missing replacement operation", lambda: need(all(boolean_program(row["old"], v) ==
           boolean_program(bad, v) for v in range(32)), "Boolean map"), "Boolean map")
    for phase, index in (("A", 0), ("D", 0), ("D", -1)):
        wrong = copy.deepcopy(candidate)
        del wrong[phase][index]
        reject("omitted " + phase + " operation " + str(index), lambda w=wrong: L["execute"](w), "boundary")
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(parent["C"])
    L["execute"](stale)
    reject("F2-valid stale cleanup", lambda: L["literal_cleanup"](stale), "literal cleanup")
    stream = L["instructions"](candidate)
    for kind, reason in (("copy", "outside lifetime"), ("erase", "not empty")):
        at = next(i for i, ins in enumerate(stream) if ins[0] == kind)
        bad_stream = stream[:at] + stream[at + 1:]
        reject("missing private " + kind, lambda s=bad_stream: L["execute"](candidate, stream=s), reason)
    wrong = copy.deepcopy(candidate)
    wrong["A"][0][0] = True
    reject("boolean frame", lambda: L["instructions"](wrong), "frame domain")
    for field, cap in (("local_upper", 104), ("nine_upper", 192)):
        wrong_price = dict(cert["prices"]["1"], **{field: str(1 << cap)})
        reject("strict equality at " + field, lambda p=wrong_price: L["require_admission"](p), "precision cap")
    wrong = copy.deepcopy(candidate)
    wrong["A"][0][0] = 0
    current = copy.copy(owning)
    current.w = wrong
    try:
        current.full()
    except Exception as error:
        need(type(error).__name__ == "Reject" and "climb not nested" in str(error), "frame control reason")
        rejected.append("non-nested physical frame")
    else:
        raise ValueError("physical frame control accepted")
    first = cert["accepted"][0]
    reject("overlapping interval plan", lambda: independent_interval(rows, [first, first], 2 * rows[first]["gain"]),
           "overlapping interval")
    bad_rows = copy.deepcopy(rows)
    del bad_rows[-1]
    dist = (metric_dir / "table.dist").read_bytes()
    reject("omitted window from census", lambda: verify_windows(parent, bad_rows, dist), "complete window domain")
    bad_rows = copy.deepcopy(rows)
    bad_rows[0]["distance"] += 1
    reject("false shortest length", lambda: verify_windows(parent, bad_rows, dist), "certified shortest length")

    # Mutate actual full-size tables. Independent C++ checks must reject them.
    last = (metric_dir / "table.last").read_bytes()
    unit = sum(1 << (6 * i) for i in range(5))
    mutations = (("wrong distance root", "dist", unit, 1, "root"),
                 ("singular matrix inserted", "dist", 0, 0, "extra root"),
                 ("spurious unreachable predecessor", "last", 0, 1, "unreachable predecessor"),
                 ("truncated distance table", "truncate", 0, 0, "table size"))
    prefix = metric_dir / "mutated"
    for label, kind, at, value, reason in mutations:
        d, p = bytearray(dist), bytearray(last)
        if kind == "dist":
            d[at] = value
        elif kind == "last":
            p[at] = value
        else:
            d = d[:-1]
        Path(str(prefix) + ".dist").write_bytes(d)
        Path(str(prefix) + ".last").write_bytes(p)
        run = subprocess.run([str(metric_dir / "check"), "5", str(prefix)], capture_output=True, text=True)
        need(run.returncode != 0 and reason in run.stderr, "metric mutation accepted or wrong failure: " + label)
        rejected.append(label)
    for suffix in (".dist", ".last"):
        Path(str(prefix) + suffix).unlink()
    # A six-cycle spanning path has valid descending predecessors but is not
    # a shortest-distance labelling. This isolates the essential lower-bound
    # (edge-Lipschitz) check from the upper-bound predecessor check.
    small_dist, small_last = bytearray([255] * 16), bytearray([255] * 16)
    state = 9
    small_dist[state] = 0
    for depth, (d, s) in enumerate(((0, 1), (1, 0), (0, 1), (1, 0), (0, 1)), 1):
        bits = [[(state >> (2 * i + j)) & 1 for j in range(2)] for i in range(2)]
        bits[d] = [a ^ b for a, b in zip(bits[d], bits[s])]
        state = sum(bits[i][j] << (2 * i + j) for i in range(2) for j in range(2))
        small_dist[state], small_last[state] = depth, 2 * d + s
    Path(str(prefix) + ".dist").write_bytes(small_dist)
    Path(str(prefix) + ".last").write_bytes(small_last)
    run = subprocess.run([str(metric_dir / "check"), "2", str(prefix)], capture_output=True, text=True)
    need(run.returncode != 0 and "edge Lipschitz" in run.stderr, "non-shortest spanning path accepted")
    rejected.append("valid predecessor tree with false shortest distances")
    # A malformed predecessor at a nonroot must also fail even when distances
    # are genuine. Restore the GL2 BFS tables, then erase one predecessor.
    subprocess.run([str(metric_dir / "build"), "2", str(prefix)], check=True, capture_output=True)
    small_dist = Path(str(prefix) + ".dist").read_bytes()
    small_last = bytearray(Path(str(prefix) + ".last").read_bytes())
    at = next(i for i, value in enumerate(small_dist) if value == 1)
    small_last[at] = 255
    Path(str(prefix) + ".last").write_bytes(small_last)
    run = subprocess.run([str(metric_dir / "check"), "2", str(prefix)], capture_output=True, text=True)
    need(run.returncode != 0 and "predecessor generator" in run.stderr, "missing predecessor accepted")
    rejected.append("missing nonroot predecessor")
    for suffix in (".dist", ".last"):
        Path(str(prefix) + suffix).unlink()
    return dict(rejected=rejected, positive_controls=["stale cleanup still F2 exact"])


def run(root, output, receipt=None, write_expected=False):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = C["pins"](root)  # Before loading any executable source dependency.
    output.mkdir(parents=True, exist_ok=False)
    build = C["module"]("gl5_builder", C["HERE"] / "build.py")
    parent, candidate, rows, cert = build.run(root, output / "build")
    for name, value in (("candidate.json.gz", candidate), ("CERTIFICATE.json", cert), ("WINDOWS.json.gz", rows)):
        same(C["load"](C["HERE"] / name), value, "complete regenerated artifact " + name)
    metric_dir = output / "build/metric"
    windows = verify_windows(parent, rows, (metric_dir / "table.dist").read_bytes())
    need(all(r["gain"] <= 0 or r["full_participation"] for r in rows),
         "unconstrained interval lower bound must include every shortening")
    independent_interval(rows, cert["chosen"], cert["interval_saving_A"])
    ceiling = cert["ceiling_six_comparison"]
    independent_interval(rows, ceiling["chosen"], ceiling["interval_saving_A"], 6)
    admission_report = admission(parent, candidate, rows, cert)
    formulas = L["source_formula"](root)
    owning, original = owner(root, parent, candidate)
    negative = controls(parent, candidate, rows, cert, original, metric_dir)
    native = C["module"]("gl5_native", C["HERE"] / "native.py").run(
        root, output / "build", cert["prices"], output / "native")
    result = dict(format="r439-gl5-shortest-receipt/1", sources_sha256=C["digest"](manifest),
                  certificate_sha256=C["digest"](cert), windows=windows, admission=admission_report,
                  formulas=formulas, metric=cert["metric"], native=native, owner=owning,
                  controls=negative, prices=cert["prices"], no_new_kappa=True)
    if write_expected:
        C["write"](C["HERE"] / "EXPECTED.json", result)
    else:
        same(C["load"](C["HERE"] / "EXPECTED.json"), result, "complete expected receipt")
    if receipt:
        C["write"](receipt, result)
    print("PASS_R439_GL5_SHORTEST:", len(cert["accepted"]), "windows;",
          cert["prices"]["0"]["ADDs"] - cert["prices"]["1"]["ADDs"],
          "ADDs saved; GL5 metric; 5/9/11 stages;", len(negative["rejected"]), "controls; no new kappa", flush=True)
    print("receipt_sha256", C["digest"](result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--write-expected", action="store_true", help="initial production only; refuses overwrite")
    args = parser.parse_args()
    if args.output:
        run(args.source_root, args.output, args.receipt, args.write_expected)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-gl5-") as temporary:
            run(args.source_root, Path(temporary) / "run", args.receipt, args.write_expected)

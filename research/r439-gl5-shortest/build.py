#!/usr/bin/env python3
"""One complete GL5 census on frozen PR1122 A; no rescan. Apache-2.0.

Gareth Davidson, with substantial OpenAI Codex assistance. Window and interval
method follows Ross Richardson PR936 and Davidson PR904/980. Optimal CNOT BFS
is established prior art; this code is a fresh small direct implementation.
"""
import argparse
import collections
import copy
import hashlib
import os
from pathlib import Path
import runpy
import shlex
import subprocess

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need = C["need"]
IDENTITY = sum(1 << (6 * i) for i in range(5))


def metric(output):
    output.mkdir()
    reports = {}
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    for stem in ("build", "check"):
        subprocess.run(compiler + ["-O3", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                       str(C["HERE"] / ("metric_" + stem + ".cpp")),
                       "-o", str(output / stem)], check=True)
        run = subprocess.run([str(output / stem), "5", str(output / "table")],
                             check=True, capture_output=True, text=True)
        (output / (stem + ".json")).write_text(run.stdout)
        reports[stem] = C["load"](output / (stem + ".json"))
    need(reports["build"]["histogram"] == reports["check"]["histogram"], "metric histograms")
    tables = [(output / ("table." + kind)).read_bytes() for kind in ("dist", "last")]
    return tables, dict(reports=reports, sha256={kind: hashlib.sha256(raw).hexdigest()
                                               for kind, raw in zip(("dist", "last"), tables)})


def flatten(word):
    return [(f, d, s) for f, d, sources in word["A"] for s in sources]


def census(word, tables):
    a = flatten(word)
    distance, last = tables
    rows = []
    for begin in range(len(a)):
        wires, frame = set(), a[begin][0]
        for final in range(begin, min(begin + 12, len(a))):
            f, d, s = a[final]
            if f != frame:
                break
            wires.update((d, s))
            if len(wires) > 5:
                break
            if len(wires) != 5:
                continue
            names = sorted(wires)
            labels = {v: i for i, v in enumerate(names)}
            old = [[labels[d], labels[s]] for _, d, s in a[begin:final + 1]]
            state = IDENTITY
            for d, s in old:
                state ^= ((state >> (5 * s)) & 31) << (5 * d)
            need(distance[state] != 255, "census map absent")
            at, backwards = state, []
            while at != IDENTITY:
                d, s = divmod(last[at], 5)
                need(0 <= d < 5 and 0 <= s < 5 and d != s, "path generator")
                backwards.append([d, s])
                before = at ^ (((at >> (5 * s)) & 31) << (5 * d))
                need(distance[before] + 1 == distance[at], "path descent")
                at = before
            new = backwards[::-1]
            need(len(new) == distance[state], "path length")
            rows.append(dict(begin=begin, end=final + 1, frame=frame, wires=names,
                             old=old, new=new, matrix=state, distance=distance[state],
                             gain=len(old) - len(new),
                             full_participation={x for g in new for x in g} == set(range(5))))
    return rows


def interval(rows, n, ceiling=12):
    ends = collections.defaultdict(list)
    for i, row in enumerate(rows):
        if row["gain"] > 0 and row["full_participation"] and row["distance"] <= ceiling:
            ends[row["end"]].append(i)
    scores, trace = [0] * (n + 1), [None] * (n + 1)
    for end in range(1, n + 1):
        scores[end], trace[end] = scores[end - 1], (end - 1, None)
        for i in ends[end]:
            row = rows[i]
            value = scores[row["begin"]] + row["gain"]
            if value > scores[end]:
                scores[end], trace[end] = value, (row["begin"], i)
    chosen, at = [], n
    while at:
        at, i = trace[at]
        if i is not None:
            chosen.append(i)
    return scores[-1], chosen[::-1]


def replace(parent, rows, chosen):
    a, out, at = flatten(parent), [], 0
    for i in chosen:
        row = rows[i]
        need(at <= row["begin"] < row["end"] <= len(a), "ordered disjoint intervals")
        out.extend(a[at:row["begin"]])
        out.extend((row["frame"], row["wires"][d], row["wires"][s]) for d, s in row["new"])
        at = row["end"]
    out.extend(a[at:])
    word = copy.deepcopy(parent)
    word["A"] = [[f, d, [s]] for f, d, s in out]
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == word["v"])
    word["C"] = [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
                 if not word["v"] <= d < 2 * word["v"]]
    return word


def positive(word, reverse=False):
    values = [1] * (2 * word["v"] + word["R"])
    peak = 1
    phases = ("C", "B", "scatter", "A", "D") if reverse else ("D", "A", "scatter", "B", "C")
    for phase in phases:
        if phase == "scatter":
            indices = range(len(word["ret"]))
            for j in reversed(indices) if reverse else indices:
                copied = values[word["ret"][j]]
                for i, sources in enumerate(word["scatter"]):
                    if j in sources:
                        values[word["v"] + i] += copied
                        peak = max(peak, values[word["v"] + i])
        else:
            for _, d, sources in reversed(word[phase]) if reverse else word[phase]:
                values[d] += sum(values[s] for s in sources)
                peak = max(peak, values[d])
    return peak


def price(word):
    f, b = positive(word), positive(word, True)
    sections = {s: sum(len(g[2]) for g in word[s]) for s in "ABCD"}
    sections["scatter"] = sum(map(len, word["scatter"]))
    local, nine = 64 * f**3 * b**2, (1 << 18) * f**5 * b**4
    return dict(ADDs=sum(sections.values()), F=f, B=b, sections=sections,
                local_upper=str(local), nine_upper=str(nine), local_bits=local.bit_length(),
                nine_bits=nine.bit_length(), admitted=local < 1 << 104 and nine < 1 << 192)


def run(root, output):
    C["pins"](root)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    parent = C["load"](C["HERE"] / C["PARENT"])
    tables, metric_report = metric(output / "metric")
    rows = census(parent, tables)
    saving, chosen = interval(rows, len(flatten(parent)))
    accepted, trials = [], []
    for i in chosen:
        trial = price(replace(parent, rows, accepted + [i]))
        trials.append(dict(window=i, price=trial))
        if trial["admitted"]:
            accepted.append(i)
    candidate = replace(parent, rows, accepted)
    ceiling_gain, ceiling_chosen = interval(rows, len(flatten(parent)), 6)
    length_pairs = collections.Counter((len(r["old"]), r["distance"]) for r in rows)
    certificate = dict(format="r439-gl5-shortest/1", seed=13, metric=metric_report,
                       windows_sha256=C["digest"](rows), window_count=len(rows),
                       distinct_maps=len({r["matrix"] for r in rows}),
                       length_pairs=[[a, b, count] for (a, b), count in sorted(length_pairs.items())],
                       shorter_count=sum(r["gain"] > 0 for r in rows),
                       shorter_above_six=sum(r["gain"] > 0 and r["distance"] > 6 for r in rows),
                       eligible_count=sum(r["gain"] > 0 and r["full_participation"] for r in rows),
                       interval_saving_A=saving, chosen=chosen, trials=trials, accepted=accepted,
                       accepted_above_six=sum(rows[i]["distance"] > 6 for i in accepted),
                       ceiling_six_comparison=dict(interval_saving_A=ceiling_gain, chosen=ceiling_chosen,
                           scope="Same first shortest representatives restricted to length <=6; not a replay of PR936"),
                       parent_sha256=C["digest"](parent), candidate_sha256=C["digest"](candidate),
                       prices={"0": price(parent), "1": price(candidate)}, new_kappa_claim=False)
    for name, value in (("0.json.gz", parent), ("1.json.gz", candidate),
                        ("WINDOWS.json.gz", rows), ("CERTIFICATE.json", certificate)):
        C["write"](output / name, value)
    return parent, candidate, rows, certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    *_, cert = run(args.source_root, args.output)
    print("BUILT", cert["window_count"], "windows;", len(cert["accepted"]), "admissions;", cert["prices"]["1"])

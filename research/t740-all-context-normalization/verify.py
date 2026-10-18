#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nick Petalas.
"""Certify commuting hosted phases and the full-child normal form for T740."""
import argparse
import gzip
import hashlib
import io
import json
from bisect import bisect_left
from collections import Counter
from pathlib import Path

from algebra import replay, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMIT = 32_000_000
BASE_ROWS = 9 * 74 * 408
OWNERS, PORTS, CHILDREN = 740, 112, 20
FILL_HASH = "8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00"
PATHS = {
    "base": "research/idle-star-paired-axis-census/vendor/BASE-FILL.json.gz",
    "journal": "research/idle-star-paired-axis-census/vendor/EXCHANGE.json",
    "providers": "research/idle-star-paired-axis-census/vendor/PROVIDERS.json",
    "order": "research/rank7-joint-endframes/allocation/ORDER.json",
    "dispatch": "research/rank7-joint-endframes/allocation/DISPATCH.json",
    "plan": "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz",
    "template": "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz",
    "phases": "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
}


def checked_bytes(path, pin):
    require(path.is_file() and not path.is_symlink(), "missing or linked source")
    require(path.stat().st_size <= LIMIT, "source size bound")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + str(path))
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
            "source Git blob: " + str(path))
    return raw


def decode(raw):
    if raw[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "decoded size bound")
    return json.loads(raw)


def load_inputs(root=ROOT):
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    pins = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pins) == set(PATHS.values()), "exact live source closure")
    data = {name: decode(checked_bytes(Path(root) / path, pins[path]))
            for name, path in PATHS.items()}
    refs = sources["retained_sources"]
    require(len(refs) == 2, "exact predecessor reference closure")
    for row in refs:
        checked_bytes(HERE / row["local_path"], row)
    data["reference"] = json.loads((HERE / "reference/PR3297-RESULT.json").read_bytes())
    return data


def windows(template):
    locals_ = {item["stage"]: item for item in template["recipe"] if item["kind"] == "local"}
    start, site, touches = {}, {}, []
    require(len(template["execution_schedule"]) <= 64, "schedule size")
    for index, event in enumerate(template["execution_schedule"]):
        kind = event["kind"]
        if kind == "local_cover_sweep":
            stage = event["stage"]
            require(stage not in start, "duplicate local stage")
            start[stage] = index
            pair = locals_[stage]["pair"]
            touches.append((index, {2 * pair, 2 * pair + 1}))
        elif kind == "bridge":
            src, dst = event["src"], event["dst"]
            touches.append((index, {2 * src, 2 * src + 1, 2 * dst, 2 * dst + 1}))
        elif kind == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                require(child not in site, "duplicate phase site")
                site[child] = index, 2 * event["pair"] + side
        else:
            require(kind in ("terminal", "terminal_Y_translations", "bank_padding_cover_sweep",
                             "translate_every_live_family"), "unclassified schedule event")
    require(set(start) == set(range(9)) and set(site) == set(range(CHILDREN)), "complete cuts")
    terminal = [i for i, e in enumerate(template["execution_schedule"]) if e["kind"] == "terminal"]
    require(len(terminal) == 1 and terminal[0] > max(end for end, _ in site.values()),
            "terminal permutation follows all insertion sites")
    allowed = {}
    for child, (end, row) in site.items():
        allowed[child] = [stage for stage in range(9) if start[stage] <= end and
                          not any(start[stage] <= i < end and row in rows for i, rows in touches)]
    return allowed, {child: row for child, (_, row) in site.items()}


def chronology(data):
    require(len(data["order"]) == 666 and len(data["dispatch"]) == 666, "base schedule size")
    order = [(stage, owner + 74 * copy) for stage, owner in data["order"] for copy in range(10)]
    times = [[] for _ in range(OWNERS)]
    for time, (stage, owner) in enumerate(order):
        require(stage == len(times[owner]), "owner stages occur once in order")
        times[owner].append(time)
    require(all(len(row) == 9 for row in times), "complete owner chronology")
    dispatch = {(stage, owner): tag for stage, owner, tag in data["dispatch"]}
    require(set(dispatch) == {(stage, owner) for stage in range(9) for owner in range(74)},
            "complete dispatch")
    return order, times, dispatch


def lifted(base, index):
    copy, old = divmod(index, BASE_ROWS)
    time, helper, owner, child, port, offset = base[old]
    return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]


def edits_for(base, journal):
    require(len(base) == BASE_ROWS, "base fill size")
    require(journal["copies"] == 10 and len(journal["edits"]) == 145, "exchange journal size")
    edits = {}
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < 10 * BASE_ROWS and index not in edits,
                "exchange index")
        require(before == lifted(base, index), "exchange preimage")
        require(len(after) == 6 and all(type(value) is int for value in after), "exchange row")
        require(after[:2] == before[:2], "exchange call/helper identity")
        edits[index] = after
    return edits


def accept_row(row, data, prepared, used, counts, histogram):
    order, times, dispatch, allowed, streams, lengths = prepared
    time, helper, owner, child, port, offset = row
    require(0 <= time < len(order) and 0 <= owner < OWNERS and 0 <= port < PORTS and
            0 <= child < CHILDREN and 0 <= helper < 408, "hosted row domain")
    stage, caller = order[time]
    width = data["providers"][dispatch[stage, caller % 74]]["widths"][helper]
    require(type(width) is int and 1 <= width <= 73 and
            0 <= offset <= lengths[port][child] - width, "hosted slice range")
    cut = bisect_left(times[owner], time)
    require(cut in allowed[child], "hosted phase crosses a noncommuting event")
    require(2 * data["plan"]["pairs"][str(child)] + data["plan"]["sides"][str(child)] ==
            streams[child], "hosted and residual physical streams agree")
    context = owner * PORTS + port
    mask = ((1 << width) - 1) << offset
    require(not used[context][child] & mask, "hosted slice overlap")
    used[context][child] |= mask
    counts[context] += 1
    histogram[child, cut] += 1


def audit_fill(data):
    allowed, streams = windows(data["template"])
    order, times, dispatch = chronology(data)
    recipes = data["phases"]["recipes"]
    require(len(recipes) == PORTS, "port coverage")
    lengths = [[len(child["orthogonal_axes"]) for child in recipe["idle_children"]]
               for recipe in recipes]
    require(all(len(row) == CHILDREN and max(row) <= 73 for row in lengths), "child dimensions")
    base = data["base"]["rows"]
    edits = edits_for(base, data["journal"])
    used = [[0] * CHILDREN for _ in range(OWNERS * PORTS)]
    counts, histogram = [0] * (OWNERS * PORTS), Counter()
    prepared = order, times, dispatch, allowed, streams, lengths
    header = {"columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
              "dispatch_overrides": []}
    prefix = json.dumps(header, sort_keys=True, separators=(",", ":"))[:-1] + ',"rows":['
    digest = hashlib.sha256(prefix.encode())
    for index in range(10 * BASE_ROWS):
        row = edits[index] if index in edits else lifted(base, index)
        accept_row(row, data, prepared, used, counts, histogram)
        encoded = ("," if index else "") + json.dumps(row, separators=(",", ":"))
        digest.update(encoded.encode())
    digest.update(b"]}\n")
    require(digest.hexdigest() == FILL_HASH, "complete expanded T740 fill payload")
    require(all(counts), "every owner/port context visited")
    profiles = Counter()
    for context, row in enumerate(used):
        require(all(mask == (1 << mask.bit_count()) - 1 for mask in row), "compact hosted prefix")
        profile = tuple(lengths[context % PORTS][child] - mask.bit_count()
                        for child, mask in enumerate(row))
        profiles[profile] += 1
    return {"owners": OWNERS, "ports": PORTS, "contexts": len(counts),
            "hosted_rows": sum(counts), "journal_edits": len(edits), "fill_sha256": digest.hexdigest(),
            "hosted_rows_per_context": [min(counts), max(counts)],
            "allowed_stage_cuts": {str(child): allowed[child] for child in range(CHILDREN)},
            "hosted_cut_histogram": [[child, cut, count] for (child, cut), count in sorted(histogram.items())],
            "residual_profiles": [[list(profile), count] for profile, count in sorted(profiles.items())]}


def normal_forms(data):
    expected = data["reference"]["polynomial_matrix"]
    require(len(expected) == 72, "reference matrix size")
    baseline = Counter()
    for row, column, mask, ambient, coefficient in expected:
        require(0 <= row < 8 and 0 <= column < 8 and 0 <= mask < 1 << CHILDREN and
                ambient in (0, -1), "reference term domain")
        baseline[row, column, ambient] += coefficient
    require({key: value for key, value in baseline.items() if value} ==
            {(i, i, 0): 1 for i in range(8)}, "full normal form has identity baseline")
    peaks = []
    for port, recipe in enumerate(data["phases"]["recipes"]):
        require(recipe["port"] == port, "literal recipe ordering")
        for child in recipe["idle_children"]:
            axes = [int(a) for a in child["orthogonal_axes"]]
            require(all((a & b).bit_count() % 2 == int(i == j)
                        for i, a in enumerate(axes) for j, b in enumerate(axes)), "orthonormal full axes")
        terms, peak = replay(data["template"], recipe)
        require(terms == expected, "full-child normal form mismatch at port " + str(port))
        peaks.append(peak)
    return {"symbolic_ports": len(peaks), "normal_form_terms": len(expected),
            "peak_symbolic_terms": max(peaks), "formal_sites": CHILDREN,
            "normal_form_sha256": hashlib.sha256(json.dumps(expected, separators=(",", ":")).encode()).hexdigest()}


def build():
    data = load_inputs()
    return {"schema_version": 1, **audit_fill(data), **normal_forms(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a deterministic receipt to this explicit path")
    args = parser.parse_args()
    observed = build()
    if args.write:
        args.write.write_text(json.dumps(observed, indent=2) + "\n")
    else:
        require(observed == json.loads((HERE / "RESULT.json").read_bytes()), "deterministic receipt mismatch")
    print("PASS_T740_ALL_CONTEXT_NORMALIZATION contexts=82880 hosted_rows=2717280 symbolic_ports=112")


if __name__ == "__main__":
    main()

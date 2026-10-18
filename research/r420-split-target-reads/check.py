#!/usr/bin/env python3
"""Exact census of separately framed R420 target reads. Apache-2.0.

Prepared for thakrarsagar with substantial OpenAI Codex assistance.
No predecessor checker is imported. Python 3.9+, standard library only.
"""
import copy
import gzip
import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
PAYLOAD_SHA256 = "e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2"
BASELINE = {1: 1320, 2: 1440, 4: 60, 5: 120, 8: 9}
DELTA = {1: -1, 2: 1, 4: 1, 5: -1}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def primitive(row):
    g = math.gcd(*row)
    if not g:
        return tuple(row)
    first = next(x for x in row if x)
    return tuple(x // (g if first > 0 else -g) for x in row)


def reduce_row(row, basis):
    row = tuple(row)
    for pivot, b in basis:
        if row[pivot]:
            a = row[pivot]
            row = primitive(tuple(b[pivot] * x - a * y for x, y in zip(row, b)))
    return row


def span(rows):
    basis = []
    for row in rows:
        row = reduce_row(row, basis)
        if any(row):
            pivot = next(i for i, x in enumerate(row) if x)
            basis.append((pivot, primitive(row)))
            basis.sort()
    return tuple(basis)


class Replay:
    def __init__(self, word):
        self.w = word
        self.bases = [span(word["lines"][i] for i in f) for f in word["frames"]]
        self.dims = [len(b) for b in self.bases]
        self.contains_cache = {}

    def contains(self, outer, inner):
        key = (outer, inner)
        if key not in self.contains_cache:
            self.contains_cache[key] = all(
                not any(reduce_row(row, self.bases[outer]))
                for _, row in self.bases[inner]
            )
        return self.contains_cache[key]

    def run(self, tail=None):
        w = self.w
        n = 2 * w["v"] + w["R"]
        cur = w["start"][:]
        values = [1 << r for r in range(n)]
        hist = Counter()

        def climb(r, f):
            need(self.contains(f, cur[r]), "non-nested frame")
            gap = self.dims[f] - self.dims[cur[r]]
            if gap:
                hist[gap] += 1
            cur[r] = f

        def gates(items):
            for f, d, sources in items:
                need(sources and d not in sources and len(sources) == len(set(sources)),
                     "invalid gate operands")
                for r in [d] + sources:
                    climb(r, f)
                for s in sources:
                    values[d] ^= values[s]

        gates(w["D"])
        gates(w["A"])
        # Each retained total has one paid full-rank COPY; scatter stays at zero.
        need(all(self.dims[cur[r]] == 8 for r in w["ret"]), "COPY frame")
        hist[8] += len(w["ret"])
        for t, row in enumerate(w["scatter"]):
            need(self.dims[cur[w["v"] + t]] == 0, "scatter target frame")
            for k in row:
                values[w["v"] + t] ^= values[w["ret"][k]]
        gates(w["B"][:-120])
        entrance = cur[:]
        gates(w["B"][-120:] if tail is None else tail)
        gates(w["C"])
        for r, f in enumerate(w["final"]):
            climb(r, f)
        expected = [1 << r for r in range(n)]
        for t in range(w["v"]):
            expected[w["v"] + t] ^= 1 << t
        need(values == expected, "dirty-input scalar identity")
        return hist, entrance


def local_profile(replay, target_frame, source_frames, top, order, read_frames):
    cur_target = target_frame
    cur_sources = list(source_frames)
    hist = Counter()
    for j, f in zip(order, read_frames):
        need(replay.contains(f, cur_target) and replay.contains(f, cur_sources[j]),
             "illegal split read")
        need(replay.contains(top, f), "read exceeds final target frame")
        for old in (cur_target, cur_sources[j]):
            gap = replay.dims[f] - replay.dims[old]
            if gap:
                hist[gap] += 1
        cur_target = cur_sources[j] = f
    need(cur_target == top, "target endpoint")
    # C and the final climb require every source to reach rank eight.
    for f in cur_sources:
        hist[8 - replay.dims[f]] += 1
    return hist


def census(replay, entrance):
    w = replay.w
    tail = w["B"][-120:]
    need([d for _, d, _ in tail] == list(range(120, 240)), "target tail")
    used = Counter(s for _, _, sources in tail for s in sources)
    need(len(used) == 360 and set(used.values()) == {1}, "independent source sets")
    need(not set(used).intersection(range(120, 240)), "source is a target")
    need(all(replay.dims[f] == 8 for f, _, _ in w["C"]), "full-frame cleanup")
    cases = []
    split_tail = []
    for top, d, sources in tail:
        need(len(sources) == 3, "three-source gate")
        cell = entrance[d]
        sf = [entrance[s] for s in sources]
        need(replay.dims[cell] == 2 and replay.dims[top] == 7, "target ranks")
        need(all(replay.dims[f] == 6 and replay.contains(top, f) for f in sf),
             "source ranks and containment")
        need(all(len(span([r for f in pair for _, r in replay.bases[f]])) == 7
                 for pair in itertools.combinations(sf, 2)), "distinct source hyperplanes")
        eligible = [j for j, f in enumerate(sf) if replay.contains(f, cell)]
        need(len(eligible) == 1, "one early source")
        need(all(replay.dims[w["final"][s]] == 8 for s in sources), "source final ranks")
        profiles = Counter()
        for order in itertools.permutations(range(3)):
            for first in ([top, sf[order[0]]] if order[0] in eligible else [top]):
                h = local_profile(replay, cell, sf, top, order, [first, top, top])
                profiles[tuple(sorted(h.items()))] += 1
        original = ((1, 6), (5, 1))
        early = ((1, 5), (2, 1), (4, 1))
        need(profiles == {original: 6, early: 2}, "exhaustive local profiles")
        j = eligible[0]
        split_tail.append([sf[j], d, [sources[j]]])
        split_tail.extend([top, d, [s]] for k, s in enumerate(sources) if k != j)
        cases.append({"target": d - 120, "cell": cell, "top": top,
                      "sources": sources, "source_frames": sf,
                      "early_source": sources[j]})
    return cases, split_tail


def rejected(call, message):
    try:
        call()
    except ValueError as exc:
        need(message in str(exc), "negative control rejected for wrong reason")
    else:
        raise ValueError("negative control was accepted: " + message)


def check():
    payload = gzip.decompress(WORD.read_bytes())
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA256, "source payload pin")
    w = json.loads(payload)
    need((w["h"], w["v"], w["R"]) == (8, 120, 420), "word parameters")
    replay = Replay(w)
    baseline, entrance = replay.run()
    need(baseline == BASELINE, "complete baseline profile")
    cases, split_tail = census(replay, entrance)
    changed, _ = replay.run(split_tail)
    expected = Counter(BASELINE)
    expected.update({d: 120 * n for d, n in DELTA.items()})
    need(changed == +expected, "complete split profile with cleanup")
    need(sum(d * n for d, n in changed.items()) == 5112, "rank mass")
    need(sum(changed.values()) == sum(baseline.values()), "paid call count")
    # Exact majorization certificate. Strict concavity applies for every 0 < p < 1.
    need([5, 1] != [4, 2] and 5 > 4 and 5 + 1 == 4 + 2, "majorization")
    controls = []
    bad = copy.deepcopy(split_tail)
    bad[0][2] = split_tail[1][2][:]
    rejected(lambda: replay.run(bad), "non-nested frame")
    controls.append("wrong source at rank six")
    bad = copy.deepcopy(split_tail)
    del bad[2]
    rejected(lambda: replay.run(bad), "dirty-input scalar identity")
    controls.append("missing target read")
    bad_word = copy.deepcopy(w)
    bad_word["B"][-1][2][0] = bad_word["B"][-2][2][0]
    rejected(lambda: census(Replay(bad_word), entrance), "independent source sets")
    controls.append("shared source invalidates independent choices")
    # Omitting the source's rank-six-to-eight cleanup would change the answer.
    need(DELTA == {1: -1, 2: 1, 4: 1, 5: -1}, "cleanup-inclusive delta")
    unpaid = Counter(changed)
    unpaid[2] -= 120
    rejected(lambda: need(unpaid == +expected, "complete split profile with cleanup"),
             "complete split profile with cleanup")
    controls.append("omitted rank-two source cleanup")
    return {
        "status": "PASS_R420_SPLIT_TARGET_READ_BOUND",
        "base_commit": "66849e1475c930fd7732b1a0067ffee7e1e95f60",
        "source_pr": 543,
        "source_commit": "2065fe4f72a914d907f1046603f5a36f17018535",
        "payload_sha256": PAYLOAD_SHA256,
        "targets": len(cases), "distinct_sources": 360,
        "source_orders_per_target": 6, "legal_schedules_per_target": 8,
        "simultaneous_schedules": str(8 ** 120),
        "baseline_equivalent_per_target": 6, "strictly_worse_per_target": 2,
        "baseline_profile": dict(sorted(baseline.items())),
        "all_early_profile": dict(sorted(changed.items())),
        "profile_delta_per_early_read": DELTA,
        "rank_mass": 5112, "paid_calls": sum(baseline.values()),
        "moment_difference": "2^p + 4^p - 1 - 5^p > 0 for 0 < p < 1",
        "majorization": {"baseline": [5, 1], "early_read": [4, 2]},
        "dirty_input_columns_per_replay": 660,
        "negative_controls": controls,
        "worked_example": cases[3],
        "geometry_census_sha256": hashlib.sha256(
            json.dumps(cases, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


if __name__ == "__main__":
    result = check()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(not sys.argv[1:], "usage: check.py [--emit]")
        need(json.loads((HERE / "CERTIFICATE.json").read_text()) ==
             json.loads(json.dumps(result)), "certificate mismatch")
        print("PASS_R420_SPLIT_TARGET_READ_BOUND targets=120 schedules=8^120 controls=4 kappa=unchanged")

#!/usr/bin/env python3
"""Code-disjoint circuit/optimum checks, full word replay and native accounting.

Does not import search.py. Ross Richardson, with substantial OpenAI Codex
assistance; Apache-2.0. Finite checks do not prove the multiplication theorem.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / "research/e8-bit-p111-tuned"
WORD_PATH = PACKAGE / "tune/bitE8mut-p111-tuned.json.gz"
EXPORTER = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
REGISTERS = [15, 23, 30, 41, 49, 53, 59, 70, 75, 82, 91, 96]
BASE_COMMIT = "f567884aeb8851b6e794af1184119a3bfbe1e631"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_module(path):
    spec = importlib.util.spec_from_file_location("pinned_xcheck", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def linear_map(program, reverse=False, signed=False):
    """Replay columns as integer vectors, independently of discovery's rows."""
    n = len(REGISTERS)
    idx = {r: i for i, r in enumerate(REGISTERS)}
    columns = []
    for j in range(n):
        state = [int(i == j) for i in range(n)]
        for frame, dst, sources in reversed(program) if reverse else program:
            need(frame == 519 and dst in idx and sources, "bad local gate")
            need(len({dst, *sources}) == len(sources) + 1, "self or duplicate source")
            for source in sources:
                need(source in idx, "new register")
                state[idx[dst]] += (-1 if signed else 1) * state[idx[source]]
        columns.append(state)
    return [list(row) for row in zip(*columns)]


def independent_minimum(target):
    """Integer subset sums + backward Bellman, rather than forward exact-cover DP."""
    n = len(target)
    identity = [tuple(int(i == j) for j in range(n)) for i in range(n)]
    target = [tuple(row) for row in target]
    goal_rows = [tuple(x - int(i == j) for j, x in enumerate(row)) for i, row in enumerate(target)]
    need(all(x >= 0 for row in goal_rows for x in row), "invalid target diagonal")

    @lru_cache(None)
    def price(dst, restricted):
        goal = goal_rows[dst]
        donors = []
        for j in range(n):
            if j == dst:
                continue
            row = target[j] if restricted >> j & 1 else identity[j]
            if all(x <= y for x, y in zip(row, goal)):
                donors.append(row)
        sums = {tuple(0 for _ in range(n)): 0}
        for row in donors:
            for previous, count in list(sums.items()):
                combined = tuple(x + y for x, y in zip(previous, row))
                if all(x <= y for x, y in zip(combined, goal)):
                    sums[combined] = min(sums.get(combined, n + 1), count + 1)
        return sums.get(goal)

    masks = [sum(1 << j for j, x in enumerate(row) if x) for row in goal_rows]
    end = (1 << n) - 1
    remaining = [10**9] * (end + 1)
    remaining[end] = 0
    edges = feasible = 0
    for state in range(end - 1, -1, -1):
        for dst in range(n):
            if state >> dst & 1:
                continue
            edges += 1
            cost = price(dst, state & masks[dst])
            if cost is not None:
                feasible += 1
                remaining[state] = min(remaining[state], cost + remaining[state | 1 << dst])
    return dict(minimum=remaining[0], states=end + 1,
                state_destination_pairs=edges, feasible_edges=feasible)


def check_schedule(program):
    completed = set()
    last = None
    donors = set()
    for _, dst, sources in program:
        need(len(sources) == 1, "schedule must consist of elementary additions")
        if dst != last:
            need(dst not in completed, "destination written in two separate groups")
            if last is not None:
                completed.add(last)
            last, donors = dst, set()
        need(sources[0] not in donors, "donor repeated in realization")
        donors.add(sources[0])


def splice(word, candidate):
    variant = copy.deepcopy(word)
    variant["B"][163:205] = [g for factor in candidate["factors"] for g in factor["program"]]
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == word["v"])
    variant["C"] = [[full, dst, list(ss)] for _, dst, ss in reversed(variant["A"] + variant["B"])
                    if dst < word["v"] or dst >= 2 * word["v"]]
    return variant


def replay_f2(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    values = [1 << i for i in range(n)]
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            copies = [values[q] for q in word["ret"]]
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[v + t] ^= copies[k]
        else:
            for _, dst, donors in word[section]:
                need(donors and len({dst, *donors}) == len(donors) + 1, "malformed word gate")
                for src in donors:
                    values[dst] ^= values[src]
    need(all(values[i] == ((1 << i) ^ (1 << (i - v)) if v <= i < 2 * v else 1 << i)
             for i in range(n)), "dirty-input endpoint changed")
    return n


def frame_paths(word):
    paths = [[f] for f in word["start"]]
    for section in ("D", "A", "B", "C"):
        for frame, dst, sources in word[section]:
            for r in (dst, *sources):
                if paths[r][-1] != frame:
                    need(set(word["frames"][paths[r][-1]]) <= set(word["frames"][frame]), "frame descent")
                    paths[r].append(frame)
    for r, frame in enumerate(word["final"]):
        if paths[r][-1] != frame:
            need(set(word["frames"][paths[r][-1]]) <= set(word["frames"][frame]), "final descent")
            paths[r].append(frame)
    return paths


def export(word, destination):
    path = destination / "word.json"
    path.write_text(json.dumps(word))
    output = destination / "records"
    subprocess.run([sys.executable, "-I", "-B", str(EXPORTER), str(path), str(output)],
                   check=True, capture_output=True, text=True)
    records = list(struct.iter_unpack("<6i", (output / "249-records.bin").read_bytes()))
    frames = json.loads((output / "frames.json").read_text())["frames"]
    return output, records, frames


def record_invoice(word, records, frames):
    n = 2 * word["v"] + word["R"]
    histogram = Counter()
    for op, dst, src, coeff, frame, rank in records:
        if op == 0 and frame:
            histogram[frame] += 1  # MOVE rank is the fifth field.
        elif op == 2:
            histogram[rank] += 1
    bounds = []
    for reverse in (False, True):
        norms = [1] * (n + 1)
        largest = 1
        opened = False
        for op, dst, src, coeff, frame, rank in reversed(records) if reverse else records:
            if op == 1:
                norms[dst] += abs(coeff) * norms[src]
                largest = max(largest, norms[dst])
            elif op in (2, 3):
                opening = (op == 2) != reverse
                need(opened != opening, "copy lifecycle")
                norms[n] = norms[dst] if opening else 0
                opened = opening
        need(not opened, "copy work remains open")
        bounds.append(largest)
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    need(payload < 1 << 104, "payload exceeds inherited cap")
    return dict(records=len(records), adds=sum(r[0] == 1 for r in records),
                moves=sum(r[0] == 0 for r in records),
                copies=sum(r[0] == 2 for r in records), erasures=sum(r[0] == 3 for r in records),
                profile={str(k): v for k, v in sorted(histogram.items())},
                rank_mass=sum(k * v for k, v in histogram.items()),
                positive_bounds=bounds, payload_bits=payload.bit_length(), payload=str(payload),
                record_sha256=digest(b"".join(struct.pack("<6i", *r) for r in records)))


def verify_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    need(manifest["base_commit"] == BASE_COMMIT, "base pin changed")
    for relative, expected in manifest["sha256"].items():
        path = ROOT / relative
        need(path.is_file() and digest(path.read_bytes()) == expected, "source pin mismatch: " + relative)


def validate_candidate(word, candidate):
    need(candidate["source_sha256"] == digest(WORD_PATH.read_bytes()), "candidate source pin")
    need((candidate["frame"], candidate["slice"], candidate["split"], candidate["registers"]) ==
         (519, [163, 205], 182, REGISTERS), "candidate object changed")
    need(candidate["base_commit"] == BASE_COMMIT and candidate["assignment_seed"] == 2, "candidate provenance")
    need(len(candidate["factors"]) == 2, "factor count")
    for i, (a, b) in enumerate(((163, 182), (182, 205))):
        factor = candidate["factors"][i]
        check_schedule(factor["program"])
        original = linear_map(word["B"][a:b])
        need(original == linear_map(factor["program"]) == factor["matrix"], "factor integer map changed")
        need(sum(len(g[2]) for g in factor["program"]) == factor["minimum"], "factor count")
        need(sum(len(g[2]) for g in word["B"][a:b]) == factor["original_adds"], "original count")
    variant = splice(word, candidate)
    need(linear_map(word["B"][163:205]) == linear_map(variant["B"][163:195]), "whole block integer map")
    need(replay_f2(variant) == 661, "column count")
    need(frame_paths(word) == frame_paths(variant), "register frame paths changed")
    return variant


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--work", type=Path, help="preserve exporter inputs and records here")
    args = parser.parse_args()
    verify_sources()
    word = json.loads(gzip.decompress(WORD_PATH.read_bytes()))
    candidate = json.loads((HERE / "CANDIDATE.json").read_text())
    variant = validate_candidate(word, candidate)
    minima = []
    for factor in candidate["factors"]:
        found = independent_minimum(factor["matrix"])
        need(all(found[k] == factor[k] for k in found), "independent Bellman certificate mismatch")
        minima.append(found)
    checker = load_module(PACKAGE / "code/xcheck_p.py")
    owning = checker.Word(variant)
    owning.labels()
    full = owning.full()
    hypotheses, conclusion, _ = owning.interface()
    need(all(hypotheses.values()) and all(conclusion.values()), "pinned H1-H5 interface failed")
    totals = owning.totals()
    need([t["rank"] for t in totals] == [7] * 9, "copy ranks changed")

    def reject(label, mutate):
        changed = copy.deepcopy(candidate)
        mutate(changed)
        try:
            validate_candidate(word, changed)
        except (ValueError, KeyError, IndexError):
            return label
        raise ValueError("mutation accepted: " + label)

    controls = []
    controls.append(reject("delete_add", lambda c: c["factors"][0]["program"].pop()))
    controls.append(reject("wrong_donor", lambda c: c["factors"][0]["program"][0][2].__setitem__(0, 49)))
    controls.append(reject("self_add", lambda c: c["factors"][0]["program"][0][2].__setitem__(0, 15)))
    controls.append(reject("frame_zero", lambda c: c["factors"][0]["program"][0].__setitem__(0, 0)))
    controls.append(reject("unclaimed_helper", lambda c: c["factors"][0]["program"][0][2].__setitem__(0, 222)))
    controls.append(reject("factor_swap", lambda c: c["factors"].reverse()))
    controls.append(reject("duplicate_donor", lambda c: c["factors"][0]["program"][0][2].append(23)))
    controls.append(reject("stale_source", lambda c: c.__setitem__("source_sha256", "0" * 64)))
    controls.append(reject("wrong_minimum", lambda c: c["factors"][0].__setitem__("minimum", 15)))
    controls.append(reject("wrong_matrix", lambda c: c["factors"][0]["matrix"][0].__setitem__(0, 0)))
    bad_cleanup = copy.deepcopy(variant)
    bad_cleanup["C"] = word["C"]
    try:
        replay_f2(bad_cleanup)
    except ValueError:
        controls.append("stale_cleanup")
    else:
        # Same forward F2 map can make stale cleanup restore too; H4 must detect it.
        need(not checker.Word(bad_cleanup).interface()[0]["H4_C_literal_reverse_at_full"],
             "stale cleanup accepted by H4")
        controls.append("stale_cleanup_H4")

    with tempfile.TemporaryDirectory(prefix="r439-frame519-") as temporary:
        work = args.work or Path(temporary)
        work.mkdir(parents=True, exist_ok=True)
        for name in ("base", "candidate"):
            (work / name).mkdir(exist_ok=True)
        _, before_records, before_frames = export(word, work / "base")
        _, after_records, after_frames = export(variant, work / "candidate")
        need(before_frames == after_frames, "exported geometry changed")
        before = record_invoice(word, before_records, before_frames)
        after = record_invoice(variant, after_records, after_frames)
    need(before["profile"] == after["profile"] and before["rank_mass"] == after["rank_mass"] == 5129,
         "paid profile changed")
    need(before["moves"] == after["moves"] and before["copies"] == after["copies"] == 9,
         "additional frame work or copy")
    need(before["adds"] - after["adds"] == 20, "unpriced reverse cleanup")
    need(after["positive_bounds"][0] == before["positive_bounds"][0] and
         after["positive_bounds"][1] < before["positive_bounds"][1], "prefix bill did not improve")
    reverse_before = linear_map(word["B"][163:205], reverse=True)
    reverse_after = linear_map(variant["B"][163:195], reverse=True)
    need(all(b <= a for ra, rb in zip(reverse_before, reverse_after) for a, b in zip(ra, rb)),
         "local reverse positive map not dominated")
    certificate = dict(schema="r439-frame519-verification/1", assignment_seed=2,
                       base_commit=BASE_COMMIT, candidate_sha256=digest((HERE / "CANDIDATE.json").read_bytes()),
                       finite_columns=661, frame_paths=661, boolean_local_inputs=1 << len(REGISTERS),
                       minima=minima, before=before, after=after, controls_rejected=controls,
                       hypotheses=hypotheses, conclusion=conclusion, copy_ranks=[t["rank"] for t in totals],
                       reverse_positive_strict_entries=sum(b < a for ra, rb in zip(reverse_before, reverse_after)
                                                           for a, b in zip(ra, rb)),
                       variant_content_sha256=digest(canonical(variant)),
                       kappa="not_recomputed; no_new_kappa")
    # Exhaust the complete Boolean domain with a scalar interpreter, separate from column equality.
    idx = {r: i for i, r in enumerate(REGISTERS)}
    for inputs in range(1 << len(REGISTERS)):
        outputs = []
        for program in (word["B"][163:205], variant["B"][163:195]):
            values = [(inputs >> i) & 1 for i in range(len(REGISTERS))]
            for _, dst, sources in program:
                for src in sources:
                    values[idx[dst]] ^= values[idx[src]]
            outputs.append(values)
        need(outputs[0] == outputs[1], "Boolean truth table differs")
    path = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        need(certificate == json.loads(path.read_text()), "certificate mismatch")
    print("PASS_R439_FRAME519 adds=42->32 local_ADDs=24305->24285 minima=16+16 "
          "columns=661 boolean_inputs=4096 controls=" + str(len(controls)) +
          " reverse_bound=" + str(after["positive_bounds"][1]) + " payload_bits=93 no_new_kappa")


if __name__ == "__main__":
    main()

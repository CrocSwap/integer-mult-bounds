#!/usr/bin/env python3
"""Exact finite verification for the R439 phase-B whole-block survey.

Independent of search.py: the class minima are rechecked here with a backward
Bellman recursion over realized-register subsets (the opposite recursion
direction to the discovery DP) and its own donor-subset enumeration; the
per-row donor-supply infeasibility certificates are rechecked by direct
counting; the spliced blocks' forward integer maps, reverse positive maps,
Boolean truth tables, splice, register frame paths, paid profile, exact F2
endpoint on all columns, inherited H1-H5 interface, exported scalar bills and
positive/payload bounds are all recomputed.

The owning geometry/interface checker is eumemic's PR555/PR589 xcheck_p.py and
the record exporter is Dylan Crow's export_records.py; both are pinned by
SHA-256 in CERTIFICATE.json and used unmodified.

The whole-block single-write class is that of open PR #873 (with PR #844's and
PR #857's neighboring framings); the verification structure adapts #873's
r439-block508-schedule verifier with attribution.  No optimality outside the
class is claimed.

Prepared with help from opencode.  Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"


class Reject(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def pins(certificate):
    need(certificate["schema"] == "r439-bsection-survey/1", "unknown schema")
    need(certificate["base_commit"] == "f567884aeb8851b6e794af1184119a3bfbe1e631",
         "certificate built against a different base")
    for path, expected in certificate["source_sha256"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        need(actual == expected, "source pin mismatch: " + path)


def integer_map(ops, n):
    """Propagate each integer basis column independently (fresh implementation)."""
    columns = []
    for column in range(n):
        values = [1 if i == column else 0 for i in range(n)]
        for dst, src in ops:
            need(type(dst) is int and type(src) is int and 0 <= dst < n and 0 <= src < n
                 and dst != src, "invalid block operation")
            values[dst] += values[src]
        columns.append(values)
    return [list(row) for row in zip(*columns)]


def dominated(new, old):
    return all(x <= y for a, b in zip(new, old) for x, y in zip(a, b))


def supply_certificate(forward, row, col):
    """Independent recheck of a per-row donor-supply obstruction.

    In the whole-block single-write class, the donors of a row are entry
    singletons or completed final rows, each at most once, and every donor
    must fit the row's goal entrywise (all values are nonnegative).  Returns
    the pair (demand, supply) where supply over-approximates every feasible
    donor combination by summing all fitting donors, including mutually
    exclusive singleton/row pairs.  demand > supply is an order-independent
    infeasibility certificate for that row.
    """
    n = len(forward)
    goal = [forward[row][j] - (1 if j == row else 0) for j in range(n)]
    need(min(goal) >= 0, "row has no e_i base")
    supply = [0] * n
    for k in range(n):
        if k == row:
            continue
        for value in ([1 if j == k else 0 for j in range(n)], list(forward[k])):
            if all(a <= b for a, b in zip(value, goal)):
                for j in range(n):
                    supply[j] += value[j]
    return goal[col], supply[col]


def row_cost(forward, goal_row, done, dst):
    """Minimum donor count realizing row dst from realized set `done`, or
    None.  Iterative deepening over donor subsets with exact integer sums and
    entrywise pruning; donors are completed rows of `done` and entry
    singletons of the registers not yet realized (each donor at most once)."""
    n = len(forward)
    donors = []
    for src in range(n):
        if src == dst:
            continue
        value = list(forward[src]) if done >> src & 1 else [1 if j == src else 0 for j in range(n)]
        if all(a <= b for a, b in zip(value, goal_row)):
            donors.append(value)
    donors.sort(key=lambda value: -sum(value))

    def extend(start, remaining, depth):
        if not any(remaining):
            return True
        if depth == 0:
            return False
        for index in range(start, len(donors)):
            value = donors[index]
            if all(a <= b for a, b in zip(value, remaining)):
                rest = [a - b for a, b in zip(remaining, value)]
                if extend(index + 1, rest, depth - 1):
                    return True
        return False

    if not any(goal_row):
        return 0
    for depth in range(1, len(donors) + 1):
        if extend(0, goal_row, depth):
            return depth
    return None


def backward_minimum(forward):
    """Backward Bellman recursion over realized-register subsets; written
    independently of search.py's forward dynamic program.  Returns None when
    no program in the class realizes the map."""
    n = len(forward)
    need(all(forward[i][i] >= 1 for i in range(n)), "missing diagonal")
    goal = [[forward[i][j] - (1 if j == i else 0) for j in range(n)] for i in range(n)]
    size = 1 << n
    infinity = 10 ** 9
    dist = [infinity] * size
    dist[size - 1] = 0
    feasible = 0
    for done in range(size - 2, -1, -1):
        for dst in range(n):
            if done >> dst & 1:
                continue
            cost = row_cost(forward, goal[dst], done, dst)
            if cost is None:
                continue
            feasible += 1
            nxt = done | (1 << dst)
            if cost + dist[nxt] < dist[done]:
                dist[done] = cost + dist[nxt]
    return {"minimum": None if dist[0] >= infinity else dist[0],
            "states": size,
            "state_destination_pairs": n * (1 << (n - 1)),
            "feasible_edges": feasible,
            "backward_distances_sha256": digest(dist)}


def block_model(blk, regs):
    index = {r: i for i, r in enumerate(regs)}
    n = len(regs)
    need(all(len(ss) == 1 and t in index and ss[0] in index and ss[0] != t for _, t, ss in blk),
         "block leaves the single-wire block class")
    return [(index[t], index[s]) for _, t, (s,) in blk], n


def bind_block(word, entry):
    need(entry["section"] == "B", "wrong section")
    first, last = entry["slice"]
    blk = word["B"][first:last]
    need(len(blk) == entry["original_gates"], "wrong original bill")
    need(all(f == entry["frame"] and len(ss) == 1 for f, t, ss in blk), "source block changed")
    regs = sorted({t for _, t, _ in blk} | {s for _, _, ss in blk for s in ss})
    need(regs == entry["registers"], "block touches undeclared wires")
    ops, n = block_model(blk, regs)
    forward = integer_map(ops, n)
    return blk, ops, forward, n


def rebuild_cleanup(word):
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == word["v"])
    return [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if d < word["v"] or d >= 2 * word["v"]]


def build_word(word, certificate):
    result = copy.deepcopy(word)
    # Right to left: a shorter replacement shifts later B indices.
    for entry in sorted((e for e in certificate["blocks"] if e["spliced"]),
                        key=lambda e: -e["slice"][0]):
        first, last = entry["slice"]
        need(len(entry["gates"]) == entry["minimum"], "gate count differs from certified minimum")
        result["B"][first:last] = copy.deepcopy(entry["gates"])
    result["C"] = rebuild_cleanup(result)
    return result


def frame_paths(word):
    frames = [set(f) for f in word["frames"]]
    paths = [[f] for f in word["start"]]

    def move(r, f):
        if paths[r][-1] != f:
            need(frames[paths[r][-1]] < frames[f], "illegal frame descent or lateral move")
            paths[r].append(f)
    for section in "DABC":
        for f, d, ss in word[section]:
            for r in [d, *ss]:
                move(r, f)
    for r, f in enumerate(word["final"]):
        move(r, f)
    return paths


def whole_endpoint(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    state = [{i} for i in range(n)]

    def run(section):
        for _, d, sources in word[section]:
            for s in sources:
                state[d].symmetric_difference_update(state[s])
    run("D")
    run("A")
    snapshots = [state[r].copy() for r in word["ret"]]
    for t, reads in enumerate(word["scatter"]):
        for k in reads:
            state[v + t].symmetric_difference_update(snapshots[k])
    run("B")
    run("C")
    for r, actual in enumerate(state):
        expected = {r, r - v} if v <= r < 2 * v else {r}
        need(actual == expected, "dirty-input endpoint mismatch at register %d" % r)
    return n


def boolean_tables(ops_old, ops_new, n):
    hits = 0
    for value in range(1 << n):
        state_old = [(value >> i) & 1 for i in range(n)]
        state_new = list(state_old)
        for ops, state in ((ops_old, state_old), (ops_new, state_new)):
            for dst, src in ops:
                state[dst] ^= state[src]
        need(state_old == state_new, "Boolean input counterexample: %d" % value)
        hits += 1
    return hits


def load_checker():
    spec = importlib.util.spec_from_file_location("bsection_survey_xcheck", ROOT / CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    return checker


def export_and_bound(word, out):
    out.mkdir(parents=True, exist_ok=True)
    path = out / "word.json.gz"
    path.write_bytes(gzip.compress(canonical(word), mtime=0))
    subprocess.run([sys.executable, "-I", "-B", str(ROOT / EXPORTER),
                    str(path), str(out / "records")],
                   check=True, capture_output=True, text=True)
    raw = (out / "records/249-records.bin").read_bytes()
    need(len(raw) % 24 == 0, "misaligned exporter records")
    records = list(struct.iter_unpack("<6i", raw))
    n = 2 * word["v"] + word["R"]
    bounds = []
    for reverse in (False, True):
        norms, maximum, opened = [1] * (n + 1), 1, False
        for op, a, b, coefficient, _, _ in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(coefficient) * norms[b]
                maximum = max(maximum, norms[a])
            elif op == 2:
                need(not opened, "nested retained copy")
                norms[b], opened = norms[a], True
            elif op == 3:
                need(opened, "unmatched retained erase")
                norms[b], opened = 0, False
            else:
                raise Reject("unknown record opcode")
        need(not opened, "unclosed retained copy")
        bounds.append(maximum)
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    need(payload < 1 << 104, "positive-prefix cap exceeded")
    return {"records": len(records), "adds": sum(r[0] == 1 for r in records),
            "copies": sum(r[0] == 2 for r in records),
            "erasures": sum(r[0] == 3 for r in records),
            "forward_positive_bound": bounds[0], "reverse_positive_bound": bounds[1],
            "payload_bits": payload.bit_length(),
            "record_sha256": hashlib.sha256(raw).hexdigest()}, records


def must_reject(name, action):
    try:
        action()
    except Reject:
        return name
    raise Reject("negative control accepted: " + name)


def verify(out):
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    pins(certificate)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8")) \
        if (HERE / "EXPECTED.json").exists() else None
    if expected is None and not globals().get("EXPECTED_MISSING_OK"):
        raise Reject("EXPECTED.json receipts missing")

    survey = {}
    spliced = {}
    for entry in certificate["blocks"]:
        blk, ops, forward, n = bind_block(word, entry)
        record = {"original_gates": entry["original_gates"], "registers": entry["registers"]}
        if entry["status"] == "infeasible":
            optimality = backward_minimum(forward)
            need(optimality["minimum"] is None, "class program exists for a block certified infeasible")
            record["backward_optimality"] = optimality
            witness = entry.get("witness")
            if witness is not None:
                demand, supply = supply_certificate(forward, witness["row"], witness["col"])
                need((demand, supply) == (witness["demand"], witness["supply"])
                     and demand > supply,
                     "donor-supply certificate does not hold")
                record["supply_witness"] = dict(witness, recomputed_demand=demand,
                                                recomputed_supply=supply)
            else:
                record["supply_witness"] = None
            survey[entry["frame"]] = record
            continue
        need(entry["status"] == "class-minimum", "unknown status: " + entry["status"])
        optimality = backward_minimum(forward)
        need(optimality["minimum"] == entry["minimum"], "class minimum receipt differs")
        record["backward_optimality"] = optimality
        record["minimum"] = entry["minimum"]
        if entry["spliced"]:
            need(entry["frame"] == entry["gates"][0][0] and
                 all(f == entry["frame"] and len(ss) == 1 and t in entry["registers"]
                     and ss[0] in entry["registers"] and ss[0] != t for f, t, ss in entry["gates"]),
                 "candidate leaves the single-wire block class")
            local, m = block_model(entry["gates"], entry["registers"])
            need(m == n, "candidate register count differs")
            forward_new = integer_map(local, n)
            need(forward_new == forward, "forward integer map differs")
            reverse_old = integer_map(ops[::-1], n)
            reverse_new = integer_map(local[::-1], n)
            record["reverse_entrywise_dominated"] = dominated(reverse_new, reverse_old)
            record["reverse_strictly_smaller_entries"] = sum(
                1 for a, b in zip(reverse_new, reverse_old) for x, y in zip(a, b) if x < y)
            record["reverse_larger_entries"] = sum(
                1 for a, b in zip(reverse_new, reverse_old) for x, y in zip(a, b) if x > y)
            record["boolean_inputs_checked"] = boolean_tables(ops, local, n)
            spliced[entry["frame"]] = record
        survey[entry["frame"]] = record

    frames = sorted(survey)
    receipts = {str(f): survey[f] for f in frames}
    if expected is not None:
        need(frames == expected["survey_frames"], "survey frame set differs")
        need(receipts == expected["survey"], "survey receipts differ")

    candidate = build_word(word, certificate)
    need(len(candidate["B"]) == len(word["B"]) - sum(
        e["original_gates"] - e["minimum"] for e in certificate["blocks"] if e["spliced"]),
         "B length differs from the spliced gate counts")
    need(all(candidate[k] == word[k] for k in word if k not in ("B", "C")), "unrelated field changed")
    need(candidate["C"] == rebuild_cleanup(candidate), "literal cleanup reversal fails")
    before_paths, after_paths = frame_paths(word), frame_paths(candidate)
    need(before_paths == after_paths, "register frame path changed")
    whole_endpoint(word)
    columns = whole_endpoint(candidate)
    checker = load_checker()
    dimensions, labels, flow, hypotheses, conclusion, _ = checker.check(candidate)
    need(all(hypotheses.values()) and all(conclusion.values()), "inherited interface guard fails")
    profile = Counter(dimensions.fdim[b] - dimensions.fdim[a]
                      for path in after_paths for a, b in itertools.pairwise(path))
    profile.update(t["rank"] for t in flow["totals"])
    need(dict(sorted(profile.items())) == {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19},
         "paid profile changed")
    need(sum(k * v for k, v in profile.items()) == 5129, "rank mass changed")

    tmp = Path(out) if out else Path(tempfile.mkdtemp(prefix="bsection-survey-"))
    before_bill, before_records = export_and_bound(word, tmp / "before")
    after_bill, after_records = export_and_bound(candidate, tmp / "after")
    if expected is not None:
        need(before_bill == expected["bill_before"], "before bill differs from receipt")
        need(after_bill == expected["bill_after"], "after bill differs from receipt")
    saved = sum(entry["original_gates"] - entry["minimum"]
                for entry in certificate["blocks"] if entry["spliced"])
    need(before_bill["adds"] - after_bill["adds"] == 2 * saved == 16,
         "ADD saving does not match the spliced gate counts")
    need(before_bill["copies"] == after_bill["copies"] == 9, "retained copy count changed")
    need(before_bill["erasures"] == after_bill["erasures"] == 9, "retained erasure count changed")
    need(after_bill["forward_positive_bound"] == before_bill["forward_positive_bound"] == 49347,
         "forward positive bound changed")
    need(after_bill["reverse_positive_bound"] < before_bill["reverse_positive_bound"] == 1113070,
         "composed reverse positive bound not reduced")
    need(after_bill["payload_bits"] == before_bill["payload_bits"] == 93, "payload bits changed")
    need(Counter(r for r in before_records if r[0] != 1)
         == Counter(r for r in after_records if r[0] != 1), "non-ADD event inventory changed")

    controls = []
    for entry in certificate["blocks"]:
        if not entry["spliced"]:
            continue
        bad = copy.deepcopy(entry["gates"])
        target = next(r for r in entry["registers"]
                      if r != bad[0][1] and r != bad[0][2][0])
        need(target != bad[0][2][0], "no distinct mutation target")
        bad[0][2] = [target]
        controls.append(must_reject(
            "mutated_candidate_source_%d" % entry["frame"],
            lambda bad=bad, entry=entry: bind_block_check(word, entry, bad)))
        controls.append(must_reject(
            "unpaid_gate_%d" % entry["frame"],
            lambda entry=entry: bind_block_check(word, entry, entry["gates"][:-1])))
    first_splice = next(entry for entry in certificate["blocks"] if entry["spliced"])
    for entry in certificate["blocks"]:
        if not entry["spliced"]:
            continue
        blk, ops, forward, n = bind_block(word, entry)
        local, _ = block_model(entry["gates"], entry["registers"])
        reverse_old = integer_map(ops[::-1], n)
        reverse_new = integer_map(local[::-1], n)
        if dominated(reverse_new, reverse_old):
            controls.append(must_reject(
                "inverted_domination_%d" % entry["frame"],
                lambda ro=reverse_old, rn=reverse_new: need(dominated(ro, rn),
                                                           "inverted domination holds")))
        else:
            controls.append(must_reject(
                "forged_domination_%d" % entry["frame"],
                lambda ro=reverse_old, rn=reverse_new: need(dominated(rn, ro),
                                                           "forged domination claim holds")))
    bad_word = copy.deepcopy(candidate)
    bad_word["C"].pop()
    controls.append(must_reject("omitted_cleanup", lambda: whole_endpoint(bad_word)))
    bad_word = copy.deepcopy(candidate)
    first, last = first_splice["slice"]
    del bad_word["B"][first]
    bad_word["C"] = rebuild_cleanup(bad_word)
    controls.append(must_reject("missing_gate_with_matching_cleanup", lambda: whole_endpoint(bad_word)))
    bad_word = copy.deepcopy(candidate)
    bad_word["B"][first][0] = 0
    controls.append(must_reject("illegal_frame_descent", lambda: frame_paths(bad_word)))
    stale = copy.deepcopy(candidate)
    stale["C"] = word["C"]
    whole_endpoint(stale)  # Positive semantic control; rejected only by literal H4.
    controls.append(must_reject("stale_cleanup_literal_H4",
                                lambda: need(stale["C"] == rebuild_cleanup(stale), "H4 fails")))
    bad_cert = copy.deepcopy(certificate)
    bad_cert["blocks"][0] = dict(certificate["blocks"][0],
                                 slice=[certificate["blocks"][0]["slice"][0] + 1,
                                        certificate["blocks"][0]["slice"][1] + 1])
    controls.append(must_reject("wrong_slice_binding",
                                lambda: bind_block(word, bad_cert["blocks"][0])))
    # A forged donor-supply certificate must be rejected by the counting recheck.
    forged = dict(next(entry["witness"] for entry in certificate["blocks"]
                       if entry.get("witness")), demand=1, supply=2)
    infeasible_entry = next(entry for entry in certificate["blocks"] if entry.get("witness"))
    blk, ops, forward, n = bind_block(word, infeasible_entry)
    controls.append(must_reject(
        "forged_supply_witness",
        lambda: need(supply_certificate(forward, forged["row"], forged["col"])
                     == (forged["demand"], forged["supply"]), "forged certificate rejected")))

    return {"status": "PASS_R439_BSECTION_SURVEY", "columns": columns,
            "survey_frames": frames, "spliced_frames": sorted(spliced),
            "survey_receipts": receipts,
            "closed_frames": labels["frames"],
            "copy_ranks": [t["rank"] for t in flow["totals"]],
            "paid_profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": 5129,
            "identical_register_frame_paths": len(after_paths),
            "hypotheses": hypotheses, "conclusion": conclusion,
            "bill_before": before_bill, "bill_after": after_bill,
            "controls_rejected": controls}


def bind_block_check(word, entry, gates):
    """Map equality for a proposed block replacement (negative-control path)."""
    blk, ops, forward, n = bind_block(word, entry)
    local, _ = block_model(gates, entry["registers"])
    need(integer_map(local, n) == forward, "forward integer map differs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None)
    parser.add_argument("--write-expected", action="store_true",
                        help="bootstrap EXPECTED.json receipts from this run")
    args = parser.parse_args()
    if args.write_expected:
        global EXPECTED_MISSING_OK
        EXPECTED_MISSING_OK = True
    result = verify(args.out)
    if args.write_expected:
        expected = {"survey_frames": result["survey_frames"],
                    "spliced_frames": result["spliced_frames"],
                    "survey": result.pop("survey_receipts"),
                    "bill_before": result["bill_before"],
                    "bill_after": result["bill_after"]}
        (HERE / "EXPECTED.json").write_text(json.dumps(expected, indent=1, sort_keys=True) + "\n",
                                            encoding="utf-8")
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

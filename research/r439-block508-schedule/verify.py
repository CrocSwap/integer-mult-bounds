#!/usr/bin/env python3
"""Exact finite verification for the shorter R439 phase-B block-508 circuit.

No search code is imported: the whole-block single-write minimum is rechecked
here with an independently written backward Bellman recursion, and the
candidate's forward integer map, reverse positive map, Boolean tables, splice,
frame paths, paid profile, exact F2 endpoint, inherited H1-H5 interface,
exported scalar bills and positive/payload bounds are all recomputed.

The owning geometry/interface checker is eumemic's PR555/PR589 xcheck_p.py and
the record exporter is Dylan Crow's export_records.py; both are pinned by
SHA-256 and used unmodified.

Prepared with help from opencode. Apache-2.0.
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
    need(certificate["schema"] == "r439-block508-schedule/1", "unknown schema")
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


def bind_and_check_maps(word, certificate):
    binding = certificate["binding"]
    need(binding["source"] == WORD and binding["section"] == "B"
         and binding["frame"] == 508 and binding["slice"] == [205, 242], "wrong binding")
    regs = binding["registers"]
    need(regs == [19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466], "wrong block registers")
    need(certificate["original_gates"] == 37, "wrong original bill")
    old = word["B"][205:242]
    need(len(old) == 37 and all(f == 508 and len(ss) == 1 for f, t, ss in old),
         "source block changed")
    need(sorted({t for _, t, _ in old} | {s for _, _, ss in old for s in ss}) == regs,
         "block touches undeclared wires")
    index = {r: i for i, r in enumerate(regs)}
    original = [(index[t], index[s]) for _, t, (s,) in old]
    gates = certificate["gates"]
    need(len(gates) == 30, "candidate gate count differs")
    need(all(f == 508 and len(ss) == 1 and t in index and ss[0] in index and ss[0] != t
            for f, t, ss in gates), "candidate leaves the single-wire block class")
    new = [(index[t], index[s]) for _, t, (s,) in gates]
    forward_old = integer_map(original, len(regs))
    forward_new = integer_map(new, len(regs))
    need(forward_new == forward_old, "forward integer map differs")
    reverse_old = integer_map(original[::-1], len(regs))
    reverse_new = integer_map(new[::-1], len(regs))
    need(dominated(reverse_new, reverse_old), "reverse positive map not dominated")
    strict = sum(1 for a, b in zip(reverse_new, reverse_old) for x, y in zip(a, b) if x < y)
    need(strict > 0, "reverse map shows no strict improvement")
    need(certificate["forward_total"] == sum(map(sum, forward_old)) == sum(map(sum, forward_new)),
         "forward total receipt differs")
    # Exhaustive Boolean truth tables over the block registers.
    table_hits = 0
    for value in range(1 << len(regs)):
        state_old = [(value >> i) & 1 for i in range(len(regs))]
        state_new = list(state_old)
        for ops, state in ((original, state_old), (new, state_new)):
            for dst, src in ops:
                state[dst] ^= state[src]
        need(state_old == state_new, "Boolean input counterexample: %d" % value)
        table_hits += 1
    return original, new, {"boolean_inputs_checked": table_hits,
                          "reverse_strictly_smaller_entries": strict,
                          "reverse_old_total": sum(map(sum, reverse_old)),
                          "reverse_new_total": sum(map(sum, reverse_new))}


def pack_row(row):
    need(all(type(x) is int and 0 <= x < 16 for x in row), "row entry outside digit range")
    return sum(x << (4 * j) for j, x in enumerate(row))


def backward_minimum(forward):
    """Backward Bellman recursion over realized-row subsets.

    State `done` holds the rows already realized (from the full set downward).
    Realizing row i appends donor additions whose values are final rows for
    donors already done and entry singletons otherwise; each donor is used at
    most once and integer sums must match exactly.  Written independently of
    the forward discovery DP in search.py.
    """
    n = len(forward)
    need(all(forward[i][i] >= 1 for i in range(n)), "missing diagonal")
    rows = [pack_row(row) for row in forward]
    goal = []
    for i in range(n):
        row = list(forward[i])
        row[i] -= 1
        goal.append(pack_row(row))
    size = 1 << n
    infinity = 10 ** 9
    dist = [infinity] * size
    dist[size - 1] = 0
    feasible = 0
    for done in range(size - 2, -1, -1):
        for dst in range(n):
            if done >> dst & 1:
                continue
            want = goal[dst]
            donors = []
            for src in range(n):
                if src == dst:
                    continue
                value = rows[src] if done >> src & 1 else (1 << (4 * src))
                fits = True
                for j in range(n):
                    if ((value >> (4 * j)) & 15) > ((want >> (4 * j)) & 15):
                        fits = False
                        break
                if fits:
                    donors.append(value)
            sums = {0: 0}
            for value in donors:
                for total, cost in list(sums.items()):
                    merged = total + value
                    overflows = False
                    for j in range(n):
                        if ((merged >> (4 * j)) & 15) > ((want >> (4 * j)) & 15):
                            overflows = True
                            break
                    if overflows:
                        continue
                    if merged not in sums:
                        sums[merged] = cost + 1
            if want in sums:
                feasible += 1
                nxt = done | (1 << dst)
                dist[done] = min(dist[done], sums[want] + dist[nxt])
    return {"minimum": dist[0], "states": size,
            "state_destination_pairs": n * (1 << (n - 1)),
            "feasible_edges": feasible,
            "backward_distances_sha256": digest(dist)}


def rebuild_cleanup(word):
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == word["v"])
    return [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if d < word["v"] or d >= 2 * word["v"]]


def build_word(word, certificate):
    need(certificate["binding"]["slice"] == [205, 242], "splice slice mismatch")
    result = copy.deepcopy(word)
    result["B"][205:242] = copy.deepcopy(certificate["gates"])
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


def load_checker():
    spec = importlib.util.spec_from_file_location("block508_original_xcheck", ROOT / CHECKER)
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
    original, new, block = bind_and_check_maps(word, certificate)
    optimality = backward_minimum(integer_map(original, len(certificate["binding"]["registers"])))
    need(optimality["minimum"] == 30 == len(certificate["gates"]) == certificate["forward_minimum"],
         "minimum/gate-count/minimum receipt disagree")
    need(optimality == certificate["backward_optimality"], "backward optimality receipt differs")
    candidate = build_word(word, certificate)
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
    before_bill, before_records = export_and_bound(word, out / "before")
    after_bill, after_records = export_and_bound(candidate, out / "after")
    need(before_bill["adds"] == 24305 and after_bill["adds"] == 24291, "ADD bills differ")
    need(before_bill["copies"] == after_bill["copies"] == 9, "retained copy count changed")
    need(before_bill["erasures"] == after_bill["erasures"] == 9, "retained erasure count changed")
    need(Counter(r for r in before_records if r[0] != 1)
         == Counter(r for r in after_records if r[0] != 1), "non-ADD event inventory changed")
    need(after_bill["forward_positive_bound"] == before_bill["forward_positive_bound"] == 49347,
         "forward positive bound changed")
    need(after_bill["reverse_positive_bound"] == 1086054 <= before_bill["reverse_positive_bound"] == 1113070,
         "reverse positive bound not reduced as certified")
    need(after_bill["payload_bits"] == before_bill["payload_bits"] == 93, "payload bits changed")

    controls = []
    bad = copy.deepcopy(certificate["gates"])
    bad[0][2] = [19] if bad[0][2] != [19] else [27]
    controls.append(must_reject("mutated_candidate_source",
                                lambda: bind_and_check_maps(word, dict(certificate, gates=bad))))
    short = copy.deepcopy(certificate["gates"])[:-1]
    controls.append(must_reject("unpaid_gate",
                                lambda: bind_and_check_maps(word, dict(certificate, gates=short))))
    controls.append(must_reject("inverted_domination",
                                lambda: need(dominated(integer_map(original[::-1], 11),
                                                       integer_map(new[::-1], 11)),
                                             "inverted domination holds")))
    bad_word = copy.deepcopy(candidate)
    bad_word["C"].pop()
    controls.append(must_reject("omitted_cleanup", lambda: whole_endpoint(bad_word)))
    bad_word = copy.deepcopy(candidate)
    del bad_word["B"][205]
    bad_word["C"] = rebuild_cleanup(bad_word)
    controls.append(must_reject("missing_gate_with_matching_cleanup",
                                lambda: whole_endpoint(bad_word)))
    bad_word = copy.deepcopy(candidate)
    bad_word["B"][205][0] = 0
    controls.append(must_reject("illegal_frame_descent", lambda: frame_paths(bad_word)))
    stale = copy.deepcopy(candidate)
    stale["C"] = word["C"]
    whole_endpoint(stale)  # Positive semantic control; rejected only by literal H4.
    controls.append(must_reject("stale_cleanup_literal_H4",
                                lambda: need(stale["C"] == rebuild_cleanup(stale), "H4 fails")))
    bad_cert = copy.deepcopy(certificate)
    bad_cert["binding"] = dict(certificate["binding"], slice=[206, 243])
    controls.append(must_reject("wrong_slice_binding",
                                lambda: bind_and_check_maps(word, bad_cert)))

    return {"status": "PASS_R439_BLOCK508_SCHEDULE", "block": block,
            "backward_optimality": optimality, "columns": columns,
            "closed_frames": labels["frames"],
            "copy_ranks": [t["rank"] for t in flow["totals"]],
            "paid_profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": 5129,
            "identical_register_frame_paths": len(after_paths),
            "hypotheses": hypotheses, "conclusion": conclusion,
            "before": before_bill, "after": after_bill,
            "adds_saved": 14, "new_kappa_claim": False,
            "word_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
            "negative_controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new output directory; must not exist")
    parser.add_argument("--record-expected", type=Path, help="write a NEW expected receipt")
    args = parser.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="r439-block508-") as directory:
            result = verify(Path(directory))
    if args.record_expected:
        with args.record_expected.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        need(result == expected, "deterministic receipt differs from EXPECTED.json")
    if args.out:
        (args.out / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                               encoding="utf-8")
    print("PASS_R439_BLOCK508_SCHEDULE gates=37->30 ADDs=24305->24291 saved=14 "
          "columns=661 controls=8 minimum=30 rank_mass=5129 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Reject, ValueError, OSError) as error:
        raise SystemExit("REJECT: " + str(error)) from error

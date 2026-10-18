"""Finite R480 quad12 construction, exact minimum and complete local accounting.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance; Apache-2.0.
Whole-word checks follow the contracts of PR691/925/952. The record emitter
and set-valued replay below do not import the supplier exporter or search.
"""
import argparse
from collections import Counter
import copy
import gzip
import itertools
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
HERE, ROOT, REGS = C["HERE"], C["ROOT"], C["REGS"]
need, digest, load = C["need"], C["digest"], C["load"]


def same(a, b, message):
    # Reject bool-for-int substitutions and preserve every JSON field.
    need(C["canonical"](a) == C["canonical"](b), message)


def transfer(ops, signed_inverse=False):
    need(type(ops) is list, "gate list")
    columns = []
    for col in range(6):
        values = [int(i == col) for i in range(6)]
        for gate in ops[::-1] if signed_inverse else ops:
            need(type(gate) is list and len(gate) == 2, "gate pair")
            d, s = gate
            need(type(d) is int and type(s) is int and 0 <= d < 6 and 0 <= s < 6 and d != s,
                 "gate indices")
            values[d] += (-1 if signed_inverse else 1) * values[s]
        columns.append(values)
    return [list(row) for row in zip(*columns)]


def local_check(old, new):
    target = transfer(old)
    same(transfer(new), target, "positive integer transfer")
    same(transfer(old, True), transfer(new, True), "signed inverse transfer")
    need({r for op in new for r in op} == set(range(6)), "all six frame paths retained")
    for bits in range(64):
        endpoints = []
        for ops in (old, new):
            values = [(bits >> i) & 1 for i in range(6)]
            for d, s in ops:
                values[d] ^= values[s]
            endpoints.append(values)
            for d, s in ops[::-1]:
                values[d] ^= values[s]
            need(values == [(bits >> i) & 1 for i in range(6)], "local inverse")
        same(*endpoints, "Boolean transfer")
    before, after = transfer(old[::-1]), transfer(new[::-1])
    return {"target_matrix": target, "signed_inverse_matrix": transfer(new, True),
            "reverse_positive_before": before, "reverse_positive_after": after,
            "reverse_increased_entries": sum(y > x for a, b in zip(before, after) for x, y in zip(a, b)),
            "reverse_decreased_entries": sum(y < x for a, b in zip(before, after) for x, y in zip(a, b)),
            "boolean_inputs": 64}


def cleanup(word):
    v = word["v"]
    return [[1, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if not v <= d < 2 * v]


def build(word, witness):
    same({k: witness[k] for k in ("phase", "start", "stop", "frame", "quad", "registers", "assignment_seed")},
         {"phase": "A", "start": 849, "stop": 872, "frame": 314, "quad": 12,
          "registers": REGS, "assignment_seed": 12}, "witness location")
    old = [[REGS.index(d), REGS.index(ss[0])] for _, d, ss in word["A"][849:872]]
    same(witness["original"], old, "witness source operations")
    new = witness["replacement"]
    local = local_check(old, new)
    need(len(new) == 11 and type(witness["minimum"]) is int and witness["minimum"] == 11, "11-gate witness")
    result = copy.deepcopy(word)
    result["A"][849:872] = [[314, REGS[d], [REGS[s]]] for d, s in new]
    result["C"] = cleanup(result)
    return result, local


def rank(rows):
    """Fraction-free row elimination, separate from the exporter's Fractions."""
    a = [list(row) for row in rows]
    pivot = 0
    for col in range(8):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        for i in range(pivot + 1, len(a)):
            if a[i][col]:
                x, y = a[pivot][col], a[i][col]
                a[i] = [x * p - y * q for p, q in zip(a[i], a[pivot])]
        pivot += 1
    return pivot


def frame_paths(word):
    paths = [[f] for f in word["start"]]
    for phase in ("D", "A", "B", "C"):
        for f, d, ss in word[phase]:
            for r in [d, *ss]:
                if paths[r][-1] != f:
                    paths[r].append(f)
    for r, f in enumerate(word["final"]):
        if paths[r][-1] != f:
            paths[r].append(f)
    return paths


def emit(word, dims):
    n, v = 2 * word["v"] + word["R"], word["v"]
    cur = list(word["start"])
    events = []
    paths = [[f] for f in cur]
    hist, counts = Counter(), Counter()

    def move(r, f):
        if cur[r] != f:
            need(set(word["frames"][cur[r]]) <= set(word["frames"][f]), "non-nested frame")
            delta = dims[f] - dims[cur[r]]
            need(delta > 0, "non-increasing climb")
            events.append((0, r, cur[r], f, delta, 0))
            hist[delta] += 1
            cur[r] = f
            paths[r].append(f)

    for phase, number in (("D", 1), ("A", 2), ("scatter", 3), ("B", 4), ("C", 5)):
        if phase == "scatter":
            for k, q in enumerate(word["ret"]):
                events.append((2, q, n, cur[q], 0, dims[cur[q]]))
                hist[dims[cur[q]]] += 1
                events.extend((1, v + i, n, 1, 0, 3) for i, row in enumerate(word["scatter"]) if k in row)
                events.append((3, q, n, cur[q], 0, 0))
        else:
            for f, d, ss in word[phase]:
                need(d not in ss and len(set(ss)) == len(ss), "distinct gate operands")
                for r in [d, *ss]:
                    need(type(r) is int and 0 <= r < n, "register index")
                    move(r, f)
                events.extend((1, d, s, 1, f, number) for s in ss)
    for r, f in enumerate(word["final"]):
        move(r, f)
    counts.update(e[0] for e in events)
    return events, {"ADDs": counts[1], "MOVEs": counts[0], "COPYs": counts[2], "ERASEs": counts[3],
                    "records": len(events), "paid_histogram": dict(sorted(hist.items())),
                    "rank_mass": sum(k * v for k, v in hist.items()), "paths_sha256": digest(paths)}


def replay(word, events):
    n, v = 2 * word["v"] + word["R"], word["v"]
    expected = [{i} if not v <= i < 2 * v else {i, i - v} for i in range(n)] + [set()]
    bounds = []
    for reverse in (False, True):
        columns = [{i} for i in range(n)] + [set()]
        positive = [1] * n + [0]
        active = None
        bound = 1
        for op, a, b, c, f, z in events[::-1] if reverse else events:
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                need(a != b and c == 1 and a < n, "native ADD contract")
                need(b != n or active is not None, "closed temporary read")
                need(a != active, "copied center mutation")
                columns[a] ^= columns[b]
                positive[a] += positive[b]
                bound = max(bound, positive[a])
            elif op == 2:
                need(active is None and b == n and not columns[n], "fresh copy")
                active = a
                columns[n] = set(columns[a])
                positive[n] = positive[a]
            elif op == 3:
                need(active == a and b == n and columns[n] == columns[a], "restore before erase")
                active = None
                columns[n] = set()
                positive[n] = 0
            else:
                raise ValueError("record opcode")
        need(active is None and columns == expected, "all-column dirty endpoint")
        bounds.append(bound)
    f, b = bounds
    payload = 64 * f ** 3 * b ** 2
    need(payload < 1 << 104, "104-bit local prefix cap")
    return {"columns_each_direction": n, "F": f, "B": b, "payload_upper": str(payload),
            "payload_bits": payload.bit_length(), "local_prefix_cap_bits": 104}


def word_contract(word):
    v = word["v"]
    need(word["C"] == cleanup(word), "literal cleanup contract")
    need(all(f == 0 and v <= d < 2*v and all(s >= 2*v for s in ss) for f, d, ss in word["D"]), "D interface")
    need(all(not v <= d < 2*v and all(not v <= s < 2*v for s in ss) for _, d, ss in word["A"]), "A interface")
    need(all(v <= d < 2*v for _, d, _ in word["B"]), "B interface")


def census_shape(programs, independent_count):
    need(type(programs) is list and len(programs) == independent_count, "shortest-program count")
    need(len({C["canonical"](p) for p in programs}) == independent_count, "duplicate shortest program")
    need(all(type(p) is list and len(p) == 11 for p in programs), "shortest-program length")


def shortest_census(original, witness, dims, minimum, selected_bounds):
    census = load(HERE / "MINIMUM-CENSUS.json")
    need(census["format"] == "r480-quad12-shortest-programs/1", "census format")
    same(census["minimum"], 11, "census minimum")
    programs = census["programs"]
    census_shape(programs, minimum["shortest_programs"])
    same(witness["shortest_programs"], len(programs), "DAG/BFS count agreement")
    groups = {}
    for i, program in enumerate(programs):
        local = local_check(witness["original"], program)
        need(local["reverse_increased_entries"] == 3, "every shortest program violates the local reverse guard")
        key = digest(local["reverse_positive_after"])
        group = groups.setdefault(key, {"indices": [], "matrix": local["reverse_positive_after"]})
        group["indices"].append(i)
    reports = []
    for key, group in sorted(groups.items()):
        first = group["indices"][0]
        recipe = copy.deepcopy(witness)
        recipe["replacement"] = programs[first]
        word, _ = build(original, recipe)
        word_contract(word)
        same(frame_paths(word), frame_paths(original), "census exact register frame paths")
        events, bill = emit(word, dims)
        bounds = replay(word, events)
        for name in ("ADDs", "MOVEs", "COPYs", "ERASEs", "paid_histogram", "rank_mass", "paths_sha256"):
            same(bill[name], selected_bounds[name], "census full-word cost/path: " + name)
        same(bounds["F"], selected_bounds["F"], "census forward bound")
        reports.append({"reverse_sha256": key, "reverse_matrix": group["matrix"],
                        "program_count": len(group["indices"]), "representative_index": first, **bounds})
    need(selected_bounds["B"] == min(x["B"] for x in reports), "selected shortest word is not best in reverse bound")

    # This relabeling was found only after the initial fixed-object experiment.
    # The prior circuit/minimum is credited, not claimed as a new discovery.
    peer = load(HERE / "PR1002-WITNESS.json")
    permutation = [2, 3, 1, 4, 0, 5]  # this wire index -> PR1002 wire index
    same([[permutation[d], permutation[s]] for d, s in witness["original"]], peer["original"], "peer ordered-circuit equivalence")
    inverse = [permutation.index(i) for i in range(6)]
    guarded = [[inverse[d], inverse[s]] for d, s in peer["replacement"]]
    prior_check = local_check(witness["original"], guarded)
    need(len(guarded) == 12 and prior_check["reverse_increased_entries"] == 0, "prior 12-gate guard witness")

    # All original R480 quads; this is an overlap check, not another synthesis.
    orbit, offset, quad = [], 0, 0
    target = transfer(witness["original"])
    for frame, items in itertools.groupby(original["A"], lambda gate: gate[0]):
        block = list(items)
        regs = sorted({r for _, d, ss in block for r in [d, *ss]})
        if len(regs) == 6 and len(block) > 8 and all(len(ss) == 1 for _, _, ss in block):
            mat = transfer([[regs.index(d), regs.index(ss[0])] for _, d, ss in block])
            matches = [list(p) for p in itertools.permutations(range(6))
                       if all(target[i][j] == mat[p[i]][p[j]] for i in range(6) for j in range(6))]
            if matches:
                orbit.append({"quad": quad, "frame": frame, "start": offset, "stop": offset + len(block),
                              "permutations": matches})
            quad += 1
        offset += len(block)
    need(quad == 60 and len(orbit) == 1 and orbit[0]["quad"] == 12, "R480 orbit census")
    return {"census_sha256": digest(census), "programs": len(programs), "reverse_classes": reports,
            "reverse_bound_range": [min(x["B"] for x in reports), max(x["B"] for x in reports)],
            "all_shortest_fail_entrywise_guard": True, "all_shortest_fit_complete_local_prefix": True,
            "peer_pr": 1002, "peer_head": "93e1a42c773a73bb55adddf35d71ed6b6c1d5748",
            "peer_index_permutation": permutation, "guarded_minimum": 12,
            "orbit_check": {"quads": quad, "permutations_per_quad": 720, "members": orbit}}


def controls(original, candidate, witness, dims):
    rejected = []

    def reject(name, function, substring):
        try:
            function()
        except ValueError as e:
            need(substring in str(e), "wrong rejection for " + name + ": " + str(e))
            rejected.append(name)
            return
        raise ValueError("control accepted: " + name)

    for i in range(11):
        new = witness["replacement"][:i] + witness["replacement"][i+1:]
        reject("deleted_gate_" + str(i), lambda new=new: local_check(witness["original"], new), "positive integer")
    bad = copy.deepcopy(witness["replacement"])
    bad[0] = [bad[0][0], bad[0][0]]
    reject("self_donor", lambda: transfer(bad), "gate indices")
    bad[0] = [True, 2]
    reject("boolean_index", lambda: transfer(bad), "gate indices")
    # Endpoint-correct stale cleanup must still fail the literal interface/cost contract.
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(original["C"])
    stale_events, stale_cost = emit(stale, dims)
    replay(stale, stale_events)
    need(stale_cost["ADDs"] == 33946, "stale cleanup positive control cost")
    reject("stale_cleanup_endpoint_correct", lambda: word_contract(stale), "literal cleanup")
    missing = copy.deepcopy(candidate)
    missing["C"].pop()
    missing_events, _ = emit(missing, dims)
    reject("omitted_cleanup", lambda: replay(missing, missing_events), "endpoint")
    wrong_frame = copy.deepcopy(candidate)
    wrong_frame["A"][849][0] = 0
    reject("lowered_operation_frame", lambda: emit(wrong_frame, dims), "frame")
    events, _ = emit(candidate, dims)
    erase = next(i for i, e in enumerate(events) if e[0] == 3)
    reject("omitted_erase", lambda: replay(candidate, events[:erase] + events[erase+1:]), "fresh copy")
    # Endpoint equivalence alone accepts a cancelling pair with a 200-bit positive lift.
    inflated = copy.deepcopy(candidate)
    pair = [[314, REGS[0], [REGS[1]]], [314, REGS[1], [REGS[0]]]] * 80
    inflated["A"][849:849] = pair + pair[::-1]
    inflated["C"] = cleanup(inflated)
    word_contract(inflated)
    huge_events, _ = emit(inflated, dims)
    reject("endpoint_correct_precision_overflow", lambda: replay(inflated, huge_events), "prefix cap")
    programs = load(HERE / "MINIMUM-CENSUS.json")["programs"]
    reject("missing_shortest_program", lambda: census_shape(programs[:-1], len(programs)), "count")
    duplicate = [programs[0], *programs[:-1]]
    reject("duplicate_shortest_program", lambda: census_shape(duplicate, len(programs)), "duplicate")
    return {"rejected": rejected, "count": len(rejected), "stale_cleanup_scalar_control_passed": True}


def call(work, name, command):
    with (work / (name + ".log")).open("w") as log:
        result = subprocess.run([str(x) for x in command], stdout=log, stderr=subprocess.STDOUT)
    need(result.returncode == 0, name + " failed; see " + str(work / (name + ".log")))


def run(work, replay_search=False):
    original = C["original_word"]()
    witness = load(HERE / "WITNESS.json")
    candidate, local = build(original, witness)
    # The inherited BFS uses flat byte matrices and does not import the row-DAG search.
    minimum = runpy.run_path(str(HERE / "optimality.py"))["check_minimum"](local["target_matrix"], 11)
    if replay_search:
        call(work, "search", [sys.executable, "-I", "-B", HERE / "search.py"])
    dims = [rank([original["lines"][i] for i in f]) for f in original["frames"]]
    reports = {}
    for name, word in (("original", original), ("candidate", candidate)):
        word_contract(word)
        same(frame_paths(word), frame_paths(original), "exact register frame paths")
        filename = work / (name + ".json.gz")
        filename.write_bytes(gzip.compress(C["canonical"](word), mtime=0))
        events, bill = emit(word, dims)
        bounds = replay(word, events)
        record_dir = work / name / "records"
        call(work, name + "-export", [sys.executable, "-I", "-B", ROOT / C["BIT"] / "export_records.py", filename, record_dir])
        raw = (record_dir / "249-records.bin").read_bytes()
        need(raw == b"".join(struct.pack("<6i", *event) for event in events), "independent record export")
        native_frames = load(record_dir / "frames.json")["frames"]
        same([native_frames[str(i)]["dim"] for i in range(len(dims))], dims, "independent frame ranks")
        call(work, name + "-interface", [sys.executable, "-I", "-B", ROOT / C["BIT"] / "independent/interface.py", filename])
        call(work, name + "-grams", [sys.executable, "-I", "-B", ROOT / C["BIT"] / "checkers/gram_frames.py", record_dir,
                                    "--gram", "e8ham", "--h", "8", "--positive"])
        reports[name] = {"word_sha256": digest(word), **bill, **bounds}
    a, b = reports["original"], reports["candidate"]
    for key in ("MOVEs", "COPYs", "ERASEs", "paid_histogram", "rank_mass", "paths_sha256"):
        same(a[key], b[key], "changed " + key)
    need(a["ADDs"] == 33958 and b["ADDs"] == 33934, "complete ADD saving")
    need(b["F"] == a["F"] and b["B"] < a["B"], "complete positive bounds")
    census = shortest_census(original, witness, dims, minimum, b)
    return {"format": "r480-quad12-exact/1", "classification": "finite construction; fixed-positive-transfer minimum; no new kappa",
            "source_sha256": C["check_sources"]()["execution_inputs"][C["WORD"]]["sha256"],
            "witness_sha256": digest(witness), "local": local, "independent_minimum": minimum,
            "shortest_census": census,
            "words": reports, "negative_controls": controls(original, candidate, witness, dims)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="fresh output directory for all logs and emitted words")
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--replay-search", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r480-quad12-") as temporary:
        work = args.output.resolve() if args.output else Path(temporary) / "run"
        work.mkdir(parents=True, exist_ok=False)
        report = run(work, args.replay_search)
        receipt = HERE / "CERTIFICATE.json"
        if args.write_certificate:
            receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            same(report, load(receipt), "certificate mismatch")
        (work / "RESULT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("PASS_R480_QUAD12 minimum=11 shortest=252 reverse_classes=4 block=23->11 ADDs=33958->33934 columns=720 controls="
              + str(report["negative_controls"]["count"]) + " no_new_kappa")


if __name__ == "__main__":
    main()

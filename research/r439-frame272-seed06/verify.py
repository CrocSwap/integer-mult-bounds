"""Exact finite frame-272 replacement, minimum and native-word checks; no new rate claim.

Adapted from research/r439-frame267-seed01/verify.py by Ross Richardson,
which credits mtpsl PR691; supplier auditor by eumemic and exporter by Dylan Crow.
This adaptation: @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
Python 3.10+, standard library only. No assertions are used for acceptance.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
AUDITOR = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
COMPARISON_WORD = "research/r439-five-wire-prefix/candidate.json.gz"


class Reject(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise Reject(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def matrix(ops, positive=False):
    need(isinstance(ops, list) and all(isinstance(g, list) and len(g) == 2 for g in ops), "invalid gate list")
    # Each column is evolved separately; search.py evolves whole rows.
    cols = []
    for j in range(6):
        values = [int(i == j) for i in range(6)]
        for d, s in ops:
            need(type(d) is int and type(s) is int and 0 <= d < 6 and
                 0 <= s < 6 and d != s, "invalid circuit gate")
            values[d] = values[d] + values[s] if positive else values[d] ^ values[s]
        cols.append(values)
    return [list(r) for r in zip(*cols)]


def circuit_check(old, new):
    need(matrix(old) == matrix(new), "circuit F2 map changed")
    positive = {}
    for direction, a, b in (("forward", old, new), ("reverse", old[::-1], new[::-1])):
        before, after = matrix(a, True), matrix(b, True)
        need(all(y <= x for rr, ss in zip(before, after) for x, y in zip(rr, ss)),
             direction + " positive matrix increased")
        positive[direction] = {"original": before, "replacement": after}
    return positive


def cleanup(w):
    return [[1, d, list(ss)] for _, d, ss in reversed(w["A"] + w["B"])
            if not 111 <= d < 222]


def build(base, recipe):
    need((recipe["phase"], recipe["start"], recipe["stop"], recipe["frame"])
         == ("A", 725, 748, 272), "unexpected circuit location")
    regs = recipe["registers"]
    need(regs == [242, 294, 296, 302, 316, 501], "unexpected circuit registers")
    matrix(recipe["original"])  # Reject malformed indices before binding physical wires.
    original = [[272, regs[d], [regs[s]]] for d, s in recipe["original"]]
    need(base["A"][725:748] == original, "original gate slice mismatch")
    pos = circuit_check(recipe["original"], recipe["replacement"])
    need(pos["forward"]["original"] == pos["forward"]["replacement"], "integer forward map changed")
    need(0 < len(recipe["replacement"]) < 23, "no strict circuit improvement")
    out = copy.deepcopy(base)
    out["A"][725:748] = [[272, regs[d], [regs[s]]] for d, s in recipe["replacement"]]
    out["C"] = cleanup(out)
    return out


def check_overlap(recipe, overlap=None):
    """Replay the transcribed prior local windows, not their complete search packages.

    Archive/certificate hashes in OVERLAP.json identify the comparison sources;
    this routine checks the algebra and composition of their displayed windows.
    """
    if overlap is None:
        overlap = json.loads((HERE / "OVERLAP.json").read_text())
    regs = recipe["registers"]
    need(overlap["format"] == "r439-frame272-overlap-v1" and overlap["comparison_only"] is True
         and overlap["frame"] == 272 and overlap["registers"] == regs, "overlap identity mismatch")
    positive = matrix(recipe["original"], True)
    need(overlap["positive_transfer"] == positive, "overlap positive transfer mismatch")
    versions = overlap["versions"]
    need([v["pr"] for v in versions] == [589, 904, 936, 952], "overlap source order changed")
    need([v["adds"] for v in versions] == [23, 20, 18, 18], "overlap gate counts changed")
    previous = copy.deepcopy(recipe["original"])
    reverse_comparisons = []
    replacement_reverse = matrix(recipe["replacement"][::-1], True)
    baseline_reverse = matrix(recipe["original"][::-1], True)
    for index, version in enumerate(versions):
        need(version["stop"] - version["start"] == version["adds"] == len(version["ops"]),
             "overlap slice length mismatch")
        if index in (1, 2):
            origin = version["parent_frame_start"]
            need(origin == versions[index - 1]["start"], "overlap parent coordinates mismatch")
            upper = len(previous)
            for window in sorted(version["selected_frame272_windows"],
                                 key=lambda x: x["start"], reverse=True):
                lo, hi = window["start"] - origin, window["stop"] - origin
                need(window["frame"] == 272 and window["section"] == "A"
                     and 0 <= lo < hi <= upper, "invalid overlap window")
                upper = lo
                wires = window["registers"]
                need(len(set(wires)) == len(wires) and set(wires) <= set(regs),
                     "invalid overlap wire binding")
                mapped = {}
                for name in ("old", "new"):
                    ops = window[name]
                    need(all(isinstance(g, list) and len(g) == 2 and
                             all(type(r) is int and 0 <= r < len(wires) for r in g)
                             and g[0] != g[1] for g in ops), "invalid overlap gate")
                    mapped[name] = [[regs.index(wires[d]), regs.index(wires[s])] for d, s in ops]
                need(previous[lo:hi] == mapped["old"]
                     and len(mapped["old"]) - len(mapped["new"]) == window["saving"],
                     "overlap source window mismatch")
                previous[lo:hi] = mapped["new"]
        need(previous == version["ops"], "overlap composed circuit mismatch")
        need(matrix(previous, True) == positive, "overlap integer map mismatch")
        previous_reverse = matrix(previous[::-1], True)
        if "reverse_positive_transfer" in version:
            need(version["reverse_positive_transfer"] == previous_reverse,
                 "overlap reverse transfer mismatch")
        increases = [{"row": i, "column": j, "prior": previous_reverse[i][j],
                      "replacement": replacement_reverse[i][j]}
                     for i in range(6) for j in range(6)
                     if replacement_reverse[i][j] > previous_reverse[i][j]]
        reverse_comparisons.append({"pr": version["pr"], "dominated": not increases,
                                    "increased_entries": increases,
                                    "prior_cap_dominated_by_pr589":
                                        all(previous_reverse[i][j] <= baseline_reverse[i][j]
                                            for i in range(6) for j in range(6))})
    record = versions[-1]["frame272_search_record"]
    need(record["old"] == previous and record["frame"] == 272 and record["wires"] == regs
         and record["new"] is None and record["nomination"] is None
         and record["saved_A"] == record["guarded_programs"] == 0,
         "PR952 overlap scope mismatch")
    if "candidate_comparison" in overlap:
        candidate = overlap["candidate_comparison"]
        expected = [{"pr": version["pr"],
                     "forward_add_saving": len(version["ops"]) - len(recipe["replacement"]),
                     "paired_cleanup_add_saving": 2 * (len(version["ops"]) - len(recipe["replacement"])),
                     "reverse_entrywise_dominated": comparison["dominated"],
                     "prior_cap_dominated_by_pr589": comparison["prior_cap_dominated_by_pr589"]}
                    for version, comparison in zip(versions, reverse_comparisons)]
        need(candidate["adds"] == len(recipe["replacement"])
             and candidate["reverse_positive_transfer"] == replacement_reverse
             and candidate["by_prior"] == expected, "overlap candidate comparison mismatch")
    need(all(row["dominated"] and row["prior_cap_dominated_by_pr589"]
             for row in reverse_comparisons), "prior reverse cap comparison failed")
    return {"sources": overlap, "this_frame272_adds": len(recipe["replacement"]),
            "frame_local_gate_count_difference_vs_pr936_with_cleanup":
                2 * (len(previous) - len(recipe["replacement"])),
            "reverse_comparisons": reverse_comparisons,
            "composition_claim": "No complete shortened prior word composed; full-word replay uses PR589 only"}


def paths(w):
    result = [[f] for f in w["start"]]
    for sec in ("D", "A", "B", "C"):
        for f, d, ss in w[sec]:
            for r in [d] + ss:
                if result[r][-1] != f:
                    result[r].append(f)
    for r, f in enumerate(w["final"]):
        if result[r][-1] != f:
            result[r].append(f)
    return result


def audit(w, module, geometry):
    # Geometry is unchanged; reuse the baseline's already checked exact spaces.
    obj = copy.copy(geometry)
    obj.w = w
    result = obj.full()
    h, c, _ = obj.interface()
    need(all(h.values()) and all(c.values()), "interface H1-H5 or decomposition failed")
    need(result["columns"] == 661, "incomplete dirty-column replay")
    result["interface_hypotheses"] = h
    result["interface_conclusions"] = c
    return result


def records_check(directory, word):
    """Independent set-valued interpreter of the actual exported instructions.

    This checks the scalar projection and literal MOVE/COPY/ERASE lifecycle,
    not the multistage formal-column or hosted-recursion contracts.
    """
    raw = (directory / "249-records.bin").read_bytes()
    need(len(raw) % 24 == 0, "truncated record")
    records = list(struct.iter_unpack("<6i", raw))
    dim = {int(k): v["dim"] for k, v in
           json.loads((directory / "frames.json").read_text())["frames"].items()}
    frames = list(word["start"]) + [None]
    values = [{i} for i in range(661)] + [set()]
    pths = [[f] for f in frames[:661]]
    hist, counts, adds_by_phase = Counter(), Counter(), Counter()
    for op, a, b, c, d, e in records:
        counts[op] += 1
        if op == 0:
            need(0 <= a < 661 and b in dim and c in dim and frames[a] == b
                 and dim[c] - dim[b] == d and d > 0 and e == 0,
                 "bad MOVE")
            need(set(word["frames"][b]) <= set(word["frames"][c]), "MOVE not nested")
            frames[a] = c
            pths[a].append(c)
            hist[d] += 1
        elif op == 1:
            need(0 <= a < 661 and 0 <= b <= 661 and a != b and c == 1
                 and d in dim and frames[a] == frames[b] == d and e in (1, 2, 3, 4, 5),
                 "bad ADD frame")
            adds_by_phase[e] += 1
            values[a] = values[a].symmetric_difference(values[b])
        elif op == 2:
            need(0 <= a < 661 and b == 661 and not values[b] and frames[b] is None
                 and c in dim and frames[a] == c,
                 "COPY lifecycle")
            need(d == 0 and e == dim[c], "COPY rank")
            values[b] = set(values[a])
            frames[b] = d
            hist[e] += 1
        elif op == 3:
            need(0 <= a < 661 and b == 661 and frames[a] == c and frames[b] == d == 0
                 and e == 0 and values[b] == values[a], "ERASE lifecycle")
            values[b] = set()
            frames[b] = None
        else:
            raise Reject("unknown record opcode")
    expected = [{i} if not 111 <= i < 222 else {i, i - 111} for i in range(661)]
    need(values[:661] == expected and not values[661], "record dirty-column endpoint")
    need(frames[:661] == word["final"] and frames[661] is None, "record frame endpoint")
    need(pths == paths(word), "record frame paths differ")
    return {"records": len(records), "adds": counts[1], "moves": counts[0],
            "adds_by_phase": dict(sorted(adds_by_phase.items())),
            "copies": counts[2], "erasures": counts[3],
            "paid_histogram": dict(sorted(hist.items())),
            "rank_mass": sum(k * v for k, v in hist.items()),
            "records_sha256": sha(raw)}


def rejected(label, fn, exceptions):
    try:
        fn()
    except exceptions:
        return label
    raise Reject("negative control accepted: " + label)


def run(output, write_certificate):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(set(pins["execution_inputs"]) == {WORD, AUDITOR, EXPORTER, COMPARISON_WORD},
         "incomplete execution source pins")
    for path in pins["execution_inputs"]:
        pin = pins["files"][path]
        need(sha((ROOT / path).read_bytes()) == pin["sha256"], "source hash mismatch: " + path)
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    need(base["v"] == 111 and base["R"] == 439 and len(base["start"]) == 661, "word dimensions")
    recipe = json.loads((HERE / "WITNESS.json").read_text())
    spec_search = importlib.util.spec_from_file_location("nomination", HERE / "search.py")
    search = importlib.util.module_from_spec(spec_search)
    spec_search.loader.exec_module(search)
    found = search.nominate(search.original_ops())
    expected_recipe = {"phase": "A", "start": 725, "stop": 748, "frame": 272,
                       "registers": search.REGS, "assignment_seed": 6,
                       "original": search.original_ops(), **found}
    need(recipe == expected_recipe, "nomination metadata or witness mismatch")
    # BFS checker evolves flat matrices and does not import nomination code.
    spec_opt = importlib.util.spec_from_file_location("independent_minimum", HERE / "optimality.py")
    opt = importlib.util.module_from_spec(spec_opt)
    spec_opt.loader.exec_module(opt)
    optimum = opt.check_minimum(matrix(recipe["original"], True), recipe["minimum"])
    need(recipe["minimum"] == len(recipe["unconstrained_replacement"]) == 11,
         "wrong unconstrained witness length")
    need(matrix(recipe["unconstrained_replacement"], True) == matrix(recipe["original"], True),
         "unconstrained witness integer map mismatch")
    need(recipe["reverse_guard"]["minimum"] == len(recipe["replacement"]) == 12,
         "wrong guarded witness length")
    guarded = opt.check_reverse_guard_exclusion(matrix(recipe["original"], True),
                                                matrix(recipe["original"][::-1], True), through=11)
    revised = build(base, recipe)
    overlap = check_overlap(recipe)
    positive = circuit_check(recipe["original"], recipe["replacement"])
    need(positive["forward"]["original"] == positive["forward"]["replacement"],
         "integer forward map changed")
    need(paths(base) == paths(revised), "physical frame path changed")

    spec = importlib.util.spec_from_file_location("predecessor_xcheck", ROOT / AUDITOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    geometry, labels, baseline, h, c, _ = module.check(base)
    need(all(h.values()) and all(c.values()), "baseline interface failed")
    revised_audit = audit(revised, module, geometry)

    # Independent exhaustive evaluation of the six-register Boolean map.
    for bits in range(64):
        endings = []
        for gates in (recipe["original"], recipe["replacement"]):
            value = bits
            for d, s in gates:
                value ^= ((value >> s) & 1) << d
            endings.append(value)
        need(endings[0] == endings[1], "exhaustive six-bit map differs")

    evidence = {}
    for name, word in (("original", base), ("replacement", revised)):
        path = output / (name + ".json.gz")
        path.write_bytes(gzip.compress(canonical(word), mtime=0))
        directory = output / name / "records"
        subprocess.run([sys.executable, "-B", str(ROOT / EXPORTER), str(path), str(directory)],
                       check=True, capture_output=True, text=True)
        evidence[name] = records_check(directory, word)
    a, b = evidence["original"], evidence["replacement"]
    saving = 2 * (23 - len(recipe["replacement"]))
    need(a["adds"] == 24305 and b["adds"] == 24305 - saving, "unexpected native ADD count")
    for key in ("moves", "copies", "erasures", "paid_histogram", "rank_mass"):
        need(a[key] == b[key], "native cost changed: " + key)
    need(b["rank_mass"] == 5129 and b["copies"] == 9, "incorrect native cost")

    controls = []
    fail = (Reject, module.Reject)
    controls.append(rejected("drop circuit gate", lambda: circuit_check(
        recipe["original"], recipe["replacement"][1:]), fail))
    wrong = copy.deepcopy(recipe["replacement"])
    wrong[0].reverse()
    controls.append(rejected("reverse circuit operand", lambda: circuit_check(
        recipe["original"], wrong), fail))
    inflated = recipe["replacement"] + [[0, 1], [0, 1]]
    need(matrix(inflated) == matrix(recipe["replacement"]), "inflation control is not F2-neutral")
    controls.append(rejected("F2-neutral positive-cost inflation", lambda: circuit_check(
        recipe["original"], inflated), fail))
    bad = copy.deepcopy(revised)
    bad["C"].pop()
    controls.append(rejected("dropped cleanup", lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad["C"] = copy.deepcopy(base["C"])
    # Same endpoint but not the literal reverse required by H4.
    obj = copy.copy(geometry)
    obj.w = bad
    obj.full()
    controls.append(rejected("nonliteral original cleanup", lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad["A"][725][0] = 0
    controls.append(rejected("illegal lower frame", lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad["D"][0][2].pop()
    controls.append(rejected("missing dirty compensation", lambda: audit(bad, module, geometry), fail))

    # The record endpoint checker must see literal instruction corruption too.
    directory = output / "replacement" / "records"
    rawpath = directory / "249-records.bin"
    raw = rawpath.read_bytes()
    recs = list(struct.iter_unpack("<6i", raw))
    for i, rec in enumerate(recs):
        if rec[0] == 1 and rec[5] == 2 and rec[4] == 272:
            rawpath.write_bytes(raw[:24*i] + raw[24*(i+1):])
            break
    else:
        raise Reject("no exported frame272 ADD found for control")
    try:
        controls.append(rejected("dropped exported frame272 ADD", lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)
    erased = next(i for i, rec in enumerate(recs) if rec[0] == 3)
    rawpath.write_bytes(raw[:24*erased] + raw[24*(erased+1):])
    try:
        controls.append(rejected("dropped exported ERASE", lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)

    cert = {"status": "PASS_R439_FRAME272", "frame": 272, "old_gates": 23, "new_gates": len(recipe["replacement"]),
            "saved_with_cleanup": saving, "labels": labels, "columns": revised_audit["columns"],
            "old_phase_gates": baseline["gates"], "new_phase_gates": revised_audit["gates"],
            "interface_hypotheses": revised_audit["interface_hypotheses"],
            "interface_conclusions": revised_audit["interface_conclusions"],
            "boolean_inputs": 64, "F2_matrix": matrix(recipe["replacement"]),
            "positive_matrices": positive, "native_records": evidence,
            "physical_frame_paths_sha256": sha(canonical(paths(revised))),
            "reconstructed_word_sha256": sha(canonical(revised)), "controls_rejected": controls,
            "independent_optimality": optimum, "independent_guard_exclusion": guarded,
            "guarded_minimum": 12, "overlap_comparison": overlap,
            "kappa_claim": "none; unchanged paid rank profile, no hosted replay"}
    path = HERE / "CERTIFICATE.json"
    if write_certificate:
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(cert) == canonical(json.loads(path.read_text())), "certificate mismatch")
    print(f"PASS_R439_FRAME272 gates=23->{len(recipe['replacement'])} "
          f"native_adds=24305->{b['adds']} columns=661 rank_mass=5129 controls={len(controls)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for reconstructed word and records")
    parser.add_argument("--write-certificate", action="store_true", help="regenerate this package's certificate")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-frame272-") as temporary:
            run(Path(temporary), args.write_certificate)


if __name__ == "__main__":
    main()

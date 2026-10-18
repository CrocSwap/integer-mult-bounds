#!/usr/bin/env python3
"""Source-acquisition certificate and all-input replay for the fixed P104 Y0 word.

Imports neither the builder nor any predecessor executable.
Prepared for commdata2338, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WITNESS = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def span(generators):
    values = {0}
    for b in generators:
        require(type(b) is int and 0 <= b < 512, "invalid binary vector")
        values.update(x ^ b for x in tuple(values))
    return frozenset(values)


def dim(frame):
    require(len(frame) & (len(frame) - 1) == 0, "invalid subspace size")
    return len(frame).bit_length() - 1


def add_row(dst, src, coefficient):
    for k, value in src.items():
        changed = dst.get(k, Fraction(0)) + coefficient * value
        if changed:
            dst[k] = changed
        else:
            dst.pop(k, None)


def read_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    inputs = {}
    for pin in pins["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            require(sha256(raw).hexdigest() == pin["sha256"], "source hash mismatch")
            inputs[pin["path"]] = json.loads(raw)
    require(set(inputs) == {WITNESS, FIXTURE}, "input inventory mismatch")
    return inputs[WITNESS], inputs[FIXTURE]


def gram_matrix(fixture):
    # Doubled coordinates of the 120 canonically oriented E8 root lines.
    roots = []
    for a, b in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[a], row[b] = 2, sign
            roots.append(tuple(row))
    roots.extend((1,) + signs for signs in product((-1, 1), repeat=7)
                 if sum(s < 0 for s in signs) % 2 == 0)
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(x) for x in puncture["F0"] + puncture["C"]}
    require(len(set(roots)) == 120 and len(removed) == 16 and removed <= set(roots),
            "invalid root fixture")
    ports = sorted(set(roots) - removed)
    require(len(ports) == 104, "port count")
    return [[Fraction(sum(x * y for x, y in zip(r, s)), 4) for s in ports]
            for r in ports]


def source_paths(word):
    histories = {r: [(0, span(b))] for r, b in word["initial_frames"].items()
                 if r.startswith(("X", "Y"))}
    for index, event in enumerate(word["program"]):
        if event[0] == "transport" and event[1] in histories:
            _, r, before, after, rank = event
            a, b = span(before), span(after)
            require(histories[r][-1][1] == a and a < b, "data path not nested")
            require(type(rank) is int and rank == dim(b) - dim(a), "path rank mismatch")
            histories[r].append((index + 1, b))
    return histories


def acquisition_certificate(paths, gram):
    """Check the premises of the README's source-causal-path argument."""
    target = paths["Y0"]
    endpoint = target[-1][1]
    require(dim(endpoint) == 8 and all(f <= endpoint for _, f in target), "target path")
    support = [s for s in range(104) if Fraction(s == 0) - gram[0][s] / 2]
    require(len(support) == 48, "correction support")
    seen, witnesses = set(), []
    for s in support:
        path = paths[f"X{s}"]
        line = path[0][1]
        require(dim(line) == 1 and line <= endpoint, "source initial line")
        q = next(x for x in line if x)
        require(q not in seen, "repeated source line")
        seen.add(q)
        require(len(path) >= 2 and not path[1][1] <= endpoint, "source can expand inside target")
        require(all(not f <= endpoint for _, f in path[1:]), "source returns inside target")
        require(all(line != f for _, f in target), "direct source-target contact")
        witnesses.append({"source": s, "label": q,
                          "first_transport_event": path[1][0] - 1,
                          "escape_vector": min(path[1][1] - endpoint)})
    require(support == [s for s in range(104)
                        if paths[f"X{s}"][0][1] <= endpoint], "support/frame binding")
    return support, witnesses


def check_cover(candidate, paths, support):
    require(candidate["schema_version"] == 1 and candidate["target"] == 0, "candidate scope")
    require(candidate["cover_normals"] == [1, 4], "cover normals changed")
    h = paths["Y0"][-1][1]
    rooms = [frozenset(v for v in h if (v & n).bit_count() % 2 == 0)
             for n in candidate["cover_normals"]]
    require(all(dim(k) == 7 for k in rooms) and rooms[0] != rooms[1], "invalid cover rooms")
    groups = candidate["groups"]
    require(len(groups) == 2 and all(len(g) == 24 for g in groups), "group sizes")
    require(sorted(groups[0] + groups[1]) == support, "group source partition")
    for group, room in zip(groups, rooms):
        require(all(paths[f"X{s}"][0][1] <= room for s in group), "source outside cover room")
    expected = {f"N{s}" for s in support}
    require(set(candidate["initial_frames"]) == set(candidate["final_frames"]) == expected,
            "helper inventory")
    require(all(span(b) == {0} for b in candidate["initial_frames"].values()), "helper entrance")
    require(all(len(span(b)) == 512 for b in candidate["final_frames"].values()), "helper exit")
    return rooms


def splice(word, candidate):
    require(not set(word["initial_frames"]) & set(candidate["initial_frames"]), "register alias")
    require([b["completed_cut"] for b in candidate["insertions"]] == [0, 3467], "insertion cuts")
    require(word["program"][3466][0:2] == ["transport", "Y0"], "delivery cut binding")
    initial = dict(word["initial_frames"], **candidate["initial_frames"])
    final = dict(word["final_frames"], **candidate["final_frames"])
    by_cut = {b["completed_cut"]: b["events"] for b in candidate["insertions"]}
    program = []
    for cut in range(len(word["program"]) + 1):
        program.extend((True, e) for e in by_cut.get(cut, []))
        if cut < len(word["program"]):
            program.append((False, word["program"][cut]))
    return initial, final, program


def replay(initial, final, program, restricted=False):
    """Sparse Fraction rows on every independent input, including helper dirt."""
    frames = {r: span(b) for r, b in initial.items()}
    rows = {r: {r: Fraction(1)} for r in initial}
    profile, additions, coeffs = Counter(), 0, Counter()
    arrivals, writers = [], []
    endpoint = span(final["Y0"])
    for added, event in program:
        op = event[0]
        if added and restricted:
            require(op in {"add", "transport"}, "forbidden added operation")
        if op == "add":
            _, dst, src, coefficient, chart = event
            require(dst != src and dst in rows and src in rows, "invalid ADD operands")
            require(frames[dst] == frames[src] == span(chart), "ADD frame mismatch")
            require(not dst.startswith("X") and not src.startswith("Y"), "X/Y direction violation")
            if added and restricted:
                require(dst == "Y0" or dst.startswith("N"), "forbidden added destination")
                require(src.startswith(("X", "N")), "forbidden added source")
            c = Fraction(coefficient)
            add_row(rows[dst], rows[src], c)
            if added:
                additions += 1
                coeffs[str(c)] += 1
                if dst == "Y0" and frames[dst] == endpoint:
                    writers.append(src)
        elif op == "transport":
            _, reg, before, after, rank = event
            a, b = span(before), span(after)
            require(reg in frames and frames[reg] == a, "transport entrance mismatch")
            require(a < b or b < a, "transport not strictly nested")
            require(type(rank) is int and rank == abs(dim(b) - dim(a)), "transport rank mismatch")
            if added:
                require(reg.startswith("N") and a < b, "added transport not monotone helper")
                profile[rank] += 1
                if b == endpoint:
                    arrivals.append(reg)
            frames[reg] = b
        elif op == "zero":
            _, reg, chart = event
            require(reg == "C" and reg not in frames, "private allocation")
            frames[reg], rows[reg] = span(chart), {}
        elif op == "copy":
            _, dst, src, chart = event
            require(dst == "C" and not rows[dst], "private copy destination")
            require(frames[dst] == frames[src] == span(chart), "COPY frame mismatch")
            rows[dst] = dict(rows[src])
        elif op == "erase":
            _, reg, chart = event
            require(reg == "C" and frames[reg] == span(chart), "private discard")
            del frames[reg], rows[reg]
        else:
            raise Invalid("unknown operation")
    require(frames == {r: span(b) for r, b in final.items()}, "final frames differ")
    return rows, {"paid_profile": dict(sorted(profile.items())),
                  "rank_mass": sum(r * n for r, n in profile.items()),
                  "transports": sum(profile.values()), "scalar_additions": additions,
                  "scalar_coefficients": dict(sorted(coeffs.items())),
                  "endpoint_arrivals": arrivals, "endpoint_writers": writers}


def check_endpoint(rows, initial, gram, corrected):
    require(set(rows) == set(initial), "final inventory differs")
    for reg in initial:
        expected = {reg: Fraction(1)}
        if reg.startswith("Y"):
            t = int(reg[1:])
            for s in range(104):
                c = Fraction(t == s) if corrected and t == 0 else gram[t][s] / 2
                if c:
                    expected[f"X{s}"] = c
        require(rows[reg] == expected, "endpoint mismatch: " + reg)


def run_candidate(word, candidate, gram):
    initial, final, program = splice(word, candidate)
    rows, invoice = replay(initial, final, program, restricted=True)
    check_endpoint(rows, initial, gram, True)
    return rows, invoice


def expect_rejection(fn, prefix):
    try:
        fn()
    except Invalid as exc:
        require(str(exc).startswith(prefix), "unexpected control failure: " + str(exc))
        return
    raise Invalid("control accepted: " + prefix)


def controls(word, candidate, gram, paths, support):
    out = []
    for label, predicate in [
        ("missing_initial_dirty_compensation", lambda e: e[:3] == ["add", "Y0", "N2"] and e[4] == []),
        ("missing_source_capture", lambda e: e[:3] == ["add", "N2", "X2"] and e[4] == [228]),
        ("missing_dirty_unmerge", lambda e: e[:4] == ["add", "N2", "N4", -1]),
        ("missing_source_cleanup", lambda e: e[:3] == ["add", "N4", "X4"] and e[4] == list(1 << j for j in range(9))),
    ]:
        bad = deepcopy(candidate)
        matches = [(block, i) for block in bad["insertions"]
                   for i, e in enumerate(block["events"]) if predicate(e)]
        require(len(matches) == 1, "ambiguous omission control")
        block, index = matches[0]
        block["events"].pop(index)
        expect_rejection(lambda: run_candidate(word, bad, gram), "endpoint mismatch")
        out.append(label)
    bad = deepcopy(candidate)
    event = next(e for b in bad["insertions"] for e in b["events"] if e[:3] == ["add", "N2", "X2"])
    event[2] = "X4"
    expect_rejection(lambda: run_candidate(word, bad, gram), "ADD frame mismatch")
    out.append("wrong_source_frame")
    bad = deepcopy(candidate)
    event = next(e for b in bad["insertions"] for e in b["events"] if e[0] == "transport")
    event[4] += 1
    expect_rejection(lambda: run_candidate(word, bad, gram), "transport rank mismatch")
    out.append("wrong_transport_invoice")
    # Test timing semantically, bypassing splice's fixed-cut schema check.
    initial, final, _ = splice(word, candidate)
    misplaced = [(True, e) for e in candidate["insertions"][0]["events"]]
    misplaced += [(False, e) for e in word["program"][:3466]]
    misplaced += [(True, e) for e in candidate["insertions"][1]["events"]]
    misplaced += [(False, e) for e in word["program"][3466:]]
    expect_rejection(lambda: replay(initial, final, misplaced, True), "ADD frame mismatch")
    out.append("delivery_one_original_event_early")
    bad_paths = deepcopy(paths)
    bad_paths["X2"][1] = (bad_paths["X2"][1][0], span([228, 196]))
    expect_rejection(lambda: acquisition_certificate(bad_paths, gram), "source can expand inside target")
    out.append("source_expansion_inside_endpoint")
    bad = deepcopy(candidate)
    bad["groups"][0][0], bad["groups"][1][0] = bad["groups"][1][0], bad["groups"][0][0]
    expect_rejection(lambda: check_cover(bad, paths, support), "source outside cover room")
    out.append("wrong_hyperplane_assignment")
    relaxed_source_path_control()
    out.append("positive_relaxed_source_paths_one_helper_two_sources")
    return out


def relaxed_source_path_control():
    """Labels alone do not force the acquisition bound."""
    initial = {"X0": [1], "X1": [2], "Y0": [], "N0": []}
    final = {r: [1, 2] for r in initial}
    events = [["add", "Y0", "N0", -1, []],
              ["transport", "X0", [1], [1, 2], 1],
              ["transport", "X1", [2], [1, 2], 1],
              ["transport", "N0", [], [1, 2], 2],
              ["add", "N0", "X0", 1, [1, 2]],
              ["add", "N0", "X1", 1, [1, 2]],
              ["transport", "Y0", [], [1, 2], 2],
              ["add", "Y0", "N0", 1, [1, 2]],
              ["add", "N0", "X0", -1, [1, 2]],
              ["add", "N0", "X1", -1, [1, 2]]]
    rows, _ = replay(initial, final, [(False, e) for e in events])
    require(rows["Y0"] == {"Y0": 1, "X0": 1, "X1": 1}, "relaxed source positive endpoint")
    require(rows["N0"] == {"N0": 1}, "relaxed source positive restoration")


def calculate():
    word, fixture = read_inputs()
    candidate = json.loads((HERE / "CIRCUIT.json").read_text())
    require(candidate["source_witness_sha256"] == sha256((ROOT / WITNESS).read_bytes()).hexdigest(),
            "candidate source binding")
    gram = gram_matrix(fixture)
    paths = source_paths(word)
    support, witnesses = acquisition_certificate(paths, gram)
    rooms = check_cover(candidate, paths, support)
    baseline, _ = replay(word["initial_frames"], word["final_frames"],
                         [(False, e) for e in word["program"]])
    check_endpoint(baseline, word["initial_frames"], gram, False)
    rows, invoice = run_candidate(word, candidate, gram)
    require(invoice["paid_profile"] == {1: 52, 2: 46, 6: 48}, "unexpected added profile")
    require(invoice["scalar_additions"] == 238 and invoice["rank_mass"] == 432,
            "unexpected added invoice")
    require(invoice["endpoint_arrivals"] == invoice["endpoint_writers"] == ["N2", "N7"],
            "two-arrival contract")
    baseline_profile = Counter(e[4] for e in word["program"] if e[0] == "transport")
    combined_profile = baseline_profile + Counter(invoice["paid_profile"])
    require(sum(r * n for r, n in baseline_profile.items()) == 2368, "baseline rank mass")
    serialized_rows = {r: {k: str(v) for k, v in sorted(row.items())}
                       for r, row in sorted(rows.items())}
    return {"schema_version": 1, "status": "PASS_P104_Y0_SOURCE_ACQUISITION",
            "scope": "Sharp 48-lifetime Y0 acquisition bound in the stated monotone model; local common-chart word only; no supplier or kappa claim.",
            "target": 0, "minimum_helper_lifetimes": 48,
            "source_support": support, "source_escape_witnesses": witnesses,
            "target_frame_cuts": [cut for cut, _ in paths["Y0"]],
            "cover_normals": [1, 4], "cover_dimensions": [dim(k) for k in rooms],
            "groups": candidate["groups"], "added_invoice": invoice,
            "combined_paid_profile": dict(sorted(combined_profile.items())),
            "combined_rank_mass": sum(r * n for r, n in combined_profile.items()),
            "combined_events": len(word["program"]) + sum(len(b["events"]) for b in candidate["insertions"]),
            "baseline_input_columns": len(word["initial_frames"]), "candidate_input_columns": len(rows),
            "full_endpoint_sha256": sha256(json.dumps(serialized_rows, sort_keys=True,
                                                       separators=(",", ":")).encode()).hexdigest(),
            "controls": controls(word, candidate, gram, paths, support)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the verified receipt exclusively to a new file")
    args = parser.parse_args()
    result = calculate()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    require(json.loads(payload) == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
    if args.out:
        with args.out.open("x", encoding="utf-8") as f:
            f.write(payload)
    print("PASS_P104_Y0_SOURCE_ACQUISITION lifetimes=48 arrivals=2 columns=328 added_rank=432 added_ADD=238 controls=10 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from exc

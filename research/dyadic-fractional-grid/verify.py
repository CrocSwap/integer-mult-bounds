"""Exact fractional-grid audit of the fixed PR837 Horner circuits.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
import gzip
import hashlib
import importlib.util
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ("W", 0)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rows = load(HERE / "rows.py", "integer_rows")
need = rows.need


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def payload(path):
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == ".gz" else raw


def read(path):
    return json.loads(payload(path))


def source_pins(root=ROOT):
    pins = read(HERE / "SOURCES.json")
    for item in pins["files"]:
        path = root / item["path"]
        raw = payload(path) if item["encoding"] == "gzip-payload" else path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source pin mismatch: " + item["path"])
    for item in pins["records"]:
        record = read(root / item["path"])
        need(record["audited_source_head"] == item["head"], "checkpoint head mismatch")
        manifest = read(root / record["source_manifest"])
        need(manifest["files"][item["spec"]] == hashlib.sha256((root / item["spec"]).read_bytes()).hexdigest(),
             "checkpoint SPEC binding")
    return pins


def inputs(root=ROOT):
    old = "research/complex-k492-owner-repair/data/SPEC.json"
    base = "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
    for provider in ("ck", "jp8"):
        parts = {name: payload(root / base / provider / name) for name in
                 ("LOCAL-PROGRAMS.json.gz", "CANONICAL-WORD.json.gz")}
        yield provider, read(root / old)["providers"][provider], parts
    archive_path = root / "research/community-frontier741-audit/composed-replay-evidence.tar.gz"
    with tarfile.open(archive_path) as archive:
        parts = {}
        for name in ("LOCAL-PROGRAMS.json.gz", "CANONICAL-WORD.json.gz"):
            members = [m for m in archive.getmembers() if m.name == "complex/local/"+name]
            need(len(members) == 1 and members[0].isfile(), "ambiguous archive member")
            parts[name] = gzip.decompress(archive.extractfile(members[0]).read())
    yield "sw4", read(root / "research/complex-sw4-frame8/data/SPEC.json")["providers"]["gauge44"], parts


def coefficient_trace(q, word):
    target, source = ("T", 0), ("S", 0)
    state = {target: ({0: 1}, 0), source: ({1: 1}, 0), WORK: ({2: 1}, 0)}
    depth, proof = 0, None
    for i, step in enumerate(word):
        need(step[1] in (target, WORK), "source or foreign write")
        e = rows.primitive(step, state)
        if e > depth:
            depth = e
            proof = {"step": i, "register": list(step[1]), **rows.witness(state[step[1]])}
    expected = rows.normalized({0: q.denominator, 1: q.numerator}, q.denominator.bit_length()-1)
    need(state[target] == expected and state[source] == ({1: 1}, 0), "coefficient endpoint")
    need(state[WORK] == ({}, 0), "dirty work remains")
    return depth, proof


def depth_formula(q, method):
    k = q.denominator.bit_length()-1
    if method.endswith("forward"):
        return k
    odd = abs(q.numerator)
    odd >>= (odd & -odd).bit_length()-1
    h = odd.bit_length()-1 if method == "binary-reverse" else (3*odd).bit_length()-2
    return max(h, k)


def program_trace(events, word, spec, orientation, lowering, reverse):
    n = 2*word["v"]+word["R"]
    state = {("L", i): ({i: 1}, 0) for i in range(n)}
    state.update({("C", i): ({n+i: 1}, 0) for i in range(len(word["centers"]))})
    state[WORK] = ({n+len(word["centers"]): 1}, 0)
    peak, proof, count, macros = 0, None, 0, 0
    counts, paid = Counter(), Counter()
    trace = hashlib.sha256()
    for event_id, event in enumerate(events):
        if event[0] in ("climb", "center"):
            paid[event[5] if event[0] == "climb" else event[4]] += 1
        if event[0] != "scalar":
            continue
        _, op, frame = event
        expected = rows.macro(op, state)
        target = tuple(op[1])
        method, circuit = lowering.choose(op, reverse=reverse)
        if op[0] == "add":
            counts[str(Q(op[3], op[4]))] += 1
        for step_id, step in enumerate(circuit):
            need(step[1] in (target, WORK), "foreign program write")
            e = rows.primitive(step, state)
            if e > peak:
                peak = e
                proof = {"event": event_id, "step": step_id, "primitive_index": count,
                         "register": list(step[1]), "frame": frame, "macro": op,
                         "method": method, **rows.witness(state[step[1]])}
            trace.update(canonical([e, step[0], list(step[1])]).encode()+b"\n")
            count += 1
        need(state[target] == expected, "macro endpoint mismatch")
        if op[0] == "add":
            need(state[WORK] == ({}, 0), "macro work not erased")
        macros += 1
    for i in range(n):
        expected = {i: 1}
        if orientation == "forward" and word["v"] <= i < 2*word["v"]:
            expected[i-word["v"]] = 1
        elif orientation == "backward" and i < word["v"]:
            expected[i+word["v"]] = -1
        need(state["L", i] == (expected, 0), "arbitrary-column endpoint mismatch")
    need(all(value == ({}, 0) for reg, value in state.items() if reg[0] != "L"), "private input leak")
    need(dict(paid) == {int(k): v for k, v in spec["expected_profile"].items()}, "paid profile mismatch")
    prior = spec["expected_local"][orientation] if "expected_local" in spec else spec["expected_local."+orientation]
    need(len(events) == prior["events"] and macros == prior["macros"], "program inventory mismatch")
    return {"scalar_projection_guard_bits": peak, "sharpness_witness": proof,
            "real_primitives": 2*count, "native_columns": n, "private_columns": len(state)-n,
            "all_endpoints_match": True, "depth_stream_sha256": trace.hexdigest()}, counts


def verify(root=ROOT):
    pins = source_pins(root)
    lowering = load(HERE / "vendor/pr837/lower.py", "pinned_pr837")
    grid = load(HERE / "fixed_grid.py", "independent_fixed_grid")
    programs, occurrences, full_counterexamples = {}, {}, {}
    all_coefficients = set()
    for provider, spec, parts in inputs(root):
        for name, data in parts.items():
            need(hashlib.sha256(data).hexdigest() == spec["artifact_semantic_sha256"][name], "SPEC payload binding")
        word = json.loads(parts["CANONICAL-WORD.json.gz"])
        for orientation, events in sorted(json.loads(parts["LOCAL-PROGRAMS.json.gz"]).items()):
            need(digest(events) == spec["program_hashes"][orientation], "program digest mismatch")
            key = provider+"/"+orientation
            results = {}
            for reverse, label in ((False, "forward_best"), (True, "bidirectional")):
                results[label], counts = program_trace(events, word, spec, orientation, lowering, reverse)
                results[label]["independent_witness_value"] = grid.check_witness(
                    events, word, lowering, reverse, results[label]["sharpness_witness"])
            old_depth = results["forward_best"]["scalar_projection_guard_bits"]
            new_depth = results["bidirectional"]["scalar_projection_guard_bits"]
            if new_depth > old_depth:
                column = results["bidirectional"]["sharpness_witness"]["input_column"]
                original = grid.program(events, word, orientation, lowering, False, old_depth, column)
                wrong = [grid.program(events, word, orientation, lowering, True, g, column)
                         for g in range(old_depth, new_depth)]
                corrected = grid.program(events, word, orientation, lowering, True, new_depth, column)
                need(original["endpoint_matches"] and original["discarded_halves"] == 0, "original fixed-grid control")
                need(all(not case["endpoint_matches"] for case in wrong), "counterexample failed to change endpoint")
                need(corrected["endpoint_matches"] and corrected["discarded_halves"] == 0, "sufficient guard control")
                full_counterexamples[key] = {"original": original, "undercharged": wrong, "corrected": corrected}
            programs[key] = results
            occurrences[key] = counts
            all_coefficients.update(map(Q, counts))
    coefficients = []
    local_counterexamples = []
    for q in sorted(all_coefficients):
        op = ["add", ["T", 0], ["S", 0], q.numerator, q.denominator]
        old_name, old = lowering.choose(op, reverse=False)
        name, new = lowering.choose(op)
        old_depth, old_proof = coefficient_trace(q, old)
        new_depth, proof = coefficient_trace(q, new)
        candidate_depths = {}
        for method, circuit in lowering.candidates(op).items():
            depth, _ = coefficient_trace(q, circuit)
            need(depth == depth_formula(q, method), "candidate fractional-depth formula")
            candidate_depths[method] = depth
        k = q.denominator.bit_length()-1
        need(old_depth == k, "forward grid formula")
        coefficients.append({"coefficient": str(q), "chosen": name,
                             "forward_depth": old_depth, "bidirectional_depth": new_depth,
                             "extra_bits": new_depth-old_depth, "witness": proof,
                             "all_candidate_depths": candidate_depths,
                             "costs_per_real_component": [len(old), len(new)]})
        if new_depth > old_depth:
            before, old_losses = grid.local(old, old_depth)
            undercharged = [{"guard": g, "result": grid.local(new, g)[0], "discarded_halves": grid.local(new, g)[1]}
                            for g in range(old_depth, new_depth)]
            corrected, losses = grid.local(new, new_depth)
            need(Q(before) == q and old_losses == 0, "local forward grid control")
            need(all(Q(x["result"]) != q for x in undercharged), "local rounded counterexample")
            need(Q(corrected) == q and losses == 0, "local additional-guard control")
            local_counterexamples.append({"coefficient": str(q), "original_result": before,
                                          "undercharged": undercharged, "corrected_result": corrected})
    extras = {r["coefficient"] for r in coefficients if r["extra_bits"] > 0}
    for key, results in programs.items():
        results["extra_grid_occurrences"] = sum(n for q, n in occurrences[key].items() if q in extras)
    paired = {p: {mode: max(programs[p+"/"+orientation][mode]["scalar_projection_guard_bits"]
                            for orientation in ("forward", "backward"))
                  for mode in ("forward_best", "bidirectional")} for p in ("ck", "jp8", "sw4")}
    return {"base_commit": pins["base_commit"], "programs": programs, "coefficients": coefficients,
            "paired_orientation_guard_bits": paired,
            "candidate_circuits_checked": sum(len(r["all_candidate_depths"]) for r in coefficients),
            "whole_program_counterexamples": full_counterexamples,
            "local_rounding_counterexamples": local_counterexamples,
            "extra_grid_coefficients": len(extras), "status": "finite fractional-grid audit; no new kappa",
            "scope": "Exact intermediate representability of scalar primitive projections on dyadic input grids. Frame/phase/child realizations and physical floating-point precision are separate obligations."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="new certificate path; refuses overwrite")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "output already exists")
    result = verify()
    if args.write:
        with args.write.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        need(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "certificate mismatch")
    print("PASS_DYADIC_FRACTIONAL_GRID programs=6 coefficients="+str(len(result["coefficients"]))+
          " extra_grid_coefficients="+str(result["extra_grid_coefficients"])+" kappa=unchanged")


if __name__ == "__main__":
    main()

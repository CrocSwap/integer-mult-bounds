#!/usr/bin/env python3
"""Exact selected two-cut native rank lift; see README for the transcript model.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex
assistance. Apache-2.0. Clifford evaluation reuses Sagar Thakrar's pinned
kernel; the stream audit and rank application below are new.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
PIVOTS = [0, 1, 2, 3, 4, 5, 6, 12]
PHASES = ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
          "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def load(root):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            need(sha((root / row["path"]).read_bytes()) == row["sha256"],
                 "source hash: " + row["path"])
    out = {}
    with tarfile.open(root / ARCHIVE, "r:gz") as archive:
        for key, pin in sources["archive_members"].items():
            members = [m for m in archive.getmembers() if m.name == pin["path"]]
            need(len(members) == 1 and members[0].isfile(), "unique archive member")
            raw = archive.extractfile(members[0]).read()
            need(sha(raw) == pin["sha256"], "member hash: " + key)
            out[key] = json.loads(gzip.decompress(raw) if pin["path"].endswith(".gz") else raw)
    spec = importlib.util.spec_from_file_location("pinned_rank_lift_clifford", root / KERNEL)
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    return out, kernel


def add_into(row, source, coefficient):
    for key, value in list(source.items()):
        new = row.get(key, Q(0)) + coefficient * value
        if new:
            row[key] = new
        else:
            row.pop(key, None)


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0)) for col in zip(*b)]
            for row in a]


def inverse_and_det(matrix):
    n = len(matrix)
    need(n > 0 and all(len(row) == n for row in matrix), "square minor")
    a = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    determinant = Q(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        need(pivot is not None, "singular minor")
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            determinant = -determinant
        v = a[j][j]
        determinant *= v
        a[j] = [x / v for x in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                v = a[i][j]
                a[i] = [x - v*y for x, y in zip(a[i], a[j])]
    inverse = [row[n:] for row in a]
    need(matmul(matrix, inverse) == identity(n), "right inverse")
    need(matmul(inverse, matrix) == identity(n), "left inverse")
    return inverse, determinant


def independent_rows(matrix):
    basis, chosen = {}, []
    for i, original in enumerate(matrix):
        row = [Q(x) for x in original]
        for j, pivot in sorted(basis.items()):
            c = row[j]
            row = [x - c*y for x, y in zip(row, pivot)]
        lead = next((j for j, x in enumerate(row) if x), None)
        if lead is not None:
            v = row[lead]
            basis[lead] = [x/v for x in row]
            chosen.append(i)
    return chosen


def residual_pair(event):
    need(len(event) in (4, 5), "wrapper syntax")
    return event[3], event[4] if len(event) == 5 else 1


def audit_stream(word, events):
    """Check extended labels and replay every arbitrary ordinary input column.

    Labels preS/preW/postT/doneW have the operators defined in README.
    No scalar ADD may cross one of these noncanonical boundary labels.
    """
    v, n = word["v"], 2*word["v"] + word["R"]
    need((word["h"], v, n) == (9, 112, 704), "selected dimensions")
    wrapped = {i for i in range(2*v, n) if (word["start"][i], word["final"][i]) != (0, 1)}
    labels = {("L", i): ("preS", i) if i < v else ("preW", i) if i in wrapped
              else ("T", word["start"][i]) for i in range(n)}
    rows = {("L", i): {i: Q(1)} for i in range(n)}
    phases, conversions, edges, bill = [], Counter(), set(), Counter()
    private_seen = set()
    phase = None
    sources = targets = None
    scatter = {i: [Q(0)]*8 for i in range(v, 2*v)}
    for event in events:
        tag = event[0]
        if tag == "phase":
            phase = event[1]
            phases.append(phase)
            if phase == "centers":
                sources = [dict(rows["L", i]) for i in word["centers"]]
                targets = [dict(rows["L", i]) for i in range(v, 2*v)]
            continue
        if tag == "climb":
            _, part, r, old, new, rank = event
            need(part == phase, "climb phase")
            need(labels["L", r] == ("T", old), "climb source label")
            need(rank == len(word["frames"][new])-len(word["frames"][old]) > 0, "climb rank")
            labels["L", r] = ("T", new)
            edges.add((old, new, rank))
        elif tag == "center":
            _, k, old, new, rank = event
            need(phase == "centers" and labels.get(("C", k)) == ("T", old), "centre source label")
            need(rank == len(word["frames"][old])-len(word["frames"][new]) == 8, "centre rank")
            labels["C", k] = ("T", new)
            edges.add((old, new, rank))
            bill["rank8"] += 1
        elif tag == "adapter":
            _, direction, r, frame = event
            need(direction in ("old_to_new", "new_to_old"), "adapter direction")
            conversions[direction, r] += 1
            if direction == "old_to_new":
                need(phase == "entry_adapters" and frame == word["start"][r], "entry adapter")
                if r < v:
                    need(labels["L", r] == ("preS", r), "source conversion label")
                    labels["L", r] = ("T", frame)
                else:
                    need(labels["L", r] == ("T", 0) and frame == 0, "identity entry")
            else:
                need(phase == "exit_adapters" and frame == word["final"][r], "exit adapter")
                need(labels["L", r] == ("T", frame), "exit conversion label")
                if v <= r < 2*v:
                    labels["L", r] = ("postT", r)
                else:
                    need(frame == 1, "identity exit")
        elif tag == "residual_adapter":
            direction, r = event[1:3]
            a, b = residual_pair(event)
            need(r in wrapped and (a, b) == (word["start"][r], word["final"][r]), "wrapper endpoint binding")
            need(direction in ("pre", "post"), "wrapper direction")
            conversions[direction, r] += 1
            if direction == "pre":
                need(phase == "entry_adapters" and labels["L", r] == ("preW", r), "pre-wrapper label")
                labels["L", r] = ("T", a)
            else:
                need(phase == "full_frame_cleanup" and labels["L", r] == ("T", b), "post-wrapper label")
                labels["L", r] = ("doneW", r)
        elif tag == "scalar":
            _, op, frame = event
            kind, dest = op[0], tuple(op[1])
            if dest[0] == "C" and dest not in private_seen:
                need(kind == "clear", "private initialization")
                private_seen.add(dest)
            if phase == "centers":
                bill[kind] += 1
            if kind == "clear":
                need(dest[0] == "C", "only private roles may clear")
                rows[dest] = {}
                labels[dest] = ("T", frame)
            elif kind == "copy":
                source = tuple(op[2])
                need(dest[0] == "C" and labels[source] == ("T", frame), "copy frame")
                need(phase == "centers" and source == ("L", word["centers"][dest[1]]), "centre carrier binding")
                rows[dest] = dict(rows[source])
                labels[dest] = ("T", frame)
            elif kind == "scale":
                need(labels[dest] == ("T", frame), "scale frame")
                q = Q(op[2], op[3])
                need(q != 0, "invertible scalar scale")
                rows[dest] = {i: q*x for i, x in rows[dest].items()}
            elif kind == "add":
                source = tuple(op[2])
                need(source != dest and labels[dest] == labels[source] == ("T", frame), "common frame")
                q = Q(op[3], op[4])
                add_into(rows[dest], rows[source], q)
                if phase == "centers":
                    need(dest[0] == "L" and v <= dest[1] < 2*v and source[0] == "C" and frame == 0, "scatter shape")
                    scatter[dest[1]][source[1]] += q
            else:
                raise ValueError("unknown scalar")
        else:
            raise ValueError("unknown event")
    need(phases == PHASES, "phase order")
    need(sources is not None and targets is not None, "source cut")
    expected_conversions = Counter()
    for i in range(n):
        if i in wrapped:
            expected_conversions["pre", i] = expected_conversions["post", i] = 1
        else:
            expected_conversions["old_to_new", i] = 1
        if i < 2*v or word["final"][i] == 1:
            expected_conversions["new_to_old", i] = 1
        expected_label = (("T", 1) if i < v else ("postT", i) if i < 2*v else
                          ("doneW", i) if i in wrapped else ("T", 1))
        need(labels["L", i] == expected_label, "final extended label")
        expected = {i: Q(1)}
        if v <= i < 2*v:
            expected[i-v] = Q(1)
        need(rows["L", i] == expected, "complete scalar endpoint")
    need(conversions == expected_conversions, "complete conversion inventory")
    need(private_seen == {("C", i) for i in range(8)}, "private inventory")
    need(all(not row for r, row in rows.items() if r[0] == "C"), "private exit")
    need(bill == Counter(add=176, copy=8, clear=16, rank8=8), "phase invoice")
    need(all(not any(row.get(j, 0) for j in PIVOTS) for row in targets), "targets already carry pivot information")
    source_minor = [[row.get(j, Q(0)) for j in PIVOTS] for row in sources]
    target_ids = [i for i, row in scatter.items() if any(row)]
    return {"source_minor": source_minor, "source_rows": sources,
            "scatter": [scatter[i] for i in target_ids], "target_ids": target_ids,
            "edges": edges, "wrapped": wrapped, "bill": dict(bill),
            "conversions": len(conversions), "scalar_columns": n}


def bind_calls(template, events):
    calls = sorted(template["calls"], key=lambda c: c["time"])[:2]
    need([(c["time"], c["stage"], c["replica"], c["orientation"], c["provider_id"])
          for c in calls] == [(0, 0, 0, "forward", "gauge44"), (1, 0, 8, "forward", "gauge44")], "call pair")
    sweeps = template["execution_schedule"][:2]
    need(len(sweeps) == 2 and all(x["kind"] == "local_cover_sweep" for x in sweeps),
         "uninterrupted first two sweeps")
    for c, sweep in zip(calls, sweeps):
        need(all(c[k] == sweep[k] for k in ("time", "stage", "replica", "provider_id")), "complete-call sweep order")
        need(c["local_program_sha256"] == sha(canonical(events)), "call program binding")
        need(c["window"] == {"local_axes": list(range(9)), "prefix_axes": []}, "stage-zero window")
        owners = [e[0] for e in c["owners"]]
        need(len(owners) == len(set(owners)) == 704, "owner injectivity")
        need(all(e[1] == [1, 0, i % 112] for i, e in enumerate(c["owners"][:224])), "stage-zero data charts")
    sets = [{e[0] for e in c["owners"]} for c in calls]
    shared = sets[0] & sets[1]
    for c in calls:
        need(not shared & {e[0] for e in c["owners"][:224]}, "shared data owner")
    need(len(shared) == 30 and len(sets[0] | sets[1]) == 1378, "selected owner census")
    return calls, sorted(shared)


def check_operators(word, recipes, residuals, audited, C):
    """All-column identities for every forward climb and centre descent.

    The residual tariff identity is not needed for this information bound;
    the literal wrappers must be invertible and attached to their own roles.
    """
    frame = {i: C.canonical_frame(U) for i, U in enumerate(word["frames"])}
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    need(len(children) == len(recipes["children"]), "unique child recipes")
    groups = {}
    for a, b, rank in audited["edges"]:
        r = children.get((a, b))
        need(r is not None and r["rank"] == rank, "used child recipe")
        need(C.well_formed(r["left"]) and C.well_formed(r["right"]), "child monomial")
        small, large = sorted((word["frames"][a], word["frames"][b]), key=len)
        need(C.f2_rank(small+large) == len(large), "nested child frames")
        groups.setdefault(b, []).append(r)
    checked = []
    for b, group in sorted(groups.items()):
        K = max(max(C.c_gates(frame[r["old"]])+r["rank"], C.c_gates(frame[b])) for r in group)
        beta = C.radix(K)
        wanted = C.run(frame[b], beta)
        for r in sorted(group, key=lambda r: r["old"]):
            circuit = frame[r["old"]] + C.monomial(r["right"]) + C.fourier(r["rank"]) + C.monomial(r["left"])
            need(C.equal(C.run(circuit, beta), C.c_gates(circuit), wanted, C.c_gates(frame[b]), beta), "native child identity")
            checked.append([r["old"], b, r["rank"]])
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    need(len(adapters) == len(recipes["endpoint_adapters"]) == 224, "adapter inventory")
    for i, q in enumerate(word["ports"]):
        for role, position in (("source", i), ("target", i+112)):
            rec = adapters[role, i]
            f = word["start"][position] if role == "source" else word["final"][position]
            need(rec["frame"] == f and C.well_formed(rec["left"]), "adapter frame binding")
            old = [("C", q, 1)] if role == "source" else [("C", q, -1)]+C.fourier(9)
            need(C.same_operator(old+C.monomial(rec["left"]), frame[f]), "native data adapter")
    wrapper_keys = set()
    for i in audited["wrapped"]:
        a, b = word["start"][i], word["final"][i]
        key = str(a) if b == 1 else f"{a}:{b}"
        rec = residuals["recipes"][key]
        need(rec["frame"] == a and rec.get("terminal", 1) == b, "wrapper record binding")
        need(C.well_formed(rec["left"]) and C.well_formed(rec["right"]), "invertible wrapper")
        wrapper_keys.add(key)
    for j in PIVOTS:
        need(C.same_operator([("C", word["ports"][j], 1), ("C", word["ports"][j], -1)], []), "input twist inverse")
    return {"used_child_recipes": len(checked), "used_child_keys_sha256": sha(canonical(sorted(checked))),
            "endpoint_adapter_identities": 224, "invertible_wrapper_records": len(wrapper_keys),
            "operator_columns": 512, "input_twist_inverses": 8}, children, adapters


def controls(word, events, template, audited, C, children, adapters):
    passed = []

    def rejected(name, action, reason):
        try:
            action()
        except ValueError as error:
            need(reason in str(error), "unrelated control failure: " + name)
            passed.append(name)
        else:
            raise ValueError("accepted control: " + name)

    j = next(i for i, e in enumerate(events) if e[0] == "climb")
    rejected("omitted_climb", lambda: audit_stream(word, events[:j]+events[j+1:]), "frame")
    bad = deepcopy(events)
    e = next(e for e in bad if e[0] == "scalar" and e[1][0] == "add" and e[2] != 0)
    e[2] = 0
    rejected("wrong_common_frame", lambda: audit_stream(word, bad), "common frame")
    j = events.index(["phase", "full_frame_cleanup"])+1
    rejected("omitted_cleanup_gate", lambda: audit_stream(word, events[:j]+events[j+1:]), "complete scalar endpoint")
    j = events.index(["phase", "B"])-1
    need(events[j][0] == "scalar" and events[j][1][0] == "clear", "clear control fixture")
    rejected("omitted_private_clear", lambda: audit_stream(word, events[:j]+events[j+1:]), "private exit")
    wrong_template = deepcopy(template)
    calls = sorted(wrong_template["calls"], key=lambda c: c["time"])[:2]
    calls[1]["owners"][0][0] = calls[0]["owners"][0][0]
    rejected("shared_source_owner", lambda: bind_calls(wrong_template, events), "shared data owner")
    wrong_schedule = deepcopy(template)
    wrong_schedule["execution_schedule"].insert(1, {"kind": "bridge"})
    rejected("intervening_bridge", lambda: bind_calls(wrong_schedule, events), "uninterrupted first two sweeps")
    singular = deepcopy(audited["source_minor"])
    for row in singular:
        row[-1] = row[0]
    rejected("duplicate_pivot_column", lambda: inverse_and_det(singular), "singular minor")
    a, b, _ = sorted(audited["edges"])[0]
    rec = deepcopy(children[a, b])
    rec["left"]["phase"] = (rec["left"]["phase"]+1) % 4
    bad_circuit = (C.canonical_frame(word["frames"][a])+C.monomial(rec["right"])
                   +C.fourier(rec["rank"])+C.monomial(rec["left"]))
    need(not C.same_operator(bad_circuit, C.canonical_frame(word["frames"][b])), "phase control")
    passed.append("wrong_child_global_phase")
    rec = adapters["source", PIVOTS[0]]
    wrong = [("C", word["ports"][PIVOTS[1]], 1)]+C.monomial(rec["left"])
    need(not C.same_operator(wrong, C.canonical_frame(word["frames"][rec["frame"]])), "wrong port control")
    passed.append("wrong_source_port")
    # For every nonzero 512-address vector v, normalized sources (e0*v,-e0*v)
    # pool to zero but give nonzero separate scatter outputs. Actual inputs
    # are C_q times the coefficients of P^-1 e0.
    pinv, _ = inverse_and_det(audited["source_minor"])
    z = matmul(audited["source_minor"], [[row[0]] for row in pinv])
    need(z == [[Q(i == 0)] for i in range(8)], "encoded centre basis")
    need(any(row[0] for row in matmul(audited["scatter"], z)), "pooled witness scatter")
    need(all(x[0]-x[0] == 0 for x in z), "pooled source sum")
    passed.append("pooled_totals_lose_nonzero_scatter")
    return passed


def run(root):
    data, C = load(root)
    word, events = data["word"], data["programs"]["forward"]
    audited = audit_stream(word, events)
    calls, shared = bind_calls(data["template"], events)
    P = audited["source_minor"]
    Pinv, pdet = inverse_and_det(P)
    selected_rows = independent_rows(audited["scatter"])
    need(len(selected_rows) == 8, "scatter rank eight")
    B = [audited["scatter"][i] for i in selected_rows]
    Binv, bdet = inverse_and_det(B)
    K = matmul(B, P)
    Kinv, kdet = inverse_and_det(K)
    need(kdet == pdet*bdet, "minor determinant product")
    predecessor = json.loads((root / "research/selected-centre-composed-source-rank/RESULT.json").read_text())
    pivot_owners = [c["owners"][j][0] for c in calls for j in PIVOTS]
    need(pivot_owners == predecessor["source_data_pivot_owner_ids"], "predecessor pivot binding")
    native, children, adapters = check_operators(word, data["recipes"], data["residuals"], audited, C)
    passed = controls(word, events, data["template"], audited, C, children, adapters)
    probe_spec = importlib.util.spec_from_file_location("centre_literal_probe", HERE / "native_probe.py")
    probe_module = importlib.util.module_from_spec(probe_spec)
    probe_spec.loader.exec_module(probe_module)
    probe_args = (data["residuals"], PIVOTS, Pinv, audited["scatter"], audited["target_ids"], C)
    direct = probe_module.probe(word, events, data["recipes"], *probe_args)
    bad_recipes = deepcopy(data["recipes"])
    descent = next(r for r in bad_recipes["children"]
                   if (r["old"], r["new"]) == (word["center_frames"][0], 0))
    descent["left"]["phase"] = (descent["left"]["phase"]+1) % 4
    try:
        probe_module.probe(word, events, bad_recipes, *probe_args)
    except ValueError as error:
        need("direct native scatter" in str(error), "unrelated native probe control failure")
    else:
        raise ValueError("accepted native descent phase mutation")
    passed.append("literal_native_descent_phase")
    qmatrix = lambda a: [[str(x) for x in row] for row in a]
    return {"status": "PASS_SELECTED_CENTRE_NATIVE_LIFT", "times": [0, 1], "replicas": [0, 8],
            "stage": 0, "ordinary_scalar_columns": audited["scalar_columns"], "events": len(events),
            "extended_label_violations": 0, "conversion_events": audited["conversions"],
            "shared_helper_owners": shared, "shared_data_owners": 0, "source_to_helper_endpoint_block": "zero",
            "target_pivot_block_at_centre_entry": "zero", "pivot_input_owners": pivot_owners,
            "source_minor": qmatrix(P), "source_minor_inverse": qmatrix(Pinv), "source_minor_det": str(pdet),
            "scatter_minor_target_roles": [audited["target_ids"][i] for i in selected_rows],
            "scatter_minor": qmatrix(B), "scatter_minor_inverse": qmatrix(Binv), "scatter_minor_det": str(bdet),
            "native_output_coefficient_minor": qmatrix(K), "native_output_coefficient_inverse": qmatrix(Kinv),
            "native_output_coefficient_det": str(kdet), "source_port_twists": [word["ports"][j] for j in PIVOTS],
            "centre_frames": word["center_frames"], "native_source_rank_per_call": 8*512,
            "native_source_rank_two_cuts": 16*512, "native_scatter_history_rank": 16*512,
            "eight_row_transcript_dimension": 8*512, "native_operator_checks": native,
            "literal_native_probe": direct,
            "unchanged_two_phase_bill": {k: 2*v for k, v in sorted(audited["bill"].items())},
            "unchanged_transport_rank_mass": 128, "controls": passed,
            "scope": "Exact 512-address local native rank and conditional source-only transcript exclusion; no recursive-call minimum or supplier gain."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-result", type=Path, help="write an absent receipt path exclusively")
    args = parser.parse_args()
    result = run(args.root)
    if args.write_result:
        with args.write_result.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()), "result receipt mismatch")
    print("PASS_SELECTED_CENTRE_NATIVE_LIFT source_rank=8192 scatter_rank=8192 "
          f"children={result['native_operator_checks']['used_child_recipes']} columns=512 "
          f"controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()

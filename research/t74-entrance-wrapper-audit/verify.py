#!/usr/bin/env python3
"""Source-bound PR2435 raised-entrance audit. Apache-2.0.
New binding and controls: Ross Richardson with OpenAI Codex assistance.
Unchanged exact kernels: Sagar Thakrar, PR1781 and PR2029 (see README).
No producer executable is imported. No full supplier or new kappa claim.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = [1 << i for i in range(9)]
ORIGINS = list(range(474, 478)) + list(range(486, 490)) + list(range(522, 530)) + list(range(534, 542))


class Reject(Exception):
    pass


def need(ok, reason):
    if not ok:
        raise Reject(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def load_inputs(root=HERE):
    manifest = json.loads((root / "INPUTS.json").read_text())
    need(manifest["format"] == "t74-entrance-inputs-v1", "input manifest format")
    paths = [r["path"] for r in manifest["files"]]
    expected = {f"inputs/{v}-{s}" for v in ("base", "extra") for s in
                ("before.json", "entrance.json", "word.json.gz", "CANONICAL-WORD.json.gz",
                 "LOCAL-PROGRAMS.json.gz", "RESIDUAL-ADAPTERS.json")}
    expected |= {"vendor/clifford.py", "vendor/closed_form.py"}
    need(len(paths) == len(set(paths)) == 14 and set(paths) == expected, "complete distinct fixed inputs")
    raw = {}
    # Authenticate every immutable source/certificate before parsing or importing.
    for row in manifest["files"]:
        path = row["path"]
        need(not Path(path).is_absolute() and ".." not in Path(path).parts, "input path")
        raw[path] = (root / path).read_bytes()
        need(digest(raw[path]) == row["sha256"], "immutable input hash: " + path)
    data = {}
    for variant in ("base", "extra"):
        data[variant] = {}
        for key, suffix in (("before", "before.json"), ("entrance", "entrance.json"), ("word", "word.json.gz"),
                            ("canon", "CANONICAL-WORD.json.gz"), ("programs", "LOCAL-PROGRAMS.json.gz"),
                            ("adapters", "RESIDUAL-ADAPTERS.json")):
            path = f"inputs/{variant}-{suffix}"
            value = raw[path]
            data[variant][key] = json.loads(gzip.decompress(value) if path.endswith(".gz") else value)
    kernels = []
    for name in ("clifford", "closed_form"):
        spec = importlib.util.spec_from_file_location("entrance_" + name, root / "vendor" / (name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        kernels.append(mod)
    return data, kernels


def span(rows):
    values = {0}
    for row in rows:
        need(type(row) is int and 0 < row < 512, "frame vector range")
        values |= {v ^ row for v in values}
    return values


def rank(rows):
    return len(span(rows)).bit_length() - 1


def gram_rank(rows):
    gram = [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(rows)) for a in rows]
    values = {0}
    for row in gram:
        values |= {v ^ row for v in values}
    return len(values).bit_length() - 1


def accesses(event):
    tag = event[0]
    if tag in ("residual_adapter", "adapter", "climb"):
        return {event[2]}
    if tag == "warp":
        return {event[1][1]} if event[1][0] == "L" else set()
    if tag == "scalar":
        return {r[1] for r in event[1][1:] if isinstance(r, list) and len(r) == 2 and r[0] == "L"}
    # Center events update private C_k frames; zero_buffer events address Z_z.
    # Neither numeric field denotes an L-register. Their L reads occur in scalar
    # events above. Physical non-aliasing of these namespaces is a caller premise.
    need(tag in ("phase", "zero_buffer", "center"), "unknown event grammar")
    return set()


def check_binding(data, A):
    word, c = data["word"], data["canon"]
    old = data["before"]["fields"]["start_extra"]
    new = data["entrance"]["fields"]["start_extra"]
    need(set(old) == set(new), "entrance domain unchanged")
    changed = sorted(int(k) for k in old if old[k] != new[k])
    need(changed == ORIGINS, "all 24 affected source helpers")
    need(word["start_extra"] == new, "shipped word uses complete entrance patch")
    need((c["v"], c["h"], c["R"]) == (112, 9, 434), "canonical dimensions")
    origins = [r for r in range(224, 704) if r not in word["removed"]]
    need(c["helper_origin"] == origins, "complete compact origin map")
    need(len(c["start"]) == len(c["final"]) == 658, "canonical endpoint lengths")
    need(sorted(c["frames"][1]) == sorted(FULL), "actual FULL representative")
    need(set(data["programs"]) == {"forward", "backward"}, "both orientations")
    phase_positions = {}
    phase_order = ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
                   "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"]
    for orientation, events in data["programs"].items():
        phases = [(i, e[1]) for i, e in enumerate(events) if e[0] == "phase"]
        need([name for _, name in phases] == phase_order, "complete ordered phase markers")
        phase_positions[orientation] = {name: i for i, name in phases}
    records, rows = {}, []
    for origin in changed:
        reg = 224 + origins.index(origin)
        frame = c["start"][reg]
        E = c["frames"][frame]
        need(len(old[str(origin)]) == rank(old[str(origin)]) == 1, "old entrance dimension one")
        need(len(new[str(origin)]) == len(E) == rank(E) == 2, "raised entrance dimension two")
        need(E == new[str(origin)], "exact source/native frame representative")
        need(span(old[str(origin)]) <= span(E), "entrance is a raise")
        need(str(origin) not in word["helper_final"] and c["final"][reg] == 1, "FULL-ended affected helper")
        need(gram_rank(E) == 1, "degenerate raised Gram form")
        rec = data["adapters"]["recipes"][str(frame)]
        need(set(rec) == {"frame", "vectors", "entrance_rank", "rank", "left", "right"}, "recipe fields")
        need((rec["frame"], rec["vectors"], rec["entrance_rank"], rec["rank"]) == (frame, E, 2, 7), "rank-seven recipe binding")
        need(A.well_formed(rec["left"]) and A.well_formed(rec["right"]), "valid two-sided monomial recipes")
        key = canonical({"E": E, "recipe": {k: v for k, v in rec.items() if k != "frame"}})
        records[key] = {"E": E, "recipe": rec}
        bound = {}
        for orientation, events in data["programs"].items():
            positions = [i for i, e in enumerate(events) if reg in accesses(e)]
            wrappers = [(i, e) for i, e in enumerate(events) if e[0] == "residual_adapter" and e[2] == reg]
            expected = [["residual_adapter", "pre", reg, frame], ["residual_adapter", "post", reg, frame]]
            need([e for _, e in wrappers] == expected, "one correct pre/post pair per affected helper")
            lo, hi = wrappers[0][0], wrappers[1][0]
            need(positions[0] == lo and positions[-1] == hi, "whole-invocation access bracketing")
            phase = phase_positions[orientation]
            need(phase["entry_adapters"] < lo < phase["A"] and
                 phase["full_frame_cleanup"] < hi < phase["done"], "actual wrapper phase placement")
            cur, paid, scalar = frame, [], 0
            for i in positions[1:-1]:
                e = events[i]
                if e[0] == "climb":
                    _, phase, r, f, g, cost = e
                    need(f == cur and span(c["frames"][f]) < span(c["frames"][g]), "nested chronological affected climb")
                    need(cost == len(c["frames"][g]) - len(c["frames"][f]) > 0, "actual affected child rank")
                    cur = g; paid.append(cost)
                elif e[0] == "scalar":
                    need(e[2] == cur, "actual scalar common frame for affected helper")
                    scalar += 1
                elif e[0] == "adapter":
                    need(e[1:] == ["new_to_old", reg, 1] and cur == 1, "affected logical exit adapter")
                else:
                    raise Reject("unexpected affected-helper operation")
            need(cur == 1 and sum(paid) == 7, "complete affected path reaches FULL")
            bound[orientation] = {"pre": lo, "post": hi, "scalar_accesses": scalar, "paid_path": paid}
        need(bound["forward"]["paid_path"] == bound["backward"]["paid_path"], "same paid path both orientations")
        rows.append({"origin": origin, "register": reg, "frame": frame, "E": E, "gram_rank": 1, "events": bound})
    need(len(records) == 12, "exact twelve distinct affected recipes")
    return rows, list(records.values())


def exact_a(A, E, rec):
    lhs = A.canonical_frame(E) + A.monomial(rec["right"]) + A.fourier(rec["rank"]) + A.monomial(rec["left"])
    return A.same_operator(lhs, A.canonical_frame(FULL))


def exact_b(B, E, rec):
    return B.wrapper_identity(E, FULL, rec["left"], rec["right"], rec["rank"]) is None


def rejects(fn, label):
    try:
        fn()
    except Reject:
        return label
    raise Reject("negative control unexpectedly accepted: " + label)


def semantic_controls(data, A, B, records):
    counts = Counter()
    for item in records:
        E, rec = item["E"], item["recipe"]
        variants = []
        for label, side, field in (("global_phase", "right", "phase"), ("translation", "left", "offset")):
            bad = copy.deepcopy(rec)
            bad[side][field] = (bad[side][field] + 1) % 4 if field == "phase" else bad[side][field] ^ 1
            variants.append((label, bad))
        bad = copy.deepcopy(rec)
        bad["right"]["linear_Z4"][0] = (bad["right"]["linear_Z4"][0] + 2) % 4
        variants.append(("input_character", bad))
        for delta in (-1, 1):
            bad = copy.deepcopy(rec); bad["rank"] += delta
            variants.append(("wrong_width_" + str(delta), bad))
        bad = copy.deepcopy(rec); bad["left"], bad["right"] = bad["right"], bad["left"]
        variants.append(("swapped_wrappers", bad))
        for label, bad in variants:
            need(not exact_a(A, E, bad), "kernel A rejects " + label)
            need(not exact_b(B, E, bad), "kernel B rejects " + label)
            counts[label] += 1
        good = copy.deepcopy(rec)
        good["left"]["phase"] = (good["left"]["phase"] + 1) % 4
        good["right"]["phase"] = (good["right"]["phase"] - 1) % 4
        need(exact_a(A, E, good) and exact_b(B, E, good), "equivalent redistributed global phase")
        counts["phase_redistribution_positive"] += 1
    binding_controls = []
    def altered(label, mutate):
        bad = copy.deepcopy(data); mutate(bad)
        binding_controls.append(rejects(lambda: check_binding(bad, A), label))
    reg = ORIGINS[0]
    def wrapper(events, kind):
        return next(i for i, e in enumerate(events) if e[:3] == ["residual_adapter", kind, reg])
    altered("missing_pre", lambda d: d["programs"]["forward"].pop(wrapper(d["programs"]["forward"], "pre")))
    altered("wrong_backward_key", lambda d: d["programs"]["backward"][wrapper(d["programs"]["backward"], "post")].__setitem__(3, 0))
    altered("entrance_dropped_to_zero", lambda d: d["canon"]["start"].__setitem__(reg, 0))
    altered("wrong_terminal", lambda d: d["canon"]["final"].__setitem__(reg, d["canon"]["start"][reg]))
    altered("origin_alias", lambda d: d["canon"]["helper_origin"].__setitem__(reg - 224, reg + 1))
    def early_access(d):
        events = d["programs"]["forward"]
        i = next(i for i, e in enumerate(events) if e[0] == "scalar" and reg in accesses(e))
        e = events.pop(i); events.insert(wrapper(events, "pre"), e)
    altered("access_before_pre", early_access)
    need(gram_rank([1, 2]) == 2, "orthogonal-coordinate negative control")
    return {"operator_mutants_per_kernel": dict(sorted(counts.items())), "binding_mutants": binding_controls,
            "orthogonal_relabel_excluded": "12 rank-one Gram forms cannot map orthogonally to rank-two coordinate span"}


def verify(data, A, B, controls=True):
    need(set(data) == {"base", "extra"}, "both fixed providers required")
    providers, distinct = {}, {}
    for name, obj in data.items():
        rows, records = check_binding(obj, A)
        providers[name] = {"roles": rows, "program_event_counts": {k: len(v) for k, v in obj["programs"].items()}}
        for item in records:
            key = canonical({"E": item["E"], "recipe": {k: v for k, v in item["recipe"].items() if k != "frame"}})
            distinct[key] = item
    need(len(distinct) == 12, "shared operator records deduplicated by every proof-relevant field")
    records = list(distinct.values())
    for item in records:
        need(exact_a(A, item["E"], item["recipe"]), "packed all-column operator identity")
        need(exact_b(B, item["E"], item["recipe"]), "closed-form all-column operator identity")
    result = {"status": "PASS_T74_RAISED_ENTRANCE_WRAPPERS", "providers": providers,
              "roles": 48, "orientation_role_bindings": 96, "distinct_operators": 12,
              "columns_per_operator": 512, "coefficients_per_kernel": 12 * 512 * 512,
              "kernels": ["PR1781 unchanged packed Gaussian integers", "PR2029 unchanged closed-form amplitudes"],
              "scope": "Changed input binding and exact local residual wrappers; scalar restoration, global hosting, full invoice and all-size interfaces remain separate. no_new_kappa"}
    if controls:
        result["controls"] = semantic_controls(data["base"], A, B, records)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a receipt to an explicit destination")
    args = parser.parse_args()
    try:
        data, (A, B) = load_inputs()
        result = verify(data, A, B)
        if args.write:
            args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            need(result == json.loads((HERE / "RESULT.json").read_text()), "complete committed receipt")
    except (Reject, OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print("FAIL_T74_RAISED_ENTRANCE_WRAPPERS:", exc, file=sys.stderr)
        return 1
    print("PASS_T74_RAISED_ENTRANCE_WRAPPERS roles=48 orientations=96 operators=12 columns=512 coefficients=3145728_per_kernel no_new_kappa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound audit of two PR3182 support-transfer operations.

The original module is imported unchanged. An AST control deletes exactly its
terminal output-loop break in memory; no archived file is modified. Geometry
and interval construction are reused and credited, not independently certified.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = "research/p104-pooled-onehop-and-physical-consumer-bill"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source changed: " + row["path"])
            pins[row["path"]] = digest
    require(len(pins) == 9, "exact live input inventory")
    return pins


def load_predecessor():
    spec = importlib.util.spec_from_file_location(
        "p104_pr3182_audited", ROOT / PREDECESSOR / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def memory_variant(old, *, write_all=False, reverse=False):
    """An exact one-break deletion and/or enumeration-order control."""
    tree = ast.parse((ROOT / PREDECESSOR / "verify.py").read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == "propagate_with_subspace_memory_bitmap")
    require(sum(isinstance(n, ast.Break) for n in ast.walk(node)) == 1,
            "exactly one audited break")
    parents = [n for n in ast.walk(node) if isinstance(n, ast.If)
               and n.body and isinstance(n.body[-1], ast.Break)]
    require(len(parents) == 1 and len(parents[0].body) == 2,
            "audited output branch shape")
    require(ast.unparse(parents[0].body[0]) == "outputs[t] |= 1 << s",
            "break must follow source-bit accumulation")
    if write_all:
        parents[0].body.pop()
    namespace = dict(vars(old))
    if reverse:
        namespace["bits"] = lambda mask, width: reversed(list(old.bits(mask, width)))
    executable = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(executable, "<pinned-memory-control>", "exec"), namespace)
    return namespace[node.name]


def one_hop_read_first(layers, direct):
    """Set-based necessary relaxation: read, one equal-frame hop, then write.

    Any same-dimension relay chain in a fixed frame assignment has equal
    endpoints and thus a direct compatibility edge. Independent interval
    contacts need not coexist; this is still only a support relaxation.
    """
    size = len(layers[0][0])
    support = [set() for _ in range(size)]
    outputs = [{s for s in range(104) if mask >> s & 1} for mask in direct]
    for adjacency, reads, writes in layers:
        acquired = [support[h] | {s for s in range(104) if reads[h] >> s & 1}
                    for h in range(size)]
        outgoing = []
        for h in range(size):
            joined = set(acquired[h])
            for j in range(size):
                if adjacency[h] >> j & 1:
                    joined.update(acquired[j])
            outgoing.append(joined)
            for t in range(104):
                if writes[h] >> t & 1:
                    outputs[t].update(joined)
        support = outgoing
    return [sum(1 << s for s in row) for row in outputs]


def tiny_checks(old):
    direct = [0] * 104
    layers = [([3, 3], [1, 0], [0, 1])]
    legacy = old.propagate_one_hop_equal_frame(layers, direct)[0]
    repaired = one_hop_read_first(layers, direct)[0]
    require((legacy, repaired) == (0, 1), "fresh read must relay in same layer")
    for changed in ([([1, 2], [1, 0], [0, 1])],
                    [([3, 3], [0, 0], [0, 1])],
                    [([3, 3], [1, 0], [0, 0])]):
        require(one_hop_read_first(changed, direct)[0] == 0,
                "missing contact/read/write must block tiny path")
    # One exact line, one helper, two independent scalar inputs in that frame.
    line = 3  # literal point set {0,1} in F_2^9
    frames = ([line], [line], [line], [line], [[0]])
    paths = {f"{kind}{i}": [] for kind in "XY" for i in range(104)}
    paths.update(X0=[line], X1=[line], Y0=[line])
    layer = [([1], [3], [1])]
    results = {}
    for mode in (False, True):
        values = []
        for write_all, reverse in ((False, False), (False, True),
                                   (True, False), (True, True)):
            fn = memory_variant(old, write_all=write_all, reverse=reverse)
            values.append(fn(frames, [(0, 0)], layer, paths, direct,
                             full_memory=mode)[0])
        require(values == [1, 2, 3, 3], "output support must not depend on enumeration")
        results[str(mode)] = values
    # H and Y arbitrary dirty: Y <- Y+X0+X1 and H restored, in one frame.
    rows = [[int(i == j) for j in range(4)] for i in range(4)]
    for target, source, sign in ((3, 2, -1), (2, 0, 1), (2, 1, 1),
                                 (3, 2, 1), (2, 1, -1), (2, 0, -1)):
        rows[target] = [a + sign*b for a, b in zip(rows[target], rows[source])]
    require(rows == [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 0, 1]],
            "arbitrary-dirty six-ADD shear")
    return {"fresh_read_legacy_corrected": [legacy, repaired],
            "memory_legacy_reverse_all_reverse": results,
            "six_add_endpoint": rows, "blocked_contact_read_write_controls": 3}


def data(old):
    word = read("research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    cert = read("research/p104-joint-unit-flags/CERTIFICATE.json")
    fixture = read("research/p104-native-channel/inputs/P104-FIXTURE.json")
    paths = old.data_paths(word)
    frames = old.cover_frames(cert, paths)
    matrix = old.correction(fixture)
    required = [sum(1 << s for s in range(104) if matrix[t][s]) for t in range(104)]
    direct = [sum(1 << s for s in range(104)
                  if set(paths[f"X{s}"]) & set(paths[f"Y{t}"])) for t in range(104)]
    p2981 = [-1] * 208
    for row in cert["helpers"]:
        p2981[2*row["source"] + row["departure_choice"]] = (
            2*row["target"] + row["arrival_choice"])
    p3013 = read("research/p104-coherent-support-witness/CONTROL.json")["pairing"]
    p3019 = read("research/p104-coherent-support-witness/WITNESS.json")["pairing"]
    pairings = {"PR2981": p2981, "PR3013": p3013, "PR3019": p3019,
                "PR3124_A": old.apply_cycle_to_pairing(p3013, [13, 203, 191, 63]),
                "PR3182_B_as_encoded": old.apply_cycle_to_pairing(p3013, [39, 154, 139, 134])}
    for name, pairing in pairings.items():
        if name == "PR3182_B_as_encoded":
            continue  # Intentionally reproduce the predecessor's invalid input.
        old.check_pairing(pairing, frames[-1])
    return word, paths, frames, matrix, required, direct, pairings


def points(basis):
    result = {0}
    for v in basis:
        require(v not in result, "independent literal basis")
        result |= {x ^ v for x in result}
    return result


def direct_path_witness(old, word, frames, matrix, pairing, legacy, write_all):
    """Check a fixed witness, not a search; use literal point-set nesting."""
    h, s, t = 201, 1, 98
    require(pairing[h] == 197, "helper 201 arrival slot")
    require(str(matrix[t][s]) == "-1/2", "required coefficient")
    fx = points([3, 8, 64, 416])
    fy = points([3, 5, 8, 16, 33, 64, 129, 256])
    # Reconstruct this helper's endpoints directly from the raw certificate
    # and native word, using literal point sets rather than interval routines.
    cert = read("research/p104-joint-unit-flags/CERTIFICATE.json")
    line = points(word["initial_frames"]["X100"])
    departure = points(word["initial_frames"]["X100"]
                       + [cert["forms"]["departure"][100][1]])
    cap = points(word["final_frames"]["Y98"])
    form = cert["forms"]["arrival"][98][1]
    arrival = {v for v in cap if (v & form).bit_count() % 2 == 0}
    as_set = lambda mask: {i for i in range(512) if mask >> i & 1}
    require((line, departure, arrival, cap) ==
            (as_set(frames[0][100]), as_set(frames[1][h]),
             as_set(frames[2][197]), as_set(frames[3][98])),
            "literal endpoints agree with source parser")
    require(line < departure < fx < arrival < cap == fy, "ordered nested waypoints")
    flag = [{0}, line, departure]
    for goal in (fx, arrival, cap, set(range(512))):
        while flag[-1] != goal:
            v = min(goal - flag[-1])
            flag.append(flag[-1] | {x ^ v for x in flag[-1]})
    require([len(f) for f in flag] == [1 << d for d in range(10)], "full flag")
    state = points(word["initial_frames"]["X1"])
    read_cut = 594
    for event in word["program"][:read_cut]:
        if event[:2] == ["transport", "X1"]:
            require(state == points(event[2]), "source old frame")
            state = points(event[3])
    require(state == fx == flag[4], "source available at exact cut 594")
    require(points(word["final_frames"]["Y98"]) == flag[8], "final target frame")
    require(not (legacy[t] >> s & 1) and (write_all[t] >> s & 1),
            "literal dependency is omitted only before output-loop repair")
    return {"helper": h, "source": s, "target": t, "arrival_slot": 197,
            "read_cut": read_cut, "write_cut": len(word["program"]),
            "coefficient": str(matrix[t][s]),
            "flag_bases": [old.frame_basis(sum(1 << x for x in f)) for f in flag],
            "legacy_has_dependency": False, "write_all_has_dependency": True,
            "dirty_restoration": "not supplied for this P104 path"}


def cycle_direction_audit(old, frames, pairing):
    prior = read("research/p104-alternating-cycle-neighborhood/RESULT.json")
    candidates = prior["complete_candidates"]
    actual = next(row["cycle"] for row in candidates if row["cycle"][0] == 39)
    require(actual == [39, 134, 139, 154], "PR3124 exact cycle order")
    encoded = [39, 154, 139, 134]
    require(encoded == [actual[0], *reversed(actual[1:])], "reversed cyclic order")
    good = old.apply_cycle_to_pairing(pairing, actual)
    bad = old.apply_cycle_to_pairing(pairing, encoded)
    old.check_pairing(good, frames[-1])
    invalid = [[a, b] for a, b in enumerate(bad) if b not in frames[-1][a]]
    require(invalid == [[39, 186], [139, 23], [154, 7]], "incompatible reversed pairs")
    # Independently express compatibility as literal subspace containment.
    literal_invalid = []
    for a in actual:
        left = {i for i in range(512) if frames[1][a] >> i & 1}
        right = {i for i in range(512) if frames[2][bad[a]] >> i & 1}
        if not left <= right:
            literal_invalid.append([a, bad[a], min(left - right)])
    require(sorted(row[:2] for row in literal_invalid) == invalid,
            "literal containment agrees")
    return {"PR3124_cycle": actual, "PR3182_encoded_cycle": encoded,
            "PR3124_compatible": True, "incompatible_pairs": invalid,
            "separating_vectors": sorted(literal_invalid)}


def build_receipt():
    pins = authenticate()
    old = load_predecessor()
    tiny = tiny_checks(old)
    word, paths, frames, matrix, required, direct, pairings = data(old)
    cycle_audit = cycle_direction_audit(old, frames, pairings["PR3013"])
    all_sources = memory_variant(old, write_all=True)
    reversed_legacy = memory_variant(old, reverse=True)
    reversed_all = memory_variant(old, write_all=True, reverse=True)
    result = {}
    literal = None
    expected = {
        "PR2981": (4781, 4395, 4397), "PR3013": (4783, 4253, 4257),
        "PR3019": (4783, 4247, 4251), "PR3124_A": (4783, 4248, 4252),
        "PR3182_B_as_encoded": (4783, 4264, 4268),
    }
    for name, pairing in pairings.items():
        edges = list(enumerate(pairing))
        layers = old.build_general_interval_layers(frames, edges, paths)
        invalid = [[a, b] for a, b in edges if b not in frames[-1][a]]
        require(invalid == ([[39, 186], [139, 23], [154, 7]]
                            if name == "PR3182_B_as_encoded" else []),
                "exact endpoint-compatibility audit")
        row = {"incompatible_endpoint_pairs": invalid}
        for mode in (False, True):
            args = (frames, edges, layers, paths, direct)
            original = old.propagate_with_subspace_memory_bitmap(*args, full_memory=mode)
            fixed = all_sources(*args, full_memory=mode)
            reverse_original = reversed_legacy(*args, full_memory=mode)
            reverse_fixed = reversed_all(*args, full_memory=mode)
            require(fixed == reverse_fixed, "write-all must be order invariant")
            require(all((a & b) == a for a, b in zip(original, fixed)),
                    "write-all must retain every old source")
            counts = [old.count_missing(x, required)[0]
                      for x in (original, fixed, reverse_original)]
            require(counts[:2] == [expected[name][0], expected[name][1 + int(mode)]],
                    "pinned memory impact counts")
            row["full_memory" if mode else "one_step_memory"] = {
                "legacy_missing": counts[0], "write_all_only_missing": counts[1],
                "reverse_legacy_missing": counts[2],
                "reverse_legacy_changed_output_rows": sum(a != b for a, b in zip(original, reverse_original)),
                "write_all_order_invariant": True,
            }
            if name == "PR3019" and mode:
                literal = direct_path_witness(old, word, frames, matrix, pairing, original, fixed)
        old_hop = old.propagate_one_hop_equal_frame(layers, direct)
        fresh_hop = one_hop_read_first(layers, direct)
        require(old_hop == fresh_hop, "fresh reads do not change these fixed receipts")
        row["one_hop_missing_before_and_after"] = old.count_missing(old_hop, required)[0]
        result[name] = row
    edges = [(a, b) for a, neighbors in enumerate(frames[-1]) for b in neighbors]
    layers = old.build_general_interval_layers(frames, edges, paths)
    original = old.propagate_one_hop_equal_frame(layers, direct)
    fixed = one_hop_read_first(layers, direct)
    missing = old.count_missing(fixed, required)
    require(original == fixed and missing == (1, [[71, 102]]), "pooled obstruction survives this fix")
    return {"schema_version": 1, "status": "PASS_P104_SUPPORT_PROPAGATION_AUDIT",
            "source_sha256": pins, "tiny": tiny, "matching_impacts": result,
            "literal_p104_path": literal,
            "cycle_direction_audit": cycle_audit,
            "pooled_read_first_control": {"edges": len(edges), "missing": missing[1],
                                          "complete_outputs_unchanged": True},
            "scope": "Audit of two propagation operations; write-all-only counts are not certified obstructions",
            "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(json.dumps(receipt, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "committed receipt mismatch")
        print("PASS_P104_SUPPORT_PROPAGATION_AUDIT tiny=2 matchings=5 path=X1-H201-Y98 pooled_missing=1 no_new_kappa")


if __name__ == "__main__":
    main()

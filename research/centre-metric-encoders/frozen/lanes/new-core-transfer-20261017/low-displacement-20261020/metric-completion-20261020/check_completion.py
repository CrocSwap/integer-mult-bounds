#!/usr/bin/env python3
"""Build a row-complete code with physical diagonal metrics."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
PINS = {
    "arithmetic": (HERE.parent / "check_response.py",
                   "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8"),
    "native": (HERE.parent / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
               "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"),
    "cyclic": (LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
               "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"),
    "reader": (LANES / "controller-followthrough-20261017/row-capture-20261020/run-normal/ROW-CAPTURE.json",
               "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7"),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source " + name)
    return raw


read("arithmetic")
spec = importlib.util.spec_from_file_location("metric_completion_arithmetic", PINS["arithmetic"][0])
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def rows(value):
    return [{int(j): F(c) for j, c in row.items() if F(c)} for row in value]


def unit(x):
    x = abs(x)
    return bool(x) and (x.numerator & (x.numerator - 1) == 0
                        and x.denominator & (x.denominator - 1) == 0)


def scale_row(a, c):
    return {j: c * v for j, v in a.items() if c * v}


def factor(matrix, ports):
    """Reduce a small dyadic matrix and reverse the paid row steps."""
    a = [dict(row) for row in matrix]
    reduction = []

    def add(i, j, c):
        if c:
            r.add(a[i], a[j], c)
            reduction.append(["add", ports[i], ports[j], str(c)])

    def scale(i, c):
        if c != 1:
            need(unit(c), "Only signed power-of-two scales are used")
            a[i] = scale_row(a[i], c)
            reduction.append(["scale", ports[i], None, str(c)])

    for j in range(len(ports)):
        candidates = [i for i in range(j, len(ports)) if unit(a[i].get(j, F(0)))]
        need(candidates, "A dyadic pivot exists")
        pivot = min(candidates, key=lambda i: (i != j, len(a[i]), abs(a[i][j])))
        if pivot != j:
            add(j, pivot, 1)
            add(pivot, j, -1)
            add(j, pivot, 1)
            scale(pivot, -1)
        scale(j, 1 / a[j][j])
        for i in range(len(ports)):
            if i != j:
                add(i, j, -a[i].get(j, F(0)))
    need(a == r.identity(len(ports)), "The complete block reduction")
    return r.inverse_word(reduction)


def matchings(edges, remaining=tuple(range(8))):
    if not remaining:
        yield []
        return
    a = remaining[0]
    for b in remaining[1:]:
        key = tuple(sorted((a, b)))
        if key in edges:
            rest = tuple(v for v in remaining if v not in (a, b))
            for tail in matchings(edges, rest):
                yield [key] + tail


def replay(word, n=112):
    a = r.identity(n)
    peak, height = F(1), 0
    for op, target, source, coefficient in word:
        coefficient = F(coefficient)
        if op == "add":
            need(target != source, "Distinct ADD fields")
            r.add(a[target], a[source], coefficient)
        else:
            need(op == "scale" and unit(coefficient), "Dyadic unit scale")
            a[target] = scale_row(a[target], coefficient)
        peak = max(peak, sum(abs(v) for v in a[target].values()))
        for value in a[target].values():
            d = value.denominator
            need(d & (d - 1) == 0, "No odd content denominator")
            height = max(height, d.bit_length() - 1)
    return a, {"scalar": r.price(word), "prefix_row_one_norm": str(peak),
               "binary_height": height, "instructions": len(word)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    native = json.loads(read("native"))
    model = native["model"]
    cyclic = json.loads(read("cyclic"))
    reader = json.loads(read("reader"))
    pairs = cyclic["pair_codes"]
    old_centres = reader["pivots"]
    centre_set = set(old_centres)
    large = set(model["large_ports"])
    pair_by_edge = {tuple(sorted(pair["vertices"])): pair for pair in pairs}
    p0 = {edge for edge, pair in pair_by_edge.items() if set(pair["ports"]) <= centre_set}
    q_ports = {2, 25, 13, 51, 11, 63, 42, 105}
    q = {edge for edge, pair in pair_by_edge.items() if set(pair["ports"]) <= q_ports}
    need(len(p0) == len(q) == 4 and not p0 & q, "Two disjoint selected matchings")
    remaining = set(pair_by_edge) - p0 - q
    found = None
    for n in matchings(remaining):
        for t in matchings(remaining - set(n)):
            found = (set(n), set(t))
            break
        if found:
            break
    need(found is not None, "Two further disjoint actual matchings")
    n_edges, t_edges = found
    labels = {"centre": p0, "contrast": q, "negative": n_edges, "negative_difference": t_edges}
    assignment = {}
    for vertex in range(8):
        assignment[vertex] = {}
        for label, edges in labels.items():
            edge = next(e for e in edges if vertex in e)
            pair = pair_by_edge[edge]
            assignment[vertex][label] = pair["ports"][pair["vertices"].index(vertex)]
    H, Hinv = r.identity(112), r.identity(112)
    hword = []
    for pair in pairs:
        pp, matrix = pair["ports"], pair["matrix"]
        local = [{j: F(c) for j, c in enumerate(row) if c} for row in matrix]
        for i, port in enumerate(pp):
            H[port] = {pp[j]: c for j, c in local[i].items()}
            Hinv[port] = {pp[j]: F(matrix[j][i], 2) for j in range(2) if matrix[j][i]}
        hword += factor(local, pp)
    need(r.product(H, Hinv) == r.product(Hinv, H) == r.identity(112), "The actual physical pair code")
    Cm, Jm, Gm = r.identity(112), r.identity(112), r.identity(112)
    block_records, mode_word, exceptional = [], [], set()
    for block in model["vertex_assignments"]:
        vertex, pp, signs = block["vertex"], block["ordered_carriers_a_b_c"], block["signs"]
        roles = assignment[vertex]
        p, c, n, t = [roles[k] for k in ("centre", "contrast", "negative", "negative_difference")]
        a, b = sorted(set(pp) - {p, c, n, t})
        template = {
            p: {j: 1 for j in pp},
            c: {j: (2 if j in (p, n) else 1) for j in pp},
            n: {b: 1, c: 1, a: -1, t: -1},
            t: {p: 1, n: -1},
            a: {b: 1, c: -1},
            b: {a: 1, t: -1},
        }
        sign = dict(zip(pp, signs))
        for port in pp:
            Cm[port] = {j: F(value * sign[j]) for j, value in template[port].items()}
            Jm[port] = {port: F(-1 if port in (p, n) else 1)}
        norms = {p: 2, c: -4, n: 4, t: -2, a: 2, b: 2}
        for port, norm in norms.items():
            Gm[port] = {port: F(norm)}
        local = [{pp.index(j): value for j, value in Cm[port].items()} for port in pp]
        mode_word += factor(local, pp)
        exceptional.update((p, c))
        block_records.append({"kind": "large6", "vertex": vertex, "ports": pp,
                              "roles": {**roles, "pair_difference_a": a, "pair_difference_b": b},
                              "signs": signs, "row_norms": norms})
    for i, pp in enumerate(model["small_cliques"]):
        left, right = pp[:4], pp[4:]
        p, c = left[0], right[0]
        template = {p: {j: 1 for j in pp},
                    c: {j: (1 if j in left else -1) for j in pp}}
        norms = {p: 8, c: 8}
        for group, outputs in ((left, right[1:]), (right, left[1:])):
            x0, x1, x2, x3 = group
            patterns = [{x0: 1, x1: -1}, {x2: 1, x3: -1},
                        {x0: 1, x1: 1, x2: -1, x3: -1}]
            for output, pattern, norm in zip(outputs, patterns, (2, 2, 4)):
                template[output], norms[output] = pattern, norm
        for port in pp:
            Cm[port] = {j: F(value) for j, value in template[port].items()}
            Gm[port] = {port: F(norms[port])}
        local = [{pp.index(j): value for j, value in Cm[port].items()} for port in pp]
        mode_word += factor(local, pp)
        exceptional.update((p, c))
        block_records.append({"kind": "small8", "index": i, "ports": pp,
                              "centre": p, "contrast": c, "row_norms": norms})
    need(r.product(r.product(Cm, Jm), r.transpose(Cm, 112)) == Gm, "Every exact mode metric")
    C = r.product(r.product(Hinv, Cm), H)
    J = r.product(r.product(Hinv, Jm), H)
    G = r.product(r.product(Hinv, Gm), H)
    need(all(set(row) == {i} and abs(row[i]) == 1 for i, row in enumerate(J)), "Physical J is diagonal signs")
    need(all(set(row) == {i} and unit(row[i]) for i, row in enumerate(G)), "Physical G is diagonal dyadic units")
    Gi = [{i: 1 / row[i]} for i, row in enumerate(G)]
    Cinv = r.product(r.product(J, r.transpose(C, 112)), Gi)
    Cdual = r.product(r.product(Gi, C), J)
    need(r.product(C, Cinv) == r.product(Cinv, C) == r.identity(112), "Both actual112 inverse orders")
    need(Cdual == r.transpose(Cinv, 112), "Physical inverse-adjoint identity")
    need(r.product(r.product(C, J), r.transpose(C, 112)) == G, "Actual physical metric")
    E = rows(model["response"])
    CE = r.product(C, E)
    Em = r.product(r.product(H, E), Hinv)
    CEm = r.product(Cm, Em)
    need(len(exceptional) == 32 and centre_set <= exceptional, "The actual32 exceptional ports")
    need(all((CEm[p].get(p, 0) != 0) == (p in exceptional) for p in range(112)),
         "Exactly32 mode diagonal exceptions")
    need(all(set(pair["ports"]) <= exceptional or not set(pair["ports"]) & exceptional for pair in pairs),
         "Complete physical pair closure")
    need(all(not CE[p].get(p, 0) for p in set(range(112)) - exceptional),
         "Every ordinary physical response diagonal is zero")
    V = rows(model["correction_V"])
    centre_rows = [C[p] for p in old_centres]
    need(r.rank(centre_rows, 112) == r.rank(V, 112) == r.rank(centre_rows + V, 112) == 16,
         "The exact old centre rowspace")
    code_word = hword + mode_word + r.inverse_word(hword)
    inverse_word = r.inverse_word(code_word)
    dual_word = [["scale", p, None, str(J[p][p])] for p in range(112) if J[p][p] != 1]
    dual_word += code_word
    dual_word += [["scale", p, None, str(Gi[p][p])] for p in range(112) if Gi[p][p] != 1]
    words = {"code": code_word, "inverse": inverse_word, "inverse_adjoint": dual_word}
    expected = {"code": C, "inverse": Cinv, "inverse_adjoint": Cdual}
    reports = {}
    for name, word in words.items():
        actual, report = replay(word, 640)
        need(actual[:112] == expected[name] and actual[112:] == r.identity(640)[112:],
             "All640 scalar columns and528 arbitrary outside fields")
        reports[name] = report
    native_audit = {}
    for provider, data in native["providers"].items():
        forward = data["forward"]
        selected_fields = {112 + p for p in exceptional}
        removed = []
        kept = []
        for i, event in enumerate(forward["events"]):
            target = event[1] if event[0] == "native" else event[1][1]
            if target in selected_fields:
                removed.append(event)
            else:
                if event[0] == "scalar" and event[1][0] == "add":
                    need(event[1][2] not in selected_fields, "No retained event reads a removed target")
                kept.append(event)
        old = Counter(event[4] for event in kept if event[0] == "native")
        profile_q = old + Counter({8: 32})
        profile_i = old + Counter({9: 32})
        need(Counter(event[4] for event in removed if event[0] == "native") == {1: 256},
             "Exactly256 old native target steps are removed")
        native_audit[provider] = {
            "removed_events": len(removed), "removed_native_profile": {"1": 256},
            "line_entry_profile": dict(sorted(profile_q.items())),
            "line_entry_mass": sum(k * v for k, v in profile_q.items()),
            "formation_profile": dict(sorted(profile_i.items())),
            "formation_mass": sum(k * v for k, v in profile_i.items()),
            "scope": "Path-removal census only. Retuned transfer weights, new native phases, late queries and full native replay remain open.",
        }
    payload = {
        "schema": "physical-diagonal-metric-completion-v1",
        "source_pins": {k: {"path": str(v[0]), "sha256": v[1]} for k, v in PINS.items()},
        "ports": model["ports"], "centre_ports": old_centres,
        "exceptional_ports": sorted(exceptional), "ordinary_ports": sorted(set(range(112)) - exceptional),
        "mode_blocks": block_records, "matchings": {k: sorted(v) for k, v in labels.items()},
        "pair_code": r.encoded(H), "pair_code_inverse": r.encoded(Hinv),
        "mode_code": r.encoded(Cm), "code": r.encoded(C), "inverse": r.encoded(Cinv),
        "inverse_adjoint": r.encoded(Cdual), "input_metric": r.encoded(J), "output_metric": r.encoded(G),
        "response": model["response"], "coded_response": r.encoded(CE),
        "mode_response": r.encoded(Em), "mode_coded_response": r.encoded(CEm), "scalar_words": words,
        "identity": "C J C^T=G; C^(-T)=G^(-1) C J. Both physical metrics are diagonal dyadic units.",
        "scope": "Complete scalar code and exact native-support census. No changed native service or routed caller is claimed.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for name, word in saved["scalar_words"].items():
        need(replay(word, 640)[0][:112] == expected[name], "Serialized scalar code")
    (args.out / "METRIC-COMPLETION.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_PHYSICAL_DIAGONAL_METRIC_COMPLETION",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "all_matrix_columns": 112, "all_scalar_columns": 640, "centre_rank": 16,
        "exceptional_rows": len(exceptional), "ordinary_rows": 80,
        "input_metric_counts": dict(Counter(str(row[i]) for i, row in enumerate(J))),
        "output_metric_counts": dict(Counter(str(row[i]) for i, row in enumerate(G))),
        "reports": reports, "native_path_census": native_audit, "scope": payload["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

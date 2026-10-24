#!/usr/bin/env python3
"""Check clean reflection maps and their hidden output columns."""

import argparse
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
HELPER = HERE / "check_reciprocal_caller.py"
PIN = "8c107239cbc9f7d491a8ef455a53826aeccd2e8c33eccfb43e9625101ceb87fc"
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError("The pinned independent arithmetic helper")
SPEC = importlib.util.spec_from_file_location("reciprocal_check", HELPER)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
N = 112


def local(r, selected, backward=False, swap=False):
    out = []
    for p in range(N):
        if p in selected:
            out.append({N+p: G.F(-1)})
        else:
            row = dict(r[p])
            if backward:
                row[N+p] = G.F(-1)
            out.append(row)
    for p in range(N):
        if p in selected:
            out.append(dict(r[p]))
        elif backward:
            out.append({N+p: G.F(1)})
        else:
            row = dict(r[p])
            row[N+p] = G.F(1)
            out.append(row)
    return conjugate_selected(out, selected) if swap else out


def inverse(r, selected, backward=False, swap=False):
    w = [
        {N+p: G.F(1)} if p in selected else
        ({p: G.F(1), N+p: G.F(1)} if backward else {p: G.F(1)})
        for p in range(N)
    ]
    out = G.mul(r, w)
    for p in range(N):
        out.append({p: G.F(-1)} if p in selected else
                   ({N+p: G.F(1)} if backward else {N+p: G.F(1), p: G.F(-1)}))
    return conjugate_selected(out, selected) if swap else out


def conjugate_selected(a, selected):
    permutation = [p+N if p in selected else p-N if p-N in selected else p
                   for p in range(2*N)]
    return [{permutation[j]: x for j, x in a[permutation[p]].items()}
            for p in range(2*N)]


def check():
    raw = gzip.decompress(G.MODEL.read_bytes())
    G.need(sha256(raw).hexdigest() == G.PIN, "The actual112 source pin")
    source = json.loads(raw)
    r = G.rows(source["physical"]["R"])
    selected = set(source["special_ports"])
    ordinary = [p for p in range(N) if p not in selected]
    rs, us, ls = [], [], []
    for stage in range(3):
        s = G.eye(N) if stage == 0 else G.sign_matrix(N, stage)
        rs.append(G.mul(s, G.mul(r, s)))
        us.append(G.mul(s, G.rows(source["reflection_U"])))
        ls.append(G.mul(G.rows(source["reflection_L"]), s))
    proj = [{p: G.F(1)} if p in ordinary else {} for p in range(N)]
    i_o = [{ordinary.index(p): G.F(1)} if p in ordinary else {} for p in range(N)]
    results = {}
    for swap in (False, True):
        forwards = [local(rs[0], selected),
                    local(rs[1], selected, True, swap),
                    local(rs[2], selected)]
        inverses = [inverse(rs[0], selected),
                    inverse(rs[1], selected, True, swap),
                    inverse(rs[2], selected)]
        for a, ai in zip(forwards, inverses):
            G.need(G.mul(a, ai) == G.mul(ai, a) == G.eye(2*N), "Both local inverse orders")
        total = G.mul(forwards[2], G.mul(forwards[1], forwards[0]))
        total_inverse = G.mul(inverses[0], G.mul(inverses[1], inverses[2]))
        G.need(G.mul(total, total_inverse) == G.mul(total_inverse, total) == G.eye(2*N),
               "Both complete inverse orders")
        ident = G.eye(N)
        ideal = G.mul(local(ident, selected),
                      G.mul(local(ident, selected, True, swap), local(ident, selected)))
        ideal_inverse = G.trans(ideal, 2*N)
        defect = G.add(G.mul(ideal_inverse, total), G.eye(2*N), -1)
        G.need(G.rank(defect) <= 48, "The complete rank bound")
        hidden = G.zero(N) + i_o
        actual = G.mul(total_inverse, hidden)
        r1_o = G.mul(rs[1], i_o)
        want_x = G.mul(rs[0], r1_o if swap else G.mul(proj, r1_o))
        want_y = G.add(i_o, r1_o, -1)
        if swap:
            want_y = G.mul(proj, want_y)
        G.need(actual == want_x + want_y, "The exact hidden-column formula")
        relative = G.add(actual, i_o + G.zero(N), -1)
        G.need(G.rank(relative) <= 32, "The hidden rank bound")
        if swap:
            q1 = G.mul(ls[1], i_o)
            q0 = G.mul(ls[0], r1_o)
            dx = G.add(G.mul(us[1], q1), G.mul(us[0], q0))
            dy = G.neg(G.mul(proj, G.mul(us[1], q1)))
            G.need(relative == dx + dy, "The two query factorization")
            G.need(all(not actual[N+p] for p in selected), "No selected borrowed hidden row")
        results["selected_conjugate" if swap else "unpermuted"] = {
            "arbitrary_two_bank_columns": 224,
            "hidden_columns": len(ordinary),
            "residual_rank_regression": G.rank(defect),
            "hidden_rank_regression": G.rank(relative),
            "hidden_X_rank": G.rank(relative[:N]),
            "hidden_Y_rank": G.rank(relative[N:]),
        }
    return {
        "schema": "clean-reflection-hidden-check-v1",
        "status": "PASS",
        "actual_model_sha256": G.PIN,
        "selected_ports": sorted(selected),
        "variants": results,
        "scope": "Exact ordered content. Signed stage conjugations are a regression, not an actual routed lower bound. No new native service or decoder.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = check()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "sha256": sha256(args.out.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()

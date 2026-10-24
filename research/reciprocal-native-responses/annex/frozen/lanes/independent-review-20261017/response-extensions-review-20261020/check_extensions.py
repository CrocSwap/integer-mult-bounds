#!/usr/bin/env python3
"""Check the changed matrices and principal inverses without native replay."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "new-core-transfer-20261017/low-displacement-20261020"
REVIEW = HERE.parent / "rank-thirty-review-20261020/check_review.py"
PINS = {
    "EXTENSIONS-FREEZE.json": "aec99dd0638e635619b14ffd056ab2581424d765d435462aed94b8c8f882a689",
    "EXTENSIONS.md": "2328ec60c1cf89efe7661b3696839f8eb32a95e11c67a62dd653781a8b0ed5fb",
    "emit_followthrough.py": "b03568530696ab810070ba3243b59dd74740fb634fe7f26b2cbdb1d3283d045f",
    "run-normal/RESPONSE-PROGRAM.json": "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
}
PAYLOADS = {
    "reciprocal-normal-v2": "e4df61bf4e121364ba53538eb2ad612bd314807cfb2050050d4595efce9cf416",
    "odd16-normal-v2": "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    need(sha256(REVIEW.read_bytes()).hexdigest() ==
         "118088a1b6d7126d50fb4c05a59fc7f69d792a8c0530ddb066d17434c3d9fff2",
         "Independent base-review helper pin")
    spec = importlib.util.spec_from_file_location("independent_rank_thirty", REVIEW)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    apply, rows, unit = helper.apply, helper.sparse, helper.unit
    for name, digest in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == digest, "Source pin")
    old = json.loads((SOURCE / "run-normal/RESPONSE-PROGRAM.json").read_text())
    for name, digest in old["source_pins"].items():
        raw = (LANES / name).read_bytes()
        need(sha256(raw).hexdigest() == digest, "Geometry pin")
        if "CYCLIC" in name:
            cyclic = json.loads(raw)
    old_e, old_ei = rows(old["response"]), rows(old["response_inverse"])
    large, small, selected = old["large_ports"], old["small_ports"], old["selected_ports"]
    ordinary = old["ordinary_ports"]
    l, li = rows(old["selected_block"]), rows(old["selected_inverse"])
    k_rows = []
    for entry in old["vertex_assignments"]:
        k = {}
        for p, sign in zip(entry["ordered_carriers_a_b_c"], entry["signs"]):
            for q, coefficient in cyclic["mode_rows"][str(p)].items():
                k[int(q)] = k.get(int(q), F(0)) + sign * F(coefficient)
        k_rows.append({p: c for p, c in k.items() if c})
    need(all(len(k) == 12 and set(k.values()) <= {-1, 1} for k in k_rows),
         "Eight signed twelve-port queries")
    need([[sum(c * other.get(p, 0) for p, c in k.items()) for other in k_rows]
          for k in k_rows] == [[12 * (i == j) for j in range(8)] for i in range(8)],
         "Exact K Gram matrix")
    reports = {}
    for folder, digest in PAYLOADS.items():
        raw = gzip.decompress((SOURCE / folder / "EXTENSION-PROGRAM.json.gz").read_bytes())
        need(sha256(raw).hexdigest() == digest, "Final extension payload")
        packet = json.loads(raw)
        model = packet["model"]
        odd = packet["kind"] == "odd-grid-rank16"
        e, ei = rows(model["response"]), rows(model["response_inverse"])
        need(model["selected_ports"] == selected and model["ordinary_ports"] == ordinary,
             "Unchanged principal partition")

        def formula(x, inverse=False):
            if not odd:
                out = apply(old_ei if inverse else old_e, x)
                source = old_e if inverse else old_ei
                for p in large:
                    out[p] = sum(source[q].get(p, F(0)) * x[q] for q in large)
                return out
            values = apply(k_rows, x)
            out = list(x)
            for p in large:
                out[p] -= sum(k.get(p, 0) * v for k, v in zip(k_rows, values)) / (10 if inverse else 2)
            for group in model["small_cliques"]:
                total = sum(x[p] for p in group) / (7 if inverse else 1)
                for p in group:
                    out[p] = x[p] - total
            return out

        columns, inverse_columns = [], []
        for j in range(112):
            x = unit(112, j)
            a, b = formula(x), formula(x, True)
            need(a == apply(e, x) and b == apply(ei, x), "Independent extension column")
            need(formula(a, True) == formula(b) == x, "Two extension inverse orders")
            columns.append(a)
            inverse_columns.append(b)
        need(helper.restrict(e, selected) == l, "Original selected block")
        inverse_l = helper.restrict(ei, selected)
        wanted = [{j: (4 * (i == j) + l[i].get(j, 0)) / F(5)
                   for j in range(8) if i == j or j in l[i]} for i in range(8)] if odd else l
        need(inverse_l == wanted == rows(model["selected_inverse_block"]), "Inverse selected block")
        p_inverse = [{j: F(10, 31) * (4 * (i == j) - l[i].get(j, 0))
                      for j in range(8) if i == j or j in l[i]} for i in range(8)] if odd else li
        need(all(apply(inverse_l, apply(p_inverse, unit(8, j))) ==
                 apply(p_inverse, apply(inverse_l, unit(8, j))) == unit(8, j) for j in range(8)),
             "Inverse selected principal inverse")
        h, hi = helper.restrict(e, ordinary), rows(model["ordinary_inverse"])
        need(all(apply(h, apply(hi, unit(104, j))) ==
                 apply(hi, apply(h, unit(104, j))) == unit(104, j) for j in range(104)),
             "Two ordinary inverse orders")
        full_det = 35 ** 8 if odd else 2 ** 25
        ordinary_det = F(7 ** 8 * 31 ** 4, 16) if odd else F(2 ** 21)
        need(helper.eliminate(e, 112)[1] == full_det == F(model["full_determinant"]),
             "Full determinant")
        need(helper.eliminate(h, 104)[1] == ordinary_det == F(model["ordinary_determinant"]),
             "Ordinary determinant")
        correction = [{q: c - (p == q) for q, c in row.items()} for p, row in enumerate(e)]
        for p, row in enumerate(correction):
            if p not in e[p]:
                row[p] = F(-1)
            correction[p] = {q: c for q, c in row.items() if c}
        need(helper.eliminate(correction, 112)[0] == (16 if odd else 30), "Correction rank")
        code_reports = {}
        if odd:
            need(sorted(p for c in model["small_cliques"] for p in c) == small and
                 len(model["small_cliques"]) == 8 and all(len(c) == 8 for c in model["small_cliques"]),
                 "Eight-clique partition")
            need(all((model["ports"][p] & model["ports"][q]).bit_count() % 2 == (p == q)
                     for c in model["small_cliques"] for p in c for q in c), "Actual eight-cliques")
            u, v = rows(model["correction_U"]), rows(model["correction_V"])
            need(helper.eliminate(u, 16)[0] == helper.eliminate(v, 112)[0] == 16, "Rank16 factors")
            need(all(apply(u, apply(v, unit(112, j))) ==
                     [c - (i == j) for i, c in enumerate(columns[j])] for j in range(112)), "UV factor")
            need(all(columns[j][i] == columns[i][j] and
                     inverse_columns[j][i] == inverse_columns[i][j] for i in range(112) for j in range(112)),
                 "Symmetric response and inverse")
            need("common_frame_words" not in model, "No unverified odd scalar word")
            need(any(c.denominator % 31 == 0 for row in hi for c in row.values()), "Prime31 is present")
        else:
            for name, word in model["common_frame_words"].items():
                expect = inverse_columns if "inverse" in name else columns
                if "transpose" in name:
                    expect = [list(r) for r in zip(*expect)]
                norm_sums, tariff = [F(0)] * len(word), 0
                for op, target, origin, text in word:
                    c = F(text)
                    a, b = abs(c.numerator), c.denominator
                    need(0 <= target < 112 and a != 0 and b & (b - 1) == 0, "Data-only dyadic word")
                    need((op == "scale" and origin is None and a & (a - 1) == 0) or
                         (op == "add" and isinstance(origin, int) and
                          0 <= origin < 112 and origin != target), "Literal scalar grammar")
                    tariff += (2 * (abs(a.bit_length() - b.bit_length()) + (c < 0)) if op == "scale"
                               else 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length()))
                for j in range(112):
                    x = unit(112, j)
                    for t, (op, target, origin, text) in enumerate(word):
                        c = F(text)
                        x[target] = c * x[target] if op == "scale" else x[target] + c * x[origin]
                        norm_sums[t] += abs(x[target])
                    need(x == expect[j], "Reciprocal literal scalar word")
                need(tariff == 3210, "Reciprocal scalar invoice")
                code_reports[name] = {"columns": 112, "scalar": tariff,
                                      "prefix_row_norm": str(max([F(1)] + norm_sums))}
        reports[packet["kind"]] = {
            "columns_per_direction": 112,
            "correction_rank": 16 if odd else 30,
            "full_determinant": str(full_det),
            "ordinary_determinant": str(ordinary_det),
            "inverse_denominators": dict(sorted(Counter(c.denominator for row in ei for c in row.values()).items())),
            "ordinary_inverse_denominators": dict(sorted(Counter(c.denominator for row in hi for c in row.values()).items())),
            "scalar_words": code_reports,
        }
    receipt = {
        "status": "PASS_INDEPENDENT_RESPONSE_EXTENSIONS",
        "source_pins": PINS,
        "payload_decompressed_pins": PAYLOADS,
        "reports": reports,
        "scope": "Exact matrices and reciprocal-large scalar words. Native phases and odd-grid implementation are separate.",
    }
    output = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (HERE / "CHECKS.json").write_bytes(output)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(output).hexdigest())


if __name__ == "__main__":
    main()

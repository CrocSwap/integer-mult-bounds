#!/usr/bin/env python3
"""Independent integer arithmetic and inverse source parsing; NOT a Lean checker.
Python 3.12+, standard library only. SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from generate import ROOT, SHAPES, load_source, require, sparse_literal, check_generated


def dense(rows: list[list[list[int]]], columns: int) -> list[list[int]]:
    result = [[0] * columns for _ in rows]
    for i, entries in enumerate(rows):
        for j, a in entries:
            result[i][j] += a
    return result


def multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    require(bool(a) and bool(b), "Empty dense matrix")
    require(all(len(row) == len(b) for row in a), "Multiplication shape mismatch")
    columns = list(zip(*b))
    require(all(len(row) == len(b[0]) for row in b), "Ragged matrix")
    # All summands are retained, including zeros. Exact Python integers only.
    return [[sum(x * y for x, y in zip(row, col)) for col in columns] for row in a]


def read_emitted_values(text: str) -> dict[str, Any]:
    """Inverse parser for the emitted literal grammar, independent of render_data.
    Exact whole-source regeneration separately verifies the dispatch trees.
    This parser checks every emitted sparse row and metadata value, including empties.
    """
    obj: dict[str, Any] = {}
    leaf = re.compile(r"^\s*(\[.*\]) -- /([MPQW])/(\d+)$", re.M)
    entry = re.compile(r"\(⟨(\d+), by decide⟩, \((-?\d+) : Int\)\)")
    found: dict[str, dict[int, list[list[int]]]] = {k: {} for k in SHAPES}
    for match in leaf.finditer(text):
        literal, name, index_text = match.groups()
        index = int(index_text)
        require(index not in found[name], f"Duplicate emitted row {name}/{index}")
        values = [[int(c), int(a)] for c, a in entry.findall(literal)]
        require(sparse_literal(values) == literal, f"Bad emitted literal grammar {name}/{index}")
        found[name][index] = values
    for name, (nr, _) in SHAPES.items():
        require(set(found[name]) == set(range(nr)), f"Missing/extra emitted row {name}")
        obj[name] = [found[name][i] for i in range(nr)]

    def literal(name: str) -> Any:
        matches = re.findall(r"^def " + re.escape(name) + r"\s*:[^\n]*? := (.*)$", text, re.M)
        require(len(matches) == 1, f"Missing/duplicate metadata declaration {name}")
        # literal_eval is a bounded literal parser; never eval/exec or code execution.
        return ast.literal_eval(matches[0])

    obj["anchors"] = literal("anchors")
    reps = literal("basePairRepresentatives")
    require(len(reps) == len(dict(reps)), "Duplicate emitted representative key")
    obj["base_pair_representatives"] = dict(reps)
    obj["coordinates"] = [list(pair) for pair in literal("coordinateLabels")]
    obj["free_parameters"] = literal("freeParameters")
    obj["parameter_order"] = {"class_parameters": literal("parameterClassCount"),
                              "g_points": literal("gPoints")}
    obj["rank"] = literal("rankMetadata")
    return obj


def numeric_result(obj: dict[str, Any]) -> dict[str, Any]:
    matrices = {name: dense(obj[name], nc) for name, (_, nc) in SHAPES.items()}
    m, p, q, w = (matrices[name] for name in ("M", "P", "Q", "W"))
    mp, qp = multiply(m, p), multiply(q, p)
    pq, wm = multiply(p, q), multiply(w, m)
    mp_ok = all(a == 0 for row in mp for a in row)
    qp_ok = all(qp[i][j] == int(i == j) for i in range(33) for j in range(33))
    residual_ok = all(int(i == j) - pq[i][j] == wm[i][j]
                      for i in range(104) for j in range(104))
    require(mp_ok and qp_ok and residual_ok, "A genuine dense matrix identity failed")
    require(w[5][0] == 1 and obj["W"][5] == [[0, 1]], "Wrong corruption starting entry")
    bad = [row[:] for row in w]
    bad[5][0] = -1
    badwm = multiply(bad, m)
    mismatches = [[i, j, int(i == j) - pq[i][j], badwm[i][j]]
                  for i in range(104) for j in range(104)
                  if int(i == j) - pq[i][j] != badwm[i][j]]
    require(mismatches == [[5, 0, 1, -1], [5, 1, -1, 1],
                           [5, 4, -1, 1], [5, 5, 1, -1]],
            "Unexpected W corruption behavior")
    return {"status": "PYTHON_INTEGER_CHECK_ONLY_NOT_KERNEL_EVIDENCE",
            "identities": {"MP=0": mp_ok, "QP=I_33": qp_ok, "I_104-PQ=WM": residual_ok},
            "identity_scalar_obligations": 288 * 33 + 33 * 33 + 104 * 104,
            "dense_scalar_multiplications_four_products": 288*104*33 + 33*104*33 +
                                                          104*33*104 + 104*288*104,
            "damaged_entry": {"row": 5, "column": 0, "original": 1, "damaged": -1},
            "damaged_residual_mismatches_row_column_lhs_rhs": mismatches,
            "new_lean_executed": False}


def main() -> None:
    check_generated(ROOT)
    obj = load_source(ROOT)
    recovered = read_emitted_values((ROOT / "P112Data.lean").read_text(encoding="utf-8"))
    require(recovered == obj, "Inverse-parsed Lean constants differ from the JSON object")
    canonical = (json.dumps(recovered, sort_keys=True, ensure_ascii=False,
                            separators=(",", ":")) + "\n").encode("utf-8")
    report = numeric_result(recovered)
    report["inverse_literal_parser_all_fields_equal"] = True
    report["recovered_canonical_json_bytes"] = len(canonical)
    report["recovered_canonical_json_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

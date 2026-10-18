#!/usr/bin/env python3
"""Deterministic source binding for the fixed P112 fragment; Python 3.12+, stdlib.

--check is read-only. --write writes generated files ONLY, never the dependency
or the handwritten proof adapter/consequences. This is a source converter, not
a Lean verifier and not an E8 geometry verifier. All new Lean units need replay.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
JSON_BYTES = 13183
JSON_SHA = "a1b43a5a7a8dcce0b84858244c512e53e6c344877cc35e87937fedd2601f29d5"
BRIDGE_BYTES = 48758
BRIDGE_SHA = "a27494b0d40bbf7874fd9a875e468c67d11545b266e17bc98f2ca75c77f6ee40"
SHAPES = {"M": (288, 104), "P": (104, 33), "Q": (33, 104), "W": (104, 288)}
ENTRIES = {"M": 1152, "P": 195, "Q": 66, "W": 111}
TOP_KEYS = {"M", "P", "Q", "W", "anchors", "base_pair_representatives",
            "coordinates", "free_parameters", "parameter_order", "rank"}
HEADER = """/-
Copyright (c) 2026 Andrey Mas and contributors.
SPDX-License-Identifier: Apache-2.0
P112 numerical instance of the unchanged PR1497/PR1610 bridge.
SOURCE ONLY / NOT YET KERNEL CHECKED. Generated deterministically by generate.py.
Proof/source assistance: GPT-6 Pro through ChatGPT (operator-selected label).
-/
"""
OPTIONS = """
set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace P112Cert
open PR1497

"""


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key {key!r}")
        result[key] = value
    return result


def pinned_file(path: Path, size: int, digest: str) -> bytes:
    data = path.read_bytes()
    require(len(data) == size, f"{path.name}: unexpected byte count")
    require(hashlib.sha256(data).hexdigest() == digest,
            f"{path.name}: unexpected SHA256")
    require(data.endswith(b"\n") and b"\r" not in data,
            f"{path.name}: not the pinned LF-terminated UTF8 file")
    data.decode("utf-8")
    return data


def load_source(root: Path = ROOT) -> dict[str, Any]:
    raw = pinned_file(root / "P112.json", JSON_BYTES, JSON_SHA)
    pinned_file(root / "PR1497Bridge.lean", BRIDGE_BYTES, BRIDGE_SHA)
    obj = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    validate_values(obj)
    return obj


def validate_values(obj: Any) -> None:
    require(type(obj) is dict and set(obj) == TOP_KEYS, "Wrong top-level schema")
    for name, (nr, nc) in SHAPES.items():
        rows = obj[name]
        require(type(rows) is list and len(rows) == nr, f"{name}: wrong row count")
        count = 0
        for i, row in enumerate(rows):
            require(type(row) is list, f"{name}/{i}: not a list")
            previous = -1
            for e in row:
                require(type(e) is list and len(e) == 2, f"{name}/{i}: bad entry")
                col, coefficient = e
                require(type(col) is int and 0 <= col < nc, f"{name}/{i}: bad column")
                require(type(coefficient) is int and coefficient != 0,
                        f"{name}/{i}: noninteger/zero stored coefficient")
                require(previous < col, f"{name}/{i}: duplicate or reordered columns")
                previous = col
                count += 1
        require(count == ENTRIES[name], f"{name}: wrong stored entry count")
    require(type(obj["coordinates"]) is list and len(obj["coordinates"]) == 104,
            "Wrong coordinate count")
    for row in obj["coordinates"]:
        require(type(row) is list and len(row) == 2, "Bad coordinate label")
        require(all(type(x) is int for x in row), "Coordinate label is not integral")
        require(0 <= row[0] < 26 and 0 <= row[1] < 8, "Coordinate label out of bounds")
    require(type(obj["anchors"]) is list and len(obj["anchors"]) == 26,
            "Wrong anchor count")
    require(all(type(x) is int and 0 <= x < 8 for x in obj["anchors"]), "Bad anchor")
    reps = obj["base_pair_representatives"]
    require(type(reps) is dict and set(reps) == set(map(str, range(1, 8))), "Bad representatives")
    require(all(type(x) is int and 0 <= x < 26 for x in reps.values()), "Bad representative value")
    order = obj["parameter_order"]
    require(type(order) is dict and set(order) == {"class_parameters", "g_points"},
            "Wrong parameter_order schema")
    require(type(order["class_parameters"]) is int and order["class_parameters"] == 26,
            "Wrong class parameter count")
    require(order["g_points"] == [1, 2, 3, 4, 5, 6, 7] and
            all(type(x) is int for x in order["g_points"]), "Wrong parameter order")
    require(type(obj["free_parameters"]) is int and obj["free_parameters"] == 33,
            "Wrong free parameter count")
    require(type(obj["rank"]) is int and obj["rank"] == 71, "Wrong rank METADATA")


def footer(names: list[str]) -> str:
    return ("\nend P112Cert\n\nset_option pp.fullNames true\n" +
            "".join(f"#print axioms P112Cert.{name}\n" for name in names))


def finlit(i: int) -> str:
    # A bound proof, rather than Fin's modulo-reducing numeral notation.
    return f"⟨{i}, by decide⟩"


def sparse_literal(row: list[list[int]]) -> str:
    return "[" + ", ".join(f"({finlit(c)}, ({a} : Int))" for c, a in row) + "]"


def tree(rows: list[list[list[int]]], name: str,
         lo: int, hi: int, indent: int = 2) -> str:
    """Balanced ordinary if tree. For a valid index each leaf is its source row."""
    require(0 <= lo < hi <= len(rows), "Bad tree interval")
    sp = " " * indent
    if hi - lo == 1:
        return f"{sp}{sparse_literal(rows[lo])} -- /{name}/{lo}\n"
    mid = (lo + hi) // 2
    return (f"{sp}if i.val < {mid} then\n" + tree(rows, name, lo, mid, indent + 2) +
            f"{sp}else\n" + tree(rows, name, mid, hi, indent + 2))


def tree_leaf(index: int, lo: int, hi: int) -> int:
    # Source-converter sanity check. This does not stand in for any Lean theorem.
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if index < mid:
            hi = mid
        else:
            lo = mid
    return lo


def render_data(obj: dict[str, Any]) -> str:
    lines = [HEADER, "import P112Sparse\n", OPTIONS]
    names: list[str] = []
    used: set[str] = set()
    for name, (nr, nc) in SHAPES.items():
        used.add(name)
        require(all(tree_leaf(i, 0, nr) == i for i in range(nr)), "Tree order mismatch")
        lines.append(f"/-- Original sparse {name} rows, in original row/entry order. -/\n")
        lines.append(f"def {name}_entries (i : Fin {nr}) : List (Fin {nc} × Int) :=\n")
        lines.append(tree(obj[name], name, 0, nr))
        lines.append(f"\ndef {name} : Mat {nr} {nc} := fun i => Sparse.row ({name}_entries i)\n\n")
        names += [f"{name}_entries", name]
    used.add("anchors")
    lines.append("/-- Provenance metadata only; no class-completeness theorem is asserted. -/\n")
    lines.append("def anchors : List Nat := [" + ", ".join(map(str, obj["anchors"])) + "]\n\n")
    names.append("anchors")
    used.add("base_pair_representatives")
    pairs = ", ".join(f"({json.dumps(k)}, {v})" for k, v in obj["base_pair_representatives"].items())
    lines.append(f"def basePairRepresentatives : List (String × Nat) := [{pairs}]\n\n")
    names.append("basePairRepresentatives")
    used.add("coordinates")
    labels = ", ".join(f"({c}, {k})" for c, k in obj["coordinates"])
    lines.append(f"def coordinateLabels : List (Nat × Nat) := [{labels}]\n\n")
    names.append("coordinateLabels")
    used.add("free_parameters")
    lines.append(f"def freeParameters : Nat := {obj['free_parameters']}\n\n")
    names.append("freeParameters")
    used.add("parameter_order")
    lines.append(f"def parameterClassCount : Nat := {obj['parameter_order']['class_parameters']}\n\n")
    lines.append("def gPoints : List Nat := [" + ", ".join(map(str, obj["parameter_order"]["g_points"])) + "]\n\n")
    names += ["parameterClassCount", "gPoints"]
    used.add("rank")
    lines.append("/-- Inherited JSON metadata, NOT a formal matrix-rank statement. -/\n")
    lines.append(f"def rankMetadata : Nat := {obj['rank']}\n")
    names.append("rankMetadata")
    require(used == set(obj), "An input field was not rendered")
    return "".join(lines) + footer(names)


def pointer_escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")


def binding_ledger(obj: dict[str, Any]) -> str:
    """Every JSON node, including empty rows, is explicitly assigned a target."""
    lines = ["json_pointer\tnode_kind\tvalue_or_shape\tlean_binding\n"]
    targets = {"M": "M_entries", "P": "P_entries", "Q": "Q_entries", "W": "W_entries",
               "anchors": "anchors", "base_pair_representatives": "basePairRepresentatives",
               "coordinates": "coordinateLabels", "free_parameters": "freeParameters",
               "rank": "rankMetadata"}

    def walk(value: Any, path: str, target: str) -> None:
        if type(value) is dict:
            rep = json.dumps(list(value), ensure_ascii=False, separators=(",", ":"))
            lines.append(f"{path or '/'}\tobject_keys\t{rep}\t{target}\n")
            for key, child in value.items():
                if path == "":
                    dest = targets.get(key, "parameter_order (split below)")
                elif path == "/parameter_order":
                    dest = {"class_parameters": "parameterClassCount", "g_points": "gPoints"}[key]
                else:
                    dest = target + f"[{json.dumps(key)}]"
                walk(child, path + "/" + pointer_escape(key), dest)
        elif type(value) is list:
            lines.append(f"{path}\tarray_length\t{len(value)}\t{target}\n")
            for i, child in enumerate(value):
                walk(child, path + f"/{i}", target + f"[{i}]")
        else:
            require(type(value) is int, f"Unexpected JSON scalar at {path}")
            lines.append(f"{path}\tinteger\t{value}\t{target}\n")

    walk(obj, "", "P112Cert constants and fixed matrix shapes")
    return "".join(lines)


def row_statement(kind: str, row: str) -> str:
    if kind == "mp":
        return f"∀ j : Fin 33, Sparse.eval (M_entries {row}) P j = 0"
    if kind == "qp":
        return f"∀ j : Fin 33, Sparse.eval (Q_entries {row}) P j = eye 33 {row} j"
    if kind == "residual":
        return (f"∀ j : Fin 104, eye 104 {row} j - Sparse.eval (P_entries {row}) Q j =\n"
                f"      Sparse.eval (W_entries {row}) M j")
    raise ValueError(kind)


def render_rows(kind: str, lo: int, hi: int) -> str:
    text = HEADER + "import P112Data\n" + OPTIONS
    names: list[str] = []
    for i in range(lo, hi):
        name = f"{kind}_row_{i:03}"
        names.append(name)
        text += (f"/-- Complete {kind} row {i}, not a sampled set of columns. -/\n"
                 f"theorem {name} :\n    {row_statement(kind, finlit(i))} := by\n"
                 "  decide\n\n")
    return text + footer(names)


def forall_assembly(kind: str, n: int) -> str:
    # Balance the proof tree too: no 288-deep nested eliminator expression.
    # Expected types supply the restricted predicates under castAdd/natAdd.
    def assemble(lo: int, hi: int, indent: int) -> str:
        sp = " " * indent
        if hi - lo == 1:
            return f"{sp}(Fin.forall_fin_one.mpr {kind}_row_{lo:03})"
        mid = (lo + hi) // 2
        return (f"{sp}(Sparse.allFinAdd (a := {mid-lo}) (b := {hi-mid})\n" +
                assemble(lo, mid, indent + 2) + "\n" +
                assemble(mid, hi, indent + 2) + ")")
    return (f"theorem {kind}_sparse_all : ∀ i : Fin {n},\n"
            f"    {row_statement(kind, 'i')} := by\n  exact\n" +
            assemble(0, n, 4) + "\n\n")


def render_certificate(modules: list[str]) -> str:
    text = HEADER + "".join(f"import {m}\n" for m in modules) + OPTIONS
    for kind, n in (("mp", 288), ("qp", 33), ("residual", 104)):
        text += forall_assembly(kind, n)
    text += """/-- Equality for the imported bridge's ordinary Int matrix product. -/
theorem mp : matMul M P = zeroMat 288 33 := by
  funext i j
  change rowMul (Sparse.row (M_entries i)) P j = (0 : Int)
  exact (congrArg (fun v : Row 33 => v j)
    (Sparse.rowMul_row (M_entries i) P)).trans (mp_sparse_all i j)

/-- Equality for the imported bridge's ordinary Int matrix product. -/
theorem qp : matMul Q P = eye 33 := by
  funext i j
  change rowMul (Sparse.row (Q_entries i)) P j = eye 33 i j
  exact (congrArg (fun v : Row 33 => v j)
    (Sparse.rowMul_row (Q_entries i) P)).trans (qp_sparse_all i j)

/-- The full 104-by-104 residual, with the original row orientation and W signs. -/
theorem residual : matSub (eye 104) (matMul P Q) = matMul W M := by
  funext i j
  change eye 104 i j - rowMul (Sparse.row (P_entries i)) Q j =
    rowMul (Sparse.row (W_entries i)) M j
  have hp := congrArg (fun v : Row 104 => v j)
    (Sparse.rowMul_row (P_entries i) Q)
  change rowMul (Sparse.row (P_entries i)) Q j =
    Sparse.eval (P_entries i) Q j at hp
  have hw := congrArg (fun v : Row 104 => v j)
    (Sparse.rowMul_row (W_entries i) M)
  change rowMul (Sparse.row (W_entries i)) M j =
    Sparse.eval (W_entries i) M j at hw
  rw [hp, hw]
  exact residual_sparse_all i j

/-- No certificate hypothesis: the three fields are the proved numerical equalities. -/
theorem certificate : MatrixIdentities M P Q W :=
  { mp := mp, qp := qp, residual := residual }
"""
    return text + footer(["mp_sparse_all", "qp_sparse_all", "residual_sparse_all",
                          "mp", "qp", "residual", "certificate"])


def generated_files(obj: dict[str, Any]) -> dict[str, bytes]:
    result: dict[str, str] = {"P112Data.lean": render_data(obj),
                              "BINDING.tsv": binding_ledger(obj)}
    modules: list[str] = []
    for kind, n, batch, prefix in (("mp", 288, 16, "MP"),
                                    ("qp", 33, 16, "QP"),
                                    ("residual", 104, 8, "Residual")):
        for unit, lo in enumerate(range(0, n, batch)):
            module = f"P112.{prefix}{unit:02}"
            modules.append(module)
            result[module.replace(".", "/") + ".lean"] = render_rows(kind, lo, min(n, lo + batch))
    result["P112Certificate.lean"] = render_certificate(modules)
    plan = ["PR1497Bridge.lean", "P112Sparse.lean", "P112Data.lean"]
    plan += [m.replace(".", "/") + ".lean" for m in modules]
    plan += ["P112Certificate.lean", "P112Consequences.lean", "P112Damaged.lean"]
    result["REPLAY_PLAN.json"] = json.dumps({
        "positive_units": plan,
        "negative_units": ["fixtures/RejectDamagedW.lean"],
        "per_unit_seconds": 120,
        "successor_total_seconds": 600,
        "dependency_excluded_from_successor_total": "PR1497Bridge.lean",
        "maximum_columns_per_decision": 104,
        "new_heartbeat_limit_per_command": 1000000,
        "new_recursion_limit": 4096,
    }, indent=2, ensure_ascii=False) + "\n"
    result["GENERATED_FILES.txt"] = "".join(x + "\n" for x in sorted([*result, "GENERATED_FILES.txt"]))
    return {name: content.encode("utf-8") for name, content in result.items()}


def check_generated(root: Path = ROOT) -> dict[str, Any]:
    obj = load_source(root)
    files = generated_files(obj)
    for name, expected in files.items():
        require((root / name).read_bytes() == expected, f"Generated source mismatch: {name}")
    expected_staged = {name for name in files if name.startswith("P112/")}
    actual_staged = {str(p.relative_to(root)) for p in (root / "P112").glob("*.lean")}
    require(actual_staged == expected_staged, "Missing/extra staged Lean file")
    return {"status": "SOURCE_BINDING_ONLY", "generated_files": len(files),
            "pinned_json_bytes": JSON_BYTES, "pinned_json_sha256": JSON_SHA,
            "pinned_bridge_bytes": BRIDGE_BYTES, "pinned_bridge_sha256": BRIDGE_SHA,
            "stored_entries": ENTRIES, "no_lean_execution": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Read-only exact regeneration check")
    mode.add_argument("--write", action="store_true", help="Write deterministic generated files")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.write:
        obj = load_source(root)
        for name, data in generated_files(obj).items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps(check_generated(root), indent=2))


if __name__ == "__main__":
    main()

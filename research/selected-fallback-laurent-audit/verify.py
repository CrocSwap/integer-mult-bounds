#!/usr/bin/env python3
"""Independent symbolic audit of pinned PR2207 compiler words.

The compiler and coefficient evaluator are the system under test. Only its
bank-read boundary and arithmetic are instrumented with Laurent polynomials.
The separate endpoint oracle imports no predecessor matrix/reconstruction code.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
import gzip
from hashlib import sha1, sha256
import importlib
import json
from math import gcd
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from laurent import Ring, add_row, identity, mismatch, require, scale_row

SEED = 67


class EndpointMismatch(ValueError):
    def __init__(self, entry, ring):
        super().__init__("symbolic endpoint mismatch: " + str(entry)[:500])
        self.entry, self.ring = entry, ring

    def concrete_witness(self):
        """A small actual unit assignment, not just a nonzero formal polynomial."""
        i, j, actual, expected = self.entry
        variables = sorted({v for poly in (actual, expected) for powers in poly for v, _ in powers})
        assignment = {v: 1 for v in variables}
        candidates = [None] + [(v, x) for v in variables
                               for x in range(2, self.ring.modulus) if gcd(x, self.ring.modulus) == 1]
        for change in candidates:
            if change:
                assignment[change[0]] = change[1]
            a, b = (self.ring.evaluate(poly, assignment) for poly in (actual, expected))
            if a != b:
                return {"output_atom": i, "input_basis_atom": j, "modulus": self.ring.modulus,
                        "default_weight": 1, "weight_overrides": {} if change is None else {str(change[0]): change[1]},
                        "actual": a, "expected": b}
            if change:
                assignment[change[0]] = 1
        raise ValueError("control needs a richer concrete witness search")


def authentic(raw, expected, label):
    require(sha256(raw).hexdigest() == expected, "source digest: " + label)
    return raw


def sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            data[item["path"]] = authentic((ROOT / item["path"]).read_bytes(),
                                             item["sha256"], item["path"])
    for item in manifest["vendored"]:
        authentic((HERE / item["path"]).read_bytes(), item["sha256"], item["path"])
    sys.path.insert(0, str(HERE / "vendor"))
    return data, importlib.import_module("fallback_program")


def selected_binding(data):
    base = "research/community-hyperplane599-audit/pr589/bit589/v9/hosted/"
    decoded = gzip.decompress(data[base + "GLOBAL-TEMPLATE.json.gz"])
    template = json.loads(decoded)
    receipt = json.loads(data[base + "GLOBAL.json"])
    raw = data["research/e8-bit-p111-tuned/tune/EXPECTED.json"]
    expected = json.loads(raw)
    assembly = json.loads(data["research/community-frontier1094-audit/ASSEMBLY.json"])
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(assembly["bit_supplier"]["pr"] == 589 and
            assembly["bit_supplier"]["git_blob_sha1"] == blob, "selected BIT citation")
    require(sha256(decoded).hexdigest() == receipt["template_sha256"], "template payload")
    require(receipt["word_sha256"] == expected["word"]["file_sha256"], "selected word")
    require(template["m"] == 64, "selected dimension")
    idle = [x for x in template["schedule"] if x["kind"] == "idle" and x["idx"] == 6]
    require(idle == [dict(idx=6, kind="idle", pair=0, rank=42,
                          source_level=2, target_level=8)], "selected idle child")
    require(not any(s[0] == 6 and s[1] == 213 for s in template["hosting"]["slots"]),
            "selected unhosted copy")
    require(template["hosting"]["remainders"]["6"] == {"2": 213, "42": 9},
            "selected remainder")
    require(expected["nine"]["profile"]["42"] == 288, "rank-42 multiplicity")
    return {"m": 64, "rank": 42, "idle_child": 6, "copy": 213,
            "selected_kappa": assembly["kappa"], "scope": "conditional GL64 charts"}


def integer_eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def product(a, b, modulus):
    bt = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) % modulus for col in bt] for row in a]


def projector_fixture(q, dense=False):
    """Explicit chart/inverse; no Gaussian elimination in the endpoint oracle.

    h has determinant-one blocks on (0,43) and (1,42). A column permutation S
    maps selected axes 22..63 to the first42. The optional dense high lift
    U=I+q*C has explicit inverse I-q*C modulo q^2.
    """
    modulus, m, rank = q*q, 64, 42
    h, hi = integer_eye(m), integer_eye(m)
    for i, j, a, b, c, d in ((0, 43, q, q-1, 1, 1), (1, 42, 1, 0, 1, 1)):
        require(a*d-b*c == 1, "fixture determinant")
        h[i][i], h[i][j], h[j][i], h[j][j] = a, b, c, d
        hi[i][i], hi[i][j], hi[j][i], hi[j][j] = d, -b, -c, a
    if dense:
        c = [[(SEED + 17*i + 29*j + i*j) % q for j in range(m)] for i in range(m)]
        u = [[int(i == j)+q*c[i][j] for j in range(m)] for i in range(m)]
        ui = [[int(i == j)-q*c[i][j] for j in range(m)] for i in range(m)]
        h, hi = product(u, h, modulus), product(hi, ui, modulus)
    require(product(h, hi, modulus) == integer_eye(m), "explicit chart inverse")
    p = [[sum(h[i][k]*hi[k][j] for k in range(rank)) % modulus
          for j in range(m)] for i in range(m)]
    require(product(p, p, modulus) == p, "projector idempotence")
    require(p[0][0] % q == 0, "nongeneric bad-class fixture")
    matrix = []
    for output in range(2*m):
        row = []
        for source in range(2*m):
            if output < m and source < m:
                value = int(output == source) - p[output][source]
            elif output < m:
                value = p[output][2*m-1-source]
            elif source < m:
                value = p[2*m-1-output][source]
            else:
                value = int(output == source) - p[2*m-1-output][2*m-1-source]
            row.append(value % modulus)
        matrix.append(row)
    require(product(matrix, matrix, modulus) == integer_eye(2*m), "residual involution")
    return matrix


def direct_operator(matrix, m, f, ring):
    """Full physical atom operator, independently from the emitted factors."""
    def address(field, column):
        return field*f + (column if field < m else f-1-column)
    out = [{} for _ in range(2*m*f)]
    for i, row in enumerate(matrix):
        for k, scalar in enumerate(row):
            if scalar:
                for j in range(f):
                    a = ring.variable(i*f+j) if i < m else ring.scalar(1)
                    b = ring.variable(k*f+j) if k < m else ring.scalar(1)
                    out[address(i, j)][address(k, j)] = ring.mul(scalar, ring.mul(a, ring.inv(b)))
    return out


@contextmanager
def symbolic_reads(compiler, m, f, ring):
    """Instrument only bank reads; preserve the coefficient function and word."""
    original = compiler.bank_weight
    def read(_prepared, field, column):
        require(0 <= field < 2*m and 0 <= column < f, "symbolic bank read bounds")
        return ring.variable(field*f+column) if field < m else ring.scalar(1)
    compiler.bank_weight = read
    try:
        yield
    finally:
        compiler.bank_weight = original


def execute(compiler, matrix, modulus, columns=3, mutation=None):
    """Source word and coefficient function; independent operator interpreter."""
    m, f = len(matrix)//2, columns
    ring = Ring(modulus)
    plan = compiler.elimination(matrix, modulus)
    operations = list(compiler.compile_program(plan))
    if mutation == "drop_zero_slot":
        k = next(i for i, op in enumerate(operations)
                 if op.kind == "lower" and op.coefficient.scalar == 0)
        del operations[k]
    require(sum(op.kind == "lower" for op in operations) == 2*m*(2*m-1),
            "complete shear-slot coverage")
    if mutation == "wrong_order":
        start = next(i for i, op in enumerate(operations) if op.coefficient.reduction_index >= 0)
        operations[start:] = operations[start:][::-1]
    if mutation == "drop_pair_weight":
        k = next(i for i, op in enumerate(operations) if op.coefficient.kind == "pair"
                 and op.coefficient.permutation[op.coefficient.first] != op.coefficient.first)
        operations[k] = replace(operations[k], coefficient=compiler.Coefficient(
            "fixed", scalar=operations[k].coefficient.scalar))
    if mutation == "omit_sign":
        require(any(op.kind == "sign" for op in operations), "sign control fixture")
        operations = [op for op in operations if op.kind != "sign"]
    if mutation == "inverse_sign":
        k = next(i for i, op in enumerate(operations) if op.kind == "lower" and op.coefficient.scalar)
        operations[k] = replace(operations[k], coefficient=replace(operations[k].coefficient,
                                  scalar=-operations[k].coefficient.scalar % modulus))
    prepared = SimpleNamespace(plan=plan, arithmetic=ring, modulus=modulus)
    out = identity(ring, 2*m*f)
    kinds = Counter()
    with symbolic_reads(compiler, m, f, ring):
        for op in operations:
            d = op.coefficient
            for t in range(f):
                column = compiler.logical_column(op.target, t, m, f)
                if mutation == "wrong_orientation" and op.kind == "lower":
                    column = compiler.logical_column(d.first, t, m, f)
                c = ring.coerce(compiler.coefficient(prepared, d, column,
                                      final_permutation=mutation == "final_permutation"))
                i = op.target*f+t
                logical = t if op.target < m else f-1-t
                k = op.source*f + (logical if op.source < m else f-1-logical)
                if op.kind == "lower":
                    require(op.target > op.source, "physical ADD order")
                    out[i] = add_row(ring, out[i], out[k], c)
                elif op.kind == "swap":
                    a, b = out[i], out[k]
                    out[i], out[k] = scale_row(ring, b, c), scale_row(ring, a, ring.inv(c))
                elif op.kind == "sign":
                    out[i] = scale_row(ring, out[i], c)
                else:
                    raise ValueError("unknown instruction")
            kinds[op.kind] += 1
    expected = direct_operator(matrix, m, f, ring)
    error = mismatch(out, expected)
    if error is not None:
        raise EndpointMismatch(error, ring)
    return {"modulus": modulus, "dimension": 2*m, "columns": f,
            "independent_weight_variables": m*f, "matrix_entries": (2*m*f)**2,
            "nonzero_endpoint_entries": sum(map(len, expected)),
            "instructions": dict(sorted(kinds.items())),
            "zero_shear_slots": sum(op.kind == "lower" and not op.coefficient.scalar for op in operations),
            "swaps_in_elimination": sum(op[0] == "swap" for op in plan.operations),
            "input_matrix_sha256": sha256(json.dumps(matrix, separators=(",", ":")).encode()).hexdigest()}


def reject(action, label, expected):
    try:
        action()
    except ValueError as exc:
        require(str(exc).startswith(expected), "wrong rejection for " + label + ": " + str(exc))
        result = {"control": label, "status": "REJECT", "reason": str(exc).split(":")[0]}
        if isinstance(exc, EndpointMismatch):
            result["witness"] = exc.concrete_witness()
        return result
    raise ValueError("negative control passed: " + label)


def run():
    data, compiler = sources()
    selected = selected_binding(data)
    records = []
    for q, dense in ((3, False), (5, False), (7, False), (5, True)):
        record = execute(compiler, projector_fixture(q, dense), q*q)
        record["chart"] = "dense-high-lift-seed67" if dense else "predecessor-block-chart"
        records.append(record)
    require(records[3]["nonzero_endpoint_entries"] > records[1]["nonzero_endpoint_entries"],
            "dense fixture must add coefficient coverage")
    # Determinant-minus-one stress fixture, not a selected rank-42 instance.
    toy = [[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    toy_result = execute(compiler, toy, 9, 2)
    controls = []
    sparse = projector_fixture(5)
    for mutation in ("final_permutation", "wrong_order", "inverse_sign",
                     "drop_pair_weight", "wrong_orientation", "drop_zero_slot"):
        reason = "complete shear-slot coverage" if mutation == "drop_zero_slot" else "symbolic endpoint mismatch"
        controls.append(reject(lambda name=mutation: execute(compiler, sparse, 25, 3, name), mutation, reason))
    controls.append(reject(lambda: execute(compiler, toy, 9, 2, "omit_sign"), "omit_fixed_sign",
                           "symbolic endpoint mismatch"))
    controls.append(reject(lambda: Ring(9).inv(Ring(9).scalar(3)), "invert_nonunit", "nonunit coefficient"))
    controls.append(reject(lambda: authentic(b"changed", sha256(b"original").hexdigest(), "fixture"),
                           "changed_source_bytes", "source digest"))
    return {"status": "PASS_SELECTED_FALLBACK_LAURENT_AUDIT", "seed": SEED,
            "selected": selected, "fixtures": records, "sign_fixture": toy_result,
            "selected_matrix_entries_checked": sum(x["matrix_entries"] for x in records),
            "selected_shear_slots_retained": sum(x["instructions"]["lower"] for x in records),
            "controls": controls, "scope": "Fixed matrices; universal unit ancestor weights. No new kappa."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-result", type=Path)
    args = ap.parse_args()
    result = run()
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "committed result differs")
    print("PASS_SELECTED_FALLBACK_LAURENT_AUDIT selected_charts=4 weights_per_chart=192 controls=9 no_new_kappa")


if __name__ == "__main__":
    main()

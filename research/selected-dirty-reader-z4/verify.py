#!/usr/bin/env python3
"""Selected dirty centre reader: a source-bound paired-cycle obstruction.

By ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
Native interpretation retains the pinned exact unitary-frame identities.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import io
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
PREFIX = "candidate/strict/global/base/providers/gauge44/"
MEMBERS = {
    "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "LOCAL-CHECKS.json": "2b8b1891a736598010232bfb26abc31973b265a53a2009a3fcfd9138b5ecadb4",
    "SCALAR-FRAME-AUDIT.json": "0e2a979aae1b948e1bee6c49c218f3ce7d7df00814b3f53b3d0866497510a28b",
    "CLIFFORD-RECIPES.json": "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "CLIFFORD-REVIEW.json": "cb0e10a8b284f176526c17177e91186ce09aa3e88b4f6acc561051daa072b0d0",
    "RESIDUAL-ADAPTERS.json": "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}
Q_ROWS = (3, 0, 1, 2, 7, 4, 5, 6)
CENTRES = (92, 57, 81, 224, 11, 240, 9, 256)
NORMS = (150, 130, 146, 134, 122, 126, 142, 146)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()


def load(root=ROOT):
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    inputs = {}
    for pin in sources["files"]:
        if pin["usage"] == "input":
            raw = (root / pin["path"]).read_bytes()
            need(digest(raw) == pin["sha256"], "live source hash: " + pin["path"])
            inputs[pin["path"]] = raw
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text(encoding="utf-8"))
    need(predecessor["head_commit"] == "f364b97ff4700147fc06e622b79952b9fe6c4fa8" and
         predecessor["sha256"] == "6de043bdef2f652ca3b179e0d61e0ac127a8981378ac4f5a5f800d200f122690",
         "PR2464 handoff pin")
    need(digest((HERE / predecessor["retained_path"]).read_bytes()) == predecessor["sha256"],
         "retained PR2464 handoff bytes")
    decoded = {}
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE]), mode="r:gz") as archive:
        for name, expected in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == PREFIX + name]
            need(len(matches) == 1 and matches[0].isfile(), "unique member: " + name)
            raw = archive.extractfile(matches[0]).read()
            need(digest(raw) == expected, "member hash: " + name)
            decoded[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return decoded


def binary_basis(vectors):
    basis = {}
    for vector in vectors:
        for bit in sorted(basis, reverse=True):
            if vector >> bit & 1:
                vector ^= basis[bit]
        if vector:
            basis[vector.bit_length() - 1] = vector
    return basis


def monomial(recipe):
    """A bijective affine address map times powers of i is exactly unitary."""
    rows = recipe["matrix_rows"]
    need(len(rows) == 9 and all(type(r) is int and 0 <= r < 512 for r in rows), "monomial rows")
    need(len(binary_basis(rows)) == 9, "invertible monomial")
    need(type(recipe["offset"]) is int and 0 <= recipe["offset"] < 512, "monomial offset")
    need(type(recipe["phase"]) is int and recipe["phase"] in range(4), "unit phase")
    need(len(recipe["linear_Z4"]) == len(recipe["quadratic_rows"]) == 9, "phase dimensions")
    need(all(type(x) is int and x in range(4) for x in recipe["linear_Z4"]), "linear phase")
    need(all(type(x) is int and 0 <= x < 512 for x in recipe["quadratic_rows"]), "quadratic phase")


def typed_segment(data, events=None):
    word = data["CANONICAL-WORD.json.gz"]
    complete = data["LOCAL-PROGRAMS.json.gz"]["forward"]
    need(digest(encoded(complete)) == data["LOCAL-CHECKS.json"]["forward"]["sha256"], "emitted program binding")
    need((word["v"], word["R"], word["h"]) == (112, 480, 9), "selected dimensions")
    need(tuple(word["centers"]) == CENTRES, "ordered centre fields")
    first = complete.index(["phase", "entry_adapters"])
    last = complete.index(["phase", "centers"])
    prefix_scalars = 0
    for event in complete[:first]:
        if event == ["phase", "zero_frame_precondition"]:
            continue
        need(event[0] == "scalar", "invertible pre-entry prefix")
        op, frame = event[1:]
        need(op[0] in ("add", "scale") and frame == 0, "zero-frame prefix alphabet")
        fields = [op[1]] + ([op[2]] if op[0] == "add" else [])
        need(all(f[0] == "L" and word["start"][f[1]] == 0 for f in fields), "prefix field frame")
        if op[0] == "add":
            need(op[1] != op[2] and F(op[3], op[4]) != 0, "invertible prefix addition")
        else:
            need(F(op[2], op[3]) != 0, "invertible prefix scale")
        prefix_scalars += 1
    segment = complete[first:last] if events is None else events
    frames = word["frames"]
    current = list(word["start"])
    need(len(current) == 704, "all arbitrary input fields")
    wrapped = {r for r in range(224, 704) if current[r] != 0 or word["final"][r] != 1}
    children = {(r["old"], r["new"]): r for r in data["CLIFFORD-RECIPES.json"]["children"]}
    seen, scalar, kinds = set(), [], Counter()
    for event in segment:
        kind = event[0]
        kinds[kind] += 1
        if kind in ("adapter", "residual_adapter"):
            if kind == "adapter":
                need(event[1] == "old_to_new", "entry direction")
            else:
                need(event[1] == "pre", "residual entry direction")
            field, frame = event[2:4]
            need(field not in seen and current[field] == frame, "one typed entry per field")
            need((kind == "residual_adapter") == (field in wrapped), "actual entry wrapper kind")
            if kind == "residual_adapter":
                terminal = event[4] if len(event) == 5 else 1
                need(terminal == word["final"][field], "residual terminal frame")
                key = str(frame) if terminal == 1 else str(frame) + ":" + str(terminal)
                need(key in data["RESIDUAL-ADAPTERS.json"]["recipes"], "residual recipe binding")
            seen.add(field)
        elif kind == "climb":
            _, part, field, old, new, rank = event
            need(part == "A" and current[field] == old, "climb source frame")
            need(len(binary_basis(frames[old] + frames[new])) == len(frames[new]), "nested frames")
            need(rank == len(frames[new]) - len(frames[old]) > 0, "climb rank")
            need((old, new) in children and children[old, new]["rank"] == rank, "emitted child recipe")
            current[field] = new
        elif kind == "scalar":
            op, frame = event[1:]
            need(op[0] in ("add", "scale") and op[1][0] == "L", "A scalar alphabet")
            target = op[1][1]
            need(current[target] == frame, "scalar target frame")
            if op[0] == "add":
                need(op[2][0] == "L" and op[2][1] != target, "independent scalar source")
                need(current[op[2][1]] == frame, "scalar source frame")
                need(F(op[3], op[4]) != 0, "nonzero addition")
            else:
                need(F(op[2], op[3]) != 0, "invertible scale")
            scalar.append(op)
        else:
            need(event in (["phase", "entry_adapters"], ["phase", "A"]), "known segment event")
    need(seen == set(range(704)), "complete entry inventory")
    need([current[c] for c in CENTRES] == word["center_frames"], "exact output frames")
    need(len(scalar) == 3451 and kinds["climb"] == 992, "exact segment extent")
    # Bind the inherited exact frame identities; independently check unitarity
    # of every emitted local monomial, without pretending it fixes constants.
    review = data["CLIFFORD-REVIEW.json"]
    need(review["all_child_equalities_include_global_phase"] is True, "retained exact phase contract")
    need(review["recipe_sha256"] == MEMBERS["CLIFFORD-RECIPES.json"], "retained recipe binding")
    need(review["canonical_word_sha256"] == MEMBERS["CANONICAL-WORD.json.gz"], "retained word binding")
    audit = data["SCALAR-FRAME-AUDIT.json"]
    need(audit["status"] == "PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES" and
         audit["live_columns_each_orientation"] == 704 and audit["helpers"] == 480,
         "retained scalar-frame audit")
    recipes = data["CLIFFORD-RECIPES.json"]["children"] + data["CLIFFORD-RECIPES.json"]["endpoint_adapters"]
    recipes += list(data["RESIDUAL-ADAPTERS.json"]["recipes"].values())
    checks = 0
    for recipe in recipes:
        for side in ("left", "right"):
            if recipe[side] is not None:
                monomial(recipe[side])
                checks += 1
    return scalar, {"event_range": [first, last], "event_counts": dict(kinds), "monomial_unitarity_checks": checks,
                    "invertible_pre_entry_scalar_gates": prefix_scalars,
                    "input_fields": 704, "output_fields": list(CENTRES), "output_frames": word["center_frames"]}


def sparse_add(target, source, coefficient):
    for index, value in source.items():
        target[index] = target.get(index, F(0)) + coefficient * value
        if not target[index]:
            del target[index]


def reader(gates):
    rows = [{i: F(1)} for i in range(704)]
    for gate in gates:
        target = gate[1][1]
        if gate[0] == "scale":
            rows[target] = {i: x * F(gate[2], gate[3]) for i, x in rows[target].items()}
        else:
            sparse_add(rows[target], rows[gate[2][1]], F(gate[3], gate[4]))
    result = [rows[i] for i in CENTRES]
    # Separate reverse pullback of eight covectors through the scalar word.
    reverse = [{i: F(1)} for i in CENTRES]
    for gate in reversed(gates):
        target = gate[1][1]
        for row in reverse:
            value = row.get(target, F(0))
            if gate[0] == "scale":
                if value:
                    row[target] = value * F(gate[2], gate[3])
            elif value:
                sparse_add(row, {gate[2][1]: value}, F(gate[3], gate[4]))
    need(result == reverse, "independent full-input pullback")
    return [[row.get(j, F(0)) for j in range(704)] for row in result]


def gram(rows):
    return [[sum(a*b for a, b in zip(r, s)) for s in rows] for r in rows]


def cycles(permutation):
    todo, result = set(range(len(permutation))), []
    while todo:
        at, cycle = min(todo), []
        while at in todo:
            todo.remove(at)
            cycle.append(at)
            at = permutation[at]
        result.append(cycle)
    return result


def rejects_every_paired_cycle(diagonal):
    rejected = []
    for permutation in itertools.permutations(range(8)):
        if sorted(map(len, cycles(permutation))) == [4, 4]:
            witnesses = [i for i in range(8) if diagonal[i] != diagonal[permutation[i]]]
            need(bool(witnesses), "paired cycle survives diagonal Gram condition")
            rejected.append([permutation, witnesses[0]])
    need(len(rejected) == 1260, "all paired-cycle output relabellings")
    return rejected


def check_signed_intertwiner(columns, P):
    need(len(P) == len(columns), "signed action dimension")
    need(len({p for p, _ in P}) == len(P), "data-only signed permutation")
    for j in range(len(P)):
        at, sign = j, 1
        for _ in range(4):
            at, edge = P[at]
            sign *= edge
        need((at, sign) == (j, 1), "data-only P fourth power")
        need(tuple(P[j][1]*x for x in columns[P[j][0]]) ==
             tuple(columns[j][i] for i in Q_ROWS), "RP equals QR")


def multiply(left, right):
    return [[sum(a*b for a, b in zip(row, col)) for col in zip(*right)] for row in left]


def calculate():
    data = load()
    gates, boundary = typed_segment(data)
    A = reader(gates)
    G = gram(A)
    diagonal = tuple(G[i][i] for i in range(8))
    need(diagonal == NORMS, "actual arbitrary-dirty row norms")
    need(max(Counter(diagonal).values()) == 2, "no possible four-cycle of equal row norms")
    rejected = rejects_every_paired_cycle(diagonal)
    R = [row[:112] for row in A]
    need(gram(R) == [[F(56 if i == j else 0) for j in range(8)] for i in range(8)], "data-only positive Gram control")
    columns = list(zip(*R))
    index = {column: j for j, column in enumerate(columns)}
    need(len(index) == 112 and len({min(c, tuple(-x for x in c)) for c in columns}) == 112, "unique signed data columns")
    P = []
    for column in columns:
        target = tuple(column[i] for i in Q_ROWS)
        sign = 1 if target in index else -1
        need(tuple(sign*x for x in target) in index, "data-only signed intertwiner exists")
        P.append((index[tuple(sign*x for x in target)], sign))
    check_signed_intertwiner(columns, P)
    need(any(sign < 0 for _, sign in P), "unsigned-permutation mutation changes the positive control")
    helper = [row[224] for row in A]
    transformed = [helper[i] for i in Q_ROWS]
    all_columns = set(zip(*A))
    need(tuple(transformed) not in all_columns and tuple(-x for x in transformed) not in all_columns, "explicit absent dirty helper image")
    # J = [R^T/56; 0] is a right inverse of A. Thus the deliberately
    # nonunitary P_t = I + J(Q^t-I)A supplies an algebraic escape, for t=1..4.
    J = [[R[k][j] / 56 for k in range(8)] for j in range(112)]
    need([[sum(A[i][j]*J[j][k] for j in range(112)) for k in range(8)] for i in range(8)] ==
         [[F(i == k) for k in range(8)] for i in range(8)], "explicit right inverse")
    identity = [[F(i == j) for j in range(8)] for i in range(8)]
    powers = [identity]
    for _ in range(4):
        powers.append([powers[-1][i] for i in Q_ROWS])
    need(powers[4] == identity and powers[2] != identity, "exact order four")
    differences = [[[power[i][j]-identity[i][j] for j in range(8)] for i in range(8)] for power in powers[:4]]
    for s, t in itertools.product(range(4), repeat=2):
        product = multiply(differences[s], differences[t])
        need([[differences[s][i][j]+differences[t][i][j]+product[i][j] for j in range(8)] for i in range(8)] ==
             differences[(s+t) % 4], "nonunitary low-rank group law")
    difference = [x-y for x, y in zip(transformed, helper)]
    delta = [sum(row[k]*difference[k] for k in range(8)) for row in J]
    escape_norm = 1 + sum(x*x for x in delta)
    need(escape_norm == F(8, 7), "nonunitary escape boundary")
    return {"status": "PASS_SELECTED_DIRTY_READER_Z4", "member_sha256": MEMBERS, "boundary": boundary,
            "reader": [[str(x) for x in row] for row in A], "gram": [[str(x) for x in row] for row in G],
            "row_norms": list(NORMS), "helper_only_row_norms": [n-56 for n in NORMS],
            "paired_cycle_rejections": rejected, "data_only_P_columns": P,
            "dirty_helper_witness": {"input": 224, "column": helper, "Q_column": transformed},
            "nonunitary_escape": {"formula": "I + J (Q-I) A, J=[R^T/56;0]", "norm_squared_on_e224": str(escape_norm),
                                  "low_rank_group_law_pairs": 16},
            "limits": "Exact selected entry-adapter-to-centres cut; all 704 dirty input fields. Unitary input actions and unitary block-permutation output actions with paired 4-cycles excluded. Exact native frame identities inherited; no global supplier claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    text = json.dumps(result, sort_keys=True, indent=2, default=str) + "\n"
    path = HERE / "RESULT.json"
    if args.write_result:
        with path.open("x", encoding="utf-8", newline="\n") as out:
            out.write(text)
    else:
        need(path.read_text(encoding="utf-8") == text, "committed receipt mismatch")
    print("PASS_SELECTED_DIRTY_READER_Z4 inputs=704 rows=8 paired_cycles=1260 data_only_control=pass nonunitary_escape=8/7 no_new_kappa")


if __name__ == "__main__":
    main()

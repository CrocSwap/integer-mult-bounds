"""Independent local two-anchor audit using reverse coordinate functionals.

Only the scalar projection and the local preparation are checked. No source,
primary, constructor or earlier campaign verifier is imported. CLEAR zeros
below concern the dual preparation, not forward erasure permission.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED, ZERO, FULL = 770, 29, 3, 127
ANCHORS = (224, 227)
PINS = {
    "sources/INPUT-WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "sources/OUTPUT-WORD.json.gz": ("e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491", "0af79e58172f85c302c35b193205c0b185b09393"),
    "sources/BASIS.json": ("28d01a60c1780dc61373a13ac70654c140fa20519abdac0dd78f24c8343a002f", "efa2be3e34cab2d15ceaf33ff43eab70ff4c12e6"),
    "sources/constructor-source.py": ("e18f0221827628e38674dc71198a95ccebc401476328e3db7569b84e4b7be969", "d92f1f92e705eafdda770ec19b958084584420a8"),
    "sources/upstream-PROOF.md": ("4d02ec61147085ed88c11340b369729c943b954a0cc41a9995ffc07d24f1a285", "3a670ce4c0ae727b4d3cd3604d67d45b189da3c7"),
    "sources/NOTICE": ("f13f42a39d4614b26d9871f5bc8fcb76e60cb44b4df8762cd51e505b43723e46", "9af7effd3a0ff5218d94331567022fd179a1e8fa"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def rational(value):
    require(type(value) is str, "Rational coefficient string")
    q = F(value)
    require(str(q) == value and q != 0, "Canonical nonzero rational coefficient")
    require(q.denominator & (q.denominator - 1) == 0, "Dyadic coefficient")
    return q


def authenticate():
    inventory = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    require(type(inventory) is list and len(inventory) == len(PINS), "Six exact source pins")
    require({r["file"]: (r["sha256"], r["git_blob"]) for r in inventory} == PINS,
            "Independently fixed source inventory")
    data = {}
    for name, (digest, blob) in PINS.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, "Exact source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Exact source Git blob: " + name)
        if name.endswith(".json.gz"):
            data[Path(name).name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            data[Path(name).name] = json.loads(raw)
    return data


def dual(word):
    require(type(word["public"]) is int and word["public"] == PUBLIC
            and type(word["owned_fields"]) is int and word["owned_fields"] == OWNED,
            "770 arbitrary public inputs and29 owned labels")
    role = list(range(PUBLIC + OWNED))
    require(type(word["live"]) is list and len(word["live"]) == 104, "104 main pairs")
    for r in word["live"]:
        integer(r, 0, PUBLIC - 112, "Main pair role")
        role[r], role[r + 112] = r + 112, r
    require(len(set(role)) == PUBLIC + OWNED, "Main-role exchange permutation")
    flip = lambda f: FULL if f == ZERO else ZERO if f == FULL else f
    initial = [None] * PUBLIC
    for r, frame in enumerate(word["final"]):
        initial[role[r]] = flip(frame)
    program = []
    for event in reversed(word["program"]):
        op, r = event[:2]
        integer(r, 0, PUBLIC + OWNED, "Literal role")
        if op == "MOVE":
            require(type(event[4]) is bool, "Boolean MOVE ownership")
            program.append([op, role[r], flip(event[3]), flip(event[2]), event[4]])
        elif op in ("INIT", "CLEAR"):
            program.append(["CLEAR" if op == "INIT" else "INIT", role[r], flip(event[2])])
        elif op in ("ADD", "COPY"):
            program.append(["ADD", role[event[2]], role[r], event[3], flip(event[4])])
        else:
            require(op == "SCALE", "Known scalar transpose opcode")
            program.append([op, role[r], event[2], flip(event[3])])
    # Non-extreme frame IDs are labels here, not constructed native complements.
    return initial, program


def typed_basis(operations):
    require(type(operations) is list, "Basis operation list")
    for event in operations:
        require(type(event) is list and event and event[0] in ("ADD", "SWAP", "SCALE"), "Basis opcode")
        require(len(event) == (4 if event[0] == "ADD" else 3), "Basis arity")
        integer(event[1], 0, PUBLIC, "Public basis destination")
        if event[0] in ("ADD", "SWAP"):
            integer(event[2], 0, PUBLIC, "Public basis source")
            require(event[1] != event[2], "Distinct elementary basis roles")
        if event[0] != "SWAP":
            rational(event[-1])
    return operations


def strip(event):
    return event[:-1] if event[0] in ("ADD", "COPY", "SCALE") else event


def source_preparation(initial, program):
    current = list(initial) + [None] * OWNED
    first, zero = {}, []
    for index, event in enumerate(program):
        op, r = event[:2]
        if op == "INIT":
            require(r >= PUBLIC and current[r] is None, "INIT inactive owned label")
            current[r] = event[2]
        elif op == "CLEAR":
            require(r >= PUBLIC and current[r] == event[2], "CLEAR active owned label/frame")
            current[r] = None
        elif op == "MOVE":
            require(current[r] == event[2] and event[4] == (r >= PUBLIC), "MOVE frame/ownership chronology")
            if r >= PUBLIC:
                require(ZERO not in event[2:4], "No owned transport through ZERO")
            else:
                require(event[3] != ZERO, "No public return to ZERO")
                if event[2] == ZERO:
                    require(r not in first, "One public departure from ZERO")
                    first[r] = (index, event[3])
            current[r] = event[3]
        else:
            require(current[r] == event[-1], "Actual scalar destination frame")
            if op in ("ADD", "COPY"):
                require(current[event[2]] == event[-1], "Actual scalar source frame")
            rational(event[-2])
        if op in ("INIT", "CLEAR", "ADD", "COPY", "SCALE") and event[-1] == ZERO:
            zero.append(event)
    require(all(x is None for x in current[PUBLIC:]), "Source owned lifetimes end")
    return zero, first


def bump(weights, role, coefficient):
    value = weights.get(role, F(0)) + coefficient
    if value:
        weights[role] = value
    else:
        weights.pop(role, None)


def functional(program, output):
    weights = {output: F(1)}
    for event in reversed(program):
        op, r = event[:2]
        if op == "INIT":
            weights.pop(r, None)
        elif op == "CLEAR":
            require(r not in weights, "Functional cannot reference an inactive post-CLEAR value")
        elif op == "SWAP":
            s = event[2]
            a, b = weights.pop(r, F(0)), weights.pop(s, F(0))
            bump(weights, r, b)
            bump(weights, s, a)
        elif op in ("ADD", "COPY"):
            value = weights.get(r, F(0))
            if op == "COPY":
                weights.pop(r, None)
            if value:
                bump(weights, event[2], rational(event[3]) * value)
        elif op == "SCALE":
            if r in weights:
                weights[r] *= rational(event[2])
        else:
            require(op == "MOVE", "Known pullback instruction")
    require(all(r < PUBLIC for r in weights), "Only original public coordinates remain")
    return weights


def encoded(row):
    return {str(r): str(q) for r, q in sorted(row.items())}


def push_column(program, input_role):
    values = [F(int(r == input_role)) for r in range(PUBLIC)] + [None] * OWNED
    for event in program:
        op, r = event[:2]
        if op == "INIT":
            require(values[r] is None, "Column INIT inactive label")
            values[r] = F(0)
        elif op == "CLEAR":
            require(values[r] == 0, "Source preparation CLEAR has zero value")
            values[r] = None
        elif op == "SWAP":
            values[r], values[event[2]] = values[event[2]], values[r]
        elif op == "SCALE":
            require(values[r] is not None, "Active scalar column role")
            values[r] *= rational(event[2])
        else:
            require(op in ("ADD", "COPY") and values[r] is not None
                    and values[event[2]] is not None, "Active scalar column operands")
            value = rational(event[3]) * values[event[2]]
            values[r] = value if op == "COPY" else values[r] + value
    return values


def inverse(operations):
    result = []
    for e in reversed(operations):
        if e[0] == "SWAP":
            result.append(list(e))
        elif e[0] == "ADD":
            result.append([e[0], e[1], e[2], str(-rational(e[3]))])
        else:
            result.append([e[0], e[1], str(1 / rational(e[2]))])
    return result


def zero_witness(program):
    clears = []
    for index, event in enumerate(program):
        if event[0] == "CLEAR":
            row = functional(program[:index], event[1])
            if row:
                r = min(row)
                return {"clear_index": index, "owned_role": event[1], "public_input": r,
                        "expected": "0", "actual": str(row[r])}, clears
            clears.append({"index": index, "role": event[1], "public_support": 0})
    return None, clears


def validate_prefix(initial, prefix):
    current = list(initial) + [None] * OWNED
    initialized, cleared = [], []
    for event in prefix:
        op, r = event[:2]
        require(op != "MOVE" and event[-1] == ZERO, "Local prefix uses only ZERO preparation")
        if op == "INIT":
            require(r >= PUBLIC and current[r] is None, "Candidate prefix INIT inactive")
            current[r] = ZERO
            initialized.append(r)
        elif op == "CLEAR":
            require(r >= PUBLIC and current[r] == ZERO, "Candidate prefix CLEAR active")
            current[r] = None
            cleared.append(r)
        else:
            require(current[r] == ZERO, "Candidate prefix scalar destination")
            if op in ("ADD", "COPY"):
                require(current[event[2]] == ZERO, "Candidate prefix scalar source")
            rational(event[-2])
    require(sorted(initialized) == sorted(cleared) == list(range(770, 781)), "Eleven distinct dual shadow lifetimes")
    require(all(x is None for x in current[PUBLIC:]), "No shadow survives the local prefix")


def run():
    data = authenticate()
    source, candidate, witness = data["INPUT-WORD.json.gz"], data["OUTPUT-WORD.json.gz"], data["BASIS.json"]
    source_initial, source_program = dual(source)
    candidate_initial, candidate_program = dual(candidate)
    A, first = source_preparation(source_initial, source_program)
    B0, B2, C = [typed_basis(witness[k]) for k in ("B0", "B2", "C")]
    require(all(e[0] == "ADD" and e[1] in ANCHORS and e[2] not in ANCHORS for e in B2),
            "B2 is a square-zero off-anchor correction")
    source_bad, source_clears = zero_witness(A)
    require(source_bad is None and len(source_clears) == 9,
            "All nine old ZERO preparation CLEAR functionals vanish on every public input")
    require(witness["anchors"] == list(ANCHORS) and witness["entries"] == {"224": 245, "227": 245}, "Exact two-anchor interface")
    main = set(source["live"]) | {r + 112 for r in source["live"]}
    helpers = {r for r in range(PUBLIC) if r not in main and source_initial[r] == ZERO
               and source["initial"][r] == ZERO}
    used = {e[1] for e in B0 + B2} | {e[2] for e in B0 + B2 if e[0] in ("ADD", "SWAP")}
    require(used <= helpers, "Input bases use only independent full helper coordinates")
    require(all(first[r][1] == 1091 for e in C for r in
                ([e[1], e[2]] if e[0] in ("ADD", "SWAP") else [e[1]])), "C stays within actual first-departure block1091")
    primitive_A = [strip(e) for e in A]
    # Full row functionals, not evaluations on two sample inputs.
    off, units = {}, {}
    for anchor in ANCHORS:
        row = functional(B0 + primitive_A + C, anchor)
        require({a: row.get(a, F(0)) for a in ANCHORS}
                == {a: F(int(a == anchor)) for a in ANCHORS}, "Unit anchor pairing before correction")
        off[anchor] = {r: q for r, q in row.items() if r != anchor}
        require(set(off[anchor]) <= helpers - set(ANCHORS), "Full off-anchor row has helper-only support")
        row = functional(B2 + B0 + primitive_A + C, anchor)
        require(row == {anchor: F(1)}, "Exact corrected unit functional on all770 public coordinates")
        units[str(anchor)] = encoded(row)
        require(encoded(off[anchor]) == witness["off_anchor"][str(anchor)], "All off-anchor coefficients match")
        expected_b2 = {anchor: F(1), **{r: -q for r, q in off[anchor].items()}}
        require(functional(B2, anchor) == expected_b2, "Exact B2 nilpotent correction row")
    for label, basis in (("B0", B0), ("B2", B2), ("C", C)):
        for role in range(PUBLIC):
            require(functional(basis + inverse(basis), role) == {role: F(1)}, "Independent basis inverse: " + label)
    expected_v = {227: 1, 228: 1, 229: -1, 232: -1, 233: 1, 238: -1, 239: 1, 449: -1}
    directions, response, pivot = {}, {}, []
    for anchor in ANCHORS:
        column = push_column(B0, anchor)
        direction = {r: value for r, value in enumerate(column[:PUBLIC]) if value}
        expected = {224: F(2), **{r: F(q if anchor == 224 else -q) for r, q in expected_v.items()}}
        require(direction == expected, "Exact arbitrary-input B0 direction")
        directions[str(anchor)] = encoded(direction)
        before_C = push_column(B0 + A, anchor)
        pivot.append([str(before_C[193] + before_C[742] / 2), str(before_C[169] + before_C[742] / 2)])
        values = push_column(B0 + A + C, anchor)
        for r, value in enumerate(values[:PUBLIC]):
            if value:
                response.setdefault(str(r), {})[str(anchor)] = str(value)
    require(pivot == [["1", "0"], ["0", "1"]], "Source-derived initial pivot evaluations")
    determinant = (F(directions["224"]["224"]) * F(directions["227"]["227"])
                   - F(directions["227"]["224"]) * F(directions["224"]["227"]))
    require(determinant == -4, "Exact dyadic-unit anchor determinant")
    require(response == witness["responses"] == {"119": {"224": "2", "227": "2"},
                "224": {"224": "1"}, "227": {"227": "1"}, "232": {"224": "-2", "227": "2"}}, "All four response rows")
    require(all(first[int(r)][1] == (1091 if int(r) in ANCHORS else 245) for r in response), "Primary/nonprimary response destination support")
    prefix_end = next(i for i, e in enumerate(candidate_program) if e[0] == "MOVE")
    require(prefix_end == witness["prep_length"] == 4759, "Exact actual local preparation length")
    prefix = candidate_program[:prefix_end]
    validate_prefix(candidate_initial, prefix)
    bad, clears = zero_witness(prefix)
    require(bad is None and len(clears) == 11, "Every actual dual preparation CLEAR functional is zero")
    controls = []
    sites = [2, 2 + len(B2), 2 + len(B2) + len(B0) + len(A)]
    for site in sites:
        require(prefix[site][0] in ("ADD", "SCALE"), "Semantic scalar mutation site")
        for action in ("omit", "sign"):
            altered = deepcopy(prefix)
            original = deepcopy(altered[site])
            if action == "omit":
                altered.pop(site)
            else:
                altered[site][-2] = str(-rational(altered[site][-2]))
            difference, _ = zero_witness(altered)
            require(difference is not None, "Actual-prefix scalar fault must change a CLEAR coefficient")
            controls.append({"site": site, "action": action, "original_event": original,
                             "clear_coefficient_witness": difference})
    return {"schema_version": 1, "status": "PASS_LOCAL_ONLY",
            "method": "independent reverse coordinate functionals and two forward input columns",
            "public_coordinates": PUBLIC, "source_zero_events": len(A),
            "old_zero_owned_labels": sorted(e[1] for e in A if e[0] == "INIT"),
            "anchors": list(ANCHORS), "anchor_block_determinant": str(determinant), "directions": directions,
            "source_old_zero_clears": source_clears,
            "departure_basis_main_roles": sorted({r for e in C for r in
                ([e[1], e[2]] if e[0] in ("ADD", "SWAP") else [e[1]]) if r in main}),
            "pivot_evaluations_by_input": pivot, "off_anchor_rows": {str(a): encoded(off[a]) for a in ANCHORS},
            "corrected_unit_rows": units, "responses": response, "actual_dual_prefix_events": prefix_end,
            "actual_dual_zero_clears": clears, "basis_inverse_public_coordinates": PUBLIC,
            "semantic_prefix_controls": controls,
            "limits": ["The whole candidate public endpoint and complete owned chronology remain for round2.",
                       "MOVE is identity in the scalar projection; non-extreme frame IDs are labels, not native operators.",
                       "Eleven zero CLEAR rows concern the dual preparation, not forward erasure permission.",
                       "No native, physical caller, invoice, all-width or kappa admission follows."]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: oracle_local.py [--emit]")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        retained = json.loads((HERE / "LOCAL-ORACLE.json").read_bytes())
        require(canonical(result) == canonical(retained), "Exact typed retained LOCAL-ORACLE.json receipt")
        print("PASS independent local pair functionals and retained receipt")

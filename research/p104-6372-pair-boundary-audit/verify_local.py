#!/usr/bin/env python3
"""Bounded rational preparation audit of PR6372's two-anchor contact block.

The scalar transpose schema credits the prior PR6355 independent audit.
MOVE is identity in this rational projection. No native complements, phases,
full-word endpoint, physical erasure or invoice are certified here.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED, ZERO, FULL = 770, 29, 3, 127
ANCHORS = (224, 227)
SHADOW = {224: 779, 227: 780}
PINNED = {
    "sources/OUTPUT-WORD.json.gz": [
        "e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491",
        "0af79e58172f85c302c35b193205c0b185b09393"
    ],
    "sources/BASIS.json": [
        "28d01a60c1780dc61373a13ac70654c140fa20519abdac0dd78f24c8343a002f",
        "efa2be3e34cab2d15ceaf33ff43eab70ff4c12e6"
    ],
    "sources/constructor-source.py": [
        "e18f0221827628e38674dc71198a95ccebc401476328e3db7569b84e4b7be969",
        "d92f1f92e705eafdda770ec19b958084584420a8"
    ],
    "sources/upstream-PROOF.md": [
        "4d02ec61147085ed88c11340b369729c943b954a0cc41a9995ffc07d24f1a285",
        "3a670ce4c0ae727b4d3cd3604d67d45b189da3c7"
    ],
    "sources/NOTICE": [
        "f13f42a39d4614b26d9871f5bc8fcb76e60cb44b4df8762cd51e505b43723e46",
        "9af7effd3a0ff5218d94331567022fd179a1e8fa"
    ],
    "sources/INPUT-WORD.json.gz": [
        "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928",
        "03ea7690285d4cda72815f962d5710ab96e08490"
    ]
}
START = time.monotonic()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def budget(rows):
    require(time.monotonic() - START < 30, "bounded local audit runtime")
    require(sum(map(len, rows)) <= 200000, "bounded local sparse coefficient inventory")


def inputs():
    result = {}
    for filename, (digest, blob) in PINNED.items():
        raw = (HERE / filename).read_bytes()
        require(sha256(raw).hexdigest() == digest, "source SHA256: " + filename)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "source Git blob: " + filename)
        if filename.endswith(".json.gz"):
            result[filename] = json.loads(gzip.decompress(raw))
        elif filename.endswith(".json"):
            result[filename] = json.loads(raw)
    return result


def q(value):
    require(type(value) is str, "rational coefficient string")
    coefficient = Fraction(value)
    require(coefficient and coefficient.denominator & (coefficient.denominator - 1) == 0,
            "nonzero dyadic coefficient")
    return coefficient


def unit_rows():
    return [{r: Fraction(1)} if r < PUBLIC else {} for r in range(PUBLIC + OWNED)]


def add(left, right, coefficient):
    result = dict(left)
    for key, value in right.items():
        updated = result.get(key, 0) + coefficient * value
        if updated:
            result[key] = updated
        else:
            result.pop(key, None)
    return result


def encoded(row):
    return [[key, str(value)] for key, value in sorted(row.items())]


def rows_digest(rows):
    return sha256((canonical([encoded(row) for row in rows]) + "\n").encode()).hexdigest()


def transpose(word):
    require(word["public"] == PUBLIC and word["owned_fields"] == OWNED, "frozen role counts")
    permutation = list(range(PUBLIC + OWNED))
    for role in word["live"]:
        require(type(role) is int and 0 <= role < PUBLIC and role + 112 < PUBLIC, "main role pair")
        permutation[role], permutation[role + 112] = role + 112, role
    require(len(set(permutation)) == PUBLIC + OWNED, "main-role permutation")
    label = lambda frame: FULL if frame == ZERO else ZERO if frame == FULL else frame
    initial, final = [None] * PUBLIC, [None] * PUBLIC
    for role in range(PUBLIC):
        initial[permutation[role]] = label(word["final"][role])
        final[permutation[role]] = label(word["initial"][role])
    program = []
    for event in reversed(word["program"]):
        op, role = event[:2]
        role = permutation[role]
        if op == "MOVE":
            program.append(["MOVE", role, label(event[3]), label(event[2]), event[4]])
        elif op in ("INIT", "CLEAR"):
            program.append(["CLEAR" if op == "INIT" else "INIT", role, label(event[2])])
        elif op in ("ADD", "COPY"):
            program.append(["ADD", permutation[event[2]], role, event[3], label(event[4])])
        else:
            require(op == "SCALE", "source scalar transpose opcode")
            program.append(["SCALE", role, event[2], label(event[3])])
    return {"initial": initial, "final": final, "program": program, "live": word["live"]}


def source_preparation(dual):
    current = dict(enumerate(dual["initial"]))
    first, zero = {}, []
    for index, event in enumerate(dual["program"]):
        op, role = event[:2]
        require(type(role) is int and 0 <= role < PUBLIC + OWNED, "dual role")
        if op == "MOVE":
            require(current.get(role) == event[2] and type(event[4]) is bool and
                    event[4] == (role >= PUBLIC), "dual MOVE source and ownership")
            if role >= PUBLIC:
                require(ZERO not in event[2:4], "no owned transport through ZERO")
            else:
                require(event[3] != ZERO, "public field never returns to ZERO")
                if event[2] == ZERO:
                    require(role not in first, "unique first departure")
                    first[role] = (index, event[3])
            current[role] = event[3]
        elif op == "INIT":
            require(role >= PUBLIC and role not in current, "dual INIT lifetime")
            current[role] = event[2]
        elif op == "CLEAR":
            require(role >= PUBLIC and current.get(role) == event[2], "dual CLEAR lifetime")
            del current[role]
        else:
            require(current.get(role) == event[-1], "dual scalar destination frame")
            if op != "SCALE":
                require(event[2] in current and current[event[2]] == event[-1], "dual scalar source frame")
        if op in ("INIT", "CLEAR", "ADD", "COPY", "SCALE") and event[-1] == ZERO:
            zero.append(event)
    require(current == dict(enumerate(dual["final"])), "dual structural endpoint frames")
    return zero, first


def execute_zero(program, initial, strict=True):
    rows = unit_rows()
    current = dict(enumerate(initial))
    clear_rows, initialized = [], []
    for index, event in enumerate(program):
        op, role = event[:2]
        require(event[-1] == ZERO, "local prefix stays in ZERO")
        if op == "INIT":
            require(role >= PUBLIC and role not in current, "local INIT lifetime")
            rows[role] = {}
            current[role] = ZERO
            initialized.append(role)
        elif op == "CLEAR":
            require(role >= PUBLIC and current.get(role) == ZERO, "local CLEAR lifetime")
            clear_rows.append({"index": index, "role": role, "row": dict(rows[role])})
            if strict:
                require(not rows[role], "preparation CLEAR has zero complete rational row")
            rows[role] = {}
            del current[role]
        else:
            require(current.get(role) == ZERO, "local scalar destination active at ZERO")
            if op == "SCALE":
                coefficient = q(event[2])
                rows[role] = {key: coefficient * value for key, value in rows[role].items()}
            else:
                require(op in ("ADD", "COPY") and current.get(event[2]) == ZERO, "local scalar source at ZERO")
                coefficient = q(event[3])
                if op == "COPY":
                    require(not rows[role], "local COPY destination zero")
                    rows[role] = {key: coefficient * value for key, value in rows[event[2]].items()}
                else:
                    rows[role] = add(rows[role], rows[event[2]], coefficient)
        if index % 128 == 0:
            budget(rows)
    require(not any(role >= PUBLIC for role in current), "all local owned lifetimes retire")
    return rows, clear_rows, initialized


def apply(rows, operations):
    for event in operations:
        op, role = event[:2]
        require(type(role) is int and 0 <= role < PUBLIC, "public basis role")
        if op in ("ADD", "SWAP"):
            require(type(event[2]) is int and 0 <= event[2] < PUBLIC and event[2] != role,
                    "distinct public basis source")
        if op == "ADD":
            rows[role] = add(rows[role], rows[event[2]], q(event[3]))
        elif op == "SCALE":
            coefficient = q(event[2])
            rows[role] = {key: coefficient * value for key, value in rows[role].items()}
        else:
            require(op == "SWAP", "reversible scalar basis opcode")
            rows[role], rows[event[2]] = rows[event[2]], rows[role]
    budget(rows)
    return rows


def inverse(operations):
    result = []
    for event in reversed(operations):
        if event[0] == "ADD":
            result.append(["ADD", event[1], event[2], str(-q(event[3]))])
        elif event[0] == "SCALE":
            result.append(["SCALE", event[1], str(1 / q(event[2]))])
        else:
            require(event[0] == "SWAP", "basis inverse opcode")
            result.append(list(event))
    return result


def product_row(row, matrix):
    result = {}
    for coordinate, coefficient in row.items():
        result = add(result, matrix[coordinate], coefficient)
    return result


def emit(operations):
    result = []
    for event in operations:
        op, role = event[:2]
        if op == "SWAP":
            other = event[2]
            expanded = [["ADD", role, other, "1"], ["ADD", other, role, "-1"],
                        ["ADD", role, other, "1"], ["SCALE", other, "-1"]]
        else:
            expanded = [event]
        for entry in expanded:
            entry = list(entry)
            entry[1] = SHADOW.get(entry[1], entry[1])
            if entry[0] == "ADD":
                entry[2] = SHADOW.get(entry[2], entry[2])
                entry[3] = str(q(entry[3]))
            else:
                entry[2] = str(q(entry[2]))
            result.append(entry + [ZERO])
    return result


def rename(event):
    result = list(event)
    result[1] = SHADOW.get(result[1], result[1])
    if result[0] in ("ADD", "COPY"):
        result[2] = SHADOW.get(result[2], result[2])
    return result


def row_difference(actual, expected):
    for coordinate in sorted(actual.keys() | expected.keys()):
        if actual.get(coordinate, 0) != expected.get(coordinate, 0):
            return {"input": coordinate, "actual": str(actual.get(coordinate, 0)),
                    "expected": str(expected.get(coordinate, 0))}
    return None


def run():
    data = inputs()
    source, output = transpose(data["sources/INPUT-WORD.json.gz"]), transpose(data["sources/OUTPUT-WORD.json.gz"])
    basis = data["sources/BASIS.json"]
    require(basis["anchors"] == list(ANCHORS) and basis["entries"] == {"224": 245, "227": 245} and
            basis["shadow"] == {"224": 779, "227": 780}, "two-anchor witness inventory")
    zero, first = source_preparation(source)
    A, old_clears, old_init = execute_zero(zero, source["initial"])
    require(len(old_clears) == 9 and set(old_init) == set(range(770, 779)), "all nine old shadow lifetimes")
    require(not (set(old_init) & set(SHADOW.values())), "disjoint new shadow labels")
    mains = set(source["live"]) | {role + 112 for role in source["live"]}
    helpers = {role for role in range(PUBLIC) if role not in mains and source["initial"][role] == ZERO and
               source["final"][role] == FULL}
    used_B0 = {event[1] for event in basis["B0"]} | {event[2] for event in basis["B0"] if event[0] == "ADD"}
    require(used_B0 <= helpers and set(ANCHORS) <= helpers, "input basis uses independent full helper channels")
    used_C = {event[1] for event in basis["C"]} | {event[2] for event in basis["C"] if event[0] in ("ADD", "SWAP")}
    require(all(first[role][1] == 1091 for role in used_C), "common literal C departure group1091")
    B0 = apply(unit_rows(), basis["B0"])
    B2 = apply(unit_rows(), basis["B2"])
    CA = apply(deepcopy(A), basis["C"])
    directions = {str(anchor): {str(r): str(B0[r][anchor]) for r in range(PUBLIC) if anchor in B0[r]}
                  for anchor in ANCHORS}
    anchor_block = [[B0[r].get(a, 0) for a in ANCHORS] for r in ANCHORS]
    determinant = anchor_block[0][0] * anchor_block[1][1] - anchor_block[0][1] * anchor_block[1][0]
    require(determinant == -4, "dyadic-unit two-anchor block determinant")
    off, unit = {}, {}
    for anchor in ANCHORS:
        paired = product_row(CA[anchor], B0)
        require(all(paired.get(other, 0) == int(anchor == other) for other in ANCHORS), "unit anchor pairing")
        row = dict(paired)
        row.pop(anchor)
        require(set(row) <= helpers - set(ANCHORS), "helper-only off-anchor support")
        off[str(anchor)] = {str(key): str(value) for key, value in row.items()}
        corrected = product_row(paired, B2)
        require(corrected == {anchor: Fraction(1)}, "complete c_r B0 B2 unit row")
        unit[str(anchor)] = encoded(corrected)
    require(off == basis["off_anchor"], "all off-anchor coefficients agree with frozen witness")
    derived_B2 = Counter((int(anchor), int(key), str(-Fraction(value)))
                         for anchor, row in off.items() for key, value in row.items())
    require(all(event[0] == "ADD" for event in basis["B2"]) and
            Counter((event[1], event[2], event[3]) for event in basis["B2"]) == derived_B2,
            "B2 is exactly I minus off-anchor correction")
    responses = {}
    for role in range(PUBLIC):
        row = product_row(CA[role], B0)
        values = {str(anchor): str(row[anchor]) for anchor in ANCHORS if row.get(anchor, 0)}
        if values:
            responses[str(role)] = values
    require(responses == basis["responses"] and set(map(int, responses)) == {119, 224, 227, 232},
            "complete four-row public response table")
    require(all(first[role][1] == (1091 if role in ANCHORS else 245) for role in map(int, responses)),
            "literal primary/nonprimary response destinations")
    inverse_checks = {}
    for name in ("B0", "B2", "C"):
        identity = unit_rows()
        restored = apply(apply(deepcopy(identity), basis[name]), inverse(basis[name]))
        require(restored == identity, "complete public basis inverse: " + name)
        inverse_checks[name] = {"operations": len(basis[name]), "public_rows": PUBLIC,
                                "restored_rows_sha256": rows_digest(restored[:PUBLIC])}
    expected_prefix = [["INIT", role, ZERO] for role in SHADOW.values()]
    expected_prefix += emit(basis["B2"]) + emit(basis["B0"])
    expected_prefix += [rename(event) for event in zero]
    expected_prefix += emit(basis["C"])
    expected_prefix += [["CLEAR", role, ZERO] for role in reversed(tuple(SHADOW.values()))]
    require(len(expected_prefix) == basis["prep_length"] == 4759, "literal4759 prefix size")
    actual_prefix = output["program"][:4759]
    require(canonical(actual_prefix) == canonical(expected_prefix), "every actual candidate dual prefix instruction")
    prepared, clears, initialized = execute_zero(actual_prefix, output["initial"])
    require(len(clears) == 11 and len(initialized) == 11 and set(initialized) == set(range(770, 781)),
            "all eleven actual zero CLEAR rows")
    control_results = {}
    correction_start = 2
    basis_start = correction_start + len(emit(basis["B2"]))
    departure_start = basis_start + len(emit(basis["B0"])) + len(zero)
    for name, index, operation in (("omitted_input_correction", correction_start, "omit"),
                                   ("wrong_input_basis_sign", basis_start, "sign"),
                                   ("omitted_departure_basis", departure_start, "omit")):
        corrupted = deepcopy(actual_prefix)
        original = deepcopy(corrupted[index])
        require(original[0] == "ADD", "scalar coefficient control site")
        if operation == "omit":
            del corrupted[index]
        else:
            corrupted[index][3] = str(-q(corrupted[index][3]))
        _, altered_clears, _ = execute_zero(corrupted, output["initial"], strict=False)
        nonzero = next((record for record in altered_clears if record["row"]), None)
        require(nonzero is not None, "semantic prefix fault must produce a nonzero CLEAR row")
        witness = row_difference(nonzero["row"], {})
        control_results[name] = {"dual_prefix_index": index, "original_event": original,
                                 "clear_role": nonzero["role"], "clear_index": nonzero["index"],
                                 "coefficient_witness": witness}
    altered_inverse = inverse(basis["B0"])[1:]
    bad_identity = apply(apply(unit_rows(), basis["B0"]), altered_inverse)
    witness = next(({"row": r, **difference} for r in range(PUBLIC)
                    if (difference := row_difference(bad_identity[r], {r: Fraction(1)})) is not None), None)
    require(witness is not None, "omitted inverse operation gives coefficient witness")
    control_results["omitted_B0_inverse_operation"] = witness
    removed_C = basis["C"][-1]
    require(removed_C == ["ADD", 204, 227, "1"] and 204 in mains,
            "source-specific final C operation into main row204")
    bad_CA = apply(deepcopy(A), basis["C"][:-1])
    for anchor in ANCHORS:
        corrected = product_row(product_row(bad_CA[anchor], B0), B2)
        require(corrected == {anchor: Fraction(1)}, "main-row fault preserves both complete anchor unit rows")
    forbidden_responses = []
    for role in range(PUBLIC):
        row = product_row(bad_CA[role], B0)
        response = {anchor: row[anchor] for anchor in ANCHORS if row.get(anchor, 0)}
        if response and role not in ANCHORS and first[role][1] != 245:
            forbidden_responses.append((role, response))
    require(len(forbidden_responses) == 1 and forbidden_responses[0][0] == 204,
            "omitted main C update leaks outside permitted response destinations")
    role, response = forbidden_responses[0]
    anchor = min(response)
    control_results["omitted_main204_response_cancellation"] = {
        "omitted_C_operation": removed_C, "complete_anchor_unit_rows_unchanged": True,
        "coefficient_witness": {"response_row": role, "input_anchor": anchor,
                                "actual": str(response[anchor]), "expected": "0",
                                "first_destination": first[role][1],
                                "permitted_nonprimary_destination": 245}}
    return {
        "schema_version": 1,
        "scope": "two-anchor rational ZERO preparation and literal4759 dual-prefix certificate only",
        "public_input_columns": PUBLIC, "anchors": list(ANCHORS), "source_zero_events": len(zero),
        "full_helper_channels": len(helpers),
        "departure_group1091_roles": sorted(role for role, (_, destination) in first.items() if destination == 1091),
        "C_role_classes": {str(role): {"is_main": role in mains, "is_full_helper": role in helpers,
                                      "initial_label": source["initial"][role], "final_label": source["final"][role],
                                      "first_departure_index": first[role][0], "first_destination": first[role][1]}
                           for role in sorted(used_C)},
        "source_zero_opcode_counts": dict(sorted(Counter(event[0] for event in zero).items())),
        "source_A_nonzero_coefficients": sum(map(len, A[:PUBLIC])),
        "source_A_public_rows_sha256": rows_digest(A[:PUBLIC]),
        "source_old_shadow_labels": sorted(old_init), "B0_directions": directions,
        "B0_anchor_block": [[str(value) for value in row] for row in anchor_block],
        "B0_anchor_determinant": str(determinant), "off_anchor": off, "complete_anchor_unit_rows": unit,
        "responses": responses, "first_destinations": {role: first[int(role)][1] for role in responses},
        "basis_inverse_checks": inverse_checks,
        "candidate_dual_prefix_events": len(actual_prefix),
        "candidate_dual_prefix_sha256": sha256((canonical(actual_prefix) + "\n").encode()).hexdigest(),
        "actual_zero_clear_rows": [{"role": record["role"], "dual_prefix_index": record["index"],
                                    "public_support": len(record["row"])} for record in clears],
        "controls": control_results,
        "limits": ["MOVE is identity only in this rational projection; frame labels do not certify native complements or phases.",
                   "Only ZERO preparation and its basis/inverse identities are checked, not the full candidate endpoint or bridge.",
                   "Dual zero CLEAR rows do not grant physical forward erasure permission.",
                   "Native/caller/price, all-width implementation and all five framework assumptions remain open."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh JSON without retained local-result comparison")
    options = parser.parse_args()
    result = run()
    if not options.emit:
        retained = HERE / "LOCAL-RESULT.json"
        require(retained.is_file(), "retained LOCAL-RESULT.json receipt must exist")
        require(canonical(json.loads(retained.read_bytes())) == canonical(result),
                "exact typed retained LOCAL-RESULT.json receipt")
    print(json.dumps(result, sort_keys=True, indent=2))

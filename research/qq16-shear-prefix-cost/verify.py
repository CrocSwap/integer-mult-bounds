#!/usr/bin/env python3
"""Exact QQ16 shear-plus-normalization prefix certificate. Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Ali Romman supplies the retained QQ16 interface and native recipes; Cinna
Davis supplies the logical shear; Charles Bethin identifies its frame gap.
No predecessor executable is imported. See README.md for the cost model.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
SIZE, SCRATCH = 712, 704
ZERO, ONE = (0, 0), (1, 0)
UNITS = (ONE, (0, 1), (-1, 0), (0, -1))
BARRIER = ("For each cover owner, execute the whole body before the next owner. "
           "One ownedC0 is reused.")
MARKER = "PASS_QQ16_SHEAR_PREFIX_COST"


def exact_json(value):
    """Preserve JSON scalar types when comparing proof-relevant artifacts."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def mul(x, y):
    return x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0]


def neg(x):
    return -x[0], -x[1]


def divide(x, y):
    d = y[0]*y[0] + y[1]*y[1]
    need(d != 0, "nonzero Gaussian pivot")
    return Q(x[0]*y[0] + x[1]*y[1], d), Q(x[1]*y[0] - x[0]*y[1], d)


def determinant(matrix):
    """Exact elimination over Q(i), independently of the block formula."""
    rows, result = deepcopy(matrix), ONE
    for col in range(len(rows)):
        pivot = next((i for i in range(col, len(rows)) if rows[i][col] != ZERO), None)
        if pivot is None:
            return ZERO
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            result = neg(result)
        entry = rows[col][col]
        result = mul(result, entry)
        for i in range(col + 1, len(rows)):
            if rows[i][col] != ZERO:
                factor = divide(rows[i][col], entry)
                rows[i] = [add(x, neg(mul(factor, y)))
                           for x, y in zip(rows[i], rows[col], strict=True)]
    return result


def row_add(left, right, coefficient=ONE):
    result = dict(left)
    for column, value in right.items():
        result[column] = add(result.get(column, ZERO), mul(coefficient, value))
        if result[column] == ZERO:
            del result[column]
    return result


def field(token):
    need(isinstance(token, list) and len(token) == 2, "field token")
    name, index = token
    need(type(index) is int and name in ("L", "C"), "field name/index")
    need(0 <= index < (704 if name == "L" else 8), "field range")
    return index + (704 if name == "C" else 0)


def phase(frame, w):
    exponent = sum(c for i, c in enumerate(frame["linear_Z4"]) if (w >> i) & 1)
    exponent += 2 * sum((row & w).bit_count() for i, row in enumerate(frame["quadratic_rows"])
                        if (w >> i) & 1)
    return exponent % 4


def line_phase(item, w):
    return (item["sign"] * ((item["label"] & w).bit_count() % 2)) % 4


def flatten(program):
    for event in program:
        if event[0] in ("private_sweep", "cover_sweep"):
            yield from flatten(event[2])
        else:
            yield event


def load_packet(root):
    for entry in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if entry["usage"] == "input":
            need(hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                 "source pin: " + entry["path"])
    return json.loads(gzip.decompress((root / "research/joint-query/certificate.json.gz").read_bytes()))


def bind(packet):
    need(packet["A_ports"] == A and packet["T_ports"] == T, "selected A/T partition")
    need(packet["field_namespace"]["formal_input_columns"] == SIZE, "all 712 inputs")
    prefix, frames = packet["programs"]["B_1_2"][:8], packet["native_frame_registry"]
    full = prefix[0][3]
    need(frames[full]["line_terms_Z4"] == [[1 << j, 1] for j in range(9)], "completed(0) frame")
    zero = next(k for k, v in frames.items() if v["line_terms_Z4"] == [])
    targets = []
    for a, t, event in zip(A, T, prefix, strict=True):
        need(event[:3] == ["native_line", ["L", t], "inverse_" + str(t)], "B1 prefix order")
        item = packet["native_line_recipes"][event[2]]
        need(item["sign"] == -1 and item["port"] == t, "inverse port recipe")
        need(item["rank"] == item["recipe"]["rank"] == 1, "one child per line")
        need(0 < item["label"] < 512 and item["label"] & 256, "common odd character")
        need(event[3] == full, "initial X_T frame")
        need(all(axis < 512 for axis, _ in frames[event[4]]["line_terms_Z4"]), "no spectator phase")
        for w in range(512):
            direct = sum(c*((axis & w).bit_count() % 2) for axis, c in frames[event[4]]["line_terms_Z4"]) % 4
            need(direct == phase(frames[event[4]], w), "stored frame polynomial")
            need((direct - phase(frames[full], w)) % 4 == line_phase(item, w), "Y_T inverse-line type")
        targets.append({"A_port": a, "T_port": t, "q": item["label"],
                        "X_frame": full, "Y_frame": event[4]})
    need(packet["programs"]["F_0"][0][:3] == ["retained_core", "forward", 0], "F0 core first")
    # Inherited core output contract; this checks only the retained F0 wrappers.
    for event in flatten(packet["programs"]["F_0"][1:]):
        token = event[1][1] if event[0] == "scalar" else event[1]
        need(field(token) not in [112 + p for p in T], "F0 wrappers leave Y_T unchanged")
    return full, zero, targets


def construct(packet, full, zero):
    program = []
    for a, t, normalization in zip(A, T, packet["programs"]["B_1_2"][:8], strict=True):
        yframe = normalization[4]
        body = [
            ["scalar", ["clear", ["C", 0]], full],
            ["scalar", ["add", ["C", 0], ["L", a], 1, 1], full],
            ["scalar", ["add", ["L", t], ["C", 0], 1, 1], full],
            ["native_line", ["C", 0], "inverse_" + str(t), full, yframe],
            ["scalar", ["add", ["L", 112+t], ["C", 0], -1, 1], yframe],
            ["scalar", ["clear", ["C", 0]], zero],
        ]
        program += [["private_sweep", "shear_prefix_" + str(t), body, BARRIER], deepcopy(normalization)]
    return program


def typed_check(packet, program, full, zero):
    """Exact phase types, owned lifetime and every spectator boundary."""
    frames = {key: tuple(phase(value, w) for w in range(512))
              for key, value in packet["native_frame_registry"].items()
              if key in {full, zero} | {e[4] for e in packet["programs"]["B_1_2"][:8]}}
    state = [("opaque", i) for i in range(SIZE)]
    state[:112] = [frames[full]] * 112
    for t, event in zip(T, packet["programs"]["B_1_2"][:8], strict=True):
        state[112+t] = frames[event[4]]
    state[SCRATCH] = frames[zero]
    expected = list(state)
    for t in T:
        expected[t] = state[112+t]
    counts = Counter()

    def consume(event, private):
        if event[0] == "native_line":
            _, token, name, old, new = event
            i = field(token)
            need(i in T or i == SCRATCH and private, "line field/lifetime")
            need(state[i] == frames[old], "line input type")
            item = packet["native_line_recipes"][name]
            state[i] = tuple((p + line_phase(item, w)) % 4 for w, p in enumerate(state[i]))
            need(state[i] == frames[new], "line output type")
            counts["native_lines"] += 1
            return
        need(event[0] == "scalar", "no maps, core or hidden primitive")
        _, gate, name = event
        i = field(gate[1])
        if gate[0] == "clear":
            need(i == SCRATCH and private, "only owned C0 may be cleared")
            state[i] = frames[name]  # Zero admits the declared frame.
            counts["clears"] += 1
        else:
            need(gate[0] == "add" and gate[3] in (-1, 1) and gate[4] == 1, "unit scalar ADD")
            j = field(gate[2])
            need(i != j and i in T + [112+t for t in T] + [SCRATCH], "ADD destination")
            need(j in A + [SCRATCH], "unchanged source or owned C0")
            need((i != SCRATCH and j != SCRATCH) or private, "scratch lifetime")
            need(state[i] == state[j] == frames[name], "equal full native ADD frames")
            counts["adds"] += 1

    for event in program:
        if event[0] != "private_sweep":
            consume(event, False)
            continue
        need(event[3] == BARRIER, "whole row before next owner")
        body = event[2]
        need(body[0][:2] == body[-1][:2] == ["scalar", ["clear", ["C", 0]]], "owned lifetime clears")
        for op in body:
            consume(op, True)
        need(state[SCRATCH] == expected[SCRATCH], "scratch zero/I each row")
        counts["private_sweeps"] += 1
    need(state == expected, "all 712 endpoint types")
    counts["native_wrapper_maps"] = 2 * counts["native_lines"]
    counts["explicit_cover_maps"] = 0
    # Pinned verify_scalar.py: unit complex ADD costs 8 real primitives; CLEAR 2.
    counts["scalar_real_primitive_bound"] = 8*counts["adds"] + 2*counts["clears"]
    return dict(sorted(counts.items()))


def transfer(packet, program, w):
    rows = [{i: ONE} for i in range(SIZE)]
    for event in flatten(program):
        if event[0] == "native_line":
            i = field(event[1])
            value = UNITS[line_phase(packet["native_line_recipes"][event[2]], w)]
            rows[i] = {j: mul(c, value) for j, c in rows[i].items()}
        else:
            need(event[0] == "scalar", "local character replay")
            gate, i = event[1], field(event[1][1])
            rows[i] = {} if gate[0] == "clear" else row_add(rows[i], rows[field(gate[2])], (gate[3], 0))
    return rows


def desired(packet, w):
    rows = [{i: ONE} for i in range(SIZE)]
    for a, t in zip(A, T, strict=True):
        q = packet["native_line_recipes"]["inverse_" + str(t)]["label"]
        c = (0, -1) if (q & w).bit_count() % 2 else ONE
        rows[t] = {t: c, a: c}
        rows[112+t] = {112+t: ONE, a: neg(c)}
    rows[SCRATCH] = {}
    return rows


def minor_difference(first, second):
    columns = [i for pair in zip(A, T, strict=True) for i in pair]
    rows = [i for t in T for i in (t, 112+t)]
    return [[add(first[i].get(j, ZERO), neg(second[i].get(j, ZERO))) for j in columns] for i in rows]


def mono(recipe, address):
    """Stored monomial action on a computational basis ket."""
    exponent, output = recipe["phase"], recipe["offset"]
    for j in range(9):
        if address & (1 << j):
            exponent += recipe["linear_Z4"][j] + 2*(recipe["quadratic_rows"][j] & address).bit_count()
    for j, row in enumerate(recipe["matrix_rows"]):
        output ^= ((row & address).bit_count() % 2) << j
    return output, UNITS[exponent % 4]


def recipe_column(recipe, address):
    """Twice a physical column: right monomial, C_e0, left monomial."""
    middle, right = mono(recipe["right"], address)
    out = {}
    for target, coefficient in ((middle, (1, 1)), (middle ^ 1, (1, -1))):
        destination, left = mono(recipe["left"], target)
        out[destination] = add(out.get(destination, ZERO), mul(mul(right, coefficient), left))
    return {i: c for i, c in out.items() if c != ZERO}


def physical_check(packet):
    count = 0
    for t in T:
        item = packet["native_line_recipes"]["inverse_" + str(t)]
        for z in range(512):
            need(recipe_column(item["recipe"], z) == {z: (1, -1), z ^ item["label"]: (1, 1)},
                 "actual recipe equals inverse line on every basis input")
            count += 1
    return count


def physical_prefix_check(packet, program):
    """Separate address-convolution engine; no character phases are used.

    Check 25 input fields at address zero. Translation equivariance proves
    the 512 shifts of each check; all unaffected fields are literal identity.
    """
    affected = A + T + [112+t for t in T] + [SCRATCH]
    for column in affected:
        fields = {i: ({0: ONE} if i == column else {}) for i in affected}
        for op in flatten(program):
            if op[0] == "native_line":
                i, item = field(op[1]), packet["native_line_recipes"][op[2]]
                row = {}
                for z, value in fields[i].items():
                    row[z] = add(row.get(z, ZERO), mul(value, (Q(1, 2), Q(item["sign"], 2))))
                    other = z ^ item["label"]
                    row[other] = add(row.get(other, ZERO), mul(value, (Q(1, 2), Q(-item["sign"], 2))))
                fields[i] = {z: v for z, v in row.items() if v != ZERO}
            else:
                gate, i = op[1], field(op[1][1])
                fields[i] = {} if gate[0] == "clear" else row_add(fields[i], fields[field(gate[2])], (gate[3], 0))
        expected = {i: ({0: ONE} if i == column else {}) for i in affected}
        expected[SCRATCH] = {}
        for a, t in zip(A, T, strict=True):
            q = packet["native_line_recipes"]["inverse_" + str(t)]["label"]
            inverse = {0: (Q(1, 2), Q(-1, 2)), q: (Q(1, 2), Q(1, 2))}
            if column in (a, t):
                expected[t] = inverse
            if column == a:
                expected[112+t] = {z: neg(c) for z, c in inverse.items()}
        need(fields == expected, "independent physical prefix identity")
    return len(affected) * 512


def failure_controls(packet, program, full, zero):
    controls = []

    def rejected(name, action):
        try:
            action()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("control not rejected: " + name)

    def semantic(candidate, w=256):
        need(transfer(packet, candidate, w) == desired(packet, w), "complete dirty endpoint")

    bad = deepcopy(program)
    del bad[0][2][3]
    rejected("omitted_scratch_inverse_types", lambda: typed_check(packet, bad, full, zero))
    rejected("omitted_scratch_inverse_semantics", lambda: semantic(bad))
    semantic(bad, 0)
    controls.append("constant_payload_blind_spot_reproduced")
    bad = deepcopy(program)
    bad[0][2][3][2] = next(k for k, v in packet["native_line_recipes"].items()
                          if v["port"] == T[0] and v["sign"] == 1)
    rejected("wrong_native_sign", lambda: semantic(bad))
    bad = deepcopy(program)
    bad[0][2][1][1][2] = ["L", A[1]]
    typed_check(packet, bad, full, zero)  # Preserves every frame type.
    rejected("equal_frame_wrong_source", lambda: semantic(bad))
    bad = deepcopy(program)
    del bad[0][2][0]
    rejected("uncleared_arbitrary_scratch", lambda: semantic(bad))
    bad = deepcopy(program)
    del bad[0][2][-1]
    # The next clear could hide the defect; test the first completed row itself.
    rejected("scratch_not_zero_at_row_boundary", lambda: typed_check(packet, bad, full, zero))
    bad = deepcopy(program)
    del bad[1]
    rejected("missing_inherited_X_normalization", lambda: semantic(bad))
    bad = deepcopy(program)
    bad[0][2][4][1][3] = 1
    rejected("wrong_Y_subtraction_sign", lambda: semantic(bad))
    bad = deepcopy(program)
    bad[0][3] = "interleave owners before clearing scratch"
    rejected("private_lifetime_barrier", lambda: typed_check(packet, bad, full, zero))
    bad = deepcopy(packet)
    bad["native_line_recipes"]["inverse_21"]["recipe"]["left"]["phase"] += 1
    rejected("native_wrapper_global_phase", lambda: physical_check(bad))
    bad = deepcopy(packet)
    bad["programs"]["B_1_2"][0][1] = ["L", T[1]]
    rejected("prefix_boundary_binding", lambda: bind(bad))
    minor = minor_difference(desired(packet, 256), desired(packet, 0))
    minor[1] = [ZERO] * 16
    rejected("missing_Y_obligation_destroys_minor", lambda: need(determinant(minor) != ZERO, "minor"))
    rejected("constant_character_cannot_certify_bound", lambda: need(
        determinant(minor_difference(desired(packet, 0), desired(packet, 0))) != ZERO, "minor"))
    return controls


def calculate(root, program=None):
    packet = load_packet(root)
    full, zero, targets = bind(packet)
    expected_program = construct(packet, full, zero)
    if program is None:
        program = expected_program
    need(exact_json(program) == exact_json(expected_program), "complete frozen prefix instructions")
    invoice = typed_check(packet, program, full, zero)
    need((invoice["native_lines"], invoice["adds"], invoice["clears"]) == (16, 24, 16), "attaining invoice")
    histogram = Counter()
    for w in range(512):
        need(transfer(packet, program, w) == desired(packet, w), "all 712 rows at character " + str(w))
        histogram[2*sum((e["q"] & w).bit_count() % 2 for e in targets)] += 1
    low = minor_difference(desired(packet, 256), desired(packet, 0))
    need(determinant(low) == (256, 0), "rank-16 exact Gaussian determinant")
    need(minor_difference(transfer(packet, program, 256), transfer(packet, program, 0)) == low,
         "minor agrees with literal program")
    recipe_columns, physical_columns = physical_check(packet), physical_prefix_check(packet, program)
    controls = failure_controls(packet, program, full, zero)
    receipt = {
        "status": MARKER, "native_line_minimum": 16, "inherited_prefix_lines": 8, "additional_lines": 8,
        "lower_bound": {"characters": [0, 256], "minor_rows": [i for t in T for i in (t, 112+t)],
                        "minor_columns": [i for pair in zip(A, T, strict=True) for i in pair],
                        "determinant_gaussian": [256, 0], "rank": 16,
                        "difference_rank_histogram": {str(k): v for k, v in sorted(histogram.items())}},
        "targets": targets, "invoice": invoice,
        "coverage": {"characters": 512, "input_fields": SIZE, "output_fields": SIZE,
                     "field_character_rows": SIZE*512, "native_recipe_basis_columns": recipe_columns,
                     "affected_physical_basis_columns_by_translation": physical_columns,
                     "participating_fields": 25, "untouched_fields": SIZE-17,
                     "identity_fields_outside_footprint": SIZE-25,
                     "borrowed_helpers_restored": 480, "owned_scratch_fields": 1},
        "controls": controls,
        "scope": "Fixed shear-plus-initial-normalization endpoint; atomic single-field native lines; no cover maps or later B1 fusion. No supplier, full controller, precision admission or kappa claim."
    }
    return program, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-results", action="store_true")
    args = parser.parse_args()
    if args.write_results:
        program, receipt = calculate(args.root)
        for name, data in (("PREFIX.json", program), ("RESULT.json", receipt)):
            (HERE / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    else:
        _, receipt = calculate(args.root, json.loads((HERE / "PREFIX.json").read_text()))
        need(exact_json(json.loads((HERE / "RESULT.json").read_text())) == exact_json(receipt),
             "complete frozen receipt")
    print(MARKER + " minimum_lines=16 inherited=8 additional=8 characters=512 inputs=712 controls="
          + str(len(receipt["controls"])))


if __name__ == "__main__":
    main()

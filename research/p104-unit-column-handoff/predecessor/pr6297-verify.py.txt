#!/usr/bin/env python3
"""Replay one non-unit dyadic handoff on the pinned PR5580 word.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor constructor, compiler and local replay are imported from their
pinned paths and are not modified on disk.
"""
import gzip
import hashlib
import importlib.util
import json
import sys
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CUT = 13762
FRAME = 1053
SOURCE = 3
TARGET = 127
PIVOT = 596
V = {592: Q(5, 16), 593: Q(5, 16), 594: Q(5, 8), 596: Q(3, 8)}
U = {592: Q(-1), 593: Q(1), 594: Q(1), 596: Q(1)}
BASE_EVENTS = 25140
BASE_PUBLIC = 735
BASE_PAID = {1: 2211, 2: 459, 5: 164, 4: 94, 3: 494, 7: 14, 6: 18}
BASE_HELPERS = {9: 424, 4: 83, 5: 5, 8: 15}
BASE_SCALAR = 217428
NEW_EVENTS = 25280
NEW_PUBLIC = 736
NEW_HELPERS = {9: 423, 4: 84, 5: 6, 8: 15}
NEW_SCALAR = 218564
SOURCE_OPS = 36
CUT_OPS = 34


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def pairs(row):
    return [[register, str(value)] for register, value in sorted(row.items())]


def unit(value):
    numerator, denominator = abs(value.numerator), value.denominator
    return numerator > 0 and numerator & (numerator - 1) == 0 and denominator & (denominator - 1) == 0


def expect(action, message):
    try:
        action()
    except ValueError as exc:
        need(str(exc) == message, "expected " + message + "; got " + str(exc))
    else:
        raise ValueError("accepted a defect: " + message)


def scalar_cost(events):
    """Match local.replay's ADD and SCALE allowance, excluding opcode frames."""
    total = 0
    for event in events:
        value = Q(event[-2])
        numerator, denominator = abs(value.numerator), value.denominator
        if event[0] == "SCALE":
            total += 2 * (abs(numerator.bit_length() - denominator.bit_length()) + int(value < 0))
        else:
            need(event[0] == "ADD", "Basis operation")
            total += 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1)
    return total


def compile_pair(compiler, left, right, pivot):
    keys = sorted(set(left) | set(right) | {pivot})
    ops = compiler(
        [Q(left.get(key, 0)) for key in keys],
        [Q(right.get(key, 0)) for key in keys],
        keys.index(pivot),
    )
    return keys, ops


def matrix_identity(compiler, left, right, pivot):
    keys, ops = compile_pair(compiler, left, right, pivot)
    width = len(keys)
    rows = [[Q(i == j) for j in range(width)] for i in range(width)]
    for op, row, source, coefficient in ops:
        need(dyadic_ok(coefficient), "Compiled coefficient is dyadic")
        need(abs(coefficient) + 1 < 2**16, "Compiled coefficient inside the growth bound")
        if op == "ADD":
            need(row != source, "Distinct ADD operands")
            rows[row] = [x + coefficient * y for x, y in zip(rows[row], rows[source])]
        else:
            need(op == "SCALE" and unit(coefficient), "Compiled SCALE is a dyadic unit")
            rows[row] = [coefficient * x for x in rows[row]]
    image = [sum(Q(left.get(keys[i], 0)) * rows[i][j] for i in range(width)) for j in range(width)]
    slot = keys.index(pivot)
    need(image == [Q(j == slot) for j in range(width)], "Compiled row identity")
    need([rows[i][slot] for i in range(width)] == [Q(right.get(key, 0)) for key in keys],
         "Compiled column identity")
    return keys, ops


def dyadic_ok(value):
    return value.denominator & (value.denominator - 1) == 0


def program_rows(keys, ops, frame):
    rows = []
    for op, row, source, coefficient in ops:
        if op == "ADD":
            rows.append(["ADD", keys[row], keys[source], str(coefficient), frame])
        else:
            rows.append(["SCALE", keys[row], str(coefficient), frame])
    return rows


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(sources["base_commit"] == "2485805a6d47f36ea83ddde6327d453ac82d44dc", "Pinned base")
    for row in sources["files"]:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "Pinned source bytes: " + row["path"])

    coupled = ROOT / "research/p104-coupled-helper-bases"
    local = load(coupled / "local.py", "local")
    construct = load(coupled / "construct.py", "p104_coupled_construct")
    compiler = load(ROOT / "research/dyadic-helper-basis-completion/basis.py", "dyadic_helper_basis")
    need(construct.L is local, "Constructor and local replay share one module")
    word = json.loads(gzip.decompress((coupled / "inputs/pr5580-WORD.json.gz").read_bytes()))
    need(word["schema"] == "p104-productive-source/1", "PR5580 word schema")
    need(word["public"] == BASE_PUBLIC and len(word["program"]) == BASE_EVENTS, "PR5580 dimensions")

    rows, frames = construct.prefix(word, CUT)
    columns = construct.suffix_columns(word, CUT)
    need(all(frame is None for frame in frames[word["public"]:]), "No owned field at the cut")
    need(rows[592] == {592: Q(1), 595: Q(-1), 597: Q(1)}, "Prefix row 592")
    need(rows[593] == {593: Q(1), 595: Q(-1), 597: Q(-1)}, "Prefix row 593")
    need(rows[594] == {594: Q(1), 595: Q(1)}, "Prefix row 594")
    need(rows[596] == {596: Q(1)}, "Prefix row 596")
    need(columns[596] == {596: Q(1), 204: Q(1, 2), 199: Q(-1, 2)}, "Suffix column 596")
    need(columns[593] == {593: Q(1), 188: Q(-1, 2), 204: Q(-1, 2)}, "Suffix column 593")
    need(columns[594] == {594: Q(1), 188: Q(-1, 2), 193: Q(-1, 2)}, "Suffix column 594")
    need(columns[592] == {592: Q(1), 199: Q(-1, 2), 193: Q(-1, 2)}, "Suffix column 592")
    for register in V:
        need(frames[register] == FRAME, "Cut chart")

    source_functional, output_direction = {}, {}
    for register, value in V.items():
        local.add(source_functional, rows[register], value)
    for register, value in U.items():
        local.add(output_direction, columns[register], value)
    need(source_functional == V, "Prefix cancellation leaves the cut row")
    need(595 not in source_functional and 597 not in source_functional, "Cancelled prefix supports")
    need(output_direction == {188: Q(-1), 592: Q(-1), 593: Q(1), 594: Q(1), 596: Q(1)},
         "Suffix image")
    need(193 not in output_direction and 199 not in output_direction and 204 not in output_direction,
         "Cancelled suffix supports")
    need(sum(source_functional.get(register, 0) * value for register, value in output_direction.items()) == 1,
         "Dual pairing")
    need(sum(V.get(register, 0) * value for register, value in U.items()) == 1, "Cut pairing")
    need(not any(unit(value) for value in list(V.values()) + list(source_functional.values())),
         "Rejected rows have no dyadic unit coordinate")

    main = construct.main_fields(word)
    group = {register for register in range(word["public"])
             if register not in main and (word["initial"][register], word["final"][register]) == (SOURCE, TARGET)}
    need(len(group) == 424 and PIVOT in group and set(source_functional) <= group and set(output_direction) <= group,
         "Helper group supports the handoff")
    need(not (set(output_direction) | {min(main)}) <= group, "A main-field enlargement leaves the group")
    need(local.span(word["frames"][SOURCE]) < local.span(word["frames"][FRAME]) < local.span(word["frames"][TARGET]),
         "Nested handoff frames")
    need(len(word["frames"][FRAME]) - len(word["frames"][SOURCE]) == 5, "Source-to-cut rank")
    need(len(word["frames"][TARGET]) - len(word["frames"][FRAME]) == 4, "Cut-to-target rank")
    need(len(word["frames"][TARGET]) - len(word["frames"][SOURCE]) == 9, "Unsplit helper rank")

    expect(lambda: construct.basis(source_functional, output_direction, PIVOT, SOURCE), "Dyadic basis pivot")
    expect(lambda: construct.basis(V, U, PIVOT, FRAME), "Dyadic basis pivot")
    accepted = construct.basis({596: Q(1), 592: Q(5, 16)}, {596: Q(1)}, PIVOT, SOURCE)
    need(accepted == [["ADD", 596, 592, "-5/16", SOURCE]], "A unit coordinate still passes the old test")

    source_keys, source_ops = matrix_identity(compiler.compile_basis, source_functional, output_direction, PIVOT)
    cut_keys, cut_ops = matrix_identity(compiler.compile_basis, V, U, PIVOT)
    need(len(source_ops) == SOURCE_OPS and len(cut_ops) == CUT_OPS, "Euclidean operation counts")
    expect(lambda: compiler.compile_basis([Q(1, 3), Q(2, 3)], [Q(1), Q(1)], 0), "Dyadic input coefficients")
    expect(lambda: compiler.compile_basis([Q(5, 16), Q(1)], [Q(-1), Q(1)], 0), "Dual pairing equals one")

    step = {
        "kind": "coupled_handoff",
        "cut": CUT,
        "frame": FRAME,
        "group": [SOURCE, TARGET],
        "pivot": PIVOT,
        "v": pairs(V),
        "u": pairs(U),
        "source_functional": pairs(source_functional),
        "output_direction": pairs(output_direction),
    }
    expect(lambda: construct.handoff(word, step), "Dyadic basis pivot")
    scaled = deepcopy(step)
    scaled["v"] = pairs({register: 3 * value for register, value in V.items()})
    expect(lambda: construct.handoff(word, scaled), "Nonzero dyadic handoff pairing")
    wrong_pivot = deepcopy(step)
    wrong_pivot["pivot"] = 0
    expect(lambda: construct.handoff(word, wrong_pivot), "Public handoff fields share the cut chart")
    wrong_group = deepcopy(step)
    wrong_group["group"] = [SOURCE, TARGET - 1]
    expect(lambda: construct.handoff(word, wrong_group), "Public handoff fields share the cut chart")
    leaked = deepcopy(step)
    leaked["output_direction"] = pairs(output_direction) + [[min(main), "1"]]
    expect(lambda: construct.handoff(word, leaked), "Exact prefix and suffix handoff witnesses")

    def admitted_basis(left, right, pivot, frame):
        keys, ops = compile_pair(compiler.compile_basis, left, right, pivot)
        return program_rows(keys, ops, frame)

    construct.basis = admitted_basis
    produced = construct.handoff(word, step)
    need(len(word["program"]) == BASE_EVENTS and word["public"] == BASE_PUBLIC, "Input word unchanged")
    need(produced["public"] == NEW_PUBLIC and len(produced["program"]) == NEW_EVENTS, "Handoff dimensions")
    need(produced["final"][PIVOT] == FRAME and produced["initial"][-1] == FRAME and produced["final"][-1] == TARGET,
         "Pivot lifetime and new helper field")
    output_ops = construct.inverse(program_rows(source_keys, source_ops, SOURCE))
    for event in output_ops:
        event[-1] = TARGET
    inserted = (
        program_rows(source_keys, source_ops, SOURCE)
        + construct.inverse(program_rows(cut_keys, cut_ops, FRAME))
        + program_rows(cut_keys, cut_ops, FRAME)
        + output_ops
    )
    need(len(inserted) == NEW_EVENTS - BASE_EVENTS == 140, "Inserted event count")
    need({event[-1] for event in inserted} == {SOURCE, FRAME, TARGET}, "Inserted charts")

    before = local.replay(word)
    after = local.replay(produced)
    need(before["paid"] == BASE_PAID and after["paid"] == BASE_PAID, "Paid histogram")
    need(before["helpers"] == BASE_HELPERS and after["helpers"] == NEW_HELPERS, "Helper histogram")
    need(before["real_scalar_allowance"] == BASE_SCALAR and after["real_scalar_allowance"] == NEW_SCALAR,
         "Scalar allowance")
    need(scalar_cost(inserted) == NEW_SCALAR - BASE_SCALAR == 1136, "Inserted scalar allowance")
    need(after["public_inputs"] == NEW_PUBLIC and after["owned_lifetimes"] == 8 and after["peak_owned_fields"] == 1,
         "Owned lifetime")

    grown = deepcopy(produced)
    add = next(event for event in grown["program"] if event[0] == "ADD")
    add[-2] = str(2**16)
    expect(lambda: local.replay(grown), "Fixed scalar growth bound")
    scaled_op = deepcopy(produced)
    scale = next(event for event in scaled_op["program"] if event[0] == "SCALE")
    scale[-2] = "3"
    expect(lambda: local.replay(scaled_op), "Dyadic unit SCALE")
    print("PASS_DYADIC_REJECTED_DUAL_TARGET")


if __name__ == "__main__":
    main()

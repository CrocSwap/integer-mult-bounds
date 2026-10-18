#!/usr/bin/env python3
"""Exact QQ16 cut audit; standard library only, no predecessor execution."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
PACKET = "research/joint-query/certificate.json.gz"
PACKET_SHA = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
AXES = tuple(1 << i for i in range(73))
UNIT = (AXES, 0)
OMEGA = (1 << 73) - 1
ZERO, ONE = (Q(0), Q(0)), (Q(1), Q(0))
MARKER = "PASS_QQ16_EVEN_MAP_NATIVE_CUT"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load_json(raw):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out

    def no_float(value):
        raise ValueError("JSON floats/nonfinite values are not permitted")

    return json.loads(raw, object_pairs_hook=unique, parse_float=no_float, parse_constant=no_float)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def div(a, b):
    d = b[0]*b[0] + b[1]*b[1]
    need(d != 0, "nonzero Gaussian divisor")
    c = mul(a, (b[0], -b[1]))
    return c[0]/d, c[1]/d


def bits(n):
    while n:
        b = n & -n
        yield b.bit_length() - 1
        n ^= b


def act(columns, vector):
    result = 0
    for i in bits(vector):
        result ^= columns[i]
    return result


@lru_cache(None)
def compose(left, right):
    g, a = left
    h, b = right
    return tuple(act(g, c) for c in h), a ^ act(g, b)


def row_add(row, other, coefficient=ONE):
    out = dict(row)
    for key, value in other.items():
        out[key] = add(out.get(key, ZERO), mul(coefficient, value))
        if out[key] == ZERO:
            del out[key]
    return out


def operate(row, operator, coefficient=ONE):
    out = {}
    for (column, old), value in row.items():
        key = column, compose(operator, old)
        out[key] = add(out.get(key, ZERO), mul(coefficient, value))
        if out[key] == ZERO:
            del out[key]
    return out


def identity():
    return [{(i, UNIT): ONE} for i in range(712)]


def register(token):
    need(type(token) is list and len(token) == 2, "field token")
    name, at = token
    need(type(at) is int and name in ("L", "C"), "field type")
    need(0 <= at < (704 if name == "L" else 8), "field range")
    return at + (704 if name == "C" else 0)


def mapping(packet, label):
    record = packet["map_registry"][label]
    return tuple(record["owner_right_matrix_columns"]), record["payload_translation_at_identity_owner"]


def line(row, item):
    """One payload layer only; this two-term formula is not a tensor power."""
    sign, q = item["sign"], item["label"]
    return row_add(operate(row, UNIT, (Q(1, 2), Q(sign, 2))),
                   operate(row, (AXES, q), (Q(1, 2), Q(-sign, 2))))


def flatten(program):
    for event in program:
        if event[0] == "private_sweep":
            yield from event[2]
        else:
            yield event


def replay(packet, program, rows=None):
    """Full ordered affine-operator replay at payload tensor length lambda=1."""
    rows = identity() if rows is None else [dict(r) for r in rows]
    for e in flatten(program):
        at = register(e[1][1] if e[0] == "scalar" else e[1])
        if e[0] == "cover_map":
            rows[at] = operate(rows[at], mapping(packet, e[2]))
        elif e[0] == "native_line":
            rows[at] = line(rows[at], packet["native_line_recipes"][e[2]])
        else:
            need(e[0] == "scalar", "known cut event")
            gate = e[1]
            if gate[0] == "clear":
                rows[at] = {}
            else:
                need(gate[0] == "add", "cut has only ADD/CLEAR")
                rows[at] = row_add(rows[at], rows[register(gate[2])], (Q(gate[3], gate[4]), Q(0)))
    return rows


def physical_shear(packet):
    rows = identity()
    for a, t in zip(A, T, strict=True):
        rows[t] = row_add(rows[t], rows[a])
        rows[112+t] = row_add(rows[112+t], line(rows[a], packet["native_line_recipes"]["inverse_" + str(t)]), neg(ONE))
    return rows


def free_replay(program, sheared=False):
    """Rational word polynomials in arbitrary noncommuting native/map operators.

    No C_q expansion, tensor specialization, or inverse relation is used.
    """
    rows = [{(i, ()): Q(1)} for i in range(712)]

    def merge(row, other, c=Q(1)):
        out = dict(row)
        for key, value in other.items():
            out[key] = out.get(key, Q(0)) + c*value
            if not out[key]:
                del out[key]
        return out

    def apply(row, tag):
        return {(col, (tag,) + word): value for (col, word), value in row.items()}

    if sheared:
        for a, t in zip(A, T, strict=True):
            rows[t] = merge(rows[t], rows[a])
            rows[112+t] = merge(rows[112+t], apply(rows[a], ("native_line", "inverse_" + str(t))), Q(-1))
    for e in flatten(program):
        at = register(e[1][1] if e[0] == "scalar" else e[1])
        if e[0] in ("cover_map", "native_line"):
            rows[at] = apply(rows[at], (e[0], e[2]))
        else:
            need(e[0] == "scalar", "free-operator primitive")
            gate = e[1]
            if gate[0] == "clear":
                rows[at] = {}
            else:
                need(gate[0] == "add", "free-operator ADD/CLEAR")
                rows[at] = merge(rows[at], rows[register(gate[2])], Q(gate[3], gate[4]))
    return rows


def construct(packet):
    original = packet["programs"]["B_1_2"]
    out = []
    for a, t, normalization in zip(A, T, original[:8], strict=True):
        full, yframe = normalization[3:]
        body = [["scalar", ["clear", ["C", 0]], full],
                ["scalar", ["add", ["C", 0], ["L", a], 1, 1], full],
                ["scalar", ["add", ["L", t], ["C", 0], 1, 1], full],
                ["native_line", ["C", 0], "inverse_" + str(t), full, yframe],
                ["scalar", ["add", ["L", 112+t], ["C", 0], -1, 1], yframe],
                ["scalar", ["clear", ["C", 0]], "f0"]]
        out += [["private_sweep", "shear_" + str(t), body, original[12][3]], deepcopy(normalization)]
    return out + deepcopy(original[8:80])


def terms(entries):
    out = Counter()
    for axis, c in entries:
        out[axis] = (out[axis] + c) % 4
    return tuple((a, c) for a, c in sorted(out.items()) if a and c)


@lru_cache(None)
def polynomial(entries):
    linear, cross = [0]*73, [0]*73
    for axis, c in entries:
        for i in bits(axis):
            linear[i] = (linear[i] + c) % 4
            if c % 2:
                for j in bits(axis):
                    if j > i:
                        cross[i] ^= 1 << j
    return tuple(linear), tuple(cross)


def typed(packet, program):
    registry = packet["native_frame_registry"]
    frames = {k: terms(v["line_terms_Z4"]) for k, v in registry.items()}
    for k, frame in frames.items():
        need(polynomial(frame) == (tuple(registry[k]["linear_Z4"]), tuple(registry[k]["quadratic_rows"])), "frame polynomial")
    state = [("opaque", i) for i in range(712)]
    full = frames["f1"]
    for p in A + T:
        state[p] = full
        q = packet["native_line_recipes"]["inverse_" + str(p)]["label"]
        state[112+p] = terms(full + ((q, -1),))
    initial = list(state)
    count = Counter()

    def consume(e, private=False):
        kind = e[0]
        at = register(e[1][1] if kind == "scalar" else e[1])
        need(at < 224 or at == 704 and private, "data/owned C0 destination")
        if kind == "cover_map":
            need(not private and at in T, "source path outside private sweep")
            need(polynomial(state[at]) == polynomial(frames[e[3]]), "map input frame")
            g, shift = mapping(packet, e[2])
            state[at] = terms(tuple((act(g, axis), c) for axis, c in state[at]) + tuple((1 << j, 2) for j in bits(shift)))
            need(polynomial(state[at]) == polynomial(frames[e[4]]), "map output frame")
            count["explicit_cover_maps"] += 1
        elif kind == "native_line":
            need(at in T or at == 704 and private, "native field/lifetime")
            need(polynomial(state[at]) == polynomial(frames[e[3]]), "native input frame")
            item = packet["native_line_recipes"][e[2]]
            state[at] = terms(state[at] + ((item["label"], item["sign"]),))
            need(polynomial(state[at]) == polynomial(frames[e[4]]), "native output frame")
            count["native_lines"] += 1
        else:
            need(kind == "scalar", "typed primitive")
            gate = e[1]
            if gate[0] == "clear":
                need(at == 704 and private, "only owned C0 is cleared")
                state[at] = frames[e[2]]
                count["clears"] += 1
            else:
                need(gate[0] == "add" and gate[4] in (1, 2), "dyadic cut ADD")
                source = register(gate[2])
                need(source < 224 or source == 704 and private, "data/owned source")
                need(source != at and polynomial(state[source]) == polynomial(state[at]) == polynomial(frames[e[2]]), "equal ADD frames")
                count["adds"] += 1

    for e in program:
        if e[0] != "private_sweep":
            consume(e)
            continue
        need(e[3] == packet["programs"]["B_1_2"][12][3], "whole-owner private barrier")
        need(e[2][0][:2] == e[2][-1][:2] == ["scalar", ["clear", ["C", 0]]], "private initial/final clears")
        for child in e[2]:
            consume(child, True)
        need(state[704] == (), "C0 returns zero/I per private row")
        count["private_sweeps"] += 1
    expected = list(initial)
    for t in T:
        expected[t] = initial[112+t]
    expected[704] = ()
    need(all((polynomial(x) == polynomial(y) if isinstance(x, tuple) and (not x or isinstance(x[0], tuple)) else x == y) for x, y in zip(state, expected, strict=True)), "all 712 final frame boundaries")
    count["native_wrapper_maps"] = 2*count["native_lines"]
    # A half ADD has bound10, a unit ADD8, CLEAR2 (complex real-component ledger).
    count["scalar_real_primitive_bound"] = sum(2 if e[1][0] == "clear" else (8 if e[1][4] == 1 else 10) for e in flatten(program) if e[0] == "scalar")
    return dict(sorted(count.items()))


def invariants(packet):
    original = packet["programs"]["B_1_2"]
    need(packet["A_ports"] == A and packet["T_ports"] == T and packet["field_namespace"]["formal_input_columns"] == 712, "selected namespace")
    need(len(original) == 557 and original[80][:3] == ["cover_map", ["L", 112], "m89"], "exact later cut")
    maps, labels = [], []
    for e in flatten(original[:80]):
        if e[0] == "cover_map":
            need(packet["map_registry"][e[2]]["action"] == "out(d,z_1,...,z_lambda)=in(d*g,z_1 XOR d*delta,...,z_lambda XOR d*delta)", "actual full owner/payload action")
            g, shift = mapping(packet, e[2])
            need(len(g) == 73 and all(type(x) is int and 0 < x < 1 << 73 for x in g), "map dimensions")
            need(all((g[i] & g[j]).bit_count() % 2 == (i == j) for i in range(73) for j in range(73)), "orthogonal owner matrix")
            need(act(g, OMEGA) == OMEGA and all(x.bit_count() % 2 == 1 for x in g), "characteristic vector fixed in both directions")
            need(type(shift) is int and 0 <= shift < 1 << 73 and shift.bit_count() % 2 == 0, "even payload translation")
            maps.append(e[2])
        elif e[0] == "native_line":
            item = packet["native_line_recipes"][e[2]]
            need(item["rank"] == item["recipe"]["rank"] == 1 and item["sign"] in (-1, 1), "atomic signed rank-one line")
            need(item["label"].bit_count() % 2 == 1, "odd native label")
            labels.append(item["label"])
    need(len(maps) == 64 and len(labels) == 16, "complete cut inventory")
    return {"maps": 64, "odd_lines": 16, "native_labels": labels, "characters": [0, OMEGA]}


def physical_check(packet):
    """Bind each used signed native line to all 512 actual recipe columns."""
    names = sorted({e[2] for e in flatten(packet["programs"]["B_1_2"][:80]) if e[0] == "native_line"})

    def mono(recipe, address):
        need(len(recipe["matrix_rows"]) == len(recipe["linear_Z4"]) == len(recipe["quadratic_rows"]) == 9, "nine-axis monomial dimensions")
        exponent = recipe["phase"]
        for j in bits(address):
            exponent += recipe["linear_Z4"][j] + 2*(recipe["quadratic_rows"][j] & address).bit_count()
        dest = recipe["offset"]
        for j, row in enumerate(recipe["matrix_rows"]):
            dest ^= ((row & address).bit_count() % 2) << j
        need(0 <= dest < 512, "native monomial address")
        return dest, ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent % 4]

    for name in names:
        item = packet["native_line_recipes"][name]
        recipe, q, sign = item["recipe"], item["label"], item["sign"]
        need(type(q) is int and 0 < q < 512 and type(sign) is int and sign in (-1, 1), "literal native label/sign")
        for address in range(512):
            mid, right = mono(recipe["right"], address)
            out = {}
            for at, coefficient in ((mid, (1, 1)), (mid ^ 1, (1, -1))):
                dest, left = mono(recipe["left"], at)
                out[dest] = add(out.get(dest, ZERO), mul(mul(right, coefficient), left))
            out = {k: v for k, v in out.items() if v != ZERO}
            need(out == {address: (1, sign), address ^ q: (1, -sign)}, "actual native recipe Gaussian column")
    return len(names)*512


def evaluate(rows, odd):
    out = []
    for row in rows:
        r = {}
        for (col, (g, shift)), value in row.items():
            need(act(g, OMEGA) == OMEGA, "evaluation preserves covariant character")
            sign = -1 if odd and shift.bit_count() % 2 else 1
            r[col] = add(r.get(col, ZERO), mul((Q(sign), Q(0)), value))
            if r[col] == ZERO:
                del r[col]
        out.append(r)
    return out


def determinant(matrix):
    matrix = [list(row) for row in matrix]
    d = ONE
    for k in range(len(matrix)):
        pivots = [i for i in range(k, len(matrix)) if matrix[i][k] != ZERO]
        if not pivots:
            return ZERO
        p = pivots[0]
        if p != k:
            matrix[k], matrix[p] = matrix[p], matrix[k]
            d = neg(d)
        pivot = matrix[k][k]
        d = mul(d, pivot)
        for i in range(k+1, len(matrix)):
            c = div(matrix[i][k], pivot)
            for j in range(k+1, len(matrix)):
                matrix[i][j] = add(matrix[i][j], neg(mul(c, matrix[k][j])))
            matrix[i][k] = ZERO
    return d


def load_packet():
    source = load_json((HERE / "SOURCES.json").read_text())
    need(source["base_commit"] == BASE, "source base")
    paths = [r["path"] for r in source["files"]]
    need(len(paths) == len(set(paths)) and PACKET in paths, "unique source inventory")
    for row in source["files"]:
        need(row["usage"] in ("input", "provenance"), "source usage")
        if row["usage"] == "input":
            path = (ROOT / row["path"]).resolve()
            need(path.is_relative_to(ROOT), "source path inside repository")
            raw = path.read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA: " + row["path"])
            need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"], "source Git blob")
    need(next(r for r in source["files"] if r["path"] == PACKET)["usage"] == "input", "packet is consumed input")
    raw = (ROOT / PACKET).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PACKET_SHA, "fixed packet pin")
    return load_json(gzip.decompress(raw))


def compute():
    packet = load_packet()
    invariant = invariants(packet)
    native_columns = physical_check(packet)
    original, upper = packet["programs"]["B_1_2"][:80], construct(packet)
    baseline_bill, upper_bill = typed(packet, original), typed(packet, upper)
    baseline = replay(packet, original)
    target = replay(packet, original, physical_shear(packet))
    actual = replay(packet, upper)
    need(actual == target, "complete ordered group-affine endpoint, all 712 rows")
    free_target = free_replay(original, sheared=True)
    need(free_replay(upper) == free_target, "all 712 free noncommuting-operator endpoint rows")
    for a, t in zip(A, T, strict=True):
        item = packet["native_line_recipes"]["inverse_" + str(t)]
        need(baseline[t] == line({(t, UNIT): ONE}, item), "every completed source path restores X_T")
        need(actual[t] == line({(t, UNIT): ONE, (a, UNIT): ONE}, item), "complete X_T endpoint")
        need(actual[112+t] == physical_shear(packet)[112+t], "complete Y_T endpoint")
    changed = set(A + T + [112+t for t in T] + [704])
    need(all(actual[i] == {(i, UNIT): ONE} for i in range(712) if i not in changed), "all fields outside complete endpoint footprint unchanged")
    need(all(actual[i] == {(i, UNIT): ONE} for i in range(224, 704)), "all 480 dirty helpers restored")
    need(actual[704] == {} and all(actual[i] == {(i, UNIT): ONE} for i in range(705, 712)), "private endpoint C0 zero, C1..7 unchanged")
    lo, hi = evaluate(target, False), evaluate(target, True)
    rr = [i for t in T for i in (t, 112+t)] + A
    cc = [i for a, t in zip(A, T, strict=True) for i in (a, t)] + [112+a for a in A]
    minor = [[add(hi[i].get(j, ZERO), neg(lo[i].get(j, ZERO))) for j in cc] for i in rr]
    need(determinant(minor) == (Q(4096), Q(0)), "exact rank-24 Gaussian minor")
    need([i for i in range(712) if lo[i] != hi[i]] == sorted(rr), "difference has exactly 24 nonzero rows")
    blo, bhi = evaluate(baseline, False), evaluate(baseline, True)
    br, bc = T + A, T + [112+a for a in A]
    need(determinant([[add(bhi[i].get(j, ZERO), neg(blo[i].get(j, ZERO))) for j in bc] for i in br]) != ZERO, "baseline rank-16 minor")
    need(sum(x != y for x, y in zip(blo, bhi, strict=True)) == 16, "baseline difference rank exactly 16")
    controls = []

    def reject(name, action):
        try:
            action()
        except (ValueError, KeyError):
            controls.append({"name": name, "outcome": "REJECT"})
        else:
            raise ValueError("control accepted: " + name)

    def semantic(program, source=packet):
        need(replay(source, program) == target, "full endpoint mismatch")

    # At two odd character layers C_q tensor C_q has eigenvalue i*i=-1.
    # A two-term simultaneous translation has eigenvalue alpha+beta=1.
    simultaneous = add((Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2)))
    tensor = mul((Q(0), Q(1)), (Q(0), Q(1)))
    reject("two_layer_simultaneous_translation_substitution", lambda: need(
        simultaneous == tensor, "one-layer two-term model differs from native tensor power"))
    bad = deepcopy(upper); bad[0][2][3], bad[0][2][4] = bad[0][2][4], bad[0][2][3]
    reject("free_operator_late_source_conversion", lambda: need(
        free_replay(bad) == free_target, "free-operator order differs before target subtraction"))
    bad = deepcopy(upper); bad[0][2][3][2] = "positive_21"
    reject("wrong_native_sign", lambda: semantic(bad))
    badp = deepcopy(packet); badp["native_line_recipes"]["inverse_21"]["recipe"]["left"]["phase"] += 1
    reject("native_wrapper_global_phase", lambda: physical_check(badp))
    bad = deepcopy(upper); del bad[0][2][0]
    reject("arbitrary_C0_without_initial_clear", lambda: semantic(bad))
    bad = deepcopy(upper); del bad[0][2][-1]
    reject("missing_row_boundary_clear", lambda: typed(packet, bad))
    bad = deepcopy(upper); del bad[1]
    reject("omitted_X_T_normalization", lambda: semantic(bad))
    bad = deepcopy(upper); bad[0][2][0][1][1] = ["L", 224]
    reject("borrowed_helper_clear", lambda: typed(packet, bad))
    bad = deepcopy(upper); bad[0][3] = "interleave owners"
    reject("private_owner_barrier", lambda: typed(packet, bad))
    badp = deepcopy(packet); name = original[8][2]
    badp["map_registry"][name]["payload_translation_at_identity_owner"] ^= 1
    reject("odd_translation_breaks_invariant", lambda: invariants(badp))
    reject("wrong_translation_full_endpoint", lambda: semantic(upper, badp))
    badp = deepcopy(packet)
    for event in original:
        if event[0] == "cover_map":
            badp["map_registry"][event[2]]["owner_right_matrix_columns"] = list(AXES)
    reject("payload_only_owner_route", lambda: semantic(upper, badp))
    bare = physical_shear(packet)
    for a, t in zip(A, T, strict=True):
        bare[112+t] = row_add({(112+t, UNIT): ONE}, {(a, UNIT): ONE}, neg(ONE))
    reject("bare_Y_subtraction", lambda: need(replay(packet, original, bare) == target, "bare Y shear differs"))
    need((baseline_bill["native_lines"], upper_bill["native_lines"]) == (16, 24), "attaining native line invoice")
    return {"status": MARKER, "source_boundary": {"base_commit": BASE, "packet_sha256": PACKET_SHA},
            "cut": {"case": "B_1_2", "end_exclusive": 80, "next_event": packet["programs"]["B_1_2"][80][:3]},
            "invoice": {"baseline": baseline_bill, "attaining": upper_bill, "delta": {k: upper_bill[k]-baseline_bill[k] for k in upper_bill}},
            "exact": {"full_operator_rows": 712, "full_operator_rows_scope": "one payload tensor layer (lambda=1)", "free_operator_rows": 712, "free_operator_rows_scope": "arbitrary noncommuting linear native/map operators, no tensor expansion", "native_recipe_basis_columns": native_columns, "dirty_helpers_restored": 480, "private_outputs": "C0 zero; C1..C7 arbitrary unchanged", "minor_rows": rr, "minor_columns": cc, "minor_det": [4096, 0], "rank": 24, "baseline_difference_rank": 16},
            "tensor_scope": {"exact_affine_replay_layers": 1,
                             "upper_bound": "all integer lambda>=1 by fresh free-operator endpoint equality and the written tensor interpretation",
                             "lower_bound": "all integer lambda>=1 by one Omega character layer and constant other layers",
                             "two_layer_odd_odd_counterexample": {"native_tensor_eigenvalue": [-1, 0], "simultaneous_two_term_eigenvalue": [1, 0]}},
            "invariant": invariant, "controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    if args.write_result:
        output = args.write_result.resolve()
        need(not output.is_relative_to(ROOT) and not output.exists(), "fresh external output only")
    result = compute()
    if args.write_result:
        with output.open("x") as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write("\n")
    else:
        need(exact(load_json((HERE / "RESULT.json").read_text())) == exact(result), "complete type-exact frozen RESULT")
    print(MARKER + " rank=24 baseline_lines=16 attaining_lines=24 controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()

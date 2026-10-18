#!/usr/bin/env python3
"""Exact local QQ16 future-chart read, with borrowed sources restored.

By ywz65 with substantial OpenAI Codex assistance, Apache-2.0. Source
reconstruction shares this author's method from the independent PR2456 audit;
no pending predecessor code is imported. No global supplier is claimed.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AXES = tuple(1 << i for i in range(73))
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
START = tuple((e, 1) for e in AXES[:17])
COMMON = tuple((e, 1) for e in AXES[9:25])
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def act(columns, vector):
    out = 0
    while vector:
        bit = vector & -vector
        out ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return out


@lru_cache(None)
def multiply(g, h):
    return tuple(act(g, v) for v in h)


def combine(a, b, coefficient=1):
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, Q(0)) + coefficient * value
    return {key: value for key, value in result.items() if value}


def routed(g, row):
    return {(variable, multiply(g, old)): value for (variable, old), value in row.items()}


@lru_cache(None)
def phase(terms):
    linear, quadratic = [0] * 73, [0] * 73
    for vector, coefficient in terms:
        bits = [i for i in range(73) if (vector >> i) & 1]
        for i in bits:
            linear[i] = (linear[i] + coefficient) % 4
            if coefficient % 2:
                for j in bits:
                    if j > i:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def move_frame(terms, mapping):
    g, shift = mapping
    return tuple((act(g, vector), coefficient) for vector, coefficient in terms) + ((shift, 2),)


def load_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    raw = {}
    for item in pins["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            need(sha(data) == item["sha256"], "source hash: " + item["path"])
            raw[item["path"]] = data
    packet = json.loads(gzip.decompress(raw["research/joint-query/certificate.json.gz"]))
    decoded = {}
    with tarfile.open(fileobj=io.BytesIO(raw["research/community-frontier1042-audit/selected-replay.tar.gz"]), mode="r:gz") as archive:
        for name, digest in MEMBERS.items():
            matches = [item for item in archive.getmembers() if item.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique source member")
            data = archive.extractfile(matches[0]).read()
            need(sha(data) == digest, "member hash: " + name)
            decoded[name.rsplit("/", 1)[-1]] = json.loads(gzip.decompress(data) if name.endswith("gz") else data)
    word, programs = decoded["CANONICAL-WORD.json.gz"], decoded["LOCAL-PROGRAMS.json.gz"]
    need((word["v"], 2 * word["v"] + word["R"]) == (112, 704), "source geometry")
    rows = [{i: Q(1)} for i in range(712)]
    for event in programs["forward"]:
        if event == ["phase", "centers"]:
            break
        if event[0] != "scalar":
            continue
        op = event[1]
        at = op[1][1] + (704 if op[1][0] == "C" else 0)
        if op[0] == "clear":
            rows[at] = {}
        elif op[0] == "scale":
            rows[at] = {j: x * Q(op[2], op[3]) for j, x in rows[at].items()}
        else:
            source = op[2][1] + (704 if op[2][0] == "C" else 0)
            need(op[0] in ("add", "copy"), "known source gate")
            rows[at] = dict(rows[source]) if op[0] == "copy" else combine(rows[at], rows[source], Q(op[3], op[4]))
    else:
        raise ValueError("missing source centre boundary")
    R = [[rows[c].get(p, Q(0)) for p in range(112)] for c in word["centers"]]
    need(R == [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]], "actual R")
    need(tuple(packet["U_ports"]) == U and tuple(packet["A_ports"]) == A and tuple(packet["T_ports"]) == T, "actual partition")
    need(all(x in (-1, 0, 1) for row in R for x in row), "signed unit coefficients")
    need(all(sum(R[k][p] ** 2 for k in range(8)) == 4 for p in U), "four terms per ordinary port")
    phases = decoded["DATA-PHASES.json"]
    program = packet["programs"]["B_1_2"]
    records = {}
    for p in U:
        source = phases["recipes"][p]
        need(source["port"] == p, "port binding")
        q = source["q"]
        basis = source["idle_children"][0]["orthogonal_axes"][:8]
        need(q < 512 and q.bit_count() % 2 == 1, "actual odd local port")
        need(all((q & b).bit_count() % 2 == 0 for b in basis), "port-normal chart")
        swaps = [b ^ AXES[17 + i] for i, b in enumerate(basis)]
        g = tuple(e ^ act(swaps, sum(((e & s).bit_count() % 2) << i for i, s in enumerate(swaps))) for e in AXES)
        shift = q ^ sum((((b.bit_count() - 1) // 2) % 2) << (17 + i) for i, b in enumerate(basis))
        inverse_shift = act(g, shift)
        names = [event[2] for event in program if event[0] == "cover_map" and event[1] == ["L", 112 + p]]
        need(len(names) == 4, "actual Y map pair inventory")
        entry, exit_map = [packet["map_registry"][name] for name in names[:2]]
        need(tuple(entry["owner_right_matrix_columns"]) == tuple(exit_map["owner_right_matrix_columns"]) == g, "actual future owner action")
        need(entry["payload_translation_at_identity_owner"] == shift and exit_map["payload_translation_at_identity_owner"] == inverse_shift, "actual future payload shifts")
        need(multiply(g, g) == AXES and act(g, q) == q, "involutive route fixes port")
        records[p] = {"q": q, "g": g, "shift": shift, "inverse_shift": inverse_shift, "entry_name": names[0], "exit_name": names[1]}
    return R, records, {name: sha(data) for name, data in raw.items()}


def literal_program(R):
    # Whole sweeps are explicit barriers: no ADD is interleaved with alignment.
    return ([{"op": "line", "port": p, "sign": -1} for p in U]
            + [{"op": "map", "port": p, "inverse": False} for p in U]
            + [{"op": "clear_output", "query": k} for k in range(8)]
            + [{"op": "add", "query": k, "port": p, "coefficient": int(R[k][p])} for k in range(8) for p in U if R[k][p]]
            + [{"op": "map", "port": p, "inverse": True} for p in U]
            + [{"op": "line", "port": p, "sign": 1} for p in U])


def replay(program, R, records, fault=None):
    frames = {p: START for p in U}
    frames.update({112 + k: () for k in range(8)})
    rows = {p: {(p, AXES): Q(1)} for p in frames}
    trace = Counter()
    for index, event in enumerate(program):
        op = event["op"]
        trace[op] += 1
        if op == "line":
            p, sign = event["port"], event["sign"]
            if fault == "omit_normalization" and sign == -1 and p == U[0]:
                continue
            if fault == "omit_restoration" and sign == 1 and p == U[0]:
                continue
            frames[p] += ((records[p]["q"], sign),)
        elif op == "map":
            p = event["port"]
            record = records[p]
            shift = record["inverse_shift"] if event["inverse"] else record["shift"]
            if fault == "omit_payload_translation" and p == U[0]:
                shift = 0
            if fault == "wrong_inverse_translation" and event["inverse"] and p == U[0]:
                shift = record["shift"]
            frames[p] = move_frame(frames[p], (record["g"], shift))
            rows[p] = routed(record["g"], rows[p])
        elif op == "clear_output":
            at = 112 + event["query"]
            if fault == "omit_output_clear" and event["query"] == 0:
                # Keep a matching declared frame to isolate the dirty-input fault.
                frames[at] = COMMON
                continue
            rows[at] = {}
            frames[at] = COMMON
        else:
            need(op == "add", "known query operation")
            p, at = event["port"], 112 + event["query"]
            need(phase(frames[p]) == phase(frames[at]), "unmatched native scalar frames at event " + str(index))
            coefficient = event["coefficient"]
            if fault == "wrong_query_coefficient" and event == next(x for x in program if x["op"] == "add"):
                coefficient = -coefficient
            rows[at] = combine(rows[at], rows[p], coefficient)
    for p in U:
        need(phase(frames[p]) == phase(START), "borrowed source frame not restored")
        need(rows[p] == {(p, AXES): Q(1)}, "borrowed source content not restored")
    for k in range(8):
        need(phase(frames[112 + k]) == phase(COMMON), "query output frame")
        expected = {(p, records[p]["g"]): R[k][p] for p in U if R[k][p]}
        need(rows[112 + k] == expected, "exact future query or dirty output mismatch")
    return dict(trace)


def rows_from_columns(columns):
    return [sum(((columns[j] >> i) & 1) << j for j in range(9)) for i in range(9)]


def linear_map(rows, address):
    return sum(((row & address).bit_count() % 2) << i for i, row in enumerate(rows))


def line_recipe(q, sign):
    pivot = (q & -q).bit_length() - 1
    columns = (q,) + tuple(1 << j for j in range(9) if j != pivot)
    images = {act(columns, address): address for address in range(512)}
    need(len(images) == 512, "invertible native wrapper")
    inverse_columns = tuple(images[1 << i] for i in range(9))
    return {"rank": 1, "left_rows": rows_from_columns(columns), "left_offset": 0 if sign == 1 else q, "right_rows": rows_from_columns(inverse_columns)}


def kernel(recipe, address):
    middle = linear_map(recipe["right_rows"], address)
    a = linear_map(recipe["left_rows"], middle) ^ recipe["left_offset"]
    b = linear_map(recipe["left_rows"], middle ^ 1) ^ recipe["left_offset"]
    need(a != b, "two native kernel terms")
    return {a: (1, 1), b: (1, -1)}  # Gaussian numerators, common denominator 2.


def calculate():
    R, records, pins = load_sources()
    program = literal_program(R)
    trace = replay(program, R, records)
    need(trace == {"line": 192, "map": 192, "clear_output": 8, "add": 384}, "literal invoice")
    need(len(program) == 776, "literal event count")
    controls = {}
    for fault in ("omit_normalization", "omit_restoration", "omit_payload_translation", "wrong_inverse_translation", "omit_output_clear", "wrong_query_coefficient"):
        try:
            replay(program, R, records, fault)
        except ValueError as error:
            controls[fault] = str(error)
        else:
            raise ValueError("ineffective fault: " + fault)
    # A first ADD before the whole alignment sweep must be rejected.
    reordered = deepcopy(program)
    target = next(i for i, event in enumerate(reordered) if event["op"] == "add")
    event = reordered.pop(target)
    first_map = next(i for i, item in enumerate(reordered) if item["op"] == "map")
    reordered.insert(first_map, event)
    try:
        replay(reordered, R, records)
    except ValueError as error:
        controls["query_before_alignment_and_output_preparation"] = str(error)
    else:
        raise ValueError("early query control ineffective")
    recipe_columns = 0
    recipes = {}
    for p in U:
        q = records[p]["q"]
        for sign in (-1, 1):
            recipe = line_recipe(q, sign)
            for address in range(512):
                need(kernel(recipe, address) == {address: (1, sign), address ^ q: (1, -sign)}, "exact signed rank-one native kernel")
                recipe_columns += 1
            recipes[f"{p}:{sign}"] = recipe
    bad = deepcopy(recipes[f"{U[0]}:-1"])
    bad["left_offset"] = 0
    need(kernel(bad, 0) != {0: (1, -1), records[U[0]]["q"]: (1, 1)}, "inverse line sign control")
    controls["inverse_line_without_translation"] = "kernel differs at address zero"
    # The unnormalized X field has precisely the residual C_q at the legal Y alignment.
    residuals = {}
    for p, record in records.items():
        aligned = move_frame(START, (record["g"], record["shift"]))
        need(phase(aligned) == phase(COMMON + ((record["q"], 1),)), "exact future-X residual")
        witness = (record["q"] & -record["q"])
        need(sum(c * ((v & witness).bit_count() % 2) for v, c in aligned) % 4 != sum(c * ((v & witness).bit_count() % 2) for v, c in COMMON) % 4, "residual is nonzero")
        residuals[str(p)] = {"line": record["q"], "nonzero_character": witness}
    invoice = {"rank_one_children": 192, "native_rank_mass": 192, "native_wrapper_maps": 384,
               "full_cover_maps": 192, "signed_ADD_macros": 384, "CLEAR_macros": 8,
               "scalar_real_primitive_allowance": 2 * (4 * 384 + 8), "owned_live_query_outputs": 8,
               "borrowed_source_arrays_restored": 96, "literal_events": 776}
    return {"status": "PASS_QQ16_FUTURE_X_QUERY", "source_sha256": pins, "member_sha256": MEMBERS,
            "source_cut": "post-B_1_2 X_U in completed frame F_(L+E1)", "output_frame": "F_(E1+E2)",
            "query": "R_U D_(2,U) C = B2 C", "formal_independent_inputs": 104,
            "future_X_residuals": residuals, "invoice": invoice, "controls": controls,
            "native_kernel_basis_columns": recipe_columns, "program": program, "native_recipes": recipes,
            "scope": "Complete local native operator read with restored sources and eight owned outputs; global delivery, retention, physical map cost, recursive precision and supplier invoice are open"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    encoded = json.dumps(result, sort_keys=True, indent=2, default=str) + "\n"
    path = HERE / "RESULT.json"
    if args.write_result:
        with path.open("x", encoding="utf-8", newline="\n") as out:
            out.write(encoded)
    else:
        need(path.read_text(encoding="utf-8") == encoded, "committed receipt mismatch")
    print("PASS_QQ16_FUTURE_X_QUERY sources=96 outputs=8 children=192 cover_maps=192 native_columns=98304 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()

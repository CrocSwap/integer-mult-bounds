#!/usr/bin/env python3
"""Review the current-query word without a producer import."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
REPO = LANES.parents[2]
SOURCE = LANES / "paired-package-review/upstream-followthrough-20261015/current-query-encoder"
PINS = {
    "CURRENT-QUERY.md": "9aedb1bf0c1a71fb0d8adef219ea3f1c31b4712d5813eb370f47bb5220d95214",
    "emit_current_query.py": "d2c45cd05f8ad0e27573226a012e183c5b0ecec4b49655beeb1f9fdd13fb3184",
    "CURRENT-QUERY.json": "efd485a0593468ca06fecced730a1cdd460868fe91d9d979b29f823dd4a94592",
}
PAYLOAD = "75d7f083af8d5687b971aa0c012e201b922f5473a4080869b581b9ba8c195fea"
CORE = "fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877"
WORD = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
GAUGE = "560aa5476d01bd6a2a595ad44b0f2e7999c6435c388882173fba000af4ea035f"
A = (0, 7, 20, 27, 36, 46, 57, 111)


def need(test, message):
    if not test:
        raise RuntimeError(message)


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Input pin: " + str(path))
    return raw


def plus(dst, src, coefficient=F(1)):
    for k, value in src.items():
        total = dst.get(k, F(0)) + coefficient * value
        if total:
            dst[k] = total
        else:
            dst.pop(k, None)


def product(a, b):
    result = []
    for row in a:
        out = {}
        for j, value in row.items():
            plus(out, b[j], value)
        result.append(out)
    return result


def deserialize(rows):
    return [{int(j): F(c) for j, c in row.items()} for row in rows]


def slot(wire):
    need(wire[0] in ("L", "C"), "Known register namespace")
    index = wire[1] + (704 if wire[0] == "C" else 0)
    need(0 <= index < 712, "Actual register bound")
    return index


def gate_info(event):
    gate = event[1]
    op, dst = gate[0], slot(gate[1])
    src = slot(gate[2]) if op in ("add", "copy") else None
    c = F(*gate[3:5]) if op == "add" else F(*gate[2:4]) if op == "scale" else F(1)
    need(src is None or src != dst, "Distinct scalar operands")
    return op, dst, src, c


def price(event):
    op, _, _, c = gate_info(event)
    if op in ("copy", "clear"):
        return 2
    n, d = abs(c.numerator), c.denominator
    need(n and not d & (d - 1), "Dyadic coefficient")
    if op == "scale":
        need(not n & (n - 1), "Unit SCALE")
        return 2 * (abs(n.bit_length() - d.bit_length()) + (c < 0))
    need(op == "add", "Known scalar gate")
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)


def replay(events, word):
    state = [{j: F(1)} for j in range(712)]
    frames = word["start"][:] + [None] * 8
    scalar_checks, native_checks = 0, 0
    for event in events:
        kind = event[0]
        if kind == "scalar":
            op, dst, src, c = gate_info(event)
            frame = event[2]
            if op == "clear":
                need(dst >= 704, "Only owned scratch is cleared")
                state[dst], frames[dst] = {}, frame
            else:
                need(frames[dst] == frame, "Scalar target frame")
                need(src is None or frames[src] == frame, "Scalar source frame")
                if op == "add":
                    plus(state[dst], state[src], c)
                elif op == "scale":
                    state[dst] = {j: value * c for j, value in state[dst].items() if value * c}
                elif op == "copy":
                    need(dst >= 704, "A new COPY uses owned scratch")
                    state[dst] = dict(state[src])
                else:
                    raise RuntimeError("Unknown scalar operation")
            scalar_checks += 1
        elif kind == "climb":
            dst, old, new = event[2:5]
            need(frames[dst] == old, "Retained native entry frame")
            frames[dst] = new
            native_checks += 1
        elif kind == "intrinsic_line":
            dst, p = slot(event[1]), event[2]
            need(p in A and dst == 112 + p and frames[dst] == word["final"][dst],
                 "The entire arbitrary selected target receives its line")
            need(event[3] == 1, "Positive selected normalization")
            frames[dst] = 1
        else:
            need(kind in ("phase", "adapter", "residual_adapter"), "Known retained event")
    return state, frames, scalar_checks, native_checks


def bit_map(rows, value):
    return sum(((row & value).bit_count() & 1) << j for j, row in enumerate(rows))


def gaussian_mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def native_checks(events, word):
    alpha, beta = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    checks, controls = 0, 0
    for event in events:
        p, recipe = event[2], event[4]
        q = word["ports"][p]
        need(recipe["rank"] == 1, "One selected line child")
        for side in ("left", "right"):
            r = recipe[side]
            need(not r["offset"] and not r["phase"] and not any(r["linear_Z4"] + r["quadratic_rows"]),
                 "Both maps have exact zero phase")
        left, right = recipe["left"]["matrix_rows"], recipe["right"]["matrix_rows"]
        for x in range(512):
            y = bit_map(right, x)
            actual = {bit_map(left, y): alpha, bit_map(left, y ^ 1): beta}
            need(actual == {x: alpha, x ^ q: beta}, "Exact spatial positive line kernel")
            # Multiply C_q by the inherited C_q^-1 at both spatial addresses.
            stay = tuple(a + b for a, b in zip(gaussian_mul(alpha, beta), gaussian_mul(beta, alpha)))
            move = tuple(a + b for a, b in zip(gaussian_mul(alpha, alpha), gaussian_mul(beta, beta)))
            need(stay == (1, 0) and move == (0, 0), "The normalized hole has no phase or translation")
            checks += 1
        # The inverse sign leaves translation X_q at the mixed endpoint.
        need(q != 0 and bit_map(left, bit_map(right, 0) ^ 1) == q, "Wrong-sign translation control")
        controls += 1
    return checks, controls


def phase_views(gauge, phases):
    checks = 0
    for p in A:
        rec = phases["recipes"][p]
        q = rec["q"]
        basis = tuple([q] + rec["idle_children"][0]["orthogonal_axes"][:8])
        for s, item in enumerate(rec["stage_alignment"]):
            route = gauge.rho(basis, s)
            need(gauge.act(route, q) == q, "Current owner view fixes the selected line")
            need(item["exit_X"] == item["exit_Y"], "Exact X/Y exterior output translations agree")
            full = gauge.UNIT[:8 * s + 9]
            hole = gauge.phase(full, (q,))
            normalized = gauge.phase(tuple(full) + (q,), (q,))
            need(normalized == gauge.phase(full), "Full 73-axis phase polynomial after the line")
            wrong = gauge.phase(full, (q, q))
            need(wrong != gauge.phase(full), "The wrong sign is not silently a FULL field")
            need(hole != normalized, "The old hole frame differs from the new selected frame")
            checks += 1
    return checks


def main():
    for name, pin in PINS.items():
        read(SOURCE / name, pin)
    data = json.loads(read(SOURCE / "CURRENT-QUERY-PROGRAM.json.gz", PAYLOAD, True))
    core = json.loads(read(LANES / "circuit-interface/CENTRE-FREE-PROGRAMS.json.gz", CORE, True))["forward"]
    raw_word = read(REPO / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz", WORD)
    word = json.loads(gzip.decompress(raw_word))
    gauge_path = LANES / "coherent-port/stage-gauge-20261015/check_gauge.py"
    read(gauge_path, GAUGE)
    spec = importlib.util.spec_from_file_location("own_stage_geometry", gauge_path)
    gauge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gauge)
    sources, phases = gauge.load()
    r = deserialize(sources["circuit-interface/INTERFACE.json"]["R"])
    need(data["selected_A"] == list(A) and deserialize(data["R"]) == r, "Actual R and selected minor")
    eye = [{p: F(1)} for p in range(112)]
    k = [{j: row[p] / 4 for j, row in enumerate(r) if p in row} for p in range(112)]
    ka = [dict(row) if p in A else {} for p, row in enumerate(k)]
    la = [{p: c for p, c in row.items() if p in A} for row in r]
    ru = [{p: c for p, c in row.items() if p not in A} for row in r]
    need(product(la, ka) == [{j: F(1)} for j in range(8)], "Actual selected dual")
    need(product(r, k) == [{j: F(14)} for j in range(8)], "Actual full Gram")
    j, ji, p, pi = [[dict(row) for row in eye] for _ in range(4)]
    for row, factor in ((j, F(-1)), (ji, F(-1, 13))):
        for n, v in enumerate(product(k, r)):
            plus(row[n], v, factor)
    for row, factor in ((p, 1), (pi, -1)):
        for n, v in enumerate(product(ka, ru)):
            plus(row[n], v, factor)
    target, inv = product(p, j), product(ji, pi)
    need(product(target, inv) == product(inv, target) == eye, "Both rational inverse orders")
    need(product(la, target) == [{p: -13 * c for p, c in row.items()} for row in r], "Exact full sum-query coefficient")
    correction = [dict(row) for row in target]
    for n, row in enumerate(j):
        plus(correction[n], row, -1)
    for name, value in (("P", p), ("J", j), ("PJ", target), ("S", correction), ("inverse_PJ", inv)):
        need(deserialize(data[name]) == value, "Rebuilt ordered matrix: " + name)
    need({n for n, row in enumerate(correction) if row} == set(A), "Only selected targets change")
    need(data["retained_core"] == core, "Every retained event is byte-equal")
    program = data["prefix"] + core + data["native_normalizations"] + data["suffix"]
    need(data["program"] == program and len(program) == 27397, "Exact event order")
    output, frames, scalars, climbs = replay(program, word)
    expected = [{n: F(1)} for n in range(712)]
    for n, row in enumerate(target):
        expected[112 + n] = dict(row)
        plus(expected[112 + n], {112 + q: c for q, c in row.items()})
    expected[704:] = [{} for _ in range(8)]
    need(output == expected, "All 712 formal input columns, including arbitrary scratch")
    need(frames == data["output_frames"], "The exact mixed endpoint frame ledger")
    need(all(frames[112 + p] == (1 if p in A else word["final"][112 + p]) for p in range(112)),
         "Selected FULL and unselected hole outputs")
    pre, _, _, _ = replay(data["prefix"], word)
    need(not pre[704] and all(pre[n] == {n: 1} for n in list(range(112)) + list(range(224, 704))),
         "The prefix clears C0 and preserves all source and borrowed inputs")
    kernels, bad_signs = native_checks(data["native_normalizations"], word)
    view_checks = phase_views(gauge, phases)
    j_prefix_length = sum(3 + len(row) + sum(mode in col for col in k) for mode, row in enumerate(r))
    no_p, _, _, _ = replay(data["prefix"][:j_prefix_length] + core + data["native_normalizations"] + data["suffix"], word)
    no_correction, _, _, _ = replay(data["prefix"] + core + data["native_normalizations"], word)
    need(no_p != expected and no_correction != expected, "Both omitted-data-factor controls fail")
    costs = {name: sum(price(e) for e in events if e[0] == "scalar")
             for name, events in (("prefix", data["prefix"]), ("core", core), ("suffix", data["suffix"]), ("total", program))}
    need(costs == {"prefix": 10880, "core": 202138, "suffix": 4932, "total": 217950}, "Independent scalar recount")
    profile = Counter(e[5] for e in core if e[0] == "climb")
    profile[1] += 8
    need(dict(profile) == {1: 2420, 2: 418, 3: 432, 4: 142, 5: 82}, "Complete local child profile")
    result = dict(status="PASS_CURRENT_QUERY_REVIEW", producer_pins=PINS, payload_sha256=PAYLOAD,
                  core_sha256=CORE, own_geometry_sha256=GAUGE, fields=712, arbitrary_helpers=480,
                  owned_private_zeros=8, exact_scalar_frame_checks=scalars, unchanged_native_climbs=climbs,
                  positive_line_spatial_columns=kernels, wrong_line_sign_controls=bad_signs,
                  omitted_data_factor_controls=2,
                  full_73_axis_exterior_view_cases=view_checks, costs=costs,
                  native_profile=dict(profile), native_mass=sum(r * n for r, n in profile.items()),
                  scope="Exact local word and phase/view composition; no new shared-owner or next-call admission.")
    (HERE / "REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_CURRENT_QUERY_REVIEW: 712 columns, 4096 native columns, and 72 exterior phase cases")


if __name__ == "__main__":
    main()

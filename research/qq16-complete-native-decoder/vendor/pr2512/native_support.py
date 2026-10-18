#!/usr/bin/env python3
"""Exact QQ16 helpers copied and adapted from ywz65 PR2492/PR2468; see PREDECESSORS.json.

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
COMMON = tuple((e, 1) for e in AXES[9:17])
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
    for item in pins['pending_sources']:
        data = (ROOT / item['path']).read_bytes()
        need(sha(data) == item['sha256'], 'pending source hash: ' + item['path'])
        raw[item['path']] = data
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
    for p in U + T:
        source = phases["recipes"][p]
        need(source["port"] == p, "port binding")
        q = source["q"]
        basis = source["idle_children"][0]["orthogonal_axes"][:8]
        need(q < 512 and q.bit_count() % 2 == 1, "actual odd local port")
        need(all((q & b).bit_count() % 2 == 0 for b in basis), "port-normal chart")
        swaps = [b ^ AXES[9 + i] for i, b in enumerate(basis)]
        g = tuple(e ^ act(swaps, sum(((e & s).bit_count() % 2) << i for i, s in enumerate(swaps))) for e in AXES)
        shift = q ^ sum((((b.bit_count() - 1) // 2) % 2) << (9 + i) for i, b in enumerate(basis))
        inverse_shift = act(g, shift)
        names = [event[2] for event in program if event[0] == "cover_map" and event[1] == ["L", 112 + p]]
        need(len(names) == 4, "actual Y map pair inventory")
        entry, exit_map = [packet["map_registry"][name] for name in names[2:]]
        need(tuple(entry["owner_right_matrix_columns"]) == tuple(exit_map["owner_right_matrix_columns"]) == g, "actual current owner action")
        need(entry["payload_translation_at_identity_owner"] == shift and exit_map["payload_translation_at_identity_owner"] == inverse_shift, "actual current payload shifts")
        need(multiply(g, g) == AXES and act(g, q) == q, "involutive route fixes port")
        records[p] = {"q": q, "g": g, "shift": shift, "inverse_shift": inverse_shift, "entry_name": names[2], "exit_name": names[3]}
    return R, records, {name: sha(data) for name, data in raw.items()}


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

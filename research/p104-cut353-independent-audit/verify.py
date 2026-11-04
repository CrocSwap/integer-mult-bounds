#!/usr/bin/env python3
"""Exact independent audit of PR6716's serialized cut353 retirement."""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
SOURCE_SHA = "0de615eb3eac51539567c56e85e177c91c0d3e5c2c69b8cd64abff46f68fc902"
CASE_SHA = "7a7e961a1971c31653770af43b0097ba55d1eb980795a050c74786e8f5c7d6c0"
SCHEMA_SHA = "3936e155a437939af360d5b2c4be83036984e56c7d04665c5eca2dc7f09ba50d"
ZERO = (F(0), F(0))
UNIT = (F(1), F(0))
MONOMIAL_ONE = (0,) * 19
ONE = {MONOMIAL_ONE: UNIT}
BYTE_CAP = 16777216


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def forbidden_number(_):
    raise ValueError("noninteger or nonfinite JSON number")


def json_types(value):
    need(type(value) in (dict, list, int, str, type(None)),
         "unsupported JSON type (including boolean)")
    if type(value) is dict:
        for key, item in value.items():
            need(type(key) is str, "nonstring JSON key")
            json_types(item)
    elif type(value) is list:
        for item in value:
            json_types(item)


def decode(data):
    need(len(data) <= BYTE_CAP, "input exceeds byte cap")
    value = json.loads(data, object_pairs_hook=unique_pairs,
                       parse_float=forbidden_number,
                       parse_constant=forbidden_number)
    json_types(value)
    return value


def load(path):
    return decode(path.read_bytes())


def exact(actual, expected, label):
    need(type(actual) is type(expected), label + ": type mismatch")
    if type(expected) is dict:
        need(set(actual) == set(expected), label + ": keys differ")
        for key in expected:
            exact(actual[key], expected[key], label + "/" + key)
    elif type(expected) is list:
        need(len(actual) == len(expected), label + ": lengths differ")
        for index, (left, right) in enumerate(zip(actual, expected)):
            exact(left, right, label + "/" + str(index))
    else:
        need(actual == expected, label + ": value differs")


def authenticate():
    for name, expected in (("SOURCE-PINS.json", SOURCE_SHA),
                           ("CASES.json", CASE_SHA),
                           ("SCHEMA.json", SCHEMA_SHA)):
        need(sha((ROOT / name).read_bytes()) == expected,
             "source/case/schema byte authentication: " + name)
    manifest = load(ROOT / "SOURCE-PINS.json")
    need(type(manifest.get("sources")) is list
         and len(manifest["sources"]) == 6, "six inert source objects")
    paths = []
    for row in manifest["sources"]:
        path = row["local_path"]
        need(path.startswith("inputs/") and ".." not in Path(path).parts,
             "source path outside inputs")
        need(sha((ROOT / path).read_bytes()) == row["sha256"],
             "source bytes differ: " + path)
        paths.append(path)
    need(len(set(paths)) == 6, "duplicate source path")


def zproduct(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def padd(left, right, factor=UNIT):
    result = dict(left)
    for key, value in right.items():
        real, imag = zproduct(value, factor)
        old = result.get(key, ZERO)
        value = old[0] + real, old[1] + imag
        if value == ZERO:
            result.pop(key, None)
        else:
            result[key] = value
    return result


def pscale(poly, coefficient):
    return padd({}, poly, (F(coefficient), F(0)))


def pshift(poly, q=0, stages=(), degree=1):
    result = {}
    for key, value in poly.items():
        exponents = list(key)
        exponents[0] = (exponents[0] + q) % 4
        for stage in stages:
            exponents[stage] += degree
        result[tuple(exponents)] = value
    return result


def plambda(poly, sign):
    return padd(padd({}, poly, (F(1, 2), F(sign, 2))),
                pshift(poly, q=2), (F(1, 2), F(-sign, 2)))


def normalized_central(poly):
    return plambda(pshift(poly, q=-1), 1)


def eye(size):
    return [[dict(ONE) if row == column else {}
             for column in range(size)] for row in range(size)]


def row_add(left, right, coefficient):
    factor = F(coefficient), F(0)
    return [padd(a, b, factor) for a, b in zip(left, right)]


def row_shift(row, q=0, stages=()):
    return [pshift(poly, q=q, stages=stages) for poly in row]


def apply(matrix, event):
    op = event[0]
    if op == "ADD":
        matrix[event[1]] = row_add(matrix[event[1]], matrix[event[2]], event[3])
    elif op == "SWAP":
        matrix[event[1]], matrix[event[2]] = matrix[event[2]], matrix[event[1]]
    elif op == "SCALE":
        matrix[event[1]] = [pscale(poly, event[2]) for poly in matrix[event[1]]]
    elif op == "LAMBDA":
        matrix[event[1]] = [plambda(poly, event[2]) for poly in matrix[event[1]]]
    elif op == "Q_POWER":
        matrix[event[1]] = row_shift(matrix[event[1]], q=event[2])
    elif op == "QUERY":
        source = row_shift(matrix[event[2]], q=event[3])
        matrix[event[1]] = row_add(matrix[event[1]], source, 1)
    elif op == "LOCAL":
        _, stage, src, dst = event
        matrix[dst] = row_add(matrix[dst], row_shift(matrix[src], q=-1), 1)
        for owner in (src, dst):
            matrix[owner] = row_shift(matrix[owner], stages=[stage])
    elif op in ("IDLE", "IDLE_ONE"):
        owners, stages = (event[1:3], event[3]) if op == "IDLE" else ([event[1]], event[2])
        for owner in owners:
            matrix[owner] = row_shift(matrix[owner], stages=stages)
    else:
        raise ValueError("unknown opcode: " + str(op))


def valid_index(value, size):
    need(type(value) is int and 0 <= value < size, "invalid role index")


def validate_event(event, size, ordinary=False):
    need(type(event) is list and len(event) >= 3, "event shape")
    op = event[0]
    lengths = {"ADD": 4, "SWAP": 3, "SCALE": 3, "LAMBDA": 3,
               "Q_POWER": 3, "QUERY": 4, "LOCAL": 4,
               "IDLE": 4, "IDLE_ONE": 3}
    need(op in lengths and len(event) == lengths[op], "opcode arity")
    if ordinary:
        need(op in ("ADD", "SWAP", "SCALE"), "nonordinary basis opcode")
    positions = [1, 2] if op in ("ADD", "SWAP", "QUERY", "IDLE") else [1]
    if op == "LOCAL":
        positions = [2, 3]
        need(type(event[1]) is int and 1 <= event[1] <= 18, "native stage")
    for index in positions:
        valid_index(event[index], size)
    if len(positions) == 2:
        need(event[positions[0]] != event[positions[1]], "aliased event roles")
    if op in ("ADD", "SCALE"):
        need(type(event[-1]) is str and F(event[-1]) != 0, "nonzero rational scalar")
    if op in ("QUERY", "LAMBDA"):
        need(type(event[-1]) is int and event[-1] in (-1, 1), "central sign")
    if op == "Q_POWER":
        need(type(event[-1]) is int, "central exponent")
    if op in ("IDLE", "IDLE_ONE"):
        stages = event[-1]
        need(type(stages) is list and len(stages) == len(set(stages)), "idle stage set")
        need(all(type(x) is int and 1 <= x <= 18 for x in stages), "idle stages")


def validate_controller(value, size, events):
    need(type(value) is dict and set(value) == {"schema", "roles", "stages",
         "ambient_rank", "events", "diagonal", "nodes"}, "controller keys")
    need(value["roles"] == size and type(value["roles"]) is int,
         "controller role count")
    need(value["stages"] == 18 and value["ambient_rank"] == 153,
         "controller stage/rank contract")
    need(len(value["events"]) == events, "controller event count")
    for event in value["events"]:
        validate_event(event, size)
    need(len(value["diagonal"]) == size, "controller target count")
    for target in value["diagonal"]:
        need(type(target) is list and len(target) == 20
             and all(type(x) is int for x in target), "target exponent schema")
        need(target[1] == 0, "nonzero undeclared stage-zero target")


def run_matrix(events, size):
    matrix = eye(size)
    for event in events:
        apply(matrix, event)
        need(sum(len(cell) for row in matrix for cell in row) <= 100000,
             "simultaneous matrix polynomial term cap exceeded")
    return matrix


def scalar_vector(entries, size):
    need(type(entries) is dict, "ordinary vector schema")
    vector = [F(0) for _ in range(size)]
    for key, value in entries.items():
        need(type(key) is str and str(int(key)) == key, "ordinary vector index")
        valid_index(int(key), size)
        need(type(value) is str, "ordinary vector coefficient")
        vector[int(key)] = F(value)
    return vector


def scalar_pair(left, right):
    return sum(a * b for a, b in zip(left, right))


def linear_combination(polys, coefficients):
    result = {}
    for poly, coefficient in zip(polys, coefficients):
        if coefficient:
            result = padd(result, poly, (coefficient, F(0)))
    return result


def row_times(vector, matrix):
    return [linear_combination(column, vector) for column in zip(*matrix)]


def matrix_times(matrix, vector):
    return [linear_combination(row, vector) for row in matrix]


def expected_vector(vector):
    return [normalized_central(pscale(ONE, coefficient)) for coefficient in vector]


def check_bases(witness, a, b, c, d):
    for name, row, column in (("boundary", c, d), ("middle", a, b)):
        for event in witness[name]:
            validate_event(event, 34, ordinary=True)
        matrix = run_matrix(witness[name], 34)
        need(matrix[4] == [pscale(ONE, value) for value in row],
             "ordinary basis row: " + name)
        image = matrix_times(matrix, column)
        need(image == [ONE if role == 4 else {} for role in range(34)],
             "ordinary basis column: " + name)


def inverse_ordinary(events):
    inverse = []
    for event in reversed(events):
        op = event[0]
        if op == "ADD":
            inverse.append([op, event[1], event[2], str(-F(event[3]))])
        elif op == "SCALE":
            inverse.append([op, event[1], str(1 / F(event[2]))])
        else:
            need(op == "SWAP", "inverse requires ordinary gates")
            inverse.append(event[:])
    return inverse


def renamed(event, pivot, fresh):
    out = event[:]
    positions = {"ADD": [1, 2], "SWAP": [1, 2], "SCALE": [1],
                 "LAMBDA": [1], "Q_POWER": [1], "QUERY": [1, 2],
                 "LOCAL": [2, 3], "IDLE": [1, 2], "IDLE_ONE": [1]}
    for position in positions[event[0]]:
        if out[position] == pivot:
            out[position] = fresh
    return out


def check_serialized_surgery(base, final, witness):
    cut, pivot, fresh = witness["cut_after"], witness["pivot"], witness["fresh"]
    need((cut, pivot, fresh, witness["handoff_after"]) == (353, 4, 34, 362),
         "literal cut/handoff ABI")
    need(base["events"][353] == ["LAMBDA", 20, 1], "actual normalized cut")
    need(witness["group"] == [4, 20, 21], "equal-target group")
    expected = inverse_ordinary(witness["boundary"])
    expected += base["events"][:cut + 1] + witness["middle"]
    expected += [renamed(e, pivot, fresh) for e in inverse_ordinary(witness["middle"])]
    expected += [renamed(e, pivot, fresh) for e in base["events"][cut + 1:]]
    expected += [["LAMBDA", owner, 1] for owner in (fresh, 20, 21)]
    expected += [renamed(e, pivot, fresh) for e in witness["boundary"]]
    expected += [["LAMBDA", owner, -1] for owner in (pivot, 20, 21)]
    need(final["events"] == expected, "complete serialized retirement surgery")
    contacts = [index for index, event in enumerate(final["events"])
                if renamed(event, fresh, 35) != event]
    need(contacts and contacts[0] == 363, "fresh role touched before handoff")


def paid_signature(events):
    result = []
    for event in events:
        op = event[0]
        if op == "LOCAL":
            result.append([op, event[1]])
        elif op == "QUERY":
            result.append([op, event[3]])
        elif op in ("IDLE", "IDLE_ONE"):
            result.append([op, event[-1]])
    return result


def encode_poly(poly):
    return [[key[0], list(key[1:]), [value[0].numerator, value[0].denominator,
            value[1].numerator, value[1].denominator]]
            for key, value in sorted(poly.items())]


def encode_vector(vector):
    return [encode_poly(poly) for poly in vector]


def derive_targets(base):
    targets = copy.deepcopy(base["diagonal"])
    need(targets[4] == targets[20] == targets[21], "complete equal-endpoint group")
    targets[4] = [-1] + [0] * 19
    targets.append([0, 0] + [int(10 <= stage <= 13) for stage in range(1, 19)])
    return targets


def check_endpoint(matrix, targets):
    for row in range(35):
        for column in range(35):
            target = targets[row]
            key = (target[0] % 4, *target[2:])
            need(matrix[row][column] == ({key: UNIT} if row == column else {}),
                 "complete independent-input endpoint row/column")


def scientific(base, final, witness):
    validate_controller(base, 34, 562)
    validate_controller(final, 35, 586)
    a, b, c, d = [scalar_vector(witness[name], 34) for name in ("a", "b", "c", "d")]
    need(scalar_pair(a, b) == scalar_pair(c, d) == 1, "two ordinary dual pairings")
    check_bases(witness, a, b, c, d)
    check_serialized_surgery(base, final, witness)
    prefix = run_matrix(base["events"][:354], 34)
    a_prefix, prefix_d = row_times(a, prefix), matrix_times(prefix, d)
    need(a_prefix == expected_vector(c), "prefix row aP=S c")
    need(prefix_d == expected_vector(b), "prefix column Pd=S b")
    targets = derive_targets(base)
    need(final["diagonal"] == targets, "independently derived retired targets")
    matrix = run_matrix(final["events"], 35)
    check_endpoint(matrix, targets)
    need(paid_signature(base["events"]) == paid_signature(final["events"]),
         "paid stage/sign/order changed")
    artifact = {"schema_version": 1, "a_prefix": encode_vector(a_prefix),
                "prefix_d": encode_vector(prefix_d),
                "final_matrix": [encode_vector(row) for row in matrix]}
    return artifact


def rejected(function, label, diagnostic=None):
    try:
        function()
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        need(diagnostic is None or diagnostic in str(error),
             "control rejected for unintended reason: " + label + ": " + str(error))
        return
    raise ValueError("control accepted: " + label)


def controls(base, final, witness):
    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1.0}', b'{"x":true}'):
        rejected(lambda raw=raw: decode(raw), "strict JSON")
    rejected(lambda: validate_event(["ADD", True, 1, "1"], 35), "boolean role")
    rejected(lambda: validate_event(["LOCAL", 19, 0, 1], 35), "unbound stage")
    mutant = copy.deepcopy(witness)
    mutant["a"]["20"] = "-2"
    a, b = [scalar_vector(mutant[name], 34) for name in ("a", "b")]
    rejected(lambda: need(scalar_pair(a, b) == 1, "broken dual pairing"), "pairing")
    targets = derive_targets(base)
    bad_query = copy.deepcopy(final["events"])
    index = next(i for i, event in enumerate(bad_query) if event[0] == "QUERY")
    bad_query[index][-1] *= -1
    bad_basis = copy.deepcopy(final["events"])
    bad_basis[0][-1] = "-2"
    bad_fresh = final["events"] + [["Q_POWER", 34, 1]]
    for events, label in ((bad_query, "query central sign"),
                          (bad_basis, "input basis coefficient"),
                          (bad_fresh, "unearned fresh central factor")):
        rejected(lambda events=events: check_endpoint(run_matrix(events, 35), targets),
                 label, "complete independent-input endpoint")
    return 10


def receipt(artifact):
    return {"schema_version": 1, "source_manifest_sha256": SOURCE_SHA,
            "case_manifest_sha256": CASE_SHA,
            "scope": "PR6716 cut353 fresh34 conditional LOCAL audit",
            "cut_after": 353, "handoff_after": 362, "pivot": 4, "fresh": 34,
            "unretired_roles": 34, "unretired_events": 562,
            "final_roles": 35, "final_events": 586, "stages": 18,
            "cut_cells": 68, "final_cells": 1225, "ordinary_identities": 6,
            "fresh_first_contact": 363,
            "artifact_sha256": sha(canonical(artifact))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--write-packet", type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    authenticate()
    base = load(ROOT / "inputs/CONTROLLER-UNRETIRED.json")
    final = load(ROOT / "inputs/CONTROLLER.json")
    witness = load(ROOT / "inputs/WITNESS.json")
    artifact = scientific(base, final, witness)
    need(len(canonical(artifact)) <= 4194304, "artifact exceeds4MiB")
    count = controls(base, final, witness)
    result = receipt(artifact)
    need(time.monotonic() - start <= 180, "runtime exceeds180seconds")
    if args.write_packet:
        args.write_packet.write_bytes(canonical(artifact) + b"\n")
    else:
        exact(load(ROOT / "PACKET.json"), artifact, "actual packet")
    if args.emit:
        sys.stdout.buffer.write(canonical(result) + b"\n")
    else:
        exact(load(ROOT / "RESULT.json"), result, "retained result")
        print(f"PASS_P104_CUT353_INDEPENDENT_AUDIT positions=1225 controls={count} no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_P104_CUT353_INDEPENDENT_AUDIT: " + str(error), file=sys.stderr)
        raise SystemExit(1)

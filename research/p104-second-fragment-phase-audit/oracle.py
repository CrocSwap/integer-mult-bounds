#!/usr/bin/env python3
"""Independent reverse-output-row transport of literal formal event matrices."""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
METADATA = {
    "CONTRACT.json": "b0288cba97a7171a41817d32c255c971201b0ef2b32bbfea6c161bed917a216f",
    "CASES.json": "74f116e973e2fb1cd5653926bd001dc18ddbca3f52f08b14f2d8e3bf3fd0bc34",
    "SOURCE-PINS.json": "1fcb4715775c545350fe2a179e73d11ea02266a3d27ae53d9dd18492d203b5e5"}
JSON_SOURCES = ("CONTROLLER-UNRETIRED.json", "CONTROLLER-ONE-RETIRED.json",
                "CONTROLLER.json", "RETIREMENT-WITNESSES.json")
ZERO_KEY = (0,) * 20
GZERO = (Fraction(0), Fraction(0))
GONE = (Fraction(1), Fraction(0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    need(type(value) is int, "proof integer excludes Boolean")
    return value


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def no_float(_):
    raise ValueError("float or nonfinite JSON token")


def decode(raw):
    need(len(raw) <= 8*1024*1024, "JSON input cap")
    return json.loads(raw, object_pairs_hook=pairs, parse_float=no_float, parse_constant=no_float)


def load(path):
    return decode(path.read_bytes())


def canonical(packet):
    return json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"


def authenticate(base):
    for name, expected in METADATA.items():
        need(hashlib.sha256((base/name).read_bytes()).hexdigest() == expected,
             "frozen metadata drift: " + name)
    pins = load(base/"SOURCE-PINS.json")
    need(len(pins["sources"]) == 12, "twelve source objects")
    seen = set()
    for row in pins["sources"]:
        name = row["local_path"]
        need(type(name) is str and name.startswith("inputs/") and ".." not in Path(name).parts
             and name not in seen, "source path schema")
        seen.add(name)
        raw = (base/name).read_bytes()
        need(len(raw) == integer(row["bytes"]), "source size drift: " + name)
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256 drift: " + name)
        header = ("blob " + str(len(raw))).encode("ascii") + b"\0"
        need(hashlib.sha1(header+raw).hexdigest() == row["git_blob"], "source Git blob drift: " + name)
    return {name: hashlib.sha256((base/"inputs"/name).read_bytes()).hexdigest()
            for name in JSON_SOURCES}


def gadd(a, b):
    return (a[0]+b[0], a[1]+b[1])


def gmul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def add_poly(a, b):
    result = a.copy()
    for key, value in b.items():
        summed = gadd(result.get(key, GZERO), value)
        if summed == GZERO:
            result.pop(key, None)
        else:
            result[key] = summed
    need(len(result) <= 100000, "polynomial term cap")
    return result


def multiply(a, b):
    result = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            key = ((ka[0]+kb[0]) % 4, 0) + tuple(ka[j]+kb[j] for j in range(2, 20))
            coefficient = gadd(result.get(key, GZERO), gmul(va, vb))
            if coefficient == GZERO:
                result.pop(key, None)
            else:
                result[key] = coefficient
    need(len(result) <= 100000, "polynomial product cap")
    return result


def monomial(exponent=0, stages=(), coefficient=GONE):
    key = [0] * 20
    key[0] = integer(exponent) % 4
    for stage in stages:
        need(1 <= integer(stage) <= 18, "stage range")
        key[stage+1] += 1
    return {} if coefficient == GZERO else {tuple(key): coefficient}


def scalar(text):
    need(type(text) is str and re.fullmatch(r"[+-]?[0-9]+(?:/[0-9]+)?", text), "rational scalar text")
    value = Fraction(text)
    need(value != 0 and value.denominator & (value.denominator-1) == 0, "nonzero dyadic scalar")
    return monomial(coefficient=(value, Fraction(0)))


def lambda_poly(sign):
    need(type(sign) is int and sign in (-1, 1), "lambda sign")
    half = Fraction(1, 2)
    return add_poly(monomial(0, coefficient=(half, sign*half)),
                    monomial(2, coefficient=(half, -sign*half)))


def set_field(row, index, value):
    if value:
        row[index] = value
    else:
        row.pop(index, None)


def transport_event(row, event, roles):
    need(type(event) is list and event and type(event[0]) is str, "event shape")
    op = event[0]
    indices = {"ADD": (1,2), "SCALE": (1,), "SWAP": (1,2), "QUERY": (1,2),
               "LOCAL": (2,3), "IDLE": (1,2), "IDLE_ONE": (1,),
               "Q_POWER": (1,), "LAMBDA": (1,)}
    sizes = {"ADD":4,"SCALE":3,"SWAP":3,"QUERY":4,"LOCAL":4,
             "IDLE":4,"IDLE_ONE":3,"Q_POWER":3,"LAMBDA":3}
    need(op in sizes and len(event) == sizes[op], "unknown/ambiguous opcode")
    for position in indices[op]:
        need(0 <= integer(event[position]) < roles, "event role range")
    if len(indices[op]) == 2:
        need(event[indices[op][0]] != event[indices[op][1]], "distinct event roles")
    if op == "SWAP":
        a, b = event[1:]
        olda, oldb = row.get(a, {}), row.get(b, {})
        set_field(row, a, oldb)
        set_field(row, b, olda)
    elif op in ("ADD", "QUERY"):
        dst, src = event[1:3]
        factor = scalar(event[3]) if op == "ADD" else monomial(integer(event[3]))
        set_field(row, src, add_poly(row.get(src, {}), multiply(row.get(dst, {}), factor)))
    elif op == "LOCAL":
        stage, src, dst = event[1:]
        body = monomial(stages=(stage,))
        set_field(row, src, multiply(row.get(src, {}), body))
        set_field(row, dst, multiply(row.get(dst, {}), body))
        set_field(row, src, add_poly(row.get(src, {}), multiply(row.get(dst, {}), monomial(-1))))
    else:
        transport_diagonal(row, event)


def transport_diagonal(row, event):
    op, role = event[:2]
    if op == "SCALE":
        factor = scalar(event[2])
    elif op == "Q_POWER":
        factor = monomial(integer(event[2]))
    elif op == "LAMBDA":
        factor = lambda_poly(event[2])
    else:
        stages = event[3] if op == "IDLE" else event[2]
        need(type(stages) is list, "stage-list type")
        factor = monomial(stages=stages)
    set_field(row, role, multiply(row.get(role, {}), factor))
    if op == "IDLE":
        other = event[2]
        set_field(row, other, multiply(row.get(other, {}), factor))


def reverse_rows(events, roles):
    need(type(events) is list and 0 < len(events) <= 607 and 1 <= roles <= 34, "matrix bounds")
    matrix = []
    for output in range(roles):
        row = {output: monomial()}
        for event in reversed(events):
            transport_event(row, event, roles)
        matrix.append([row.get(column, {}) for column in range(roles)])
    return matrix


def target_matrix(controller):
    roles = integer(controller["roles"])
    need(len(controller["diagonal"]) == roles, "declared diagonal size")
    result = [[{} for _ in range(roles)] for _ in range(roles)]
    for index, raw in enumerate(controller["diagonal"]):
        need(type(raw) is list and len(raw) == 20 and integer(raw[1]) == 0, "diagonal dummy/key shape")
        need(all(type(value) is int for value in raw) and all(value >= 0 for value in raw[2:]), "diagonal exponent type")
        key = (raw[0] % 4, 0, *raw[2:])
        result[index][index] = {key: GONE}
    return result


def linear(polynomials, coefficients):
    result = {}
    for index, coefficient in coefficients.items():
        factor = monomial(coefficient=(Fraction(coefficient), Fraction(0)))
        result = add_poly(result, multiply(polynomials[int(index)], factor))
    return result


def endpoint_gate(actual, expected):
    need(actual == expected, "endpoint_mismatch")


def event_roles(event):
    positions = {"ADD":(1,2),"SCALE":(1,),"SWAP":(1,2),"QUERY":(1,2),
                 "LOCAL":(2,3),"IDLE":(1,2),"IDLE_ONE":(1,),
                 "Q_POWER":(1,),"LAMBDA":(1,)}
    need(type(event) is list and event and event[0] in positions, "chronology opcode")
    return tuple(integer(event[position]) for position in positions[event[0]])


def structural_binding(controller, one, witness):
    expected = {"cut_after":394,"handoff_after":401,"pivot":4,"fresh":33,
                "prefix_stages":[10]}
    for name, value in expected.items():
        need(witness[name] == value, "second witness binding: " + name)
    prefix_target = [0] * 20
    prefix_target[0], prefix_target[11] = -1, 1
    suffix_target = [0] * 20
    for stage in range(11, 15):
        suffix_target[stage+1] = 1
    need(witness["prefix_target"] == prefix_target, "witness prefix target")
    need(witness["suffix_target"] == suffix_target, "witness suffix target")
    events = controller["events"]
    need(events[:402] == witness["input_basis"] + one["events"][:395]
         + witness["cut_basis"], "literal prefix concatenation")
    need(all(33 not in event_roles(event) for event in events[:402]), "premature fresh33 contact")
    need(all(4 not in event_roles(event) for event in events[402:]), "parked4 suffix contact")


def identity_gate(final, prefix, one, controller, contract, witnesses):
    endpoint_gate(final, target_matrix(controller))
    retired = monomial(-1, (10,))
    for index in range(34):
        need(prefix[4][index] == (retired if index == 4 else {}), "retired row phase")
        need(prefix[index][4] == (retired if index == 4 else {}), "retired column phase")
        need(prefix[33][index] == (monomial() if index == 33 else {}), "fresh row untouched")
        need(prefix[index][33] == (monomial() if index == 33 else {}), "fresh column untouched")
    pair = contract["pair"]
    factor = multiply(lambda_poly(1), monomial(-1, (10,)))
    for index in range(33):
        pc = linear(one[index], pair["c"])
        bp = linear([one[j][index] for j in range(33)], pair["b"])
        a = pair["a"].get(str(index), 0)
        d = pair["d"].get(str(index), 0)
        need(pc == multiply(factor, monomial(coefficient=(Fraction(a), Fraction(0)))), "Pc phase identity")
        need(bp == multiply(factor, monomial(coefficient=(Fraction(d), Fraction(0)))), "bP phase identity")
    unit_and_inverse(pair, witnesses[1]["cut_basis"])
    return {name: True for name in contract["identities"]}


def unit_and_inverse(pair, basis):
    dc = sum(value*pair["c"].get(index, 0) for index, value in pair["d"].items())
    ba = sum(value*pair["a"].get(index, 0) for index, value in pair["b"].items())
    need(dc == 1 and ba == 1, "unit pairings")
    inverse = []
    for event in reversed(basis):
        op = event[0]
        if op == "ADD":
            inverse.append([op,event[1],event[2],str(-Fraction(event[3]))])
        elif op == "LAMBDA":
            inverse.append([op,event[1],-integer(event[2])])
        elif op == "SWAP":
            inverse.append(event[:])
        else:
            raise ValueError("cut basis opcode")
    expected = [[monomial() if i == j else {} for j in range(34)] for i in range(34)]
    need(reverse_rows(basis+inverse, 34) == expected, "cut basis inverse")
    need(reverse_rows(inverse+basis, 34) == expected, "inverse cut basis")


def mutate(events, case):
    result = copy.deepcopy(events)
    if "delete" in case:
        del result[integer(case["delete"])]
    elif "replace_index" in case:
        result[integer(case["replace_index"])] = case["event"]
    elif "swap_indices" in case:
        a, b = map(integer, case["swap_indices"])
        result[a], result[b] = result[b], result[a]
    elif "insert_index" in case:
        result.insert(integer(case["insert_index"]), case["event"])
    else:
        start, stop = map(integer, case["replace_slice"])
        result[start:stop] = case["events"]
    return result


def semantic_controls(controller, cases):
    expected = target_matrix(controller)
    results = []
    for case in cases["controls"]:
        actual = reverse_rows(mutate(controller["events"], case), 34)
        try:
            endpoint_gate(actual, expected)
        except ValueError as error:
            need(str(error) == "endpoint_mismatch", "wrong semantic failure")
            results.append({"id":case["id"],"accepted":False,"failure_gate":"endpoint_mismatch"})
        else:
            raise ValueError("semantic control accepted: " + case["id"])
    need(len(results) == 7, "seven semantic controls")
    return results


def serialize_matrix(matrix):
    return [[[[list(key),[value[0].numerator,value[0].denominator,
                         value[1].numerator,value[1].denominator]]
               for key,value in sorted(cell.items())] for cell in row] for row in matrix]


def certificate(base):
    sources = authenticate(base)
    contract, cases = load(base/"CONTRACT.json"), load(base/"CASES.json")
    controllers = {name: load(base/"inputs"/name) for name in JSON_SOURCES[:3]}
    matrices = {}
    for name, descriptor in contract["matrices"].items():
        data = controllers[descriptor["file"]]
        need(integer(data["roles"]) == descriptor["roles"] and integer(data["stages"]) == 18, "controller dimensions")
        count = integer(descriptor["take_events"])
        need(count <= len(data["events"]), "prefix event count")
        matrices[name] = reverse_rows(data["events"][:count], data["roles"])
    controller = controllers["CONTROLLER.json"]
    need(len(controller["events"]) == 606, "final word length")
    witnesses = load(base/"inputs/RETIREMENT-WITNESSES.json")
    structural_binding(controller, controllers["CONTROLLER-ONE-RETIRED.json"], witnesses[1])
    identities = identity_gate(matrices["final606"], matrices["prefix402"],
                               matrices["one_prefix395"], controller, contract, witnesses)
    controls = semantic_controls(controller, cases)
    return {"schema":contract["certificate"]["schema"],"sources":sources,
            "matrices":{name:serialize_matrix(matrix) for name,matrix in matrices.items()},
            "identities":identities,"controls":controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=HERE)
    parser.add_argument("--certificate-out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    need(not(args.certificate_out and args.check), "choose emission or comparison")
    packet = certificate(args.inputs)
    raw = canonical(packet)
    if args.certificate_out:
        args.certificate_out.write_bytes(raw)
    else:
        actual = (args.check or HERE/"ORACLE.json").read_bytes()
        decode(actual)
        need(actual == raw, "whole actual certificate byte mismatch")
    print("PASS_CUT401_REVERSE_ROWS matrices3 controls7 conditional_no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError,ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as error:
        print("FAIL_CUT401_REVERSE_ROWS: " + str(error), file=sys.stderr)
        raise SystemExit(1)

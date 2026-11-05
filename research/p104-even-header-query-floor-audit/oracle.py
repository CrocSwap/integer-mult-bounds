#!/usr/bin/env python3
"""Four-character exact scalar-header audit; stdlib only, no source imports."""
import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


META = {
    "CONTRACT.json": "e953a170c71e0bd956b7dafa0d7447d5982d465d65a469869d3ba0bad006c10d",
    "CASES.json": "688c76fd3d68fcbfb9b96090080fc5fbd611e58587d9e890c27cb20ee0c6270f",
    "SOURCE-PINS.json": "56853ff086872d33612e4698540d14caa7ebd69e965432bd9ad89740b5d24557",
}
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
IMAG = (Fraction(0), Fraction(1))
ROOTS = (ONE, (-ONE[0], ZERO[1]), IMAG, (ZERO[0], -ONE[0]))
CAP = 8388608


class Failure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def no_number(text):
    raise Failure("noninteger JSON number prohibited: " + text)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_bytes(path):
    data = path.read_bytes()
    require(len(data) <= CAP, "input byte cap")
    return data


def load(data):
    try:
        return json.loads(data, object_pairs_hook=unique_pairs,
                          parse_float=no_number, parse_constant=no_number)
    except (ValueError, UnicodeError) as exc:
        raise Failure("invalid JSON: " + str(exc)) from exc


def is_int(value):
    return type(value) is int


def int_range(value, lower, upper, label):
    require(is_int(value) and lower <= value <= upper, "invalid " + label)
    return value


def authenticate(base):
    metadata = {}
    for name, expected in META.items():
        data = read_bytes(base / name)
        require(hashlib.sha256(data).hexdigest() == expected,
                "metadata SHA mismatch: " + name)
        metadata[name] = load(data)
    pins = metadata["SOURCE-PINS.json"]
    require(type(pins) is dict and type(pins.get("sources")) is list,
            "source manifest structure")
    require(len(pins["sources"]) == 8, "source object count")
    raw = {}
    for row in pins["sources"]:
        name = row["local_path"]
        require(type(name) is str and name.startswith("inputs/")
                and ".." not in Path(name).parts, "source path")
        require(name not in raw, "repeated source path")
        data = read_bytes(base / name)
        require(type(row["bytes"]) is int and len(data) == row["bytes"],
                "source size mismatch: " + name)
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source SHA mismatch: " + name)
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob mismatch: " + name)
        raw[name] = data
    return metadata, raw


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    if a == ZERO or b == ZERO:
        return ZERO
    if a[1] == 0:
        return (a[0] * b[0], a[0] * b[1])
    if b[1] == 0:
        return (a[0] * b[0], a[1] * b[0])
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def divide(a, b):
    require(b != ZERO, "division by zero")
    norm = b[0] * b[0] + b[1] * b[1]
    return ((a[0] * b[0] + a[1] * b[1]) / norm,
            (a[1] * b[0] - a[0] * b[1]) / norm)


def power(root, exponent):
    result = ONE
    for unused in range(exponent % 4):
        result = mul(result, root)
    return result


def rational(text, nonzero=False):
    require(type(text) is str, "rational must be a string")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise Failure("invalid rational string") from exc
    require(value.denominator & (value.denominator - 1) == 0,
            "nondyadic ordinary coefficient")
    require(not nonzero or value != 0, "zero SCALE")
    return (value, Fraction(0))


def identity(n):
    return [[ONE if row == col else ZERO for col in range(n)]
            for row in range(n)]


def scale_row(matrix, row, coefficient):
    matrix[row] = [mul(coefficient, value) for value in matrix[row]]


def shear(matrix, destination, source, coefficient):
    old_source = matrix[source]
    matrix[destination] = [add(a, mul(coefficient, b))
                           for a, b in zip(matrix[destination], old_source)]


def pair_components(positive, negative, q0):
    even, odd = [], []
    twice_q = mul((Fraction(2), Fraction(0)), q0)
    for left, right in zip(positive, negative):
        even.append([mul(add(a, b), (Fraction(1, 2), Fraction(0)))
                     for a, b in zip(left, right)])
        odd.append([divide(add(a, neg(b)), twice_q)
                    for a, b in zip(left, right)])
    return even, odd


def column_rank(matrix):
    """Incremental column-space basis; no row Gaussian-elimination routine."""
    n = len(matrix)
    basis = {}
    for column in range(n):
        vector = [matrix[row][column] for row in range(n)]
        for pivot in sorted(basis):
            factor = vector[pivot]
            if factor != ZERO:
                vector = [add(a, neg(mul(factor, b)))
                          for a, b in zip(vector, basis[pivot])]
        pivot = next((row for row, value in enumerate(vector)
                      if value != ZERO), None)
        if pivot is not None:
            divisor = vector[pivot]
            basis[pivot] = [divide(value, divisor) for value in vector]
    return len(basis)


def sector_matrices(matrices):
    return [pair_components(matrices[0], matrices[1], ONE),
            pair_components(matrices[2], matrices[3], IMAG)]


def ranks(matrices):
    return [column_rank(even) for even, unused in sector_matrices(matrices)]


def role(value, n):
    return int_range(value, 0, n - 1, "role")


def stages(values, count):
    require(type(values) is list and len(values) > 0, "stage list")
    for value in values:
        int_range(value, 1, count, "stage")


def instruction(event, n, count):
    require(type(event) is list and event and type(event[0]) is str,
            "instruction must be an array")
    name = event[0]
    arity = {"ADD": 4, "SCALE": 3, "SWAP": 3, "QUERY": 4,
             "LOCAL": 4, "IDLE": 4, "IDLE_ONE": 3,
             "LAMBDA": 3, "Q_POWER": 3}
    require(name in arity and len(event) == arity[name], "instruction shape")
    if name == "LOCAL":
        int_range(event[1], 1, count, "stage")
        source, destination = role(event[2], n), role(event[3], n)
        require(source != destination, "coincident LOCAL ports")
        return name, destination, source, -1, event[1]
    destination = role(event[1], n)
    if name in ("ADD", "SWAP", "QUERY", "IDLE"):
        source = role(event[2], n)
        require(source != destination, "coincident instruction ports")
    else:
        source = None
    if name == "ADD":
        rational(event[3])
    elif name == "SCALE":
        rational(event[2], nonzero=True)
    elif name == "QUERY":
        require(is_int(event[3]) and event[3] % 2 == 1,
                "QUERY must have an odd integral exponent")
    elif name == "IDLE":
        stages(event[3], count)
    elif name == "IDLE_ONE":
        stages(event[2], count)
    elif name == "LAMBDA":
        require(is_int(event[2]) and event[2] in (-1, 1), "LAMBDA sign")
    elif name == "Q_POWER":
        require(is_int(event[2]), "Q_POWER exponent")
        require(event[2] % 2 == 0, "odd_free_control")
    exponent = event[3] if name == "QUERY" else None
    return name, destination, source, exponent, None


def dispatch(matrix, root, event, info):
    name, destination, source, exponent, unused = info
    if name == "ADD":
        shear(matrix, destination, source, rational(event[3]))
    elif name == "SCALE":
        scale_row(matrix, destination, rational(event[2], nonzero=True))
    elif name == "SWAP":
        matrix[destination], matrix[source] = matrix[source], matrix[destination]
    elif name in ("QUERY", "LOCAL"):
        shear(matrix, destination, source, power(root, exponent))
    elif name == "LAMBDA":
        sign = event[2]
        first = (Fraction(1, 2), Fraction(sign, 2))
        second = (Fraction(1, 2), Fraction(-sign, 2))
        scale_row(matrix, destination, add(first, mul(second, power(root, 2))))
    elif name == "Q_POWER":
        scale_row(matrix, destination, power(root, event[2]))
    elif name not in ("IDLE", "IDLE_ONE"):
        raise Failure("unhandled instruction")


def replay(events, n, count, track):
    matrices = [identity(n) for unused in ROOTS]
    traces = [[], []]
    ordinal = 0
    for index, event in enumerate(events):
        info = instruction(event, n, count)
        paid = info[0] in ("QUERY", "LOCAL")
        before = ranks(matrices) if track and paid else None
        for matrix, root in zip(matrices, ROOTS):
            dispatch(matrix, root, event, info)
        if paid:
            ordinal += 1
        if track and paid:
            after = ranks(matrices)
            for sector in range(2):
                traces[sector].append({
                    "event_index": index, "ordinal": ordinal,
                    "opcode": info[0], "source": info[2],
                    "destination": info[1], "stage": info[4],
                    "exponent": info[3], "rank_before": before[sector],
                    "rank_after": after[sector],
                })
    return matrices, traces


def validate_controller(controller, contract):
    require(type(controller) is dict, "controller object")
    expected = contract["expect"]
    require(type(controller.get("roles")) is int
            and controller["roles"] == expected["roles"], "roles mismatch")
    require(type(controller.get("stages")) is int
            and controller["stages"] == expected["stages"], "stages mismatch")
    events, diagonal = controller.get("events"), controller.get("diagonal")
    require(type(events) is list and len(events) == expected["events"],
            "event count mismatch")
    require(type(diagonal) is list and len(diagonal) == controller["roles"],
            "declared diagonal shape")
    for vector in diagonal:
        require(type(vector) is list and len(vector) == 20
                and all(is_int(value) for value in vector), "monomial vector")
        require(vector[1] == 0, "nonzero dummy exponent")
    for event in events:
        instruction(event, controller["roles"], controller["stages"])


def endpoint(matrices, diagonal):
    n = len(diagonal)
    for matrix, root in zip(matrices, ROOTS):
        for row in range(n):
            for col in range(n):
                expected = power(root, diagonal[row][0]) if row == col else ZERO
                require(matrix[row][col] == expected, "endpoint_mismatch")


def encode(matrix):
    return [[[a.numerator, a.denominator, b.numerator, b.denominator]
             for a, b in row] for row in matrix]


def word_summary(controller, contract):
    counts = dict(Counter(event[0] for event in controller["events"]))
    odd = sum(vector[0] % 2 for vector in controller["diagonal"])
    result = {"roles": controller["roles"], "events": len(controller["events"]),
              "stages": controller["stages"], "native_queries": counts.get("LOCAL", 0),
              "thin_queries": counts.get("QUERY", 0),
              "total_queries": counts.get("LOCAL", 0) + counts.get("QUERY", 0),
              "odd_targets": odd, "even_targets": controller["roles"] - odd,
              "opcode_counts": counts}
    require(result == contract["expect"], "word inventory mismatch")
    return result


def sector_receipts(matrices, traces):
    receipts = []
    for index, (even, odd) in enumerate(sector_matrices(matrices)):
        trace = traces[index]
        require(trace and trace[0]["rank_before"] == 34, "initial rank")
        require(trace[0]["rank_after"] == 34, "first query changed even rank")
        for item in trace:
            require(item["rank_before"] - item["rank_after"] <= 1,
                    "odd shear rank-drop violation")
        final_rank = column_rank(even)
        require(final_rank == 2, "final even rank mismatch")
        receipts.append({"theta": 1 if index == 0 else -1,
                         "initial_even_rank": 34, "final_even_rank": final_rank,
                         "minimum_queries": 34 - final_rank + 1,
                         "even_final": encode(even), "odd_final": encode(odd),
                         "query_trace": trace})
    return receipts


def mutation(controller, case):
    events = copy.deepcopy(controller["events"])
    diagonal = copy.deepcopy(controller["diagonal"])
    if "delete_event" in case:
        del events[case["delete_event"]]
    elif "replace_event" in case:
        events[case["replace_event"]] = copy.deepcopy(case["value"])
    elif "insert_event" in case:
        events.insert(case["insert_event"], copy.deepcopy(case["value"]))
    elif "target_field" in case:
        diagonal[case["target_field"]][0] = case["target_q_exponent"]
    else:
        raise Failure("unrecognized control")
    return events, diagonal


def control_receipts(controller, cases):
    result = []
    for case in cases["controls"]:
        events, diagonal = mutation(controller, case)
        try:
            matrices, unused = replay(events, controller["roles"],
                                      controller["stages"], False)
            endpoint(matrices, diagonal)
        except Failure as exc:
            require(str(exc) == case["failure_gate"],
                    "control failed at unintended gate: " + case["id"])
            result.append({"id": case["id"], "accepted": False,
                           "failure_gate": str(exc)})
        else:
            raise Failure("control unexpectedly accepted: " + case["id"])
    return result


def produce(base):
    metadata, raw = authenticate(base)
    contract, cases = metadata["CONTRACT.json"], metadata["CASES.json"]
    controller = load(raw["inputs/CONTROLLER.json"])
    validate_controller(controller, contract)
    summary = word_summary(controller, contract)
    matrices, traces = replay(controller["events"], controller["roles"],
                              controller["stages"], True)
    endpoint(matrices, controller["diagonal"])
    return {"schema": contract["certificate"]["schema"],
            "sources": {"CONTROLLER.json": hashlib.sha256(
                raw["inputs/CONTROLLER.json"]).hexdigest()},
            "word": summary, "sectors": sector_receipts(matrices, traces),
            "controls": control_receipts(controller, cases)}


def same_types(actual, expected):
    require(type(actual) is type(expected), "certificate type mismatch")
    if type(expected) is dict:
        require(set(actual) == set(expected), "certificate key mismatch")
        for key in expected:
            same_types(actual[key], expected[key])
    elif type(expected) is list:
        require(len(actual) == len(expected), "certificate list length")
        for left, right in zip(actual, expected):
            same_types(left, right)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--certificate-out", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    base = here if (here / "CONTRACT.json").is_file() else here.parent
    result = produce(base)
    data = canonical(result)
    if args.certificate_out:
        args.certificate_out.write_bytes(data)
        print("PASS: emitted complete four-character certificate")
    else:
        path = args.check or (base / "ORACLE.json")
        incoming = read_bytes(path)
        same_types(load(incoming), result)
        require(incoming == data, "complete certificate byte mismatch")
        print("PASS: recomputed complete four-character certificate matches")


if __name__ == "__main__":
    try:
        main()
    except (Failure, OSError, KeyError, TypeError, IndexError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact source-only audit of the two swapped PR1862 charts.

No predecessor executable is imported. Native frames and routing are outside
this check. Default execution reads sources and compares the saved receipt.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
N, RANK = 112, 8
MAX_BYTES = 8 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [{i: Q(1)} for i in range(n)]


def add(a, b, scale=1):
    require(len(a) == len(b), "matrix row mismatch")
    result = [row.copy() for row in a]
    for target, source in zip(result, b):
        for j, value in source.items():
            updated = target.get(j, 0) + scale * value
            if updated:
                target[j] = updated
            else:
                target.pop(j, None)
    return result


def multiply(a, b):
    result = []
    for row in a:
        target = {}
        for k, value in row.items():
            for j, other in b[k].items():
                target[j] = target.get(j, 0) + value * other
        result.append({j: x for j, x in target.items() if x})
    return result


def scaled(a, scale):
    return [{j: scale * x for j, x in row.items() if scale * x} for row in a]


def transpose(a, columns):
    return [{i: row[j] for i, row in enumerate(a) if j in row}
            for j in range(columns)]


def selected(a, ports):
    return [{j: x for j, x in row.items() if j in ports} for row in a]


def load_sources(archive_path):
    pins = json.loads((HERE / "ARCHIVE.json").read_text(encoding="utf-8"))
    require(archive_path.stat().st_size <= MAX_BYTES, "archive size limit")
    require(sha256(archive_path.read_bytes()).hexdigest() == pins["sha256"],
            "archive pin mismatch")
    objects = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        require(len(members) <= 2000, "archive member limit")
        for name, pin in pins["members"].items():
            matches = [m for m in members if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "member ambiguity")
            member = matches[0]
            require(member.size <= MAX_BYTES, "member size limit")
            stream = archive.extractfile(member)
            require(stream is not None, "missing member stream")
            with stream:
                raw = stream.read(MAX_BYTES + 1)
            require(len(raw) == member.size, "partial member read")
            require(sha256(raw).hexdigest() == pin["sha256"], "member pin mismatch")
            payload = gzip.decompress(raw)
            require(len(payload) <= MAX_BYTES, "payload size limit")
            require(sha256(payload).hexdigest() == pin["payload_sha256"],
                    "payload pin mismatch")
            objects[Path(name).name] = json.loads(payload)
    return objects


def extract_query(word, program):
    """Propagate only the 112 source columns to the unique centre cut."""
    require((word["v"], word["R"], word["h"]) == (112, 480, 9), "geometry")
    require(len(program) <= 30000, "program event limit")
    cut = ["phase", "centers"]
    require(program.count(cut) == 1, "ambiguous centre cut")
    require(len(word["centers"]) == 8 and len(set(word["centers"])) == 8,
            "centre register count")
    rows = identity(N) + [{} for _ in range(712 - N)]
    for event in program[:program.index(cut)]:
        if event[0] != "scalar":
            continue
        op = event[1]
        target = register(op[1])
        if op[0] == "clear":
            rows[target] = {}
        elif op[0] == "copy":
            rows[target] = rows[register(op[2])].copy()
        elif op[0] == "scale":
            rows[target] = scaled([rows[target]], Q(op[2], op[3]))[0]
        else:
            require(op[0] == "add", "unknown scalar operation")
            rows[target] = add([rows[target]], [rows[register(op[2])]],
                               Q(op[3], op[4]))[0]
    return [rows[c] for c in word["centers"]]


def register(port):
    kind, index = port
    require(type(index) is int, "register index type")
    require((kind == "L" and 0 <= index < 704) or
            (kind == "C" and 0 <= index < 8), "register bounds")
    return index + (704 if kind == "C" else 0)


def chart(R, K, P, L):
    unit = identity(RANK)
    require(multiply(R, P) == unit, "RP != I")
    require(multiply(L, K) == unit, "LK != I")
    require(not any(multiply(L, P)), "LP != 0")
    Z = add(K, multiply(P, add(multiply(R, K), unit, -1)), -1)
    query = add(R, L, -1)
    G = add(add(identity(N), multiply(Z, query)), multiply(P, R), -1)
    require(not any(multiply(query, Z)), "QZ != 0")
    return {"G": G, "P": P, "L": L, "Z": Z, "Q": query}


def apply_factors(code, vector):
    """Separate column oracle: apply I+ZQ, then I-PL, in that order."""
    query = [sum(x * vector[j] for j, x in row.items()) for row in code["Q"]]
    middle = [value + sum(x * query[j] for j, x in row.items())
              for value, row in zip(vector, code["Z"])]
    logged = [sum(x * middle[j] for j, x in row.items()) for row in code["L"]]
    return [value - sum(x * logged[j] for j, x in row.items())
            for value, row in zip(middle, code["P"])]


def small_action(swapped=False):
    dense = [[-12, -1, -156], [1, 1, 12], [1, 0, 13]]
    if swapped:
        dense = [[1, 1, 12], [-1, -12, -156], [0, 1, 13]]
    return [{j: Q(x) for j, x in enumerate(row) if x} for row in dense]


def lift(a):
    """Three sections, each containing the same eight query coordinates."""
    return [{RANK * j + k: x for j, x in row.items()}
            for row in a for k in range(RANK)]


def determinant3(a):
    x = [[row.get(j, 0) for j in range(3)] for row in a]
    return (x[0][0] * (x[1][1]*x[2][2] - x[1][2]*x[2][1])
            - x[0][1] * (x[1][0]*x[2][2] - x[1][2]*x[2][0])
            + x[0][2] * (x[1][0]*x[2][1] - x[1][1]*x[2][0]))


def polynomial3(a):
    trace = sum(row.get(i, 0) for i, row in enumerate(a))
    square = multiply(a, a)
    second = (trace**2 - sum(row.get(i, 0) for i, row in enumerate(square))) / 2
    return [-determinant3(a), second, -trace, Q(1)]


def evaluate(coefficients, x):
    value = Q(0)
    for coefficient in reversed(coefficients):
        value = value * x + coefficient
    return value


def verify_actions(codes, E, left):
    require(multiply(left, E) == identity(24), "active sections dependent")
    projection = multiply(E, left)
    fixed = add(identity(N), projection, -1)
    for code, action in zip(codes, (small_action(), small_action(True))):
        require(multiply(code["G"], E) == multiply(E, lift(action)), "active action")
        require(multiply(code["G"], fixed) == fixed, "fixed complement")
        power = identity(3)
        for exponent in range(1, 7):
            power = multiply(action, power)
            require((power == identity(3)) == (exponent == 6), "fixed-chart order")
    product = multiply(codes[1]["G"], codes[0]["G"])
    for j in range(N):
        vector = [Q(i == j) for i in range(N)]
        first = apply_factors(codes[0], vector)
        second = apply_factors(codes[1], vector)
        require(first == [row.get(j, 0) for row in codes[0]["G"]], "first oracle")
        require(second == [row.get(j, 0) for row in codes[1]["G"]], "second oracle")
        both = apply_factors(codes[1], first)
        require(both == [row.get(j, 0) for row in product], "product oracle")
    require(sum(row.get(i, 0) for i, row in enumerate(product)) == 1456,
            "full product trace")


def controls(R, K, codes, E, left):
    bad = [row.copy() for row in codes[0]["P"]]
    bad[A[0]] = {}
    try:
        chart(R, K, bad, codes[0]["L"])
    except ValueError as error:
        require(str(error) == "RP != I", "wrong malformed-minor rejection")
    else:
        raise ValueError("malformed minor accepted")
    try:
        chart(R, K, codes[0]["P"], selected(R, A))
    except ValueError as error:
        require(str(error) == "LP != 0", "wrong overlap rejection")
    else:
        raise ValueError("overlapping chart accepted")
    broken = [row.copy() for row in E]
    broken[A[0]].clear()
    require(multiply(left, broken) != identity(24), "basis corruption undetected")
    wrong = small_action(True)
    wrong[0][2] = Q(11)
    require(multiply(codes[1]["G"], E) != multiply(E, lift(wrong)),
            "action corruption undetected")
    same = multiply(small_action(), small_action())
    require(polynomial3(same) == [-1, 0, 0, 1], "same-chart positive control")
    require(multiply(multiply(same, same), same) == identity(3), "same-chart return")


def run(archive_path):
    data = load_sources(archive_path)
    R = extract_query(data["CANONICAL-WORD.json.gz"],
                      data["LOCAL-PROGRAMS.json.gz"]["forward"])
    K = scaled(transpose(R, N), Q(1, 4))
    require(multiply(R, K) == scaled(identity(RANK), 14), "RK != 14I")
    P = [row.copy() if i in A else {} for i, row in enumerate(K)]
    S = [row.copy() if i in T else {} for i, row in enumerate(K)]
    LA, LT = selected(R, A), selected(R, T)
    codes = (chart(R, K, P, LT), chart(R, K, S, LA))
    U = add(add(K, P, -1), S, -1)
    E = [{**p, **{8+j: x for j, x in s.items()}, **{16+j: x for j, x in u.items()}}
         for p, s, u in zip(P, S, U)]
    left = LA + LT + scaled(add(add(R, LA, -1), LT, -1), Q(1, 12))
    verify_actions(codes, E, left)
    controls(R, K, codes, E, left)
    pair = multiply(small_action(True), small_action())
    coefficients = polynomial3(pair)
    require(coefficients == [-1, 27, -171, 1], "pair characteristic polynomial")
    signs = [evaluate(coefficients, x) for x in (170, 171)]
    require(signs == [-24311, 4616], "root bracket")
    serial_R = [[str(row.get(j, 0)) for j in range(N)] for row in R]
    return {
        "status": "PASS_SOURCE_CODE_CHART_ORDER",
        "query_sha256": sha256(json.dumps(serial_R, separators=(",", ":")).encode()).hexdigest(),
        "ports": N, "query_rank": RANK, "A": list(A), "T": list(T),
        "individual_chart_order": 6, "pair_fixed_dimension": 88,
        "pair_active_dimension": 24,
        "pair_action": [[str(row.get(j, 0)) for j in range(3)] for row in pair],
        "pair_characteristic_polynomial_low_to_high": [int(x) for x in coefficients],
        "full_characteristic_polynomial": "(t-1)^88 * (t^3-171*t^2+27*t-1)^8",
        "pair_trace": 1456, "pair_order": "infinite over Q and Q(i)",
        "real_eigenvalue_interval": [170, 171], "polynomial_at_endpoints": [int(x) for x in signs],
        "column_oracle_cases": 336, "semantic_failure_controls": 4,
        "same_chart_pair_order": 3,
        "scope": "Source-only port algebra, not native chart transport or a complete supplier.",
        "selected_frontier_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path,
                        default=ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz")
    parser.add_argument("--write", action="store_true", help="regenerate this package's receipt")
    args = parser.parse_args()
    result = run(args.archive)
    receipt = HERE / "RESULT.json"
    if args.write:
        raw = json.dumps(result, indent=2) + "\n"
        require(receipt.write_text(raw, encoding="utf-8") == len(raw), "partial receipt write")
    else:
        require(json.loads(receipt.read_text(encoding="utf-8")) == result, "receipt mismatch")
    print("PASS_SOURCE_CODE_CHART_ORDER orders=6,6,infinite trace=1456 eigenvalue=170..171 columns=336 controls=4 no_new_kappa")


if __name__ == "__main__":
    main()

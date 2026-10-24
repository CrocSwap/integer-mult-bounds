"""Check constant centre codes for both actual response families."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "rank30": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "rank16": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    ),
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    answer = [[F(0)] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                answer[i] = [x + value * y for x, y in zip(answer[i], b[k])]
    return answer


def inverse(a):
    n = len(a)
    rows = [row[:] + unit for row, unit in zip(a, identity(n))]
    for j in range(n):
        pivot = next((k for k in range(j, n) if rows[k][j]), None)
        need(pivot is not None, "Constant code is a rational unit")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        value = rows[j][j]
        rows[j] = [x / value for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                value = rows[i][j]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def dense(rows, columns):
    return [[F(row.get(str(j), 0)) for j in range(columns)] for row in rows]


def invert_word(word):
    result = []
    for gate in reversed(word):
        kind = gate[0]
        if kind == "ADD":
            result.append(gate[:3] + [-gate[3]])
        elif kind == "SCALE2":
            result.append(gate[:2] + [-gate[2]])
        elif kind in {"MULTIPLY_ODD", "DIVIDE_ODD"}:
            result.append(["DIVIDE_ODD" if kind == "MULTIPLY_ODD" else "MULTIPLY_ODD"] + gate[1:])
        else:
            need(kind == "NEG", "Invertible constant gate")
            result.append(gate[:])
    return result


def diagonal_word(target, value):
    need(value.denominator == 1 and value, "Nonzero integer diagonal")
    value = int(value)
    out = []
    positive = abs(value)
    while positive % 2 == 0:
        out.append(["SCALE2", target, 1])
        positive //= 2
    if positive != 1:
        out.append(["MULTIPLY_ODD", target, positive])
    if value < 0:
        out.append(["NEG", target])
    return out


def apply(rows, gate):
    kind, target = gate[:2]
    if kind == "ADD":
        source, sign = gate[2:]
        rows[target] = [x + sign * y for x, y in zip(rows[target], rows[source])]
    elif kind == "NEG":
        rows[target] = [-x for x in rows[target]]
    else:
        factor = F(2) ** gate[2] if kind == "SCALE2" else F(gate[2])
        if kind == "DIVIDE_ODD":
            factor = 1 / factor
        need(kind in {"SCALE2", "MULTIPLY_ODD", "DIVIDE_ODD"}, "Known constant gate")
        rows[target] = [factor * x for x in rows[target]]


def denominator_height(x, p):
    denominator, h = x.denominator, 0
    while denominator % p == 0:
        denominator //= p
        h += 1
    return h


def replay(word, n, initial=None, valid=False):
    state = identity(n + 2)
    if initial is not None:
        state[:n] = [row[:] + [F(0), F(0)] for row in initial]
    bound = max(sum(abs(x) for x in row) for row in state)
    levels = {p: 0 for p in (2, 3, 5, 7)}
    for gate in word:
        kind, target = gate[:2]
        need(0 <= target < n, "Only centre data are written")
        if kind == "ADD":
            need(0 <= gate[2] < n and gate[2] != target and gate[3] in (-1, 1),
                 "Literal unit ADD within the centre")
        if kind == "DIVIDE_ODD" and valid:
            need(all(x.denominator % gate[2] and x.numerator % gate[2] == 0
                     for x in state[target]), "Exact valid-code quotient")
        apply(state, gate)
        bound = max(bound, sum(abs(x) for x in state[target]))
        for p in levels:
            levels[p] = max(levels[p], max(denominator_height(x, p) for x in state[target]))
    need(state[n:] == identity(n + 2)[n:], "Arbitrary spectators remain identity")
    need(all(row[n:] == [0, 0] for row in state[:n]), "No spectator baseline enters a centre")
    return [row[:n] for row in state[:n]], {"max_prefix_row_l1": str(bound), "denominator_heights": levels}


def invoice(word):
    counts = Counter(g[0] for g in word)
    scans = Counter((g[0], g[2]) for g in word if g[0] in {"MULTIPLY_ODD", "DIVIDE_ODD"})
    return {"old_real_scalar_units": 8 * counts["ADD"] + 2 * (counts["SCALE2"] + counts["NEG"]),
            "gate_counts": dict(sorted(counts.items())),
            "real_fixed_odd_scans": {kind + "_" + str(p): 2 * count for (kind, p), count in sorted(scans.items())},
            "native_children": 0, "owned_fields": 0, "maps_inside_common_chart": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    records, pins = {}, {}
    for name, (path, digest) in PINS.items():
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == digest, "Source pin " + name)
        model = json.loads(raw)
        model = model.get("model", model)
        pins[name] = {"path": str(path), "payload_sha256": digest}
        n = len(model["correction_V"])
        u = dense(model["correction_U"], n)
        v = dense(model["correction_V"], 112)
        b0 = product(v, u)
        g0 = [[x + F(i == j) for j, x in enumerate(row)] for i, row in enumerate(b0)]
        e = [[x + F(i == j) for j, x in enumerate(row)] for i, row in enumerate(product(u, v))]
        need(e == dense(model["response"], 112), "Actual full response is I+UV")
        words = {"B0": [], "G0": []}
        if n == 30:
            for x in range(0, 16, 2):
                y = x + 1
                need([[b0[i][j] for j in (x, y)] for i in (x, y)] == [[-4, 1], [2, -2]],
                     "Actual large B0 block")
                words["B0"] += [["ADD", y, x, -1], ["MULTIPLY_ODD", x, 3],
                                ["ADD", x, y, -1], ["SCALE2", y, 1], ["NEG", x], ["NEG", y]]
                words["G0"] += [["SCALE2", x, 1], ["ADD", y, x, -1], ["SCALE2", x, -1],
                                ["ADD", x, y, -1], ["NEG", x], ["NEG", y]]
            first_diagonal = 16
        else:
            need(n == 16 and [b0[i][i] for i in range(n)] == [-6] * 8 + [-8] * 8,
                 "Actual rank-sixteen B0 diagonal")
            first_diagonal = 0
        for target in range(first_diagonal, n):
            need(all(not b0[target][j] for j in range(n) if j != target), "Separate scalar block")
            words["B0"] += diagonal_word(target, b0[target][target])
            words["G0"] += diagonal_word(target, g0[target][target])
        checks = {}
        for label, target in (("B0", b0), ("G0", g0)):
            inv = inverse(target)
            words[label + "_inverse"] = invert_word(words[label])
            for suffix, expected in (("", target), ("_inverse", inv)):
                key = label + suffix
                actual, bounds = replay(words[key], n)
                need(actual == expected, "All exact constant-code columns")
                checks[key] = {"invoice": invoice(words[key]), "prefix_bounds": bounds}
            need(product(target, inv) == product(inv, target) == identity(n), "Both inverse orders")
            actual, bounds = replay(words[label + "_inverse"], n, target, True)
            need(actual == identity(n), "Valid-code decode")
            checks[label + "_inverse"]["valid_code_bounds"] = bounds
        records[name] = {"dimension": n, "B0": [[str(x) for x in row] for row in b0],
                         "G0": [[str(x) for x in row] for row in g0], "words": words, "checks": checks}
    payload = {"source_pins": pins, "families": records}
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (args.out / "CENTRE-CONSTANTS.json").write_bytes(raw)
    receipt = {"status": "PASS_ACTUAL_CENTRE_CONSTANT_CODES",
               "payload_sha256": sha256(raw).hexdigest(), "source_pins": pins,
               "families": {name: row["checks"] for name, row in records.items()},
               "scope": "Common-chart constant centre operations only. No physical source, views, ownership, or terminal is supplied."}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps(receipt["families"], sort_keys=True))


if __name__ == "__main__":
    main()

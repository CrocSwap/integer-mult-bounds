"""Independent exact readout-first check on the eight frozen R74 banks."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import argparse
import gzip
import json

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "banks": "9b17806949c347926b7f95bb70d207e89ca3ed1c6cf78f6729652b3728993c01",
    "g68": "ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76",
    "g69": "a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45",
    "admission": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "word": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
CASE_CAP, TIME_CAP = 8, 15


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path, name):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == PINS[name], "changed input " + name)
    return raw


def adjoint(body, roles, output):
    functional = {r: Q(r == output) for r in roles}
    for event in reversed(body):
        op, dst = event[:2]
        if op == "ADD":
            functional[event[2]] += Q(event[3]) * functional[dst]
        else:
            require(op == "SCALE", "invalid component operation")
            functional[dst] *= Q(event[2])
    return functional


def forward(body, roles, input_role):
    vector = {r: Q(r == input_role) for r in roles}
    for event in body:
        op, dst = event[:2]
        if op == "ADD":
            vector[dst] += Q(event[3]) * vector[event[2]]
        else:
            require(op == "SCALE", "invalid component operation")
            vector[dst] *= Q(event[2])
    return vector


def readout(body, roles, h, q):
    want = adjoint(body, roles, h)
    donor = adjoint(body, roles, q)
    exterior = [r for r in roles if r != h]
    pivot = next((r for r in exterior if donor[r]), None)
    if pivot is None:
        missing = next((r for r in exterior if want[r]), None)
        if missing is not None:
            return None, {"missing_donor_coordinate": missing, "required_value": str(want[missing])}
        beta = Q(0)
    else:
        beta = want[pivot] / donor[pivot]
        for r in exterior:
            minor = want[r] * donor[pivot] - donor[r] * want[pivot]
            if minor:
                return None, {"exterior_coordinates": [pivot, r], "determinant": str(minor)}
    alpha = want[h] - beta * donor[h]
    require(alpha, "invertible block returned zero dirty-readout multiplier")
    require(all(want[r] == alpha * (r == h) + beta * donor[r] for r in roles), "invalid readout coefficient")
    return (alpha, beta), None


def solve_rectangular(rows, n):
    matrix = [row.copy() for row in rows]
    pivots = []
    for column in range(n):
        first = len(pivots)
        pivot = next((i for i in range(first, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[first], matrix[pivot] = matrix[pivot], matrix[first]
        v = matrix[first][column]
        matrix[first] = [x / v for x in matrix[first]]
        for i, row in enumerate(matrix):
            if i != first and row[column]:
                v = row[column]
                matrix[i] = [x - v * y for x, y in zip(row, matrix[first], strict=True)]
        pivots.append(column)
    obstruction = next((row for row in matrix if not any(row[:-1]) and row[-1]), None)
    if obstruction is not None:
        return None, len(pivots)
    result = [Q(0)] * n
    for i, col in enumerate(pivots):
        result[col] = matrix[i][-1]
    require(all(sum(x * y for x, y in zip(row[:-1], result, strict=True)) == row[-1] for row in rows),
            "forward witness does not solve exact equations")
    return result, len(pivots)


def forward_gate(body, roles, h, low, q):
    cols = {r: forward(body, roles, r) for r in [h, *low]}
    exterior = [r for r in roles if r not in (h, q)]
    equations = [[*(cols[p][i] for p in low), -cols[h][i]] for i in exterior]
    answer, rank = solve_rectangular(equations, len(low))
    if answer is None:
        return None, rank
    combined = {i: cols[h][i] + sum(a * cols[p][i] for a, p in zip(answer, low, strict=True)) for i in roles}
    require(all(not combined[i] for i in exterior), "forward output has exterior leakage")
    coeff = {p: str(a) for p, a in zip(low, answer, strict=True) if a}
    return {"low_coefficients": coeff, "high_correction": str(combined[q]), "owned_residual": str(combined[h])}, rank


def controls():
    h, a, b, q, other = range(5)
    roles = [h, a, b, q, other]
    events = [
        ["ADD", a, h, "-2", 7],
        ["ADD", b, h, "1/2", 7],
        ["ADD", q, h, "-3", 7],
        ["SCALE", h, "-2", 7],
        ["ADD", h, q, "1", 7],
    ]
    coefficients, failure = readout(events, roles, h, q)
    require(coefficients == (Q(-2), Q(1)) and failure is None, "signed readout control")
    found, rank = forward_gate(events, roles, h, [a, b], q)
    require(found == {"low_coefficients": {a: "2", b: "-1/2"}, "high_correction": "-3",
                      "owned_residual": "-5"} and rank == 2, "two-low forward control")
    require(forward_gate(events, roles, h, [a], q)[0] is None, "single donor accepted")
    require(forward_gate(events + [["ADD", other, h, "1", 7]], roles, h, [a, b], q)[0] is None,
            "extra exterior defect accepted")
    _, rejection = readout(events + [["ADD", h, a, "1", 7]], roles, h, q)
    require(rejection and "determinant" in rejection, "exterior readout corruption accepted")
    return ["signed nonunit readout", "two low coefficients required", "extra exterior defect rejected",
            "corrupted dirty readout rejected"]


def verify(args):
    control = controls()
    bank = json.loads(read(args.banks, "banks"))
    geos = [json.loads(read(getattr(args, n), n)) for n in ("g68", "g69")]
    admission = json.loads(read(args.admission, "admission"))
    require(bank["head"] == admission["head"] == HEAD and admission["exit"] == 0, "wrong admission")
    sites = {s["key"]: s for g in geos for s in g["survivors"] if len(s["low"]) > 1}
    pending = bank["rows"]
    require(len(sites) == len(pending) == len({x["key"] for x in pending}) == CASE_CAP, "wrong exact bank count")
    require(set(sites) == {x["key"] for x in pending}, "different eligible low bank keys")
    start = monotonic()
    word = json.loads(gzip.decompress(read(args.word, "word")))["program"]
    done, survivors = [], []
    for selected in pending:
        if len(done) == CASE_CAP or monotonic() - start >= TIME_CAP:
            break
        site = sites[selected["key"]]
        h, roles, low, high = (site[k] for k in ("h", "roles", "low", "high"))
        require((h, low, high, site["clock"], site["chart_path"]) ==
                (selected["h"], selected["low"], selected["high"], selected["cut"], selected["chart_path"]),
                "unmatched frozen geometry detail")
        require(len(high) == 1 and 2 <= len(low) <= 4 and h not in low + high, "unexpected role stock")
        q = high[0]
        body = [word[t] for t in site["block"]]
        require(all(e[-1] == site["chart_path"][1] for e in body), "wrong component chart")
        coefficients, obstruction = readout(body, roles, h, q)
        result = {"key": selected["key"], "h": h, "rank_type": selected["rank_type"], "readout_peer": q}
        if coefficients is None:
            done.append(result | {"status": "readout_excluded", "certificate": obstruction})
            continue
        require(not selected["prior_readout_excluded"], "prior readout result disagrees")
        support, rank = forward_gate(body, roles, h, low, q)
        if support is None:
            done.append(result | {"status": "forward_span_excluded", "exterior_donor_rank": rank,
                                  "exterior_augmented_rank": rank + 1})
            continue
        require(len(support["low_coefficients"]) >= 2, "contradiction to one-low exclusion")
        alpha, beta = coefficients
        winner = result | {"status": "rational_support_survives", "alpha": str(alpha), "beta": str(beta), **support}
        done.append(winner)
        survivors.append(winner)
    unvisited = [x["key"] for x in pending[len(done):]]
    return {"head": HEAD, "input_sha256": PINS, "status": "CAPPED" if unvisited else "EXHAUSTED",
            "case_cap": CASE_CAP, "runner_cap_seconds": TIME_CAP, "controls": control, "tested": len(done),
            "counts": dict(Counter(row["status"] for row in done)), "outcomes": done,
            "unvisited": unvisited, "survivors": survivors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--controls-only", action="store_true")
    for name in PINS:
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    result = {"status": "PASS", "controls": controls()} if args.controls_only else verify(args)
    print(json.dumps(result, indent=2, sort_keys=True))

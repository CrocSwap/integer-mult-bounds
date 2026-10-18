#!/usr/bin/env python3
"""Exact rational controls for the ordered paired-log controller decoder.

Copyright 2026 Jose Manuel (@jmbarrancoml). Apache-2.0.
Prepared with substantial OpenAI Codex assistance; see README.md for credit.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from random import Random
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
RECIPE = "research/community-reconciliation-third100-audit/regenerated/pr377-outputs/work/odd-stages/RECIPE-9.json.gz"
RECIPE_HASH = "910fffd7b8980f1130d8bbec56d5ac34f92986c2a2c480b6aea40754b4b832ac"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def combine(*terms):
    result = [{} for _ in terms[0][1]]
    for scalar, matrix in terms:
        for row, source in zip(result, matrix):
            for j, value in source.items():
                row[j] = row.get(j, Q(0)) + scalar * value
                if not row[j]:
                    del row[j]
    return result


def multiply(left, right):
    return [combine(*[(value, [right[j]]) for j, value in row.items()])[0] if row else {}
            for row in left]


def rank(rows):
    pivots = {}
    for original in rows:
        row = original.copy()
        while row:
            j = min(row)
            if j not in pivots:
                pivots[j] = {k: x / row[j] for k, x in row.items()}
                break
            row = combine((1, [row]), (-row[j], [pivots[j]]))[0]
    return len(pivots)


def validate_chart(chart):
    R, P, Z = chart
    eye = [{i: Q(1)} for i in range(len(R))]
    require(multiply(R, P) == multiply(R, Z) == eye, "right-inverse hypotheses")


def make_chart(rng, n, r):
    selected = rng.sample(range(n), r)
    others = [i for i in range(n) if i not in selected]
    R = [{p: Q(1), **{j: Q(rng.choice((-2, -1, 1, 2))) for j in others}} for p in selected]
    P, Z = [{} for _ in range(n)], [{} for _ in range(n)]
    for k, p in enumerate(selected):
        P[p] = {k: Q(1)}
    for j in others:
        Z[j] = {k: Q(value) for k in range(r) if (value := rng.randint(-2, 2))}
    for k, p in enumerate(selected):
        z = {k: Q(1)}
        for j in others:
            z = combine((1, [z]), (-R[k][j], [Z[j]]))[0]
        Z[p] = z
    chart = (R, P, Z)
    validate_chart(chart)
    return chart


def run_word(x, y, logs, charts, recipe, wrong_inverse=False):
    x, y, logs = list(x), list(y), list(logs)
    for event in recipe:
        if event["kind"] == "terminal":
            continue  # The theorem and decoder use banks before signed exchange.
        if event["kind"] == "bridge":
            dst, src, c = event["dst"], event["src"], event["coefficient"]
            x[dst] = combine((1, x[dst]), (c, x[src]))
            y[src] = combine((1, y[src]), (-c, y[dst]))
            continue
        require(event["kind"] == "local", "unknown controller event")
        s, j = event["stage"], event["pair"]
        R, P, Z = charts[s]
        forward = not event["reverse"]
        source = x[j] if forward else y[j]
        query = multiply(R, source)
        if forward:
            x[j] = combine((1, source), (-1, multiply(Z, query)), (1, multiply(P, logs[s])))
            y[j] = combine((1, y[j]), (1, x[j]))
        else:
            x[j] = combine((1, x[j]), (-1, source))
            left, right = (Z, P) if wrong_inverse else (P, Z)
            y[j] = combine((1, source), (-1, multiply(left, query)), (1, multiply(right, logs[s])))
        logs[s] = query
    return x, y, logs


def decode(x, y, logs, charts, query_b=None, query_f=None):
    n = len(x[0])
    zero = [{} for _ in range(n)]
    if query_b is None:
        query_b = [multiply(charts[2 * j + 1][0], y[j]) for j in range(4)]
    if query_f is None:
        query_f = [multiply(charts[2 * j][0], y[j]) for j in range(4)]
    c = [x[0]]
    for j in range(1, 4):
        c.append(combine((1, x[j]), (-1, c[j - 1])))
    eta = [None] * 9
    eta[8] = multiply(charts[8][0], c[3])
    d_next = c[3]
    restored_x, restored_y = [None] * 4, [None] * 4
    for j in (3, 2, 1, 0):
        f, b = 2 * j + 2, 2 * j + 1
        previous = c[j - 1] if j else zero
        restored_y[j] = combine((-1, previous), (-1, c[j]),
                                (-1, multiply(charts[f][2], logs[f])),
                                (1, multiply(charts[f][1], eta[f])))
        eta[b] = combine((1, query_b[j]), (-1, multiply(charts[b][0], d_next)))
        d = combine((-1, d_next), (1, multiply(charts[b][1], logs[b])),
                    (-1, multiply(charts[b][2], eta[b])), (-1, restored_y[j]))
        eta[2 * j] = combine((1, query_f[j]), (1, multiply(charts[2 * j][0], d)))
        restored_x[j] = combine((1, y[j]), (1, d), (-1, previous)) if j else combine(
            (1, y[0]), (1, d), (-1, multiply(charts[0][1], eta[0])),
            (1, multiply(charts[0][2], logs[0])))
        d_next = d
    return restored_x, restored_y, eta


def fixture(seed, mode, recipe, n=5, r=2):
    rng = Random(seed)
    charts = [make_chart(rng, n, r) for _ in range(9)]
    if mode == "common":
        charts = [charts[0]] * 9
    elif mode == "mixed":
        charts[1], charts[3] = charts[0], charts[2]
    size = 8 * n + 9 * r
    eye = [{i: Q(1)} for i in range(size)]
    x0 = [eye[2 * j * n:(2 * j + 1) * n] for j in range(4)]
    y0 = [eye[(2 * j + 1) * n:(2 * j + 2) * n] for j in range(4)]
    z0 = [eye[8 * n + s * r:8 * n + (s + 1) * r] for s in range(9)]
    x, y, logs = run_word(x0, y0, z0, charts, recipe)
    require(decode(x, y, logs, charts) == (x0, y0, z0), "all-column restoration")
    hidden = [8 * n + s * r + k for s in (1, 3, 5, 7) for k in range(r)]
    require(all(not row.get(k) for bank in x + logs for row in bank for k in hidden), "hidden backward logs")
    # Final Y ranges freely when final X/logs are fixed, since the word is invertible.
    hard_y = [[{j * n + p: Q(1)} for p in range(n)] for j in range(4)]
    zero_x = [[{} for _ in range(n)] for _ in range(4)]
    zero_logs = [[{} for _ in range(r)] for _ in range(9)]
    eta = decode(zero_x, hard_y, zero_logs, charts)[2]
    query_rows = [row for j in range(4) for s in (2 * j, 2 * j + 1)
                  for row in multiply(charts[s][0], hard_y[j])]
    eta_rows = [row for bank in eta for row in bank]
    query_rank = rank(query_rows)
    require(rank(eta_rows) == rank(eta_rows + query_rows) == query_rank, "observation row space")
    deltas = []
    for j in range(4):
        Rf, _, _ = charts[2 * j]
        Rb, _, Zb = charts[2 * j + 1]
        residual = combine((1, Rf), (-1, multiply(multiply(Rf, Zb), Rb)))
        deltas.append(rank(residual))
    require(query_rank == 4 * r + sum(deltas), "query dimension formula")
    require(4 * r <= query_rank <= 8 * r, "dimension bounds")
    # These corruptions attack distinct obligations rather than numerical precision.
    wrong_queries = [[{} for _ in range(r)] for _ in range(4)]
    require(decode(x, y, logs, charts, query_b=wrong_queries) != (x0, y0, z0), "missing Y-query control")
    require(decode(x, y, zero_logs, charts) != (x0, y0, z0), "discarded log control")
    missing_bridge = [e for i, e in enumerate(recipe) if i != 2]
    bad = run_word(x0, y0, z0, charts, missing_bridge)
    require(decode(*bad, charts) != (x0, y0, z0), "missing bridge control")
    bad = run_word(x0, y0, z0, charts, recipe, wrong_inverse=True)
    require(decode(*bad, charts) != (x0, y0, z0), "wrong source inverse control")
    bad_R, bad_P, bad_Z = charts[0]
    bad_Z = [row.copy() for row in bad_Z]
    bad_Z[0] = combine((1, [bad_Z[0]]), (1, [{0: Q(1)}]))[0]
    try:
        validate_chart((bad_R, bad_P, bad_Z))
    except ValueError:
        pass
    else:
        raise ValueError("missing right-inverse hypothesis survived")
    a, b = multiply(charts[0][0], charts[1][1]), multiply(charts[2][0], charts[3][2])
    noncommuting = multiply(a, b) != multiply(b, a)
    if mode == "varied":
        require(noncommuting, "varied fixture lacks noncommutativity")
    return dict(seed=seed, mode=mode, input_columns=size, query_rank=query_rank,
                residual_ranks=deltas, noncommuting=noncommuting, rejected_controls=5)


def main():
    raw = (ROOT / RECIPE).read_bytes()
    require(sha256(raw).hexdigest() == RECIPE_HASH, "controller source drift")
    recipe = json.loads(gzip.decompress(raw))
    require(len(recipe) == 19 and recipe[-1] == {"kind": "terminal", "pairs": 4}, "controller boundary")
    results = [fixture(71, "common", recipe), fixture(17, "mixed", recipe)]
    results += [fixture(seed, "varied", recipe) for seed in (17, 29, 43)]
    require(results[0]["query_rank"] == 8 and all(r["query_rank"] == 16 for r in results[2:]), "sharpness fixtures")
    require(8 < results[1]["query_rank"] < 16, "intermediate fixture")
    print(json.dumps(dict(fixtures=results, exact_input_columns=sum(r["input_columns"] for r in results),
                         scope="Ordered algebra and finite field-linear observation spaces; no native acquisition or exponent certificate."), sort_keys=True))
    print("PASS_PAIRED_LOG_ORDERED_DECODER")


if __name__ == "__main__":
    main()

"""Exact DAG-cut controls for the forward macro-prefix proof; no all-size enumeration."""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "retained_matrix_helpers", ROOT / "research/q-toeplitz-factorization/verify.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load retained matrix helpers")
HELPERS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPERS)
eye, mul, toeplitz = HELPERS.identity, HELPERS.multiply, HELPERS.toeplitz


def need(ok, message):
    if not ok:
        raise ValueError(message)


def norm(a):
    return max(sum(map(abs, row)) for row in a)


def divide(a, b):
    need(b[0] == 1, "unit denominator required")
    q = []
    for i, value in enumerate(a):
        q.append(value - sum(b[j] * q[i-j] for j in range(1, i+1)))
    return q


def inverse(a):
    n = len(a)
    need(all(a[i][i] == 1 and all(a[i][j] == 0 for j in range(i+1, n))
             for i in range(n)), "unit lower triangular matrix required")
    b = eye(n)
    for i in range(n):
        for j in range(i):
            b[i][j] = -sum(a[i][k] * b[k][j] for k in range(j, i))
    need(mul(a, b) == mul(b, a) == eye(n), "two-sided inverse")
    return b


def events(f, indices, after=(), path=""):
    """Parent U precedes both children; parent L follows both completions."""
    n = len(f)
    need(n > 0 and n & (n-1) == 0 and f[0] == 1, "unit dyadic symbol required")
    if n == 1:
        return [], after
    m = n // 2
    e, o = f[::2], f[1::2]
    k = divide(o, e)
    s = e.copy()
    for i in range(1, m):
        s[i] -= sum(o[j] * k[i-1-j] for j in range(i))
    ev, od = indices[::2], indices[1::2]
    u, l = path + "U", path + "L"
    upper = (u, after, [(ev[i], od[j], k[i-j-1])
                       for i in range(m) for j in range(i)])
    a, da = events(e, ev, (u,), path+"E")
    b, db = events(s, od, (u,), path+"S")
    lower = (l, tuple(sorted(set(da+db))), [(od[i], ev[j], k[i-j])
                                          for i in range(m) for j in range(i+1)])
    return [upper] + a + b + [lower], (l,)


def apply(p, event):
    # Every source row is read before this atomic shear macro is applied.
    out = [row.copy() for row in p]
    for i, j, coefficient in event[2]:
        for col in range(len(p)):
            out[i][col] += coefficient * p[j][col]
    return out


def cut_check(p, t, ti, eta):
    n = len(t)
    r = mul(p, ti)  # Inverse suffix; the multiplication direction matters.
    need(mul(r, t) == p, "R T = P")
    for i in range(n):
        need(p[i][i] == r[i][i] == 1, "unit diagonal")
        h = [p[i][j] - int(i == j) for j in range(n)]
        g = [r[i][j] - int(i == j) for j in range(n)]
        need(all(x == 0 or y == 0 for x, y in zip(h, g)), "disjoint supports")
        hs, gs = sum(map(abs, h)), sum(map(abs, g))
        difference = [h[j]-g[j] for j in range(n)]
        product = [sum(r[i][k] * (t[k][j]-int(k == j))
                       for k in range(n)) for j in range(n)]
        need(difference == product, "H-G = R(T-I)")
        need(sum(map(abs, difference)) == hs+gs, "disjoint row equality")
        need(hs + (1-eta)*gs <= eta, "row tradeoff")
    need(norm(p) <= 1+eta, "forward bound")
    return norm(r)


def replay(f):
    eta = sum(map(abs, f[1:]))
    need(eta <= 1, "the forward theorem requires eta <= 1")
    t, ti = toeplitz(f), inverse(toeplitz(f))
    es, _ = events(f, list(range(len(f))))
    start = frozenset()
    states = {start: eye(len(f))}
    todo = [start]
    max_p, max_r = F(0), F(0)
    while todo:
        done = todo.pop()
        p = states[done]
        max_r = max(max_r, cut_check(p, t, ti, eta))
        max_p = max(max_p, norm(p))
        for event in es:
            name, deps, _ = event
            if name in done or not set(deps) <= done:
                continue
            nxt, matrix = done | {name}, apply(p, event)
            if nxt in states:
                need(states[nxt] == matrix, "interleaving commutation")
            else:
                states[nxt] = matrix
                todo.append(nxt)
    complete = frozenset(event[0] for event in es)
    need(states[complete] == t, "compiler endpoint")
    return {"n": len(f), "eta": str(eta), "dag_cuts": len(states),
            "max_P": str(max_p), "max_inverse_suffix": str(max_r)}


def rejected(call, message):
    try:
        call()
    except ValueError as exc:
        need(message in str(exc), "wrong rejection: " + str(exc))
    else:
        raise ValueError("missing rejection: " + message)


def main():
    fixtures = [
        ("identity", [1]),
        ("two_wires", [1, F(-1, 2)]),
        ("proper_sharp_half", [1, F(1, 2), 0, 0]),
        ("mixed_half", [1, F(1, 4), F(1, 8), F(1, 8), 0, 0, 0, 0]),
        ("signed_three_quarters", [1, F(1, 8), F(-1, 8), F(1, 8),
                                   F(-1, 8), F(1, 8), F(-1, 8), 0]),
        ("eta_one_geometric", [1, -1, 0, 0, 0, 0, 0, 0]),
        ("eta_one_mixed", [1, F(1, 2), F(-1, 4), F(1, 4), 0, 0, 0, 0]),
    ]
    results = {name: replay(list(map(F, f))) for name, f in fixtures}
    need(results["mixed_half"]["dag_cuts"] == 123, "eight-wire DAG inventory")
    need(results["eta_one_geometric"]["max_P"] == "2", "eta-one forward edge")
    need(results["eta_one_geometric"]["max_inverse_suffix"] == "8", "eta-one inverse grows")
    for eta in (F(1, 2), F(1)):
        es, _ = events([F(1), eta, F(0), F(0)], list(range(4)))
        need(norm(apply(eye(4), es[0])) == 1+eta, "proper prefix sharpness")

    # Non-macro midpoint fails the stronger support invariant even at eta=1/2.
    t = toeplitz([F(1), F(1, 2)])
    midpoint = eye(2)
    midpoint[1][0] = F(1, 4)
    rejected(lambda: cut_check(midpoint, t, inverse(t), F(1, 2)), "disjoint supports")
    rejected(lambda: events([F(1)]*3, list(range(3))), "unit dyadic")
    rejected(lambda: events([F(2), F(0)], list(range(2))), "unit dyadic")

    # Changing a nonzero final left-shear sign must break the exact endpoint.
    f = list(map(F, [1, F(1, 4), F(1, 8), F(1, 8), 0, 0, 0, 0]))
    es, _ = events(f, list(range(8)))
    name, deps, adds = es[-1]
    es[-1] = (name, deps, [(i, j, -c) for i, j, c in adds])
    p = eye(8)
    for event in es:
        p = apply(p, event)
    rejected(lambda: need(p == toeplitz(f), "compiler endpoint"), "compiler endpoint")

    # The eta <= 1 guard is real: a proper root-U prefix at eta=2 has norm 4 > 3.
    outside = list(map(F, [1, 1, 1, 0, 0, 0, 0, 0]))
    es, _ = events(outside, list(range(8)))
    need(norm(apply(eye(8), es[0])) == 4, "outside-domain counterexample")
    rejected(lambda: replay(outside), "eta <= 1")
    print(json.dumps(results, sort_keys=True))
    print("PASS_PARITY_FORWARD_BOUND exact_DAG_controls=7 negative_controls=5 no_new_kappa")


if __name__ == "__main__":
    main()

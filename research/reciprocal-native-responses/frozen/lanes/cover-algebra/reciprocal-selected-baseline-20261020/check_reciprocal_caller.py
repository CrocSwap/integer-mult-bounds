#!/usr/bin/env python3
"""Check the reciprocal caller with exact rational matrices."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
MODEL = LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020/model-normal-v2/RESPONSE.json.gz"
PIN = "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0"


def need(value, text):
    if not value:
        raise ValueError(text)


def rows(raw):
    return [{int(j): F(x) for j, x in row.items() if F(x)} for row in raw]


def eye(n):
    return [{i: F(1)} for i in range(n)]


def zero(n):
    return [{} for _ in range(n)]


def put(row, j, x):
    value = row.get(j, F(0)) + x
    if value:
        row[j] = value
    else:
        row.pop(j, None)


def add(a, b, scale=1):
    out = [dict(row) for row in a]
    for row, extra in zip(out, b):
        for j, x in extra.items():
            put(row, j, scale * x)
    return out


def mul(a, b):
    out = []
    for row in a:
        result = {}
        for j, x in row.items():
            for k, y in b[j].items():
                put(result, k, x * y)
        out.append(result)
    return out


def trans(a, width):
    out = zero(width)
    for i, row in enumerate(a):
        for j, x in row.items():
            out[j][i] = x
    return out


def block(a, b, c, d):
    n = len(a)
    return [
        dict(list(left.items()) + [(n + j, x) for j, x in right.items()])
        for left, right in zip(a + c, b + d)
    ]


def diag(a):
    z = zero(len(a))
    return block(a, z, z, a)


def lower(a):
    n = len(a)
    return block(eye(n), zero(n), a, eye(n))


def upper(a):
    n = len(a)
    return block(eye(n), a, zero(n), eye(n))


def neg(a):
    return [{j: -x for j, x in row.items()} for row in a]


def rank(a):
    basis = {}
    for source in a:
        row = dict(source)
        while row:
            p = min(row)
            x = row[p]
            if p not in basis:
                basis[p] = {j: y / x for j, y in row.items()}
                break
            for j, y in basis[p].items():
                put(row, j, -x * y)
    return len(basis)


def sign_matrix(n, stage):
    return [{p: F(-1 if ((p * (stage + 3) + p // (stage + 2)) % 5) < 2 else 1)}
            for p in range(n)]


def replay(word, n):
    state = eye(n)
    for op, target, source, raw in word:
        value = F(raw)
        if op == "add":
            need(target != source, "Distinct ADD fields")
            for j, x in state[source].items():
                put(state[target], j, value * x)
        else:
            need(op == "scale" and value, "An invertible scalar scale")
            state[target] = {j: value * x for j, x in state[target].items()}
    return state


def check():
    raw = gzip.decompress(MODEL.read_bytes())
    need(sha256(raw).hexdigest() == PIN, "The actual model pin")
    source = json.loads(raw)
    matrices = {name: rows(value) for name, value in source["physical"].items()}
    e, p, r, j, ji = (matrices[name] for name in ("E", "P", "R", "J", "inverse_J"))
    ei = matrices["inverse_E"]
    u, ell = rows(source["reflection_U"]), rows(source["reflection_L"])
    n = 112
    i, z = eye(n), zero(n)
    need(mul(p, p) == mul(r, r) == i, "The two involutions")
    need(mul(p, r) == e and mul(r, p) == ei, "The ordered E factors")
    need(mul(e, ei) == mul(ei, e) == i, "Both E inverse orders")
    need(mul(ji, j) == mul(j, ji) == i, "Both metric inverse orders")
    need(mul(trans(e, n), mul(j, e)) == j, "The E metric")
    need(mul(trans(p, n), mul(j, p)) == j, "The P metric")
    need(mul(trans(r, n), mul(j, r)) == j, "The R metric")
    need(mul(ji, mul(trans(e, n), j)) == ei, "The inverse metric order")
    need(mul(j, mul(e, ji)) == trans(ei, n), "The inverse-adjoint metric order")
    need(mul(ell, u) == [{k: F(-2)} for k in range(16)], "L U=-2I")
    need(add(i, mul(u, ell)) == r, "The actual reflection factor")
    need(rank(add(r, i, -1)) == 16 and rank(add(e, i, -1)) == 32,
         "The actual correction ranks")
    special = set(source["special_ports"])
    need(len(special) == 32, "The exact special-port count")
    for row, delta in enumerate(add(p, i, -1)):
        need(not delta or row in special, "P changed rows stay selected")
        need(all(col in special for col in delta), "P changed columns stay selected")
    need(sum(len(row) for row in p) == 160, "P is not a monomial")
    need(replay(source["scalar_words"]["P"], n) == p, "The actual scalar P word")
    need(all(e[k].get(k, 0) == ei[k].get(k, 0) == 0 for k in range(n)),
         "Both actual response diagonals")

    ps, rs, us, ls = [], [], [], []
    for stage in range(3):
        s = eye(n) if stage == 0 else sign_matrix(n, stage)
        ps.append(mul(s, mul(p, s)))
        rs.append(mul(s, mul(r, s)))
        us.append(mul(s, u))
        ls.append(mul(ell, s))
    need(mul(rs[0], rs[1]) != mul(rs[1], rs[0]), "A noncommuting stage test")
    h, hi = mul(ps[1], ps[0]), mul(ps[0], ps[1])
    pt, pti = mul(ps[2], h), mul(hi, ps[2])
    rh = [rs[0], mul(ps[0], mul(rs[1], ps[0])), mul(hi, mul(rs[2], h))]
    uh = [us[0], mul(ps[0], us[1]), mul(hi, us[2])]
    lh = [ls[0], mul(ls[1], ps[0]), mul(ls[2], h)]
    ks = [add(a, i, -1) for a in rh]
    for k, col, row in zip(ks, uh, lh):
        need(mul(col, row) == k, "The transported rank factor")
    fs = [mul(diag(ps[s]), lower(rs[s])) for s in range(3)]
    b1 = mul(diag(ps[1]), upper(neg(rs[1])))
    f1i = mul(lower(neg(rs[1])), diag(ps[1]))
    need(mul(diag(ji), mul(trans(f1i, 2*n), diag(j))) == b1,
         "The whole wrapped inverse-adjoint metric conversion")
    triple = mul(fs[2], mul(b1, fs[0]))
    stripped = mul(diag(pti), triple)
    expected = mul(lower(rh[2]), mul(upper(neg(rh[1])), lower(rh[0])))
    need(stripped == expected, "The ordered transported triple")
    wi = block(z, i, neg(i), z)
    t = mul(wi, stripped)
    a0 = lower(ks[0])
    a1 = block(add(i, ks[1], -1), neg(ks[1]), ks[1], add(i, ks[1]))
    a2 = upper(neg(ks[2]))
    need(mul(a2, mul(a1, a0)) == t, "The three square-zero factors")
    for a in (a0, a1, a2):
        delta = add(a, eye(2*n), -1)
        need(mul(delta, delta) == zero(2*n), "A square-zero difference")
        need(rank(delta) == 16, "Each exact factor rank")
    a0i = lower(neg(ks[0]))
    a1i = block(add(i, ks[1]), ks[1], neg(ks[1]), add(i, ks[1], -1))
    a2i = upper(ks[2])
    ti = mul(a0i, mul(a1i, a2i))
    need(mul(ti, t) == mul(t, ti) == eye(2*n), "Both residual inverse orders")

    x = [dict(row) for row in eye(2*n)[:n]]
    y = [dict(row) for row in eye(2*n)[n:]]
    c0 = mul(ls[0], x)
    after0 = mul(fs[0], x + y)
    c1 = mul(ls[1], after0[n:])
    after1 = mul(b1, after0)
    c2 = mul(ls[2], after1[:n])
    want_x = add(add(x, mul(uh[1], c1), -1), mul(uh[2], c2))
    want_y = add(add(y, mul(uh[0], c0)), mul(uh[1], c1))
    need(t == want_x + want_y, "All224 source-record columns")
    need(rank(add(t, eye(2*n), -1)) <= 48, "The residual rank bound")
    need(mul(pt, pti) == mul(pti, pt) == i, "Both common-code inverse orders")
    for row, delta in enumerate(add(pt, i, -1)):
        need(not delta or row in special, "The common code has selected rows")
        need(all(col in special for col in delta), "The common code has selected columns")

    controls = {
        "omit_P_transport": mul(lower(rs[2]), mul(upper(neg(rs[1])), lower(rs[0]))) != stripped,
        "reverse_reflection_factors": mul(a0, mul(a1, a2)) != t,
        "use_E_as_involution": mul(e, e) != i,
        "omit_first_query_transport": mul(ls[1], add(y, mul(rs[0], x))) != c1,
    }
    need(all(controls.values()), "Every negative control rejects")
    return {
        "schema": "reciprocal-selected-baseline-check-v1",
        "status": "PASS",
        "model_sha256": PIN,
        "actual_ports": n,
        "actual_reflection_rank": 16,
        "actual_E_minus_I_rank": 32,
        "physical_P_nonzeros": 160,
        "physical_P_support": sorted(special),
        "three_stage_regression": "Independent signed conjugations of the actual112 model; not D25 routes.",
        "two_bank_columns": 224,
        "ordered_source_queries": 3,
        "factor_ranks": [16, 16, 16],
        "regression_residual_rank": rank(add(t, eye(2*n), -1)),
        "both_inverse_orders": True,
        "negative_controls": controls,
        "native_record_or_scatter_claim": False,
        "scope": "Exact matrix and ordered caller proof. The native service, saved records, phase scatter, host and full supplier remain separate.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = check()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "sha256": sha256(args.out.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()

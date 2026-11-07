#!/usr/bin/env python3
"""Exact checks for the hub-gauge torsor and pure-pair invariance.

Standard library only. New code: CubeJerry with OpenAI ChatGPT assistance.
Retained predecessor modules are hash-checked before source-only execution.
This is an executable certificate and rejection suite, not a proof kernel.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import sys
import time
import types

HERE = Path(__file__).resolve().parent
BASE_COMMIT = "7c49fe32c55de02c2c873655c804b16e4c3fef0a"
PAYLOAD_SHA256 = "d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821"
CONTROLS: list[str] = []


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(label, action, expected):
    try:
        action()
    except ValueError as exc:
        need(expected in str(exc), (label, "wrong rejection", str(exc)))
        CONTROLS.append(label)
    else:
        raise ValueError((label, "accepted an invalid contract"))


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    need(not a or len(a[0]) == len(b), "matrix dimensions")
    cols = len(b[0]) if b else 0
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Q(0))
             for j in range(cols)] for i in range(len(a))]


def mv(a, v):
    return [sum((x * y for x, y in zip(row, v)), Q(0)) for row in a]


def vm(v, a):
    return [sum((v[i] * a[i][j] for i in range(len(a))), Q(0))
            for j in range(len(a[0]))]


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q(0))


def inv(a):
    n = len(a)
    need(all(len(row) == n for row in a), "inverse needs square matrix")
    rows = [[Q(x) for x in row] + unit for row, unit in zip(a, eye(n))]
    for c in range(n):
        p = next((r for r in range(c, n) if rows[r][c]), None)
        need(p is not None, "singular matrix")
        rows[c], rows[p] = rows[p], rows[c]
        v = rows[c][c]
        rows[c] = [x / v for x in rows[c]]
        for r in range(n):
            if r != c and rows[r][c]:
                v = rows[r][c]
                rows[r] = [x - v * y for x, y in zip(rows[r], rows[c])]
    return [row[n:] for row in rows]


def det(a):
    n = len(a)
    if not n:
        return Q(1)
    rows = [[Q(x) for x in row] for row in a]
    out = Q(1)
    for c in range(n):
        p = next((r for r in range(c, n) if rows[r][c]), None)
        if p is None:
            return Q(0)
        if p != c:
            rows[c], rows[p] = rows[p], rows[c]
            out = -out
        v = rows[c][c]
        out *= v
        for r in range(c + 1, n):
            q = rows[r][c] / v
            for j in range(c + 1, n):
                rows[r][j] -= q * rows[c][j]
    return out


def dyadic(x):
    d = Q(x).denominator
    return d & (d - 1) == 0


def unit(x):
    x = Q(x)
    n = abs(x.numerator)
    return bool(n) and n & (n - 1) == 0 and dyadic(x)


def check_gl_d(a):
    ai = inv(a)
    need(all(dyadic(x) for row in a + ai for x in row), "not GL over dyadics")
    return ai


def supported(a, indices):
    inds = set(indices)
    return all(a[r][c] == Q(r == c) if r not in inds or c not in inds else True
               for r in range(len(a)) for c in range(len(a)))


def check_endpoint_form(a, k, r):
    j, i = set(k) - set(r), set(r) - set(k)
    need(all(a[x][y] == Q(x == y) or (x in j and y in i)
             for x in range(len(a)) for y in range(len(a))), "endpoint support")


def check_gauge(a, t, g0, g9, k, r):
    check_endpoint_form(a, k, r)
    for matrix in (a, t, g0, g9):
        check_gl_d(matrix)
    need(supported(g0, k) and supported(g9, r), "hub support")
    need(mm(g9, mm(t, g0)) == a, "gauge endpoint")


def check_pair(p, g, rf, c, d, u, a):
    """Check coefficient matrices for P = t^e p, job s = t^e.

    The central formal monomial cancels from both purity equations. The
    prefix is allowed to be rectangular; all current state rows are included.
    """
    need(all(dyadic(x) for v in (c, d, u, a) for x in v), "non-dyadic witness")
    need(all(not c[j] and not d[j] for j in range(len(c)) if j not in g), "helper support")
    need(all(not u[j] and not a[j] for j in range(len(u)) if j not in rf), "physical frame support")
    need(mv(p, c) == u, "pure column")
    need(vm(a, p) == d, "pure row")
    need(dot(d, c) == dot(a, u) == 1, "unit dual pair")


def check_two_sided_split(p, suffix, g, rf, c, d, u, a):
    """Ali Romman's prefix/suffix sufficient contract, normalized s=tau=1."""
    need(all(dyadic(x) for v in (c, d, u, a) for x in v), "non-dyadic witness")
    need(all(not c[j] and not d[j] for j in range(len(c)) if j not in g), "helper support")
    need(all(not u[j] and not a[j] for j in range(len(u)) if j not in rf), "physical frame support")
    need(vm(a, p) == d and mv(suffix, u) == c, "two-sided read/write equations")
    need(dot(d, c) == dot(a, u) == 1, "two-sided unit pairings")


def gram(vcols, wrows):
    return [[dot(d, c) for c in vcols] for d in wrows]


def dyadic_capacity_by_minors(g):
    """Small exact Gram checker via determinantal ideals over Z[1/2].

    Clearing powers of two does not change these ideals. The odd gcd of
    numerators of all k-minors is 1 iff the first k Smith factors are units.
    This avoids conflating rational rank with unit-pair capacity.
    """
    need(all(dyadic(x) for row in g for x in row), "Gram not dyadic")
    rows, cols = len(g), len(g[0]) if g else 0
    capacity, rank = 0, 0
    ideals = []
    for k in range(1, min(rows, cols) + 1):
        ideal = 0
        for rr in itertools.combinations(range(rows), k):
            for cc in itertools.combinations(range(cols), k):
                v = det([[g[r][c] for c in cc] for r in rr])
                n = abs(v.numerator)
                while n and n % 2 == 0:
                    n //= 2
                ideal = math.gcd(ideal, n)
        ideals.append(ideal)
        if ideal:
            rank = k
        if ideal == 1:
            capacity = k
    return {"capacity": capacity, "rational_rank": rank, "odd_determinantal_gcds": ideals}


def small_checks():
    # All four endpoint classes, and a two-dimensional common hub.
    n = 5
    k, r, h = {0, 2, 3}, {1, 2, 3}, {2, 3}
    endpoint = eye(n)
    endpoint[0][1] = Q(1)
    g0, g9, b = eye(n), eye(n), eye(n)
    g0[2][0], g0[3][2], g0[0][0] = Q(3), Q(1, 2), Q(2)
    g9[1][2], g9[3][1], g9[3][3] = Q(1), Q(-2), Q(1, 2)
    b[2][2], b[2][3], b[3][3] = Q(2), Q(1, 2), Q(1, 2)
    t = mm(inv(g9), mm(endpoint, inv(g0)))
    new0, new9 = mm(g0, b), mm(inv(b), g9)
    check_gauge(endpoint, t, g0, g9, k, r)
    check_gauge(endpoint, t, new0, new9, k, r)
    need(mm(inv(g0), new0) == b and supported(b, h), "stabilizer parameter")
    need(mm(new9, inv(g9)) == inv(b), "inverse stabilizer parameter")
    # A legal start-hub shear outside H requires an illegal end-hub repair.
    escape = eye(n)
    escape[2][0] = Q(1)
    repair = mm(endpoint, mm(inv(escape), inv(endpoint)))
    reject("start-hub shear outside H cannot be repaired at R", lambda:
           check_gauge(endpoint, endpoint, escape, repair, k, r), "hub support")
    rational_b = eye(n)
    rational_b[2][2] = Q(3)
    need(mm(inv(rational_b), mm(endpoint, rational_b)) == endpoint, "rational control endpoint")
    reject("rational gauge is not a dyadic gauge", lambda: check_gl_d(rational_b), "not GL over dyadics")
    bad_endpoint = eye(n)
    bad_endpoint[2][1] = Q(1)
    reject("wrong endpoint support invalidates stabilizer contract", lambda:
           check_endpoint_form(bad_endpoint, k, r), "endpoint support")

    # Productive formal job s=t: P=t*P_m, S=t^-1*P_m^-1, endpoint I.
    family_results = []
    b = [[Q(2), Q(1, 2), Q(0)], [Q(0), Q(1, 2), Q(0)], [Q(0), Q(0), Q(1)]]
    bi = check_gl_d(b)
    for m in (0, 3, 4):
        p = [[Q(m), Q(1), Q(0)], [Q(1), Q(0), Q(1)], [Q(0), Q(1), Q(-m - 1)]]
        need(det(p) == 1 and mm(inv(p), p) == eye(3), "toy word endpoint")
        # Completeness is proved in PROOF.md: outside-RF helper coefficient
        # is exactly c_1; forbidden input coefficient in aP is exactly a_1.
        need(p[2][0:2] == [0, 1] and [p[0][2], p[1][2]] == [0, 1], "toy lattice eliminations")
        v, w = [[Q(1), Q(0), Q(0)]], [[Q(m), Q(1), Q(0)]]
        vnew, wnew = [mv(bi, c) for c in v], [vm(d, b) for d in w]
        need(gram(v, w) == gram(vnew, wnew) == [[Q(m)]], "Gram transport")
        result = dyadic_capacity_by_minors(gram(v, w))
        need(result["capacity"] == (m == 4), "toy dyadic capacity")
        family_results.append({"m": m, **result})
        if m == 4:
            c, d = v[0], [Q(1), Q(1, 4), Q(0)]
            u, a = [Q(4), Q(1), Q(0)], [Q(1, 4), Q(0), Q(0)]
            check_pair(p, {0, 1}, {0, 1}, c, d, u, a)
            check_pair(mm(p, b), {0, 1}, {0, 1}, mv(bi, c), vm(d, b), u, a)
            # Exact independent fresh input z: coefficient of x loses c*d,
            # coefficient of z is c (formal job exponent cancels in S*u).
            su = mv(inv(p), u)
            need(su == c, "fresh input routed into retired helper")
            read = vm(a, p)
            need(read == d, "retirement emits the pure row")
            defect = [[su[i] * read[j] for j in range(3)] for i in range(3)]
            need(defect == [[c[i] * d[j] for j in range(3)] for i in range(3)], "independent old-input defect")
            reject("smaller physical frame loses pure column", lambda:
                   check_pair(p, {0, 1}, {0}, c, d, u, a), "physical frame support")
            reject("row purity cannot be omitted", lambda:
                   check_pair(p, {0, 1}, {0, 1}, c, [Q(1), Q(0), Q(0)], u, a), "pure row")
            reject("unit pairing cannot be omitted", lambda:
                   check_pair(p, {0, 1}, {0, 1}, [Q(0)] * 3, d, [Q(0)] * 3, a), "unit dual pair")
        elif m == 3:
            reject("rational pure pair with denominator three is not legal", lambda:
                   check_pair(p, {0, 1}, {0, 1}, v[0], [Q(1), Q(1, 3), Q(0)],
                              [Q(3), Q(1), Q(0)], [Q(1, 3), Q(0), Q(0)]), "non-dyadic witness")
    mixed = dyadic_capacity_by_minors([[Q(4), Q(0)], [Q(0), Q(3)]])
    need(mixed == {"capacity": 1, "rational_rank": 2, "odd_determinantal_gcds": [1, 3]}, "mixed simultaneous capacity")
    need(dyadic_capacity_by_minors([[Q(3), Q(5)]])["capacity"] == 1, "Bezout combinations count as units")

    # A labelled proper subset is not the complete common-boundary class.
    p, swap = eye(2), [[Q(0), Q(1)], [Q(1), Q(0)]]
    e0, e1 = [Q(1), Q(0)], [Q(0), Q(1)]
    check_pair(p, {0}, {0}, e0, e0, e0, e0)
    check_pair(swap, {0, 1}, {0}, e1, e1, e0, e0)
    reject("transport leaves a noninvariant labelled helper subset", lambda:
           check_pair(swap, {0}, {0}, e1, e1, e0, e0), "helper support")
    need(mv(swap, e0)[1] == 1, "restricted subset capacity falls to zero")

    shear = [[Q(1), Q(1)], [Q(0), Q(1)]]
    need(mv(shear, e0) == e0, "column-only invariant subset control")
    reject("column-submodule invariance alone does not preserve pure rows", lambda:
           check_pair(shear, {0}, {0}, e0, e0, e0, e0), "pure row")

    # Rectangular state with a private copy. The theorem preserves all rows.
    p = [[Q(1), Q(0)], [Q(0), Q(1)], [Q(1), Q(0)]]
    suffix = [[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)]]
    b = [[Q(1), Q(1)], [Q(0), Q(1)]]
    need(mm(suffix, p) == eye(2), "rectangular endpoint")
    u, a = [Q(1), Q(0), Q(1)], [Q(1), Q(0), Q(0)]
    check_pair(p, {0, 1}, {0, 2}, e0, e0, u, a)
    check_pair(mm(p, b), {0, 1}, {0, 2}, mv(inv(b), e0), vm(e0, b), u, a)
    reject("dropping a live private row can create false purity", lambda:
           check_pair(p, {0, 1}, {0}, e0, e0, u, a), "physical frame support")
    # Broader endpoint retirement can exploit a suffix kernel, outside PURE.
    injection = [Q(1), Q(0), Q(0)]
    check_two_sided_split(p, suffix, {0, 1}, {0}, e0, e0, injection, a)
    check_two_sided_split(mm(p, b), mm(inv(b), suffix), {0, 1}, {0},
                          mv(inv(b), e0), vm(e0, b), injection, a)
    need(mv(suffix, injection) == e0, "suffix-kernel example")
    reject("rectangular endpoint split need not be a PURE pair", lambda:
           check_pair(p, {0}, {0}, e0, e0, [Q(1), Q(0), Q(0)], a), "pure column")
    return {"all_endpoint_classes": True, "formal_job": "t", "toy_pairings": family_results,
            "simultaneous_mixed_pairing": mixed, "rectangular_state_checked": True, "two_sided_witness_transport_checked": True}


def frame_word(mixed):
    # Frame bases in F_2^9: 0, F0, F1, F2, F3, full.
    frames = [[], [1], [1, 2], [1, 4], [1, 2, 4], [1 << k for k in range(9)]]
    program = [["MOVE", 0, 0, 1, False]]
    if mixed:
        program += [["ADD", 0, 1, "1", 1], ["ADD", 1, 0, "1", 1]]
    program += [["MOVE", 0, 1, 2, False], ["MOVE", 1, 1, 3, False]]
    cut = len(program)
    program += [["MOVE", 0, 2, 4, False], ["MOVE", 1, 3, 4, False]]
    if mixed:
        program += [["ADD", 1, 0, "-1", 4], ["ADD", 0, 1, "-1", 4]]
    program += [["MOVE", 0, 4, 5, False], ["MOVE", 1, 4, 5, False]]
    return {"public": 2, "owned_fields": 0, "initial": [0, 1], "final": [5, 5],
            "frames": frames, "program": program}, cut


def authenticate():
    pins = json.loads((HERE / "retained/SHA256.json").read_text())
    for name, pin in pins.items():
        raw = (HERE / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin["sha256"], ("retained SHA256", name))
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == pin["git_blob"] and len(raw) == pin["size_bytes"], ("retained blob", name))
    # Compile the authenticated bytes directly: do not read or trust .pyc files.
    modules = []
    for name in ("hubmodel", "hub"):
        path = HERE / "retained/pr6835" / (name + ".py")
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
        modules.append(module)
    return modules, len(pins)


def sparse(a):
    return [{c: v for c, v in enumerate(row) if v} for row in a]


def dense(a, n):
    return [[row.get(c, Q(0)) for c in range(n)] for row in a]


def laurent_add(a, b):
    out = dict(a)
    for e, q in b.items():
        out[e] = out.get(e, Q(0)) + q
        if not out[e]:
            del out[e]
    return out


def laurent_monomial(frame, sign=1):
    e = [0] * 5
    if frame:
        e[frame - 1] = sign
    return {tuple(e): Q(1)}


def laurent_mul(a, b):
    out = {}
    for ea, qa in a.items():
        for eb, qb in b.items():
            e = tuple(x + y for x, y in zip(ea, eb))
            out[e] = out.get(e, Q(0)) + qa * qb
            if not out[e]:
                del out[e]
    return out


def frame_laurent_replay(word, upto=None):
    """Exact formal chart jobs: MOVE F->G multiplies by z_G/z_F.

    This tiny control has no private registers. Frame 0 has z_0=1;
    the five other frames get independent central invertible variables.
    """
    one = laurent_monomial(0)
    rows = [[dict(one) if r == c else {} for c in range(2)] for r in range(2)]
    program = word["program"] if upto is None else word["program"][:upto]
    for e in program:
        if e[0] == "MOVE":
            q = laurent_mul(laurent_monomial(e[3]), laurent_monomial(e[2], -1))
            rows[e[1]] = [laurent_mul(q, x) for x in rows[e[1]]]
        elif e[0] == "ADD":
            q = {tuple([0] * 5): Q(e[3])}
            rows[e[1]] = [laurent_add(x, laurent_mul(q, y))
                           for x, y in zip(rows[e[1]], rows[e[2]])]
        else:
            raise ValueError("unexpected Laurent control event")
    return rows


def intermediate_checks(hm, hub):
    first, k0 = frame_word(False)
    second, k1 = frame_word(True)
    for w in (first, second):
        hm.check_legal(w)
        need(hm.replay(w, w["program"])[0] == hm.identity(2), "intermediate word endpoint")
        labels, _ = hub.decompose(w, hm.Frames(w), w["program"])
        need(all(x is None for x in labels), "all events of control are in middle")
    need([e for e in first["program"] if e[0] == "MOVE"] ==
         [e for e in second["program"] if e[0] == "MOVE"], "same MOVE events")
    p0 = dense(hm.replay(first, first["program"][:k0])[0], 2)
    p1 = dense(hm.replay(second, second["program"][:k1])[0], 2)
    need(p0 == eye(2) and p1 == [[1, 1], [1, 2]], "matched cut prefixes")
    e0 = [Q(1), Q(0)]
    check_pair(p0, {0}, {0}, e0, e0, e0, e0)
    # For c=(c0,0), the off-frame component of P1*c is c0. Thus V=0.
    need(p1[1][0] == 1, "mixed helper has zero pure-column module")
    reject("same net middle map does not fix interior capacity", lambda:
           check_pair(p1, {0}, {0}, e0, e0, e0, e0), "pure column")

    lp0, lp1 = frame_laurent_replay(first, k0), frame_laurent_replay(second, k1)
    end0, end1 = frame_laurent_replay(first), frame_laurent_replay(second)
    expected_endpoint = [[laurent_monomial(5), {}],
                         [{}, laurent_mul(laurent_monomial(5), laurent_monomial(1, -1))]]
    need(end0 == end1 == expected_endpoint, "same formal chart endpoint")
    need(lp0[0][0] == laurent_monomial(2) and lp0[0][1] == lp0[1][0] == {},
         "productive pure job z_F1 before mixing")
    need(lp1[1][0] == laurent_monomial(3), "formal off-frame helper column is a unit")

    # Section 3.2 of #6835 proves completion exists; its greedy construction
    # is intentionally incomplete. This example supplies no new algorithm.
    gamma = [[Q(3), Q(1)], [Q(5), Q(2)]]
    t = inv(gamma)
    check_gauge(eye(2), t, gamma, eye(2), {0, 1}, {1})
    need(not unit(3) and not unit(5), "neither N entry is a unit")
    reject("predecessor greedy unit-entry completion is incomplete", lambda:
           hub.gauge(sparse(t), sparse(gamma), hm.identity(2), [0, 1], [1], 2), "no unit pivot found")
    return {"same_total_middle_map": "I2", "same_MOVE_events": 7,
            "complete_helper_class": [0], "matched_frame_registers": [0],
            "capacity_before": 1, "capacity_after": 0,
            "changed_mid_ADD_events": 4, "formal_chart_job": "z_F1",
            "formal_chart_endpoint_equal": True, "greedy_completion_control": "N=(3,5)^T"}


def spmul(a, b):
    """Independent sparse multiplication, also for rectangular live states."""
    out = []
    for row in a:
        rr = defaultdict(Q)
        for k, v in row.items():
            for c, w in b[k].items():
                rr[c] += v * w
        out.append({c: v for c, v in rr.items() if v})
    return out


def spidentity(n):
    return [{r: Q(1)} for r in range(n)]


def sp_supported(a, indices):
    indices = set(indices)
    return all(row == {r: Q(1)} if r not in indices else all(c in indices for c in row)
               for r, row in enumerate(a))


def linear_step(rows, e):
    op, dest = e[0], e[1]
    if op == "MOVE":
        return
    if op in ("INIT", "CLEAR"):
        rows[dest] = {}
        return
    if op == "SCALE":
        q = Q(e[2])
        rows[dest] = {k: q * v for k, v in rows[dest].items() if q * v}
        return
    q, src = Q(e[3]), e[2]
    if op == "COPY":
        rows[dest] = {k: q * v for k, v in rows[src].items() if q * v}
        return
    need(op == "ADD", "unknown native scalar event")
    row = rows[dest]
    for k, v in rows[src].items():
        value = row.get(k, Q(0)) + q * v
        if value:
            row[k] = value
        else:
            row.pop(k, None)


def native_checks(hm, hub):
    w = hm.load(HERE / "retained/pr6824/WORD.json.gz")
    need(hm.payload_sha(w) == PAYLOAD_SHA256, "published native payload")
    pin = json.loads((HERE / "retained/pr6824/SOURCE-PINS.json").read_text())[0]
    need(pin["payload_sha256"] == PAYLOAD_SHA256 and pin["commit"] ==
         "2a7ca44fbda3abaa4df355b183ed7d7478eef7c1", "native provenance")
    frames, n = hm.Frames(w), w["public"]
    census = hm.check_legal(w)
    classes = hub.classes(w, frames)
    k, r = classes["K"], classes["R"]
    h = set(k) & set(r)
    labels, _ = hub.decompose(w, frames, w["program"])
    pre = [e for e, tag in zip(w["program"], labels) if tag == "pre"]
    mid = [e for e, tag in zip(w["program"], labels) if tag is None]
    post = [e for e, tag in zip(w["program"], labels) if tag == "post"]
    endpoint = hm.endpoint_matrix(w)
    ainv = [dict(row) for row in endpoint]
    for x, row in enumerate(ainv):
        for y in row:
            if x != y:
                row[y] = -row[y]
    old0, _ = hm.replay(w, pre)
    old9, _ = hm.replay(w, post)
    t, _ = hm.replay(w, mid)
    need(spmul(old9, spmul(t, old0)) == endpoint, "original factored endpoint")
    tinv = spmul(old0, spmul(ainv, old9))
    ident = spidentity(n)
    need(spmul(tinv, t) == ident == spmul(t, tinv), "middle inverse")
    new0, dnew, new9 = hub.gauge(t, tinv, endpoint, k, r, n)
    old0inv = spmul(ainv, spmul(old9, t))
    b = spmul(old0inv, new0)
    bi = spmul(dnew, old0)
    need(spmul(b, bi) == ident == spmul(bi, b), "native B inverse")
    need(b != ident and sp_supported(b, h) and sp_supported(bi, h), "native stabilizer support")
    need(all(dyadic(v) for matrix in (b, bi) for row in matrix for v in row.values()), "native dyadic stabilizer")
    need(spmul(old0, b) == new0 and spmul(bi, old9) == new9, "native torsor identity")
    # Equal initial/final helper classes. Only H can be affected by B.
    main = set(classes["X"]) | set(classes["Y"])
    boundary = defaultdict(list)
    for j in range(n):
        if j not in main:
            boundary[(w["initial"][j], w["final"][j])].append(j)
    need(set(boundary[(frames.zero, frames.full)]) == h, "native common-hub helper class")
    need(all(set(g) == h or not (set(g) & h) for g in boundary.values()), "all complete boundary classes invariant")

    # Choose the most populated proper frame at a cut with a live private
    # lifetime, plus quarter and three-quarter cuts. The rule is data-driven
    # and fixed; it does not cherry-pick a successful purity witness.
    cur = {j: w["initial"][j] for j in range(n)}
    best = (-1, None, None)
    for i, e in enumerate(mid, 1):
        if e[0] == "MOVE":
            cur[e[1]] = e[3]
        elif e[0] == "INIT":
            cur[e[1]] = e[2]
        elif e[0] == "CLEAR":
            cur.pop(e[1], None)
        if any(j >= n for j in cur):
            counts = Counter(f for f in cur.values() if f not in (frames.zero, frames.full))
            if counts:
                f, count = max(counts.items(), key=lambda x: (x[1], -x[0]))
                if count > best[0]:
                    best = (count, i, f)
    need(best[1] is not None, "native interior live-private cut exists")
    selected = {len(mid) // 4, 3 * len(mid) // 4, best[1]}
    oldrows = [dict(row) for row in old0] + [{} for _ in range(w["owned_fields"])]
    newrows = [dict(row) for row in new0] + [{} for _ in range(w["owned_fields"])]
    cur = {j: w["initial"][j] for j in range(n)}
    cuts = []
    clear_values = {"zero": 0, "nonzero": 0}
    for i, e in enumerate(mid, 1):
        if e[0] == "CLEAR":
            # This replay treats CLEAR as a linear reset, as the predecessor
            # scalar model does. Record, do not assume, zero-before-clear.
            need(spmul([oldrows[e[1]]], b)[0] == newrows[e[1]], "private clear covariance")
            need(bool(oldrows[e[1]]) == bool(newrows[e[1]]), "private clear zero status")
            clear_values["nonzero" if oldrows[e[1]] else "zero"] += 1
        linear_step(oldrows, e)
        linear_step(newrows, e)
        if e[0] == "MOVE":
            cur[e[1]] = e[3]
        elif e[0] == "INIT":
            cur[e[1]] = e[2]
        elif e[0] == "CLEAR":
            cur.pop(e[1], None)
        if i in selected:
            need(spmul(oldrows, b) == newrows, ("all public/private prefix rows", i))
            need(spmul(newrows, bi) == oldrows, ("inverse prefix transport", i))
            active_private = [j for j in cur if j >= n]
            proper_counts = Counter(f for f in cur.values() if f not in (frames.zero, frames.full))
            largest = max(proper_counts.values(), default=0)
            cuts.append({"mid_cut": i, "public_rows": n, "private_slots": w["owned_fields"],
                         "active_private": len(active_private), "largest_proper_frame_residency": largest,
                         "all_rows_equal_PB": True})
    need(spmul(new9, newrows[:n]) == endpoint, "new native endpoint independently replayed")
    return {"payload_sha256": PAYLOAD_SHA256, "public": n, "helper_common_hub": len(h),
            "K": len(k), "R": len(r), "M": n - len(set(k) | set(r)),
            "complete_helper_boundary_classes": len(boundary),
            "pre_mid_post_events": [len(pre), len(mid), len(post)],
            "B_nonzeros": sum(len(row) for row in b),
            "B_inverse_nonzeros": sum(len(row) for row in bi),
            "native_word_legality": census, "cuts": cuts, "middle_CLEAR_input_rows": clear_values,
            "scope": "normalized scalar replay and class/frame applicability; not a symbolic productive-pair census"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--small-only", action="store_true", help="omit the source-bound native replay")
    parser.add_argument("--output", type=Path, help="write a JSON certificate to this path")
    args = parser.parse_args()
    started = time.monotonic()
    (hm, hub), count = authenticate()
    result = {"schema_version": 1, "status": "PASS", "base_commit": BASE_COMMIT,
              "claim": "fixed-word endpoint hub gauge preserves PURE pairing; no new kappa",
              "retained_files_checked": count, "small": small_checks(),
              "changed_word_control": intermediate_checks(hm, hub)}
    if not args.small_only:
        result["native"] = native_checks(hm, hub)
    result["semantic_rejection_controls"] = CONTROLS
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["python"] = sys.version.split()[0]
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(data)
    print(data, end="")


if __name__ == "__main__":
    main()

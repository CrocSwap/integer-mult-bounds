#!/usr/bin/env python3
"""Exact integer group-algebra certificate; Python 3.12, standard library only.

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.
The quantified implications are proved in README.md, not by sampling cuts.
"""
from itertools import permutations, product
import json


E = (1, 2, 4)
C = (2, 4, 1)
FACTORS = ((7, -6, 1), (42, -14, 1), (-5, 1), (-6, 1), (-7, 1), (-9, 1))
EXPECTED_P = (555660, -1006362, 741006, -295897, 70871, -10494, 942, -47, 1)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank2(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def multiply(a, b):
    """Rows of a*b, acting on column addresses; no permutation representation."""
    return tuple((b[0] if r & 1 else 0) ^ (b[1] if r & 2 else 0)
                 ^ (b[2] if r & 4 else 0) for r in a)


def add(a, b, scale=1):
    result = dict(a)
    for g, coefficient in b.items():
        result[g] = result.get(g, 0) + scale * coefficient
        if not result[g]:
            del result[g]
    return result


def convolution(a, b):
    result = {}
    for g, x in a.items():
        for h, y in b.items():
            k = multiply(g, h)
            result[k] = result.get(k, 0) + x * y
    return {g: x for g, x in result.items() if x}


def poly_product(factors):
    result = [1]
    for factor in factors:
        out = [0] * (len(result) + len(factor) - 1)
        for i, x in enumerate(result):
            for j, y in enumerate(factor):
                out[i + j] += x * y
        result = out
    return result


def evaluate(coefficients, operator, vector):
    out = {}
    for coefficient in reversed(coefficients):
        out = add(convolution(operator, out), vector, coefficient)
    return out


def below_ceiling(out_c, sum_out_g):
    """6*out(c) <= ((27+9*sqrt(2))/7) * sum_g out(g), exactly."""
    need(out_c >= 0 and sum_out_g >= 0, "negative crossing count")
    excess = 42 * out_c - 27 * sum_out_g
    return excess <= 0 or excess * excess <= 162 * sum_out_g * sum_out_g


def cross_rank(action, cut, scalar_rows):
    """Literal binary cross-block rank of P_action tensor scalar_rows."""
    size = len(scalar_rows)
    rows = {}
    for x in cut:
        y = action[x]
        if y in cut:
            continue
        for r, scalar_row in enumerate(scalar_rows):
            rows[(y, r)] = rows.get((y, r), 0) ^ (scalar_row << (size * x))
    return rank2(rows.values())


def model_checks(group, gates):
    index = {g: i for i, g in enumerate(group)}
    action = lambda g: [index[multiply(g, h)] for h in group]
    cuts = [{index[E]}, {i for i, g in enumerate(group) if g[0] < g[1]},
            {i for i in range(168) if i % 5 < 2}, set(range(84))]
    projectors = []
    for u, v in product(range(1, 4), repeat=2):
        if (u & v).bit_count() % 2:
            projectors.append([v if (u >> r) & 1 else 0 for r in range(2)])
    need(len(projectors) == 6, "rank-one projector inventory")
    checked = 0
    for cut in cuts:
        for g in gates:
            perm = action(g)
            crossing = sum(perm[x] not in cut for x in cut)
            for projector in projectors:
                need(cross_rank(perm, cut, projector) == crossing, "paid rank/crossing binding")
                checked += 1
        forward, inverse = action(C), action(multiply(C, C))
        out_c = sum(forward[x] not in cut for x in cut)
        need(out_c == sum(inverse[x] not in cut for x in cut), "inverse orientation")
        target_rows = [0] * (3 * 168)
        for x in cut:
            for role, perm in enumerate((forward, inverse, list(range(168)))):
                y = perm[x]
                if y not in cut:
                    target_rows[3 * y + role] ^= 1 << (3 * x + role)
        need(rank2(target_rows) == 2 * out_c, "two targets plus restored dirty role")
        counts = [sum(action(g)[x] not in cut for x in cut) for g in gates]
        need(below_ceiling(out_c, sum(counts)), "regular cut bound")
    one = {index[E]}
    need(cross_rank(action(gates[0]), one, [1, 2]) == 2, "rank-two control")
    need(cross_rank(action(C), one, [1, 2, 4]) == 3, "unrestored third-role control")
    return {"paid_cross_block_checks": checked, "dirty_endpoint_checks": len(cuts),
            "rank_two_and_unrestored_role_controls": 2}


def spectator_action_checks(gates):
    """Every cut in the 15-point natural GL4 action, with axis 3 a spectator."""
    points = range(1, 16)

    def perm(g):
        return [sum(((row & x).bit_count() & 1) << i for i, row in enumerate(g))
                + (x & 8) - 1 for x in points]

    actions = [perm(g) for g in gates] + [perm(C)]
    images = []
    for action in actions:
        table = [0] * (1 << 15)
        for cut in range(1, 1 << 15):
            bit = cut & -cut
            table[cut] = table[cut ^ bit] | (1 << action[bit.bit_length() - 1])
        images.append(table)
    for cut in range(1 << 15):
        counts = [(table[cut] & ~cut).bit_count() for table in images]
        need(below_ceiling(counts[-1], sum(counts[:-1])), "spectator permutation cut")
    return 1 << 15


def verify():
    group = [g for g in product(range(1, 8), repeat=3) if rank2(g) == 3]
    need(len(group) == 168 and len(set(group)) == 168, "GL3 enumeration")
    gates = []
    for i, j in permutations(range(3), 2):
        rows = list(E)
        rows[i] ^= rows[j]
        gates.append(tuple(rows))
    c2 = multiply(C, C)
    need(multiply(c2, C) == E and C != E, "cycle order")
    need(all(multiply(g, g) == E for g in gates), "CNOT involutions")
    need({multiply(multiply(C, g), c2) for g in gates} == set(gates), "cyclic conjugation")
    need(all(multiply(g, h) in set(group) for g in gates for h in group), "regular permutations")
    ell = {E: 6, **{g: -1 for g in gates}}
    b = {E: 2, C: -1, c2: -1}
    need(convolution(ell, b) == convolution(b, ell), "L and B commute")
    need(convolution(b, b) == {g: 3 * x for g, x in b.items()}, "B^2=3B")
    p = poly_product(FACTORS)
    q = poly_product(FACTORS[1:])
    need(tuple(p) == EXPECTED_P, "expanded polynomial")
    need(not evaluate(p, ell, b), "integer group-algebra identity p(L)B=0")
    v = evaluate(q, ell, b)
    shifted = add(ell, {E: 1}, -3)
    w = convolution(shifted, v)
    need(v and w, "nonzero sharpness vectors")
    need(convolution(shifted, w) == {g: 2 * x for g, x in v.items()}, "(L-3)w=2v")
    need(convolution(b, v) == {g: 3 * x for g, x in v.items()}, "Bv=3v")
    vv = sum(x * x for x in v.values())
    ww = sum(x * x for x in w.values())
    vw = sum(x * w.get(g, 0) for g, x in v.items())
    need((len(v), len(w), vv, ww, vw) == (165, 165, 117151272, 234302544, -165676896),
         "sharpness vector receipt")
    # Exact root separation and beta < 23/4: 3>sqrt(2), sqrt(7)<3, 36sqrt(2)<53.
    need(9 > 2 and 9 > 7 and 36 * 36 * 2 < 53 * 53, "algebraic root bounds")
    altered_p = list(p)
    altered_p[0] += 1
    need(evaluate(altered_p, ell, b), "altered polynomial must fail")
    missing_gate = add(add(ell, {gates[0]: 1}), {E: 1}, -1)
    need(evaluate(p, missing_gate, b), "missing CNOT must fail")
    wrong_b = {E: 1, gates[0]: -1}
    need(evaluate(p, ell, wrong_b), "order-two target must fail")
    need(not evaluate(q, ell, {}), "identity target cannot witness sharpness")
    need(not below_ceiling(1, 1), "a claimed six-to-one crossing ratio must fail")
    return {
        "status": "PASS_THREE_CYCLE_CUT_CEILING",
        "group_order": len(group), "integer_identity_coefficients": len(group),
        "p_low_to_high": p, "q_low_to_high": q,
        "sharp_spectral_ceiling": "(27+9*sqrt(2))/7",
        "boolean_cut_optimum": "not determined",
        "v_nonzero_coefficients": len(v), "w_nonzero_coefficients": len(w),
        "v_norm_squared": vv, "w_norm_squared": ww, "v_dot_w": vw,
        "coefficient_and_budget_controls": 5,
        "source_model": model_checks(group, gates),
        "natural_GL4_cuts": spectator_action_checks(gates),
        "scope": "Exact finite algebra certificate for the written all-dimension cut-cone theorem; no word optimum or new kappa.",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

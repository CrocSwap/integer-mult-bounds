#!/usr/bin/env python3
"""Independent exact Q^2 audit of the 24-array information contract.

Only the pinned scalar packet is read. No production or predecessor checker
is imported. Chart maps here are synthetic noncommuting rational operators;
this is not an audit of the actual owner/payload route binding.

Prepared by the run's recursive-interfaces specialist with substantial
OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/joint-query/certificate.json.gz"
PACKET_SHA256 = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"


def need(condition, message):
    if not condition:
        raise ValueError(message)


raw = PACKET.read_bytes()
need(hashlib.sha256(raw).hexdigest() == PACKET_SHA256, "packet digest")
packet = json.loads(gzip.decompress(raw))
R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
A = tuple(packet["A_ports"])
T = tuple(packet["T_ports"])
U = tuple(packet["U_ports"])
SELECTED = A + T
need(A == (0, 7, 20, 27, 36, 46, 57, 111), "A partition")
need(T == (21, 37, 47, 76, 81, 87, 92, 110), "T partition")
need(U == tuple(p for p in range(112) if p not in SELECTED), "U partition")
need(len(R) == 8, "eight scalar query coordinates")
need(all(sum(R[i][p] * R[j][p] for p in ports) == 4 * (i == j)
         for ports in (A, T) for i in range(8) for j in range(8)),
     "selected Grams")


def linear(*terms):
    """Exact sparse scalar linear forms in independent input coordinates."""
    result = {}
    for coefficient, value in terms:
        for variable, weight in value.items():
            result[variable] = result.get(variable, Q(0)) + coefficient * weight
    return {k: v for k, v in result.items() if v}


def array(*terms):
    return tuple(linear(*[(c, v[i]) for c, v in terms]) for i in range(2))


def matrix(stage, port):
    if stage == 0:
        return ((1, 0), (0, 1))
    t = 1 + (port + 2 * stage) % 3
    u = (-1) ** (port + stage)
    return ((1, t), (u, 1 + u * t))


def route(stage, port, value, inverse=False):
    m = matrix(stage, port)
    if inverse:
        m = ((m[1][1], -m[0][1]), (-m[1][0], m[0][0]))
    return tuple(linear(*[(m[i][j], value[j]) for j in range(2)])
                 for i in range(2))


def query(bank, stage, ports):
    moved = {p: route(stage, p, bank[p]) for p in ports}
    return tuple(array(*[(R[i][p], moved[p]) for p in ports if R[i][p]])
                 for i in range(8))


def section(values, stage, ports, wrong_order=False):
    if wrong_order:
        need(len(ports) == 8, "wrong-order control has eight selected ports")
        moved = [route(stage, ports[i], values[i], True) for i in range(8)]
        return {p: array(*[(R[i][p] / 4, moved[i])
                           for i in range(8) if R[i][p]]) for p in ports}
    return {p: route(stage, p,
                     array(*[(R[i][p] / 4, values[i])
                              for i in range(8) if R[i][p]]), True)
            for p in ports}


def forward(x, y):
    f = query(x, 0, range(112))
    correction = section(f, 0, U)
    xx = {p: array((1, x[p]), (-1, correction[p])) for p in U}
    xx.update(section(query(x, 0, T), 0, A))
    xx.update(section(f, 0, T))
    yy = {p: array((1, y[p]), (1, xx[p])) for p in U}
    yy.update({p: array((1, x[p]), (1, y[p]), (-1, xx[p])) for p in SELECTED})
    return xx, yy


def observe(x, y):
    """Original inputs to the 200 observations and 24 retained arrays."""
    xx, yy = forward(x, y)
    correction = section(query(xx, 1, T), 1, U)
    logger = section(query(yy, 2, U + T), 2, A)
    return ({p: array((1, xx[p]), (-1, yy[p])) for p in U},
            {p: array((1, yy[p]), (1, correction[p])) for p in U},
            {p: array((1, yy[p]), (1, logger[p])) for p in A},
            {p: xx[p] for p in SELECTED},
            {p: yy[p] for p in T})


def recover(observations, fault=None):
    C, Y, YA, sx, yt = observations
    correction = section(query(sx, 1, T), 1, U)
    yu = {p: array((1, Y[p]), (0 if fault == "omit_K" else -1, correction[p]))
          for p in U}
    xu = {p: array((-1 if fault == "C_sign" else 1, C[p]), (1, yu[p])) for p in U}
    logger = query(yu, 2, U)
    if fault != "omit_future_T":
        logger = tuple(array((1, a), (1, b)) for a, b in zip(logger, query(yt, 2, T)))
    logger = section(logger, 2, A, fault == "reverse_section_order")
    ya = {p: array((1, YA[p]), (1 if fault == "logger_sign" else -1, logger[p]))
          for p in A}
    sy = {**ya, **yt}
    f = query(sx, 0, T)
    old_t = section(query(sx, 0, A), 0, T)
    correction = section(f, 0, U)
    x = {p: array((1, xu[p]), (1, correction[p])) for p in U}
    x.update(old_t)
    center = tuple(array((1, a), (-1, b), (-1, c))
                   for a, b, c in zip(f, query(x, 0, U), query(old_t, 0, T)))
    x.update(section(center, 0, A))
    y = {p: array((-1, C[p])) for p in U}
    y.update({p: array((1, sx[p]), (1, sy[p]), (-1, x[p])) for p in SELECTED})
    return x, y


def variable(index):
    return ({2 * index: Q(1)}, {2 * index + 1: Q(1)})


def first_residual(actual, expected):
    for side in range(2):
        for port in range(112):
            for coordinate in range(2):
                residual = linear((1, actual[side][port][coordinate]),
                                  (-1, expected[side][port][coordinate]))
                if residual:
                    k = min(residual)
                    return [side, port, coordinate, k, str(residual[k])]
    return None


def main():
    for stage in (0, 1, 2):
        for port in range(112):
            v = variable(0)
            need(route(stage, port, route(stage, port, v), True) == v,
                 "two-coordinate route inverse")
            need(route(stage, port, route(stage, port, v, True)) == v,
                 "two-coordinate inverse route")
    x = {p: variable(p) for p in range(112)}
    y = {p: variable(112 + p) for p in range(112)}
    observations = observe(x, y)
    need(recover(observations) == (x, y), "all 448 input coefficients recovered")
    independent = []
    index = 0
    for ports in (U, U, A, SELECTED, T):
        block = {}
        for p in ports:
            block[p] = variable(index)
            index += 1
        independent.append(block)
    need(index == 224, "224 independent observation and retention arrays")
    need(observe(*recover(independent)) == tuple(independent),
         "all 448 observation and retention coefficients recovered")
    controls = {}
    for fault in ("omit_K", "C_sign", "omit_future_T", "logger_sign",
                  "reverse_section_order"):
        controls[fault] = first_residual(recover(observations, fault), (x, y))
        need(controls[fault] is not None, "undetected control: " + fault)
    print(json.dumps({
        "status": "PASS_INDEPENDENT_TWO_COORDINATE_REVIEW",
        "formal_input_coordinates": 448,
        "formal_observation_coordinates": 448,
        "identity_orders": 2,
        "logical_maps": "synthetic port-dependent determinant-one rational maps; actual pinned R",
        "negative_control_witnesses": controls,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

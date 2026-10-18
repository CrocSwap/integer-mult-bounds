#!/usr/bin/env python3
"""Exact finite evidence for the nonlinear frame-cut theorem. Apache-2.0.

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance.
Full truth tables replace linear-column replay. No repository code is imported.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[F(0) for _ in range(n)] for _ in range(n)]


def add(a, b, sign=1):
    return [[x+sign*y for x, y in zip(r, s)] for r, s in zip(a, b)]


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def eliminate(a, columns):
    a = [list(map(F, row)) for row in a]
    pivot = 0
    for j in range(columns):
        k = next((k for k in range(pivot, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[pivot], a[k] = a[k], a[pivot]
        scale = a[pivot][j]
        a[pivot] = [x/scale for x in a[pivot]]
        for k in range(len(a)):
            if k != pivot and a[k][j]:
                scale = a[k][j]
                a[k] = [x-scale*y for x, y in zip(a[k], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return a, pivot


def rank(a):
    return eliminate(a, len(a[0]))[1]


def inverse(a):
    n = len(a)
    result, r = eliminate([row+unit for row, unit in zip(a, eye(n))], n)
    need(r == n, "singular flag basis")
    return [row[n:] for row in result]


def decode(value, size, q):
    return [(value//q**j) % q for j in range(size)]


def table_gate(kind, roles, q=2, coefficient=1):
    roles = list(roles)
    table = []
    for code in range(q**len(roles)):
        v = decode(code, len(roles), q)
        if kind == "product":
            v[2] = (v[2]+coefficient*v[0]*v[1]) % q
        elif kind == "sum":
            v[1] = (v[1]+coefficient*v[0]) % q
        elif kind == "not":
            v[0] = (v[0]+coefficient) % q
        elif kind == "swap":
            v[0], v[1] = v[1], v[0]
        else:
            raise ValueError("unknown fixture gate")
        table.append(sum(x*q**j for j, x in enumerate(v)))
    return {"roles": roles, "table": table}


def apply(gate, values, q):
    roles = gate["roles"]
    code = sum(values[r]*q**j for j, r in enumerate(roles))
    new = decode(gate["table"][code], len(roles), q)
    result = list(values)
    for r, v in zip(roles, new):
        result[r] = v
    return result


def binary_word(w):
    # Four genuinely nonlinear steps implement t ^= a using a^2=a.
    gadget = [table_gate("product", (0, 2, 1)), table_gate("sum", (0, 2)),
              table_gate("product", (0, 2, 1)), table_gate("sum", (0, 2))]
    tail = [table_gate("sum", (1, 0)), table_gate("sum", (0, 1))]
    prefix = []
    if w >= 4:
        u = [table_gate("product", (1, 2, 3)), table_gate("sum", (0, 3)), table_gate("not", (2,))]
        prefix = u + list(reversed(deepcopy(u)))
    return prefix + gadget + tail


def ternary_word():
    return [table_gate("product", (0, 1, 2), 3), table_gate("sum", (2, 0), 3),
            table_gate("sum", (2, 0), 3, -1), table_gate("product", (0, 1, 2), 3, -1),
            table_gate("swap", (0, 1), 3)]


def make_case(w, m, q=2, sharp=False, nonsplit=False):
    gates = binary_word(w) if q == 2 else ternary_word()
    basis = [[F((i+1)**j) for j in range(m)] for i in range(m)]
    inv = inverse(basis)
    gauge = zero(m)
    gauge[-1][0] = F(2, 3)

    def frame(k):
        if sharp:
            return zero(m)
        if nonsplit:
            a, b = F(k % 4-2, 2), F(k % 3-1, 3)
            return [[a, -b], [b, a]]
        t = [[F((k+2*i+3*j) % 7-3, 2+(k+i+j) % 2) if i <= j else F(0)
              for j in range(m)] for i in range(m)]
        return add(gauge, multiply(multiply(basis, t), inv))

    sources = [frame(i) for i in range(w)]
    for k, g in enumerate(gates):
        g["frame"] = frame(w+k)
    rho = [1, 0] + list(range(2, w))
    sinks = [None]*w
    for r in range(w):
        sinks[rho[r]] = add(sources[r], eye(m))
    return dict(W=w, m=m, q=q, gates=gates, rho=rho, sources=sources, sinks=sinks,
                basis=eye(m) if sharp else basis, gauge=zero(m) if sharp else gauge,
                mode="nonsplit" if nonsplit else "rational-flag")


def graph_and_traces(c):
    w, m, q = c["W"], c["m"], c["q"]
    need(type(w) is int and w >= 2 and type(m) is int and m >= 2
         and type(q) is int and q >= 2, "invalid dimensions")
    need(len(c["sources"]) == len(c["sinks"]) == w, "all terminals required")
    need(len(c["rho"]) == w and all(type(x) is int for x in c["rho"])
         and set(c["rho"]) == set(range(w)), "invalid role permutation")
    frames = c["sources"] + [g["frame"] for g in c["gates"]] + c["sinks"]
    for a in frames:
        need(len(a) == m and all(len(row) == m for row in a), "matrix shape")
        need(all(type(x) in (int, F) for row in a for x in row), "exact matrix entries required")
    need(all(add(c["sinks"][c["rho"][r]], c["sources"][r], -1) == eye(m)
             for r in range(w)), "endpoint frame difference is not identity")
    last, edges, incoming = list(range(w)), [], {}
    for k, g in enumerate(c["gates"]):
        need(set(g) == {"roles", "table", "frame"}, "one common gate frame required")
        roles = g["roles"]
        need(roles and len(set(roles)) == len(roles)
             and all(type(r) is int and 0 <= r < w for r in roles), "invalid gate ports")
        need(len(g["table"]) == q**len(roles)
             and all(type(v) is int and 0 <= v < q**len(roles) for v in g["table"]), "invalid truth table")
        node = w+k
        incoming[node] = []
        for r in roles:
            incoming[node].append(len(edges))
            edges.append((last[r], node, r))
            last[r] = node
    for r in range(w):
        node = w+len(c["gates"])+r
        incoming[node] = [len(edges)]
        edges.append((last[r], node, r))
    traces = []
    for x in product(range(q), repeat=w):
        state, values = list(x), []
        for g in c["gates"]:
            values.extend(state[r] for r in g["roles"])
            state = apply(g, state, q)
        values.extend(state)
        need(all(state[c["rho"][r]] == x[r] for r in range(w)), "truth-table endpoint fails")
        traces.append((x, tuple(values), tuple(state)))
    return frames, edges, incoming, traces


def outside_outputs(c, edges, incoming, labels, label, x, transcript):
    """Simulate the complement using only outside inputs and outgoing messages."""
    w = c["W"]
    values = {(r, r): x[r] for r in range(w) if labels[r] != label}

    def edge_value(index):
        source, _, role = edges[index]
        if labels[source] == label:
            need(index in transcript, "missing outgoing message")
            return transcript[index]
        return values[source, role]

    for k, g in enumerate(c["gates"]):
        node = w+k
        if labels[node] == label:
            continue
        v = [edge_value(i) for i in incoming[node]]
        code = sum(a*c["q"]**j for j, a in enumerate(v))
        for role, value in zip(g["roles"], decode(g["table"][code], len(v), c["q"])):
            values[node, role] = value
    result = {}
    for r in range(w):
        node = w+len(c["gates"])+r
        if labels[node] != label:
            result[r] = edge_value(incoming[node][0])
    return result


def audit_partition(c, edges, incoming, traces, labels, omit=None):
    w = c["W"]
    terminal = w+len(c["gates"])
    separated = sum(labels[r] != labels[terminal+c["rho"][r]] for r in range(w))
    contexts = simulations = 0
    for label in set(labels[:w]):
        demanded = [r for r in range(w) if labels[r] == label
                    and labels[terminal+c["rho"][r]] != label]
        if not demanded:
            continue
        leaving = [i for i, (u, v, _) in enumerate(edges) if labels[u] == label and labels[v] != label]
        if omit is not None:
            leaving = [i for i in leaving if i != omit]
        fixed = [r for r in range(w) if r not in demanded]
        recovered, context_keys = {}, set()
        for x, values, output in traces:
            key = (tuple(x[r] for r in fixed), tuple(values[i] for i in leaving))
            hidden = tuple(x[r] for r in demanded)
            need(key not in recovered or recovered[key] == hidden, "outgoing transcript collision")
            recovered[key] = hidden
            context_keys.add(key[0])
        need(len(recovered) == c["q"]**w, "transcript does not determine all inputs")
        need(len(leaving) >= len(demanded), "cut capacity below demanded inputs")
        for x, values, output in traces:
            outside = outside_outputs(c, edges, incoming, labels, label, x,
                                      {i: values[i] for i in leaving})
            need(all(outside[c["rho"][r]] == x[r] for r in demanded), "outside decoding fails")
            need(all(value == output[r] for r, value in outside.items()), "outside simulation differs")
            simulations += 1
        contexts += len(context_keys)
    return separated, contexts, simulations


def partitions(c, frames):
    m = c["m"]
    if c["mode"] == "nonsplit":
        need(m == 2, "nonsplit fixture dimension")
        parameters = []
        for f in frames:
            a, b = f[0][0], f[1][0]
            need(f == [[a, -b], [b, a]], "not the declared Q(i) family")
            parameters.append((a, b))
        return [parameters, [(a, -b) for a, b in parameters]]
    inv = inverse(c["basis"])
    triangular = [multiply(multiply(inv, add(f, c["gauge"], -1)), c["basis"]) for f in frames]
    need(all(t[i][j] == 0 for t in triangular for i in range(m) for j in range(i)),
         "supplied common flag fails")
    return [[t[i][i] for t in triangular] for i in range(m)]


def verify_case(c):
    frames, edges, incoming, traces = graph_and_traces(c)
    parts = partitions(c, frames)
    ranks = [rank(add(frames[v], frames[u], -1)) for u, v, _ in edges]
    crossing = [sum(labels[u] != labels[v] for labels in parts) for u, v, _ in edges]
    need(all(a <= b for a, b in zip(crossing, ranks)), "partition charges exceed edge rank")
    results = [audit_partition(c, edges, incoming, traces, labels) for labels in parts]
    lower = sum(r[0] for r in results)
    need(lower == c["W"]*c["m"] and sum(ranks) >= lower, "rank-mass bound fails")
    return dict(W=c["W"], m=c["m"], alphabet=c["q"], gates=len(c["gates"]),
                inputs=len(traces), edges=len(edges), rank_mass=sum(ranks), lower_bound=lower,
                fixed_input_contexts=sum(r[1] for r in results),
                outside_simulations=sum(r[2] for r in results))


def reject(fn, name):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("control escaped: " + name)


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for p in pins["files"]:
        if p["usage"] == "input":
            need(sha256((ROOT / p["path"]).read_bytes()).hexdigest() == p["sha256"], "source drift")
    cases = [(f"binary_W{w}_m{m}", make_case(w, m)) for w in (3, 4, 5, 6) for m in (2, 3)]
    cases += [(f"ternary_W{w}", make_case(w, 2, q=3)) for w in (3, 4)]
    cases += [("sharp", make_case(6, 3, sharp=True)),
              ("nonsplit", make_case(4, 2, nonsplit=True))]
    results = {name: verify_case(c) for name, c in cases}
    need(results["sharp"]["rank_mass"] == 18, "sharp control differs")
    c = make_case(4, 2)
    controls = 0
    for kind in ("rho", "endpoint", "terminals", "ports", "table", "basis", "flag"):
        bad = deepcopy(c)
        if kind == "rho": bad["rho"] = list(range(4))
        elif kind == "endpoint": bad["sinks"][0][0][0] += 1
        elif kind == "terminals": bad["sinks"].pop()
        elif kind == "ports": bad["gates"][0]["port_frames"] = []
        elif kind == "table": bad["gates"][0]["table"][0] = -1
        elif kind == "basis": bad["basis"][1] = bad["basis"][0][:]
        else: bad["gates"][0]["frame"][1][0] += 1
        reject(lambda: verify_case(bad), kind)
        controls += 1
    # A Toffoli-only candidate fools zero/one-hot tests of an identity endpoint.
    bad = make_case(3, 2, sharp=True)
    bad["gates"] = [dict(table_gate("product", (0, 1, 2)), frame=zero(2))]
    bad["rho"] = list(range(3))
    for x in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)):
        need(apply(bad["gates"][0], x, 2) == list(x), "basis-only adversary changed")
    reject(lambda: verify_case(bad), "basis-only acceptance")
    controls += 1
    sharp = make_case(3, 2, sharp=True)
    frames, edges, incoming, traces = graph_and_traces(sharp)
    labels = partitions(sharp, frames)[0]
    leaving = [i for i, (u, v, _) in enumerate(edges) if labels[u] == 0 and labels[v] != 0]
    reject(lambda: audit_partition(sharp, edges, incoming, traces, labels, omit=leaving[0]), "omitted message")
    controls += 1
    # Exact Boolean cancellation; deleting nonlinear gates loses the CNOT.
    gadget = binary_word(3)[:4]
    for x in product(range(2), repeat=3):
        actual, linear_only = list(x), list(x)
        for g in gadget:
            actual = apply(g, actual, 2)
            if len(g["roles"]) == 2:
                linear_only = apply(g, linear_only, 2)
        need(actual == [x[0], x[1] ^ x[0], x[2]], "Boolean cancellation fails")
        need(linear_only == list(x), "linear-only control fails")
    controls += 1
    # Non-common-flag geometry: the diagonal-count inequality needs its premise.
    need(rank([[1, 1], [1, 1]]) == 1, "rank-one control")
    j, b = [[F(0), F(1)], [F(-1), F(0)]], [[F(0), F(0)], [F(-1), F(1)]]
    commutator = add(multiply(j, b), multiply(b, j), -1)
    need(commutator[0][0]*commutator[1][1]-commutator[0][1]*commutator[1][0] == -2,
         "non-common-flag seed changed")
    controls += 1
    print(json.dumps({"status": "PASS_NONLINEAR_FRAME_CUT_BOUND", "cases": results,
                      "total_inputs": sum(r["inputs"] for r in results.values()),
                      "outside_simulations": sum(r["outside_simulations"] for r in results.values()),
                      "controls": controls, "bound": "s >= W*m", "kappa": "unchanged"},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Independent full-table DAG/cut checks; standard library, no inherited code."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(matrix):
    a = [[Q(x) for x in row] for row in matrix]
    r = 0
    for c in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        v = a[r][c]
        a[r] = [x / v for x in a[r]]
        for i in range(len(a)):
            if i != r:
                v = a[i][c]
                a[i] = [x - v*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


ZERO = ((0, 0), (0, 0))
IDENTITY = ((1, 0), (0, 1))


def node(kind, inputs=(), frame=ZERO, value=0):
    return {"kind": kind, "inputs": list(inputs), "frame": frame, "value": value}


def apply(kind, args, value=0):
    if kind == "const":
        return value
    if kind in ("copy", "sink"):
        return args[0]
    if kind == "xor":
        return args[0] ^ args[1]
    if kind == "and":
        return args[0] & args[1]
    if kind == "not":
        return 1 ^ args[0]
    if kind == "table":
        return value[sum(x << i for i, x in enumerate(args))]
    raise ValueError("unknown gate")


def evaluate(nodes, assignment):
    values = []
    for i, n in enumerate(nodes):
        need(all(type(j) is int and 0 <= j < i for j in n["inputs"]), "acyclic port reference")
        values.append(assignment[n["value"]] if n["kind"] == "input" else
                      apply(n["kind"], [values[j] for j in n["inputs"]], n["value"]))
    return values


def edge_list(nodes):
    return [(u, v, port) for v, n in enumerate(nodes) for port, u in enumerate(n["inputs"])]


def endpoint(nodes, demands):
    data = [s for s, _ in demands]
    sinks = [t for _, t in demands]
    need(len(data) == len(set(data)) and len(sinks) == len(set(sinks)), "distinct designated demands")
    indices = [n["value"] for n in nodes if n["kind"] == "input"]
    need(sorted(indices) == list(range(len(indices))), "independent input indices")
    need(all(nodes[s]["kind"] == "input" for s in data), "data source")
    tables = [(a, evaluate(nodes, a)) for a in product((0, 1), repeat=len(indices))]
    need(all(values[s] == values[t] for _, values in tables for s, t in demands), "designated endpoint")
    return tables


def cut_check(nodes, demands, tables, labels, omit=None):
    edges = edge_list(nodes)
    reconstructions = 0
    for label in set(labels):
        crossing = [e for e in edges if labels[e[0]] == label and labels[e[1]] != label and e != omit]
        moving = [s for s, t in demands if labels[s] == label and labels[t] != label]
        moving_ids = {nodes[s]["value"] for s in moving}
        seen = {}
        for assignment, values in tables:
            fixed = tuple((i, x) for i, x in enumerate(assignment) if i not in moving_ids)
            transcript = tuple(values[u] for u, _, _ in crossing)
            key = (fixed, transcript)
            unknowns = tuple(values[s] for s in moving)
            need(key not in seen or seen[key] == unknowns, "transcript collision")
            seen[key] = unknowns
            messages = {e: values[e[0]] for e in crossing}
            outside = {}
            for v, n in enumerate(nodes):
                if labels[v] == label:
                    continue
                if n["kind"] == "input":
                    need(n["value"] not in moving_ids, "unknown outside input")
                    outside[v] = assignment[n["value"]]
                else:
                    args = []
                    for port, u in enumerate(n["inputs"]):
                        if labels[u] == label:
                            need((u, v, port) in messages, "missing outgoing message")
                            args.append(messages[(u, v, port)])
                        else:
                            args.append(outside[u])
                    outside[v] = apply(n["kind"], args, n["value"])
                need(outside[v] == values[v], "outside reconstruction")
            reconstructions += 1
        need(len(crossing) >= len(moving), "data-only cut bound")
    return reconstructions


def framed_check(nodes, demands):
    tables = endpoint(nodes, demands)
    for n in nodes:
        need(n["frame"][1][0] == 0, "supplied triangular flag")
    for s, t in demands:
        need(tuple(tuple(nodes[t]["frame"][i][j] - nodes[s]["frame"][i][j]
                         for j in range(2)) for i in range(2)) == IDENTITY, "endpoint frame shift")
    bill = 0
    for u, v, _ in edge_list(nodes):
        delta = [[nodes[v]["frame"][i][j] - nodes[u]["frame"][i][j] for j in range(2)] for i in range(2)]
        charge = rank(delta)
        need(charge >= sum(delta[i][i] != 0 for i in range(2)), "triangular rank charge")
        bill += charge
    for i in range(2):
        cut_check(nodes, demands, tables, [n["frame"][i][i] for n in nodes])
    need(bill >= 2*len(demands), "data rank floor")
    return tables, bill


def fixtures():
    examples = [
        ("clean-copy-discard", [node("input"), node("const"), node("xor", (0, 1)),
                               node("copy", (2,)), node("sink", (3,), IDENTITY),
                               node("copy", (0,))], [(0, 4)]),
        ("nonlinear-garbage", [node("input"), node("input", value=1), node("and", (0, 1)),
                               node("xor", (0, 2)), node("xor", (3, 2)),
                               node("sink", (4,), IDENTITY), node("sink", (1,), IDENTITY)], [(0, 5), (1, 6)]),
        ("unrestored-dirty", [node("input"), node("input", value=1), node("xor", (0, 1)),
                              node("xor", (2, 1)), node("sink", (3,), IDENTITY),
                              node("not", (2,))], [(0, 4)]),
        ("copies-not-volume", [node("input"), node("copy", (0,), IDENTITY),
                               node("sink", (1,), IDENTITY), node("sink", (1,), IDENTITY),
                               node("sink", (1,), IDENTITY)], [(0, 2)]),
        ("constant-erasure", [node("input"), node("const", value=1), node("and", (0, 1)),
                              node("sink", (2,), IDENTITY), node("const")], [(0, 3)]),
    ]
    name, nodes, demands = deepcopy(examples[1])
    nodes[2]["frame"] = ((0, Q(1, 2)), (0, 1))
    nodes[3]["frame"] = ((1, 0), (0, 0))
    nodes[4]["frame"] = ((Q(1, 2), 1), (0, Q(-1, 2)))
    examples.append(("noncommuting-fractional-interior", nodes, demands))
    # Independent arbitrary Boolean truth tables can create/dispose nonlinear
    # scratch without changing the two data endpoints. The third source is
    # arbitrary dirty input, so all eight table entries actually execute.
    for truth in product((0, 1), repeat=8):
        nodes = [node("input"), node("input", value=1), node("input", value=2),
                 node("table", (0, 1, 2), value=truth), node("xor", (0, 3)),
                 node("xor", (4, 3)), node("sink", (5,), IDENTITY),
                 node("sink", (1,), IDENTITY)]
        examples.append(("three-input-table-" + "".join(map(str, truth)), nodes, [(0, 6), (1, 7)]))
    return examples


def compute():
    cases = []
    for name, nodes, demands in fixtures():
        tables, bill = framed_check(nodes, demands)
        replays = 0
        for labels in product((0, 1), repeat=len(nodes)):
            replays += cut_check(nodes, demands, tables, labels)
        cases.append({"name": name, "vertices": len(nodes), "physical_edges": len(edge_list(nodes)),
                      "input_assignments": len(tables), "independent_demands": len(demands),
                      "rank_bill": bill, "binary_partitions": 2**len(nodes), "outside_reconstructions": replays})
    controls = []

    def rejects(name, action):
        try:
            action()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("accepted control " + name)

    _, nodes, demands = fixtures()[0]
    bad = deepcopy(nodes)
    bad[4] = node("sink", (1,), IDENTITY)
    rejects("erased-required-data", lambda: endpoint(bad, demands))
    rejects("missing-outgoing-wire", lambda: cut_check(nodes, demands, endpoint(nodes, demands), [0, 0, 0, 0, 1, 0], (3, 4, 0)))
    rejects("duplicate-demand-volume", lambda: endpoint(fixtures()[3][1], [(0, 2), (0, 3), (0, 4)]))
    bad = deepcopy(nodes)
    bad[4]["frame"] = ZERO
    rejects("missing-terminal-frame", lambda: framed_check(bad, demands))
    bad = deepcopy(nodes)
    bad[3]["frame"] = ((1, 1), (1, 1))
    rejects("noncommon-flag-rank-one", lambda: framed_check(bad, demands))
    # A nonlinear endpoint agrees on zero and one-hot inputs, but fails at 11.
    bad = [node("input"), node("input", value=1), node("and", (0, 1)),
           node("xor", (0, 2)), node("sink", (3,), IDENTITY), node("sink", (1,), IDENTITY)]
    need(all(evaluate(bad, a)[4:] == list(a) for a in ((0, 0), (1, 0), (0, 1))), "basis-only control premise")
    rejects("basis-only-nonlinear-endpoint", lambda: endpoint(bad, [(0, 4), (1, 5)]))
    # Wrongly collapsing the distinct physical outgoing fanout edges loses
    # one unknown data value at this cut; each input port is a distinct wire.
    ports = [node("input"), node("input", value=1), node("xor", (0, 1)),
             node("xor", (2, 1)), node("sink", (3,), IDENTITY), node("sink", (1,), IDENTITY)]
    rejects("fanout-edge-omission", lambda: cut_check(ports, [(0, 4), (1, 5)],
            endpoint(ports, [(0, 4), (1, 5)]), [0, 0, 1, 1, 1, 1], (1, 3, 1)))
    # A preloaded data-dependent copy at a different frame is a genuine
    # counterexample if the independence condition is silently weakened.
    preload = [node("input"), node("input", frame=IDENTITY, value=1),
               node("sink", (1,), IDENTITY), node("copy", (0,))]
    need(all(evaluate(preload, (x, x))[2] == x for x in (0, 1)), "preloaded-copy correlated endpoint")
    preload_bill = sum(rank([[preload[v]["frame"][i][j] - preload[u]["frame"][i][j]
                             for j in range(2)] for i in range(2)]) for u, v, _ in edge_list(preload))
    need(preload_bill == 0, "preloaded-copy zero bill")
    rejects("preloaded-data-dependent-outside-copy", lambda: endpoint(preload, [(0, 2)]))
    # The unrestricted/noncommon flag boundary is a written countermodel;
    # do not count a tautological integer comparison as an execution check.
    return {"cases": cases, "rejection_controls": controls,
            "duplicate_copy_bill": 2,
            "duplicate_copy_outputs": 3, "duplicate_copy_independent_demands": 1,
            "excluded_preloaded_copy": {"correlated_assignments": 2, "rank_bill": preload_bill,
                                        "declared_data_demands": 1, "address_dimension": 2},
            "scope": "finite full-table evidence for credited data-only cut corollary; no universal enumeration"}


if __name__ == "__main__":
    import json
    print(json.dumps(compute(), indent=2))

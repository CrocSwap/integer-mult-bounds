#!/usr/bin/env python3
"""Exact lower bound for all monotone scalar and transported handoff frames."""

import argparse, copy, gzip, hashlib, importlib.util, itertools, json, math, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import frame_model as F
import domains as J
import reduce_frames
from eliminate import solve, INF

SCALE = 1 << 40


def read(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == ".gz" else b)


def canonical(x):
    return json.dumps(json.loads(json.dumps(x)), sort_keys=True, separators=(",", ":"))


def engine(source_bytes):
    s = importlib.util.spec_from_file_location(
        "fine_moment", ROOT / "vendor/fine_moment.py"
    )
    m = importlib.util.module_from_spec(s)
    # Use the exact authenticated bytes; -B does not prevent reading .pyc files.
    exec(compile(source_bytes, str(ROOT / "vendor/fine_moment.py"), "exec"), m.__dict__)
    m.SH = 256
    m.GRID = 1 << 256
    m.LOG_TERMS = 100
    m.EXP_TERMS = 96
    return m


def optimize(w, cost):
    fs, loc, pr, nx, profile, transports = F.model(w)
    for (a, z), G in transports.items():
        J.inverse(G)
        F.need(J.image(fs[a], G) == fs[z], "source warp image")
    original_loc = list(loc)
    loc, pr, nx, aliases = reduce_frames.reduce(loc, pr, nx)
    L, U = J.bounds(fs, loc, pr, nx, transports)
    comps = J.components(L, U, pr, nx, transports)
    variables = {i for c in comps for i in c}
    best = list(fs)
    rows = []
    minimum = 0
    # All child costs not incident to a variable, plus cut-copy charges.
    edge_profile = Counter()
    for z, aa in pr.items():
        for a in aa:
            if a not in variables and z not in variables:
                d = F.rank(L[z]) - F.rank(L[a])
                F.need(d >= 0 and L[a] & L[z] == L[a], "fixed edge")
                minimum += cost[d]
    # Copy descents are the only invoice entries absent from the graph edges.
    _, _, raw_pr, _, _, _ = F.model(w)
    for z, aa in raw_pr.items():
        for a in aa:
            d = F.rank(fs[z]) - F.rank(fs[a])
            if d:
                edge_profile[d] += 1
    copies = Counter({int(k): v for k, v in w["report"]["local_profile"].items()})
    copies.subtract(edge_profile)
    F.need(
        all(n >= 0 for n in copies.values())
        and {r: n for r, n in copies.items() if n} == {8: 8},
        "private copy invoice",
    )
    minimum += sum(n * cost[r] for r, n in copies.items())
    for ci, comp in enumerate(comps):
        dom = {i: J.domain(L[i], U[i]) for i in comp}
        cs = set(comp)
        F.need(all(fs[i] in dom[i] for i in comp), "source outside complete domains")
        edges = set((a, i) for i in comp for a in pr[i]) | set(
            (i, j) for i in comp for j in nx[i]
        )
        factors = []
        for a, z in sorted(edges):
            da = dom.get(a, [L[a]])
            dz = dom.get(z, [L[z]])
            arr = np.full((len(da), len(dz)), INF, dtype=np.int64)
            for ia, fa in enumerate(da):
                for iz, fz in enumerate(dz):
                    if fa & fz == fa:
                        arr[ia, iz] = pr[z].count(a) * cost[F.rank(fz) - F.rank(fa)]
            scope = sorted({a, z} & cs)
            factors.append((scope, arr.reshape([len(dom[i]) for i in scope])))
        for (a, z), G in transports.items():
            if a not in cs and z not in cs:
                continue
            da = dom.get(a, [L[a]])
            dz = dom.get(z, [L[z]])
            lookup = {f: j for j, f in enumerate(dz)}
            arr = np.full((len(da), len(dz)), INF, dtype=np.int64)
            for i, f in enumerate(da):
                image = J.image(f, G)
                if image in lookup:
                    arr[i, lookup[image]] = 0
            scope = sorted({a, z} & cs)
            factors.append((scope, arr.reshape([len(dom[i]) for i in scope])))
        score, chosen, maxstates = solve(dom, factors)
        F.need(0 <= score < INF, "no feasible component")
        minimum += score
        for i, j in chosen.items():
            best[i] = dom[i][j]
        rows.append(dict(nodes=len(comp), minimum=score, max_table_states=maxstates))
    for i, j in aliases.items():
        best[i] = best[j]
    # Check the reconstructed assignment against the original, uncontracted graph.
    for z, aa in raw_pr.items():
        for a in aa:
            F.need(best[a] & best[z] == best[a], "reconstructed inclusion")
    for (a, z), G in transports.items():
        F.need(J.image(best[a], G) == best[z], "reconstructed transport")
    for i, where in enumerate(original_loc):
        if where is None:
            F.need(best[i] == fs[i], "changed fixed anchor")
    p = profile(best)
    original = profile(fs)
    F.need(
        sum(r * n for r, n in p.items())
        == sum(r * n for r, n in original.items())
        == 5371,
        "invariant local mass",
    )
    F.need(
        minimum <= sum(n * cost[r] for r, n in p.items()),
        "lower bound exceeds reconstructed cost",
    )
    F.need(
        minimum == sum(n * cost[r] for r, n in original.items()),
        "expected rounded optimum changed",
    )
    return dict(
        minimum_excess_units=minimum,
        scale=SCALE,
        local_rank_mass=5371,
        source_profile=original,
        reconstructed_profile=p,
        contracted_nodes=len(aliases),
        variable_nodes=len(variables),
        components=rows,
    )


def packing(dual, stock, inventory, flo):
    y = list(map(Q, dual["width_dual"]))
    z = list(map(Q, dual["bin_dual"]))
    sizes = dual["widths"]
    ranks = dual["bin_ranks"]
    slacks = []
    F.need(
        sizes == [4, 5, 7, 8, 9]
        and ranks == [8, 16, 32, 48]
        and len(y) == 5
        and len(z) == 4,
        "dual dimensions",
    )
    for R, v in zip(ranks, z):
        for ns in itertools.product(*(range(R // s + 1) for s in sizes)):
            rem = R - sum(s * n for s, n in zip(sizes, ns))
            if rem < 0:
                continue
            slack = flo[rem] - v - sum(n * q for n, q in zip(ns, y))
            F.need(slack >= 0, "invalid packing dual")
            slacks.append(slack)
    F.need(len(slacks) == 1163, "pattern enumeration")
    return sum(666 * inventory[s] * v for s, v in zip(sizes, y)) + sum(
        stock[R] * v for R, v in zip(ranks, z)
    ), min(slacks)


def controls(cost):
    # Complete F2^3 lattice has 1,7,7,1 subspaces. Independent cardinality control.
    ds = J.domain(1, F.mask((1, 2, 4)))
    F.need(
        Counter(F.rank(m) for m in ds) == {0: 1, 1: 7, 2: 7, 3: 1},
        "complete lattice control",
    )
    # Brute-force a nontrivial cyclic factor graph, including infeasible pairs.
    dom = {i: [0, 1, 2] for i in range(4)}
    factors = []
    for a, z in [(0, 1), (1, 2), (2, 3), (0, 3), (1, 3)]:
        table = np.array([[0, 9, INF], [4, 1, 7], [INF, 2, 5]], dtype=np.int64) + (
            a + z
        )
        table = np.minimum(table, INF)
        # Competing pairwise preferences make the optimum depend on the cycle.
        table = np.roll(table, (a + z) % 3, axis=1)
        factors.append(([a, z], table))
    optimum = min(
        sum(int(t[assignment[a], assignment[z]]) for (a, z), t in factors)
        for assignment in itertools.product(range(3), repeat=4)
    )
    score, choices, _ = solve(dom, copy.deepcopy(factors))
    F.need(
        score
        == optimum
        == sum(int(t[choices[a], choices[z]]) for (a, z), t in factors),
        "elimination vs brute force",
    )
    # Actual reduction of a split rank-2 climb, with fixed endpoints.
    loc = [None, ("scale", 0), None]
    pr = {1: [0], 2: [1]}
    nx = {0: [1], 1: [2]}
    reduced, rpr, rnx, aliases = reduce_frames.reduce(loc, pr, nx)
    F.need(
        aliases == {1: 0} and rpr[2] == [0] and rnx[0] == [2],
        "contraction reconstruction",
    )
    F.need(2 * cost[1] > cost[2], "contraction must improve split positive control")
    fixed = [None, None, None]
    F.need(not reduce_frames.reduce(fixed, pr, nx)[3], "fixed anchors must survive")
    F.need(
        not reduce_frames.reduce(loc, {1: [0], 2: [1]}, {0: [1], 1: [2, 2]})[3],
        "unbalanced incidence must survive",
    )
    return dict(
        complete_three_space_counts=[1, 7, 7, 1],
        cyclic_assignments=81,
        cyclic_optimum=optimum,
        split_climb_saving_units=2 * cost[1] - cost[2],
        fixed_anchors_preserved=True,
        unbalanced_node_preserved=True,
    )


def run():
    pins = read(ROOT / "INPUTS.json")
    verified = {}
    for p in pins["sources"]:
        data = (ROOT / p["path"]).read_bytes()
        F.need(
            hashlib.sha256(data).hexdigest() == p["sha256"],
            "source digest: " + p["path"],
        )
        verified[p["path"]] = data
        if "uncompressed_sha256" in p:
            F.need(
                hashlib.sha256(gzip.decompress(data)).hexdigest()
                == p["uncompressed_sha256"],
                "uncompressed digest",
            )
    dual = read(ROOT / "DUAL.json")
    b = Q(dual["threshold"])
    F.need(b == Q(4243, 2500000), "threshold")
    e = engine(verified["vendor/fine_moment.py"])
    flo = {0: Q(0)}
    for r in range(1, 49):
        flo[r] = (73 * e.moment(73, 1, [(r, 1)], b)[0] - r) / b
    cost = [int((flo[r] * SCALE).__floor__()) for r in range(10)]
    F.need(all(0 <= c < INF // 20000 for c in cost), "integer range")
    words = {tag: read(ROOT / f"inputs/{tag}.json.gz") for tag in ["base", "extra"]}
    inventory = None
    results = {}
    for tag, w in words.items():
        F.need(
            (w["report"]["v"], w["report"]["h"], w["report"]["R"]) == (112, 9, 480),
            "word geometry",
        )
        live = set(range(224, 704)) - set(w["removed"])
        inv = Counter(
            F.rank(
                F.mask(tuple(w["helper_final"].get(str(r), [1 << i for i in range(9)])))
            )
            - F.rank(F.mask(tuple(w["start_extra"].get(str(r), []))))
            for r in live
        )
        F.need(dict(inv) == {4: 33, 5: 9, 7: 38, 8: 114, 9: 240}, "helper widths")
        inventory = inv
        results[tag] = optimize(w, cost)
    plan = read(ROOT / "inputs/plan.json.gz")
    stock = Counter()
    F.need(
        (plan["M"], plan["live"], plan["deficit"]) == (73, 66304, 23680),
        "parent dimensions",
    )
    F.need(
        len(plan["order"]) == 666 and len({tuple(x) for x in plan["order"]}) == 666,
        "call count",
    )
    F.need(
        set(plan["windows"]) == {f"{r},{c}" for r in range(74) for c in range(18)},
        "window keys",
    )
    for rank, times in plan["windows"].values():
        stock[rank] += 112
    F.need(dict(stock) == {8: 49728, 16: 33152, 32: 33152, 48: 33152}, "bin stock")
    D, slack = packing(dual, stock, inventory, flo)
    local = min(Q(r["minimum_excess_units"], SCALE) for r in results.values())
    idle_mass = sum(r * n for r, n in stock.items()) - 666 * sum(
        r * n for r, n in inventory.items()
    )
    mass = 666 * 5371 + idle_mass
    F.need(mass == 73 * 66304 - 23680, "total mass")
    lower = (mass + b * (666 * local + D)) / (73 * 66304)
    F.need(lower > 1, "cap not established")
    tests = controls(cost)
    rejected = []
    bad = copy.deepcopy(words["extra"])
    bad["report"]["local_profile"]["1"] -= 1
    try:
        optimize(bad, cost)
    except ValueError:
        rejected.append("undercharged invoice")
    else:
        raise ValueError("undercharged invoice accepted")
    bad = copy.deepcopy(words["extra"])
    bad["warps"][0][2][0] = 0
    try:
        optimize(bad, cost)
    except ValueError:
        rejected.append("singular logical transport")
    else:
        raise ValueError("singular transport accepted")
    bad = copy.deepcopy(dual)
    bad["bin_dual"][0] = str(Q(bad["bin_dual"][0]) + 1)
    try:
        packing(bad, stock, inventory, flo)
    except ValueError:
        rejected.append("overstated dual")
    else:
        raise ValueError("overstated dual accepted")
    return dict(
        schema=1,
        threshold=str(b),
        sources=pins,
        dual_sha256=hashlib.sha256((ROOT / "DUAL.json").read_bytes()).hexdigest(),
        integer_costs=cost,
        words=results,
        helper_widths=dict(inventory),
        bin_stock=dict(stock),
        packing_excess_lower=str(D),
        minimum_pattern_slack=str(slack),
        total_rank_mass=mass,
        moment_lower=str(lower),
        margin=str(lower - 1),
        controls=tests,
        rejected=rejected,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", type=Path)
    a = ap.parse_args()
    if a.record:
        F.need(not a.record.exists(), "receipt already exists")
    result = run()
    if a.record:
        with a.record.open("x") as f:
            f.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        F.need(
            canonical(result) == canonical(read(ROOT / "EXPECTED.json")),
            "receipt mismatch",
        )
    print(
        "PASS_T74_VARIABLE_FRAME_CAP",
        result["threshold"],
        "margin",
        float(Q(result["margin"])),
        "max_table_states",
        max(
            c["max_table_states"]
            for w in result["words"].values()
            for c in w["components"]
        ),
    )


if __name__ == "__main__":
    main()

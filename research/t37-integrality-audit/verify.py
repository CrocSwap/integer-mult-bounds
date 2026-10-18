#!/usr/bin/env python3
"""Audit integer consequences of the fixed-U8 signed-dual bound.

New bin enumeration, lattice reasoning and residue certificate; the pinned
base-two rational transcendental engine is reused, not claimed independent.
All proof-relevant checks remain enabled under -O. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import argparse
import hashlib
import heapq
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 10**24
Z = Q("0.001664727258740678855773")
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPS = ((8, 672, 2), (16, 448, 4), (32, 448, 8), (48, 448, -13))
INVENTORY = (80, 32, 54, 122, 216)
ENGINE = "research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def floor_tick(x):
    return (x * SCALE).__floor__()


def ceil_tick(x):
    return (x * SCALE).__ceil__()


def source_check():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for name, digest in manifest["sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "source drift: " + name)
    return manifest


def bins():
    """Depth-first traversal of count vectors, independent of original loops."""
    upper = {}
    count = 0

    def visit(index, remaining, score):
        nonlocal count
        if index == len(WIDTHS):
            count += 1
            upper[remaining] = max(upper.get(remaining, -10**9), score)
            return
        for multiplicity in range(remaining // WIDTHS[index] + 1):
            visit(index + 1, remaining - WIDTHS[index] * multiplicity,
                  score + PRICES[index] * multiplicity)

    for cap, _, bonus in CAPS:
        visit(0, cap, bonus)
    require(count == 1163, "complete legal-bin coverage")
    return dict(sorted(upper.items())), count


def intervals(upper):
    spec = importlib.util.spec_from_file_location("t37_retained_base_two", ROOT / ENGINE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    phi = {}
    for r in upper:
        if r:
            lo, hi = engine.log_bounds(Q(73, r))
            phi[r] = (r * engine.exp_bounds(Z * lo)[0],
                      r * engine.exp_bounds(Z * hi)[1])
    c = {r: (48 * phi[r][0] - r * phi[48][1],
             48 * phi[r][1] - r * phi[48][0])
         for r in phi if r < 48}
    lam = (c[1][0] / 925, c[1][1] / 925)
    delta = {}
    for r, pair in c.items():
        if r == 1:
            continue
        v = 48 * upper[r] + 13 * r
        # Multiplication reverses interval endpoints for negative v.
        products = (v * lam[0], v * lam[1])
        delta[r] = (pair[0] - max(products), pair[1] - min(products))
    require(lam[0] > 0, "positive support multiplier")
    require(all(lo > 0 for lo, _ in delta.values()), "strict off-support costs")
    require(all(delta[2][1] < lo for r, (lo, _) in delta.items() if r != 2),
            "rank two uniquely minimizes the off-support penalty")
    require(delta[2][1] < 1200 * lam[0], "rank two beats one slack unit")
    return lam, delta


def graph(upper, lam, delta):
    edges = []
    for r, (lo, hi) in sorted(delta.items()):
        v = 48 * upper[r] + 13 * r
        require(v % 25 == 0, "integer width-price lattice")
        edges.append(dict(label="rank_" + str(r), rank=r, step=(v // 25) % 37,
                          lower=floor_tick(lo), upper=ceil_tick(hi)))
    edges.append(dict(label="slack", rank=None, step=(-48) % 37,
                      lower=floor_tick(1200 * lam[0]), upper=ceil_tick(1200 * lam[1])))
    require(all(e["lower"] > 0 for e in edges), "positive graph edges")
    return edges


def shortest_paths(edges):
    distance = [None] * 37
    paths = [None] * 37
    distance[0], paths[0] = 0, []
    queue = [(0, 0)]
    while queue:
        value, a = heapq.heappop(queue)
        if value != distance[a]:
            continue
        for e in edges:
            b = (a + e["step"]) % 37
            candidate = value + e["lower"]
            if distance[b] is None or candidate < distance[b]:
                distance[b] = candidate
                paths[b] = paths[a] + [e["label"]]
                heapq.heappush(queue, (candidate, b))
    require(all(x is not None for x in distance), "all 37 states reachable")
    return distance, paths


def check_potential(potential, certificate_edges, true_edges):
    require(certificate_edges == true_edges, "complete, correctly rounded graph edges")
    require(len(potential) == 37 and potential[0] == 0, "normalized 37-state potential")
    checks = 0
    for a in range(37):
        for e in true_edges:
            require(potential[(a + e["step"]) % 37] <= potential[a] + e["lower"],
                    "Bellman edge inequality")
            checks += 1
    return checks


def check_profile(T, profile, upper):
    require(type(T) is int and T > 0, "positive integer replicas")
    require(all(type(r) is int and r in upper and type(n) is int and n >= 0
                for r, n in profile.items()), "nonnegative integer attainable counts")
    require(sum(r * n for r, n in profile.items()) == 14382 * T, "rank mass")
    require(sum(upper[r] * n for r, n in profile.items()) >= -3892 * T,
            "signed credit")
    slack = sum((48 * upper[r] + 13 * r) * n for r, n in profile.items()) - 150 * T
    require(slack >= 0 and slack % 1200 == 0, "1200-unit slack lattice")
    return slack


def witnesses(paths, edges, upper, potential):
    lookup = {e["label"]: e for e in edges}
    rows = []
    for residue in range(37):
        T = residue or 37
        path = paths[(6 * T) % 37]
        off = Counter(lookup[label]["rank"] for label in path if label != "slack")
        k = path.count("slack")
        numerator = 6 * T + 48 * k - sum((48 * upper[r] + 13 * r) // 25 * n
                                        for r, n in off.items())
        require(numerator % 37 == 0, "integer rank-one completion")
        n1 = numerator // 37
        mass = 14382 * T - n1 - sum(r * n for r, n in off.items())
        require(mass % 48 == 0, "integer rank-48 completion")
        profile = dict(off)
        profile.update({1: n1, 48: mass // 48})
        profile = {r: n for r, n in sorted(profile.items()) if n}
        slack = check_profile(T, profile, upper)
        require(slack == 1200 * k, "path credit slack")
        lower = potential[(6 * T) % 37]
        high = sum(lookup[label]["upper"] for label in path)
        require(lower == sum(lookup[label]["lower"] for label in path), "attaining lower-weight path")
        require(lower <= high and high - lower <= 10, "narrow exact relaxation sandwich")
        rows.append(dict(replica_residue=residue, first_positive_T=T, path=path,
                         profile={str(r): n for r, n in profile.items()},
                         slack=slack, gap_lower_ticks=lower, witness_gap_upper_ticks=high))
    return rows


def controls(upper, potential, edges):
    rejected = []

    def reject(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    fractional = {1: Q(6, 37), 48: Q(11086, 37)}
    require(sum(r * n for r, n in fractional.items()) == 14382,
            "fractional control mass premise")
    require(sum(upper[r] * n for r, n in fractional.items()) == -3892,
            "fractional control credit premise")
    reject("fractional_equality_at_T1", lambda: check_profile(1, fractional, upper))
    require(48 * 2397 == 14382 * 8, "credit control preserves mass")
    reject("drop_credit_at_T8", lambda: check_profile(8, {48: 2397}, upper))
    require(upper[1] + 299 * upper[48] >= -3892, "mass control preserves credit")
    reject("drop_mass_at_T1", lambda: check_profile(1, {1: 1, 48: 299}, upper))
    require(check_profile(1, {30: 1, 48: 299}, upper) == 0,
            "strictness control preserves integer mass and credit")
    target = 65 % 37
    altered = potential[:]
    altered[target] += SCALE * 100
    reject("inflate_seeded_residue_potential", lambda: check_potential(altered, edges, edges))
    reject("omit_slack_edge", lambda: check_potential(potential, edges[:-1], edges))
    negative = next(e for e in edges if e["rank"] is not None
                    and 48 * upper[e["rank"]] + 13 * e["rank"] < 0)
    reject("omit_negative_credit_rank", lambda: check_potential(
        potential, [e for e in edges if e != negative], edges))
    corrupt = deepcopy(edges)
    corrupt[0]["lower"] += 1
    reject("overstate_certified_edge", lambda: check_potential(potential, corrupt, edges))
    corrupt = deepcopy(edges)
    next(e for e in corrupt if e["rank"] == 30)["lower"] = 0
    reject("erase_strict_rank30_penalty", lambda: check_potential(potential, corrupt, edges))
    return dict(rejected=rejected,
                fractional_equality={"T": 1, "n1": "6/37", "n48": "11086/37"},
                credit_omission={"T": 8, "n48": 2397, "credit_shortfall": 1200},
                mass_omission={"T": 1, "n1": 1, "n48": 299, "mass_shortfall": 29},
                strictness_omission={"T": 1, "n30": 1, "n48": 299, "credit_slack": 0},
                seeded_mutation_residue=target)


def run():
    sources = source_check()
    upper, count = bins()
    mass = sum(cap * n for cap, n, _ in CAPS) - 9 * sum(w * n for w, n in zip(WIDTHS, INVENTORY))
    signed = sum(n * b for _, n, b in CAPS) + 9 * sum(p * n for p, n in zip(PRICES, INVENTORY))
    require((mass, signed, upper[0], upper[48]) == (14382, -3892, 0, -13), "fixed inventory")
    require(all((48 * b + 13 * cap) % 25 == 0 for cap, _, b in CAPS), "bin bonus lattice")
    require(all((48 * p - 13 * w) % 25 == 0 for p, w in zip(PRICES, WIDTHS)), "helper lattice")
    require(all((48 * u + 13 * r) % 25 == 0 for r, u in upper.items()), "all attained rank credits")
    lam, delta = intervals(upper)
    edges = graph(upper, lam, delta)
    potential, paths = shortest_paths(edges)
    checked = check_potential(potential, edges, edges)
    rows = witnesses(paths, edges, upper, potential)
    require(check_profile(29, {1: 4, 2: 1, 48: 8689}, upper) == 0, "sharp uniform gap witness")
    require(all(row["gap_lower_ticks"] > 0 for row in rows if row["replica_residue"]),
            "positive penalty in every nonzero replica residue")
    require(all(row["slack"] == 0 for row in rows), "reported witnesses have zero slack")
    return dict(status="PASS_T37_INTEGRALITY_AUDIT", base_commit=sources["base_commit"],
                endpoint=str(Z), arithmetic_engine="pinned retained base-two rational engine",
                tick_denominator=SCALE, legal_bin_patterns=count,
                upper={str(r): u for r, u in upper.items()},
                mass_per_replica=mass, signed_price_per_replica=signed,
                credit_divisor=25, slack_modulus=1200,
                uniform_gap=dict(exact_expression="c(2)-26*c(1)/37",
                                 lower_ticks=floor_tick(delta[2][0]), upper_ticks=ceil_tick(delta[2][1]),
                                 sharp_relaxed_profile={"T": 29, "1": 4, "2": 1, "48": 8689},
                                 full_moment_denominator_per_T=48 * 73 * 896),
                edges=edges, potential_ticks=potential, checked_edge_inequalities=checked,
                residue_certificates=rows, negative_controls=controls(upper, potential, edges),
                source_sha256=sources["sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; existing files refused")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        require(result == expected, "complete receipt differs from EXPECTED.json")
    print(result["status"] + ": 1163 bins; 37 residue certificates; "
          + str(result["checked_edge_inequalities"]) + " edge inequalities; "
          + str(len(result["negative_controls"]["rejected"]))
          + " rejection controls; no new kappa")


if __name__ == "__main__":
    main()

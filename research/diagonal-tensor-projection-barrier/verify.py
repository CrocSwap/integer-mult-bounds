#!/usr/bin/env python3
"""Replay the fixed PR117 carrier word and its diagonal path defects.

Copyright 2026 Jose Manuel (@jmbarrancoml). Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
The matching and physical assignment port icekylinx's algorithms; the DAG
and frame definitions belong to eumemic/PR117. See NOTICE.md.
"""
from collections import deque
from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
DAG = ROOT / "references/three-stage-cover/pr117/dag.json.gz"
DAG_HASH = "3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b"
MATCH_HASH = "ec8411359cdada71bcce5db2b77522df15af7f8f0120fe45febdc86121e4a9a6"
EXPECTED = [6048, 5982, 6046, 6176, 6046, 6084, 6026, 6048,
            6004, 6082, 6048, 6152, 6112, 6134, 6114, 6046,
            6112, 6046, 6114, 6042, 6116, 6046, 6114, 6046]
FULL = (1 << 24) - 1
ROOT_USE = 1 << 31


def require(ok, message):
    if not ok:
        raise ValueError(message)


def build(w):
    require((w["h"], w["central_disjoint"], w["center_denominator"]) == (24, 24, 21), "producer parameters")
    triples = [sum(1 << i for i in t) for t in combinations(range(24), 3)]
    require(w["v"] == len(triples), "input count")
    args = [(0, 0)] * (len(triples) + 1)
    supports = [0] + [1 << i for i in range(len(triples))]
    core, cover = [0] + triples, [0] + triples
    diagonal = [0] + triples
    ranks = [0] + [1] * len(triples)
    kinds = [0] + [1] * len(triples)
    require(len(w["args"]) % 2 == 0, "operand pairs")
    for a, b in zip(w["args"][::2], w["args"][1::2]):
        x = len(args)
        require(0 < a < x and 0 < b < x, "operand order")
        require(not supports[a] & supports[b], "overlapping summands")
        args.append((a, b))
        supports.append(supports[a] | supports[b])
        core.append(core[a] & core[b])
        cover.append(cover[a] | cover[b])
        kind = 1 if core[x].bit_count() >= 2 else 2
        kinds.append(kind)
        ranks.append(supports[x].bit_count() if kind == 1 else cover[x].bit_count())
        # Common-pair triples are orthonormal. Their projector diagonal is
        # the XOR of their triple vectors, not their coordinate union.
        diagonal.append(diagonal[a] ^ diagonal[b] if kind == 1 else cover[x])
    point = [sum(1 << j for j, t in enumerate(triples) if t >> i & 1) for i in range(24)]
    all_inputs = (1 << len(triples)) - 1
    require(len(w["D"]) == 2024 and len(w["P"]) == 6072 and len(w["A"]) == 24, "root counts")
    for t, x in zip(triples, w["D"]):
        excluded = 0
        for i in range(24):
            if t >> i & 1:
                excluded |= point[i]
        require(0 < x < len(args) and supports[x] == all_inputs ^ excluded, "disjoint root")
    stars = [(a, b, i) for a, b in combinations(range(24), 2) for i in range(24) if i not in (a, b)]
    for (a, b, i), x in zip(stars, w["P"]):
        require(0 < x < len(args) and supports[x] == point[a] & point[b] & ~point[i], "pair-star root")
    for i, x in enumerate(w["A"]):
        require(0 < x < len(args) and supports[x] == all_inputs ^ point[i], "centre root")
    roots = w["D"] + w["P"] + w["A"]
    active = set(roots)
    for x in range(len(args) - 1, 0, -1):
        if x in active and args[x][0]:
            active.update(args[x])
    uses = [[] for _ in args]
    for x in sorted(active):
        if args[x][0]:
            for j, y in enumerate(args[x]):
                uses[y].append(2 * x + j)
    for j, x in enumerate(roots):
        uses[x].append(ROOT_USE | j)
    return dict(args=args, core=core, cover=cover, diagonal=diagonal,
                ranks=ranks, kinds=kinds, roots=roots, active=active, uses=uses)


def target(d, use):
    return d["roots"][use & (ROOT_USE - 1)] if use & ROOT_USE else use // 2


def legal(d, donor, use):
    x = target(d, use)
    r = d["ranks"]
    later_id = len(d["args"]) + (use & (ROOT_USE - 1)) if use & ROOT_USE else x
    if (r[donor], donor) >= (r[x], later_id):
        return False
    kinds, core, cover = d["kinds"], d["core"], d["cover"]
    if kinds[donor] == kinds[x] == 1:
        return not (core[x] & ~core[donor] or cover[donor] & ~cover[x])
    return kinds[x] == 2 and not cover[donor] & ~cover[x]


def matching(d):
    adjacency = {}
    for x in sorted(d["active"]):
        if d["args"][x][0]:
            edges = [u for value in d["args"][x] for u in d["uses"][value] if legal(d, x, u)]
            if edges:
                adjacency[x] = edges
    left, right = {}, {}
    infinity = len(d["args"])
    while True:
        distance = {x: infinity if x in left else 0 for x in adjacency}
        queue = deque(x for x in adjacency if x not in left)
        shortest = infinity
        while queue:
            x = queue.popleft()
            if distance[x] >= shortest:
                continue
            for use in adjacency[x]:
                y = right.get(use)
                if y is None:
                    shortest = distance[x] + 1
                elif distance[y] == infinity:
                    distance[y] = distance[x] + 1
                    queue.append(y)
        if shortest == infinity:
            break

        def augment(x):
            for use in adjacency[x]:
                y = right.get(use)
                if (y is None and distance[x] + 1 == shortest) or (y is not None and distance[y] == distance[x] + 1 and augment(y)):
                    left[x], right[use] = use, x
                    return True
            distance[x] = infinity
            return False

        require(any([augment(x) for x in adjacency if x not in left]), "matching progress")
    arcs = sorted(left.items())
    require(len(arcs) == 71185, "matching count")
    require(sha256(json.dumps(arcs, separators=(",", ":")).encode()).hexdigest() == MATCH_HASH, "matching receipt")
    return arcs


def validate_arcs(d, arcs):
    require(len(arcs) == 71185, "matching count")
    require(len({x for x, _ in arcs}) == len(arcs), "repeated donor")
    require(len({u for _, u in arcs}) == len(arcs), "repeated use")
    for x, use in arcs:
        require(x in d["active"] and d["args"][x][0], "inactive donor")
        require(any(use in d["uses"][v] for v in d["args"][x]), "unrelated use")
        require(legal(d, x, use), "illegal carrier arc")


def paths(d, arc_list):
    validate_arcs(d, arc_list)
    arcs = dict(arc_list)
    incoming = {use for _, use in arc_list}
    assignment, result = {}, []
    operations = 0
    diag = d["diagonal"]
    # The matcher enumerates uses in node order. The physical compiler
    # enumerates nonterminal uses in frame-rank order, then root uses.
    # Keep those distinct orders: changing the latter changes carriers.
    physical_uses = {}
    for x in d["active"]:
        ordinary = [u for u in d["uses"][x] if not u & ROOT_USE]
        ordinary.sort(key=lambda u: (d["ranks"][u // 2], u // 2))
        physical_uses[x] = ordinary + [u for u in d["uses"][x] if u & ROOT_USE]

    def touch(role, value):
        if result[role][-1] != value:
            result[role].append(value)

    for x in sorted(d["active"], key=lambda node: (d["ranks"][node], node)):
        aa, bb = d["args"][x]
        if aa:
            p, o = assignment[2 * x], assignment[2 * x + 1]
            if x in arcs:
                use = arcs[x]
                value = target(d, use) if use & ROOT_USE else d["args"][use // 2][use & 1]
                if value == aa:
                    p, o = o, p
                require(value in (aa, bb) and use not in assignment, "carrier assignment")
                assignment[use] = o
            touch(p, diag[x])
            touch(o, diag[x])
            operations += 1
        else:
            p = len(result)
            result.append([diag[x]])
        free = [use for use in physical_uses[x] if use not in incoming]
        require(bool(free), "unmatched outgoing use")
        for j, use in enumerate(free):
            require(use not in assignment, "reused slot")
            if j == 0:
                assignment[use] = p
            else:
                assignment[use] = len(result)
                result.append([diag[x]])
                touch(p, diag[x])
                operations += 1
    for j, x in enumerate(d["roots"][:-24]):
        triple = d["core"][x] | (FULL ^ d["cover"][x])
        require(triple.bit_count() == 3, "ordinary target cap")
        touch(assignment[ROOT_USE | j], FULL ^ triple)
    require((len(result), operations) == (28705, 118451), "physical word counts")
    return result


def defects(role_paths):
    answer = [0] * 24
    for path in role_paths:
        for a, b in zip(path, path[1:]):
            change = a ^ b
            for i in range(24):
                answer[i] += (change >> i) & 1
        net = path[0] ^ path[-1]
        for i in range(24):
            answer[i] -= (net >> i) & 1
    require(min(answer) >= 0, "negative path defect")
    return answer


def rank(rows):
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


def controls(w, d, arcs, role_paths):
    rejected = 0

    def reject(function):
        nonlocal rejected
        try:
            function()
        except ValueError:
            rejected += 1
        else:
            raise ValueError("corruption survived")

    bad = dict(w, center_denominator=19)
    reject(lambda: build(bad))
    bad = dict(w, args=list(w["args"]))
    bad["args"][1] = bad["args"][0]
    reject(lambda: build(bad))
    bad = dict(w, D=[1] + w["D"][1:])
    reject(lambda: build(bad))
    reject(lambda: validate_arcs(d, arcs[:-1]))
    bad_arcs = list(arcs)
    bad_arcs[-1] = (bad_arcs[0][0], bad_arcs[-1][1])
    reject(lambda: validate_arcs(d, bad_arcs))
    bad_arcs = list(arcs)
    bad_arcs[-1] = (bad_arcs[-1][0], bad_arcs[0][1])
    reject(lambda: validate_arcs(d, bad_arcs))
    # Remove a genuine backtracking incidence, which understates paid work.
    for role, path in enumerate(role_paths):
        found = next((j for j in range(1, len(path) - 1)
                      if (path[j - 1] ^ path[j]) & (path[j] ^ path[j + 1])), None)
        if found is not None:
            changed = list(role_paths)
            changed[role] = path[:found] + path[found + 1:]
            reject(lambda: require(defects(changed) == EXPECTED, "omitted incidence"))
            break
    require(rejected == 7, "negative-control coverage")
    for k in range(1, 9):
        for wvec in range(1 << k):
            rows = [(1 << i) ^ (wvec if wvec >> i & 1 else 0) for i in range(k)]
            require(rank(rows) == k - wvec.bit_count() % 2, "data endpoint rank")
    isometries = 0
    odd = [x for x in range(16) if x.bit_count() % 2]
    for k in range(1, 5):
        for rows in product(odd, repeat=k):
            if any((a & b).bit_count() % 2 for a, b in combinations(rows, 2)):
                continue
            isometries += 1
            for y in range(1 << k):
                image = 0
                linear = 0
                for i, row in enumerate(rows):
                    if y >> i & 1:
                        image ^= row
                        linear += row.bit_count() - 1
                require((image.bit_count() - y.bit_count() - linear) % 4 == 0, "Pauli phase correction")
    require(isometries > 0, "isometry controls")
    return dict(rejected_corruptions=rejected, small_isometries=isometries)


def main():
    raw = DAG.read_bytes()
    require(sha256(raw).hexdigest() == DAG_HASH, "source drift")
    witness = json.loads(gzip.decompress(raw))
    data = build(witness)
    arcs = matching(data)
    role_paths = paths(data, arcs)
    result = defects(role_paths)
    require(result == EXPECTED, "coordinate defect census")
    pair_count = comb(23, 2) * comb(21, 2)
    gain = 2 * comb(23, 2) ** 3
    excess = pair_count * min(result)
    require((pair_count, gain, excess, excess - gain) ==
            (53130, 32388554, 317823660, 285435106), "integer budget")
    require(excess > gain, "positive obstruction margin")
    checked = controls(witness, data, arcs, role_paths)
    receipt = dict(roles=28705, middle_adds=118451, matching_arcs=len(arcs),
                   singleton_defects=result, pair_count=pair_count,
                   excess_per_nonzero_column=excess, data_gain_per_odd_column=gain,
                   margin_per_nonzero_column=excess - gain, **checked)
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_DIAGONAL_TENSOR_PROJECTION_BARRIER")


if __name__ == "__main__":
    main()

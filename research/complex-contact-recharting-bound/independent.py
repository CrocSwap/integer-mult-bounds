#!/usr/bin/env python3
"""Independent source reconstruction and exhaustive mixed-corridor review."""
from __future__ import annotations
from collections import Counter, defaultdict, deque
from itertools import product
from pathlib import Path
import gzip, hashlib, json
HERE = Path(__file__).resolve().parent
MAIN = "e54523517d0f03e58352e647c403a5af3e525a57"
NATIVE = HERE / "inputs/pr7481-WORD.json.gz"
NATIVE_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
CONTRACT_PATH = "research/shared-wire-split-composition/independent.py"
CONTRACT_SHA = "21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874"
FULL = (1 << 512) - 1


def need(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)

def span(vectors) -> int:
    values = {0}
    for v in vectors:
        values |= {x ^ v for x in tuple(values)}
    return sum(1 << x for x in values)

def basis_of(mask: int) -> list[int]:
    pivots: dict[int, int] = {}
    for v in range(512):
        if not ((mask >> v) & 1):
            continue
        x = v
        for p in sorted(pivots, reverse=True):
            if (x >> p) & 1:
                x ^= pivots[p]
        if x:
            pivots[x.bit_length() - 1] = x
    return [pivots[p] for p in sorted(pivots, reverse=True)]

def dim(mask: int) -> int:
    count = mask.bit_count()
    need(count and count & (count - 1) == 0, "subspace cardinality is a power of two")
    return count.bit_length() - 1

def join(a: int, b: int) -> int:
    return span(basis_of(a) + basis_of(b))

def subset(a: int, b: int) -> bool:
    return (a & b) == a

class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, a: int) -> int:
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[a] = b

def rebuild_visits(word: dict):
    n = int(word["public"]) + int(word["owned_fields"])
    visits: list[dict] = []
    current: list[int | None] = [None] * n
    dsu = DSU(n + len(word["program"]))
    move_visit_pairs: dict[int, tuple[int, int, bool]] = {}

    def new(role: int, chart: int, entrance, frozen):
        vid = len(visits)
        visits.append({"id": vid, "owner": role, "chart": chart,
                       "entrance": entrance, "exit": None,
                       "frozen": frozen, "scalar_events": []})
        current[role] = vid
        return vid

    for role, chart in enumerate(word["initial"]):
        new(role, int(chart), None, "public entrance")

    for event_id, event in enumerate(word["program"]):
        op, role = event[:2]
        if op == "INIT":
            need(current[role] is None, "INIT starts a retired owned role")
            new(role, int(event[2]), None, "INIT")
        elif op == "CLEAR":
            vid = current[role]
            need(vid is not None and visits[vid]["chart"] == int(event[2]), "CLEAR closes active visit")
            visits[vid]["frozen"] = "CLEAR"
            current[role] = None
        elif op == "MOVE":
            src, dst, owned = int(event[2]), int(event[3]), bool(event[4])
            vid = current[role]
            need(vid is not None and visits[vid]["chart"] == src, "MOVE source chart matches active visit")
            need(owned == (role >= int(word["public"])), "MOVE ownership bit")
            visits[vid]["exit"] = event_id
            nxt = new(role, dst, event_id, None)
            move_visit_pairs[event_id] = (vid, nxt, owned)
        elif op in ("ADD", "COPY", "SCALE"):
            target_chart = int(event[-1])
            target_vid = current[role]
            need(target_vid is not None and visits[target_vid]["chart"] == target_chart,
                 "scalar target visit chart")
            visits[target_vid]["scalar_events"].append(event_id)
            if op in ("ADD", "COPY"):
                source_role = int(event[2])
                source_vid = current[source_role]
                need(source_vid is not None and visits[source_vid]["chart"] == target_chart,
                     "ADD/COPY source cochart")
                visits[source_vid]["scalar_events"].append(event_id)
                dsu.union(target_vid, source_vid)
        else:
            raise AssertionError(f"unexpected opcode: {op}")

    for role in range(int(word["public"])):
        vid = current[role]
        need(vid is not None and visits[vid]["chart"] == int(word["final"][role]),
             "public exit chart")
        visits[vid]["frozen"] = "public exit"

    groups_by_root: dict[int, list[dict]] = {}
    for visit in visits:
        root = dsu.find(visit["id"])
        groups_by_root.setdefault(root, []).append(visit)
    groups = list(groups_by_root.values())
    visit_to_component = {v["id"]: i for i, group in enumerate(groups) for v in group}
    component_chart = []
    component_frozen = []
    for i, group in enumerate(groups):
        chart_masks = {span(word["frames"][v["chart"]]) for v in group}
        need(len(chart_masks) == 1, f"component {i} is cocharted")
        component_chart.append(next(iter(chart_masks)))
        component_frozen.append(any(v["frozen"] for v in group))
    moves = []
    for event_id in sorted(move_visit_pairs):
        old_vid, new_vid, owned = move_visit_pairs[event_id]
        old_comp, new_comp = visit_to_component[old_vid], visit_to_component[new_vid]
        moves.append({"source_event": event_id, "from_component": old_comp,
                      "to_component": new_comp,
                      "owner": visits[old_vid]["owner"], "owned": owned})
    return visits, groups, component_chart, component_frozen, moves

def verify_contract_and_move_geometry(word, charts, moves):
    contract = (HERE / "inputs/CONTRACT-SOURCE.py").read_bytes()
    digest = hashlib.sha256(contract).hexdigest()
    need(digest == CONTRACT_SHA, "canonical public-MOVE contract pin")
    code = contract.decode()
    public_rule = "assert (frames[a]<frames[b]) if not owned else (frames[a]<frames[b] or frames[b]<frames[a])"
    need(public_rule in code, "strict public ascent / either owned direction rule")

    types = Counter()
    for e in moves:
        a, b = charts[e["from_component"]], charts[e["to_component"]]
        if not e["owned"]:
            need(subset(a, b) and a != b, "public MOVE is strictly ascending")
            types["public_ascending"] += 1
        else:
            need((subset(a, b) and a != b) or (subset(b, a) and b != a),
                 "owned MOVE endpoints are strictly comparable")
            types["owned_ascending" if dim(a) < dim(b) else "owned_descending"] += 1
    need(types == Counter({"public_ascending": 6232, "owned_ascending": 23,
                          "owned_descending": 24}), "direction census")
    return {"canonical_main": MAIN, "contract_path": CONTRACT_PATH,
            "contract_sha256": digest, "move_directions": dict(types)}

def derive_caps_and_floors(charts, frozen, moves):
    n = len(charts)
    dims = [dim(x) for x in charts]
    upper = [set() for _ in charts]
    lower = [set() for _ in charts]
    for e in moves:
        if e["owned"]:
            continue
        a, b = e["from_component"], e["to_component"]
        upper[a].add(b)
        lower[b].add(a)

    caps = [FULL] * n
    for i in sorted(range(n), key=lambda j: dims[j], reverse=True):
        if frozen[i]:
            caps[i] = charts[i]
        else:
            for j in upper[i]:
                caps[i] &= caps[j]
        need(subset(charts[i], caps[i]), f"component {i} original is below its public cap")

    floors = [charts[i] if frozen[i] else 1 for i in range(n)]
    for i in sorted(range(n), key=lambda j: dims[j]):
        if not frozen[i]:
            for j in lower[i]:
                floors[i] = join(floors[i], floors[j])
        need(subset(floors[i], charts[i]), f"component {i} public floor below original")

    for e in moves:
        if not e["owned"]:
            a, b = e["from_component"], e["to_component"]
            need(subset(caps[a], caps[b]), "cap preserves public edge order")
            need(subset(floors[a], floors[b]), "floor preserves public edge order")
    need(all(subset(floors[i], charts[i]) and subset(charts[i], caps[i]) for i in range(n)),
         "floor <= original <= cap")
    free = {i for i in range(n) if not frozen[i] and caps[i] != charts[i]}
    shrink = {i for i in range(n) if not frozen[i] and floors[i] != charts[i]}
    owned_touched = {i for e in moves if e["owned"]
                     for i in (e["from_component"], e["to_component"])}
    owned_internal = {i for i in owned_touched if not frozen[i]}
    need(free.isdisjoint(owned_touched), "public caps lock every owned MOVE endpoint")
    need(all(caps[i] == charts[i] for i in owned_touched), "owned MOVE charts fixed under growth")
    need(owned_internal == {482, 883}, "two internal owned-containing components")
    need(free.isdisjoint(shrink), "no component has both strict growth and strict shrink room")
    need(all(floors[i] == charts[i] or caps[i] == charts[i] for i in range(n)),
         "each component's full corridor is one-sided around its original chart")
    return dims, upper, lower, caps, floors, free, shrink, owned_touched

def interval_subspaces(floor: int, ceiling: int) -> list[int]:
    need(subset(floor, ceiling), "interval endpoints nested")
    complement = []
    current = floor
    for vector in basis_of(ceiling):
        if not ((current >> vector) & 1):
            complement.append(vector)
            current = join(current, span([vector]))
    need(current == ceiling, "quotient basis spans interval")
    quotient_vectors = []
    for bits in range(1, 1 << len(complement)):
        v = 0
        for j, q in enumerate(complement):
            if (bits >> j) & 1:
                v ^= q
        quotient_vectors.append(v)
    candidates = {floor}
    for v in quotient_vectors:
        extension = join(floor, span([v]))
        candidates |= {join(old, extension) for old in tuple(candidates)}
    need(all(subset(floor, x) and subset(x, ceiling) for x in candidates), "all interval choices valid")
    return sorted(candidates, key=lambda x: (dim(x), x))

def factors_for(variable: set[int], moves: list[dict]) -> list[list[int]]:
    adjacent = {i: set() for i in variable}
    for e in moves:
        a, b = e["from_component"], e["to_component"]
        if a in variable and b in variable:
            adjacent[a].add(b); adjacent[b].add(a)
    unseen = set(variable)
    factors = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        stack = [start]
        factor = {start}
        while stack:
            a = stack.pop()
            for b in adjacent[a] & unseen:
                unseen.remove(b); factor.add(b); stack.append(b)
        factors.append(sorted(factor))
    return factors

def enumerate_subfamily(charts, dims, moves, variable, low, high):
    domains = {i: interval_subspaces(low[i], high[i]) for i in variable}
    factors = factors_for(variable, moves)
    cartesian, legal_total = 0, 0
    factor_receipts = []
    for factor in factors:
        incident = [e for e in moves if e["from_component"] in factor or e["to_component"] in factor]
        old_paid = Counter(abs(dims[e["from_component"]] - dims[e["to_component"]]) for e in incident)
        maxima = [-10**9] * 9
        states = legal = 0
        profiles = []
        for picked in product(*(domains[i] for i in factor)):
            states += 1
            repl = dict(zip(factor, picked))
            new_frame = lambda i: repl.get(i, charts[i])
            okay = True
            for e in incident:
                left, right = new_frame(e["from_component"]), new_frame(e["to_component"])
                if e["owned"]:
                    okay &= subset(left, right) or subset(right, left)
                else:
                    okay &= subset(left, right)
            if not okay:
                continue
            legal += 1
            new_paid = Counter(abs(dim(new_frame(e["from_component"])) -
                                   dim(new_frame(e["to_component"]))) for e in incident)
            delta = {r: new_paid[r] - old_paid[r] for r in new_paid.keys() | old_paid.keys()
                     if new_paid[r] != old_paid[r]}
            savings = [-sum(c * min(r, k) for r, c in delta.items() if r)
                       for k in range(1, 10)]
            maxima = [max(x, y) for x, y in zip(maxima, savings)]
            profiles.append({"choice_dimensions": [dim(x) for x in picked],
                             "paid_delta": {str(r): c for r, c in sorted(delta.items()) if c},
                             "extreme_savings": savings})
        need(legal > 0, f"factor {factor} has legal original choice")
        need(maxima == [0] * 9, f"factor {factor} has no positive concave-generator saving")
        cartesian += states; legal_total += legal
        factor_receipts.append({"factor": factor, "cartesian": states, "legal": legal,
                                "maxima_min_r_k": maxima, "profiles": profiles})
    # Check factorization completeness: no move joins two distinct variable factors.
    comp_of = {i: j for j, group in enumerate(factors) for i in group}
    need(all(e["from_component"] not in variable or e["to_component"] not in variable or
             comp_of[e["from_component"]] == comp_of[e["to_component"]] for e in moves),
         "no omitted cross-factor MOVE")
    # All actual MOVE endpoints are checked: public orientation and owned
    # bidirectional comparability.  Equality is an optimistic zero-rank limit.
    return {"variable_components": len(variable), "factor_count": len(factors),
            "cartesian_states": cartesian, "legal_states": legal_total,
            "all_9_extreme_cone_maxima_zero": True, "factors": factor_receipts}

def audit_corridors(charts, dims, frozen, moves, floors, caps, free, shrink):
    variable = {i for i in range(len(charts)) if not frozen[i] and floors[i] != caps[i]}
    need(variable == free | shrink and free.isdisjoint(shrink), "corridor variable partition")
    need(len(variable) == 96, "full floor-to-cap variable count")
    mixed_domains = {i: interval_subspaces(floors[i], caps[i]) for i in variable}
    need(Counter(len(mixed_domains[i]) for i in free) == Counter({2:18,16:2}),
         "growth interval domain cardinalities")
    need(Counter(len(mixed_domains[i]) for i in shrink) == Counter({2:73,5:3}),
         "shrink interval domain cardinalities")

    grow = enumerate_subfamily(charts, dims, moves, free, charts, caps)
    shrink_result = enumerate_subfamily(charts, dims, moves, shrink, floors, charts)
    mixed = enumerate_subfamily(charts, dims, moves, variable, floors, caps)
    need((grow["factor_count"], grow["cartesian_states"], grow["legal_states"]) == (18,68,66),
         "independent pure-growth factor census")
    need((shrink_result["factor_count"], shrink_result["cartesian_states"], shrink_result["legal_states"]) == (72,163,157),
         "independent pure-shrink factor census")
    need((mixed["factor_count"], mixed["cartesian_states"], mixed["legal_states"]) == (77,253,214),
         "independent combined-corridor factor census")

    # The separate directional families are not enough by themselves: actual
    # MOVE edges connect 13 growth variables to shrink variables.  The combined
    # interval enumeration above places every such pair in one factor.
    cross_edges = [e for e in moves if
                   (e["from_component"] in free and e["to_component"] in shrink) or
                   (e["to_component"] in free and e["from_component"] in shrink)]
    return {"variable_components": len(variable), "growth_variables": len(free),
            "shrink_variables": len(shrink), "cross_direction_edges": len(cross_edges),
            "growth_only": grow, "shrink_only": shrink_result, "combined": mixed}


def run():
    raw = NATIVE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == NATIVE_SHA, "exact independent word pin")
    word = json.loads(gzip.decompress(raw))
    visits, groups, charts, frozen, moves = rebuild_visits(word)
    need(len(groups) == 1517 and len(moves) == 6279, "complete independent source inventory")
    contract = verify_contract_and_move_geometry(word, charts, moves)
    dims, upper, lower, caps, floors, free, shrink, owned = derive_caps_and_floors(charts, frozen, moves)
    corridors = audit_corridors(charts, dims, frozen, moves, floors, caps, free, shrink)
    return {"status": "PASS_INDEPENDENT_COMPLETE_MIXED_CORRIDOR", "source_sha256": NATIVE_SHA,
            "source_contract": contract, "components": len(groups), "visits": len(visits),
            "frozen_components": sum(frozen), "growth_variables": len(free),
            "shrink_variables": len(shrink), "cross_direction_edges": corridors["cross_direction_edges"],
            "combined": corridors["combined"]}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

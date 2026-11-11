#!/usr/bin/env python3
"""Exact bounded literal-source comparisons for contiguous row indexing."""
from collections import Counter
import hashlib
import importlib.util
import json
from math import comb
from functools import lru_cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


I = load("source_index", HERE / "source_index.py")
C = I.C
oracle = HERE / "inputs/finite_dag_audit.py"
need(hashlib.sha256(oracle.read_bytes()).hexdigest() ==
     "f842f0e07ca40a181782a565a381b0ee20c6a4b08b8c2b8a4d5d630381bd1e8e",
     "literal oracle hash")
O = load("source_index_literal_oracle", oracle)


class AmbientRule(O.Rule):
    @property
    def dimension(self):
        return self._ambient


def literal(rule, n):
    old = AmbientRule(rule.roles, rule.rounds, rule.owned)
    object.__setattr__(old, "_ambient", rule.ambient)
    tree = O.IntegerTree(old, n)
    occurrence, units = Counter(), {}
    for unit in tree.units:
        key = (unit["path"], unit["point"])
        units[unit["uid"]] = C.Unit(*key, occurrence[key])
        occurrence[key] += 1
    order = {role: j for j, (role, _) in enumerate(rule.roles)}
    sources = [(units[s["unit"]], s["role"]) for s in tree.sources]
    sources.sort(key=lambda x: (x[0].path, x[0].point, x[0].ordinal, order[x[1]]))
    return sources, tree


def check(rule, n):
    expected, tree = literal(rule, n)
    index = I.SourceIndex(rule, n, replicas=3)
    need(index.size == len(expected), "full literal source count")
    for rank, (unit, role) in enumerate(expected):
        need(index.rank_source(unit, role) == rank, "literal source rank")
        need(index.unrank_source(rank) == (unit, role), "literal source unrank")
        for replica in (0, 2):
            owner = ("flow", replica, "source", unit.path, unit.point, unit.ordinal, role)
            physical = replica*index.size + rank
            need(index.row(owner) == physical and index.owner(physical) == owner,
                 "complete replicated physical row bijection")
    q, G, d = len(index.paid), index.height, len(rule.types)
    bound = 1 + q*comb(G+q-1, q) if G else 1
    need(len(index.total) <= bound, "aggregated-state bound")
    need(sum(map(len, index.point_data)) == comb(G+d, d), "point count")
    return Counter(cases=1, sources=len(expected), states=len(index.total),
                   literal_classes=len(tree.classes), native_units=len(tree.units))


def rejected(action, label):
    try:
        action()
    except (ValueError, AssertionError):
        return label
    raise ValueError("negative control accepted: " + label)


def independent_counts(index):
    """Count ordered target words by product, then subtract incoming units."""
    targets = Counter(k for _, k in index.rule.roles)
    words = [Counter({1: 1})]
    for _ in range(index.height):
        layer = Counter()
        for product, count in words[-1].items():
            for rank, weight in targets.items():
                layer[product*rank] += count*weight
        words.append(layer)
    paid = tuple(r for r, _ in index.rule.rounds)
    W = len(index.rule.roles)

    @lru_cache(None)
    def units(h, rho):
        cap = index.rank // (index.rule.ambient*rho)
        return sum(count for product, count in words[index.height-h].items()
                   if product <= cap)

    @lru_cache(None)
    def subtree(h, rho, previous):
        local = W*units(h, rho) - (units(h-1, rho//previous) if h else 0)
        need(local == index.local[h, rho, previous], "independent local incoming subtraction")
        total = local
        if h < index.height:
            total += sum(subtree(h+1, rho*r, r) for r in paid)
        need(total == index.total[h, rho, previous], "independent subtree count")
        return total

    need(subtree(0, 1, 0) == index.size, "independent source total")
    return subtree.cache_info().currsize


def collision_family():
    """Fixed rule whose same-depth states all hash alike; no timing claim."""
    H, G = sys.hash_info.modulus, 8
    rank = 8*H
    rule = C.Rule((("single", rank),),
                  tuple((H*s, "single") for s in (1, 2, 3, 5, 7)),
                  ambient=rank)
    index = I.SourceIndex(rule, rank**(G+1))
    need(type(index.local) is I.SortedStateTable and
         type(index.total) is I.SortedStateTable and
         type(index.point_data) is list, "deterministic expanding metadata")
    need(index.local._keys is index.total._keys, "shared fixed sorted key vector")
    level_counts = []
    for h in range(1, G+1):
        layer = [state for state in index.total if state[0] == h]
        need(len(layer) == 5*comb(h+3, 4), "exact colliding state family")
        need(all(hash(rho) == hash(last) == 0 for _, rho, last in layer),
             "integer hash collision witness")
        need(all(hash(state) == hash(layer[0]) for state in layer),
             "one state hash per positive depth")
        need(all(index.local[state] == index.total[state] == 0 for state in layer),
             "single target has no nonroot fresh source")
        level_counts.append(len(layer))
    need(index.size == 1 and len(index.total) == 1+5*comb(G+4, 5),
         "collision-family exact count")
    unit, role = index.unrank_source(0)
    need(index.rank_source(unit, role) == 0 and unit.path == () and
         unit.point == (G,) and role == "single", "collision-family row inverse")
    return {"height": G, "hash_modulus": str(H), "states": len(index.total),
            "states_per_positive_depth": level_counts,
            "state_hashes_per_positive_depth": 1, "source_count": 1,
            "lookup": "sorted keys and deterministic binary search"}


def controls():
    r = C.Rule((("small", 2), ("large", 5)), ((1, "small"), (1, "bank")))
    index = I.SourceIndex(r, 10, replicas=2)
    need(index.size == 4, "literal repeated-rank source fixture")
    child = index.total[1, 1, 1]
    bad_total = index.local[0, 1, 0] + child
    out = [rejected(lambda: need(bad_total == index.size, "lost occurrence multiplicity"),
                    "dropped repeated paid occurrence"),
           rejected(lambda: index.unrank_source(index.size), "source upper endpoint"),
           rejected(lambda: index.unrank_source(-1), "negative source index"),
           rejected(lambda: index.owner(2*index.size), "replicated row upper endpoint")]
    owner = index.owner(0)
    out.append(rejected(lambda: index.row(("wrong",)+owner[1:]), "wrong namespace"))
    out.append(rejected(lambda: index.row(owner[:2]+("owned",)+owner[3:]),
                        "owned bank credited as source"))
    matched = C.Unit((0,), (0, 0), 0)
    out.append(rejected(lambda: index.rank_source(matched, "small"),
                        "matched role passed as fresh source"))
    other = I.SourceIndex(C.Rule((("a", 3), ("b", 5)),
                           ((1, "a"), (2, "bank"))), 45)
    need(other.local[2, 2, 1] == 1 and other.local[2, 2, 2] == 0,
         "last-paid-rank distinction fixture")
    out.append(rejected(lambda: need(other.local[2, 2, 1] == other.local[2, 2, 2],
                                     "last rank omitted"), "dropped last paid rank"))
    unit, role = index.unrank_source(0)
    wrong_ordinal = C.Unit(unit.path, unit.point, C.multiplicity(r, unit.point))
    out.append(rejected(lambda: index.rank_source(wrong_ordinal, role),
                        "out-of-range native occurrence"))
    child_sources = [index.unrank_source(rank) for rank in range(index.size)
                     if index.unrank_source(rank)[0].path]
    need(len(child_sources) == 2, "two equal-statistic sibling sources")
    left, right = child_sources
    out.append(rejected(lambda: need(index.rank_source(*left) == index.rank_source(*right),
                                     "sibling path merged"), "physical occurrence merge"))
    out.append(rejected(lambda: index.total[100, 1, 1], "absent sorted-table state"))
    out.append(rejected(lambda: I.SortedStateTable(((1, 1, 1), (0, 1, 0))),
                        "unsorted table keys"))
    out.append(rejected(lambda: I.SortedStateTable(((0, 1, 0), (0, 1, 0))),
                        "duplicate table keys"))
    empty = I.SortedStateTable(((0, 1, 0),))
    out.append(rejected(lambda: empty[0, 1, 0], "uninitialized table count"))
    return out


def main():
    totals = Counter()
    for ranks in ((2, 3), (2, 5), (3, 5), (4, 6)):
        for duplicate in (False, True):
            roles = (("large", ranks[1]), ("small", ranks[0]))
            if duplicate:
                roles += (("extra", ranks[0]),)
            for owned in (False, True):
                rule = C.Rule(roles, ((1, "small"), (min(ranks)-1,
                               "bank" if owned else "large")), ambient=max(ranks)+1)
                A, k = rule.ambient, min(ranks)
                for n in (A, A*k-1, A*k, A*k*k-1, A*k*k, A*k*k*k):
                    totals.update(check(rule, n))
    rule = C.Rule((("c", 5), ("a", 3), ("b", 4), ("d", 3)),
                  ((1, "a"), (1, "bank"), (2, "c")), ambient=7)
    for n in (7, 21, 62, 63, 188, 189):
        totals.update(check(rule, n))
    large = I.SourceIndex(C.Rule((("a", 3), ("b", 3), ("c", 5), ("d", 5)),
                         ((1, "a"), (1, "bank"), (2, "c")), ambient=7), 7*3**64)
    samples = (0, 1, large.size//2, large.size-2, large.size-1)
    for k in samples:
        need(large.rank_source(*large.unrank_source(k)) == k, "large interval inverse")
    need(len(large.total) <= 1+2*comb(65, 2), "large polynomial state bound")
    independently_counted = independent_counts(large)
    result = {"status": "PASS_CONTIGUOUS_SOURCE_INDEX", "totals": dict(totals),
              "negative_controls": controls(), "collision_family": collision_family(),
              "large_case": {
                  "height": 64, "states": len(large.total),
                  "target_multiindices": sum(map(len, large.point_data)),
                  "independent_word_product_states": independently_counted,
                  "literal_classes_not_enumerated": str((3**65-1)//2),
                  "source_count": str(large.size), "round_trip_samples": len(samples)},
              "scope": "offline logical row indexing; no payload tape tariff or kappa"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

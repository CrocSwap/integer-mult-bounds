#!/usr/bin/env python3
"""Bounded, exact checks of the logical Pascal owner codec (stdlib only)."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from collections import Counter

HERE = Path(__file__).resolve().parent
ORACLE_SHA256 = "f842f0e07ca40a181782a565a381b0ee20c6a4b08b8c2b8a4d5d630381bd1e8e"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


raw = (HERE / "inputs/finite_dag_audit.py").read_bytes()
need(hashlib.sha256(raw).hexdigest() == ORACLE_SHA256, "predecessor source hash")
C = load("pascal_codec", HERE / "codec.py")
O = load("pascal_predecessor_oracle", HERE / "inputs/finite_dag_audit.py")


class AmbientOracleRule(O.Rule):
    @property
    def dimension(self):
        return self._ambient


def compare(rule, n):
    oracle_rule = AmbientOracleRule(rule.roles, rule.rounds, rule.owned)
    object.__setattr__(oracle_rule, "_ambient", rule.ambient)
    tree = O.IntegerTree(oracle_rule, n)
    codec = C.FlowCodec(rule, n)
    need(codec.height == tree.depth, "height")
    ordinal = Counter()
    names, translated = {}, {}
    for unit in tree.units:
        key = (unit["path"], unit["point"])
        names[unit["uid"]] = C.Unit(*key, ordinal[key])
        ordinal[key] += 1
    for source in tree.sources:
        unit = names[source["unit"]]
        translated[source["field"]] = ("flow", 0, "source", unit.path,
                unit.point, unit.ordinal, source["role"])
    for unit in tree.units:
        u = names[unit["uid"]]
        for name, field in unit["owned"].items():
            translated[field] = ("flow", 0, "owned", u.path, u.point, u.ordinal, name)
    roles, inverse, exits = 0, 0, 0
    for unit in tree.units:
        u = names[unit["uid"]]
        for role, field in unit["fields"].items():
            need(codec.owner(u, role) == translated[field], "literal physical owner")
            parent = codec.parent(u, role)
            if parent is not None:
                decoded = C.decode(rule, parent.point, parent.ordinal)
                need(decoded == (u.point, u.ordinal, role), "Pascal inverse")
                r = rule.rounds[u.path[-1]][0]
                k = dict(rule.roles)[role]
                left = r * codec.dilation(parent.path) * C.column(rule, parent.point)
                right = k * codec.dilation(u.path) * C.column(rule, u.point)
                need(left == right, "whole-job rank equality")
                inverse += 1
            roles += 1
    for path, ids in tree.classes:
        expected = [names[uid] for uid in ids]
        need(list(codec.iter_units(path)) == expected, "complete ordered class stream")
        fields = [codec.owner(u, role) for u in expected for role, _ in rule.roles]
        need(len(fields) == len(set(fields)), "simultaneous source/owner alias")
    for group in tree.exits:
        for job in group:
            u = names[job["uid"]]
            need(codec.paid_owner(u, job["round"]) == translated[job["field"]],
                 "literal exit owner")
            exits += 1
    return {"units": len(tree.units), "roles": roles, "matched": inverse,
            "sources": len(tree.sources), "exits": exits, "classes": len(tree.classes)}


def rejection(action, label):
    try:
        action()
    except (ValueError, AssertionError):
        return label
    raise ValueError("negative control accepted: " + label)


def distinct(ids):
    need(len(ids) == len(set(ids)), "duplicate occurrence identity")


def controls():
    r = C.Rule((("a", 2), ("b", 2), ("c", 3)), ((1, "b"), (1, "bank")))
    checks = [rejection(lambda: C.Rule((("a", 0),), ((1, "a"),)), "zero target rank"),
              rejection(lambda: C.Rule((("a", 2),), ((0, "a"),)), "zero paid rank"),
              rejection(lambda: C.Rule((("a", 2),), ((2, "a"),)), "nonseparated rank"),
              rejection(lambda: C.Rule((("a", 2), ("a", 3)), ((1, "a"),)),
                        "duplicate productive label"),
              rejection(lambda: C.encode(r, (2, 0), 0, "c"), "missing Pascal letter"),
              rejection(lambda: C.decode(r, (1, 1), 4), "out-of-range occurrence")]
    correct = C.encode(r, (1, 1), 0, "c")
    wrong = 0  # omit the lower-type interval offset
    checks.append(rejection(lambda: need(C.decode(r, (1, 1), wrong) ==
                  C.decode(r, (1, 1), correct), "wrong offset"), "wrong offset"))
    f = C.FlowCodec(r, 12)
    u = next(f.iter_units(()))
    ids = [f.owner(u, x) for x, _ in r.roles]
    checks.append(rejection(lambda: distinct([ids[0], ids[0], ids[2]]),
                            "duplicated occurrence"))
    checks.append(rejection(lambda: C.FlowCodec(r, 11).validate_unit(
                    C.Unit((), (2, 0), 0)), "absent cap-boundary unit"))
    edge = C.FlowCodec(r, 12)
    edge.validate_unit(C.Unit((), (2, 0), 0))
    checks.append(rejection(lambda: need(edge.owner(u, "a", replica=0) ==
                  edge.owner(u, "a", replica=1), "replica identity"), "dropped replica"))
    return checks


def main():
    totals, cases, ambient_cases = Counter(), 0, 0
    for ranks in ((2, 3), (2, 4), (3, 4), (4, 6)):
        for duplicate in (False, True):
            roles = (("a", ranks[0]), ("c", ranks[1]))
            if duplicate:
                roles = (roles[0], ("b", ranks[0]), roles[1])
            for owned_call in (False, True):
                rounds = ((1, "a"), (min(ranks)-1, "bank" if owned_call else "c"))
                for extra in (0, 1):
                    rule = C.Rule(roles, rounds, ambient=max(ranks)+extra)
                    m, k = rule.ambient, min(ranks)
                    for n in sorted(set((m, m*k-1, m*k, m*k*k-1, m*k*k,
                                         m*k*k*k, m*k*k*k+1))):
                        totals.update(compare(rule, n))
                        cases += 1
                        ambient_cases += bool(extra)
    # Three target types and native role orders that do not group equal ranks.
    roles = (("z", 5), ("a", 2), ("b", 3), ("c", 2), ("d", 5))
    for ordering in (roles, tuple(reversed(roles)), roles[2:]+roles[:2]):
        rule = C.Rule(ordering, ((1, "c"), (1, "bank"), (1, "a")), ambient=7)
        for n in (7, 14, 27, 28, 55, 56):
            totals.update(compare(rule, n))
            cases += 1
            ambient_cases += 1
    # A 128-level descriptor addresses 2^128 root occurrences without enumeration.
    rule = C.Rule((("a", 2), ("b", 2)), ((1, "b"),))
    flow = C.FlowCodec(rule, 2**129)
    owner = flow.owner(C.Unit((0,)*128, (0,), 0), "b")
    need(owner == ("flow", 0, "source", (), (128,), 2**128-1, "b"),
         "long ancestry exact binary address")
    result = {"status": "PASS_PASCAL_OCCURRENCE_CODEC", "cases": cases,
              "ambient_exceeds_target_cases": ambient_cases,
              "totals": dict(sorted(totals.items())), "negative_controls": controls(),
              "long_ancestry_depth": 128, "unmaterialized_root_occurrences": "2^128",
              "oracle_sha256": ORACLE_SHA256, "scope": "logical identity, no tape tariff or kappa"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

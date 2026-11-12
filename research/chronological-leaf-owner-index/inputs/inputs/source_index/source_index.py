"""Contiguous source rows by aggregated lockstep-subtree counting.

Apache-2.0. Prepared for CubeJerry with substantial OpenAI assistance.
This is offline indexing, not a fixed-tape payload implementation.
"""
from collections import Counter
from bisect import bisect_left
import hashlib
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CODEC_HASH = "cec2c8b5e153a264127e8301ed59591fe97c9a46078ff2343b3784d177c6984d"
CODEC_PATH = HERE / "inputs/pascal_codec.py"
if hashlib.sha256(CODEC_PATH.read_bytes()).hexdigest() != CODEC_HASH:
    raise ValueError("frozen occurrence codec hash")
spec = importlib.util.spec_from_file_location("source_index_codec", CODEC_PATH)
C = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = C
spec.loader.exec_module(C)


def points(degree, dimensions):
    """Lexicographic nonnegative multiindices of one exact degree."""
    if dimensions == 1:
        yield (degree,)
        return
    for first in range(degree + 1):
        for rest in points(degree - first, dimensions - 1):
            yield (first,) + rest


def sorted_unique(items):
    """Deterministic comparison sort and adjacent deduplication; no hashing."""
    ordered = sorted(items)
    unique = []
    for item in ordered:
        if not unique or item != unique[-1]:
            unique.append(item)
    return unique


class SortedStateTable:
    """Fixed sorted integer keys, binary-search lookup and indexed values.

    The two count tables share one immutable key tuple. No growing state
    set/dictionary and no expected hash-table time enters the theorem.
    """
    def __init__(self, keys):
        C.require(all(a < b for a, b in zip(keys, keys[1:])),
                  "strictly sorted distinct state keys")
        self._keys = keys
        self._values = [None] * len(keys)

    def position(self, key):
        at = bisect_left(self._keys, key)
        C.require(at < len(self._keys) and self._keys[at] == key,
                  "state key absent from fixed table")
        return at

    def __getitem__(self, key):
        value = self._values[self.position(key)]
        C.require(value is not None, "state count not initialized")
        return value

    def __setitem__(self, key, value):
        self._values[self.position(key)] = value

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._keys)

    def keys(self):
        return iter(self._keys)

    def values(self):
        return iter(self._values)

    def items(self):
        return zip(self._keys, self._values)


class SourceIndex:
    def __init__(self, rule, rank, replicas=1, namespace="flow"):
        C.natural(replicas, "replica count")
        C.require(replicas > 0, "positive replica count")
        self.flow = C.FlowCodec(rule, rank)
        self.rule, self.rank = rule, rank
        self.replicas, self.namespace = replicas, namespace
        self.height = self.flow.height
        self.types, self.weights = rule.types, rule.weights
        self.paid = Counter(r for r, _ in rule.rounds)
        # Counter is confined to the fixed input list; its worst-case
        # collision cost is covered by the specification-size factor.
        self.point_data = []
        for g in range(self.height + 1):
            self.point_data.append(tuple((a, C.column(rule, a), C.multiplicity(rule, a))
                                         for a in points(g, len(self.types))))
        levels = [[(1, 0)]]
        for _ in range(self.height):
            # Adjacent equal dilations differ only in their last rank.
            # Deduplicate them before generating children: (rho*r,r) is
            # injective in rho at fixed r, and distinct r give distinct keys.
            dilations = []
            for rho, _ in levels[-1]:
                if not dilations or rho != dilations[-1]:
                    dilations.append(rho)
            levels.append(sorted_unique((rho*r, r) for rho in dilations
                                        for r in self.paid))
        keys = tuple((h, rho, previous) for h, level in enumerate(levels)
                     for rho, previous in level)
        self.local, self.total = SortedStateTable(keys), SortedStateTable(keys)
        for h in range(self.height, -1, -1):
            for rho, previous in levels[h]:
                state = (h, rho, previous)
                local = sum(u*count for _, _, u, count in self.blocks(state))
                total = local
                if h < self.height:
                    total += sum(mult*self.total[h+1, rho*r, r]
                                 for r, mult in self.paid.items())
                self.local[state], self.total[state] = local, total
        self.size = self.total[0, 1, 0]
        C.require(self.size > 0, "nonempty source interval")

    def fresh_type(self, state, column, i):
        h, rho, previous = state
        return h == 0 or self.rule.ambient * (rho // previous) * column * self.types[i] > self.rank

    def blocks(self, state):
        h, rho, _ = state
        for point, column, units in self.point_data[self.height-h]:
            if self.rule.ambient * rho * column <= self.rank:
                count = sum(w for i, w in enumerate(self.weights)
                            if self.fresh_type(state, column, i))
                if count:
                    yield point, column, units, count

    def fresh_roles(self, state, column):
        return tuple(name for name, k in self.rule.roles
                     if self.fresh_type(state, column, self.types.index(k)))

    def rank_source(self, unit, role):
        self.flow.validate_unit(unit)
        self.rule.type_of(role)
        state, offset = (0, 1, 0), 0
        for chosen in unit.path:
            h, rho, _ = state
            offset += self.local[state]
            for r, _ in self.rule.rounds[:chosen]:
                offset += self.total[h+1, rho*r, r]
            r = self.rule.rounds[chosen][0]
            state = (h+1, rho*r, r)
        for point, column, units, count in self.blocks(state):
            if point < unit.point:
                offset += units*count
                continue
            if point == unit.point:
                roles = self.fresh_roles(state, column)
                C.require(role in roles, "slot is matched, not a fresh source")
                return offset + unit.ordinal*count + roles.index(role)
            break
        raise ValueError("slot is matched, not a fresh source")

    def unrank_source(self, index):
        C.natural(index, "source index")
        C.require(index < self.size, "source index range")
        state, path = (0, 1, 0), ()
        while True:
            if index < self.local[state]:
                for point, column, units, count in self.blocks(state):
                    if index < units*count:
                        ordinal, role = divmod(index, count)
                        return C.Unit(path, point, ordinal), self.fresh_roles(state, column)[role]
                    index -= units*count
                raise ValueError("local count/index disagreement")
            index -= self.local[state]
            h, rho, _ = state
            C.require(h < self.height, "no child beyond the last class")
            for j, (r, _) in enumerate(self.rule.rounds):
                child = (h+1, rho*r, r)
                if index < self.total[child]:
                    state, path = child, path + (j,)
                    break
                index -= self.total[child]
            else:
                raise ValueError("subtree count/index disagreement")

    def row(self, owner):
        C.require(type(owner) is tuple and len(owner) == 7, "complete field identifier")
        namespace, replica, kind, path, point, ordinal, role = owner
        C.require(namespace == self.namespace, "invocation namespace")
        C.natural(replica, "replica")
        C.require(replica < self.replicas, "replica range")
        C.require(kind == "source", "owned bank has no productive source row")
        return replica*self.size + self.rank_source(C.Unit(path, point, ordinal), role)

    def owner(self, row):
        C.natural(row, "physical row index")
        C.require(row < self.replicas*self.size, "physical row index range")
        replica, index = divmod(row, self.size)
        unit, role = self.unrank_source(index)
        return (self.namespace, replica, "source", unit.path, unit.point, unit.ordinal, role)

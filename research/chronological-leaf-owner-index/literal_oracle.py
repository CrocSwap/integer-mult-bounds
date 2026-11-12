"""Separate finite oracle: materialize every class, match slot lists, expand calls.

No production codec, source DP, weighted suffix DP or owner resolver is imported.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from math import gcd, prod


@dataclass(frozen=True)
class Row:
    replication: int
    width: int
    leaves: int
    units: int


class LiteralFlow:
    def __init__(self, roles, rounds, owned, ambient, rank, cap=100000):
        self.roles, self.rounds, self.owned = roles, rounds, owned
        self.ambient, self.rank = ambient, rank
        self.types = tuple(sorted({k for _, k in roles}))
        type_index = {k: i for i, k in enumerate(self.types)}
        threshold, self.height = ambient, 0
        while threshold*min(self.types) <= rank:
            threshold *= min(self.types)
            self.height += 1
        points = []
        for degree in range(self.height+1):
            if len(roles)**degree > cap:
                raise ValueError('literal role-word capacity')
            counts = Counter()
            for word in product(range(len(roles)), repeat=degree):
                alpha = [0]*len(self.types)
                for letter in word:
                    alpha[type_index[roles[letter][1]]] += 1
                counts[tuple(alpha)] += 1
            points.append(sorted(counts.items()))
        self.classes, self.owners, self.fresh = {}, {}, []
        self.units = 0

        def construct(path, incoming=None):
            rho = prod(rounds[j][0] for j in path)
            units, buckets = [], defaultdict(list)
            for alpha, count in points[self.height-len(path)]:
                column = prod(k**a for k, a in zip(self.types, alpha))
                if ambient*rho*column > rank:
                    continue
                for ordinal in range(count):
                    unit = path, alpha, ordinal
                    units.append(unit)
                    for name, k in roles:
                        slot = unit+(name,)
                        beta = list(alpha)
                        beta[type_index[k]] += 1
                        buckets[tuple(beta)].append(slot)
            self.units += len(units)
            if self.units > cap:
                raise ValueError('literal unit capacity')
            self.classes[path] = units
            if incoming is not None:
                for alpha, supply in incoming.items():
                    targets = buckets[alpha]
                    if len(supply) != len(targets):
                        raise ValueError('literal Pascal list mismatch')
                    for value, target in zip(supply, targets):
                        self.owners[target] = value
            for unit in units:
                for name, k in roles:
                    slot = unit+(name,)
                    if slot not in self.owners:
                        self.owners[slot] = ('source', slot)
                        self.fresh.append((slot, rho*prod(t**a for t, a in
                                                         zip(self.types, unit[1]))*k))
            if len(path) < self.height:
                for j, (_, name) in enumerate(rounds):
                    supply = defaultdict(list)
                    for unit in units:
                        value = (('owned', unit, name) if name in owned else
                                 self.owners[unit+(name,)])
                        supply[unit[1]].append(value)
                    construct(path+(j,), supply)
        construct(())
        self.fresh_index = {slot: i for i, (slot, _) in enumerate(self.fresh)}
        if len(rounds)**(self.height+1) > cap:
            raise ValueError('literal cut capacity')
        self.cuts = tuple(product(range(len(rounds)), repeat=self.height+1))

    def exit(self, cut):
        unit = self.classes[cut[:-1]][0]
        if len(self.classes[cut[:-1]]) != 1 or any(unit[1]):
            raise ValueError('deepest single-unit condition')
        name = self.rounds[cut[-1]][1]
        value = (('owned', unit, name) if name in self.owned else
                 self.owners[unit+(name,)])
        return prod(self.rounds[j][0] for j in cut), value


def library(roles, rounds, owned, ambient, maximum):
    rows, flows = [None], {}
    for n in range(1, maximum+1):
        if n < ambient:
            rows.append(Row(1, 1, n, 0))
            continue
        flow = LiteralFlow(roles, rounds, owned, ambient, n)
        flows[n] = flow
        sources = Counter(s for _, s in flow.fresh)
        batches = [(n-s, count) for s, count in sorted(sources.items()) if s < n]
        batches += [(flow.exit(cut)[0], 1) for cut in flow.cuts]
        a = 1
        for q, count in batches:
            if not 0 < q < n:
                raise ValueError('literal rank descent')
            factor = rows[q].width//gcd(rows[q].width, count)
            a = a//gcd(a, factor)*factor
        leaves = sum(a*count//rows[q].width*rows[q].leaves for q, count in batches)
        units = a*flow.units+sum(a*count//rows[q].width*rows[q].units
                                 for q, count in batches)
        rows.append(Row(a, a*len(flow.fresh), leaves, units))
    return tuple(rows), flows


def expand(roles, rounds, owned, ambient, rows, flows, root, namespace='compiler',
           leaf_cap=100000):
    """Return fully expanded leaf descriptors and whole-call input receipts."""
    if rows[root].leaves > leaf_cap or rows[root].width > leaf_cap:
        raise ValueError('literal expanded-program capacity')
    leaves, calls = [], []

    def visit(n, chain, fields):
        if len(fields) != rows[n].width or len(set(fields)) != len(fields):
            raise ValueError('literal whole-input alias/width')
        if n < ambient:
            for axis in range(n):
                leaves.append((chain, n, axis, fields[0]))
            return
        flow, a = flows[n], rows[n].replication

        def lift(replica, value):
            if value[0] == 'source':
                return fields[replica*len(flow.fresh)+flow.fresh_index[value[1]]]
            _, unit, role = value
            path, point, ordinal = unit
            return ('owned', namespace, chain, replica, path, point, ordinal, role)

        def invoke(q, kind, key, batch):
            width = rows[q].width
            if len(batch) % width:
                raise ValueError('literal incomplete child')
            for at in range(0, len(batch), width):
                step = n, kind, key, at//width
                child_chain = chain+(step,)
                inputs = tuple(batch[at:at+width])
                calls.append((child_chain, q, inputs))
                visit(q, child_chain, inputs)

        for s in sorted({s for _, s in flow.fresh}):
            if s < n:
                batch = [fields[b*len(flow.fresh)+i]
                         for b in range(a) for i, (_, rank) in enumerate(flow.fresh)
                         if rank == s]
                invoke(n-s, 'complement', s, batch)
        for cut in flow.cuts:
            e, value = flow.exit(cut)
            invoke(e, 'exit', cut, [lift(b, value) for b in range(a)])

    visit(root, (), tuple(('source', namespace, row) for row in range(rows[root].width)))
    if len(leaves) != rows[root].leaves:
        raise ValueError('literal expanded count')
    return leaves, calls

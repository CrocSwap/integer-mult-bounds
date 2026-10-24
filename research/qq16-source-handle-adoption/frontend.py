"""Paid finite-schema lowering of the retained adoption metadata transaction.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from kernel import Store, need, access_cost

# Fixed schema positions; skipped source fields keep their ordinal positions.
BANK, PRIVATE, ROLES, PARKED, PARKING, OUTPUT, CAPSULE, CHILD, BINDING = range(9)
PACKETS, BANK_OUTPUT = range(2)
PARKING_ROLES, STACK, REVERSE = range(3)


class Frontend:
    """Finite constructor records, followed by paid source-specific updates.

    Each record is (Tape handle, attribute count, [(child, followed), ...]).
    Node zero is the unique opaque leaf. No host object IDs or numeric payloads
    enter this machine. Live object identity is its occupied record address.
    """
    def __init__(self, limit, records, roots):
        need(type(limit) is int and limit >= 4, 'positive schema capacity')
        self.limit = limit
        self.stride = 4 + 2*limit
        self.store = Store(8*limit*limit)
        self.base, _ = self.store.allocate([0]*(limit*self.stride))
        self.roots = tuple(roots)
        need(len(self.roots) == 7 and len(records) <= limit, 'bounded constructor roots')
        tapes = [r[0] for r in records if r[0]]
        need(len(set(tapes)) == len(tapes), 'unique constructor Tape handles')
        need(all(0 <= r < len(records) for r in self.roots) and
             all(0 <= child < len(records) for _, _, edges in records for child, _ in edges),
             'constructor references are live')
        for node, (tape, attributes, edges) in enumerate(records):
            self.install(node, tape, attributes, edges)
        need(records[0] == (0, 0, []), 'canonical opaque leaf')
        self.store.accesses += 16*self.limit*self.stride  # constructor record input and roots
        self.store.tick(64*self.limit*self.stride)
        self.constructor_accesses = self.store.accesses

    def at(self, node, slot):
        need(type(node) is int and 0 <= node < self.limit, 'finite node address')
        self.store.tick(4)
        return self.base + self.stride*node + slot

    def read(self, node, slot):
        return self.store.read(self.at(node, slot))

    def write(self, node, slot, value):
        self.store.write(self.at(node, slot), value)

    def install(self, node, tape, attributes, edges):
        need(0 <= tape <= self.limit and 0 <= attributes <= self.limit and
             len(edges) <= self.limit, 'finite constructor record')
        need(not tape or not edges, 'opaque Tape record')
        for slot, value in enumerate((1, tape, attributes, len(edges))):
            self.write(node, slot, value)
        for i, (child, followed) in enumerate(edges):
            need(type(child) is int and 0 <= child < self.limit and
                 type(followed) is bool, 'finite ordered schema edge')
            self.write(node, 4+2*i, child)
            self.write(node, 5+2*i, int(followed))

    def edge(self, node, index):
        need(self.read(node, 0) == 1 and 0 <= index < self.read(node, 3), 'existing source slot')
        return self.read(node, 4+2*index)

    def put(self, node, index, child):
        self.edge(node, index)
        need(0 <= child < self.limit and self.read(child, 0), 'live replacement handle')
        self.write(node, 4+2*index, child)

    def sequence(self, node):
        return [self.edge(node, i) for i in range(self.read(node, 3))]

    def fresh(self, children):
        # One source tuple constructor; reuse only records proved unreachable.
        for node in range(1, self.limit):
            if not self.read(node, 0):
                self.install(node, 0, 0, [(x, True) for x in children])
                return node
        raise ValueError('transient schema capacity exhausted')

    def collect(self):
        """Full finite mark/sweep, including source-omitted reference edges."""
        seen = set()
        stack = list(self.roots) + [0]
        # Sets/stacks here fast-forward bounded word scans charged explicitly.
        while stack:
            node = stack.pop()
            self.store.tick(8)
            self.store.accesses += 4*self.limit
            if node in seen:
                continue
            need(self.read(node, 0), 'root-reachable live node')
            seen.add(node)
            stack.extend(self.sequence(node))
        for node in range(1, self.limit):
            self.store.accesses += 2*self.limit
            if node not in seen and self.read(node, 0):
                for slot in range(self.stride):
                    self.write(node, slot, 0)

    def dfs(self, root):
        seen, tapes = set(), []
        stack = [root]
        while stack:
            node = stack.pop()
            self.store.tick(8)
            self.store.accesses += 4*self.limit
            if node in seen:
                continue
            need(self.read(node, 0), 'DFS live node')
            seen.add(node)
            tape = self.read(node, 1)
            if tape:
                tapes.append(tape)
            else:
                for i in range(self.read(node, 3)-1, -1, -1):
                    if self.read(node, 5+2*i):
                        stack.append(self.edge(node, i))
        return tapes

    def inventory(self):
        """Emit the predecessor kernel ABI from the owned finite store.

        Local numbering is irrelevant to DFS order. The reserved scratch block
        implements all host maps/lists by padded scans, paid here explicitly.
        """
        self.store.accesses += 128*self.limit**3
        self.store.tick(512*self.limit**3)
        def graph(root):
            nodes, indices, rows, attributes = [root], {root: 0}, [], 0
            for node in nodes:
                need(self.read(node, 0), 'inventory live source record')
                tape = self.read(node, 1)
                attributes += self.read(node, 2)
                children = []
                for i in range(self.read(node, 3)):
                    if self.read(node, 5+2*i):
                        child = self.edge(node, i)
                        if child not in indices:
                            indices[child] = len(nodes); nodes.append(child)
                        children.append(indices[child])
                rows.append([int(bool(tape)), tape, children])
            return dict(root=0, rows=rows, attributes=attributes)
        def tapes(node):
            values = [self.read(x, 1) for x in self.sequence(node)]
            need(all(values), 'inventory lists contain Tape handles')
            return values
        service, native, parent, engines, external, auxiliary, storage = self.roots
        return dict(graphs=[graph(x) for x in (service, native, parent)],
                    saved=[tapes(x) for x in self.sequence(self.edge(engines, 0))],
                    external=tapes(self.edge(external, 0)), auxiliary=tapes(auxiliary),
                    storage=tapes(storage), acquired=[])

    def replace(self, sequence, old, new):
        values = self.sequence(sequence)
        self.store.accesses += 8*self.limit
        self.store.tick(16*self.limit)
        need(values.count(old) == 1 and new not in values, 'one finite role replacement')
        return self.fresh([new if x == old else x for x in values])

    def adopt(self, caller, native, target, bank_slots):
        """Exact graph-bearing effects of PR4167 adopt_return, after guards.

        Physical marker checks, old.clear and erase_marker remain source actions;
        their cost is deliberately outside this metadata invoice.
        """
        need(type(target) is int and 0 <= target < bank_slots+self.read(self.edge(caller, PRIVATE), 3),
             'admitted finite target')
        bank = self.edge(caller, BANK)
        packets = self.edge(bank, PACKETS)
        need(bank_slots == self.read(packets, 3), 'exact source bank slot count')
        selected = packets if target < bank_slots else self.edge(caller, PRIVATE)
        index = target if target < bank_slots else target-bank_slots
        old = self.edge(selected, index)
        result = self.edge(native, OUTPUT)
        need(old != result, 'exclusive protected return and target')
        parked = self.sequence(self.edge(caller, PARKED))
        parking = self.edge(caller, PARKING)
        roles = self.sequence(self.edge(caller, ROLES))
        bank_values = self.sequence(packets)
        private = self.sequence(self.edge(caller, PRIVATE))
        capsule = self.sequence(self.edge(caller, CAPSULE))
        self.store.accesses += 32*self.limit*self.limit
        self.store.tick(64*self.limit*self.limit)
        need(len(set(parked)) == len(parked) and parked.count(old) == 1 and
             self.sequence(self.edge(parking, PARKING_ROLES)) == parked and
             parked == roles+bank_values+private, 'complete current parked-role bindings')
        need(result not in parked+capsule+[self.edge(caller, OUTPUT), self.edge(bank, BANK_OUTPUT),
                                         self.edge(parking, STACK), self.edge(parking, REVERSE)],
             'protected return has no caller alias')
        replacement = self.fresh([result if i == index else t for i, t in enumerate(self.sequence(selected))])
        self.put(bank if target < bank_slots else caller, PACKETS if target < bank_slots else PRIVATE, replacement)
        joined = self.fresh(roles+self.sequence(self.edge(bank, PACKETS))+self.sequence(self.edge(caller, PRIVATE)))
        self.put(caller, PARKED, joined)
        self.put(parking, PARKING_ROLES, joined)
        self.put(native, OUTPUT, old)
        return old, result

    def caches(self, engine_holder, external_holder, old, result, service_call, auxiliary):
        """PR4790's exact ordered engine/external cache substitution."""
        service, native = self.sequence(self.edge(engine_holder, 0))
        if service_call:
            service = self.replace(service, old, result)
        native = self.replace(native, result, old)
        self.put(engine_holder, 0, self.fresh([service, native]))
        external = self.fresh(self.sequence(service)+self.sequence(native)+self.sequence(auxiliary))
        self.put(external_holder, 0, external)

    def finish(self):
        # The store remains live across arbitrary transactions; its predecessor
        # per-kernel aggregate ceiling is not a session-length restriction.
        self.store.accesses += self.store.limit['capacity']
        self.store.cells[:] = [0]*len(self.store.cells)
        width = self.store.width
        return dict(accesses=self.store.accesses, scalar=self.store.scalar,
                    bits=self.store.accesses*access_cost(self.store.limit['capacity'], width)
                         + self.store.scalar*(16*width+16),
                    capacity=self.store.limit['capacity'], width=width)

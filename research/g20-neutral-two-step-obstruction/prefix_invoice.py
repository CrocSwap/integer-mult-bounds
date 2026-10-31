"""Exact unchanged-prefix reuse for the complete native metric invoice.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
A snapshot is taken strictly before the first deleted gate. Every later scalar
record, every correction, all formal input columns and all returns are replayed.
"""
from collections import Counter


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Invoice:
    def __init__(self, start, owned, distances, direct):
        self.rows = [1 << index for index in range(len(start))]
        self.frames = list(start)
        self.paid = Counter()
        self.new_paid = set()
        self.owned = owned
        self.distances = distances
        self.direct = direct

    def copy(self):
        other = object.__new__(Invoice)
        other.rows, other.frames = self.rows.copy(), self.frames.copy()
        other.paid, other.new_paid = self.paid.copy(), self.new_paid.copy()
        other.owned, other.distances, other.direct = self.owned, self.distances, self.direct
        return other

    def demand(self, role, target):
        source = self.frames[role]
        if source == target:
            return
        if source is None:
            need(role in self.owned and not self.rows[role], 'whole-zero owned header')
        else:
            rank = self.distances[source][target]
            need(type(rank) is int and rank > 0, 'positive distinct-frame distance')
            if self.rows[role]:
                self.paid[rank] += 1
                if (source, target) not in self.direct:
                    self.new_paid.add((source, target))
        self.frames[role] = target

    def step(self, event):
        op, destination = event[:2]
        if op in ('INIT', 'ERASE'):
            need(destination in self.owned and (op != 'INIT' or not self.rows[destination]),
                 'owned scalar event')
            self.rows[destination], self.frames[destination] = 0, event[2]
            return
        need(op == 'ADD', 'scalar alphabet')
        source, frame = event[2:]
        if not self.rows[source]:
            return
        self.demand(destination, frame)
        self.demand(source, frame)
        self.rows[destination] ^= self.rows[source]

    def finish(self, final):
        for role, frame in enumerate(final):
            if role in self.owned:
                need(not self.rows[role], 'owned final zero')
            else:
                self.demand(role, frame)
            self.frames[role] = frame
        need(self.frames == list(final), 'every final frame included')


def snapshots(records, candidates, start, owned, distances, direct):
    lefts = {candidate[0] for candidate in candidates}
    state, saved = Invoice(start, owned, distances, direct), {}
    for index, event in enumerate(records):
        if index in lefts:
            saved[index] = state.copy()
        state.step(event)
    need(set(saved) == lefts, 'all prefix snapshots captured')
    return saved


def changed_invoice(records, candidate, saved, final, endpoint):
    left, right, a, b, corrections = candidate
    need(records[left][:3] == records[right][:3] == ('ADD', a, b), 'equal outer gates')
    need(left in saved, 'first deletion has a prefix snapshot')
    state = saved[left].copy()
    for index in range(left + 1, len(records)):
        if index == right:
            continue
        state.step(records[index])
        if index in corrections:
            state.step(corrections[index])
    need(state.rows == endpoint, 'every formal input column at rewritten endpoint')
    state.finish(final)
    return state.paid, state.new_paid

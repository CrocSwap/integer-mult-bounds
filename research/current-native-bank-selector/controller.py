"""Run bank selection and reset through two charged unit-step heads."""
from collections import Counter


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def seek_table(count, direction, alphabet):
    need(direction in (-1, 1), 'unit selector direction')
    table = {}
    for remaining in range(count):
        table[remaining, 'left', None] = ('done', None, 0) if remaining == 0 else (remaining - 1, None, direction)
        table[remaining, 'right', None] = (remaining, None, direction)
        for symbol in alphabet:
            table[remaining, 'cell', symbol] = (remaining, None, direction)
    return table


class Machine:
    """The controller can access cells only at its two current heads."""
    def __init__(self, guide, count, parent_count, source):
        self.source = source
        self.unit = tuple(guide)
        self.extent = len(guide) - 2
        self.count = count
        self.guide = self.unit * count
        self.data = []
        for owner in range(count):
            body = []
            for index, (_, symbol) in enumerate(guide[1:-1]):
                if owner < parent_count:
                    body.append(str((owner + index) % 2) if symbol == '0' else symbol)
                else:
                    body.append(source.ALPHABET[(owner + index) % len(source.ALPHABET)])
            self.data.extend([source.LEFT, *body, source.RIGHT])
        self.guide_head = self.data_head = 0
        self.counts = Counter()
        self.forward = seek_table(count, 1, source.ALLOWED)
        self.backward = seek_table(count, -1, source.ALLOWED)

    def execute(self, table, state):
        while state != 'done':
            token = self.guide[self.guide_head]
            self.counts['guide_reads'] += 1
            self.counts['control_rows'] += 1
            state, write, move = table[state, *token]
            if write is not None:
                self.data[self.data_head] = write
                self.counts['data_writes'] += 1
            need(move in (-1, 0, 1), 'physical unit move')
            self.guide_head += move
            self.data_head += move
            self.counts['unit_moves'] += 2 * abs(move)
        need(self.guide_head == self.data_head, 'aligned distinct heads')

    def reset(self, slot, operation):
        need(0 <= slot < self.count and self.guide_head == self.data_head == 0, 'selector entry')
        before = self.counts.total()
        self.execute(self.forward, slot)
        need(self.guide_head == slot * len(self.unit), 'selected physical origin')
        self.execute(self.source.graph(operation), 'start')
        self.execute(self.backward, slot)
        need(self.guide_head == self.data_head == 0, 'complete head return')
        charged = self.counts.total() - before
        need(charged == 8 * slot * (self.extent + 2) + 9 * self.extent + 14, 'exact complete reset cost')
        return charged


def require_view(parent, child):
    need(tuple(parent) == tuple(child), 'complete shape and order equality')

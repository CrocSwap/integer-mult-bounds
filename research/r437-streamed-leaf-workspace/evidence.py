"""Checker-only accounting; none of these observations select runtime actions.

Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
"""
from contextlib import contextmanager


def need(value, message):
    if not value:
        raise ValueError(message)


def actions(meter):
    return {name: getattr(meter, name) for name in ("reads", "writes", "moves")}


def plus(target, values):
    for name, value in values.items():
        target[name] += value


class Audit:
    def __init__(self, pool):
        self.pool = pool
        self.identities = tuple(id(tape) for tape in pool.tapes)
        self.ids = set(self.identities)
        self.lease_actions = dict(reads=0, writes=0, moves=0)
        self.clear_actions = dict(reads=0, writes=0, moves=0)
        self.retired = self.clear_calls = self.callback_closes = 0
        self.boundaries = []

    def meter(self):
        result = dict(reads=0, writes=0, moves=0)
        for tape in self.pool.tapes:
            plus(result, actions(tape.meter))
        return result

    @contextmanager
    def installed(self):
        from records import Tape
        from scratch_pool import Lease
        import controller
        from words import BLANK
        old_clear, old_retire, old_close = Tape.clear, Lease.clear, controller.Callback.close

        def clear(tape):
            if id(tape) not in self.ids:
                return old_clear(tape)
            before, head = actions(tape.meter), tape.head
            length = 0
            for value in tape.cells[1:]:
                if value == BLANK:
                    break
                length += 1
            need(all(value == BLANK for value in tape.cells[length + 1:]),
                 "no hidden nonblank suffix before scratch erasure")
            old_clear(tape)
            delta = {name: getattr(tape.meter, name) - before[name] for name in before}
            need(delta == dict(reads=head + 2 * length + 2, writes=length,
                               moves=head + 2 * length + 3),
                 "literal clear read/write/unit-move formula")
            self.clear_calls += 1
            plus(self.clear_actions, delta)

        def retire(lease):
            active = lease.active
            old_retire(lease)
            if active and lease.pool is self.pool:
                self.retired += 1
                plus(self.lease_actions, actions(lease.meter))

        def close(callback):
            old_close(callback)
            self.callback_closes += 1

        Tape.clear, Lease.clear, controller.Callback.close = clear, retire, close
        try:
            yield self
        finally:
            Tape.clear, Lease.clear, controller.Callback.close = old_clear, old_retire, old_close

    def observe(self, pool):
        from words import BLANK
        need(pool is self.pool and tuple(id(t) for t in pool.tapes) == self.identities,
             "same physical roles at every complete prefix")
        need(not pool.live and pool.allocations == self.retired == self.clear_calls,
             "each acquisition has exactly one paid retirement")
        need(all(t.head == 1 and all(x == BLANK for x in t.cells[1:]) for t in pool.tapes),
             "all retained pool backing blank at the complete boundary")
        prefixes, capacity = len(self.boundaries) + 1, len(pool.tapes)
        total = self.meter()
        need(total == dict(
            reads=self.lease_actions["reads"] + pool.allocations + 2 * capacity * prefixes,
            writes=self.lease_actions["writes"],
            moves=self.lease_actions["moves"] + 2 * capacity * prefixes,
        ), "complete physical/lease/acquire/boundary traffic conservation")
        self.boundaries.append(dict(
            prefixes=prefixes, roles=capacity, peak=pool.peak,
            acquisitions=pool.allocations, retired=self.retired,
            backing=sum(len(t.cells) for t in pool.tapes),
            largest=max(len(t.cells) for t in pool.tapes),
            record_actions=total, lease_actions=dict(self.lease_actions),
            clear_calls=self.clear_calls, clear_actions=dict(self.clear_actions),
            callback_closes=self.callback_closes,
            allocation_and_boundary_actions=pool.allocations + 4 * capacity * prefixes,
        ))

    def result(self):
        need(self.boundaries, "nonempty complete-prefix evidence")
        result = dict(self.boundaries[-1])
        result["first_prefix_backing"] = self.boundaries[0]["backing"]
        result["backing_constant_after_first_prefix"] = all(
            row["backing"] == result["first_prefix_backing"] for row in self.boundaries)
        return result

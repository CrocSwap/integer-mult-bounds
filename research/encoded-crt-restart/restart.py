"""Persistent 79-role restart for the pinned encoded balanced CRT endpoints.

Only the first acquisition calls Port or Bank allocation. Successful calls
establish the whole-history blank invariant used at the next restart; this
is not a cleaner for arbitrary externally dirtied retired tails.
Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0.
"""
from types import SimpleNamespace


class Restart:
    """One physical inventory, one active endpoint, no runtime geometry."""

    def __init__(self, words, records, entry, numeric, owner, canonical,
                 forward, inverse, subtractive, writer, ports=None):
        self.w, self.r, self.e = words, records, entry
        self.numeric, self.subtractive = numeric, subtractive
        self.canonical, self.forward = canonical, forward
        self.reverse, self.writer = inverse.bind(forward), writer
        if ports is None:
            self.bank = owner.Bank(words, entry)
            # Eight guard, seven topology, one staging roles, in the unchanged
            # constructor's fixed order. Each keeps its original meter/backing.
            self.external = tuple(entry.Port(words) for _ in range(16))
            for port in self.external:
                port.retire()
        else:
            # Optional pre-owned, completely blank historical inventory.
            # Blank tails are an admission premise, not inferred by these
            # constant-size local checks.
            words.need(len(ports) == 79, 'complete supplied role inventory')
            self.bank = owner.Bank(words, entry, ports=ports[:63])
            self.external = tuple(ports[63:])
        self.ports = (*self.bank.ports, *self.external)
        words.need(len({id(p.cells) for p in self.ports}) == 79,
                   '79 distinct persistent histories')
        for port in self.ports:
            words.need(port.head == 1 and port.read() == words.BLANK,
                       'initial retired role body')
            port.step(-1)
            words.need(port.read() == words.BLANK, 'initial retired role marker')
            port.step(1)
        self.active = False
        self.cursor = 0
        self.current = None

    def _bank(self, words, entry):
        words.need(words is self.w and self.active and not self.bank.busy,
                   'same retired numerical bank')
        return self.bank

    def _take(self, words):
        words.need(words is self.w and self.active and self.cursor < 16,
                   'fixed external restart role')
        port = self.external[self.cursor]
        self.cursor += 1
        words.need(port.head == 1 and port.read() == words.BLANK,
                   'retired restart body')
        port.step(-1)
        words.need(port.read() == words.BLANK, 'retired restart marker')
        port.write(words.LEFT)
        port.step(1)
        return port

    def start(self, source, reverse=False):
        """Rearm local markers, then read all geometry from the actual source.

        The source is a supplied, disjoint, already encoded borrowed port at
        its origin. A direction bit chooses one of two fixed providers.
        """
        w = self.w
        w.need(type(reverse) is bool, 'finite direction flag')
        w.need(not self.active and not self.bank.busy,
               'previous whole invocation must finish')
        w.need(source.head == 1, 'source at admitted origin')
        w.need(id(source.cells) not in {id(p.cells) for p in self.ports},
               'source disjoint from all 79 histories')
        self.active, self.cursor = True, 0
        adapter = SimpleNamespace(Port=self._take, Entry=self.e.Entry)
        fixed_owner = SimpleNamespace(Bank=self._bank)
        frontend = self.reverse if reverse else self.forward
        numeric = self.subtractive if reverse else self.numeric
        # The original constructor obtains the same sixteen ports through
        # the fixed adapter. No history, meter or backing is reinitialized.
        self.current = self.writer.Endpoint(frontend, w, self.r, adapter,
            numeric, fixed_owner, self.canonical, source)
        w.need(self.cursor == 16, 'complete external role reentry')
        return self.current

    def finish(self):
        """Release only after the complete endpoint and source commit retire."""
        w, endpoint = self.w, self.current
        w.need(self.active and endpoint is not None,
               'one active whole invocation')
        w.need(endpoint.iterator.closed and not endpoint.iterator.live and
               not self.bank.busy and not endpoint.pending,
               'whole traversal and source commit must retire')
        # These are fixed-role local checks. The full historical-tail claim
        # follows by successful predecessor retirement, not a hidden scan.
        for port in self.ports:
            w.need(port.head == 1 and port.read() == w.BLANK,
                   'complete retired role head and body')
            port.step(-1)
            w.need(port.read() == w.BLANK, 'complete retired role marker')
            port.step(1)
        self.current = None
        self.active = False

    def run(self, source, reverse=False):
        endpoint = self.start(source, reverse)
        endpoint.run()
        self.finish()

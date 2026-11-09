"""Original-coordinate routes around one unchanged physical Full D event.

Explicit new owner ABI; no synthetic FullRoot or payload callback is used.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The ownership/route pattern is credited to the published complete Core join.
"""
from cardinal_counts import Count
from compact_counts import append_bits
from encoded import compare
from records import Tape
from router_metadata import owned
from session import (borrowed_count, borrowed_tape, erase_marker, sealed_constructors)
from words import BLANK, LEFT, need
from global_h_boundary import GlobalBoundary
from physical_engine import NullCounters, private_tapes
from physical_controls import emit_unsigned
from join_engine import FastFullPhysical


def origin(tape):
    """Check a borrowed head is immediately right of its actual left marker."""
    need(tape.read() != LEFT, "remaining-diagonal borrowed head at origin")
    tape.step(-1)
    try:
        need(tape.read() == LEFT, "remaining-diagonal borrowed head at origin")
    finally:
        tape.step(1)


class RemainingOwner(GlobalBoundary):
    def __init__(self, root, observe=None):
        super().__init__(root)
        self.diagonal = FastFullPhysical(root, observe=observe)
        if observe is None:
            self.calls = NullCounters(self.calls)
        self.pending = False
        self.private = private_tapes(self)

    def idle(self):
        super().idle()
        if hasattr(self, "diagonal"):
            self.diagonal.idle()
            need(self.diagonal.closed and self.diagonal.output.read() == BLANK,
                 "consumed remaining-diagonal child")

    def consume(self):
        need(self.closed and self.pending, "protected remaining-diagonal return")
        self.output.clear()
        erase_marker(self.output)
        self.pending = False
        self.idle()

    def run(self, payload, forward, inverse, route_parameters, code, parameters):
        data = tuple(borrowed_tape(t) for t in (payload, forward, inverse, code))
        payload, forward, inverse, code = data
        rp = tuple(borrowed_count(x) for x in route_parameters)
        fp = tuple(borrowed_count(x) for x in parameters)
        need(len(rp) == 4 and len(fp) == 16, "complete remaining-diagonal route/control ports")
        ports = (*data, *(x.tape for x in (*rp, *fp)))
        need(len(set(data)) == len(data) and all(t not in self.private for t in ports)
             and all(x.tape not in data for x in (*rp, *fp)),
             "external remaining-diagonal source/control ports")
        need(not self.pending, "consume previous remaining-diagonal return")
        for tape in ports:
            origin(tape)
        self.rearm()
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                n, precision, support, pw = rp
                need(compare(n, fp[0]) == 0 and compare(fp[5], fp[10]) == 0,
                     "same original/packed full field and unchanged grid carrier")
                with owned(Count.literal(1)) as (one,):
                    self.current = self.pool.acquire()
                    append_bits(payload, self.current)
                    payload.rewind()
                    self.current.rewind()
                    self.gather(forward, n, precision, support, pw, fp[5], one, one)
                    with self.scope.suspended():
                        returned = self.diagonal.run(self.current, code, *fp)
                    following = self.pool.acquire()
                    try:
                        append_bits(returned, following)
                    finally:
                        returned.clear()
                        erase_marker(returned)
                    self.current.clear()
                    self.current = following
                    self.current.rewind()
                    self.gather(inverse, n, precision, support, pw, fp[5], one, one)
                    append_bits(self.current, self.output)
                self.current.clear()
                self.current = None
                self.pool.empty()
                succeeded = self.pending = True
        finally:
            if self.diagonal.closed and self.diagonal.output.read() != BLANK:
                self.diagonal.output.clear()
                erase_marker(self.diagonal.output)
            if self.current is not None:
                self.current.clear()
                self.current = None
            self.pool.empty()
            for tape in ports:
                tape.rewind()
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
                self.pending = False
            self.closed = True
        return self.output


class PreparedRoutes:
    def __init__(self, layout, width):
        self.forward, self.inverse = Tape(), Tape()
        pw = max(1, (layout.n - 1).bit_length())
        for tape, mapping in ((self.forward, layout.gather), (self.inverse, layout.inverse)):
            for old, new in sorted(mapping.items()):
                emit_unsigned(tape, old, pw)
                emit_unsigned(tape, new, pw)
            tape.rewind()
        self.parameters = tuple(Count.literal(x) for x in
                                (layout.n, width + layout.h, len(layout.gather), pw))

    def close(self):
        for value in self.parameters:
            value.close()
            erase_marker(value.tape)
        for tape in (self.forward, self.inverse):
            tape.clear()
            erase_marker(tape)


class BoundRemaining:
    """Protected external q-grid return, with exactly zero extra normalization."""
    def __init__(self, codec, owner, routes, prepared):
        need(codec.fmt.drop == codec.fmt.lift == codec.fmt.normalizer_bits == 0,
             "remaining diagonal keeps external q grid without another scale")
        need(codec.fmt.native_grid == prepared.metadata["fractional_bits"]
             == prepared.metadata["incoming_bits"] and codec.fmt.native_bits
             == prepared.metadata["data_width"] == prepared.metadata["incoming_width"],
             "actual remaining-diagonal source and codec formats agree")
        self.codec, self.owner, self.routes, self.prepared = codec, owner, routes, prepared
        self.pending = False

    def run(self, source):
        need(not self.pending, "consume previous external remaining-diagonal output")
        succeeded = False
        try:
            payload = self.codec.prepare_input(source)
            returned = self.owner.run(payload, self.routes.forward, self.routes.inverse,
                                      self.routes.parameters, self.prepared.code, self.prepared.parameters)
            self.codec.prepare_return(returned, source)
            self.owner.consume()
            succeeded = self.pending = True
            return self.codec.output
        finally:
            if self.owner.pending:
                self.owner.consume()
            if not succeeded:
                self.codec.abort()

    def consume(self):
        need(self.pending, "protected external remaining-diagonal return")
        self.codec.abort()
        self.pending = False

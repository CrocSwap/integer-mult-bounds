"""Actual recursive Frame entry/return using one pair of numerical banks."""
from contextlib import contextmanager

import loader
bank_codec = loader.activate()
from directory import Context, append_tape
from records import Program
from words import Ring, need


class NumericLease:
    """Three owned argument grants and one matched parent-bank checkpoint."""
    def __init__(self, session, parent_context, parent_indices, width, depth):
        self.session = session
        self.arena, self.indices = session.arena, session.indices
        need(parent_context.arena is self.arena and parent_indices is self.indices,
             "one shared bank pair throughout the recursive run")
        self.modulus = self.width = self.depth = self.ring = self.context = None
        self.phase = "preparing"
        self.entry_residues, self.entry_indices = frozenset(self.arena.live), frozenset(self.indices.live)
        codes = parent_context.codes
        try:
            # All reads of parent numerical values finish before PARK.
            self.modulus = self.arena.copy(parent_context.ring.modulus)
            self.width = self.indices.copy(width)
            self.depth = self.indices.copy(depth)
            keep = ({self.modulus.slot}, {self.width.slot, self.depth.slot})
            self.phase = "parking"
            session.codec.park(keep)
            self.phase = "child"
            self.ring = Ring(self.modulus)
            self.context = Context(self.ring, codes)
        except BaseException:
            if self.phase == "preparing":
                self.arena.rollback(self.entry_residues)
                self.indices.rollback(self.entry_indices)
                self.phase = "closed"
            elif self.phase == "child":
                self.close(strict=False)
            # Incomplete codec operations are outside the retained interruption
            # contract. Do not pretend that a partially written PUSH completed.
            raise

    def close(self, strict=True):
        need(self.phase == "child", "one completed numerical lease return")
        first_error = None
        if strict:
            residues = {self.modulus.slot, self.ring.one.slot, self.context.cap.slot}
            indices = {self.width.slot, self.depth.slot}
            if self.arena.live != residues or self.indices.live != indices:
                first_error = ValueError("callee closes its numerical locals before Frame return")
        actions = []
        if self.context is not None:
            actions.append(self.context.close)
        if self.ring is not None:
            actions.append(self.ring.close)
        for arena, word in ((self.arena, self.modulus), (self.indices, self.width), (self.indices, self.depth)):
            if word is not None:
                def release(arena=arena, word=word):
                    if word.slot in arena.live:
                        arena.free(word)
                actions.append(release)
        for action in actions:
            try:
                action()
            except ValueError as error:
                if first_error is None:
                    first_error = error
        # Any remaining live words belong to this child; the parent is still
        # parked. Clear them before restoring the parent's original aliases.
        self.arena.rollback(frozenset())
        self.indices.rollback(frozenset())
        self.session.codec.restore()
        self.phase = "closed"
        if first_error is not None and strict:
            raise first_error


class Callee:
    """Keep the source node body and distinguish return from interrupted exit."""
    def __init__(self, frame, node):
        self.frame, self.node = frame, node

    def run_generator(self, source, *args, **kwargs):
        self.frame.borrowed_source = source
        result = yield from self.node.run_generator(source, *args, **kwargs)
        self.frame.output = result
        self.frame.callee_returned = True
        return result


class SharedFrame:
    def __init__(self, parent, program, event, session):
        self.session = session
        self.arena, self.indices = session.arena, session.indices
        self.lease = self.program = self.node = None
        self.closed = False
        self.callee_returned = False
        self.output = self.borrowed_source = None
        try:
            self.lease = NumericLease(session, parent.context, parent.indices, event.width, event.depth)
            self.modulus, self.size, self.depth = self.lease.modulus, self.lease.width, self.lease.depth
            self.ring, self.context = self.lease.ring, self.lease.context
            self.program = Program(self.indices, self.arena, program.code_bits)
            append_tape(program.tape, self.program.tape)
            self.program.tape.rewind()
            from node import SelectedNode
            node = SelectedNode(self.context, self.indices, self.program, self.size, self.depth,
                                parent.specifications.catalogue, parent.specifications)
            self.node = Callee(self, node)
            if session.observe is not None:
                session.observe("enter", self)
        except BaseException:
            if self.program is not None:
                self.program.tape.clear()
            if self.lease is not None and self.lease.phase == "child":
                self.lease.close(strict=False)
            self.closed = True
            raise

    def close(self):
        need(not self.closed, "shared Frame closes once")
        try:
            self.program.tape.clear()
            self.lease.close(strict=self.callee_returned)
        except BaseException:
            if self.output is not None and self.output is not self.borrowed_source:
                self.output.clear()
            raise
        finally:
            self.closed = True
        if self.session.observe is not None:
            self.session.observe("return", self)


class Session:
    """One physical codec shared by the source caller's whole nested run.

    The frozen logical scheduler still owns its generator continuation.
    This adapter closes the numerical bank interface, not that separate one.
    """
    def __init__(self, arena, indices, machine=None, observe=None):
        self.arena, self.indices = arena, indices
        self.codec = bank_codec.BankParking(arena, indices, machine)
        self.observe = observe
        self.installed = False

    @contextmanager
    def install(self):
        import recursive_call
        need(not self.installed, "one active Frame adapter per session")
        previous = recursive_call.Frame
        self.installed = True
        def frame(parent, program, event):
            return SharedFrame(parent, program, event, self)
        recursive_call.Frame = frame
        try:
            yield self
        finally:
            recursive_call.Frame = previous
            self.installed = False

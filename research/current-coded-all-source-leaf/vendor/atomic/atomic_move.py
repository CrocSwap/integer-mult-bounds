"""Protected whole-occurrence composition of one actual current MOVE.

Atomicity covers the inherited named arithmetic rejections on the valid
format/header domain, not interruptions or arbitrary malformed service output.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import gzip
from hashlib import sha256
import json
import sys
from move_sources import HERE, activate, need

S = activate()
_source = None


def source_boundary():
    global _source
    if _source is not None:
        return _source
    entry, leave, record, predecessor = S.selected.source_boundary()
    word = json.loads(gzip.decompress(
        (HERE / "vendor/monomial/vendor/selected/WORD.json.gz").read_bytes()))
    ir = sys.modules["selected_phase_current_ir"]
    events, stats = ir.current_local(word)
    index = events.index(entry)
    triple = tuple(events[index:index + 3])
    need(triple[2] == leave and triple[1].op == "PAID" and triple[1].rank == 1
         and triple[1].fields == (236,)
         and triple[1].token == ("local", 9896, ("MOVE", 236, 3, 7, False)),
         "actual consecutive entrance/positive PAID/exit source triple")
    clifford = sys.modules["selected_phase_clifford"]
    original = clifford.canonical_frame(9, tuple(word["frames"][3])).adjoint().then(
        clifford.canonical_frame(9, tuple(word["frames"][7])))
    columns = [clifford.fourier(1).zero_state(j) for j in (0, 1)]
    need(columns == [([(1, 1), (1, -1)], 1), ([(1, -1), (1, 1)], 1)],
         "source positive C including its absolute phase and half normalization")
    report = dict(event=9896, owner=236, raw=("MOVE", 236, 3, 7, False),
                  source_events=stats["events"], raw_tokens=[e.token for e in triple],
                  native_rank=9, positive_paid_rank=1, record_sha256=predecessor["record_sha256"],
                  whole_raw_move=True, enclosing_caller_placement=False,
                  shared_schema=list(S.monomial.SCHEMA))
    _source = triple, record, original, report
    return _source


def same_event(given, expected):
    def typed_equal(a, b):
        return type(a) is type(b) and (len(a) == len(b) and all(
            typed_equal(x, y) for x, y in zip(a, b)) if isinstance(a, tuple) else a == b)
    return all(typed_equal(getattr(given, name), getattr(expected, name))
               for name in ("op", "fields", "token", "rank"))


class AtomicMove:
    def __init__(self, triple, ordinary_factory):
        expected, record, _original, self.report = source_boundary()
        need(len(triple) == 3 and all(same_event(x, y) for x, y in zip(triple, expected)),
             "exact raw MOVE triple, chronology, owner and paid rank")
        self.entry = S.monomial.Provider(record["right"], ordinary_factory)
        self.leaf = S.leaf_provider.Provider()
        self.exit = S.monomial.Provider(record["left"], ordinary_factory)
        self.stage = self.field = self.context = self.work = None

    @property
    def port_count(self):
        return 1 + self.entry.port_count + self.leaf.port_count + self.exit.port_count

    def bind(self, work, fields, context):
        need(len(work) == self.port_count and len(set(map(id, work))) == len(work),
             "exact fixed distinct whole-MOVE inventory")
        need(236 in fields, "source owner has a complete coded field")
        field = fields[236]
        need(field.tape is not context.tape
             and all(field.tape is not p and context.tape is not p for p in work),
             "public, descriptor and complete private cohorts are distinct")
        self.work, self.field, self.context = tuple(work), field, context
        self.stage = S.abi.CodedPort(work[0])
        start = 1
        for provider in (self.entry, self.leaf, self.exit):
            stop = start + provider.port_count
            provider.bind(work[start:stop])
            start = stop
        need(start == len(work), "every fixed port bound once")

    def commit(self):
        """Copy only after all factors have returned complete, equal-size data."""
        source, target = self.stage.tape, self.field.tape
        S.abi.origin(source); S.abi.origin(target)
        while (bit := source.read()) != S.abi.BLANK:
            need(bit in (0, 1) and target.read() in (0, 1), "whole equal-size complete result")
            target.write(bit)
            source.move(1); target.move(1)
        need(target.read() == S.abi.BLANK, "preserved complete public frontier")
        S.abi.origin(source); S.abi.origin(target)

    def run(self):
        need(self.work is not None, "whole-MOVE ports bound before execution")
        # Raw administrative copying preserves every three-bit code, including
        # all component delimiters. No payload is decoded by this wrapper.
        S.abi.transfer(self.field.tape, self.stage.tape)
        try:
            self.entry.run(self.stage, self.context)
            self.leaf.run(self.stage, self.context)
            self.exit.run(self.stage, self.context)
            self.commit()
        finally:
            S.abi.retire(self.stage.tape)


if __name__ == "__main__":
    print(json.dumps(source_boundary()[3], sort_keys=True))

"""Bind one actual selected rank-one PAID token to the current leaf provider.

The source monomial adapters remain separate. This installs only their positive
Gaussian middle child. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
import gzip
from hashlib import sha256
import json
from leaf_sources import HERE, authenticate, load, need
from leaf_provider import Provider

_source = None
EVENT = 9896
RAW = ("MOVE", 236, 3, 7, False)


def source_boundary():
    global _source
    if _source is not None:
        return _source
    authenticate()
    word = json.loads(gzip.decompress((HERE / "vendor/selected/WORD.json.gz").read_bytes()))
    need(tuple(word["program"][EVENT]) == RAW, "actual selected MOVE token")
    ir = load("current_leaf_source_ir", HERE / "vendor/binding/vendor/lifecycle/source_ir.py")
    events, statistics = ir.current_local(word)
    matches = [event for event in events if event.op == "PAID" and event.token == ("local", EVENT, RAW)]
    need(len(matches) == 1 and matches[0].fields == (236,) and matches[0].rank == 1,
         "one actual positive rank-one current PAID event")
    event = matches[0]
    k = events.index(event)
    need(events[k - 1].token == ("move-in", "local", EVENT, RAW)
         and events[k + 1].token == ("move-out", "local", EVENT, RAW),
         "source chronological adapter/positive-child/adapter order")
    clifford = load("current_leaf_clifford", HERE / "vendor/selected/clifford_exact.py")
    left = clifford.canonical_frame(9, tuple(word["frames"][3]))
    right = clifford.canonical_frame(9, tuple(word["frames"][7]))
    record, lowered = clifford.lower_child(left.adjoint().then(right))
    need(record["rank"] == 1, "actual canonical middle Fourier rank")
    # Both columns of the exact source-positive C, with absolute normalization.
    columns = [clifford.fourier(1).zero_state(),
               clifford.xgate(1, 1).then(clifford.fourier(1)).zero_state()]
    need(columns == [([(1, 1), (1, -1)], 1), ([(1, -1), (1, 1)], 1)],
         "source C coefficients, phase and exact denominator")
    report = dict(event=EVENT, raw=RAW, owner=236, rank=1, token=event.token,
                  source_events=statistics["events"], exact_C_columns=columns,
                  record_sha256=sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                  positive_child_only=True, monomials_included=False,
                  selected_frontier_changed=False)
    _source = event, report
    return _source


class Service:
    def __init__(self, event):
        expected, self.report = source_boundary()
        need((event.op, event.fields, event.token, event.rank)
             == (expected.op, expected.fields, expected.token, expected.rank),
             "exact actual current PAID token, owner and rank")
        self.owner = event.fields[0]
        self.token = ("leaf",) + event.token
        self.provider = Provider()
        self.field = self.context = None

    @property
    def port_count(self):
        return self.provider.port_count

    def bind(self, work, fields, context):
        need(self.owner in fields, "actual current owner has a complete physical field")
        self.field, self.context = fields[self.owner], context
        self.provider.bind(work)

    def run(self):
        need(self.field is not None, "source/service binding completed before numerical input")
        self.provider.run(self.field, self.context)


if __name__ == "__main__":
    print("PASS_CURRENT_SELECTED_LEAF_BINDING " + json.dumps(source_boundary()[1], sort_keys=True))

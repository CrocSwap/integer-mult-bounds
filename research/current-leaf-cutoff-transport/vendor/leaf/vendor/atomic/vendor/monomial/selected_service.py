"""One current #6030 MOVE boundary, with its actual source monomial.

The width-one phase record and its tensor convention are inherited from #6293
and #6930. This file binds the actual source token and owner to the current
signed-format service; it does not re-audit the primary native recorder.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import gzip
from hashlib import sha256
import json
from phase_binding import HERE, authenticate, load, need
from phase_adapter import Provider

_selected = None
EVENT = 9896
RAW = ("MOVE", 236, 3, 7, False)


def source_boundary():
    global _selected
    if _selected is not None:
        return _selected
    authenticate()
    root = HERE / "vendor/selected"
    word = json.loads(gzip.decompress((root / "WORD.json.gz").read_bytes()))
    need(tuple(word["program"][EVENT]) == RAW, "actual selected MOVE source record")
    ir = load("selected_phase_current_ir", HERE / "vendor/binding/vendor/lifecycle/source_ir.py")
    events, stats = ir.current_local(word)
    entry = next(e for e in events if e.op == "SERVICE" and e.token == ("move-in", "local", EVENT, RAW))
    leave = next(e for e in events if e.op == "SERVICE" and e.token == ("move-out", "local", EVENT, RAW))
    need(entry.fields == leave.fields == (236,), "actual selected field owner at both monomial cuts")
    clifford = load("selected_phase_clifford", root / "clifford_exact.py")
    start = clifford.canonical_frame(9, tuple(word["frames"][3]))
    stop = clifford.canonical_frame(9, tuple(word["frames"][7]))
    record, _compiled = clifford.lower_child(start.adjoint().then(stop))
    need(record["rank"] == 1 and record["right"]["phase"] == 1
         and record["left"]["phase"] == 0, "inherited #6930 actual chart record")
    raw = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    report = dict(event=EVENT, raw=RAW, owner=236, rank=record["rank"],
                  right=record["right"], left=record["left"], source_token=entry.token,
                  record_sha256=sha256(raw).hexdigest(),
                  source_phase_audit="unpaidmoon/integer-mult-bounds@c726399fbdb6d80dd13bed760b56572fb4ea1022",
                  phase_algebra_inherited_from=[3087, 6293, 6930],
                  current_source_events=stats["events"], selected_frontier_changed=False)
    _selected = entry, leave, record, report
    return _selected


class Service:
    def __init__(self, event, native_factory):
        entry, leave, record, self.report = source_boundary()
        need(event.op == "SERVICE" and len(event.fields) == 1 and len(event.token) >= 4,
             "actual single-owner current MOVE service")
        tail = event.token[-4:]
        need(tail in (entry.token, leave.token), "fixed current source chart and occurrence token")
        self.token, self.owner = event.token, event.fields[0]
        self.side = "right" if tail == entry.token else "left"
        self.provider = Provider(record[self.side], native_factory)
        self.field = self.context = None

    @property
    def port_count(self):
        return self.provider.port_count

    def bind(self, work, fields, context):
        need(self.owner in fields, "actual current MOVE owner has its physical field")
        self.field, self.context = fields[self.owner], context
        self.provider.bind(work)

    def run(self):
        need(self.field is not None, "fixed current source/field/context binding before input")
        self.provider.run(self.field, self.context)


if __name__ == "__main__":
    print(json.dumps(source_boundary()[3], sort_keys=True))

"""Fixed-workspace specialization of the unchanged #5055 leaf/XOR consumer.

Krzysztof Wójt, with substantial OpenAI Codex assistance; Apache-2.0.
The source algorithm is JoyboyBrian's; physical leases are Jose Manuel's.
No frozen source is modified. This module must be loaded after the source loader.
"""

import importlib.util
from pathlib import Path
from types import FunctionType

from records import Tape
from scratch_pool import ScratchPool
from words import need


ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "r437_workspace_predecessor",
    ROOT / "research/r437-streaming-directory/streaming.py",
)
_source = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_source)

# Public producer is exactly the predecessor's producer, including its guards.
visit = _source.visit


def role_capacity(q):
    """A conservative source-call-graph bound, not an observed peak."""
    need(type(q) is int and q >= 2, "compiled radix at least two")
    return q * q + 136


class Workspace:
    """One caller-owned pool, reused only at complete prefix boundaries.

    `observe` is an optional checker hook and is not part of runtime semantics.
    Callers must not retain a scratch lease beyond the synchronous consumer.
    """

    def __init__(self, q, *, capacity=None, observe=None):
        bound = role_capacity(q)
        self.q = q
        self.pool = ScratchPool(bound if capacity is None else capacity)
        self.observe = observe
        self.active = False

    def tape(self):
        # Only the full returned output is allocated outside the local interval.
        # The finite phase flag never depends on an encoded numerical value.
        return self.pool.acquire() if self.active else Tape()

    def consume(self, callback, prefix):
        need(not self.active and not self.pool.live, "closed workspace entry")
        self.active = True
        try:
            with self.pool.install():
                callback(prefix)
        finally:
            self.active = False
        # This is a successful-return contract, not arbitrary-exception rollback.
        self.pool.empty()
        if self.observe is not None:
            self.observe(self.pool)


def run(source, target, events, layout, old, old_fields, old_count, code,
        context, coefficient, observe=None, *, workspace=None, visitor=None):
    """Execute the exact predecessor code with bounded allocation specialization.

    `visitor` is only for a separately labelled selected-prefix calibration.
    The ordinary path uses the full unchanged high-cube producer.
    The returned full output remains an ordinary caller-owned physical tape.
    """
    owned = workspace if workspace is not None else Workspace(layout.q)
    need(owned.q == layout.q, "workspace compiled radix matches layout")
    producer = visit if visitor is None else visitor

    def pooled_visit(old, fields, count, source_code, ctx, callback):
        def consume(prefix):
            return owned.consume(callback, prefix)
        return producer(old, fields, count, source_code, ctx, consume)

    body = FunctionType(
        _source.run.__code__,
        dict(_source.run.__globals__, Tape=owned.tape, visit=pooled_visit),
        _source.run.__name__,
        _source.run.__defaults__,
    )
    # Literal source execution: source order, guards, callbacks and copies remain.
    return body(source, target, events, layout, old, old_fields, old_count,
                code, context, coefficient, observe)

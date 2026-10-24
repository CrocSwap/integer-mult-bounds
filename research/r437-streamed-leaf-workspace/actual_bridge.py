"""Two selected actual64 prefixes; never a full 3**4096-domain claim.

Adapted from JoyboyBrian's #5055 actual_bridge.py, preserving its reader/guards.
Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
import importlib.util
from cardinal_counts import Count, positive
from stream import Counter
from words import BLANK, Unsigned, need
import packet

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r437_workspace_body", HERE / "pooled.py")
body = importlib.util.module_from_spec(spec)
spec.loader.exec_module(body)


def run(source, target, events, layout, prefixes, prefix_count, field_count,
        coefficient, context, old_count, observe=None, *, workspace=None):
    need(len({id(source), id(target), id(prefixes)}) == 3, "distinct streamed borrowed roles")
    positive(prefix_count)
    positive(old_count)
    positive(context.highs)
    total = Count.product(old_count, context.highs)
    try:
        need(total.equals(prefix_count), "complete calibration prefix product")
    finally:
        total.close()

    def selected(old, fields, count, code, ctx, consume):
        remaining = Counter(prefix_count)
        try:
            old.rewind()
            while not remaining.finished:
                prefix = packet.read_prefix(old, field_count)
                try:
                    consume(prefix)
                finally:
                    prefix.clear()
                remaining.decrement()
            need(old.read() == BLANK, "complete calibration selected directory")
            return Count(prefix_count)
        finally:
            old.rewind()
            remaining.close()

    one = field_count.arena.literal(1)
    previous, borrow = Unsigned(field_count.arena).subtract(field_count, one)
    field_count.arena.free(one)
    need(not borrow, "positive calibration field count")
    try:
        return body.run(source, target, events, layout, prefixes, previous,
                        old_count, 0, context, coefficient, observe,
                        workspace=workspace, visitor=selected)
    finally:
        field_count.arena.free(previous)

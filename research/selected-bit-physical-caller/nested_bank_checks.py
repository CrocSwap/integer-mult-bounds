"""The predecessor's complete recursive GL2 payload with shared numeric banks.

Only the model's child frame construction changes. Its production Node,
Driver, residuals, routes and stream primitives keep their pinned bodies.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader
loader.activate()

import json
from unittest.mock import patch
import check_nested_model as model
from numerical_frame import NumericLease, Session
from words import need


def run():
    original_consumer, original_node = model.Consumer, model.Node
    holder = {"leases": 0, "returns": 0}

    class Consumer(original_consumer):
        def __init__(self, context, indices, program, size, depth, catalogue, topology,
                     incoming, plans, tracker, counters, root_axes=False, root_level=False):
            self.lease = None
            if root_level:
                need("session" not in holder, "one shared numerical session for the model root")
                holder["session"] = Session(context.arena, indices)
            else:
                session = holder["session"]
                self.lease = NumericLease(session, context, indices, size, depth)
                context, size, depth = self.lease.context, self.lease.width, self.lease.depth
                incoming = model.UnitIncoming(context)
                holder["leases"] += 1
            super().__init__(context, indices, program, size, depth, catalogue, topology,
                             incoming, plans, tracker, counters, root_axes, root_level)

    class Node(original_node):
        def __init__(self, context, indices, program, parent_size, depth,
                     topology, consumer, incoming, stock_multiple=1):
            self.lease = consumer.lease
            if self.lease is not None:
                # The old local invoke still passes its parent references.
                # Replace them before the source Node reads any numeric value.
                context, parent_size, depth = self.lease.context, self.lease.width, self.lease.depth
                incoming = consumer.incoming
            try:
                super().__init__(context, indices, program, parent_size, depth,
                                 topology, consumer, incoming, stock_multiple)
            except BaseException:
                if self.lease is not None:
                    self.lease.close(strict=False)
                raise

        def run_generator(self, *args, **kwargs):
            completed = False
            try:
                output = yield from super().run_generator(*args, **kwargs)
                completed = True
                return output
            finally:
                if self.lease is not None:
                    self.lease.close(strict=completed)
                    holder["returns"] += 1

    with patch.object(model, "Consumer", Consumer), patch.object(model, "Node", Node):
        result = model.run()
    session = holder["session"]
    need(holder["leases"] == holder["returns"] == 12, "twelve real completed shared-bank child calls")
    need(session.codec.machine.tapes == [{}, {0: "^"}] and session.codec.machine.heads == [0, 1],
         "complete payload run leaves no parked numerical frame")
    need(not session.arena.live and not session.indices.live, "complete payload run closes both numerical banks")
    return {"model": result, "shared_bank_calls": holder["leases"],
            "shared_bank_returns": holder["returns"], "separate_child_arenas": 0,
            "parking_charge": dict(session.codec.machine.counts),
            "codec_charge": dict(session.codec.codec_counts)}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

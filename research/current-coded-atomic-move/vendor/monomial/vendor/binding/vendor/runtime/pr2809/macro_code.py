"""Compile fixed source schedules; numerical dimensions never enter this pass."""
from dataclasses import dataclass

import loader
loader.activate()
from control import LocalState
from driver import compile_owner
from residual_blocks import Cursor
from words import need


@dataclass(frozen=True)
class Residual:
    code: int
    plan: object
    identifier: int
    common: bool
    low: tuple
    axis: object = None
    constants: object = None


@dataclass(frozen=True)
class Code:
    operations: tuple
    staged_roles: int


def compile_node(topology, binding, mode=0):
    """Finite offline expansion of the source's q-dependent instruction word.

    The selected GL64 expansion can be enormous. This routine proves an
    effective finite emitter; practical selected runs may compile regions with
    the same finite labels. The small model uses the complete emitted tuple.
    """
    operations = [("node",)]
    staged = 0
    def residual(role, identifier, common, low):
        definition = binding.residual(identifier, common, low, mode)
        operations.append(("residual_begin", role, definition))
        if definition.axis is not None:
            operations.append(("block", definition, ("axis", definition.axis, 0)))
        else:
            cursor = Cursor(definition.plan)
            while not cursor.done:
                operations.append(("block", definition, cursor.take()))
        operations.append(("residual_end", role, definition))
    for event in topology.schedule:
        kind = event["kind"]
        if kind == "local_cover_sweep":
            for replica in range(topology.replicas):
                call = topology.call(event["stage"], replica)
                staged = max(staged, len(call.owners) + 1)
                for low in topology.catalogue.low_classes():
                    slots = []
                    for role, owner in enumerate(call.owners):
                        native, forward, backward = compile_owner(
                            topology.matrix(owner.chart), low, topology.catalogue.codes)
                        slots.append((owner.family, native, backward))
                        operations.append(("gather_route", ("stage", role), owner.family, native, forward))
                    state = LocalState(call)
                    for position, item in enumerate(call.events):
                        op, role = state.accept(position)
                        target = ("stage", role)
                        if op == 0:
                            residual(target, call.requests[position], True, low)
                        elif op == 1:
                            operations.append(("xor", target, ("stage", item[2])))
                        elif op == 2:
                            operations.append(("copy", target, "copy_source"))
                            residual("copy_source", call.requests[position], True, low)
                            operations.append(("move", "copy_source", ("stage", state.private)))
                        else:
                            need(op == 3, "closed local opcode")
                            operations.append(("clear", ("stage", state.private)))
                    state.finish()
                    for role, (family, native, backward) in enumerate(slots):
                        operations.append(("route_scatter", ("stage", role), family, native, backward))
                    for role in range(len(call.owners) + 1):
                        operations.append(("clear", ("stage", role)))
        elif kind == "idle":
            for replica in range(topology.replicas):
                for identifier in topology.idles[event["idx"]]:
                    family = topology.idle_family(identifier, replica)
                    for low in topology.catalogue.low_classes():
                        operations.append(("gather", "idle", family, low))
                        residual("idle", identifier, False, low)
                        operations.append(("scatter", "idle", family, low))
                        operations.append(("clear", "idle"))
        elif kind == "bridge":
            need(event["coefficient"] in (-1, 1), "native Boolean bridge coefficient")
            for replica in range(topology.replicas):
                for port in range(topology.ports):
                    for target, source, side in ((event["dst"], event["src"], 0),
                                                 (event["src"], event["dst"], 1)):
                        operations.append(("family_xor", topology.family(replica, target, side, port),
                                           topology.family(replica, source, side, port)))
        else:
            need(kind == "exchange", "closed global opcode")
            for replica in range(topology.replicas):
                for pair in range(topology.pairs):
                    for port in range(topology.ports):
                        operations.append(("exchange", topology.family(replica, pair, 0, port),
                                           topology.family(replica, pair, 1, port)))
        operations.append(("checkpoint", kind, event.get("stage", event.get("idx", -1))))
    operations.append(("return",))
    return Code(tuple(operations), staged)

"""Exact GF(2) payloads for the whole-word ordering boundary, not tape kernels."""

from contextlib import ExitStack, contextmanager
from dataclasses import replace
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch

import driver
import macro_machine
import model
from macro_code import Residual
from macro_machine import Machine
from plan import Plan
from topology import Owner


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Packet:
    """A complete low-keyed packet of four symbolic Boolean coordinates."""

    def __init__(self, data=None):
        self.data = {} if data is None else dict(data)

    def clear(self):
        self.data.clear()

    def close(self):
        self.clear()

    def rewind(self):
        pass  # Heads and physical traffic are deliberately outside this model.


def clone(source, *_args):
    return Packet(source.data)


def append(source, target):
    require(not target.data, "canonical commit clears its old destination")
    target.data = dict(source.data)


def transfer(source, target):
    target.data = dict(source.data)
    source.clear()


def gather(family, _context, _count, low, _fibre):
    return Packet({low: family.data[low]})


def route(source, definition, *_args):
    require(tuple(source.data) == (definition.low,), "route receives its native low")
    # An arbitrary invertible boundary permutation. This is NOT high_key.
    shift = sum(int(x) for row in definition.target_low for x in row) % 4
    bits = source.data[definition.low]
    return Packet({definition.target_low: bits[shift:] + bits[:shift]})


def scatter(family, packet, _context, _count, low, _fibre):
    require(tuple(packet.data) == (low,), "scatter receives its exact low")
    result = clone(family)
    result.data[low] = packet.data[low]
    return result


def xor(source, target, *_args):
    require(source.data.keys() == target.data.keys(), "aligned complete XOR")
    return Packet(
        {
            key: tuple(a ^ b for a, b in zip(source.data[key], target.data[key]))
            for key in source.data
        }
    )


def frozen(packet):
    return tuple(sorted(packet.data.items()))


class Residuals:
    def __init__(self):
        self.receipts = []

    def apply(self, source, identifier, common, low, *_args):
        require(tuple(source.data) == (low,), "residual receives the correct view")
        bits = list(source.data[low])
        # Noncommuting invertible shears distinguish residual order and inputs.
        axis = identifier % 4
        bits[axis] ^= bits[(axis + 1) % 4]
        following = Packet({low: tuple(bits)})
        self.receipts.append(
            (identifier, common, low, frozen(source), frozen(following))
        )
        return following


class Binding:
    def residual(self, identifier, common, low, mode):
        require(mode == 0, "one abstract boundary program")
        return Residual(
            identifier, Plan(2, 1, True, ()), identifier, common, low, axis=0
        )


class Catalogue(model.Catalogue):
    def __init__(self, reverse_lows):
        super().__init__()
        self.reverse_lows = reverse_lows

    def low_classes(self):
        values = tuple(super().low_classes())
        return iter(tuple(reversed(values)) if self.reverse_lows else values)


class Topology(model.Topology):
    def __init__(self, replicas, reverse_schedule=False, reverse_lows=False):
        require(replicas in (1, 2), "bounded fixture domain")
        super().__init__(Catalogue(reverse_lows))
        self.replicas, self.families = replicas, 4 * replicas
        if reverse_schedule:
            self.schedule = tuple(reversed(self.schedule))

    def call(self, stage, replica):
        original = super().call(stage, 0)
        owners = tuple(
            Owner(owner.family + 4 * replica, owner.chart) for owner in original.owners
        )
        return replace(original, replica=replica, owners=owners)

    def idle_family(self, identifier, replica):
        return self.catalogue.requests[identifier].family + 4 * replica

    @staticmethod
    def family(replica, pair, side, port):
        require(port == 0, "one fixture port")
        return 4 * replica + 2 * pair + side


def inputs(topology):
    lows = tuple(topology.catalogue.low_classes())
    families = {}
    for family in range(topology.families):
        families[family] = Packet(
            {
                low: tuple(
                    1 << (4 * (family * len(lows) + i) + bit) for bit in range(4)
                )
                for i, low in enumerate(lows)
            }
        )
    return families


def snapshot(families):
    return tuple(
        (family, frozen(packet)) for family, packet in sorted(families.items())
    )


class BoundaryMachine(Machine):
    """Run production dispatch/commit; substitute only the declared boundaries."""

    def __init__(self, topology, residuals, observe):
        self.context = SimpleNamespace(codes=topology.catalogue.codes)
        self.roles = {name: Packet() for name in macro_machine.NAMES}
        self.roles.update({("stage", i): Packet() for i in range(4)})
        self.roles.update(
            {("family", i): packet for i, packet in inputs(topology).items()}
        )
        self.residuals, self.observe = residuals, observe

    def count(self, label):
        return label  # Encoded extents are abstract, not measured in this audit.

    def node(self):
        pass  # Input split is the lemma's entry premise.

    def returned(self):
        return True  # Output merge is the lemma's exit premise.

    def close_geometry(self):
        pass  # Complete residual semantics are an explicit assumption.

    def residual_begin(self, role, _definition):
        self.commit(self.tape(role), "current")

    def block(self, definition, _block):
        following = self.residuals.apply(
            self.tape("current"),
            definition.identifier,
            definition.common,
            definition.low,
        )
        self.commit(following, "current")
        return False

    def families(self):
        return {
            label[1]: packet
            for label, packet in self.roles.items()
            if isinstance(label, tuple) and label[0] == "family"
        }


@contextmanager
def kernels(xor_receipts):
    def recorded_xor(source, target, *args):
        output = xor(source, target, *args)
        xor_receipts.append((frozen(source), frozen(target), frozen(output)))
        return output

    replacements = {
        "gather": gather,
        "scatter": scatter,
        "route_packet": route,
        "xor_packet": recorded_xor,
        "xor_family": recorded_xor,
    }
    with ExitStack() as stack:
        for module in (driver, macro_machine):
            for name, function in replacements.items():
                stack.enter_context(patch.object(module, name, function))
        stack.enter_context(patch.object(driver, "clone_packet", clone))
        stack.enter_context(
            patch.object(driver, "family_rows", lambda _context: Packet())
        )
        stack.enter_context(patch.object(macro_machine, "append_tape", append))
        stack.enter_context(patch.object(macro_machine, "transfer", transfer))
        yield


def logical(topology):
    families, residuals, cuts, xors = inputs(topology), Residuals(), [], []

    def observe(kind, *labels):
        if kind == "global_return":
            cuts.append((labels, snapshot(families)))

    context = SimpleNamespace(codes=topology.catalogue.codes)
    runner = driver.Driver(
        context, topology, residuals, Packet(), 1, 1, 1, 1, 1, observe=observe
    )
    with kernels(xors):
        events = runner.global_word(families)
        # An abstract nonrecursive residual returns directly; no scheduler yield.
        require(next(events, None) is None, "whole abstract source word completes")
    return {
        "final": snapshot(families),
        "cuts": cuts,
        "residuals": residuals.receipts,
        "xors": xors,
    }


def compiled(topology, code):
    residuals, cuts, xors = Residuals(), [], []

    def observe(machine, kind, *labels):
        if kind in ("local_cover_sweep", "idle", "bridge", "exchange"):
            cuts.append(((kind, *labels), snapshot(machine.families())))

    machine = BoundaryMachine(topology, residuals, observe)
    with kernels(xors):
        for operation in code.operations:
            require(
                machine.dispatch(operation) in ("next", "done"),
                "no abstract recursive jump",
            )
    require(
        not any(
            packet.data
            for label, packet in machine.roles.items()
            if not (isinstance(label, tuple) and label[0] == "family")
        ),
        "completed word clears every staged/private/current packet",
    )
    return {
        "final": snapshot(machine.families()),
        "cuts": cuts,
        "residuals": residuals.receipts,
        "xors": xors,
    }


def fingerprint(result):
    return sha256(repr(result).encode("ascii")).hexdigest()

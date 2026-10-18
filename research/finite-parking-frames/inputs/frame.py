"""Local return boundaries for sequential, completed nested callees.

The retained Tape/Park primitives own the charged bit movement. These frames
scope their descriptors and observational cleanup ledger; no fixed-tape or
adversarial-Python isolation theorem is asserted.
"""
import pipeline as prior


class ParkFrame(prior.Park):
    """Append/pop above the current caller head, never below that local floor."""
    def __init__(self, parent):
        prior.need(parent.head == len(parent.cells) and parent.head >= parent.floor,
                   'parent parking is at its current top')
        self.parent = parent
        self.meter = parent.meter
        self.cells = parent.cells
        self.floor = parent.head
        self.head = self.floor
        self.minimum_head = self.floor
        self.peak = self.floor
        self.closed = False

    def push(self, source):
        prior.need(not self.closed, 'parking frame is open')
        prior.need(source.meter is self.meter, 'parking meter agreement')
        return super().push(source)

    def pop(self, size):
        prior.need(not self.closed, 'parking frame is open')
        # Check the complete requested extent before consuming any parked bit.
        prior.need(type(size) is int and 0 <= size <= self.head - self.floor,
                   'local opaque ancestor boundary')
        return super().pop(size)

    def close(self):
        prior.need(not self.closed, 'parking frame closes once')
        prior.need(self.head == self.floor and len(self.cells) == self.floor,
                   'local parking extent restored')
        prior.need(self.parent.head == self.floor, 'caller parking descriptor unchanged')
        self.parent.peak = max(self.parent.peak, self.peak)
        self.parent.minimum_head = min(self.parent.minimum_head, self.minimum_head)
        self.closed = True


def invoke(active, inactive, park, callee):
    """Transfer the listed tapes into one frame and return the same extents.

    callee(argument, child_park) returns one rewound tape of unchanged length.
    It may recursively invoke this wrapper. Caller-owned tapes not supplied as
    arguments are outside the frame; a completed callee must not access them.
    Only successful completed returns are specified, not rollback on errors.
    """
    inactive = list(inactive)
    inputs = [active, *inactive]
    meter = active.meter
    prior.need(park.meter is meter and all(isinstance(t, prior.TrackingTape)
               and t.meter is meter and t.head == 0 for t in inputs),
               'owned inputs use one meter and rewound heads')
    prior.need(len({id(t) for t in inputs}) == len(inputs), 'distinct owned inputs')
    prior.need(all(any(t is known for known in meter.tapes) for t in inputs),
               'owned inputs are registered tapes')
    start = len(meter.tapes)
    width = len(active.data)
    local = ParkFrame(park)
    extents = [local.push(tape) for tape in inactive]
    argument = prior.TrackingTape(meter)
    prior.copy(active, argument, width)
    active.finish()
    active.erase()
    argument.rewind()

    # The callee's floor also protects this invocation's own parked packets.
    # Exposing local directly would let a callee pop those caller-owned bits.
    child_park = ParkFrame(local)
    returned = callee(argument, child_park)
    child_park.close()
    owned = {id(t) for t in inputs} | {id(t) for t in meter.tapes[start:]}
    prior.need(isinstance(returned, prior.TrackingTape) and returned.meter is meter
               and id(returned) in owned, 'return tape belongs to this invocation')
    prior.need(returned.head == 0 and len(returned.data) == width,
               'returned packet has the original extent and rewound head')
    output = prior.TrackingTape(meter)
    prior.copy(returned, output, width)
    returned.finish()
    returned.erase()
    output.rewind()
    restored = [None] * len(extents)
    for index in reversed(range(len(extents))):
        restored[index] = local.pop(extents[index])
    local.close()
    survivors = {id(t) for t in [output, *restored]}
    owned_tapes = [*inputs, *meter.tapes[start:]]
    prior.need(all(not t.data and t.head == 0 for t in owned_tapes if id(t) not in survivors),
               'all invocation-owned working tapes cleared')
    return output, restored

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with OpenAI Codex.
"""Literal local tape routes for the attributed paired-SCALE gate streams.

The chosen layout has separate little-endian real and imaginary ribbons of W
bits and a one-cell carry ribbon. All three heads start at their ribbon origin.
This is a compiled fixed-W schedule, not an encoded-width controller or a
supplier allocation. A control is XORed into one of two finite-control bits,
used at the target, then cleared by rereading its unchanged cell. The compiler
does not erase scratch, carry, or head positions.

Instruction tuples are ("move", bank, direction), ("xor", slot, bank), and
("flip", bank, control_count). A flip always reads and writes its target, even
when its controls are false. Each move is one cell. Input construction,
precondition inspection, and endpoint snapshots are unmetered fixture work;
every operation within the physical instruction stream uses Tape methods.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def wire_map(width):
    """Return the injective (ribbon, offset) map for all logical wires."""
    require(type(width) is int and 4 <= width <= 256, "width must be 4..256")
    locations = tuple((bank, offset) for bank in (0, 1) for offset in range(width))
    locations += ((2, 0),)
    require(len(set(locations)) == 2 * width + 1, "injective wire layout")
    return locations


def compile_route(width, gates):
    """Compile distinct-wire CNOT/Toffoli gates, including all origin returns."""
    locations = wire_map(width)
    heads = [0, 0, 0]
    route = []

    def visit(wire):
        bank, destination = locations[wire]
        while heads[bank] != destination:
            direction = 1 if heads[bank] < destination else -1
            route.append(("move", bank, direction))
            heads[bank] += direction
        return bank

    for gate in gates:
        require(isinstance(gate, (tuple, list)), "gate must be a tuple or list")
        require(len(gate) in (2, 3), "gate must be CNOT or Toffoli")
        require(
            all(type(wire) is int and 0 <= wire < len(locations) for wire in gate),
            "gate wire outside layout",
        )
        require(len(set(gate)) == len(gate), "gate wires must be distinct")
        controls = gate[:-1]
        for slot, wire in enumerate(controls):
            route.append(("xor", slot, visit(wire)))
        route.append(("flip", visit(gate[-1]), len(controls)))
        for slot in reversed(range(len(controls))):
            route.append(("xor", slot, visit(controls[slot])))

    for bank in range(3):
        while heads[bank]:
            route.append(("move", bank, -1))
            heads[bank] -= 1
    return tuple(route)


class Tape:
    """Finite binary ribbon whose metered access is confined to its head."""

    def __init__(self, bits):
        bits = tuple(bits)
        require(bool(bits), "empty ribbon")
        require(all(type(bit) is int and bit in (0, 1) for bit in bits), "binary ribbon")
        self._bits = bytearray(bits)
        self.head = 0
        self.counts = {"moves": 0, "reads": 0, "writes": 0}

    def read(self):
        self.counts["reads"] += 1
        return self._bits[self.head]

    def write(self, bit):
        require(type(bit) is int and bit in (0, 1), "binary write")
        self.counts["writes"] += 1
        self._bits[self.head] = bit

    def move(self, direction):
        require(type(direction) is int and direction in (-1, 1), "unit head move")
        destination = self.head + direction
        require(0 <= destination < len(self._bits), "head outside ribbon")
        self.counts["moves"] += 1
        self.head = destination

    def snapshot(self):
        """Unmetered fixture observation, never a routing primitive."""
        return tuple(self._bits)


def _instruction(instruction):
    require(
        isinstance(instruction, (tuple, list)) and len(instruction) == 3,
        "instruction must have three fields",
    )
    operation, first, second = instruction
    require(type(first) is int and type(second) is int, "integer instruction operands")
    if operation == "move":
        require(first in (0, 1, 2) and second in (-1, 1), "invalid move instruction")
    elif operation == "xor":
        require(first in (0, 1) and second in (0, 1, 2), "invalid xor instruction")
    elif operation == "flip":
        require(first in (0, 1, 2) and second in (1, 2), "invalid flip instruction")
    else:
        raise ValueError("unknown routing instruction")
    return operation, first, second


def counters(route):
    """Count primitive moves, reads and writes in a literal instruction stream."""
    result = {"moves": 0, "reads": 0, "writes": 0}
    for instruction in route:
        operation, _, _ = _instruction(instruction)
        if operation == "move":
            result["moves"] += 1
        else:
            result["reads"] += 1
            if operation == "flip":
                result["writes"] += 1
    return result


def run_route(width, route, tapes):
    """Execute on three distinct ribbons and require clean origin-return exit.

    Return a dict with unsigned `components` (real, imag), scalar `carry`,
    `heads` (real, imag, carry), two `scratch` bits, and `counters` with the
    keys moves/reads/writes. Counters report this execution's Tape method calls.
    The caller supplies the clean carry and heads at zero; validation and
    output snapshots are observations outside the metered instruction stream.
    """
    wire_map(width)
    tapes = tuple(tapes)
    require(len(tapes) == 3 and all(isinstance(tape, Tape) for tape in tapes), "three tapes required")
    require(len({id(tape._bits) for tape in tapes}) == 3, "tapes must not alias")
    before = tuple(tape.snapshot() for tape in tapes)
    require(tuple(map(len, before)) == (width, width, 1), "ribbon widths")
    require(all(tape.head == 0 for tape in tapes), "heads must start at origin")
    require(before[2] == (0,), "clean carry entrance")
    initial = {name: sum(tape.counts[name] for tape in tapes) for name in ("moves", "reads", "writes")}
    scratch = [0, 0]
    for instruction in route:
        operation, first, second = _instruction(instruction)
        if operation == "move":
            tapes[first].move(second)
        elif operation == "xor":
            scratch[first] ^= tapes[second].read()
        else:
            control = scratch[0] if second == 1 else scratch[0] & scratch[1]
            tapes[first].write(tapes[first].read() ^ control)

    after = tuple(tape.snapshot() for tape in tapes)
    require(scratch == [0, 0], "finite-control scratch must return clean")
    require(after[2] == (0,), "clean carry return")
    require(all(tape.head == 0 for tape in tapes), "heads must return to origin")
    return {
        "components": tuple(sum(bit << i for i, bit in enumerate(bits)) for bits in after[:2]),
        "carry": after[2][0],
        "heads": tuple(tape.head for tape in tapes),
        "scratch": tuple(scratch),
        "counters": {name: sum(tape.counts[name] for tape in tapes) - initial[name] for name in initial},
    }


def execute(width, gates, real, imag, carry=0):
    """Run signed component inputs and return unsigned endpoint bit patterns.

    This evaluator checks the routing contract, not signed SCALE prefix guards.
    Those remain the authenticated logical supplier's separate obligation.
    """
    route = compile_route(width, gates)
    limit = 1 << (width - 1)
    require(
        all(type(value) is int and -limit <= value < limit for value in (real, imag)),
        "signed component inputs",
    )
    require(type(carry) is int and carry == 0, "clean carry entrance")
    tapes = [Tape((value >> i) & 1 for i in range(width)) for value in (real, imag)]
    tapes.append(Tape((carry,)))
    return run_route(width, route, tapes)


def expected_counts(width, *, control=False):
    """Closed tariffs for the pinned paired-negation or two-negation circuit.

    These formulas do not apply to arbitrary gate streams accepted by execute.
    The verifier compares them to compiled streams at every width from 4..256.
    """
    wire_map(width)
    require(type(control) is bool, "boolean control choice")
    if control:
        return {"moves": 104 * width - 176, "reads": 150 * width - 96, "writes": 42 * width - 24}
    return {"moves": 64 * width - 140, "reads": 88 * width - 108, "writes": 24 * width - 28}

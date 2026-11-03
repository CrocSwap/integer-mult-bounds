"""A resident, single-ribbon reversible signed doubling circuit.

The instruction grammar follows Ali Romman's PR6513/6530 tape interface.
The adjacent-swap schedule and resident SCALE compiler are new here.
"""

MAX_WIDTH = 64
MAX_DIMENSION = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def doubling_gates(width, dimension):
    """Rotate each signed record left, then clear its duplicated sign bit."""
    require(type(width) is int and 2 <= width <= MAX_WIDTH, "width domain")
    require(type(dimension) is int and 1 <= dimension <= MAX_DIMENSION,
            "dimension domain")
    gates = []
    for record in range(2 * dimension):
        base = record * width
        for bit in range(width - 2, -1, -1):
            a, b = base + bit, base + bit + 1
            gates.extend(((a, b), (b, a), (a, b)))
        gates.append((base + width - 1, base))
    assert len(gates) == 2 * dimension * (3 * width - 2)
    return tuple(gates)


def compile_route(width, dimension, inverse=False):
    """Emit unit moves and CNOTs using one restored finite-control bit."""
    gates = doubling_gates(width, dimension)
    if inverse:
        gates = tuple(reversed(gates))
    head, route = 0, []
    for control, target in gates:
        for address, operation in ((control, "xor"), (target, "flipmask"),
                                   (control, "xor")):
            delta = address - head
            route.extend(("move", 0, 1 if delta > 0 else -1)
                         for _ in range(abs(delta)))
            head = address
            route.append((operation, 0, 0 if operation == "xor" else 1))
    route.extend(("move", 0, -1) for _ in range(head))
    require(len(route) <= 220000, "compiled route capacity")
    return tuple(route)


class Tape:
    """Fixed-capacity binary tape; every payload access is metered."""

    def __init__(self, bits, head=0):
        require(1 <= len(bits) <= 131072 and all(b in (0, 1) for b in bits),
                "binary tape capacity")
        require(type(head) is int and 0 <= head < len(bits), "initial head")
        self.bits = list(bits)
        self.head = head
        self.reads = self.writes = self.moves = 0

    def read(self):
        self.reads += 1
        return self.bits[self.head]

    def write(self, bit):
        require(bit in (0, 1), "binary write")
        self.writes += 1
        self.bits[self.head] = bit

    def move(self, direction):
        require(direction in (-1, 1), "unit move")
        require(0 <= self.head + direction < len(self.bits), "tape boundary")
        self.head += direction
        self.moves += 1

    def traffic(self):
        return self.reads, self.writes, self.moves


def seek(tape, address):
    require(type(address) is int and 0 <= address < len(tape.bits), "seek domain")
    delta = address - tape.head
    for _ in range(abs(delta)):
        tape.move(1 if delta > 0 else -1)


def execute(route, tapes):
    """Two finite-control bits; neither the instruction pointer nor heads read data."""
    require(1 <= len(tapes) <= 3 and len({id(t) for t in tapes}) == len(tapes),
            "distinct physical tapes")
    require(len(route) <= 220000, "route capacity")
    scratch = [0, 0]
    for op, first, second in route:
        if op == "move":
            tapes[first].move(second)
        elif op == "xor":
            require(first in (0, 1), "control index")
            scratch[first] ^= tapes[second].read()
        elif op == "flipmask":
            require(0 <= second <= 3, "control mask")
            flag = all(scratch[j] for j in (0, 1) if second & (1 << j))
            tapes[first].write(tapes[first].read() ^ int(flag))
        else:
            raise ValueError("instruction domain")
    require(scratch == [0, 0], "control restoration")


def transfer(source, destination, length):
    """PR6527/6530 clean transfer, including its restored control bit."""
    require(source is not destination and type(length) is int and 1 <= length <= 8192,
            "transfer domain")
    for bit in range(length):
        control = source.read()
        destination.write(destination.read() ^ control)
        source.write(source.read() ^ control)
        control ^= destination.read()
        require(control == 0, "clean transfer destination")
        if bit + 1 < length:
            source.move(1)
            destination.move(1)


def staged_scale(owner, ribbons, carry, target, width, dimension, route):
    """Unchanged PR6527 SCALE staging, used only as the comparison path."""
    start = target * 2 * dimension * width
    for returning in (False, True):
        seek(owner, start)
        for record in range(dimension):
            for component in (0, 1):
                seek(owner, start + (2 * record + component) * width)
                seek(ribbons[component], record * width)
                pair = (ribbons[component], owner) if returning else (owner, ribbons[component])
                transfer(*pair, width)
        for ribbon in ribbons:
            seek(ribbon, 0)
        if not returning:
            for record in range(dimension):
                for ribbon in ribbons:
                    seek(ribbon, record * width)
                execute(route, [*ribbons, carry])
    for ribbon in ribbons:
        seek(ribbon, 0)


def normalized_baseline(owner, ribbons, carry, fields, target, width,
                        dimension, route, evict_order, acquire_order):
    """Flush, source SCALE, reacquire the same banks, restore the owner head."""
    require(len(fields) == 2 and len(set(fields)) == 2 and target in fields,
            "resident field contract")
    entry_head = owner.head
    length = 2 * dimension * width
    for bank in evict_order:
        seek(owner, fields[bank] * length)
        transfer(ribbons[bank], owner, length)
        seek(ribbons[bank], 0)
    staged_scale(owner, ribbons, carry, target, width, dimension, route)
    for bank in acquire_order:
        seek(owner, fields[bank] * length)
        transfer(owner, ribbons[bank], length)
        seek(ribbons[bank], 0)
    seek(owner, entry_head)

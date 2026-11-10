"""Whole-tree CRT current-state composition over the paid row providers.

Topology is compiled data. Runtime coordinates, moduli and numerical values
stay on the unchanged predecessor tapes. The eight protected numerical slots
are owned zero words, physically prepared and retired at each node precision.
Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. See PROOF.md for the source-relative execution boundary.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def commands(widths, ell, reverse=False):
    """Compile the published level/row order, with disjoint nodes serialized."""
    widths = tuple(widths)
    d = len(widths)
    need(type(ell) is int and ell >= 2, 'declared ell')
    need(d >= 2 and d & (d - 1) == 0, 'dyadic axis count at least two')
    need(all(type(h) is int and h in (ell - 1, ell) for h in widths),
         'declared width family')
    result = tuple((level, start, row)
                   for level in range(1, d.bit_length())
                   for row in range(2 * ell - 1)
                   for start in range(0, d, 1 << level))
    return tuple(reversed(result)) if reverse else result


class ProtectedZeros:
    """Eight permanent owned roles, with paid current-width entry and erasure."""
    def __init__(self, w, entry):
        self.w = w
        self.ports = []
        for _ in range(8):
            port = object.__new__(entry.Port)
            port.w = w
            port.cells = bytearray([w.BLANK])
            port.head = 0
            port.meter = w.Meter()
            self.ports.append(port)
        self.started = False
        self.live = False
        self.setup_cells = 8

    def prepare(self, precision):
        # precision is a constant in this compiled node, not a decoded value.
        need(not self.live, 'protected-zero words must retire before resize')
        need(type(precision) is int and precision >= 4, 'compiled precision')
        w = self.w
        for port in self.ports:
            if self.started:
                port.step(-1)
            need(port.read() == w.BLANK, 'blank protected-zero origin')
            port.write(w.LEFT)
            port.step(1)
            for _ in range(precision):
                need(port.read() == w.BLANK, 'retired protected-zero body')
                port.write(w.ZERO)
                port.step(1)
            need(port.read() == w.BLANK, 'retired protected-zero delimiter')
            port.write(w.RIGHT)
            port.rewind()
        self.started = True
        self.live = True

    def retire(self):
        need(self.live, 'one retirement of protected-zero words')
        for port in self.ports:
            port.retire()
        self.live = False


class WholeTree:
    """One actual source owner and one reusable numerical/ROM workspace.

The dependency modules and their theorems are explicit provider parameters.
No coordinate or numerical result is supplied by an observer/oracle.
"""
    def __init__(self, modules, workspace_module, query_module, source, widths, ell):
        helper, base, rom, original, adapter, program = modules
        w, records, entry, numeric, caller_module, crt, row_module = base
        self.w, self.records = w, records
        self.entry, self.numeric, self.row_module = entry, numeric, row_module
        self.rom, self.program = rom, program
        self.query_module, self.adapter = query_module, adapter
        self.source, self.widths, self.ell = source, tuple(widths), ell
        self.schedule = commands(widths, ell)
        self.workspace = workspace_module.Workspace()
        self.guards = ProtectedZeros(w, entry)
        self.staging = original.Tape()

    def step(self, command, fault=None):
        level, start, row = command
        size = 1 << level
        middle, stop = start + size // 2, start + size
        active = any(self.widths[i] == self.ell or row not in (self.ell - 1, self.ell)
                     for i in range(middle, stop))
        if not active:
            return None  # Literal idle: no provider and no tape operation.
        precision = 1 + sum(self.widths[start:stop])
        self.guards.prepare(precision)
        query = self.query_module.RowQuery(
            self.w, self.records, self.entry, self.numeric, self.row_module,
            self.rom, self.program, self.source, self.guards.ports,
            self.widths, self.ell, level, start, row, self.workspace,
            fault=fault)
        self.adapter.consume_into_source(query, self.staging, self.widths, level, start)
        self.guards.retire()
        return query

    def run(self, reverse=False):
        schedule = reversed(self.schedule) if reverse else self.schedule
        for command in schedule:
            self.step(command)


def bank_bound(precision, height):
    n = 1 << height
    return (5 * precision * n * (height * height + 3 * height + 1)
            + n * (4 * height - 1) + 48 * precision + 2 * height + 104)


def row_bound(widths, ell, command):
    """The complete predecessor sum plus paid variable-precision preparation."""
    level, start, row = command
    size = 1 << level
    middle, stop = start + size // 2, start + size
    active = [i for i in range(middle, stop)
              if widths[i] == ell or row not in (ell - 1, ell)]
    if not active:
        return 0
    precision = 1 + sum(widths[start:stop])
    length = 2 + sum(3 * h + 4 for h in widths)
    stream = 2 + sum(widths[middle:stop]) + size // 2
    work = length + (size + 1) * (precision + 2)
    work += sum(((1 << widths[i]) + 1) * (widths[i] + 1)
                + (1 << widths[i]) * (2 * widths[i] - 1)
                + 2 * widths[i] + 4 for i in active)
    bound = (2**20 * (precision + 2)**4 + 2**16 * (precision + 2)**2
             + 128 * (length + precision + size + 1)
             + 4096 * (work + length + stream))
    bound += sum(2 * 10**6 * precision**2 * ((1 << widths[i]) + 1)**3
                 * (widths[i] + 1)**4 for i in active)
    # Stable-workspace entry + explicit protected-zero prepare/retire.
    return bound + 4 * 63 + 118 + 2**12 * (precision + 2)


def whole_bound(widths, ell, directions=1):
    need(directions in (1, 2), 'one traversal or a forward/reverse pair')
    return directions * sum(row_bound(widths, ell, c) for c in commands(widths, ell)) + 8


def retained_bound(widths, ell):
    """Rolewise maximum envelope, including the supplied axis tape and guards."""
    d, address = len(widths), sum(widths)
    precision = address + 1
    source = 2 + sum(3 * h + 4 for h in widths)
    stream = 2 + address + d
    numerical = 58 * (precision + 2) + 5 * (d * (2 * precision + 4) + 2)
    rom = 52 * bank_bound(precision, ell)
    query = 2 * (ell + 2) + stream
    return source + stream + 8 * (precision + 2) + numerical + rom + query

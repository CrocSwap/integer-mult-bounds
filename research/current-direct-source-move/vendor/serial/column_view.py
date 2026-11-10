"""Physically encoded serialization into genuine one-column monomial calls.

Runtime integers remain on fixed raw binary tapes. Construction depends only
on the finite recipe rank. Prepared for @CubeJerry with substantial OpenAI
assistance. Apache-2.0.
"""
from serial_sources import activate, need

S = activate()
R = S.rows
ROLES = dict(R.SCHEMA)
PARENT, VIEW = R.HEADER, R.CHILD_HEADER
FBOUND, OLD_K, COLUMN, ACC, SUM, M = range(40, 46)
PORTS = 46
PRIVATE = tuple(i for i in range(PORTS) if i != PARENT)
FIELDS = tuple(port for _, port in R.SCHEMA)


def literal(b, tape, value):
    """Only a fixed compile-time integer is supplied here."""
    need(type(value) is int and value >= 0, "fixed nonnegative literal")
    b.empty(tape)
    for digit in bin(value)[2:][::-1]:
        b.write(tape, digit)
        b.move(tape, 1)
    b.rewind(tape)


def compile_prepare(rank):
    need(type(rank) is int and 1 <= rank <= 73, "fixed compiled monomial rank")
    b = R.Builder()
    for port in (PARENT, *PRIVATE):
        b.boundary(port)
    for port in PRIVATE:
        b.empty(port)
    b.decode(PARENT, FIELDS)
    b.canonical(ROLES["f"], positive=True)
    b.canonical(ROLES["K"], positive=True)
    b.copy(ROLES["f"], FBOUND)
    b.copy(ROLES["K"], OLD_K)
    literal(b, COLUMN, 0)
    literal(b, ACC, 0)
    loop, more, end = (b.fresh("product") for _ in range(3))
    b.mark(loop)
    b.compare(COLUMN, FBOUND, more, end, "reject")
    b.mark(more)
    b.add(ACC, OLD_K, SUM)
    b.clear(ACC)
    b.copy(SUM, ACC)
    b.clear(SUM)
    b.increment(COLUMN)
    b.go(loop)
    b.mark(end)
    b.clear(ROLES["K"])
    b.copy(ACC, ROLES["K"])
    b.clear(ACC)
    b.clear(ROLES["f"])
    literal(b, ROLES["f"], 1)
    b.clear(ROLES["selected_axes"])
    literal(b, M, rank)
    b.add(M, ROLES["remainder"], ROLES["selected_axes"])
    b.clear(M)
    b.clear(COLUMN)
    literal(b, COLUMN, 0)
    b.encode(FIELDS, VIEW)
    b.code.append(("result", "ready"))
    return b.close()


def compile_next():
    b = R.Builder()
    b.clear(VIEW)
    b.increment(COLUMN)
    more, end = (b.fresh("column") for _ in range(2))
    b.compare(COLUMN, FBOUND, more, end, "reject")
    b.mark(more)
    b.add(ROLES["rho"], OLD_K, SUM)
    b.clear(ROLES["rho"])
    b.copy(SUM, ROLES["rho"])
    b.clear(SUM)
    b.encode(FIELDS, VIEW)
    b.code.append(("result", "ready"))
    b.mark(end)
    b.code.append(("result", "finished"))
    return b.close()


def compile_release():
    b = R.Builder()
    for port in PRIVATE:
        b.clear(port)
    b.rewind(PARENT)
    return b.close()


NEXT, RELEASE = compile_next(), compile_release()


def validate(table):
    for row in table:
        need(row[0] in ("read", "write", "move", "goto", "done", "result", "reject", "quarantine"),
             "literal local instruction vocabulary")
        if row[0] in ("read", "write", "move"):
            need(type(row[1]) is int and 0 <= row[1] < PORTS, "fixed role")
        if row[0] == "write":
            need(row[1] != PARENT and row[2] in (R.ZERO, R.ONE, R.BLANK),
                 "parent and markers are read-only")
        if row[0] == "move":
            need(row[2] in (-1, 1), "unit movement")
        if row[0] == "result":
            need(row[1] in ("ready", "finished"), "finite decision alphabet")
    return len(table)


class ColumnView:
    port_count = len(PRIVATE)

    def __init__(self, rank):
        self.prepare_table = compile_prepare(rank)
        for table in (self.prepare_table, NEXT, RELEASE):
            validate(table)
        self.ports = self.parent = self.work = None
        self.active = False

    def bind(self, work, context):
        need(not self.active and len(work) == self.port_count,
             "complete fixed descriptor bank before execution")
        need(len(set(map(id, work))) == len(work)
             and all(port is not context.tape for port in work),
             "distinct descriptor segments; actual disjointness is a caller premise")
        self.parent, self.work = context, tuple(work)
        self.ports = {PARENT: R.PhysicalPort(context.tape)}
        self.ports.update((role, R.PhysicalPort(port)) for role, port in zip(PRIVATE, work))

    @property
    def context(self):
        need(self.ports is not None, "bound descriptor bank")
        return S.abi.BinaryContextPort(self.ports[VIEW].tape)

    def prepare(self):
        need(self.ports is not None and not self.active, "single active descriptor iteration")
        self.active = True
        try:
            result, _steps = R.run_choice(self.prepare_table, self.ports)
            need(result == "ready", "first column available")
        except Exception:
            self.release()
            raise

    def advance(self):
        need(self.active, "active descriptor iteration")
        result, _steps = R.run_choice(NEXT, self.ports)
        need(result in ("ready", "finished"), "finite column decision")
        return result

    def release(self):
        need(self.active, "active descriptor iteration to retire")
        try:
            R.run(RELEASE, self.ports)
        finally:
            self.active = False


class SerialProvider:
    """Actual unchanged monomial, with physically priced descriptor iteration.

Partial column updates can precede a later named arithmetic rejection. A
protected whole-field wrapper is required for whole-job public atomicity.
No provider is reset, recreated, or given decoded shape values between calls.
"""
    def __init__(self, literal_recipe, native_factory, inverse=False):
        self.native = S.adapter.Provider(literal_recipe, native_factory, inverse=inverse)
        self.view = ColumnView(self.native.rank)
        self.field = self.work = None

    @property
    def port_count(self):
        return self.view.port_count + self.native.port_count

    def bind(self, work, field, context):
        need(len(work) == self.port_count and len(set(map(id, work))) == len(work),
             "fixed distinct complete inventory")
        need(field.tape is not context.tape
             and all(field.tape is not p and context.tape is not p for p in work),
             "field, parent descriptor and work are disjoint")
        self.work, self.field = tuple(work), field
        self.view.bind(work[:self.view.port_count], context)
        self.native.bind(work[self.view.port_count:])

    def run(self):
        need(self.work is not None, "bound serial monomial")
        try:
            self.view.prepare()
            while True:
                self.native.run(self.field, self.view.context)
                if self.view.advance() == "finished":
                    break
        finally:
            if self.view.active:
                self.view.release()

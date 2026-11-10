"""Literal encoded native view at the first normalized caller-local helper.

All runtime shape data stay on raw binary tapes. The only loop bounds in
construction are fixed roles and finite table states, before runtime varies.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from header_sources import activate, need

S = activate()
R = S.rows
SCHEMA = tuple(name for name, _ in R.SCHEMA)
ROLES = dict(R.SCHEMA)
PARENT, VIEW = R.HEADER, R.CHILD_HEADER
PRIVATE = tuple(i for i in range(R.FIRST_ROLE) if i != PARENT)
AMBIENT = 145
NATIVE_RANK = 9


def compile_prepare():
    """Valid ordinary N=145 header -> same complete field, local nine view.

Valid parent geometry and the fixed source placement are input premises.
This checks canonical encoding and positive f, not an alternate parent
geometry calculation or a reconstruction of the global numerical tariff.
"""
    b = R.Builder()
    for port in (PARENT, *PRIVATE):
        b.boundary(port)
    for port in PRIVATE:
        b.empty(port)
    fields = tuple(port for _, port in R.SCHEMA)
    b.decode(PARENT, fields)
    b.canonical(ROLES["f"], positive=True)
    b.clear(ROLES["selected_axes"])
    b.multiply_constant(ROLES["f"], ROLES["selected_axes"], NATIVE_RANK)
    b.clear(ROLES["entry_start"])
    b.copy(ROLES["active_start"], ROLES["entry_start"])
    b.clear(ROLES["remainder"])
    b.write(ROLES["remainder"], R.ZERO)
    b.encode(fields, VIEW)
    for port in fields:
        b.clear(port)
    return b.close()


def compile_release():
    """Retire current prefixes and restore origins, retaining old backing."""
    b = R.Builder()
    for port in PRIVATE:
        b.clear(port)
    b.rewind(PARENT)
    return b.close()


PREPARE = compile_prepare()
RELEASE = compile_release()


def validate_tables():
    for table in (PREPARE, RELEASE):
        for row in table:
            need(row[0] in ("read", "write", "move", "goto", "done", "reject", "quarantine"),
                 "literal local table vocabulary")
            if row[0] in ("read", "write", "move"):
                need(type(row[1]) is int and 0 <= row[1] < R.FIRST_ROLE,
                     "fixed physical role")
            if row[0] == "write":
                need(row[1] != PARENT and row[2] in (R.ZERO, R.ONE, R.BLANK),
                     "parent and all origin markers are read-only")
            if row[0] == "move":
                need(row[2] in (-1, 1), "unit movement")
    return dict(prepare_instructions=len(PREPARE), release_instructions=len(RELEASE),
                private_ports=len(PRIVATE), parent_role=PARENT, view_role=VIEW,
                parent_ambient=AMBIENT, native_rank=NATIVE_RANK)


TABLE_REPORT = validate_tables()


class HeaderView:
    """One fixed physical bank, borrowed parent, and read-only native view."""
    port_count = len(PRIVATE)

    def __init__(self):
        self.ports = self.parent = self.work = None
        self.active = False

    def bind(self, work, context):
        need(not self.active and len(work) == self.port_count,
             "complete fixed header bank before execution")
        need(len(set(map(id, work))) == len(work)
             and all(port is not context.tape for port in work),
             "distinct header segments; physical disjointness is a caller premise")
        self.parent, self.work = context, tuple(work)
        self.ports = {PARENT: R.PhysicalPort(context.tape)}
        self.ports.update((role, R.PhysicalPort(port)) for role, port in zip(PRIVATE, work))

    @property
    def context(self):
        need(self.ports is not None, "bound header bank")
        return S.abi.BinaryContextPort(self.ports[VIEW].tape)

    def prepare(self):
        need(self.ports is not None and not self.active, "one active native view")
        self.active = True
        try:
            return R.run(PREPARE, self.ports)
        except Exception:
            self.release()
            raise

    def release(self):
        need(self.ports is not None and self.active, "an active view to retire")
        try:
            return R.run(RELEASE, self.ports)
        finally:
            self.active = False


class NativeEntrance:
    """Actual typed caller cut -> unchanged published monomial service.

The production path calls the real native service, never a payload callback.
Its full huge-field path is covered relatively by the inherited endpoint;
bounded evidence exercises metadata and actual phase controls separately.
"""
    def __init__(self, event, route, native_factory):
        from source_binding import bind_event
        adapted, self.report = bind_event(event, route)
        self.native = S.selected.Service(adapted, native_factory)
        self.view = HeaderView()
        self.bound = False

    @property
    def port_count(self):
        return self.view.port_count + self.native.port_count

    def bind(self, work, fields, context):
        need(len(work) == self.port_count and len(set(map(id, work))) == len(work),
             "fixed distinct header and native banks")
        owner = self.report["owner"]
        need(owner in fields and fields[owner].tape is not context.tape
             and all(fields[owner].tape is not port and context.tape is not port for port in work),
             "complete actual owner field and disjoint borrowed context")
        self.view.bind(work[:self.view.port_count], context)
        self.native.bind(work[self.view.port_count:], fields, self.view.context)
        self.bound = True

    def run(self):
        need(self.bound, "native entrance bound before input")
        self.view.prepare()
        try:
            self.native.run()
        finally:
            self.view.release()

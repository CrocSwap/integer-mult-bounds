"""Literal LEAF-only header view: replace f by rank*f, retain 22 values.

The resulting metadata are not a general native or monomial descriptor.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from all_leaf_sources import activate, need

S = activate()
R = S.rows
ROLES = dict(R.SCHEMA)
PARENT, VIEW = R.HEADER, R.CHILD_HEADER
PRIVATE = tuple(i for i in range(R.FIRST_ROLE) if i != PARENT)


def prepare_table(rank):
    need(type(rank) is int and 1 <= rank <= 8, "compiled selected positive source rank")
    b = R.Builder()
    for port in (PARENT, *PRIVATE):
        b.boundary(port)
    for port in PRIVATE:
        b.empty(port)
    fields = tuple(port for _, port in R.SCHEMA)
    b.decode(PARENT, fields)
    b.canonical(ROLES["f"], positive=True)
    # VIEW is blank after decoding. Use it as the product scratch, then clear
    # it before canonical encoding. No other decoded field is overwritten.
    b.multiply_constant(ROLES["f"], VIEW, rank)
    b.clear(ROLES["f"])
    b.copy(VIEW, ROLES["f"])
    b.clear(VIEW)
    b.encode(fields, VIEW)
    for port in fields:
        b.clear(port)
    return b.close()


def release_table():
    b = R.Builder()
    for port in PRIVATE:
        b.clear(port)
    b.rewind(PARENT)
    return b.close()


RELEASE = release_table()


class LeafView:
    port_count = len(PRIVATE)

    def __init__(self, rank):
        self.rank, self.table = rank, prepare_table(rank)
        self.ports = self.parent = self.work = None
        self.active = False

    def bind(self, work, context):
        need(not self.active and len(work) == self.port_count
             and len(set(map(id, work))) == len(work)
             and all(port is not context.tape for port in work), "fixed disjoint leaf-header bank")
        self.parent, self.work = context, tuple(work)
        self.ports = {PARENT: R.PhysicalPort(context.tape)}
        self.ports.update((role, R.PhysicalPort(port)) for role, port in zip(PRIVATE, work))

    @property
    def context(self):
        need(self.ports is not None, "bound leaf-header view")
        return S.common.abi.BinaryContextPort(self.ports[VIEW].tape)

    def prepare(self):
        need(self.ports is not None and not self.active, "one leaf-header use at a time")
        self.active = True
        try:
            return R.run(self.table, self.ports)
        except Exception:
            self.release()
            raise

    def release(self):
        need(self.active, "active leaf-header view")
        try:
            return R.run(RELEASE, self.ports)
        finally:
            self.active = False


class PositiveChild:
    """Exact source-rank child; the parent is never given scaled f semantics."""
    def __init__(self, rank):
        self.view = LeafView(rank)
        self.native = S.common.leaf_provider.Provider()
        self.parent = self.work = None

    @property
    def port_count(self):
        return self.view.port_count+self.native.port_count

    def bind(self, work, context):
        need(len(work) == self.port_count and len(set(map(id, work))) == len(work),
             "complete fixed positive-child inventory")
        need(all(port is not context.tape for port in work), "child header/numerical banks disjoint from parent")
        self.parent, self.work = context, tuple(work)
        self.view.bind(work[:self.view.port_count], context)
        self.native.bind(work[self.view.port_count:])

    def run(self, field, context):
        need(self.parent is not None and context.tape is self.parent.tape
             and field.tape is not context.tape
             and all(field.tape is not port for port in self.work),
             "bound parent and disjoint complete child field")
        self.view.prepare()
        try:
            # The unchanged leaf physically checks rank*f <= original cutoff.
            # n/t/H and the nine-vector monomial semantics remain on parent.
            return self.native.run(field, self.view.context)
        finally:
            self.view.release()

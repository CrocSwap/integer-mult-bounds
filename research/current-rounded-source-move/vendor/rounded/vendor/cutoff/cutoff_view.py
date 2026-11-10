"""LEAF-private translation (f,t) -> (r*f,r*t) using literal encoded tables.

This view is not a general native/ordinary/root descriptor. Its only numeric
consumer is the unchanged positive leaf. Prepared for @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
"""
from cutoff_sources import activate, need

S=activate(); R=S.rows
ROLES=dict(R.SCHEMA)
PARENT,VIEW=R.HEADER,R.CHILD_HEADER
PRIVATE=S.view.PRIVATE
RELEASE=S.view.RELEASE


def prepare_table(rank):
    need(type(rank) is int and 1 <= rank <= 8, "fixed selected positive rank")
    b=R.Builder()
    for port in (PARENT,*PRIVATE):
        b.boundary(port)
    for port in PRIVATE:
        b.empty(port)
    fields=tuple(port for _,port in R.SCHEMA)
    b.decode(PARENT,fields)
    for name in ("f","cutoff"):
        b.canonical(ROLES[name],positive=True)
    # The two source multipliers are compile-time constants. Every runtime
    # digit and carry is read/written on the unchanged physical tape alphabet.
    for name in ("f","cutoff"):
        source=ROLES[name]
        b.multiply_constant(source,VIEW,rank)
        b.clear(source); b.copy(VIEW,source); b.clear(VIEW)
    b.encode(fields,VIEW)
    for port in fields:
        b.clear(port)
    return b.close()


class CutoffView(S.view.LeafView):
    """Same fixed39-port lifecycle, with two paid changed metadata fields."""
    def __init__(self,rank):
        self.rank,self.table=rank,prepare_table(rank)
        self.ports=self.parent=self.work=None
        self.active=False


class PositiveChild(S.view.PositiveChild):
    """Parent f<=t iff actual unchanged private leaf guard r*f<=r*t."""
    def __init__(self,rank):
        self.view=CutoffView(rank)
        self.native=S.common.leaf_provider.Provider()
        self.parent=self.work=None

    def run(self,field,context):
        need(self.parent is not None and context.tape is self.parent.tape
             and field.tape is not context.tape
             and all(field.tape is not port for port in self.work),
             "bound unchanged parent and complete disjoint leaf field")
        self.view.prepare()
        try:
            return self.native.run(field,self.view.context)
        finally:
            self.view.release()


class PaidService:
    """Exact raw selected PAID binding; no remap/token erasure is introduced."""
    def __init__(self,event):
        triple,_op,record=S.catalog.bind_paid(event)
        self.owner=triple[1].fields[0]; self.rank=record["rank"]
        self.provider=PositiveChild(self.rank)
        self.field=self.context=None

    @property
    def port_count(self):
        return self.provider.port_count

    bind=S.selected.PaidService.bind
    run=S.selected.PaidService.run

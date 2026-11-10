"""Protected once-rounded whole raw MOVE, with rounding after the exact exit.

The full widened direct coordinator keeps its own protected stage and its
complete invoice. No numerical routine is replaced by an oracle or callback.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from rounded_move_sources import activate,need

S=activate();P=S.rounded

class ExactMoveChild:
    """Adapt fixed direct-MOVE bindings to the borrowed-field child protocol."""
    def __init__(self,triple,ordinary_factory):
        self.engine=S.direct.DirectMove(triple,ordinary_factory)
        self.work=self.context=self.field=None

    @property
    def port_count(self):return self.engine.port_count

    def bind(self,work,context):
        # Completed numerical binding follows immediately in attach(), before
        # any runtime input is read. No metadata value selects a work role.
        need(len(work)==self.port_count and len(set(map(id,work)))==len(work)
             and all(p is not context.tape for p in work),'fixed exact-MOVE inventory')
        self.work,self.context=tuple(work),context

    def attach(self,field):
        need(self.work is not None and self.field is None,'one fixed widened-field binding')
        self.field=field
        self.engine.bind(self.work,{self.engine.owner:field},self.context)

    def run(self,field,context):
        need(self.field is not None and field.tape is self.field.tape
             and context.tape is self.context.tape,'unchanged prebound widened whole-MOVE field')
        return self.engine.run()

class RoundedMove(P.Provider):
    """612+Q_R+Q_L roles; the cap64 predecessor factory gives 4368.

    All original f<=cutoff and full nine-block geometry premises remain.
    The record/row-only widened parent is newly proved suitable for serial
    monomials. The separately f/t-scaled positive view stays LEAF-private.
    """
    def __init__(self,triple,ordinary_factory):
        actual,_original,record=S.catalog.bind_move(triple)
        self.rank,self.owner=record['rank'],actual[1].fields[0]
        self.child=ExactMoveChild(triple,ordinary_factory)
        with P.C.collect_tapes() as tapes:
            self.pool=P.ScratchPool(128);self.scope=P.OuterScope(self.pool)
            self.header_guide,self.length_guide=P.Tape(),P.Tape()
        self.cohort=P.L.LeafCohort(tapes)
        self.parent=self.work=self.field=self.context=None

    def bind(self,work,fields,context):
        need(self.owner in fields,'actual whole-MOVE owner field')
        self.field,self.context=fields[self.owner],context
        need(self.field.tape is not context.tape
             and all(self.field.tape is not p for p in work),'disjoint original whole-MOVE field')
        P.Provider.bind(self,work,context)
        self.child.attach(self.expanded)

    def run(self):
        need(self.field is not None,'whole rounded MOVE bound before runtime')
        # The inherited outer order is lift -> child.run -> drop -> commit.
        # Here child.run is the complete exact entrance -> C -> exit -> commit,
        # so its exit necessarily precedes the sole final upward rounding.
        return P.Provider.run(self,self.field,self.context)

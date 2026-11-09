"""Selected source-complete direct positive child and protected MOVE join.

Whole MOVE semantics remain relative to both monomial contracts. Prepared
for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from all_leaf_sources import activate, need
from leaf_view import PositiveChild
from source_catalog import bind_move, bind_paid

S = activate()


class PaidService:
    def __init__(self, event):
        triple, _op, record = bind_paid(event)
        self.owner = triple[1].fields[0]
        self.rank = record["rank"]
        self.provider = PositiveChild(self.rank)
        self.field = self.context = None

    @property
    def port_count(self):
        return self.provider.port_count

    def bind(self, work, fields, context):
        need(self.owner in fields, "complete actual paid owner field")
        self.field, self.context = fields[self.owner], context
        need(self.field.tape is not context.tape and all(self.field.tape is not x for x in work),
             "paid field disjoint from descriptor and private banks")
        self.provider.bind(work, context)

    def run(self):
        need(self.field is not None, "source-paid ports bound before runtime")
        return self.provider.run(self.field, self.context)


class Move:
    def __init__(self, triple, ordinary_factory):
        actual, _op, record = bind_move(triple)
        self.owner, self.rank = actual[1].fields[0], record["rank"]
        self.entry = S.common.monomial.Provider(record["right"], ordinary_factory)
        self.leaf = PositiveChild(self.rank)
        self.exit = S.common.monomial.Provider(record["left"], ordinary_factory)
        self.work = self.field = self.context = self.stage = None

    @property
    def port_count(self):
        return 1+self.entry.port_count+self.leaf.port_count+self.exit.port_count

    def bind(self, work, fields, context):
        need(len(work) == self.port_count and len(set(map(id, work))) == len(work),
             "complete source-dependent fixed MOVE inventory")
        need(self.owner in fields, "complete actual source owner field")
        field = fields[self.owner]
        need(field.tape is not context.tape
             and all(field.tape is not x and context.tape is not x for x in work),
             "complete disjoint MOVE grant")
        self.work, self.field, self.context = tuple(work), field, context
        self.stage = S.common.abi.CodedPort(work[0])
        a = 1; b = a+self.entry.port_count; c = b+self.leaf.port_count
        self.entry.bind(work[a:b])
        self.leaf.bind(work[b:c], context)
        self.exit.bind(work[c:])

    # The exact public protected copy/commit/retire control is reused.
    # Only the leaf receives its derived f'=rank*f view; both monomials get
    # the untouched parent descriptor through the unchanged run sequence.
    commit = S.core.AtomicMove.commit
    run = S.core.AtomicMove.run

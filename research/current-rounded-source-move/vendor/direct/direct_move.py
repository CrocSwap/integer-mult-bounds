"""Protected selected raw MOVE through serial monomials and a ranked C leaf.

No ordinary numerical runtime premise is used on the admitted direct branch.
All setup, complete fixed cohorts and inherited physical primitives remain.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from direct_sources import activate, need

S = activate()


class DirectMove:
    def __init__(self, triple, ordinary_factory):
        actual, _original, record = S.catalog.bind_move(triple)
        self.owner = actual[1].fields[0]
        self.rank = record["rank"]
        self.entry = S.serial(record["right"], ordinary_factory)
        self.child = S.child(self.rank)
        self.exit = S.serial(record["left"], ordinary_factory)
        self.work = self.field = self.context = self.stage = None

    @property
    def port_count(self):
        return 1+self.entry.port_count+self.child.port_count+self.exit.port_count

    def bind(self, work, fields, context):
        need(len(work) == self.port_count and len(set(map(id, work))) == len(work),
             "complete fixed direct-MOVE inventory")
        need(self.owner in fields, "actual complete selected source owner")
        field = fields[self.owner]
        need(field.tape is not context.tape and
             all(field.tape is not p and context.tape is not p for p in work),
             "public field, parent and all private cohorts are disjoint")
        self.work, self.field, self.context = tuple(work), field, context
        self.stage = S.abi.CodedPort(work[0])
        a = 1; b = a+self.entry.port_count; c = b+self.child.port_count
        self.entry.bind(work[a:b], self.stage, context)
        self.child.bind(work[b:c], context)
        self.exit.bind(work[c:], self.stage, context)

    # Exactly the previously verified complete raw-bit commit loop.
    commit = S.atomic.commit

    def run(self):
        need(self.work is not None, "direct-MOVE ports bound before execution")
        S.abi.transfer(self.field.tape, self.stage.tape)
        try:
            self.entry.run()
            self.child.run(self.stage, self.context)
            self.exit.run()
            self.commit()
        finally:
            S.abi.retire(self.stage.tape)

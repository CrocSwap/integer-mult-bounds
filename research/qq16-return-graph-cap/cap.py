"""Source-bound return-cut graph envelope, separate from payload storage.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import types

SKIP = {'binding', 'catalogue', 'group', 'data', 'source', 'native_child', 'at_fence',
        'observe', 'codes', 'recipes', 'template', 'packet', 'core', 'events', 'word'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def inspect(owner, Tape, stops=()):
    seen = set()
    objects = []
    edges = attributes = 0

    def visit(value):
        nonlocal edges, attributes
        if id(value) in seen or id(value) in stops:
            return
        seen.add(id(value))
        objects.append(value)
        if isinstance(value, Tape):
            return
        if isinstance(value, dict):
            children = list(value.values())
        elif isinstance(value, (tuple, list)):
            children = list(value)
        elif not isinstance(value, (type, types.ModuleType, types.FunctionType, types.MethodType)) and hasattr(value, '__dict__'):
            attributes += len(vars(value))
            children = [v for k, v in vars(value).items() if k not in SKIP]
        else:
            children = []
        edges += len(children)
        for child in children:
            visit(child)

    visit(owner)
    return dict(vertices=len(seen), edges=edges, attributes=attributes), objects


def weight(shape):
    return sum(shape[k] for k in ('vertices', 'edges', 'attributes'))


def recipe_bound(dimension):
    need(type(dimension) is int and 0 < dimension <= 73, 'source monomial dimension')
    return 3 * dimension * dimension + 3 * dimension + 20


class ReturnCap:
    """Compile once before numerical input; do not collect historical graphs."""
    def __init__(self, protocol, Tape):
        self.Tape = Tape
        self.owners = (protocol.installation.service, protocol.installation.native_child, protocol.parent)
        self.schemas = {}
        self.parameters = []
        self.tapes = set()
        for owner in self.owners:
            shape, objects = inspect(owner, Tape)
            for value in objects:
                if isinstance(value, Tape):
                    self.tapes.add(id(value))
                elif hasattr(value, '__dict__') and not isinstance(value, (type, types.ModuleType, types.FunctionType, types.MethodType)):
                    self.schemas.setdefault(type(value), set()).update(vars(value))
            scalar = max(weight(inspect(v, Tape)[0]) for v in owner.scalar.recipes.values())
            dimension = owner.binding.dimension
            slots = owner.bank.slots
            s = weight(shape)
            self.parameters.append(dict(constructor_weight=s, dimension=dimension, slots=slots,
                                        scalar_recipe_weight=scalar,
                                        owner_cap=2*s + 43 + recipe_bound(dimension) + scalar + 2*slots + 128))
        i = protocol.installation
        self.engine_lengths = tuple(map(len, i.engine_roles))
        self.auxiliary = len(protocol.auxiliary)
        self.storage = len(i.storage.roles)
        acquisition = i.acquisition
        self.acquired = len(acquisition.packets) + 1 + len(acquisition.pool.tapes)
        self.list_cap = 2*sum(self.engine_lengths) + 2*self.auxiliary + self.storage + self.acquired + 1
        self.handle_cap = len(self.tapes) + self.auxiliary + self.storage + self.acquired
        self.size = max(self.handle_cap, sum(p['owner_cap'] for p in self.parameters) + self.list_cap)
        self.schemas[type(protocol.parent)].add('enter_child')
        self.schemas[type(i.service)].add('enter_child')

    def check(self, protocol, snapshot):
        need(tuple(map(len, protocol.installation.engine_roles)) == self.engine_lengths, 'fixed engine role cardinalities')
        need(len(protocol.auxiliary) == self.auxiliary and len(protocol.installation.storage.roles) == self.storage,
             'fixed supplied role cardinalities')
        for owner, parameter, encoded in zip(self.owners, self.parameters, snapshot['graphs'], strict=True):
            shape, objects = inspect(owner, self.Tape)
            need(shape == dict(vertices=len(encoded['rows']), edges=sum(len(r[2]) for r in encoded['rows']),
                               attributes=encoded['attributes']), 'independent exact graph size')
            need(weight(shape) <= parameter['owner_cap'], 'derived owner graph cap')
            native = owner.monomial.compact.binary.native
            runtime = native.runtime
            need(runtime.geometry_state is None, 'retired runtime geometry at external return')
            need(runtime.numerical.machine.tapes == [{}, {}], 'closed numerical parking baseline')
            need(all(len(bank.available) <= bank.capacity for bank in (*native.banks, runtime.arena, runtime.indices)),
                 'fixed numerical inventory capacity')
            for value in objects:
                name = type(value).__name__
                if name == 'ScratchPool':
                    need(not value.live, 'no retained lease at external return')
                if name == 'OuterScope':
                    need(value.manager is None, 'suspended or closed source scope at external return')
                if type(value) in self.schemas:
                    need(set(vars(value)) <= self.schemas[type(value)], 'no undeclared retention attribute')
            selection = owner.bank.selection
            need(selection is None or (type(selection) is dict and len(selection) <= parameter['slots'] and
                 all(type(v) is int and 0 <= v < parameter['slots'] for v in selection.values())),
                 'bounded source bank selection')
        total = sum(weight(dict(vertices=len(g['rows']), edges=sum(len(r[2]) for r in g['rows']),
                                attributes=g['attributes'])) for g in snapshot['graphs'])
        total += sum(map(len, snapshot['saved']))
        total += sum(len(snapshot[k]) for k in ('external', 'auxiliary', 'storage', 'acquired')) + 1
        need(total <= self.size, 'derived complete graph contract')
        need(all(x <= self.handle_cap for key in ('saved',) for row in snapshot[key] for x in row),
             'compiled lifetime handle universe')
        return total

# SPDX-License-Identifier: Apache-2.0
"""Read-only state/measurement oracles; never a reset or machine operation."""
from hashlib import sha256

_CODEC_BACKING = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def arenas(engine):
    return tuple((f'banks[{i}]', bank) for i, bank in enumerate(engine.banks)) + (
        ('runtime.arena', engine.runtime.arena), ('runtime.indices', engine.runtime.indices))


def tapes(*objects):
    from records import Tape
    seen, result = set(), []
    ignored = {'binding', 'catalogue', 'topology', 'programs', 'program', 'recipes',
               'recipe', 'actions', 'observe', 'codes', 'specifications', 'meter',
               'counts', 'codec_counts', 'context', 'geometry_state', 'transform', 'manager'}
    def visit(value, path):
        if id(value) in seen: return
        seen.add(id(value))
        if isinstance(value, Tape):
            result.append((path, value)); return
        if isinstance(value, dict):
            for key in sorted(value, key=repr): visit(value[key], path + '[' + repr(key) + ']')
        elif isinstance(value, (tuple, list)):
            for i, child in enumerate(value): visit(child, path + '[' + str(i) + ']')
        elif hasattr(value, '__dict__') and not isinstance(value, type):
            for name, child in vars(value).items():
                if name not in ignored: visit(child, path + '.' + name)
    for i, value in enumerate(objects): visit(value, 'object' + str(i))
    return tuple(result)


def codec_backing(codec):
    key=codec
    if key not in _CODEC_BACKING:
        _CODEC_BACKING[key]=[[min([head,*tape.keys()]),max([head,*tape.keys()])]
                            for head,tape in zip(codec.machine.heads,codec.machine.tapes)]
    bounds=_CODEC_BACKING[key]
    for bound,head in zip(bounds,codec.machine.heads):
        bound[0]=min(bound[0],head);bound[1]=max(bound[1],head)
    return [list(bound) for bound in bounds]


def snapshot(engine):
    from words import BLANK
    banks = []
    for name, bank in arenas(engine):
        banks.append(dict(name=name, capacity=bank.capacity, available=list(bank.available),
            live=sorted(bank.live), initialized=bank.initialized,
            template=dict(head=bank.template.head, body=list(bank.template.cells), backing=len(bank.template.cells)),
            slots=[dict(slot=w.slot, head=w.head, nonblank=sum(x != BLANK for x in w.cells),
                        backing=len(w.cells)) for w in bank.words]))
    codec = engine.runtime.numerical
    return dict(arenas=banks, closed=engine.closed, runtime_closed=engine.runtime.closed,
        outer_scope_active=engine.scope.manager is not None,
        outer_live=sorted(engine.pool.live), inner_live=sorted(engine.runtime.pool.live),
        output=dict(head=engine.output.head, body=list(engine.output.cells), backing=len(engine.output.cells)),
        codec=dict(backing_bounds=codec_backing(codec), state=codec.machine.state, heads=list(codec.machine.heads), tapes=[sorted(t.items()) for t in codec.machine.tapes]),
        roles=[dict(path=path, head=tape.head, nonblank=sum(x != BLANK for x in tape.cells),
                    backing=len(tape.cells)) for path,tape in tapes(engine)],
        contract='Read-only fixture observation; escaped Python references are excluded by caller ownership, not discovered.')


def fixed_tapes(engine, *borrowed):
    """Literal constructor inventory, independently cross-checked with graph walk."""
    from records import Tape
    result=[word.tape for _,bank in arenas(engine) for word in (*bank.words,bank.template)]
    result.extend((*engine.pool.tapes,*engine.runtime.pool.tapes,
                   *engine.runtime.roles.values(),*engine.runtime.handoff.values(),
                   engine.output,engine.runtime.output))
    result.extend(value if isinstance(value,Tape) else value.tape for value in borrowed)
    unique={id(t):t for t in result}
    discovered={id(t):t for _,t in tapes(engine,*borrowed)}
    need(set(unique)==set(discovered),'literal six-arena/controller/borrowed inventory equals graph oracle')
    return tuple(unique.values())


def allocation_control():
    from records import Tape
    from session import sealed_constructors
    try:
        with sealed_constructors():Tape()
    except ValueError:
        return {'status':'PASS_DYNAMIC_TAPE_REJECTION','source_sealed_constructor':True}
    raise ValueError('dynamic Tape accepted inside inherited sealed execution')


class Meter:
    """Count source Tape meters and both dictionary-codec counter banks exactly once."""
    def __init__(self, engine, *borrowed):
        self.roles = fixed_tapes(engine, *borrowed)
        codec=engine.runtime.numerical
        self.banks=(codec.codec_counts, codec.machine.counts)
        self.start=self.total()
    def total(self):
        return tuple(sum(getattr(t.meter,name) for t in self.roles) +
                     sum(bank[name] for bank in self.banks)
                     for name in ('reads','writes','moves'))
    def delta(self):return tuple(x-y for x,y in zip(self.total(),self.start))


def body(tape):
    from words import BLANK
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def digest(tape):return sha256(body(tape)).hexdigest()

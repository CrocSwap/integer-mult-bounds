"""Source-bound streaming sink: retain residual identities and original PCs."""
from bisect import bisect_right
from dataclasses import dataclass, fields, is_dataclass
from hashlib import sha256
from operator import index
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def frozen(value):
    """Typed structural snapshot; mutable nested fields are inadmissible."""
    if type(value) in (int, bool, str, type(None)):
        return type(value).__name__, value
    if type(value) is tuple:
        return ('tuple', tuple(frozen(x) for x in value))
    if is_dataclass(value) and value.__dataclass_params__.frozen:
        return (type(value).__module__, type(value).__qualname__,
                tuple((f.name, frozen(getattr(value, f.name))) for f in fields(value)))
    raise ValueError('mutable plan field')


@dataclass(frozen=True)
class PlanIndex:
    plan: object
    snapshot: tuple
    ends: tuple
    count: int

    @classmethod
    def build(cls, plan):
        snapshot = frozen(plan)
        ends = []
        if not plan.good:
            for command in plan.commands:
                need(command.kind in ('add', 'sign', 'child'), 'unsupported command')
                ends.append((ends[-1] if ends else 0) + (3 if command.kind == 'child' else 1))
        return cls(plan, snapshot, tuple(ends), 3 if plan.good else (ends[-1] if ends else 0))

    def validate(self):
        need(frozen(self.plan) == self.snapshot, 'plan mutation')

    def at(self, offset):
        need(0 <= offset < self.count, 'block offset')
        if self.plan.good:
            return ('forward', 'good', 'backward')[offset], offset, 0
        position = bisect_right(self.ends, offset)
        start = self.ends[position - 1] if position else 0
        command = self.plan.commands[position]
        return ('pair', position, offset - start) if command.kind == 'child' else ('sweep', position, 0)


@dataclass(frozen=True)
class BlockRun:
    definition: object
    plan: PlanIndex
    axis: object

    @property
    def count(self):
        return 1 if self.axis is not None else self.plan.count

    def at(self, offset, validate=True):
        if validate:
            need(self.definition.plan is self.plan.plan and frozen(self.definition.axis) == frozen(self.axis),
                 'definition mutation')
            self.plan.validate()
        block = ('axis', self.axis, 0) if self.axis is not None else self.plan.at(offset)
        return 'block', self.definition, block


@dataclass(frozen=True)
class Word:
    entries: tuple
    ends: tuple

    def __len__(self):
        return self.ends[-1] if self.ends else 0

    def __getitem__(self, key):
        # Tuple-compatible integer indexing. Slices deliberately materialize.
        if isinstance(key, slice):
            return tuple(self[i] for i in range(*key.indices(len(self))))
        offset = index(key)
        if offset < 0:
            offset += len(self)
        if not 0 <= offset < len(self):
            raise IndexError('instruction index out of range')
        region = bisect_right(self.ends, offset)
        entry = self.entries[region]
        if isinstance(entry, BlockRun):
            start = self.ends[region - 1] if region else 0
            return entry.at(offset - start)
        return entry

    def census(self):
        runs = [e for e in self.entries if isinstance(e, BlockRun)]
        return dict(instructions=len(self), retained_records=len(self.entries),
                    block_instructions=sum(r.count for r in runs), block_runs=len(runs),
                    plan_indexes=len({id(r.plan) for r in runs}),
                    plan_prefix_entries=sum(len(p.ends) for p in {id(r.plan): r.plan for r in runs}.values()))


class Sink:
    """Validate each source append before discarding only its block tuple."""
    def __init__(self, initial, observer=None):
        self.entries, self.ends, self.plans = [], [], {}
        self.active = None
        self.observer = observer
        for operation in initial:
            self.append(operation)

    def retain(self, entry, count=1):
        self.entries.append(entry)
        self.ends.append((self.ends[-1] if self.ends else 0) + count)
        need(self.ends[-1] <= sys.maxsize, 'finite Python PC bound')

    def append(self, operation):
        if self.observer is not None:
            self.observer(operation)
        kind = operation[0]
        if kind == 'residual_begin':
            need(self.active is None, 'nested residual')
            _, role, definition = operation
            plan = self.plans.get(id(definition.plan))
            if plan is None:
                plan = PlanIndex.build(definition.plan)
                self.plans[id(definition.plan)] = plan
            plan.validate()
            run = BlockRun(definition, plan, definition.axis)
            self.active = role, run, 0
            self.retain(operation)
        elif kind == 'block':
            need(self.active is not None, 'block outside residual')
            role, run, offset = self.active
            need(offset < run.count, 'extra block')
            need(operation[1] is run.definition and operation[2] == run.at(offset, False)[2],
                 'source block mismatch')
            if offset == 0:
                self.retain(run, run.count)
            self.active = role, run, offset + 1
        elif kind == 'residual_end':
            need(self.active is not None, 'end outside residual')
            role, run, offset = self.active
            need(operation[1] == role and operation[2] is run.definition, 'end identity')
            need(offset == run.count, 'missing block')
            run.plan.validate()
            self.active = None
            self.retain(operation)
        else:
            need(self.active is None, 'operation inside residual')
            self.retain(operation)

    def finish(self):
        need(self.active is None, 'unterminated residual')
        return Word(tuple(self.entries), tuple(self.ends))


def compiler(module, source, digest, observer=None):
    """Compile checked bytes in a PRIVATE namespace; never patch source globals."""
    need(sha256(source).hexdigest() == digest, 'emitter source hash')
    text = source.decode()
    old = ('operations = [("node",)]', 'Code(tuple(operations), staged)')
    new = ('operations = _itinerary_sink([("node",)])', 'Code(operations.finish(), staged)')
    for before, after in zip(old, new):
        need(text.count(before) == 1, 'unsupported emitter shape')
        text = text.replace(before, after)
    namespace = dict(module.__dict__)
    # Execute only the compile_node definition. Its authenticated body and all
    # original namespace objects are unchanged except the two sink boundaries.
    import ast
    tree = ast.parse(text)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'compile_node']
    need(len(functions) == 1, 'unsupported emitter function')
    namespace['_itinerary_sink'] = lambda initial: Sink(initial, observer)
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<authenticated-compact-emitter>', 'exec'), namespace)
    return namespace['compile_node']

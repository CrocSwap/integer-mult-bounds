"""Complete-field ownership for the literal direct-circulant convolution.

Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
Logical storage/access realization, not a CPython heap bound or accelerated
native implementation. Reference death is only a diagnostic of the proved
explicit last-use schedule; the physical construction uses explicit erasure.
"""
import ast
from fractions import Fraction
from hashlib import sha1, sha256
import json
from math import prod
from pathlib import Path
from types import SimpleNamespace, MethodType


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sources(root):
    manifest = json.loads((root/'SOURCES.json').read_text())
    answer = {}
    for row in manifest['sources']:
        data = (root/row['retained']).read_bytes()
        require(sha256(data).hexdigest() == row['sha256'], 'source SHA256 mismatch')
        require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],
                'source Git blob mismatch')
        answer[Path(row['retained']).name] = data
    return answer


class Field:
    def __init__(self, pool, slot, generation, serial):
        self.pool, self.slot, self.generation, self.serial = pool, slot, generation, serial
        self.used = 0

    def valid(self):
        require(self.pool.generations[self.slot] == self.generation and self.slot in self.pool.live,
                'stale field owner')

    def __len__(self):
        self.valid()
        return self.used

    def __iter__(self):
        for i in range(self.used):
            yield self[i]

    def __getitem__(self, i):
        self.valid()
        require(0 <= i < self.used, 'field read extent')
        return self.pool.storage[self.slot][i]

    def __setitem__(self, i, value):
        self.valid()
        require(0 <= i < self.used, 'field write extent')
        require(type(value) is tuple and len(value) == 2, 'complex field record')
        self.pool.storage[self.slot][i] = value

    def __del__(self):
        # Diagnostic only: emitted physical retirement is justified in PROOF.md.
        if (hasattr(self, 'pool') and self.slot in self.pool.live
                and self.pool.generations[self.slot] == self.generation):
            self.pool.retire(self.slot, self.generation)


class FieldPool:
    def __init__(self, length, capacity=7):
        self.length, self.capacity = length, capacity
        self.storage, self.generations = [None]*capacity, [0]*capacity
        self.live, self.events = {}, []
        self.created = self.peak = self.visited_slots = self.cleared_records = 0

    def make(self, values, origin):
        free = [i for i in range(self.capacity) if i not in self.live]
        require(bool(free), 'complete-field capacity exceeded')
        slot = free[0]
        if self.storage[slot] is None:
            self.storage[slot] = [(0, 0)]*self.length
            self.visited_slots += 1
        serial = self.created
        self.created += 1
        self.live[slot] = (serial, origin)
        owner = Field(self, slot, self.generations[slot], serial)
        self.peak = max(self.peak, len(self.live))
        self.events.append(('acquire', serial, slot, origin, len(self.live)))
        try:
            for value in values:
                require(owner.used < self.length, 'oversized complete field')
                require(type(value) is tuple and len(value) == 2, 'complex record required')
                self.storage[slot][owner.used] = value
                owner.used += 1
            require(owner.used == self.length, 'incomplete complete field')
            return owner
        except BaseException:
            self.retire(slot, owner.generation)
            raise

    def retire(self, slot, generation):
        require(slot in self.live and self.generations[slot] == generation, 'invalid field retirement')
        serial, origin = self.live.pop(slot)
        for i in range(self.length):
            self.storage[slot][i] = (0, 0)
        self.cleared_records += self.length
        self.generations[slot] += 1
        self.events.append(('retire', serial, slot, origin, len(self.live)))


class WindowLease:
    def __init__(self, window, generation):
        self.window, self.generation = window, generation

    def valid(self):
        require(self.window.active and self.window.generation == self.generation,
                'expired native window lease')

    def __len__(self):
        self.valid()
        return self.window.length

    def __getitem__(self, i):
        self.valid()
        require(0 <= i < self.window.length, 'native window read extent')
        return self.window.records[i]

    def __setitem__(self, i, value):
        self.valid()
        require(0 <= i < self.window.length, 'native window write extent')
        require(type(value) is tuple and len(value) == 2, 'native complex record')
        self.window.records[i] = value


class NativeWindow:
    """One serial conversion window, with private callback storage separate.

    Callback writes the complete normalized endpoint into its borrowed window
    and returns None. Other owners must be restored; private owners must not
    escape. The lease guard does not prove arbitrary callback code satisfies
    that retained ownership/storage contract.
    """
    def __init__(self, length, P, E, hmax, callback, pool):
        self.length, self.P, self.E, self.hmax = length, P, E, hmax
        self.callback, self.pool = callback, pool
        self.width = P+E+3*hmax+31
        self.records, self.active, self.generation = None, False, 0
        self.calls = self.scanned_records = self.phase = 0
        self.cuts = []

    def apply(self, data, strides):
        require(not self.active, 'overlapping native conversion windows')
        require(len(data) == self.length, 'incomplete native field')
        require(strides and len(set(strides)) == len(strides), 'selected stride set')
        require(all(s > 0 and not s & (s-1) and 2*s <= self.length for s in strides), 'actual address bit')
        h = len(strides)
        require(h <= self.hmax, 'window format cap')
        if self.records is None:
            self.records = [(0, 0)]*self.length
        require(all(x == (0, 0) for x in self.records), 'dirty conversion-window entry')
        self.active = True
        lease = WindowLease(self, self.generation)
        self.cuts.append((self.phase, len(self.pool.live), tuple(sorted(v[0] for v in self.pool.live.values())), h))
        try:
            for i, (a, b) in enumerate(data):
                lease[i] = (a << h, b << h)
            self.scanned_records += self.length
            request = dict(P=self.P, E=self.E, h=h, Q=self.P+self.E+1+h,
                           T=self.length, strides=tuple(strides), width=self.width)
            require(self.callback(lease, request) is None, 'native returned an unowned output')
            for i in range(self.length):
                data[i] = lease[i]
            self.scanned_records += self.length
            self.calls += 1
        finally:
            self.active = False
            self.generation += 1
            for i in range(self.length):
                self.records[i] = (0, 0)
            self.scanned_records += self.length


class FieldConstruction(ast.NodeTransformer):
    def __init__(self, scope, alias_copy=False):
        self.scope, self.alias_copy = scope, alias_copy

    def visit_ListComp(self, node):
        generator = ast.GeneratorExp(elt=node.elt, generators=node.generators)
        return ast.copy_location(ast.Call(func=ast.Name(id='_field', ctx=ast.Load()),
                   args=[generator, ast.Constant(f'{self.scope}:{node.lineno}')], keywords=[]), node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'list':
            if self.alias_copy and self.scope == 'apply':
                return ast.copy_location(node.args[0], node)
            return ast.copy_location(ast.Call(func=ast.Name(id='_field', ctx=ast.Load()),
                     args=[*node.args, ast.Constant(f'{self.scope}:{node.lineno}')], keywords=[]), node)
        return self.generic_visit(node)


def extract(raw, name, namespace, owner=None, tracked=False, alias_copy=False):
    body = ast.parse(raw).body
    if owner:
        body = next(x for x in body if isinstance(x, ast.ClassDef) and x.name == owner).body
    definition = next(x for x in body if isinstance(x, (ast.FunctionDef, ast.ClassDef)) and x.name == name)
    if tracked:
        definition = FieldConstruction(name, alias_copy).visit(definition)
    unit = ast.fix_missing_locations(ast.Module(body=[definition], type_ignores=[]))
    exec(compile(unit, '<authenticated-source:'+name+'>', 'exec'), namespace)
    return namespace[name]


def literal_caller(raw, sides, P, public_bits, jobs, pool=None, native=None, alias_copy=False):
    namespace = dict(Fraction=Fraction, prod=prod, word_product=lambda a,b: a*b)
    if pool is not None:
        namespace['_field'] = pool.make
    grid_type = extract(raw['tensor_word.py'], 'Grid', namespace)
    grid = grid_type(P)
    extract(raw['tensor_word.py'], 'product_diagonal', namespace)
    raw_h = extract(raw['tensor_word.py'], 'hadamard', namespace)
    if native is not None:
        namespace['hadamard'] = native.apply
    apply = extract(raw['tensor_word.py'], 'apply', namespace, 'TensorWord', pool is not None, alias_copy)
    one = (1 << P, 0)
    transform = SimpleNamespace(grid=grid, sides=tuple(sides), jobs=jobs,
                               entrance=[tuple([one]*s) for s in sides],
                               exit=[tuple([one]*s) for s in sides])
    phase = 0
    def invoke(values, opposite=False):
        nonlocal phase
        phase += 1
        if native is not None:
            native.phase = phase
        return apply(transform, values, opposite)
    transform.apply = invoke
    machine = SimpleNamespace(grid=grid, public_bits=public_bits, transform=transform)
    for name in ('public', 'public_product', 'convolution_grid'):
        fn = extract(raw['product.py'], name, namespace, 'Multiplier',
                     tracked=pool is not None and name == 'convolution_grid')
        setattr(machine, name, MethodType(fn, machine))
    return machine, raw_h


def source_jobs(raw, sides, P, public_bits):
    packs = extract(raw['tensor_word.py'], 'axis_packs', {})
    one, half = (1 << P, 0), (1 << (P-1), 0)
    strides = [prod(sides[:i]) for i in range(len(sides))]
    jobs, hmax = [], 0
    for pack in packs(sides, public_bits):
        schedule = []
        for bit in sorted({0, sides[pack[0]].bit_length()-2}):
            tables = [tuple([half if i in pack else one]*side) for i, side in enumerate(sides)]
            target = tuple(strides[i] << bit for i in pack)
            schedule.append((tables, target))
            hmax = max(hmax, len(target))
        jobs.append(schedule)
    return jobs, hmax

"""Metered physical tape fixtures, separate from the compiled runtime.

Only fixture construction and post-execution oracles decode integers or inspect
storage. The runtime is the unchanged source execute_table on local tape ports.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import importlib.util
import sys
from source_binding import check_dependencies


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parent
check_dependencies()
A = load_module('scalar_retained_lifecycle',ROOT/'vendor/lifecycle/machine.py')
IR = load_module('scalar_retained_source_ir',ROOT/'vendor/lifecycle/source_ir.py')


class Tape:
    """A physical one-sided current segment; addresses are observer data only."""
    def __init__(self, symbols=(), origin=17, readonly=False, marker=A.LEFT):
        self.origin = origin
        self.pos = origin
        self.marker = marker
        self.cells = {origin-1:marker, origin-2:91}
        self.cells.update({origin+i:s for i,s in enumerate(symbols)})
        self.readonly = readonly
        self.actions = self.reads = self.writes = self.moves = 0
        self.highwater = origin+len(symbols)
        self.floor = origin

    def tick(self):
        if self.pos < self.origin-1:
            raise ValueError('accessed ancestor beyond local marker')
        self.highwater = max(self.highwater,self.pos)
        self.floor = min(self.floor,self.pos)
        self.actions += 1

    def read(self):
        self.tick(); self.reads += 1
        return self.cells.get(self.pos,A.BLANK)

    def write(self, value):
        self.tick(); self.writes += 1
        if self.readonly:
            raise ValueError('write to borrowed read-only source')
        if self.pos < self.origin:
            raise ValueError('overwrite protected origin')
        if value not in range(7):
            raise ValueError('physical alphabet')
        self.cells[self.pos] = value

    def move(self, delta):
        if delta not in (-1,1):
            raise ValueError('nonunit physical move')
        self.tick(); self.moves += 1
        self.pos += delta
        if self.pos < self.origin-1:
            raise ValueError('crossed ancestor boundary')
        self.highwater = max(self.highwater,self.pos)

    def body(self):
        end = self.origin
        while self.cells.get(end,A.BLANK) != A.BLANK:
            end += 1
        return tuple(self.cells.get(i,A.BLANK) for i in range(self.origin,end))

    def blank(self):
        return all(s == A.BLANK for i,s in self.cells.items() if i >= self.origin)

    def sentinel_ok(self):
        return self.cells[self.origin-1] == self.marker and self.cells[self.origin-2] == 91


def encode_symbols(symbols):
    return tuple((s>>k)&1 for s in symbols for k in (2,1,0))


def symbols_for(values, width):
    if width < 1:
        raise ValueError('positive fixture width')
    out = []
    for value in values:
        if not -(1<<(width-1)) <= value < (1<<(width-1)):
            raise ValueError('fixture value outside signed width')
        out.extend((value>>j)&1 for j in range(width))
        out.append(2)
    return tuple(out)


def decode_body(body, width):
    if len(body)%3:
        raise ValueError('partial physical codeword')
    syms = [4*body[i]+2*body[i+1]+body[i+2] for i in range(0,len(body),3)]
    block = width+1
    if len(syms)%block:
        raise ValueError('partial fixture component')
    values = []
    for i in range(0,len(syms),block):
        bits = syms[i:i+width]
        if any(x not in (0,1) for x in bits) or syms[i+width] != 2:
            raise ValueError('corrupt numeric component')
        value = sum(x<<j for j,x in enumerate(bits))-(bits[-1]<<width)
        values.append(value)
    return tuple(values)


def execute(table, op, target, source, width, work=None):
    """Use exactly the inherited primitive entry/table/exit sequence."""
    public = [Tape(encode_symbols(symbols_for(target,width)),origin=17)]
    if op == 'ADD':
        public.append(Tape(encode_symbols(symbols_for(source,width)),origin=29,readonly=True))
    if work is None:
        work = [Tape(origin=41),Tape(origin=53)]
    before = [t.body() for t in public]
    start_actions = sum(t.actions for t in public+work)
    error = None
    try:
        for t in work:
            A.retire(t)
        A.execute_table(table,tuple(public+work))
        for t in work:
            A.retire(t)
    except ValueError as exc:
        error = str(exc)
    actions = sum(t.actions for t in public+work)-start_actions
    return dict(error=error,public=public,work=work,before=before,actions=actions,
                output=None if error else decode_body(public[0].body(),width))

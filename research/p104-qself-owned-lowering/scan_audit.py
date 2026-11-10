"""Physical scan-cost receipts for the unchanged lifecycle functions only.

No Gaussian or fullcaller execution is represented by this fixture.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('qself_retained_machine', ROOT/'vendor/machine.py')
A = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = A
spec.loader.exec_module(A)


def require(ok, why):
    if not ok:
        raise ValueError(why)


class Tape:
    """Observer only; the original routines use read/write/unit move."""
    def __init__(self, body=(), origin=31):
        self.origin = origin
        self.pos = origin
        self.cells = {origin-1: A.LEFT, origin-2: 91}
        self.cells.update({origin+j: b for j, b in enumerate(body)})
        self.actions = 0
        self.highwater = origin+len(body)

    def tick(self):
        require(self.pos >= self.origin-1, 'no ancestor access')
        self.actions += 1
        self.highwater = max(self.highwater, self.pos)

    def read(self):
        self.tick()
        return self.cells.get(self.pos, A.BLANK)

    def write(self, symbol):
        self.tick()
        require(self.pos >= self.origin, 'origin marker is protected')
        self.cells[self.pos] = symbol

    def move(self, direction):
        require(direction in (-1, 1), 'unit head step')
        self.tick(); self.pos += direction
        require(self.pos >= self.origin-1, 'no ancestor crossing')
        self.highwater = max(self.highwater, self.pos)

    def body(self):
        stop = self.origin
        while self.cells.get(stop, A.BLANK) != A.BLANK:
            stop += 1
        return tuple(self.cells[k] for k in range(self.origin, stop))

    def check_origin(self):
        require(self.pos == self.origin and self.cells[self.origin-1] == A.LEFT and self.cells[self.origin-2] == 91,
                'complete local head and ancestor restoration')


def encode(values, widths):
    raw = []
    for x, width in zip(values, widths):
        require(-(1 << (width-1)) <= x < (1 << (width-1)), 'signed fixture domain')
        for symbol in tuple((x >> j) & 1 for j in range(width)) + (A.COMPONENT,):
            raw += [(symbol >> k) & 1 for k in (2, 1, 0)]
    return tuple(raw)


def verify():
    cases = 0
    actions = 0
    for widths in ((1, 1), (1, 2), (2, 3), (5, 5), (8, 16), (65, 129), (129, 1, 3, 8)):
        for pattern in range(3):
            values = tuple((-(1 << (w-1)) if pattern == 0 else
                            (1 << (w-1))-1 if pattern == 1 else 0) for w in widths)
            body = encode(values, widths); V = len(body); L = V//3; bits = sum(widths)
            for dirty in (0, 1, 17, V+11):
                source = Tape(body, 31); target = Tape((1,)*dirty, 97)
                A.initialize(target, source)
                require(source.actions+target.actions == 5*dirty+25*V//3+17, 'exact INIT cost including dirty erasure and heads')
                require(target.body() == encode((0,)*len(widths), widths) and source.body() == body, 'actual cleared complete shape')
                source.check_origin(); target.check_origin()
                before = source.actions+target.actions
                A.copy_as_add(target, source)
                require(source.actions+target.actions-before == 14*L+9*bits+4*V+14, 'exact COPY numerical/source-access/head cost')
                require(target.body() == source.body() == body, 'arbitrary signed copied contents')
                source.check_origin(); target.check_origin()
                before = target.actions; old_backing = target.highwater
                A.retire(target)
                require(target.actions-before == 5*V+7 and target.body() == (), 'exact physical erasure cost')
                require(all(v == A.BLANK for k, v in target.cells.items() if k >= target.origin), 'no raw coded bits survive')
                require(target.highwater >= old_backing, 'erasure retains historical backing')
                source.check_origin(); target.check_origin()
                actions += source.actions+target.actions; cases += 1
    # COPY is actual addition: an uncleared numerical residue is preserved.
    source = Tape(encode((2, 0), (3, 3))); target = Tape(encode((1, 0), (3, 3)), 97)
    A.copy_as_add(target, source)
    require(target.body() == encode((3, 0), (3, 3)) and target.body() != source.body(), 'uncleared-copy negative control exposes residual')
    return {'physical_scan_cases': cases, 'physical_cell_actions': actions,
            'checked_functions': ['initialize', 'copy_as_add', 'retire'],
            'normal_head_and_raw_erasure_controls': True, 'dirty_copy_control': True,
            'Gaussian_or_fullcaller_execution': False}

"""Weak identity census of every retained source array, not Python heap size."""
from contextlib import contextmanager
import sys
import weakref
from binding import need


class Census:
    def __init__(self, arenas):
        self.arenas = arenas
        self.tapes = weakref.WeakValueDictionary()
        self.categories = {}
        self.active = False
        self.phase = 'entry'
        self.peak = self.record_peak = self.samples = 0
        self.phases = {}
        self.quota = None
        self.baseline = {}
        self.capture = None

    def register(self, tape, caller):
        self.tapes[id(tape)] = tape
        if not self.active:
            category = 'entry'
        else:
            module = caller.f_globals.get('__name__','')
            function = caller.f_code.co_name
            owner = type(caller.f_locals.get('self')).__name__
            if module == 'records' and owner in ('Stack','Fields','Program'):
                category = {'Stack':'continuation','Fields':'empty_fields','Program':'extended_program'}[owner]
            elif module in ('stream','cardinality','counts','cardinal_counts') and function != 'add_pass':
                category = 'count'
            elif module == 'stream' and function == 'add_pass':
                category = 'payload'
            else:
                raise RuntimeError(f'unclassified source array: {module}.{function}/{owner}')
        self.categories[id(tape)] = category
        self.observe()

    def observe(self):
        if not self.active:
            return
        rows = list(self.tapes.items())
        for identity, (length, snapshot) in self.baseline.items():
            need(identity in self.tapes and len(self.tapes[identity].cells) == length,
                 'entry array identity and length preserved')
        numerical = sum((len(a.words)+1)*(a.bits+2) for a in self.arenas)
        categories = {}
        for identity,tape in rows:
            cat = self.categories[identity]
            categories[cat] = categories.get(cat,0)+len(tape.cells)
        total = numerical+sum(categories.values())
        records = sum(categories.get(x,0) for x in ('continuation','empty_fields','extended_program'))
        self.record_peak = max(self.record_peak,records)
        self.peak = max(self.peak,total)
        self.phases[self.phase] = max(self.phases.get(self.phase,0),total)
        self.samples += 1
        need(self.quota is None or total <= self.quota,'complete backing quota')

    def start(self):
        self.baseline = {i:(len(t.cells),bytes(t.cells)) for i,t in self.tapes.items()}
        self.baseline_cells = sum(x[0] for x in self.baseline.values()) + sum(
            (len(a.words)+1)*(a.bits+2) for a in self.arenas)
        self.active = True
        self.observe()


@contextmanager
def observed(m, arenas):
    census = Census(arenas)
    init,write,zero = m.records.Tape.__init__,m.records.Tape.write,m.words.Arena.zero
    def tape_init(tape):
        init(tape)
        census.register(tape,sys._getframe(1))
    def tape_write(tape,symbol):
        write(tape,symbol)
        census.observe()
    def arena_zero(arena):
        length = len(arena.words)
        result = zero(arena)
        if len(arena.words) != length:
            census.observe()
        return result
    try:
        m.records.Tape.__init__,m.records.Tape.write,m.words.Arena.zero = tape_init,tape_write,arena_zero
        yield census
    finally:
        m.records.Tape.__init__,m.records.Tape.write,m.words.Arena.zero = init,write,zero

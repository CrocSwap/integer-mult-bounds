"""Literal child-coefficient lifetime audit. Standard library; read-only replay."""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
HEAD = 'a53fdf4bcbe33c6732f0bec1badc8c023380f9d1'
MODULES = ('words', 'records', 'matrices', 'controller', 'forms', 'children', 'numeric')
RESIDUES, INDICES = 20494, 22


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def check_result(actual, path):
    expected = json.loads(path.read_text(encoding='utf-8'))
    require(canonical(actual) == canonical(expected), 'fixed typed receipt')


def sources(package=PACKAGE):
    manifest = json.loads((package / 'SNAPSHOT.json').read_text(encoding='utf-8'))
    require(manifest['head'] == HEAD and manifest['repository'] == 'CrocSwap/integer-mult-bounds',
            'scientific source identity')
    wanted = {'vendor/' + name + '.py' for name in MODULES} | {
        'vendor/NOTICE.md', 'references/PR2770.md', 'references/PR2781.md'}
    require(len(manifest['files']) == len(wanted), 'closed snapshot inventory')
    exports = {}
    for entry in manifest['files']:
        name = entry['path']
        require(name in wanted and name not in exports, 'unique canonical snapshot path')
        target = package / name
        require(not target.is_symlink() and target.is_file(), 'regular scientific source')
        raw = target.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'source SHA256')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == entry['git_blob'], 'source Git blob')
        if name.startswith('vendor/'):
            leaf = name.split('/')[1]
            original = 'research/selected-bit-node/' + ('' if leaf == 'NOTICE.md' else 'vendor/') + leaf
            require(entry['source_path'] == original, 'original runtime path')
        exports[name] = raw
    return exports


def load_sources():
    exports = sources()
    require(not any(name in sys.modules for name in MODULES), 'no preloaded scientific modules')
    for name in MODULES:
        module = ModuleType(name)
        module.__file__ = str(PACKAGE / 'vendor' / (name + '.py'))
        sys.modules[name] = module
        # Authenticate every input first; execute these exact bytes, not a .pyc.
        exec(compile(exports['vendor/' + name + '.py'], module.__file__, 'exec', dont_inherit=True),
             module.__dict__)
    return SimpleNamespace(**{name: sys.modules[name] for name in MODULES})


def matrices(modulus, q, good, rank, high_digit=0):
    """Explicit invertible two-coordinate block; independent integer projector."""
    low = [[int(i == j) for j in range(64)] for i in range(64)]
    low[0][rank] = 1
    low[rank][0], low[rank][rank] = (1, 2) if good else (2, 1)
    high = [[0] * 64 for _ in range(64)]
    high[0][0] = high_digit
    a, b, c, d = 1 + q * high_digit, 1, low[rank][0], low[rank][rank]
    inv_det = pow(a * d - b * c, -1, modulus)
    p = [[int(i == j and i < rank) for j in range(64)] for i in range(64)]
    p[0][0], p[0][rank] = a * d * inv_det % modulus, -a * b * inv_det % modulus
    p[rank][0], p[rank][rank] = c * d * inv_det % modulus, -c * b * inv_det % modulus
    return low, high, p


def pair_data(projector, modulus):
    """Independent modular row elimination, using integer residues, no Word code."""
    n = 128
    a = [[0] * n for _ in range(n)]
    for i in range(64):
        for j in range(64):
            p = projector[i][j]
            a[i][j] = a[127-i][127-j] = (int(i == j) - p) % modulus
            a[i][127-j] = a[127-i][j] = p
    permutation = list(range(n))
    for j in range(n):
        pivot = next(i for i in range(j, n) if gcd(a[i][j], modulus) == 1)
        a[j], a[pivot] = a[pivot], a[j]
        permutation[j], permutation[pivot] = permutation[pivot], permutation[j]
        inv = pow(a[j][j], -1, modulus)
        for i in range(n):
            if i != j and a[i][j]:
                multiple = a[i][j] * inv % modulus
                a[i] = [(x - multiple*y) % modulus for x, y in zip(a[i], a[j], strict=True)]
    require(all(a[i][j] == 0 for i in range(n) for j in range(n) if i != j),
            'independent residual diagonal')
    return [a[i][i] for i in range(n)], permutation


def fixture(m, good=False, rank=1, modulus=3, history='', kind='pair', field=0,
            half=False, coordinate=0, negative=False, high_digit=0, borrowed=3):
    require(modulus in (3, 9, 25) and 0 <= len(history) <= 3, 'bounded fixture')
    q = 5 if modulus == 25 else 3
    require(all(letter in 'GPU' for letter in history), 'bounded history alphabet')
    root = 256 * 64**len(history)
    r = m.words.Arena(modulus.bit_length()+1, 65536)
    ix = m.words.Arena(root.bit_length()+1, 128)
    modulus_word = r.literal(modulus)
    ring = m.words.Ring(modulus_word)
    ident = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    low, high, p = matrices(modulus, q, good, rank, high_digit)
    specs = {0: SimpleNamespace(code=0, good=good, low=low,
                               template=SimpleNamespace(q=q, rank=rank, preparation=ident))}
    events, field_records, oracle_steps = [], [], []
    for letter in history:
        ancestor_good = letter == 'G'
        lo, hi, pp = matrices(modulus, q, ancestor_good, 1)
        code = 1 if ancestor_good else 2
        specs[code] = SimpleNamespace(code=code, good=ancestor_good, low=lo,
                                     template=SimpleNamespace(q=q, rank=1, preparation=ident))
        tag = {'G': 0, 'P': 1, 'U': 2}[letter]
        events.append((tag, code, 1, 0, 0, 0))
        field_records.append((code, hi))
        oracle_steps.append((letter, pp))
    program = m.records.Program.fixture(ix, r, root, 2, events)
    field_records.append((0, high))
    fields = m.records.Fields.fixture(ix, r, field_records)
    f = 4
    out_size = rank*f if kind == 'good' else f//2 if half else f
    require(0 <= coordinate < out_size, 'fixture child coordinate')
    coord = ix.literal(coordinate)
    request = SimpleNamespace(kind='child', child_kind=kind, field=field,
                              reverse=kind == 'pair' and field >= 64, half=half,
                              coordinate=coord, negative_inverse=negative)
    plan = SimpleNamespace(dimension=64, rank=rank, good=good)
    for i in range(borrowed):
        r.literal(i % modulus)
        ix.literal(i+2)

    def incoming(level, position):
        if not level:
            return 2
        letter, pp = oracle_steps[level-1]
        if letter == 'U':
            return 1
        if letter == 'G':
            return incoming(level-1, position) * pp[0][0] % modulus
        diagonal, permutation = pair_data(pp, modulus)
        parent_f = 256 * 64**(len(history)-level)
        numerator = incoming(level-1, permutation[0]*parent_f+position) if permutation[0] < 64 else 1
        denominator = incoming(level-1, position)
        return diagonal[0]*numerator*pow(denominator, -1, modulus) % modulus

    if kind == 'unit':
        expected = 1
    elif kind == 'good':
        k = coordinate // f
        pivot = p[0][0] if k == 0 else 1
        expected = incoming(len(history), coordinate)*pivot % modulus
    else:
        diagonal, permutation = pair_data(p, modulus)
        column = f-1-coordinate if field >= 64 else coordinate
        numerator = incoming(len(history), permutation[field]*f+column) if permutation[field] < 64 else 1
        denominator = incoming(len(history), field*f+column) if field < 64 else 1
        expected = diagonal[field]*numerator*pow(denominator, -1, modulus) % modulus
    if negative:
        expected = -pow(expected, -1, modulus) % modulus
    return SimpleNamespace(**locals())


def state(case):
    return tuple({s: (bytes(a.words[s].cells), a.words[s].head) for s in a.live} for a in (case.r, case.ix))


def preserved(case, saved, inputs):
    require(state(case) == saved, 'entry ownership, numerical bytes and heads')
    require(tuple((bytes(t.cells), t.head) for t in (case.program.tape, case.fields.tape)) == inputs,
            'program/field bytes and heads')
    require(case.r.template.head == case.ix.template.head == 1, 'permanent template heads')


class Observe:
    def __init__(self, m, case, bounds=(RESIDUES, INDICES)):
        self.m, self.case, self.bounds = m, case, bounds
        self.arenas = (case.r, case.ix)
        self.entry = [len(a.live) for a in self.arenas]
        self.peak, self.scans, self.created, self.callbacks = list(self.entry), 0, [], []

    def cells(self):
        for a in self.arenas:
            occupied = sum(c not in (self.m.words.LEFT, self.m.words.BLANK)
                           for w in (*a.words, a.template) for c in w.cells)
            require(occupied == (len(a.live)+1)*(a.bits+1), 'literal occupied numerical cells')
        self.scans += 1

    def __enter__(self):
        require(all(a.template.head == 1 and all(a.words[s].head == 1 for s in a.live)
                    for a in self.arenas), 'restored entry heads')
        self.zero, self.program, self.callback = self.m.words.Arena.zero, self.m.children.Program, self.m.children.Callback
        owner = self

        def allocate(a):
            word = owner.zero(a)
            i = owner.arenas.index(a)
            require(len(a.live) <= owner.entry[i]+owner.bounds[i], 'child numerical budget')
            if len(a.live) > owner.peak[i]:
                owner.peak[i] = len(a.live)
                if len(a.live) == owner.entry[i]+owner.bounds[i] or len(a.live) in (8192, 16384):
                    owner.cells()
            return word

        def program(*args, **kwargs):
            obj = owner.program(*args, **kwargs)
            owner.created.append(obj)
            return obj

        def callback(*args, **kwargs):
            obj = owner.callback(*args, **kwargs)
            owner.callbacks.append(obj)
            return obj

        self.m.words.Arena.zero = allocate
        self.m.children.Program, self.m.children.Callback = program, callback
        self.cells()
        return self

    def __exit__(self, *_):
        self.m.words.Arena.zero = self.zero
        self.m.children.Program, self.m.children.Callback = self.program, self.callback


def execute(m, parameters, bounds=(RESIDUES, INDICES), fail=None, repeats=1):
    c = fixture(m, **parameters)
    saved = state(c)
    inputs = tuple((bytes(t.cells), t.head) for t in (c.program.tape, c.fields.tape))
    try:
        if fail == 'coordinate':
            c.request.coordinate = c.ix.literal(c.out_size)
            saved = state(c)
        elif fail == 'field':
            c.request.field = 127
        elif fail == 'missing_current':
            c.fields.tape.cells = bytearray([m.words.LEFT])
            c.fields.tape.head = 1
            inputs = tuple((bytes(t.cells), t.head) for t in (c.program.tape, c.fields.tape))
        with Observe(m, c, bounds) as observer:
            old_weight = m.controller.Callback.weight
            if fail == 'weight':
                def rejected_weight(callback, position):
                    old_weight(callback, position)
                    raise ValueError('injected completed-weight failure')
                m.controller.Callback.weight = rejected_weight
            try:
                failed = False
                for _ in range(repeats):
                    try:
                        value = m.numeric.selected_coefficient(c.plan, c.ring, c.ix, c.program,
                                    c.fields, c.specs, 0, c.request)
                    except ValueError:
                        if fail is None:
                            raise
                        failed = True
                        break
                    require(value.inspect() == c.expected, 'independent child coefficient')
                    c.r.free(value)
                    preserved(c, saved, inputs)
                require(failed == (fail is not None), 'required source rejection')
                preserved(c, saved, inputs)  # Before external fixture teardown.
                observer.cells()
                for obj in observer.created:
                    require(obj.tape.head == 1 and all(x == m.words.BLANK for x in obj.tape.cells[1:]),
                            'extended program erased by source')
                for callback in observer.callbacks:
                    for stack in (callback.pending, callback.values):
                        for tape in (stack.tape, stack.reverse):
                            require(tape.head == 1 and all(x == m.words.BLANK for x in tape.cells[1:]),
                                    'child continuations erased by source')
            finally:
                m.controller.Callback.weight = old_weight
        return {'parameters': parameters, 'result': c.expected, 'repeats': repeats,
                'entry': observer.entry, 'extra': [p-e for p, e in zip(observer.peak, observer.entry)],
                'cell_scans': observer.scans, 'source_rejected': failed,
                'callbacks': len(observer.callbacks), 'extensions': len(observer.created)}
    finally:
        c.r.rollback(set())
        c.ix.rollback(set())
        c.program.tape.clear()
        c.fields.tape.clear()


def receipt(m):
    parameters = [
        {'kind': 'pair'},
        {'kind': 'good', 'good': True, 'rank': 42, 'coordinate': 167},
        {'kind': 'good', 'good': True, 'rank': 1, 'coordinate': 3, 'modulus': 9, 'high_digit': 1},
        {'kind': 'unit', 'half': True, 'coordinate': 1, 'negative': True},
        {'kind': 'pair', 'field': 126, 'coordinate': 3, 'negative': True, 'modulus': 9, 'high_digit': 1},
        {'kind': 'pair', 'history': 'P', 'field': 64, 'coordinate': 2},
        {'kind': 'good', 'good': True, 'rank': 42, 'history': 'GPU', 'coordinate': 3, 'negative': True},
        {'kind': 'pair', 'history': 'UP', 'field': 1, 'coordinate': 1, 'modulus': 25, 'high_digit': 1, 'borrowed': 7},
    ]
    records = [execute(m, p, repeats=2 if i == 0 else 1) for i, p in enumerate(parameters)]
    require(records[0]['extra'][0] == RESIDUES, 'residue excess attained')
    require(records[1]['extra'][1] == INDICES, 'index excess attained')
    require(all(r['callbacks'] == 2*r['repeats'] and r['extensions'] == r['repeats'] for r in records),
            'two literal callbacks and one extension per call')
    return {'schema_version': 1, 'source_head': HEAD, 'residue_excess': RESIDUES,
            'index_excess': INDICES, 'fixtures': records,
            'scope': 'closed recursive-child coefficient; numerical occupied content above all entry residents'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    actual = receipt(load_sources())
    if args.emit:
        print(json.dumps(actual, indent=2))
    else:
        check_result(actual, PACKAGE / 'RESULT.json')
        print(f'PASS_SELECTED_CHILD_NUMERICAL_LIFECYCLE fixtures={len(actual["fixtures"])} '
              f'residues={RESIDUES} indices={INDICES} no_new_kappa')


if __name__ == '__main__':
    main()

"""Literal exact owned MOVE28141. Apache-2.0; substantial Codex assistance.

The immutable local modules supply phase, CNOT and positive-C instructions.
Only construction-time fixed words and tape/PC labels are joined here.
"""
from pathlib import Path
from hashlib import sha1, sha256
import atexit
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_cache = tempfile.TemporaryDirectory(prefix='rank2-source-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name) / 'required-absent')
if Path(sys.pycache_prefix).exists():
    raise ValueError('source cache prefix must be absent')


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for pin in manifest['files']:
        raw = (HERE / pin['local']).read_bytes()
        if len(raw) != pin['bytes'] or sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('source drift: ' + pin['local'])
        if sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != pin['blob']:
            raise ValueError('source Git blob: ' + pin['local'])
    for pin in manifest['generated']:
        if sha256((HERE / pin['local']).read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('generated binding drift: ' + pin['local'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / 'reference' / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


authenticate()
LINEAR = load('rank2_linear', 'linear/linear.py')
PHASE = load('rank2_phase', 'phase/phase.py')
LEAF = load('rank2_leaf', 'leaf/leaf.py')
Builder = LINEAR.Builder
BLANK, ONE, MARK = LINEAR.BLANK, LINEAR.ONE, LINEAR.MARK
BITS = ('0', ONE)
HEADER, DATA, WORK, TRACE = range(4)
TAPES = 31
RECIPE = json.loads((HERE / 'RECIPE.json').read_text())
SWAP01 = ((0, 1), (1, 0), (0, 1))


def compile_word(word):
    """One fixed nine-slot CNOT word, using the unchanged literal gate body."""
    if not word or any(type(t) is not int or type(c) is not int or
                       not 0 <= t < 9 or not 0 <= c < 9 or t == c for t, c in word):
        raise ValueError('fixed CNOT word')
    h = LINEAR
    a = Builder()
    for tape in h.PRIVATE:
        a.op('move', tape, -1); a.op('write', tape, MARK); a.op('move', tape, 1)
    for tape in (h.F, h.R, h.P, h.S, h.WIDTH):
        h.gamma(a, tape)
    h.trace_return(a, h.HEADER, h.HTRACE)
    h.volume(a); h.clone(a)
    a.op('write', h.MODE, '0')
    for target, control in word:
        h.cnot_columns(a, target, control)
    a.op('read', h.MODE, {'0': 'commitA', ONE: 'commitB'})
    for label, source in (('commitA', h.A), ('commitB', h.B)):
        a.mark(label); h.commit(a, source); a.op('goto', 'retire')
    a.mark('retire')
    for tape in (h.F, h.R, h.P, h.S, h.WIDTH, h.VOLUME):
        h.clear(a, tape)
    h.clear(a, h.MODE, BITS)
    for tape in h.PRIVATE:
        a.op('move', tape, -1); a.op('write', tape, BLANK); a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject'); a.op('read', h.HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))


def compile_guard(*, weak=False):
    """Physically compare 2f to encoded cutoff, retaining original f geometry."""
    h = LEAF
    a = Builder()
    for tape in h.PRIVATE:
        a.op('move', tape, -1); a.op('write', tape, MARK); a.op('move', tape, 1)
    h.gamma(a, h.F, capture=(h.FBIN, h.FLEN))
    if not weak:
        for tape, symbols, bit in ((h.FBIN, BITS, '0'), (h.FLEN, (ONE,), ONE)):
            label = 'append_' + str(tape)
            a.mark(label)
            a.op('read', tape, {s: label + '_step' for s in symbols} | {BLANK: label + '_write'})
            a.mark(label + '_step'); a.op('move', tape, 1); a.op('goto', label)
            a.mark(label + '_write'); a.op('write', tape, bit); a.op('move', tape, 1)
            a.rewind(tape, symbols)
    for tape in (h.R, h.P, h.S, h.WIDTH):
        h.gamma(a, tape)
    h.gamma_binary(a); h.cutoff_guard(a)
    h.trace_return(a, h.HEADER, h.HTRACE)
    for tape in h.PRIVATE:
        a.rewind(tape, BITS)
        h.clear(a, tape, BITS)
    for tape in h.PRIVATE:
        a.op('move', tape, -1); a.op('write', tape, BLANK); a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject'); a.op('read', h.HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))


def return_source(a):
    a.op('move', TRACE, -1)
    label = 'return_' + str(len(a.code))
    a.mark(label)
    a.op('read', TRACE, {ONE: label + '_bit', MARK: label + '_done'})
    a.mark(label + '_bit')
    a.op('write', TRACE, BLANK); a.op('move', TRACE, -1); a.op('move', DATA, -1)
    a.op('goto', label)
    a.mark(label + '_done'); a.op('move', TRACE, 1)


def insert(a, name, code, alphabet, after):
    if alphabet != (BLANK, '0', ONE, MARK):
        raise ValueError('component alphabet')
    def port(t):
        return HEADER if t == 0 else WORK if t == 1 else t + 2
    for pc, (op, *args) in enumerate(code):
        a.mark(name + str(pc))
        if op == 'read':
            a.op(op, port(args[0]), {s: name + str(dst) for s, dst in args[1].items()})
        elif op in ('write', 'move'):
            a.op(op, port(args[0]), args[1])
        elif op == 'goto':
            a.op(op, name + str(args[0]))
        elif op == 'halt':
            a.op('goto', after)
        else:
            raise ValueError('nonliteral component instruction')


def _compile_move(mutation=None):
    right, left = RECIPE['right'], RECIPE['left']
    if RECIPE['source_event'] != ['MOVE', 1526, 601, 470, True] or RECIPE['rank'] != 2:
        raise ValueError('actual owned source binding')
    if right['offset'] or left['offset']:
        raise ValueError('this source needs no affine translation')
    words = {side: tuple(tuple(r[1:]) for r in RECIPE[side + '_records'] if r[0] == 'XROW')
             for side in ('right', 'left')}
    factors = [
        ('rank_guard_', compile_guard(weak=mutation == 'weak_cutoff')),
        ('right_phase_', PHASE.compile_phase(right['linear_Z4'], right['quadratic_rows'],
                                             (right['phase'] + (mutation == 'wrong_phase')) % 4)),
        ('right_G_', compile_word(words['right'])),
        ('first_C_', LEAF.compile_leaf()),
        ('swap_into_', compile_word(SWAP01)),
        ('second_C_', LEAF.compile_leaf()),
        ('swap_back_', compile_word(SWAP01)),
        ('left_phase_', PHASE.compile_phase(left['linear_Z4'], left['quadratic_rows'], left['phase'])),
        ('left_G_', compile_word(words['left'])),
    ]
    if mutation == 'omit_second_C':
        factors = [item for item in factors if item[0] != 'second_C_']
    a = Builder()
    for tape in (WORK, TRACE):
        a.op('move', tape, -1); a.op('write', tape, MARK); a.op('move', tape, 1)
    a.mark('clone')
    a.op('read', DATA, {'0': 'clone0', ONE: 'clone1', BLANK: 'cloned'})
    for bit in BITS:
        a.mark('clone' + bit)
        a.op('write', WORK, bit); a.op('move', WORK, 1); a.op('move', DATA, 1)
        a.op('write', TRACE, ONE); a.op('move', TRACE, 1); a.op('goto', 'clone')
    a.mark('cloned'); return_source(a); a.rewind(WORK, BITS)
    entries = {}
    for index, (name, (code, alphabet)) in enumerate(factors):
        entries[name] = len(a.code)
        after = factors[index + 1][0] + '0' if index + 1 < len(factors) else 'commit'
        insert(a, name, code, alphabet, after)
    a.mark('commit'); entries['commit'] = len(a.code)
    a.op('read', WORK, {'0': 'commit0', ONE: 'commit1', BLANK: 'committed'})
    for bit in BITS:
        a.mark('commit' + bit)
        a.op('write', DATA, bit); a.op('write', WORK, BLANK)
        a.op('move', WORK, 1); a.op('move', DATA, 1)
        a.op('write', TRACE, ONE); a.op('move', TRACE, 1); a.op('goto', 'commit')
    a.mark('committed'); return_source(a); a.rewind(WORK, (BLANK,))
    for tape in (WORK, TRACE):
        a.op('move', tape, -1); a.op('write', tape, BLANK); a.op('move', tape, 1)
    a.op('halt')
    code, alphabet = a.finish((BLANK, '0', ONE, MARK))
    return code, alphabet, entries


def compile_move():
    code, alphabet, _ = _compile_move()
    return code, alphabet

"""One fixed literal direct implementation of selected #7000 MOVE24472.

The source modules are retained byte for byte. Construction-time relabeling
joins their local-symbol graphs; no runtime callback implements a factor.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def authenticate():
    for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        raw = (HERE / pin['local']).read_bytes()
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('source drift: ' + pin['local'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if blob != pin['blob']:
            raise ValueError('Git blob drift: ' + pin['local'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / 'reference' / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


authenticate()
LINEAR = load('move_join_linear', 'linear/linear.py')
PHASE = load('move_join_phase', 'phase/phase.py')
LEAF = load('move_join_leaf', 'leaf/leaf.py')
TRANSLATION = load('move_join_translation', 'translation/translate.py')
Builder, Tape, Machine = LINEAR.Builder, LINEAR.Tape, LINEAR.Machine
BLANK, ONE, MARK = LINEAR.BLANK, LINEAR.ONE, LINEAR.MARK
HEADER, DATA, WORK, TRACE = range(4)
TAPES = 31
BITS = ('0', ONE)


def return_source(a):
    """Erase the paid trace and return the original DATA head."""
    a.op('move', TRACE, -1)
    a.mark('return_' + str(len(a.code)))
    loop = 'return_' + str(len(a.code))
    # mark() does not append code, so loop is the label just installed.
    a.op('read', TRACE, {ONE: loop + '_bit', MARK: loop + '_done'})
    a.mark(loop + '_bit')
    a.op('write', TRACE, BLANK)
    a.op('move', TRACE, -1)
    a.op('move', DATA, -1)
    a.op('goto', loop)
    a.mark(loop + '_done')
    a.op('move', TRACE, 1)


def insert(a, name, code, alphabet, after):
    """Only fixed jump addresses and fixed tape ports are renamed."""
    if alphabet != (BLANK, '0', ONE, MARK):
        raise ValueError('module alphabet')
    ports = lambda t: HEADER if t == 0 else WORK if t == 1 else t + 2
    for pc, (op, *args) in enumerate(code):
        a.mark(name + str(pc))
        if op == 'read':
            a.op(op, ports(args[0]), {s: name + str(dst) for s, dst in args[1].items()})
        elif op in ('write', 'move'):
            a.op(op, ports(args[0]), args[1])
        elif op == 'goto':
            a.op(op, name + str(args[0]))
        elif op == 'halt':
            a.op('goto', after)
        else:
            raise ValueError('nonlocal retained opcode')


def _compile_move(mutation=None):
    recipe = json.loads((HERE / 'reference/RECIPE.json').read_text())['lowered_recipe']
    right = recipe['right']
    left = recipe['left']
    factors = [
        ('right_phase_', PHASE.compile_phase(right['linear_Z4'], right['quadratic_rows'],
                                             0 if mutation == 'drop_absolute_phase' else right['phase'])),
        ('right_linear_', LINEAR.compile_linear('right')),
        ('right_offset_', TRANSLATION.compile_translation()),
        ('positive_child_', LEAF.compile_leaf()),
        ('left_phase_', PHASE.compile_phase(left['linear_Z4'], left['quadratic_rows'], left['phase'])),
        ('left_linear_', LINEAR.compile_linear('left')),
    ]
    if mutation == 'swap_right_order':
        factors[0], factors[1] = factors[1], factors[0]
    if mutation == 'omit_offset':
        factors = [item for item in factors if item[0] != 'right_offset_']
    a = Builder()
    for tape in (WORK, TRACE):
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    a.mark('clone')
    a.op('read', DATA, {'0': 'clone0', ONE: 'clone1', BLANK: 'cloned'})
    for bit in BITS:
        a.mark('clone' + bit)
        a.op('write', WORK, bit)
        a.op('move', WORK, 1)
        a.op('move', DATA, 1)
        a.op('write', TRACE, ONE)
        a.op('move', TRACE, 1)
        a.op('goto', 'clone')
    a.mark('cloned')
    return_source(a)
    a.rewind(WORK, BITS)
    entries = {}
    for index, (name, (code, alphabet)) in enumerate(factors):
        entries[name] = len(a.code)
        after = factors[index + 1][0] + '0' if index + 1 < len(factors) else 'commit'
        insert(a, name, code, alphabet, after)
    a.mark('commit')
    entries['commit'] = len(a.code)
    a.op('read', WORK, {'0': 'commit0', ONE: 'commit1', BLANK: 'committed'})
    for bit in BITS:
        a.mark('commit' + bit)
        a.op('write', DATA, '1' if mutation == 'corrupt_commit' else bit)
        a.op('write', WORK, BLANK)
        a.op('move', WORK, 1)
        a.op('move', DATA, 1)
        a.op('write', TRACE, ONE)
        a.op('move', TRACE, 1)
        a.op('goto', 'commit')
    a.mark('committed')
    return_source(a)
    a.rewind(WORK, (BLANK,))
    for tape in (WORK, TRACE):
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    code, alphabet = a.finish((BLANK, '0', ONE, MARK))
    return code, alphabet, entries


def compile_move():
    """Fixed science table: no runtime size, scalar, child or recipe argument."""
    code, alphabet, _ = _compile_move()
    return code, alphabet

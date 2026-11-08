# SPDX-License-Identifier: Apache-2.0
"""Authenticated retained local machines; all imports use pinned source bytes.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. The retained
decoder, arithmetic, rotation, commit, and interpreter authors keep their credit.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOW = 'research/bit-low-carry-lowering/'
COMMIT = 'research/bit-full-fiber-low-commit/'
ROTATE = 'research/runtime-quarter-carry/'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(row, data):
    require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob: ' + row['path'])


@contextmanager
def aliases(mapping):
    absent = object()
    previous = {name: sys.modules.get(name, absent) for name in mapping}
    sys.modules.update(mapping)
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is absent:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def load():
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    raw = {}
    for row in rows:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        require(not path.is_symlink(), 'source symlink')
        data = path.read_bytes()
        authenticate(row, data)
        raw[row['path']] = data
    modules = {}
    locations = {name: ROTATE + 'inputs/' + name + '.py'
                 for name in ('machine', 'counters', 'shear', 'descriptor', 'independent')}
    locations.update(offset=LOW+'offset.py', low=LOW+'controller.py',
                     rotation=ROTATE+'kernel.py', commit=COMMIT+'controller.py',
                     types=COMMIT+'type_compiler.py',
                     route_generator='research/bit-row-route-generator/generator.py',
                     route_interpreter='research/bit-row-route-generator/interpreter.py')
    for name, path in locations.items():
        module = types.ModuleType('_whole_low_pinned_' + name)
        module.__file__ = str(ROOT / path)
        with aliases({**modules, module.__name__: module}):
            exec(compile(raw[path], str(ROOT / path), 'exec', optimize=0), module.__dict__)
        modules[name] = module
    return modules, raw


def frontend(modules, q, weights, positions, cells, tapes):
    """Generalize #6241's literal PC/tape translation; no runtime callback."""
    with aliases({'offset': modules['offset']}):
        old = modules['low'].compile_frontend(q, weights, positions, cells)
    m = modules['machine']
    symbol = {None: m.BLANK, 0: m.ZERO, 1: m.ONE, 2: m.RIGHT, 3: m.LEFT}
    mapping = (17, 18, 9, 5, 14)
    starts, size = [], 2
    for row in old['code']:
        starts.append(size)
        size += 2 if row[0] in ('move', 'write') else 1
    code = [('move', 14, 1), ('goto', starts[old['start']])]
    for pc, row in enumerate(old['code']):
        require(len(code) == starts[pc], 'retained source-PC embedding')
        op = row[0]
        if op == 'branch':
            code.append(('branch', mapping[row[1]], tuple((symbol[s], starts[t]) for s, t in row[2]), starts[row[3]]))
        elif op == 'move':
            code.extend((('move', mapping[row[1]], row[2]), ('goto', starts[row[3]])))
        elif op == 'write':
            code.extend((('write', mapping[row[1]], symbol[row[2]]), ('goto', starts[row[3]])))
        elif op == 'goto':
            code.append(('goto', starts[row[1]]))
        elif op == 'halt':
            code.append(('halt',))
        elif op == 'reject':
            code.append(('reject', 'retained source carry frontend'))
        else:
            raise ValueError('unknown retained local instruction')
    return m.Program(tuple(code), tapes)

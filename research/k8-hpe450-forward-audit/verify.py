#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for @ToikY with substantial OpenAI Codex assistance.
"""Exact forward-basis corroboration of PR1611's scalar row/column claim.

Uses the pinned main producers only. Does not import the pending PR checker,
its reverse covector implementation, or a producer replay function.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 712
H = 450
SOURCE = 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'
VENDOR = 'research/complex-k492-owner-repair/vendor/multicold'
RAW = 'research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz'
ROUTING = VENDOR + '/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
PINS = 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def normalize(n, e):
    """Canonical n / 2**e, with odd n unless zero; e may be negative."""
    if not n:
        return (0, 0)
    absolute = abs(n)
    shift = (absolute & -absolute).bit_length() - 1
    return (n >> shift, e - shift)


def coefficient(a, b):
    require(type(a) is int and type(b) is int and b != 0, 'invalid coefficient')
    if b < 0:
        a, b = -a, -b
    common = math.gcd(a, b)
    a, b = a // common, b // common
    require(b & (b - 1) == 0, 'non-dyadic coefficient')
    return normalize(a, b.bit_length() - 1)


def plus(a, b):
    if not a[0]:
        return b
    if not b[0]:
        return a
    e = max(a[1], b[1])
    return normalize((a[0] << (e - a[1])) + (b[0] << (e - b[1])), e)


def times(a, b):
    return (a[0] * b[0], a[1] + b[1]) if a[0] and b[0] else (0, 0)


def rational(a):
    return Fraction(a[0], 1 << a[1]) if a[1] >= 0 else Fraction(a[0] << -a[1])


def wire(reg):
    require(isinstance(reg, list) and len(reg) == 2 and type(reg[1]) is int,
            'invalid wire')
    tag, index = reg
    require(tag in ('L', 'C') and 0 <= index < (704 if tag == 'L' else 8), 'wire range')
    return index + (704 if tag == 'C' else 0)


def label(index):
    return ['L', index] if index < 704 else ['C', index - 704]


def decode(events):
    ops = []
    for event in events:
        if event[0] != 'scalar':
            continue
        op = event[1]
        require(op[0] in ('clear', 'copy', 'scale', 'add'), 'unknown scalar')
        tag = op[0]
        require(len(op) == {'clear': 2, 'copy': 3, 'scale': 4, 'add': 5}[tag], 'scalar shape')
        target = wire(op[1])
        source = wire(op[2]) if tag in ('copy', 'add') else None
        require(source != target, 'scalar alias')
        q = coefficient(*op[-2:]) if tag in ('scale', 'add') else None
        ops.append((tag, target, source, q))
    return ops


def push(ops, basis, size=N):
    """Literal forward execution on one basis input; no inverse/row pullback."""
    values = [(0, 0)] * size
    values[basis] = (1, 0)
    for tag, target, source, q in ops:
        if tag == 'clear':
            values[target] = (0, 0)
        elif tag == 'copy':
            values[target] = values[source]
        elif tag == 'scale':
            values[target] = times(values[target], q)
        else:
            values[target] = plus(values[target], times(values[source], q))
    return values


def all_inputs(ops):
    column = None
    for basis in range(N):
        final = push(ops, basis)
        require(final[H] == ((1, 0) if basis == H else (0, 0)),
                'helper row differs at ' + str(label(basis)))
        if basis == H:
            column = final
    require(column == [(1, 0) if i == H else (0, 0) for i in range(N)],
            'helper dirt column leaks')
    return {'basis_inputs': N, 'output_row': [[label(H), '1']],
            'dirt_column': [[label(H), '1']], 'private_input_coefficients': ['0'] * 8}


def witness(ops):
    # Check the helper column first, then every remaining input if needed.
    for basis in [H] + [i for i in range(N) if i != H]:
        final = push(ops, basis)
        if basis == H:
            for out, value in enumerate(final):
                wanted = (1, 0) if out == H else (0, 0)
                if value != wanted:
                    return {'input': label(basis), 'output': label(out),
                            'actual': str(rational(value)), 'expected': str(rational(wanted))}
        wanted = (1, 0) if basis == H else (0, 0)
        if final[H] != wanted:
            return {'input': label(basis), 'output': label(H),
                    'actual': str(rational(final[H])), 'expected': str(rational(wanted))}
    raise ValueError('mutant preserves audited row and column')


def controls(events):
    last = max(i for i, e in enumerate(events) if e[0] == 'scalar' and
               ['L', H] in e[1][1:3])
    require(events[last][1][0] == 'add', 'last helper operation is not ADD')
    cases = {}
    bad = copy.deepcopy(events)
    bad.pop(last)
    cases['omitted_last_helper_add'] = witness(decode(bad))
    bad = copy.deepcopy(events)
    bad[last][1][3] *= -1
    cases['flipped_last_helper_add'] = witness(decode(bad))
    bad = copy.deepcopy(events)
    bad.insert(last + 1, ['scalar', ['add', ['L', 230], ['L', H], 1, 1], events[last][2]])
    cases['restored_row_but_dirt_leak'] = witness(decode(bad))
    # Independent row audit must still pass the dirt-leak control.
    bad_ops = decode(bad)
    require(all(push(bad_ops, i)[H] == ((1, 0) if i == H else (0, 0))
                for i in range(N)), 'leak unexpectedly alters helper row')
    return cases


def arithmetic_control():
    # Fraction is only a small oracle, never the full-word implementation.
    values = [coefficient(a, b) for a in range(-8, 9) for b in (1, 2, 4, -8)]
    for a, b in itertools.product(values, repeat=2):
        require(rational(plus(a, b)) == rational(a) + rational(b), 'dyadic add oracle')
        require(rational(times(a, b)) == rational(a) * rational(b), 'dyadic multiply oracle')
    for a, b in ((1, 0), (True, 1), (1, 3)):
        try:
            coefficient(a, b)
        except ValueError:
            pass
        else:
            raise ValueError('invalid coefficient accepted')
    # Dirty COPY/CLEAR echo: all three local coordinates are unchanged and
    # private scratch is zero, even when its input was arbitrary.
    half = coefficient(1, 2)
    toy = [('copy', 3, 1, None), ('add', 0, 3, half), ('clear', 3, None, None),
           ('add', 0, 1, coefficient(-1, 2)),
           ('scale', 2, None, coefficient(-2, 1)),
           ('scale', 2, None, coefficient(-1, 2))]
    for basis in range(4):
        require(push(toy, basis, 4) == [(1, 0) if i == basis and i < 3 else (0, 0)
                                       for i in range(4)], 'dirty echo map')
    add_instead = [('add', 3, 1, (1, 0))] + toy[1:]
    require(push(add_instead, 3, 4)[0] == half, 'COPY overwrite control')
    no_clear = toy[:2] + toy[3:]
    require(push(no_clear, 1, 4)[3] == (1, 0), 'CLEAR scratch control')
    return {'exact_arithmetic_pairs': len(values) ** 2, 'invalid_coefficients_rejected': 3,
            'dirty_echo_basis_inputs': 4, 'copy_clear_semantic_controls': 2}


def source_bindings():
    rows = load(HERE / 'SOURCES.json')['files']
    inputs = {}
    for row in rows:
        if row['usage'] != 'input':
            continue
        path = (ROOT / row['path']).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'source path')
        require(sha(path.read_bytes()) == row['sha256'], 'source drift: ' + row['path'])
        inputs[row['path']] = row['sha256']
    return inputs


def compute():
    inputs = source_bindings()
    pins = load(ROOT / PINS)
    selected = load(ROOT / 'research/community-frontier1094-audit/SELECTED-SOURCE.json')
    require(selected['files'][PINS] == inputs[PINS], 'selected slot source binding')
    require(sha(gzip.decompress((ROOT / RAW).read_bytes())) == pins['word_sha256'], 'raw pin')
    env = dict(os.environ, MULTICOLD_SOURCE=str(ROOT / VENDOR))
    for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME'):
        env.pop(key, None)
    with tempfile.TemporaryDirectory(prefix='hpe450-forward-') as tmp:
        out = Path(tmp) / 'local'
        commands = [
            [ROOT / SOURCE / 'hpe_audit_and_transport.py', '--raw', ROOT / RAW,
             '--routing', ROOT / ROUTING, '--out', out],
            [ROOT / SOURCE / 'hpe_emit_local.py', out],
        ]
        for cmd in commands:
            run = subprocess.run([sys.executable, '-I', '-B', *map(str, cmd)],
                                 cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
            require(run.returncode == 0, 'producer failure: ' + run.stdout[-1000:] + run.stderr[-1000:])
        require(sha(gzip.decompress((out / 'CANONICAL-WORD.json.gz').read_bytes())) ==
                pins['canonical_sha256'], 'canonical pin')
        programs = load(out / 'LOCAL-PROGRAMS.json.gz')
        require(set(programs) == {'forward', 'backward'}, 'orientations')
        result = {}
        for name in ('forward', 'backward'):
            events = programs[name]
            require(sha(encoded(events)) == pins['program_sha256'][name], 'program pin')
            ops = decode(events)
            result[name] = dict(events=len(events), scalar_operations=len(ops),
                                **all_inputs(ops), controls=controls(events))
        require(source_bindings() == inputs, 'sources changed during run')
    return {'status': 'PASS_HPE450_FORWARD_BASIS_AUDIT', 'helper': H,
            'audited_pr': 1611, 'audited_head': '156cc788b5a8122b19686f015e5654b117e4389d',
            'program_sha256': pins['program_sha256'], 'input_sha256': inputs,
            'arithmetic_control': arithmetic_control(), 'orientations': result,
            'scope': 'Exact finite scalar row/column corroboration only. No event-to-Lean '
                     'translation, operator/recipe theorem, hosting, full cold replay or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write_result:
        with args.write_result.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    else:
        require(encoded(result) == encoded(load(HERE / 'RESULT.json')), 'receipt mismatch')
    print(result['status'] + ' orientations=2 basis_inputs=1424 controls=6 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        raise SystemExit('FAIL: ' + str(exc))

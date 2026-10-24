#!/usr/bin/env python3
"""Gate-level repair of the PR5270 replay-reference transcription.

Successor step to the audit in PR #5349 (research/pr5270-reference-audit).
That audit showed the emitted listing's reference differs from the formal
thinned controller in three ways, and checked a corrected interpreter at
p=2 and p=19. This package expresses the same three corrections as an
explicit transformation of the gate list itself, interprets the repaired
list with a plain interpreter that has no correction flags, and compares
against the formal controller for every p from 2 to 19 at the audit's
specialization (q=1, odd stage letters i, even stage letters 1).

Scope: this repairs the reference transcription only. It does not bind a
rank-eight native invocation, does not use independent stage blocks, and
does not recalculate any invoice. No new kappa is claimed.

The Gaussian-integer interpreter, the formal Laurent controller execution,
and the retained vendor files follow PR #5349's audit package, which
vendored them unchanged from PR5270 head df9e503 and PR4940's controller
package. Apache-2.0. Retained source files keep their original notices.
"""
import ast
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ZERO, ONE, I = (0, 0), (1, 0), (0, 1)

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

def ipow(k):
    return (ONE, I, (-1, 0), (0, -1))[k % 4]

def exact_matrix(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]

class Polynomial:
    @staticmethod
    def plus(a, b, coefficient=1):
        out = dict(a)
        for term, value in b.items():
            out[term] = out.get(term, 0) + coefficient * value
        return {k: v for k, v in out.items() if v}

    @staticmethod
    def monomial_times(a, term, coefficient=1):
        return {tuple(x + y for x, y in zip(k, term)): coefficient * v
                for k, v in a.items() if coefficient * v}

def retained_functions(path, names, environment):
    tree = ast.parse(path.read_bytes())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need({n.name for n in selected} == set(names), 'missing retained function')
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), environment)
    return environment

def formal_matrix(p):
    """Retained formal controller plus its thinning, at the audit specialization."""
    env = retained_functions(HERE / 'vendor/controller_verify.py',
                             ['controller', 'keep_of', 'thin'],
                             {'C': Polynomial, 'Q': Fraction})
    pat = 'I' * ((p - 1) // 2) + 'T' * (p - 1 - (p - 1) // 2)
    raw, idles = env['controller'](p, env['keep_of'](p, pat),
                                    {s: 1 for s in range(2 * p + 1)})
    thinned = env['thin'](raw, set(range(1, 2 * p, 2)))
    result = [[ZERO for _ in range(2 * p)] for _ in range(2 * p)]
    for term, matrix in thinned.items():
        value = ipow(sum(term[1:]))
        for i, row in enumerate(matrix):
            for j, coefficient in enumerate(row):
                need(coefficient.denominator == 1, 'integer specialization')
                result[i][j] = add(result[i][j], mul((int(coefficient), 0), value))
    return result

def interpret(gates, n):
    """Plain exact Gaussian-integer interpreter. No correction flags."""
    matrix = exact_matrix(n)

    def scaled(row, coefficient):
        return [mul(x, coefficient) for x in row]

    def accumulate(dst, src, coefficient):
        matrix[dst] = [add(x, y) for x, y in zip(matrix[dst], scaled(matrix[src], coefficient))]

    for gate in gates:
        kind = gate[0]
        if kind in ('GAUGE_LOAD', 'GAUGE_UNLOAD'):
            continue
        if kind == 'FORWARD':
            accumulate(gate[2], gate[1], ONE)
        elif kind == 'REVERSE':
            accumulate(gate[1], gate[2], (-1, 0))
        elif kind == 'LETTER':
            need(gate[3] == 'R', 'changed letter')
            for role in gate[1:3]:
                matrix[role] = scaled(matrix[role], I)
        elif kind == 'IDLE':
            for role in gate[1:3]:
                matrix[role] = scaled(matrix[role], ipow(gate[3]))
        elif kind == 'BRIDGE':
            accumulate(gate[1], gate[2], (gate[3], 0))
        elif kind == 'SWAP':
            matrix[gate[1]], matrix[gate[2]] = matrix[gate[2]], scaled(matrix[gate[1]], (-1, 0))
        else:
            raise ValueError('unknown gate ' + kind)
    return matrix

def repair(gates, p, skip=()):
    """The three transcription corrections, applied to the gate list.

    1. bridges: swap the endpoints of the first 2(p-1) odd-role BRIDGE
       gates (the forward loop). Later odd bridges belong to the final
       reverse sweep, whose direction is already correct, and stay as
       written.
    2. middle: IDLE gates tagged 'middle' become identity (power 0).
       They sit at even stages, which thinning removes.
    3. outer: IDLE gates tagged 'initial' or 'terminal' keep only the
       thick-stage share of their interval power (power // 2; every such
       interval in the listing starts at an odd stage and has even
       length, so the power is even).

    `skip` names a correction class to leave out, for negative controls.
    Returns (repaired_gates, stats).
    """
    out = []
    odd_seen = 0
    stats = {'bridges_swapped': 0, 'middle_zeroed': 0, 'outer_halved': 0}
    for gate in gates:
        if gate[0] == 'BRIDGE' and gate[1] % 2 == 1:
            odd_seen += 1
            if 'bridges' not in skip and odd_seen <= 2 * (p - 1):
                out.append(('BRIDGE', gate[2], gate[1], gate[3]))
                stats['bridges_swapped'] += 1
                continue
        if gate[0] == 'IDLE' and gate[4] == 'middle' and 'middle' not in skip:
            out.append(('IDLE', gate[1], gate[2], 0, gate[4]))
            stats['middle_zeroed'] += 1
            continue
        if gate[0] == 'IDLE' and gate[4] in ('initial', 'terminal') and 'outer' not in skip:
            need(gate[3] % 2 == 0, 'expected even outer interval power')
            out.append(('IDLE', gate[1], gate[2], gate[3] // 2, gate[4]))
            stats['outer_halved'] += 1
            continue
        out.append(gate)
    return out, stats

def listing(p):
    env = retained_functions(HERE / 'vendor/p19_word.py', ['pattern_of', 'listing'], {})
    return env['listing'](p)

def mismatches(a, b):
    n = len(a)
    return sum(1 for i in range(n) for j in range(n) if a[i][j] != b[i][j])

def main():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for row in pins['files']:
        need(sha256((HERE / row['local_path']).read_bytes()).hexdigest() == row['sha256'],
             'changed pinned source ' + row['local_path'])

    rows = []
    for p in range(2, 20):
        gates = listing(p)
        expected = formal_matrix(p)
        raw = interpret(gates, 2 * p)
        need(raw != expected, f'p{p}: original mismatch absent')
        fixed, stats = repair(gates, p)
        need(len(fixed) == len(gates), f'p{p}: gate count changed')
        need(stats == {'bridges_swapped': 2 * (p - 1), 'middle_zeroed': p - 1,
                       'outer_halved': p - 1}, f'p{p}: unexpected repair counts {stats}')
        changed = sum(1 for a, b in zip(gates, fixed) if a != b)
        need(changed == sum(stats.values()), f'p{p}: repair touched extra gates')
        again, _ = repair(gates, p)
        need(again == fixed, f'p{p}: repair not deterministic')
        repaired = interpret(fixed, 2 * p)
        need(repaired == expected, f'p{p}: repaired reference differs from formal controller')
        rows.append({'p': p, 'gates': len(gates),
                     'mismatched_entries_before': mismatches(raw, expected),
                     'mismatched_entries_after': 0,
                     'bridges_swapped': stats['bridges_swapped'],
                     'middle_zeroed': stats['middle_zeroed'],
                     'outer_halved': stats['outer_halved']})

    # The repaired p2 matrix is the audit's formal diagonal, entry for entry.
    need(interpret(repair(listing(2), 2)[0], 4) ==
         [[(-1, 0), ZERO, ZERO, ZERO], [ZERO, (-1, 0), ZERO, ZERO],
          [ZERO, ZERO, I, ZERO], [ZERO, ZERO, ZERO, I]], 'p2 repaired diagonal')

    # Negative controls: dropping any one correction class breaks the
    # equality at p=2, p=3 and p=19.
    controls = []
    for p in (2, 3, 19):
        expected = formal_matrix(p)
        for cls in ('bridges', 'middle', 'outer'):
            partial, _ = repair(listing(p), p, skip=(cls,))
            need(interpret(partial, 2 * p) != expected,
                 f'p{p}: {cls}-only defect not detected')
            controls.append(f'p{p} without {cls} correction')

    output = {
        'status': 'PASS_PR5270_REFERENCE_TRANSCRIPTION_REPAIR',
        'builds_on': 'PR #5349 audit (research/pr5270-reference-audit)',
        'specialization': {'q': '1', 'odd_stage_letters': 'i', 'even_stage_letters': '1'},
        'range': 'every p from 2 to 19',
        'rows': rows,
        'negative_controls_rejected': controls,
        'scope': ('The repaired gate list, read by a plain interpreter with no '
                  'correction flags, agrees with the formal thinned controller '
                  'at the audit specialization for every p in 2..19. Reference '
                  'transcription only. No rank-eight native binding, no '
                  'independent-block binding, no invoice recalculation, no '
                  'new kappa.'),
    }
    text = json.dumps(output, indent=2)
    print(text)
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(text + '\n')

if __name__ == '__main__':
    main()

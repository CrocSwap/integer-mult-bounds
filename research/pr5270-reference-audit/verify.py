#!/usr/bin/env python3
"""Exact, scoped witness that PR5270's replay reference is not its thinned invoice.

New audit: OpenAI Codex for ahrazzle. Apache-2.0.
Retained source files keep their original authorship and notices.
No full-supplier impossibility or new multiplication exponent is claimed.
"""
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ZERO, ONE, I = (0, 0), (1, 0), (0, 1)

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def add(a, b):
    return (a[0]+b[0], a[1]+b[1])

def mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

def ipow(k):
    return (ONE, I, (-1, 0), (0, -1))[k % 4]

def exact_matrix(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]

class Polynomial:
    @staticmethod
    def plus(a, b, coefficient=1):
        out = dict(a)
        for term, value in b.items():
            out[term] = out.get(term, 0)+coefficient*value
        return {k: v for k, v in out.items() if v}

    @staticmethod
    def monomial_times(a, term, coefficient=1):
        return {tuple(x+y for x, y in zip(k, term)): coefficient*v
                for k, v in a.items() if coefficient*v}

def retained_functions(path, names, environment):
    tree = ast.parse(path.read_bytes())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need({n.name for n in selected} == set(names), 'missing retained function')
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), environment)
    return environment

def formal_matrix(p):
    """Execute retained Laurent-polynomial controller, then its exact thinning.

    Evaluate q=1 and every retained odd stage letter at i. This is a valid
    Gaussian eigenvalue specialization. No diagonalizer or numerical solver.
    """
    env = retained_functions(HERE/'vendor/controller_verify.py',
                             ['controller', 'keep_of', 'thin'],
                             {'C': Polynomial, 'Q': Fraction})
    pat = 'I'*((p-1)//2)+'T'*(p-1-(p-1)//2)
    raw, idles = env['controller'](p, env['keep_of'](p, pat),
                                    {s: 1 for s in range(2*p+1)})
    thinned = env['thin'](raw, set(range(1, 2*p, 2)))
    result = [[ZERO for _ in range(2*p)] for _ in range(2*p)]
    for term, matrix in thinned.items():
        value = ipow(sum(term[1:]))
        for i, row in enumerate(matrix):
            for j, coefficient in enumerate(row):
                need(coefficient.denominator == 1, 'integer specialization')
                result[i][j] = add(result[i][j], mul((int(coefficient), 0), value))
    return result

def listed_matrix(p, fix_middle=False, fix_outer=False, fix_bridges=False):
    """Separate exact Gaussian-integer interpreter of the emitted reference.

    Boundary codes are omitted because this audits the standard() reference
    to which the source claims the coded listing is gauge-equivalent.
    """
    env = retained_functions(HERE/'vendor/p19_word.py', ['pattern_of', 'listing'], {})
    gates = env['listing'](p)
    matrix = exact_matrix(2*p)

    def scaled(row, coefficient):
        return [mul(x, coefficient) for x in row]

    def accumulate(dst, src, coefficient):
        matrix[dst] = [add(x, y) for x, y in zip(matrix[dst], scaled(matrix[src], coefficient))]

    odd_bridges = 0
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
            power = gate[3]
            if gate[4] == 'middle' and fix_middle:
                power = 0
            elif gate[4] in ('initial', 'terminal') and fix_outer:
                # Both intervals start at an odd stage and have even length.
                # Exactly half of their letters survive odd-stage thinning.
                need(power % 2 == 0, 'expected even outer interval')
                power //= 2
            for role in gate[1:3]:
                matrix[role] = scaled(matrix[role], ipow(power))
        elif kind == 'BRIDGE':
            dst, src = gate[1:3]
            if dst % 2:
                if fix_bridges and odd_bridges < 2*(p-1):
                    dst, src = src, dst
                odd_bridges += 1
            accumulate(dst, src, (gate[3], 0))
        elif kind == 'SWAP':
            matrix[gate[1]], matrix[gate[2]] = matrix[gate[2]], scaled(matrix[gate[1]], (-1, 0))
        else:
            raise ValueError('unknown gate '+kind)
    return matrix

def native_reference_matrix():
    """Run the retained standard() itself on a genuine 512-address eigenvector.

    v[x]=(-1)^bit_1(x): central Q fixes v; full nine-axis R multiplies it by i.
    Four basis-role inputs recover the full 4x4 role matrix. Arithmetic mod
    65537 is exact; i=256. This binds the independent interpreter to the actual
    source reference, without running its random dense p19 experiment.
    """
    spec = importlib.util.spec_from_file_location('retained_lift', HERE/'vendor/physical_gauge_lift.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    env = retained_functions(HERE/'vendor/p19_word.py',
                             ['gaussian_power', 'pattern_of', 'standard'], {'P': 65537, 'SIZE': 512})
    prime = 65537
    vector = [1 if not x & 2 else prime-1 for x in range(512)]
    need(module.gaussian([vector], [0]) == [vector], 'Q eigenvalue one')
    need(module.gaussian([vector], range(9)) == [[256*x % prime for x in vector]], 'R eigenvalue i')
    matrix = [[0]*4 for _ in range(4)]
    for column in range(4):
        initial = [[[0]*512] for _ in range(4)]
        initial[column] = [vector]
        out = env['standard'](2, initial, 'R', module)
        for row in range(4):
            coefficient = out[row][0][0]
            need(out[row][0] == [coefficient*x % prime for x in vector], 'eigenvector subspace preserved')
            matrix[row][column] = coefficient
    return matrix

def main():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        need(sha256((HERE/row['local_path']).read_bytes()).hexdigest() == row['sha256'],
             'changed pinned source '+row['local_path'])
    expected = formal_matrix(2)
    actual = listed_matrix(2)
    need(expected == [[(-1,0),ZERO,ZERO,ZERO], [ZERO,(-1,0),ZERO,ZERO],
                      [ZERO,ZERO,I,ZERO], [ZERO,ZERO,ZERO,I]], 'formal p2 diagonal')
    need(actual == [[(0,-1),ZERO,ZERO,(1,-1)], [ZERO,(0,-1),(1,-1),ZERO],
                    [ZERO,ZERO,(-1,0),ZERO], [ZERO,(0,-1),(2,-1),(-1,0)]], 'literal p2 witness')
    need(actual != expected, 'counterexample disappeared')
    reduce_field = lambda m: [[(a+256*b) % 65537 for a,b in row] for row in m]
    need(native_reference_matrix() == reduce_field(actual), 'retained source reference differs from independent interpreter')
    # Reference-path consistency controls, not admission of a repaired supplier.
    need(listed_matrix(2, True, True, True) == expected, 'corrected reference positive control')
    need(listed_matrix(2, True, False, True) != expected, 'terminal-only defect not detected')
    need(listed_matrix(2, False, True, True) != expected, 'middle-only defect not detected')
    need(listed_matrix(2, True, True, False) != expected, 'bridge-only defect not detected')
    expected19, actual19 = formal_matrix(19), listed_matrix(19)
    need(actual19 != expected19, 'p19 mismatch absent')
    need(listed_matrix(19, True, True, True) == expected19, 'p19 corrected reference positive control')
    mismatches = [(i,j) for i in range(38) for j in range(38) if expected19[i][j] != actual19[i][j]]
    output = {
        'status': 'PASS_SCOPED_PR5270_REFERENCE_INVOICE_COUNTEREXAMPLE',
        'source_head': pins['head'],
        'specialization': {'q': '1', 'odd_stage_letters': 'i', 'even_stage_letters': '1'},
        'p2_formal_matrix_gaussian_pairs': expected,
        'p2_source_reference_matrix_gaussian_pairs': actual,
        'p2_retained_512_address_reference': 'matches independent Gaussian-integer interpreter modulo 65537',
        'p19_mismatched_matrix_entries': len(mismatches),
        'p19_first_mismatches': mismatches[:12],
        'positive_controls': ['corrected p2 bridge direction and idle thinning', 'corrected p19 bridge direction and idle thinning'],
        'rejected_controls': ['uncorrected p2 middle idle', 'uncorrected p2 terminal idle', 'uncorrected p2 odd-role bridge direction'],
        'scope': 'Source replay reference is not the formal thinned controller whose invoice is priced. No impossibility claim; no new kappa; no supplier repair admitted.'
    }
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()

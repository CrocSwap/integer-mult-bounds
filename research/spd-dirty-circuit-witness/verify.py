"""Exact differential and literal checks for the bounded-condition witness.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from witness import produce
from literal import check, endpoint, action, require
from fields import scalars


def expanded(problem):
    scalar = scalars(problem)
    initial = [{(j, ()): scalar(1)} for j in range(problem['roles'])]

    def combine(a, b, c):
        out = a.copy()
        for key, x in b.items():
            out[key] = out.get(key, scalar(0))+c*x
        return {key: x for key, x in out.items() if x}

    def run(ops):
        rows = [row.copy() for row in initial]
        for op in ops:
            d, kind = op['dst'], op['op']
            if kind == 'swap':
                s = op['src']; rows[d], rows[s] = rows[s], rows[d]
            elif kind == 'scale':
                rows[d] = combine({}, rows[d], scalar(op['coefficient']))
            else:
                value = rows[d if kind == 'apply' else op['src']].copy()
                if kind in ('apply', 'query'):
                    value = {(j, (op['symbol'],)+word): x for (j, word), x in value.items()}
                rows[d] = value if kind == 'apply' else combine(rows[d], value, scalar(op.get('coefficient', 1)))
        return rows

    left = run(problem['program'])
    if 'reference' in problem:
        right = run(problem['reference'])
    else:
        t = problem['target']
        right = [row.copy() if t.get('identity', True) else {} for row in initial]
        for term in t.get('terms', []):
            d = term['out']
            right[d] = combine(right[d], {(term['in'], tuple(term['word'])): scalar(term.get('coefficient', 1))}, scalar(1))
    return [combine(a, b, scalar(-1)) for a, b in zip(left, right)]


def reject(fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError):
        return
    raise ValueError('control accepted')


def fixtures():
    rng = random.Random(5260)
    count = negative = positive = 0
    for field in ('Q', 'Qi'):
        for size in range(1, 5):
            for trial in range(30):
                ops = []
                for _ in range(12):
                    kind = rng.choice(('add', 'query', 'scale', 'swap', 'apply'))
                    op = {'op': kind, 'dst': rng.randrange(size)}
                    if kind in ('add', 'query', 'swap'): op['src'] = rng.randrange(size)
                    if kind in ('query', 'apply'): op['symbol'] = rng.choice(('X', 'Y', 'Z'))
                    if kind in ('add', 'query', 'scale'):
                        op['coefficient'] = rng.choice(('0', '1', '-1', '2/3', '1+i') if field == 'Qi' else ('0', '1', '-1', '2/3'))
                    ops.append(op)
                problem = {'roles': size, 'field': field, 'program': ops,
                           'reference': ops if trial % 5 == 0 else []}
                polynomial = expanded(problem)
                degrees = [len(word) for row in polynomial for _, word in row]
                cert = produce(problem)
                require(cert['equivalent'] == (not degrees), 'equivalence differs from expansion')
                if degrees:
                    require(len(cert['word']) == max(degrees), 'wrong top degree')
                    actual = polynomial[cert['output']][(cert['input'], tuple(cert['word']))]
                    require(str(actual) == cert['coefficient'], 'wrong top coefficient')
                    for epsilon in (Q(1, 4), Q(1, 64)):
                        check(problem, produce(problem, epsilon))
                    negative += 1
                else:
                    positive += 1
                count += 1
    return {'differential_circuits': count, 'negative_circuits': negative,
            'equivalent_circuits': positive, 'literal_replays': 2*negative}


def controls():
    # A shortest constant witness fails at X=3I/4, but the degree-one path succeeds.
    p = {'roles': 1, 'program': [{'op': 'apply', 'dst': 0, 'symbol': 'X'}],
         'target': {'identity': False, 'terms': [{'out': 0, 'in': 0, 'word': [], 'coefficient': '3/4'}]}}
    c = produce(p)
    require(c['word'] == ['X'] and check(p, c) == '1/8', 'highest-degree control')
    require(endpoint(p, [[Q(1)]], [], Q(1, 4)) == [[Q(0)]], 'constant witness must fail')
    for key, value in [('word', []), ('coefficient', '-1'), ('input', 1), ('output', 1),
                       ('epsilon', '0'), ('epsilon', '1/2'), ('dimension', 1),
                       ('spectral_interval', ['0', '1']), ('problem_sha256', '0'*64),
                       ('equivalent', True)]:
        mutant = deepcopy(c); mutant[key] = value
        reject(lambda: check(p, mutant))
    reject(lambda: produce(dict(p, field=2)))
    reject(lambda: produce(p, 0))
    # A returned dirty helper can fail while the requested data role is unchanged.
    dirty = {'roles': 2, 'program': [{'op': 'query', 'src': 1, 'dst': 1, 'symbol': 'X'}], 'reference': []}
    d = produce(dirty); require((d['output'], d['input']) == (1, 1), 'dirty role omitted'); check(dirty, d)
    # A commutator must not vanish under the symmetric path substitution.
    comm = {'roles': 1, 'program': [], 'target': {'terms': [
        {'out': 0, 'in': 0, 'word': ['X', 'Y']},
        {'out': 0, 'in': 0, 'word': ['Y', 'X'], 'coefficient': -1}]}}
    check(comm, produce(comm))
    return 15


def stress():
    ops = []
    for _ in range(64):
        ops.extend([{'op': 'scale', 'dst': 1, 'coefficient': 0},
                    {'op': 'query', 'src': 0, 'dst': 1, 'symbol': 'X'},
                    {'op': 'query', 'src': 0, 'dst': 1, 'symbol': 'Y'},
                    {'op': 'swap', 'src': 0, 'dst': 1}])
    p = {'roles': 2, 'program': ops, 'target': {'identity': False}}
    cert = produce(p)
    require(len(cert['word']) == 64, 'stress degree')
    difference = check(p, cert)
    require(Q(difference) == Q(1, 8)**64, 'stress endpoint')
    return {'expanded_top_words': 2**64, 'degree': 64, 'dimension': cert['dimension'],
            'states': cert['statistics']['states'],
            'maximum_layer_dimension': max(cert['statistics']['layer_dimensions']),
            'sum_layer_dimensions': sum(cert['statistics']['layer_dimensions']),
            'discrepancy': difference}


def spectral_checks():
    cases = 0
    for length in range(16):
        word = ['X' if j % 3 else 'Y' for j in range(length)]
        for epsilon in (Q(1, 4), Q(1, 64)):
            for symbol in ('X', 'Y', 'Z'):
                n = length+1
                columns = [action([Q(int(i == j)) for i in range(n)], symbol, word, epsilon) for j in range(n)]
                require(all(columns[j][i] == columns[i][j] for i in range(n) for j in range(n)), 'not symmetric')
                for i in range(n):
                    radius = sum(abs(columns[j][i]) for j in range(n) if j != i)
                    require(columns[i][i]-radius >= 1-2*epsilon and columns[i][i]+radius <= 1, 'spectral enclosure')
                cases += 1
    return cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--small', action='store_true')
    args = ap.parse_args()
    report = {'fixtures': fixtures(), 'controls': controls(), 'spectral_matrices': spectral_checks()}
    if args.small:
        print(json.dumps(report, sort_keys=True)); return
    report['stress'] = stress()
    example = json.loads((HERE/'wrong-order.json').read_text())
    cert = produce(example)
    report['source_example'] = {'certificate': cert, 'discrepancy': check(example, cert)}
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for f in ('fields.py', 'linear_words.py', 'wrong-order.json'):
        row = next(r for r in sources['files'] if r['path'].endswith('/'+f))
        require(hashlib.sha256(((HERE/'vendor'/f) if f.endswith('.py') else (HERE/f)).read_bytes()).hexdigest() == row['sha256'], 'vendor drift')
    names = sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'RESULT.json')
    report['files'] = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in names}
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    else:
        require(report == json.loads((HERE/'RESULT.json').read_text()), 'receipt drift')
    print('PASS_SPD_DIRTY_WITNESS ' + json.dumps({k: v for k, v in report.items() if k != 'files'}, sort_keys=True))


if __name__ == '__main__':
    main()

"""Replay a returned counterexample without coefficient-space elimination.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Scalar arithmetic is retained from zxv; see NOTICE.md.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from fields import scalars


def require(value, message):
    if not value:
        raise ValueError(message)


def action(vector, symbol, word, epsilon):
    result = [(1-epsilon)*value for value in vector]
    for j, label in enumerate(word):
        if label == symbol:
            result[j] += epsilon/2*vector[j+1]
            result[j+1] += epsilon/2*vector[j]
    return result


def run(instructions, inputs, word, epsilon, scalar):
    rows = [row[:] for row in inputs]
    for op in instructions:
        dst = op['dst']
        kind = op['op']
        if kind == 'swap':
            src = op['src']
            rows[src], rows[dst] = rows[dst], rows[src]
        elif kind == 'scale':
            rows[dst] = [scalar(op['coefficient'])*x for x in rows[dst]]
        else:
            src = dst if kind == 'apply' else op['src']
            value = rows[src][:]
            if kind in ('query', 'apply'):
                value = action(value, op['symbol'], word, epsilon)
            if kind == 'apply':
                rows[dst] = value
            else:
                require(kind in ('add', 'query'), 'invalid instruction')
                c = scalar(op.get('coefficient', 1))
                rows[dst] = [x+c*y for x, y in zip(rows[dst], value)]
    return rows


def endpoint(problem, inputs, word, epsilon):
    scalar = scalars(problem)
    left = run(problem['program'], inputs, word, epsilon, scalar)
    if 'reference' in problem:
        right = run(problem['reference'], inputs, word, epsilon, scalar)
    else:
        target = problem['target']
        right = [row[:] if target.get('identity', True) else [scalar(0)]*len(row)
                 for row in inputs]
        for term in target.get('terms', []):
            value = inputs[term['in']][:]
            for symbol in reversed(term['word']):
                value = action(value, symbol, word, epsilon)
            c = scalar(term.get('coefficient', 1))
            out = term['out']
            right[out] = [x+c*y for x, y in zip(right[out], value)]
    return [[x-y for x, y in zip(a, b)] for a, b in zip(left, right)]


def check(problem, certificate):
    """Check the negative witness only. Positive certificates need the source checker."""
    require(certificate.get('schema') == 'spd-dirty-witness/v1', 'wrong schema')
    require(certificate.get('equivalent') is False, 'negative witness required')
    require(problem.get('field', 'Q') in ('Q', 'Qi'), 'ordered field required')
    encoded = json.dumps(problem, sort_keys=True, separators=(',', ':')).encode()
    require(hashlib.sha256(encoded).hexdigest() == certificate['problem_sha256'], 'problem drift')
    word = certificate['word']
    require(isinstance(word, list) and all(type(s) is str and s for s in word), 'word required')
    dimension = len(word) + 1
    require(certificate['dimension'] == dimension, 'wrong dimension')
    epsilon = Q(certificate['epsilon'])
    require(0 < epsilon <= Q(1, 4), 'bad spectral parameter')
    require(certificate['spectral_interval'] == [str(1-2*epsilon), '1'], 'wrong interval')
    scalar = scalars(problem)
    source, output = certificate['input'], certificate['output']
    n = problem['roles']
    require(type(source) is int and type(output) is int and 0 <= source < n and 0 <= output < n,
            'wrong role')
    inputs = [[scalar(0)]*dimension for _ in range(n)]
    inputs[source][-1] = scalar(1)
    difference = endpoint(problem, inputs, word, epsilon)[output][0]
    predicted = scalar(certificate['coefficient'])*(epsilon/2)**len(word)
    require(bool(predicted) and difference == predicted, 'literal endpoint disagrees')
    return str(difference)

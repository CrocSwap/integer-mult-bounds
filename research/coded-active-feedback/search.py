#!/usr/bin/env python3
"""Bounded active-query synthesis in a declared universal operator algebra.

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
The symbolic algebra is a sufficient identity model, not a faithful model of
every additional relation in the physical source.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reduce_word(word):
    """Normal form in C4(Q) * C2(C1) * C2(C3)."""
    out = []
    for letter in word:
        if abs(letter) in (2, 3):
            letter = abs(letter)
            if out and out[-1] == letter:
                out.pop()
            else:
                out.append(letter)
        else:
            need(abs(letter) == 1, 'Unknown formal generator')
            exponent = letter
            while out and abs(out[-1]) == 1:
                exponent += out.pop()
            exponent %= 4
            out.extend((1,) * exponent if exponent <= 2 else (-1,))
    return tuple(out)


def algebra():
    path = ROOT / 'research/coded-native-caller/gauge.py'
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() ==
         '390391d291353741c89daea999d483660ca185987ed96a15b82576280c487cad',
         'Changed inherited group-algebra engine')
    module = types.ModuleType('feedback_inherited_gauge')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    module.reduce_word = reduce_word
    return module.Algebra(2)


def words(length):
    return [()] + [tuple(2 + ((j + start) % 2) for j in range(n))
                   for n in range(1, length + 1) for start in range(2)]


def scaled(a, scalar, row):
    return [a.mul(a.term((), (0, 0), scalar), entry) for entry in row]


def replay(a, feedback1, feedback2, coefficient1=1, coefficient2=1,
           codes=True):
    q, qi = a.gen(1), a.inv(a.gen(1))
    c1, c3 = (a.gen(2), a.gen(3)) if codes else (a.one, a.one)
    d1, d3 = a.D(0), a.D(1)
    rows = [[a.one if i == j else {} for j in range(4)] for i in range(4)]
    observed = []
    responses = []

    def snap(label):
        observed.extend((label + ':' + str(i), list(row))
                        for i, row in enumerate(rows))

    def plus(dst, src, op):
        rows[dst] = [a.add(x, a.mul(op, y))
                     for x, y in zip(rows[dst], rows[src])]

    def left(index, op):
        rows[index] = [a.mul(op, entry) for entry in rows[index]]

    def query(pair, argument, label, after=None):
        response = [a.mul(qi, entry) for entry in argument]
        observed.append((label, response))
        responses.append(response)
        rows[2 * pair + 1] = [a.add(x, a.mul(after or a.one, y))
                              for x, y in zip(rows[2 * pair + 1], response)]
        return response

    def full(pair, code, stage):
        plus(2 * pair, 2 * pair + 1, a.neg(a.mul(q, code)))
        left(2 * pair, stage)
        left(2 * pair + 1, stage)

    def bridge(dst, src, sign):
        plus(2 * dst, 2 * src, scaled(a, sign, [a.one])[0])
        plus(2 * src + 1, 2 * dst + 1, scaled(a, -sign, [a.one])[0])

    rows[0][2], rows[3][1] = a.neg(a.one), a.one
    snap('right')
    query(0, rows[0], 'response0', c1)
    snap('query0')
    full(0, c1, d1)
    snap('FULL1')
    late_y = list(rows[1])
    left(2, d1)
    left(3, d1)
    snap('IDLE')
    bridge(0, 1, 1)
    argument = [a.add(a.mul(c1, x), a.mul(feedback1, y))
                for x, y in zip(rows[0], scaled(a, coefficient1, late_y))]
    response2 = query(0, argument, 'response2')
    snap('bridge_query2')
    bridge(0, 1, -1)
    snap('bridge_minus')
    full(1, c3, d3)
    snap('FULL3')
    argument = [a.add(a.mul(c3, x), a.mul(feedback2, y))
                for x, y in zip(rows[2], scaled(a, coefficient2, response2))]
    query(1, argument, 'response4')
    snap('query4')
    bridge(1, 0, 1)
    for x, y in ((0, 1), (2, 3)):
        rows[x], rows[y] = rows[y], [a.neg(entry) for entry in rows[x]]
    plus(0, 2, a.one)
    plus(3, 1, a.neg(a.one))
    snap('left')
    targets = [a.mul(d1, qi), a.mul(d1, q),
               a.mul(d3, d1, qi), a.mul(d3, d1, q)]
    targets = [[target if i == j else {} for j in range(4)]
               for i, target in enumerate(targets)]
    return observed, targets, rows


def vector(row):
    return {(source, word, powers): value
            for source, entry in enumerate(row)
            for (word, powers), value in entry.items() if value}


def axpy(x, scalar, y):
    out = dict(x)
    for key, value in y.items():
        out[key] = out.get(key, F(0)) + scalar * value
        if not out[key]:
            del out[key]
    return out


class Span:
    def __init__(self, a, controls):
        self.a, self.controls = a, controls
        self.basis, self.generators = {}, []

    def clone(self):
        out = Span(self.a, self.controls)
        out.basis, out.generators = dict(self.basis), list(self.generators)
        return out

    def add(self, label, row):
        a, basis, generators = self.a, self.basis, self.generators
        for word in self.controls:
            op = a.term(word, (0, 0))
            value = vector([a.mul(op, entry) for entry in row])
            index = len(generators)
            generators.append((label, word))
            recipe = {index: F(1)}
            while value:
                pivot = min(value)
                if pivot not in basis:
                    factor = 1 / value[pivot]
                    basis[pivot] = ({key: v * factor for key, v in value.items()},
                                    {key: v * factor for key, v in recipe.items()})
                    break
                base, base_recipe = basis[pivot]
                factor = value[pivot]
                value = axpy(value, -factor, base)
                recipe = axpy(recipe, -factor, base_recipe)

    def test(self, targets, certificate=False):
        basis, generators = self.basis, self.generators
        results = []
        for row in targets:
            value, recipe = vector(row), {}
            while value:
                pivot = min(value)
                if pivot not in basis:
                    break
                base, base_recipe = basis[pivot]
                factor = value[pivot]
                value = axpy(value, -factor, base)
                recipe = axpy(recipe, factor, base_recipe)
            answer = {'attained': not value,
                      'recipe': [{'observation': generators[i][0],
                                  'word': list(generators[i][1]),
                                  'coefficient': str(v)}
                                 for i, v in sorted(recipe.items())] if not value else None,
                      'residual_terms': len(value)}
            if value and certificate:
                functional = {min(value): F(1)}
                for pivot, (base, _) in sorted(basis.items(), reverse=True):
                    v = -sum(coefficient * functional.get(key, 0)
                             for key, coefficient in base.items() if key != pivot)
                    if v:
                        functional[pivot] = v
                    else:
                        functional.pop(pivot, None)
                need(all(sum(v * functional.get(key, 0) for key, v in base.items()) == 0
                         for base, _ in basis.values()), 'Dual annihilates basis')
                pairing = sum(v * functional.get(key, 0) for key, v in vector(row).items())
                need(pairing != 0, 'Dual separates failed target')
                answer['dual'] = [[i, list(w), list(d), str(v)]
                                  for (i, w, d), v in sorted(functional.items())]
                answer['target_pairing'] = str(pairing)
            results.append(answer)
        return {'dimension': len(basis), 'results': results}


def span(a, observations, targets, controls):
    out = Span(a, controls)
    for label, row in observations:
        out.add(label, row)
    return out.test(targets)


def verify_answer(a, observations, target, controls, answer):
    """Direct dot products/recipe replay, independent of elimination pivots."""
    if answer['attained']:
        rows = dict(observations)
        value = {}
        for term in answer['recipe']:
            op = a.term(term['word'], (0, 0), F(term['coefficient']))
            value = axpy(value, 1, vector([a.mul(op, entry)
                                          for entry in rows[term['observation']]]))
        need(value == vector(target), 'Positive recipe directly reproduces target')
    else:
        dual = {(i, tuple(w), tuple(d)): F(v) for i, w, d, v in answer['dual']}
        for _, row in observations:
            for word in controls:
                op = a.term(word, (0, 0))
                value = vector([a.mul(op, entry) for entry in row])
                need(sum(v * dual.get(key, 0) for key, v in value.items()) == 0,
                     'Dual directly annihilates every declared generator')
        pairing = sum(v * dual.get(key, 0) for key, v in vector(target).items())
        need(pairing == F(answer['target_pairing']) != 0,
             'Dual directly separates target')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--length', type=int, default=3)
    parser.add_argument('--decoder-length', type=int, default=7)
    parser.add_argument('--coefficients', default='1')
    parser.add_argument('--certificates', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    need(0 <= args.length <= 7 and 0 <= args.decoder_length <= 7,
         'Declared bounded word lengths are zero through seven')
    a = algebra()
    c1, c3, q = a.gen(2), a.gen(3), a.gen(1)
    need(a.mul(c1, c1) == a.one and a.mul(c3, c3) == a.one,
         'Code involutions')
    need(a.mul(q, q, q, q) == a.one, 'Actual Gaussian fourth power')
    need(a.mul(c1, a.D(0), q) == a.mul(a.D(0), q, c1),
         'Own full-Gaussian commutator')
    need(a.mul(c1, a.D(0)) != a.mul(a.D(0), c1),
         'Own partial-Gaussian noncommutation')
    controls = words(args.decoder_length)
    # The Q^2 factor is a physically free Pauli, required to turn Q^-1
    # response2 into Q response2 before the second transverse query.
    controls += [reduce_word(w + (1, 1)) for w in words(args.decoder_length)]
    controls = list(dict.fromkeys(controls))
    coefficients = [F(value) for value in args.coefficients.split(',')]
    need(len(coefficients) == len(set(coefficients)) and all(coefficients),
         'Distinct nonzero feedback coefficients')
    choices = [(None, F(0))] + [(word, coefficient)
               for word in words(args.length) for coefficient in coefficients]
    cases, best, histogram = [], 0, Counter()
    for v1, coefficient1 in choices:
        op1 = {} if v1 is None else a.term(v1, (0, 0))
        fixed, targets, _ = replay(a, op1, {}, coefficient1, 0)
        third_index = next(i for i, (label, _) in enumerate(fixed) if label == 'response4')
        before_third = fixed[:third_index]
        base = Span(a, controls)
        for label, row in before_third:
            base.add(label, row)
        for v2, coefficient2 in choices:
            op2 = {} if v2 is None else a.term(v2 + (1, 1), (0, 0))
            observed, targets, _ = replay(a, op1, op2, coefficient1, coefficient2)
            response4 = observed[third_index]
            need(response4[0] == 'response4', 'Last paid response index')
            bounded = before_third + [response4]
            candidate = base.clone()
            candidate.add(*response4)
            result = candidate.test(targets, args.certificates)
            if args.certificates:
                for target, answer in zip(targets, result['results']):
                    verify_answer(a, bounded, target, controls, answer)
            score = sum(entry['attained'] for entry in result['results'])
            histogram[str(score)] += 1
            row = {'feedback1': v1, 'feedback2_before_Pauli': v2,
                   'coefficient1': str(coefficient1), 'coefficient2': str(coefficient2),
                   'attained': [entry['attained'] for entry in result['results']],
                   'basis_dimension': result['dimension']}
            if score > best:
                best = score
                print(json.dumps({'new_best': row}), flush=True)
            if score >= 2 or args.certificates:
                row['recipes'] = result['results']
            cases.append(row)
    receipt = {'status': 'FINITE_FORMAL_FEEDBACK_SEARCH',
               'feedback_length': args.length, 'decoder_length': args.decoder_length,
               'decoder_controls': [list(word) for word in controls],
               'feedback1_source': 'saved_FULL1_Y',
               'feedback2_source': 'modified_response2',
               'feedback2_Pauli': 'Q^2 before the code word',
               'original_query_input_coefficients': ['1', '1'],
               'coefficients': [str(v) for v in coefficients], 'cases': cases,
               'attainment_histogram': dict(sorted(histogram.items())),
               'maximum_attained_jobs': best,
               'physical_emission': False, 'new_kappa': None}
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: value for key, value in receipt.items() if key != 'cases'}))


if __name__ == '__main__':
    main()

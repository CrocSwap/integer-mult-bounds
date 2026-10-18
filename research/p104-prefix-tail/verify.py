"""Exact P104 tail-prefix certificates; no search or predecessor imports.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
The shared-space/minimum-rank reduction is credited to PR2345.
"""
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location('p104_tail_trace', HERE / 'trace.py')
trace = module_from_spec(SPEC)
SPEC.loader.exec_module(trace)
need = trace.need


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def rank(rows):
    """Exact rational Gauss-Jordan elimination."""
    matrix = [list(map(Q, row)) for row in rows]
    if not matrix:
        return 0
    width, pivot_row = len(matrix[0]), 0
    need(all(len(row) == width for row in matrix), 'rectangular rank input')
    for column in range(width):
        pivot = next((i for i in range(pivot_row, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[pivot], matrix[pivot_row] = matrix[pivot_row], matrix[pivot]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [x / divisor for x in matrix[pivot_row]]
        for i, row in enumerate(matrix):
            if i != pivot_row and row[column]:
                coefficient = row[column]
                matrix[i] = [x - coefficient * y for x, y in zip(row, matrix[pivot_row])]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def validate_certificate(certificate):
    need(set(certificate) == {'schema', 'upper_witnesses', 'lower_vectors'} and
         certificate['schema'] == 'p104-prefix-tail/1', 'certificate schema')
    witnesses = certificate['upper_witnesses']
    need([(x['cut'], x['minimum']) for x in witnesses] == [(2646, 99), (2754, 98)],
         'upper interval coverage')
    wanted = []
    for item in witnesses:
        seen = set()
        for term in item['terms']:
            need(isinstance(term, list) and len(term) == 4, 'contact shape')
            target, cut, register, weight = term
            need(type(target) is int and 0 <= target < 104, 'contact target')
            need(type(cut) is int and 0 <= cut <= item['cut'], 'future contact')
            need(isinstance(register, str) and isinstance(weight, str) and Q(weight) != 0,
                 'contact register or rational weight')
            key = (target, cut, register)
            need(key not in seen, 'duplicate contact')
            seen.add(key)
            wanted.append(key)
    vectors = certificate['lower_vectors']
    need(set(vectors) == {'p', 'q', 'w', 'a', 'b', 'k'}, 'lower vector names')
    for row in vectors.values():
        need(len(row) == 8 and all(type(x) is int for x in row), 'integer 8-vector')
    return wanted


def check_lower(pools, ports, vectors, three):
    p, q, w = (vectors[x] for x in ('p', 'q', 'w'))
    a, b, k = (vectors[x] for x in ('a', 'b', 'k'))
    pairs = [(p, a), (p, b), (q, a)]
    if three:
        pairs += [(p, k), (q, k), (w, k)]
    checks = 0
    for target, pool in enumerate(pools):
        for coefficient in pool:
            for left, right in pairs:
                need(dot(left, ports[target]) * dot(coefficient, right) == 0,
                     'annihilator is violated by an eligible snapshot')
                checks += 1
    # These exact entries force a nonsingular compression for EVERY I-M.
    need(dot(p, a) == 0 and dot(p, b) == -1 and dot(q, a) == -1,
         'fixed nonzero two-dimensional compression')
    determinant = -1
    if three:
        need(dot(p, k) == dot(q, k) == 0 and dot(w, k) == 2,
             'fixed nonzero third compression entry')
        determinant = -2
    return dict(minimum_dimension=99 if three else 98,
                compression_rank=3 if three else 2, determinant=determinant,
                generator_pair_checks=checks)


def check_upper(item, collected):
    ports, contacts = collected['ports'], collected['contacts']
    a = [[Q(0)] * 8 for _ in ports]
    for target, cut, register, weight in item['terms']:
        key = target, cut, register
        need(key in contacts, 'unavailable upper contact')
        a[target] = [x + Q(weight) * y for x, y in zip(a[target], contacts[key])]
    residual = [[Q(i == j) - sum(ports[t][i] * a[t][j] for t in range(104))
                 for j in range(8)] for i in range(8)]
    small_rank = rank(residual)
    if item['cut'] == 2754:
        u, v = [0, 0, -1, 1, 0, 0, 0, 1], [0, -1, 0, 0, 0, 0, 0, 0]
        alpha, beta = [0, 1, 0, 0, 0, 0, 0, 2], [0, 0, 1, 0, 0, 0, 0, 0]
        explicit = [[u[i] * alpha[j] + v[i] * beta[j] for j in range(8)] for i in range(8)]
        need(residual == explicit, 'explicit rank-two residual differs')
    correction = [[Q(t == s) - Q(dot(ports[t], ports[s]), 8) +
                   12 * dot(a[t], ports[s]) for s in range(104)] for t in range(104)]
    large_rank = rank(correction)
    need(large_rank == 96 + small_rank == item['minimum'], 'upper correction rank')
    return dict(cut=item['cut'], contacts=len(item['terms']), residual_rank=small_rank,
                full_source_correction_rank=large_rank)


def run(certificate=None, collected=None):
    certificate = trace.read(HERE / 'WITNESS.json') if certificate is None else certificate
    wanted = validate_certificate(certificate)
    collected = trace.collect([2753, 2823], wanted) if collected is None else collected
    need(not collected['receipt']['input_overrides'], 'acceptance requires pinned inputs')
    lower99 = check_lower(collected['pools'][2753], collected['ports'], certificate['lower_vectors'], True)
    lower98 = check_lower(collected['pools'][2823], collected['ports'], certificate['lower_vectors'], False)
    upper = [check_upper(item, collected) for item in certificate['upper_witnesses']]
    return dict(schema='p104-prefix-tail-result/1', status='PASS_P104_PREFIX_TAIL',
                intervals=[dict(start=2718, end=2753, minimum=99),
                           dict(start=2754, end=2823, minimum=98)],
                lower_certificates={'2753': lower99, '2823': lower98},
                upper_certificates=upper, trace=collected['receipt'],
                scope='Rational unchanged-trace pooled availability; no chronological or paid-cost claim.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    need(args.out is None or not args.out.exists(), 'output already exists')
    result = run()
    need(result == trace.read(HERE / 'RESULT.json'), 'exact receipt mismatch')
    if args.out:
        with args.out.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write('\n')
    print(result['status'], '99 through2753; 98 from2754 through2823')


if __name__ == '__main__':
    main()

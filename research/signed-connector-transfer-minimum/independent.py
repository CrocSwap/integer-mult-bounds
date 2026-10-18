#!/usr/bin/env python3
"""Separate integer block-matrix and tape oracle; imports no other package code.
Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
This is implementation independence, not independent human review.
"""
from collections import Counter
import argparse
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
M = ((1, 1, 1), (1, 1, -1), (1, -1, 0))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def execute(word, matrices, L, initial=None):
    rows = identity(11*L) if initial is None else [x[:] for x in initial]
    peak = max(sum(abs(x) for x in row) for row in rows)
    for kind, operator, sign, src, dst in word:
        need(0 <= src < 11 and 0 <= dst < 11 and src != dst, 'distinct physical rows')
        block = matrices[operator] if kind == 'F' else [[operator*int(i == j) for j in range(L)] for i in range(L)]
        need(kind in ('F', 'R'), 'primitive kind')
        for i in range(L):
            for j in range(L):
                coefficient = sign * block[i][j]
                if coefficient:
                    target = rows[dst*L+i]
                    source = rows[src*L+j]
                    rows[dst*L+i] = [x+coefficient*y for x, y in zip(target, source)]
                    peak = max(peak, sum(abs(x) for x in rows[dst*L+i]))
    return rows, peak


def target_matrix(matrices, L):
    # Independently form each whole operator by dense multiplication in
    # application order; no echo tree is used in this reference.
    lengths = (2, 3, 4, 5, 6, 7)
    operators = []
    start = 0
    for length in lengths:
        product = identity(L)
        for factor in matrices[start:start+length]:
            product = multiply(factor, product)
        operators.append(product)
        start += length
    answer = identity(11*L)
    for i in range(3):
        for j in range(3):
            product = multiply(operators[3+i], operators[j])
            for a in range(L):
                for b in range(L):
                    answer[(3+i)*L+a][j*L+b] += M[i][j]*product[a][b]
    return answer


def tape(word, L):
    bill = Counter()
    for kind, operator, sign, src, dst in word:
        head = 0
        def visit(cell):
            nonlocal head
            bill['head_moves'] += abs(cell-head)
            head = cell
        if kind == 'F':
            for a in range(L):
                for b in range(L):
                    visit(11*L + operator*L*L + a*L+b)
                    bill['coefficient_reads'] += 1
                    visit(src*L+b)
                    visit(dst*L+a)
                    bill['source_reads'] += 1
                    bill['target_read_writes'] += 1
                    bill['multiplications'] += 1
                    bill['additions'] += 1
                    bill['work_clears'] += 1
                    if sign == -1:
                        bill['negations'] += 1
        else:
            for a in range(L):
                visit(src*L+a)
                visit(dst*L+a)
                bill['source_reads'] += 1
                bill['target_read_writes'] += 1
                bill['additions'] += 1
                bill['work_clears'] += 1
                if operator*sign < 0:
                    bill['negations'] += 1
                if abs(operator) == 2:
                    bill['doublings'] += 1
        visit(0)
        bill['instructions'] += 1
    return dict(sorted(bill.items()))


def independent_paths():
    # DFS forces the second occurrence opposite to the first, unlike the
    # primary check's permutation of six pre-labelled signed moves.
    histogram = Counter()
    def visit(counts, first, current, seen):
        if sum(counts) == 6:
            available = {tuple(x-y for x, y in zip(a, b)) for a in seen for b in seen}
            mask = sum(2**i for i, row in enumerate(M) if row in available)
            histogram[mask] += 1
            return
        for j in range(3):
            if counts[j] == 2:
                continue
            choices = (-1, 1) if counts[j] == 0 else (-first[j],)
            for sign in choices:
                count2, first2, point = counts[:], first[:], list(current)
                count2[j] += 1
                if counts[j] == 0:
                    first2[j] = sign
                point[j] += sign
                visit(count2, first2, tuple(point), seen+[tuple(point)])
    visit([0]*3, [0]*3, (0, 0, 0), [(0, 0, 0)])
    return dict(sorted(histogram.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', action='store_true', help='explicitly write the independent expected receipt')
    args = ap.parse_args()
    cert = json.loads((HERE/'CERTIFICATE.json').read_text())
    need(cert['target'] == [list(x) for x in M], 'declared target')
    census = {int(k): v for k, v in cert['one_root_census']['cover_masks'].items()}
    need(independent_paths() == {k:v for k,v in census.items() if v}, 'independent one-root census')
    words = [cert['expanded_word'], cert['predecessor_expanded_word']]
    for word, expected_length in zip(words, (304, 306)):
        need(len(word) == expected_length, 'complete primitive bill')
        need(sum(x[0] == 'F' for x in word) == 300, 'factor bill')
    rng = random.Random(32)
    columns = dense_cases = noncommuting = 0
    peaks = []
    for L in (1, 2, 3, 4):
        for fixture in range(3):
            matrices = [[[rng.randrange(-2, 3) for _ in range(L)] for _ in range(L)] for _ in range(27)]
            expected = target_matrix(matrices, L)
            noncommuting += multiply(matrices[0], matrices[-1]) != multiply(matrices[-1], matrices[0])
            for word in words:
                state, peak = execute(word, matrices, L)
                need(state == expected, 'direct matrix product disagrees')
                reverse = [(k, o, -s, src, dst) for k, o, s, src, dst in reversed(word)]
                restored, reverse_peak = execute(reverse, matrices, L, state)
                need(restored == identity(11*L), 'inverse does not restore every basis input')
                peaks.append([L, fixture, len(word), peak, reverse_peak])
                columns += 11*L
                dense_cases += 1
    need(noncommuting >= 8, 'noncommuting controls')
    # An order reversal is invisible on scalar fixtures but must fail here.
    matrices = [[[rng.randrange(-2, 3) for _ in range(2)] for _ in range(2)] for _ in range(27)]
    bad = [x[:] for x in words[0]]
    for event in bad:
        if event[0] == 'F' and event[1] in (0, 1):
            event[1] = 1-event[1]
    need(execute(bad, matrices, 2)[0] != target_matrix(matrices, 2), 'noncommuting factor-order mutation')
    # Missing a complete scratch-restoration child must be observable on
    # arbitrary scratch columns, not only on clean input rows.
    bad = words[0][:]
    bad.pop(next(i for i, e in enumerate(bad) if e[0] == 'F' and e[4] >= 8))
    need(execute(bad, matrices, 2)[0] != target_matrix(matrices, 2), 'dirty scratch mutation')
    tape_cases = []
    for L in (1, 2, 3, 4, 8, 16):
        bills = [tape(word, L) for word in words]
        for bill, name in zip(bills, ('candidate', 'predecessor')):
            polynomial = cert[name]['head_moves_coefficients_L0_through_L4']
            need(bill['head_moves'] == sum(c*L**i for i, c in enumerate(polynomial)), 'literal tape vs polynomial')
        need(bills[1]['head_moves'] - bills[0]['head_moves'] == 24*L**3+4*L**2+20*L-4, 'changed-port head saving')
        need(bills[1]['source_reads']-bills[0]['source_reads'] == 2*L, 'source reads paid')
        need(bills[1]['target_read_writes']-bills[0]['target_read_writes'] == 2*L, 'target updates paid')
        need(bills[1]['doublings'] == 2*L and bills[0].get('doublings', 0) == 0, 'root doubling bill')
        tape_cases.append({'L': L, 'candidate': bills[0], 'predecessor': bills[1]})
    report = {'dense_cases': dense_cases, 'basis_columns_per_direction': columns,
              'noncommuting_fixtures': noncommuting, 'peaks': peaks, 'tape': tape_cases,
              'controls': ['factor-order', 'scratch-restoration'], 'one_root_paths': 720}
    expected_path = HERE / 'INDEPENDENT.json'
    if args.record:
        expected_path.write_text(json.dumps(report, indent=2) + '\n')
    need(report == json.loads(expected_path.read_text()), 'independent full receipt equality')
    print('PASS_INDEPENDENT_MATRIX_TAPE dense_cases=' + str(dense_cases) + ' basis_columns_per_direction=' + str(columns) + ' tape_lengths=6 controls=2')


if __name__ == '__main__':
    main()

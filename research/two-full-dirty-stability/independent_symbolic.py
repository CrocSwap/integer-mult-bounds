#!/usr/bin/env python3
"""Independent exact free-word expansion for dirty-identity stabilization.

Standard library only. The default command writes no files and prints a
JSON receipt. This checks polynomial identities, not the all-width theorem,
actual Clifford grades, a physical native caller, or scientific acceptance.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def one():
    return {(): 1}


def letter(name):
    return {(name,): 1}


def plus(*polynomials):
    result = {}
    for polynomial in polynomials:
        for word, coefficient in polynomial.items():
            result[word] = result.get(word, 0) + coefficient
            if not result[word]:
                del result[word]
    return result


def times(*polynomials):
    result = one()
    for polynomial in polynomials:
        new = {}
        for left, a in result.items():
            for right, b in polynomial.items():
                word = left + right
                new[word] = new.get(word, 0) + a*b
        result = {word: a for word, a in new.items() if a}
    return result


def zeros(n):
    return [[{} for _ in range(n)] for _ in range(n)]


def identity(n):
    result = zeros(n)
    for i in range(n):
        result[i][i] = one()
    return result


def multiply(a, b):
    n = len(a)
    return [[plus(*(times(a[i][k], b[k][j]) for k in range(n)))
             for j in range(n)] for i in range(n)]


def remove_symbols(polynomial, removed):
    return {word: a for word, a in polynomial.items()
            if not any(symbol in removed for symbol in word)}


def remove_from_matrix(matrix, removed):
    return [[remove_symbols(p, removed) for p in row] for row in matrix]


def native(stage, direction, n):
    diagonal = identity(n)
    for i in range(2):
        diagonal[i][i] = letter(f'D{stage}_{i}')
    shear = identity(n)
    destination, source = (0, 1) if direction == 'upper' else (1, 0)
    shear[destination][source] = letter('a' if stage == 1 else 'b')
    return multiply(diagonal, shear)


def fixture(first, second, scratch):
    n = scratch + 2
    w = [[letter(f'w_{i}_{j}') for j in range(n)] for i in range(n)]
    t1 = native(1, first, n)
    t2 = native(2, second, n)
    body = multiply(multiply(t2, w), t1)
    # Untouched column of the first shear; untouched row of the second.
    c = 0 if first == 'upper' else 1
    r = 1 if second == 'upper' else 0
    j = 1-c
    i = 1-r
    row_checks = column_checks = 0
    for z in range(2, n):
        first_row = times(letter(f'D2_{r}'), letter(f'w_{r}_{z}'))
        need(body[r][z] == first_row, 'Untouched main-to-scratch row')
        second_row = plus(
            times(letter(f'D2_{i}'), letter(f'w_{i}_{z}')),
            times(letter(f'D2_{i}'), letter('b'), letter(f'w_{r}_{z}')))
        need(body[i][z] == second_row, 'Other main-to-scratch row')
        need(remove_symbols(body[i][z], {f'w_{r}_{z}'}) ==
             times(letter(f'D2_{i}'), letter(f'w_{i}_{z}')),
             'First cross-row zero makes second row pure')
        first_column = times(letter(f'w_{z}_{c}'), letter(f'D1_{c}'))
        need(body[z][c] == first_column, 'Untouched scratch-to-main column')
        second_column = plus(
            times(letter(f'w_{z}_{j}'), letter(f'D1_{j}')),
            times(letter(f'w_{z}_{c}'), letter(f'D1_{c}'), letter('a')))
        need(body[z][j] == second_column, 'Other scratch-to-main column')
        need(remove_symbols(body[z][j], {f'w_{z}_{c}'}) ==
             times(letter(f'w_{z}_{j}'), letter(f'D1_{j}')),
             'First cross-column zero makes second column pure')
        row_checks += 3
        column_checks += 3
    removed = {f'w_{i}_{j}' for i in range(n) for j in range(n)
               if (i < 2) != (j < 2)}
    reduced = remove_from_matrix(body, removed)
    for z in range(2, n):
        for h in range(2):
            need(not reduced[h][z] and not reduced[z][h],
                 'All body cross blocks vanish')
        for z2 in range(2, n):
            need(reduced[z][z2] == w[z][z2], 'Scratch block exactly Wss')
    mm = [row[:2] for row in w[:2]]
    expected_main = multiply(multiply(native(2, second, 2), mm),
                             native(1, first, 2))
    need([row[:2] for row in reduced[:2]] == expected_main,
         'Main block is the original two-owner body')
    corner = times(letter(f'D2_{r}'), letter(f'w_{r}_{c}'),
                   letter(f'D1_{c}'))
    need(reduced[r][c] == corner, 'Pure untouched main corner')
    other = remove_symbols(reduced[i][c], {f'w_{r}_{c}'})
    need(other == times(letter(f'D2_{i}'), letter(f'w_{i}_{c}'),
                        letter(f'D1_{c}')),
         'Zero first corner makes other entry of input column pure')
    zero_column = remove_from_matrix(reduced, {f'w_{r}_{c}', f'w_{i}_{c}'})
    need(not zero_column[0][c] and not zero_column[1][c],
         'Both inferred W zeros remove whole main input column')
    # A checker must not silently commute a query past a transverse factor.
    wrong_order = times(letter('b'), letter(f'D2_{i}'),
                        letter(f'w_{r}_2'))
    actual_order = times(letter(f'D2_{i}'), letter('b'),
                         letter(f'w_{r}_2'))
    need(wrong_order != actual_order, 'Noncommuting order control')
    need(bool(remove_symbols(body[i][2], {f'w_{r}_2'})),
         'Killing only first cross row leaves another nonzero cross entry')
    return {
        'first_orientation': first,
        'second_orientation': second,
        'scratch_owners': scratch,
        'untouched_first_column': c,
        'untouched_second_row': r,
        'cross_row_identities': row_checks,
        'cross_column_identities': column_checks,
        'block_diagonal_reduction': True,
        'scratch_block_preserved_exactly': True,
        'untouched_main_column_identities': 3,
        'noncommuting_order_control': True,
        'incomplete_cross_zero_control': True,
    }


def main():
    fixtures = [fixture(first, second, s)
                for first in ('upper', 'lower')
                for second in ('upper', 'lower')
                for s in (1, 2, 3)]
    receipt = {
        'status': 'PASS_INDEPENDENT_FREEWORD_DIRTY_IDENTITY_BLOCK_EXPANSION',
        'arithmetic': 'Exact integer-coefficient noncommutative free words',
        'fixtures': fixtures,
        'fixture_count': len(fixtures),
        'cross_row_identities': sum(x['cross_row_identities'] for x in fixtures),
        'cross_column_identities': sum(x['cross_column_identities'] for x in fixtures),
        'untouched_main_column_identities': 36,
        'runtime_file_writes': 0,
        'imports_other_checkers': False,
        'scope': ('Finite corroboration of block expansion and zero substitutions. '
                  'The universal grade projection, B-to-A rank argument and all-width '
                  'faithfulness are written proof obligations, not established by this fixture.'),
    }
    # Publication adapter: compare the unchanged independent mathematical receipt.
    expected=json.loads(Path(__file__).with_name("INDEPENDENT-SYMBOLIC.json").read_text())
    need(receipt == expected, "Committed independent receipt equality")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Independent dense-query multipair free-word corroboration.

Default execution is read-only and compares the mathematical receipt with
MULTIPAIR.json. --write is the explicit authoring path. Standard library
only; imports no other checker. This finite polynomial check does not prove
Clifford grade facts, tensor faithfulness, native admission or a new kappa.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unit():
    return {(): 1}


def atom(name):
    return {(name,): 1}


def add(*polys):
    out = {}
    for p in polys:
        for w, v in p.items():
            out[w] = out.get(w, 0) + v
            if not out[w]:
                del out[w]
    return out


def product(*polys):
    out = unit()
    for p in polys:
        nxt = {}
        for a, x in out.items():
            for b, y in p.items():
                w = a+b
                nxt[w] = nxt.get(w, 0)+x*y
        out = {w: v for w, v in nxt.items() if v}
    return out


def empty(n):
    return [[{} for _ in range(n)] for _ in range(n)]


def eye(n):
    out = empty(n)
    for i in range(n):
        out[i][i] = unit()
    return out


def matmul(a, b):
    n = len(a)
    return [[add(*(product(a[i][k], b[k][j]) for k in range(n)))
             for j in range(n)] for i in range(n)]


def without(p, removed):
    return {w: a for w, a in p.items() if not any(v in removed for v in w)}


def substitute_zero(a, removed):
    return [[without(p, removed) for p in row] for row in a]


def sets(m, orientation):
    low = tuple(range(m))
    high = tuple(range(m, 2*m))
    return (low, high) if orientation == 'upper' else (high, low)


def full(stage, m, scratch, orientation):
    n = 2*m+scratch
    d = eye(n)
    for i in range(2*m):
        d[i][i] = atom(f'D{stage}_{i}')
    e = eye(n)
    dest, source = sets(m, orientation)
    for i in dest:
        for j in source:
            e[i][j] = atom(f'Q{stage}_{i}_{j}')
    return matmul(d, e)


def fixture(m, scratch, first, second):
    n = 2*m+scratch
    main = tuple(range(2*m))
    work = tuple(range(2*m, n))
    cset, jset = sets(m, first)       # untouched input columns; other columns
    iset, rset = sets(m, second)      # affected output rows; untouched rows
    w = [[atom(f'w_{i}_{j}') for j in range(n)] for i in range(n)]
    t1 = full(1, m, scratch, first)
    t2 = full(2, m, scratch, second)
    body = matmul(matmul(t2, w), t1)
    cross_initial = cross_reduced = 0
    for z in work:
        for r in rset:
            need(body[r][z] == product(atom(f'D2_{r}'), atom(f'w_{r}_{z}')),
                 'Untouched multipair main-to-scratch row')
            cross_initial += 1
        for i in iset:
            expected = product(atom(f'D2_{i}'), add(
                atom(f'w_{i}_{z}'),
                *(product(atom(f'Q2_{i}_{r}'), atom(f'w_{r}_{z}')) for r in rset)))
            need(body[i][z] == expected, 'Affected dense-query main-to-scratch row')
            removed = {f'w_{r}_{z}' for r in rset}
            need(without(body[i][z], removed) ==
                 product(atom(f'D2_{i}'), atom(f'w_{i}_{z}')),
                 'All untouched cross rows zero imply affected row pure')
            cross_initial += 1
            cross_reduced += 1
        for c in cset:
            need(body[z][c] == product(atom(f'w_{z}_{c}'), atom(f'D1_{c}')),
                 'Untouched multipair scratch-to-main column')
            cross_initial += 1
        for j in jset:
            expected = add(
                product(atom(f'w_{z}_{j}'), atom(f'D1_{j}')),
                *(product(atom(f'w_{z}_{c}'), atom(f'D1_{c}'),
                          atom(f'Q1_{c}_{j}')) for c in cset))
            need(body[z][j] == expected, 'Affected dense-query scratch-to-main column')
            removed = {f'w_{z}_{c}' for c in cset}
            need(without(body[z][j], removed) ==
                 product(atom(f'w_{z}_{j}'), atom(f'D1_{j}')),
                 'All untouched cross columns zero imply other column pure')
            cross_initial += 1
            cross_reduced += 1
    cross_zero = {f'w_{i}_{j}' for i in range(n) for j in range(n)
                  if (i in main) != (j in main)}
    reduced = substitute_zero(body, cross_zero)
    for z in work:
        for i in main:
            need(not reduced[i][z] and not reduced[z][i], 'Whole cross blocks zero')
        for z2 in work:
            need(reduced[z][z2] == w[z][z2], 'Exact unchanged Ws block')
    expected_main = matmul(matmul(full(2, m, 0, second),
                                  [row[:2*m] for row in w[:2*m]]),
                           full(1, m, 0, first))
    need([row[:2*m] for row in reduced[:2*m]] == expected_main,
         'Main block equals native multipair body')
    for r in rset:
        for c in cset:
            pure = product(atom(f'D2_{r}'), atom(f'w_{r}_{c}'), atom(f'D1_{c}'))
            need(reduced[r][c] == pure, 'Whole untouched m-by-m corner pure')
    corner_zero = {f'w_{r}_{c}' for r in rset for c in cset}
    corner_reduced = substitute_zero(reduced, corner_zero)
    for i in iset:
        for c in cset:
            pure = product(atom(f'D2_{i}'), atom(f'w_{i}_{c}'), atom(f'D1_{c}'))
            need(corner_reduced[i][c] == pure,
                 'Other m rows in same m columns pure after corner zero')
    full_column_zero = corner_zero | {f'w_{i}_{c}' for i in iset for c in cset}
    final = substitute_zero(reduced, full_column_zero)
    final_w = substitute_zero(w, cross_zero | full_column_zero)
    for c in cset:
        need(all(not final[i][c] for i in range(n)), 'Whole body m columns zero')
        need(all(not final_w[i][c] for i in range(n)), 'Whole W m columns zero')
    # Dense Q is genuine: every one of its m*m unrelated letters occurs.
    q_letters = {symbol for row in t1+t2 for p in row for word in p for symbol in word
                 if symbol.startswith('Q')}
    need(len(q_letters) == 2*m*m, 'All independent dense query letters present')
    # Preserve order instead of commuting Q through rank-eight factors.
    i, r, c = iset[0], rset[0], cset[0]
    ordered = product(atom(f'D2_{i}'), atom(f'Q2_{i}_{r}'),
                      atom(f'w_{r}_{c}'), atom(f'D1_{c}'))
    wrong = product(atom(f'Q2_{i}_{r}'), atom(f'D2_{i}'),
                    atom(f'w_{r}_{c}'), atom(f'D1_{c}'))
    need(ordered != wrong, 'Noncommuting D/query order control')
    # Leave exactly one untouched-corner entry nonzero: its query term remains.
    almost = corner_zero - {f'w_{r}_{c}'}
    need(next(iter(ordered)) in without(reduced[i][c], almost),
         'Incomplete corner-zero control')
    return {
        'pairs': m,
        'scratch': scratch,
        'first_orientation': first,
        'second_orientation': second,
        'dense_query_letters': len(q_letters),
        'initial_cross_formulas': cross_initial,
        'reduced_cross_formulas': cross_reduced,
        'untouched_main_corner_formulas': m*m,
        'remaining_main_column_formulas': m*m,
        'whole_W_columns_forced_zero': m,
        'exact_block_diagonal_reduction': True,
        'scratch_block_unchanged': True,
        'noncommuting_order_control': True,
        'incomplete_corner_zero_control': True,
    }


def report():
    fixtures = [fixture(m, s, a, b) for m in (1, 2, 3) for s in (0, 1, 2)
                for a in ('upper', 'lower') for b in ('upper', 'lower')]
    return {
        'status': 'PASS_INDEPENDENT_DENSE_MULTIPAIR_FREEWORD_EXPANSION',
        'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic': 'Exact integer-coefficient noncommutative free words',
        'imports_other_checker': False,
        'fixture_count': len(fixtures),
        'fixtures': fixtures,
        'scope': ('Finite polynomial corroboration for m=1,2,3 and s=0,1,2. '
                  'The written proof supplies arbitrary-m/s quantifiers, Clifford grade '
                  'invariance, subgroup rank and all-width faithfulness. No physical '
                  'native endpoint, retained-helper theorem or kappa is established.'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Author the frozen receipt')
    args = parser.parse_args()
    result = report()
    path = Path(__file__).with_name('MULTIPAIR.json')
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(path.is_file(), 'Missing frozen MULTIPAIR.json; use --write only for authoring')
        need(json.loads(path.read_text()) == result, 'Frozen multipair receipt mismatch')
    print(json.dumps({k: v for k, v in result.items() if k != 'fixtures'},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

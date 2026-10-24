"""Exact finite corroboration of the extension-field UT3 rank proof.

Produced by Nick Petalas. Apache-2.0.
No predecessor implementation is imported. Normal execution is read-only.
"""

import hashlib
import itertools
import json
from pathlib import Path
import sys


MUL = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
INV = (0, 1, 3, 2)
PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def group(a, b):
    x, y, z = a % 4, (a // 4) % 4, a // 16
    xx, yy, zz = b % 4, (b // 4) % 4, b // 16
    return (x ^ xx) + 4 * (y ^ yy) + 16 * (z ^ zz ^ MUL[x][yy])


def phi(a):
    x, y, z = a % 4, (a // 4) % 4, a // 16
    return (1, x, y, z, z ^ MUL[x][y])


def algebra(a, b):
    out = [0] * 5
    for i in range(5):
        out[i] = MUL[a[0]][b[i]] ^ MUL[a[i]][b[0]]
    out[0] = MUL[a[0]][b[0]]
    out[3] ^= MUL[a[1]][b[2]]
    out[4] ^= MUL[a[2]][b[1]]
    return tuple(out)


def rank(matrix):
    if not matrix:
        return 0
    a = [list(row) for row in matrix]
    rows, cols, pivot = len(a), len(a[0]), 0
    need(rows <= 10 and cols <= 10, 'rank domain exceeded')
    need(all(len(row) == cols for row in a), 'ragged matrix')
    for col in range(cols):
        candidates = [j for j in range(pivot, rows) if a[j][col]]
        if not candidates:
            continue
        j = candidates[0]
        a[pivot], a[j] = a[j], a[pivot]
        scale = INV[a[pivot][col]]
        a[pivot] = [MUL[scale][v] for v in a[pivot]]
        for j in range(rows):
            if j != pivot and a[j][col]:
                scale = a[j][col]
                a[j] = [v ^ MUL[scale][w] for v, w in zip(a[j], a[pivot])]
        pivot += 1
        if pivot == rows:
            break
    return pivot


def zero(r):
    return tuple((0,) * r for _ in range(r))


def add(a, b):
    return tuple(tuple(x ^ y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def outer(u, v, coefficient, r):
    return tuple(tuple(coefficient if (u >> i) & (v >> j) & 1 else 0
                       for j in range(r)) for i in range(r))


def right_rank_one(a, u, v, coefficient, r):
    column = [0] * r
    for i in range(r):
        for j in range(r):
            if (u >> j) & 1:
                column[i] ^= a[i][j]
    return tuple(tuple(MUL[column[i]][coefficient] if (v >> j) & 1 else 0
                       for j in range(r)) for i in range(r))


def validate(call, r):
    kind, coefficient, u, v = call
    need(1 <= r <= 5, 'role domain exceeded')
    need(kind in (0, 1), 'non-axis label')
    need(coefficient in (1, 2, 3), 'zero or invalid label coefficient')
    need(0 < u < 2**r and 0 < v < 2**r, 'non-rank-one call')


def quotient_step(state, call, r):
    validate(call, r)
    kind, coefficient, u, v = call
    a, b, c, d = state
    n = outer(u, v, coefficient, r)
    if kind == 0:
        return add(a, n), b, c, add(d, right_rank_one(b, u, v, coefficient, r))
    return a, add(b, n), add(c, right_rank_one(a, u, v, coefficient, r)), d


def check_floor(state, nx, ny):
    a, b, c, d = state
    ax = tuple(ar + cr for ar, cr in zip(a, c))
    by = tuple(br + dr for br, dr in zip(b, d))
    lower_x = rank(ax) + rank(a + d) - rank(a)
    lower_y = rank(by) + rank(b + c) - rank(b)
    need(nx >= lower_x and ny >= lower_y, 'extension-field span floor failed')


def identity(r):
    return tuple(tuple(1 if i == j else 0 for j in range(r)) for i in range(r))


def formal_step(word, call, r):
    validate(call, r)
    kind, coefficient, u, v = call
    g = coefficient * (1 if kind == 0 else 4)
    result = [list(row) for row in word]
    for i in range(r):
        p = 0
        for j in range(r):
            if (u >> j) & 1:
                p ^= word[i][j]
        translated = 0
        for h in range(64):
            if (p >> h) & 1:
                translated ^= 1 << group(h, g)
        for j in range(r):
            if (v >> j) & 1:
                result[i][j] ^= p ^ translated
    return tuple(tuple(row) for row in result)


def formal_quotient(word, r):
    out = [[[0] * r for _ in range(r)] for _ in range(5)]
    for i in range(r):
        for j in range(r):
            for h in range(64):
                if (word[i][j] >> h) & 1:
                    for k, value in enumerate(phi(h)):
                        out[k][i][j] ^= value
    need(tuple(map(tuple, out[0])) == identity(r), 'augmentation changed')
    return tuple(tuple(map(tuple, matrix)) for matrix in out[1:])


def execute(calls, r):
    need(len(calls) <= 32, 'word domain exceeded')
    state, word = (zero(r),) * 4, identity(r)
    nx = ny = 0
    for call in calls:
        state = quotient_step(state, call, r)
        word = formal_step(word, call, r)
        nx += call[0] == 0
        ny += call[0] == 1
    need(state == formal_quotient(word, r), 'formal/quotient disagreement')
    check_floor(state, nx, ny)
    return word, state


def witness(parameters):
    calls = []
    for i, z in enumerate(parameters):
        calls.extend(((0, z, 1 << i, 1 << i), (1, 1, 1 << i, 1 << i)) * 2)
    return tuple(calls)


def target(parameters, r):
    return tuple(tuple((1 << (16 * parameters[i]) if i < len(parameters) else 1)
                       if i == j else 0 for j in range(r)) for i in range(r))


def field_and_homomorphism():
    for a, b in itertools.product(range(4), repeat=2):
        polynomial = (a if b & 1 else 0) ^ ((a << 1) if b & 2 else 0)
        if polynomial & 4:
            polynomial ^= 7
        need(polynomial == MUL[a][b], 'field table differs from polynomial reduction')
    for a, b in itertools.product(range(64), repeat=2):
        need(phi(group(a, b)) == algebra(phi(a), phi(b)), 'quotient is not multiplicative')
    return 16, 4096


def rank_controls():
    count = 0
    for entries in itertools.product(range(4), repeat=4):
        matrix = (entries[:2], entries[2:])
        binary_rows = []
        for i, bit in itertools.product(range(2), repeat=2):
            row = 0
            for j, input_bit in itertools.product(range(2), repeat=2):
                output = MUL[matrix[i][j]][1 << input_bit]
                row |= ((output >> bit) & 1) << (2 * j + input_bit)
            binary_rows.append(row)
        basis, binary_rank = [0] * 4, 0
        for row in binary_rows:
            for pivot in reversed(range(4)):
                if (row >> pivot) & 1:
                    if basis[pivot]:
                        row ^= basis[pivot]
                    else:
                        basis[pivot] = row
                        binary_rank += 1
                        break
        need(binary_rank == 2 * rank(matrix), 'field/binary rank disagreement')
        count += 1
    return count


def short_words():
    factors = tuple(itertools.product(range(2), range(1, 4), range(1, 4), range(1, 4)))
    counts, formal_checks, nilpotent_words = [0] * 4, 0, 0
    for length in range(4):
        for calls in itertools.product(factors, repeat=length):
            state = (zero(2),) * 4
            for call in calls:
                state = quotient_step(state, call, 2)
            nx = sum(call[0] == 0 for call in calls)
            check_floor(state, nx, length - nx)
            if any((u & v).bit_count() % 2 == 0 for _, _, u, v in calls):
                nilpotent_words += 1
            if length <= 2:
                word, full_state = execute(calls, 2)
                need(full_state == state and word is not None, 'full replay failed')
                for source in range(2):
                    need(regular_column(calls, 2, source, 0)
                         == tuple(row[source] for row in word),
                         'literal short-word action differs from formal coefficients')
                formal_checks += 1
            counts[length] += 1
    need(counts == [1, 54, 2916, 157464], 'short-word enumeration incomplete')
    return counts, formal_checks, nilpotent_words


def regular_column(calls, r, source, address):
    """Apply the word to one dirty basis column without formal polynomials."""
    values = [0] * r
    values[source] = 1 << address
    for kind, coefficient, u, v in reversed(calls):
        p = 0
        for j in range(r):
            if (v >> j) & 1:
                p ^= values[j]
        shifted = 0
        for h in range(64):
            if (p >> h) & 1:
                x, y, z = h % 4, (h // 4) % 4, h // 16
                if kind == 0:
                    new = (x ^ coefficient) + 4 * y + 16 * (z ^ MUL[coefficient][y])
                else:
                    new = x + 4 * (y ^ coefficient) + 16 * z
                shifted ^= 1 << new
        for i in range(r):
            if (u >> i) & 1:
                values[i] ^= p ^ shifted
    return tuple(values)


def check_regular_witness(parameters, r):
    count = 0
    for source, address in itertools.product(range(r), range(64)):
        expected = [0] * r
        z = parameters[source] if source < len(parameters) else 0
        expected[source] = 1 << (address ^ (16 * z))
        need(regular_column(witness(parameters), r, source, address) == tuple(expected),
             'literal regular-action endpoint failed')
        count += 1
    return count


def witnesses_and_involutions():
    fixtures = basis_columns = 0
    for w in range(1, 5):
        parameters = tuple(1 + i % 3 for i in range(w))
        for r in (w, w + 1):
            word, state = execute(witness(parameters), r)
            need(word == target(parameters, r), 'full dirty endpoint failed')
            need(state[:2] == (zero(r), zero(r)), 'first-order endpoint is nonzero')
            need(rank(state[2]) == rank(state[3]) == w, 'central rank differs')
            fixtures += 1
            basis_columns += check_regular_witness(parameters, r)
    word, _ = execute(witness((1, 2, 3)), 5)
    need(word == target((1, 2, 3), 5), 'two dirty spectators changed')
    idempotents = nilpotents = 0
    for u, v in itertools.product(range(1, 8), repeat=2):
        if (u & v).bit_count() % 2:
            idempotents += 1
        else:
            nilpotents += 1
        for kind, coefficient in itertools.product(range(2), range(1, 4)):
            call = (kind, coefficient, u, v)
            need(execute((call, call), 3)[0] == identity(3), 'paid call not involutive')
    basis_columns += check_regular_witness((1, 2, 3), 5)
    return fixtures + 1, basis_columns, idempotents, nilpotents


def controls():
    parameters, r = (1, 2, 3), 4
    calls, expected = witness(parameters), target(parameters, r)
    omissions = 0
    for i in range(len(calls)):
        need(execute(calls[:i] + calls[i + 1:], r)[0] != expected, 'omission undetected')
        omissions += 1
    wrong = calls[:-1] + ((1, 2, 4, 4),)
    need(execute(wrong, r)[0] != expected, 'wrong coefficient undetected')
    dirty, _ = execute(calls + ((0, 1, 1, 8),), r)
    need(all(dirty[i][:3] == expected[i][:3] for i in range(r)), 'clean trap is not clean')
    need(dirty != expected, 'dirty restoration not checked')
    # The degree-three augmentation product is nonzero formally, zero in Q.
    kernel = 0
    for choose in itertools.product(range(2), repeat=3):
        h = 0
        for selected, g in zip(choose, (1, 4, 1)):
            if selected:
                h = group(h, g)
        kernel ^= 1 << h
    need(kernel != 0, 'kernel control vanished formally')
    trap = [list(row) for row in identity(2)]
    trap[0][1] ^= kernel
    need(formal_quotient(trap, 2) == (zero(2),) * 4, 'kernel not in quotient kernel')
    need(tuple(map(tuple, trap)) != identity(2), 'quotient used as faithful certificate')
    rejected = 0
    for call in ((2, 1, 1, 1), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 16)):
        try:
            validate(call, r)
        except ValueError:
            rejected += 1
    need(rejected == 4, 'illegal paid alphabet accepted')
    noncentral = quotient_step((zero(1),) * 4, (0, 1, 1, 1), 1)
    need(rank(noncentral[0]) == 1 and 2 * rank(noncentral[0]) > 1,
         'zero-sum hypothesis control failed')
    # Four rank-two calls would implement two central targets, below 4w.
    parallel = ((0, 1, 1, 1), (0, 1, 2, 2),
                (1, 1, 1, 1), (1, 1, 2, 2)) * 2
    need(execute(parallel, 2)[0] == target((1, 1), 2) and rank(identity(2)) == 2,
         'higher-rank exclusion control failed')
    return {'omissions': omissions, 'wrong_coefficient': 1, 'dirty_restore': 1,
            'nonfaithful_quotient': 1, 'invalid_calls': rejected,
            'noncentral_first_order': 1, 'higher_rank_excluded': 1,
            'kernel_support': kernel.bit_count()}


def compute():
    field_products, group_products = field_and_homomorphism()
    words, formal_checks, nilpotent_words = short_words()
    fixtures, columns, idempotents, nilpotents = witnesses_and_involutions()
    result = {
        'claim_type': 'scoped proof with finite corroboration',
        'triple_minimum': 12, 'minimum_X_calls': 6, 'minimum_Y_calls': 6,
        'field_products': field_products, 'group_products': group_products,
        'field_rank_controls': rank_controls(),
        'short_words_by_length': words, 'short_words_with_nilpotents': nilpotent_words,
        'full_short_word_checks': formal_checks, 'regular_short_columns': 2 * formal_checks,
        'full_endpoint_fixtures': fixtures,
        'full_endpoint_basis_columns': columns, 'rank_one_idempotents_r3': idempotents,
        'rank_one_nilpotents_r3': nilpotents, 'involution_checks': 6 * (idempotents + nilpotents),
        'controls': controls(), 'no_new_kappa': True,
    }
    result['source_sha256'] = {
        name: hashlib.sha256(read_small(PACKAGE / name)).hexdigest()
        for name in ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    }
    return result


def read_small(path):
    with path.open('rb') as source:
        raw = source.read(65537)
    need(len(raw) <= 65536, 'oversized package file')
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def main():
    need(sys.argv[1:] in ([], ['--emit']), 'usage: verify.py [--emit]')
    actual = compute()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    raw = read_small(PACKAGE / 'RESULT.json')
    expected = json.loads(raw, object_pairs_hook=unique_object)
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
         'receipt or authenticated source mismatch')
    print('PASS_UT3_F4_NILPOTENT_TARIFF minimum=12 nX=6 nY=6 '
          f'short_words={sum(actual["short_words_by_length"])} '
          f'involutions={actual["involution_checks"]} no_new_kappa')


if __name__ == '__main__':
    main()

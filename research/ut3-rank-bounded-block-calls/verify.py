#!/usr/bin/env python3
"""Exact corroboration of the written rank-cap theorem; no supplier claim.
Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def dense_rank(rows, width):
    """Separate Boolean-array Gaussian elimination."""
    matrix = [[bool(row & (1 << j)) for j in range(width)] for row in rows]
    pivot = 0
    for j in range(width):
        candidate = next((i for i in range(pivot, len(matrix)) if matrix[i][j]), None)
        if candidate is None:
            continue
        matrix[pivot], matrix[candidate] = matrix[candidate], matrix[pivot]
        for i in range(pivot + 1, len(matrix)):
            if matrix[i][j]:
                matrix[i] = [x != y for x, y in zip(matrix[i], matrix[pivot])]
        pivot += 1
    return pivot


def identity(n):
    return tuple(1 << i for i in range(n))


def binary_mul(left, right):
    answer = []
    for row in left:
        value = 0
        while row:
            bit = (row & -row).bit_length() - 1
            value ^= right[bit]
            row &= row - 1
        answer.append(value)
    return tuple(answer)


def group_mul(g, h):
    u, v, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    U, V, Z = h & 1, (h >> 1) & 1, (h >> 2) & 1
    return (u ^ U) | ((v ^ V) << 1) | ((z ^ Z ^ (u & V)) << 2)


GM = tuple(tuple(group_mul(g, h) for h in range(8)) for g in range(8))


def ring_mul(left, right):
    value = 0
    for g in range(8):
        if left & (1 << g):
            for h in range(8):
                if right & (1 << h):
                    value ^= 1 << GM[g][h]
    return value


def formal_identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def formal_mul(left, right):
    n = len(left)
    answer = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if left[i][k]:
                for j in range(n):
                    if right[k][j]:
                        answer[i][j] ^= ring_mul(left[i][k], right[k][j])
    return tuple(map(tuple, answer))


def factor(g, rows):
    n = len(rows)
    return tuple(tuple(int(i == j) ^ ((1 ^ (1 << g)) if rows[i] & (1 << j) else 0)
                       for j in range(n)) for i in range(n))


def scalar(rows):
    return tuple(tuple(int(bool(row & (1 << j))) for j in range(len(rows))) for row in rows)


def target(r, w):
    return tuple(tuple((1 << 4 if i < w else 1) if i == j else 0 for j in range(r))
                 for i in range(r))


def count_per_label(w, k):
    require(type(w) is int and type(k) is int and w >= 1 and k >= 1, 'positive integer w,k')
    return max(2, (2 * w + k - 1) // k)


def construction(r, w, k):
    require(type(r) is int and r >= w, 'workspace r must be at least w')
    t = count_per_label(w, k)
    supports = [set() for _ in range(t)]
    for i in range(w):
        supports[(2 * i) % t].add(i)
        supports[(2 * i + 1) % t].add(i)
    word = []
    for support in supports:
        rows = tuple(1 << i if i in support else 0 for i in range(r))
        require(1 <= rank(rows) <= k, 'empty or oversized block')
        word.extend(((1, rows), (2, rows)))
    return tuple(word)


def invoice(word, k):
    counts, masses = [0, 0], [0, 0]
    for g, rows in word:
        require(g in (1, 2), 'only paid labels a,b are allowed')
        d = rank(rows)
        require(1 <= d <= k, 'rank cap violated')
        counts[g - 1] += 1
        masses[g - 1] += d
    return {'counts': counts, 'rank_mass': masses}


def replay(word, r):
    answer = formal_identity(r)
    for g, rows in word:
        answer = formal_mul(answer, factor(g, rows))
    return answer


def check_word(word, r, w, k, claimed_invoice):
    for _, rows in word:
        require(len(rows) == r and all(type(row) is int and 0 <= row < 1 << r for row in rows),
                'invalid scalar coupling dimensions')
    require(invoice(word, k) == claimed_invoice, 'undercharged invoice')
    require(replay(word, r) == target(r, w), 'incorrect complete dirty boundary')


# Basis 1,X,Y,XY,YX; this algebra multiplication does not use GM.
QM = ((0, 1, 2, 3, 4), (1, None, 3, None, None),
      (2, 4, None, None, None), (3, None, None, None, None),
      (4, None, None, None, None))


def quotient_mul(left, right):
    value = 0
    for i in range(5):
        for j in range(5):
            if left & (1 << i) and right & (1 << j) and QM[i][j] is not None:
                value ^= 1 << QM[i][j]
    return value


def quotient(g):
    u, v, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    return 1 | (u << 1) | (v << 2) | (z << 3) | ((z ^ (u & v)) << 4)


def formal_quotient(matrix):
    out = {i: [] for i in range(1, 5)}
    for row in matrix:
        values = [0] * 5
        for j, entry in enumerate(row):
            q = 0
            for g in range(8):
                if entry & (1 << g):
                    q ^= quotient(g)
            for i in range(1, 5):
                if q & (1 << i):
                    values[i] |= 1 << j
        for i in out:
            out[i].append(values[i])
    return {i: tuple(rows) for i, rows in out.items()}


def coefficients(word, r):
    """Ordered one/two-subsequence expansion, with matrix factors in order."""
    zero = tuple(0 for _ in range(r))
    out = {1: zero, 2: zero, 3: zero, 4: zero}
    for j, (g, rows) in enumerate(word):
        out[g] = tuple(a ^ b for a, b in zip(out[g], rows))
        for h, previous in word[:j]:
            if h != g:
                key = 3 if h == 1 else 4
                contribution = binary_mul(previous, rows)
                out[key] = tuple(a ^ b for a, b in zip(out[key], contribution))
    return out


def quotient_replay(word, r):
    """Separate dynamic recurrence, with no subsequence list."""
    zero = tuple(0 for _ in range(r))
    X, Y, XY, YX = zero, zero, zero, zero
    for g, rows in word:
        if g == 1:
            YX = tuple(a ^ b for a, b in zip(YX, binary_mul(Y, rows)))
            X = tuple(a ^ b for a, b in zip(X, rows))
        else:
            XY = tuple(a ^ b for a, b in zip(XY, binary_mul(X, rows)))
            Y = tuple(a ^ b for a, b in zip(Y, rows))
    return {1: X, 2: Y, 3: XY, 4: YX}


def rank_factorization(rows):
    """A=UV, U full column rank and V full row rank, over F2."""
    r = len(rows)
    basis, coordinates = [], []
    columns = [sum(((rows[i] >> j) & 1) << i for i in range(r)) for j in range(r)]
    for column in columns:
        lookup = {0: 0}
        for j, value in enumerate(basis):
            lookup.update({x ^ value: c | (1 << j) for x, c in list(lookup.items())})
        if column not in lookup:
            basis.append(column)
            coordinates.append(1 << (len(basis) - 1))
        else:
            coordinates.append(lookup[column])
    U = tuple(sum(((col >> i) & 1) << j for j, col in enumerate(basis)) for i in range(r))
    V = tuple(sum(((coordinates[j] >> i) & 1) << j for j in range(r)) for i in range(len(basis)))
    require(binary_mul(U, V) == rows, 'rank factorization')
    return U, V


def span_check(word, r):
    """Check actual zero-sum, carrier spans and mixed coefficients."""
    coeff = coefficients(word, r)
    for g in (1, 2):
        left_columns, right_rows = [], []
        for h, rows in word:
            if h == g:
                U, V = rank_factorization(rows)
                for j in range(len(V)):
                    left_columns.append(sum(((U[i] >> j) & 1) << i for i in range(r)))
                right_rows.extend(V)
        U = tuple(sum(((col >> i) & 1) << j for j, col in enumerate(left_columns)) for i in range(r))
        require(binary_mul(U, tuple(right_rows)) == coeff[g], 'degree-one sum')
        col_mixed, row_mixed = coeff[3 if g == 1 else 4], coeff[4 if g == 1 else 3]
        columns = [sum(((col_mixed[i] >> j) & 1) << i for i in range(r)) for j in range(r)]
        require(rank(left_columns + columns) == rank(left_columns), 'mixed column containment')
        require(rank(right_rows + list(row_mixed)) == rank(right_rows), 'mixed row containment')
        if not any(coeff[g]):
            require(rank(U) + rank(right_rows) <= len(right_rows), 'zero-product rank inequality')
            require(rank(col_mixed) + rank(row_mixed) <= len(right_rows), 'rank-volume lower bound')


# Faithful regular engine: literal 3x3 address matrices, independent group
# enumeration and multiplication. It never calls GM or ring_mul.
ADDRESS = tuple(tuple((int(i == j) ^ (u if (i, j) == (0, 1) else 0)
                       ^ (v if (i, j) == (1, 2) else 0)
                       ^ (z if (i, j) == (0, 2) else 0))
                      for i in range(3) for j in range(3))
                for u, v, z in product((0, 1), repeat=3))


def address_mul(a, b):
    return tuple(sum(a[3 * i + t] * b[3 * t + j] for t in range(3)) % 2
                 for i in range(3) for j in range(3))


def regular_address(address):
    rows = [0] * 8
    for j, h in enumerate(ADDRESS):
        rows[ADDRESS.index(address_mul(address, h))] |= 1 << j
    return tuple(rows)


RA, RB, RC = (regular_address(ADDRESS[i]) for i in (4, 2, 1))


def regular_from_formal(matrix):
    """Bridge only for comparison; the regular replay never calls this."""
    r = len(matrix)
    out = [0] * (8 * r)
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            for g in range(8):
                if entry & (1 << g):
                    index = 4 * (g & 1) + 2 * ((g >> 1) & 1) + ((g >> 2) & 1)
                    action = regular_address(ADDRESS[index])
                    for s in range(8):
                        out[8 * i + s] ^= action[s] << (8 * j)
    return tuple(out)


def regular_factor(g, rows):
    r = len(rows)
    transport = RA if g == 1 else RB
    output = list(identity(8 * r))
    for i, row in enumerate(rows):
        for j in range(r):
            if row & (1 << j):
                for s in range(8):
                    output[8 * i + s] ^= (transport[s] ^ (1 << s)) << (8 * j)
    return tuple(output)


def regular_scalar(rows):
    return tuple(sum((1 << (8 * j + s)) for j in range(len(rows)) if row & (1 << j))
                 for row in rows for s in range(8))


def regular_target(r, w):
    return tuple((RC[s] if i < w else 1 << s) << (8 * i) for i in range(r) for s in range(8))


def regular_replay(word, r):
    result = identity(8 * r)
    for g, rows in word:
        result = binary_mul(result, regular_factor(g, rows))
    return result


def expect_rejection(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control was accepted')


def run():
    for g, h in product(range(8), repeat=2):
        require(quotient(GM[g][h]) == quotient_mul(quotient(g), quotient(h)), 'quotient homomorphism')
    for x, y, z in product(range(32), repeat=3):
        require(quotient_mul(quotient_mul(x, y), z) == quotient_mul(x, quotient_mul(y, z)), 'quotient associativity')
    require(quotient(4) == 1 ^ 8 ^ 16, 'both mixed coefficients required')
    coupling_counts = {}
    for r in (1, 2, 3):
        counts = [0] * (r + 1)
        for rows in product(range(1 << r), repeat=r):
            d = rank(rows)
            require(d == dense_rank(rows, r), 'independent rank mismatch')
            U, V = rank_factorization(rows)
            counts[d] += 1
            for g in (1, 2):
                F = factor(g, rows)
                split = formal_identity(r)
                for j, v in enumerate(V):
                    component = tuple(v if U[i] & (1 << j) else 0 for i in range(r))
                    require(rank(component) == 1, 'nonzero rank-one decomposition component')
                    split = formal_mul(split, factor(g, component))
                require(split == F, 'same-label rank decomposition')
                require(formal_mul(F, F) == formal_identity(r), 'arbitrary-rank call inverse')
                D = regular_factor(g, rows)
                require(binary_mul(D, D) == identity(8 * r), 'regular call inverse')
        coupling_counts[str(r)] = counts
    matrices = [rows for rows in product(range(4), repeat=2) if any(rows)]
    alphabet = [(g, rows) for g in (1, 2) for rows in matrices]
    short_words = 0
    for length in range(4):
        for word in product(alphabet, repeat=length):
            require(coefficients(word, 2) == quotient_replay(word, 2), 'ordered coefficient mismatch')
            require(coefficients(word, 2) == formal_quotient(replay(word, 2)), 'formal quotient mismatch')
            span_check(word, 2)
            short_words += 1
    for first, second in product(alphabet, repeat=2):
        require(regular_from_formal(replay((first, second), 2)) == regular_replay((first, second), 2),
                'formal/regular arbitrary two-factor mismatch')
    fixtures, omissions, basis_columns, profiles = 0, 0, 0, []
    for w in range(1, 13):
        for k in range(1, w + 3):
            r = w + 2
            word = construction(r, w, k)
            bill = invoice(word, k)
            t = count_per_label(w, k)
            require(bill == {'counts': [t, t], 'rank_mass': [2 * w, 2 * w]}, 'sharp invoice')
            require(replay(word, r) == target(r, w), 'full formal dirty endpoint')
            require(replay(tuple(reversed(word)), r) == target(r, w), 'formal inverse endpoint')
            require(regular_replay(word, r) == regular_target(r, w), 'faithful regular dirty endpoint')
            require(regular_replay(tuple(reversed(word)), r) == regular_target(r, w), 'regular inverse endpoint')
            span_check(word, r)
            profiles.append([w, k, t, [rank(rows) for _, rows in word]])
            fixtures += 1
            basis_columns += 2 * 8 * r
            if w <= 3:
                for j in range(len(word)):
                    bad = word[:j] + word[j + 1:]
                    require(replay(bad, r) != target(r, w), 'omitted-call formal control')
                    require(regular_replay(bad, r) != regular_target(r, w), 'omitted-call regular control')
                    omissions += 1
    r, w, k = 5, 3, 2
    pilot = construction(r, w, k)
    S = list(identity(r))
    S[0] ^= 1 << 4
    S[1] ^= 1 << 2
    S = tuple(S)
    require(binary_mul(S, S) == identity(r), 'scalar gauge inverse')
    gauged = tuple((g, binary_mul(binary_mul(S, rows), S)) for g, rows in pilot)
    F, D = replay(gauged, r), regular_replay(gauged, r)
    require(formal_mul(formal_mul(scalar(S), F), scalar(S)) == target(r, w), 'full gauged dirty boundary')
    require(binary_mul(binary_mul(regular_scalar(S), D), regular_scalar(S)) == regular_target(r, w), 'regular gauged boundary')
    require(F != target(r, w) and D != regular_target(r, w), 'missing scalar boundary control')
    span_check(gauged, r)
    expect_rejection(lambda: invoice(pilot, 1))
    expect_rejection(lambda: invoice(((4, identity(r)),), r))
    expect_rejection(lambda: construction(2, 3, 2))
    expect_rejection(lambda: construction(3, 3, 0))
    expect_rejection(lambda: check_word(pilot, r, w, k, {'counts': [3, 3], 'rank_mass': [6, 5]}))
    wrong = ((2, pilot[0][1]),) + pilot[1:]
    require(replay(wrong, r) != target(r, w), 'wrong paid label control')
    require(regular_replay(wrong, r) != regular_target(r, w), 'wrong paid label regular control')
    dirty = list(pilot[0][1])
    dirty[0] ^= 1 << 3
    leaked = ((1, tuple(dirty)),) + pilot[1:]
    require(replay(leaked, r) != target(r, w), 'dirty-source contamination formal control')
    require(regular_replay(leaked, r) != regular_target(r, w), 'dirty-source contamination regular control')
    extra = tuple(1 << 3 if i == 3 else 0 for i in range(r))
    unrestored = pilot + ((1, extra),)
    require(replay(unrestored, r) != target(r, w), 'unrestored workspace formal control')
    require(regular_replay(unrestored, r) != regular_target(r, w), 'unrestored workspace regular control')
    perturbed = [list(row) for row in target(r, w)]
    perturbed[0][r - 1] ^= ring_mul(1 ^ (1 << 1), 1 ^ (1 << 4))
    perturbed = tuple(map(tuple, perturbed))
    require(perturbed != target(r, w), 'nonzero quotient-kernel control')
    require(formal_quotient(perturbed) == formal_quotient(target(r, w)), 'kernel perturbation must be invisible to quotient')
    require(regular_from_formal(perturbed) != regular_target(r, w), 'faithful kernel rejection')
    tariff_checks = 0
    for w in range(1, 13):
        for k in range(1, w + 3):
            bill = invoice(construction(w, w, k), k)
            t = count_per_label(w, k)
            for aa, ab, ba, bb in ((1, 1, 0, 0), (0, 0, 1, 1),
                                   (Fraction(3, 2), Fraction(5, 7), Fraction(2, 3), Fraction(7, 11))):
                paid = aa * bill['counts'][0] + ab * bill['counts'][1] + ba * bill['rank_mass'][0] + bb * bill['rank_mass'][1]
                require(paid == t * (aa + ab) + 2 * w * (ba + bb), 'exact affine tariff')
                tariff_checks += 1
    return {'schema_version': 1, 'result': 'sharp rank-cap invocation count; no new kappa',
            'formula': 't=max(2,ceil(2w/k)); counts=(t,t); rank_mass=(2w,2w)',
            'quotient_products': 64, 'quotient_associativity_triples': 32768,
            'all_binary_couplings_rank_counts': coupling_counts,
            'same_label_rank_decompositions': 1060,
            'short_words': short_words, 'full_formal_and_regular_fixtures': fixtures,
            'arbitrary_two_factor_formal_regular_comparisons': len(alphabet) ** 2,
            'forward_inverse_regular_basis_columns': basis_columns,
            'omitted_call_controls': omissions, 'other_model_controls': 10,
            'scalar_gauged_fixtures': 1, 'exact_rational_tariff_checks': tariff_checks,
            'profiles_sha256': hashlib.sha256(json.dumps(profiles, separators=(',', ':')).encode()).hexdigest(),
            'pilot': {'w': 3, 'k': 2, 'r': 5, 'invoice': invoice(pilot, k),
                      'supports': [[i for i in range(r) if rows[i]] for _, rows in pilot]}}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print fresh receipt; never write package files')
    args = parser.parse_args()
    receipt = run()
    if args.emit:
        print(json.dumps(receipt, sort_keys=True, indent=2))
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text(), object_pairs_hook=unique_object)
        require(json.dumps(receipt, sort_keys=True) == json.dumps(expected, sort_keys=True), 'certificate mismatch')
        print('PASS_UT3_RANK_CAP calls=2*max(2,ceil(2w/k)) rank_mass=4w pilot_calls=6 no_new_kappa')


if __name__ == '__main__':
    main()

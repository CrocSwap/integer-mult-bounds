"""Exact controls for the written arbitrary-register UT3 bound. Apache-2.0.

Finite checks corroborate README.md; they do not enumerate all register counts
or certify formal equality from a quotient. Substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASIS = ('', 'x', 'y', 'xy', 'yx')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def qmul(left, right):
    out = 0
    for i, a in enumerate(BASIS):
        if left >> i & 1:
            for j, b in enumerate(BASIS):
                if right >> j & 1:
                    word = a + b
                    if word in BASIS:
                        out ^= 1 << BASIS.index(word)
    return out


def group_mul(g, h):
    """UT3 triples encoded x+2y+4z; multiplication is noncommutative."""
    return g ^ h ^ (((g & 1) * ((h >> 1) & 1)) << 2)


def image(g):
    x, y, z = g & 1, (g >> 1) & 1, (g >> 2) & 1
    return 1 | (x << 1) | (y << 2) | (z << 3) | ((z ^ (x * y)) << 4)


def eye(r):
    return tuple(1 << i for i in range(r))


def zero(r):
    return (0,) * r


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def mm(a, b):
    rows = []
    for row in a:
        result = 0
        while row:
            bit = row & -row
            result ^= b[bit.bit_length() - 1]
            row ^= bit
        rows.append(result)
    return tuple(rows)


def rank(a):
    pivots = {}
    for row in a:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def outer(u, v, r):
    return tuple(v if u >> i & 1 else 0 for i in range(r))


def projectors(r):
    return [outer(u, v, r) for u in range(1, 1 << r)
            for v in range(1, 1 << r) if (u & v).bit_count() % 2]


def rank_one_matrices(r):
    return [outer(u, v, r) for u in range(1, 1 << r) for v in range(1, 1 << r)]


def validate_paid(n):
    need(rank(n) == 1, 'not a rank-one paid coupling')


def validate_projector(n):
    need(rank(n) == 1 and mm(n, n) == n, 'not a rank-one idempotent')


def qword(word, r):
    """Matrix product in quotient coefficients; order matches written product."""
    out = [eye(r), *[zero(r) for _ in range(4)]]
    for g, n in word:
        label = 1 if g == 1 else 2
        need(g in (1, 2), 'restricted alphabet')
        nxt = list(out)
        for i in range(5):
            monomial = BASIS[i] + BASIS[label]
            if monomial in BASIS:
                j = BASIS.index(monomial)
                nxt[j] = add(nxt[j], mm(out[i], n))
        out = nxt
    return tuple(out)


def formal_word(word, r):
    """Full eight-coefficient group-algebra product, not quotient admission."""
    out = {0: eye(r)}
    for g, n in word:
        nxt = dict(out)
        for h, coefficient in out.items():
            term = mm(coefficient, n)
            for label in (h, group_mul(h, g)):
                nxt[label] = add(nxt.get(label, zero(r)), term)
        out = {g: n for g, n in nxt.items() if any(n)}
    return out


def quotient_formal(formal, r):
    out = [zero(r) for _ in range(5)]
    for g, matrix in formal.items():
        for i in range(5):
            if image(g) >> i & 1:
                out[i] = add(out[i], matrix)
    return tuple(out)


def regular_word(word, r):
    """Separate F2 replay in a faithful regular representation.

    Construct literal 3x3 address matrices instead of using group_mul/image,
    then form 8r-dimensional right-regular operators and multiply row masks.
    """
    addresses = [(1 | ((g & 1) << 1) | (((g >> 2) & 1) << 2),
                  2 | (((g >> 1) & 1) << 2), 4) for g in range(8)]
    out = eye(8 * r)
    for g, n in word:
        permutation = [addresses.index(mm(h, addresses[g])) for h in addresses]
        rows = []
        for i in range(r):
            for h in range(8):
                row = 1 << (8 * i + h)
                for j in range(r):
                    if n[i] >> j & 1:
                        row ^= (1 << (8 * j + h)) ^ (1 << (8 * j + permutation[h]))
                rows.append(row)
        out = mm(out, tuple(rows))
    return out


def regular_formal(formal, r):
    addresses = [(1 | ((g & 1) << 1) | (((g >> 2) & 1) << 2),
                  2 | (((g >> 1) & 1) << 2), 4) for g in range(8)]
    rows = [0] * (8 * r)
    for g, n in formal.items():
        for h in range(8):
            destination = addresses.index(mm(addresses[h], addresses[g]))
            for i in range(r):
                for j in range(r):
                    if n[i] >> j & 1:
                        rows[8 * i + h] ^= 1 << (8 * j + destination)
    return tuple(rows)


def determinant_dual(n):
    """Leibniz determinant of I+tN over F2[t]/t^2, without rank-one shortcut."""
    r = len(n)
    out = 0
    for permutation in itertools.permutations(range(r)):
        term = 1
        for i, j in enumerate(permutation):
            value = int(i == j) | (((n[i] >> j) & 1) << 1)
            term = ((term & 1) * (value & 1)) | (
                (((term & 1) * (value >> 1)) ^ ((term >> 1) * (value & 1))) << 1)
        out ^= term
    return out


def target(r, w=2):
    q = tuple(1 << i if i < w else 0 for i in range(r))
    return {0: add(eye(r), q), 4: q} if r > w else {4: q}


def direct(r, w=2):
    return [(g, outer(1 << i, 1 << i, r))
            for i in range(w) for g in (1, 2, 1, 2)]


def coefficient_rank_check(word, r):
    """Check both scalar-span bounds used in the proof, without inferring equality."""
    coefficients = qword(word, r)
    for label, linear, column_mixed, row_mixed in ((1, 1, 3, 4), (2, 2, 4, 3)):
        factors = [n for g, n in word if g == label]
        vectors = []
        for n in factors:
            v = next((row for row in n if row), 0)
            need(v != 0 and all(row in (0, v) for row in n), 'rank-one factorization')
            u = sum(1 << i for i, row in enumerate(n) if row)
            vectors.append((u, v))
        u_matrix = tuple(sum(((u >> i) & 1) << j for j, (u, v) in enumerate(vectors))
                         for i in range(r))
        vt_matrix = tuple(v for u, v in vectors)
        need(mm(u_matrix, vt_matrix) == coefficients[linear], 'linear coefficient UV^T')
        need(rank(coefficients[column_mixed]) <= rank(u_matrix), 'mixed column span')
        need(rank(coefficients[row_mixed]) <= rank(vt_matrix), 'mixed row span')
        if not any(coefficients[linear]):
            need(rank(u_matrix) + rank(vt_matrix) <= len(factors), 'zero-product rank inequality')


def zero_product_controls():
    """All binary 2-by-p / p-by-2 pairs, p=1..4; no paid-word assumption."""
    checked = 0
    for p in range(1, 5):
        for packed_u in range(1 << (2 * p)):
            u = (packed_u & ((1 << p) - 1), packed_u >> p)
            for packed_v in range(1 << (2 * p)):
                vt = tuple((packed_v >> (2 * i)) & 3 for i in range(p))
                if mm(u, vt) == zero(2):
                    need(rank(u) + rank(vt) <= p, 'independent rectangular rank control')
                    checked += 1
    return checked


def symbolic_patterns():
    """Expand by selecting at most two nonconstant factors, independently.

    B symbols are chronological and both x symbols are N. These bounded
    patterns corroborate the written all-length coefficient formula.
    """
    patterns = 0
    for k in range(2, 9):
        for first, second in itertools.combinations(range(k), 2):
            labels = ['y'] * k
            labels[first] = labels[second] = 'x'
            names = [('N',) if t == 'x' else (f'B{i}',) for i, t in enumerate(labels)]
            coefficients = {'x': set(), 'xy': set(), 'yx': set()}
            for i in range(k):
                if labels[i] == 'x':
                    coefficients['x'].symmetric_difference_update([names[i]])
                for j in range(i + 1, k):
                    monomial = labels[i] + labels[j]
                    if monomial in ('xy', 'yx'):
                        coefficients[monomial].symmetric_difference_update([names[i] + names[j]])
            middle = [f'B{i}' for i in range(first + 1, second)]
            need(not coefficients['x'], 'linear coefficient must vanish')
            need(coefficients['xy'] == {('N', b) for b in middle}, 'left factorization')
            need(coefficients['yx'] == {(b, 'N') for b in middle}, 'right factorization')
            patterns += 1
    return patterns


def run_checks():
    for a, b in itertools.product(range(8), repeat=2):
        need(image(group_mul(a, b)) == qmul(image(a), image(b)), 'quotient homomorphism')
    for a, b, c in itertools.product(range(32), repeat=3):
        need(qmul(qmul(a, b), c) == qmul(a, qmul(b, c)), 'quotient associativity')
    need(image(4) == 1 | 8 | 16, 'central target has both mixed coefficients')

    count = 0
    for r in (2, 3, 4):
        ns = projectors(r)
        need(len(ns) == ((1 << r) - 1) * (1 << (r - 1)), 'complete outer-product count')
        for n in ns:
            validate_projector(n)
            need(determinant_dual(n) == 3, 'separate-label determinant parity')
            count += 1

    expanded_generators, nilpotent_count = 0, 0
    for r in (2, 3, 4):
        matrices = rank_one_matrices(r)
        need(len(matrices) == ((1 << r) - 1) ** 2, 'complete rank-one alphabet')
        need(len(set(matrices)) == len(matrices), 'unique outer products over F2')
        for n in matrices:
            validate_paid(n)
            if mm(n, n) == zero(r):
                need(determinant_dual(n) == 1, 'nilpotent coupling has no parity contribution')
                nilpotent_count += 1
            else:
                need(mm(n, n) == n, 'rank-one trace dichotomy')
            for g in (1, 2):
                need(formal_word([(g, n), (g, n)], r) == {0: eye(r)}, 'every expanded paid call is involutory')
                need(regular_word([(g, n), (g, n)], r) == eye(8 * r), 'faithful expanded involution')
                expanded_generators += 1

    concrete = 0
    ns = rank_one_matrices(2)
    for bcount in range(4):
        for first, second in itertools.combinations(range(bcount + 2), 2):
            for n in ns:
                for bs in itertools.product(ns, repeat=bcount):
                    word, at, middle = [], 0, zero(2)
                    for i in range(bcount + 2):
                        if i in (first, second):
                            word.append((1, n))
                        else:
                            word.append((2, bs[at]))
                            if first < i < second:
                                middle = add(middle, bs[at])
                            at += 1
                    out = qword(word, 2)
                    need(out[1] == zero(2), 'two equal a linear coefficient')
                    need(out[3] == mm(n, middle) and out[4] == mm(middle, n), 'mixed coefficient law')
                    need(rank(out[3]) <= 1 and rank(out[4]) <= 1, 'rank-one obstruction')
                    concrete += 1

    witness_counts, controls = [], 0
    for r in (2, 3, 4, 8, 16):
        word, wanted = direct(r), target(r)
        formal = formal_word(word, r)
        need(formal == wanted, 'complete dirty boundary of eight-call witness')
        need(qword(word, r) == quotient_formal(formal, r), 'formal/quotient compatibility')
        need(regular_word(word, r) == regular_formal(wanted, r), 'faithful regular witness')
        for i in range(8):
            need(formal_word(word[:i] + word[i + 1:], r) != wanted, 'omitted paid call')
            controls += 1
        need(formal_word(direct(r, 1), r) == target(r, 1), 'rank-one target legitimately costs four')
        witness_counts.append(r * 8)

    general_witnesses = []
    for r in (1, 2, 3, 4, 8, 16):
        for w in range(1, r + 1):
            word, wanted = direct(r, w), target(r, w)
            need(formal_word(word, r) == wanted, '4w complete formal witness')
            need(regular_word(word, r) == regular_formal(wanted, r), '4w faithful boundary')
            coefficient_rank_check(word, r)
            general_witnesses.append([r, w, 4 * w])

    r = 5
    scalar = list(eye(r))
    scalar[0] ^= scalar[4]
    scalar = tuple(scalar)
    word = [(g, mm(mm(scalar, n), scalar)) for g, n in direct(r)]
    conjugated = {g: mm(mm(scalar, n), scalar) for g, n in target(r).items()}
    need(formal_word(word, r) == conjugated, 'arbitrary dirty scalar conjugation')
    need(regular_word(word, r) == regular_formal(conjugated, r), 'conjugated faithful boundary')
    coefficient_rank_check(word, r)
    need(formal_word(word, r) != target(r), 'nontrivial scalar/output boundary detected')
    controls += 1

    for n in (zero(2), eye(2)):
        try:
            validate_paid(n)
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid paid primitive admitted')
    need(formal_word([(g, eye(2)) for g in (1, 2, 1, 2)], 2) == target(2),
         'rank-two primitives destroy the eight-unit bound')
    controls += 1
    expanded = [(4, outer(1 << i, 1 << i, 3)) for i in range(2)]
    need(formal_word(expanded, 3) == target(3), 'central-label primitive destroys the bound')
    controls += 1
    kernel = {g: (1,) for g in range(8)}
    need(quotient_formal(kernel, 1) == (zero(1),) * 5, 'nonfaithful quotient kernel')
    need(any(regular_formal(kernel, 1)), 'formal nonzero kernel survives faithful replay')
    controls += 1
    need(formal_word(direct(3) + [(1, outer(4, 4, 3))], 3) != target(3), 'dirty extra must be restored')
    controls += 1
    validate_paid((2, 0))
    need(determinant_dual((2, 0)) == 1, 'legal nilpotent coupling defeats idempotent parity shortcut')
    controls += 1

    return {'schema_version': 1, 'status': 'PASS_UT3_ANY_REGISTERS',
        'written_theorem': 'minimum 4w for every finite r>=w>=1 with all nonzero rank-one scalar couplings; eight at w=2',
        'finite_evidence': {'group_products': 64, 'algebra_associativity_triples': 32768,
            'idempotent_determinants': count, 'expanded_paid_involutions': expanded_generators,
            'nilpotent_scalar_couplings': nilpotent_count,
            'symbolic_two_occurrence_patterns': symbolic_patterns(),
            'concrete_two_occurrence_words': concrete, 'faithful_witness_columns': witness_counts,
            'conjugated_witness_columns': 40, 'general_witnesses': general_witnesses,
            'zero_product_rank_pairs': zero_product_controls(), 'controls': controls},
        'acceptance_limit': 'Finite checks corroborate README proof; quotient equality never admits a formal word.',
        'new_kappa': False}


def check_pins():
    root = HERE.parents[1]
    for source in json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if source['usage'] == 'input':
            need(hashlib.sha256((root / source['path']).read_bytes()).hexdigest() == source['sha256'], 'source pin')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print fresh receipt without writing files')
    args = parser.parse_args()
    check_pins()
    receipt = run_checks()
    if args.emit:
        print(json.dumps(receipt, indent=2))
    else:
        expected = json.loads((HERE / 'EXPECTED.json').read_text(encoding='utf-8'))
        need(json.dumps(receipt, sort_keys=True) == json.dumps(expected, sort_keys=True), 'receipt mismatch')
        print(receipt['status'], 'minimum=4w registers=any-finite-r>=w>=1 two_targets=8',
              'controls=' + str(receipt['finite_evidence']['controls']), 'no_new_kappa')


if __name__ == '__main__':
    main()

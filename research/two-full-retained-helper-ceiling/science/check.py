#!/usr/bin/env python3
"""Exact source normalizers and symbolic separated-helper compression, no search.
Apache-2.0; substantial OpenAI Codex assistance; predecessor credit in PROOF.md.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent


def need(test, why):
    if not test:
        raise ValueError(why)


def sym(name):
    return {(name,): 1}


ONE = {(): 1}
ZERO = {}


def plus(*polynomials):
    result = defaultdict(int)
    for polynomial in polynomials:
        for word, coefficient in polynomial.items():
            result[word] += coefficient
    return {word: c for word, c in result.items() if c}


def mul(*polynomials):
    result = ONE
    for polynomial in polynomials:
        new = defaultdict(int)
        for word, coefficient in result.items():
            for second, c in polynomial.items():
                new[word + second] += coefficient * c
        result = {word: c for word, c in new.items() if c}
    return result


def mm(left, right):
    return [[plus(*(mul(left[i][k], right[k][j]) for k in range(len(right))))
             for j in range(len(right[0]))] for i in range(len(left))]


def eye(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def diag(entries):
    n = len(entries)
    return [[entries[i] if i == j else ZERO for j in range(n)] for i in range(n)]


def compress_fixture(m1, m2, scratch):
    n = 2 + m1 + m2 + scratch
    first_helpers = set(range(2, 2+m1))
    second_helpers = set(range(2+m1, 2+m1+m2))
    d1 = [sym('D1x'), sym('D1y')] + [ONE for _ in range(n-2)]
    d2 = [sym('D2x'), sym('D2y')] + [ONE for _ in range(n-2)]
    for j in first_helpers:
        d1[j] = sym('H1_' + str(j))
    for j in second_helpers:
        d2[j] = sym('barH2_' + str(j))
    E1, E2 = eye(n), eye(n)
    E1[1][0] = sym('Q1inv')
    E2[0][1] = {('Q2',): -1}
    W = [[sym('W%d_%d' % (i, j)) for j in range(n)] for i in range(n)]
    T1, T2 = mm(diag(d1), E1), mm(diag(d2), E2)
    M = mm(mm(T2, W), T1)

    # Only a SINGLE outside-subgroup letter may be discarded without knowing
    # products of outside letters. Keep all double-letter terms as opaque pi.
    outside = {'Q1inv', 'Q2'} | {'H1_' + str(j) for j in first_helpers}
    outside |= {'barH2_' + str(j) for j in second_helpers}

    def pi(polynomial):
        result = {}
        for word, c in polynomial.items():
            count = sum(token in outside for token in word)
            if count == 0:
                result[word] = c
            elif count >= 2:
                result[('OPAQUE_PI',) + word] = c
        return result

    # Row0 is the second shear destination. Its source row1 stays in U.
    U = [i for i in range(n) if i not in second_helpers and i != 0]
    C = [j for j in range(n) if j not in first_helpers]
    for i in U:
        for j in C:
            need(pi(M[i][j]) == mul(d2[i], W[i][j], d1[j]),
                 'exact noncommutative projected compression')
    need(len(U)+len(C)-n == scratch+1, 'Sylvester lower bound')
    # An excluded destination row has actual double-nonB terms. Treating it as
    # an untouched row would require an unjustified outside*outside rule.
    need(any('OPAQUE_PI' in word for word in pi(M[0][0])), 'wrong-row control')
    need(mul(sym('D1y'), sym('Q1inv')) != mul(sym('Q1inv'), sym('D1y')),
         'raw transverse/query order is never silently commuted')
    return dict(m1=m1, m2=m2, scratch=scratch, owners=n,
                untouched_rows=U, ordinary_input_columns=C,
                projected_rank_lower_bound=str(scratch+1)+'*dim(B_f)',
                target_projected_rank=str(scratch)+'*dim(B_f)')


def main():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['files']:
        raw = (HERE/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == row['git_blob'], 'source Git blob')
    phase_check = (HERE/'source/phase_check.py').read_text()
    need("actual=P.conjugate(ce,op) if d=='backward' else op" in phase_check,
         'actual retained backward helper ABI')
    data = json.loads((HERE/'source/DATA-PHASES.json').read_text())
    actual = json.loads(gzip.decompress((HERE/'source/ACTUAL-WORD.json.gz').read_bytes()))
    canonical = actual['canonical']
    need(canonical['start'][224] == 0 and canonical['final'][224] == 1,
         'actual independent helper224 empty-to-full native job')
    need(canonical['frames'][0] == [] and sorted(canonical['frames'][1]) == [1 << j for j in range(9)],
         'literal fullH9 frame is native productC_ej')
    normalizers = []
    phase_equalities = 0
    for port, recipe in enumerate(data['recipes']):
        q = recipe['q']
        axes = recipe['idle_children'][0]['orthogonal_axes'][:8]
        basis = [q] + axes
        need(len(basis) == 9 and all((a & b).bit_count() % 2 == int(i == j)
             for i, a in enumerate(basis) for j, b in enumerate(basis)),
             'literal q plus transverse8 source orthonormal basis')
        # In the Fourier character indexed by k, C_v has eigenvalue
        # i^parity(v.k). Derive the translation from the nine basis characters,
        # then check ALL512 characters, retaining its absolute phase.
        def difference(k):
            return (k.bit_count() - (q & k).bit_count()%2
                    - sum((a & k).bit_count()%2 for a in axes)) % 4
        singles = [difference(1 << j) for j in range(9)]
        need(all(v in (0, 2) for v in singles), 'even linear translation')
        t = sum((v//2) << j for j, v in enumerate(singles))
        u = 0
        for a in axes:
            u ^= a
        for k in range(512):
            pA = sum((a & k).bit_count()%2 for a in axes)
            pQ = (q & k).bit_count()%2
            need(difference(k) == 2*((t & k).bit_count()%2) % 4,
                 'absolute F9 Q^-1 = X_t D_A')
            need((-k.bit_count() - (2*(((t ^ u) & k).bit_count()%2)
                  + pA - pQ)) % 4 == 0,
                 'actual conjugate F9bar = X_(t xor u) D_A Q^-1')
            phase_equalities += 2
        normalizers.append(dict(port=port, q=q, transverse_axes=axes,
                                translation=t, transverse_square_translation=u,
                                backward_translation=t ^ u,
                                rawD0_commutes_with_S=((q & t).bit_count()%2 == 0)))
    need(len(normalizers) == 112, 'all112 actual ports')
    need(normalizers[0]['q'] == 11 and normalizers[0]['translation'] == 15
         and normalizers[0]['backward_translation'] == 507,
         'independent predecessor literal port0 control')
    need(not normalizers[0]['rawD0_commutes_with_S'], 'real rawD0/S noncommutation control')
    fixtures = [compress_fixture(1, 1, 0), compress_fixture(1, 1, 2),
                compress_fixture(2, 1, 1), compress_fixture(0, 0, 2)]
    result = dict(status='PASS_SEPARATED_HELPER_PROJECTION_GATE', new_kappa=False,
                  native_source=sources['source_4610'],
                  corrected_backward_helper='entrywise conjugate(H), NOT adjoint(H) in general',
                  fullH9_exception='barF9=F9.adjoint because literal C_ej factors commute',
                  normalizer_phase_equalities=phase_equalities, normalizers=normalizers,
                  symbolic_noncommutative_compressions=fixtures,
                  search_performed=False, native_word_emitted=False,
                  positive_consumer_constructed=False,
                  scope='Two simultaneous FULLs, distinct original helper jobs per invocation, arbitrary invertible pre/inter/post over separated central-monomial/transverse-Clifford algebra, restored B-valued scratch; arbitrary noncommuting query/helper words outsideB.',
                  exclusions=['central/fresh address mixing outside separated subgroup',
                              'prefix taps or extra nonmonomial operations',
                              'changed helper jobs, census or input ownership',
                              'non-columnwise width-specific address grammar'])
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'fixed receipt')
    print('PASS_SEPARATED_HELPER_PROJECTION_GATE 112actual_normalizers '
          + str(phase_equalities)+'absolute_phase_equalities 4symbolic_compressions '
          'backward_conjugation_corrected no_new_kappa')


if __name__ == '__main__':
    main()

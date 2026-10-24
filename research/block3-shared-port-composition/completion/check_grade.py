#!/usr/bin/env python3
"""Exact, source-bound five-bank grade expansion; no circuit search. Apache-2.0."""
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for row in sources['files']:
        raw = (HERE / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'SHA256 ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == row['git_blob'], 'Git blob ' + row['path'])
    d = {'__name__': 'retained_source'}
    exec(compile((HERE / 'sources/inputs/pr4813-verify_schedule.py').read_bytes(),
                 'retained_pr4813', 'exec'), d)
    op = d['load_operators']()
    word, adj, plus, scale = [d[k] for k in ['word', 'adjoint', 'plus', 'scale']]
    zero, I, q = d['ZERO'], d['ident'](), d['q']
    Z = scale(zero, I)
    A, B, D, F, K = [op[k] for k in ['A', 'B', 'D', 'F', 'K']]
    S = d['s_letter'](7)
    V = d['monomial']([0, 2, 1, 3, 4, 6, 5, 7])
    P = word(S, d['monomial']([0, 5, 2, 7, 4, 1, 6, 3]), S)
    Q = word(S, V, S)
    L = plus(P, scale(q(2), Q))
    N = word(A, D, adj(K))
    need(B == word(D, L, A) and F == word(A, L, A), 'native coupling words')
    need(word(A, A) == d['pauli'](1, 0), 'absolute A^2=X0')
    need(word(A, D) == word(N, K), 'native fusion AD=N K')

    def grade(m):
        rows = {sum(z != zero for z in r) for r in m}
        cols = {sum(r[j] != zero for r in m) for j in range(8)}
        need(rows == cols and len(rows) == 1, 'uniform pure Clifford support')
        n = next(iter(rows))
        need(n > 0 and n & (n - 1) == 0, 'power-of-two Clifford support')
        need(word(adj(m), m) == I, 'pure-word unitarity')
        return n.bit_length() - 1

    def projective(m):
        first = next(z for row in m for z in row if z != zero)
        return tuple(tuple(d['div'](z, first) for z in row) for row in m)

    def serial(m):
        return [[[str(z[0]), str(z[1])] for z in row] for row in m]

    # Each tuple is (absolute one-column group matrix, OUTSIDE-tensor coefficient,
    # literal branch label). Never tensor-power a sum.
    b = [word(D, g, A) for g in (P, Q)]
    h = [word(A, g, A) for g in (P, Q)]

    def expand(prefix, n, suffix=(), name=''):
        answer = []
        for bits in product((0, 1), repeat=n):
            answer.append((word(*prefix, *(b[j] for j in bits), *suffix),
                           2 ** sum(bits), name + ''.join('PQ'[j] for j in bits)))
        return answer

    blocks = [[[] for _ in range(5)] for _ in range(5)]
    blocks[0][0] = [(word(A, A), 1, 'A^2')]
    for bit in (0, 1):
        blocks[0][0] += [(m, c * 2**bit, 'F' + 'PQ'[bit] + ':' + label)
                         for m, c, label in expand((h[bit],), 4)]
    for k in range(1, 5):
        for bit in (0, 1):
            blocks[0][k] += [(m, c * 2**bit, 'F' + 'PQ'[bit] + ':' + label)
                             for m, c, label in expand((h[bit],), 4-k, (D,))]
    for j in range(1, 5):
        blocks[j][0] = expand((A,), j)
        for k in range(1, j+1):
            blocks[j][k] = expand((A,), j-k, (D,))

    def evaluate(terms):
        ans = Z
        for m, c, _ in terms:
            ans = plus(ans, scale(q(c), m))
        return ans

    # Independent recurrence at the one-column operator level.
    expected = [[Z for _ in range(5)] for _ in range(5)]
    expected[0][0] = plus(word(A, A), word(F, B, B, B, B))
    for k in range(1, 5):
        expected[0][k] = word(F, *([B] * (4-k)), D)
    for j in range(1, 5):
        expected[j][0] = word(A, *([B]*j))
        for k in range(1, j+1):
            expected[j][k] = word(A, *([B]*(j-k)), D)
    need([[evaluate(t) for t in row] for row in blocks] == expected,
         'all25 expanded blocks match actual recurrence')

    # Bind both actual emitted schedules IN THE GROUP ALGEBRA, not merely
    # after the nonfaithful width-one matrix evaluation.
    letters = dict(op, P=P, Pinv=adj(P), Q=Q, Qinv=adj(Q), V=V,
                   Z1=d['pauli'](0, 2), N=N)
    schedules = json.loads((HERE / 'sources/WORD.json').read_text())
    def grouped(terms):
        ans = defaultdict(int)
        for m, c, _ in terms:
            ans[m] += c
        return {m: c for m, c in ans.items() if c}

    expected_groups = [[grouped(t) for t in row] for row in blocks]

    def replay(schedule):
        mat = [[{I: 1} if j == k else {} for k in range(5)] for j in range(5)]
        bill = Counter()
        for gate in schedule:
            kind, dst = gate[:2]
            if kind == 'add':
                _, _, src, c = gate
                for k in range(5):
                    ans = defaultdict(int, mat[dst][k])
                    for m, coefficient in mat[src][k].items():
                        ans[m] += c * coefficient
                    mat[dst][k] = {m: coefficient for m, coefficient in ans.items() if coefficient}
                bill['ADD'] += 1
            else:
                letter = letters[gate[2]]
                rank = grade(letter)
                need(kind == 'paid' or rank == 0, 'actual monomial gate has grade0')
                mat[dst] = [{word(letter, m): c for m, c in cell.items()} for cell in mat[dst]]
                bill['H' + str(grade(letter)) if kind == 'paid' else 'monomial'] += 1
        return mat, dict(sorted(bill.items()))

    bills = {}
    for key in ('five_ports', 'fused_five_ports'):
        mat, bill = replay(schedules[key])
        need(mat == expected_groups, 'actual emitted ' + key + ' group-algebra all25 blocks')
        need([[evaluate([(m, c, '') for m, c in cell.items()]) for cell in row]
              for row in mat] == expected, 'ordinary matrix evaluation of ' + key)
        bills[key] = bill
    need(bills['fused_five_ports'] == {'ADD': 10, 'H1': 2, 'H3': 4, 'monomial': 24},
         'complete fused primitive invoice')
    mutated = [list(gate) for gate in schedules['fused_five_ports']]
    first_add = next(j for j, gate in enumerate(mutated) if gate[0] == 'add')
    mutated[first_add][3] *= -1
    need(replay(mutated)[0] != expected_groups, 'actual wrong-ADD-sign control')
    closing_a = max(j for j, gate in enumerate(schedules['fused_five_ports'])
                    if gate == ['paid', 0, 'A'])
    omitted = [gate for j, gate in enumerate(schedules['fused_five_ports']) if j != closing_a]
    need(replay(omitted)[0] != expected_groups, 'actual omitted-closing-A control')

    entries = []
    for j in range(5):
        for k in range(5):
            terms = blocks[j][k]
            groups = defaultdict(lambda: [0, []])
            for m, c, label in terms:
                groups[m][0] += c
                groups[m][1].append(dict(branch=label, coefficient=c))
            bygrade = Counter()
            group_rows = []
            for m, (c, branches) in groups.items():
                r = grade(m)
                bygrade[r] += 1
                group_rows.append(dict(grade=r, coefficient=c, matrix=serial(m), branches=branches))
            entries.append(dict(row=j, column=k, raw_terms=len(terms),
                                exact_group_terms=len(groups),
                                projective_classes=len({projective(m) for m in groups}),
                                grade_group_counts={str(r): bygrade[r] for r in range(4)},
                                terms=group_rows))

    witness = entries[0]
    need(witness['raw_terms'] == 33 and witness['exact_group_terms'] == 32
         and witness['projective_classes'] == 32, 'M00 absolute/projective grouping')
    need(witness['grade_group_counts'] == {'0': 6, '1': 0, '2': 26, '3': 0},
         'M00 exact grade census')
    maximal = [[{m: c for m, c in cell.items() if grade(m) == 3}
                for cell in row] for row in expected_groups]
    need(all(not maximal[0][k] and not maximal[k][0] for k in range(5)),
         'grade3 first row and first column both zero')
    diagonal = word(A, D)
    need(grade(diagonal) == 3 and all(maximal[j][j] == {diagonal: 1} for j in range(1, 5)),
         'four grade3 diagonal group units')
    need(all(not maximal[j][k] for j in range(1, 5) for k in range(j+1, 5)),
         'lower4x4 grade3 triangular form')
    xclass = projective(word(A, A))
    hits = [(m, c, label) for m, c, label in blocks[0][0] if projective(m) == xclass]
    need(len(hits) == 1 and hits[0][1:] == (1, 'A^2'), 'uncancelled X0 projective class')
    # Discriminating controls: absolute phase must affect width-dependent
    # coefficients, and dropping A^2 must remove its unique class.
    need(projective(scale(q(-1), I)) == projective(I) and scale(q(-1), I) != I,
         'phase-collision control')
    need(not any(projective(m) == xclass for m, _, label in blocks[0][0] if label != 'A^2'),
         'omitted-A^2 control')
    need(grade(K) == 3 and grade(word(A, A)) == 0, 'target-versus-witness control')
    result = dict(status='PASS_EXACT_FREE_COMPLETION_OBSTRUCTION', new_kappa=False,
                  source_4856=sources['source_4856'], source_4920=sources['source_4920'],
                  bills=bills, blocks=entries,
                  witness=dict(block=[0, 0], word='A^2=X0', coefficient=1, grade=0,
                               projectively_unique=True, surviving_every_central_character=True),
                  controls=['phase collision', 'omit A^2', 'target/witness grades',
                            'actual wrong ADD sign', 'actual omitted closing A'],
                  literal_group_algebra_schedule_binding=['five_ports', 'fused_five_ports'],
                  maximal_grade_resource=dict(grade=3, zero_input_columns=[0], zero_output_rows=[0],
                                              lower_triangular_unit_diagonal_owners=[1, 2, 3, 4],
                                              exact_regular_input_rank='4*dim(B_f)',
                                              five_target_rank='5*dim(B_f)',
                                              maximum_grade3_target_count=4,
                                              five_target_reward_upper_bound='4*3^t+2^t',
                                              unchanged_profile_moment_upper_bound='2^t-2<=0 for 0<=t<=1',
                                              arbitrary_rectangular_pre_post=True,
                                              identity_bypass_and_clean_copy_drop_reset=True),
                  scope='Fixed finite columnwise Clifford alphabet; arbitrary rectangular full-monomial-algebra pre/post linear controls, owned clean/copy/drop/reset workspace and saved-input identity bypass; five independent pure rank3 targets.',
                  excludes=['non-columnwise width-specific address operations',
                            'transformed nonmonomial helper resources',
                            'prefix taps, changed or internally interleaved paid word',
                            'changed target census or owner sizes'])
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads((HERE / 'RESULT.json').read_text()) == result, 'fixed exact receipt')
    print('PASS_EXACT_FREE_COMPLETION_OBSTRUCTION all25_blocks raw+fused schedules '
          'M00=6grade0+26grade2 X0_unique grade3_resource_rank4_not5 no_new_kappa')


if __name__ == '__main__':
    main()

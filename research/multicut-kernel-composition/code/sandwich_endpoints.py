#!/usr/bin/env python3
"""Exact rational checks of the shortened endpoints, the bank re-tiling and the new normalizers (SymPy), for the
cleanup-sandwich stage. Adapted from research/cleanup-sandwich-263/endpoints263.py (evmckinney9, Apache-2.0).

Address geometry is over Q with G = 9I - J; a frame with row basis B has projector P = B^T (B G B^T)^-1 B G.
banks: each retired helper keeps its rank-one entrance S and now ends at its four-dimensional frame F; since
P_S P_F = P_F P_S = P_S its completed relative endpoint is the partial swap D_(P_F - P_S) of rank 3 (completed-core
identity, research/community-round8-audit/BANK-SCHEDULE.md), so its bank residual changes from width 23 to width 3.
The width-120 bank patterns of the native bank review (run on the pre-sandwich word, whose helper entrances are
unchanged) are re-tiled and must fill every slot exactly.
normalizers: every new frame Gram matrix, every connector touching a new frame and every new endpoint has an exact
chart reducing it to a coordinate projector by elementary factors, all entries below 2^80.
usage: sandwich_endpoints.py EXPORT LEAD BANK_REVIEW_JSON OUTPUT_DIR
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json, struct, sys, time
import sympy as sp
if not __debug__: raise SystemExit('assertions required')
H = 24; BOUND = 2 ** 80; MAX_FACTORS = 548; G = 9 * sp.eye(H) - sp.ones(H)
X, L, BANK, O = map(Path, sys.argv[1:5]); t0 = time.time()
def load(p): return json.loads(Path(p).read_text())
receipt = load(L / 'CLEANUP-SANDWICH.json'); records = (L / 'COHORT249-RECORDS.bin').read_bytes()
frames = load(X / 'frames.json')['frames']; frames.update(load(L / 'COHORT249-FRAMES.json'))
new_frames = {str(e['frame']) for e in receipt['edits']}
def projector(f):
    d = frames[str(f)]['dim']
    if d == H: return sp.eye(H), None
    if d == 0: return sp.zeros(H), None
    B = sp.Matrix(frames[str(f)]['B']); gram = B * G * B.T
    return B.T * gram.inv() * B * G, gram
def make_guard():
    state = {'max': 1}
    def guard(values):
        for value in values:
            x = Q(value); state['max'] = max(state['max'], abs(x.numerator), x.denominator)
        assert state['max'] < BOUND, 'normalizer entry exceeds 2^80'
    return guard, state
def chart(E, rank, guard):
    C = sp.Matrix.hstack(*E.columnspace(), *E.nullspace()); inverse = C.inv()
    assert inverse * E * C == sp.diag(*([1] * rank + [0] * (H - rank))), 'chart does not normalize the projector'
    guard(list(E) + list(C) + list(inverse) + [C.det()])
    A = [[Q(x) for x in C.row(i)] for i in range(H)]; factors = 0
    for j in range(H):
        k = next(k for k in range(j, H) if A[k][j])
        if k != j: A[j], A[k] = A[k], A[j]; factors += 1
        pivot = A[j][j]; guard([pivot, 1 / pivot])
        if pivot != 1: A[j] = [x / pivot for x in A[j]]; factors += 1
        for i in range(H):
            if i != j and A[i][j]:
                c = A[i][j]; guard([c]); A[i] = [x - c * y for x, y in zip(A[i], A[j])]; factors += 1
    assert A == [[Q(i == j) for j in range(H)] for i in range(H)]
    assert factors <= MAX_FACTORS, 'chart exceeds the inherited factor bound'
    return factors
# banks
guard, state = make_guard()
for e in receipt['edits']:
    assert frames[str(e['entrance_frame'])]['dim'] == 1 and frames[str(e['frame'])]['dim'] == 4
    S, _ = projector(e['entrance_frame']); F, _ = projector(e['frame'])
    assert S * F == F * S == S, 'entrance is not inside the new exit frame'
    E = F - S; assert E * E == E and E.rank() == 3; chart(E, 3, guard)
bank = load(BANK); k = len(receipt['edits']); patterns = [dict(p) for p in bank['bank_patterns']]
# 40 replicas: k helpers x 40 width-23 residuals become width-3 residuals. 10k banks [23]*4+[4]*7 release their
# 40k width-23 slots; their 70k width-4 slots refill 7k/3 banks [4]*30 (k = 45: 105); the 40k width-3 residuals fill k banks [3]*40.
assert (70 * k) % 30 == 0, 'width-4 remainder'
next(p for p in patterns if p['widths'] == [23] * 4 + [4] * 7)['count'] -= 10 * k
next(p for p in patterns if p['widths'] == [4] * 30)['count'] += 70 * k // 30
patterns.append({'widths': [3] * 40, 'count': k})
family = Counter({int(r): c for r, c in bank['residual_families'].items()}); family[23] -= k; family[3] += k
slots, count = Counter(), 0
for p in patterns:
    assert p['count'] >= 0 and sum(p['widths']) == 120, 'bank pattern does not fill width 120'
    count += p['count']
    for r in p['widths']: slots[r] += p['count']
assert slots == Counter({r: 40 * c for r, c in family.items() if c}), 'residuals do not tile the banks exactly'
fewer = bank['banks_per_stage'] - count; assert fewer == 10 * k - 70 * k // 30 - k
banks = {'literal_stock': bank['literal_stock'] - 5 * fewer, 'banks_per_stage': count, 'banks_fewer_per_stage': fewer,
         'actual_role_replica_stage_assignments': bank['actual_role_replica_stage_assignments'], 'bank_patterns': patterns,
         'residual_families': {str(r): c for r, c in sorted(family.items()) if c}, 'endpoint_max_entry': state['max']}
# normalizers
guard, state = make_guard()
for f in new_frames:
    _, gram = projector(f); guard(list(gram) + list(gram.inv()) + [gram.det()])
pairs = {(b, c, r) for op, a, b, c, r, z in struct.iter_unpack('<6i', records) if op == 0 and (str(b) in new_frames or str(c) in new_frames)}
moves = len(pairs); pairs |= {(e['entrance_frame'], e['frame'], 3) for e in receipt['edits']}; most = 0
for before, after, rank in sorted(pairs):
    E = projector(after)[0] - projector(before)[0]
    assert E * E == E and E.rank() == rank, ('connector is not a projector of its rank', before, after)
    most = max(most, chart(E, rank, guard))
norm = {'new_frames': len(new_frames), 'move_pairs': moves, 'charts': len(pairs), 'max_factors': most, 'max_numerator_denominator': state['max']}
M = max(norm['max_numerator_denominator'], int(bank['max_intermediate_numerator']), int(bank['max_intermediate_denominator'])); U = 40 * M * M; g = 2 * U * U; assert g < 2 ** 80
invoice = dict(banks, normalized_stock=banks['literal_stock'] // 5, new_exact_charts=bank['new_exact_charts'] + k + norm['move_pairs'],
               max_new_chart_factors=max(bank['max_new_chart_factors'], norm['max_factors']) + 24, max_intermediate_numerator=str(g), max_intermediate_denominator=str(g),
               selector_charge=2 * 5 * 40 * (banks['literal_stock'] - 1 + 16587 * 120 * 787), routing_prime_guard={'normalized_scaled_chart_entry_bound': U, 'pairwise_difference_numerator_bound': g},
               status='PASS_SANDWICH_ENDPOINTS_EXACT_CHARTS_AND_BANK_RETILING', base_bank_review_sha256=__import__('hashlib').sha256(BANK.read_bytes()).hexdigest(), normalizers=norm)
assert banks['literal_stock'] % 5 == 0
O.mkdir(parents=True, exist_ok=True); (O / 'SANDWICH-BANK-INVOICE.json').write_text(json.dumps(invoice, indent=2) + '\n')
print('PASS sandwich endpoints: %d helpers, %d charts, max factors %d, banks per stage %d (-%d), literal stock %d, %.0fs' % (k, norm['charts'], most, count, fewer, banks['literal_stock'], time.time() - t0), flush=True)

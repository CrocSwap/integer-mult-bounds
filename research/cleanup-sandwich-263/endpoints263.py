"""Exact rational checks of the shortened endpoints, the bank tiling and the new normalizers (SymPy).

Address geometry is over Q with G = 9I - J; a frame with row basis B has projector P = B^T (B G B^T)^-1 B G.

`banks`: each retired helper keeps its rank-one entrance S and now ends at its four-dimensional frame F. Since
P_S P_F = P_F P_S = P_S, its completed relative endpoint is the partial swap D_(P_F - P_S) of rank 3, by the
inherited completed-core identity (research/community-round8-audit/BANK-SCHEDULE.md). Its bank residual therefore
changes from width 23 to width 3. The width-120 bank patterns are re-tiled and must fill every slot exactly.

`normalizers`: every new frame Gram matrix, every connector that touches a new frame and every new endpoint has an
exact chart reducing it to a coordinate projector by elementary factors, all with numerator and denominator below
2^80. Their nonzero factors are units modulo every admissible prime, as for the inherited charts.
"""
from collections import Counter
from fractions import Fraction as Q
import json
import struct

import sympy as sp

H = 24
BOUND = 2 ** 80
MAX_FACTORS = 548       # the inherited chart-factor bound of #259
G = 9 * sp.eye(H) - sp.ones(H)


def frames_of(replay, new_frames):
    def load(p): return json.loads(p.read_text())
    frames = load(replay / 'temporal/CURRENT249-EXPORT/frames.json')['frames']
    frames.update(load(replay / 'lead/COHORT249-FRAMES.json'))
    frames.update(new_frames)
    return frames


def projector(frames, f):
    d = frames[str(f)]['dim']
    if d == H:
        return sp.eye(H), None
    if d == 0:
        return sp.zeros(H), None
    B = sp.Matrix(frames[str(f)]['B'])
    gram = B * G * B.T
    return B.T * gram.inv() * B * G, gram


def chart(E, rank, guard):
    """Exact chart C with C^-1 E C = diag(1^rank, 0); returns (C, C^-1, elementary factor count)."""
    C = sp.Matrix.hstack(*E.columnspace(), *E.nullspace())
    inverse = C.inv()
    assert inverse * E * C == sp.diag(*([1] * rank + [0] * (H - rank))), 'chart does not normalize the projector'
    guard(list(E) + list(C) + list(inverse) + [C.det()])
    A = [[Q(x) for x in C.row(i)] for i in range(H)]
    factors = 0
    for j in range(H):
        k = next(k for k in range(j, H) if A[k][j])
        if k != j:
            A[j], A[k] = A[k], A[j]
            factors += 1
        pivot = A[j][j]
        guard([pivot, 1 / pivot])
        if pivot != 1:
            A[j] = [x / pivot for x in A[j]]
            factors += 1
        for i in range(H):
            if i != j and A[i][j]:
                c = A[i][j]
                guard([c])
                A[i] = [x - c * y for x, y in zip(A[i], A[j])]
                factors += 1
    assert A == [[Q(i == j) for j in range(H)] for i in range(H)]
    assert factors <= MAX_FACTORS, 'chart exceeds the inherited factor bound'
    return C, inverse, factors


def make_guard():
    state = {'max': 1}

    def guard(values):
        for value in values:
            x = Q(value)
            state['max'] = max(state['max'], abs(x.numerator), x.denominator)
        assert state['max'] < BOUND, 'normalizer entry exceeds 2^80'
    return guard, state


def banks(replay, new_frames, receipt):
    """Shortened endpoints are rank-3 partial swaps; re-tile the width-120 banks; return the new bank inventory."""
    frames = frames_of(replay, new_frames)
    guard, state = make_guard()
    for e in receipt['edits']:
        assert frames[str(e['entrance_frame'])]['dim'] == 1
        S, _ = projector(frames, e['entrance_frame'])
        F, _ = projector(frames, e['frame'])
        assert S * F == F * S == S, 'entrance is not inside the new exit frame'
        E = F - S
        assert E * E == E and E.rank() == 3
        chart(E, 3, guard)
    bank = json.loads((replay / 'compiler/COHORT-BANK-REVIEW.json').read_text())
    assert len(receipt['edits']) == 45
    patterns = [dict(p) for p in bank['bank_patterns']]
    # 40 replicas: 45 helpers x 40 = 1800 width-23 residuals become width-3 residuals.
    # 450 banks [23]*4 + [4]*7 release their 1800 width-23 slots; their 3150 width-4 slots refill 105 banks [4]*30;
    # the 1800 width-3 residuals fill 45 new banks [3]*40. Net: 300 fewer banks per stage, 1500 fewer in the stock.
    next(p for p in patterns if p['widths'] == [23] * 4 + [4] * 7)['count'] -= 450
    next(p for p in patterns if p['widths'] == [4] * 30)['count'] += 105
    patterns.append({'widths': [3] * 40, 'count': 45})
    family = Counter({int(r): c for r, c in bank['residual_families'].items()})
    family[23] -= 45
    family[3] += 45
    slots, count = Counter(), 0
    for p in patterns:
        assert p['count'] >= 0 and sum(p['widths']) == 120, 'bank pattern does not fill width 120'
        count += p['count']
        for r in p['widths']:
            slots[r] += p['count']
    assert slots == Counter({r: 40 * c for r, c in family.items() if c}), 'residuals do not tile the banks exactly'
    assert count == bank['banks_per_stage'] - 300
    return {'literal_stock': bank['literal_stock'] - 1500, 'banks_per_stage': count,
            'actual_role_replica_stage_assignments': bank['actual_role_replica_stage_assignments'],
            'bank_patterns': patterns, 'residual_families': {str(r): c for r, c in sorted(family.items()) if c},
            'endpoint_max_entry': state['max']}


def normalizers(replay, new_frames, records, receipt):
    """Charts for every new frame, every connector touching a new frame and every new endpoint."""
    frames = frames_of(replay, new_frames)
    guard, state = make_guard()
    for f in new_frames:
        _, gram = projector(frames, f)
        guard(list(gram) + list(gram.inv()) + [gram.det()])
    pairs = {(b, c, r) for op, a, b, c, r, z in struct.iter_unpack('<6i', records)
             if op == 0 and (str(b) in new_frames or str(c) in new_frames)}
    moves = len(pairs)
    pairs |= {(e['entrance_frame'], e['frame'], 3) for e in receipt['edits']}
    most = 0
    for before, after, rank in sorted(pairs):
        E = projector(frames, after)[0] - projector(frames, before)[0]
        assert E * E == E and E.rank() == rank, ('connector is not a projector of its rank', before, after)
        most = max(most, chart(E, rank, guard)[2])
    return {'new_frames': len(new_frames), 'move_pairs': moves, 'charts': len(pairs),
            'max_factors': most, 'max_numerator_denominator': state['max']}

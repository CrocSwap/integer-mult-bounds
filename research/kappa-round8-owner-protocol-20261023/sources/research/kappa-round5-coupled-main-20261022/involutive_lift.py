"""Native dyadic involutive 120-port completion of clean-J.

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
No closed recursive supplier or improved kappa is claimed.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

import lift_native as L

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def matrix(geo):
    B, C, _, _ = L.matrices(geo)
    T = [dict(row) for row in geo['J']]
    for i in range(112):
        T[i].update({112+k: -v for k, v in B[i].items()})
    T += [{**{i: 12*v for i, v in row.items()}, 112+k: Q(13)} for k, row in enumerate(C)]
    assert L.mm(T, T) == [{i: Q(1)} for i in range(120)]
    selected = geo['selected']
    D = [{k: row[a] for k, a in enumerate(selected) if row.get(a, 0)} for row in C]
    Dt = [{k: D[k][i] for k in range(8) if D[k].get(i, 0)} for i in range(8)]
    assert L.mm(D, Dt) == L.mm(Dt, D) == [{i: Q(1)} for i in range(8)]
    return B, C, T


def port_matrix(M, roles, frame):
    n = len(roles)
    work = [[M[i].get(j, Q(0)) for j in range(n)] for i in range(n)]
    elimination = []
    for j in range(n):
        pivot = next(i for i in range(j, n) if work[i][j])
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            elimination.append(['swap', j, pivot])
        if work[j][j] != 1:
            scale = 1/work[j][j]
            work[j] = [scale*x for x in work[j]]
            elimination.append(['scale', j, scale])
        for i in range(n):
            if i != j and work[i][j]:
                scale = -work[i][j]
                work[i] = [a+scale*b for a, b in zip(work[i], work[j])]
                elimination.append(['add', i, j, scale])
    out = []
    for op in reversed(elimination):
        if op[0] == 'swap':
            a, b = roles[op[1]], roles[op[2]]
            out += [L.add(a, b, Q(1), frame), L.add(b, a, Q(-1), frame), L.add(a, b, Q(1), frame), ['scalar', ['scale', ['L', b], -1, 1], frame]]
        elif op[0] == 'scale':
            q = 1/op[2]
            assert abs(q.numerator) & (abs(q.numerator)-1) == 0 and q.denominator & (q.denominator-1) == 0
            out.append(['scalar', ['scale', ['L', roles[op[1]]], q.numerator, q.denominator], frame])
        else:
            q = -op[3]
            assert q.denominator & (q.denominator-1) == 0
            out.append(L.add(roles[op[1]], roles[op[2]], q, frame))
    return out


def adapter(main, aux, geo, B, C, frame):
    selected = geo['selected']; ordinary = geo['ordinary']
    out = [['phase', 'involutive_lift_t_coordinate']]
    D = [{k: row[a] for k, a in enumerate(selected) if row.get(a, 0)} for row in C]
    Dt = [{k: D[k][i] for k in range(8) if D[k].get(i, 0)} for i in range(8)]
    Cprime = L.mm(Dt, C)
    Bprime = L.mm(B, D)
    assert all({i: v for i, v in row.items() if i in selected} == {selected[k]: Q(1)} for k, row in enumerate(Cprime))
    assert all(Bprime[a] == {k: Q(1)} for k, a in enumerate(selected))
    out += port_matrix(Dt, aux, frame)
    # V = D^t C X, stored at selected coordinates, while Z is D^t Z.
    for k, a in enumerate(selected):
        for i, q in sorted(Cprime[k].items()):
            if i in ordinary:
                out.append(L.add(main[a], main[i], q, frame))
    for k, a in enumerate(selected):
        out.append(L.add(main[a], aux[k], Q(1), frame))
    # t=V+Z is live at selected coordinates.
    for i in ordinary:
        for k, q in sorted(Bprime[i].items()):
            out.append(L.add(main[i], main[selected[k]], -q, frame))
    for k, a in enumerate(selected):
        out.append(L.add(aux[k], main[a], Q(12), frame))
        out.append(['scalar', ['scale', ['L', main[a]], -1, 1], frame])
        out.append(L.add(main[a], aux[k], Q(-1), frame))
    for k, a in enumerate(selected):
        for i, q in sorted(Cprime[k].items()):
            if i in ordinary:
                out.append(L.add(main[a], main[i], -q, frame))
    out += port_matrix(D, aux, frame)
    return out


def construct(base, geo, B, C, Z, W):
    extended, wrapped = {}, {}
    for d, program in base.items():
        pre = [['phase', 'involutive_cross_zero']]
        post = [['phase', 'involutive_cross_full']]
        if d == 'forward':
            for i, row in enumerate(B):
                for k, q in sorted(row.items()):
                    pre.append(L.add(112+i, Z[k], -q, 0))
            for k, row in enumerate(C):
                for i, q in sorted(row.items()):
                    post.append(L.add(W[k], i, 12*q, 1))
                post.append(L.add(W[k], Z[k], Q(13), 1))
        else:
            for k, row in enumerate(C):
                for i, q in sorted(row.items()):
                    pre.append(L.add(Z[k], 112+i, -12*q, 0))
                pre.append(L.add(Z[k], W[k], Q(-13), 0))
            for i, row in enumerate(B):
                for k, q in sorted(row.items()):
                    post.append(L.add(i, W[k], q, 1))
        extended[d] = pre+deepcopy(program)+post
        wrapped[d] = adapter(list(range(112, 224)), W, geo, B, C, 0)+extended[d]+adapter(list(range(112)), Z, geo, B, C, 1)
    return extended, wrapped


def main():
    began = time.monotonic()
    N = L.load(ROOT/'research/kappa-rebuild/complex/rebuild_native.py', 'involutive_rebuild')
    assert N.digest(N.P_PATH) == N.P_SHA and N.digest(N.BASE/'RESULT.json') == N.RECEIPT_SHA
    P = L.load(N.P_PATH, 'involutive_prune')
    assert N.digest(P.CHECKER) == P.CHECKER_SHA
    V = L.load(P.CHECKER, 'involutive_retained_verifier')
    packet = ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/certificate.json.gz'
    assert N.digest(packet) == 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7'
    receipt = L.read(N.BASE/'RESULT.json')
    for filename, pin in receipt['providers']['THREE-base']['artifacts'].items():
        assert N.digest(N.BASE/filename) == pin
    geo = N.geometry(packet)
    c = L.read(N.BASE/'THREE-base-CANONICAL.json.gz')
    base = L.read(N.BASE/'THREE-base-NATIVE-WORD.json.gz')
    cold = [r for r in range(224, 632) if c['start'][r] == 0 and c['final'][r] == 1]
    assert len(cold) == 213
    Z, W = cold[:8], cold[8:16]
    source, target = list(range(112))+Z, list(range(112, 224))+W
    B, C, T = matrix(geo)
    extended, wrapped = construct(base, geo, B, C, Z, W)
    checks = {}; oldexpected = V.expected
    for name, words in [('extended', extended), ('wrapped', wrapped)]:
        checks[name] = {}
        for d, program in words.items():
            oracle = lambda role: L.expected(V, role, source, target, T, T, d, name == 'wrapped')
            rec = L.replay(V, N, c, program, oracle, d)
            V.expected = lambda role, R, back, clean: oracle(role)
            try:
                rec['retained_operation_replay'] = V.replay(program, c, [], d == 'backward', False)
            finally:
                V.expected = oldexpected
            checks[name][d] = rec
            print('PASS_INVOLUTIVE_NATIVE_LIFT', name, d, rec['scalar_allowance'], flush=True)
    # Complete in-place adapter columns, including both auxiliary directions.
    for twice in [False, True]:
        rows = [{i: Q(1)} for i in range(120)]
        word = adapter(list(range(112)), list(range(112, 120)), geo, B, C, 0)
        for event in word*(2 if twice else 1):
            if event[0] == 'phase':
                continue
            gate = event[1]; dst = gate[1][1]
            if gate[0] == 'add':
                rows[dst] = plus(rows[dst], rows[gate[2][1]], Q(gate[3], gate[4]))
            else:
                q = Q(gate[2], gate[3]); rows[dst] = {j: q*v for j, v in rows[dst].items()}
        assert rows == ([{i: Q(1)} for i in range(120)] if twice else T)
    # Deliberately omit the new bottom-right 13Z contribution.
    bad = deepcopy(extended['forward'])
    cut = next(i for i, e in enumerate(bad) if e[0] == 'scalar' and e[1][0] == 'add' and e[1][1] == ['L', W[0]] and e[1][2] == ['L', Z[0]] and e[1][3:] == [13, 1])
    bad.pop(cut)
    rejected = False
    try:
        oracle = lambda role: L.expected(V, role, source, target, T, T, 'forward', False)
        L.replay(V, N, c, bad, oracle, 'forward')
    except AssertionError:
        rejected = True
    assert rejected
    payload = dict(canonical=c, source_roles=source, target_roles=target, extended=extended, wrapped=wrapped)
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    (HERE/'INVOLUTIVE-WORD.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    result = dict(status='PASS_EXACT_NATIVE_120_CHANNEL_DYADIC_INVOLUTION', author='Cao Yifan', new_kappa=False,
                  matrix='T=[[J,-B],[12C,13I8]], B=R^t/2, C=R/2, CB=14I8, J=I-BC',
                  T_squared_identity_all_120_columns=True,
                  in_place_adapter_all_120_columns=True,
                  adapter_used_twice_is_identity=True,
                  adapter_core_macros=dict(half_ADD=1248, unit_ADD=16, ADD12=8, negate=8),
                  adapter_basis_changes='Two explicit eight-port dyadic orthogonal basis changes, D=C_A and D^t, added around the core.',
                  checks=checks, source_auxiliaries=Z, target_auxiliaries=W,
                  remaining_independent_helper_mass=3157, paid_rank_mass=5093,
                  optimistic_unconverted_main_mass=1936, optimistic_unconverted_deficit=0,
                  ordinary_port_conversion_paid_H1=16, ordinary_port_conversion_target_mass_lost=16,
                  ordinary_120_port_main_mass=1920, converted_local_deficit=32,
                  omitted_13Z_negative_control_rejected=True,
                  word_payload_sha256=sha256(raw).hexdigest(),
                  source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), HERE/'lift_native.py', N.P_PATH, Path(P.CHECKER), packet, N.BASE/'RESULT.json', N.BASE/'THREE-base-CANONICAL.json.gz', N.BASE/'THREE-base-NATIVE-WORD.json.gz']},
                  scope='Actual 632-input native operation and new endpoint replay in both orientations; ZERO/FULL scalar contacts and an in-place involution adapter. No recursive caller closure, terminal Gaussian-job independence, finite-precision transfer or kappa improvement is claimed.',
                  seconds=time.monotonic()-began)
    (HERE/'INVOLUTIVE-LIFT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
    print(result['status'], round(result['seconds'], 3), flush=True)


def plus(a, b, q):
    out = dict(a)
    for j, v in b.items():
        out[j] = out.get(j, 0)+q*v
        if not out[j]:
            del out[j]
    return out


if __name__ == '__main__':
    main()

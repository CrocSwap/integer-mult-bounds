#!/usr/bin/env python3
"""Exact checks for the relay-hub normal form and its companions.  Python 3.12, standard library only.

Run:  python3 -B research/p104-relay-hub-normal-form/verify.py        (also with -O)
Expected marker: PASS_RELAY_HUB_NORMAL_FORM

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

Checks (exact Fraction/int arithmetic; every failure raises ValueError, so all checks stay active under -O):
  0. retained word bytes and payload digest against SOURCE-PINS.json and the digest published in #6824
  1. word model: frame legality, climbing public moves, descending private moves, exact endpoint A on all 772 rows
  2. up-set crossing bound (Prop. 2.1) and the odd-clique corollary, wall entries, all 759 maximum cliques
  3. hub normal form (Thm 3.1/3.2): decomposition, conditions, exact inverse, gauge re-solved from T alone,
     rewritten word (legality, identical MOVE events, exact endpoint), small instances and controls
  4. feed-forward corollary (Cor. 3.4) on random small instances and a control
  5. scheduling invariance (Prop. 4.1): random linear extensions of the register-order partial order
  6. pair-exchange law (Prop. 5.1): global frame check over all events, the literal exchange of registers 679/686
"""
import hashlib
import json
import random
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hubmodel import (Frames, check_legal, coeff, elementary, endpoint_matrix, event_frame, identity, load,  # noqa: E402
                      is_dyadic, mul, need, payload_sha, rank_exact, regs, replay, to_word_events)
from hub import classes, conditions, decompose, gauge, inverse  # noqa: E402

OUT = {}
PAYLOAD_6824 = 'd3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821'


def expect_error(fn, tag):
    try:
        fn()
    except ValueError as e:
        need(tag in str(e), ('wrong failure', tag, str(e)[:200]))
        return str(e)[:70]
    raise ValueError('control accepted: ' + tag)


# ---------------------------------------------------------------------------------------- 0 pins
def check_pins():
    pins = json.loads((HERE / 'retained/SOURCE-PINS.json').read_text())
    for p in pins:
        data = (HERE / p['local']).read_bytes()
        need(len(data) == p['bytes'], ('size', p['local']))
        need(hashlib.sha256(data).hexdigest() == p['sha256'], ('sha256', p['local']))
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == p['git_blob'], ('git blob', p['local']))
    word = load(HERE / 'retained/pr6824/WORD.json.gz')
    need(payload_sha(word) == PAYLOAD_6824 == pins[0]['payload_sha256'], 'payload digest of the #6824 native word')
    OUT['retained_inputs'] = len(pins)
    return word


def odd_matrix(word):
    ports = word['ports']
    return [[bin(a & b).count('1') & 1 for b in ports] for a in ports]


# -------------------------------------------------------------------------------- 1 and 2: wall
def check_model_and_wall(word, F):
    pub = word['public']
    census = check_legal(word)
    need((census['public_rise'], census['private_fall'], census['lifetimes']) == (3432, 24, 47), census)
    A = endpoint_matrix(word)
    rows, _ = replay(word, word['program'])
    need(rows == A, 'endpoint of the word is not I + E on all 772 rows')
    live, ports = word['live'], word['ports']
    for i, q in enumerate(ports):                      # ports, init and final frames of the main registers
        need(F.sets[word['initial'][live[i]]] == frozenset({0, q}), ('init of X', i))
        need(F.sets[word['final'][live[i] + 112]] == frozenset(v for v in range(512) if bin(v & q).count('1') % 2 == 0),
             ('final of Y', i))
        need(bin(q).count('1') % 2 == 1, 'port is not an odd vector')
    odd = odd_matrix(word)
    n = len(ports)
    OUT['model'] = dict(census, public=pub, ports=n)

    # all private moves cut: wall lemma on every entry
    prow, cuts = replay(word, word['program'], symbolic_cut=lambda e: True)
    need(len(cuts) == 24, 'descent count')
    nz = 0
    for j in range(pub):
        for k, v in prow[j].items():
            if isinstance(k, tuple):
                continue
            nz += 1
            need(F.sub(word['initial'][k], word['final'][j]), ('wall violated', k, j))
    odd_pairs = sum(map(sum, odd))
    odd_nonzero = sum(1 for s in range(n) for r in range(n)
                      if odd[s][r] and prow[live[s] + 112].get(live[r], 0))
    even_nonzero = sum(1 for s in range(n) for r in range(n)
                       if not odd[s][r] and prow[live[s] + 112].get(live[r], 0))
    need((odd_pairs, odd_nonzero, even_nonzero) == (5824, 0, 4972), (odd_pairs, odd_nonzero, even_nonzero))

    # odd cliques: Bron-Kerbosch with pivoting on the odd graph (off-diagonal)
    adj = [sum(1 << j for j in range(n) if j != i and odd[i][j]) for i in range(n)]
    cliques = []

    def bk(Rm, Pm, Xm, k):
        if not Pm:
            if not Xm:
                cliques.append((k, Rm))
            return
        cand = Pm | Xm
        pv = max((v for v in range(n) if cand >> v & 1), key=lambda v: bin(Pm & adj[v]).count('1'))
        for v in [v for v in range(n) if (Pm & ~adj[pv]) >> v & 1]:
            bk(Rm | 1 << v, Pm & adj[v], Xm & adj[v], k + 1)
            Pm &= ~(1 << v)
            Xm |= 1 << v
    bk(0, (1 << n) - 1, 0, 0)
    omega = max(k for k, _ in cliques)
    top = [m for k, m in cliques if k == omega]
    need(omega == 8 and len(top) == 759, ('clique number', omega, len(top)))

    descents = [(e[2], e[3]) for e in word['program'] if e[0] == 'MOVE' and e[4]]

    def in_up(f, S):                                   # frame f lies in the up-set generated by the lines of S
        return any(F.sub(word['initial'][live[i]], f) for i in S)

    def crossing(S):
        return sum(1 for a, b in descents if in_up(a, S) and not in_up(b, S))

    stats = Counter()
    for m in top:
        S = [i for i in range(n) if m >> i & 1]
        stats[crossing(S)] += 1
    need(stats == Counter({8: 759}), stats)
    # the sub-cliques: rank of A[J,I] equals |S| and the replay with only crossing descents cut has no J x I flow
    for S in ([i for i in range(n) if top[0] >> i & 1][:k] for k in (1, 3, 8)):
        sIn = set(i for i in range(word['public']) if in_up(word['initial'][i], S))
        sJ = [j for j in range(word['public']) if not in_up(word['final'][j], S)]
        sub = [{k: v for k, v in A[j].items() if k in sIn} for j in sJ]
        rk = rank_exact(sub, word['public'])
        need(rk == len(S), ('rank A[J,I]', rk, len(S)))
        rows2, cuts2 = replay(word, word['program'],
                              symbolic_cut=lambda e, S=S: in_up(e[2], S) and not in_up(e[3], S))
        for j in sJ:
            need(all(isinstance(k, tuple) or k not in sIn for k in rows2[j]), 'public flow leaves the up-set')
        need(len(cuts2) >= len(S), 'crossing descents fewer than the rank')
    OUT['wall'] = dict(nonzero_public_entries=nz, odd_pairs=odd_pairs, odd_nonzero=odd_nonzero, even_nonzero=even_nonzero,
                       even_pairs=n * n - odd_pairs, clique_number=omega, maximum_cliques=len(top),
                       crossing_descents_per_maximum_clique=dict(stats), descents=24)

    # controls: a climbing public move turned into a descent is rejected by the legality check
    prog = [list(e) for e in word['program']]
    i = next(i for i, e in enumerate(prog) if e[0] == 'MOVE' and e[1] < pub)
    prog[i][2], prog[i][3] = prog[i][3], prog[i][2]
    OUT['wall_controls'] = dict(reversed_public_move=expect_error(lambda: check_legal(word, prog), 'move'))


# ------------------------------------------------------------------------------------ 3: hub form
def check_hub(word, F):
    pub = word['public']
    P = word['program']
    cl = classes(word, F)
    K, R = cl['K'], cl['R']
    lab, pure = decompose(word, F, P)
    need(Counter(lab) == Counter({None: 7356, 'pre': 5766, 'post': 5500}), Counter(lab))
    pre = [e for e, l in zip(P, lab) if l == 'pre']
    mid = [e for e, l in zip(P, lab) if l is None]
    post = [e for e, l in zip(P, lab) if l == 'post']
    sK, sR = set(K), set(R)
    for e in pre:                                       # pre events: zero frame, registers in K
        need(event_frame(e) == F.zero and all(r in sK for r in regs(e)), ('pre event', e))
    for e in post:                                      # post events: full frame, public registers in R or pure private
        need(event_frame(e) == F.full or e[0] in ('INIT', 'CLEAR'), ('post event', e))
        need(all(r in sR or r >= pub for r in regs(e)), ('post event outside R', e))
    # same per-register event sequences as the word
    def seqs(order):
        d = {}
        for i in order:
            for r in set(regs(P[i])):
                d.setdefault(r, []).append(i)
        return d
    idx = [i for i, l in enumerate(lab) if l == 'pre'] + [i for i, l in enumerate(lab) if l is None] + \
          [i for i, l in enumerate(lab) if l == 'post']
    need(seqs(idx) == seqs(range(len(P))), 'pre + mid + post does not preserve per-register sequences')
    need(check_legal(word, [P[i] for i in idx])['lifetimes'] == 47, 'reordered word is legal')

    A = endpoint_matrix(word)
    T, _ = replay(word, mid)
    G0w, _ = replay(word, pre)
    G9w, _ = replay(word, post)
    need(mul(G9w, mul(T, G0w)) == A, 'G9 T G0 = A for the word itself')
    Ainv = [dict(r) for r in A]
    for r in word['live']:
        Ainv[r + 112][r] = Q(-1)
    Tinv = mul(G0w, mul(Ainv, G9w))
    need(mul(T, Tinv) == identity(pub) and mul(Tinv, T) == identity(pub), 'exact inverse of T')
    dens = sorted({v.denominator for row in Tinv for v in row.values()})
    need(all(d & (d - 1) == 0 for d in dens), 'T^-1 is dyadic')
    cond = conditions(T, Tinv, A, Ainv, K, R, pub)
    need(all(cond.values()), cond)
    sub = [{c: v for c, v in T[r].items() if c in sK} for r in R]
    rk = rank_exact(sub, pub)
    need(rk == len(cl['H09']) == 359, ('rank T[R,K]', rk))

    # re-solve both hubs from T and its inverse alone, then rebuild the word
    G0, D, G9 = gauge(T, Tinv, A, K, R, pub)
    e0 = elementary(G0, K)
    e9 = elementary(G9, R)
    new = to_word_events(e0, F.zero) + mid + to_word_events(e9, F.full)
    census = check_legal(word, new)
    need([e for e in new if e[0] == 'MOVE'] == [e for e in P if e[0] == 'MOVE'], 'MOVE events unchanged')
    rows, _ = replay(word, new)
    need(rows == A, 'rewritten word has endpoint I + E on all 772 rows')
    need(all(is_dyadic(coeff(e)) for e in new if e[0] in ('ADD', 'COPY', 'SCALE')), 'all coefficients dyadic')
    sY = set(cl['Y'])
    ff = dict(rows_X_are_unit_rows=all(T[x] == {x: Q(1)} for x in cl['X']),
              columns_Y_zero_outside_Y=all(not (set(T[r]) & sY) for r in range(pub) if r not in sY),
              helpers_all_span9=not (cl['H0n'] or cl['Hn9'] or cl['Hnn']))
    need(not all(ff.values()), 'the literal word is not feed-forward')
    old_gauge = (len(pre), len(post))
    OUT['hub'] = dict(K=len(K), R=len(R), J=len(cl['Y']) + len(cl['H0n']), H09=len(cl['H09']), Hnn=len(cl['Hnn']),
                      pre_events=old_gauge[0], post_events=old_gauge[1], mid_events=len(mid),
                      T_nonzeros=sum(len(r) for r in T), inverse_denominators=dens, rank_T_RK=rk,
                      conditions=cond, new_pre=len(e0), new_post=len(e9), new_events=len(new),
                      pure_private_lifetimes_removed=len(pure), lifetimes_after=census['lifetimes'],
                      feed_forward_hypotheses=ff)
    return T, Tinv, A, cl


def tiny(rows):
    return [{j: Q(v) for j, v in enumerate(r) if v} for r in rows]


def check_small():
    ctl = {}
    # (a) Hnn nonempty: C1 and C3 hold, C2 fails, no gauge.  Registers (a, b): a in Hnn, b in K and R.
    T = tiny([[1, 0], [1, 1]])
    A = tiny([[1, 0], [0, 1]])
    Ti = inverse(T)
    K, R = [1], [1]
    cond = conditions(T, Ti, A, A, K, R, 2)
    need(cond == {'C1': True, 'C2': False, 'C2p': True, 'C3': True}, cond)
    for g0 in (Q(2) ** k * s for k in range(-4, 5) for s in (1, -1)):
        for g9 in (Q(2) ** k * s for k in range(-4, 5) for s in (1, -1)):
            G0, G9 = tiny([[1, 0], [0, 0]]), tiny([[1, 0], [0, 0]])
            G0[1] = {1: g0}
            G9[1] = {1: g9}
            need(mul(G9, mul(T, G0)) != A, 'a gauge exists in the Hnn toy')
    ctl['hnn_two_conditions_insufficient'] = expect_error(lambda: gauge(T, Ti, A, K, R, 2), 'conditions fail')
    # (b) over Q only: T = [3] on one helper with initial zero and final full is not in GL(Z[1/2])
    T = tiny([[3]])
    A = tiny([[1]])
    ctl['not_dyadic'] = expect_error(lambda: gauge(T, inverse(T), A, [0], [0], 1), 'not in GL')
    # (c) conditions fail on a perturbed T of the literal system is covered in check_hub_controls
    OUT['small_controls'] = ctl


def check_hub_controls(word, F, T, Tinv, A, cl):
    pub = word['public']
    K, R = cl['K'], cl['R']
    Ainv = [dict(r) for r in A]
    for r in word['live']:
        Ainv[r + 112][r] = Q(-1)
    ctl = {}
    sK, sR = set(K), set(R)
    Rb = [r for r in range(pub) if r not in sR]
    Kb = [r for r in range(pub) if r not in sK]
    # C1: change one entry of T[Rbar, Kbar]
    T1 = [dict(r) for r in T]
    i, j = Rb[0], Kb[0]
    T1[i][j] = T1[i].get(j, 0) + 1
    need(not conditions(T1, Tinv, A, Ainv, K, R, pub)['C1'], 'C1 control')
    ctl['C1'] = 'flagged'
    # C2: put weight on T[R, Hnn]
    T2 = [dict(r) for r in T]
    h = cl['Hnn'][0]
    T2[R[0]][h] = T2[R[0]].get(h, 0) + 1
    need(not conditions(T2, Tinv, A, Ainv, K, R, pub)['C2'], 'C2 control')
    ctl['C2'] = 'flagged'
    # C2': put weight on T[Hnn, K]
    T3 = [dict(r) for r in T]
    T3[h][K[0]] = T3[h].get(K[0], 0) + 1
    need(not conditions(T3, Tinv, A, Ainv, K, R, pub)['C2p'], "C2' control")
    ctl["C2'"] = 'flagged'
    # a perturbed T is rejected by the gauge builder (not the inverse of the supplied matrix)
    ctl['gauge_rejects_perturbed'] = expect_error(lambda: gauge(T1, Tinv, A, K, R, pub), 'conditions fail')
    OUT['hub_controls'] = ctl


# ------------------------------------------------------------------------------- 4: feed-forward
def feed_forward(rng, nx, h, bad=False):
    """X: 0..nx-1, Y: nx..2nx-1, H: 2nx..; mid T with X rows fixed, Y never read, T[Y,X] = I."""
    n = 2 * nx + h
    Xs, Ys, Hs = list(range(nx)), list(range(nx, 2 * nx)), list(range(2 * nx, n))
    T = [dict() for _ in range(n)]
    for i in Xs:
        T[i][i] = Q(1)
    for i in range(nx):
        T[Ys[i]][Ys[i]] = Q(1)
        T[Ys[i]][Xs[i]] = Q(1)
        for c in Hs:
            if rng.random() < 0.5:
                T[Ys[i]][c] = Q(rng.randint(-2, 2), 2)
                if not T[Ys[i]][c]:
                    del T[Ys[i]][c]
    for a in Hs:                                         # T[H,H]: product of random dyadic elementary matrices
        T[a][a] = Q(1)
    for _ in range(4 * h if h > 1 else 0):
        d, s = rng.sample(Hs, 2)
        c = Q(rng.choice([-2, -1, 1, 2]), rng.choice([1, 2]))
        for k, v in list(T[s].items()):
            if k in Hs:
                T[d][k] = T[d].get(k, 0) + c * v
                if not T[d][k]:
                    del T[d][k]
    for a in Hs:
        for i in Xs:
            if rng.random() < 0.5:
                T[a][i] = Q(rng.randint(-3, 3), 2)
                if not T[a][i]:
                    del T[a][i]
    if bad:                                              # T[H,H] with determinant 3: invertible over Q only
        T[Hs[0]] = {k: 3 * v for k, v in T[Hs[0]].items()}
    A = identity(n)
    for i in range(nx):
        A[Ys[i]][Xs[i]] = Q(1)
    return T, A, Ys + Hs, Xs + Hs, n


def check_feed_forward():
    rng = random.Random(20261107)
    done = 0
    for trial in range(30):
        nx, h = rng.randint(1, 4), rng.randint(1, 5)
        T, A, K, R, n = feed_forward(rng, nx, h)
        Ti = inverse(T)
        G0, D, G9 = gauge(T, Ti, A, sorted(K), sorted(R), n)
        need(mul(G9, mul(T, G0)) == A, 'feed-forward gauge')
        done += 1
    T, A, K, R, n = feed_forward(rng, 2, 3, bad=True)
    ctl = expect_error(lambda: gauge(T, inverse(T), A, sorted(K), sorted(R), n), 'not in GL')
    OUT['feed_forward'] = dict(random_instances=done, control_T_HH_det3=ctl)


# ------------------------------------------------------------------------------- 5: scheduling
def linear_extension(program, rng):
    last, succ, indeg = {}, [[] for _ in program], [0] * len(program)
    for i, e in enumerate(program):
        for r in set(regs(e)):
            if r in last:
                succ[last[r]].append(i)
                indeg[i] += 1
            last[r] = i
    ready = [i for i in range(len(program)) if indeg[i] == 0]
    order = []
    while ready:
        k = rng.randrange(len(ready))
        ready[k], ready[-1] = ready[-1], ready[k]
        i = ready.pop()
        order.append(i)
        for j in succ[i]:
            indeg[j] -= 1
            if indeg[j] == 0:
                ready.append(j)
    need(len(order) == len(program), 'cycle')
    return order


def peak(program):
    live = best = 0
    for e in program:
        if e[0] == 'INIT':
            live += 1
            best = max(best, live)
        elif e[0] == 'CLEAR':
            live -= 1
    return best


def invoice(word, program, F):
    pub = word['public']
    main = set(word['live']) | {r + 112 for r in word['live']}
    helpers = Counter(F.dim[word['final'][r]] - F.dim[word['initial'][r]] for r in range(pub) if r not in main)
    moves = Counter(abs(F.dim[e[3]] - F.dim[e[2]]) for e in program if e[0] == 'MOVE')
    return helpers, moves


def check_schedule(word, F):
    P = word['program']
    A = endpoint_matrix(word)
    base_inv = invoice(word, P, F)
    rng = random.Random(6831)
    peaks, moved = [peak(P)], 0
    for t in range(10):
        order = linear_extension(P, rng)
        prog = [P[i] for i in order]
        moved += sum(1 for a, b in zip(order, order[1:]) if b < a)
        check_legal(word, prog)
        need(invoice(word, prog, F) == base_inv, 'invoice histograms depend on the schedule')
        rows, _ = replay(word, prog)
        need(rows == A, 'endpoint depends on the schedule')
        peaks.append(peak(prog))
    # control: exchanging a MOVE with the next event of the same register is not a linear extension
    i = next(i for i, e in enumerate(P) if e[0] == 'MOVE' and e[1] < word['public'])
    j = next(j for j in range(i + 1, len(P)) if P[i][1] in regs(P[j]) and P[j][0] != 'MOVE')
    bad = list(P)
    bad[i], bad[j] = bad[j], bad[i]
    ctl = expect_error(lambda: check_legal(word, bad), 'co-rest')
    OUT['schedule'] = dict(schedules=10, order_inversions_total=moved, owned_peak_original=peaks[0],
                           owned_peak_min=min(peaks), owned_peak_max=max(peaks),
                           helper_rank_histogram=sorted(base_inv[0].items()), move_rank_histogram=sorted(base_inv[1].items()),
                           control_move_swapped_past_its_event=ctl)


# ------------------------------------------------------------------------------ 6: pair exchange
def event_reach(word, cut_descents):
    """For every event, the bit set of public registers whose final value depends on the value the event writes,
    along dependency paths; with cut_descents the paths may not pass through a private MOVE."""
    pub = word['public']
    P = word['program']
    reach = [(1 << r) if r < pub else 0 for r in range(pub + word['owned_fields'])]
    ev = [0] * len(P)
    for i in range(len(P) - 1, -1, -1):
        e = P[i]
        o = e[0]
        if o in ('ADD', 'COPY'):
            ev[i] = reach[e[1]]
            reach[e[2]] |= reach[e[1]]
            if o == 'COPY':
                reach[e[1]] = 0
        elif o == 'SCALE':
            ev[i] = reach[e[1]]
        elif o in ('INIT', 'CLEAR'):
            reach[e[1]] = 0
        elif o == 'MOVE' and cut_descents and e[4]:
            reach[e[1]] = 0
    return ev


def check_exchange(word, F):
    pub = word['public']
    P = word['program']
    final = word['final']
    ev = event_reach(word, True)
    allowed = {}
    pairs = 0
    for i, e in enumerate(P):
        if e[0] in ('ADD', 'COPY', 'SCALE'):
            G = e[-1]
            if G not in allowed:
                allowed[G] = sum(1 << s for s in range(pub) if F.sub(G, final[s]))
            need(ev[i] & ~allowed[G] == 0, ('event frame not inside the final frame of a sink it feeds', i, e))
            pairs += bin(ev[i]).count('1')
    # control: without the cut at private descents the inclusion fails (content is carried down by a private register)
    ev2 = event_reach(word, False)
    violations = sum(1 for i, e in enumerate(P) if e[0] in ('ADD', 'COPY', 'SCALE') and ev2[i] & ~allowed[e[-1]])
    need(violations > 0, 'control: uncut reach should violate the inclusion')
    # the literal exchange of registers 679 and 686 at frame 1011
    i1 = next(i for i, e in enumerate(P) if e == ['ADD', 679, 686, '1', 1011])
    i2 = next(i for i, e in enumerate(P) if e == ['ADD', 686, 679, '-1/2', 1011])
    need(i2 == i1 + 1, 'the two exchange events are consecutive')
    s1, s2 = 164, 218
    need(ev[i1] >> s1 & 1 and ev[i2] >> s2 & 1, 'outputs of the exchange reach the sinks 164 and 218 without a descent')
    F1, F2, G = final[s1], final[s2], 1011
    meet = F.sets[F1] & F.sets[F2]
    need((F.dim[F1], F.dim[F2], len(meet).bit_length() - 1, F.dim[G]) == (8, 8, 7, 7), 'dimensions 8, 8, 7, 7')
    need(F.sets[G] == meet, 'the exchange frame equals the intersection of the two sink frames')
    for f in (881, 888, 1049, 3):                       # earlier frames of the two inputs sit inside the exchange frame
        need(F.sub(f, G), ('input frame inside the exchange frame', f))
    need(not F.sub(F1, F2) and not F.sub(F2, F1), 'neither sink frame contains the other')
    OUT['exchange'] = dict(events_checked=sum(1 for e in P if e[0] in ('ADD', 'COPY', 'SCALE')), event_sink_pairs=pairs,
                           uncut_violations=violations,
                           instance=dict(first=i1, second=i2, sinks=[s1, s2], sink_frames=[F1, F2], exchange_frame=G),
                           dims=dict(sink=8, intersection=7, exchange_frame=7))


def main():
    word = check_pins()
    F = Frames(word)
    check_model_and_wall(word, F)
    T, Tinv, A, cl = check_hub(word, F)
    check_small()
    check_hub_controls(word, F, T, Tinv, A, cl)
    check_feed_forward()
    check_schedule(word, F)
    check_exchange(word, F)
    print(json.dumps(OUT, indent=1, sort_keys=True, default=str))
    print('PASS_RELAY_HUB_NORMAL_FORM')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Network-coded owned carriers on the PR6030 P104 word: finite facts for the Lean lemmas.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.

Checks:
  1. exact replay of the PR6030 word: frame rules (public ascents, owned strict descents, common-chart arithmetic),
     endpoint rows, owned lifetimes, owned-to-owned transfers, read dimensions, and the crossing profile of the seven
     dimension cuts of p104-owned-coding-boundaries (8 crossings on every level 2..8, owned paid 56);
  2. Y_j final frame = p_j^perp with p_j . p_j = 1, so X_j and Y_j never share a frame;
  3. the eight dimension-1 delivery lines l_c are the eight removed E8 root lines that carry deliveries; carrier
     contents s_c (52 live coordinates, +-1/4) are collected in G_c = span of their ports (dimension 8, normal g_c);
     receivers R_c = {j : p_j . l_c = 0} (52 each); <g_c> + span p_{R_c} = l_c^perp; g_a . l_c = [a != c];
  4. Lemma S equality: dual walk cost dim(<g_c> + span p_{R_c}) - 1 = binary rank of the pairing [p_j . p_i] = 7;
  5. the masked decoder: on the costly pairs of every port j (p_i . p_j = 1, i = j included) the eight carrier
     rows have rank 8, so d_j is unique; d_jc = +-2 exactly on the carriers with j in R_c;
  6. htop facts of Lean `merge_count`: <g_a, g_c> + span p_{R_c} = F2^9 for every a != c;
  7. Lean `pair_merge` finite fact `nocover`: for every pair {a, b} and ratio +-1, no two subspaces containing
     <g_a, g_b>, each of dimension <= 6, cover the non-proportional receivers N;
  8. the computed record equals RESULT.json.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, itertools, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL ' + why)


def log(kind, **data):
    print(kind, json.dumps(data, sort_keys=True, default=str)[:300], flush=True)


def dot(a, b):
    return bin(a & b).count('1') & 1


def rank(vs):
    b = []
    for v in vs:
        for x in b:
            v = min(v, v ^ x)
        if v:
            b.append(v)
    return len(b)


def span(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    return frozenset(s)


def normals(vs):
    return [u for u in range(1, 512) if all(dot(u, v) == 0 for v in vs)]


def qrank(rows):
    m = [list(r) for r in rows]
    r = 0
    for c in range(len(m[0]) if m else 0):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c] / m[r][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[r])]
        r += 1
    return r


def qsolve(A, b):
    """Unique exact solution of A x = b (A has full column rank), else None."""
    n = len(A[0])
    m = [list(r) + [bb] for r, bb in zip(A, b)]
    r = 0
    piv = []
    for c in range(n):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            return None
        m[r], m[p] = m[p], m[r]
        inv = 1 / m[r][c]
        m[r] = [x * inv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[r])]
        piv.append(c)
        r += 1
    if any(m[i][n] != 0 for i in range(r, len(m))):
        return None
    return [m[i][n] for i in range(n)]


def replay(w):
    S = [span(b) for b in w['frames']]
    dims = [len(b) for b in w['frames']]
    n, m = w['public'], w['owned_fields']
    live = list(w['live'])
    lset = set(live)
    cur = list(w['initial']) + [None] * m
    rows = [{r: Q(1)} for r in range(n + m)]
    owned = set()
    lifetimes, life = [], {}
    deliveries = {}
    reads = Counter()
    o2o = 0
    for e in w['program']:
        op, r = e[0], e[1]
        if op == 'MOVE':
            a, b, private = e[2], e[3], e[4]
            need(cur[r] == a and (r in owned) == private, 'move source')
            need(S[b] < S[a] if private else S[a] < S[b], 'strict nesting')
            cur[r] = b
            if private:
                life[r]['path'].append(dims[b])
            continue
        if op == 'INIT':
            need(r >= n and r not in owned, 'init')
            owned.add(r)
            cur[r] = e[2]
            rows[r] = {}
            life[r] = {'path': [dims[e[2]]]}
            lifetimes.append(life[r])
            continue
        if op == 'CLEAR':
            need(r in owned and cur[r] == e[2], 'clear')
            owned.discard(r)
            cur[r] = None
            rows[r] = {}
            continue
        q, f = Q(e[-2]), e[-1]
        need(q != 0 and cur[r] == f, 'destination chart')
        if op == 'SCALE':
            rows[r] = {k: q * v for k, v in rows[r].items()}
            continue
        s = e[2]
        need(cur[s] == f, 'common chart')
        if s >= n and r >= n:
            o2o += 1
        if s >= n and r < n:
            reads[dims[f]] += 1
            if dims[f] == 1:
                line = min(v for v in S[f] if v)
                vec = {k: v for k, v in rows[s].items() if k in lset}
                deliveries.setdefault(line, []).append(vec)
        if op == 'COPY':
            need(r in owned and not rows[r], 'copy')
            rows[r] = {k: q * v for k, v in rows[s].items()}
        else:
            need(op == 'ADD', 'opcode')
            t = dict(rows[r])
            for k, v in rows[s].items():
                x = t.get(k, 0) + q * v
                if x:
                    t[k] = x
                else:
                    t.pop(k, None)
            rows[r] = t
    need(not owned and cur[:n] == w['final'], 'exits')
    for r in range(n):
        exp = {r: Q(1)}
        if r - 112 in lset:
            exp[r - 112] = Q(1)
        need(rows[r] == exp, 'endpoint row %d' % r)
    return lifetimes, deliveries, reads, o2o


def subspaces(nn, d):
    out = []
    for piv in itertools.combinations(range(nn), d):
        free = [(r, c) for r in range(d) for c in range(piv[r] + 1, nn) if c not in piv]
        for bits in range(1 << len(free)):
            rows = [1 << piv[r] for r in range(d)]
            for t, (r, c) in enumerate(free):
                if bits >> t & 1:
                    rows[r] |= 1 << c
            out.append(span(rows))
    return out


def main():
    src = json.loads((HERE / 'SOURCES.json').read_text())
    for row in src['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin ' + row['path'])
    w = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    P = w['ports']
    live = list(w['live'])
    lidx = {r: k for k, r in enumerate(live)}
    res = {}

    # 1. replay and cut profile
    lifetimes, deliveries, reads, o2o = replay(w)
    cross = Counter()
    paid = 0
    for L in lifetimes:
        for a, b in zip(L['path'], L['path'][1:]):
            paid += a - b
            for k in range(b + 1, a + 1):
                cross[k] += 1
    res['word'] = {'owned_lifetimes': len(lifetimes), 'owned_to_owned_adds': o2o, 'owned_paid': paid,
                   'cut_crossings_levels_1_to_9': [cross[k] for k in range(1, 10)],
                   'owned_reads_by_frame_dim': {str(k): v for k, v in sorted(reads.items())}}
    need(paid == 56 and all(cross[k] == 8 for k in range(2, 9)), 'cut profile')
    log('REPLAY', **res['word'])

    # 2. Y_j final frame
    S = [span(b) for b in w['frames']]
    yn = []
    for k, r in enumerate(live):
        nv = normals([v for v in S[w['final'][r + 112]] if v])
        need(len(nv) == 1 and nv[0] == P[k] and dot(P[k], P[k]) == 1, 'Y final = p^perp')
        need(min(v for v in S[w['initial'][r]] if v) == P[k] and len(S[w['initial'][r]]) == 2, 'X start = <p>')
        yn.append(nv[0])
    res['frames'] = {'Y_final_is_p_perp': 104, 'X_start_is_p_line': 104, 'p_dot_p_is_1': 104}

    # 3. carriers
    lines = sorted(deliveries)
    need(len(lines) == 8, 'eight delivery lines')
    carriers = []
    for l in lines:
        vecs = {json.dumps(sorted((lidx[k], str(v)) for k, v in d.items())) for d in deliveries[l]}
        need(len(vecs) == 1, 'one content per line')
        d0 = deliveries[l][0]
        carriers.append({lidx[k]: v for k, v in d0.items()})
    weight3or7 = [q for q in range(512) if bin(q).count('1') in (3, 7)]
    removed = [q for q in weight3or7 if q not in P]
    need(len(removed) == 16 and all(l in removed for l in lines), 'lines are removed root lines')
    g, R = [], []
    for c, l in enumerate(lines):
        s = carriers[c]
        need(len(s) == 52 and set(abs(v) for v in s.values()) == {Q(1, 4)}, 'carrier content')
        ports = [P[i] for i in s]
        need(rank(ports) == 8, 'G_c dim 8')
        nv = normals(ports)
        need(len(nv) == 1, 'normal')
        g.append(nv[0])
        R.append([j for j in range(104) if dot(P[j], l) == 0])
        need(len(R[c]) == 52, '52 receivers')
        need(rank([g[c]] + [P[j] for j in R[c]]) == 8 and all(dot(v, l) == 0 for v in [g[c]] + [P[j] for j in R[c]]),
             '<g_c> + p_R = l^perp')
    gl = [[dot(g[a], lines[c]) for a in range(8)] for c in range(8)]
    need(all(gl[c][a] == (a != c) for a in range(8) for c in range(8)), 'g_a . l_c = [a != c]')
    res['carriers'] = {'lines': lines, 'normals_g': g, 'support_sizes': [len(s) for s in carriers],
                       'receivers': [len(r) for r in R], 'g_dot_l_is_offdiagonal_one': True}
    log('CARRIERS', lines=lines, g=g)

    # 4. Lemma S equality: dual walk cost = F2 pairing rank = 7
    walk = [rank([g[c]] + [P[j] for j in R[c]]) - 1 for c in range(8)]
    pair = [rank([sum(dot(P[j], P[i]) << t for t, i in enumerate(sorted(carriers[c]))) for j in R[c]])
            for c in range(8)]
    need(walk == [7] * 8 and pair == [7] * 8, 'Lemma S equality')
    res['lemma_S'] = {'dual_walk_cost': walk, 'pairing_rank': pair}

    # 5. masked decoder
    D = []
    for j in range(104):
        costly = [i for i in range(104) if dot(P[i], P[j]) == 1]
        A = [[carriers[c].get(i, Q(0)) for c in range(8)] for i in costly]
        need(qrank(A) == 8, 'unique decoder row')
        x = qsolve(A, [Q(1) if i == j else Q(0) for i in costly])
        need(x is not None, 'decoder solvable')
        need(all((x[c] != 0) == (j in R[c]) for c in range(8)) and all(v in (0, 2, -2) for v in x), 'decoder support')
        D.append(x)
    res['decoder'] = {'unique_rows': 104, 'values': [-2, 2], 'support_equals_receivers': True,
                      'carriers_per_port': dict(sorted(Counter(sum(1 for v in d if v) for d in D).items()))}

    # 6. htop facts
    for a in range(8):
        for c in range(8):
            if a != c:
                need(rank([g[a], g[c]] + [P[j] for j in R[c]]) == 9, 'htop')
    res['merge_count_htop'] = {'pairs': 56}

    # 7. pair nocover
    S4 = subspaces(7, 4)
    need(len(S4) == 11811, 'subspace count')
    rows = []
    for a, b in itertools.combinations(range(8), 2):
        G = [g[a], g[b]]
        Gb = []
        for v in sorted(G, reverse=True):
            for x in Gb:
                v = min(v, v ^ x)
            Gb.append(v)
            Gb.sort(reverse=True)

        def red(v):
            for x in Gb:
                v = min(v, v ^ x)
            return v
        comp = []
        for e in range(9):
            if rank([red(c) for c in comp] + [red(1 << e)]) > len(comp):
                comp.append(1 << e)
        coord = {}
        for mm in range(128):
            x = 0
            for i in range(7):
                if mm >> i & 1:
                    x ^= red(comp[i])
            coord[x] = mm
        need(len(coord) == 128, 'quotient')
        for lam in (1, -1):
            N = [j for j in range(104) if (D[j][a] or D[j][b]) and not (D[j][a] and D[j][b] and D[j][b] == lam * D[j][a])]
            Nq = [coord[red(P[j])] for j in N]
            feas = sum(1 for Sx in S4 if rank([x for x in Nq if x not in Sx]) <= 4)
            need(feas == 0, 'pair cover %s' % ((a, b, lam),))
            rows.append(len(N))
    res['pair_nocover'] = {'pairs': 28, 'ratios': 2, 'six_dim_subspaces_tested_each': 11811,
                           'min_N': min(rows), 'max_N': max(rows), 'feasible_covers': 0}
    log('PAIRS', **res['pair_nocover'])

    out = json.dumps(res, indent=1, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(out)
    need((HERE / 'RESULT.json').read_text() == out, 'RESULT.json')
    print('PASS_P104_NETWORK_CODED_CARRIERS')


if __name__ == '__main__':
    main()

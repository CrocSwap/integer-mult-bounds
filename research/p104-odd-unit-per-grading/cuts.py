#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cut Lemma check on two exact P104 words, plus the partner-graph numbers alpha(P104) = 8 and alpha(R) = 6.

Standard library only, one file; run it as  python3 -I -B cuts.py.

Cut Lemma.  Let G be an up-set of frames.  PI = public vectors entering G (tokens of public registers born in G
and contents of public registers at their moves from outside G into G), O = contents of owned registers at their
moves from outside G into G, F = finals of the public registers that end in G.  Then F <= span(PI + O) and
|PI| = |F|, hence  rank(O mod PI) >= def(G) := rank(F + PI) - rank(F).
Here G_s = {frames containing the port label q_s}.  Ranks are exact over Q, computed modulo the two primes
1000000007 and 998244353 (the two must agree).

Words (data only, replayed here with the legality rules of words.py):
  W6805      CubeJerry's #6805 word (data/W6805.json.gz, SHA256 of the file pinned below).  Expected: def(G_s) = 0 on
             104/104 ports, no owned crossing (its 24 owned moves all descend), lemma holds 104/104.
  feeder6805 our feeder variant, data/edits-feeder6805.json.gz applied to W6805 (520 inserted events, one more owned
             field).  Expected: def(G_s) = 1 on 104/104, exactly one owned crossing into each G_s, lemma holds 104/104.
Control: the feeder word with its owned crossings removed from O must be flagged on every port (rank(O mod PI) = 0 < def).
alpha(G) = largest set of ports whose labels are pairwise odd (q_s . q_t = 1 over F2); exhaustive branch and bound
with a greedy-colouring bound (the search is a proof of maximality), for all 104 labels and for MIX14 (b') R.
"""
import collections
import copy
import gzip
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
W6805_SHA256 = '2b70b1c76f5bacc32c1dc8bf5b74db3b7b6496e2a5682092124ead9d4b90bbdc'
FEEDER_CANON_SHA256 = '8e426c532be89d569721854f213f75b3c598eb5262e8299609bf17d3e2ca8157'
PRIMES = (1000000007, 998244353)


def require(cond, label):
    if not cond:
        raise AssertionError(label)


# --------------------------------------------------------------------------------------------- word handling
def span(vectors):
    s = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512 and v not in s, 'frame vectors independent in F2^9')
        s |= {x ^ v for x in s}
    return frozenset(s)


def apply_edits(A, E):
    require(len(A['program']) == E['base_events'], 'edit list base length')
    out, pos = [], 0
    for i1, i2, evs in E['replace']:
        require(pos <= i1 <= i2 <= len(A['program']), 'edit ranges ordered')
        out.extend(A['program'][pos:i1])
        out.extend(evs)
        pos = i2
    out.extend(A['program'][pos:])
    W = copy.deepcopy(A)
    for key, h in E['header'].items():
        W[key] = h['value']
    W['program'] = out
    return W


def replay(W):
    """Exact replay with legality; returns rows of the public registers, the public and the owned MOVE records
    (register, from chart, to chart, content at the move), and the frame spans."""
    n, N = W['public'], W['public'] + W['owned_fields']
    sp = [span(f) for f in W['frames']]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * W['owned_fields']
    alive = set()
    pub_moves, own_moves = [], []
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        require(type(r) is int and 0 <= r < N, '%d register index' % i)
        if op == 'MOVE':
            a, b, flag = e[2], e[3], e[4]
            require(type(flag) is bool and flag == (r >= n) and cur[r] == a, '%d MOVE flag / current chart' % i)
            if r >= n:
                require(r in alive and (sp[a] < sp[b] or sp[b] < sp[a]), '%d owned MOVE live and nested' % i)
                own_moves.append((r, a, b, dict(rows[r])))
            else:
                require(sp[a] < sp[b], '%d public MOVE strictly ascends' % i)
                pub_moves.append((r, a, b, dict(rows[r])))
            cur[r] = b
        elif op == 'INIT':
            require(r >= n and r not in alive and len(e) == 3, '%d INIT of a dead owned field' % i)
            alive.add(r); rows[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR':
            require(r >= n and r in alive and (len(e) == 2 or cur[r] == e[2]), '%d CLEAR (a dirty CLEAR carries no chart)' % i)
            alive.discard(r); rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            q = Q(e[2])
            require(q != 0 and cur[r] == e[3] and (r < n or r in alive), '%d SCALE' % i)
            rows[r] = {k: v * q for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            s, q, f = e[2], Q(e[3]), e[4]
            require(type(s) is int and 0 <= s < N and s != r and q != 0, '%d operand' % i)
            require(cur[r] == f and cur[s] == f, '%d ADD/COPY operands at chart %d' % (i, f))
            require(all(x < n or x in alive for x in (r, s)), '%d owned field live' % i)
            if op == 'COPY':
                require(not rows[r], '%d COPY into a zero field' % i)
            R = rows[r]
            for k, v in rows[s].items():
                nv = R.get(k, 0) + q * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
        else:
            raise AssertionError('%d unknown op %r' % (i, op))
    require(not alive, 'every owned field cleared')
    require(cur[:n] == list(W['final']), 'public fields end at final charts')
    return rows[:n], pub_moves, own_moves, sp


# --------------------------------------------------------------------------------------------- exact ranks mod p
class Basis:
    """Incremental row-echelon basis over GF(p) of sparse vectors {column: Fraction}."""

    def __init__(self, p):
        self.p, self.piv = p, {}

    def reduce(self, v):
        p = self.p
        v = {k: (x.numerator % p) * pow(x.denominator % p, p - 2, p) % p for k, x in v.items()}
        v = {k: x for k, x in v.items() if x}
        while v:
            k = min(v)
            b = self.piv.get(k)
            if b is None:
                return k, v
            c = v[k]
            for j, y in b.items():
                nv = (v.get(j, 0) - c * y) % p
                if nv:
                    v[j] = nv
                else:
                    v.pop(j, None)
        return None, None

    def add(self, v):
        k, r = self.reduce(v)
        if k is None:
            return False
        inv = pow(r[k], self.p - 2, self.p)
        self.piv[k] = {j: x * inv % self.p for j, x in r.items()}
        return True

    def copy(self):
        b = Basis(self.p); b.piv = dict(self.piv)
        return b

    def rank(self):
        return len(self.piv)


def ranks(F, PI, O):
    """(rank PI, rank F, rank F+PI, rank PI+O, rank F+PI+O), identical modulo both primes.
    Vectors are fed shortest first, which keeps the elimination sparse."""
    seen = set()
    key = lambda v: len(v)
    F, PI, O = sorted(F, key=key), sorted(PI, key=key), sorted(O, key=key)
    for p in PRIMES:
        bF, bPI = Basis(p), Basis(p)
        for v in F:
            bF.add(v)
        for v in PI:
            bPI.add(v)
        bFPI = bPI.copy()
        for v in F:
            bFPI.add(v)
        bPO = bPI.copy()
        for v in O:
            bPO.add(v)
        bAll = bFPI.copy()
        for v in O:
            bAll.add(v)
        seen.add((bPI.rank(), bF.rank(), bFPI.rank(), bPO.rank(), bAll.rank()))
    require(len(seen) == 1, 'ranks agree modulo both primes: %s' % sorted(seen))
    return seen.pop()


def cut_check(W):
    """Run the Cut Lemma on every port.  Returns per-port records (def, #owned crossings, rank PI, rank F, rank F+PI,
    rank PI+O, rank F+PI+O), the number of non-ascending public moves (0, replay enforces it) and the owned
    move directions."""
    n = W['public']
    fin, pub_moves, own_moves, sp = replay(W)
    odir = collections.Counter('asc' if sp[a] < sp[b] else 'desc' for r, a, b, c in own_moves)
    recs = []
    for q in W['ports']:
        G = [q in s for s in sp]
        PI = [{r: Q(1)} for r in range(n) if G[W['initial'][r]]]
        PI += [c for r, a, b, c in pub_moves if not G[a] and G[b]]
        O = [c for r, a, b, c in own_moves if not G[a] and G[b]]
        F = [fin[r] for r in range(n) if G[W['final'][r]]]
        require(len(PI) == len(F), '|PI| = |F| for port %d' % q)
        rPI, rF, rFPI, rPO, rAll = ranks(F, PI, O)
        recs.append((rFPI - rF, len(O), rPI, rF, rFPI, rPO, rAll))
    return recs, odir


def evaluate(recs, drop_owned=False):
    """Lemma check per port: F <= span(PI + O) and rank(O mod PI) >= def.  With drop_owned the owned crossings are
    removed from O (control).  Returns (violations, histogram (def, crossings, rank(O mod PI)))."""
    bad, hist = 0, collections.Counter()
    for dfc, nO, rPI, rF, rFPI, rPO, rAll in recs:
        if drop_owned:
            rPO, rAll, nO = rPI, rFPI, 0
        bad += not (rAll == rPO and rPO - rPI >= dfc)
        hist[(dfc, nO, rPO - rPI)] += 1
    return bad, hist


# --------------------------------------------------------------------------------------------- alpha
def alpha(labels, subset=None):
    """Largest set of indices (within `subset`) with pairwise odd labels (dot product 1 over F2), exhaustive
    branch and bound (greedy-colouring bound); returns (size, example)."""
    dot = lambda a, b: bin(a & b).count('1') & 1
    idx = list(range(len(labels))) if subset is None else list(subset)
    adj = {s: {t for t in idx if t != s and dot(labels[s], labels[t])} for s in idx}
    best = [0, []]

    def colour_bound(cand):
        order, bound, left = [], {}, list(cand)
        k = 0
        while left:
            k += 1
            cls, rest = [], []
            for v in left:
                if all(v not in adj[u] for u in cls):
                    cls.append(v)
                else:
                    rest.append(v)
            for v in cls:
                order.append(v); bound[v] = k
            left = rest
        return order, bound

    def expand(cur, cand):
        order, bound = colour_bound(cand)
        for v in reversed(order):
            if len(cur) + bound[v] <= best[0]:
                return
            nc = [u for u in cand if u in adj[v]]
            if nc:
                expand(cur + [v], nc)
            elif len(cur) + 1 > best[0]:
                best[0], best[1] = len(cur) + 1, cur + [v]
            cand = [u for u in cand if u != v]
    expand([], idx)
    ex = best[1]
    require(all(dot(labels[a], labels[b]) for a in ex for b in ex if a != b), 'example set pairwise odd')
    return best[0], sorted(ex)


# --------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    raw = (DATA / 'W6805.json.gz').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == W6805_SHA256, 'vendored W6805 bytes')
    A = json.loads(gzip.decompress(raw))
    E = json.loads(gzip.decompress((DATA / 'edits-feeder6805.json.gz').read_bytes()))
    Fd = apply_edits(A, E)
    cs = hashlib.sha256(json.dumps(Fd, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(cs == FEEDER_CANON_SHA256, 'feeder6805 rebuilt sha256 ' + cs)
    print('PASS feeder6805 = W6805 + %d replacement(s) (%d events -> %d, owned fields %d -> %d), sha256 %s...'
          % (len(E['replace']), len(A['program']), len(Fd['program']), A['owned_fields'], Fd['owned_fields'], cs[:12]))
    require(len(A['ports']) == 104 and A['ports'] == Fd['ports'], '104 port labels')

    for W, name, want in ((A, 'W6805', {(0, 0, 0): 104}), (Fd, 'feeder6805', {(1, 1, 1): 104})):
        recs, odir = cut_check(W)
        bad, hist = evaluate(recs)
        require(bad == 0, '%s: lemma violations %d' % (name, bad))
        require(dict(hist) == want, '%s: (def, crossings, rank(O mod PI)) histogram %s' % (name, dict(hist)))
        print('PASS %s: exact replay legal; owned moves %s; ports 104; lemma violations 0; histogram '
              '(def(G_s), owned crossings into G_s, rank(O mod PI)) = %s' % (name, dict(odir), dict(hist)))
        if name == 'W6805':
            require(dict(odir) == {'desc': 24}, 'W6805: 24 owned moves, all descending')
        else:
            bad, hist = evaluate(recs, drop_owned=True)
            require(bad == 104, 'control: every port flagged')
            print('PASS control: feeder6805 with the owned crossings dropped is flagged on %d/104 ports '
                  '(def 1 not covered by rank(O mod PI) = 0): %s' % (bad, dict(hist)))
        if name == 'W6805':
            bad, hist = evaluate(recs, drop_owned=True)
            require(bad == 0, 'control: W6805 has def 0 and no crossings, so the same drop flags nothing')
            print('PASS control: W6805 (def 0, no owned crossings) is not flagged by the same drop')

    labels = A['ports']
    a_all, ex = alpha(labels)
    require(a_all == 8, 'alpha(P104) = 8')
    print('PASS alpha(P104) = %d (exhaustive branch and bound over the 104 labels); example port indices %s'
          % (a_all, ex))
    M = json.loads((DATA / 'mix14-bprime-R.json').read_text())
    require(sorted(M['L']) == sorted(labels), 'MIX14 labels = word labels as a set')
    a_R, exR = alpha(M['L'], M['R'])
    require(a_R == 6, 'alpha(R) = 6')
    print('PASS alpha(R) = %d for MIX14 (b\') R of %d ports (indices into the MIX14 label list); example %s'
          % (a_R, len(M['R']), exR))
    print('runtime %.0f s' % (time.time() - t0))
    print('PASS_CUT_LEMMA')


if __name__ == '__main__':
    sys.exit(main())

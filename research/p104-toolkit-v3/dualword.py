#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Frame-perp transpose ("duality") of a P104 native word (our DUALWORD / DUALSCAN lanes).  Standard library only.

dual(W): reverse time, transpose every local op, replace every frame F by F^perp (standard dot on F2^9), and swap the
X/Y register of each port (live r <-> r + 112, hosted X2 <-> Y2).  Op rules:
    ADD r += q*s  ->  ADD s += q*r        SCALE r *= q -> SCALE r *= q
    MOVE r a->b   ->  MOVE r b->a (on perp frames; perp reverses inclusion, so an ascent stays an ascent)
    INIT <-> CLEAR                        COPY -> ADD (COPY targets an empty register; ADD is the same map there)
Facts (README Part B): perp preserves every dimension gap, and every charge of the native invoice is a function of
dimension gaps, so the dual is priced bit-identically; dual(dual(W)) = W up to the frame basis lists (same spans) and the
one COPY.  The 8 native-B ports need free SCALEs to restore the contract (fix_b_ports).

API
  dual(W) -> W*                       raw dual (exact, no arithmetic)
  fix_b_ports(base, D) -> (D', ports)  free SCALEs (x*2 at start, Y*1/2 at end) on ports whose contract row differs
  restore_copy(D, base) -> D'          put the base word's single COPY back (dual maps COPY to ADD)
  swap_frames(W, a, b) -> W'           relabel two frame indices (an involution; used to run tokdrop.py on a dual,
                                       where {0} and V trade places: swap_frames(dual(W), Z, V))
  same_word(A, B) -> (bool, why)       equality up to frame basis lists (compares spans)
CLI
  python3 dualword.py IN OUT          write dual(IN)
"""
import copy
import gzip
import json
import sys


def load(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        return json.load(f)


def save(W, path):
    with gzip.open(path, 'wt') as f:
        json.dump(W, f)


def span(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in s}
    return frozenset(s)


def perp_basis(b):
    """ascending greedy basis of b^perp in F2^9 (standard dot)."""
    Pv = [v for v in range(512) if all(bin(v & u).count('1') % 2 == 0 for u in b)]
    basis = []; s = {0}
    for v in Pv:
        if v not in s:
            basis.append(v); s |= {x ^ v for x in s}
    if len(span(b)) == 1 << len(b):
        assert len(basis) == 9 - len(b)
    return basis


def port_swap(W):
    n = W['public']; H = W['hosted']
    pi = list(range(n))
    for r in W['live']:
        pi[r], pi[r + 112] = r + 112, r
    for x, y in zip(H['X2'], H['Y2']):
        pi[x], pi[y] = y, x
    return pi


def dual(W):
    n = W['public']; pi = port_swap(W)
    D = copy.deepcopy(W)
    cache = {}

    def pp(b):
        t = tuple(b)
        if t not in cache:
            cache[t] = perp_basis(b)
        return cache[t]
    D['frames'] = [pp(b) for b in W['frames']]
    new_init = [None] * n; new_fin = [None] * n
    for k in range(n):
        new_init[pi[k]] = W['final'][k]; new_fin[pi[k]] = W['initial'][k]
    D['initial'] = new_init; D['final'] = new_fin
    m = lambda r: pi[r] if r < n else r
    prog = []
    for e in reversed(W['program']):
        op = e[0]
        if op in ('ADD', 'COPY'):
            prog.append(['ADD', m(e[2]), m(e[1]), e[3], e[4]])
        elif op == 'SCALE':
            prog.append(['SCALE', m(e[1]), e[2], e[3]])
        elif op == 'MOVE':
            prog.append(['MOVE', m(e[1]), e[3], e[2], e[4]])
        elif op == 'INIT':
            prog.append(['CLEAR', e[1], e[2]])
        elif op == 'CLEAR':
            prog.append(['INIT', e[1], e[2]])
        else:
            raise ValueError('unknown op %r' % (op,))
    D['program'] = prog
    return D


def restore_copy(D, base):
    cps = [e for e in base['program'] if e[0] == 'COPY']
    out = copy.deepcopy(D)
    for c in cps:
        k = [i for i, e in enumerate(out['program']) if e == ['ADD'] + list(c[1:])]
        if len(k) != 1:
            raise ValueError('COPY %r matches %d ADD events' % (c, len(k)))
        out['program'][k[0]] = list(c)
    return out


def fix_b_ports(base, D, rows_base, rows_dual):
    """rows_*: exact final public rows (e.g. pricekit.replay(W)['rows']).  Adds the free SCALEs on every live port
    whose X row differs (the native-B ports, contract [[1,-1],[1/2,1/2]])."""
    bad = [r for r in base['live'] if rows_base[r] != rows_dual[r]]
    out = copy.deepcopy(D)
    pre = [['SCALE', r, '2', out['initial'][r]] for r in bad]
    post = [['SCALE', r + 112, '1/2', out['final'][r + 112]] for r in bad]
    out['program'] = pre + out['program'] + post
    return out, bad


def swap_frames(W, a, b):
    sw = lambda f: b if f == a else a if f == b else f
    out = copy.deepcopy(W)
    fr = out['frames']; fr[a], fr[b] = fr[b], fr[a]
    out['initial'] = [None if f is None else sw(f) for f in out['initial']]
    out['final'] = [None if f is None else sw(f) for f in out['final']]
    for e in out['program']:
        op = e[0]
        if op == 'MOVE':
            e[2] = sw(e[2]); e[3] = sw(e[3])
        elif op in ('ADD', 'COPY'):
            e[4] = sw(e[4])
        elif op == 'SCALE':
            e[3] = sw(e[3])
        elif op in ('INIT', 'CLEAR'):
            e[2] = sw(e[2])
    return out


def same_word(A, B):
    for k in A:
        if k not in ('frames',) and A[k] != B.get(k):
            return False, 'field %s differs' % k
    if len(A['frames']) != len(B['frames']):
        return False, 'frame count'
    if any(span(x) != span(y) for x, y in zip(A['frames'], B['frames'])):
        return False, 'frame spans differ'
    return True, 'equal up to frame bases'


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    save(dual(load(sys.argv[1])), sys.argv[2])

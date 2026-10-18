#!/usr/bin/env python3
"""Exhaustive r = w = 2 search for fifteen-call two-target UT4(F2) central words.

Generalizes the (4,6,4) fast driver of CrocSwap/integer-mult-bounds#1690 (vendored unchanged as
pr1690_search.py) to unequal a/c counts and seven middle calls, so it covers every split
(n_a, n_b, n_c) allowed by CrocSwap/integer-mult-bounds#1662's bound for a 15-call word:
(5,6,4), (4,6,5) and (4,7,4).

Per canonical middle sequence the side screen (ab, ba, aba, bab for the a-prefix profile;
cb, bc, cbc, bcb for the c-suffix profile) runs over every profile with a trie walk, so the
whole search is standard library only. `workers` parallelizes over middle sequences with
multiprocessing (stdlib); results are merged in sequence order, so counts are deterministic.

Josie Elliston's donated session, with Claude Code. Apache-2.0.
"""
import itertools
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pr1690_search as S  # noqa: E402

R = W = 2
TARGET_CROSS = (9, 9)          # abc = cba = I_2 (bits 0 and 3)
SPLITS = ((5, 6, 4), (4, 6, 5), (4, 7, 4))


# ---------- profile tries ----------
def profile_trie(nb, n, seqs):
    """Nested dict trie of all prefix-sum profiles (P_1..P_nb) of n couplings with zero total.
    Leaves are marked by the key None -> profile tuple."""
    root = {}
    for P in S.profiles(nb, n, seqs):
        node = root
        for p in P:
            node = node.setdefault(p, {})
        node[None] = P
    return root


def key_tables(bt):
    """kt[j][p] = 4-bit code (u0, u1, w0, w1) of position j with P_j = p; see S.key."""
    out = []
    for N in bt:
        x, y = S.split(N)
        row = []
        for p in range(16):
            code = 0
            for s in range(2):
                u = w = 0
                for k in range(2):
                    u ^= (p >> (2 * s + k)) & (x >> k) & 1
                    w ^= (y >> k) & (p >> (2 * k + s)) & 1
                code |= u << s | w << (2 + s)
            row.append(code)
        out.append(row)
    return out


def screen(trie, tab, kt, want):
    """{key: [profiles]} for every profile in `trie` whose side value equals `want`.
    Keys match S.key(bt, P)."""
    nb = len(tab)
    out = {}
    stack = [(trie, 0, 0, 0, 0, 0, 0)]
    last = nb - 1
    tl, kl = tab[last], kt[last]
    while stack:
        node, j, v, u0, u1, w0, w1 = stack.pop()
        if j == last:                                      # leaves inline: most trie nodes are here
            v ^= want
            for p, child in node.items():
                if tl[p] == v:
                    c = kl[p]
                    out.setdefault((u0 | (c & 1) << j, u1 | (c >> 1 & 1) << j,
                                    w0 | (c >> 2 & 1) << j, w1 | (c >> 3 & 1) << j), []).append(child[None])
            continue
        tj, kj = tab[j], kt[j]
        for p, child in node.items():
            c = kj[p]
            stack.append((child, j + 1, v ^ tj[p],
                          u0 | (c & 1) << j, u1 | (c >> 1 & 1) << j,
                          w0 | (c >> 2 & 1) << j, w1 | (c >> 3 & 1) << j))
    return out


# ---------- key pairing for nb-bit masks ----------
PAR = [bin(m).count('1') & 1 for m in range(1 << 7)]
_SOL = {}


def _sol(nb, u0, u1, e0, e1):
    k = (nb, u0, u1, e0, e1)
    if k not in _SOL:
        _SOL[k] = [m for m in range(1 << nb) if PAR[u0 & m] == e0 and PAR[u1 & m] == e1]
    return _SOL[k]


def key_cross(kp, kq):
    """(abc, cba) from keys, as S.key_cross but for masks of up to seven bits
    (PR1690's parity table has only 64 entries)."""
    abc = cba = 0
    for s in range(2):
        for t in range(2):
            abc |= PAR[kp[s] & kq[2 + t]] << (2 * s + t)
            cba |= PAR[kq[s] & kp[2 + t]] << (2 * s + t)
    return abc, cba


def key_pairs(nb, akeys, ckeys, target=TARGET_CROSS):
    """All (ka, kc) with key_cross(ka, kc) == target (same indexing as PR1690, nb bits)."""
    abc = target[0]
    byW = {}
    for k in ckeys:
        byW.setdefault(k[2:], []).append(k)
    for ka in akeys:
        for m0 in _sol(nb, ka[0], ka[1], abc & 1, abc >> 2 & 1):
            for m1 in _sol(nb, ka[0], ka[1], abc >> 1 & 1, abc >> 3 & 1):
                for kc in byW.get((m0, m1), ()):
                    if key_cross(ka, kc) == target:
                        yield ka, kc


# ---------- driver ----------
_CTX = {}


def _init(counts):
    na, nb, nc = counts
    seqs = S.make_seqs(R, max(na, nc))
    _CTX.update(counts=counts, seqs=seqs, TA=profile_trie(nb, na, seqs),
                TC=profile_trie(nb, nc, seqs))


def one_bt(bt, want=None, seen=None):
    """Process one middle sequence; returns (stats, solutions)."""
    na, nb, nc = _CTX['counts']
    wa, wc, cross = want or (0, 0, TARGET_CROSS)
    tab, kt = S.side_tables(bt), key_tables(bt)
    ga = screen(_CTX['TA'], tab, kt, wa)
    gc = ga if (na == nc and wa == wc) else screen(_CTX['TC'], tab, kt, wc)  # same trie, same screen
    st = dict(canonical=1, a_pass=sum(map(len, ga.values())), c_pass=sum(map(len, gc.values())),
              a_keys=len(ga), c_keys=len(gc), key_pairs=0, pairs=0, words=0, q_pass=0, formal_pass=0)
    sols = []
    for ka, kc in key_pairs(nb, ga, gc, cross):
        st['key_pairs'] += 1
        for P in ga[ka]:
            for Q in gc[kc]:
                st['pairs'] += 1
                S.expand(bt, P, Q, na, nc, _CTX['seqs'], R, W, st, sols, seen)
    return st, sols


def _chunk(bts):
    tot, sols = {}, []
    for bt in bts:
        st, s = one_bt(bt)
        for k, v in st.items():
            tot[k] = tot.get(k, 0) + v
        sols += s
    return tot, sols


def search(counts, workers=None, limit=None, log=None):
    """Exhaustive search for one split; returns all formal solutions (sorted)."""
    na, nb, nc = counts
    bts = list(S.middle_sequences(R, nb, True))
    if limit is not None:
        bts = bts[:limit]
    _init(counts)
    stats = dict(canonical=0, profiles_a=len(S.profiles(nb, na, _CTX['seqs'])),
                 profiles_c=len(S.profiles(nb, nc, _CTX['seqs'])), a_pass=0, c_pass=0, a_keys=0,
                 c_keys=0, key_pairs=0, pairs=0, words=0, q_pass=0, formal_pass=0)
    chunks = [bts[i:i + 64] for i in range(0, len(bts), 64)]
    workers = workers or os.cpu_count() or 1
    sols = []
    if workers == 1:
        results = map(_chunk, chunks)
    else:
        import multiprocessing as mp
        pool = mp.get_context('fork' if sys.platform != 'win32' else 'spawn').Pool(
            workers, initializer=_init, initargs=(counts,))
        results = pool.imap(_chunk, chunks)
    for tot, s in results:
        for k, v in tot.items():
            stats[k] += v
        sols += s
    if workers != 1:
        pool.close()
        pool.join()
    if log is not None:
        log.update(stats)
    return sorted(sols)


if __name__ == '__main__':
    import json
    import time
    which = [tuple(map(int, a.split(','))) for a in sys.argv[1:] if ',' in a] or list(SPLITS)
    lim = next((int(a) for a in sys.argv[1:] if a.isdigit()), None)
    for counts in which:
        t = time.time()
        st = {}
        sols = search(counts, limit=lim, log=st)
        st['solutions'] = len(sols)
        st['seconds'] = round(time.time() - t, 1)
        print(json.dumps({'counts': counts, **st}), flush=True)
        for s in sols[:5]:
            print(s, flush=True)

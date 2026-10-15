#!/usr/bin/env python3
"""Executable check of the radix-distributed sparse-union schedule (outer/UNION-SCHEDULE.md).

Simulates, on small exact integer tensors, the schedule that applies the Kronecker product  (x)_i T_i  (T_i = I on E_i^c, arbitrary on E_i) with
    * records tagged by their flag set F(x) = {i : x_i in E_i};
    * rounds r = 1,2,...: S_r = {|F| >= r} (lexicographic stream), tag f_r(F) = r-th smallest flag;
    * stable binary radix distribution by tag (ceil(log2 g) passes, inverted by replaying the stored bits);
    * per axis substream: per-prefix-block small-field transpose by lockstep zip passes (ceil(log2 |E_f|) levels, row length never needed), T_f on complete E_f-lines,
      inverse unzip passes;
    * records with |F| = r go to a LIFO stack, popped at the end and interleaved by the stored indicator bits;
and checks (1) the result equals the full tensor product exactly, (2) every substream is a union of complete E_f-lines, (3) the streamed volume is exactly
sum_x |F(x)| = sum_i |U_i| <= g |U| and the number of record moves is within C * sum_x|F(x)| * (log g + log |E_f| + 1), (4) tamper control: dropping one flag round breaks the result.
Prints PASS_UNION_SCHEDULE."""
import itertools, math, random
import numpy as np


def ceil_log2(n):
    return max(1, (n - 1).bit_length())


class Moves:
    n = 0


def radix_distribute(recs, tags, nbits):
    """stable LSD binary radix by tag; returns (stream, per-pass bit lists). Each pass = one scan splitting onto two output tapes + concatenation."""
    passes = []
    cur = list(zip(recs, tags))
    for k in range(nbits):
        bits = [(t >> k) & 1 for _, t in cur]
        zeros = [x for x, b in zip(cur, bits) if b == 0]
        ones = [x for x, b in zip(cur, bits) if b == 1]
        passes.append(bits)
        cur = zeros + ones
        Moves.n += len(cur)
    return cur, passes


def radix_undo(cur, passes):
    for bits in reversed(passes):
        nz = len(bits) - sum(bits)
        zeros, ones = iter(cur[:nz]), iter(cur[nz:])
        cur = [next(ones) if b else next(zeros) for b in bits]
        Moves.n += len(cur)
    return cur


def zip_transpose(rows):
    """rows: a lists of equal length b (unknown to the routine). Returns the suffix-major order [row0_j, row1_j, ..., row(a-1)_j for j=0..b-1] using
    ceil(log2 a) levels of lockstep zips: at each level two tapes are read in lockstep chunk by chunk (chunk sizes h and a-h are known from a only)."""
    a = len(rows)
    if a == 1:
        return list(rows[0])
    h = a // 2
    ta, tb = zip_transpose(rows[:h]), zip_transpose(rows[h:])
    out = []
    ia = ib = 0
    while ia < len(ta) or ib < len(tb):          # lockstep: end markers of the two tapes coincide
        out.extend(ta[ia:ia + h]); ia += h
        out.extend(tb[ib:ib + a - h]); ib += a - h
    Moves.n += len(out)
    return out


def zip_untranspose(seq, a):
    if a == 1:
        return [list(seq)]
    h = a // 2
    ta, tb = [], []
    i = 0
    while i < len(seq):
        ta.extend(seq[i:i + h]); i += h
        tb.extend(seq[i:i + a - h]); i += a - h
    Moves.n += len(seq)
    return zip_untranspose(ta, h) + zip_untranspose(tb, a - h)


def run(g, L, esizes, seed, drop_round=None):
    rnd = random.Random(seed)
    rng = np.random.default_rng(seed)
    E = [sorted(rnd.sample(range(L), esizes[i])) for i in range(g)]
    Tm = []
    for i in range(g):
        sub = rng.integers(-2, 3, (len(E[i]), len(E[i]))).astype(np.int64)
        M = np.eye(L, dtype=np.int64)
        M[np.ix_(E[i], E[i])] = sub
        Tm.append(M)
    X = rng.integers(-3, 4, (L,) * g).astype(np.int64)
    ref = X.copy()
    for i in range(g):
        ref = np.moveaxis(np.tensordot(Tm[i], ref, axes=([1], [i])), 0, i)
    assert int(np.abs(ref).max()) < 2 ** 62
    pts = list(itertools.product(range(L), repeat=g))                    # lexicographic stream
    flags = {x: tuple(i for i in range(g) if x[i] in E[i]) for x in pts}
    Moves.n = 0
    sumF = sum(len(f) for f in flags.values())
    inU = [bool(flags[x]) for x in pts]                                   # indicator bits of the one group scan that forms U
    S = [(x, int(X[x])) for x in pts if flags[x]]                         # records carry their current values
    U = len(S)
    gbits = ceil_log2(g)
    stack = []                                                            # LIFO tape of (rest records, indicator bits)
    r = 0; streamed = 0
    while S:
        streamed += len(S)
        tags = [flags[x][r] for x, _ in S]
        dist, passes = radix_distribute(S, tags, gbits)
        newv = {}
        i0 = 0
        while i0 < len(dist):
            f = dist[i0][1]
            i1 = i0
            while i1 < len(dist) and dist[i1][1] == f:
                i1 += 1
            sub = [rec for rec, _ in dist[i0:i1]]                          # (x, v) records of axis f, lexicographic
            a = len(E[f])
            sub_mat = Tm[f][np.ix_(E[f], E[f])]
            j = 0
            while j < len(sub):
                pre = sub[j][0][:f]
                k = j
                while k < len(sub) and sub[k][0][:f] == pre:
                    k += 1
                block = sub[j:k]
                rows, cur_row, last = [], [], None
                for rec in block:
                    if last is not None and rec[0][f] != last:
                        rows.append(cur_row); cur_row = []
                    cur_row.append(rec); last = rec[0][f]
                rows.append(cur_row)
                assert len(rows) == a and len({len(rw) for rw in rows}) == 1        # complete E_f-lines, equal rows
                assert [rw[0][0][f] for rw in rows] == E[f]
                seq = zip_transpose(rows)                                           # suffix-major, E_f ordinals consecutive
                Moves.n += len(seq)
                outseq = []
                for t in range(len(seq) // a):
                    line = seq[t * a:(t + 1) * a]
                    assert [rec[0][f] for rec in line] == E[f] and len({rec[0][:f] + rec[0][f + 1:] for rec in line}) == 1
                    res = sub_mat @ np.array([rec[1] for rec in line], dtype=np.int64)
                    if drop_round is not None and r == drop_round:
                        outseq.extend(line)
                    else:
                        outseq.extend((rec[0], int(v)) for rec, v in zip(line, res))
                rows2 = zip_untranspose(outseq, a)                                  # restore lexicographic order (cost counted)
                for rw in rows2:
                    pass
                block_new = [rec for rw in rows2 for rec in rw]
                for rec in block_new:
                    newv[rec[0]] = rec[1]
                j = k
            i0 = i1
        radix_undo(dist, passes)                                                    # restore the stream order
        S = [(x, newv[x]) for x, _ in S]
        Moves.n += len(S)
        keep = [len(flags[x]) > r + 1 for x, _ in S]
        stack.append(([rec for rec, kp in zip(S, keep) if not kp], keep))
        S = [rec for rec, kp in zip(S, keep) if kp]
        r += 1
    # pop the LIFO stack: interleave rest_r with the continuing (final) stream by the stored indicator bits
    cur = []
    for rest, keep in reversed(stack):
        ir, ic = iter(rest), iter(cur)
        cur = [next(ic) if kp else next(ir) for kp in keep]
        Moves.n += len(keep)
    final = iter(cur)
    res = np.zeros_like(X)
    for x, u in zip(pts, inU):
        res[x] = next(final)[1] if u else X[x]                                      # identity records pass through
    assert next(final, None) is None
    ok = bool(np.array_equal(res, ref))
    return ok, dict(streamed=streamed, sumF=sumF, U=U, g=g, moves=Moves.n, amax=max(len(e) for e in E), rounds=r)


def main():
    cases = [(5, 7, [2, 3, 2, 3, 2], 5), (4, 6, [2, 2, 3, 2], 11), (6, 5, [2, 2, 2, 3, 2, 2], 3), (3, 8, [3, 2, 3], 21)]
    for g, L, es, seed in cases:
        ok, st = run(g, L, es, seed)
        assert ok, (g, L, seed)
        assert st['streamed'] == st['sumF']                                          # streamed volume = sum|F| = sum_i |U_i|
        assert st['sumF'] == sum(es[i] * L ** (g - 1) for i in range(g))
        assert st['sumF'] <= g * st['U']
        bound = 3 * st['sumF'] * (ceil_log2(g) + 2 * ceil_log2(st['amax']) + 4)
        assert st['moves'] <= bound, (st, bound)
        print('case g=%d L=%d: exact tensor product reproduced; sum|F|=%d = sum|U_i|; g|U|=%d (x%.2f); moves=%d <= %d; rounds=%d' %
              (g, L, st['sumF'], g * st['U'], g * st['U'] / st['sumF'], st['moves'], bound, st['rounds']))
    ok, _ = run(5, 7, [2, 3, 2, 3, 2], 5, drop_round=1)                              # tamper: skip the second round's application
    assert not ok
    print('PASS_UNION_SCHEDULE')


if __name__ == '__main__':
    main()

"""Code-disjoint exhaustive census of the PR1498 two-connector model.

Model (PR1438/PR1498 README, re-derived here, no predecessor code read):
  five read-only sources b_0..b_4, two dirty connectors z0,z1 with
  independent formal dirt markers e0,e1;
  B_j(p): z_p ^= b_j  (each label exactly twice, each occurrence any port);
  C:      z0 ^= z1    (t calls);
  A_m(p): reads z_p; each output read exactly twice.
A mask m is realizable iff two readout states (port,cut) have identical
dirt part and source parts XORing to m.  A skeleton is legal iff both
connectors end exactly at their initial formal values.

Formal value encoding: bits 0..4 = source coefficients, bit 5 = e0, bit 6 = e1.
"""
import itertools, sys, time, json, hashlib
from collections import Counter
import numpy as np

N = 5
E0, E1 = 1 << 5, 1 << 6
SRC = (1 << N) - 1


def canonical_words():
    # brute force over all distinct multiset permutations, quotient by
    # first-occurrence relabeling (method differs from matching recursion)
    seen = set()
    for perm in set(itertools.permutations([0, 0, 1, 1, 2, 2, 3, 3, 4, 4])):
        ren, out = {}, []
        for x in perm:
            if x not in ren:
                ren[x] = len(ren)
            out.append(ren[x])
        seen.add(tuple(out))
    return sorted(seen)


def legal_port_patterns(w):
    """All 2^10 per-occurrence port patterns, filtered by exact z1 restoration
    (z1 is changed only by port-1 B calls, independent of C placement)."""
    res = []
    for pat in range(1 << 10):
        z1 = 0
        for k in range(10):
            if (pat >> k) & 1:
                z1 ^= 1 << w[k]
        if z1 == 0:
            res.append(pat)
    return res


def placements(t):
    """op sequences: entries -1 = C, k = k-th B call."""
    seqs = []
    for c in itertools.combinations_with_replacement(range(11), t):
        seq = []
        for k in range(11):
            seq.extend([-1] * c.count(k))
            if k < 10:
                seq.append(k)
        seqs.append(seq)
    return np.array(seqs, dtype=np.int8).reshape(len(seqs), 10 + t)


# pair table: code a (7 bits), code b -> 32-bit mask bit of src xor if dirt equal
codes = np.arange(128)
dirt = codes >> 5
src = codes & SRC
TABLE = np.where(dirt[:, None] == dirt[None, :],
                 np.left_shift(np.uint32(1), (src[:, None] ^ src[None, :]).astype(np.uint32)),
                 np.uint32(0)).astype(np.uint32).reshape(-1)
FULL = np.uint32(0xFFFFFFFF)


def census(t, words, full_pairs=True, witness_limit=50):
    ops = placements(t)                       # (P, 10+t)
    P, S = ops.shape
    hist = Counter()
    hist_by_r = {r: Counter() for r in range(6)}
    legal_total = 0
    illegal_total = 0
    witnesses = []
    full_count = 0
    full_by_r = Counter()
    for wi, w in enumerate(words):
        pats = legal_port_patterns(w)
        npat = len(pats)
        # increments per pattern per B call
        inc0 = np.zeros((npat, 11), dtype=np.int16)
        inc1 = np.zeros((npat, 11), dtype=np.int16)
        rvals = []
        for pi, pat in enumerate(pats):
            for k in range(10):
                if (pat >> k) & 1:
                    inc1[pi, k] = 1 << w[k]
                else:
                    inc0[pi, k] = 1 << w[k]
            rvals.append(len({w[k] for k in range(10) if (pat >> k) & 1}))
        rvals = np.array(rvals)
        # rows = pattern x placement
        R = npat * P
        prow = np.repeat(np.arange(npat), P)
        orow = np.tile(np.arange(P), npat)
        z0 = np.full(R, E0, dtype=np.int16)
        z1 = np.full(R, E1, dtype=np.int16)
        st0 = np.empty((R, S + 1), dtype=np.int16)
        st1 = np.empty((R, S + 1), dtype=np.int16)
        st0[:, 0] = z0
        st1[:, 0] = z1
        for s in range(S):
            k = ops[orow, s].astype(np.int64)
            isC = k < 0
            kk = np.where(isC, 10, k)
            z0 = z0 ^ np.where(isC, z1, inc0[prow, kk])
            z1 = z1 ^ inc1[prow, kk]  # inc1[:,10] == 0 for C
            st0[:, s + 1] = z0
            st1[:, s + 1] = z1
        legal = (z0 == E0) & (z1 == E1)
        legal_total += int(legal.sum())
        illegal_total += int((~legal).sum())
        if not legal.any():
            continue
        st0 = st0[legal]
        st1 = st1[legal]
        rl = rvals[prow[legal]]
        idx_p = prow[legal]
        idx_o = orow[legal]
        allst = np.concatenate([st0, st1], axis=1).astype(np.int64) if full_pairs else st0.astype(np.int64)
        cov = np.zeros(allst.shape[0], dtype=np.uint32)
        M = allst.shape[1]
        for a in range(M):
            ca = allst[:, a] * 128
            for b in range(a + 1, M):
                cov |= TABLE[ca + allst[:, b]]
        if not full_pairs:
            # z1 coverage: values of z1 never interact with z0 (different dirt);
            # add z1 pair differences separately
            z1s = st1.astype(np.int64)
            for a in range(S + 1):
                ca = z1s[:, a] * 128
                for b in range(a + 1, S + 1):
                    cov |= TABLE[ca + z1s[:, b]]
        cov |= np.uint32(1)  # zero mask always (same readout twice)
        pc = np.bitwise_count(cov).astype(np.int64)
        for val, cnt in zip(*np.unique(pc, return_counts=True)):
            hist[int(val)] += int(cnt)
        for r in range(6):
            m = rl == r
            if m.any():
                for val, cnt in zip(*np.unique(pc[m], return_counts=True)):
                    hist_by_r[r][int(val)] += int(cnt)
        fullm = cov == FULL
        nf = int(fullm.sum())
        if nf:
            full_count += nf
            for r, cnt in Counter(rl[fullm].tolist()).items():
                full_by_r[r] += cnt
            for i in np.nonzero(fullm)[0][: max(0, witness_limit - len(witnesses))]:
                witnesses.append({"word": list(w), "pattern": pats[idx_p[i]],
                                  "ops": ops[idx_o[i]].tolist()})
    return {
        "t": t, "placements": P, "legal": legal_total, "illegal": illegal_total,
        "hist": dict(sorted(hist.items())),
        "max": max(hist) if hist else None,
        "hist_by_r": {r: dict(sorted(h.items())) for r, h in hist_by_r.items()},
        "max_by_r": {r: (max(h) if h else None) for r, h in hist_by_r.items()},
        "full_count": full_count, "full_by_r": dict(full_by_r),
        "witnesses": witnesses,
    }


if __name__ == "__main__":
    ts = [int(x) for x in sys.argv[1].split(",")]
    full_pairs = (len(sys.argv) < 3 or sys.argv[2] != "fast")
    words = canonical_words()
    print("canonical words", len(words), flush=True)
    if len(sys.argv) >= 5:
        lo, hi = int(sys.argv[3]), int(sys.argv[4])
        words = words[lo:hi]
        print("word range", lo, hi, flush=True)
    for t in ts:
        t0 = time.time()
        res = census(t, words, full_pairs=full_pairs)
        res["seconds"] = round(time.time() - t0, 1)
        print(json.dumps(res), flush=True)

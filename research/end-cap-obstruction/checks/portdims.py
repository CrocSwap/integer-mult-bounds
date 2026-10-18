"""dim of the common perp of the ports of a reader set, over the 112 ports of the k8 word: cross-block pairs, triples and quads.
For ports in F_2^9, dim(cap perp(u_i)) = 9 - rank(u_i).  Quads are counted with numpy over all (14 choose 4) * 8^4 index choices."""
import gzip, itertools, json, os
import numpy as np
w = json.loads(gzip.decompress(open(os.environ['EO_ROOT'] + '/inputs/words/w1018.json.gz', 'rb').read()))
P = w['ports']; blk = [P[8 * b:8 * b + 8] for b in range(14)]
def rank(vs):
    b = []
    for v in vs:
        for x in b: v = min(v, v ^ x)
        if v: b.append(v)
    return len(b)
assert len(set(P)) == 112 and all(bin(p).count('1') % 2 == 1 for p in P)
print('ports 112 distinct odd-weight, 14 blocks of 8, block ranks', sorted({rank(b) for b in blk}))
pairs = {9 - rank([a, b]) for i, j in itertools.combinations(range(14), 2) for a in blk[i] for b in blk[j]}
npairs = sum(1 for i, j in itertools.combinations(range(14), 2) for a in blk[i] for b in blk[j])
print('cross-block pairs', npairs, 'dim of common perp', sorted(pairs))
tr = [9 - rank([a, b, c]) for i, j, k in itertools.combinations(range(14), 3) for a in blk[i] for b in blk[j] for c in blk[k]]
print('cross-block triples', len(tr), 'dim of common perp', sorted(set(tr)))
n6 = n5 = other = 0
A = [np.array(b, dtype=np.int64) for b in blk]
for i, j, k, l in itertools.combinations(range(14), 4):
    a, b, c, d = (A[i][:, None, None, None], A[j][None, :, None, None], A[k][None, None, :, None], A[l][None, None, None, :])
    zero = ((a ^ b ^ c ^ d) == 0) | ((a ^ b ^ c) == 0) | ((a ^ b ^ d) == 0) | ((a ^ c ^ d) == 0) | ((b ^ c ^ d) == 0)
    z = int(zero.sum()); n6 += z; n5 += 8 ** 4 - z
print('cross-block quads', n5 + n6, 'dim 5:', n5, 'dim 6 (zero-sum, rank 3):', n6)

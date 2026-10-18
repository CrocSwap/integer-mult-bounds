"""Shared data for the census checks: E8 lines, P112, the non-orthogonality graph, the 440,880 maximal sections, the 47 representatives.
numpy only.  Everything is rebuilt from lib/e8.py (the 120 root lines in doubled coordinates) and the shipped normal list."""
import io, json, lzma, os, sys
import numpy as np
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PKG, 'lib'))
import e8

def load():
    """-> dict with L (120x8 int), IP (120x120 true inner products), P (list of the 112 line ids), NO (112x112 bool: non-orthogonal, off-diagonal),
    Z (440880x112 bool: line of P112 lies in the section = orthogonal to the normal), reps (47 section indices)."""
    L = np.array(e8.lines(), dtype=np.int64)
    ip = L @ L.T
    assert (ip % 4 == 0).all(); IP = ip // 4
    F0 = [e8.idx(v) for v in e8.F0]
    assert len(set(F0)) == 8 and all(IP[a, b] == 0 for a in F0 for b in F0 if a != b)
    P = [t for t in range(120) if t not in F0]; assert P == list(e8.P112) and len(P) == 112
    NO = np.array([[(IP[t, s] % 2 != 0) for s in P] for t in P]); assert (NO == NO.T).all() and not NO.diagonal().any()
    assert set(NO.sum(1)) == {52}
    N = np.load(io.BytesIO(lzma.open(os.path.join(PKG, 'data', 'normals_x840.npy.xz')).read())).astype(np.int64)
    assert N.shape == (440880, 8)
    Z = (N @ L[P].T) == 0
    assert len(np.unique(np.packbits(Z, axis=1), axis=0)) == 440880          # all sections distinct
    Z120 = (N[::88] @ L.T) == 0                                              # every 88th normal: its 120-line section spans rank 7
    assert all(np.linalg.matrix_rank(L[z].astype(float)) == 7 for z in Z120)
    reps = json.load(open(os.path.join(PKG, 'data', 'hyp_reps.json')))
    keyidx = {bytes(r): i for i, r in enumerate(np.packbits(Z, axis=1))}
    repidx = []
    for rep in reps:
        b = np.zeros(112, bool); b[[P.index(v) for v in rep]] = True
        repidx.append(keyidx[bytes(np.packbits(b))])
    assert len(set(repidx)) == 47
    return dict(L=L, IP=IP, P=P, NO=NO, Z=Z, N=N, reps=repidx, F0=F0)

def write_graph(D, path):
    """graph.txt for census/cen.cpp: '112 47 440880', 112 adjacency rows (non-orthogonal), 47 rep sections, 440880 sections (0/1 strings)."""
    with open(path, 'w') as f:
        f.write('112 47 440880\n')
        for row in D['NO']: f.write(''.join('1' if x else '0' for x in row) + '\n')
        for i in D['reps']: f.write(''.join('1' if x else '0' for x in D['Z'][i]) + '\n')
        for z in D['Z']: f.write(''.join('1' if x else '0' for x in z) + '\n')

def write_mcdata(D, path):
    """data.txt for census/mc.cpp (first implementation): adjacency, 47 R masks (complement of the rep section), distinct sections' complements A-masks."""
    Z = D['Z']; P = D['P']
    def m128(b):
        lo = sum(1 << i for i in range(64) if b[i]); hi = sum(1 << (i - 64) for i in range(64, 112) if b[i]); return lo, hi
    U = np.unique(np.packbits(Z, axis=1), axis=0); Zu = np.unpackbits(U, axis=1)[:, :112].astype(bool)
    with open(path, 'w') as f:
        f.write('112\n')
        for t in range(112): lo, hi = m128(D['NO'][t]); f.write('%d %d\n' % (lo, hi))
        f.write('47\n')
        for i in D['reps']: lo, hi = m128(~Z[i]); f.write('%d %d\n' % (lo, hi))
        f.write('%d\n' % len(Zu))
        for z in Zu: lo, hi = m128(~z); f.write('%d %d\n' % (lo, hi))

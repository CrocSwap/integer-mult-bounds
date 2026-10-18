"""Enumerate all flats (sets of E8 lines = lines in a subspace spanned by lines) by rank, exactly."""
import numpy as np, pickle, sys, time
from geo import *
Lf = L.astype(float)
def closure_mask(idx):
    B = Lf[idx]
    # orthonormal basis of span via QR on B^T
    Qm, R = np.linalg.qr(B.T)
    r = np.linalg.matrix_rank(B)
    # use SVD for robustness
    Uu, s, Vt = np.linalg.svd(B, full_matrices=False)
    Vb = Vt[:r]
    res = Lf - (Lf @ Vb.T) @ Vb
    inside = np.where(np.abs(res).sum(1) < 1e-9)[0]
    return sum(1 << int(i) for i in inside), r
def enumerate_flats(maxrank=7):
    flats = {1: {1 << i for i in range(NL)}}
    for r in range(2, maxrank + 1):
        t = time.time(); new = set()
        for F in flats[r - 1]:
            mem = members(F)
            rep = mem[:]  # basis: pick r-1 independent members
            basis = row_basis(mem)
            for l in range(NL):
                if F >> l & 1: continue
                m, rr = closure_mask(basis + [l])
                new.add(m)
        flats[r] = new
        print('rank', r, len(new), round(time.time() - t, 1), flush=True)
    return flats
def row_basis(mem):
    b = []
    for i in mem:
        if np.linalg.matrix_rank(Lf[b + [i]]) > len(b): b.append(i)
    return b
if __name__ == '__main__':
    fl = enumerate_flats(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    pickle.dump(fl, open('flats.pkl', 'wb'))

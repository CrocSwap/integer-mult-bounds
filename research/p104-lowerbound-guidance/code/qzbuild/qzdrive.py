# QZBUILD driver: design = masks + pieces (stage sets of non-main incidences) + HOST order + idle placement.
import sys, time, json, itertools
import numpy as np
from qzfast import *
from qzexact import *
def make_design(n, k, masks, pieces, order, place, name=''):
    """pieces: list of stage sets (idle incidences; the 2k contacts are implicit).
    place: dict piece_index -> position p in 0..k (inserted right after the p-th HOST block; 0 = before any HOST)."""
    ev = []
    for p in range(k+1):
        if p > 0: ev.append(('H', order[p-1]))
        for i, S in enumerate(pieces):
            if place[i] == p: ev.append(('I', frozenset(S)))
    return Design(n, k, masks, ev, name)
def try_design(d, tries=4, seed=0, it=400, tol=1e-11, verbose=False):
    S = Sys(d, seed=seed)
    best = (1e9, None)
    for t in range(tries):
        z = np.random.default_rng(seed*100+t).normal(size=d.nv)
        z, nr = lm(S, z, it=it)
        if verbose: print('   try', t, '%.2e' % nr, flush=True)
        if nr < best[0]: best = (nr, z)
        if nr < tol and abok(S, z): return True, z, S, nr
    return False, best[1], S, best[0]

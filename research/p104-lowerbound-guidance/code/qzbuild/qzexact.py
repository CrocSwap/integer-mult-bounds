# QZBUILD exactification: sequential rational fixing + LM re-solve, then rational reconstruction of the rest,
# then an exact model check (Fractions) and an exact word replay (qzcheck).
import numpy as np
from fractions import Fraction as Fr
from qzfast import lm

def ratround(x, dens=(1, 2, 3, 4, 5, 6, 8, 10, 12, 16)):
    best = None
    for q in dens:
        p = round(x*q); f = Fr(p, q)
        if best is None or abs(float(f)-x) < abs(float(best)-x) - 1e-12: best = f
    return best

def abok(sys, z, eps=1e-6):
    d = sys.d; ab = z[2*d.n*d.m:].reshape(-1, 2)
    return all(abs(a) > eps and abs(b) > eps and abs(a*b+1) > eps for a, b in ab)
def fix_all(sys, z, order=None, tol=1e-10, verbose=False, it=200, dens_list=((1,2,4),(1,2,3,4,5,6,8),(1,2,3,4,5,6,7,8,9,10,12,16,20,24,32))):
    nv = len(z); fixed = np.zeros(nv, bool); vals = {}
    order = list(range(nv)) if order is None else order
    for i in order:
        if fixed[i]: continue
        ok = False
        for dens in dens_list:
            f = ratround(z[i], dens)
            z2 = z.copy(); z2[i] = float(f); fx = fixed.copy(); fx[i] = True
            z3, nr = lm(sys, z2, it=it, fix=fx)
            if nr < tol and abok(sys, z3):
                z = z3; fixed = fx; vals[i] = f; ok = True; break
        if verbose: print('  fix', i, 'ok' if ok else 'FREE', '%d fixed' % fixed.sum(), flush=True)
    return z, fixed, vals
def recon(x, maxden=10**6):
    return Fr(x).limit_denominator(maxden)

def exact_word(d, z, fixed, vals, maxden=10**6, path=None):
    from qzword import assemble
    import qzcheck, json
    zz = [vals[i] if fixed[i] else recon(z[i], maxden) for i in range(len(z))]
    n, m = d.n, d.m
    V = [zz[e*n:(e+1)*n] for e in range(m)]; W = [zz[n*m+e*n:n*m+(e+1)*n] for e in range(m)]
    ab = [zz[2*n*m+2*h:2*n*m+2*h+2] for h in range(len(d.hosts))]
    C = assemble(d, V, W, ab)
    ok, wf = qzcheck.legal(C)
    if path: json.dump(C, open(path, 'w'))
    return ok, wf, C, (V, W, ab)

def fix_batch(sys, z, order, tol=1e-10, it=150, dens=(1, 2, 3, 4, 5, 6, 8, 10, 12, 16), verbose=False):
    """fix coordinates in batches (bisect on failure)."""
    nv = len(z); fixed = np.zeros(nv, bool); vals = {}
    def attempt(idx):
        nonlocal z, fixed
        z2 = z.copy(); fx = fixed.copy(); fv = {}
        for i in idx:
            f = ratround(z[i], dens); z2[i] = float(f); fx[i] = True; fv[i] = f
        z3, nr = lm(sys, z2, it=it, fix=fx)
        if nr < tol and abok(sys, z3):
            z = z3; fixed = fx; vals.update(fv); return True
        return False
    stack = [order[i:i+16] for i in range(0, len(order), 16)]
    while stack:
        blk = stack.pop(0)
        blk = [i for i in blk if not fixed[i]]
        if not blk: continue
        if attempt(blk): continue
        if len(blk) > 1:
            h = len(blk)//2; stack = [blk[:h], blk[h:]] + stack
        if verbose: print('  fail', len(blk), flush=True)
    return z, fixed, vals

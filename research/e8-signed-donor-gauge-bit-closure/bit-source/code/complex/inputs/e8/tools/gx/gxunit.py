"""gxunit.py: unit of the bridged word B_2 for a gcert/1 block histogram, expected
exponents (bridge-rate's foldlib, READ-ONLY), and the split plan (sizes -> segment counts)."""
import sys
import gxpaths
import foldlib as fl

# split plan (defaults from MEASURED runs of the new checks on my data, NOTES.md "Measured")
GSEG = 12000           # most gates in one replay segment (gx-labels: one packed elimination per gate)
SCAL_ADDS = 30000      # most single adds (scatter entries included) checked in ONE source batch.  Measured with the tagged
                       # GS.scalCheck (Work/GCert/Scalar/Seg.lean): time and memory follow the ADDS, not the sources:
                       # 7,440 adds 3 s 1.2 GB (p6); 14,407 adds 6 s 2.0 GB (p7); 81,103 adds x 165 sources 168 s 6.8 GB (#168);
                       # 80,821 adds x 660 sources 180 s 7.0 GB (#193).  Above SCAL_ADDS: two batches (each under the 5-minute hold).
TSPLIT = 2             # the frame table is checked in 2^TSPLIT subtries


def plan(D, opt):
    adds = sum(len(g[3]) for g in D['A'] + D['B']) + (D['v'] * D['h'] if D['scat'][0] == 'star' else sum(map(len, D['scat'][1])))
    b = int(opt.get('batches', 1 if adds <= SCAL_ADDS else 2))
    return dict(gseg=int(opt.get('gseg', GSEG)), batches=b, tsplit=int(opt.get('tsplit', TSPLIT)))


def unit(inv, h, v, R, cst):
    """block list of one unit: 5 x (blocks of one invocation) + 2v x {h-1, 2h-2, 2h+2, 4}"""
    H = {}

    def add(r, n):
        if n:
            H[r] = H.get(r, 0) + n
    for r, n in inv.items():
        add(r, 5 * n)
    for cv, rk in fl.BANK['B2']:
        add(rk(h), cv * v)
    m, W = 5 * h, 4 * v + R
    D = W * m - sum(r * n for r, n in H.items())
    assert D == 4 * v - 5 * cst, (D, 4 * v - 5 * cst)
    return dict(kind='B2', h=h, m=m, W=W, D=D, v=v, R=R, H=H, inv=dict(inv), cst=cst)


def rates(u, B, s):
    """as crate.rate_module chooses them: evaluated units, then the largest with a rational certificate"""
    A0, Af, Ar0, Arf = fl.best_units(u, B, s)
    A, Ar = A0, Ar0
    while fl.plan_block(u, A, B, s) is None:
        A -= 1
    while fl.plan_rank(u, Ar, B, s) is None:
        Ar -= 1
    return dict(A=A, A_eval=A0, A_fails=Af, A_rank=Ar, A_rank_eval=Ar0, A_rank_fails=Arf, B=B, s=s)

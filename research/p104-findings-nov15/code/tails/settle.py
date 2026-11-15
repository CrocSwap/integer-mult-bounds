"""TOKDEBT step 2: settlement rank of a clean-mode repaired schedule.  Premix = invertible block-diagonal C0 (blocks = registers
sharing an initial frame, applied at t=0).  Need Xnew_obs[:,R_f] C0_f = Xbase_obs[:,R_f] for every birth frame f.
rank = sum_f rank([Xn_f|Xb_f]) - rank(Xn_f)   (mod p; 0 <=> solvable)."""
import sys, collections, numpy as np; sys.path.insert(0,'.'); sys.path.insert(0,'inputs/SEEDBUILD'); sys.path.insert(0,'inputs/NETCOMPILE')
import eng_c
from ort_c import *
from flint import nmod_mat
def tomat(A): return nmod_mat(A.shape[0], A.shape[1], [int(x) for x in A.ravel()], P)
def obs_rows(W2, org, Xb_obs_src):
    """stack (new rows, base rows, kind) for public finals + surviving owned observations."""
    n2 = W2['public']; X, _, ow, cl = replay_mod(W2)
    Xb, _, owb, clb = BREP
    new = [X[r][:n2] for r in range(n2)]; base = [Xb[r][:n] for r in range(n)]; kind = [('pub', r) for r in range(n2)]
    for j, row in ow.items():
        oi = org[j]
        if oi is not None and oi in owb: new.append(row); base.append(owb[oi]); kind.append(('ow', j))
    for j, row in cl.items():
        oi = org[j]
        if oi is not None and oi in clb: new.append(row); base.append(clb[oi]); kind.append(('cl', j))
    return np.array(new) % P, np.array(base) % P, kind
def corrected(r):
    """W2 with corrections inserted (mod-p integer coefficients)."""
    W2 = r['W2']; evs = collections.defaultdict(list)
    for (a, b, pos, F), v in zip(r.get('cands', []), r.get('x', [])):
        if v: evs[pos].append(['ADD', a, b, str(int(v)), F])
    prog = []
    org = list(r['org'])
    org2 = []
    for j, e in enumerate(W2['program'] + [None]):
        for ev in evs.get(j, []): prog.append(ev); org2.append(None)
        if e is None: break
        prog.append(e); org2.append(org[j])
    W3 = dict(W2); W3['program'] = prog
    return W3, org2
def settle(W3, org2, tier='A'):
    mains = mains_of(B0); hc = [c for c in range(n) if c not in mains]; pc = sorted(mains)
    Xn, Xb, kind = obs_rows(W3, org2, None)
    Vh = {r for r in range(n) if B0['final'][r] == VFR and r not in mains}
    keep = [i for i, k in enumerate(kind) if not (tier == 'A' and k[0] == 'pub' and k[1] in Vh)]
    Xn = Xn[keep]; Xb = Xb[keep]
    # pi check
    pi_ok = not ((Xn[:, pc] - Xb[:, pc]) % P).any() if tier == 'A' else None
    # birth frames
    fr = collections.defaultdict(list)
    for r in range(n): fr[B0['initial'][r]].append(r)
    tot = 0; per = {}
    for f_, R in fr.items():
        An = Xn[:, R]; Ab = Xb[:, R]
        if not (An != Ab).any(): continue
        rn = tomat(An).rank(); rj = tomat(np.hstack([An, Ab])).rank()
        if rj > rn: per[f_] = rj - rn; tot += rj - rn
    return tot, per, pi_ok, len(keep)

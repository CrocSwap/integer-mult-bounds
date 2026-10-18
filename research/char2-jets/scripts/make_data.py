"""Authors only (not run by verify.sh): writes data/tied_min_B.json (the 518 test matrices of Theorem T') and
data/cr2_realisations.json (stored char-2 realisations of the full incidence pattern, found by lib/cr2.py:realise).
Needs python-sat for the first file.  usage: python3 scripts/make_data.py [outdir]   (default: current directory)"""
import sys, os, json, random
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG + '/lib')
from kit import *; from cr2 import realise, cfg_data
out = sys.argv[1] if len(sys.argv) > 1 else '.'
# --- T' matrices: B is stored as the bitmask g over `free` (bit i = free[i]), as in kit.tomat
from satlib import enumerate_B
P, Q = load_cfg('tied_min.json'); v = 12; R, A, free = setup(P, Q); idx = {e: i for i, e in enumerate(free)}
opt = [sum(1 << idx[e] for e in ent) for ent in enumerate_B(P, Q, (4, 4, 4))]
random.seed(1); random.randrange(2, 1 << 16)           # same stream as tied_min_jet_cert.py (epsilon draw first)
full = (1 << len(free)) - 1; rnd = [random.getrandbits(len(free)) for _ in range(300)]
json.dump({'config': 'tied_min.json', 'f': len(free), 'optima': opt, 'full': full, 'random': rnd}, open(out + '/tied_min_B.json', 'w'))
print('tied_min_B.json: %d optima, full, %d random' % (len(opt), len(rnd)))
# --- CR2 realisations
names = ['aff14', 'cech_v8', 'cex_joint_v7', 'cex_wholeTS_v9', 'gad', 'supmin_fail_v8'] + ['nojoint_21_%d' % i for i in range(1, 15)] + ['cex_min_1']
res = {}
for nm in names:
    P, Q = load_cfg(nm + '.json'); v = len(P); R, A, free = setup(P, Q); pi, sig = cfg_data(P, Q)
    for k in (1, 2, 3, 4):
        r = realise(pi, sig, set(free), k=k)
        if isinstance(r, dict):
            res[nm] = {'k': k, 'P': [r[('p', t)] for t in range(v)], 'Q': [r[('l', s)] for s in range(v)]}; break
    print(nm, v, len(free), 'GF(2^%d)' % res[nm]['k'] if nm in res else 'NONE')
json.dump(res, open(out + '/cr2_realisations.json', 'w'))

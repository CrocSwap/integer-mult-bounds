"""Fast exact cost evaluator for a five-stage banked bit core-block word.
Word format (PR249 snapshot): records = int32 six-tuples
  MOVE (0, role, old_frame, new_frame, rank, z)
  ADD  (1, dst, src, coeff, frame, category)
  COPY (2, center, temp, copy_frame, target_frame, rank)   [paid child of given rank]
  ERASE(3, ...)
"""
import json, struct, collections
import numpy as np
from mpmath import mp, mpf, findroot
mp.dps = 50

def load_snapshot(d):
    s = json.load(open(f'{d}/249-states.json'))
    fr = json.load(open(f'{d}/frames.json'))
    dim = {int(k): len(v['B']) for k, v in fr['frames'].items()}
    rec = np.frombuffer(open(f'{d}/249-records.bin','rb').read(), dtype='<i4').reshape(-1, 6)
    return s, fr, dim, rec

def local_profile(rec, s, dim, h=24):
    """Return (local child histogram incl. copies, sum of helper residuals, v)."""
    v = s['v']; n = s['n']
    H = collections.Counter()
    moves = rec[rec[:, 0] == 0]
    for r in moves:
        if r[4] > 0: H[int(r[4])] += 1
    copies = rec[rec[:, 0] == 2]
    for r in copies:
        if r[5] > 0: H[int(r[5])] += 1
    init = s['initial']
    resid = sum(h - dim[init[str(r)]] for r in range(2 * v, n))
    return H, resid, v

def five_stage(H, resid, v, h=24, stages=5):
    m = stages * h
    prof = collections.Counter()
    for j, c in H.items(): prof[j] += stages * c
    for j in (2*h - 2, h - 1, 2*h + 2, 4): prof[j] += 2 * v
    W = mpf(4 * v) + mpf(resid) / h
    mass = sum(j * c for j, c in prof.items())
    return prof, W, m, W * m - mass

def solve_moment(prof, W, m, bad=mpf('1e-16')):
    calls = sum(prof.values())
    items = [(mpf(j) / m, c) for j, c in prof.items()]
    def mu(sv):
        t = 1 - sv
        return (sum(c * x ** t for x, c in items) + bad * 32 * m * m * calls * (mpf(1) / m) ** t) / W - 1
    return findroot(mu, mpf('0.0007'))

def evaluate(rec, s, dim, h=24):
    H, resid, v = local_profile(rec, s, dim, h)
    prof, W, m, deficit = five_stage(H, resid, v, h)
    sv = solve_moment(prof, W, m)
    return dict(saving=sv, kappa_approx=sv / (1 + sv), W=W, deficit=deficit, m=m,
                calls=sum(prof.values()), local=dict(sorted(H.items())), resid=resid)

if __name__ == '__main__':
    import sys
    s, fr, dim, rec = load_snapshot(sys.argv[1])
    r = evaluate(rec, s, dim)
    print({k: (float(v) if hasattr(v, 'real') and not isinstance(v, dict) else v) for k, v in r.items() if k != 'local'})

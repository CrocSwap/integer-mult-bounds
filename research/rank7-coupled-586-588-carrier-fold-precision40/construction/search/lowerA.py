"""lowerA.py -- option (a) census: lower the END frame of every restored helper h by one dimension (U_h -> hyperplane W of U_h),
frame-only (gates/algebra unchanged), exact certified solver.  Necessary: W contains the solver lower bound L_h of h's last vertex.
usage: python -B lowerA.py WORD.json.gz OUT.json part nparts"""
import sys, json, copy, time, collections
sys.path.insert(0, 'S/r13/agents/A-extract/code')
from synth import *
from lower import terminal_lower
BE = 2091300
w = load(sys.argv[1]); outp = sys.argv[2]; part, nparts = int(sys.argv[3]), int(sys.argv[4]); base = solve_frames(w, key='b')
tl, g, al = terminal_lower(w)
hs = sorted(map(int, w['helper_final']))[part::nparts]; out = []; t0 = time.time()
for h in hs:
    U = PM.basis(w['helper_final'][str(h)]); L = tl[h]; d = len(U)
    # hyperplanes of U containing L: W = {x in U : f(x)=0} for nonzero functionals f on U vanishing on L
    Ws = set(); spanU = set()
    for m in range(1, 1 << d):
        z = 0
        for i in range(d):
            if m >> i & 1: z ^= U[i]
        spanU.add(z)
    for n in range(1, 512):
        if all(((x & n).bit_count() & 1) == 0 for x in U): continue
        W = PM.basis([z for z in spanU if ((z & n).bit_count() & 1) == 0])
        if PM.basis(list(L) + list(W)) == W: Ws.add(W)
    rec = dict(h=h, end_dim=d, lower=list(L), lower_dim=len(L), candidates=len(Ws), results=[])
    for W in sorted(Ws):
        x = copy.deepcopy(w); x['helper_final'][str(h)] = list(W)
        try: dd = bp.frame_profile(x, literal=False)['cost'] - base['cost']
        except Exception as ex: rec['results'].append(dict(W=list(W), status='INFEASIBLE')); continue
        rec['results'].append(dict(W=list(W), delta=dd, margin=-dd - BE))
    best = max((r for r in rec['results'] if 'margin' in r), key=lambda r: r['margin'], default=None)
    rec['best'] = best; out.append(rec)
    print(f'h {h}: end dim {d}, lower dim {len(L)}, candidate W {len(Ws)}, best {best and best["margin"]} ({round(time.time()-t0)}s)', flush=True)
    json.dump(out, open(outp, 'w'), indent=0)

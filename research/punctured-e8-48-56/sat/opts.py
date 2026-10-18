"""Option sets per flat type for middrv.py.  usage: opts.py OUTDIR [type ...]   (default: all 8 types; ~1 min per type after a ~30 s flat enumeration)
Writes OUTDIR/opts56_T.npz with keys flat, out (lines outside F*), gens (reflections generating W_J), orb{i} (W_J-orbits of outside lines, largest
first) and o{s} (packed boolean option rows of the outside line s, |e| <= 56).  options(s) = inclusion-minimal { s^perp \\ F' : F' rank-7 flat through s }."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import e8punct as E
from sympy.combinatorics import Permutation, PermutationGroup
out_dir = sys.argv[1]; types = [int(x) for x in sys.argv[2:]] or list(range(8))
os.makedirs(out_dir, exist_ok=True)
t0 = time.time(); M = E.all_flats(); assert M.shape == (440880, 120); print('flats', M.shape, f'{time.time()-t0:.0f}s', flush=True)
for typ in types:
    t0 = time.time(); flat = E.FLATREP[typ]; out = [s for s in range(120) if not flat[s]]
    Wj = PermutationGroup([Permutation(E.PER[r]) for r in range(120) if flat[r]])
    orbs = sorted({tuple(sorted(Wj.orbit(s))) for s in out}, key=lambda o: (-len(o), o))
    d = dict(flat=np.array(sorted(np.flatnonzero(flat).tolist())), out=np.array(out), gens=np.array([list(g.array_form) for g in Wj.generators]))
    for i, O in enumerate(orbs): d[f'orb{i}'] = np.array(O)
    n = 0
    for s in out:
        A = E.options(M, s, 56); n += len(A); d[f'o{s}'] = np.packbits(A.astype(np.uint8), axis=1)
    np.savez_compressed(f'{out_dir}/opts56_{typ}.npz', **d)
    print('type', typ, '|F*|', int(flat.sum()), 'out', len(out), '|W_J|', Wj.order(), 'orbits', [len(o) for o in orbs], 'options', n, f'{time.time()-t0:.0f}s', flush=True)

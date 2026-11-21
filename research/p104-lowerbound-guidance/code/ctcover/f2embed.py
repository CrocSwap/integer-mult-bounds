"""CTCOVER f2embed.py: does the R2TEST pattern P (R=2 < mass 3) embed into an identity-target run beating m_F2(I)? GF(2) exact (SP f2mass, own swarm code)."""
import sys; sys.path.insert(0, '../seppays')
from f2mass import all_mass
P = [1, 2, 7, 11, 13]
odd, idx, dist = all_mass(P)
pat = lambda cells: sum(1 << idx[c] for c in cells if c in idx)
I = pat([(t, t) for t in range(5)])
Pp = pat([(0,2),(0,3),(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2),(3,3)])
print('odd cells', len(odd), 'm(I)', dist[I], 'm(P)', dist[Pp], 'm(I+P)', dist[I ^ Pp], 'composite R <=', 2 + dist[I ^ Pp])
# all patterns X: best composite 'run_P then honest X' for target T: R(P)+m(T^P)

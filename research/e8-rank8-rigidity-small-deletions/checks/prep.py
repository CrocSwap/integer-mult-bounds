# masks for s.c: orbm.txt (W(E6)-orbits on the 118 lines, as in orbs.json order) and orth.txt (per line, mask of orthogonal lines)
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from e8lib import N,G
orb=json.load(open('orbs.json'))
m=lambda s:sum(1<<x for x in s)
open('orbm.txt','w').write(''.join('%d %d\n'%(m(o)&(2**64-1),m(o)>>64) for o in orb))
open('orth.txt','w').write(''.join('%d %d\n'%(m([y for y in range(N) if G[x][y]==0])&(2**64-1),m([y for y in range(N) if G[x][y]==0])>>64) for x in range(N)))
print('orbit sizes',[len(o) for o in orb])

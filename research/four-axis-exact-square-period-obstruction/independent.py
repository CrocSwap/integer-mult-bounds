# Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""Independent integer-vector witnesses; no package imports."""
import json

def require(c,m):
    if not c: raise RuntimeError(m)
def plus(*vectors): return tuple(sum(a) for a in zip(*vectors))
def scale(c,x): return tuple(c*a for a in x)
def e(j): return tuple(int(k==j) for k in range(16))
def walsh(x):
    return tuple(sum((-1 if (r&s).bit_count()%2 else 1)*x[s] for s in range(16)) for r in range(16))
def in_l(x): return all(a%4==0 for a in walsh(x))
def in_2l(x): return all(a%2==0 for a in x) and all(a%8==0 for a in walsh(x))
def same(x,y): return in_2l(plus(x,scale(-1,y)))
def kval(s):
    return plus(e(s),scale(s.bit_count()-1,e(0)),*(scale(-1,e(1<<j)) for j in range(4) if s>>j&1))
def K(x): return tuple((-1 if r.bit_count()%2 else 1)*x[r^15] for r in range(16))
u=[scale(4,e(0))]+[scale(2,plus(e(1<<j),scale(-1,e(0)))) for j in range(4)]
require(all(in_l(x) for x in u),'u in L')
for mask in range(1,32):
    require(not in_2l(plus(*(u[j] for j in range(5) if mask>>j&1))),'E independent')
require(same(K(u[0]),u[0]),'K u0')
for j in range(1,5): require(same(K(u[j]),plus(u[j],u[0])),'K ui')
Au1=tuple(v//4 for v in walsh(u[1]))
require(all(v%4==0 for v in walsh(u[1])),'A u1 integral')
xi=plus(u[1],Au1,kval(3),kval(5),kval(9))
v=plus(*u[1:])
require(in_l(xi),'xi in L')
require(same(plus(K(u[1]),u[1]),u[0]),'first N2 witness')
require(same(plus(K(xi),xi),v),'second N2 witness')
for x in (u[0],v,plus(u[0],v)): require(not in_2l(x),'independent N2 images in E')
print(json.dumps({'status':'PASS_INDEPENDENT_PERIOD_WITNESSES','E_dimension':5,'rank_N2_on_E':1,'independent_E_intersect_image_N2_vectors':2,'xi':xi,'v':v},sort_keys=True))

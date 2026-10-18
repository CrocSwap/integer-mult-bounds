import gzip,json,sys,copy
from fractions import Fraction as Q
GK=__import__('os').environ['EO_ROOT']+'/inputs/repo/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112
V=112
def load(p): return json.loads(gzip.decompress(open(p,'rb').read()))
def save(w,p): open(p,'wb').write(G.dump(w))
_pc={}
def inperp(F,t,P):
    if P[t] not in _pc: _pc[P[t]]=G.perp(P[t])
    pp=_pc[P[t]]; return G.basis(list(F)+list(pp))==pp
def rows_final(w,order=None):
    n=2*V+w['report']['R']; rows=[{r:Q(1)} for r in range(n)]
    seq=(order if order is not None else w['A']+w['cut']+w['B'])
    for e in seq: G.apply_op(e,rows)
    return rows

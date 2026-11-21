"""mod-2 covering clauses for tight rows: port t needs cbar_t in span_F2{zbar : t in D_z}
<=> for every phi in F2^8 (functional via plain dot on coords... use B-dual) with phi(cbar_t)=1 some z in K_t has phi(zbar)=1."""
import sys; sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
import pickle
Phi=np.array(list(itertools.product([0,1],repeat=8)),np.int64)
PC=(Phi@Cb.T)%2; PZ=(Phi@Zb.T)%2     # plain dot = some functional; all 256 functionals covered
Rm=(PZ*(1<<np.arange(16))).sum(1)
CL={}
for t in range(n):
    Rs=sorted(set(Rm[PC[:,t]==1].tolist()),key=lambda r:bin(r).count('1'))
    mins=[]
    for r in Rs:
        if not any((a&r)==a for a in mins): mins.append(r)
    CL[t]=mins
pickle.dump(CL,open('f2clauses.pkl','wb'))
Z4=pickle.load(open('../nonlin/zclauses.pkl','rb'))
print('F2 clauses per port',min(len(v) for v in CL.values()),max(len(v) for v in CL.values()),'sizes',sorted(set(bin(r).count('1') for v in CL.values() for r in v)))
# sanity: every F2 clause is implied by Z4 clauses (relaxation): each F2 clause must contain some Z4 clause
bad=sum(1 for t in range(n) for r in CL[t] if not any((a&r)==a for a in Z4[t]))
print('F2 clauses not implied by a Z4 clause (should be 0):',bad)

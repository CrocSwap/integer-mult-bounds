"""decode kissat model of esat.py; recompute U_z, prices (Q-rank), exemptions, decodability (zfeas) independently of CNF."""
import sys; sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
import pickle
cnf=sys.argv[1]; mp=pickle.load(open(cnf+'.map','rb'))
FE=np.load('../nonlin/zfeas.npy')
val=set()
for line in open(sys.argv[2]):
    if line.startswith('v'):
        for x in line.split()[1:]:
            x=int(x)
            if x>0: val.add(x)
allv=np.array(list(itertools.product([0,1],repeat=9)))
Sz=[np.nonzero((C@(G@Z[k]))%4)[0] for k in range(16)]
tot=0; allowed=np.zeros(n,np.int64); prices=[]
for z in range(16):
    F=[[1 if mp['f'][z,i,c] in val else 0 for c in range(9)] for i in range(9) if mp['used'][z,i] in val]
    inU=~(((allv@np.array(F).T)%2).any(1)) if F else np.ones(512,bool)
    U=allv[inU]
    P=[t for t in range(n) if any((U==H[t]).all(1))]
    for t in P: allowed[t]|=1<<z
    p=f2rank(Q[np.ix_(P,Sz[z])]) if P else 0
    prices.append(p); tot+=p
ex=[t for t in range(n) if mp['ex'][t] in val]
# exempt port: singleton loose row y=G c_t, price = rank Q[{t},S] = Q[t,t]=1
pex=sum(f2rank(Q[np.ix_([t],np.nonzero((C@(G@C[t]))%4)[0])]) for t in ex)
ok=all(FE[t,allowed[t]] or t in ex for t in range(n))
print('tight prices',prices,'sum',tot,'exempt',len(ex),'exempt price',pex,'TOTAL',tot+pex,'all ports decodable',ok)

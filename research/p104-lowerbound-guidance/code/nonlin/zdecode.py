"""decode a kissat model of zsat.py; independently recompute U_z, prices, and decodability."""
from ncore import *
import pickle,sys
cnf=sys.argv[1]; mp=pickle.load(open(cnf+'.map','rb'))
FE=np.load('zfeas.npy')
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
    if F: inU=~(((allv@np.array(F).T)%2).any(1))
    else: inU=np.ones(512,bool)
    U=allv[inU]
    P=[t for t in range(n) if inU[int(sum(H[t,c]<<(8-c) for c in range(9)))]]
    # recompute index properly
    P=[t for t in range(n) if any((U==H[t]).all(1))]
    for t in P: allowed[t]|=1<<z
    p=f2rank(Q[np.ix_(P,Sz[z])]) if P else 0
    prices.append(p); tot+=p
print('prices',prices,'total',tot,'all ports decodable',all(FE[t,allowed[t]] for t in range(n)))

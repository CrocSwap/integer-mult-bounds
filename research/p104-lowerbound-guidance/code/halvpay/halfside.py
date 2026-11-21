"""HALVPAY halfside.py: E_lam, E_psi for the toy finals X_t: <q_t>,x_t -> V, x_t + M_t y ; Y_t: {0},y_t -> q_t^perp,y_t
with M = I + side information on EVEN cells (q_t.q_s = 0), entries drawn from {0, +-1/2, +-1, 3/2}; on Q96 (n=9) and random small toys."""
import random, sys, pickle
from fractions import Fraction as Fr
from ebound import ebound
dot=lambda a,b: bin(a&b).count('1')&1
def sp(vs):
    S={0}
    for v in vs:
        if v not in S: S|={x^v for x in S}
    return frozenset(S)
def run(n,Q,M):
    N=1<<n; V=frozenset(range(N)); Z=frozenset([0]); perp=lambda q: frozenset(x for x in range(N) if not dot(x,q))
    k=len(Q); cols={('x',t):t for t in range(k)}; cols.update({('y',t):k+t for t in range(k)})
    pubs=[]
    for t in range(k):
        fin={('x',t):Fr(1)}; fin.update({('y',s):M[t][s] for s in range(k) if M[t][s]!=0})
        pubs.append((sp([Q[t]]),{('x',t):Fr(1)},V,fin)); pubs.append((Z,{('y',t):Fr(1)},perp(Q[t]),{('y',t):Fr(1)}))
    return ebound(pubs,n,cols)
def randM(Q,rng,dens,vals):
    k=len(Q); return [[Fr(1) if s==t else (rng.choice(vals) if (not dot(Q[t],Q[s]) and rng.random()<dens) else Fr(0)) for s in range(k)] for t in range(k)]
rng=random.Random(int(sys.argv[2]) if len(sys.argv)>2 else 1); H=[Fr(1,2),Fr(-1,2),Fr(3,2)]; VALS=H+[Fr(1),Fr(-1)]
if __name__!='__main__': pass
elif sys.argv[1]=='small':
    worst={}; wp={}; cnt=0
    for it in range(400):
        n=rng.choice([3,4,5]); odd=[v for v in range(1,1<<n) if dot(v,v)]
        Q=rng.sample(odd,rng.randint(2,min(8,len(odd)))); M=randM(Q,rng,rng.choice([.3,.6,1.0]),rng.choice([H,VALS]))
        e=run(n,Q,M); k=len(Q); key=(n,k); worst[key]=min(worst.get(key,99),e['E_lam']-k); wp[key]=min(wp.get(key,99),e['E_psi']-k); cnt+=1
    print('small: runs',cnt,'min (E - |Q|) over lam/psi by (n,|Q|):',dict(sorted(worst.items())),'PSI:',dict(sorted(wp.items())))
else:
    d=pickle.load(open('f56run_nomix.pkl','rb')); Q=d['P'][:96]
    for dens in (0.05,0.3,1.0):
        M=randM(Q,rng,dens,H); e=run(9,Q,M); print('Q96 half side info density',dens,'E_lam',e['E_lam'],'E_psi',e['E_psi'],flush=True)

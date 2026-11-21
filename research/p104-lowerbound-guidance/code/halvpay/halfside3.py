"""HALVPAY halfside3.py: probes between 'all even cells half' (E=72) and integral (E=96)."""
import random, pickle
from fractions import Fraction as Fr
from halfside import run, dot
d=pickle.load(open('f56run_nomix.pkl','rb')); Q=d['P'][:96]; k=96; rng=random.Random(9)
def M_of(f): return [[Fr(1) if s==t else (f(t,s) if not dot(Q[t],Q[s]) else Fr(0)) for s in range(k)] for t in range(k)]
A=set(rng.sample(range(k),48))
for name,f in [('all half except 1% zero',lambda t,s: Fr(0) if rng.random()<.01 else Fr(1,2)),
               ('all half except 1% integer 1',lambda t,s: Fr(1) if rng.random()<.01 else Fr(1,2)),
               ('rows in A (48) all half, others 0',lambda t,s: Fr(1,2) if t in A else Fr(0)),
               ('cols in A all half',lambda t,s: Fr(1,2) if s in A else Fr(0)),
               ('all half, diag 3 instead of 1',None)]:
    if f is None:
        M=M_of(lambda t,s: Fr(1,2)); 
        for t in range(k): M[t][t]=Fr(3)
    else: M=M_of(f)
    e=run(9,Q,M); print('%-36s E_lam %d'%(name,e['E_lam']),flush=True)

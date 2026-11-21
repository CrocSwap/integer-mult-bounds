"""HALVPAY halfside2.py: how low can E_lam(Q96, M = I + half side info on even cells) go?  Random dense patterns + simple
structured ones (all +1/2; random signs; half on a random fraction of even cells)."""
import random, sys, pickle
from fractions import Fraction as Fr
from halfside import run, dot
d=pickle.load(open('f56run_nomix.pkl','rb')); Q=d['P'][:96]; k=96
rng=random.Random(5)
def M_of(f):
    return [[Fr(1) if s==t else (f(t,s) if not dot(Q[t],Q[s]) else Fr(0)) for s in range(k)] for t in range(k)]
tests=[('all +1/2',lambda t,s: Fr(1,2)),('symmetric random signs',None),('random signs',lambda t,s: rng.choice([Fr(1,2),Fr(-1,2)])),
       ('half w.p. .7 else 0',lambda t,s: Fr(1,2) if rng.random()<.7 else Fr(0)),('half w.p. .5 else 1',lambda t,s: Fr(1,2) if rng.random()<.5 else Fr(1))]
sg={}
for name,f in tests:
    if f is None:
        f=lambda t,s: sg.setdefault((min(t,s),max(t,s)),rng.choice([Fr(1,2),Fr(-1,2)]))
    e=run(9,Q,M_of(f)); print('%-28s E_lam %d  E_psi %d'%(name,e['E_lam'],e['E_psi']),flush=True)

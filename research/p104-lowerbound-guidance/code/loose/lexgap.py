"""Audit of TIGHT55 cube reduction: does 'd lexmax in Aut-orbit' imply 'indicator of {d=9} lexmax in orbit'?
Search for a counterexample d in {0..9}^16 (d = dim U_z^perp, 9 = inactive)."""
import pickle, itertools, random
P=pickle.load(open('../tight55/perms.pkl','rb')); P=[tuple(p) for p in P]
reps=set(pickle.load(open('../tight55/reps.pkl','rb')))
def act(d,p): return tuple(d[p[j]] for j in range(16))   # (d o p)_j = d_{p(j)}  (as in zsat_sym)
def lexmax(d): return all(d>=act(d,p) for p in P)
def ind(I): return tuple(1 if I>>j&1 else 0 for j in range(16))
# orbit-lexmax masks per the same convention
lm=set()
for I in range(1,1<<16):
    v=ind(I)
    if all(v>=act(v,p) for p in P): lm.add(I)
print('lexmax nonempty masks (same convention):',len(lm),' reps.pkl:',len(reps),' equal:',lm==reps)
# counterexample search: random d lexmax-ified (take max of orbit), check indicator
rng=random.Random(1); bad=[]
for trial in range(200000):
    k=rng.randrange(0,17)
    d=[9 if rng.random()<k/16 else rng.randrange(0,9) for _ in range(16)]
    dm=max(act(tuple(d),p) for p in P)        # lexmax representative of its orbit
    I=sum(1<<j for j in range(16) if dm[j]==9)
    if I and I not in reps: bad.append((dm,I)); 
    if len(bad)>=5: break
print('counterexamples found:',len(bad))
for b in bad[:5]: print(b)

import sys,pickle,random
from f2sa import *
Kt=pickle.load(open('../nonlin/e8_Kt.pkl','rb'))
rec=[]
for t in range(n):
    fs=[zb[k] for k in range(16) if Kt[t]>>k&1]
    # F2 recipe: need independent subset summing to cb; E8 z's form basis? check
    x=0
    for f in fs: x^=f
    rec.append(fs)
    assert rk(fs)==len(fs) and x==cb[t], (t,fs)
D={}
for t in range(n):
    for f in rec[t]: D.setdefault(f,set()).add(t)
print('E8 F2 cost',sum(price_f(f,D[f]) for f in D))
seed=int(sys.argv[1]); steps=int(sys.argv[2]); T0=float(sys.argv[3])
b,rec2=run(seed,steps,T0,0.05,init=[list(r) for r in rec])
print('best from E8 start',b)
pickle.dump(rec2,open(f'f2e8_{seed}.pkl','wb'))

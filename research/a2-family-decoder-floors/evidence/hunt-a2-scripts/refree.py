import pickle,sys,sympy as sp
al2,be2,al3,be3=sp.symbols('al2 be2 al3 be3')
from a2lib import *
r3v=R[X[2]]
co3=nullspace([[r1[k],r2[k],-r3v[k]] for k in range(8)],3)[0]; co3=[x/co3[2] for x in co3]
Bloc=[[Fr(1),Fr(0),Fr(1),Fr(0)],[Fr(0),Fr(1),Fr(0),Fr(0)],[Fr(0),Fr(0),co3[0],co3[1]]]
bn=nullspace(Bloc,4); assert len(bn)==1; bn=bn[0]
Bf=sum(sp.Rational(str(c))*s_ for c,s_ in zip(bn,(al2,be2,al3,be3)))
print('B-locus form',Bf)
g_=[[0]*8,[al2*x_+be2*y_ for x_,y_ in zip(r1,r2)],[al3*x_+be3*y_ for x_,y_ in zip(r1,r2)]]
def kap(i,k):
    s_=next(s_ for s_ in O[k] if Gm[X[i]][s_]!=0 and s_ not in X)
    return sp.factor(sum((sp.Rational(str(R[X[i]][q]))+g_[i][q]-g_[k][q])*sp.Rational(str(R[s_][q])) for q in range(8)))
FORB=[Bf]+[kap(i,k) for i in range(3) for k in range(3) if i!=k]
print('forbidden forms',FORB)
for k in sys.argv[1:]:
    EX=pickle.load(open(f'expr_{k}.pkl','rb')); free=set(); kinds={}
    for key,e in EX.items():
        if e==0 or not e.free_symbols: continue
        num,den=sp.fraction(sp.together(e)); num=sp.factor(num)
        if not num.free_symbols: kinds[key]='den-only'; continue
        q=num
        for Ff in FORB:
            while True:
                qq=sp.cancel(q/Ff)
                if sp.fraction(sp.together(qq))[1].free_symbols: break
                q=qq
        if not q.free_symbols: kinds[key]='forbidden'; continue
        free.add(key); kinds[key]=str(num)
    print(k,'free',len(free),sorted(set(kinds[x] for x in free))[:30])
    pickle.dump(free,open(f'free_{k}.pkl','wb'))

# BILINEAR bl0x: EXACT (Fractions) check of the kernel gauge for random rational walks: G'kap=0, lam^T G'=0, Ghat block sums 0,
# Ghat_st = 1/4 eps_st alpha_s beta_t (s!=t), and every block kap_t, lam_t invertible.
from fractions import Fraction as F
import random
random.seed(5)
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def ad(a,b,c=1):return [[a[i][j]+c*b[i][j] for j in range(2)] for i in range(2)]
def sc(c,a):return [[c*a[i][j] for j in range(2)] for i in range(2)]
def det(a):return a[0][0]*a[1][1]-a[0][1]*a[1][0]
def inv(a):d=det(a);return [[a[1][1]/d,-a[0][1]/d],[-a[1][0]/d,a[0][0]/d]]
I=[[F(1),F(0)],[F(0),F(1)]];Z=[[F(0)]*2 for _ in range(2)]
ok=True
for k in range(3,8):
  for trial in range(3):
    while True:
        As=[[[F(random.randint(-5,5),random.randint(1,4)) for j in range(2)] for i in range(2)] for _ in range(k-1)]
        if all(det(a)!=0 for a in As):break
    P=I
    for a in As:P=mm(a,P)
    As.append(sc((-1)**(k+1),inv(P)))
    if any(det(ad(a,I))==0 for a in As):continue
    Gp=lambda s,t:ad(sc(1 if s<=t else -1,I),sc(2,inv(ad(As[t],I))),-1) if s==t else sc(1 if s<=t else -1,I)
    S=[I];[S.append(sc(-1,mm(As[t],S[-1]))) for t in range(k)];kap=[sc(F(1,2),mm(ad(As[t],I),S[t])) for t in range(k)]
    T=[None]*k;T[k-1]=I
    for t in range(k-1,0,-1):T[t-1]=sc(-1,mm(T[t],As[t]))
    lam=[sc(F(1,2),mm(T[t],ad(As[t],I))) for t in range(k)]
    Q=[I];[Q.append(sc(-1,mm(a,Q[-1]))) for a in As]
    for s in range(k):
        r=Z
        for t in range(k):r=ad(r,mm(Gp(s,t),kap[t]))
        ok&=r==Z
        r=Z
        for t in range(k):r=ad(r,mm(lam[t],Gp(t,s)))
        ok&=r==Z
    Gh=lambda s,t:mm(mm(lam[s],Gp(s,t)),kap[t])
    for s in range(k):
        rs=Z;cs=Z
        for t in range(k):rs=ad(rs,Gh(s,t));cs=ad(cs,Gh(t,s))
        ok&=rs==Z and cs==Z
        for t in range(k):
            if s!=t:ok&=Gh(s,t)==sc(F(1,4)*(1 if s<=t else -1),mm(ad(inv(Q[s+1]),inv(Q[s]),-1),ad(Q[t+1],Q[t],-1)))
    ok&=all(det(x)!=0 for x in kap+lam)
print('EXACT kernel-gauge identities hold:',ok)

# THINQ tq8: closed form of the e=0 / per-stage-leaf-law optimum (2 all-main full hubs + d1 = k(2k-4)/(k-1) leaves), exact mpmath
from mpmath import mp,mpf
mp.dps=40; s=mpf('0.99'); pw=lambda x: mpf(x)**s
v1=pw(9)-pw(8); bar=mpf('128.891')
def HQ(k):
    vmh=pw(8*k+1)-k*pw(8); d1=mpf(k*(2*k-4))/(k-1)
    return mpf(104)/k*(2*k-2-2*(1-vmh)-d1*(1-v1))
def HP(k): return mpf(208)/k*((k-2)*(pw(17)-pw(16))+pw(8*k+1)-pw(8)*k)
for k in (8,12,13,14,16,72,80,81,82,100):
    print(k,mp.nstr(HQ(k),12),'HP',mp.nstr(HP(k),12))
vals=[(HQ(k),k) for k in range(3,200001)]
print('max',mp.nstr(max(vals)[0],12),'at k',max(vals)[1])
first=[k for v,k in vals if v<bar][0]; print('first k below bar',first,'any above bar after it:',any(v>=bar for v,k in vals if k>=first))
dec=all(vals[i+1][0]<vals[i][0] for i in range(len(vals)-1) if vals[i][1]>=13); print('strictly decreasing k>=13 up to 2e5:',dec)

"""DEN4 run3: (1) E8-56 half decoder on P104: Toeplitz e=1 and embedded at e=2 (v->2v, and w->2w on half the rows) must give rank(I+X);
(2) P104 Gram-class decoders (root coords, B=Gb, norm 2); (3) negative controls: perturbed decoders must FAIL the carry identity."""
import numpy as np, sympy, sys
from qlib import *; from carrypoly import analyse; from quarter import quarter; from gauge import climb
O='code/orbitlp/'
W4=np.load(O+'e8W.npy')%4; V4=np.load(O+'e8V.npy')%4
C=CALL[:104]; Q=Qof(C)
assert set(np.unique(W4))<= {0,1,3} and set(np.unique(V4))<={0,1,3}
sgn=lambda A: np.where(A==3,-1,A)
Wi=sgn(W4); Vi=sgn(V4)       # integer sign rows, sum D(w)QD(v) = 2I on Q-cells (mod 4 data; signs exact)
pr=[rk2(Q[np.ix_(np.nonzero(Wi[:,k])[0],np.nonzero(Vi[:,k])[0])]) for k in range(Wi.shape[1])]
r1=analyse(1,Wi%4,Vi%4,pr,Q,'E8-56 e=1')
r2=analyse(2,Wi%8,(2*Vi)%8,pr,Q,'E8-56 as e=2 (v->2v)')
Wm=Wi.copy(); Vm=2*Vi.copy(); Wm[:,::2]*=2; Vm[:,::2]//=2
r3=analyse(2,Wm%8,Vm%8,pr,Q,'E8-56 as e=2 mixed')
rng=np.random.default_rng(5)
# P104 Gram class
GbS=sympy.Matrix(GB.tolist())
for trial in range(4):
    U=rand_unimod(8,rng)*sympy.diag(*[2 if i<trial+1 else 1 for i in range(8)])*rand_unimod(8,rng,6)
    rows=gram_rows_B(C.tolist(),GbS,U,2)
    assert check_decoder(rows,Q)==0
    e,W,V,pr2,D,S=normalise(rows,Q)
    r=analyse(e,W,V,pr2,Q,'P104 gram',verbose=False); g=climb(e,W,V,pr2,Q,'toeplitz',30,1)
    line=dict(set='P104',e=e,C=r['C'],toep=r['toeplitz'],toep_gauge=g[1],poly=r['polyrank'])
    if e==2: line['master']=quarter(e,W,V,pr2,Q,verbose=False)['master']
    print(line,flush=True)
# negative controls: flip one entry of a valid quarter decoder -> identity must fail
L=std_set('HS64'); QH=Q_std(L)
U=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): U[2*t+s,i]=2; U[2*t+s,i+1]=2*sg
rows=gram_rows_std(L,U.tolist()); e,W,V,prh,D,S=normalise(rows,QH)
fails=0
for trial in range(20):
    W2=W.copy(); k=rng.integers(W.shape[1]); t=rng.choice(np.nonzero(W[:,k]%8)[0]); W2[t,k]=(W2[t,k]+int(rng.choice([2,4,6])))%8
    try: analyse(e,W2,V,prh,QH,verbose=False)
    except AssertionError: fails+=1
print('negative control: perturbed HS decoders failing the identity:',fails,'/ 20')

# h=5 relay instance from net2dec/ngmin5.log : T = M o Q, list odd cells
from common import *
h=5
labs=[1, 2, 4, 7, 8, 11, 13, 14, 16, 19, 21, 22, 25, 26, 28, 31]
n=len(labs)
Fj=[1, 3, 1, 1, 3, 3, 3, 0, 3, 3, 0, 0, 1, 3, 3, 3]
Fk=[0, 2, 0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0]
Gj=[3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]
Gk=[0, 0, 0, 1, 3, 0, 0, 3, 0, 1, 1, 0, 0, 0, 1, 0]
eta=3
rk=[Fk[p]+eta*Fj[p] for p in range(n)]
M=[[Gj[t]*Fj[p]+Gk[t]*rk[p] for p in range(n)] for t in range(n)]
Q=[[dot(labs[t],labs[p]) for p in range(n)] for t in range(n)]
T=[[M[t][p]*Q[t][p] for p in range(n)] for t in range(n)]
odd=[(t,p) for t in range(n) for p in range(n) if Q[t][p]]
nz=[(t,p) for (t,p) in odd if T[t][p]]
readers=sorted({t for t,p in nz}); gathers=sorted({p for t,p in nz})
if __name__=='__main__':
    print('odd',len(odd),'nonzero odd',len(nz),'readers',readers,'gathers',gathers)
    print('price fwd rows: j',price([labs[t] for t in range(n) if Gj[t]],[labs[p] for p in range(n) if Fj[p]]),
          'k',price([labs[t] for t in range(n) if Gk[t]],[labs[p] for p in range(n) if rk[p]]))
    gb=[Gj[t]+eta*Gk[t] for t in range(n)]
    print('price bwd rows: j',price([labs[t] for t in range(n) if gb[t]],[labs[p] for p in range(n) if Fj[p]]),
          'k',price([labs[t] for t in range(n) if Gk[t]],[labs[p] for p in range(n) if Fk[p]]))
    for t in readers: print(labs[t],[T[t][p] for p in range(n)])

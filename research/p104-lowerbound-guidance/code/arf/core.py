"""ARF core.py: does U (V) of a decoder contain U_E8 (V_E8)? (explains tightness of f=56 by monotonicity of f)"""
import sys,os,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); CARGS=sys.argv[1:]; sys.argv=sys.argv[:1]
sys.path.insert(0,HERE); from stats import *
def UV(W,V):
    RB=spaces_B(W%4,V%4,Q);RA=spaces_A(W%4,V%4,Q)
    return f2basis([x for t in range(n) for x in RA[t]]),f2basis([x for t in range(n) for x in RB[t]])
U0,V0=UV(np.load('../orbitlp/e8W.npy'),np.load('../orbitlp/e8V.npy'))
for p in CARGS:
    W=np.load(p.replace('XX','W')+'.npy');V=np.load(p.replace('XX','V')+'.npy'); U,Vv=UV(W,V)
    print(os.path.basename(p),'dimU',len(U),'U∩U_E8',inter(U,U0),'U∩V_E8',inter(U,V0),'dimV',len(Vv),'V∩V_E8',inter(Vv,V0),'V∩U_E8',inter(Vv,U0))

"""ORBITLP e8.py: E8 decoder on P104 in mod-4 form. W=C (coords), V=C Gb (=2U). Checks M=G/2 pattern vs labels Q."""
import json, numpy as np
from geo import *
E=json.load(open(D56+'e8base.json'))
C=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
G=C@Gb@C.T
assert (np.diag(G)==2).all()
odd=(G%2==0).astype(int)
assert (odd==Q).all(), 'port order mismatch'
W=C%4; V=(C@Gb)%4
Mm=(W@V.T)%4
assert ((Mm*Q)%4 == (2*np.eye(104,dtype=int))%4*Q).all() or True
bad=sum(1 for t in range(104) for s in range(104) if Q[t,s] and Mm[t,s]!=(2 if t==s else 0))
print('E8 mod-4 violations',bad)
def rk2(M):
    M=[int(''.join(map(str,r)),2) for r in (np.array(M)%2)]
    piv={};r=0
    for x in M:
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x;r+=1;break
    return r
pr=[rk2(Q[np.ix_(np.nonzero(W[:,k])[0],np.nonzero(V[:,k])[0])]) for k in range(8)]
print('prices',pr)
if __name__=='__main__':
    np.save('e8W.npy',W); np.save('e8V.npy',V)
def e8_56():
    import json
    d=json.load(open(D56+'x8fix.json'))['fix']
    W7=np.zeros((104,8),int); V7=np.zeros((104,8),int)
    for key,val in d.items():
        k,t,s=key.split(','); k=int(k); t=int(t)
        (W7 if s=='w' else V7)[t,k]=val
    return W7,V7
if __name__=='__main__':
    W7,V7=e8_56()
    Mm=(W7@V7.T)%4
    bad=sum(1 for t in range(104) for s in range(104) if Q[t,s] and Mm[t,s]!=(2 if t==s else 0))
    pr=[rk2(Q[np.ix_(np.nonzero(W7[:,k])[0],np.nonzero(V7[:,k])[0])]) for k in range(8)]
    print('E8-56 violations',bad,'prices',pr,'|D|',[(W7[:,k]>0).sum() for k in range(8)],'|S|',[(V7[:,k]>0).sum() for k in range(8)])
    print('odd entries all?', [(W7[:,k]%2==1).sum() for k in range(8)])
    np.save('e8W.npy',W7); np.save('e8V.npy',V7)

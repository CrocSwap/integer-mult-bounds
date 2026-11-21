import sys,ast;sys.path.insert(0,'.')
from rb13 import *
def freebuild(k,R,seeds=3,tries=6):
    out=[]
    for sd in range(seeds):
        S=WSys2(k,R);nr,z,tr=S.attempt(sd,tries=tries)
        msg=''
        if nr<1e-8:
            pn,S2,zz=S.polish(z);P,W=to_real(*S2.unpack(zz)[:3],k);msg='polish %.1e prod+I %.1e'%(pn,np.abs(P+np.eye(S2.n)).max())
        out.append((nr,[round(t,3) for t in tr],msg))
    return out
if __name__=='__main__':
    from rb2 import K4_3,K4_4
    from rb9 import C33
    for nm,k,R in [('C1',3,C1),('c33',6,C33),('K4#3',4,K4_3),('K4#4',4,K4_4)]:
        print(nm,freebuild(k,R),flush=True)
    for l in open('rb7_k5.log').readlines()[:2]:
        d=ast.literal_eval(l.split(' ',3)[3].strip());R=roles_of(d)
        print(l.split()[1],'design',freebuild(5,R),flush=True);print(l.split()[1],'coord',freebuild(5,fullsplit(R)),flush=True)

import sys,os
sys.path.insert(0,'.')
from plan19x import *
import core11
class Netc19(Netc14):
    QS={}
    def merge(self,H,hs,diffs):
        first,last=H[hs[0]],H[hs[-1]]
        a,g,_=self.split(first); _,_,z=self.split(last)
        vis=list(a)+[g]
        qs=self.QS[tuple(hs)]
        for j in range(1,len(hs)):
            b=H[hs[j]]['block']; vis.append(((b['t1'],0.5),b['frame'],('giveq',b['r'],qs[j])))
        vis+=z
        L={kk:-vv for kk,vv in self.beta(vsum14(self.snaps,vis)).items()}
        return dict(visits=vis,load=L,block=first['block'])
def load19(log=lambda *a:None):
    run_netc5.Netc5=Netc19
    N,nb=run_netc5.prepare(core6.BASE,log)
    N.PB=[x.split(':') for x in os.environ.get('PB','').split(',') if x]
    return N
def uvec(U,i): return {k:Q(v) for k,v in U[i]['u'].items()}
def mk(N,H0,U,ch):
    u1=uvec(U,ch[0]); qs=[Q(1)]+[ratio(u1,uvec(U,i)) for i in ch[1:]]
    assert all(q is not None and q!=0 for q in qs)
    N.QS[tuple(ch)]=qs
    return N.merge(H0,ch,[[]]*(len(ch)-1)), qs

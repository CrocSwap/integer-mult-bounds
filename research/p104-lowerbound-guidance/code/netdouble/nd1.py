# NETDOUBLE nd1 (own code): exact F2 checks of the NETWORK DOUBLING (port-doubled tensor potential) on random legal NetWs.
#  MASTER: rank [[ (y Nb f')oQ, (y Nb f)oQ ], [ (y' Nb f')oQ, (y' Nb f)oQ ]] <= D  for y,y' (n x m) with y_k ⊆ L(b_k^perp), f,f' with f_k ⊆ L(a_k)
#  CANON : y'=Gbar, f'=Fbar  (lower-left = Mbar o Q)
#  controls: EPS  = content perturbation also driven through H' (z = Nb(f + H' Nb f'))   [relay scalar-2 term]
#            FREEY= y unconstrained by the chart;  NORULE = relay rule b_j ⊆ a_k dropped
import random, sys
from ndlib import *
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); mode=sys.argv[4] if len(sys.argv)>4 else 'legal'
random.seed(seed)
def rmask(mask): return [[v & (random.random()<.5) for v in r] for r in mask]
def T(A): return [list(r) for r in zip(*A)]
viol={'master':0,'canon':0,'eps':0,'freey':0}; tested=0; worst={}
for tr in range(TR):
    net=rand_net(h,ctrl=(mode=='norule'))
    n,m=net.n,net.m; Q=net.Q; Nb=net.Nb
    Hp=[[(v//2)%2 for v in r] for r in net.H]
    for rep in range(3):
        y=T(rmask(net.inBp)); y2=T(rmask(net.inBp)); f=rmask(net.inA); f2=rmask(net.inA)
        if rep==0: y2=net.Gb; f2=net.Fb
        def blk(y,y2,z,z2):
            A=had(mm(y,z2,2),Q); B=had(mm(y,z,2),Q); C=had(mm(y2,z2,2),Q); E=had(mm(y2,z,2),Q)
            return [ra+rb for ra,rb in zip(A,B)]+[rc+re for rc,re in zip(C,E)]
        z=mm(Nb,f,2); z2=mm(Nb,f2,2)
        r=rk2(blk(y,y2,z,z2)); tested+=1
        if r>net.D: viol['master']+=1; viol['canon']+= (rep==0)
        # EPS control: z driven through H' from copy-1 content z2
        ze=mm(Nb,[[ (a+b)%2 for a,b in zip(r1,r2)] for r1,r2 in zip(f,mm(Hp,z2,2))],2)
        re_=rk2(blk(y,y2,ze,z2))
        if re_>net.D: viol['eps']+=1; worst['eps']=max(worst.get('eps',0),re_-net.D)
        yf=[[random.randint(0,1) for _ in range(m)] for _ in range(n)]
        rf=rk2(blk(yf,y2,z,z2))
        if rf>net.D: viol['freey']+=1
print('h',h,'mode',mode,'tested',tested,'viol',viol,'max excess',worst)

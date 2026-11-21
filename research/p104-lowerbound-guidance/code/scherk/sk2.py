"""SCHERK sk2: DYADIC crossing law -> witness LP row.  [proof in SK.md]
CROSS [P]: for disjoint stage sets X,Y (positions in the call order), #{roles r : M_r meets X and Y} >= 2*rank(E_XY) = 2*min(#X-runs,#Y-runs).
DYADIC_J [P, from CROSS summed over the dyadic tree]: for every call order,
    sum_r ( #distinct residues of M_r mod 2^(J+1)  - 1 )  >=  R_J(k) := sum_{l=0..J} sum_{j<2^l} 2*floor(m_{l,j}/2),  m_{l,j} = #{s<k : s = j mod 2^l}
  and #distinct residues <= min(D_r, 2^(J+1))  =>  type row  sum_r (min(D_r,2^(J+1)) - 1) >= R_J(k).
modes:  check  -> exact checks (rank E_XY formula by Fractions; built-caller frames)
        lp k.. -> ms9 witness LP (FAM coord,pfix,shal; imported unmodified) + DYADIC_J rows, J=1..ceil(log2 k)"""
import os,sys,signal,json,itertools
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
os.environ.setdefault('FAM','coord,pfix,shal')
from fractions import Fraction as Fr
from math import ceil,log2
BASE='<research-tree>/cards/WILD/'
def RJ(k,J):return sum(2*(len(range(j,k,2**l))//2) for l in range(J+1) for j in range(2**l))
def rankQ(M):
    M=[[Fr(x) for x in r] for r in M];rk=0;cols=len(M[0]) if M else 0
    for c in range(cols):
        p=next((i for i in range(rk,len(M)) if M[i][c]!=0),None)
        if p is None:continue
        M[rk],M[p]=M[p],M[rk]
        for i in range(len(M)):
            if i!=rk and M[i][c]!=0:
                f=M[i][c]/M[rk][c];M[i]=[a-f*b for a,b in zip(M[i],M[rk])]
        rk+=1
    return rk
def runs(seq,lab):  # linear runs of label lab in seq of labels
    return sum(1 for i,x in enumerate(seq) if x==lab and (i==0 or seq[i-1]!=lab))
def check():
    # (1) rank E_XY = min(#X-runs,#Y-runs) for all labelings of k<=9 positions with X,Y,ignored
    bad=0;tot=0
    for k in range(2,9):
        for lab in itertools.product('XY.',repeat=k):
            X=[i for i in range(k) if lab[i]=='X'];Y=[i for i in range(k) if lab[i]=='Y']
            if not X or not Y:continue
            E=[[1 if x<=y else -1 for y in Y] for x in X];s=[c for c in lab if c!='.']
            tot+=1;bad+=rankQ(E)!=min(runs(s,'X'),runs(s,'Y'))
    print('rank E_XY formula: %d labelings, %d mismatches'%(tot,bad))
    # (2) built frames (degree-1 pure IDLE_ODD roles dropped; they are outside the n=2k-2 frame)
    import glob
    for fn in sorted(glob.glob(BASE+'UNIMODEL/arm1/caller_*.json'))+[BASE+'UNIMODEL/swarm/d3star/caller_C1.json']:
        W=json.load(open(fn));k=W['stages'];n=W['roles']
        order=[];[order.append(e[1]) for e in W['events'] if e[0]=='HOST' and e[1] not in order]
        pos={st:i for i,st in enumerate(order)}
        masks=[frozenset(pos[i+1] for i,b in enumerate(W['diagonal'][r][2:]) if b) for r in range(n)]
        fr=[m for m in masks if len(m)>=2]
        if k<3:print('%-22s k=%d skipped (k<3)'%(fn.split('/')[-1],k));continue
        # full CROSS check over all X,Y labelings
        worst=None
        for lab in itertools.product('XY.',repeat=k):
            X={i for i in range(k) if lab[i]=='X'};Y={i for i in range(k) if lab[i]=='Y'}
            if not X or not Y:continue
            s=[c for c in lab if c!='.'];need=2*min(runs(s,'X'),runs(s,'Y'))
            have=sum(1 for m in fr if m&X and m&Y);sl=have-need
            if worst is None or sl<worst[0]:worst=(sl,''.join(lab))
        dy=[(J,sum(len({p%2**(J+1) for p in m})-1 for m in fr),RJ(k,J)) for J in range(1,ceil(log2(k))+1)]
        print('%-22s k=%d frame n=%d (2k-2=%d) CROSS min slack %d at %s; DYADIC (J,lhs,R_J) %s'%(fn.split('/')[-1],k,len(fr),2*k-2,worst[0],worst[1],dy))
if __name__=='__main__':
    signal.alarm(3000)
    if sys.argv[1]=='check':check();sys.exit()
    sys.path.insert(0,BASE+'UNIMODEL/routes/mainscan');import ms9
    class LP(ms9.LP):
        def __init__(s_,k):
            super().__init__(k);Jm=int(os.environ.get('JMAX',ceil(log2(k))))
            for J in range(1,Jm+1):s_.X.append((lambda D,c=2**(J+1):float(min(D,c)-1),lambda L:0.0,lambda D:0.0,0.0,float(RJ(k,J))))
    for k in [int(a) for a in sys.argv[2:]]:
        L=LP(k);res=L.solve()
        if res is None:print('k',k,'INFEASIBLE',flush=True);continue
        B,p,sup=res
        print('DYADIC k',k,'cB',round(104*B/k,3),'cP',round(104*p/k,3),'R_J',[RJ(k,J) for J in range(1,ceil(log2(k))+1)],sup if os.environ.get('SUP') else '',flush=True)

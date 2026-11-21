"""BILINEAR bl7: exact-in-the-limit COVER bound by branch & bound over monotone tau-profiles (all thresholds l=3..Lmax).
Box [lo,hi] (monotone-propagated): relaxed bl5 LP with rows S_l >= lo_l, U(L)=min_{l<=L} hi_l.  Valid: every design has a monotone
profile tau' (tau'_l = min_{l'<=l}|T_l'|) with S_l >= tau'_l and eff incidences of pieces L bounded by tau'_L.  Best-first; stops when the best open
box bound minus the best leaf (lo==hi) value <= GAP or after MAXN LPs.  Reports UB = max open/closed box bound (valid).  usage: bl7.py k..."""
import os,sys,signal,heapq
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bl5
def prop(lo,hi):
    lo=list(lo);hi=list(hi);n=len(lo)
    for i in range(n-2,-1,-1):lo[i]=max(lo[i],lo[i+1])
    for i in range(1,n):hi[i]=min(hi[i],hi[i-1])
    return lo,hi
def val(k,ls,lo,hi):
    r=bl5.LP(k,ls,lo,hi).solve()
    return -1e9 if r is None else 104*r[0]/k
if __name__=='__main__':
    signal.alarm(int(os.environ.get('AL','3000')))
    GAP=float(os.environ.get('GAP','0.05'));MAXN=int(os.environ.get('MAXN','3000'))
    for k in [int(a) for a in sys.argv[1:]]:
        ls=list(range(3,k-1));n=len(ls)
        lo,hi=prop([0]*n,[k]*n);v=val(k,ls,lo,hi);H=[(-v,lo,hi)];best_leaf=-1e9;cnt=1;closed_max=-1e9
        while H and cnt<MAXN:
            nv,lo,hi=heapq.heappop(H);v=-nv
            if v<=max(best_leaf,128.891-10)+0 and v<=best_leaf+GAP:closed_max=max(closed_max,v);continue
            gaps=[hi[i]-lo[i] for i in range(n)]
            if max(gaps)==0:best_leaf=max(best_leaf,v);closed_max=max(closed_max,v);continue
            if v-best_leaf<=GAP and best_leaf>-1e8:closed_max=max(closed_max,v);break
            i=max(range(n),key=lambda j:(gaps[j],-j));mid=(lo[i]+hi[i])//2
            for a,b in ((lo[i],mid),(mid+1,hi[i])):
                l2=list(lo);h2=list(hi);l2[i]=a;h2[i]=b;l2,h2=prop(l2,h2)
                if any(l2[j]>h2[j] for j in range(n)):continue
                vv=val(k,ls,l2,h2);cnt+=1
                if all(l2[j]==h2[j] for j in range(n)):best_leaf=max(best_leaf,vv)
                heapq.heappush(H,(-vv,l2,h2))
        ub=max([closed_max]+[-h[0] for h in H])
        top=H[0] if H else None
        print('COVER-BB k',k,'UB %.3f'%ub,'best leaf %.3f'%best_leaf,'LPs',cnt,'open',len(H),'top box',(top[1],top[2]) if top and os.environ.get('V') else '',flush=True)

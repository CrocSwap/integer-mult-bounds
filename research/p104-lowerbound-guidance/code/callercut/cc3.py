"""CALLERCUT cc3: SIZING ONLY (row NOT proved): cc1 + pure-pair cap  #{roles of type (2,(2,))} <= c*k  (env PPC=c).
Primal value cP is reported (the cap is handled by explicit columns; cB is not a certificate here)."""
import os,sys,signal
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import cc1,numpy as np
class LP(cc1.LP):
    def __init__(s_,k,rls,c):
        super().__init__(k,rls);s_.rowsE.append(('PP',0,-c*k))
    def erow(s_,D,P):
        k=s_.k;out=[]
        for kind,a,b in s_.rowsE:
            if kind=='PP':out.append(-1.0 if (D==2 and tuple(P)==(2,)) else 0.0)
            elif kind=='dm':out.append(min(D,2**(a+1))-1)
            elif kind=='R':out.append(sum(L for L in P if L<a) if D>=a else D*(D-1)/(k-1))
            elif kind=='R2':out.append(sum(L*(k-L) for L in P if L<a)/(k-1) if D>=a else (D*D-sum(L*L for L in P))/(k-1))
        return np.array(out,float)
    def price6(s_,w,y,wm,wx,we):
        out=super().price6(w,y,wm,wx,we);i=[j for j,(kd,a,b) in enumerate(s_.rowsE) if kd=='PP'][0]
        out=[(sc-(we[i] if (D==2 and tuple(P)==(2,)) else 0.0),D,P,mf) for sc,D,P,mf in out]
        # explicit rescoring of a few near-pure alternatives is unnecessary: the DP returns the best per (D,mf,hasone); pure pair is the only D=2 no-one type
        out.sort(reverse=True);return out
if __name__=='__main__':
    signal.alarm(3000);c=float(os.environ.get('PPC','1'))
    for k in [int(a) for a in sys.argv[1:]]:
        r=LP(k,list(range(3,k+1)),c).solve()
        if r is None:print('k',k,'INF');continue
        B,p,sup=r;print('PPC',c,'k',k,'cP %.3f'%(104*p/k),sup if os.environ.get('SUP') else '',flush=True)

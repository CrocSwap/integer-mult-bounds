"""MAINPLACE mp4: SIZING ONLY (row NOT proved): cc1 RC2 LP + DEEP3 row #{roles D>=l0} >= c (env L0 frac of k, C)."""
import os,sys,math
sys.path.insert(0,'code/callercut')
import cc1,numpy as np
class LP(cc1.LP):
    def __init__(s_,k,rls,l0,c):
        super().__init__(k,rls);s_.l0=l0;s_.rowsE.append(('DP',l0,float(c)))
    def erow(s_,D,P):
        out=list(super().erow.__wrapped__(s_,D,P)) if hasattr(super().erow,'__wrapped__') else None
        k=s_.k;o=[]
        for kind,a,b in s_.rowsE:
            if kind=='DP':o.append(1.0 if D>=a else 0.0)
            elif kind=='dm':o.append(min(D,2**(a+1))-1)
            elif kind=='R':o.append(sum(L for L in P if L<a) if D>=a else D*(D-1)/(k-1))
            elif kind=='R2':o.append(sum(L*(k-L) for L in P if L<a)/(k-1) if D>=a else (D*D-sum(L*L for L in P))/(k-1))
        return np.array(o,float)
    def price6(s_,w,y,wm,wx,we):
        i=len(s_.rowsE)-1;wd=we[i]
        out=super().price6(w,y,wm,wx,we[:i]) if False else None
        s_.rowsE,keep=s_.rowsE[:-1],s_.rowsE[-1]
        try:out=cc1.LP.price6(s_,w,y,wm,wx,we[:-1])
        finally:s_.rowsE.append(keep)
        out=[(sc+(wd if D>=s_.l0 else 0.0),D,P,mf) for sc,D,P,mf in out];out.sort(reverse=True);return out
if __name__=='__main__':
    f=float(os.environ.get('L0','0.5'));c=float(os.environ.get('C','3'))
    for k in [int(a) for a in sys.argv[1:]]:
        l0=max(3,math.ceil(f*k));r=LP(k,list(range(3,k+1)),l0,c).solve()
        B,p,sup=r;print('DEEP>=%d count>=%g k %d cP %.3f'%(l0,c,k,104*p/k),sup if os.environ.get('SUP') else '',flush=True)

"""MAINPLACE mp0: cc1 RC2 LP with ALL pure roles banned (SIZING, not a law) -> support (argmax design types)."""
import os,sys
sys.path.insert(0,'code/callercut')
import cc1
class LP(cc1.LP):
    def ok(s_,t):
        D,P,mf=t
        if len(P)==1:return False
        return super().ok(t)
    def price6(s_,*a):
        return [o for o in super().price6(*a) if len(o[2])>1]
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        r=LP(k,list(range(3,k+1))).solve()
        B,p,sup=r;print('NOPURE k',k,'cB %.3f cP %.3f'%(104*B/k,104*p/k),sup,flush=True)

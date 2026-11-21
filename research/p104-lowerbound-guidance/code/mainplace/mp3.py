"""MAINPLACE mp3: SIZING ONLY (filters are NOT laws): cc1 RC2 LP with type bans. env BAN = comma list of
 pure (no single-piece roles), mc (no (1,1) chords with mains), mc2 (no D=2 role carrying a main), m3 (mains only on D>=3), chordall (no D=2 roles at all)."""
import os,sys
sys.path.insert(0,'code/callercut')
import cc1
BAN=set(os.environ.get('BAN','').split(','))
def bad(D,P,mf):
    if 'pure' in BAN and len(P)==1:return True
    if 'mc' in BAN and D==2 and tuple(P)==(1,1) and mf==1:return True
    if 'm3' in BAN and mf==1 and D<3 and 1 in P:return True
    if 'chordall' in BAN and D==2:return True
    return False
class LP(cc1.LP):
    def ok(s_,t):
        return (not bad(*t)) and super().ok(t)
    def price6(s_,*a):
        return [o for o in super().price6(*a) if not bad(o[1],o[2],o[3])]
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        r=LP(k,list(range(3,k+1))).solve()
        if r is None:print('BAN',sorted(BAN),'k',k,'INFEASIBLE',flush=True);continue
        B,p,sup=r;print('BAN',sorted(BAN),'k',k,'cB %.3f cP %.3f'%(104*B/k,104*p/k),sup,flush=True)

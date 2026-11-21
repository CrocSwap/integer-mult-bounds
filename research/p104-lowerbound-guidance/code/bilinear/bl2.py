"""BILINEAR bl2: bl1 LP + WALT_w rows for w in a range (env WS='lo:hi', default 3:k) [+ optional bl1 extra ROW]. usage: bl2.py ROW k..."""
import os,sys,signal
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bl1
if __name__=='__main__':
    signal.alarm(3000);row=sys.argv[1]
    for k in [int(a) for a in sys.argv[2:]]:
        lo,hi=(os.environ.get('WS','3:%d'%k)).split(':');ws=range(int(lo),min(int(hi),k)+1)
        L=bl1.LP(k,bl1.parse(row,k));L.X+=bl1.walt_rows(k,ws);res=L.solve()
        if res is None:print('WALT',row,'k',k,'INFEASIBLE',flush=True);continue
        B,p,sup=res;print('WALT',row,'k',k,'cB',round(104*B/k,3),'cP',round(104*p/k,3),sup if os.environ.get('SUP') else '',flush=True)

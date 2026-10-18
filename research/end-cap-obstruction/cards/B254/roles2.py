import pickle,collections
from feas import *
S=pickle.load(open('S161.pkl','rb'));ok=set(pickle.load(open('ok161.pkl','rb')))
def lay(h):
    return ('cold0' if len(start[h])==0 else 'enter%d'%len(start[h]))+('/endFULL' if end[h]==FULLB else '/endU')
c=collections.Counter();ex={}
for h in S:
    bw=br=C=asc=ar=aw=0;nB=0
    for idx,(tag,e) in enumerate(prog):
        if e[0]=='scale':
            if e[1]==h and tag[0]=='A':asc=1
            continue
        if h in e[1:3]:
            t=tag[0]
            if t=='C':C=1
            if t=='B':
                nB+=1
                if e[1]==h:bw=1
                else:br=1
            if t=='A' and e[1]==h:aw=1
    # A-phase "real" (non-gauge) activity: A write by h counts
    role=('Cglue' if C else 'Brelay' if (bw and br) else 'other')+('+Arot' if asc else '')+('+Awr' if aw else '')
    k=(lay(h),role,'algOK' if h in ok else 'rotlock')
    c[k]+=1;ex.setdefault(k,h)
for k,n in sorted(c.items()):print(n,k,'ex',ex[k])

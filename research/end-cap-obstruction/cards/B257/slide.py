import sys,collections,itertools
from hoist import *
# per (reg) write positions
wr=collections.defaultdict(list);rd_=collections.defaultdict(list)
for i,(tag,e) in enumerate(prog):
    if e[0]=='add':wr[e[1]].append(i);rd_[e[2]].append(i)
    else:wr[e[1]].append(i)
import bisect
def nextw(s,i):
    L=wr[s];k=bisect.bisect_right(L,i);return L[k] if k<len(L) else 10**9
def lastread(x,r):
    L=rd_[x];k=bisect.bisect_left(L,r);return L[k-1] if k>0 else -1
def build(h):
    st,rd=contribs(h)
    if st!='ok':return None
    items=[]  # (ridx,x,a,widx,s,c,lo,hi,f)
    for ridx,x,a,ent in rd:
        for widx,s,c in ent:
            if prog[widx][0][0] in 'PC':return None
            lo=max(widx,lastread(x,ridx)+0)  # place after last read of x (insert after op lo)
            hi=min(ridx-1,nextw(s,widx)-1)   # insert after op hi at latest; s unwritten through hi
            # s-write at widx itself is h-write op not s. nextw(s,widx) first write to s after widx
            items.append([ridx,x,a,widx,s,c,lo,hi])
    return items
def mk(h,items,taus,mode='Z'):
    ins=collections.defaultdict(list);drop={i for i,(tag,e) in enumerate(prog) if e[0]=='add' and h in e[1:3]}
    for it,t in zip(items,taus):
        ridx,x,a,widx,s,c,lo,hi=it
        f=Fr(1)
        for i in range(widx+1,t+1):
            tg,e=prog[i]
            if e[0]=='scale' and e[1]==x:f*=Fr(e[2],e[3])
        # x scales between t and ridx: new op placed after t, before those scales -> need a*c/f' where f'=scales in (t,ridx)
        f=Fr(1)
        for i in range(t+1,ridx):
            tg,e=prog[i]
            if e[0]=='scale' and e[1]==x:f*=Fr(e[2],e[3])
        co=a*c/f
        E=[] if mode=='Z' else prog[ridx][1][5]
        ins[t].append((prog[t][0],['add',x,s,co.numerator,co.denominator,E]))
    new=[]
    for idx,(tag,e) in enumerate(prog):
        if idx not in drop:new.append((tag,e))
        for te in ins.get(idx,[]):new.append(te)
    return new
if __name__=='__main__':
    stat=collections.Counter();feas=[];nopos=0
    for h in range(224,704):
        if h in centers or track(h)[0]!='ok':continue
        items=build(h)
        if items is None:stat['PC']+=1;continue
        if any(it[6]>it[7] for it in items):stat['no-position']+=1;continue
        # candidate taus per item: all positions lo..hi (limit sample)
        cands=[]
        for it in items:
            cs=list(range(it[6],it[7]+1))
            if len(cs)>40:cs=cs[:20]+cs[-20:]
            cands.append(cs)
        nprod=1
        for c in cands:nprod*=len(c)
        stat['window-ok']+=1
        best=None
        combos=itertools.product(*cands) if nprod<=400 else [tuple(c[0] for c in cands),tuple(c[-1] for c in cands)]
        for taus in combos:
            ok,why,paid,m=simulate(mk(h,items,taus),removed={h})
            if ok:best=(taus,m);break
        if best:feas.append((h,best))
    print(stat,'frame-ok',len(feas),feas)

"""greedy bin evacuation: for lightly used bins, move every role to best-fit holes elsewhere (window, family, capacity), accept if the idle moment drops. argv: FILL_IN PROV FILL_OUT"""
import sys,json,gzip,collections,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fillbase import *
pv=json.load(open(sys.argv[2]));widths=pv['widths'];paid={k:{int(a):b for a,b in v.items()} for k,v in pv['paid'].items()}
rows=[list(x) for x in read(sys.argv[1])['rows']]
win={}
for key,(cap,times) in windows.items():
    r,ch=map(int,key.split(','));ts=sorted(times);win[r,ch]=(cap,ts[0],ts[-1])
wid=[widths[dispatch[tuple(order[x[0]])]][x[1]] for x in rows]
B=lambda i:tuple(rows[i][2:5])
members=collections.defaultdict(set);used=collections.Counter();cf=collections.defaultdict(collections.Counter)
for i in range(len(rows)):members[B(i)].add(i);used[B(i)]+=wid[i];cf[rows[i][0]][family(*B(i))]+=1
allbins=[(r,ch,p) for (r,ch) in win for p in range(112)]
K=0.0017037;g=lambda f:0.0 if f<=0 else f*(73/f)**K
cap=lambda b:win[b[:2]][0]
def move(i,b):
    o=B(i);t=rows[i][0];members[o].discard(i);used[o]-=wid[i];cf[t][family(*o)]-=1
    rows[i][2],rows[i][3],rows[i][4]=b;members[b].add(i);used[b]+=wid[i];cf[t][family(*b)]+=1
# holes index by free size
def holes():
    h=collections.defaultdict(list)
    for b in allbins:
        f=cap(b)-used[b]
        if f>0 and not(cap(b)==48 and used[b]==0):h[f].append(b)
    return h
tot=0;passes=0
for rnd in range(3):
    H=holes();cand=sorted([b for b in allbins if 0<used[b]<=int(__import__("os").environ.get("EVMAX","24"))],key=lambda b:used[b]);acc=0
    for b in cand:
        if used[b]==0:continue
        plan=[];tmpused=collections.Counter();tmpcf=collections.Counter();ok=True
        for i in sorted(members[b],key=lambda i:-wid[i]):
            t=rows[i][0];best=None
            for f in range(wid[i],49):
                for hb in H.get(f,[]):
                    if hb==b:continue
                    fr=cap(hb)-used[hb]-tmpused[hb]
                    lo,hi=win[hb[:2]][1:]
                    if fr>=wid[i] and lo<=t<=hi and cf[t][family(*hb)]+tmpcf[t,family(*hb)]==0:best=hb;break
                if best:break
            if not best:ok=False;break
            plan.append((i,best));tmpused[best]+=wid[i];tmpcf[t,family(*best)]+=1
        if not ok:continue
        touched={b}|{hb for _,hb in plan}
        before=sum(g(cap(x)-used[x]) for x in touched)
        after=g(cap(b))+sum(g(cap(x)-used[x]-tmpused[x]) for x in touched if x!=b)
        if after<before-1e-9:
            for i,hb in plan:move(i,hb)
            acc+=1;tot+=before-after
            H=holes()
    print('round',rnd,'evacuated',acc,'gain',tot,flush=True)
    if not acc:break
rows=compact(rows,lambda r:widths[dispatch[tuple(order[r[0]])]][r[1]])
idle,Hh=check(rows,widths,paid);print('idle',dict(sorted(idle.items())),'kappa',kappa(Hh))
open(sys.argv[3],'wb').write(gzip.compress(json.dumps(dict(columns=fill['columns'],dispatch_overrides=fill['dispatch_overrides'],rows=rows),separators=(',',':')).encode()))

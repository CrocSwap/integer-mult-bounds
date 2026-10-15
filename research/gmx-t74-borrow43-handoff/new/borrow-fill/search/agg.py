"""aggregate <-> fill conversion, realization (stage 2), exact pricing"""
import sys,collections,json,gzip,random;sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from base74 import *
cid={};
for ci,c in enumerate(CL):
    for b in cls[c]:cid[b]=ci
def to_agg(rows):
    bins=collections.defaultdict(list)
    for t,hh,rep,ch,port,off in rows:bins[rep,ch,port].append((t,wd[hh]))
    x=collections.defaultdict(collections.Counter);y=collections.Counter()
    for ci,c in enumerate(CL):
        for b in cls[c]:
            it=bins.get(b,[]);cnt=collections.Counter(w for t,w in it)
            x[ci][tuple(cnt[w] for w in WID)]+=1
            for t,w in it:y[ci,t,w]+=1
    return x,y
def realize_class(ci,xc,yc,rng):
    cap,lo,hi=CL[ci];bl=cls[CL[ci]]
    slots=[]
    for p,n in sorted(xc.items()):
        for _ in range(n):slots.append(collections.Counter({w:k for w,k in zip(WID,p) if k}))
    assert len(slots)==len(bl)
    rem=[sum(s.values()) for s in slots]
    byt=collections.defaultdict(list)
    for (t,w),n in yc.items():byt[t]+= [w]*n
    out=[[] for _ in bl]
    for t in sorted(byt,key=lambda t:(-len(byt[t]),rng.random())):
        used=set()
        ws=list(byt[t]);rng.shuffle(ws)
        # widths ordered by scarcity of bins offering them
        avail={w:sum(1 for b in range(len(bl)) if slots[b][w]) for w in set(ws)}
        for w in sorted(ws,key=lambda w:avail[w]):
            best=None;bk=None
            for b in range(len(bl)):
                if b in used or not slots[b][w]:continue
                k=(rem[b],slots[b][w],rng.random())
                if bk is None or k>bk:bk=k;best=b
            if best is None:return None
            used.add(best);slots[best][w]-=1;rem[best]-=1;out[best].append((t,w))
    assert all(r==0 for r in rem)
    return {bl[b]:out[b] for b in range(len(bl))}
def realize_cp(ci,xc,yc,tl=60,maxv=None):
    from ortools.sat.python import cp_model
    bl=cls[CL[ci]];slots=[]
    if maxv:
        nv=sum(n*sum(1 for (t,w),k in yc.items() if k and p[WID.index(w)]) for p,n in xc.items())
        if nv>maxv:print('   realize_cp too big',ci,nv,flush=True);return None
    for p,n in sorted(xc.items()):
        for _ in range(n):slots.append(dict(zip(WID,p)))
    m=cp_model.CpModel();z={}
    for b in range(len(bl)):
        for (t,w),n in yc.items():
            if n and slots[b][w]:z[b,t,w]=m.NewBoolVar('')
    for (t,w),n in yc.items():m.Add(sum(z[b,t,w] for b in range(len(bl)) if (b,t,w) in z)==n)
    bt=collections.defaultdict(list);bw=collections.defaultdict(list)
    for (b,t,w),v in z.items():bt[b,t].append(v);bw[b,w].append(v)
    for v in bt.values():m.AddAtMostOne(v)
    for b in range(len(bl)):
        for w in WID:m.Add(sum(bw[b,w])==slots[b][w])
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=tl;s.parameters.num_workers=1
    st=s.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        print('   realize_cp',ci,CL[ci],s.StatusName(st),len(z),dict(xc),flush=True);return None
    out=collections.defaultdict(list)
    for (b,t,w),v in z.items():
        if s.Value(v):out[bl[b]].append((t,w))
    return {b:out.get(b,[]) for b in bl}
def realize(x,y,seed=0,base_rows=None):
    rng=random.Random(seed)
    keep={}
    if base_rows is not None:
        bx,byy=to_agg(base_rows);bby=collections.defaultdict(collections.Counter)
        for (ci,t,w),n in byy.items():
            if n:bby[ci][t,w]+=n
        yb2=collections.defaultdict(collections.Counter)
        for (ci,t,w),n in y.items():
            if n:yb2[ci][t,w]+=n
        same={ci for ci in range(len(CL)) if +bx[ci]==+x[ci] and bby[ci]==yb2[ci]}
        for r in base_rows:
            ci=cid[tuple(r[2:5])]
            if ci in same:keep.setdefault(ci,[]).append(list(r))
        print('reusing',len(same),'classes from base',flush=True)
    yby=collections.defaultdict(collections.Counter)
    for (ci,t,w),n in y.items():
        if n:yby[ci][t,w]+=n
    hel={t:collections.defaultdict(list) for t in range(len(order))}
    for t in hel:
        for i,w in enumerate(wd):hel[t][w].append(i)
    rows=[];fails=[]
    for ci in keep:
        for r in keep[ci]:
            t=r[0];hel[t][wd[r[1]]].remove(r[1]);rows.append(r)
    for ci in range(len(CL)):
        if ci in keep:continue
        res=None
        for k in range(300):
            res=realize_class(ci,x[ci],yby[ci],rng)
            if res:break
        if res is None:res=realize_cp(ci,x[ci],yby[ci])
        if res is None:fails.append(ci);continue
        for b,items in res.items():
            off=0
            for t,w in sorted(items):
                rows.append([t,hel[t][w].pop(),b[0],b[1],b[2],off]);off+=w
    return rows,fails
def idle_of(x):
    I=collections.Counter()
    for ci,xc in x.items():
        for p,n in xc.items():
            f=idle(CL[ci][0],p)
            if f and n:I[f]+=n
    return I
def save(rows,path):
    open(path,'wb').write(gzip.compress(json.dumps(dict(columns=fill['columns'],dispatch_overrides=fill['dispatch_overrides'],rows=rows),separators=(',',':')).encode()))
if __name__=='__main__':
    rows=read(sys.argv[1])['rows'];x,y=to_agg(rows);print('idle',dict(sorted(idle_of(x).items())))
    r2,fails=realize(x,y);print('fails',fails)
    if not fails:
        paid={p:{int(k):v for k,v in d['actual_paid_profile'].items()} for p,d in prov.items()}
        widths={p:d['widths'] for p,d in prov.items()}
        idl,H=check(r2,widths,paid);print('check ok',dict(sorted(idl.items())),kappa(H))

"""time-set LNS: free the items of a set TS of calls in every class open there; others' items fixed.
argv: IN(fill or pkl) OUTDIR ROUNDS SEED TL"""
import sys,os,time,pickle;sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from agg import *
from ortools.sat.python import cp_model
fin,outd,ROUNDS,SEED,TL=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5])
os.makedirs(outd,exist_ok=True);rng=random.Random(SEED)
if fin.endswith('.pkl'):x,y=pickle.load(open(fin,'rb'))
else:x,y=to_agg(read(fin)['rows'])
yby=collections.defaultdict(collections.Counter)
for (ci,t,w),n in y.items():
    if n:yby[ci][t,w]=n
SC=10**6;HI=[int(round(SC*h(f))) for f in range(49)]
GOOD={(8,(0,0,0,1,0)),(16,(0,0,0,2,0)),(16,(0,0,1,0,1)),(32,(0,0,0,0,3)),(32,(0,0,0,4,0)),(32,(0,0,1,2,1)),(32,(0,0,2,0,2)),(32,(0,1,0,0,3)),(32,(1,0,0,0,3)),(48,(0,0,0,0,0)),(48,(0,0,0,0,5))}
EXTRA=[(32,(0,0,0,0,1)),(32,(0,0,0,0,2)),(32,(0,0,0,1,2)),(48,(0,0,0,0,4)),(48,(0,0,0,1,4)),(32,(1,0,0,1,2)),(48,(0,0,0,0,1)),(32,(0,0,0,0,0)),(48,(1,0,0,1,4))]
def lossy_classes():return [ci for ci in range(len(CL)) if any((CL[ci][0],p) not in GOOD for p,n in x[ci].items() if n)]
def tot():return sum(n*HI[idle(CL[ci][0],p)] for ci in x for p,n in x[ci].items())
print('start',tot(),dict(sorted(idle_of(x).items())),flush=True)
FROZEN=set();prevTS=None
for rnd in range(ROUNDS):
    t0=time.monotonic()
    lc=lossy_classes()
    if not lc:print('no lossy classes');break
    TS=set()
    for ci in rng.sample(lc,min(len(lc),int(os.environ.get('NL',4)))):
        ts={t for (t,w),n in yby[ci].items() if n}
        if FROZEN and rnd>0 and prevTS:continue
        TS|=set(rng.sample(sorted(ts),min(len(ts),int(os.environ.get('PERCLS',6)))))
    if FROZEN and prevTS:TS=set(prevTS)
    prevTS=TS
    extra=int(os.environ.get('EXTRAT',4));TS|=set(rng.sample(range(len(order)),extra))
    FL=int(os.environ.get('FREEZELATE',9999));F=[ci for ci in range(len(CL)) if ci not in FROZEN and not (CL[ci][1]>=FL and CL[ci][0]>8 and rng.random()<0.85) and any(CL[ci][1]<=t<=CL[ci][2] for t in TS)]
    m=cp_model.CpModel();X={};Y={}
    for ci in F:
        cap,lo,hi=CL[ci];n=len(cls[CL[ci]])
        ps={p for (c,p) in GOOD|set(EXTRA) if c==cap}|{p for p,k in x[ci].items() if k}
        for p in ps:X[ci,p]=m.NewIntVar(0,n,'')
        m.Add(sum(X[ci,p] for p in ps)==n)
        mytimes=[t for t in TS if lo<=t<=hi]
        ft=collections.Counter()
        for (t,ww),k in yby[ci].items():
            if t not in TS:ft[t]+=k
        if ft and (ci,(0,0,0,0,0)) in X:m.Add(n-X[ci,(0,0,0,0,0)]>=max(ft.values()))
        for t in mytimes:
            for w in WID:
                if w<=cap:Y[ci,t,w]=m.NewIntVar(0,min(n,DW[w]),'')
            fixed_t=0
            E0=(0,0,0,0,0)
            m.Add(sum(Y[ci,t,w] for w in WID if w<=cap)<=n-(X[ci,E0] if (ci,E0) in X else 0))
            for S2 in ((7,8,9),(8,9),(4,5),(4,5,7)):
                ws=[w for w in S2 if w<=cap]
                if ws:m.Add(sum(Y[ci,t,w] for w in ws)<=sum(X[ci,p] for p in ps if any(p[WID.index(w)] for w in ws)))
        for j,w in enumerate(WID):
            if w>cap:continue
            fixed=sum(k for (t,ww),k in yby[ci].items() if ww==w and t not in TS)
            nw=sum(X[ci,p] for p in ps if p[j]>=1)
            for t in mytimes:m.Add(Y[ci,t,w]<=nw)
            fx=[k for (t,ww),k in yby[ci].items() if ww==w and t not in TS]
            if fx:m.Add(nw>=max(fx))
            m.Add(fixed+sum(Y[ci,t,w] for t in mytimes)==sum(p[j]*X[ci,p] for p in ps))
    tw=collections.defaultdict(list)
    for (ci,t,w),v in Y.items():tw[t,w].append(v)
    for (t,w),vs in tw.items():m.Add(sum(vs)==sum(yby[ci][t,w] for ci in F))
    for (ci,p),v in X.items():m.AddHint(v,x[ci][p])
    for (ci,t,w),v in Y.items():m.AddHint(v,yby[ci][t,w])
    m.Minimize(sum(HI[idle(CL[ci][0],p)]*v for (ci,p),v in X.items()))
    cur=sum(n*HI[idle(CL[ci][0],p)] for ci in F for p,n in x[ci].items())
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=TL;s.parameters.num_workers=int(os.environ.get('NW',2))
    st=s.Solve(m)
    print(rnd,'TS',len(TS),'F',len(F),'vars',len(X)+len(Y),s.StatusName(st),'obj',s.ObjectiveValue() if st in (2,4) else None,'cur',cur,'bound',s.BestObjectiveBound(),round(time.monotonic()-t0),flush=True)
    if not (st in (cp_model.OPTIMAL,cp_model.FEASIBLE) and s.ObjectiveValue()<cur-0.5):FROZEN=set();prevTS=None
    if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) and s.ObjectiveValue()<cur-0.5:
        nx={};ny={};ok=True;changed=[]
        for ci in F:
            nx[ci]=collections.Counter({p:s.Value(X[ci,p]) for (c,p) in X if c==ci and s.Value(X[ci,p])})
            ny[ci]=collections.Counter({k:v for k,v in yby[ci].items() if k[0] not in TS})
            for (c,t,w),v in Y.items():
                if c==ci and s.Value(v):ny[ci][t,w]+=s.Value(v)
            if nx[ci]==x[ci] and ny[ci]==yby[ci]:continue
            changed.append(ci)
        bad=[]
        for ci in changed:
            r=None
            for k in range(5):
                r=realize_class(ci,nx[ci],ny[ci],rng)
                if r:break
            if r is None:r=realize_cp(ci,nx[ci],ny[ci],30,200000)
            if r is None:bad.append(ci)
        print('  changed',len(changed),'unrealizable',bad,flush=True)
        if bad:
            FROZEN|=set(bad);continue
        FROZEN=set()
        for ci in changed:x[ci]=nx[ci];yby[ci]=ny[ci]
        print('  ACCEPT',tot(),dict(sorted(idle_of(x).items())),flush=True)
        y2=collections.Counter({(ci,t,w):n for ci,c in yby.items() for (t,w),n in c.items()})
        pickle.dump((x,y2),open(outd+'/state.pkl','wb'))

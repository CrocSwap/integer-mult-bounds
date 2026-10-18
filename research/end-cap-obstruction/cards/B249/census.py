import gzip,json,sys,collections
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B240')
from prof import basis
w=json.load(gzip.open(sys.argv[1] if len(sys.argv)>1 else __import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz'))
v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];n=2*v+R
FULLB=basis([1<<i for i in range(h)])
_c={}
def B(U):
    k=tuple(U)
    if k not in _c:_c[k]=basis(U)
    return _c[k]
_n={}
def nested(a,b):
    k=(a,b)
    if k not in _n:
        ok=True
        for x in a:
            for y in b:
                if x>>(y.bit_length()-1)&1:x^=y
            if x:ok=False;break
        _n[k]=ok
    return _n[k]
tail=[w['cleanup'][i][:-1]+[U] for i,U in w['early_cleanup']]
ev=[]
for sec in ('A','B'):
    for e in w[sec]:ev.append((sec,e))
for e in tail:ev.append(('T',e))
END=len(ev)-1
start=[(p,) for p in w['ports']]+[()]*(v+R)
start=[B(s) for s in start]
for q,U in w.get('start_extra',{}).items():start[int(q)]=B(U)
fin=[FULLB]*n
for q,U in w.get('helper_final',{}).items():fin[int(q)]=B(U)
for q in range(v,2*v):fin[q]=B([x for x in range(1,1<<h) if (x&w['ports'][q-v]).bit_count()%2==0])
def regs(e):return (e[1],e[2]) if e[0]=='add' else (e[1],)
ops=collections.defaultdict(list)   # reg -> [(i,frame,isread)]
reads=collections.defaultdict(list)
for i,(s,e) in enumerate(ev):
    f=B(e[-1])
    ops[e[1]].append((i,f))
    if e[0]=='add':ops[e[2]].append((i,f));reads[e[2]].append((i,f))
# leavers
LV={}
for r in range(v):
    if reads[r]:
        t,g=max(reads[r],key=lambda x:x[0]);LV[r]=(t,g)
print('leavers',len(LV),'of',v,'gdim hist',sorted(collections.Counter(len(g) for t,g in LV.values()).items()))
# does any leaver have a later write? climbs left
print('leaver sources with no read',v-len(LV))
# helpers
cat={}
H={}
for hh in range(2*v,n):
    O=ops[hh]
    H[hh]=O
def layer(hh):
    c0=len(start[hh])==0
    return ('cold0' if c0 else 'enter%d'%len(start[hh]))+('/endFULL' if fin[hh]==FULLB else '/endU')
def grp(hh):
    return 'a' if hh<2*v+224 else 'b' if hh<2*v+224+144 else 'c'
print('helper index ranges by start/end:')
rng=collections.defaultdict(list)
for hh in H:rng[layer(hh)].append(hh)
for k,l in sorted(rng.items()):print(' ',k,len(l),min(l),max(l))
res=collections.defaultdict(lambda:collections.Counter())
best={}
for hh,O in H.items():
    L=layer(hh);res[L]['n']+=1
    if not O:res[L]['noops']+=1;continue
    res[L]['frame0ops']+=any(len(f)==0 for i,f in O)
    bw=bp=False;bc=0;bcf=0
    for z,(tL,g) in LV.items():
        # timed
        k=len(O)
        while k>0 and O[k-1][0]>tL and nested(g,O[k-1][1]):k-=1
        kf=len(O)
        while kf>0 and nested(g,O[kf-1][1]):kf-=1
        for kk,fl in ((k,0),(kf,1)):
            cov=(len(O)-kk)/len(O)
            if fl==0:
                bc=max(bc,cov)
                if kk==0:bw=True
                elif cov>=0.8:bp=True
            else:
                bcf=max(bcf,cov)
                if kk==0:res[L]['whole_fo']+=0
        if kf==0:res[L]['_wf']+=1
    res[L]['whole']+=bw;res[L]['p80']+=(bp and not bw);res[L]['anyoverlap']+=bc>0
    res[L]['bestcov_max_x1000']=max(res[L]['bestcov_max_x1000'],int(bc*1000))
    res[L]['bestcov_frameonly_max_x1000']=max(res[L]['bestcov_frameonly_max_x1000'],int(bcf*1000))
    res[L]['whole_frameonly_helpers']+=any(
        all(nested(g,f) for i,f in O) for z,(tL,g) in LV.items())
    res[L]['p80_frameonly_helpers']+=any(
        sum(1 for i,f in O if nested(g,f))/len(O)>=0.8 for z,(tL,g) in LV.items())
tot=collections.Counter()
for L,c in sorted(res.items()):
    c.pop('_wf',None);print(L,dict(c))
    for k in('n','whole','p80'):tot[k]+=c[k]
print('TOTAL',dict(tot))
# B236 live co-framing: any source reg r (live, frame at op time) nested in op frame for ALL ops of helper
def frame_at(r,i):
    f=start[r]
    for (j,ff) in ops[r]:
        if j<i:f=ff
        else:break
    return f
co=collections.defaultdict(lambda:[0,0,0.0])
for hh,O in H.items():
    O2=[(i,f) for i,f in O if len(f)>0]
    if not O2:continue
    L=layer(hh);bb=0;ba=False
    for r in range(v):
        c=sum(1 for i,f in O2 if nested(frame_at(r,i),f))/len(O2)
        bb=max(bb,c)
        if c==1:ba=True
    co[L][0]+=1;co[L][1]+=ba;co[L][2]+=bb
for L,(a,b,c) in sorted(co.items()):print('cof',L,'n',a,'helpers with a live source whole-life co-framed',b,'mean best frac %.2f'%(c/a))

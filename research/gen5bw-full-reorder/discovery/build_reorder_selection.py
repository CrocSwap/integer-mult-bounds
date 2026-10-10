"""Freeze reorder-selection.json: run the pipeline through the last stage of this package (kernel, second descent,
restoration, terminal sinks), screen every ADD whose frame is a strict
breakpoint of an operand path, try it at the frame of each of the six previous/next ADD incidences of either operand
(admitted when no crossed gate reads a or writes b, no COPY/ERASE of a is crossed and both rebuilt frame chains stay
nested), price the change of both operand paths with phi(r) = r ln(120/r), and keep a greedy disjoint set of
negative moves; moves whose result breaks the source-span rule of any gate are dropped. Round r screens the word
after the previous rounds. Not run by verify.py.
Usage: python3 -B discovery/build_reorder_selection.py TAG [PREVIOUS_TAG ...]   (reorder, then reorder2 reorder)
Ported from PR #299's reorder stage onto PR #305's weighted gen5b word (second descent before restoration)."""
import sys,json,importlib.util,hashlib,math,bisect
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('portable527_prepare',ROOT/'prepare.py').prepare()
producer=load('portable527_physical',ROOT/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
run=load('portable527_parity',ROOT/'parity_transform.py').run(producer)
for st in ('descent_transform','target_transform','kernel_transform'):run=load('portable527_'+st,ROOT/(st+'.py')).run(run)
run=load('portable527_descent2',ROOT/'descent_transform.py').run(run,selection_path=ROOT/'descent2-selection.json')
for st in ('restore_transform','sink_transform'):run=load('portable527_'+st,ROOT/(st+'.py')).run(run)
TAG=sys.argv[1];rm=load('portable527_reorder',ROOT/'reorder_transform.py')
for prev in sys.argv[2:]:run=rm.run(run,tag=prev)
W,C=run['W'],run['C'];old=run['records'];v=W.v;n=2*v+len(run['context']['regs']);init=dict(run['initial_state']);final=dict(run['final_state'])
cats=list(run['physical']['category_names']);ev=[tuple(old[k:k+6])for k in range(0,len(old),6)]
phi=lambda r:r*math.log(120/r)if r else 0.0
incf=defaultdict(list);reads=defaultdict(list);writes=defaultdict(list)
for i,(op,a,b,c,f,z)in enumerate(ev):
    if op==1:
        incf[a].append((i,f,True));writes[a].append(i)
        if b!=n:incf[b].append((i,f,True));reads[b].append(i)
    elif op==2:incf[a].append((i,c,False));reads[a].append(i)
    elif op==3:reads[a].append(i)
inct={s:[t for t,f,x in L]for s,L in incf.items()}
def cost(fs):return sum(phi(C.dimf[b]-C.dimf[a])for a,b in zip(fs,fs[1:])if a!=b)
def legal(fs):return all(C.sub(a,b)for a,b in zip(fs,fs[1:]))
def path(r,dele=None,add=None):
    L=[(t,f)for t,f,x in incf[r]if t!=dele]+([add]if add else []);L.sort()
    return [init[r]]+[f for t,f in L]+[final[r]]
def count(L,lo,hi):return bisect.bisect_left(L,hi)-bisect.bisect_left(L,lo)
cands=[]
for i,(op,a,b,c,f,z)in enumerate(ev):
    if op!=1 or b==n:continue
    def bp(r):
        L=inct[r];k=bisect.bisect_left(L,i);pf=incf[r][k-1][1]if k else init[r];nf=incf[r][k+1][1]if k+1<len(L)else final[r]
        return pf!=f and nf!=f
    if not(bp(a)or bp(b)):continue
    base=cost(path(a))+cost(path(b));best=None
    for r in(a,b):
        L=inct[r];k=bisect.bisect_left(L,i)
        for j in range(1,7):
            for kk,side in((k+j,'before'),(k-j,'after')):
                if not(0<=kk<len(L))or not incf[r][kk][2]:continue
                T,F,_=incf[r][kk];lo,hi=(i+1,T)if side=='before'else(T+1,i)
                if count(reads[a],lo,hi)or count(writes[b],lo,hi):continue
                pa=path(a,i,(T+(-.5 if side=='before'else .5),F));pb=path(b,i,(T+(-.5 if side=='before'else .5),F))
                if not(legal(pa)and legal(pb)):continue
                d=cost(pa)+cost(pb)-base
                if d<-1e-9 and(best is None or (d,T)<(best[0],best[1])):best=(d,T,side,F)
    if best:cands.append((best[0],i,best[1],best[2],best[3]))
cands.sort(key=lambda x:(round(x[0],9),x[1]));used=set();keep=[]
for d,i,T,side,F in cands:
    op,a,b,c,f,z=ev[i]
    if {a,b}&used:continue
    used|={a,b};keep.append(dict(record=i,anchor=T,side=side,incidence=[a,b,c],category=cats[z],old_frame_rank=C.dimf[f],frame_rank=C.dimf[F],frame_basis=[list(x)for x in C.B[F]],phi=round(d,6)))
print('candidates',len(cands),'kept',len(keep),'phi',sum(e['phi']for e in keep),flush=True)
def mk(keep):return dict(status='GEN5_REORDER_SCREEN',tag=TAG,n=n,v=v,input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),input_scalar_sha256=run['physical']['scalar_projection_sha256'],selected=len(keep),moves=keep,expected_local_delta={})
while True:
    sel=mk(keep);out,initial,fin,cats2,proof,nn,_=rm.transform(run,sel,TAG)
    bad=rm.span_violations(out,W,C,n,v)
    if not bad:break
    badregs=set()
    for k,src in bad:badregs|={out[6*k+1],out[6*k+2]}
    drop=[e for e in keep if set(e['incidence'][:2])&badregs]
    print('span violations',len(bad),'dropping',len(drop),flush=True);assert drop
    keep=[e for e in keep if e not in drop]
hist=Counter()
for k in range(0,len(out),6):
    if out[k]==0 and out[k+4]:hist[out[k+4]]+=1
    elif out[k]==2:hist[out[k+5]]+=1
dd=Counter(hist);dd.subtract({int(r):c for r,c in run['physical']['paid_histogram'].items()})
sel['expected_local_delta']={str(r):c for r,c in sorted(dd.items())if c}
(ROOT/(TAG+'-selection.json')).write_text(json.dumps(sel,separators=(',',':'))+'\n')
print(TAG,'kept',len(keep),'delta',sel['expected_local_delta'],'phi',sum(c*phi(int(r))for r,c in sel['expected_local_delta'].items()),flush=True)

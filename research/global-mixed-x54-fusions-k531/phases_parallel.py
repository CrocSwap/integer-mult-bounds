"""Parallel version of pr558 phases_full.py: identical computation, edges split over processes.
CLIFFORD-RECIPES.json is byte-identical; CLIFFORD-REVIEW.json identical except 'seconds'."""
import gzip,hashlib,json,sys,time,os
from collections import Counter
from pathlib import Path
import subprocess
sys.path.insert(0,str(Path(sys.argv[2]).resolve()))
from clifford_exact import *

OUT=Path(sys.argv[1]);P=OUT/'CANONICAL-WORD.json.gz'
JOBS=int(os.environ.get('FAST_PHASES_JOBS','4'))
c=json.load(gzip.open(P));n=c['h'];frames=c['frames']
ops=None
def build():
    global ops
    ops=[]
    for U in frames:
        op=canonical_frame(n,U)
        L=[u|(u<<n) for u in U]+[v<<n for v in nullspace(U,n)]
        pre=[x|(z<<n) for x,z,p in inverse(op.tab)[n:]]
        assert rank(L)==n and rank(L+pre)==n
        assert rank([x for x,z,p in op.tab[n:]])==len(U)
        ops.append(op)
def edge(ab):
    a,b=ab
    op=ops[a].adjoint().then(ops[b]);rec,compiled=lower_child(op)
    assert rec['rank']==abs(len(frames[a])-len(frames[b]))
    return {'old':a,'new':b,**rec}
def port(ir):
    i,q=ir;res=[];F=fourier(n)
    for role,old,f in [('source',cgate(n,q),c['start'][i]),
                       ('target',cgate(n,q).adjoint().then(F),c['final'][c['v']+i])]:
        rec,compiled=lower_child(old.adjoint().then(ops[f]));assert rec['rank']==0
        res.append({'port':i,'role':role,'frame':f,**rec})
    return res
CACHE=os.environ.get('FAST_PHASES_CACHE')  # opt-in memo of pure per-edge/per-port lowering, keyed by frame CONTENT
def ekey(a,b):return hashlib.sha256(json.dumps([n,frames[a],frames[b]]).encode()).hexdigest()
def pkey(i,q):
    f1=c['start'][i];f2=c['final'][c['v']+i]
    return hashlib.sha256(json.dumps([n,q,frames[f1],frames[f2]]).encode()).hexdigest()
def load_cache():
    d={}
    if CACHE and Path(CACHE).is_dir():
        for p in Path(CACHE).glob('*.json'):
            try:d.update(json.loads(p.read_text()))
            except ValueError:pass
    return d
def split(rec):return {k:v for k,v in rec.items() if k not in('old','new','port','role','frame')}
W=os.environ.get('FAST_WORKER')
if W is not None:
    k=int(W);build()
    edges=set(map(tuple,c['edges']))|{(a,b) for f in c['center_frames'] for a,b in ((f,0),(0,f))}
    elist=sorted(edges)
    cache=load_cache()
    part={'edges':[edge(e) if ekey(*e) not in cache else {'old':e[0],'new':e[1],**cache[ekey(*e)]} for e in elist[k::JOBS]]}
    if k==0:part['ports']=[x for i,q in enumerate(c['ports']) for x in (port((i,q)) if pkey(i,q) not in cache else [{'port':i,'role':r,'frame':f,**cache[pkey(i,q)][r]} for r,f in (('source',c['start'][i]),('target',c['final'][c['v']+i]))])]
    (OUT/('.part%d.json'%k)).write_text(json.dumps(part,sort_keys=True))
    sys.exit(0)
if True:
    start=time.monotonic()
    edges=set(map(tuple,c['edges']))|{(a,b) for f in c['center_frames'] for a,b in ((f,0),(0,f))}
    elist=sorted(edges)
    ps=[subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),str(OUT),sys.argv[2]],env=dict(os.environ,FAST_WORKER=str(k)),creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0) for k in range(JOBS)]
    for p in ps:assert p.wait()==0
    parts=[json.loads((OUT/('.part%d.json'%k)).read_text()) for k in range(JOBS)]
    recipes=[None]*len(elist)
    for k,pt in enumerate(parts):
        for j,r in enumerate(pt['edges']):recipes[k+j*JOBS]=r
    adapters=parts[0]['ports']
    for k in range(JOBS):(OUT/('.part%d.json'%k)).unlink()
    if CACHE:
        Path(CACHE).mkdir(parents=True,exist_ok=True);new={}
        for (a,b),r in zip(elist,recipes):new[ekey(a,b)]=split(r)
        for i in range(len(c['ports'])):new[pkey(i,c['ports'][i])]={x['role']:split(x) for x in adapters if x['port']==i}
        (Path(CACHE)/('%d-%d.json'%(os.getpid(),time.time_ns()))).write_text(json.dumps(new))
    print('exact phase edges',len(elist),'/',len(edges),'seconds',time.monotonic()-start,flush=True)
    hist=Counter(r['rank'] for r in recipes)
    build()  # parent re-validates every frame as the original does
    raw=json.dumps({'children':recipes,'endpoint_adapters':adapters},sort_keys=True,separators=(',',':')).encode()
    (OUT/'CLIFFORD-RECIPES.json').write_bytes(raw)
    result={'status':'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES',
            'canonical_word_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),
            'frames':len(frames),'directed_edges':len(edges),'ranks':dict(hist),
            'endpoint_adapters':len(adapters),'all_child_equalities_include_global_phase':True,
            'recipe_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-start,
            'scope':'Every local frame and center transition. Expanded scalar-interface integration and global emitted program are separate obligations.'}
    (OUT/'CLIFFORD-REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS exact local phases',result['seconds'],'seconds',flush=True)

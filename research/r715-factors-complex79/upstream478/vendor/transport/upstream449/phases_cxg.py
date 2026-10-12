# Adapted from PR425 for heterogeneous centres by icekylinx with Codex assistance.
"""Exact phase-aware lowering of every used edge of the new structural word."""
import gzip,hashlib,json,sys,time
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path('work/odd-stages').resolve()))
from clifford_exact import *

OUT=Path('split-centres');P=OUT/'CANONICAL-WORD.json.gz'
c=json.load(gzip.open(P));n=c['h'];frames=c['frames'];start=time.monotonic();ops=[]
for U in frames:
    op=canonical_frame(n,U)
    L=[u|(u<<n) for u in U]+[v<<n for v in nullspace(U,n)]
    pre=[x|(z<<n) for x,z,p in inverse(op.tab)[n:]]
    assert rank(L)==n and rank(L+pre)==n
    assert rank([x for x,z,p in op.tab[n:]])==len(U)
    ops.append(op)
edges=set(map(tuple,c['edges']))|{(a,b) for f in c['center_frames'] for a,b in ((f,0),(0,f))};recipes=[];hist=Counter()
for i,(a,b) in enumerate(sorted(edges)):
    op=ops[a].adjoint().then(ops[b]);rec,compiled=lower_child(op)
    assert rec['rank']==abs(len(frames[a])-len(frames[b]))
    hist[rec['rank']]+=1;recipes.append({'old':a,'new':b,**rec})
    if i%200==0:print('exact phase edges',i,'/',len(edges),'seconds',time.monotonic()-start,flush=True)
adapters=[];F=fourier(n)
for i,q in enumerate(c['ports']):
    for role,old,f in [('source',cgate(n,q),c['start'][i]),
                       ('target',cgate(n,q).adjoint().then(F),c['final'][c['v']+i])]:
        rec,compiled=lower_child(old.adjoint().then(ops[f]));assert rec['rank']==0
        adapters.append({'port':i,'role':role,'frame':f,**rec})
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

# Warp-aware copy of phases_full.py (PR425 / icekylinx with Codex assistance, heterogeneous centres).
# BW: exact lowering of every anticipatory-dirty-borrowing warp (PR2226, Cinna Davis @1337isnot1337, with OpenAI Codex assistance):
# each distinct physical warp product T_to K_G^{+-1} T_from^-1 is lowered with the unchanged lower_child and must have rank ZERO
# (a monomial Clifford); its serialized monomial is then compared with an independent exact numpy column product on all 512 columns.
"""Exact phase-aware lowering of every used edge of a BORROW canonical word, warps included.  usage: bw_phases.py OUT_DIR"""
if not __debug__:
    raise RuntimeError('assertions must remain enabled')   # every check of this stage is an assert
import gzip,hashlib,json,sys,time
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor/clifford'));sys.path.insert(0,str(HERE))
from clifford_exact import *
import bw_gauss
from bw_adapters import Kop

OUT=Path(sys.argv[1]);P=OUT/'CANONICAL-WORD.json.gz'
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
# BW: warps.  Edge classes are (sign, operator, from frame, to frame); the physical product is T_to K^{+-1} T_from^-1.
G_of={w['op']:w['G_columns'] for w in c.get('warps',[])}
warps=[]
for sign,op_id,f0,f1 in sorted(map(tuple,c.get('warp_edges',[]))):
    G=G_of[op_id];K=Kop(G);Ks=K if sign>0 else K.adjoint()
    op=ops[f0].adjoint().then(Ks).then(ops[f1]);rec,compiled=lower_child(op)
    assert rec['rank']==0 and rec['right'] is None,('warp is not a monomial Clifford',sign,op_id,f0,f1)
    Z=bw_gauss.warp_product(G,frames[f0],frames[f1],sign*op_id,n)
    assert bw_gauss.equal_scaled(Z,bw_gauss.recipe_matrix(rec['left'],n)),('recipe differs from the exact column product',sign,op_id,f0,f1)
    hist['warp']+=1;warps.append({'sign':sign,'op':op_id,'old':f0,'new':f1,'G_columns':G,**rec})
raw=json.dumps({'children':recipes,'endpoint_adapters':adapters,'warps':warps},sort_keys=True,separators=(',',':')).encode()
(OUT/'CLIFFORD-RECIPES.json').write_bytes(raw)
result={'status':'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES',
        'canonical_word_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),
        'frames':len(frames),'directed_edges':len(edges),'ranks':{str(k):x for k,x in hist.items()},
        'endpoint_adapters':len(adapters),'warp_recipes':len(warps),'warp_recipes_rank_zero':all(w['rank']==0 for w in warps),
        'warp_recipes_equal_exact_512_column_product':True,
        'all_child_equalities_include_global_phase':True,
        'recipe_sha256':hashlib.sha256(raw).hexdigest(),'seconds':time.monotonic()-start,
        'scope':'Every local frame, centre transition and warp. Expanded scalar-interface integration and global emitted program are separate obligations.'}
(OUT/'CLIFFORD-REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS exact local phases',result['seconds'],'seconds',flush=True)

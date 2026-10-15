"""Independent recheck of the emitted warp recipes against the emitted programs (numpy only, no clifford_exact).

Every warp event class (sign, operator, from frame, to frame) used by LOCAL-PROGRAMS in either orientation must have a recipe in
CLIFFORD-RECIPES.json whose serialized monomial equals, on all 512 columns exactly (global phase included), the product
T_to K_G^{+-1} T_from^-1 recomputed here from the canonical word's G and frames (port of PR2226's operators.py).  The logical
K_G recipe of RESIDUAL-ADAPTERS.json must equal the exact K_G.  Mutated recipes (phase, translation, quadratic form, wrong G,
inverse used for the forward warp, a missing class, swapped frames) must all be rejected.  usage: bw_check_recipes.py OUT_DIR
"""
if not __debug__:
    raise RuntimeError('assertions must remain enabled')   # every check of this stage is an assert
import copy,gzip,hashlib,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bw_gauss as g
OUT=Path(sys.argv[1]);t0=time.monotonic()
c=json.load(gzip.open(OUT/'CANONICAL-WORD.json.gz'));h=c['h'];frames=c['frames']
progs=json.load(gzip.open(OUT/'LOCAL-PROGRAMS.json.gz'))
rec_all=json.loads((OUT/'CLIFFORD-RECIPES.json').read_text())
res_all=json.loads((OUT/'RESIDUAL-ADAPTERS.json').read_text())
G_of={w['op']:w['G_columns'] for w in c.get('warps',[])}
used=set()
for orientation in ('forward','backward'):
    for e in progs[orientation]:
        if e[0]=='warp':used.add((1 if e[2]>0 else -1,abs(e[2]),e[3],e[4]))
assert used==set(map(tuple,c.get('warp_edges',[]))),'emitted warp classes differ from the word'
by={(w['sign'],w['op'],w['old'],w['new']):w for w in rec_all.get('warps',[])}
assert set(by)==used,('recipe classes differ from the emitted warp classes',len(set(by)^used))
def numeric_K(G):
    pv,ph=g.monomial(list(G),h);N=1<<h;re=np.zeros((N,N),dtype=np.int64);im=np.zeros((N,N),dtype=np.int64)
    unit=[(1,0),(0,1),(-1,0),(0,-1)]
    for x in range(N):re[pv[x],x],im[pv[x],x]=unit[ph[x]]
    return re,im,0
def product_ok(sign,op,f0,f1,left,G=None):
    G=G_of[op] if G is None else G
    if left is None:return False
    try:Z=g.warp_product(G,frames[f0],frames[f1],sign*op,h)
    except AssertionError:return False
    return g.equal_scaled(Z,g.recipe_matrix(left,h))
def logical_ok(op,rec,G=None):
    G=G_of[op] if G is None else G
    return g.equal_scaled(numeric_K(G),g.recipe_matrix(rec,h))
for key,w in sorted(by.items()):
    sign,op,f0,f1=key
    assert w['rank']==0 and w['right'] is None and w['G_columns']==G_of[op],key
    assert product_ok(sign,op,f0,f1,w['left']),('warp recipe is not the exact column product',key)
for w in c.get('warps',[]):
    r=res_all['warps'][str(w['op'])]
    assert r['G_columns']==w['G_columns'] and (r['from_frame'],r['to_frame'])==(w['from_frame'],w['to_frame'])
    assert logical_ok(w['op'],r['K']),('logical K_G recipe is not exact',w['op'])
controls=[]
def reject(name,ok):
    if ok:raise AssertionError('mutation accepted: '+name)
    controls.append(name)
if by:
    key=next(k for k in sorted(by) if k[0]>0 and k[2]!=k[3]);w=by[key];sign,op,f0,f1=key;left=w['left'];Gx=G_of[op]
    reject('recipe: wrong global phase',product_ok(*key,dict(left,phase=(left['phase']+1)%4)))
    reject('recipe: wrong translation',product_ok(*key,dict(left,offset=left['offset']^1)))
    reject('recipe: wrong linear phase',product_ok(*key,dict(left,linear_Z4=[(left['linear_Z4'][0]+2)%4]+left['linear_Z4'][1:])))
    reject('recipe: wrong quadratic form',product_ok(*key,dict(left,quadratic_rows=[left['quadratic_rows'][0]^2,left['quadratic_rows'][1]^1]+left['quadratic_rows'][2:])))
    reject('recipe: wrong matrix',product_ok(*key,dict(left,matrix_rows=[left['matrix_rows'][1],left['matrix_rows'][0]]+left['matrix_rows'][2:])))
    G2=list(Gx);G2[0]^=G2[1]
    reject('recipe: wrong G (still invertible)',product_ok(*key,left,G=G2))
    sing=list(Gx);sing[1]=sing[0]
    reject('recipe: non-invertible G',product_ok(*key,left,G=sing))
    reject('recipe: inverse warp recipe used for the forward warp',product_ok(sign,op,f0,f1,next(x for k,x in by.items() if k[0]==-sign and k[1]==op)['left']) if any(k[0]==-sign and k[1]==op for k in by) else False)
    # frame mismatch: the recipe of this class used for a class with another frame
    other=next((k for k in by if k!=key and k[0]==sign and k[1]!=op),None)
    reject('recipe: recipe of another warp class',product_ok(*key,by[other]['left']) if other else False)
    reject('recipe: swapped from/to frames',product_ok(sign,op,f1,f0,left))
    # a class missing from the recipe file
    try:
        miss=copy.copy(by);miss.pop(key);assert set(miss)==used
    except AssertionError:controls.append('recipe: missing warp class')
    else:raise AssertionError('missing class accepted')
    reject('logical: wrong G',logical_ok(op,res_all['warps'][str(op)]['K'],G=G2))
    reject('logical: wrong phase',logical_ok(op,dict(res_all['warps'][str(op)]['K'],phase=(res_all['warps'][str(op)]['K']['phase']+1)%4)))
out=dict(status='PASS_WARP_RECIPES_EXACT_ON_ALL_512_COLUMNS',canonical_word_sha256=hashlib.sha256((OUT/'CANONICAL-WORD.json.gz').read_bytes()).hexdigest(),
  recipe_sha256=hashlib.sha256((OUT/'CLIFFORD-RECIPES.json').read_bytes()).hexdigest(),warp_classes=len(by),operators=len(c.get('warps',[])),
  columns_each=1<<h,controls_rejected=controls)
(OUT/'WARP-RECIPE-CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(by),'classes',len(controls),'controls rejected',flush=True)

"""Incremental exact Clifford/phase audit of new candidate edges; old source audit pinned."""
import sys,os,json,gzip,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;PUB=Path(os.environ.get('COMPLEX_PUBLIC',str(Path(__file__).resolve().parent/'public')));BASE=PUB/'381/source/research/e8-nine-stage-kappa/complex377';FAR=PUB/'378/source/research/e8-complex-far-retiming/data/gcert1-e8-r783-far.json.gz';CP=Path(os.environ['COMPLEX_CERT']);OUT=Path(os.environ['COMPLEX_OUTPUT']);OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'work/odd-stages'));from clifford_exact import *
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();t0=time.monotonic();a=json.load(gzip.open(FAR));c=json.load(gzip.open(CP));assert c['frames']==a['frames'] and c['start']==a['start'] and c['final']==a['final'] and c['ret']==a['ret']
OLD_OUT=Path(os.environ.get('COMPLEX_BASELINE_OUTPUT',str(HERE/'complex-admission')))
old=OLD_OUT/'CLIFFORD-REVIEW.json';oldrec=json.loads(old.read_text());assert oldrec['status']=='PASS_EXACT_GAUSSIAN_CLIFFORD_LOCAL_FRAMES_AND_CHILDREN' and oldrec['frames']==len(a['frames']) and oldrec['all_child_equalities_include_global_phase']
bound=json.loads((OLD_OUT/'RESULT.json').read_text());assert bound['source_hashes'][str(FAR)]==sha(FAR) and bound['source_hashes'][str(BASE/'work/odd-stages/clifford_exact.py')]==sha(BASE/'work/odd-stages/clifford_exact.py')
def edges(z):
 cur=z['start'][:];out=set()
 for ph in ['A','B']:
  for g in z[ph]:
   for r in [g[2]]+[t for t,_,_ in g[3]]+(g[4] if g[0]=='out' else []):
    if cur[r]!=g[1]:out.add((cur[r],g[1]));cur[r]=g[1]
 for r,f in enumerate(z['final']):
  if cur[r]!=f:out.add((cur[r],f));cur[r]=f
 for k,r,f in z['ret']:out.add((f,0));out.add((0,f))
 assert cur==z['final'];return out
E0=edges(a);E=edges(c);assert len(E0)==oldrec['distinct_directed_edges'];recipes=[]
for f,g in sorted(E-E0):
 op=canonical_frame(9,c['frames'][f]).adjoint().then(canonical_frame(9,c['frames'][g]));rec,compiled=lower_child(op);assert rec['rank']==abs(len(c['frames'][g])-len(c['frames'][f]));recipes.append(dict(old=f,new=g,**rec))
result=dict(status='PASS_NEW_EDGES_EXACT_GAUSSIAN_PHASE_WITH_PINNED_OLD_EDGE_AUDIT',certificate_sha256=sha(CP),old_certificate_sha256=sha(FAR),original_phase_receipt_sha256=sha(old),new_edge_count=len(E-E0),removed_edge_count=len(E0-E),total_directed_edges=len(E),unchanged_frames=len(c['frames']),unchanged_endpoint_adapters=240,new_edge_recipes=recipes,old_recipes_sha256=sha(OLD_OUT/'CLIFFORD-RECIPES.json'),all_child_equalities_include_global_phase=True,seconds=time.monotonic()-t0)
(OUT/'CLIFFORD-DELTA.json').write_text(json.dumps(result,indent=2));print('PASS changed Clifford edges',result['new_edge_count'],'total',result['total_directed_edges'],flush=True)

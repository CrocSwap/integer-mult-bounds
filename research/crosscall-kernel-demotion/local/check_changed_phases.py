"""Changed-edge exact lowering only; unchanged public PR1148 phases inherited.
Uses upstream PR552 exact Clifford algebra, Apache-2.0 predecessor attribution.
No discovery executable, WSL, GPU or background service.
"""
import sys,json,gzip,hashlib,time,copy
from pathlib import Path
P=Path(__file__).parent
G=P/'vendor/clifford'
sys.path.insert(0,str(G))
from clifford_exact import canonical_frame,lower_child,diag,perm,xgate,Op,identity,fourier,rank,inverse,nullspace

def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def edges(c):return {(tuple(c['frames'][a]),tuple(c['frames'][b])) for a,b in c['edges']}
def wrappers(c):return {(tuple(c['frames'][c['start'][r]]),tuple(c['frames'][c['final'][r]])) for r in range(2*c['v'],len(c['start'])) if c['start'][r]!=0 or c['final'][r]!=1}
def monomial(r):return diag(9,tuple(r['quadratic_rows']),tuple(r['linear_Z4'])).then(perm(9,tuple(r['matrix_rows']))).then(xgate(9,r['offset'])).then(Op(9,identity(9),[('phase',r['phase'])]))
def equality(op,r):
 o=monomial(r['left']) if r['rank']==0 else monomial(r['right']).then(fourier(9,range(r['rank']))).then(monomial(r['left']))
 return o.tab==op.tab and o.zero_state()==op.zero_state()
def main():
 if not __debug__:raise RuntimeError("Assertion-based Clifford engine requires normal Python, not -O")
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--old',type=Path,required=True);ap.add_argument('--new',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists(),'fresh output required'
 t=time.monotonic();old,new=[read(x) for x in (a.old,a.new)];changed=sorted(edges(new)-edges(old));wr=sorted(wrappers(new)-wrappers(old));newframes=set(map(tuple,new['frames']))-set(map(tuple,old['frames']));operations={}
 for U in set(x for pair in changed+wr for x in pair):
  op=canonical_frame(9,U);pre=[x|(z<<9) for x,z,p in inverse(op.tab)[9:]];L=[u|(u<<9) for u in U]+[v<<9 for v in nullspace(U,9)];assert rank(L)==9 and rank(L+pre)==9;assert rank([x for x,z,p in op.tab[9:]])==len(U);operations[U]=op
 records=[];controls=[]
 for kind,pairs in [('edge',changed),('wrapper',wr)]:
  for U,V in pairs:
   op=operations[U].adjoint().then(operations[V]);rec,comp=lower_child(op);assert rec['rank']==abs(len(V)-len(U));assert equality(op,rec)
   mut=copy.deepcopy(rec);mut['left']['phase']=(mut['left']['phase']+1)%4;assert not equality(op,mut);controls.append(kind+':phase')
   if kind=='wrapper':
    wrapped=monomial(rec['right']).adjoint().then(op).then(monomial(rec['left']).adjoint());target=fourier(9,range(rec['rank']));assert wrapped.tab==target.tab and wrapped.zero_state()==target.zero_state()
   records.append(dict(kind=kind,before=U,after=V,recipe=rec))
 out=dict(status='PASS_CHANGED_EDGES_AND_WRAPPER_PHASE_EXACT',seconds=time.monotonic()-t,parent_canonical_sha256=hashlib.sha256(a.old.read_bytes()).hexdigest(),changed_canonical_sha256=hashlib.sha256(a.new.read_bytes()).hexdigest(),engine_sha256=hashlib.sha256((G/'clifford_exact.py').read_bytes()).hexdigest(),new_frames=sorted(newframes),changed_edges=len(changed),changed_wrappers=len(wr),controls=controls,records=records,scope='Fresh exact lowering and serialized independent monomial decode of every newly introduced edge and wrapper, including global phases. Identical unchanged public PR1148 edges/wrappers and endpoint adapters inherited, no full ancestor replay.')
 a.out.write_text(json.dumps(out,indent=2));print('PASS',len(changed),'changededges',len(wr),'wrappers',len(controls),'controls',out['seconds'],'seconds')
if __name__=='__main__':main()

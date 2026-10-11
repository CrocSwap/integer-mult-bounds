from pathlib import Path
from collections import defaultdict
import json,hashlib,importlib.util
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/complex-direct8-eleven451';ph=json.load(open(P/'hosted/DATA-PHASES.json'));sp=importlib.util.spec_from_file_location('phase89',O/'source_complex_chart.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);a.M=89
checked=routes=0
def poly(terms,translation=0):
 d=defaultdict(int)
 for axis,coef in terms:
  for k,v in a.phase([axis]).items():d[k]+=coef*v
 for k,v in a.phase([],translation).items():d[k]+=v
 return {k:v%4 for k,v in d.items()if v%4}
for rec in ph['recipes']:
 q=rec['q'];basis=[q]+rec['idle_children'][0]['orthogonal_axes'][:8]+[1<<i for i in range(9,89)];assert a.orthogonal(basis)
 def desired(level,side):
  if level<0:return [(q,1)]if side==0 else[]
  return [(1<<i,1)for i in range(9+8*level)]+([]if side==0 else[(q,-1)])
 for s,al in enumerate(rec['stage_alignment']):
  B=a.identity()
  if s:
   axes=basis[1:9];off=9+8*(s-1)
   for i in range(9):B[i]=(q if q>>i&1 else 0)^sum(((v>>i)&1)<<(off+j)for j,v in enumerate(axes))
   for j,v in enumerate(axes):B[off+j]=v
  assert a.orthogonal(B)and a.compose(B,B)==a.identity();routes+=1
  for name,local,level,side,entry in [('entry_X',[(q,1)],s-1,0,True),('entry_Y',[],s-1,1,True),('exit_X',[(1<<i,1)for i in range(9)],s,0,False),('exit_Y',[(1<<i,1)for i in range(9)]+[(q,-1)],s,1,False)]:
   actual=[(a.image(B,v),c)for v,c in local+[(1<<i,1)for i in range(9,9+8*s)]];canon=desired(level,side);left,right=(canon,actual)if entry else(actual,canon);assert poly(left,al[name])==poly(right);checked+=1
 expected=[x for j in range(1,5)for side in range(2)for x in [(-1,2*j-1,side),(2*j-1,2*j,side)]]+[(2*j+2,10,side)for j in range(5)for side in range(2)]
 assert len(expected)==len(rec['idle_children'])
 for ch,(old,new,side)in zip(rec['idle_children'],expected):
  assert len(ch['orthogonal_axes'])==8*(new-old);delta=[(v,-c)for v,c in desired(old,side)]+desired(new,side);assert poly([(v,1)for v in ch['orthogonal_axes']],ch['translation_after'])==poly(delta);checked+=1
 assert poly([(q,-1)]+desired(10,1),rec['terminal_Y_translation'])==poly([(1<<i,1)for i in range(89)]);checked+=1
assert(routes,checked)==(1320,8520)
out={'status':'PASS_INDEPENDENT_COMPLEX451_STAGE_IDLE_TERMINAL_FULL_CHARACTER_PHASES','orthogonal_routes':routes,'exact_phase_equalities':checked,'method':'IndependentZ4 quadraticcharacterpolynomials; explicit89column q-projector/orthogonal-complement exteriorroutes; allphase translations. Uniformcharacter value1 fixesglobalphase.','source_sha256':hashlib.sha256((P/'hosted/DATA-PHASES.json').read_bytes()).hexdigest(),'scope':'Finiteactualphase/interface proof; generalizedphysicalClifford/commonprime/compiler hypotheses retained.'};(O/'COMPLEX451-DATA-PHASES.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])

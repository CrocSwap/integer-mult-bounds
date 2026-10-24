"""Dyadic involutive code and phase-correct common-query caller binding."""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,gzip
sys.path.insert(0,str(Path(__file__).resolve().parent))
import clifford_exact as ce, native_core as V, gauge
from backward import conjugate
P=Path(__file__).resolve().parent

def equal(a,b):return a.tab==b.tab and a.zero_state()==b.zero_state()
def word(circ):
 a=ce.ident(9)
 for e in circ:
  t=e[0]
  if t=='P':b=ce.perm(9,e[1])
  elif t=='D':b=ce.diag(9,e[1],e[2])
  elif t=='X':b=ce.xgate(9,e[1])
  elif t=='phase':b=ce.Op(9,ce.identity(9),[('phase',e[1])])
  else:raise ValueError('Nonmonomial wrapper')
  a=a.then(b)
 return a

def main():
 a=json.loads(gzip.decompress((P/'INVOLUTIVE-WORD.json.gz').read_bytes()));c=a['canonical'];F=[[Q(x)for x in r]for r in a['F']]
 R=[[Q(x)for x in r]for r in json.loads((P/'R.json').read_bytes())];S=set(a['selected_ports'])
 U=[[(1-12*(i in S))*R[k][i]/4 for k in range(8)]for i in range(112)]
 V.need(all(sum(R[k][i]*U[i][l]for i in range(112))==2*(k==l)for k in range(8)for l in range(8)),'RU=2I')
 V.need(all(F[i][j]==(i==j)-sum(U[i][k]*R[k][j]for k in range(8))for i in range(112)for j in range(112)),'Actual inherited F factor')
 V.need(any(F[i][j]!=F[j][i]for i in range(112)for j in range(112)),'Transpose is essential')
 for transpose in (False,True):
  for j in range(112):
   x=[Q(i==j)for i in range(112)]
   for iteration in range(2):
    t=[sum((U[i][k]if transpose else R[k][i])*x[i]for i in range(112))for k in range(8)]
    x=[v-sum((R[k][i]if transpose else U[i][k])*t[k]for k in range(8))for i,v in enumerate(x)]
    want=[(F[j][i]if transpose else F[i][j])if iteration==0 else Q(i==j)for i in range(112)]
    V.need(x==want,'Literal eight-mode forward/transpose inverse recoding')
 V.need(all(v.denominator&(v.denominator-1)==0 for row in U for v in row),'Dyadic coefficients only')
 rows,paid,mx=V.replay(c,a['program'])
 for i in range(632):
  expected=V.identity(i)
  if 112<=i<224:
   for j,v in enumerate(F[i-112]):
    if v:V.add(expected,V.identity(j),v)
  V.need(rows[i]==expected,'Fresh forward all-input replay')
 N=json.loads((P/'NORMALIZERS.json').read_bytes());D=ce.fourier(9,range(1,9));q=ce.cgate(9,1);full=ce.fourier(9)
 for r in N['ports']:
  i=r['port'];K=word(r['K_word']);wr={n:word(v['word'])for n,v in r['compiled_wrappers'].items()}
  V.need(equal(K.then(full),full.then(K)),'Real K commutes full Gaussian')
  V.need(all(e[0]!='D'or all(x%2==0 for x in e[2])for e in K.circuit),'Real K')
  E=ce.canonical_frame(9,c['frames'][c['start'][i]]);T=ce.canonical_frame(9,c['frames'][c['final'][112+i]])
  V.need(equal(wr['input_X'].then(E.adjoint()),q.adjoint().then(K)),'Forward arbitrary coded columns')
  V.need(equal(T.then(wr['output_Y']),K.adjoint().then(D)),'Forward arbitrary coded rows')
  V.need(equal(wr['input_X'].then(E.adjoint()).then(full).then(wr['output_X']),D),'Forward X diagonal')
  V.need(equal(wr['input_Y'].then(T).then(wr['output_Y']),D),'Forward Y diagonal')
  V.need(equal(wr['backward_input_Y'],K),'Backward arbitrary coded columns')
  V.need(equal(conjugate(full).then(wr['backward_output_X']),K.adjoint().then(q).then(D)),'Backward transposed coded rows')
  V.need(equal(wr['backward_input_X'].then(conjugate(E).adjoint()).then(conjugate(full)).then(wr['backward_output_X']),D),'Backward X diagonal')
  V.need(equal(K.then(conjugate(T)).then(wr['backward_output_Y']),D),'Backward Y diagonal')
 core=gauge.noncommutative_core(P/'CONTROLLER.json');gauge.local_checks();gauge.idle_checks()
 recipe=gauge.typed_caller_recipe(P/'CONTROLLER.json')
 for e in recipe['emission']:
  if e['op']=='CODE':e['execution_order']=[[s,'transpose'if sign<0 else'forward']for s,sign in e['execution_order']]
  elif e['op']=='CENTER_FREE_FULL':e['op']='INVOLUTIVE_FULL'
 for e in recipe['endpoint']:
  e['code_word_left_to_right']=[[s,'transpose'if sign<0 else'forward']for s,sign in e['code_word_left_to_right']]
 # All inverse code instructions execute the same involutive stage code.
 for e in recipe['positive_half_postdecode']:
  e['execution_order']=[[s,'transpose'if sign>0 else'forward']for s,sign in e['execution_order']]
 recipe['recursive_delta_vs_retained_caller']={'rank_8':-144,'rank_1':144}
 recipe.pop('denominator_13_realization');recipe['fixed_scalar_coefficients']='Dyadic; F inverse = F and transpose inverse = transpose. Rounding and outer implementation still require admission.'
 recipe['forward_code_evaluations']=recipe.pop('A_evaluations');recipe['transpose_code_evaluations']=recipe.pop('A_inverse_evaluations')
 recipe['shared_owned_code_temporaries']=8
 recipe.pop('dense_code_add_bound_each');recipe.pop('dense_code_add_bound_total')
 result={'status':'PASS_DYADIC_TYPED_CALLER','normalizer_ports':112,'basis_recodings':224,'core_entries':core['matrix_entries_checked'],'recipe':recipe,'new_kappa':None,'gaussian_supplier':False}
 if '--emit'in sys.argv:(P/'CALLER.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
 else:V.need(json.loads((P/'CALLER.json').read_bytes())==json.loads(json.dumps(result)),'Frozen dyadic caller recipe')
 print(json.dumps({k:v for k,v in result.items()if k!='recipe'},sort_keys=True))
if __name__=='__main__':main()

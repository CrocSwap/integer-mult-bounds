"""Read/derive transfer of the standalone one-bank ceiling, no search.
Apache-2.0; substantial OpenAI Codex assistance. Rank proof credited to parent.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import json,gzip,types,sys
HERE=Path(__file__).resolve().parent
def need(v,m):
 if not v:raise ValueError(m)
def main():
 f=json.loads(gzip.decompress((HERE/'inputs/INVOLUTIVE-WORD.json.gz').read_bytes()))
 F=[[Q(x) for x in row] for row in f['F']];S=f['selected_ports'];N=112
 need(S==[0,7,20,23,86,93,108,111],'Selected source coordinates')
 need(all(F[i][i]==(12 if i in S else 0) for i in range(N)),'ActualF diagonal12D_J')
 need(all(F[i][j]==(12 if i==j else 0) for i in S for j in S),'ActualF_JJ=12I')
 # Integer witness for G^-1=(143F-12F D_J F)/143, no determinant oracle.
 B=[[int(2*x) for x in row] for row in F]
 need(all(Q(B[i][j],2)==F[i][j] for i in range(N) for j in range(N)),'Half-integer matrix')
 C=[[B[i][j]-24*int(i==j and i in S) for j in range(N)] for i in range(N)]
 Z=[[143*B[i][j]-6*sum(B[i][k]*B[k][j] for k in S) for j in range(N)] for i in range(N)]
 def product(X,Y):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*Y)] for row in X]
 need(product(C,Z)==product(Z,C)==[[572*int(i==j) for j in range(N)] for i in range(N)],'Exact two-sided inverse witness offdiagonalG')
 # Directly recheck every supported offdiagonal transport of actual F.
 ce=types.ModuleType('independent_ceiling_ce');sys.modules[ce.__name__]=ce
 source=(HERE/'inputs/clifford_exact.py').read_bytes()
 need(sha256(source).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','Exact Clifford source')
 exec(compile(source,'pinned_ce','exec'),ce.__dict__)
 c=f['canonical'];U=[ce.canonical_frame(9,c['frames'][c['start'][i]]) for i in range(N)]
 def grade(op):
  pivots={}
  for x,z,p in op.tab[9:]:
   while x:
    bit=x.bit_length()-1
    if bit not in pivots:pivots[bit]=x;break
    x^=pivots[bit]
  return len(pivots)
 grades=Counter(grade(U[j].adjoint().then(U[i])) for i in range(N) for j in range(N) if i!=j and F[i][j])
 need(grades==Counter({2:5824}),'AllactualsupportedFoffdiagonalgrades')
 engine=(HERE/'inputs/intervals.py').read_bytes()
 need(sha256(engine).hexdigest()=='0ce7e7137422d5ffeda22085c81fa88471bbe963100fdad62e659f1e3bf89326','Exact intervalengine source')
 scope={'__name__':'independent_ceiling_intervals','__file__':str(HERE/'inputs/intervals.py')};exec(compile(engine,'intervals','exec'),scope)
 H=Counter({4:28,7:7,8:47,9:326});T=Counter({r:2*v for r,v in H.items()});T[17]=224
 P=Counter({1:4418,2:824,3:1020,4:254,5:80});models={}
 def outward(v):
  z=10**30;lo=(v[0]*z).__floor__();hi=-((-v[1]*z).__floor__())
  def fmt(n):s=str(abs(n)).rjust(31,'0');return ('-' if n<0 else '')+s[:-30]+'.'+s[-30:]
  return [fmt(lo),fmt(hi)]
 for name,extra in [('unrealized224H17',{}),('after112H2',{2:112})]:
  paid=P+Counter(extra);coeff={r:T.get(r,0)-paid.get(r,0) for r in T.keys()|paid.keys() if T.get(r,0)!=paid.get(r,0)}
  need(all((n<0 and r<=5) or (n>0 and r>=7) for r,n in coeff.items()),'Signseparation normalizedmoment at5')
  values={}
  for cs in ('.0030217758','.0034'):
   a=scope['moment'](dict(T),1-Q(cs));b=scope['moment'](dict(paid),1-Q(cs));v=(a[0]-b[1],a[1]-b[0]);need(v[0]>0 if not extra else v[1]<0,'Price sign')
   values[cs]=outward(v)
  models[name]={'target':dict(T),'paid':dict(paid),'intervals':values,'endpoint_constructed':False}
 result={'status':'PASS_SCOPED_ONE_BANK_TRANSFER','F_diagonal':'12D_J','F_JJ':'12I8','G':'F-12D_J','determinant_lemma_factor':'(-143)^8','inverse_witness':'G(143F-12F D_J F)=(143F-12F D_J F)G=143I','supported_offdiagonal_grade2':5824,'regular_module_rank':'112dimA_f','minimum_parallel_grade2_channels':112,'interval_proof':'M(t)/5^t increasing; negativeatfundedlowerC coversfullCinterval','models':models,'scope':'FixedfinitecolumnwiseCliffordalphabet. ONEstandaloneparallelbank plusrectangular monomialCliffordcontrols/zero scratch/freebypass. No multibank/nativeabsorption/prefix/directcodedconsumer/approximation or noncolumnwisegeneralization.','new_kappa':None}
 print(json.dumps(result,indent=2))
 if '--emit' in __import__('sys').argv:(HERE/'CEILING.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()

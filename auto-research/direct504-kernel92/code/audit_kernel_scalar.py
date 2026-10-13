"""Independent exact scalar witness for a selected complex kernel word.
Uses immutable correct-word compensation for omission controls; no repaired
compensation is silently supplied to a mutant. No physical-hosting claim.
"""
import sys,json,gzip,hashlib,copy
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
p=Path(__file__).resolve().parent
path=Path(sys.argv[1]);selection=Path(sys.argv[2]);out=Path(sys.argv[3]);w=json.loads(gzip.decompress(path.read_bytes()));sel=json.loads(selection.read_text());V=len(w['ports']);n=2*V+w['report']['R']
def ident():return[{r:Q(1)}for r in range(n)]
def apply(e,rows):
 if e[0]=='scale':
  _,t,a,b,*_=e;q=Q(a,b);rows[t]={j:q*x for j,x in rows[t].items()};return
 _,t,s,a,b,*_=e;q=Q(a,b)
 for j,x in list(rows[s].items()):
  z=rows[t].get(j,Q(0))+q*x
  if z:rows[t][j]=z
  else:rows[t].pop(j,None)
def inv(e,dual=False):
 e=copy.deepcopy(e)
 if e[0]=='add':
  e[3]*=-1
  if dual:e[1],e[2]=e[2],e[1]
 else:e[2],e[3]=e[3],e[2]
 return e
def replay(es):
 rows=ident()
 for e in es:apply(e,rows)
 return rows
main=w['A']+w['cut']+w['B'];mx=replay(main);dirty=[{}for _ in range(n)]
for r in range(V,2*V):dirty[r]={j:x for j,x in mx[r].items()if j>=2*V}
for e in w['precondition']:apply(e,dirty)
comp=[]
for r in range(V,2*V):
 for j,x in sorted(dirty[r].items()):
  assert not w.get('start_extra',{}).get(str(j)),('nonzero-frame compensation',j)
  comp.append(['add',r,j,-x.numerator,x.denominator,[]])
cleanup=[inv(e)for e in reversed(w['A']+w['B'])if not V<=e[1]<2*V]
assert[e[:-1]for e in cleanup]==[e[:-1]for e in w['cleanup']]
program=w['precondition']+comp+main+cleanup;expected=ident()
for t in range(V):expected[V+t][t]=Q(1)
assert replay(program)==expected
back=ident()
for t in range(V):back[t][V+t]=Q(-1)
assert replay([inv(e,True)for e in program])==back
controls={}
for cl in sel['kernel']:
 for h in cl['pivots']:
  aa=[e for e in w['A']if not(e[0]=='add'and e[2]==2*V+h and e[1]>=2*V and e[-1]==cl['E'])]
  assert len(aa)<len(w['A']);cc=[inv(e)for e in reversed(aa+w['B'])if not V<=e[1]<2*V]
  assert replay(w['precondition']+comp+aa+w['cut']+w['B']+cc)!=expected
  controls[str(h)]='REJECTED_OMITTED_KERNEL_CORRECTION'
r=dict(status='PASS_EXACT_RATIONAL_FORWARD_AND_INVERSE_TRANSPOSE',word_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),selection_sha256=hashlib.sha256(selection.read_bytes()).hexdigest(),columns_each_orientation=n,compensations=len(comp),program_operations=len(program),kernel_pivots=len(controls),controls=controls,scope='Exact local scalar identity and preserved frame-zero compensation; physical owner routing, complete invoice and outer kappa separate.')
out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],n,len(controls))

"""Exact new-kernel omission controls with the correct compensation frozen."""
import argparse,copy,gzip,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
if not __debug__:raise SystemExit('Assertions required.')
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w=json.loads(gzip.decompress(a.word.read_bytes()));recipe=json.loads(a.recipe.read_text());V=112;N=728
def inverse(e,dual=False):
 e=copy.deepcopy(e)
 if e[0]=='add':
  e[3]*=-1
  if dual:e[1],e[2]=e[2],e[1]
 else:e[2],e[3]=e[3],e[2]
 return e
def ident():return[{r:Q(1)}for r in range(N)]
def apply(e,rows):
 if e[0]=='scale':
  t=e[1];q=Q(e[2],e[3]);rows[t]={j:q*x for j,x in rows[t].items()};return
 t,s=e[1:3];q=Q(e[3],e[4])
 for j,x in list(rows[s].items()):
  z=rows[t].get(j,Q(0))+q*x
  if z:rows[t][j]=z
  else:rows[t].pop(j,None)
def replay(es):
 rows=ident()
 for e in es:apply(e,rows)
 return rows
main=w['A']+w['cut']+w['B'];mx=replay(main);dirty=[{}for _ in range(N)]
for r in range(V,2*V):dirty[r]={j:x for j,x in mx[r].items()if j>=2*V}
for e in w['precondition']:apply(e,dirty)
comp=[]
for r in range(V,2*V):
 for j,x in sorted(dirty[r].items()):assert not w['start_extra'].get(str(j));comp.append(['add',r,j,-x.numerator,x.denominator,[]])
expected=ident();expected_back=ident()
for t in range(V):expected[V+t][t]=Q(1);expected_back[t][V+t]=Q(-1)
correct=w['precondition']+comp+main+w['cleanup'];assert replay(correct)==expected and replay([inverse(e,True)for e in correct])==expected_back
indices=list(range(recipe['index'],recipe['index']+len(recipe['coefficients'])));controls=[]
for omitted in [[i]for i in indices]+[indices]:
 B=[e for i,e in enumerate(w['B'])if i not in omitted];cleanup=[inverse(e)for e in reversed(w['A']+B)if not V<=e[1]<2*V];program=w['precondition']+comp+w['A']+w['cut']+B+cleanup
 assert replay(program)!=expected and replay([inverse(e,True)for e in program])!=expected_back
 controls.append(dict(omitted_B_indices=omitted,forward_rejected=True,reflected_rejected=True))
r=dict(status='PASS_EXACT_NEW_KERNEL_OMISSION_CONTROLS',word_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest(),columns_each_orientation=N,correct_compensation_frozen=True,compensation_entries=len(comp),controls=controls,scope='Each new donor gate and entire new kernel omitted. Cleanup is regenerated, correct compensation is held fixed, and both exact scalar orientations reject each mutant.');a.out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(controls))

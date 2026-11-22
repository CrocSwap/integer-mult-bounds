"""Exact terminal-history feasibility for recoding the existing 509->0 return.

The frozen one-residual word is unchanged except that, immediately before
its existing paid MOVE 3150 from 509 to 0, a source-local linear combination
of the then-live chart-509 registers is XORed into that moving field.  Every
chart is granted free retention of all its actual earlier incoming fields.
All 630 native output masks must be decodable at their original charts.
"""
import collections,gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gf2 import Echelon,bits

path=Path(str(Path(__file__).resolve().parent/'pinned'/'ONE-RESIDUAL.json.gz'))
G=json.load(gzip.open(path,'rt')); n=G['public']; mark=1<<n; low=mark-1
want=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
ch=dict(enumerate(G['start']));v={i:1<<i for i in ch};seen=collections.defaultdict(list)
for i,c in ch.items():seen[c].append(v[i])
site=None; source=None
for k,row in enumerate(G['program']):
 op,d,*a=row
 if row==['MOVE',3150,509,0]:
  assert site is None;site=k;source=[(i,v[i]&low) for i,c in ch.items() if c==509]+[(f'history-{j}',r&low) for j,r in enumerate(seen[509])];v[d]^=mark
 if row==['MOVE',3317,0,91]:
  zero_before=[(i,v[i]) for i,c in ch.items() if c==0];zero_history=list(seen[0])
 if op=='INIT':assert d not in ch;ch[d],v[d]=a[0],0
 elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[d]^=v[s]
 elif op=='MOVE':assert ch[d]==a[0];ch[d]=a[1];seen[a[1]].append(v[d])
 elif op=='SWAP':
  s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
  seen[ch[d]].append(v[d]);seen[ch[s]].append(v[s])
 elif op=='CLEAR':assert ch.pop(d)==a[0];v.pop(d)
 else:raise ValueError(row)
assert site is not None and ch==dict(enumerate(G['final']))
print('site',site,'source_live',len(source),'source_ids',[i for i,_ in source]);print('original_missing',[i for i in range(n) if (v[i]&low)!=want[i]])

# Echelon equations over the source-local combination bits. Keep a small
# provenance set to identify a concrete contradictory subset if one occurs.
m=len(source);basis={};conflicts=[];tested=0; constrained=[];original={};spaces={}
def add_equation(lhs,rhs,why):
 global tested
 tested+=1; row=lhs|(rhs<<m);proof={why};original[why]=(lhs,rhs)
 while row & ((1<<m)-1):
  p=(row&-row).bit_length()-1
  if p not in basis:basis[p]=(row,proof);return
  other,orig=basis[p];row^=other;proof=proof.symmetric_difference(orig)
 if row>>m:conflicts.append(proof)

for chart,rows in sorted(seen.items()):
 outputs=[i for i,c in enumerate(G['final']) if c==chart and i!=130]
 if not outputs:continue
 marked=[r&low for r in rows if r&mark]
 plain=[r&low for r in rows if not r&mark]
 if not marked:
  E=Echelon(plain)
  for i in outputs:
   if E.residue(want[i]):conflicts.append({(chart,i,'unaffected_impossible')})
  continue
 pivot=marked[0];even=plain+[x^pivot for x in marked[1:]];E=Echelon(even)
 if chart==525:spaces['chart525']=(E,pivot)
 required=[i for i in outputs if E.residue(want[i])]
 if not required:continue
 sr=[E.residue(x) for _,x in source]
 constrained.append((chart,tuple(required),len(rows),len(E.rows)))
 for i in required:
  rhs=E.residue(want[i]^pivot)
  coords=rhs
  for val in sr:coords|=val
  for bit in bits(coords):
   lhs=sum(((val>>bit)&1)<<j for j,val in enumerate(sr));b=(rhs>>bit)&1
   add_equation(lhs,b,(chart,i,bit))

# At the second existing ingress, all chart-0 fields except the already
# changed return 3150 are marker-free. They must combine with 3150 to
# reconstruct the missing x38 correction, using only actual live fields.
changed=[x for i,x in zero_before if x&mark]
assert len(changed)==1
E=Echelon([x&low for _,x in zero_before if not x&mark]+[x&low for x in zero_history if not x&mark])
assert E.residue(1<<38), 'x38 is already present without the recoded return'
spaces['chart0']=(E,changed[0]&low)
rhs=E.residue((1<<38)^(changed[0]&low));sr=[E.residue(x) for _,x in source]
coords=rhs
for val in sr:coords|=val
for bit in bits(coords):
 lhs=sum(((val>>bit)&1)<<j for j,val in enumerate(sr));b=(rhs>>bit)&1
 add_equation(lhs,b,('chart0_x38',bit))

print('constrained_charts',len(constrained),'details',constrained)
print('equations',tested,'variable_rank',len(basis),'conflicts',len(conflicts))
if conflicts:
 witness=min(conflicts,key=len);print('FIRST_MIN_CONFLICT',sorted(witness,key=str))
 for label in sorted(witness,key=str):
  if label in original:
   lhs,rhs=original[label];print('  CONFLICT_EQUATION',label,[source[j][0] for j in range(m) if lhs>>j&1],'=',rhs)
 for name,(ES,pivot) in spaces.items():
  z=1
  for p,row in sorted(ES.rows.items()):
   if (z&row).bit_count()&1:z|=1<<p
  assert all(not ((z&r).bit_count()&1) for r in ES.rows.values())
  print('  DUAL',name,'support',list(bits(z)),'source_flip_ids',[i for i,x in source if (x&z).bit_count()&1],
        'target130_x38_flip',bool(z&(1<<38)), 'target111_flip',bool((want[111]&z).bit_count()&1),
        'pivot_flip',bool((pivot&z).bit_count()&1))
else:
 sol=0
 for p,(row,_) in sorted(basis.items(),reverse=True):
  rhs=(row>>m)&1;higher=row&((1<<m)-1)&~(1<<p)
  if rhs^((higher&sol).bit_count()&1):sol|=1<<p
 ids=[source[j][0] for j in range(m) if sol>>j&1]
 q=0
 for j,(_,mask) in enumerate(source):
  if sol>>j&1:q^=mask
 print('SAT_SOURCE_IDS',ids,'SOURCE_FORM_SUPPORT',list(bits(q)))

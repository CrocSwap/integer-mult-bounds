"""Necessary exact test for one source-local recoding of one existing MOVE.

The input is the frozen 629/630 word and a field ID of a MOVE. The sender
may inject any linear combination of all live source-chart fields. Every
terminal chart gets all fields ever received there as a free observation;
no terminal decoder is fixed. The rest of the physical tape is unchanged.
"""
import collections,gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gf2 import Echelon,bits
field=int(sys.argv[1]);historical='--historical' in sys.argv[2:];G=json.load(gzip.open(str(Path(__file__).resolve().parent/'pinned'/'ONE-RESIDUAL.json.gz'),'rt'));n=G['public'];mark=1<<n;low=mark-1
want=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
ch=dict(enumerate(G['start']));v={i:1<<i for i in ch};seen=collections.defaultdict(list)
for i,c in ch.items():seen[c].append(v[i])
source=site=None
for k,(op,d,*a) in enumerate(G['program']):
 if op=='MOVE' and d==field:
  assert site is None;site=(k,d,*a);source=[(i,v[i]&low) for i,c in ch.items() if c==a[0]];v[d]^=mark
  if historical:source += [(f'history-{j}',r&low) for j,r in enumerate(seen[a[0]])]
 if op=='INIT':ch[d],v[d]=a[0],0
 elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[d]^=v[s]
 elif op=='MOVE':assert ch[d]==a[0];ch[d]=a[1];seen[a[1]].append(v[d])
 elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d];seen[ch[d]].append(v[d]);seen[ch[s]].append(v[s])
 elif op=='CLEAR':assert ch.pop(d)==a[0];v.pop(d)
 else:raise ValueError(op)
assert site and ch==dict(enumerate(G['final']))
m=len(source);basis={};bad=[];equations=0;origin={}
def add(lhs,rhs,why):
 global equations
 equations+=1;row=lhs|(rhs<<m);proof={why};origin[why]=(lhs,rhs)
 while row & ((1<<m)-1):
  pivot=(row&-row).bit_length()-1
  if pivot not in basis:basis[pivot]=(row,proof);return
  other,old=basis[pivot];row^=other;proof^=old
 if row>>m:bad.append(proof)
for chart,rows in sorted(seen.items()):
 outputs=[i for i,c in enumerate(G['final']) if c==chart]
 if not outputs:continue
 marked=[r&low for r in rows if r&mark];plain=[r&low for r in rows if not r&mark]
 if not marked:
  E=Echelon(plain)
  for i in outputs:
   if E.residue(want[i]):bad.append({(chart,i,'unaffected')})
  continue
 pivot=marked[0];E=Echelon(plain+[x^pivot for x in marked[1:]])
 needs=[i for i in outputs if E.residue(want[i])]
 if not needs:continue
 sr=[E.residue(x) for _,x in source]
 for i in needs:
  rhs=E.residue(want[i]^pivot);coords=rhs
  for x in sr:coords|=x
  for bit in bits(coords):
   lhs=sum(((val>>bit)&1)<<j for j,val in enumerate(sr));add(lhs,(rhs>>bit)&1,(chart,i,bit))
print('SITE',site,'SOURCE_LIVE',len(source),'EQUATIONS',equations,'RANK',len(basis),'CONFLICTS',len(bad))
if bad:
 witness=min(bad,key=len);print('CORE',sorted(witness,key=str))
 for why in sorted(witness,key=str):
  if why in origin:
   lhs,rhs=origin[why];print('EQUATION',why,[source[j][0] for j in range(m) if lhs>>j&1],'=',rhs)
else:
 solution=0
 for p,(row,_) in sorted(basis.items(),reverse=True):
  rhs=(row>>m)&1;higher=row&((1<<m)-1)&~(1<<p)
  if rhs^((higher&solution).bit_count()&1):solution|=1<<p
 print('SAT_SOURCE_IDS',[source[j][0] for j in range(m) if solution>>j&1])

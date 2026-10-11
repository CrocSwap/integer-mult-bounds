"""Independent sparse full integer replay and exact rational frame checks."""
from pathlib import Path
from collections import Counter
import json,struct,hashlib
O=Path(__file__).resolve().parent;P=O/'source-closure/candidate'
files=[P/'records/249-records.bin',P/'baseline.json',P/'signed-records.bin',P/'records/frames.json',P/'records/249-states.json',P/'SELECTION.json',P/'word.json.gz'];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
ev=list(struct.iter_unpack('<6i',(P/'signed-records.bin').read_bytes()));F=json.loads((P/'records/frames.json').read_text())['frames'];st=json.loads((P/'records/249-states.json').read_text());n=st['n'];assert n==980

base=json.loads((P/'baseline.json').read_text());rawrows=[{i:1}for i in range(n)]
def upd(a,b,c=1):
 for k,v in list(b.items()):
  x=a.get(k,0)+c*v
  if x:a[k]=x
  else:a.pop(k,None)
for f,a,ss in base['A']:
 for b in ss:upd(rawrows[a],rawrows[b])
ret=[dict(rawrows[a])for a in base['ret']]
for t,ks in enumerate(base['scatter']):
 for k in ks:upd(rawrows[120+t],ret[k])
for f,a,ss in base['B']:
 for b in ss:upd(rawrows[a],rawrows[b])
M=[{k:c for k,c in rawrows[120+t].items() if k<120}for t in range(120)]
def run(reverse=False):
 rows=[{i:1}for i in range(n)]+[{}];borrow=None;copies=0;state={int(i):f for i,f in st['final' if reverse else 'initial'].items()};H=Counter();maxactual=1
 for op,a,b,c,f,z in reversed(ev)if reverse else ev:
  if op==0:
   old,new=(c,b)if reverse else(b,c);assert state[a]==old
   x,y=F[str(old)],F[str(new)];assert all(sum(i*j for i,j in zip(u,v))==0 for u in(x['A']if reverse else x['B'])for v in(y['B']if reverse else y['A']))
   r=x['dim']-y['dim']if reverse else y['dim']-x['dim'];assert r==f and r>=0
   if r:H[r]+=1
   state[a]=new
  elif op==1:
   assert a!=b and a<n and state[a]==state[b]==f and a!=borrow
   coeff=-c if reverse else c
   for k,v in list(rows[b].items()):
    val=rows[a].get(k,0)+coeff*v
    if val:rows[a][k]=val
    else:rows[a].pop(k,None)
   maxactual=max(maxactual,sum(map(abs,rows[a].values())))
  elif op==(3 if reverse else 2):
   assert borrow is None and b==n and n not in state and state[a]==c and f==st['ZERO']and F[str(c)]['dim']==8
   rows[n]=dict(rows[a]);state[n]=f;borrow=a;H[8]+=1
  else:
   assert op==(2 if reverse else 3)and borrow==a and b==n and rows[n]==rows[a] and state[n]==f
   borrow=None;rows[n]={};del state[n];copies+=1
 assert state=={int(i):f for i,f in st['initial' if reverse else 'final'].items()} and copies==9 and borrow is None
 want=[{i:1}for i in range(n)]+[{}]
 for i in range(120):upd(want[120+i],M[i],-1 if reverse else 1)
 assert rows==want
 return {'copies':copies,'all_signed_columns':n,'profile':dict(sorted(H.items())),'rank_mass':sum(r*k for r,k in H.items()),'max_actual_integer_row_l1':maxactual}
native=list(struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()));assert [(op,a,b,c%2 if op==1 else c,f,z)for op,a,b,c,f,z in ev if op!=1 or c%2]==native
a=run();b=run(True);assert a['profile']==b['profile'];assert all(hashlib.sha256(p.read_bytes()).hexdigest()==pins[str(p)]for p in files)
r={'status':'PASS_INDEPENDENT_ACTUAL_CASCADE_980_SIGNED_DIRT_INVERSE_PHYSICAL_LEDGER','source_pins':pins,'forward':a,'reflected_inverse':b,'changed_helpers_or_private_work':0,'literal_native_parity_exact':True,'source_response':'All120 actual integer sourcefunctional rowsM independently rebuiltfromungaugedbaselineA/scatter/B; fullsignedwordforward y+=M x,inverse y−=M x, not assumedscalarI.','scope':'Actualfullsignedsourceword/arbitrarycorrelateddirt andliteralinverse, everyforward/reflected rationalMOVE containment, equalADDlabels,9borrowedsourcecopies/eraseequality. Prefixreportedhereactualsparse rownorm; cancellationfreeprefix/fullcompiler/paidinvoice andnewglobalassignment remainseparategates. Nooptimizedsuppliergainclaimed.'}
(O/'FULL-WORD-AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],a,b)

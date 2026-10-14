"""Independent free-group chart replay. No producer or predecessor imports.
Each frame chart is a freely noncommuting invertible symbol. This checks
algebra conditional on realizing those charts, not a Clifford compiler.
"""
from pathlib import Path
from fractions import Fraction as Q
import json
HERE=Path(__file__).resolve().parent

def require(c,msg):
 if not c:raise ValueError(msg)
def span(rows):
 s={0}
 for x in rows:s|={y^x for y in tuple(s)}
 return tuple(sorted(s))
def reduce_word(w):
 a=[]
 for x in w:
  if a and a[-1]==-x:a.pop()
  else:a.append(x)
 return tuple(a)
def check(w,phase_fault=False):
 ids={}
 def chart(f):
  key=span(f)
  if len(key)==1:return ()
  if key not in ids:ids[key]=len(ids)+1
  return (ids[key],)
 def inverse(word):return tuple(-x for x in reversed(word))
 names=list(w['initial_frames']);rows={r:{(r,()):Q(1)} for r in names};frames={r:span(f) for r,f in w['initial_frames'].items()};first=True
 for e in w['program']:
  op=e[0]
  if op=='transport':
   _,r,a,b,rank=e;sa,sb=span(a),span(b)
   require(frames[r]==sa,'wrong entry chart');require(set(sa)<=set(sb) or set(sb)<=set(sa),'not nested');require(abs((len(sa).bit_length()-1)-(len(sb).bit_length()-1))==rank,'wrong child rank')
   prefix=chart(b)+inverse(chart(a));factor=-1 if phase_fault and first else 1;first=False
   rows[r]={(j,reduce_word(prefix+word)):factor*x for (j,word),x in rows[r].items()};frames[r]=sb
  elif op=='zero':
   _,r,f=e;require(r not in frames,'private allocation collision');rows[r]={};frames[r]=span(f)
  elif op=='erase':
   _,r,f=e;require(frames[r]==span(f),'erase chart');del rows[r];del frames[r]
  elif op=='copy':
   _,r,s,f=e;require(frames[r]==frames[s]==span(f),'copy charts');require(not rows[r],'copy into live row');rows[r]=dict(rows[s])
  elif op=='add':
   _,r,s,a,f=e;require(frames[r]==frames[s]==span(f),'addition charts')
   for key,x in rows[s].items():
    val=rows[r].get(key,Q(0))+Q(a)*x
    if val:rows[r][key]=val
    else:rows[r].pop(key,None)
  else:raise ValueError('unknown operation')
 # Reconstruct D from raw doubled-coordinate roots and the frozen fixture,
 # without importing its geometric/producer verifier.
 ref=HERE/'source/research/biframe-decoder-ladder/RESULTS.json'
 if not ref.exists():ref=HERE.parent/'kernel106/source/research/biframe-decoder-ladder/RESULTS.json'
 fixture=json.loads(ref.read_text())['section4_explicit_P104'];removed={tuple(x) for x in fixture['F0']+fixture['C']}
 import itertools
 roots=[]
 for i,j in itertools.combinations(range(8),2):
  for sign in (-1,1):
   r=[0]*8;r[i]=2;r[j]=2*sign;roots.append(tuple(r))
 for signs in itertools.product((-1,1),repeat=7):
  if signs.count(-1)%2==0:roots.append((1,*signs))
 ports=[r for r in sorted(roots) if r not in removed];pairs=fixture['pairs_doubled_coordinates']
 require(set(rows)==set(names),'private row remains')
 for r in names:
  f=w['final_frames'][r];require(frames[r]==span(f),'endpoint chart')
  coeffs={r:Q(1)}
  if r.startswith('Y'):
   t=int(r[1:])
   for k,a in enumerate(ports):
    c=Q(sum(x*y for x,y in zip(ports[t],a)),8)
    if c:coeffs[f'X{k}']=c
  expected={(j,reduce_word(chart(f)+inverse(chart(w['initial_frames'][j])))):x for j,x in coeffs.items()}
  require(rows[r]==expected,'free chart endpoint mismatch '+r)
 return {'status':'PASS_FREE_NONCOMMUTING_CHART_REPLAY','arbitrary_input_columns':len(names),'chart_symbols':len(ids),'scope':'All invertible consistent frame charts; concrete Clifford realization and recursive hosting not established.'}
def main():
 w=json.loads((HERE/'LOWRANK-WITNESS.json').read_text());r=check(w)
 try:check(w,True)
 except ValueError:r['wrong_phase_control']='REJECTED'
 else:raise ValueError('phase control failed')
 print(json.dumps(r,indent=2));return r
if __name__=='__main__':main()

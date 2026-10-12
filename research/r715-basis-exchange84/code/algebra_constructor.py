"""Exact response-kernel packet deletion constructor.
Scalar/frame checker adapted from the existing prefix.py checker in tensor-normalization.
No floating-point arithmetic, network, native compilation, or third-party Python dependency.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,hashlib,json
SOURCE='e2ab3c0c4f25e78f96f14a548a795adaefda5bacbb01cd0ea61950f029aadf63'
GATES=[1426,2331,2340,2341,2346,2347,2636,2637,2640,2642,2694,2705,2752,2753,2767,2768,2810,2811,2828,2830,2868,2892]
from schur_constructor import check, rank

def responses(z):
 v=z['v'];n=2*v+z['R'];r=[0]*n
 for t in range(v):r[v+t]=1<<t
 def rev(e):
  f,d,ss=e
  for s in ss:r[s]^=r[d]
 for e in reversed(z['B']):rev(e)
 for t,ss in enumerate(z['scatter']):
  for k in ss:r[z['ret'][k]]^=r[v+t]
 result={}
 for i in range(len(z['A'])-1,-1,-1):
  f,d,ss=z['A'][i]
  if len(ss)==1 and ss[0]<v:result[i]=(ss[0],r[d])
  rev(z['A'][i])
 return result

def construct(z,selection):
 GATES=selection["gates"]
 assert all(e[1]>=2*z['v'] for e in z['A'])
 assert all(z['v']<=e[1]<2*z['v'] for e in z['B'])
 n=2*z['v']+z['R'];x=[1<<i for i in range(n)]
 for ph in ['A','C']:
  for f,d,ss in z[ph]:
   for s in ss:x[d]^=x[s]
 assert x==[1<<i for i in range(n)],'cleanup inverse'
 dims=[rank([z['lines'][i]for i in f])for f in z['frames']]
 base=check(z,dims);rs=responses(z);ann={};terms=[]
 for i in GATES:
  source,col=rs[i];ann[source]=ann.get(source,0)^col
  terms.append(dict(index=i,event=z['A'][i],source=source,response_hex=hex(col)))
 assert all(c==0 for c in ann.values()),'packet annihilator'
 w=copy.deepcopy(z);w['A']=[e for i,e in enumerate(z['A'])if i not in GATES]
 w['C']=[[1,d,ss]for f,d,ss in reversed(w['A'])]
 got=check(w,dims);delta={k:got['profile'].get(k,0)-base['profile'].get(k,0)for k in set(base['profile'])|set(got['profile'])};delta={k:v for k,v in delta.items()if v}
 assert delta=={1:-1,5:-1,6:1}
 controls={}
 for idx in GATES:
  bad=copy.deepcopy(z);bad['A'].pop(idx);bad['C']=[[1,d,ss]for f,d,ss in reversed(bad['A'])]
  try:check(bad,dims)
  except AssertionError as e:controls[str(idx)]=str(e)
  else:raise AssertionError('vacuous single deletion control')
 return w,dict(status='PASS_EXACT_PACKET_DELETION',base=base,candidate=got,delta=delta,terms=terms,controls=controls,removed_additions=44,scope='Finite provider replacement; inherited all-size compiler and assembly interfaces retained.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();raw=a.source.read_bytes();sel=json.loads(a.selection.read_bytes());assert hashlib.sha256(raw).hexdigest()==sel['source_sha256'];assert not a.output.exists()
 w,r=construct(json.loads(raw),sel);blob=json.dumps(w,sort_keys=True,separators=(',',':')).encode();r.update(source_sha256=sel['source_sha256'],candidate_sha256=hashlib.sha256(blob).hexdigest());assert r['candidate_sha256']==sel['candidate_sha256']
 a.output.mkdir(parents=True);(a.output/'word.json').write_bytes(blob);(a.output/'CHECKS.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(r['candidate_sha256'])
if __name__=='__main__':main()

"""Immutable-source retiming with exact finite source-bound replay.
Run: python retime_constructor.py SOURCE SELECTION OUTPUT_DIRECTORY
Requires the retained schur_constructor.py exact checker on its import path.
"""
from pathlib import Path
import argparse,copy,hashlib,json
from schur_constructor import rank,check
canon=lambda z:json.dumps(z,sort_keys=True,separators=(',',':')).encode()
def response(z,index,destination):
 v=z['v'];r=[0]*(2*v+z['R'])
 for t in range(v):r[v+t]=1<<t
 def rev(e):
  for s in e[2]:r[s]^=r[e[1]]
 for e in reversed(z['B']):rev(e)
 for t,ss in enumerate(z['scatter']):
  for k in ss:r[z['ret'][k]]^=r[v+t]
 for i in range(len(z['A'])-1,index,-1):rev(z['A'][i])
 return r[destination]
def construct(z,s):
 old=s['remove'];at=s['after'];gate=s['insert'];assert z['A'][old]==s['removed_event'];assert z['A'][at]==s['anchor_event'];assert len(gate[2])==1 and gate[2]==z['A'][old][2] and gate[2][0]<z['v'];assert all(e[1]>=2*z['v'] for e in z['A']);assert all(z['v']<=e[1]<2*z['v']for e in z['B']);a=response(z,old,z['A'][old][1]);b=response(z,at,gate[1]);assert a==b and a!=0
 dims=[rank([z['lines'][i]for i in f])for f in z['frames']];base=check(z,dims)
 def rewrite(remove,insert):
  w=copy.deepcopy(z);new=[]
  for i,e in enumerate(z['A']):
   if not(remove and i==old):new.append(e)
   if insert and i==at:new.append(gate)
  w['A']=new;w['C']=[[1,d,ss]for f,d,ss in reversed(new)];return w
 w=rewrite(True,True);got=check(w,dims);delta={k:got['profile'].get(k,0)-base['profile'].get(k,0)for k in set(got['profile'])|set(base['profile'])};delta={k:v for k,v in delta.items()if v};assert delta=={1:-1,3:-1,4:1};controls={}
 for label,remove,insert in [('deletion_without_reinsertion',True,False),('reinsertion_without_deletion',False,True)]:
  try:check(rewrite(remove,insert),dims)
  except AssertionError as e:controls[label]=str(e)
  else:raise AssertionError('vacuous control: '+label)
 assert all(w[k]==z[k]for k in z if k not in ('A','C'))
 return w,dict(status='PASS_EXACT_RESPONSE_RETIMING',base=base,candidate=got,delta=delta,response_hex=hex(a),controls=controls,selection=s,scope='Finite helper/target formal columns, exact rational frame ranks, monotone routing and integer operand spans. Complete global/invoice/analytic interfaces remain separate.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('out',type=Path);args=ap.parse_args();raw=args.source.read_bytes();s=json.loads(args.selection.read_bytes());assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];assert not args.out.exists();w,r=construct(json.loads(raw),s);blob=canon(w);assert hashlib.sha256(blob).hexdigest()==s['candidate_sha256'];r.update(source_sha256=s['source_sha256'],candidate_sha256=s['candidate_sha256']);args.out.mkdir(parents=True);(args.out/'word.json').write_bytes(blob);(args.out/'RETIME-AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()

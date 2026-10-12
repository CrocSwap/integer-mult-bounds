"""Pinned finite Schur target-interval constructor and exact replay.
Retains inherited all-size bit compiler/hosting/analytic interfaces. No optimizer,
network, external package or public-baseline verification is run here.
Rank and integer-support audit reused from our target-prefix constructor.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import argparse,copy,gzip,hashlib,json
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def rank(a):
 rows=[]
 for aa in a:
  r=list(map(Q,aa))
  for s in rows:
   p=next(i for i,x in enumerate(s)if x)
   if r[p]:q=r[p]/s[p];r=[x-q*y for x,y in zip(r,s)]
  if any(r):rows.append(r)
 return len(rows)
def check(z,dims):
 v=z['v'];n=2*v+z['R'];frames=list(map(frozenset,z['frames']));cur=z['start'][:];x=[1<<i for i in range(n)];supp=[Counter({i:1})if i<v else Counter()for i in range(n)];H=Counter();target_reads=0
 def visit(r,f):
  a=cur[r];assert frames[a]<=frames[f],('frame',r,a,f)
  if a!=f:dr=dims[f]-dims[a];assert dr>0;H[dr]+=1;cur[r]=f
 def run(phase):
  nonlocal target_reads
  for k,(f,d,ss)in enumerate(z[phase]):
   assert d>=v and d not in ss and len(ss)==len(set(ss))
   for r in [d]+ss:visit(r,f)
   for s in ss:
    assert set(supp[s])<=frames[f],('integer operand span',phase,k,s)
    if v<=s<2*v:target_reads+=1
    x[d]^=x[s];supp[d].update(supp[s])
   if d>=2*v:assert set(supp[d])<=frames[f]
 run('D');assert cur==z['start'];run('A');assert all(cur[t]==0 for t in range(v,2*v))
 cp=[x[r]for r in z['ret']]
 for r in z['ret']:H[dims[cur[r]]]+=1
 for t,ss in enumerate(z['scatter']):
  for k in ss:x[v+t]^=cp[k]
 run('B');run('C')
 for r,f in enumerate(z['final']):visit(r,f)
 expected=[1<<i for i in range(n)]
 for t in range(v):expected[v+t]^=1<<t
 assert x==expected,'raw arbitrary-dirty identity'
 return dict(columns=n,profile=dict(sorted(H.items())),target_reads=target_reads,all_integer_operand_spans=True)

def rewrite(z,sels):
 w=copy.deepcopy(z);B=[];start=defaultdict(list);end=defaultdict(list);rm=set();ad=defaultdict(list)
 busy=set()
 for ix,s in enumerate(sels):
  assert s['u']not in busy and s['d']not in busy;busy|={s['u'],s['d']}
  start[s['start']].append((ix,[s['setup_frame'],s['u'],[s['d']]]));end[s['end']].append((ix,[s['recover_frame'],s['u'],[s['d']]]));rm.update(map(tuple,s['remove']))
  for k,h in s['add_after']:ad[k].append((ix,[z['B'][k][0],s['u'],[h]]))
 marks=[]
 for k,(f,d,ss)in enumerate(z['B']):
  for ix,g in start[k]:marks.append((ix,'setup',len(B)));B.append(g)
  ss=[h for h in ss if(k,h)not in rm]
  if ss:B.append([f,d,ss])
  for ix,g in ad[k]:marks.append((ix,'correction',len(B)));B.append(g)
  for ix,g in end[k]:marks.append((ix,'recovery',len(B)));B.append(g)
 w['B']=B;return w,marks

def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();z=read(a.source);sel=read(a.selection)
 assert hashlib.sha256(canon(z)).hexdigest()==sel['source_canonical_sha256']
 assert not a.out.exists();a.out.mkdir(parents=True)
 dims=[rank([z['lines'][i]for i in f])for f in z['frames']];before=check(z,dims);w,marks=rewrite(z,sel['selected']);after=check(w,dims)
 assert all(w[k]==z[k]for k in z if k!='B')
 delta={r:after['profile'].get(r,0)-before['profile'].get(r,0)for r in set(before['profile'])|set(after['profile'])};delta={r:n for r,n in delta.items()if n}
 assert delta=={int(k):v for k,v in sel['expected_local_delta'].items()}and sum(r*n for r,n in delta.items())==0
 controls={}
 for ix,label,pos in marks:
  bad=copy.deepcopy(w);bad['B'].pop(pos)
  try:check(bad,dims)
  except AssertionError:controls[str(ix)+' '+label]='REJECTED'
  else:raise AssertionError('vacuous mutation '+str((ix,label)))
 raw=canon(w);assert hashlib.sha256(raw).hexdigest()==sel['expected_candidate_sha256'];(a.out/'word.json').write_bytes(raw)
 receipt=dict(status='PASS_SCHUR_INTERVAL_COMPLETE_FINITE_REPLAY',source_canonical_sha256=sel['source_canonical_sha256'],candidate_sha256=hashlib.sha256(raw).hexdigest(),selection_sha256=hashlib.sha256(a.selection.read_bytes()).hexdigest(),audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),before=before,after=after,delta=delta,all_other_word_fields_identical=True,mutations_rejected=controls,scope='All955 arbitrary-dirty binary columns, exact rational frame ranks, monotone frames and integer-clean-operand support. Native signed/formal-column and unchanged all-size/analytic interfaces remain separate.')
 (a.out/'SCHUR-AUDIT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

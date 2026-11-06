#!/usr/bin/env python3
"""Independent forward SSA/residence census and dual span certificates.
Jerry Chen / @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict, Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import contextlib, gzip, io, json, sys
from random import Random
from math import isqrt
P=65521
PIN='fb09340a36be41e1ac0570556a1b5ff51e2dbb314c6d54a1318f29393c8795a9'
def need(x,s):
 if not x:raise ValueError(s)
def q(x):
 x=Fraction(x);need(x.denominator&(x.denominator-1)==0,'Dyadic source coefficient')
 return x.numerator*pow(x.denominator,-1,P)%P
def add(a,b,c=1):
 for k,v in b.items():
  z=(a.get(k,0)+c*v)%P
  if z:a[k]=z
  elif k in a:del a[k]
def key(v):return tuple(sorted(v.items()))
def build(w):
 program=w['program'];n=w['public'];N=n+w['owned_fields'];edges=[]
 def new(parents=()):edges.append(list(parents));return len(edges)-1
 state=[new()for _ in range(n)]+[None]*(N-n);frames=w['initial'][:]+[None]*(N-n);start=[0]*N
 residences=[];writes=defaultdict(list);reads=defaultdict(list);after={};monitors=[]
 copies=sum(e[0]=='COPY'for e in program)
 for i,e in enumerate(program):
  op,r=e[:2];affected=[r];writes[r].append(i)
  if op in ('ADD','COPY'):
   s=e[2];need(s!=r,'No self ADD/COPY');affected.append(s);reads[s].append(i)
  for a in affected:
   if frames[a]is not None:residences.append((a,start[a],i,frames[a],state[a]))
   start[a]=i+1
  if op=='INIT':need(frames[r]is None,'Fresh INIT');frames[r]=e[2];state[r]=new()
  elif op=='CLEAR':need(frames[r]==e[2],'CLEAR frame');frames[r]=None;state[r]=None
  elif op=='MOVE':need(frames[r]==e[2],'MOVE frame');frames[r]=e[3];state[r]=new([(state[r],1)])
  elif op=='SCALE':
   need(frames[r]==e[3],'SCALE frame');f=Fraction(e[2]);need(abs(f.numerator)&(abs(f.numerator)-1)==0,'SCALE inverse is dyadic');a=q(e[2]);need(a,'Modular SCALE unit');state[r]=new([(state[r],a)])
  elif op in ('ADD','COPY'):
   need(frames[r]==frames[s]==e[4],'ADD/COPY frame');oldr,olds=state[r],state[s]
   if op=='COPY':monitors.append((oldr,n+copies-1-len(monitors)))
   state[r]=new([(oldr,1),(olds,q(e[3]))]);state[s]=new([(olds,1)])
  else:raise ValueError(op)
  after[i]=state[r]
 for r in range(N):
  if frames[r]is not None:residences.append((r,start[r],len(program),frames[r],state[r]))
 need(frames==w['final']+[None]*w['owned_fields'],'Forward final frames')
 need(len({tuple(f)for f in w['frames']})==len(w['frames']),'Unique frame encodings')
 adj=[{}for _ in edges]
 for r in range(n):
  if w['final'][r]!=127:adj[state[r]][r]=1
 for node,label in monitors:adj[node][label]=1
 for node in range(len(edges)-1,-1,-1):
  for prev,a in edges[node]:add(adj[prev],adj[node],a)
 rng=Random(27);values=[rng.randrange(P)for _ in range(n)]
 for parents in edges[n:]:values.append(sum(values[j]*a for j,a in parents)%P)
 main=set(w['live'])|{r+112 for r in w['live']};cs=[]
 for r in range(n):
  if r in main:continue
  mov=[i for i in writes[r]if program[i][0]=='MOVE']
  for i,j in zip(mov,mov[1:]):
   between=[z for z in writes[r]if i<z<j]
   if any(program[z][0]!='SCALE'for z in between):continue
   exports=[z for z in reads[r]if i<z<j]
   if not exports:continue
   need(all(program[z][0]=='ADD'for z in exports),'ADD-only exports')
   previous=[z for z in writes[r]if z<i and program[z][0]!='SCALE'];following=[z for z in writes[r]if z>j and program[z][0]!='SCALE']
   lo=previous[-1]+1 if previous else 0;hi=following[0]if following else len(program)
   left=max([lo]+[z+1 for z in reads[r]if lo<=z<i]);right=min([hi]+[z for z in reads[r]if j<z<hi])
   need(values[after[i]],'Independent exact held-row nonzero witness, seed27')
   E,F,G=program[i][2],program[i][3],program[j][3];target={}
   for z in exports:
    a=q(program[z][3])
    for t in between:
     if t<z:a=a*q(program[t][2])%P
    add(target,adj[after[z]],a)
   nodes=[]
   for rr,a,b,frame,node in residences:
    if rr==r or not adj[node]:continue
    if frame==E and max(a,lo)<=min(b,right):nodes.append((max(a,lo),rr,key(adj[node]),'E'))
    if frame==G and max(a,left)<=min(b,hi):nodes.append((min(b,hi),rr,key(adj[node]),'G'))
   cs.append(dict(role=r,first=i,second=j,lo=lo,hi=hi,move_lo=left,move_hi=right,E=E,F=F,G=G,exports=exports,target=target,nodes=nodes))
 return cs,residences,len(edges),len(monitors)
def dual(columns,target):
 basis={}
 for col in reversed(columns):
  v=dict(col)
  for pivot in sorted(basis,reverse=True):
   if pivot in v:add(v,basis[pivot],-v[pivot])
  if v:
   pivot=max(v);a=pow(v[pivot],-1,P);basis[pivot]={k:x*a%P for k,x in v.items()}
 v=target.copy()
 for pivot in sorted(basis,reverse=True):
  if pivot in v:add(v,basis[pivot],-v[pivot])
 if not v:return None
 lam={max(v):1}
 for k in sorted(basis):
  z=sum(lam.get(j,0)*a for j,a in basis[k].items())%P
  if z:
   value=(lam.get(k,0)-z)%P
   if value:lam[k]=value
   elif k in lam:del lam[k]
 z=sum(lam.get(j,0)*a for j,a in target.items())%P;need(z,'Nonzero dual target')
 lam={j:a*pow(z,-1,P)%P for j,a in lam.items()}
 need(all(sum(lam.get(j,0)*a for j,a in col.items())%P==0 for col in columns),'Dual annihilates every column')
 need(sum(lam.get(j,0)*a for j,a in target.items())%P==1,'Dual evaluates target to one')
 return lam
def dual_ok(lam,columns,target):
 return all(sum(lam.get(j,0)*a for j,a in col.items())%P==0 for col in columns) and sum(lam.get(j,0)*a for j,a in target.items())%P==1
def main():
 need(all(P%d for d in range(2,isqrt(P)+1)),'65521 is prime')
 package=Path(sys.argv[1]).resolve();name=sys.argv[2]if len(sys.argv)>2 else 'PR6702';source=package/'inputs'/f'{name}-WORD.json.gz';w=json.load(gzip.open(source))
 raw=(package/'search.py').read_bytes();need(sha256(raw).hexdigest()==PIN,'Pinned generator');text=raw.decode()
 fragment=text.split('hits=[];stats=Counter()')[0]
 fragment=fragment.replace('def save(r,lo,hi):\n    global nodes','def save(r,lo,hi):\n    global nodes\n    trace.append((r,lo,hi,frames[r]))')
 old=sys.argv;sys.argv=['search.py',str(source),'/tmp/not-written.json'];ns={'trace':[],'__name__':'reviewed_generator'}
 try:
  with contextlib.redirect_stdout(io.StringIO()):exec(compile(fragment,str(package/'search.py'),'exec'),ns)
 finally:sys.argv=old
 own,residences,ssa,monitors=build(w);author=ns['intervals']
 need(Counter((r,a,b,f)for r,a,b,f,_ in residences)==Counter(t for t in ns['trace']if t[3]is not None and t[1]<=t[2]),'Forward and reverse residence census agrees')
 need(len(own)==len(author),'Complete helper interval census')
 certificates=[];systems=0;nomination=0;dotchecks=0;hit_intervals=set();controls=0
 for c,d in zip(own,author):
  for field in ('role','first','second','lo','hi','move_lo','move_hi','E','F','G','exports','target'):need(c[field]==d[field],'Independent interval/target '+field)
  need(Counter(c['nodes'])==Counter((t,r,key(v),kind)for t,r,v,kind in d['nodes']),'Every carrier residence and response')
  cuts=sorted({c['move_lo'],c['move_hi']}|{t for t,_,_,_ in c['nodes']if c['move_lo']<=t<=c['move_hi']})
  for t in cuts:
   columns=[dict(v)for v in sorted({v for z,_,v,kind in c['nodes']if(kind=='E'and z<=t)or(kind=='G'and z>=t)})]
   lam=dual(columns,c['target']);systems+=1
   if lam is None:nomination+=1;hit_intervals.add((c['role'],c['first'],c['second']));continue
   need(dual_ok(lam,columns,c['target']),'Independent final dot-product validation')
   if not controls:
    k=next(iter(lam));bad=c['target'].copy();add(bad,{k:1},pow(lam[k],-1,P))
    need(not dual_ok({},columns,c['target']),'Reject zero witness')
    need(not dual_ok(lam,columns+[{k:1}],c['target']),'Reject changed column inventory')
    need(not dual_ok(lam,columns,bad),'Reject changed target');controls=3
   dotchecks+=len(columns)+1
   certificates.append({'role':c['role'],'first':c['first'],'second':c['second'],'cut':t,'dual':dict(sorted(lam.items())),'column_count':len(columns)})
 receipt={'source':name,'source_sha256':sha256(source.read_bytes()).hexdigest(),'generator_sha256':PIN,'ssa_nodes':ssa,'live_residences':len(residences),'intervals':len(own),'systems':systems,'modular_nominations':nomination,'copy_monitors':monitors,'held_row_nonzero_witnesses':len(own),'held_row_witness_seed':27,'dual_witnesses':len(certificates),'checked_dot_products':dotchecks,'nomination_intervals':sorted(hit_intervals),'mutation_controls':controls,'certificates':certificates}
 if name=='PR6453':need(len(hit_intervals)==2 and {x[0]for x in hit_intervals}=={336,368},'Exactly two historical fusion intervals')
 if name=='PR6702':need((len(own),systems,nomination)==(631,2387,0),'Current complete no-hit result')
 out=Path(sys.argv[3])if len(sys.argv)>3 else Path(__file__).with_name(name+'-REVIEW.json');out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in receipt.items()if k!='certificates'},sort_keys=True));print('PASS_FORWARD_SSA_RESIDENCES_AND_DUAL_CERTIFICATES')
if __name__=='__main__':main()

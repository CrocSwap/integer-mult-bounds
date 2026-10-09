#!/usr/bin/env python3
"""Independent multiplicative endpoint-gauge and literal-word eligibility audit.

Default verifies endpoint-check.json; --record writes it deterministically.
No production profile or arithmetic checker is imported.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
from itertools import product,combinations
import argparse,gzip,hashlib,json
HERE=Path(__file__).resolve().parent

def require(ok,message):
 if not ok:raise ValueError(message)

def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def add(A,B,sgn=1):return [[a+sgn*b for a,b in zip(x,y)] for x,y in zip(A,B)]
def mul(A,B):return [[sum((a*b for a,b in zip(row,col)),Q()) for col in zip(*B)] for row in A]
def inv(A):
 n=len(A);T=[list(row)+unit for row,unit in zip(A,eye(n))]
 for j in range(n):
  k=next(i for i in range(j,n) if T[i][j]);T[j],T[k]=T[k],T[j];v=T[j][j];T[j]=[x/v for x in T[j]]
  for i in range(n):
   if i!=j:
    q=T[i][j];T[i]=[x-q*y for x,y in zip(T[i],T[j])]
 return [r[n:] for r in T]
def D(A):
 B=add(eye(len(A)),A,-1)
 return [x+y for x,y in zip(B,A)]+[x+y for x,y in zip(A,B)]

def exact_operator_audit():
 n=3;I=eye(n);K=[[Q(1+(i==j)) for j in range(n)] for i in range(n)];Ki=inv(K)
 P=mul(mul(K,[[Q(i==j and i==0) for j in range(n)] for i in range(n)]),Ki)
 H=mul(mul(K,[[Q(i==j and i<2) for j in range(n)] for i in range(n)]),Ki);E=add(I,H,-1)
 O=eye(2*n);F=D(I);DE=D(E);DH=D(H)
 require(mul(P,P)==P and mul(H,H)==H and mul(E,E)==E,'Projector fixture')
 require(mul(E,P)==[[0]*n for _ in range(n)] and mul(P,E)==[[0]*n for _ in range(n)],'Orthogonal exterior')
 entrance=add(E,P);retirement=add(I,P,-1)
 require(mul(entrance,entrance)==entrance and mul(retirement,retirement)==retirement,'Merged idempotents')
 for stage,S,T,G,last in [(1,O,F,D(P),DH),(2,DE,DH,mul(DE,D(P)),F)]:
  newS,newT=mul(S,DE),mul(T,DE)
  require(mul(T,inv(S))==F and mul(newT,inv(newS))==F,'Endpoint quotient changed')
  require(mul(G,inv(newS))==D(entrance),'Wrong merged entrance')
  require(mul(newT,inv(last))==O,'Final exterior did not vanish')
  require(mul(DE,D(add(H,P,-1)))==D(retirement),'Wrong merged retirement')
 wrong_one=mul(F,inv(DE))
 wrong_negative=mul(DH,inv(D([[-x for x in row] for row in E])))
 require(wrong_one!=F,'One-endpoint negative control missed')
 require(wrong_negative!=F,'Literal negative-projector negative control missed')
 return dict(noncoordinate_rational_fixture=True,stages_checked=2,merged_entrance_idempotent=True,merged_retirement_idempotent=True,endpoint_quotients_preserved=True,final_exterior_removed=True,negative_controls=dict(one_endpoint_only_rejected=True,literal_D_minus_E_rejected=True))

def dirty_audit():
 # A real pointwise XOR shear restores an arbitrary auxiliary. Every
 # coordinate address delta in each of three independent streams is tested.
 p=3;n=3;addresses=list(product(range(p),repeat=2*n));index={a:i for i,a in enumerate(addresses)}
 perms=[]
 for mask in range(1<<n):
  row=[]
  for a in addresses:
   b=list(a)
   for j in range(n):
    if mask>>j&1:b[j],b[n+j]=b[n+j],b[j]
   row.append(index[tuple(b)])
  perms.append(row)
 def moved(values,mask):return {perms[mask][x] for x in values}
 checked=0
 for stage in (1,2):
  offset=0 if stage==1 else 4
  oldS=0 if stage==1 else 4;oldT=7 if stage==1 else 3
  # aux+=x; y+=aux; aux+=x; y+=aux. The auxiliary returns
  # exactly and y gains x. Gate frames and XORs are never changed.
  gates=[(2,0,1^offset),(1,2,3^offset),(2,0,3^offset),(1,2,1^offset)]
  for changed in (False,True):
   source=[0,0,oldS^(4 if changed else 0)];sink=[0,0,oldT^(4 if changed else 0)]
   for role in range(3):
    for address in range(len(addresses)):
     values=[set(),set(),set()];values[role]={address};frames=source.copy()
     for target,control,frame in gates:
      for w in (target,control):values[w]=moved(values[w],frames[w]^frame);frames[w]=frame
      values[target]^=values[control]
     for w in range(3):values[w]=moved(values[w],frames[w]^sink[w])
     expected=[set(),set(),set()]
     if role==0:expected[0]={address};expected[1]={address}
     elif role==1:expected[1]={address}
     else:expected[2]={perms[7][address]}
     require(values==expected,'Full arbitrary-dirty fixture failed');checked+=1
 return dict(address_prime=p,ambient_dimension=n,address_deltas=len(addresses),independent_roles=3,stages=2,baseline_and_shifted=True,complete_basis_runs=checked,all_dirty_and_data_outputs_unchanged=True)

def validate_selection(s,R,outputroles):
 a,b=s['entrance'],s['exit']
 require(a==sorted(set(a)) and b==sorted(set(b)),'Noncanonical selection')
 require(all(type(x)is int and 0<=x<R for x in a+b),'Role out of range')
 require(not(set(a)&set(b)),'A role cannot merge both endpoints')
 require(not(set(b)&outputroles),'Retirement merge would precede an output/scatter incidence')

def word_audit(path,selection_path,h):
 compressed=path.read_bytes();raw=gzip.decompress(compressed) if path.suffix=='.gz' else compressed;d=json.loads(raw);selection_raw=selection_path.read_bytes();s=json.loads(selection_raw)
 R=d['R'];F=d['frames'];v=d['v'];require(d['h']==h and s['h']==h and s['R']==R,'Axis metadata')
 require(s['word_sha256']==hashlib.sha256(compressed).hexdigest(),'Selection word hash')
 require(v==len(list(combinations(range(h),3))),'Source count')
 require(len(set(map(tuple,F)))==len(F),'Duplicate frames')
 ranks=[]
 for core,cover in F:
  require(core and not(core&~cover) and(core.bit_count()in(1,2)or core==cover and core.bit_count()==3),'Bad envelope')
  ranks.append(1 if core==cover else cover.bit_count()-core.bit_count())
 recorded=[[] for _ in range(R)];state=[None]*R
 for slot,old,new in d['events']:
  require(0<=slot<R and 0<=new<len(F),'Bad event')
  require(state[slot]==(None if old==-1 else old),'Event chronology')
  if not recorded[slot] or recorded[slot][-1]!=new:recorded[slot].append(new)
  state[slot]=new
 actual=[[] for _ in range(R)]
 def incidence(slot,frame):
  require(0<=slot<R and 0<=frame<len(F),'Bad incidence')
  if actual[slot]:
   old=actual[slot][-1];c,u=F[old];cc,uu=F[frame]
   require(not(cc&~c) and not(u&~uu),'Decreasing original frame')
  if not actual[slot] or actual[slot][-1]!=frame:actual[slot].append(frame)
 triples=list(combinations(range(h),3));lookup={tuple(f):i for i,f in enumerate(F)}
 for source,slot in d['sources'].items():
  mask=sum(1<<i for i in triples[int(source)]);incidence(slot,lookup[mask,mask])
 for a,b,g in d['ops']:
  require(a!=b,'Self XOR');incidence(a,g);incidence(b,g)
 outputroles=set();centers=set()
 for slot,g,common,target in d['outputs']:
  require(slot not in outputroles,'Duplicate output slot');outputroles.add(slot);incidence(slot,g)
  c,u=F[g]
  if len(target)==1:
   require(c==1<<common and u==(1<<h)-1,'Center frame');centers.add(slot)
  else:require(len(target)==3 and c==1<<common and u==((1<<h)-1)^sum(1<<j for j in target if j!=common),'Side frame')
 require(len(centers)==h,'Center count')
 require(actual==recorded and all(actual),'Literal per-role transition paths differ from events')
 validate_selection(s,R,outputroles)
 expected=set()
 for kind,slots in [('entrance',s['entrance']),('exit',s['exit'])]:
  for slot in slots:
   frame=actual[slot][0 if kind=='entrance' else -1];expected.add(f'{kind}:{frame}')
   removed=ranks[frame] if kind=='entrance' else h-ranks[frame]
   edge=s['merged_edges'][f'{kind}:{frame}'];require(edge['rank']==575-h+removed,'Merged rank mismatch')
   require(sum(edge['runs'])==edge['rank'],'Merged profile mass')
 require(expected==set(s['merged_edges']),'Unused or omitted merged edges')
 bad=dict(s);out=min(outputroles);bad['entrance']=sorted(set(s['entrance'])-{out});bad['exit']=sorted(set(s['exit'])|{out})
 try:validate_selection(bad,R,outputroles)
 except ValueError as error:require('output/scatter' in str(error),'Wrong negative-control rejection')
 else:raise ValueError('Output retirement negative control was accepted')
 return dict(h=h,R=R,word_sha256=hashlib.sha256(raw).hexdigest(),compressed_word_sha256=hashlib.sha256(compressed).hexdigest(),selection_sha256=hashlib.sha256(selection_raw).hexdigest(),every_role_literal_transition_sequence_checked=True,all_first_and_last_frames_reconstructed=True,entrance_roles=len(s['entrance']),retirement_roles=len(s['exit']),creation_merged_output_roles=len(set(s['entrance'])&outputroles),creation_merged_center_roles=len(set(s['entrance'])&centers),retirement_roles_exclude_all_scatter_outputs=True,output_retirement_negative_control_rejected=True,scope='Endpoint eligibility and chronological frame compatibility. The separately pinned original dirty replay and exact recursive profiles remain required.')

def generate(words,selections):
 return dict(scope='Multiplicative partial-swap endpoint proof, exact rational/two-stage arbitrary-dirty fixtures, and literal selected-word endpoint eligibility. Does not re-certify full recursive profiles or arithmetic.',operator=exact_operator_audit(),dirty=dirty_audit(),axes=[word_audit(w,s,h) for w,s,h in zip(words,selections,(23,25))],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--word23',type=Path,default=HERE/'word-23.json.gz');p.add_argument('--word25',type=Path,default=HERE/'word-25.json.gz');p.add_argument('--selection23',type=Path,default=HERE/'selection-23.json');p.add_argument('--selection25',type=Path,default=HERE/'selection-25.json');p.add_argument('--receipt',type=Path,default=HERE/'endpoint-check.json');p.add_argument('--record',action='store_true');a=p.parse_args()
 result=generate([a.word23,a.word25],[a.selection23,a.selection25]);encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if a.record:a.receipt.write_text(encoded)
 else:require(a.receipt.read_text()==encoded,'Frozen endpoint audit differs')
 print('Multiplicative endpoint, arbitrary-dirty and actual-word eligibility audit PASS')

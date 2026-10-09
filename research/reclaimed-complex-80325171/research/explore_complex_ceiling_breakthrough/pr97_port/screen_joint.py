import sys,os
if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
 raise RuntimeError("Optimized Python is not permitted for scientific checks")
"""Original one-shot rational same-frame signal ledger; no physical word claim."""
exec(compile(open(__file__.replace('screen_joint.py','screen_groups.py')).read(),__file__,'exec'))
from fractions import Fraction as F
from math import log,exp
# Fraction echelon; groups have at most27 inputs and4 requested output values.
def reduce_row(row,basis):
 row={i:F(x) for i,x in row.items() if x}
 for p,b in basis:
  q=row.get(p,0)
  if q:
   for i,x in b.items():
    v=row.get(i,0)-q*x
    if v:row[i]=v
    elif i in row:del row[i]
 return row

def ins(row,basis):
 row=reduce_row(row,basis)
 if not row:return False
 p=min(row);q=row[p];basis.append((p,{i:x/q for i,x in row.items()}));return True
order=sorted(range(len(blocks)),key=lambda k:(blocks[k]['rank'],min(blocks[k]['nodes'])))
position={k:i for i,k in enumerate(order)}
uses=[];value_uses=defaultdict(list)
for b in blocks:b['use_ids']=[]
for k,b in enumerate(blocks):
 b['ins']=sorted(b['ins'])
 for y in b['ins']:
  uid=len(uses);uses.append((y,k,False));value_uses[y].append(uid);blocks[owner[y]]['use_ids'].append(uid)
for j,x in enumerate(roots):
 uid=len(uses);uses.append((x,owner[x],True));value_uses[x].append(uid);blocks[owner[x]]['use_ids'].append(uid)
H=Counter();R=0;sumrank=0
for k in order:
 b=blocks[k];n=len(b['ins']);b['basis']=[];b['inputs_index']={x:i for i,x in enumerate(b['ins'])}
 if not n:
  b['basis']=[(0,{0:F(1)})];b['output_rank']=1
  R+=len(b['outs']);H[1]+=len(b['outs']);continue
 coeff={x:{i:F(1)} for i,x in enumerate(b['ins'])}
 for x in b['nodes']:
  a,z=g.a[x];row=coeff[a].copy()
  for i,vv in coeff[z].items():row[i]=row.get(i,0)+vv
  coeff[x]=row
 for x in sorted(set(b['outs'])):ins(coeff[x],b['basis'])
 rk=len(b['basis']);b['output_rank']=rk;sumrank+=rk
 fresh=len(b['outs'])-rk;R+=fresh;H[b['rank']]+=fresh;H[h-b['rank']]+=n-rk
 for y in b['ins']:H[b['rank']-g.r[y]]+=1
 b['coeff']=coeff
for j,x in enumerate(roots):
 r=g.r[x]
 if j<len(pieces):H[h-1-r]+=1;H[1]+=1
 else:H[r]+=1;H[h-r]+=1
assert sum(r*n for r,n in H.items())==h*R+ell
base_R=R;base_H=H.copy()
# Greedy independent carrier selection. One use per carrier; chronological legal containments.
whole=(1<<h)-1
def contains(x,y):
 tx,ty=g.ty[x],g.ty[y]
 if tx==ty==1:return not(g.c[y]&~g.c[x] or g.u[x]&~g.u[y])
 if tx in (1,2) and ty==2:return not g.u[x]&~g.u[y]
 if tx==1 and ty==3:return bool(g.c[x]&g.c[y])
 if tx==2 and ty==3:return not g.u[x]&~g.c[y]
 if tx==3 and ty==2:return g.u[y]==whole
 if tx==ty==3:return g.c[x]==g.c[y]
 return False
selected={};candidates=0;capacity=0;selected_rank_hist=Counter()
# deterministic earliest use, largest donor rank first, only a single attempt.
choices=[]
for k in order:
 b=blocks[k];n=len(b['ins'])
 if not n:continue
 capacity+=n-b['output_rank'];x=b['nodes'][0]
 for i,y in enumerate(b['ins']):
  if not reduce_row({i:1},b['basis']):continue
  for uid in value_uses[y]:
   _,target,terminal=uses[uid]
   # source output terminal own frame lies earlier than receiving block; no late equal-rank free reordering
   if position[k]<position[target] and contains(x,blocks[target]['nodes'][0]):
    choices.append((position[target],-b['rank'],k,uid,i,y,target));candidates+=1
for _,__,k,uid,i,y,target in sorted(choices):
 if uid in selected:continue
 b=blocks[k]
 if ins({i:1},b['basis']):
  selected[uid]=(k,i);R-=1;r=b['rank'];selected_rank_hist[r]+=1
  # Remove fresh copy at value's owner and donor retirement; replace old entrance into future frame.
  yr=g.r[y];tr=blocks[target]['rank'];H[h-r]-=1;H[yr]-=1;H[tr-yr]-=1;H[tr-r]+=1
assert min(H.values())>=0,[(x,y)for x,y in H.items() if y<0]
assert sum(r*n for r,n in H.items())==h*R+ell

def profile(R,H):
 N=g.v*g.v;m=h*h;W=2*N+2*g.v*R;child=Counter({m-h:2*g.v*R,(h-1)**2:2*N,h-1:4*N,1:N})
 for r,n in H.items():
  if r:child[r]+=2*g.v*n
 assert sum(r*n for r,n in child.items())==m*W-N+2*g.v*ell
 moment=lambda a:sum(n*r*exp(a*log(m/r)) for r,n in child.items())/(W*m)
 lo,hi=0,.001
 for _ in range(60):
  mid=(lo+hi)/2
  if moment(mid)<1:lo=mid
  else:hi=mid
 target=1.5*6.3965813e-5
 return dict(R=R,W=W,histogram=dict(sorted(H.items())),child_histogram=dict(sorted(child.items())),mass=sum(r*n for r,n in child.items()),root_author_float=(lo+hi)/2,target97=target,moment_at_target97=moment(target),moment_at_target97_div09=moment(target/.9))
result=dict(status='Author exact region/matroid-independent carrier ledger only; no literal physical synthesis, reclamation, replay, or bound',baseline=profile(base_R,base_H),greedy=profile(R,H),rational_output_rank_sum=sumrank,eligible_candidates=candidates,unused_coordinate_capacity=capacity,selected_carriers=len(selected),carrier_rank_hist=dict(selected_rank_hist),seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(root/'JOINT_SCREEN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('baseline','greedy')},indent=2));print('base',base_R,result['baseline']['root_author_float']);print('greedy',R,result['greedy']['root_author_float'],result['greedy']['moment_at_target97'])

#!/usr/bin/env python3
"""Literal binary chronology and signed dirty controls for complex B-defer.
Scratch research artifact: no final stopped/precision/assembly certificate.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import json,gzip,hashlib,argparse,struct
from complex_profile import basis,null,inside,nondeg,selection_to_json,selection_from_json
HERE=Path(__file__).resolve().parent
if not __debug__:raise SystemExit("Assertions required")

def run(word,sel,screen,out):
 blob=word.read_bytes();d=json.loads(gzip.decompress(blob));h,v,R=d['h'],d['v'],d['R'];tr=list(combinations(range(h),3));tid={T:i for i,T in enumerate(tr)};lines=[(sum(1<<i for i in T),)for T in tr];full=tuple(1<<i for i in reversed(range(h)));hyp=[null(u,h)for u in lines]
 sigma=sel['sigma'];order=[s for s in sel['order']if s in sigma];covmask=sel['cov_masks'];phase=set(d['center_phase']);touched=set(d['center_touched']);assert not set(sigma)&touched
 # Derive the phase again from actual role-order precedence, not supplied IDs.
 last={};pred=[]
 for j,(a,b)in enumerate(d['ops']):pred.append(tuple(last[s]for s in(a,b)if s in last));last[a]=last[b]=j
 todo=[last[s]for s,j,k in d['outputs']if k and s in last];actualphase=set()
 while todo:
  j=todo.pop()
  if j not in actualphase:actualphase.add(j);todo.extend(pred[j])
 assert phase==actualphase
 index=sorted(phase)+[j for j in range(len(d['ops']))if j not in phase]
 position={j:i for i,j in enumerate(index)}
 assert all(position[p]<position[j]for j in range(len(pred))for p in pred[j])
 def nodeframe(node):
  typ,c,u,r=d['frames'][node]
  if typ==2:B=basis(1<<j for j in range(h)if u>>j&1)
  elif c.bit_count()==3:B=(c,)
  else:B=basis(c|(1<<j)for j in range(h)if u>>j&1 and not c>>j&1)
  assert len(B)==r and nondeg(B);return B
 frames={};bs=[]
 def key(B):
  B=basis(B)
  if B not in frames:frames[B]=len(bs);bs.append(B)
  return frames[B]
 zero=key(());whole=key(full);source=[key(x)for x in lines];targets=[key(x)for x in hyp];of=[key(nodeframe(n))for n in d['opframes']]
 sig=[key(sigma.get(s,()))for s in range(R)];cur=source+[zero]*v+sig[:];initial=cur[:];off=2*v;events=[];H=Counter();parts={x:Counter()for x in('aux','data','center')};geometry=set();readout_count=0
 def move(s,f):
  old=cur[s]
  if old==f:return
  A,B=bs[old],bs[f];assert inside(A,B)and nondeg(A)and nondeg(B)
  r=len(B)-len(A);assert r>0;D=tuple(x for x in null(A,h))
  # Orthogonal difference has exactly r dimensions and nondegenerate Gram.
  residual=null(basis(null(B,h)+A),h);assert len(residual)==r and nondeg(residual)
  parts['aux'if s>=off else'data'][r]+=1;H[r]+=1;cur[s]=f;events.append((0,s,old,f,r));geometry.add((old,f))
 def add(a,b,n=1,den=1):
  assert a!=b and cur[a]==cur[b];events.append((1,a,b,n,den))
 # Exact signed ordinary-root covectors by bounded packed lanes. Center-free
 # slots have no center contribution, proved again by reverse reachability.
 rt=list(range(v));sg=[1]*v
 for a,b in combinations(range(h),2):
  for i in sorted((i for i in range(h)if i not in(a,b)),key=lambda i:((i^1)in(a,b),i)):
   rt.append(tid[tuple(sorted((a,b,i)))]);sg.append(-1)
 bound=[0]*R;reach=[0]*R
 for s,j,k in d['outputs']:
  if k:reach[s]=1
  else:bound[s]+=1
 for a,b in reversed(d['ops']):bound[b]+=bound[a];reach[b]|=reach[a]
 bits=16;guard=1<<(bits-1);assert max(bound)<guard;packed=[0]*R
 for s,j,k in d['outputs']:
  if not k:packed[s]+=sg[j]<<(bits*rt[j])
 for a,b in reversed(d['ops']):packed[b]+=packed[a]
 guards=sum(guard<<(bits*t)for t in range(v));mask=(1<<bits)-1
 coefficients={}
 for s in order:
  assert not reach[s];value=packed[s]+guards;ts=[];z=covmask[s]
  while z:
   b=z&-z;z-=b;t=b.bit_length()-1;n=((value>>(bits*t))&mask)-guard;assert n;ts.append((t,n))
  coefficients[s]=ts
 # Grouped zero-frame readouts are C_s=J L column. They are uniquely specified
 # by the full ordinary L and rational J below; no dense matrix is needed.
 for s in range(R):
  if s not in sigma:assert cur[off+s]==zero
 assert all(cur[v+t]==zero for t in range(v))
 nondeferred=R-len(sigma)
 def inject(early):
  for s,node in d['sources']:
   if (s in touched)!=early:continue
   t=node-1;move(off+s,source[t]);assert cur[t]==source[t];add(off+s,t)
 def mix(indices,high=False):
  for j in indices:
   a,b=d['ops'][j];f=whole if high else of[j];move(off+a,f);move(off+b,f);add(off+a,off+b,-1 if high else 1)
 inject(True);mix(sorted(phase))
 centers=[]
 for s,j,k in d['outputs']:
  if not k:continue
  i=j-4*v;assert 0<=i<h;assert cur[off+s]==key(nodeframe(d['root_nodes'][j]));assert len(bs[cur[off+s]])==h-1
  assert all(cur[v+t]==zero for t in range(v));events.append((2,off+s,cur[off+s],i,h-1));parts['center'][h-1]+=1;H[h-1]+=1;centers.append((s,i))
 # A center copied after any selected readout would require every Y at0,
 # since 2-21*1[i in T] is nonzero for every triple T.
 for s in order:
  assert cur[off+s]==sig[s]
  for t,n in coefficients[s]:move(v+t,sig[s]);add(v+t,off+s,-n,2);readout_count+=1
 assert any(cur[v+t]!=zero for t in range(v));late_center_rejected=not all(cur[v+t]==zero for t in range(v));assert late_center_rejected
 inject(False);mix([j for j in range(len(d['ops']))if j not in phase])
 for s,j,k in d['outputs']:
  if k:continue
  t=rt[j];move(off+s,targets[t]);move(v+t,targets[t]);add(v+t,off+s,sg[j],2)
 mix(list(reversed(index)),high=True)
 for s,node in d['sources']:
  t=node-1;move(off+s,whole);move(t,whole);add(off+s,t,-1)
 for s in range(R):move(off+s,whole)
 assert cur[:v]==[whole]*v and cur[v:off]==targets and cur[off:]==[whole]*R
 assert sum(r*n for r,n in parts['aux'].items())==R*h-sum(len(B)for B in sigma.values())
 assert sum(r*n for r,n in parts['data'].items())==2*v*(h-1)
 assert parts['center']==Counter({h-1:h})
 # Literal reflected opposite stage: reverse every signed event, complement
 # all frames, and swap data banks. Scalar signs are negated.
 bank=lambda s:s+v if s<v else s-v if s<off else s
 complement={j:key(null(B,h))for j,B in enumerate(bs[:])};rev=[None]*len(cur)
 for s in range(len(cur)):rev[bank(s)]=complement[cur[s]]
 RH=Counter();reflected_adds=0
 for kind,a,b,c,e in reversed(events):
  a=bank(a)
  if kind==0:
   assert rev[a]==complement[c];A,B=bs[complement[c]],bs[complement[b]];assert inside(A,B)and nondeg(A)and nondeg(B);assert len(B)-len(A)==e;rev[a]=complement[b];RH[e]+=1
  elif kind==1:
   b=bank(b);assert rev[a]==rev[b];reflected_adds+=1
  else:
   assert rev[a]==complement[b]
   assert all(rev[bank(v+t)]==complement[zero]for t in range(v));RH[e]+=1;reflected_adds+=v
 assert RH==H
 assert all(rev[bank(s)]==complement[initial[s]]for s in range(len(cur)))
 # Rebuild the complete rank histogram directly from actual forward events.
 m=h*h;N=v*v;W=2*N+2*v*R;paid=Counter({r:2*v*n for r,n in H.items()})
 for s in range(R):paid[m-h+len(sigma.get(s,()))]+=2*v
 paid[(h-1)**2]+=2*N;paid[1]+=N
 expected=screen;assert dict(paid)=={int(k):n for k,n in expected['histogram'].items()if n};assert sum(r*n for r,n in paid.items())==W*m-N+2*v*h*(h-1)
 # Full actual scalar program fixtures. Y is represented with denominator42,
 # while X/Z are integral. Matrix linearity and C=JL prove all dirty inputs.
 def scatter(vals,center=True,ordinary=True):
  y=[0]*v
  for s,j,k in d['outputs']:
   if k and center:
    i=j-4*v
    for t,T in enumerate(tr):y[t]+=(2-21*(i in T))*vals[s]
   elif not k and ordinary:y[rt[j]]+=21*sg[j]*vals[s]
  return y
 def forward(z,indices):
  for j in indices:
   a,b=d['ops'][j];z[a]+=z[b]
 fixtures=[];bad_omission=False
 for seed in(3,17,43):
  z=[((s+3)*(seed+7)+s*s)%29-14 for s in range(R)];x=[((t+5)*(seed+11)+t*t)%31-15 for t in range(v)];y0=[((t+7)*(seed+13))%37-18 for t in range(v)];lz=z[:];forward(lz,range(len(d['ops'])));allread=scatter(lz);defer=[0]*v
  for s in order:
   for t,n in coefficients[s]:defer[t]+=21*n*z[s]
  y=[42*a-b+c for a,b,c in zip(y0,allread,defer)];vals=z[:]
  for s,node in d['sources']:
   if s in touched:vals[s]+=x[node-1]
  forward(vals,sorted(phase));cen=scatter(vals,ordinary=False);y=[a+b for a,b in zip(y,cen)]
  for s in order:
   assert vals[s]==z[s]
   for t,n in coefficients[s]:y[t]-=21*n*vals[s]
  for s,node in d['sources']:
   if s not in touched:vals[s]+=x[node-1]
  forward(vals,[j for j in range(len(d['ops']))if j not in phase]);ordinary=scatter(vals,center=False);y=[a+b for a,b in zip(y,ordinary)]
  assert y==[42*(a+b)for a,b in zip(y0,x)]
  for j in reversed(index):a,b=d['ops'][j];vals[a]-=vals[b]
  for s,node in d['sources']:vals[s]-=x[node-1]
  assert vals==z;bad_omission|=any(defer)
  fixtures.append(hashlib.sha256(json.dumps([seed,y,vals],separators=(',',':')).encode()).hexdigest())
 assert bad_omission
 result=dict(status='EXACT_LOCAL_SCHEDULE_PASS',h=h,v=v,R=R,selected_gauges=len(sigma),sigma_rank_sum=sum(map(len,sigma.values())),center_phase_ops=len(phase),center_phase_untouched_verified=True,all_reordered_precedence_edges_verified=True,all_gates_equal_frame=True,all_moves_nested_and_nondegenerate=True,all_sigma_signed_target_caps_verified=True,all_data_readout_chains_verified=True,actual_deferred_signed_adds=readout_count,grouped_zero_frame_readouts=nondeferred,forward_events=len(events),distinct_frames=len(bs),actual_geometric_edges=len(geometry),reflected_opposite_signed_schedule_verified=True,reflected_rank_histogram_identical=True,auxiliary_internal_rank_mass=sum(r*n for r,n in parts['aux'].items()),local_data_rank_mass=sum(r*n for r,n in parts['data'].items()),center_copy_rank_mass=sum(r*n for r,n in parts['center'].items()),full_paid_histogram=dict(sorted(paid.items())),local_histograms={name:dict(sorted(HH.items()))for name,HH in parts.items()},maxchild=max(paid),dirty_fixtures=3,dirty_fixture_hashes=fixtures,negative_controls=dict(omitting_deferred_readout_changes_map=bad_omission,center_copy_after_readouts_rejected_by_chronology=late_center_rejected),word_sha256=hashlib.sha256(gzip.decompress(blob)).hexdigest(),selection_sha256=hashlib.sha256(selection_to_json(sel).encode()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Exact reordered scalar/physical-frame chronology, reflected inverse, full paid rank ledger and characteristic-zero dirty fixtures. Generic signed C_sigma endpoint proof and retained tensor endpoint corrections remain written dependencies; no all-size recursion/precision/row-stock/assembly claim.')
 out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--record',action='store_true');a=ap.parse_args();work=a.work
 result=run(work/'complex/literal-word.json.gz',selection_from_json((work/'complex-selection.json').read_text()),json.loads((work/'complex-screen.json').read_text()),work/'complex-word.json')
 raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
 if a.record:(HERE/'gauge-audit.json').write_text(raw)
 else:assert (HERE/'gauge-audit.json').read_text()==raw,'Frozen gauge chronology differs'
 print('PASS full signed gauge chronology and dirty controls')

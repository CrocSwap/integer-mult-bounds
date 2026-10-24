"""Independent R740-kernel audit: source word, emitted banks, invoice and exact outer arithmetic.
Usage: python independent_audit.py PACKAGE REPLAY_OUTPUT AUDIT_JSON
Python standard library only. No construction, discovery or pricing imports.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import sys,json,gzip,hashlib,math,copy

def audit_local(base_path,word_path,selection_path,retime_path=None):
 base=json.loads(gzip.decompress(base_path.read_bytes()));w=json.loads(word_path.read_bytes());s=json.loads(selection_path.read_bytes())
 sha=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert sha(base)==s['input_sha256']=='d6ec8811541d6ab59a3bbbaaa15bccc8918b3b43b23d9f593198cfe90826fd20';assert retime_path is not None or sha(w)==s['output_sha256']
 n=2*w['v']+w['R'];v=w['v'];h=w['h'];full=set(range(v));lines=w['lines']
 assert w['frames']==base['frames'] and w['lines']==base['lines']
 def primitive(x):
  g=math.gcd(*x)
  return [a//g for a in x] if g else x

 def basis(vectors):
  B={}
  for x in vectors:
   x=list(x)
   for p,b in B.items():
    if x[p]:
     q=x[p];x=primitive([b[p]*a-q*c for a,c in zip(x,b)])
   p=next((j for j,z in enumerate(x) if z),None)
   if p is not None:B[p]=primitive(x)
  return B

 def contained(x,B):
  x=list(x)
  for p,b in B.items():
   if x[p]:
    q=x[p];x=primitive([b[p]*a-q*c for a,c in zip(x,b)])
  return not any(x)
 F=[set(x) for x in w['frames']];B=[basis(lines[i] for i in f) for f in F];dims=list(map(len,B))
 for f,b in zip(F,B):assert f=={i for i,x in enumerate(lines) if contained(x,b)},'frame closure'
 resp=defaultdict(int)
 for f,t,src in base['D']:
  assert not F[f] and v<=t<2*v
  for q in src:resp[q]^=1<<(t-v)
 first={q:None for q in range(2*v,n)}
 for ph in ('D','A','B','C'):
  for f,d,src in base[ph]:
   if F[f]:
    for q in [d]+src:
     if q in first and first[q] is None:first[q]=F[f]
 for q in first:
  if first[q] is None:first[q]=F[base['final'][q]]
 piv={};donors={};bydon=defaultdict(list);rank=0
 for ef,p,ds in s['entries']:
  E=set(ef);assert E and E in F and len(ds)==len(set(ds));assert 2*v<=p<n and p not in piv and p not in donors and p not in base['ret']
  z=resp[p]
  for d in ds:
   assert 2*v<=d<n and d not in piv and d not in base['ret'];assert donors.setdefault(d,E)==E;bydon[d,tuple(ef)].append(p);z^=resp[d]
  assert z==0,('response relation',p)
  assert all(E<=first[q] for q in [p]+ds),('first frame',p)
  piv[p]=E;rank+=len(basis(lines[i] for i in E))
 assert not (set(piv)&set(donors));assert rank==s['total_entrance_rank'] and rank%8==0
 assert len(piv)==s['entries_count'];assert len(bydon)==s['donor_slots']
 # Reconstruct exactly using our own indices and sorted grouping.
 r=copy.deepcopy(base)
 for p,E in piv.items():r['start'][p]=next(i for i,f in enumerate(F) if f==E)
 r['D']=[[f,t,[q for q in src if q not in piv]] for f,t,src in base['D']]
 pre=[[next(i for i,f in enumerate(F) if f==set(E)),d,sorted(ps)] for (d,E),ps in sorted(bydon.items(),key=lambda kv:(kv[0][0],sum(1<<i for i in kv[0][1])))]
 post=[[next(i for i,f in enumerate(F) if f==full),d,sorted(ps)] for (d,E),ps in sorted(bydon.items(),key=lambda kv:(kv[0][0],sum(1<<i for i in kv[0][1])))]
 r['A']=pre+base['A'];r['C']=base['C']+post
 assert sha(r)==s['output_sha256'],'independent kernel reconstruction differs'
 retiming_changes=0
 if retime_path is not None:
  rs=json.loads(retime_path.read_bytes());assert rs['input_sha256']==sha(r)
  primitive=copy.deepcopy(r)
  for ph in ('D','A','B','C'):primitive[ph]=[[f,d,[src]] for f,d,ss in r[ph] for src in ss]
  expanded_input_sha=sha(primitive)
  assert expanded_input_sha=='cb2afa377baeb8578e867ecda0f81caa68b2dac9cca805f41247754cfe91deb5'
  if 'primitive_input_sha256' in rs:assert rs['primitive_input_sha256']==expanded_input_sha
  for ph in ('D','A','B','C'):
   assert [(d,src) for f,d,ss in primitive[ph] for src in ss]==[(d,src) for f,d,ss in w[ph] for src in ss],'primitive scalar sequence changed'
   assert all(len(ss)==1 for f,d,ss in w[ph])
  done=set()
  for ph,k,old,new in rs['gates']:
   assert ph in ('A','B') and (ph,k) not in done;done.add((ph,k));f,d,ss=primitive[ph][k]
   assert primitive['frames'][f]==old and set(old)!=set(new)
   nf=next(i for i,fr in enumerate(primitive['frames']) if fr==new);primitive[ph][k]=[nf,d,ss]
  assert primitive==w and sha(w)==rs['output_sha256'];retiming_changes=len(done)
 else:assert r==w,'independent reconstruction differs'

 # Independent scalar expansion and forward chronology.
 cur=w['start'][:];ev=[];hist=Counter();coeff=[{i:1} if i<v else {} for i in range(n)];spanchecks=0
 for phase in ('D','A','scatter','B','C'):
  if phase=='scatter':
   for k,q in enumerate(w['ret']):
    assert dims[cur[q]]==8
    ev.append(('copy',q));hist[8]+=1
    for t,sc in enumerate(w['scatter']):
     for kk in sc:
      if kk==k:ev.append(('add',v+t,n))
    ev.append(('erase',q))
   continue
  for f,d,src in w[phase]:
   assert d not in src and len(set(src))==len(src)
   for q in [d]+src:
    if cur[q]!=f:
     assert F[cur[q]]<=F[f];delta=dims[f]-dims[cur[q]];assert delta>=0
     ev.append(('move',q,cur[q],f,delta));hist[delta]+=bool(delta);cur[q]=f
   for q in src:
    if q<v or q>=2*v:assert set(coeff[q])<=F[f];spanchecks+=1
    for x,c in coeff[q].items():coeff[d][x]=coeff[d].get(x,0)+c
    ev.append(('add',d,q))
   if d<v or d>=2*v:assert set(coeff[d])<=F[f];spanchecks+=1
 for q,f in enumerate(w['final']):
  if cur[q]!=f:
   assert F[cur[q]]<=F[f];delta=dims[f]-dims[cur[q]];assert delta>=0
   ev.append(('move',q,cur[q],f,delta));hist[delta]+=bool(delta);cur[q]=f
 hist.pop(0,None)
 assert cur==w['final']
 def scalar(events,rev=False,omit=None):
  vals=[1<<q for q in range(n)]+[0];current=(w['final'] if rev else w['start'])[:];hs=Counter();copies=0
  for idx,e in enumerate(reversed(events) if rev else events):
   if omit is not None and omit(e,idx):continue
   if e[0]=='move':
    _,q,a,b,d=e
    if rev:a,b=b,a
    assert current[q]==a;delta=(h-dims[b])-(h-dims[a]) if rev else dims[b]-dims[a]
    assert delta==d and delta>=0;current[q]=b
    if d:hs[d]+=1
   elif e[0]=='add':vals[e[1]]^=vals[e[2]]
   elif e[0]==('erase' if rev else 'copy'):
    assert vals[n]==0;vals[n]=vals[e[1]];hs[8]+=1;copies+=1
   else:
    assert e[0]==('copy' if rev else 'erase') and vals[n]==vals[e[1]];vals[n]=0
  assert current==(w['start'] if rev else w['final']);assert copies==len(w['ret'])
  assert all(vals[q]==((1<<q)^((1<<(q-v)) if v<=q<2*v else 0)) for q in range(n)) and vals[n]==0,'scalar/dirty failure'
  assert hs==hist
  return dict(all_columns=n,dirty_columns=w['R'],copies=copies,paid_profile=dict(sorted(hs.items())))
 forward=scalar(ev);reverse=scalar(ev,True)
 # Negative controls must break the actual scalar computation.
 controls=[]
 first_event=next(i for i,e in enumerate(ev) if e==('add',pre[0][1],pre[0][2][0]))
 last_event=max(i for i,e in enumerate(ev) if e==('add',post[-1][1],post[-1][2][0]))
 for name,pred in [('omitted_first_basis',lambda e,i:i==first_event),('omitted_final_basis',lambda e,i:i==last_event)]:
  try:scalar(ev,omit=pred)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 for name,entries in [('missing_donor',copy.deepcopy(s['entries']))]:
  E,p,ds=entries[0];z=resp[p]
  for d in ds[1:]:z^=resp[d]
  assert z!=0;controls.append(name)
 result=dict(retiming_changes=retiming_changes,status='PASS_INDEPENDENT_R740_KERNEL_AND_RETIMING' if retiming_changes else 'PASS_INDEPENDENT_R740_KERNEL',source_sha256=sha(base),candidate_sha256=sha(w),entries=len(piv),donor_slots=len(bydon),total_entrance_rank=rank,root_closed_frames=len(F),source_span_checks=spanchecks,forward=forward,reflected=reverse,negative_controls=controls,events=len(ev),scope='Independent reconstruction, every F2 scalar column and dirty restoration, exact source span/first-frame relations and both complementary dimension ledgers; global banking and pricing audited separately.')
 return dict(w=w,ev=ev,hist=hist,dims=dims,sha=sha,receipt=result)

P=Path(sys.argv[1]);O=Path(sys.argv[2]);out=Path(sys.argv[3])
retime_path=next((p for p in (P/'stages/retime-selection.json',P/'stages/retiming-selection.json') if p.exists()),None)
a=audit_local(P/'vendor/pr436/data/bit/bitE8-r740.json.gz',O/'bit426-source-centres/bit-source-centres.json',P/'stages/kernel-selection.json',retime_path)
local_receipt=a['receipt']
w,ev,localH,dims=a['w'],a['ev'],a['hist'],a['dims'];R=w['R'];N=240+R;D=O/'bit426-source-centres/global'
read=lambda p:json.loads(p.read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
g=read(D/'GLOBAL.json');geo=read(D/'GEOMETRY.json');result=read(O/'RESULT.json');blob=gzip.decompress((D/'GLOBAL-TEMPLATE.json.gz').read_bytes());t=json.loads(blob)
assert g['word_sha256']==a['sha'](w) and sha(blob)==g['template_sha256']==result['bit_template_sha256']
assert t['geometry_sha256']==sha((D/'GEOMETRY.json').read_bytes())
assert t['source_record_sha256']==sha((O/'bit426-source-centres/records/249-records.bin').read_bytes())
# Compare both emitted scalar streams with the independently expanded source word.
def normalize(prog):
 out=[]
 for e in prog:
  if e[0]==0:out.append(('move',e[1],e[2],e[3],e[4]))
  elif e[0]==1:assert abs(e[3])==1;out.append(('add',e[1],e[2]))
  elif e[0]==2:assert e[5]==8;out.append(('copy',e[1]))
  else:out.append(('erase',e[1]))
 return out
assert normalize(t['local_programs']['forward'])==ev
rev=[]
for e in reversed(ev):
 if e[0]=='move':rev.append(('move',e[1],e[3],e[2],e[4]))
 elif e[0]=='copy':rev.append(('erase',e[1]))
 elif e[0]=='erase':rev.append(('copy',e[1]))
 else:rev.append(e)
assert normalize(t['local_programs']['reverse'])==rev
width=[8-dims[f] for f in w['start'][240:]];ENT=sum(8-x for x in width);NB=R-ENT//8;W=7680+9*NB
assert ENT%8==0 and (NB,W)==(723,14187)
assert (t['live'],t['banks_per_stage'],t['private_centre_reserve'],t['replicas'],t['stages'],t['entrance_rank_total'])==(W,NB,9,8,9,ENT)
assert g['physical']==W+9 and t['bank_padding'] is None
# Explicit isometries from E-perp to coordinate blocks, checked independently.
def validate_routes(routes):
 byframe={}
 for r in routes:
  f=r['frame'];rank=r['entrance_rank'];matrix=r['orthogonal_rows_numerator']
  assert f not in byframe and rank==dims[f] and r['denominator']==2
  indices=r['entrance_basis']+r['residual_basis'];assert len(indices)==8 and len(r['entrance_basis'])==rank
  assert matrix==[w['lines'][i] for i in indices] and len(matrix)==8 and all(len(row)==8 for row in matrix)
  assert all(type(x) is int and x%2==0 for row in matrix for x in row)
  dot=lambda u,v:sum(x*y for x,y in zip(u,v))
  assert all(dot(u,v)==4*int(i==j) for i,u in enumerate(matrix) for j,v in enumerate(matrix))
  assert all(sum(dot(w['lines'][i],row)**2 for row in matrix[:rank])==4*dot(w['lines'][i],w['lines'][i]) for i in w['frames'][f])
  reduced=[[Q(x,2) for x in row] for row in matrix];ops=r['gaussian_reduction'];assert len(ops)<=7
  for op,i,j,c in ops:
   assert op=='swap' and c is None and i in range(8) and j in range(8);reduced[i],reduced[j]=reduced[j],reduced[i]
  assert reduced==[[int(i==j) for j in range(8)] for i in range(8)];byframe[f]=r
 assert set(byframe)==set(w['start'][240:])
 return byframe
isometries=validate_routes(t['residual_isometries']);route_controls=[]
for name in ('altered_basis','missing_factor','wrong_frame'):
 damaged=copy.deepcopy(t['residual_isometries'])
 if name=='altered_basis':damaged[0]['orthogonal_rows_numerator'][0][0]+=1
 elif name=='missing_factor':next(r for r in damaged if r['gaussian_reduction'])['gaussian_reduction'].pop()
 else:damaged[0]['frame']=damaged[1]['frame']
 try:validate_routes(damaged)
 except AssertionError:route_controls.append(name)
 else:raise AssertionError(name)
occ=defaultdict(int);seen=set();paid=Counter();events=0;assign=0;expanded=hashlib.sha256()
for call in t['calls']:
 st,rep,p,ori=call['stage'],call['replica'],call['pair'],call['orientation'];rv=ori=='reverse'
 assert st in range(9) and rep in range(8) and (st,rep) not in seen;seen.add((st,rep));assert p==max(0,(st-1)//2) and rv==(st in (1,3,5,7))
 owners=call['owners'];assert len(owners)==N
 for q,(family,route) in enumerate(owners):
  if q<240:
   side=q//120
   if rv:side=1-side
   assert family==rep*960+(2*p+side)*120+q%120 and route==['data',st,q%120]
  else:
   assert len(route)==4 and route[3]==w['start'][q] and route[3] in isometries and route[0]=='bank' and route[2]==width[q-240] and 7680+st*NB<=family<7680+(st+1)*NB
   bits=((1<<route[2])-1)<<route[1];assert 0<=route[1] and bits<1<<64 and not(occ[family]&bits);occ[family]|=bits;assign+=1
 for e in t['local_programs'][ori]:
  events+=1
  if e[0]==0:
   if e[4]:paid[e[4]]+=1
   mapped=[0,owners[e[1]],*e[2:]]
  else:
   mapped=[e[0],owners[e[1]],owners[e[2]] if e[2]<N else [W,['private',0]],*e[3:]]
   if e[0]==2:paid[e[5]]+=1
  expanded.update((json.dumps(mapped,separators=(',',':'))+'\n').encode())
assert seen=={(s,r) for s in range(9) for r in range(8)} and len(occ)==9*NB and all(z==(1<<64)-1 for z in occ.values())
assert events==g['emitted_events']==72*len(ev) and expanded.hexdigest()==g['emitted_program_sha256'];assert assign==g['bank_assignments']==72*R
# Every unbanked global basis column from the independently expanded source events.
GN=960+9*R;values=[1<<q for q in range(GN)]+[0];global_stages=[]
for schedule_event in t['schedule']:
 kind=schedule_event['kind']
 if kind=='local_cover_sweep':
  st,p,rv=schedule_event['stage'],schedule_event['pair'],schedule_event['reverse'];before=values[:]
  def owner(q):
   if q==N:return GN
   if q<240:
    side=q//120
    if rv:side=1-side
    return (2*p+side)*120+q%120
   return 960+st*R+q-240
  for e in (rev if rv else ev):
   if e[0]=='add':values[owner(e[1])]^=values[owner(e[2])]
   elif e[0]=='copy':assert values[GN]==0;values[GN]=values[owner(e[1])]
   elif e[0]=='erase':assert values[GN]==values[owner(e[1])];values[GN]=0
  source,destination=(2*p+int(rv))*120,(2*p+int(not rv))*120
  for q in range(120):before[destination+q]^=before[source+q]
  assert values==before;global_stages.append(st)
 elif kind=='bridge':
  d,src=schedule_event['dst'],schedule_event['src']
  for q in range(120):values[2*d*120+q]^=values[2*src*120+q];values[(2*src+1)*120+q]^=values[(2*d+1)*120+q]
 elif kind=='exchange':
  for p in range(4):
   for q in range(120):x,y=2*p*120+q,(2*p+1)*120+q;values[x],values[y]=values[y],values[x]
assert values==[1<<q for q in range(GN)]+[0] and global_stages==list(range(9))
# Exact signed scalar 8-block assembly and its 18 bridge omission controls.
def small(skip=-1):
 z=[[int(i==j) for j in range(8)] for i in range(8)];level=[-1]*4;stages=[];bridge=0;exchange=0
 def add(d,s,coef):z[d]=[x+coef*y for x,y in zip(z[d],z[s])]
 for e in t['schedule']:
  kind=e['kind']
  if kind=='local_cover_sweep':
   st,p,rv=e['stage'],e['pair'],e['reverse'];assert level[p]==st-1;level[p]=st;stages.append(st)
   add(2*p,2*p+1,-1) if rv else add(2*p+1,2*p,1)
  elif kind=='idle':
   p,u,d,r=e['pair'],e['source_level'],e['target_level'],e['rank'];assert level[p]==u and u<=d<=8 and r==7*(d-u);level[p]=d
  elif kind=='bridge':
   d,s,c=e['dst'],e['src'],e['coefficient'];assert level[d]==level[s] and abs(c)==1
   for x,y,coef in [(2*d,2*s,c),(2*s+1,2*d+1,-c)]:
    if bridge!=skip:add(x,y,coef)
    bridge+=1
  else:
   assert kind=='exchange' and level==[8]*4 and exchange==0;exchange+=1
   for p in range(4):z[2*p],z[2*p+1]=z[2*p+1],[-x for x in z[2*p]]
 assert stages==list(range(9)) and bridge==18 and exchange==1
 return z
identity=[[int(i==j) for j in range(8)] for i in range(8)];assert small()==identity
assert all(small(i)!=identity for i in range(18))
for e in t['schedule']:
 if e['kind']=='idle' and e['rank']:paid[e['rank']]+=1920
assert dict(sorted(paid.items()))=={int(k):v for k,v in g['profile'].items()};E=sum(paid.values());mass=sum(r*c for r,c in paid.items());assert 64*W-mass==2496
# Derive scalar norm guards from actual source events, not stored summary counts.
def norm(events):
 z=[1]*N+[0];mx=1
 for e in events:
  if e[0]=='add':z[e[1]]+=z[e[2]];mx=max(mx,z[e[1]])
  elif e[0]=='copy':z[N]=z[e[1]]
  elif e[0]=='erase':z[N]=0
 return mx
cf,cb=norm(ev),norm(rev);prefix=2**18*cf**5*cb**4
assert cf==g['local_checks']['forward']['cancellation_free_row_l1'] and cb==g['local_checks']['reverse']['cancellation_free_row_l1']
assert prefix==int(g['global_prefix_bound']) and prefix<2**128
localadds=sum(e[0]=='add' for e in ev);copies=sum(e[0]=='copy' for e in ev)
assert localadds==g['local_additions'] and copies==9 and g['bridge_additions']==18*120*8 and g['copy_erase_episodes']==72*copies
J=8*8*9*N+8*7680+2*assign+2*72*copies
selectors=2*9*8*((W-1)+R*64*(geo['max_route_factors']+144+63+64))
coefficient=72*localadds+18*120*8+J*(16*(4097)**2)+J*(W+9)+E*((8*64*64+8)+128*128**3)+16*64**3+72*copies+selectors+prefix+1
two=(coefficient+1)**2*(E+1)**2;assert two<2**512 and 2*max(paid)**2<64**2
invoice=dict(prefix_bits=prefix.bit_length(),charged_prefix_bits=128,coefficient_bits=coefficient.bit_length(),two_level_coefficient_bits=two.bit_length(),charged_two_level_coefficient_bits=512,row_coefficient=18355,live=W,physical=W+9)
invoice.update(extra_helper_route_factor_bound=144,selector_charge=selectors,full_counted_coefficient=str(coefficient),two_level_coefficient=str(two))
assert invoice==result['bit_invoice'];assert geo['bad_prime_factors']==[2] and geo['route_denominators']==[1,2,4]
# Third rational moment enclosure: range-reduced atanh series + positive exponential series.
GRID=10**70
from functools import lru_cache
@lru_cache(None)
def log_bounds(x):
 k=0
 while x>2:x/=2;k+=1
 def unit(y):
  z=(y-1)/(y+1);s=Q(0);power=z
  for j in range(100):s+=2*power/(2*j+1);power*=z*z
  return s,s+2*power/(201*(1-z*z))
 l,u=unit(x);l2,u2=unit(Q(2));return Q(((l+k*l2)*GRID).__floor__(),GRID),Q(((u+k*u2)*GRID).__ceil__(),GRID)
def expo(x):
 assert 0<=x<1;t=s=Q(1)
 for j in range(1,25):t*=x/j;s+=t
 return s,s+t*x/25/(1-x/26)
def moment(c):
 lo=hi=Q(0)
 for r,count in list(paid.items())+[(1,Q(32*64*64*E,10**16))]:
  l,u=log_bounds(Q(64,r));a,b=expo(c*l)[0],expo(c*u)[1];lo+=Q(r*count,64*W)*a;hi+=Q(r*count,64*W)*b
 return lo,hi
c=Q(result['bit_lower']);l,u=moment(c);assert u<1
lup,uup=moment(c+Q(1,10**24));assert lup>1
# Recompute finite bootstrap and every exact outer inequality without pricing imports.
b=Q(result['complex_lower']);eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);chain=[Q(384599,10**10)];cuts=[]
for _ in range(6):
 old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
 ceil=lambda x:-((-x.numerator)//x.denominator)
 cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap));assert cut*gap**2>=36 and cut*gap>=1032;cuts.append({'gap':str(gap),'cutoff_log2':str(cut)});chain.append(a)
assert cuts==result['bootstrap'];a=chain[-1];q=a*(1-2*eta);tau,sigma=1-a,1-b;lp=1-q;lam=(tau+lp)/2;cc=q+eta/4;eps=(1-eta)/(1+q);minimum=eps*q;rr=(minimum+1-eps)/2;delta=eta/8;internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
margin={'balanced_prefix':1-eps,'coordinate_movement':a,'compact_phase_layer':minimum,'bulk_exposure':a,'Gaussian_arithmetic':min(1-eps-delta,rr-delta),'scalar_work':1-eps-delta,'dimension':eps}
k=Q(((minimum*10**18).numerator-1)//(minimum*10**18).denominator,10**18);assert k==Q(result['kappa']) and k<minimum<=k+Q(1,10**18)
slack=dict(bit_positive=a,complex_above_bit=b-a,complex_below_one_over32=Q(1,32)-b,beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-a,q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=cc,c_below_one=1-cc,q_below_reservations=cc-q,lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-cc),lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,K_geometry=1-eps*(1+cc),K_dominates_log=eps*cc,record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=rr-delta,gamma_sublinear=1-eps-rr,cell_above_band=eps-(1-rr)/2,prime_interval_packing=1-eps,alpha_positive=rr,alpha_below_one=1-rr,alpha_below_one_fourth=Q(1,4)-rr,delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,small_field_exposure=1-eps-minimum,artificial_boundary=8-eps+rr-delta-minimum,literal_scalar_guard=Q(1),row_product_gap=Q(10**6)-Q(51*20161,25))
slack.update({name+'_above_kappa':value-k for name,value in margin.items()});assert len(slack)==47 and min(slack.values())>0
assert {name:str(value) for name,value in slack.items()}==result['strict_outer_constraints']
r=dict(local_audit=local_receipt,status='PASS_INDEPENDENT_GLOBAL_INVOICE_AND_EXACT_ASSEMBLY',candidate_sha256=g['word_sha256'],global_template_sha256=g['template_sha256'],expanded_program_sha256=expanded.hexdigest(),events=events,global_scalar_columns=GN,global_dirty_columns=9*R,all_global_scalar_columns_restored=True,bank_assignments=assign,bank_families=len(occ),residual_isometries=len(isometries),route_corruption_controls=route_controls,extra_route_factors=144,banks_per_stage=NB,live=W,physical=W+9,paid_profile=dict(sorted(paid.items())),deficit=2496,source_bound_invoice=invoice,independent_moment='third rational enclosure; lower passes, adjacent upper fails',bit_lower=str(c),kappa=str(k),kappa_decimal=result['kappa_decimal'],strict_outer_constraints=len(slack),bridge_omission_controls=18,bootstrap_levels=6)
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Independent bounded PR322/323 witness composition on the fixed paid892 word.
Upstream selections and programs are inert text. No upstream code is executed.
Selections: eumemic (OpenAI Codex assistance); retiming mechanism inherited from
Rohan Arun/PR287 (Anthropic Claude assistance). This checker is independently
prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd,lcm
import json,gzip,hashlib,copy
if not __debug__:raise RuntimeError('Assertions required')
P=packet.EXPERIMENT;BASE=packet.BASE_FRAME;PAID=packet.BASE_BANK
AD=packet.BASE_CODE/"admission";SOURCE=packet.BASE_INPUTS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def dump(n,v):(P/n).write_text(json.dumps(packet.portable(v),indent=2)+'\n')
base=read(BASE/'RESULT.json');assert base['candidate_sha256']=='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
for n,h in base['artifacts'].items():assert sha(BASE/n)==h
E=read(BASE/'local-events.json.gz');F={int(k):{'rank':v['rank'],'basis':[[Q(x)for x in row]for row in v['basis']],'annihilator':[[Q(x)for x in row]for row in v['annihilator']],'key':v['key']}for k,v in read(BASE/'local-frames.json.gz').items()}
end=read(BASE/'local-endpoints.json');initial={int(k):v for k,v in end['initial'].items()};final={int(k):v for k,v in end['final'].items()};n=end['n'];assert n==10141
removed=end['removed_sink_columns'];compact=lambda a:a-sum(x<a for x in removed)
witness322=read(packet.INPUTS/'pr322-presink-selection.json');witness323=read(packet.INPUTS/'pr323-kernel2-selection.json')
ZERO=next(k for k,v in F.items()if v['rank']==0);FULL=next(k for k,v in F.items()if v['rank']==20)
def rref(rows,cols=20):
 a=[list(map(Q,row))for row in rows];piv=[];z=0
 for j in range(cols):
  t=next((t for t in range(z,len(a))if a[t][j]),None)
  if t is None:continue
  a[z],a[t]=a[t],a[z];c=a[z][j];a[z]=[x/c for x in a[z]]
  for i in range(len(a)):
   if i!=z and a[i][j]:c=a[i][j];a[i]=[x-c*y for x,y in zip(a[i],a[z])]
  piv.append(j);z+=1
  if z==len(a):break
 return a,piv
def null(rows):
 a,ps=rref(rows);out=[]
 for j in range(20):
  if j in ps:continue
  v=[Q(int(i==j))for i in range(20)]
  for i,k in enumerate(ps):v[k]=-a[i][j]
  den=lcm(*(x.denominator for x in v));u=[int(x*den)for x in v];g=gcd(*u);out.append([x//g for x in u])
 return out
def determinant(A):
 a=[list(map(Q,row))for row in A];d=Q(1)
 for j in range(len(a)):
  k=next((k for k in range(j,len(a))if a[k][j]),None)
  if k is None:return Q(0)
  if k!=j:a[k],a[j]=a[j],a[k];d=-d
  v=a[j][j];d*=v
  for k in range(j+1,len(a)):
   u=a[k][j]/v
   for t in range(j+1,len(a)):a[k][t]-=u*a[j][t]
 return d
newframes=[]
def install(basis,label):
 assert len(rref(basis)[1])==len(basis);ann=null(basis);gram=[[9*sum(a*b for a,b in zip(x,y))-sum(x)*sum(y)for y in basis]for x in basis];det=determinant(gram);assert det and det.denominator==1 and abs(det)<2**80
 k=max(F)+1;F[k]={'rank':len(basis),'basis':[list(map(Q,row))for row in basis],'annihilator':list(map(lambda row:list(map(Q,row)),ann)),'key':[label,len(newframes)]};newframes.append({'frame':k,'label':label,'rank':len(basis),'gram_9I_minusJ_determinant':str(det),'eligible_prime_bound_preserved':True});return k
@lru_cache(None)
def sub(a,b):
 if a==b:return True
 return F[a]['rank']<=F[b]['rank'] and all(sum(x*y for x,y in zip(u,v))==0 for u in F[b]['annihilator']for v in F[a]['basis'])
def histogram(events,starts=initial,verify_roles=()):
 needs=defaultdict(list);copies=Counter()
 for i,e in enumerate(events):
  if e['op']==1:
   needs[e['a']].append((i,e['frame']))
   if e['b']!=n:needs[e['b']].append((i,e['frame']))
  elif e['op']==2:needs[e['a']].append((i,e['frame']));copies[F[e['frame']]['rank']]+=1
 H=Counter(copies);receipts=[]
 for s,f in starts.items():
  fs=[(-1,f)]+needs[s]+[(len(events),final[s])];rs=[]
  for (i,a),(j,b)in zip(fs,fs[1:]):
   gap=F[b]['rank']-F[a]['rank'];assert gap>=0
   if s in verify_roles:
    assert sub(a,b),('nonnested exact role path',s,i,j,a,b,F[a]['rank'],F[b]['rank'])
    # Same exact inclusion proves the reflected annihilator path.
    assert len(F[a]['annihilator'])-len(F[b]['annihilator'])==gap
   if gap:H[gap]+=1;rs.append(gap)
  if s in verify_roles:receipts.append({'role':s,'initial_rank':F[f]['rank'],'final_rank':F[final[s]]['rank'],'positive_gaps':rs,'actual_path_entries':len(fs),'exact_forward_and_reflected_containment':True})
 return H,receipts
baseH,_=histogram(E);assert dict(baseH)=={int(k):v for k,v in base['one_stage_paid_histogram'].items()}
# Resolve the four selected operations by content and actual old basis hash,
# not by stale upstream raw offsets. Keep our already admitted133reorders.
retimed=copy.deepcopy(E);retiming=[];retime_roles=set()
for entry in witness322['entries']:
 a,b,c,_=entry['scalar'];a,b=compact(a),compact(b)
 matches=[i for i,e in enumerate(E)if e['op']==1 and[e['a'],e['b'],e['c']]==[a,b,c]and e['semantic'][0]=='kernel_setup'];assert len(matches)==1
 i=matches[0];old=E[i]['frame'];assert F[old]['rank']==entry['old_dimension']
 oldbasis=[[int(x)if x.denominator==1 else str(x)for x in row]for row in F[old]['basis']]
 assert hashlib.sha256(json.dumps(oldbasis,separators=(',',':')).encode()).hexdigest()==entry['old_basis_sha256']
 f=install(entry['new_basis'],'PR322-retime');assert F[f]['rank']==entry['new_dimension'];retimed[i]['frame']=f;retime_roles.update([a,b]);retiming.append({'upstream_record':entry['record'],'actual_event':i,'compact_ports':[a,b],'original_ports':entry['scalar'][:2],'old_frame':old,'new_frame':f,'old_rank':F[old]['rank'],'new_rank':F[f]['rank'],'scalar_semantic':E[i]['semantic']})
retimeH,retimepaths=histogram(retimed,verify_roles=retime_roles);delta=Counter(retimeH);delta.subtract(baseH);delta={r:k for r,k in delta.items()if k}
assert delta=={int(k):v for k,v in witness322['expected_local_histogram_delta'].items()}
print('PR322 exact live path retiming passes',delta,flush=True)
# Newly installed rank-two kernels are keyed in compact live namespaces.
families=copy.deepcopy(witness323['families']);members={x for e in families for x in [e['pivot']]+e['donors']};assert len(members)==12
assert not members&retime_roles
for e in families:
 for s in [e['pivot']]+e['donors']:assert initial[s]==ZERO and final[s]==FULL
 e['frame']=install(e['basis'],'PR323-kernel2')
last={};first={};reads=Counter()
for i,e in enumerate(retimed):
 if e['op']==1:
  a,b,c=e['a'],e['b'],e['c']
  if b in members and e['frame']==ZERO and e['semantic'][0]=='plain'and 960<=a<1920:last[b]=i;reads[b]+=1;continue
  for s in [a,b]:
   if s in members:first.setdefault(s,(i,e['frame']))
 elif e['op']==2 and e['a']in members:first.setdefault(e['a'],(i,e['frame']))
bycut=defaultdict(list);pivots={e['pivot']:e for e in families}
for e in families:
 ms=[e['pivot']]+e['donors'];cut=max(last[s]for s in ms);row=retimed[cut]
 assert [row['a'],row['b'],row['c']]==e['cut_read']
 assert cut<min(first[s][0]for s in ms)
 assert all(sub(e['frame'],first[s][1])for s in ms)
 e.update(cut=cut,removed_reads=reads[e['pivot']],first_frames={str(s):first[s][1]for s in ms});bycut[cut].append(e)
# Independent 12-column prefix calculation over F2, including all targets.
bit={s:1<<i for i,s in enumerate(sorted(members))};cols=[bit.get(i,0)for i in range(n+1)];temp=None
for row in retimed[:max(bycut)+1]:
 op,a,b,c=row['op'],row['a'],row['b'],row['c']
 if op==1:
  if c%2:cols[a]^=cols[b]
 elif op==2:assert temp is None;temp=a;cols[b]=cols[a]
 else:assert temp==a;temp=None
assert temp is None
assert all(cols[i]==bit.get(i,0)for i in range(n)if not 960<=i<1920)
for e in families:
 targets=[]
 for t in range(960):
  x=bool(cols[960+t]&bit[e['pivot']]);y=False
  for d in e['donors']:y^=bool(cols[960+t]&bit[d])
  assert x==y
  if x:targets.append(t)
 assert targets;e['prefix_response_targets']=targets
print('PR323 exact cuts and2880prefix relations pass',flush=True)
starts=dict(initial);starts.update({e['pivot']:e['frame']for e in families});combined=[];deleted=[]
for i,row in enumerate(retimed):
 if row['op']==1 and row['b']in pivots and row['frame']==ZERO and row['semantic'][0]=='plain':
  assert i<=pivots[row['b']]['cut'];deleted.append(i)
 else:combined.append(copy.deepcopy(row))
 if i in bycut:
  for e in bycut[i]:
   for d in e['donors']:combined.append({'op':1,'a':d,'b':e['pivot'],'c':1,'frame':e['frame'],'semantic':['new_kernel2_setup',e['pivot'],d]})
for e in families:
 for d in e['donors']:combined.append({'op':1,'a':d,'b':e['pivot'],'c':-1,'frame':FULL,'semantic':['new_kernel2_restore',e['pivot'],d]})
assert len(deleted)==sum(e['removed_reads']for e in families)==32
combinedH,combinedpaths=histogram(combined,starts,retime_roles|members);kd=Counter(combinedH);kd.subtract(retimeH);kd={r:v for r,v in kd.items()if v};assert kd=={int(k):v for k,v in witness323['expected_local_delta'].items()}
# Targeted source-span calculation on the actual combined signed word.
graph=read(packet.BASE_INPUTS/'bitword/selected/bit/graph_p10.json');sourcecols=[{s:1}if s<960 else{}for s in range(n+1)];span_receipts=[]
for i,e in enumerate(combined):
 op,a,b,c=e['op'],e['a'],e['b'],e['c']
 if op==2:sourcecols[b]=dict(sourcecols[a]);continue
 if op==3:continue
 if not 960<=a<1920:
  assert not 960<=b<1920
  for q,val in sourcecols[b].items():
   z=sourcecols[a].get(q,0)+c*val
   if z:sourcecols[a][q]=z
   else:sourcecols[a].pop(q,None)
 if e['frame']in {x['frame']for x in newframes}:
  need=set()
  if not 960<=a<1920:need.update(sourcecols[a])
  if b!=n and not 960<=b<1920:need.update(sourcecols[b])
  assert all(sum(row[j]for j in graph['labels'][q])==0 for q in need for row in F[e['frame']]['annihilator'])
  span_receipts.append({'event':i,'semantic':e['semantic'],'frame':e['frame'],'source_support':sorted(need)})
assert len(span_receipts)==13
# Complete arbitrary-dirty scalar/COPY replay on every live formal column.
def scalar_replay(events,reverse=False,omit=None):
 columns=[1<<i for i in range(n+1)];norm=[1]*(n+1);temp=None;hist=Counter();digest=hashlib.sha256()
 for e in reversed(events)if reverse else events:
  op,a,b,c=e['op'],e['a'],e['b'],e['c']
  if op==1:
   if e['semantic'][0]==omit:continue
   assert a!=b and c%2;columns[a]^=columns[b];norm[a]+=abs(c)*norm[b];hist[abs(c)]+=1
   digest.update((json.dumps([a,temp if b==n else b,-c if reverse else c],separators=(',',':'))+'\n').encode())
  elif op==(3 if reverse else 2):assert temp is None;temp=a;columns[b]=columns[a];norm[b]=norm[a]
  else:assert temp==a and columns[b]==columns[a];temp=None
 assert temp is None
 wrong=[i for i in range(n)if columns[i]!=((1<<i)^((1<<(i-960))if 960<=i<1920 else 0))]
 if omit:assert wrong
 else:assert not wrong
 return {'reverse':reverse,'columns':n,'wrong_rows':len(wrong),'weighted_additions':sum(hist.values()),'unit_additions':sum(r*k for r,k in hist.items()),'coefficient_histogram':dict(hist),'max_norm':max(norm),'event_sha256':digest.hexdigest()}
forward=scalar_replay(combined);inverse=scalar_replay(combined,True);controls=[scalar_replay(combined,omit='new_kernel2_setup'),scalar_replay(combined,omit='new_kernel2_restore')]
assert forward['weighted_additions']==336239 and forward['unit_additions']==338159
print('Both complete scalar directions and both omission controls pass',flush=True)
payload=64*forward['max_norm']**3*inverse['max_norm']**2;assert payload<2**104
# Directly derive complete literal histogram; packing/paid completion is a
# separate explicit finite construction below. No upstream300replica claim used.
oldpaid=read(PAID/'RESULT.json');regular=Counter({r:300*v for r,v in combinedH.items()});regular.update({r:60*1920 for r in [4,19,38,42]})
# Existing partial40 bank plus freed10width4 blocks becomes80 real coordinates.
proposal=packet.base_packing();patterns=copy.deepcopy(proposal['packing_patterns'])
for row in patterns:
 if row['widths']==[18]*4+[20,4,4]:row['count']+=45
 elif row['widths']==[20]*5:row['count']-=45
 elif row['widths']==[4]*25:row['count']-=4
 elif row.get('paid_complement_widths'):row['widths']=[20,20]+[4]*10;row['paid_complement_widths']=[20]
residual=Counter({int(k):v for k,v in proposal['residual_census'].items()});residual[20]-=3;residual[18]+=3
use=Counter()
for row in patterns:
 assert row['count']>0 and sum(row['widths'])+sum(row.get('paid_complement_widths',[]))==100
 for r in row['widths']:use[r]+=row['count']
assert use==Counter({r:60*v for r,v in residual.items()})
banks=sum(r['count']for r in patterns);stock=230400+5*banks;assert banks==85571 and stock==658255
H=regular.copy();H[20]+=5;mass=sum(r*v for r,v in H.items());calls=sum(H.values());assert stock*100-mass==122400
assert mass==65703100 and calls==15006605
out={'status':'PASS_LOCAL_COMPOSITION_AND_EXPLICIT_WIDTH_PACKING_NOT_FULL_ADMISSION','source_word_sha256':base['candidate_sha256'],'base_frame_result_sha256':sha(BASE/'RESULT.json'),'source_heads':{'PR322':'8ce22e5e487e9d1017c26702adc09d5646565d0c','PR323':'e51f5ffee8ab574e5b8249a4612411b2ca5f100d'},'retiming_entries':retiming,'retiming_live_path_checks':retimepaths,'retiming_delta':delta,'new_kernel_entries':families,'new_kernel_delta':kd,'combined_live_path_checks':combinedpaths,'new_frame_gram_witnesses':newframes,'changed_frame_source_supports':span_receipts,'prefix_target_comparisons':2880,'prefix_responses_confined_to_targets_and_own_columns':True,'deleted_initial_reads':32,'added_setup_restore':18,'existing133reorders_kept_as_actual_events':True,'old_endpoints_unchanged_except_three_rank2_entrances':True,'scalar_forward':forward,'scalar_inverse':inverse,'omission_controls':controls,'payload_bound':payload,'payload_bits':payload.bit_length(),'one_stage_histogram':dict(sorted(combinedH.items())),'one_stage_calls':sum(combinedH.values()),'one_stage_mass':sum(r*v for r,v in combinedH.items()),'residual_census':dict(sorted(residual.items())),'packing_patterns':patterns,'banks_per_stage':banks,'literal_stock':stock,'literal_regular_histogram':dict(sorted(regular.items())),'literal_completion_histogram':{20:5},'literal_histogram':dict(sorted(H.items())),'literal_calls':calls,'literal_rank_mass':mass,'literal_deficit':122400,'next_gates':['Exact new rank2 endpoint charts and literal role/replica assignment','Emit and independently bind modified global frame/scalar word, routes and stage completion phase','Recompute full finite invoice, prime inventory, fallback moment and47assembly inequalities before claiming an admitted gain'],'checker_sha256':sha(Path(__file__)),'input_hashes':{str(p):sha(p)for p in packet.INPUTS.iterdir()if p.is_file()},'scope':'Concrete newly authored composition on the paid892 live word, not blind reuse of upstream byte hashes or discovery selections; current publication untouched.'}
dump('RESULT.json',out)
for name,data in [('combined-events.json.gz',combined),('combined-frames.json.gz',{str(k):{**v,'basis':[[str(x)for x in row]for row in v['basis']],'annihilator':[[str(x)for x in row]for row in v['annihilator']]}for k,v in F.items()}),('combined-endpoints.json.gz',{'initial':starts,'final':final,'n':n})]:(P/name).write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
print(json.dumps({k:out[k]for k in ['status','retiming_delta','new_kernel_delta','one_stage_calls','one_stage_mass','literal_stock','literal_calls','literal_rank_mass','scalar_forward','scalar_inverse','payload_bits']},indent=2))

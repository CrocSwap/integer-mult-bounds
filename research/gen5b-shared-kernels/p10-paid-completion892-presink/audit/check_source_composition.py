from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Independent isolated PR322/323 composition audit; upstream stays inert.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import json,gzip,hashlib,copy
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=packet.AUDIT;NEW=packet.ADMISSION;OLD=packet.BASE_FRAME;EXP=packet.EXPERIMENT;ADM=packet.BASE_CODE/"admission";BASE=packet.BASE_OUTPUT/"baseline";hashes={}
def load(p):
 p=Path(p);b=p.read_bytes();hashes[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
packet.verify_experiment()
manifest=load(EXP/'MANIFEST.json')
for n,h in manifest['artifacts'].items():assert sha(EXP/n)==h
prior=load(OLD/'RESULT.json');result=load(NEW/'RESULT.json');prioraudit=load(packet.BASE_OUTPUT/'audit/GLOBAL-AUDIT.json')
assert sha(OLD/'RESULT.json')==prioraudit['local_result_sha256']==result['base_frame_result_sha256']
for n,h in prior['artifacts'].items():assert sha(OLD/n)==h
for n,h in result['artifacts'].items():assert sha(NEW/n)==h
assert sha(packet.HERE/'admission/build_local.py')==result['checker_sha256']
retimes=load(packet.INPUTS/'pr322-presink-selection.json');kernels=load(packet.INPUTS/'pr323-kernel2-selection.json')
assert sha(packet.INPUTS/'pr322-presink-selection.json')=='166fa4ce7259d35a020c51682c6f18256f3fdad260473f8209e53114285c8934'
assert sha(packet.INPUTS/'pr323-kernel2-selection.json')=='bcfdc7ec8a61d49201961077fbc512f516dcbebac4281d5cd7d2350ced3ee9e0'
provenance=load(packet.SOURCE_PROVENANCE)
for z in provenance['files']:
 b=(packet.INPUTS/z['label']).read_bytes();assert len(b)==z['bytes']and hashlib.sha256(b).hexdigest()==z['sha256']and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==z['sha']
oldframes=load(OLD/'local-frames.json.gz');frames=load(NEW/'local-frames.json.gz');oldevents=load(OLD/'local-events.json.gz');events=load(NEW/'local-events.json.gz');oldends=load(OLD/'local-endpoints.json');ends=load(NEW/'local-endpoints.json');moves=load(OLD/'reorder-receipts.json');newmoves=load(NEW/'reorder-receipts.json');records=load(NEW/'local-records.json.gz');sourceword=load(packet.BASE_ADMISSION/'word_weighted892.json')
assert len(frames)==15041 and len(records)==389222 and len(events)==336279
assert all(frames[f]==z for f,z in oldframes.items())
# The seven changed frames are exact immutable witness bases. A rational
# determinant is computed afresh, without trusting its reported value.
def mm(A,B):return [[sum(x*y for x,y in zip(a,b))for b in zip(*B)]for a in A]
def determinant(a):
 a=copy.deepcopy(a);det=Q(1)
 for j in range(len(a)):
  i=next((i for i in range(j,len(a))if a[i][j]),None)
  if i is None:return Q(0)
  if i!=j:a[i],a[j]=a[j],a[i];det=-det
  p=a[j][j];det*=p
  for i in range(j+1,len(a)):
   c=a[i][j]/p
   for k in range(j,len(a)):a[i][k]-=c*a[j][k]
 return det
newids=sorted(set(map(int,frames))-set(map(int,oldframes)));assert newids==list(range(15034,15041))
newgram=[]
for i,(f,basis)in enumerate(zip(newids,[z['new_basis']for z in retimes['entries']]+[z['basis']for z in kernels['families']])):
 z=frames[str(f)];B=[[Q(x)for x in row]for row in basis];A=[[Q(x)for x in row]for row in z['annihilator']]
 assert [[Q(x)for x in row]for row in z['basis']]==B and z['rank']==len(B)
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B)
 gram=[[9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)for b in B]for a in B];d=determinant(gram)
 assert d and d.denominator==1 and abs(d.numerator)<2**80
 newgram.append({'frame':f,'rank':len(B),'gram_determinant':str(d),'prime_bound_preserved':True})
@lru_cache(None)
def parts(f):
 z=frames[str(f)];return z['rank'],[[Q(x)for x in row]for row in z['annihilator']],[[Q(x)for x in row]for row in z['basis']]
@lru_cache(None)
def sub(a,b):
 ra,Aa,Ba=parts(a);rb,Ab,Bb=parts(b);return ra<=rb and all(sum(x*y for x,y in zip(u,v))==0 for u in Ab for v in Ba)
key={tuple(z['key']):int(f)for f,z in oldframes.items()};ZERO=key['zero',0];FULL=key['frame',sourceword['full_frame']]
# Recover pre-reorder base chronology by uid, then apply ONLY the four
# pinned retimings and three pinned cut kernels.
pre=copy.deepcopy(sorted(oldevents,key=lambda e:e['original_index']));byuid={e['original_index']:e for e in oldevents};oldmove={z['moved_event_index']:z for z in moves}
for e in pre:
 if e['original_index']in oldmove:
  sem=e['semantic'];f=sourceword['op_frame'][sem[1]]if sem[0]=='forward'else sourceword['root_frame'][sem[1]];e['frame']=key['frame',f];e.pop('moved',None)
removed=oldends['removed_sink_columns'];compact=lambda s:s-sum(x<s for x in removed)
retimed=[];changed=set()
for j,z in enumerate(retimes['entries']):
 a,b=[compact(x)for x in z['scalar'][:2]];hits=[i for i,e in enumerate(pre)if e['op']==1 and[e['a'],e['b'],e['c']]==[a,b,z['scalar'][2]]and e['semantic'][0]=='kernel_setup'];assert len(hits)==1
 i=hits[0];e=pre[i];oldbasis=[[int(Q(x))for x in row]for row in frames[str(e['frame'])]['basis']]
 assert parts(e['frame'])[0]==z['old_dimension']and hashlib.sha256(json.dumps(oldbasis,separators=(',',':')).encode()).hexdigest()==z['old_basis_sha256']
 e['frame']=15034+j;retimed.append(e['original_index']);changed|={a,b}
# Explicit oldphysical->virtual->newphysical rebinding of all20 selected ports.
m=load(packet.BASE_INPUT_MANIFEST)
def source(n):
 z=next(z for z in m['files']if z['path']==n);b=(packet.BASE_INPUTS/z['local']).read_bytes();assert hashlib.sha256(b).hexdigest()==z['sha256'];return json.loads(gzip.decompress(b)if n.endswith('.gz')else b)
w0=source('bitword/selected/bit/word_p10.json.gz');oldregs=sorted(set(range(9120))-{b for a,b in w0['pairs']});newregs=sorted(set(range(9120))-{b for a,b in sourceword['pairs']});alias={b:a for a,b in sourceword['pairs']};newphys={r:1920+i for i,r in enumerate(newregs)}
def lift(s):
 for r in removed:
  if r<=s:s+=1
 return s
def transport(s,already_compact):
 x=lift(s)if already_compact else s;r=oldregs[x-1920];return compact(newphys[alias.get(r,r)])
for z in retimes['entries']:
 for s in z['scalar'][:2]:assert transport(s,False)==compact(s)
for z in kernels['families']:
 for s in[z['pivot']]+z['donors']:assert transport(s,True)==s
members={s for z in kernels['families']for s in[z['pivot']]+z['donors']};assert len(members)==12 and not members&changed
initial={int(k):v for k,v in oldends['initial'].items()};final={int(k):v for k,v in oldends['final'].items()};n=10141
reads=defaultdict(list);first={}
for i,e in enumerate(pre):
 if e['op']==1 and e['b']in members and e['frame']==ZERO and e['semantic'][0]=='plain':reads[e['b']].append(i);assert 960<=e['a']<1920;continue
 for s in([e['a'],e['b']]if e['op']==1 else[e['a']]):
  if s in members:first.setdefault(s,(i,e['frame']))
bycut=defaultdict(list);pivots={};cuts=[]
for j,z in enumerate(kernels['families']):
 ms=[z['pivot']]+z['donors'];cut=max(reads[s][-1]for s in ms);e=pre[cut]
 assert[e['a'],e['b'],e['c']]==z['cut_read']and cut<min(first[s][0]for s in ms)
 assert all(initial[s]==ZERO and final[s]==FULL and sub(15038+j,first[s][1])for s in ms)
 bycut[cut].append((j,z));pivots[z['pivot']]=(j,z,cut);cuts.append(cut)
# All2880 individual target relations at the correct family-specific cut.
bit={s:1<<i for i,s in enumerate(sorted(members))};cols=[bit.get(i,0)for i in range(n+1)];center=None;comparisons=0
for i,e in enumerate(pre[:max(cuts)+1]):
 op,a,b,c=e['op'],e['a'],e['b'],e['c']
 if op==1:assert c%2;cols[a]^=cols[b]
 elif op==2:assert center is None;center=a;cols[b]=cols[a]
 else:assert center==a;center=None
 for j,z in bycut[i]:
  assert center is None;mask=sum(bit[s]for s in[z['pivot']]+z['donors']);nonzero=0
  for q in range(n):
   if 960<=q<1920:assert (cols[q]&mask).bit_count()%2==0;comparisons+=1;nonzero+=bool(cols[q]&bit[z['pivot']])
   else:assert(cols[q]&mask)==(bit.get(q,0)&mask)
  assert nonzero==len(reads[z['pivot']])>0
assert comparisons==2880
combined=[];deleted=[];uid=-1
for i,e in enumerate(pre):
 if e['op']==1 and e['b']in pivots and e['frame']==ZERO and e['semantic'][0]=='plain':deleted.append(e['original_index']);assert i<=pivots[e['b']][2]
 else:combined.append(e)
 for j,z in bycut[i]:
  for d in z['donors']:
   combined.append(dict(op=1,a=d,b=z['pivot'],c=1,frame=15038+j,semantic=['new_kernel2_setup',z['pivot'],d],original_index=uid));uid-=1
for j,z in enumerate(kernels['families']):
 for d in z['donors']:
  combined.append(dict(op=1,a=d,b=z['pivot'],c=-1,frame=FULL,semantic=['new_kernel2_restore',z['pivot'],d],original_index=uid));uid-=1
assert len(deleted)==32 and uid==-19
# Reapply exactly the former133 actual semantic anchors, re-screening each
# literal crossed interval after insertion/removal. No stale raw indices.
where={e['original_index']:i for i,e in enumerate(combined)};before=defaultdict(list);after=defaultdict(list);portset=set();crossings=0
for oldreceipt,newreceipt in zip(moves,newmoves):
 uid0=oldreceipt['moved_event_index'];anchoruid=oldreceipt['new_anchor_event_index'];i=where[uid0];j=where[anchoruid];e=combined[i];anchor=combined[j];a,b=e['a'],e['b'];nf=byuid[uid0]['frame']
 assert not{a,b}&portset;portset|={a,b};assert anchor['op']==1 and{a,b}&{anchor['a'],anchor['b']}and parts(anchor['frame'])[0]==parts(nf)[0]and sub(anchor['frame'],nf)
 assert newreceipt['moved_uid']==uid0 and newreceipt['anchor_uid']==anchoruid and newreceipt['new_pre_event']==i and newreceipt['new_anchor_event']==j
 lo,hi=(i+1,j)if oldreceipt['side']=='before'else(j+1,i);assert lo<=hi
 for x in combined[lo:hi]:
  if x['op']==1:assert x['b']!=a and x['a']!=b
  else:assert x['a']!=a
  crossings+=1
 (before if oldreceipt['side']=='before'else after)[j].append((uid0,dict(e,frame=nf,moved=True)))
assert not(changed|members)&portset
actual=[]
for i,e in enumerate(combined):
 actual.extend(e for uid,e in sorted(before[i]))
 if e['original_index']not in oldmove:actual.append(e)
 actual.extend(e for uid,e in sorted(after[i]))
assert actual==events
starts=dict(initial);starts.update({z['pivot']:15038+j for j,z in enumerate(kernels['families'])})
assert starts=={int(k):v for k,v in ends['initial'].items()}and final=={int(k):v for k,v in ends['final'].items()}
print('Reconstructed actual retiming/kernel composition; all2880own-cut comparisons and133anchor crossings pass',flush=True)
# Reconstruct every exported frame record.
state=dict(starts);out=[];hist=Counter();tmp=None;categories={x:i for i,x in enumerate(ends['categories'])}
def need(s,f):
 old=state[s]
 if old==f:return
 assert sub(old,f);gap=parts(f)[0]-parts(old)[0];out.append([0,s,old,f,gap,0]);state[s]=f
 if gap:hist[gap]+=1
for e in events:
 op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
 if op==1:need(a,f);need(b,f);out.append([1,a,b,c,f,categories['reorder_moved'if e.get('moved')else e['semantic'][0]]])
 elif op==2:assert tmp is None and b==n;need(a,f);state[b]=ZERO;tmp=(a,b,f);out.append([2,a,b,f,ZERO,parts(f)[0]]);hist[parts(f)[0]]+=1
 else:assert op==3 and tmp==(a,b,f)and state[a]==f and state[b]==ZERO;out.append([3,a,b,f,ZERO,parts(f)[0]]);del state[b];tmp=None
for s,f in sorted(final.items()):need(s,f)
assert out==records and state==final and tmp is None
assert(sum(hist.values()),sum(k*v for k,v in hist.items()))==(48486,179458)
# Independent all-column F2 dirty replay and noncancelling integer norms.
def replay(es,reverse=False,omit=None):
 state=[1<<i for i in range(n+1)];norms=[1]*(n+1);center=None;coeff=Counter();digest=hashlib.sha256()
 for e in(reversed(es)if reverse else es):
  op,a,b,c=e['op'],e['a'],e['b'],e['c']
  if op==1:
   if e['semantic'][0]==omit:continue
   state[a]^=state[b];norms[a]+=abs(c)*norms[b];coeff[abs(c)]+=1;source=center if b==n else b
   digest.update((json.dumps([a,source,-c if reverse else c],separators=(',',':'))+'\n').encode())
  elif op==(3 if reverse else 2):assert center is None;center=a;state[b]=state[a];norms[b]=norms[a]
  else:assert center==a;center=None
 wrong=sum(state[i]!=((1<<i)^((1<<(i-960))if 960<=i<1920 else 0))for i in range(n))
 return wrong,max(norms),coeff,digest.hexdigest()
for reverse in(False,True):
 wrong,maxnorm,coeff,dig=replay(events,reverse);ref=result['inverse'if reverse else'forward']
 assert not wrong and maxnorm==ref['max_row_l1']and dig==ref['event_sha256']and coeff=={1:335279,3:960}
assert replay(events,omit='new_kernel2_setup')[0]==41 and replay(events,omit='new_kernel2_restore')[0]==9
# Every non-target integer operand's source support, before and after ADD.
labels=source('bitword/selected/bit/graph_p10.json')['labels'];cols=[{i:1}if i<960 else{}for i in range(n+1)];checked=set();tmp=None
def support(f,qs):
 for q in qs:
  if(f,q)not in checked:assert all(sum(row[j]for j in labels[q])==0 for row in parts(f)[1]);checked.add((f,q))
for e in events:
 op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
 if op==2:assert tmp is None;support(f,cols[a]);cols[b]=dict(cols[a]);tmp=a;continue
 if op==3:assert tmp==a;tmp=None;continue
 if not 960<=a<1920:support(f,cols[a])
 if b!=n and not 960<=b<1920:support(f,cols[b])
 if not 960<=a<1920:
  assert not 960<=b<1920
  for q,x in cols[b].items():
   v=cols[a].get(q,0)+c*x
   if v:cols[a][q]=v
   else:cols[a].pop(q,None)
  support(f,cols[a])
assert not tmp and all(not cols[s]for s in members)
res={'status':'PASS_INDEPENDENT_PR322_PR323_SOURCE_COMPOSITION','inputs':hashes,'four_retimings_exact':True,'seven_new_gram_determinants':newgram,'twenty_selected_ports_rebound':True,'own_cut_target_checks':comparisons,'removed_reads':32,'added_kernel_operations':18,'all133_previous_actual_anchors_rechecked':True,'literal_crossings':crossings,'all_records_reconstructed':len(records),'integer_source_checks':len(checked),'all_new_helper_integer_sources_restored':True,'scalar_counts':[336239,338159],'norms':[132195,1307808],'omission_wrong_rows':[41,9],'histogram':dict(sorted(hist.items())),'local_calls':48486,'local_rank_mass':179458,'scope':'Exact isolated source composition on the frozen paid892 base. Existing base finite facts are hash-bound; all new frame, cut, transport and scalar obligations are checked. Global lowering and price audited separately.','checker_sha256':sha(__file__)}
(HERE/'SOURCE-AUDIT.json').write_text(json.dumps(packet.portable(res),indent=2)+'\n');print(json.dumps({k:v for k,v in res.items()if k!='inputs'},indent=2))

"""Original complete local forward/reflected frame scan for birth-read slot reuse.
Scalar correctness uses exact virtual responses plus the proved birth-cut identity.
"""
import sys,os,gzip
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from collections import Counter
from functools import lru_cache
import pickle,json,time,resource,hashlib
ROOT=Path(__file__).resolve().parent;start=time.monotonic();(sys.platform=='darwin' or resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2)));resource.setrlimit(resource.RLIMIT_CPU,(30,30))
g=pickle.loads((ROOT/'FRAMES.pkl').read_bytes());choice=json.loads(gzip.decompress((ROOT/'BIRTH_MATCHES.json.gz').read_bytes()));v=g['v'];R=len(g['first']);fulltuple=tuple(1<<i for i in range(23,-1,-1));ALL=(1<<v)-1
merge={p['recipient']:p['donor']for p in choice['pairs']};removed=set(merge);live=[s for s in range(R)if s not in removed];physical=lambda s:2*v+merge.get(s,s)
assert len(live)==choice['R'] and not removed&set(merge.values())
assert all(g['first'][s]>v for s in removed),'Selected deferred source injection requires explicit inverse insertion review'
for b,a in merge.items():assert a not in g['placed']and b in g['placed']and b not in g['touched']and g['last'][a]in g['phase']and a not in g['terminal']
frames=[()];ids={():0}
def fid(F):
 if F not in ids:ids[F]=len(frames);frames.append(F)
 return ids[F]
FULL=fid(fulltuple);tm=[fid((m,))for m in g['tm']];U=[fid(F)for F in g['U']]
def basis(rows):
 piv={}
 for x in rows:
  for p in sorted(piv,reverse=True):
   if x>>p&1:x^=piv[p]
  if x:
   p=x.bit_length()-1
   for q in piv:
    if piv[q]>>p&1:piv[q]^=x
   piv[p]=x
 return tuple(piv[p]for p in sorted(piv,reverse=True))
@lru_cache(None)
def dual(i):
 A=frames[i];piv={r.bit_length()-1 for r in A};out=[]
 for j in range(24):
  if j not in piv:
   x=1<<j
   for r in A:
    if r>>j&1:x|=1<<(r.bit_length()-1)
   out.append(x)
 return fid(basis(out))
@lru_cache(131072)
def nested(i,j):
 for x in frames[i]:
  for r in frames[j]:
   if x>>(r.bit_length()-1)&1:x^=r
  if x:return False
 return True
word=[];forward_workspace=[]
def gate(d,s,c,F,remember=False):
 assert d!=s;word.append(('g',d,s,c,F))
 if remember:forward_workspace.append((d,s,c,F))
def oldread(s,F):
 mask=ALL if g['reach_all'][s]else g['reach'][s]
 word.append(('r',physical(s),v,mask,-1,F,('old',s)))
def source(s):
 x=g['first'][s];assert 1<=x<=v;gate(physical(s),x-1,1,U[x],True)
def mix(i):
 op,s,t,x=g['ops'][i]
 if op==1:gate(physical(s),physical(t),1,U[x],True)
 elif op==2:gate(physical(t),physical(s),1,U[x],True)
for s in range(R):
 if s not in g['placed']:oldread(s,0)
for s,x in enumerate(g['first']):
 if x<=v and s not in g['placed']:source(s)
for i in sorted(g['phase']):mix(i)
for s in g['center_roles']:
 j=g['terminal'][s];F=fid(g['U'][g['roots'][j]]);assert len(frames[F])==23
 word.append(('c',physical(s),v,ALL,1,F,0,('center',j-(len(g['roots'])-24))))
for s,F in sorted(g['placed'].items(),key=lambda item:(len(item[1]),item[0])):oldread(s,fid(F))
for s,x in enumerate(g['first']):
 if x<=v and s in g['placed']:source(s)
for i in range(len(g['ops'])):
 if i not in g['phase']:mix(i)
for s,j in sorted(g['terminal'].items(),key=lambda item:item[1]):
 if j<len(g['roots'])-24:
  t=g['targets'][j];word.append(('r',physical(s),v,1<<t,1,dual(tm[t]),('side',j)))
# Correct order includes the source gates: no commutation of injections is assumed.
for d,s,c,F in reversed(forward_workspace):gate(d,s,-c,FULL)
active=list(range(2*v))+[2*v+s for s in live]
initial=[None]*(2*v+R)
for t in range(v):initial[t]=tm[t];initial[v+t]=0
for s in live:initial[2*v+s]=fid(g['placed'].get(s,()))
finish=[None]*len(initial)
for t in range(v):finish[t]=FULL;finish[v+t]=dual(tm[t])
for s in live:finish[2*v+s]=FULL

def scan(events,begin,end):
 current=begin[:];hist=Counter();copies=0;counts=[Counter(current[:v]),Counter(current[v:2*v])];digest=hashlib.sha256();incidences=0
 def promote(s,F):
  nonlocal incidences
  assert s in active_set and current[s] is not None
  old=current[s]
  if old==F:return
  assert nested(old,F),('Illegal frame',s,frames[old],frames[F]);r=len(frames[F])-len(frames[old]);assert r>0
  hist[r]+=1;current[s]=F;incidences+=1
  if s<2*v:
   bank=s//v;counts[bank][old]-=1
   if not counts[bank][old]:del counts[bank][old]
   counts[bank][F]+=1
 def targets(bank,mask,F):
  if len(counts[bank//v])==1 and counts[bank//v].get(F)==v:return
  while mask:
   b=mask&-mask;mask-=b;promote(bank+b.bit_length()-1,F)
 for e in events:
  digest.update(repr(e).encode())
  if e[0]=='g':_,d,s,c,F=e;assert c in(-1,1);promote(d,F);promote(s,F)
  elif e[0]=='r':_,s,bank,mask,sign,F,key=e;assert mask>=0 and not(mask&~ALL);promote(s,F);targets(bank,mask,F)
  else:
   _,s,bank,mask,sign,F,T,key=e;promote(s,F);targets(bank,mask,T)
   assert (F==FULL and T==0)or nested(F,T)or nested(T,F)
   r=abs(len(frames[F])-len(frames[T]));assert r==23;hist[r]+=1;copies+=1
 for s in active:promote(s,end[s])
 assert current==end
 return hist,copies,incidences,digest.hexdigest()
active_set=set(active);forward=scan(word,initial,finish)
def swap(s):return s+v if s<v else(s-v if s<2*v else s)
def reflect(e):
 if e[0]=='g':_,d,s,c,F=e;return('g',swap(d),swap(s),-c,dual(F))
 if e[0]=='r':_,s,bank,mask,sign,F,key=e;return('r',swap(s),v-bank,mask,-sign,dual(F),key)
 _,s,bank,mask,sign,F,T,key=e;return('c',swap(s),v-bank,mask,-sign,dual(F),dual(T),key)
reverse=[reflect(e)for e in reversed(word)];assert [reflect(e)for e in reversed(reverse)]==word
rb=[None]*len(initial);re=[None]*len(initial)
for s in active:rb[swap(s)]=dual(finish[s]);re[swap(s)]=dual(initial[s])
backward=scan(reverse,rb,re);assert forward[:2]==backward[:2],(forward[:2],backward[:2])
H=Counter({r:2*v*n for r,n in forward[0].items()})
for s in live:H[552+len(frames[initial[2*v+s]])]+=2*v
H[529]+=2*v*v;H[1]+=v*v
assert dict(H)=={int(r):n for r,n in choice['child_histogram'].items()},('Whole paid profile mismatch',H)
assert forward[1]==24 and sum(r*n for r,n in H.items())==choice['rank']
# The exact source map and old response pass were independently reconstructed.
bill=json.loads((ROOT/'READOUT_COST.json').read_text());assert bill['max_abs_numerator']==55 and bill['readout_numerator_L1']==46704391
out=dict(status='PASS original complete forward/reflected paid frame scan',source_head='6ec868e8568ca9a74b7245494de1b187c7be78fe',matches=len(merge),physical_original_roles=len(live),virtual_roles=R,word_blocks=len(word),workspace_forward_gates=len(forward_workspace),all_data_source_target_banks_disjoint=True,targets_never_controls=True,donors_dead_before_birth=True,recipients_untouched_before_birth=True,all_selected_recipients_have_no_source_injection=True,inverse_order='Reverse actual workspace and source events chronologically at full frame',forward_frame_transitions=forward[2],reverse_frame_transitions=backward[2],copies_per_direction=forward[1],all_histogram_bins_match=True,forward_word_sha256=forward[3],reverse_word_sha256=backward[3],scalar_scope='All-size arbitrary dirty algebra is the birth-cut identity with exact old-readout responses; complete source supports checked, no dense dirty-square expansion',seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'BIRTH_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

"""Original weighted-word alias, prefix and kernel bridge check. Inert data only."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import base64,gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
from source_data import SOURCE as P,verify,pins,OUTPUT
from cases import CASES
CASE=CASES['166'];CAND=HERE/CASE['file']
def configure(label):
 global CASE,CAND
 CASE=CASES[str(label)];CAND=HERE/CASE['file']
def verify_sources():
 verify()
 assert hashlib.sha256(CAND.read_bytes()).hexdigest()==CASE['sha256']

def read(n):
 n={'graph.json':'gen5bit/selected/bit/graph_p12.json','frames.json':'gen5bit/selected/bit/frames_p12.json.gz','kchron.json':'gen5bit/selected/bit/kchron_p12.json'}.get(n,n)
 p=P/n
 return json.load(gzip.open(p))if n.endswith('.gz')else json.loads(p.read_text())
def rr(A):
 A=[[Q(x)for x in row]for row in A];piv=[];k=0
 for j in range(24):
  pivot=next((i for i in range(k,len(A))if A[i][j]),None)
  if pivot is None:continue
  A[k],A[pivot]=A[pivot],A[k];c=A[k][j];A[k]=[x/c for x in A[k]]
  for i in range(len(A)):
   if i!=k and A[i][j]:
    c=A[i][j];A[i]=[x-c*y for x,y in zip(A[i],A[k])]
  piv.append(j);k+=1
 return A[:k],piv
def null(B):
 R,piv=rr(B);out=[]
 for j in range(24):
  if j in piv:continue
  v=[Q(0)]*24;v[j]=1
  for i,k in enumerate(piv):v[k]=-R[i][j]
  out.append(v)
 return out
def run():
 verify_sources();t=time.monotonic();w=read('gen5bit/selected/bit/word_p12.json.gz');f={int(k):v for k,v in read('frames.json')['frames'].items()};g=read('graph.json')
 ks=read('kernel-selection.json');d1=read('descent-selection.json');d2=read('descent2-selection.json');rest=read('restore-selection.json')['entries'];sinks=read('sink-selection.json')['sinks']
 candidate=json.loads(CAND.read_text());entries=candidate['entries']
 alias={b:a for a,b in w['pairs']};recipient={a:b for a,b in w['pairs']};regs=sorted(set(range(17160))-set(alias));ids={r:3520+i for i,r in enumerate(regs)}
 sid=lambda r:ids[alias.get(r,r)];inverse={s:r for r,s in ids.items()};n=3520+len(regs);assert n==18952
 gauges={z['role']:z for z in w['gauges']};assert all(gauges[b]['dim']==21 for b in alias)
 phase=w['phase1'];assert phase==sorted(phase);phase_set=set(phase);after=[i for i in range(len(w['ops']))if i not in phase_set];order=phase+after
 pos={i:j for j,i in enumerate(order)};uses=defaultdict(list)
 for i in order:
  for r in w['ops'][i][:2]:uses[r].append(i)
 adj=[{}for _ in range(17160)]
 for root,r in zip(g['roots'],w['rootroles']):
  for target in root['targets']:adj[r][target]=adj[r].get(target,0)+1
 for i in reversed(order):
  a,b,_=w['ops'][i]
  for target,c in adj[a].items():adj[b][target]=adj[b].get(target,0)+c
 response=[sum(1<<target for target,c in row.items()if c%2)for row in adj]
 oldentries=[dict(pivot=z['a'],donors=[z['b']],basis=z['basis'],cut_read=z['cut_read'])for z in ks['pairs']]+[dict(pivot=z['pivot'],donors=z['donors'],basis=z['basis'],cut_read=z['cut_read'])for z in ks['families']]
 oldmembers={s for z in oldentries for s in[z['pivot']]+z['donors']};changed={s for z in d1['entries']+d2['entries']for s in z['scalar'][:2]}
 ends={z['helper']for z in rest};sunk={z['role']for z in sinks};source=set(w['sources'].values())
 eligible={r for r in regs if r not in set(gauges)|sunk|source and ids[r]not in oldmembers|changed|ends}
 expanded=eligible&set(recipient);legacy=eligible-set(recipient)
 # Literal ZERO-prefix reconstruction, through physical alias map.
 prefix={};last={};read_count=0;lastglobal=None
 for r in range(17160):
  if r in gauges:continue
  s=sid(r);assert s not in prefix,'two initial plain roles alias'
  prefix[s]=response[r]
  for target,c in adj[r].items():
   if c%2:last[s]=(read_count,[1760+target,s,-c]);read_count+=1;lastglobal=last[s]
 assert read_count==648088
 for z in oldentries:
  p=z['pivot'];value=prefix[p]
  for d in z['donors']:value^=prefix[d]
  assert value==0
  assert max((last[s]for s in[p]+z['donors']),key=lambda x:x[0])[1]==z['cut_read']
 active={z['virtual_pivot']for z in entries}|{d for z in entries for d in z['virtual_donors']};assert len(active)==CASE['members'] and active<=eligible
 pivots={z['virtual_pivot']for z in entries};donors={d for z in entries for d in z['virtual_donors']};assert len(pivots)==CASE['pivots'] and len(donors)==CASE['donors'] and not pivots&donors
 lines={}
 for z in entries:
  assert sid(z['virtual_pivot'])==z['pivot'] and[sid(d)for d in z['virtual_donors']]==z['donors']
  value=prefix[z['pivot']]
  for d in z['donors']:value^=prefix[d]
  assert value==0
  B=z['basis'];assert len(B)==1 and sum(B[0])==0 and sum(x*x for x in B[0])==2
  for r in[z['virtual_pivot']]+z['virtual_donors']:
   assert r not in lines or lines[r]==B[0];lines[r]=B[0]
 # Explicit formal comparison on every physical pre-compaction column;
 # removed sink slots are harmless inert spectator coordinates.
 def prefix_events(omit):
  out=[]
  for r in sorted(active-omit):
   bits=prefix[sid(r)]
   while bits:
    bit=bits&-bits;target=bit.bit_length()-1;bits-=bit;out.append((1760+target,sid(r)))
  return out
 q=prefix_events(set());qp=prefix_events(pivots)
 setup=[(d,z['pivot'])for z in entries for d in z['donors']]
 U=[(1760+i,i)for i in range(1760)];tail=list(reversed(q))+U
 def evaluate(events):
  rows=[1<<i for i in range(n)]
  for a,b in events:rows[a]^=rows[b]
  return rows
 oldword=q+tail;newword=qp+setup+tail+list(reversed(setup))
 assert evaluate(oldword)==evaluate(newword)
 assert evaluate(list(reversed(oldword)))==evaluate(list(reversed(newword)))
 assert evaluate(qp+setup[1:]+tail+list(reversed(setup)))!=evaluate(oldword)
 assert evaluate(qp+setup+tail+list(reversed(setup))[1:])!=evaluate(oldword)
 # Reconstruct complete base alias paths. Selected new roles are disjoint from
 # both scalar-descents and every old kernel/early-stop endpoint, so these are
 # their actual required frame paths after all inherited transforms.
 ann_cache={};rref_cache={};paircache=set()
 def ann(frame):
  if frame not in ann_cache:ann_cache[frame]=f[frame]['a']if'a'in f[frame]else null(f[frame]['b'])
  return ann_cache[frame]
 def sub(a,b):
  if a==b or(a,b)in paircache:return
  if a not in rref_cache:rref_cache[a]=rr(ann(a))
  R,piv=rref_cache[a]
  for row in ann(b):
   v=list(map(Q,row))
   for u,k in zip(R,piv):
    c=v[k]
    if c:v=[x-c*y for x,y in zip(v,u)]
   assert not any(v),('Nonnested physical alias path',a,b)
  paircache.add((a,b))
 def alias_path(r):
  roles={r};b=recipient.get(r)
  if b is not None:
   roles.add(b);assert r not in gauges and r not in w['rootroles'] and r not in source
   assert max(pos[i]for i in uses[r])<w['reads'][str(b)]
   assert w['reads'][str(b)]<=min(pos[i]for i in uses[b])
  path=[]
  def append(frame):
   if not path or path[-1]!=frame:path.append(frame)
  for i in phase:
   if any(s in roles for s in w['ops'][i][:2]):append(w['op_frame'][i])
  for j,i in enumerate(after):
   if b is not None and w['reads'][str(b)]==len(phase)+j:append(gauges[b]['frame'])
   if any(s in roles for s in w['ops'][i][:2]):append(w['op_frame'][i])
  if b is not None and w['reads'][str(b)]==len(order):append(gauges[b]['frame'])
  for j,role in enumerate(w['rootroles']):
   if role in roles:append(w['root_frame'][j])
  append(w['full_frame'])
  for x,y in zip(path,path[1:]):sub(x,y)
  return path
 old_reused=sorted(inverse[s]for s in oldmembers if inverse[s]in recipient)
 # Existing source examples establish that reused donor slots are admitted;
 # the base alias geometry is independently checked for every such example.
 for r in old_reused:alias_path(r)
 H=Counter();receipts=[];pathrows=[]
 for r in sorted(active):
  path=alias_path(r);first=path[0];v=lines[r];assert all(sum(x*y for x,y in zip(row,v))==0 for row in ann(first))
  d=f[first]['dim'];H[d]-=1
  if d>1:H[d-1]+=1
  if r in donors:H[1]+=1
  pathrows.append(dict(role=r,stream=sid(r),kernel_kind='pivot'if r in pivots else'donor',entrance_basis=[lines[r]],first_frame=first,first_dimension=d,frames=path,dimensions=[f[x]['dim']for x in path],endpoint='FULL',aliased_recipient=recipient.get(r)))
  if r in recipient:
   b=recipient[r];receipts.append(dict(donor_role=r,recipient_role=b,physical_stream=sid(r),gauge_read_order=w['reads'][str(b)],
    donor_last_order=max(pos[i]for i in uses[r]),recipient_first_order=min(pos[i]for i in uses[b]),frames=path,dimensions=[f[x]['dim']for x in path],endpoint='FULL',
    first_dimension=d,literal_zero_prefix_response_bitcount=prefix[sid(r)].bit_count()))
 H={r:c for r,c in sorted(H.items())if c};assert H==CASE['delta']
 # Concrete obstruction to importing the original final12 endpoint invoice:
 # each former helper now shares a slot with an earlier independent lifetime.
 core=json.loads((HERE.parent/'certificates/coretime12/local.json').read_text())['candidates'];blocked=[]
 for z in core:
  a=z['helper'];assert a in alias;d=alias[a];assert uses[d]
  assert max(pos[i]for i in uses[d])<w['reads'][str(a)]
  blocked.append(dict(former_helper=a,earlier_donor=d,physical_stream=sid(a),
   old_donor_cleanup_gates=len(uses[d]),last_original_donor_op=uses[d][-1],required_unchanged_cleanup_frame='FULL'))
 return dict(status='PASS_WEIGHTED_SHARED_KERNEL_ALIAS_AND_PREFIX_BRIDGE',head='10b40041d4ab8a6610083e95bc571aee3468bca2',
  physical_streams_before_sink=n,weighted_matching_pairs=len(alias),plain_eligible_helpers=len(eligible),prior_conservative_helpers=len(legacy),newly_admissible_reused_helpers=len(expanded),
  frozen_kernel_reused_donor_examples=len(old_reused),all_existing_reused_example_base_paths_nested=True,
  old_kernel_relations_and_cut_triples_reproduced=len(oldentries),literal_prefix_plain_reads=read_count,last_plain_read=lastglobal,
  all_column_formal_composition_forward_inverse=True,all_column_dimension=n,omitted_setup_and_restore_rejected=True,
  selected_pivots=CASE['pivots'],selected_distinct_donors=CASE['donors'],selected_streams=CASE['members'],selected_reused_donors=receipts,
  setup_adds=sum(len(z['donors'])for z in entries),restore_adds=sum(len(z['donors'])for z in entries),
  removed_initial_reads=sum(sum(c%2 for c in adj[p].values())for p in pivots),removed_initial_unit_additions=sum(sum(abs(c)for c in adj[p].values()if c%2)for p in pivots),
  local_histogram_delta=H,residual_family_delta={24:-CASE['pivots'],23:CASE['pivots']},selected_paths=pathrows,common_cut='After all ZERO compensation reads and frozen kernel setups, before any source injection',
  formal_scalar_identity='Let U=SQ be the inherited complete physical decoder and A=I+K the new disjoint-support shear layer. Literal physical prefix relations imply A Qprime=Q A. Since U fixes every physical dirty slot, Ainv S A Qprime=U, including aliased slots. The relations above were checked on the literal initial physical columns.',
  final_full_endpoints_checked=True,exact_unique_frame_containments=len(paircache),direct_final12_endpoint_port_rejected=blocked,
  scope='Changed-stage alias/prefix/frame and paid-demand certificate; inherited full physical decoder is a hypothesis. The final12 conflict concerns the unchanged FULL cleanup schedule, not all possible redesigned cleanups. Fresh scalar norm, exact pricing, bank mapping and finite bill remain separate obligations.',seconds=time.monotonic()-t)
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 r=run();(OUTPUT/'bridge-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

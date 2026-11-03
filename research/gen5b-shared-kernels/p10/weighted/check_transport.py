"""Independent exact transport proof, reading pinned JSON and inert source text only.
No code from PR320 is imported or run. This is not raw-record regeneration.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import json,hashlib,time
from weighted_source_data import read,read_bytes,verify,HEAD
CODE=Path(__file__).resolve().parent
from weighted_source_data import OUTPUT,PACKAGE_OUTPUT,PACKAGE_ROOT
HERE=OUTPUT
OVER=PACKAGE_OUTPUT/'matching'/'word_weighted892.json'
OVER_SHA='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
CAND=PACKAGE_ROOT/'witnesses'/'candidate19-residue4.json'
CAND_SHA='0f1a39a516e12fe3ca3b92a1925dc1b5df9d5437aff821a75b46188f779ec954'
def compact(c):return {int(k):v for k,v in sorted(c.items())if v}
def diff(a,b):
 c=Counter(b);c.subtract(a);return compact(c)
def rr(rows,width=20):
 a=[list(map(Q,r)) for r in rows];piv=[];k=0
 for j in range(width):
  z=next((i for i in range(k,len(a))if a[i][j]),None)
  if z is None:continue
  a[k],a[z]=a[z],a[k];c=a[k][j];a[k]=[x/c for x in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:
    c=a[i][j];a[i]=[x-c*y for x,y in zip(a[i],a[k])]
  piv.append(j);k+=1
 return a[:k],piv
def null(rows):
 a,p=rr(rows);out=[]
 for j in set(range(20))-set(p):
  r=[Q(0)]*20;r[j]=1
  for row,k in zip(a,p):r[k]=-row[j]
  out.append(r)
 return out
def included(rows,space):
 a,p=rr(space)
 for row in rows:
  row=list(map(Q,row))
  for v,k in zip(a,p):
   c=row[k]
   if c:row=[x-c*y for x,y in zip(row,v)]
  if any(row):return False
 return True
def run():
 t=time.monotonic();verify();assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA;assert hashlib.sha256(CAND.read_bytes()).hexdigest()==CAND_SHA
 old=read('bitword/selected/bit/word_p10.json.gz');w=json.loads(OVER.read_text());cand=json.loads(CAND.read_text());f={int(k):v for k,v in read('frames.json')['frames'].items()};g=read('graph.json')
 assert [k for k in old if old[k]!=w[k]]==['pairs','reads']
 gauges={e['role']:e for e in w['gauges']};sources=set(w['sources'].values());roots=set(w['rootroles'])
 def mapping(word):
  aliases={b:a for a,b in word['pairs']};roles=sorted(set(range(9120))-set(aliases));ids={r:1920+i for i,r in enumerate(roles)}
  return aliases,roles,ids,{r:ids[aliases.get(r,r)]for r in range(9120)}
 oa,oreg,oi,os=mapping(old);na,nreg,ni,ns=mapping(w);inv={s:r for r,s in oi.items()};n=1920+len(nreg)
 assert len(oa)==890 and len(na)==892 and n==10148
 assert set(na)-set(oa)=={9118,9119} and set(oa)<=set(na)
 assert all(oi[r]==ni[r]for r in nreg)
 pairs_old=set(map(tuple,old['pairs']));pairs_new=set(map(tuple,w['pairs']));changed={r for p in pairs_old^pairs_new for r in p}
 rolemap=[dict(virtual_role=r,old_physical=os[r],new_physical=ns[r],old_representative=oa.get(r,r),new_representative=na.get(r,r))for r in range(9120)]
 (HERE/'virtual-physical-map.json').write_text(json.dumps(dict(head=HEAD,overlay_sha256=OVER_SHA,rows=rolemap),indent=2)+'\n')
 phase=sorted(w['phase1']);ps=set(phase);rest=[i for i in range(len(w['ops']))if i not in ps];order=phase+rest;pos={i:j for j,i in enumerate(order)};uses=defaultdict(list)
 for i in order:
  a,b,_=w['ops'][i];assert ns[a]!=ns[b]
  uses[a].append(i);uses[b].append(i)
 for a,b in pairs_new:
  assert a not in set(gauges)|sources|roots and b in gauges and gauges[b]['dim']==17
  assert max(pos[i]for i in uses[a])<w['reads'][str(b)]<=min(pos[i]for i in uses[b])
 adj=[{}for _ in range(9120)]
 for root,r in zip(g['roots'],w['rootroles']):
  for q in root['targets']:adj[r][q]=adj[r].get(q,0)+1
 for i in reversed(order):
  a,b,_=w['ops'][i]
  for q,c in adj[a].items():adj[b][q]=adj[b].get(q,0)+c
 responses=[sum(1<<q for q,c in x.items()if c%2)for x in adj]
 prefix={};last={};count=0;events=[]
 for r in range(9120):
  if r in gauges:continue
  assert ns[r]not in prefix;prefix[ns[r]]=responses[r]
  for q,c in adj[r].items():
   if c%2:last[ns[r]]=(count,[960+q,ns[r],-c]);events.append((960+q,ns[r],-c));count+=1
 assert count==300560
 ks=read('kernel-selection.json');raw=[dict(pivot=z['a'],donors=[z['b']],cut_read=z['cut_read'],rank=z['rank'],basis=z['basis'])for z in ks['pairs']]+[dict(pivot=z['pivot'],donors=z['donors'],cut_read=z['cut_read'],rank=z['rank'],basis=z['basis'])for z in ks['families']]
 oldmembers={s for e in raw for s in[e['pivot']]+e['donors']};newentries=[]
 for index,e in enumerate(raw):
  vr=[inv[s]for s in[e['pivot']]+e['donors']];ss=[ns[r]for r in vr];p,*ds=ss;value=prefix[p]
  for d in ds:value^=prefix[d]
  assert value==0 and prefix[p]
  cut=max((last[s]for s in ss),key=lambda z:z[0]);assert cut[1]==[e['cut_read'][0],ns[inv[e['cut_read'][1]]],e['cut_read'][2]]
  newentries.append(dict(index=index,virtual_pivot=vr[0],virtual_donors=vr[1:],pivot=p,donors=ds,cut_read=cut[1],cut_index=cut[0],rank=e['rank'],basis=e['basis']))
 assert len(newentries)==775
 (HERE/'rebound-kernel-entries.json').write_text(json.dumps(dict(n=n,entries=newentries),indent=2)+'\n')
 # Exact rational containment on complete required forward paths. Reverse
 # annihilator nesting follows by duality, with equal complementary dimensions.
 anncache={};subcache=set();pathcache={}
 def ann(fid):
  if fid not in anncache:anncache[fid]=f[fid]['a']if'a'in f[fid]else null(f[fid]['b'])
  assert len(anncache[fid])==20-f[fid]['dim']
  return anncache[fid]
 def sub(a,b):
  if a==b or(a,b)in subcache:return
  assert f[a]['dim']<=f[b]['dim'] and included(ann(b),ann(a)),('not nested',a,b)
  subcache.add((a,b))
 def fullpath(word,r):
  key=('new'if word is w else'old',r)
  if key in pathcache:return pathcache[key]
  pair=dict(word['pairs']);b=pair.get(r);members={r}if b is None else{r,b};out=[]
  def add(fid):
   if not out or out[-1]!=fid:out.append(fid)
  if r in gauges:add(gauges[r]['frame'])
  elif r in sources:add(word['source_frame'][next(int(q)for q,s in word['sources'].items()if s==r)])
  for i in phase:
   if members.intersection(word['ops'][i][:2]):add(word['op_frame'][i])
  # Center copies occur before all gauge reads and rest operations.
  for j,rrr in enumerate(word['rootroles']):
   if rrr in members and g['roots'][j]['kind']=='center':add(word['root_frame'][j])
  for j,i in enumerate(rest):
   if b is not None and word['reads'][str(b)]==len(phase)+j:add(gauges[b]['frame'])
   if members.intersection(word['ops'][i][:2]):add(word['op_frame'][i])
  if b is not None and word['reads'][str(b)]==len(order):add(gauges[b]['frame'])
  for j,rrr in enumerate(word['rootroles']):
   if rrr in members and g['roots'][j]['kind']=='side':add(word['root_frame'][j])
  add(word['full_frame'])
  for a,b in zip(out,out[1:]):sub(a,b)
  pathcache[key]=out;return out
 for r in oreg:fullpath(old,r)
 for r in nreg:fullpath(w,r)
 # Existing kernel entrance chains are fixed before all forward operations.
 def kernel_delta(word):
  chain=defaultdict(list);piv={e['virtual_pivot']:e for e in newentries}
  for e in sorted(newentries,key=lambda e:(e['cut_index'],e['rank'],e['pivot'])):
   for r in e['virtual_donors']:chain[r].append(e['basis'])
  result=Counter();receipts=[]
  for r in sorted({inv[s]for s in oldmembers}):
   path=fullpath(word,r);first=path[0];bases=chain[r]
   if r in piv:bases=[piv[r]['basis']]+bases
   for B in bases:assert all(sum(x*y for x,y in zip(a,b))==0 for a in ann(first)for b in B)
   for A,B in zip(bases,bases[1:]):assert included(A,B),('nonnested entrance',r)
   dims=([len(piv[r]['basis'])]if r in piv else[0])+[len(B)for B in chain[r]]+[f[x]['dim']for x in path]
   baseline=[0]+[f[x]['dim']for x in path]
   before=Counter(b-a for a,b in zip(baseline,baseline[1:])if b>a);after=Counter(b-a for a,b in zip(dims,dims[1:])if b>a)
   result.update(after);result.subtract(before)
   receipts.append(dict(role=r,physical=ns[r],first_frame=first,frames=path,entrance_ranks=[len(B)for B in bases],delta=diff(before,after)))
  return compact(result),receipts
 oldD,_=kernel_delta(old);newD,receipts=kernel_delta(w)
 assert oldD==newD=={int(k):v for k,v in ks['expected_local_delta'].items()}
 (HERE/'kernel-path-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 # Check additional fixed19 on rebound coordinates and exact all-column shear identity.
 cands=[];active=set();pivots=set();donors=set();lines={}
 for e in cand['entries']:
  vr=[e['virtual_pivot']]+e['virtual_donors'];ss=[ns[r]for r in vr];p,*ds=ss
  assert e['pivot']==os[vr[0]] and e['donors']==[os[r]for r in vr[1:]]
  val=prefix[p]
  for d in ds:val^=prefix[d]
  assert val==0
  assert e['cut_read']==list(events[-1])
  B=e['basis'];assert len(B)==1 and sum(B[0])==0 and sum(x*x for x in B[0])==2
  for r in vr:
   assert r not in lines or lines[r]==B[0];lines[r]=B[0]
  active.update(vr);pivots.add(vr[0]);donors.update(vr[1:]);cands.append(dict(e,pivot=p,donors=ds))
 assert (len(pivots),len(donors),len(active))==(19,22,41)and not pivots&donors
 assert not active&changed and not{ns[r]for r in active}&oldmembers
 assert all(r not in set(gauges)|sources for r in active)
 H=Counter();candpaths=[]
 for r in sorted(active):
  path=fullpath(w,r);first=path[0];assert all(sum(x*y for x,y in zip(a,lines[r]))==0 for a in ann(first));d=f[first]['dim'];H[d]-=1
  if d>1:H[d-1]+=1
  if r in donors:H[1]+=1
  candpaths.append(dict(role=r,physical=ns[r],frames=path,dimension=d,aliased_recipient=dict(w['pairs']).get(r)))
 assert compact(H)=={int(k):v for k,v in cand['local_histogram_delta'].items()}
 q=[(960+t,ns[r])for r in sorted(active)for t in range(960)if responses[r]>>t&1];qp=[e for e in q if inv[e[1]]not in pivots]
 setups=[(d,e['pivot'])for e in cands for d in e['donors']];tail=list(reversed(q))+[(960+i,i)for i in range(960)]
 def evaluate(seq):
  rows=[1<<i for i in range(n)]
  for a,b in seq:rows[a]^=rows[b]
  return rows
 left=q+tail;right=qp+setups+tail+list(reversed(setups));want=evaluate(left)
 assert want==evaluate(right)and evaluate(reversed(left))==evaluate(reversed(right))
 assert want!=evaluate(qp+setups[1:]+tail+list(reversed(setups)))
 assert want!=evaluate(qp+setups+tail+list(reversed(setups))[1:])
 (HERE/'rebound-candidate19.json').write_text(json.dumps(dict(cand,entries=cands,overlay_sha256=OVER_SHA),indent=2)+'\n')
 # Direct-role separation of every inherited later transform, with the sink
 # compaction explicitly reversed for reorder operands.
 descent=read('descent-selection.json')['entries'];restore=read('restore-selection.json')['entries'];sinks=read('sink-selection.json')['sinks'];reorder=read('reorder-selection.json')['moves'];removed=sorted(z['stream']for z in sinks)
 def lift(s):
  for q in removed:
   if q<=s:s+=1
  return s
 role=lambda s:inv[s]if s>=1920 else None
 affected=changed|active
 overlaps=dict(descent=[i for i,e in enumerate(descent)if{role(s)for s in e['scalar'][:2]}&affected],restore=[i for i,e in enumerate(restore)if{role(e[k])for k in('helper','donor')}&affected],sink=[e['role']for e in sinks if e['role']in affected],reorder=[i for i,e in enumerate(reorder)if{role(lift(s))for s in e['incidence'][:2]}&affected])
 assert not any(overlaps.values())
 out=dict(status='PASS_EXACT_KERNEL_AND_FIXED19_CONDITIONAL_TRANSPORT',head=HEAD,overlay_sha256=OVER_SHA,original_candidate_sha256=CAND_SHA,rebound_candidate_sha256=hashlib.sha256((HERE/'rebound-candidate19.json').read_bytes()).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),old_physical_columns=10150,new_physical_columns=n,old_pairs=890,new_pairs=892,preserved_pairs=len(pairs_old&pairs_new),changed_role_count=len(changed),physical_representatives_removed=[9118,9119],all_retained_representative_ids_unchanged=True,virtual_map_rows=len(rolemap),initial_plain_reads=count,kernel_entries_rebound=len(newentries),kernel_relations_and_cut_triples_exact=True,kernel_entries_touching_changed_roles=sum(bool(({e['virtual_pivot']}|set(e['virtual_donors']))&changed)for e in newentries),kernel_delta_old=oldD,kernel_delta_new=newD,complete_old_paths_checked=len(oreg),complete_new_paths_checked=len(nreg),unique_exact_containment_pairs=len(subcache),candidate19_delta=compact(H),candidate19_members=len(active),candidate19_setup_and_restore_pairs=len(setups),candidate19_all_column_f2_identity_forward_reverse=True,candidate19_omission_controls_rejected=True,direct_role_overlaps=overlaps,selected_paths=candpaths,scope='Exact matching map, literal installed-kernel relations/cuts, full base alias containment, unchanged installed-kernel paid delta, and fixed19 composition. Full raw-word regeneration, inherited transform record/anchor rebinding, target-prefix cut chronology, fresh norm bounds, pricing and bank admission are separate obligations.',source_loader_sha256=hashlib.sha256((CODE/'weighted_source_data.py').read_bytes()).hexdigest())
 (HERE/'transport-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()

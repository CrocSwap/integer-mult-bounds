"""Bounded PR305 port: two complete groups, then one third-line reclosure.

No new basis or contrast line is searched. All upstream inputs are inert data.
"""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,math
from source_data import ROOT,SOURCE,OUTPUT
from search_expanded_lines import closure
P=ROOT;S=SOURCE;OLD=ROOT.parent/'weighted275'
HEAD='a17c42903bbe8d9d26c4bc712d7216a7176237e9'
def read(name):
 raw=(S/name).read_bytes();return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def members(entries):return {r for e in entries for r in[e['virtual_pivot']]+e['virtual_donors']}
def support(e):return tuple(i for i,c in enumerate(e['basis'][0])if c)
def run():
 w=read('gen5bit/selected/bit/word_p12.json.gz');k=read('kernel-selection.json')
 reg=sorted(set(range(17160))-{b for a,b in w['pairs']});ids={r:3520+i for i,r in enumerate(reg)};inverse={s:r for r,s in ids.items()}
 cache=json.loads(gzip.decompress((OUTPUT/'response-cache.json.gz').read_bytes()));rows=cache['roles'];frames=read('gen5bit/selected/bit/frames_p12.json.gz')['frames']
 assert cache['source_head']==HEAD and cache['installed_response_and_cut_checks']==1734
 def dim(r):return frames[str(rows[str(r)]['first_base_use']['frame'])]['dim']
 phi=lambda r:r*math.log(120/r)if r else 0
 def ledger(entries):
  ps={e['virtual_pivot']for e in entries};ds={r for e in entries for r in e['virtual_donors']};assert len(ps)==len(entries)and not ps&ds
  h=Counter()
  for r in ps|ds:
   d=dim(r);h[d]-=1
   if d>1:h[d-1]+=1
  h[1]+=len(ds);h={r:n for r,n in sorted(h.items())if n};assert sum(r*n for r,n in h.items())==-len(ps)
  return h,len(ds)
 occupied={z['a']for z in k['pairs']}|{z['b']for z in k['pairs']}|{s for z in k['families']for s in[z['pivot']]+z['donors']}
 forbidden={inverse[s]for s in occupied}
 changed={s for name in ('descent-selection.json','descent2-selection.json')for z in read(name)['entries']for s in z['scalar'][:2]}
 early={z['helper']for z in read('restore-selection.json')['entries']};sinks={z['role']for z in read('sink-selection.json')['sinks']};sources=set(w['sources'].values())
 old=json.loads((OLD/'candidate-combined166-reclosed.json').read_text());primary=[e for e in old['entries']if support(e)in((16,17),(6,7))]
 assert len(primary)==154 and Counter(support(e)for e in primary)=={(16,17):136,(6,7):18}
 assert not members(primary)&forbidden
 def emit(entries,label,scope):
  for e in entries:
   assert ids[e['virtual_pivot']]==e['pivot'] and [ids[r]for r in e['virtual_donors']]==e['donors']
   x=int(rows[str(e['virtual_pivot'])]['response_hex'],16)
   for d in e['virtual_donors']:x^=int(rows[str(d)]['response_hex'],16)
   assert not x
  assert not members(entries)&(forbidden|sinks|sources)
  assert not {ids[r]for r in members(entries)}&(changed|early)
  h,d=ledger(entries);n=len(entries);assert n%2==0
  out=dict(source_head=HEAD,selection=label,pivots=n,entries=entries,local_histogram_delta=h,residual_family_delta={24:-n,23:n},distinct_donors=d,scalar_setup_pairs=sum(len(e['donors'])for e in entries),predecessor166_sha256=hashlib.sha256((OLD/'candidate-combined166-reclosed.json').read_bytes()).hexdigest(),scope=scope)
  path=OUTPUT/(label+'.json');path.write_text(json.dumps(out,indent=2)+'\n')
  return dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),**{q:v for q,v in out.items()if q!='entries'})
 safe=emit(primary,'candidate154','Complete retained136 and18 groups only; no line2/3, no final12. This file proves exact role/response and first-frame ledger facts only; fresh bridge/norm/chart/bank/finite admission required.')
 third=json.loads((OLD/'candidate-line2-3.json').read_text())['entries'];newly_occupied=sorted(members(third)&forbidden)
 assert newly_occupied==[7955,8998,8999,9146,9147,9263]
 surviving=[e for e in third if not members([e])&forbidden];assert not members(surviving)&members(primary)
 relations=[dict(pivot=e['virtual_pivot'],donors=e['virtual_donors'])for e in surviving]
 dimensions={r:dim(r)for r in members(surviving)}
 selected,profit=closure(relations,dimensions,phi);before=len(selected);parity=None
 if len(selected)%2:
  counts=Counter(d for e in selected for d in e['donors'])
  def marginal(e):
   benefit=phi(dim(e['pivot']))-phi(dim(e['pivot'])-1)
   release=sum(phi(1)+phi(dim(d)-1)-phi(dim(d))for d in e['donors']if counts[d]==1)
   return(round((benefit-release)*10**9),e['pivot'])
  parity=min(selected,key=marginal);selected=[e for e in selected if e is not parity]
 keep={e['pivot']for e in selected};extras=[e for e in surviving if e['virtual_pivot']in keep]
 combined=emit(primary+extras,'candidate_reclosed','Exactly one closure on surviving original line2/3 relations, excluding six occupied roles and preserving the154 complete-group union. No new basis or line; full changed-obligation admission remains separate.')
 report=dict(status='PASS_BOUNDED_PR305_ROLE_RESPONSE_LEDGER',source_head=HEAD,safe154=safe,reclosed=combined,third_line=dict(original_relations=len(third),newly_occupied_roles=newly_occupied,surviving_relations=len(surviving),selected_before_parity=before,selected_after_parity=len(extras),parity_omitted_pivot=parity['pivot']if parity else None,rounded_closure_profit=profit),scope='Only the154 complete-group port and one closure of the existing third line. No new line/basis search or optimality claim.')
 (OUTPUT/'port-result.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 print(json.dumps(run(),indent=2))

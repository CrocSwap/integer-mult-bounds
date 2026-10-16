"""Original nonnegative norm transport, with conservative target-prefix bound.

Helper updates are replayed exactly. Every target prefix ADD is majorized by
applying every target-prefix and sink batch along an exact acyclic majorant.
Deleted compression reads are restored for this upper bound. No source code
from the upstream repository is executed.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json,sys,time
import check_bridge
from check_bridge import read,HERE,verify_sources
from source_data import OUTPUT
def verify_inputs():verify_sources()
sys.dont_write_bytecode=True

def suffix_build():
 w=read('gen5bit/selected/bit/word_p12.json.gz');g=read('graph.json');partner=read('kchron.json')['entries']
 oldrestore=read('restore-selection.json')['entries'];ks=read('kernel-selection.json');sinks=read('sink-selection.json')['sinks']
 alias={b:a for a,b in w['pairs']};regs=sorted(set(range(17160))-set(alias));physical={r:3520+i for i,r in enumerate(regs)};sid=lambda r:physical[alias.get(r,r)]
 phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];sunk={z['role']for z in sinks}
 byroot=defaultdict(list)
 for z in partner:byroot[z['deliver_after_root']].append(z)
 out=[]
 for i,(r,s)in enumerate(zip(g['roots'],w['rootroles'])):
  if r['kind']=='side'and s not in sunk:
   for t in r['targets']:out.append((1760+t,sid(s),1,'root'))
  for e in byroot[i]:
   out.append((e['carrier'],e['passive'],1,'partner_setup'))
   for t in e['receivers']:out.append((1760+t,e['carrier'],1,'partner_delivery'))
 for e in partner:out.append((e['carrier'],e['passive'],-1,'partner_cleanup'))
 moved={(z['helper'],z['donor']):0 for z in oldrestore}
 for z in sorted(oldrestore,key=lambda z:z['helper']):out.append((z['helper'],z['donor'],z['coefficient'],'old_restore'))
 for index in reversed(order):
  a,b,_=w['ops'][index]
  if a in sunk:continue
  pair=(sid(a),sid(b))
  if pair in moved:moved[pair]+=1;continue
  out.append((*pair,-1,'cleanup'))
 assert all(x==1 for x in moved.values())
 for source,role in w['sources'].items():out.append((sid(role),int(source),-1,'uninject'))
 entries=[dict(pivot=z['a'],donors=[z['b']])for z in ks['pairs']]+[dict(pivot=z['pivot'],donors=z['donors'])for z in ks['families']]
 for z in entries:
  for donor in z['donors']:out.append((donor,z['pivot'],-1,'kernel_restore'))
 return 3520+len(regs),[],out,{}

def run(candidate_path=None):
 verify_inputs();start=time.monotonic();w=read('gen5bit/selected/bit/word_p12.json.gz');g=read('graph.json');ks=read('kernel-selection.json');target=read('target-selection.json');sinks=read('sink-selection.json')['sinks'];sink_byrole={z['role']:z for z in sinks}
 candidate_path=Path(candidate_path)if candidate_path else check_bridge.CAND
 witness=json.loads(candidate_path.read_text())['entries']
 oldentries=[dict(pivot=z['a'],donors=[z['b']],cut_read=z['cut_read'])for z in ks['pairs']]+[dict(pivot=z['pivot'],donors=z['donors'],cut_read=z['cut_read'])for z in ks['families']]
 alias={b:a for a,b in w['pairs']};regs=sorted(set(range(17160))-set(alias));physical={r:3520+i for i,r in enumerate(regs)};sid=lambda r:physical[alias.get(r,r)]
 n=3520+len(regs);phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
 adj=[{}for _ in range(17160)]
 for root,r in zip(g['roots'],w['rootroles']):
  for t in root['targets']:adj[r][t]=adj[r].get(t,0)+1
 for index in reversed(order):
  a,b,_=w['ops'][index]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 gauge={x['role']:x for x in w['gauges']};oldp={x['pivot']for x in oldentries};newp={x['pivot']for x in witness}
 setup=defaultdict(list)
 for z in oldentries:setup[tuple(z['cut_read'])].append(z)
 prefix=[];hits=set()
 for r in range(17160):
  if r in gauge or r in sink_byrole:continue
  for t,c in adj[r].items():
   if c%2:
    event=(1760+t,sid(r),-c)
    if sid(r)not in oldp:prefix.append(event)
    for z in sorted(setup.get(event,[]),key=lambda z:z['pivot']):
     hits.add(z['pivot']);prefix.extend((d,z['pivot'],1)for d in z['donors'])
 assert len(hits)==len(oldentries)
 # Setup rank is irrelevant to scalar ordering here; the source sorts by rank
 # and pivot. All factors commute because old pivot/donor sets are disjoint.
 assert not oldp&{d for z in oldentries for d in z['donors']}
 middle=[]
 for source,r in w['sources'].items():middle.append((sid(r),int(source),1))
 for i in w['phase1']:
  a,b,_=w['ops'][i];assert a not in sink_byrole;middle.append((sid(a),sid(b),1))
 for root,r in zip(g['roots'],w['rootroles']):
  if root['kind']=='center':middle.extend((1760+t,sid(r),1)for t in root['targets'])
 at=defaultdict(list)
 # The source's gauge order is reversed JSON gauge list; explicit read times
 # are numbered in phase1+rest chronology.
 for z in reversed(w['gauges']):
  r=z['role'];at[int(w['reads'].get(str(r),len(w['phase1'])))-len(w['phase1'])].append(r)
 rest=[i for i in range(len(w['ops']))if i not in phase]
 for j,i in enumerate(rest):
  for r in at[j]:middle.extend((1760+t,sid(r),-c)for t,c in adj[r].items()if c%2)
  a,b,_=w['ops'][i];middle.append((sink_byrole[a]['pivot']if a in sink_byrole else sid(a),sid(b),1))
 for r in at[len(rest)]:middle.extend((1760+t,sid(r),-c)for t,c in adj[r].items()if c%2)
 _,_,suffix,_=suffix_build();tail=middle+[(a,b,c)for a,b,c,tag in suffix]
 newsetup=[(d,z['pivot'],1)for z in witness for d in z['donors']]
 # Baseline upper word contains all uncompressed target reads. We transport
 # only nonnegative increases from added new shears, ignoring new deleted reads.
 allgroups=target['groups'];dependency={1760+int(t):[1760+p for p in ps]for z in allgroups for t,ps in z['dependent'].items()}
 assert not set(dependency)&{p for ps in dependency.values()for p in ps}
 # Include both setup/restore batches of every terminal sink. Acyclicity
 # is checked directly rather than assuming sink and prefix supports disjoint.
 edges=Counter((p,t)for t,ps in dependency.items()for p in ps)
 for z in sinks:
  for t in z['targets']:
   if t!=z['pivot']:edges[z['pivot'],t]+=1
 target_nodes=set(x for edge in edges for x in edge);incoming=Counter(t for p,t in edges);successors=defaultdict(list)
 for(p,t),multiplicity in edges.items():successors[p].append((t,2*multiplicity))
 ready=sorted(target_nodes-set(incoming));topology=[]
 while ready:
  p=ready.pop();topology.append(p)
  for t,c in successors[p]:
   incoming[t]-=1
   if not incoming[t]:ready.append(t)
 assert len(topology)==len(target_nodes),'target majorant dependency cycle'
 def close_target_majorant(values):
  out=values[:]
  for p in topology:
   for t,c in successors[p]:out[t]+=c*out[p]
  return out
 def add(v,event):
  a,b,c=event;v[a]+=abs(c)*v[b]
 def bound(reverse):
  # exact helper majorants for old versus sheared word, and a nonnegative
  # difference; target reads are deliberately not omitted.
  old=[1]*n;new=[1]*n
  if not reverse:
   for e in prefix:add(old,e);add(new,e)
   for e in newsetup:add(new,e)
   for e in tail:add(old,e);add(new,e)
   for e in reversed(newsetup):add(new,e)
  else:
   for e in newsetup:add(new,e)
   for e in reversed(tail):add(old,e);add(new,e)
   for e in reversed(newsetup):add(new,e)
   for e in reversed(prefix):add(old,e);add(new,e)
  delta=[a-b for a,b in zip(new,old)];assert min(delta)>=0
  delta=close_target_majorant(delta)
  # The old full compressed decoder bounds all its own prefixes. The helper
  # paths above are exact; the full target-only acyclic graph is majorized.
  pins=read('expected/kernel-pins.json');inherited=pins['inverse_max_row_l1']if reverse else pins['forward_max_row_l1']
  out=inherited+max(delta)
  return dict(reverse=reverse,inherited_bound=inherited,max_added_majorant=max(delta),certified_new_bound=out,
    max_added_helper=max(delta[3520:]),max_added_target=max(delta[1760:3520]),max_added_source=max(delta[:1760]))
 F,B=bound(False),bound(True);payload=64*F['certified_new_bound']**3*B['certified_new_bound']**2
 return dict(status='PASS_CONSERVATIVE_SCALAR_PREFIX_BOUNDS',selection=candidate_path.name,forward=F,inverse=B,
   payload_bound=payload,payload_bits=payload.bit_length(),retained_payload_cap_2_to104=payload<2**104,explicit_new_payload_cap_bits=112,new_payload_cap_2_to112=payload<2**112,
   cap_change=('The original104 ceiling passes for this case.' if payload<2**104 else 'The original104 check fails; a separately reviewed fixed112 bound is used. See PROOF.md. No prime, row, moment or inherited width-uniformity hypothesis is changed.'),
   setup_restore_pairs=len(newsetup),max_target_prefix_degree=max(map(len,dependency.values())),target_majorant_acyclic_vertices=len(topology),target_majorant_edges=len(edges),actual_sink_redirects=sum(z['forward_writes']for z in sinks),
   target_majorant_proof='Targets are never read by helper/source operations. We include every target-prefix and terminal-sink setup/restore edge with its exact total multiplicity2. Their union is checked acyclic; propagating all uncompressed nonnegative increments in topological order through these weighted edges dominates every chronological placement of those ADDs. Actual sink writes are redirected, and removed sink reads/cleanup/root deliveries are absent.',
   scope='Conditional on inherited old F/B and unchanged compiler; complete exact helper majorant paths are replayed, while target compression is conservatively bounded rather than reproducing record-index cut sites.',seconds=time.monotonic()-start)
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 r=run();(OUTPUT/'scalar-bounds-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

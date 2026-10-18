"""Deterministically regenerate the corrected literal owners, standard library only.

No optimizer, NumPy or SciPy is imported. The compact integer primal is checked,
then integral networks split the source calls. Byte-identical outputs reuse the
pinned complete owner and independent literal receipts; --owner-check requests
a fresh retained whole-owner replay as well.
"""
from pathlib import Path
from array import array
from collections import Counter,defaultdict
import argparse,gzip,hashlib,json,time
from verify_aggregate import check,common,HERE,W,INV,LOCAL,P
from integral_network import copy_colors

def authenticate():
 pins=common.read(HERE/'SOURCE-PINS.json')
 for rel,digest in pins['repo_files'].items():
  if common.sha(P.parents[1]/rel)!=digest:raise ValueError('stale retained source '+rel)
 for rel in ('AGGREGATE-INTEGER-FLOW.json.gz','actual-t740-prefix/PROVIDERS.json',
             'actual-t740-prefix/PROFILE.json','actual-t740-prefix/PREFIX-REPACK.json',
             'actual-t740-prefix/OWNER-CHECK.json'):
  if common.sha(HERE/rel)!=pins['candidate_files'][rel]:raise ValueError('stale finite owner input '+rel)
 return pins

class Rows:
 def __init__(self,calls,task_width,task_bin,owner,child,port,order,dispatch,providers):
  self.calls,self.width,self.bin,self.owner,self.child,self.port=calls,task_width,task_bin,owner,child,port
  self.order,self.dispatch,self.providers=order,dispatch,providers
 def __len__(self):return len(self.calls)*408
 def __iter__(self):
  offset=array('B',[0])*len(self.owner)
  for t,tasks in enumerate(self.calls):
   pool=defaultdict(list);pid=self.dispatch[tuple(self.order[t])]
   for h,w in enumerate(self.providers[pid]['widths']):pool[w].append(h)
   call=[]
   for i in sorted(tasks,key=lambda i:(self.width[i],i)):
    w=self.width[i];h=pool[w].pop();b=self.bin[i];call.append((h,b,w))
   assert not any(pool.values())
   for h,b,w in sorted(call):
    z=offset[b];offset[b]+=w
    yield [t,h,self.owner[b],self.child[b],self.port[b],z]

def write_fill(path,rows):
 payload=hashlib.sha256();prefix=json.dumps({'columns':['time','helper','owner_replica','child','port','offset'],'dispatch_overrides':[]},sort_keys=True,separators=(',',':'))[:-1]+',"rows":['
 with path.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=1,mtime=0) as out:
  data=prefix.encode();out.write(data);payload.update(data)
  for j,row in enumerate(rows):
   data=((',' if j else '')+json.dumps(row,separators=(',',':'))).encode();out.write(data);payload.update(data)
  data=b']}\n';out.write(data);payload.update(data)
 return dict(rows=len(rows),sha256=common.sha(path),payload_sha256=payload.hexdigest())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--owner-check',action='store_true');a=ap.parse_args()
 pins=authenticate();cert=common.read(HERE/'AGGREGATE-INTEGER-FLOW.json.gz');primal=check(cert);S=cert['S'];G=cert['groups'];T=37*S
 c=common.context();order37=cert['order'];win=c.owner.windows(c.template,order37,37);groups=defaultdict(list)
 for (o,ch),(cap,lo,hi) in win.items():
  for p in range(112):groups[cap,lo,hi].append((o,ch,p))
 groupkeys=sorted(groups);assert [[*g,len(groups[g])] for g in groupkeys]==G
 # Source child windows sharing a physical family are pairwise disjoint.
 fw=defaultdict(list)
 for (o,ch),(cap,lo,hi) in win.items():fw[o,c.families[ch]].append((lo,hi))
 for intervals in fw.values():
  for j,(lo,hi) in enumerate(intervals):assert all(max(lo,l)>=min(hi,h) for l,h in intervals[j+1:])
 xg=defaultdict(list);zg=defaultdict(list)
 for gi,q,n in cert['x']:xg[gi].append((q,n))
 for gi,t,w,n in cert['z']:zg[gi].append((t,w,n))
 task_width=array('B');task_bin=array('I');bin_group=array('H');required=array('b');macro=[array('I') for _ in range(333)];bin_ranges=[]
 for gi,g in enumerate(G):
  bstart=len(bin_group);available=defaultdict(lambda:array('I'))
  for q,n in sorted(xg[gi]):
   widths=[w for w,k in zip(W,q) for _ in range(k)]
   for _ in range(n):
    b=len(bin_group);bin_group.append(gi);required.append(-1)
    for w in widths:
     i=len(task_width);task_width.append(w);task_bin.append(b);available[w].append(i)
  cursor=Counter()
  for t,w,n in sorted(zg[gi]):
   ids=available[w][cursor[w]:cursor[w]+n];assert len(ids)==n;macro[t].extend(ids);cursor[w]+=n
  assert all(cursor[w]==len(ids) for w,ids in available.items())
  assert len(bin_group)-bstart==g[3]*S;bin_ranges.append((bstart,len(bin_group)))
 assert len(task_width)==333*S*408
 actual=[array('I') for _ in range(333*S)];group_n={gi:g[3] for gi,g in enumerate(G)};stats=Counter();t0=time.monotonic()
 for t,indices in enumerate(macro):
  colors,stat=copy_colors(sorted(indices),task_bin,task_width,bin_group,group_n,S)
  for i,cp in colors.items():
   actual[S*t+cp].append(i);b=task_bin[i];gi=bin_group[b]
   if t==G[gi][2]:required[b]=max(required[b],cp)
  stats['flows']+=stat['flows'];stats['max_nodes']=max(stats['max_nodes'],stat['max_nodes']);stats['max_edges']=max(stats['max_edges'],stat['max_edges'])
  if t%40==0:print('PORTABLE_CALL_DECOMPOSITION',t,'seconds',round(time.monotonic()-t0,2),flush=True)
 assert all(len(call)==408 for call in actual)
 owners=array('H',[0])*len(bin_group);children=array('H',[0])*len(bin_group);ports=array('B',[0])*len(bin_group)
 for gi,(lo,hi) in enumerate(bin_ranges):
  base=groups[groupkeys[gi]];m=len(base)
  for j,b in enumerate(sorted(range(lo,hi),key=lambda b:(required[b],b),reverse=True)):
   cp=S-1-j//m;o,ch,p=base[j%m];assert cp>=required[b]
   owners[b]=o+37*cp;children[b]=ch;ports[b]=p
 order=[[s,r+37*cp] for s,r in order37 for cp in range(S)];dispatch={(s,r+37*cp):c.dispatch[s,r] for s,r in order37 for cp in range(S)}
 providers=common.read(HERE/'actual-t740-prefix/PROVIDERS.json')
 for provider in providers.values():provider['actual_paid_profile']={int(k):v for k,v in provider['actual_paid_profile'].items()}
 for pid,provider in providers.items():
  assert provider['widths']==[w-int(h in (389,397)) for h,w in enumerate(c.providers[pid]['widths'])]
  assert provider['actual_paid_profile']==LOCAL
 a.out.mkdir(parents=True,exist_ok=False)
 for name,obj in [('ORDER.json',order),('DISPATCH.json',[[s,r,dispatch[s,r]] for s,r in order]),('PROFILE.json',cert['profile']),('PROVIDERS.json',common.read(HERE/'actual-t740-prefix/PROVIDERS.json'))]:
  # The source profile file uses indented sorted-rank formatting.
  if name=='PROFILE.json':data=json.dumps({int(k):v for k,v in sorted(cert['profile'].items(),key=lambda kv:int(kv[0]))},indent=2)+'\n'
  else:data=json.dumps(obj,separators=(',',':'))+'\n'
  (a.out/name).write_text(data)
  assert common.sha(a.out/name)==pins['candidate_files']['actual-t740-prefix/'+name],('changed literal input',name)
 rows=Rows(actual,task_width,task_bin,owners,children,ports,order,dispatch,providers);made=write_fill(a.out/'COMPOSED-FILL.json.gz',rows)
 expected=common.read(HERE/'actual-t740-prefix/PREFIX-REPACK.json')['materialized']
 # Container bytes are provenance only: zlib streams may vary across runtimes.
 assert made['rows']==expected['rows'] and made['payload_sha256']==expected['payload_sha256'],('changed literal payload',made,expected)
 report=dict(status='PASS_STANDARD_LIBRARY_SEMANTIC_LITERAL_REPLAY',replicas=T,calls=333*S,roles=len(rows),physical=896*T+509,materialized=made,decomposition=dict(stats),primal=primal,reused_complete_owner_receipt_sha256=common.sha(HERE/'actual-t740-prefix/OWNER-CHECK.json'),reused_independent_literal_receipt=pins['external_receipts'].get('../staged-pair-review/OWNER-REVIEW.json'),fresh_retained_owner_check=False,scope='Fresh deterministic literal payload equality and exact integer networks. A separate fresh independent audit and full release are required.')
 if a.owner_check:
  fill={'columns':['time','helper','owner_replica','child','port','offset'],'dispatch_overrides':[],'rows':rows}
  result,_,_=c.owner.check(T,order,fill,dispatch,cert['profile'],c.plan,c.template,providers);report['fresh_retained_owner_check']=True;report['owner_check']=result
 (a.out/'PORTABLE-REPLAY.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('PORTABLE_REPLAY_PASS',json.dumps(made),flush=True)

if __name__=='__main__':main()

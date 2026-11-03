"""New signed-adjoint and literal initial-read cache from pinned inert word data."""
from pathlib import Path
import gzip,json,hashlib
from collections import defaultdict,Counter
from source_data import ROOT,SOURCE as S,OUTPUT
OUTPUT.mkdir(parents=True,exist_ok=True)
def read(n):
 b=(S/n).read_bytes()
 return json.loads(gzip.decompress(b)if n.endswith('.gz')else b)
def run():
 w=read('gen5bit/selected/bit/word_p12.json.gz');g=read('gen5bit/selected/bit/graph_p12.json');frames=read('gen5bit/selected/bit/frames_p12.json.gz')['frames'];ks=read('kernel-selection.json')
 alias={b:a for a,b in w['pairs']};recipient={a:b for a,b in w['pairs']};regs=sorted(set(range(17160))-alias.keys());phys={r:3520+i for i,r in enumerate(regs)};inverse={s:r for r,s in phys.items()}
 sid=lambda r:phys[alias.get(r,r)]
 phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
 adj=[{}for _ in range(17160)]
 for root,r in zip(g['roots'],w['rootroles']):
  for t in root['targets']:adj[r][t]=adj[r].get(t,0)+1
 for i in reversed(order):
  a,b,_=w['ops'][i]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 masks=[sum(1<<t for t,c in row.items()if c%2)for row in adj]
 gauges={z['role']:z for z in w['gauges']};last={};readcount=0
 for r in range(17160):
  if r in gauges:continue
  for t,c in adj[r].items():
   if c%2:last[r]=dict(record=readcount,scalar=[1760+t,sid(r),-c]);readcount+=1
 first={};logical_ops=defaultdict(list)
 for source,r in w['sources'].items():first.setdefault(alias.get(r,r),dict(kind='source',source=int(source),frame=w['source_frame'][int(source)]))
 for chron,i in enumerate(order):
  for r in w['ops'][i][:2]:
   logical_ops[r].append(dict(chronology=chron,op=i,frame=w['op_frame'][i]))
   first.setdefault(alias.get(r,r),dict(kind='gate',op=i,chronology=chron,logical_role=r,frame=w['op_frame'][i]))
 installed=[];mismatches=[]
 for z in ks['pairs']+ks['families']:
  p=z.get('pivot',z.get('a'));ds=z.get('donors',[z.get('b')]);roles=[inverse[s]for s in [p]+ds]
  x=masks[roles[0]]
  for r in roles[1:]:x^=masks[r]
  assert x==0 and masks[roles[0]]
  cut=max((last[r]for r in roles),key=lambda x:x['record']);assert cut['scalar']==z['cut_read']
  declared=z['first_frame_dims'];declared={p:declared[0],ds[0]:declared[1]}if isinstance(declared,list)else{int(k):v for k,v in declared.items()}
  for stream,dim in declared.items():
   role=inverse[stream];actual=frames[str(first[role]['frame'])]['dim']
   if actual!=dim:mismatches.append(dict(stream=stream,role=role,base_dimension=actual,selected_dimension=dim))
  installed.append(dict(pivot=roles[0],donors=roles[1:],physical_pivot=p,physical_donors=ds,rank=z['rank'],basis=z['basis'],declared_first_dimensions=declared,cut=cut))
 roles={}
 for r in regs:
  row=dict(stream=phys[r],response_hex=hex(masks[r]),initial_read_count=masks[r].bit_count()if r not in gauges else 0,first_base_use=first.get(r),last_initial_read=last.get(r),is_gauge=r in gauges)
  if r in recipient:
   other=recipient[r];row['reuse']=dict(recipient=other,gauge_frame=gauges[other]['frame'],gauge_dimension=gauges[other]['dim'],read_time=w['reads'][str(other)],last_donor_op=logical_ops[r][-1],first_recipient_op=logical_ops[other][0])
  roles[r]=row
 output=dict(source_head='10b40041d4ab8a6610083e95bc571aee3468bca2',helpers_before_sinks=len(regs),plain_initial_reads=readcount,last_plain_read=max(last.values(),key=lambda x:x['record']),installed_response_and_cut_checks=len(installed),base_vs_selected_first_dimension_mismatches=mismatches,roles=roles,installed_entries=installed,scope='Exact signed adjoint reduced mod2, literal plain-read cut triples and alias map. first_base_use is before selected descent transforms; installed first dimensions are separately declared and mismatches disclosed. No full aliased chronological geometry admission.')
 raw=json.dumps(output,separators=(',',':')).encode();(OUTPUT/'response-cache.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 summary={k:v for k,v in output.items()if k not in ('roles','installed_entries')};summary['cache_sha256']=hashlib.sha256((OUTPUT/'response-cache.json.gz').read_bytes()).hexdigest();(OUTPUT/'response-cache-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return output
if __name__=='__main__':run()

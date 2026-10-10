from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Independent PR325 finite ledger reconstruction from inert JSON only.
Prepared with substantial OpenAI assistance; Apache-2.0.
This recount does not establish containment, scalar replay, or admission.
"""
import json,base64,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict
if not __debug__: raise RuntimeError('Assertions required')
P=contract.BANK; I=contract.INERT
def read(name): return json.loads((I/name).read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
source=json.loads((I.parent/'SOURCES.json').read_text()); manifest=read('MANIFEST.json'); bound=[]
for x in source:
 n=x['path'].replace('/','__')
 if x['encoding']=='base64': raw=base64.b64decode((I/(n+'.b64')).read_text()); decoded=gzip.decompress(raw); assert decoded==(I/n[:-3]).read_bytes()
 else: raw=(I/(n+('.txt' if n.endswith('.py') else ''))).read_bytes()
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==x['git_blob']
 bound.append(dict(path=x['path'],url=x['url'],git_blob=x['git_blob'],sha256=sha(raw)))
w,g,F,k=(read('bitword__selected__bit__'+n+'_p10.json') for n in ('word','graph','frames','kchron'))
f=F['frames']; dim=lambda i:f[str(i)]['dim']; h=g['h']; v=g['v']; assert (h,v)==(20,960)
R=max(a for op in w['ops'] for a in op[:2])+1; pair=dict(w['pairs']); destinations=set(pair.values()); physical=sorted(set(range(R))-destinations)
assert len(pair)==len(w['pairs'])==len(destinations) and not (set(pair)&destinations)
assert all(0<=a<R and 0<=b<R for a,b in pair.items())
# Work from fresh role IDs and their exact current operation order.
first=set(w['phase1']); order=sorted(first)+[i for i in range(len(w['ops'])) if i not in first]
incident=defaultdict(list)
for i in order:
 for role in w['ops'][i][:2]: incident[role].append(w['op_frame'][i])
for role,frame in zip(w['rootroles'],w['root_frame']):incident[role].append(frame)
gauges={x['role']:x['frame'] for x in w['gauges']}; src={role:int(s) for s,role in w['sources'].items()}
def histogram(path):
 d=list(map(dim,path)); assert all(a<=b for a,b in zip(d,d[1:]));return Counter(b-a for a,b in zip(d,d[1:]) if b>a)
internal=Counter(); widths={}; chains=hashlib.sha256(); gauge_counts=Counter()
for role in physical:
 start=gauges.get(role,w['source_frame'][src[role]] if role in src else None)
 path=([start] if start is not None else [])+incident[role]
 if role in pair:
  alias=pair[role];path+=[gauges[alias]]+incident[alias]
 dims=([0] if start is None else [])+[dim(i) for i in path]+[20]
 assert all(a<=b for a,b in zip(dims,dims[1:])),role
 internal.update(b-a for a,b in zip(dims,dims[1:]) if b>a)
 if role in src:internal[1]+=1
 entrance=dim(gauges[role]) if role in gauges else 0; widths[role]=20-entrance
 if entrance:gauge_counts[entrance]+=1
 chains.update(json.dumps([role,dims],separators=(',',':')).encode()+b'\n')
copy=Counter(dim(w['root_frame'][j]) for j,r in enumerate(g['roots']) if r['kind']=='center');internal.update(copy)
source_gaps=Counter()
for e in k['entries']:
 source_gaps.update(histogram(e['carrier_chain']));source_gaps.update(histogram(e['passive_chain']))
# Targets independently receive dirty compensation, roots, and source deliveries.
targets=[[] for _ in range(v)]
# Stable original reversed-gauge order resolves equal read positions.
for e in sorted(reversed(w['gauges']),key=lambda e:w['reads'].get(str(e['role']),len(first))):
 for target in e['targets']: targets[target].append(e['frame'])
deliveries=defaultdict(list)
for e in k['entries']: deliveries[e['deliver_after_root']].append(e)
for j,root in enumerate(g['roots']):
 if root['kind']=='side':
  for target in root['targets']:targets[target].append(w['root_frame'][j])
 for e in deliveries[j]:
  for target in e['receivers']:targets[target].append(e['deliver_frame'])
target_gaps=Counter()
for path in targets:
 d=[0]+list(map(dim,path))+[19];assert all(a<=b for a,b in zip(d,d[1:]));target_gaps.update(b-a for a,b in zip(d,d[1:]) if b>a)
helper=internal+source_gaps+target_gaps; paid=Counter({r:5*n for r,n in helper.items()});paid.update({r:1920 for r in [4,19,38,42]})
width=Counter(widths.values());total_width=sum(widths.values());assert 60*total_width%100==0
banks=60*total_width//100;stock=4*960*60+5*banks;literal={r:60*n for r,n in paid.items()}
assert max(literal)<50
pins=read('word-pins.json');compare={'physical_R':len(physical),'virtual_R':R,'reuse_pairs':len(pair),'banked_calls':sum(paid.values()),'banked_rank_mass':sum(r*n for r,n in paid.items()),'local_paid_rank_mass':sum(r*n for r,n in helper.items()),'banks_per_stage':banks,'literal_stock':stock}
assert all(pins[n]==x for n,x in compare.items())
peer=json.loads((I.parent/'LEDGER.json').read_text())['pr325']
for name,value in [('helper',helper),('internal',internal),('source',source_gaps),('target',target_gaps),('residual_families',width)]:assert {int(k):v for k,v in peer[name].items()}==value
result={'status':'PASS_INDEPENDENT_FINITE_BASE_LEDGER_NOT_SOURCE_ADMISSION','source_head':'0eca9340a3df6141b8e71a41638c3937b3522888','source_bindings':bound,'physical_roles':physical,'role_residual_widths':widths,'inventory':width,'gauges':gauge_counts,'helper_internal':internal,'source':source_gaps,'target':target_gaps,'helper':helper,'normalized_paid':paid,'literal_histogram':literal,'literal_calls':sum(literal.values()),'literal_rank_mass':sum(r*n for r,n in literal.items()),'literal_stock':stock,'banks_per_stage':banks,'deficit':100*stock-sum(r*n for r,n in literal.items()),'copy_rank_counts':copy,'role_dimension_chain_sha256':chains.hexdigest(),'pin_comparisons':compare,'checker_sha256':sha(Path(__file__).read_bytes()),'scope':'Exact count from current PR325 physical role chains, without old role selections; rational source nesting and scalar correctness delegated to fresh independent admission.'}
(P/'BASE-LEDGER.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({x:result[x] for x in ['status','inventory','helper','literal_calls','literal_rank_mass','literal_stock','banks_per_stage','deficit']},indent=2))

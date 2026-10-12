"""Emit a stage-dependent whole-owner template from freshly compiled local words."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,hashlib,copy
ROOT=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();BASE=R/'local';P=ROOT;O=R/'mixed';O.mkdir(exist_ok=False)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
variants={name:dict(canonical=read(BASE/name/'split-centres/CANONICAL-WORD.json.gz'),programs=read(BASE/name/'split-centres/LOCAL-PROGRAMS.json.gz'),checks=read(BASE/name/'split-centres/LOCAL-CHECKS.json'),recipes=read(BASE/name/'split-centres/CLIFFORD-RECIPES.json'),adapters=read(BASE/name/'split-centres/RESIDUAL-ADAPTERS.json')) for name in ['baseline','middle']};parent=read(BASE/'baseline/split-centres/GLOBAL-TEMPLATE.json.gz');t=copy.deepcopy(parent);ph=read(BASE/'baseline/work/complex-nine-native/DATA-PHASES.json');roles=read(P/'data/COLORED-OWNERS.json.gz');bycall=defaultdict(dict);sigmas={}
def basis(q):
 z=next(i for i in range(9) if not(q>>i)&1);a=q^(1<<z);order=list(range(9));order[z],order[0]=order[0],order[z];return [(1<<i)^(a if(a>>i)&1 else 0) for i in order]+[1<<i for i in range(9,73)]
for z in roles:
 s,rep,h=z['stage'],z['replica'],z['helper'];cp=z['copy'];port=cp%120;i=z['child'];off=z['offset'];w=z['width'];c=variants['middle' if s==4 else 'baseline']['canonical'];assert w==9-len(c['frames'][c['start'][240+h]])
 B=basis(c['ports'][port]);pending=list(map(int,ph['recipes'][port]['idle_children'][i]['orthogonal_axes']));occ=[B.index(v) for v in pending[off:off+w]];sp=[j for j in range(73) if j not in occ][:9-w];order=occ+sp+[j for j in range(73) if j not in occ+sp];sigma=[B[j] for j in order];assert len(set(sigma))==73;sigmas[hashlib.sha256(canon(sigma)).hexdigest()]=sigma
 bycall[s,rep][h]=[z['family'],[4,i,off,w,sp] if w<9 else [3,i,off]]
paid=Counter()
for c in t['calls']:
 name='middle' if c['stage']==4 else 'baseline';k=c['stage'],c['replica'];c['variant']=name;c['owners']=c['owners'][:240]+[bycall[k][h] for h in range(560)];assert len({f for f,_ in c['owners']})==800;c['local_program_sha256']=variants[name]['checks'][c['orientation']]['sha256'];paid.update({int(r):n for r,n in variants[name]['checks'][c['orientation']]['paid_profile'].items()})
remainders=read(P/'data/REMAINDERS.json.gz');t['idle_children']=[dict(child=z['child'],copy=z['copy'],replica=z['copy']//120,replicas=1,port=z['copy']%120,family=z['family'],pending_offset=z['offset'],rank=z['rank']) for z in remainders];paid.update(z['rank'] for z in remainders)
expected=read(P/'EXACT-ARITHMETIC.json');assert dict(paid)=={int(r):n for r,n in expected['profile'].items()}
t.update(version='stage-dependent-pooled-whole-owner-v1',live=7680,physical=8258,local_variants=variants,private_namespace={'centers':[7680,7696],'reserved_tableau':[7696,8256],'coefficient':[8256,8258]})
# Consumers must select the serialized variant on each call; remove the ambiguous
# single-word fields so an unchanged single-word consumer cannot silently accept it.
for k in ['local_programs','exact_local_clifford_recipe_sha256','residual_adapter_sha256']:t.pop(k,None)
t['hosting']=dict(rule='one-helper-per-physical-family-per-complete-invocation',pooled_slots=roles,banks=[0]*9,max_helpers_per_physical_family_per_call=1)
t['bank_padding']['families']=[];t['cover_final_correction']['families']=[0,7680];t['cover_final_correction']['charged_calls_per_cover']=7680
for e in t['execution_schedule']:
 if e['kind']=='bank_padding_cover_sweep':e['families']=[7680,7680]
 elif e['kind']=='translate_every_live_family':e.update(t['cover_final_correction'])
raw=canon(t);(O/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0));(O/'ACTUAL-SIGMAS.json.gz').write_bytes(gzip.compress(canon(sigmas),mtime=0));receipt=dict(status='EMITTED_MIXED_STAGE_TEMPLATE',template_sha256=hashlib.sha256(raw).hexdigest(),global_profile=dict(sorted(paid.items())),live=7680,physical=8258,sigma_count=len(sigmas),variant_calls=dict(Counter(c['variant'] for c in t['calls'])),scope='Emission only. Independent owner, finite invoice and normalized global prefix admission required.');(O/'HOSTED.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)

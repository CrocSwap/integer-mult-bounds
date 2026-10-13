"""Bind the new supplier to the unchanged verified 112-port data controller.

The parent uses one dedicated bank per helper and stage. Each of its eight
complete invocations uses a disjoint width-w block; the residual bank frame is
listed literally. The final whole-owner derivative removes every such bank.
All inherited data routes and exact data phase recipes remain byte-identical.
"""
import argparse
import copy
import gzip
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--data-base',type=Path,required=True)
ap.add_argument('--local',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):
 b=json.dumps(obj,sort_keys=True,separators=(',',':')).encode();p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
 return hashlib.sha256(b).hexdigest()
assert not a.out.exists(),'Output must be new'
old=read(a.data_base/'split-centres/GLOBAL-TEMPLATE.json.gz')
oldcan=read(a.data_base/'split-centres/CANONICAL-WORD.json.gz')
can=read(a.local/'CANONICAL-WORD.json.gz');checks=read(a.local/'LOCAL-CHECKS.json');programs=read(a.local/'LOCAL-PROGRAMS.json.gz')
V,H,R=can['v'],can['h'],can['R'];C=len(can['centers']);M,T,L,K=73,8,9,4
assert(V,H,C)==(112,9,8)and can['ports']==oldcan['ports']
widths=[H-len(can['frames'][f])for f in can['start'][2*V:]];assert len(widths)==R
local_H={int(r):n for r,n in checks['forward']['paid_profile'].items()}
assert all({int(r):n for r,n in z['paid_profile'].items()}==local_H for z in checks.values())
assert sum(r*n for r,n in local_H.items())==2*V*(H-1)+64+sum(widths)
D=a.out/'split-centres';D.mkdir(parents=True)
required=('CANONICAL-WORD.json.gz','FULL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','INDEPENDENT-LOCAL-REPLAY.json')
for name in required:assert(a.local/name).is_file()
for p in a.local.iterdir():
 if p.is_file():shutil.copyfile(p,D/p.name)
shutil.copyfile(a.local/'INDEPENDENT-LOCAL-REPLAY.json',D/'INDEPENDENT-REPLAY.json')
for rel in('work/complex-nine-native/DATA-PHASES.json',*[f'work/pr361/code/engines/{n}'for n in('moment.py','base_two_moment.py','outer.py')]):
 dst=a.out/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.data_base/rel,dst)
DATA=2*K*T*V;W=DATA+L*R;P=W+R+C+2
t=copy.deepcopy(old);t.update(version='round20-new-supplier-dedicated-bank-parent-v1',live=W,physical=P,local_programs=programs)
t['private_namespace']={'centers':[W,W+C],'reserved_tableau':[W+C,W+C+R],'coefficient':[P-2,P]}
for c in t['calls']:
 s,rep=c['stage'],c['replica'];owners=copy.deepcopy(c['owners'][:2*V])
 for helper,w in enumerate(widths):
  family=DATA+s*R+helper
  route=[2,rep]if w==9 else[2,rep*w,w,list(range(T*w,T*w+9-w))]
  owners.append([family,route])
 assert len(owners)==len({f for f,_ in owners})==2*V+R
 c['owners']=owners;c['local_program_sha256']=checks[c['orientation']]['sha256']
bank_children=[];pad=Counter()
for s in range(L):
 for helper,w in enumerate(widths):
  f=DATA+s*R+helper;axes=list(range(T*w,M));rank=len(axes)
  assert 0<rank<52
  bank_children.append(dict(family=f,rank=rank,axis_indices=axes,orthogonal_axes=[1<<j for j in axes]))
  pad[rank]+=1
t['bank_padding']={'families':list(range(DATA,W)),'children':bank_children,
 'semantics':'Each listed complement frame is applied once after the eight disjoint residual blocks of that dedicated bank. The final hosted derivative has empty families and children.'}
t['cover_final_correction'].update(families=[0,W],charged_calls_per_cover=W)
for i,e in enumerate(t['execution_schedule']):
 if e['kind']=='bank_padding_cover_sweep':
  t['execution_schedule'][i]={'kind':'bank_padding_cover_sweep','families':[DATA,W],'children_source':'bank_padding.children'}
 elif e['kind']=='translate_every_live_family':e.update(t['cover_final_correction'])
t['exact_data_phase_recipe_sha256']=sha(a.out/'work/complex-nine-native/DATA-PHASES.json')
t['exact_local_clifford_recipe_sha256']=sha(D/'CLIFFORD-RECIPES.json')
t['residual_adapter_sha256']=sha(D/'RESIDUAL-ADAPTERS.json')
t['supplier_substitution']={'parent_template_sha256':sha(a.data_base/'split-centres/GLOBAL-TEMPLATE.json.gz'),
 'old_canonical_word_sha256':sha(a.data_base/'split-centres/CANONICAL-WORD.json.gz'),
 'new_canonical_word_sha256':sha(D/'CANONICAL-WORD.json.gz'),
 'exact_same_ports':True,'data_contract':'The same ordered 112 data ports and both complete-invocation identity-shear orientations feed the unchanged nine-stage controller. No old local program or helper profile is reused.'}
t['route_semantics']['helper']='Dedicated family DATA+stage*R+helper; one helper per bank per complete invocation. Width-nine route[2,replica] uses axes9*replica..9*replica+8. Width-w entering route[2,w*replica,w,spectators] uses the disjoint residual block and paid normalization wrappers; spectator axes start at8*w, beyond all residual blocks.'
paid=Counter(pad)
for c in t['calls']:
 for r,n in checks[c['orientation']]['paid_profile'].items():paid[int(r)]+=n
for z in t['idle_children']:paid[z['rank']]+=z['replicas']
mass=sum(r*n for r,n in paid.items());assert M*W-mass==2560 and M*M>2*max(paid)**2
assert t['recipe']==old['recipe'] and t['idle_children']==old['idle_children']
assert t['execution_schedule'][:30]==old['execution_schedule'][:30]
assert all(c['owners'][:2*V]==oc['owners'][:2*V]for c,oc in zip(t['calls'],old['calls']))
th=dump(D/'GLOBAL-TEMPLATE.json.gz',t)
report=dict(status='BOUND_NEW_LOCAL_SUPPLIER_TO_UNCHANGED_DATA_CONTROLLER',R=R,v=V,m=M,
 live=W,physical=P,rank_mass=mass,deficit=2560,global_profile=dict(sorted(paid.items())),
 bank_remainder_profile=dict(sorted(pad.items())),bank_assignments=L*T*R,
 global_template_sha256=th,local_program_checks=checks,
 canonical_word_sha256=sha(D/'CANONICAL-WORD.json.gz'),exact_phase_receipt_sha256=sha(D/'CLIFFORD-REVIEW.json'),
 scope='The new local programs and phase/normalization artifacts are hash-bound to the unchanged data controller. Every dedicated bank and complement frame is explicit. The final whole-owner placement and independent scalar/finite recount are supplied separately; this file does not assert an old finite invoice.')
dump(D/'INTEGRATION.json',report)
print(json.dumps({k:report[k]for k in('status','R','live','physical','global_profile','bank_remainder_profile')},indent=2),flush=True)

"""Materialize the omitted generated PR558 parent, then require its reviewed hash.

The integrated review contains the native inputs and INTEGRATION.json but
omits GLOBAL-TEMPLATE.json.gz. This is only the deterministic template
binding from the inherited prepare_supplier_base.py; no old circuit or
phase calculation is rerun. The whole exact payload must match the review.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import shutil

assert __debug__, 'Assertions required'
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--source',type=Path,required=True)
ap.add_argument('--baseline',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not a.out.exists()
base=a.out/'complex-global/base'
shutil.copytree(a.baseline/'complex-global/base',base)
d=base/'split-centres'
parent=a.source/'vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz'
old=read(parent);can=read(d/'CANONICAL-WORD.json.gz')
checks=read(d/'LOCAL-CHECKS.json');programs=read(d/'LOCAL-PROGRAMS.json.gz')
v,h,r=can['v'],can['h'],can['R'];c=len(can['centers']);m,t,l,k=73,8,9,4
assert(v,h,r,c)==(112,9,504,8)
widths=[h-len(can['frames'][f])for f in can['start'][2*v:]]
data=2*k*t*v;live=data+l*r;physical=live+r+c+2
word=copy.deepcopy(old)
word.update(version='round20-new-supplier-dedicated-bank-parent-v1',live=live,physical=physical,local_programs=programs)
word['private_namespace']={'centers':[live,live+c],'reserved_tableau':[live+c,live+c+r],'coefficient':[physical-2,physical]}
for call in word['calls']:
 s,rep=call['stage'],call['replica'];owners=copy.deepcopy(call['owners'][:2*v])
 for helper,w in enumerate(widths):
  route=[2,rep]if w==9 else[2,rep*w,w,list(range(t*w,t*w+9-w))]
  owners.append([data+s*r+helper,route])
 call['owners']=owners;call['local_program_sha256']=checks[call['orientation']]['sha256']
children=[]
for s in range(l):
 for helper,w in enumerate(widths):
  axes=list(range(t*w,m))
  children.append(dict(family=data+s*r+helper,rank=len(axes),axis_indices=axes,orthogonal_axes=[1<<j for j in axes]))
word['bank_padding']={'families':list(range(data,live)),'children':children,
 'semantics':'Each listed complement frame is applied once after the eight disjoint residual blocks of that dedicated bank. The final hosted derivative has empty families and children.'}
word['cover_final_correction'].update(families=[0,live],charged_calls_per_cover=live)
for i,e in enumerate(word['execution_schedule']):
 if e['kind']=='bank_padding_cover_sweep':word['execution_schedule'][i]={'kind':'bank_padding_cover_sweep','families':[data,live],'children_source':'bank_padding.children'}
 elif e['kind']=='translate_every_live_family':e.update(word['cover_final_correction'])
word['exact_data_phase_recipe_sha256']=sha(base/'work/complex-nine-native/DATA-PHASES.json')
word['exact_local_clifford_recipe_sha256']=sha(d/'CLIFFORD-RECIPES.json')
word['residual_adapter_sha256']=sha(d/'RESIDUAL-ADAPTERS.json')
word['supplier_substitution']={'parent_template_sha256':sha(parent),
 'old_canonical_word_sha256':sha(a.baseline/'complex-global/controller-input/split-centres/CANONICAL-WORD.json.gz'),
 'new_canonical_word_sha256':sha(d/'CANONICAL-WORD.json.gz'),
 'exact_same_ports':True,'data_contract':'The same ordered 112 data ports and both complete-invocation identity-shear orientations feed the unchanged nine-stage controller. No old local program or helper profile is reused.'}
word['route_semantics']['helper']='Dedicated family DATA+stage*R+helper; one helper per bank per complete invocation. Width-nine route[2,replica] uses axes9*replica..9*replica+8. Width-w entering route[2,w*replica,w,spectators] uses the disjoint residual block and paid normalization wrappers; spectator axes start at8*w, beyond all residual blocks.'
raw=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
expected=read(d/'INTEGRATION.json')['global_template_sha256']
assert hashlib.sha256(raw).hexdigest()==expected=='7db047a427a7979d69e163c78a1e32bd445628fb86723e131a3138361355a9c3'
(d/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0))
print('PASS_EXACT_REVIEWED_PARENT_TEMPLATE_RESTORED',expected)

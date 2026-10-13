"""Frozen earlier-cut kernel constructor; Apache-2.0.

Prepared by OpenAI Codex. Direct supplier provenance: PR558, using PR552's
weighted word and the research session's exact earlier-cut suffix relation.
This script establishes scalar relation/frame construction only. Its output
requires fresh native, phase, mixed-owner, invoice and assembly verification.
"""
import argparse,copy,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
if not __debug__:raise SystemExit('Assertions required.')
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--gk-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sys.path.insert(0,str(a.gk_dir.resolve()));import gk_word as g,gk_common as co
g.V=co.V=112;g.DATA=co.DATA=7168
raw=gzip.decompress(a.input.read_bytes());recipe=json.loads(a.recipe.read_text());assert hashlib.sha256(raw).hexdigest()==recipe['input_content_sha256'];w=json.loads(raw);old=copy.deepcopy(w);P=g.profile(w);part=recipe['part'];index=recipe['index'];pivot=recipe['pivot'];E=co.basis(recipe['frame']);assert part=='B'and 224<=pivot<728 and str(pivot)not in w['start_extra']
regs=lambda e:e[1:3]if e[0]=='add'else e[1:2]
assert all(pivot not in regs(e)for e in w['A']+w['cut']+w['B'][:index]),'pivot must be untouched before the chosen cut'
cols=[{}for _ in range(728)]
for t in range(112):cols[112+t]={t:Q(1)}
def add(a,b,q):
 for j,x in b.items():
  z=a.get(j,Q(0))+q*x
  if z:a[j]=z
  else:a.pop(j,None)
for e in reversed(w['B'][index:]):
 if e[0]=='add':add(cols[e[2]],cols[e[1]],Q(e[3],e[4]))
 else:cols[e[1]]={t:x*Q(e[2],e[3])for t,x in cols[e[1]].items()}
residual=cols[pivot].copy();new=[]
for donor,coefficient in sorted(recipe['coefficients'].items(),key=lambda z:int(z[0])):
 donor=int(donor);q=Q(coefficient);assert donor!=pivot and donor not in range(112,224);assert q.denominator&(q.denominator-1)==0
 add(residual,cols[donor],-q);new.append(['add',donor,pivot,-q.numerator,q.denominator,list(E)])
assert not residual,'exact suffix dirty-response relation failed'
w['B']=w['B'][:index]+new+w['B'][index:];w['start_extra'][str(pivot)]=list(E);w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224];PP=g.profile(w);delta={r:PP[r]-P[r]for r in set(P)|set(PP)if PP[r]!=P[r]};assert delta=={int(r):n for r,n in recipe['profile_delta'].items()};assert sum(r*n for r,n in delta.items())==-len(E)
w['report']['local_profile']=dict(PP);encoded=g.dump(w);assert hashlib.sha256(gzip.decompress(encoded)).hexdigest()==recipe['output_content_sha256']
a.out.mkdir(parents=True,exist_ok=False);(a.out/'FULL-WORD.json.gz').write_bytes(encoded)
r=dict(status='PASS_FROZEN_EARLIER_CUT_KERNEL_CONSTRUCTION',input_content_sha256=hashlib.sha256(raw).hexdigest(),output_content_sha256=hashlib.sha256(gzip.decompress(encoded)).hexdigest(),pivot=pivot,changed_helper=pivot-224,entrance_frame=list(E),inserted_gates=len(new),exact_suffix_relation=True,pivot_untouched_before_cut=True,profile_before=dict(P),profile_after=dict(PP),delta=delta,helper_width_before=9,helper_width_after=9-len(E),scope='Literal scalar donor word, fixed-cut suffix response, exact frame chains and cleanup constructed. Native/all-column, phase, owner, invoice and assembly checks remain separate. No claimed homogeneous resource gain.')
(a.out/'KERNEL-CONSTRUCTION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

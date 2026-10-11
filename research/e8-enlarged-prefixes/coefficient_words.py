"""OpenAI Codex 2026-10-11: exact primitive-word microcheck for PR404 prefix extension.
Apache-2.0; imports inherited PR404 pure scalar lowerer with disclosed dyadic extension.
"""
import os,sys,json,hashlib
from pathlib import Path
from fractions import Fraction as Q
import argparse
p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
os.environ['CX_PINS']=str(args.output/'MINIMAL-PINS.json');sys.path.insert(0,str(args.package/'deps'))
import complex_scalars as C,complex_splice as S
src=('L',0);target=('L',1);work=('W',0)
def ax(row,other,q):
 for k,a in list(other.items()):
  z=row.get(k,Q(0))+q*a
  if z:row[k]=z
  else:row.pop(k,None)
def execute(word):
 reg={src:{'source':Q(1)},target:{'target':Q(1)},work:{'dirty_work':Q(1)}}
 for e in word:
  op=e[0];t=e[1]
  if op=='copy':reg[t]=dict(reg[e[2]])
  elif op=='clear':reg[t]={}
  elif op=='accumulate':ax(reg[t],reg[e[2]],Q(e[3]))
  elif op in ['double','halve','divide3']:
   a={'double':Q(2),'halve':Q(1,2),'divide3':Q(1,3)}[op];reg[t]={k:q*a for k,q in reg[t].items()}
  else:raise AssertionError(op)
 return reg
qs={Q(a,b) for a in [-2,-1,1,2] for b in [1,2,3,4,6,8] if abs(Q(a,b).numerator) in [1,2]}
recipes=[]
for q in sorted(qs):
 e=('add',target,src,q.numerator,q.denominator);word=S.lower_scalar(e);reg=execute(word)
 assert reg[src]=={'source':Q(1)} and reg[target]=={'target':Q(1),'source':q} and reg[work]=={}
 assert len(word)==C.coeff_steps(q)
 assert sum(e[0]=='halve' for e in word)==(q.denominator & -q.denominator).bit_length()-1
 recipes.append(dict(coefficient=str(q),literal_word=word,Gaussian_primitive_steps=len(word)))
word=S.lower_scalar(('add',target,src,1,8));at=[i for i,e in enumerate(word) if e[0]=='halve'][-1]
assert execute(word[:at]+word[at+1:])[target]!={'target':Q(1),'source':Q(1,8)}
z=dict(status='PASS_LITERAL_COEFFICIENT_WORDS',all_literal_coefficient_words=recipes,arbitrary_source_preserved=True,independent_dirty_work_erased=True,omitted_third_halving_rejected=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),lowerer_sha256=hashlib.sha256(Path(S.__file__).read_bytes()).hexdigest(),invoice_sha256=hashlib.sha256(Path(C.__file__).read_bytes()).hexdigest(),scope='Exact all-column microcheck of every signed coefficient in bounded palette. Every halving and source copy, accumulation, and work clear is a real paid primitive; macro equivalence composes with full native1021-column word replay.')
(args.output/'COEFFICIENT-WORDS.json').write_text(json.dumps(z,indent=2));print(z['status'],len(recipes))

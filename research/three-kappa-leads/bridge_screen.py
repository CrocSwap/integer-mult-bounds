#!/usr/bin/env python3
"""Source-bound four-axis/one-bridge test. Standard library, exact integers."""
from pathlib import Path
import importlib.util,json,hashlib,argparse
from check_inputs import authenticate
authenticate()
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def dot(a,b):return (a&b).bit_count()%2
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(8))for j in range(8)]for i in range(8)]
def eye():return [[int(i==j)for j in range(8)]for i in range(8)]
def shear(event):
 b=eye();s,d,c=event['src'],event['dst'],event['coefficient'];b[2*d][2*s]=c;b[2*s+1][2*d+1]=-c;return b

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',type=Path);a=ap.parse_args()
 src=load(ROOT/'research/rank7-idle-star-stream-obstruction/source.py','bound_source');context=src.load_context()
 # Reconstruct residuals from the pinned owner projection without executing its interpreter.
 recipe=context['recipe'];axes=[list(map(int,c['orthogonal_axes']))for c in recipe['idle_children']];used={i:set()for i in range(20)}
 for t,h,o,ch,port,offset in context['rows']:
  stage,rep=context['order'][t];pid=context['dispatch'][stage,rep%74];w=context['providers'][pid]['widths'][h]
  used[ch].update(range(offset,offset+w))
 residual={ch:[v for j,v in enumerate(basis)if j not in used[ch]]for ch,basis in enumerate(axes)}
 old=residual[12][:4];need(len(residual[12])==48,'terminal donor rank');need(all(dot(x,y)==int(i==j)for i,x in enumerate(old)for j,y in enumerate(old)),'orthonormal source four-frame')
 delta=0
 for v in old:delta^=v
 new=[delta^v for v in old];need(all(dot(x,y)==int(i==j)for i,x in enumerate(new)for j,y in enumerate(new)),'orthonormal changed dictionary')
 need(len(set(old)&set(new))==0,'genuine dictionary change')
 bridges=[e for e in context['template']['execution_schedule']if e['kind']=='bridge'];event=bridges[-1]
 need(event=={'kind':'bridge','src':0,'dst':1,'coefficient':1},'last actual bridge')
 B=shear(event);cases=[]
 for mask in range(16):
  character=0
  for i,v in enumerate(old):
   if mask>>i&1:character^=v
  before=sum(dot(character,v)for v in old)%4;after=sum(dot(character,v)for v in new)%4
  need((after-before)%4==2*dot(character,delta),'Z4 difference')
  D=eye();D[0][0]=(-1)**dot(character,delta)
  # All other factors between child12 and final bridge are unchanged, invertible,
  # and fix stream0. Thus the unique replacement is B'=B D^-1=B D.
  replacement=mm(B,D);need(mm(replacement,D)==B,'exact 8x8 intertwining')
  need((replacement==B)==(dot(character,delta)==0),'nonconstant bridge')
  cases.append({'mask':mask,'character':character,'phase_difference':(after-before)%4,'replacement':replacement})
 # For ANY axis dictionary (not just this four-frame), at x=0 all phases are 1.
 # Invertible fixed prefix/suffix force any address-independent replacement B'=B.
 need(cases[0]['replacement']==B,'trivial-character uniqueness')
 need(cases[1]['replacement']!=B,'wrong constant bridge negative control')
 # Dirty-state counterexample uses a basis vector; equality of matrices covers all values.
 e0=[1]+[0]*7;got=[sum(cases[1]['replacement'][i][j]*e0[j]for j in range(8))for i in range(8)]
 need(got!=[sum(B[i][j]*e0[j]for j in range(8))for i in range(8)],'dirty basis witness')
 out={'status':'SCOPED_NEGATIVE_ADDRESS_INDEPENDENT_SINGLE_BRIDGE','owner':0,'port':0,'child':12,'rank_before':48,'rank_after':48,'old_four_axes':old,'new_four_axes':new,'delta':delta,'bridge':event,'cases':cases,'rank_saving':0,'both_supplier_caps':'unchanged; no improved full candidate','address_dependent_bridge':'OPEN; formal solution only, no priced native realization','general_claim':'Any address-independent replacement matrix at one bridge is forced to equal the original by the trivial Fourier character, regardless of residual dictionary changes. Fixed-word injectivity source applies separately; not re-proved here.'}
 payload=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.write:a.write.write_text(payload)
 else:
  expected=json.loads((P/'BRIDGE-RESULT.json').read_text());need(out==expected,'receipt differs')
 print('PASS_BRIDGE_SCREEN 16_exact_intertwiners rank_delta=0 scalar_bridge_rejected_at_nonzero_character general_address_dependent_case=OPEN')
if __name__=='__main__':main()

"""Nominate the exact composition of PR627 factored ends and PR629 h4a.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
Credits: Jeremy Diviney (PR627), Jeremy Kothe (PR629 and K-triangle lineage),
DreamingOfClouds (cold-end framework), and all inherited NOTICE attributions.
This deterministic constructor nominates data; unchanged PR629 admission checks
must independently validate native words, phases, owners and exact pricing.
"""
import argparse,json,gzip,copy,importlib.util,hashlib
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
if not __debug__:raise RuntimeError('Assertions required')
ap=argparse.ArgumentParser();ap.add_argument('--base-hpe',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
PKG=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build',PKG/'code/build_cold_end.py');au=load('native',PKG/'code/hpe_audit_and_transport.py');read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
assert hashlib.sha256(gzip.decompress(args.base_hpe.read_bytes())).hexdigest()=='a51b37b5bd5e9e66ea14e9759f88cb6181bab041cb09aecd08e7a11956100016'
base=read(args.base_hpe);r=read(PKG/'data/nominations/PR629-JP8-RECIPE.json.gz');d=json.loads((PKG/'data/nominations/PR627-FACTORED-END.json').read_text())
assert hashlib.sha256((PKG/'data/nominations/PR629-JP8-RECIPE.json.gz').read_bytes()).hexdigest()=='b189542d8df48e2d55bea705c790d1c17433b76bde6a5c0aea7bc0a052a478e1'
assert hashlib.sha256((PKG/'data/nominations/PR627-FACTORED-END.json').read_bytes()).hexdigest()=='2067f48007b451dc970114d2449d4ad5377dadecd81a2c2b5ef74f9a178ad755'
d['additional_forward_insertions'].append([1665,['add',95,403,1,4,[265,137,96,6]]])
old=b.apply(copy.deepcopy(base),copy.deepcopy(r));r['premix']=d['premix']+r['premix'];r['forward_insertions']=sorted(r['forward_insertions']+d['additional_forward_insertions'],key=lambda x:x[0]);r['cold_ends'].update({str(z['helper']):z['terminal_frame'] for z in d['helpers']})
tail=[old['cleanup'][i][:-1]+[F] for i,F in old['early_cleanup']]+d['extra_tail'];r['cleanup']=tail;r['early_cleanup']=[[i,e[-1]]for i,e in enumerate(tail)]
w=b.apply(copy.deepcopy(base),r);P,_=au.state_maps(w['A']+w['cut']+w['B']+tail,716)
prefix=[];cold=set(range(224,716))-set(map(int,w['start_extra']))
def gate(t,s,c):return ['add',t,s,c.numerator,c.denominator,[]]
def prepend(e):
 prefix.insert(0,e);t,s,c=e[1],e[2],Q(e[3],e[4])
 for row in P:
  z=row.get(s,Q(0))+c*row.get(t,Q(0))
  if z:row[s]=z
  else:row.pop(s,None)
for h in (581,590):
 assert P[h].get(h)==1 and set(P[h])<=cold
 for j,c in list(P[h].items()):
  if j!=h:prepend(gate(h,j,-c))
 _,Pi=au.state_maps(prefix+w['A']+w['cut']+w['B']+tail,716);x={i:Pi[i][h]for i in range(716)if Pi[i].get(h)};assert set(x)<=cold and x[h]==1,x
 for j,c in x.items():
  if j!=h:prepend(gate(j,h,c))
 for t in range(112,224):
  if P[t].get(h):prepend(gate(t,h,-P[t][h]))
ended=set(map(int,w['helper_final']))
for j in ended:
 assert P[j]=={j:Q(1)},('badrow',j,P[j]);assert all(not P[i].get(j)for i in range(716)if i!=j and not 112<=i<224),('badcol',j)
print('repair prefix',prefix,flush=True)
full=[256,128,64,32,16,8,4,2,1];rest=[]
def emit(e):au.apply(e,P);rest.append(e)
def add(t,s,z):return ['add',t,s,z.numerator,z.denominator,full]
def unit(z):return z and abs(z.numerator)&(abs(z.numerator)-1)==0 and z.denominator&(z.denominator-1)==0
remaining=[j for j in range(716)if not 112<=j<224 and j not in ended]
for k,j in enumerate(remaining):
 pivot=next((i for i in remaining[k:]if unit(P[i].get(j,Q(0)))),None);assert pivot is not None,j
 if pivot!=j:
  emit(add(j,pivot,Q(1)));emit(add(pivot,j,Q(-1)));emit(add(j,pivot,Q(1)));emit(['scale',pivot,-1,1,full])
 z=P[j][j]
 if z!=1:emit(['scale',j,(1/z).numerator,(1/z).denominator,full])
 for i in remaining:
  if i!=j and P[i].get(j):emit(add(i,j,-P[i][j]))
assert all(P[j]=={j:Q(1)}for j in range(716)if not 112<=j<224)
r['premix']=prefix+r['premix'];r['cleanup']=tail+rest
meta=r['refactored_cleanup'];meta['cold_low_frame_ended_helpers']=sorted(map(int,r['cold_ends']));meta['premix_gates']=len(r['premix']);meta['premix_target_writes']=sum(112<=e[1]<224 for e in r['premix']);meta['forward_absorptions']=len(r['forward_insertions']);meta['forward_absorption_A_indices']=[len(r['premix'])+t+1+j for j,(t,e)in enumerate(r['forward_insertions'])];meta['lower_frame_gates']=len(tail)-34;meta['construction']='Experimental composition of PR629 h4a with PR627 factored helpers581+590 and delayed release cancellation; exact cold-basis correction and FULL Gauss-Jordan cleanup.'
w=b.apply(copy.deepcopy(base),r);enc=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode();raw=enc(w);assert hashlib.sha256(raw).hexdigest()=='45bcd9ebc2cee387d6ccc90eddae85d3af20f1a5b1574fa180a359020bf6c2eb';r['output_content_sha256']=hashlib.sha256(raw).hexdigest();out=args.out;out.mkdir(parents=True,exist_ok=False);(out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));(out/'RECIPE.json.gz').write_bytes(gzip.compress(enc(r),mtime=0));(out/'REPAIR.json').write_text(json.dumps(prefix,indent=2));print('READY',r['output_content_sha256'],w['report'],flush=True)

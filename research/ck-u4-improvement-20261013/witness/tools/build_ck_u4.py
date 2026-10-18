"""Transfer PR637's four premix-only cold ends to CK and reconstruct the exact FULL cleanup.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
The u4 premix and tail are Jeremy Kothe's PR637 CarrierBypass construction.
This nominates a word; unchanged native/global admission must verify it.
"""
from pathlib import Path
import json,gzip,copy,importlib.util
from fractions import Fraction as Q
import argparse,hashlib
ap=argparse.ArgumentParser();ap.add_argument('--base-hpe',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
p=Path(__file__).resolve().parents[1]
def mod(n,f):
 s=importlib.util.spec_from_file_location(n,f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=mod('b',p/'code/build_cold_end.py');a=mod('a',p/'code/hpe_audit_and_transport.py');read=lambda f:json.loads(gzip.decompress(Path(f).read_bytes()))
base=read(args.base_hpe);r=read(p/'data/nominations/PR637/CK-RECIPE.json.gz');j=read(p/'data/nominations/PR637/JP8-RECIPE.json.gz');old=read(p/'data/nominations/PR635-JP8-RECIPE.json.gz')
assert j['premix'][56:]==old['premix']
assert [[j['cleanup'][i],f] for i,f in j['early_cleanup'][:146]]==[[old['cleanup'][i],f] for i,f in old['early_cleanup']]
assert hashlib.sha256(gzip.decompress(args.base_hpe.read_bytes())).hexdigest()=='93228917343883327493cf8e8af68be06251be4db719039ae3ca8d54595f2be6'
r['premix']=j['premix'][:56]+r['premix'];tail=[r['cleanup'][i][:-1]+[F] for i,F in r['early_cleanup']]+[j['cleanup'][i][:-1]+[F] for i,F in j['early_cleanup'][146:]];r['cleanup']=tail;r['early_cleanup']=[[i,e[-1]]for i,e in enumerate(tail)]
for h in [233,265,425,441]:r['cold_ends'][str(h)]=j['cold_ends'][str(h)]
w=b.apply(copy.deepcopy(base),r);P,I=a.state_maps(w['A']+w['cut']+w['B']+tail,716);cold=set(range(224,716))-set(map(int,w['start_extra']))
from collections import Counter
ended=set(map(int,w['helper_final']))
for h in ended:
 assert P[h]=={h:Q(1)},(h,P[h]);assert all(not P[i].get(h)for i in range(716)if i!=h and not 112<=i<224),h
full=[256,128,64,32,16,8,4,2,1];rest=[]
def emit(e):a.apply(e,P);rest.append(e)
def add(t,s,z):return ['add',t,s,z.numerator,z.denominator,full]
def unit(z):return z and abs(z.numerator)&(abs(z.numerator)-1)==0 and z.denominator&(z.denominator-1)==0
remaining=[j for j in range(716)if not 112<=j<224 and j not in ended]
for k,h in enumerate(remaining):
 pivot=next((i for i in remaining[k:]if unit(P[i].get(h,Q(0)))),None);assert pivot is not None,h
 if pivot!=h:
  emit(add(h,pivot,Q(1)));emit(add(pivot,h,Q(-1)));emit(add(h,pivot,Q(1)));emit(['scale',pivot,-1,1,full])
 z=P[h][h]
 if z!=1:emit(['scale',h,(1/z).numerator,(1/z).denominator,full])
 for i in remaining:
  if i!=h and P[i].get(h):emit(add(i,h,-P[i][h]))
assert all(P[h]=={h:Q(1)}for h in remaining)
r['cleanup']=tail+rest;m=r['refactored_cleanup'];m['cold_low_frame_ended_helpers']=sorted(map(int,r['cold_ends']));m['premix_gates']=len(r['premix']);m['premix_target_writes']=sum(112<=e[1]<224 for e in r['premix']);m['lower_frame_gates']=len(tail)-34;m['forward_absorption_A_indices']=[len(r['premix'])+t+1+j for j,(t,e) in enumerate(r['forward_insertions'])];m['construction']='PR637 CarrierBypass four-end construction transferred unchanged to CK basis; exact FULL Gauss-Jordan remainder regenerated.'
w=b.apply(copy.deepcopy(base),r);import hashlib
enc=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode();raw=enc(w);r['output_content_sha256']=hashlib.sha256(raw).hexdigest();out=args.out;out.mkdir(parents=True,exist_ok=False);(out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));(out/'RECIPE.json.gz').write_bytes(gzip.compress(enc(r),mtime=0));print('READY',r['output_content_sha256'],w['report']['local_profile'],flush=True)

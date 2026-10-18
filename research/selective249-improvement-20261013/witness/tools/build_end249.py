"""Construct the raw249 terminal end from the pinned PR637 JP8 recipe.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
The zero-pairing cold row cancels carrier26 in the feasible inverse row;
the remaining ports share one dim4 accumulator. Native admission is separate.
"""
import json,gzip,copy,importlib.util,hashlib,argparse
from pathlib import Path
from fractions import Fraction as Q
ap=argparse.ArgumentParser();ap.add_argument('--base-hpe',type=Path,required=True);ap.add_argument('--source-recipe',type=Path,required=True);ap.add_argument('--code',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('b',args.code/'build_cold_end.py');a=load('a',args.code/'hpe_audit_and_transport.py')
read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
r=read(args.source_recipe);base=read(args.base_hpe);w=b.apply(copy.deepcopy(base),copy.deepcopy(r));source_tail=[w['cleanup'][i][:-1]+[f]for i,f in w['early_cleanup']];P,I=a.state_maps(w['A']+w['cut']+w['B']+source_tail,716)
def add(t,s,z,f):z=Q(z);return ['add',t,s,z.numerator,z.denominator,list(f)]
U=[256,128,64,32,16,8,6,1];B=[296,168,120,6]
targetfix={t:-sum(I[t].get(z,Q(0))*P[z].get(249,Q(0)) for z in range(112,224))/2 for t in range(112,224)}
prefix=[add(t,249,c,[])for t,c in targetfix.items()if c]
prefix+=[['scale',249,1,2,[]]]+[add(249,j,z,[])for j,z in [(256,1),(246,-1),(242,-1),(240,-2),(254,-2),(245,-2)]]
tail=[r['cleanup'][i][:-1]+[f]for i,f in r['early_cleanup']]
newtail=[['scale',31,4,1,B],add(31,29,-2,B),add(31,24,3,B),add(31,28,2,B),add(249,31,1,U),add(249,255,-2,U),add(249,25,-4,U),add(255,249,Q(1,4),U)]
P,_=a.state_maps(prefix+w['A']+w['cut']+w['B']+tail+newtail,716)
ended=set(map(int,w['helper_final']))|{249}
for h in ended:
 assert P[h]=={h:Q(1)},('row',h,P[h]);assert all(not P[j].get(h)for j in range(716)if j!=h),('col',h,{j:P[j][h]for j in range(716)if j!=h and P[j].get(h)})
print('ALL',len(ended),'ENDS ISOLATED',flush=True)
full=[256,128,64,32,16,8,4,2,1];rest=[]
def emit(e):a.apply(e,P);rest.append(e)
def unit(z):return z and abs(z.numerator)&(abs(z.numerator)-1)==0 and z.denominator&(z.denominator-1)==0
remaining=[j for j in range(716)if not 112<=j<224 and j not in ended]
for k,j in enumerate(remaining):
 pivot=next((i for i in remaining[k:]if unit(P[i].get(j,Q(0)))),None);assert pivot is not None,j
 if pivot!=j:
  emit(add(j,pivot,1,full));emit(add(pivot,j,-1,full));emit(add(j,pivot,1,full));emit(['scale',pivot,-1,1,full])
 z=P[j][j]
 if z!=1:emit(['scale',j,(1/z).numerator,(1/z).denominator,full])
 for i in remaining:
  if i!=j and P[i].get(j):emit(add(i,j,-P[i][j],full))
r['premix']=prefix+r['premix'];r['cleanup']=tail+newtail+rest;r['early_cleanup']=[[i,g[-1]]for i,g in enumerate(tail+newtail)];r['cold_ends']['249']=U
meta=r['refactored_cleanup'];meta['cold_low_frame_ended_helpers']=sorted(map(int,r['cold_ends']));meta['premix_gates']=len(r['premix']);meta['premix_target_writes']=sum(112<=e[1]<224 for e in r['premix']);meta['forward_absorption_A_indices']=[x+len(prefix)for x in meta['forward_absorption_A_indices']];meta['lower_frame_gates']=len(tail+newtail)-34;meta['construction']='PR637 plus raw249 cold end using a null-pairing row to eliminate dim7 carrier26 and factor a shared dim4 accumulator.'
r.pop('output_content_sha256',None);z=b.apply(copy.deepcopy(base),r);enc=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode();raw=enc(z);r['output_content_sha256']=hashlib.sha256(raw).hexdigest();out=args.out;out.mkdir(exist_ok=True);(out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));(out/'RECIPE.json.gz').write_bytes(gzip.compress(enc(r),mtime=0));(out/'ADDED.json').write_text(json.dumps({'prefix':prefix,'tail':newtail},indent=2));print('RAW',r['output_content_sha256'],z['report'],flush=True)

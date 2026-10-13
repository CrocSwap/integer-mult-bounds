"""Exact target-response slicing of the admitted static44 complex word."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,gzip,hashlib,json,sys
ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
p=Path(__file__).resolve().parents[1]/'vendor/static44';sys.path.insert(0,str(p/'gk'));import gk_word as G;import gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
w=json.load(gzip.open(a.source));original=copy.deepcopy(w);raw=json.load(gzip.open(p/'inputs/RAW504.json.gz'));frozen=len(w['A'])-len(raw['A']);V=112;N=224+w['report']['R'];response=[({r-V:Q(1)} if V<=r<2*V else {}) for r in range(N)];dead={'A':[],'B':[]}
for sec in ['B','cut','A']:
 for i in reversed(range(len(w[sec]))):
  e=w[sec][i];d=e[1];q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3]);identity=e[0]=='scale' and q==1
  if sec in dead and not V<=d<2*V and not(sec=='A' and i<frozen) and (not response[d] or identity):dead[sec].append(dict(index=i,gate=e,reason='identity_scale' if identity else 'zero_exact_target_response'))
  if e[0]=='add':
   s=e[2]
   for t,x in list(response[d].items()):
    y=response[s].get(t,Q(0))+q*x
    if y:response[s][t]=y
    else:response[s].pop(t,None)
  else:response[d]={t:q*x for t,x in response[d].items() if q*x}
for sec in dead:
 indices={x['index'] for x in dead[sec]};w[sec]=[e for i,e in enumerate(w[sec]) if i not in indices]
# Retain every advertised center-frame boundary even if a scalar identity was its last touch.
cur=[G.basis([w['ports'][r]]) if r<V else G.basis(w.get('start_extra',{}).get(str(r),[])) for r in range(N)]
for e in w['A']:
 for r in [e[1]]+([e[2]] if e[0]=='add' else []):assert G.span(cur[r])<=G.span(G.basis(e[-1]));cur[r]=G.basis(e[-1])
sentinels=[]
for r,F in zip(w['centers'],w['center_frames']):
 if cur[r]!=G.basis(F):
  assert G.span(cur[r])<=G.span(G.basis(F));e=['scale',r,1,1,list(F)];w['A'].append(e);sentinels.append(e)
w['cleanup']=[G.inverse(e,G.FULL) for e in reversed(w['A']+w['B']) if not V<=e[1]<2*V]
oldH=G.profile(original);newH=G.profile(w);assert G.widths_of(w)==G.widths_of(original);assert sum(r*n for r,n in oldH.items())==sum(r*n for r,n in newH.items())
w['report']['local_profile']=dict(newH);w['report']['local_rank_mass']=sum(r*n for r,n in newH.items())
blob=G.dump(w);blob=blob[:9]+bytes([255])+blob[10:];(a.out/'FULL-WORD.json.gz').write_bytes(blob)
r=dict(status='EXACT_TARGET_RESPONSE_SLICE_PENDING_INDEPENDENT_ADMISSION',source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),word_sha256=hashlib.sha256(blob).hexdigest(),removed=dead,sentinels=sentinels,before=dict(oldH),after=dict(newH),frozen_prefix=frozen,scope='Zero exact suffix response or identity scale; frame boundaries retained, cleanup regenerated. Local incidence/profile verified; independent arbitrary-input and physical admission still required.')
(a.out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print('SLICED',{k:len(v) for k,v in dead.items()},'sentinels',len(sentinels),'old',dict(oldH),'new',dict(newH),flush=True)

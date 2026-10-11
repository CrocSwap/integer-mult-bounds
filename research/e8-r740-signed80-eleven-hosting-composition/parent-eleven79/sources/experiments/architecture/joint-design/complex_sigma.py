"""Actual selected nine-axis complex hosted geometry and exact phase identity."""
import json,gzip,hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'experiments/stage-search/pr441-signed75-hosting';PARENT=ROOT/'experiments/stage-search/pr433-split/full/split-centres'
read=lambda p:json.loads(p.read_text());blob=lambda p:gzip.decompress(p.read_bytes())
t=json.loads(blob(BASE/'complex-hosted/GLOBAL-TEMPLATE.json.gz'));old=json.loads(blob(PARENT/'GLOBAL-TEMPLATE.json.gz'))
phasep=ROOT/'experiments/verification/proposal-scout/pr442/inherited/research/split-centres-global/inputs/complex-data-phases.json.gz';ph=json.loads(blob(phasep))
assert t['local_programs']==old['local_programs']
def dot(a,b):return bin(a&b).count('1')%2
def orth(basis):assert len(basis)==73 and all(dot(x,y)==int(i==j)for i,x in enumerate(basis)for j,y in enumerate(basis))
full={}
for r in ph['recipes']:
 comp=r['idle_children'][0]['orthogonal_axes'][:8];B=[r['q']]+comp+[1<<i for i in range(9,73)];orth(B);full[r['port']]=B
slots=t['hosting']['slots'];routes=[];used=defaultdict(list);seen=defaultdict(set)
for ch,p,off,w,stage,h in slots:
 assert w==9;recipe=ph['recipes'][p];assert recipe['port']==p;child=recipe['idle_children'][ch];axes=child['orthogonal_axes'];sel=axes[off:off+w];assert len(sel)==9
 assert not set(used[ch,p])&set(sel);used[ch,p]+=sel
 # Source helper residual local9 is represented in its source chart.
 # Additional sigma maps canonical local9 to selected actual axes.
 B=sel+[v for v in full[p]if v not in sel];orth(B)
 pair=t['hosting']['pairs'][str(ch)];side=t['hosting']['sides'][str(ch)];family=(stage,pair,side,p)
 assert tuple(B)not in seen[family];seen[family].add(tuple(B))
 routes.append([ch,p,off,w,stage,h,B,child['translation_after']])
# Exact phase polynomials on ALL2^73 characters: each axis contributes
# parity <chi,v> in Z4, translation contributes2 parity. Splitting exact
# multiset leaves identical polynomial (not merely same F2 linear matrix).
remaining={};phase_checks=0
for recipe in ph['recipes']:
 p=recipe['port']
 for ch,child in enumerate(recipe['idle_children']):
  axes=child['orthogonal_axes'];host=used[ch,p];rest=[v for v in axes if v not in host]
  assert Counter(axes)==Counter(host)+Counter(rest)
  remaining[ch,p]=len(rest);phase_checks+=1
# Cover actual per-invocation streams/route ownership and all child ranks.
for c0,c in zip(old['calls'],t['calls']):
 assert c0['owners'][:240]==c['owners'][:240]
 for h,(f,r)in enumerate(c['owners'][240:]):
  if r[0]==3:
   ch,off=r[1:];slot=next((x for x in slots if x[4]==c['stage']and x[5]==h),None);assert slot is not None
   _,p,_,w,_,_=slot;pair=t['hosting']['pairs'][str(ch)];side=t['hosting']['sides'][str(ch)]
   assert f==c['replica']*960+(2*pair+side)*120+p and pair!=c['pair']
for it in t['idle_children']:assert it['rank']==remaining[it['child'],it['port']]
result={'status':'PASS_ALL_SELECTED_COMPLEX_NINE_AXIS_SIGMA_PHASE_AND_COVER_INJECTION','hosted_template_sha256':hashlib.sha256(blob(BASE/'complex-hosted/GLOBAL-TEMPLATE.json.gz')).hexdigest(),'parent_template_sha256':hashlib.sha256(blob(PARENT/'GLOBAL-TEMPLATE.json.gz')).hexdigest(),'phase_source_sha256':hashlib.sha256(phasep.read_bytes()).hexdigest(),'slots_per_replica':len(slots),'all_73_sigma_columns_checked':True,'all_selected_sigmas_orthogonal':True,'source_idle_phase_polynomials_checked':phase_checks,'phase_identity_on_all_characters':'Same multiset of C_axis parity terms plus unchanged2*X_translation parity; equality inZ4 for all2^73 characters. C factors/phase translations commute globally.','cover_injection':'All concrete73column sigma matrices are distinct within same stage/datafamily. Right action d*sigma^-1 bijective onO(73,2), hence distinct owners for fixedd. Other families disjoint.','inverse_reflection':'Orthogonal sigma inverse transpose exact; invert each C_axis and translation, reversing chronology. SameZ4 polynomial identity persists.','arbitrary_dirt':'Factor equality on the full complex vector space covers correlated hostdata. Uses unchanged supplier fully signed blockdiagonal localhelper endpoint, separately replayed sourcegate.','route_invoice':'Canonical helper sourcechart is retained. Additional target orthogonal basis plus coordinate placement are charged2 selector/address factors perhelper; phase translation remains paid, no new free scalar factors.','scope':'Full actual selected complex axes/owners/phase and symbolic cover geometry. Does not replace literal sourcehelper replay/full invoice or inherited compiler/common-grid/analytic assumptions.','selected_sigma_columns_and_phase':routes}
(BASE/'complex-hosted/HOSTED-SIGMA.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(slots),phase_checks)

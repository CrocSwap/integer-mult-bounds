"""Independent witness-only replay; does not import the producer or its checker."""
from pathlib import Path
import gzip,json,hashlib,collections,sys
p,ph,out=map(Path,sys.argv[1:]);raw=p.read_bytes();t=json.loads(gzip.decompress(raw));b=ph.read_bytes();assert hashlib.sha256(b).hexdigest()==t['source_bindings']['data_phase'];phase=json.loads(b)
full=[]
for rec in phase['recipes']:
 basis=sorted({rec['q']}|{x for e in rec['idle_children']for x in e['orthogonal_axes']});assert len(basis)==89
 assert all(((x&y).bit_count()&1)==(i==j)for i,x in enumerate(basis)for j,y in enumerate(basis));full.append(basis)
idle={e['idx']:e for e in t['execution_schedule']if e['kind']=='idle'};seen=set();act=set();comps=collections.defaultdict(set);count=collections.Counter();rh=hashlib.sha256()
for c in t['calls']:
 for fam,route in c['owners'][240:]:
  kind,i,off,foot,w,spec=route;assert kind==5 and foot==9
  within=fam%1200;pair,port=divmod(within,240);side,port=divmod(port,120);assert pair==idle[i]['pair']
  axes=phase['recipes'][port]['idle_children'][idle[i]['phase_children'][side]]['orthogonal_axes'];active=axes[off:off+w];assert len(active)==w
  fp=active+([spec]if w==8 else[]);assert len(set(fp))==9 and set(fp)<=set(full[port])
  if w==8:assert spec not in axes
  for a in fp:assert(c['stage'],fam,a)not in seen;seen.add((c['stage'],fam,a))
  for a in active:assert(fam,a)not in act;act.add((fam,a))
  sigma=fp+[a for a in full[port]if a not in fp];assert len(sigma)==len(set(sigma))==89
  rh.update(json.dumps([c['stage'],c['replica'],fam,sigma],separators=(',',':')).encode());comps[i,fam].update(active);count[w]+=1
for c in t['idle_children']:
 fam=c['replica']*1200+(2*idle[c['idle']]['pair']+c['side'])*120+c['port'];axes=phase['recipes'][c['port']]['idle_children'][c['phase_child']]['orthogonal_axes'];paid={axes[k]for k in c['paid_complement_coordinates']};a=comps[c['idle'],fam]
 assert not(a&paid)and(a|paid)==set(axes)and len(paid)==c['rank']
z=dict(status='PASS_INDEPENDENT_CANONICAL_ORTHOGONAL_COMPLETION_AND_PAID_AXIS_PARTITION',input_sha256=hashlib.sha256(raw).hexdigest(),canonical_template_sha256=hashlib.sha256(json.dumps(t,sort_keys=True,separators=(',',':')).encode()).hexdigest(),phase_sha256=hashlib.sha256(b).hexdigest(),canonical_route_sigma_stream_sha256=rh.hexdigest(),helpers_by_active_width=dict(count),whole_footprint_cells=len(seen),globally_disjoint_active_cells=len(act),scope='Independent direct read of delivered witness; canonical full89 routing matrix constructed perhelper, Gram follows checkedbasis permutation. No emitter/auditor imports. Scalar/provider and runtime evidence separate.')
out.write_text(json.dumps(z,indent=2));print(json.dumps(z,indent=2))

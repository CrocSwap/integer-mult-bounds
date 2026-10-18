"""Normalize all nonzero helper entrances on full nine-axis footprints.
Emits explicit monomial events around each COMPLETE local program. Scalar
backward uses unchanged frame chronology and therefore the same wrappers.
"""
import argparse,gzip,json,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--canonical',type=Path,required=True);p.add_argument('--programs',type=Path,required=True);p.add_argument('--checks',type=Path,required=True);p.add_argument('--clifford',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(a.clifford.parent))
from clifford_exact import *
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
c=json.loads(gzip.decompress(a.canonical.read_bytes()));programs=json.loads(gzip.decompress(a.programs.read_bytes()));checks=json.loads(a.checks.read_text());n=c['h'];assert n==9
helpers={r:c['start'][r]for r in range(2*c['v'],2*c['v']+c['R'])if c['start'][r]};frames=set(helpers.values());adapters={};allcontrols={}
def fromrec(r):return diag(n,r['quadratic_rows'],r['linear_Z4']).then(perm(n,r['matrix_rows'])).then(xgate(n,r['offset'])).then(Op(n,identity(n),[('phase',r['phase'])]))
for f in sorted(frames):
 E=tuple(c['frames'][f]);phi=canonical_frame(n,E).adjoint().then(canonical_frame(n,c['frames'][1]));rec,_=lower_child(phi);assert rec['rank']==9-len(E);L=fromrec(rec['left']);R=fromrec(rec['right']);pre=R.adjoint();post=L.adjoint();got=pre.then(phi).then(post);want=fourier(n,range(rec['rank']));assert got.tab==want.tab
 for x in range(512):assert got.zero_state(x)==want.zero_state(x),(f,x)
 mon=[]
 for op in (pre,post):
  _,r=monomial(op);assert all(e[0]!='C'for e in op.circuit);columns=[];seen=set()
  for x in range(512):
   vec,d=op.zero_state(x);nz=[(i,v)for i,v in enumerate(vec)if v!=(0,0)];assert d==0 and len(nz)==1;row,v=nz[0];assert row not in seen and v in[(1,0),(-1,0),(0,1),(0,-1)];seen.add(row);columns.append([row,*v])
  mon.append(dict(recipe=r,circuit=op.circuit,columns=columns))
 bad={'omit_entry':phi.then(post),'omit_exit':pre.then(phi),'reverse_endpoint':pre.then(canonical_frame(n,c['frames'][1]).then(canonical_frame(n,E).adjoint())).then(post),'transformed_spectator':got.then(cgate(n,1<<rec['rank'])),'swap_wrappers':post.then(phi).then(pre)};controls={}
 for k,t in bad.items():
  witness=next((x for x in range(512)if t.zero_state(x)!=want.zero_state(x)),None);assert witness is not None,k;controls[k]=witness
 adapters[f]=dict(E=E,physical_width=9,active_width=rec['rank'],pre=mon[0],post=mon[1],all512columns=True);allcontrols[f]=controls
# Explicitly validate that the raw emitter did not touch a nonzero entrance in its zero phase.
for name,events in programs.items():
 assert digest(events)==checks[name]['sha256'], 'raw program/check hash mismatch'
 for e in events:
  if e==['phase','entry_adapters']:break
  if e[0]=='scalar':
   op=e[1];assert op[0]in('add','scale');regs=[op[1][1]]+([op[2][1]]if op[0]=='add'else[]);assert all(c['start'][r]==0 for r in regs)
 pre=[['monomial-wrapper','entry',r,f,adapters[f]['pre']['circuit']]for r,f in sorted(helpers.items())];post=[['monomial-wrapper','exit',r,f,adapters[f]['post']['circuit']]for r,f in sorted(helpers.items())]
 events=[e for e in events if not(e[0]=='adapter'and e[2]>=2*c['v'])]
 assert not any(e[0]=='adapter'and e[2]>=2*c['v']for e in events)
 programs[name]=pre+events+post;checks[name].update(raw_program_sha256=checks[name]['sha256'],sha256=digest(programs[name]),events=len(programs[name]),wrapper_helpers=len(helpers),helper_endpoint_adapter_markers_omitted=2*c['R'],wrapper_extra_real_component_primitive_bound=16*len(helpers),real_component_primitive_bound=checks[name]['real_component_primitive_bound']+16*len(helpers),wrapper_scope='16 real component primitives per AMBIENT scalar entry per changedhelper; in-place cycles using one complex temporary in existing coefficient workspace; no recursive Fourier child; full9 physical footprint')
raw=json.dumps(programs,sort_keys=True,separators=(',',':')).encode();(a.out/'NORMALIZED-PROGRAMS.json.gz').write_bytes(gzip.compress(raw,mtime=0));(a.out/'NORMALIZED-CHECKS.json').write_text(json.dumps(checks,indent=2));receipt=dict(status='EXACT_CANONICAL_ENTRANCE_NORMALIZATION',canonical_sha256=hashlib.sha256(a.canonical.read_bytes()).hexdigest(),raw_programs_sha256=hashlib.sha256(a.programs.read_bytes()).hexdigest(),normalized_programs_sha256=hashlib.sha256((a.out/'NORMALIZED-PROGRAMS.json.gz').read_bytes()).hexdigest(),clifford_sha256=hashlib.sha256(a.clifford.read_bytes()).hexdigest(),helpers=helpers,adapters=adapters,negative_controls=allcontrols,backward_convention='scalar inverse-transpose, same frame climbs; same helper Phi and wrappers',convention='column matrices; A.then(B)=B*A; Phi=T_FULL*T_E^-1; pre=R^-1,post=L^-1')
(a.out/'CANONICAL-WRAPPERS.json').write_text(json.dumps(receipt,indent=2));print('NORMALIZED PROGRAMS READY',len(helpers),'helpers',len(frames),'frames',flush=True)



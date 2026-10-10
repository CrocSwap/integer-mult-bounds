#!/usr/bin/env python3
"""Fresh admission of a p10 complex gcert candidate; no bit or kappa claim.
Exact scalar identity, labels, complete reflected splices, all finite invoices
and two rational moment engines are rerun. Prepared with OpenAI Codex; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
import argparse,collections,hashlib,importlib.util,json,pathlib,time
from copy import deepcopy
from fractions import Fraction as Q
HERE=pathlib.Path(__file__).resolve().parent
DEFAULT_SOURCE=HERE/'vendor/neutral/vendor/pr315'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(pathlib.Path(p).read_text())
def load(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,int) and x.bit_length()>4000:return str(x)
 if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [serial(v) for v in x]
 return x

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=pathlib.Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--source',type=pathlib.Path,default=DEFAULT_SOURCE);ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
 begun=time.monotonic();assert not args.output.exists();raw=args.input.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest==args.expected_sha256;c=json.loads(raw)
 geometry=read(HERE/'GEOMETRY.json');assert sha(HERE/geometry['path'])==geometry['sha256']
 geometry_text=(HERE/geometry['path']).read_text()
 for literal in geometry['required_literals']:assert literal in geometry_text
 deriv=read(HERE/'DERIVATION.json');mods={}
 for name,d in deriv.items():
  assert sha(HERE/d['source'])==d['source_sha256'] and sha(HERE/'code'/(name+'.py'))==d['derived_sha256']
  derived=(HERE/d['source']).read_text()
  for edit in d['parameterizations']:
   assert derived.count(edit['old'])==1;derived=derived.replace(edit['old'],edit['new'])
  assert derived.encode()==(HERE/'code'/(name+'.py')).read_bytes()
  mods[name]=load(HERE/'code'/(name+'.py'),'p10_supplier_'+name)
 for name in ('complex_scalars','complex_splice'):mods[name].configure(c)
 pins=read(args.source/'inputs/complex/source-pins.json');verified={};upstream={}
 for rel,pin in pins['files'].items():
  path=args.source/rel;assert sha(path)==pin['sha256'];verified[rel]=pin['sha256'];upstream[pin['upstream']]=path
 H=collections.Counter()
 for block in c['blocks'].values():H.update({int(r):n for r,n in block.items()})
 checks=mods['complex_labels'].replay_label_counts(c,dict(frames=len(c['frames']),gates={p:len(c[p]) for p in ('A','B')},histogram=dict(H)))
 H5=collections.Counter({r:5*n for r,n in H.items()});h,v,R=c['h'],c['v'],c['R'];m,W=5*h,4*v+R
 for r in (2*h-2,h-1,2*h+2,4):H5[r]+=2*v
 ledger=dict(histogram={str(r):n for r,n in sorted(H5.items())},calls=sum(H5.values()),rank_mass=sum(r*n for r,n in H5.items()),max_child=max(H5),deficit=m*W-sum(r*n for r,n in H5.items()),copy_calls=5*h,idle_calls=8*v)
 assert (m,h,v,c['cst'],ledger['deficit'],ledger['max_child'])==(100,20,960,360,2040,42)
 lines=upstream['Work/GCert/Chain/NetDef.lean'].read_text().splitlines();refs={};sourcepin='f010392c923279e3dd59ef3aa5fedad23affc5fd'
 for name in ['x01','y01','x12','y12','x23','y23','x34','y34','sfin','term']:
  indices=[i for i,line in enumerate(lines) if name+' :' in line];assert indices;i=indices[-1] if name=='sfin' else indices[0]
  refs[name]=dict(source='Work/GCert/Chain/NetDef.lean',anchor=name+' :',line=i+1,declaration_line=' '.join(x.strip() for x in lines[i:i+(2 if name=='sfin' else 1)]),url='https://github.com/jacobalansussman/wht-power-saving-lean/blob/'+sourcepin+'/Work/GCert/Chain/NetDef.lean#L'+str(i+1))
 chronology=['stage0','stage1','climbA','bridgeA','stage2','climbB','bridgeB','stage3','stage4','final_climbs','bridgeC','terminal_shifts','signed_exchange']
 manifest=dict(source_pin=sourcepin,parameters=dict(h=h,m=m,v=v,R=R,W_live=W,invocation_live=2*v+R),ledger=ledger,checks=checks,chronology=chronology,source_frame_equalities=refs)
 scalar=mods['complex_scalars'];splice=mods['complex_splice'];A=scalar.flat(c['A']);B=scalar.flat(c['B']);bill={};life={};programs={};controls=[]
 for ori in ('forward','backward'):
  bill[ori]=scalar.bill(scalar.inv_schedule(ori,A,B,c));life[ori]=scalar.lifecycle(scalar.inv_schedule(ori,A,B,c))
  events=list(splice.emit(c,ori));programs[ori]=splice.validate(events,c,ori,manifest,bill);controls.extend(splice.controls(events,c,ori,manifest,bill))
 global_contract=splice.global_contract(manifest);splice.validate_global(global_contract,manifest)
 mutations=[('wrong_helper_owner',lambda x:x['stage_recipe'][1].__setitem__('helper_owner','s1^(-1)(d)')),('rank_only_frame',lambda x:x['exact_frame_bindings']['x23'].__setitem__('declaration_line','same rank only')),('scratch_alias',lambda x:x['scratch_namespace'].__setitem__('centers',[W-1,W+h-1])),('wrong_live_normalization',lambda x:x.__setitem__('recursive_volume_denominator',W+R+h+1)),('free_RAM',lambda x:x.__setitem__('primitive_policy','free_RAM')),('missing_tableau',lambda x:x.__setitem__('physical',W+h+1))]
 for name,fn in mutations:
  bad=deepcopy(global_contract);fn(bad)
  try:splice.validate_global(bad,manifest)
  except ValueError as error:controls.append(dict(name=name,rejected=True,reason=str(error)))
  else:raise ValueError('global mutation accepted '+name)
 guard=load(HERE/'finite_guard.py','p10_finite_guard').finite_guard(manifest,bill,mods['complex_basis'])
 assert mods['complex_labels'].scalar_word([(1,0,1),(0,1,-1),(0,2,1),(3,1,-1),(1,0,1),(3,1,1),(0,2,-1),(2,3,-1),(3,2,1),(1,3,-1),(2,0,1)])==[[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]]
 print('PASS both complete reflected scalar splices, recomputed p10 paid ledgers, guard and 20 mutation controls',flush=True)
 cost=load(args.source/'moment.py','p10_admission_moment');other=load(args.source/'base_two_moment.py','p10_admission_base2');roots={};grid=Q(1,10**18)
 for fallback in (True,False):
  root=cost.certify(dict(H5),m,W,fallback);b=Q(int(Q(root['lower'])*10**18),10**18)
  interval=cost.moment(dict(H5),m,W,b,fallback);excluded=cost.moment(dict(H5),m,W,b+grid,fallback);assert interval[1]<1<excluded[0]
  lo,hi=other.moment(m,W,list(H5.items()),b);nlo,nhi=other.moment(m,W,list(H5.items()),b+grid)
  if fallback:
   calls=32*m*m*sum(H5.values());a,z=other.moment(m,W,[(1,calls)],b);na,nz=other.moment(m,W,[(1,calls)],b+grid)
   lo+=Q(1,10**16)*a;hi+=Q(1,10**16)*z;nlo+=Q(1,10**16)*na;nhi+=Q(1,10**16)*nz
  assert hi<1<nlo
  roots['with_fallback' if fallback else 'without_fallback']=dict(b=b,moment_interval=interval,next_grid_excluded=excluded,independent_moment_interval=(lo,hi),independent_next_grid=(nlo,nhi))
 print('PASS both exact rational moment engines and adjacent-grid exclusions',flush=True)
 gx=mods['complex_gx'].check(args.source,raw)
 assert sha(args.input)==digest
 script_pins={p.relative_to(HERE).as_posix():sha(p) for p in HERE.rglob('*.py')};script_pins['DERIVATION.json']=sha(HERE/'DERIVATION.json');engine_pins={p:sha(args.source/p) for p in ['moment.py','base_two_moment.py']}
 result=dict(status='PASS_RESEARCH_P10_COMPLEX_SUPPLIER_FULL_SCALAR_SPLICE_GUARD_TWO_MOMENTS',candidate_sha256=digest,source_pins=verified,script_pins=script_pins,moment_engine_pins=engine_pins,parameterization_derivation=deriv,generic_geometry_binding=geometry,parameters=manifest['parameters'],labels=checks,ledger=ledger,scalar_bill=bill,scratch_lifetimes=life,reflected_splices=programs,mutation_controls=controls,global_contract=global_contract,finite_guard=guard,roots=roots,gx_check=gx,seconds=time.monotonic()-begun,kappa_claim=False,scope='Research p10 complex supplier only. Exact scalar identity, full labels, two complete reflected splices and new p10 finite invoice checked. Dirty lifting, exact frame geometry, finite cover, common-grid recovery and outer interfaces inherited from byte-pinned general source statements. No new Lean run; no bit or combined kappa claim.')
 args.output.write_text(json.dumps(serial(result),sort_keys=True,indent=2)+'\n');print('PASS p10 complex coarse',roots['with_fallback']['b'],flush=True)
if __name__=='__main__':main()

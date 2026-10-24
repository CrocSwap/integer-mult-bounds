#!/usr/bin/env python3
"""Read literal JSON only; no candidate checker, price engine or RESULT import."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json

HERE=Path(__file__).resolve().parent

def digest(p): return sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def hist(c):return {str(k):v for k,v in sorted(c.items()) if v}
def emit(name,x):
 p=HERE/name;p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');return digest(p)
def req(p,s):
 a=list(p.rglob(s));assert len(a)==1,(s,a);return a[0]
def scalar(g):
 if g[0] in ('copy','clear'):return 2
 q=Fraction(*(g[3:] if g[0]=='add' else g[2:]))
 n,d=abs(q.numerator),q.denominator
 assert n and d&(d-1)==0
 if g[0]=='scale':
  assert n&(n-1)==0
  return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
 assert g[0]=='add'
 return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
def local(x,orientation):
 c=x['canonical'];prog=x['programs'][orientation]
 owned={tuple(r) for r in x.get('owned',{}).get(orientation,[['C',0]])}
 paid=Counter();kinds=Counter();ops=Counter();coef=Counter();allowance=0;rows=[]
 for i,e in enumerate(prog):
  k=e[0];kinds[k]+=1;charge=0
  if k in ('climb','center'):
   rank=e[-1];assert rank>0;paid[rank]+=1
   a,b=e[-3:-1];assert abs(len(c['frames'][a])-len(c['frames'][b]))==rank
  elif k=='scalar':
   g=e[1];charge=scalar(g);ops[g[0]]+=1;allowance+=charge
   if g[0] in ('add','scale'):coef[str(Fraction(*(g[3:] if g[0]=='add' else g[2:])))]+=1
  rows.append({'index':i,'event':e,'ordinary_scalar_units':charge})
 helpers=Counter()
 for i in range(2*c['v'],len(c['start'])):
  if ('L',i) not in owned:
   rank=len(c['frames'][c['final'][i]])-len(c['frames'][c['start'][i]])
   assert rank>0;helpers[rank]+=1
 return {'event_count':len(prog),'event_kinds':dict(kinds),'paid':hist(paid),'helpers':hist(helpers),'scalar_opcodes':dict(ops),'scalar_coefficients':dict(coef),'scalar_units':allowance,'owned_roles':[list(r) for r in sorted(owned)],'independent_persistent_roles':len(c['start'])-sum(r[0]=='L' for r in owned),'main_chart_groups':4*c['v'],'warp_groups':kinds['warp'],'chronology':rows}
def main():
 a=argparse.ArgumentParser();a.add_argument('capsule',type=Path);opt=a.parse_args();cap=opt.capsule
 manifest=read(cap/'IMMUTABLE-MANIFEST.json')
 assert manifest['candidate_head']=='b1ab650d36f59e5be682a813145b7c67e219e341','Exact candidate manifest head mismatch'
 if (cap/'snapshot').is_dir():cap=cap/'snapshot'
 hits=list(cap.rglob('WORD.json.gz'));wordp=next(p for p in hits if p.parent.name=='eight-owned-relations')
 hits=list(cap.rglob('ACTUAL-WORD.json.gz'));basep=next(p for p in hits if p.parent.name=='kappa-round3-warp-20261022')
 hits=list(cap.rglob('CONTROLLER.json'));controllerp=next(p for p in hits if p.parent.name=='joint-helper-lattice')
 x,base,controller=map(read,(wordp,basep,controllerp))
 locals_={o:local(x,o) for o in ('forward','backward')};bl={o:local(base,o) for o in ('forward','backward')}
 paid=Counter();target=Counter();basepaid=Counter();basetarget=Counter();events=[];counts=Counter();idle=Counter();main=Counter()
 ports=x['canonical']['v'];assert ports==112
 fullstages={e[1] for e in controller['physical_events'] if e[0]=='LOCAL'}
 for i,e in enumerate(controller['physical_events']):
  kind=e[0];counts[kind]+=1;ep=Counter();et=Counter();ebp=Counter();ebt=Counter()
  if kind=='LOCAL':
   o='backward' if e[3] else 'forward';counts['FULL_'+o]+=1
   ep.update({int(k):v for k,v in locals_[o]['paid'].items()});et.update({int(k):v for k,v in locals_[o]['helpers'].items()})
   ebp.update({int(k):v for k,v in bl[o]['paid'].items()});ebt.update({int(k):v for k,v in bl[o]['helpers'].items()})
  elif kind=='QUERY_SHEAR':ep[1]+=ports;ebp[1]+=ports
  elif kind=='IDLE':
   active=[j for j in e[2] if j in fullstages];assert len(active)==len(e[2])
   r=8*len(active);assert r>0
   ep[r]+=2*ports;ebp[r]+=2*ports;idle[r]+=2*ports
  else:assert kind in ('ADD','SIGNED_SWAP')
  paid.update(ep);target.update(et);basepaid.update(ebp);basetarget.update(ebt)
  events.append({'index':i,'event':e,'paid':hist(ep),'productive_helpers':hist(et)})
 for row in controller['diagonal']:
  assert len(row)==34 and abs(row[0])==1 and all(q in (0,1) for q in row[1:])
  assert all(not q or j in fullstages for j,q in enumerate(row[1:]))
  main[1+8*sum(row[1:])]+=ports
 target.update(main);basetarget.update(main)
 def boundaryunit(e):
  if e[0]=='SWAP':return 26
  if e[0]=='SCALE':
   q=Fraction(e[2]);return scalar(['scale',['L',0],q.numerator,q.denominator])
  assert e[0]=='ADD';q=Fraction(e[3]);return scalar(['add',['L',0],['L',1],q.numerator,q.denominator])
 boundary={}
 for side in ('left','right'):
  program=controller['boundaries'][side+'_program']
  boundary[side]={'event_count':len(program),'opcodes':dict(Counter(e[0] for e in program)),'explicit_scalar_units':ports*sum(map(boundaryunit,program)),'all_records_dominated_by_32_units_per_port':all(boundaryunit(e)<=32 for e in program)}
 maxpaid=max(sum(v['paid'].values()) for v in locals_.values());maxhelpers=max(sum(v['helpers'].values()) for v in locals_.values())
 extraowned=max(len(v['owned_roles']) for v in locals_.values())-1
 routes=maxpaid+2*maxhelpers+max(v['warp_groups'] for v in locals_.values())+max(v['main_chart_groups'] for v in locals_.values())+2*extraowned
 scal=max(v['scalar_units'] for v in locals_.values());raw=counts['LOCAL']*10**7+counts['QUERY_SHEAR']*ports*16+32*ports*(len(events)+sum(v['event_count'] for v in boundary.values()))
 assert scal+routes*1000<10**7
 chronology_hash=emit('CHRONOLOGY-v2.json',{'local':{k:v.pop('chronology') for k,v in locals_.items()},'controller':events,'boundaries':controller['boundaries']})
 inputs={str(p.relative_to(cap)):{'sha256':digest(p),'payload_sha256':sha256(gzip.decompress(p.read_bytes())).hexdigest() if p.suffix=='.gz' else digest(p)} for p in (wordp,basep,controllerp)}
 result={'schema':'independent-literal-invoice/1','candidate':{'pr':5387,'head':'b1ab650d36f59e5be682a813145b7c67e219e341','base':'1ec1119972c9aefe42525172d07b332fcff81cb4','module':'research/eight-owned-relations'},'method':'Literal JSON parsing only; no imports/evaluation of author RESULT, verifier or price engine. Coefficients evaluated as Fraction. Rank count from literal frame dimension and full controller occurrences.','capsule_manifest_sha256':digest(opt.capsule/'IMMUTABLE-MANIFEST.json'),'input_hashes':inputs,'chronology_sha256':chronology_hash,'locals':locals_,'local_baseline_comparison':{o:{'source_event_count':bl[o]['event_count'],'source_scalar_units':bl[o]['scalar_units'],'scalar_unit_delta':locals_[o]['scalar_units']-bl[o]['scalar_units'],'scalar_opcode_deltas':{k:locals_[o]['scalar_opcodes'].get(k,0)-bl[o]['scalar_opcodes'].get(k,0) for k in set(locals_[o]['scalar_opcodes'])|set(bl[o]['scalar_opcodes'])}} for o in locals_},'controller':{'counts':dict(counts),'boundaries':boundary,'main_targets':hist(main),'idle_paid':hist(idle)},'histograms':{'paid':hist(paid),'productive':hist(target)},'totals':{'paid_jobs':sum(paid.values()),'productive_fields':sum(target.values()),'paid_rank_mass':sum(k*v for k,v in paid.items()),'productive_rank_mass':sum(k*v for k,v in target.items()),'rank_surplus':sum(k*v for k,v in target.items())-sum(k*v for k,v in paid.items())},'baseline_delta':{'paid':hist(Counter({k:paid[k]-basepaid[k] for k in paid.keys()|basepaid.keys()})),'productive':hist(Counter({k:target[k]-basetarget[k] for k in target.keys()|basetarget.keys()}))},'ordinary':{'scalar_units_local_max':scal,'route_group_reservation':routes,'route_unit_multiplier':1000,'route_units_upper':routes*1000,'local_units_upper':scal+routes*1000,'raw_nonrecursive_units_upper':raw,'raw_global_budget':10**9,'route_formula':{'max_paid':maxpaid,'two_times_max_helpers':2*maxhelpers,'warp_groups':max(v['warp_groups'] for v in locals_.values()),'main_chart_groups':max(v['main_chart_groups'] for v in locals_.values()),'two_times_additional_owned_lifetimes':2*extraowned},'classification':'constructively_upper_bounded','unit':'retained elementary scalar/movement/phase record; asymptotic physical primitive implementation domain remains conditional','unknown_charges_are_zero':False},'census_status':'LITERAL_RANK_AND_SCALAR_CENSUS_READY','complete_bill_status':'PENDING_PHYSICAL_AND_EXPANDED_TEMPLATE_APPLICABILITY','not_established':['all-column physical identities (role 01)','expanded precision, stock and tape closure (role 03)','complete numerical funding (role 04)','actual tape runtime or full compiler materialization'],'credit':'Ali Romman construction; Cao Yifan #4610 word; Cinna Davis controller/helper lineage; zxv native/precision/compiler; Jacob Alan Sussman recursion; retained source notices. Independent census prepared with substantial OpenAI assistance.'}
 print(json.dumps({'invoice_sha256':emit('INVOICE-v2.json',result),'totals':result['totals'],'ordinary':result['ordinary'],'delta':result['baseline_delta']},indent=2))
if __name__=='__main__':main()

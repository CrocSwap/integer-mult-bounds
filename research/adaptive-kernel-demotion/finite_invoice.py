"""Fresh complete finite invoice for literal mixed admitted variants.
All historical reserve formulas are retained; only the old charged allowance is read.
Standard library; no subprocesses, WSL, networking, GPU or native binaries.
"""
import argparse,collections,gzip,hashlib,json
from pathlib import Path

def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise RuntimeError(m)
def rank(vs):
 d={}
 for x in vs:
  need(type(x) is int and 0<=x<512,'actual local binary frame')
  while x:
   i=x.bit_length()-1
   if i in d:x^=d[i]
   else:d[i]=x;break
 return len(d)

def guards(group,used,compiler,physical,mass,primitive,maxchild,prefix):
 stock=group*physical;streamed=group*mass;logical=group*used+64
 router=compiler*(logical+1)*(stock+1)**2
 literal=2*(2**30000)*stock**2+8*streamed+4*stock+4+32*73
 total=streamed+2**100000;row=2*stock.bit_length()+9909+252+2*512
 checks=dict(local_primitive_bound=primitive<2**48,logical=logical<2**6050,router=router<2**30000,literal=literal<2**100000,mass=total<2**100001,precision=32*73*total*total<2**210000,tape=2*total+18<2**210000,row=row<20161,halving=73**2>2*maxchild**2)
 return checks,dict(physical_stock_bits=stock.bit_length(),logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),total_mass_bits=total.bit_length(),precision_bits=(32*73*total*total).bit_length(),tape_bits=(2*total+18).bit_length(),physical_row_coefficient=row,global_prefix_bits=prefix)

def calculate(spec,audit,dispatch,native,prior):
 M,V,T,R=73,112,16,480;compiler=64*74**3;C=spec['providers']['gauge44']['complete_contract']
 # k0 scalar admission stays inherited. All changed providers are read from fresh native output.
 providers={0:dict(children=sum(C['paid_profile'].values()),local=C['local'],wrappers=C['entering_helpers']+C['cold_hyperplane_ended_helpers'],profile={int(k):v for k,v in C['paid_profile'].items()})}
 native_bindings={}
 for k,d in native.items():
  w=read(d/'CANONICAL-WORD.json.gz');checks=read(d/'LOCAL-CHECKS.json');receipt=read(d/'INDEPENDENT-LOCAL-REPLAY.json');programs=read(d/'LOCAL-PROGRAMS.json.gz')
  need(sha(d/'CANONICAL-WORD.json.gz')==receipt['canonical_word_sha256'] and sha(d/'LOCAL-PROGRAMS.json.gz')==receipt['local_programs_sha256'],'native source binding')
  dims=[rank(x) for x in w['frames']];indices=range(224,704)
  entering=sum(dims[w['start'][q]]>0 for q in indices);cold=sum(dims[w['start'][q]]==0 and dims[w['final'][q]]<9 for q in indices)
  need(entering==receipt['entering_helpers']==192 and cold==receipt['cold_hyperplane_ended_helpers']==48,'actual wrapper-selected helper sets')
  lp={int(r):n for r,n in w['local_profile'].items()};local={}
  for o in ('forward','backward'):
   z=checks[o];need(len(programs[o])==z['events'],'literal event count')
   macros=sum(p[0]=='scalar' for p in programs[o]);need(macros==z['scalar_macros'],'literal macro count')
   need(lp=={int(r):n for r,n in z['paid_profile'].items()}=={int(r):n for r,n in receipt['paid_profiles'][o].items()},'fresh local profile binding')
   local[o]=dict(macros=macros,real_component_primitives=z['real_component_primitive_bound'],prefix_bits=receipt['local'][o]['prefix_bits_upper'])
  providers[k]=dict(children=sum(lp.values()),local=local,wrappers=entering+cold,profile=lp)
  native_bindings[str(k)]={x:sha(d/x) for x in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json')}
 dt={tuple(d['call']):d.get('variant',1) for d in dispatch};need(len(dt)==len(dispatch),'dispatch uniqueness')
 selected=[];paid=collections.Counter();counts=collections.Counter()
 for s in range(9):
  for r in range(16):
   k=dt.get((s,r),0);need(k in providers,'missing actual provider');p=providers[k];o='backward' if s%2 else 'forward';z=p['local'][o]
   selected.append(dict(stage=s,replica=r,variant=k,orientation=o,macros=z['macros'],real_component_primitives=z['real_component_primitives'],wrappers=2*p['wrappers']));paid.update(p['profile']);counts[k]+=1
 idle={int(r):n for r,n in audit['idle_profile'].items()};local_paid=dict(paid);paid.update(idle)
 need(dict(paid)=={int(r):n for r,n in audit['profile'].items()},'complete invoice profile');mass=sum(r*n for r,n in paid.items());need(mass==1041408 and 73*14336-mass==5120,'complete rank mass')
 adapters={k:16*(max(z['macros'] for z in p['local'].values())+p['children']+224+480+8)+64*73 for k,p in providers.items()}
 primitive={k:max(z['real_component_primitives'] for z in p['local'].values())+adapters[k]*compiler for k,p in providers.items()}
 scalar=sum(x['real_component_primitives'] for x in selected);macros=sum(x['macros'] for x in selected);wrapper_factors=sum(x['wrappers'] for x in selected)*144
 parent_live,parent_physical,parent_idle=23408,23922,32256;parent_banks=(parent_live-2*112*4*16)//9
 bridges,shifts,moves=2*112*144,4*112*16,8*112*16
 need(sum(idle.values())<=parent_idle,'complete remainder reserve')
 nonlocal_items=(4*112*16*9+2*112*16*9+2*144*480+parent_idle+9*parent_banks+bridges+shifts+moves+parent_live+parent_physical+wrapper_factors)
 outside=8*nonlocal_items+64*73
 pervertex=scalar+bridges+shifts+moves+parent_live+(144*max(adapters.values())+outside)*compiler+64*parent_physical
 live,physical=14336,14826;rebased=pervertex+65*(physical-parent_physical)+(live-parent_live)
 need(prior['compiler']==compiler and prior['charged_prefix_bits']==512,'retained allowance interface')
 used=max(pervertex,rebased,prior['conservative_pervertex_used']+pervertex)
 prefix=max(z['prefix_bits'] for p in providers.values() for z in p['local'].values())+37+144+144+4;need(prefix<512,'whole controller prefix reserve')
 group=2**(36*36)
 for j in range(1,37):group*=2**(2*j)-1
 checks,bits=guards(group,used,compiler,physical,mass,max(primitive.values()),max(paid),prefix);need(all(checks.values()),'strict finite guards')
 controls=[]
 for name,change in [('local_cap',dict(primitive=2**48)),('logical_cap',dict(used=2**6050)),('row_cap',dict(physical=2**2100)),('halving_cap',dict(maxchild=52))]:
  args=dict(group=group,used=used,compiler=compiler,physical=physical,mass=mass,primitive=max(primitive.values()),maxchild=max(paid),prefix=prefix);args.update(change);failed=guards(**args)[0];need(not all(failed.values()),'accepted finite control');controls.append(dict(name=name,failed=[k for k,v in failed.items() if not v]))
 return dict(status='PASS_FRESH_MIXED_COMPLETE_FINITE_INVOICE',provider_counts=dict(sorted(counts.items())),selected_calls=selected,selected_local_paid_profile=dict(sorted(local_paid.items())),global_profile=dict(sorted(paid.items())),idle_remainder_profile=idle,idle_remainders=sum(idle.values()),rank_mass=mass,deficit=5120,selected_real_component_primitives=scalar,selected_scalar_macros=macros,wrapper_elementary_factors_charged=wrapper_factors,local_adapters=max(adapters.values()),local_primitive_bound=max(primitive.values()),compiler=compiler,unhosted_pervertex=pervertex,hosted_rebased_pervertex=rebased,retained_prior_allowance=prior['conservative_pervertex_used'],added_complete_new_pervertex=pervertex,conservative_pervertex_used=used,physical=physical,live=live,actual_73column_sigmas=audit['actual_73column_sigmas'],finite=bits,strict_checks=checks,negative_controls=controls,native_bindings=native_bindings,scope='Fresh literal changed-provider counts, wrappers, mixed call totals, complete histogram, actual charts and all nine finite guard inequalities. k0 scalar semantic admission, universal routing/compiler and historical reserve formulas are retained inherited contracts. Prior file contributes only its charged allowance, not a changed-map admission receipt.')

def main():
 a=argparse.ArgumentParser()
 for k in ('spec','owner-audit','dispatch','prior','pins','out'):a.add_argument('--'+k,type=Path,required=True)
 a.add_argument('--native',action='append',default=[],required=True);z=a.parse_args();need(not z.out.exists(),'fresh output required')
 pins=read(z.pins);expected=next(v for k,v in pins.items() if k.endswith('vendor531/evidence/audit/PREFIX-AND-INVOICE.json'));need(sha(z.prior)==expected,'retained allowance exact source pin')
 result=calculate(read(z.spec),read(z.owner_audit),read(z.dispatch),{int(x.split('=',1)[0]):Path(x.split('=',1)[1]) for x in z.native},read(z.prior));result['retained_source_sha256']=sha(z.prior)
 z.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:v for k,v in result.items() if k not in ('selected_calls','native_bindings')},indent=2))
if __name__=='__main__':main()

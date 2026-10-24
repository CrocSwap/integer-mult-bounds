#!/usr/bin/env python3
"""Independent static invoice and conditional closure screen; no provider code imports.
All closure target credit is explicitly hypothetical. Does not construct a caller.
Credit: native/source/normalizer/provider authors and predecessor independent price engine.
Chris R/Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import argparse, gzip, json, resource, time
HERE=Path(__file__).resolve().parent
IN=HERE/'inputs'
HEAD='3348fccea855082786d5f0fc5558b73d4974e745'
def need(v,s):
 if not v: raise ValueError(s)
def read(n):
 b=(IN/n).read_bytes();return json.loads(gzip.decompress(b)if n.endswith('.gz')else b)
def enc(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):enc(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v)for v in x]
 return x
def tariff(g):
 if g[0]in ('copy','clear'):return 2
 q=Q(*(g[3:]if g[0]=='add'else g[2:]));n,d=abs(q.numerator),q.denominator
 need(n>0 and d&(d-1)==0,'nonzero dyadic tariff')
 if g[0]=='scale':
  need(n&(n-1)==0,'scale is dyadic unit')
  return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
 need(g[0]=='add','scalar tariff alphabet')
 return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
def basis_gate(g):
 q=Q(g[-1]);return [g[0],g[1],g[2],q.numerator,q.denominator]if g[0]=='add'else[g[0],g[1],q.numerator,q.denominator]
def static():
 pins=read('ALL-PINS.json')
 for p in pins:
  need(sha256((HERE/p['local']).read_bytes()).hexdigest()==p['sha256'],'changed input: '+p['local'])
 a,w,s,n=read('PROVIDER.json'),read('WORD.json.gz')['word'],read('SOURCE-WORD.json.gz'),read('NORMALIZERS.json')
 original=s['programs']['backward'];c=s['canonical']; paid=Counter(e[-1]for e in w if e[0]in('climb','center'))
 raw_orig=Counter(e[-1]for e in original if e[0]in('climb','center'))
 mode=set(a['mode_owners']);need(len(mode)==8,'eight distinct mode owners')
 helpers=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]])for r in range(224,632)if r not in mode)
 need(paid==Counter({1:2193,2:412,3:510,4:127,5:40}),'literal paid census')
 need(helpers==Counter({4:28,7:7,8:47,9:318}),'autonomous remainder frame census')
 scalars=[e[1]for e in w if e[0]=='scalar']; old=[e[1]for e in original if e[0]=='scalar']
 bp=[a['input_basis_program'],a['output_basis_program']]
 basis=[basis_gate(g)for p in bp for g in p]
 # Boundary exterior factors: input 2; emitted cache_scalar is ALREADY output1/(2*f_i).
 boundary=[]
 for m in a['mode_boundaries']:
  for q in [Q(2),Q(m['cache_scalar'])]:boundary.append(['scale',m['owner'],q.numerator,q.denominator])
 full=scalars+basis+boundary+[['clear',['C',i]]for i in range(1,9)]
 counts=Counter(g[0]for g in full);need(counts==Counter(add=17917,scale=1204,copy=16,clear=40),'complete field operation census')
 oldcounts=Counter(g[0]for g in old);delta=counts-oldcounts
 # Read all monomial words literally; native physical validation belongs to another lane.
 wrappers=[p['compiled_wrappers'][k]['word']for p in n['ports']for k in ['backward_input_X','backward_input_Y','backward_output_X','backward_output_Y']]
 words=wrappers+[m[k]['literal_word']for m in a['mode_boundaries']for k in ['input_K','output_N']]
 need(len(words)==464,'complete boundary monomial count')
 gates=Counter(g[0]for w0 in words for g in w0);need(set(gates)<=set(['D','P','X','phase']),'monomial word alphabet')
 kinds=Counter(e[0]for e in w);need(kinds['zero_retag']==8,'retag census')
 units=sum(tariff(g)for g in full)+8*26
 need(sum(tariff(g)for g in old)==158168,'original raw source scalar tariff binding')
 return dict(status='PASS_STATIC_LITERAL_BUDGET_INVENTORY',head=HEAD,paid=paid,autonomous_helpers=helpers,paid_calls=sum(paid.values()),paid_rank_mass=sum(r*v for r,v in paid.items()),autonomous_count=sum(helpers.values()),autonomous_rank_mass=sum(r*v for r,v in helpers.items()),coupled=dict(owners=8,diagonal_rank=8,autonomous_credit=0),original_paid=raw_orig,removed_paid=raw_orig-paid,original_scalar=oldcounts,changed_word_scalar=Counter(g[0]for g in scalars),basis_counts=[Counter(g[0]for g in p)for p in bp],basis_scalar_units=[sum(tariff(basis_gate(g))for g in p)for p in bp],boundary_scalar_units=sum(tariff(g)for g in boundary),complete_scalar=counts,added_scalar=delta,whole_field_swaps=8,monomial_maps=len(words),monomial_primitive_gates=gates,scalar_tariff_units_including_swaps=units,scalar_tariff_units_added=units-158168,retained_native_word_records=kinds,owned_fields=9,owned_credit=0,unknown_costs=['ordinary monomial maps at machine/tape level','retained native warps/adapters/phase annotations and recursive primitive internals','consumer closure recursive invoice and changed/lost targets','caller query/idles/boundaries/main diagonal','full caller finite precision/movement/storage/compiler/outer funding'],scope='Static literal census and inherited scalar tariff only; source equation, endpoint and physical admission are separate gates')
def full_profile(paid,helpers):
 ref=read('REFERENCE-5400-INVOICE.json');ctl=read('REFERENCE-5398-CONTROLLER.json');P,T=Counter(),Counter();events=Counter();idles=Counter()
 for e in ctl['physical_events']:
  events[e[0]]+=1
  if e[0]=='LOCAL':need(e[3] is True,'all comparison providers backward');P.update(paid);T.update(helpers)
  elif e[0]=='QUERY_SHEAR':P[1]+=112
  elif e[0]=='IDLE':need(len(set(e[2]))==len(e[2]),'distinct idle stage incidence');r=8*len(e[2]);P[r]+=224;idles[r]+=224
  else:need(e[0]in('ADD','SIGNED_SWAP','Q_POWER'),'comparison caller ordinary alphabet')
 main=Counter()
 for term in ctl['diagonal']:
  need(abs(term[0])==1 and all(x in(0,1)for x in term[1:]),'comparison main diagonal');main[1+8*sum(term[1:])]+=112
 T.update(main)
 need((P,T)==tuple(Counter({int(k):v for k,v in ref['histograms'][name].items()})for name in ['paid','productive']),'reconstructed complete comparison invoice differs')
 need(events['LOCAL']==18 and sum(P.values())==64116 and sum(T.values())==10784,'full comparison census')
 optimistic=T.copy();optimistic[8]+=8*18
 equal_paid=P.copy();equal_paid[8]+=8*18
 bct={side:Counter(g[0]for g in ctl['boundaries'][side+'_program'])for side in ['left','right']}
 return dict(reference_head='174fb211493b43a42210434083e9702b4fb7a2ce',reference_paid=P,reference_targets=T,main_targets=main,whole_idles=idles,caller_events=events,boundary_program_events=bct,hypothetical_paid=P,hypothetical_targets=optimistic,hypothetical_paid_count=sum(P.values()),hypothetical_target_count=sum(optimistic.values()),hypothetical_rank_mass_surplus=sum(r*v for r,v in optimistic.items())-sum(r*v for r,v in P.items()),hypothetical_added_target_profile={8:144},eight_paid_H8_per_provider=dict(paid=equal_paid,targets=optimistic,signed_profile_equals_reference={r:optimistic[r]-equal_paid[r]for r in optimistic.keys()|equal_paid.keys()}=={r:T[r]-P[r]for r in T.keys()|P.keys()}),unproved_contract='All 18 providers must close to standard B main outputs, preserve400 ordinary helpers each, and supply8 new autonomous H8 each; no source proves this contract. Closure paid jobs/lost targets and ordinary overhead are unknown, not zero.',ordinary_provider_subtotal_for_18={k:18*v for k,v in dict(ADD=17917,SCALE=1204,COPY=16,CLEAR=40,SWAP=8,monomial_field_map=464).items()},ordinary_caller_scope='The literal caller and left/right boundary record counts are retained; ADD, SIGNED_SWAP and Q_POWER each act on112 fields. QUERY_SHEAR recursive costs are included in P. Consumer closure operations and their finite movement/storage/precision costs remain unknown.')
def screen():
 from independent_price_engine import power,moment,difference
 ref=read('REFERENCE-5400-INVOICE.json')['histograms'];P={int(r):v for r,v in ref['paid'].items()};T={int(r):v for r,v in ref['productive'].items()}
 rows=[]
 for k in [Q('.00302728823'),Q('.00302728824'),Q('.00302728825')]:
  t=1-k;base=difference(moment(T,t),moment(P,t));u=power(8,t);credit=(8*u[0],8*u[1]);ratios={}
  for r in [1,2,3,4,5,8,9,16,32,64,145]:
   v=power(r,t);lo,hi=(Q(8),Q(8)) if r==8 else (credit[0]/v[1],credit[1]/v[0])
   # Strict incremental budget requires m < ratio; equality is not gain.
   maximum=(lo.numerator-1)//lo.denominator
   need(maximum < lo and maximum+1>=hi,'integer budget separated')
   ratios[r]=dict(ratio_interval=(lo,hi),max_identical_paid_jobs_for_strict_incremental_gain=maximum)
  rows.append(dict(kappa=k,reference_target_minus_paid=base,hypothetical_credit_per_provider=credit,identical_paid_jobs=ratios,reference_full_calls=18,hypothetical_p16_credit=(18*credit[0],18*credit[1])))
 return dict(status='PASS_CONDITIONAL_CLOSURE_NECESSARY_SCREEN_NO_CALLER_NO_KAPPA',new_kappa=None,rows=rows,contract='For any completed comparator at t=1-kappa: margin_new=margin_reference+sum(extra_target_count[r]*r^t)-sum(closure_paid_count[r]*r^t)-sum(lost_target_count[r]*r^t)+main_idle_other_delta. Unknown terms never default to zero.',relaxation='Reference p16 invoice plus n times eight autonomous H8, all other paid/productive jobs unchanged. Coupled5402 H fields do NOT supply this credit; physical reachability is unproved.',stop_test='If all other changes vanish and per-provider closure costs eight H8 plus any positive paid job, its incremental margin is strictly negative for every 0<kappa<1. Eight H8 alone exactly cancels the hypothetical credit. This does not forbid changed compiler headroom, a changed connection graph or productive contract.',ordinary_warning='Field operation/monomial counts are ordinary work, never recursive moment terms.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--moments',action='store_true');p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 resource.setrlimit(resource.RLIMIT_AS,(128*1024*1024,128*1024*1024));start=time.monotonic();result=static()
 result['full_profile']=full_profile(result['paid'],result['autonomous_helpers'])
 if args.moments:result['conditional_screen']=screen()
 need(result['boundary_scalar_units']==42 and result['scalar_tariff_units_including_swaps']==175022,'direct emitted boundary scalar bill')
 result['executed_checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
 result['runtime']=dict(seconds=time.monotonic()-start,maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 need(not args.output.exists(),'immutable output path exists');args.output.write_text(json.dumps(enc(result),indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'moments':args.moments,'runtime':result['runtime'],'output':str(args.output)}))
if __name__=='__main__':main()

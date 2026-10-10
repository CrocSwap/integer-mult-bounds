"""Arithmetic-only PR290 refinement. Inherited finite operator proof is gated.
Substantial AI assistance; two rational engines derive from own R305 ancestry.
No saved supplier exponent or final margin is accepted as an answer.
"""
import argparse,copy,hashlib,json,sys,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from math import prod,isfinite
from interval_moment import log_interval,exp_interval
from base_two_moment import moment as second
from constant_plan import build as constants,validate,ref
from outer import assembly
sys.set_int_max_str_digits(100000)
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];START=time.monotonic()
LEVELS=8;ETA=Q(1,10**12);BETA=Q(1,10**9);FRONTIER=Q(186178624839407,250000000000000000)
HEAD='739c3bb0ad0596f427e0a72a2ebeca23277217a3'
def need(ok,why):
 if not ok:raise ValueError(why)
def progress(s):print('R325 '+s+' '+format(time.monotonic()-START,'.3f')+'s',file=sys.stderr,flush=True)
def serial(v):
 if isinstance(v,Q):return str(v)
 if type(v) is dict:return {str(k):serial(x) for k,x in v.items()}
 if type(v) in (tuple,list):return [serial(x) for x in v]
 return v
def exact(v,path=()):
 if path and (path[-1]=='seconds' or 'timings' in path):
  need(type(v) in (int,float,dict) and (type(v) is dict or isfinite(v) and v>=0),'finite timing metadata')
  if type(v) is not dict:return
 if type(v) is dict:
  for k,x in v.items():exact(x,path+(k,))
 elif type(v) is list:
  for j,x in enumerate(v):exact(x,path+(j,))
 else:need(type(v) in (str,int,bool,type(None)),'exact artifact types')
def count(v,why):need(type(v) is int and v>=0,why);return v
def hist(v):
 need(type(v) is dict,'histogram object');out=Counter()
 for k,n in v.items():
  need(type(k) is str and k.isdecimal() and str(int(k))==k and int(k)>0 and type(n) is int and n>0,'canonical exact positive histogram');out[int(k)]=n
 return out
def paid(H,m,W,a,bad):
 need(type(m) is int and type(W) is int and m>1 and W>0 and a>=0,'exact moment dimensions');lo=hi=Q(0)
 for r,n in H.items():
  need(type(r) is int and type(n) is int and 0<r<m and n>0,'proper moment children');l,u=log_interval(Q(m,r));el,eu=exp_interval(a*l,a*u);p=Q(r*n,m*W);lo+=p*el;hi+=p*eu
 if bad:
  l,u=log_interval(Q(m));el,eu=exp_interval(a*l,a*u);p=Q(32*m*sum(H.values()),10**16*W);lo+=p*el;hi+=p*eu
 return lo,hi
def paid2(H,m,W,a,bad):
 l,u=second(m,W,sorted(H.items()),a)
 if bad:
  bl,bu=second(m,W,[(1,32*m*m*sum(H.values()))],a);l+=Q(1,10**16)*bl;u+=Q(1,10**16)*bu
 return l,u
def optimum(H,m,W,bad):
 scale=10**18;lo=0;hi=scale//100
 need(paid(H,m,W,Q(0),bad)[1]<1 and paid(H,m,W,Q(hi,scale),bad)[0]>1,'initial paid bracket')
 while hi-lo>1:
  mid=(hi+lo)//2;l,u=paid(H,m,W,Q(mid,scale),bad)
  if u<1:lo=mid
  elif l>1:hi=mid
  else:raise ValueError('exact moment precision insufficient')
 a=Q(lo,scale);next_=Q(hi,scale);x=paid(H,m,W,a,bad);y=paid(H,m,W,next_,bad);x2=paid2(H,m,W,a,bad);y2=paid2(H,m,W,next_,bad)
 need(x[1]<1<y[0] and x2[1]<1<y2[0],'two engines adjacent supplier proof')
 return a,{'accepted':x,'rejected':y,'second_accepted':x2,'second_rejected':y2}
def discharge(H,removed):
 out=Counter(H)
 for r,n in removed.items():
  need(out[r]>=n,'actual complete bank removal availability');out[r]-=n
  if not out[r]:del out[r]
 return out

def invoice(d):
 raw=d['raw'];physical=d['physical'];glob=d['global_result'];bank=d['banks']['banks'];bk=d['banks']['banked_result'];finite=d['finite'];scalar=d['scalar'];primes=d['primes']
 for v in d.values():exact(v)
 need('kernel' in d,'actual kernel artifact prerequisite')
 kernel=d['kernel'];need(kernel==raw['kernel_transform']==physical['kernel_transform'],'actual kernel receipt binding')
 need(kernel['status']=='PASS_GEN4_PER_ENTRY_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS' and kernel['selected_entries']==450 and kernel['selected_pairs']==260 and kernel['rank_drop']==1022 and kernel['both_reflected_ledgers'] is True and kernel['unchanged_data_input_output_and_dirty_output_frames'] is True and kernel['unchanged_copy_lifetimes'] is True and kernel['proof']['source_context_preserved'] is True,'actual complete kernel qualification')
 need(raw['h']==24 and raw['v']==1760 and count(raw['physical_R'],'exact physical stock')==15886 and count(raw['source_aliases'],'source aliases')==0,'original unchanged dimensions')
 R=raw['physical_R'];v=raw['v'];T=count(bank['physical_replicas'],'replicas');W=count(bank['literal_stock'],'stock');m=120
 need(T==60 and W==1244515 and bank['assignments']==5*T*R and bank['gen5_roles']==R,'actual bank stock/assignments')
 H=hist(glob['paid_histogram']);need(H==hist(raw['five_stage_profile']['histogram']),'actual global raw paid equality')
 local=hist(physical['paid_histogram']);need(local==hist(raw['one_stage_helper_histogram_including_copies']),'actual local raw paid equality')
 reconstructed=Counter({r:5*n for r,n in local.items()});reconstructed.update({r:2*v for r in (4,23,46,50)})
 births=hist(raw['auxiliary_entrance_rank_histogram']);need(births=={1:294,2:82,3:16,4:21,5:2,6:3,7:2,9:1,10:1,11:14,12:1,14:1,15:4,16:6,17:3,18:17,20:2182,21:354} and hist(physical['initial_independent_entrances'])==births,'actual independent entrance census')
 removed=hist(bk['removed_completion_histogram']);need(removed==Counter({5*r:n for r,n in births.items()}),'actual bank removed completions')
 reconstructed.update({5*r:n for r,n in births.items()})
 need(H==reconstructed,'actual five stages boundaries and unmatched entrances')
 H=discharge(H,removed)
 literal=Counter({r:T*n for r,n in H.items()});need(literal==hist(bk['literal_paid_histogram']),'actual literal bank histogram')
 mass=sum(r*n for r,n in literal.items());E=sum(literal.values());need(m*W-mass==T*4400 and 2*max(literal)<m,'literal stock rank deficit/halving')
 need(W%5==0 and all(n%5==0 for n in literal.values()),'exact moment normalization');normalized=Counter({r:n//5 for r,n in literal.items()})
 f=scalar['forward'];b=scalar['inverse'];columns=2*v+R
 for z in (f,b):
  need(z['all_source_and_dirty_restored'] is True and z['arbitrary_target_contents_preserved'] is True and count(z['all_formal_columns'],'scalar columns')==columns,'all actual source dirty columns')
  need(z['weighted_additions']==physical['weighted_scalar_events'] and hist(z['coefficient_counts'])==hist(physical['coefficient_histogram']),'full scalar coefficient census')
  need(z['literal_unit_additions']==sum(r*n for r,n in hist(z['coefficient_counts']).items()),'scalar unit expansion')
 need(f['event_sha256']==physical['scalar_projection_sha256']==glob['scalar_projection_sha256'] and physical['tagged_scalar_sha256']==glob['local_tagged_sha256'],'actual scalar/source binding')
 need(primes['independent_entrances']==sum(births.values())==3004 and hist(primes['entrance_rank_counts'])==births and primes['bundled_unique_bases']==bank['charts']==bk['charts']==545,'actual kernel birth charts')
 need(bank['max_chart_factors']==bk['max_chart_factors']==576 and bank['normalizer_factor_bound']==bk['normalizer_factor_bound']==815,'actual kernel normalizer factors')
 need(bank['conservative_extra_selector_calls']==932937188400,'actual kernel selector source bill')
 need(f['weighted_additions']==b['weighted_additions']==565050 and f['literal_unit_additions']==b['literal_unit_additions']==568570 and f['max_intermediate_row_l1']==67127 and b['max_intermediate_row_l1']==2360408,'actual kernel scalar and prefix bills')
 need(primes['all_remaining_factors_below_2_power_80'] is True and primes['physical_inventory_bound'] is True,'accepted prime inventory')
 unit=T*(5*f['literal_unit_additions']+6*v);J=T*(24*v+10*R);N=2*m;K=count(bank['conservative_extra_selector_calls'],'actual bank selectors')
 need(bank['normalizer_factor_bound']==bk['normalizer_factor_bound'] and K==2*5*T*((W-1)+R*m*bank['normalizer_factor_bound']),'actual normalizer selector bill')
 coefficient=unit+J*16*(m*m+1)**2+J*(W+24)+E*(8*m*m+8)+E*128*N**3+16*m**3+120*T+E+K+1
 need(finite['q_power_bound']['coefficient']==coefficient and finite['paid_inventory']['positive_rank_children']==E and finite['paid_inventory']['rank_mass']==mass,'reconstructed complete finite bill')
 payload=64*f['max_intermediate_row_l1']**3*b['max_intermediate_row_l1']**2
 need(finite['paid_inventory']['payload_prefix_upper']==payload and finite['paid_inventory']['extra_bank_selector_calls']==K,'actual prefix and selector overhead')
 # Conservative additional fixed overhead, absorbed before choosing each L_j.
 complete=coefficient+8*T*v+8+8*(f['max_intermediate_row_l1'].bit_length()+b['max_intermediate_row_l1'].bit_length())
 need(complete<2**80 and payload<2**104 and 2*m**3*10**16<2**80 and W+24<2**80,'common prime and finite recipe threshold')
 return {'m':m,'W':W//5,'histogram':normalized,'literal_W':W,'literal_histogram':literal,'literal_mass':mass,'children':E,'recipe':complete,'original_recipe':coefficient,'prefix':payload,'prime_strict_threshold':max(2**80,complete,W+24),'row':14401,'replicas':T}
def complex_invoice(d):
 cr=d['complex'];H=hist(cr['five_stage_histogram']);ledger=cr['ledger'];checks=cr['label_checks'];bill=cr['scalar_bill'];m=110;v=1320;R=9412;W=4*v+R
 expected=Counter({r:5*n for r,n in hist(checks['invocation_histogram']).items()});expected.update({r:2*v for r in (42,21,46,4)})
 need(H==expected==hist(ledger['histogram']) and sum(r*n for r,n in H.items())==1613040 and m*W-1613040==3080,'actual complex five-stage paid invoice')
 scalar=max(bill[o]['totals']['real_component_primitive_steps'] for o in ('forward','backward'));macros=max(bill[o]['totals']['scalar_macros'] for o in ('forward','backward'));scalar5=3*bill['forward']['totals']['real_component_primitive_steps']+2*bill['backward']['totals']['real_component_primitive_steps']
 need(bill['five_invocation_scalar_primitives_per_vertex']==scalar5,'both complex scalar directions')
 physical=W+R+23;adapters=8*(macros+checks['invocation_calls']+2*v+R+22)+32*m;outside=8*(ledger['idle_calls']+6*v+physical)+32*m;compiler=64*(m+1)**3
 pervertex=scalar5+12*v+(5*adapters+outside)*compiler+64*physical
 group=(1<<(m-1+(m//2-1)**2))*prod((1<<(2*i))-1 for i in range(1,m//2));stock=group*physical;s=group*ledger['rank_mass'];K=group*pervertex+64;router=compiler*(K+1)*(stock+1)**2;G=1<<30000;E=1<<100000;C0=1<<210000;B=s+E;literal=2*G*stock**2+8*s+4*stock+4+32*m
 need(router<G and literal<E and 32*m*B*B<C0 and 2*B+18<C0,'fresh complex finite semantic bill')
 row=stock.bit_length()+9909+252;need(row<20161 and cr['precision_guard']['retained_row_coefficient']==20161,'complete complex row reserve')
 return {'m':m,'W':W,'histogram':H,'row':row,'C0':C0,'strict_literal_gap':min(G-router,E-literal,C0-32*m*B*B,C0-(2*B+18))}
def ordinary(c,levels=LEVELS):
 need(type(levels) is int and levels==LEVELS,'exact eight finite ordinary levels');chain=[Q(384599,10**10)];gaps=[]
 for j in range(levels):
  old=chain[-1];a=(1-c)*c+c*old;need(old<a<c<1-a,'ordinary recurrence strictness');gap=min(c-a,1-a-c,1-a-c*(1-old),1-c);need(gap>0,'finite ordinary positive gaps');chain.append(a);gaps.append(gap)
 need(chain[-1]==c-c**levels*(c-chain[0]),'closed finite recurrence identity');return chain,gaps
def compute(d):
 progress('actual bank/native/complex invoices');bit=invoice(d);cp=complex_invoice(d)
 progress('both exact bit moments');c,cm=optimum(bit['histogram'],120,bit['W'],True)
 progress('both exact complex moments');b,bm=optimum(cp['histogram'],110,cp['W'],False)
 need(c<(1-BETA)*b,'unchanged bit binding supplier compatibility')
 chain,gaps=ordinary(c);linear=1-paid(bit['histogram'],120,bit['W'],Q(0),True)[1];stopped=1-cm['accepted'][1]
 plan=constants(chain,gaps,bit['recipe'],linear,stopped)
 bridge={'semantic':{'strict_literal_gap':cp['strict_literal_gap'],'C0':cp['C0'],'completed_bit_constant':plan},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
 a=chain[-1];q=a*(1-2*ETA);ceiling=(1-ETA)*q/(1+q);ticks=ceiling*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
 result=assembly(a,b,bridge,k,ETA,BETA);need(len(result['strict_constraints'])==47 and len(result['margins'])==7 and min(result['strict_constraints'].values())>0,'all47 plus7 strict margins')
 adjacent(a,b,bridge,k);need(k>FRONTIER,'strict pinned PR290 improvement')
 return {'schema':'R325-pr290-arithmetic-only-v001','bit':bit,'complex':cp,'bit_coarse':c,'complex_coarse':b,'bit_moments':cm,'complex_moments':bm,'ordinary_chain':chain,'ordinary_gaps':gaps,'constant_plan':plan,'bridge':bridge,'assembly':result,'kappa':k,'frontier':FRONTIER,'eta':ETA,'beta':BETA,'construction_changed':False,'scope':'finite arithmetic under accepted exact PR290 operator/bank/source parents and inherited conditional theorem interfaces; no full allsize proof'}
def adjacent(a,b,bridge,k):
 try:assembly(a,b,bridge,k+Q(1,10**18),ETA,BETA)
 except ValueError as e:need('compact_phase_layer_above_kappa' in str(e),'adjacent compact phase rejection');return str(e)
 raise ValueError('adjacent final grid admitted')
def reject(name,why,fn):
 try:fn()
 except ValueError as e:need(why in str(e),'wrong rejection reason '+name+': '+str(e));return {'name':name,'reason':str(e)}
 raise ValueError('control admitted '+name)
def controls(d,r):
 out=[]
 def change(section,key,value):
  z=copy.deepcopy(d);z[section][key]=value;invoice(z)
 for name,value in [('bool',True),('float',15886.0),('100bitfloat',float(2**100+1))]:out.append(reject('physical-stock-'+name,'exact physical stock' if type(value) is bool else 'exact artifact types',lambda value=value:change('raw','physical_R',value)))
 out.append(reject('100bitexact','original unchanged dimensions',lambda:change('raw','physical_R',2**100+1)))
 def paidbad(which):
  z=copy.deepcopy(d);h=z['banks']['banked_result']['literal_paid_histogram'];keys=sorted(map(int,h));a,b=keys[0],keys[-1]
  if which=='one':h[str(a)]+=1
  else:need(h[str(a)]>b,'mass control applicability');h[str(a)]-=b;h[str(b)]+=a
  invoice(z)
 for name in ('one','mass'):out.append(reject('actual-paid-'+name,'actual literal bank histogram',lambda name=name:paidbad(name)))
 def missing_parent():
  from prepare import admission_guard
  admission_guard({'issuer':'/root','full_finite_proof_admitted':False})
 out.append(reject('missing-accepted-parent','actual accepted complete PR290 baseline prerequisite',missing_parent))
 def bankbad():
  z=copy.deepcopy(d);z['banks']['banks']['literal_stock']+=1;invoice(z)
 out.append(reject('actual-stock','actual bank stock/assignments',bankbad))
 def overhead():
  z=copy.deepcopy(d);z['finite']['q_power_bound']['coefficient']-=1;invoice(z)
 out.append(reject('finite-overhead','reconstructed complete finite bill',overhead))
 def prefix():
  z=copy.deepcopy(d);z['finite']['paid_inventory']['payload_prefix_upper']-=1;invoice(z)
 out.append(reject('finite-prefix','actual prefix and selector overhead',prefix))
 def birth():
  z=copy.deepcopy(d);z['banks']['banked_result']['removed_completion_histogram']['105']-=1;invoice(z)
 out.append(reject('actual-completion','actual bank removed completions',birth))
 for n in (3,7,9,True,8.0):out.append(reject('chainlength-'+str(n),'exact eight finite ordinary levels',lambda n=n:ordinary(r['bit_coarse'],n)))
 plan=r['constant_plan'];chain=r['ordinary_chain'];gaps=r['ordinary_gaps']
 def constantsbad(which):
  z=copy.deepcopy(plan)
  if which=='inflation':z['levels'][0]['next']={'op':'add','arguments':[ref('C_large_0'),ref('C_old_0')]}
  elif which=='future':z['levels'][0]['cutoff']['arguments'][2]['argument']['arguments'][1]['arguments'][1]['argument']=ref('C_next_0')
  elif which=='recipe':z['recipe_coefficient']-=1
  elif which=='level':z['levels'].pop()
  validate(z,chain,gaps,r['bit']['recipe'],plan['induction_factor'])
 for name,reason in [('inflation','sequential ordinary small-width inflation formula'),('future','noncircular sequential constant dependency'),('recipe','sequential actual recipe/induction bindings'),('level','bounded sequential ordinary constant levels')]:out.append(reject('finite-constant-'+name,reason,lambda name=name:constantsbad(name)))
 bit=r['bit'];out.append(reject('supplier-adjacent','excluded bit adjacent',lambda:need(paid(bit['histogram'],120,bit['W'],r['bit_coarse']+Q(1,10**18),True)[1]<1,'excluded bit adjacent')))
 out.append({'name':'outer-adjacent','reason':adjacent(chain[-1],r['complex_coarse'],r['bridge'],r['kappa'])})
 out.append(reject('outer-zero-saving','bit_positive',lambda:assembly(Q(0),r['complex_coarse'],r['bridge'],Q(0),ETA,BETA)))
 def kernelbad():
  z=copy.deepcopy(d);del z['kernel'];invoice(z)
 out.append(reject('missing-kernel-artifact','actual kernel artifact prerequisite',kernelbad))
 def residualbad():
  H=hist(d['global_result']['paid_histogram']);removed=hist(d['banks']['banked_result']['removed_completion_histogram']);correct=discharge(H,removed);bad=Counter(H)
  overlap=[r for r,n in removed.items() if H[r]>n];need(overlap,'actual overlapping completion applicability')
  for r in removed:bad.pop(r,None)
  need(bad==correct,'overlapping core child residual retained')
 out.append(reject('completion-overlap-deletion','overlapping core child residual retained',residualbad))
 def underflow():
  H=hist(d['global_result']['paid_histogram']);removed=hist(d['banks']['banked_result']['removed_completion_histogram']);rank=min(removed);removed[rank]=H[rank]+1;discharge(H,removed)
 out.append(reject('completion-underflow','actual complete bank removal availability',underflow))
 def normalizer():
  z=copy.deepcopy(d);z['banks']['banks']['normalizer_factor_bound']-=1;invoice(z)
 out.append(reject('actual-normalizer','actual kernel normalizer factors',normalizer))
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();s=json.loads((HERE/'SOURCE.json').read_bytes());need(s['actual_parent_admitted'] is True,'actual admitted parent gate')
 d={}
 for name,pin in s['actual_inputs'].items():
  path=ROOT/pin['path'];b=path.read_bytes();need(len(b)==pin['bytes'] and hashlib.sha256(b).hexdigest()==pin['sha256'],'actual input SHA binding');d[name]=json.loads(b)
 from prepare import admission_guard,authenticate_source
 authenticate_source(s)
 admission_guard(d.pop('parent'))
 r=compute(d);progress('semantic controls');r['controls']=controls(d,r)
 with args.out.open('x',encoding='utf-8') as f:json.dump(serial(r),f,sort_keys=True);f.write('\n')
if __name__=='__main__':main()

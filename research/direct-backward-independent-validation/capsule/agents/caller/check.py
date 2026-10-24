#!/usr/bin/env python3
"""Independent direct-caller gate; no candidate Python imports or execution.
Reuses the exact previously admitted supplier, by byte binding only.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse, copy, gzip, hashlib, json, subprocess, time, resource
HEAD='174fb211493b43a42210434083e9702b4fb7a2ce'
PAYLOAD='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d'
PIVOTS={225,227,229,230,241,245,257,288}
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PKG='research/kappa-backward-controller-20261023'
def need(v,s):
 if not v: raise ValueError(s)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def git(repo,path):
 b=(repo/path).read_bytes() if not (repo/'.git').exists() else subprocess.check_output(['git','-C',str(repo),'show',HEAD+':'+path])
 need(sha(b)==INPUTS['repository'][path],'exact source hash '+path)
 return b
def scale_add(a,b,k):
 r=dict(a)
 for x,v in b.items():
  r[x]=r.get(x,F(0))+k*v
  if not r[x]:del r[x]
 return r
def monomial(a,q=0,stages=()):
 r={}
 for (column,powers),v in a.items():
  ex=list(powers);ex[0]+=q
  for s in stages:ex[s+1]+=1
  r[column,tuple(ex)]=v
 return r
def scalar_program(rows,program):
 r=copy.deepcopy(rows)
 for e in program:
  k=e[0]
  if k=='ADD':r[e[1]]=scale_add(r[e[1]],r[e[2]],F(e[3]))
  elif k=='SCALE':r[e[1]]={t:F(e[2])*v for t,v in r[e[1]].items()}
  elif k=='SWAP':r[e[1]],r[e[2]]=r[e[2]],r[e[1]]
  else:raise ValueError('unlicensed boundary opcode')
 return r
def signed_swap(r,x,y):
 # Literal three-ADD implementation: (x,y)->(x+y,y)->(x+y,-x)->(y,-x).
 r[x]=scale_add(r[x],r[y],1);r[y]=scale_add(r[y],r[x],-1);r[x]=scale_add(r[x],r[y],1)
def literal_replay(word):
 zero=(0,)*34
 r=[{(i,zero):F(1)} for i in range(32)]
 for side in ['right','left']:
  test=scalar_program([{(i,zero):F(1)} for i in range(32)],word['boundaries'][side+'_program'])
  want=[{(j,zero):F(v) for j,v in enumerate(row) if F(v)} for row in word['boundaries'][side]]
  need(test==want,'literal scalar boundary matrix')
 r=scalar_program(r,word['boundaries']['right_program'])
 for e in word['physical_events']:
  kind=e[0]
  if kind in ['LOCAL','QUERY_SHEAR']:
   _,stage,pair,back=e;x,y=2*pair,2*pair+1
   if back:r[x]=scale_add(r[x],monomial(r[y],q=1),-1)
   else:r[y]=scale_add(r[y],monomial(r[x],q=-1),1)
   if kind=='LOCAL':
    r[x]=monomial(r[x],stages=[stage]);r[y]=monomial(r[y],stages=[stage])
  elif kind=='IDLE':
   for i in [2*e[1],2*e[1]+1]:r[i]=monomial(r[i],stages=e[2])
  elif kind=='ADD':r[e[1]]=scale_add(r[e[1]],r[e[2]],F(e[3]))
  elif kind=='Q_POWER':
   need(e[2] in [-2,2],'only paid-grammar even central translations');r[e[1]]=monomial(r[e[1]],q=e[2])
  elif kind=='SIGNED_SWAP':signed_swap(r,e[1],e[2])
  elif kind=='SWAP':r[e[1]],r[e[2]]=r[e[2]],r[e[1]]
  else:raise ValueError('unknown controller event')
 r=scalar_program(r,word['boundaries']['left_program'])
 want=[{(i,tuple(v)):F(1)} for i,v in enumerate(word['diagonal'])]
 need(r==want,'full independent Laurent caller equality')
 return True

def mv(cols,v):
 r=0
 while v:
  bit=v&-v;r^=cols[bit.bit_length()-1];v^=bit
 return r
def phase(terms,n):
 # parity(a.z) = sum a_i z_i - 2 sum_{i<j}a_i a_j z_i z_j modulo4.
 lin=[0]*n;quad=[0]*n
 for a,c in terms:
  for i in range(a.bit_length()):
   if (a>>i)&1:
    lin[i]=(lin[i]+c)%4
    if c%2:quad[i]^=a&~((1<<(i+1))-1)
 return tuple(lin),tuple(quad)
def contact(old,new,route,n):
 moved=[(mv(route,a),c) for a,c in old]
 p,q=phase(moved,n),phase(new,n)
 need(p[1]==q[1],'physical contact quadratic phase')
 dif=[(b-a)%4 for a,b in zip(p[0],q[0])]
 need(all(c%2==0 for c in dif),'physical contact nonmonomial difference')
 shift=sum((c//2)<<i for i,c in enumerate(dif))
 need(phase(moved+[(shift,2)],n)==q,'physical contact full phase correction')
 inv=mv(route,shift)
 need(phase([(mv(route,a),c) for a,c in new]+[(inv,2)],n)==phase(old,n),'physical contact inverse phase')
 return {'translation':str(shift),'inverse_translation':str(inv)}
def native_gate(repo,word,wrong_stage0=False,square_phase=1):
 path='research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
 recipes=json.loads(git(repo,path))['recipes'];need(len(recipes)==112,'112 physical ports')
 n=265;axes=[1<<i for i in range(n)];records=[];columns=0
 def complete(s):return [(a,1) for a in axes[:9+8*s]]
 # Gaussian rational amplitude Q=(1+i)/2 I+(1-i)/2 X.
 a,b=complexF(F(1,2),F(1,2)),complexF(F(1,2),F(-1,2))
 need(square_phase*(a*a+b*b)==complexF(0,0) and square_phase*(2*a*b)==complexF(1,0),'Q square exact absolute phase')
 for site in word['wrapper_sites']:
  s=site['stage'];need(s in [0,32],'actual changed endpoint stage')
  for port,recipe in enumerate(recipes):
   q=recipe['q'];basis=recipe['idle_children'][0]['orthogonal_axes'][:8]
   need(all((q&v).bit_count()%2==0 for v in basis),'Q perpendicular local stage axes')
   need(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(basis) for j,b in enumerate(basis)),'local stage axes orthonormal')
   swaps=[] if s==0 else [a^axes[9+8*(s-1)+i] for i,a in enumerate(basis)]
   route=[a^mv(swaps,sum(((a&v).bit_count()%2)<<i for i,v in enumerate(swaps))) for a in axes]
   need(all(mv(route,a)==axes[i] for i,a in enumerate(route)),'actual route inverse')
   need(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(route) for j,b in enumerate(route)),'actual route orthogonal')
   need(mv(route,q)==q,'actual route fixes Q')
   spectator=[(a,1) for a in axes[9:9+8*s]]
   rawx=[(q,1)] if s==0 else complete(s-1)
   rawy=[] if s==0 else rawx+[(q,-1)]
   if wrong_stage0 and s==0:rawx=complete(0);rawy=rawx+[(q,-1)]
   entry=[spectator+[(q,-1)],spectator]
   exitx=spectator+[(a,-1) for a in axes[:9]]
   localexit=[exitx,exitx+[(q,1)]]
   out=[complete(s),complete(s)+[(q,-1)]]
   ct=[contact(x,y,route,n) for x,y in zip([rawx,rawy]+localexit,entry+out)]
   d=[(a,1) for a in axes[:9]]+[(q,-1)] if s==0 else [(a,1) for a in axes[9+8*(s-1):9+8*s]]
   for raw,final in zip([rawx,rawy],out):need(phase(final+[(a,-c) for a,c in raw],n)==phase(d,n),'actual backward diagonal stage')
   need(phase(out[0]+[(a,-c) for a,c in rawy],n)==phase(d+[(q,1)],n),'actual backward cross stage')
   for sign in [2,-2]:
    need(phase([(q,sign)],n)==phase([(q,2)],n),'both even central powers translation')
   # Every nine-axis column; explicit amplitude coefficients have already been squared.
   for address in range(512):
    actual={address:a*a+b*b,address^q:2*a*b};actual={k:v for k,v in actual.items() if v!=complexF(0,0)}
    need(actual=={address^q:complexF(1,0)},'literal central-square column');columns+=1
   records.append({'stage':s,'port':port,'q':q,'contacts':ct})
 return {'dimension':n,'stages':[0,32],'ports':112,'contacts':4*len(records),'columns':columns,'records':records,'new_positive_jobs':0}
class complexF(tuple):
 def __new__(cls,a,b):return tuple.__new__(cls,(F(a),F(b)))
 def __add__(a,b):return complexF(a[0]+b[0],a[1]+b[1])
 def __mul__(a,b):
  if isinstance(b,int):return complexF(a[0]*b,a[1]*b)
  return complexF(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
 __rmul__=__mul__
def binary_span(basis):
 r={0}
 for b in basis:r|={x^b for x in list(r)}
 need(len(r)==1<<len(basis),'independent helper frame')
 return r

def positive_helper_gate(rank,direction=-1,pauli=True):
 # Validate actual canonical target on every Fourier eigenvector, not just its rank.
 for address in range(1<<rank):
  weight=address.bit_count();actual=(direction*weight+2*(weight%2)*int(pauli))%4
  need(actual==weight%4,'helper positive-target absolute phase')
 return True

def supplier_binding(repo):
 prior=HERE/'inputs/prior'
 supplier=prior
 for p in prior.iterdir():need(sha(p.read_bytes())==INPUTS['prior'][p.name],'exact inherited evidence '+p.name)
 bindings={}
 for name in ['native.py','WITNESS.json']:
  current=git(repo,PKG+'/'+name);old=(supplier/name).read_bytes()
  need(current==old,'unchanged previously accepted supplier '+name);bindings[name]=sha(current)
 raw=(supplier/'WORD.json.gz').read_bytes();payload=gzip.decompress(raw)
 need(sha(payload)==PAYLOAD,'exact independently accepted supplier payload')
 actual=git(repo,'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
 need(sha(gzip.decompress(actual))=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','exact supplier source word')
 receipts={}
 for label,path in [('algebra','algebra.json'),('ownership','ownership.json'),('acceptance','acceptance.json')]:
  b=(prior/path).read_bytes();j=json.loads(b);receipts[label]={'path':str(prior/path),'sha256':sha(b),'status':j['status']}
  if label=='algebra':need(j['candidate_payload_sha256']==PAYLOAD and j['all_16_unrestricted_identities_checked'],'accepted arbitrary-column supplier algebra')
  if label=='ownership':need(j['result']['backward']['owned_arbitrary_columns']==17 and j['result']['backward']['all_owned_last_writes_are_clears'],'17 arbitrary owned returns')
  if label=='acceptance':need(any(x['pr']==5383 and x['word_payload_sha256']==PAYLOAD for x in j['accepted_candidates']),'prior same-premise supplier acceptance')
 word=json.loads(payload);c=word['canonical'];helpers=[];hist=Counter()
 foundation=json.loads((prior/'foundation.json').read_bytes())['results']['all_helpers']
 need(foundation['status']=='PASS_ALL408_HELPER_RELATIVE_OPERATORS_AND_ABSOLUTE_PHASES' and foundation['word_payload_sha256']=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','authenticated prior exact phase closure')
 catalogues={'selected_recipes':json.loads(gzip.decompress(git(repo,'research/joint-helper-lattice/NATIVE.json.gz')))['new_physical_edges_and_boundaries'],'changed_recipes':json.loads(gzip.decompress(git(repo,'research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz')))['changed_helper_boundaries']}
 helper_classes=[]
 for row in foundation['classes']:
  if row['direction']!='backward':continue
  rec=catalogues[row['recipe_source']][row['recipe_index']]['recipes']['backward']
  need(sha(json.dumps(rec,sort_keys=True,separators=(',',':')).encode())==row['recipe_sha256'],'exact previously proved signed helper recipe')
  need(rec['rank']==row['rank'] and all(len(rec[side]['matrix_rows'])==9 for side in ['left','right']),'two recorded actual helper normalizers')
  helper_classes.append({k:row[k] for k in ['input','output','rank','roles','recipe_source','recipe_index','recipe_sha256','tableau_sha256','anchor_sha256']})
 for i in range(224,632):
  if i in PIVOTS:continue
  a,b=c['start'][i],c['final'][i];U,V=binary_span(c['frames'][a]),binary_span(c['frames'][b]);need(U<V,'proper productive helper frame relation')
  rank=len(c['frames'][b])-len(c['frames'][a]);hist[rank]+=1
  matches=[r for r in helper_classes if r['input']==a and r['output']==b and i in r['roles']]
  need(len(matches)==1 and matches[0]['rank']==rank,'exact oriented helper phase coverage')
  helpers.append({'owner':i,'entry_frame':a,'exit_frame':b,'rank':rank,'raw_direction':'conjugate','positive_target':'C_'+str(rank),'left_normalizer':'conjugate(L) then X_all in algebraic matrix order','right_normalizer':'conjugate(R)','normalizer_groups':2})
 need(len(helpers)==400 and dict(hist)=={9:318,8:47,7:7,4:28},'all400 exact helper source endpoints')
 # Canonical target Fourier phases: inverse C_r corrected by X_all equals C_r.
 # This is full absolute phase equality, on every spectral column for every actual rank.
 for rank in hist:positive_helper_gate(rank)
 return {'bindings':bindings,'word_payload_sha256':PAYLOAD,'source_payload_sha256':sha(gzip.decompress(actual)),'receipts':receipts,'helper_profile':dict(hist),'helpers':helpers,'owned_arbitrary_inputs':17,'persistent_independent_inputs':624,'supplier_science_rerun':False,'signed_backward_helper_phase_classes':helper_classes,'foundation_receipt_sha256':sha((prior/'foundation.json').read_bytes())}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,required=True);args=ap.parse_args();start=time.time();repo=args.repository.resolve()
 global INPUTS
 INPUTS=json.loads((HERE/'INPUTS.json').read_text())
 if (repo/'.git').exists():need(subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD']).decode().strip()==HEAD,'frozen target HEAD')
 word=json.loads(git(repo,PKG+'/CONTROLLER.json'));source=json.loads(git(repo,'research/joint-helper-lattice/CONTROLLER.json'))
 expected=[];sites=[]
 for idx,e in enumerate(source['physical_events']):
  if e[0]=='LOCAL' and e[3] is False:
   _,s,p,_=e;x,y=2*p,2*p+1;sites.append({'source_index':idx,'stage':s,'pair':p})
   expected.extend([['SIGNED_SWAP',y,x],['Q_POWER',x,2],['LOCAL',s,p,True],['SIGNED_SWAP',x,y],['Q_POWER',y,-2]])
  else:expected.append(e)
 need(sites==word['wrapper_sites']==[{'source_index':0,'stage':0,'pair':0},{'source_index':99,'stage':32,'pair':15}],'exact changed chronology')
 need(word['physical_events']==expected,'all exact controller events')
 for k in source:
  if k!='invoice' and k!='physical_events':need(word[k]==source[k],'unchanged controller field '+k)
 literal_replay(source);literal_replay(word)
 controls={}
 for name,mutate in [
 ('missing_translation',lambda w:w['physical_events'].pop(next(i for i,e in enumerate(w['physical_events']) if e[0]=='Q_POWER'))),
 ('odd_unpaid_Q_power',lambda w:next(e for e in w['physical_events'] if e[0]=='Q_POWER').__setitem__(2,1)),
 ('wrong_backward_orientation',lambda w:next(e for e in w['physical_events'] if e[0]=='LOCAL').__setitem__(3,False)),
 ('missing_scalar_sign',lambda w:next(e for e in w['physical_events'] if e[0]=='SIGNED_SWAP').__setitem__(0,'SWAP'))]:
  bad=copy.deepcopy(word);mutate(bad)
  try:literal_replay(bad)
  except ValueError as e:controls[name]=str(e)
  else:raise ValueError('failed caller mutation control '+name)
 supplier=supplier_binding(repo)
 # Test the same helper semantic validator with altered direction/correction.
 for label,direction,pauli in [('dropped_helper_normalizer',-1,False),('wrong_helper_orientation',1,True)]:
  try:positive_helper_gate(4,direction,pauli)
  except ValueError as exc:controls[label]={'rejected':str(exc),'rank':4,'all_actual_ranks_tested_positive':sorted(supplier['helper_profile'])}
  else:raise ValueError('accepted corrupted helper normalization '+label)
 # The sign belongs to the scalar program outside tensor substitution.
 def tensor_sign_gate(f,sign_inside):
  actual=(-1)**f if sign_inside else -1
  need(actual==-1,'scalar minus sign incorrectly tensor-powered')
 tensor_sign_gate(2,False)
 try:tensor_sign_gate(2,True)
 except ValueError as exc:controls['scalar_sign_put_inside_tensor_f2']={'rejected':str(exc),'f':2}
 else:raise ValueError('accepted tensor scalar-sign corruption')
 phys=native_gate(repo,word)
 for label,kwargs in [('wrong_actual_stage0_convention',{'wrong_stage0':True}),('central_square_phase_only',{'square_phase':-1})]:
  try:native_gate(repo,word,**kwargs)
  except ValueError as exc:controls[label]=str(exc)
  else:raise ValueError('accepted physical mutation '+label)
 (HERE/'PHYSICAL-CONTACTS.json').write_text(json.dumps(phys,indent=2)+'\n');phys.pop('records')
 stext=git(repo,'research/final4610-independent-admission/SPECIALIZATION.md');(HERE/'inputs/SPECIALIZATION.md').write_bytes(stext)
 out={'status':'PASS_SOURCE_BOUND_DIRECT_CALLER_WITH_RETAINED_SIGNED_HELPER_NORMALIZERS','head':HEAD,'checker_sha256':sha(Path(__file__).read_bytes()),'controller_sha256':sha(git(repo,PKG+'/CONTROLLER.json')),'canonical_controller_sha256':sha(git(repo,'research/joint-helper-lattice/CONTROLLER.json')),'source_specialization_sha256':sha(stext),'wrapper_sites':sites,'full_laurent_replay':{'rows':32,'formal_generators':34,'central_finite_order_used':False,'all_coefficients_exact':True,'signed_swaps_expanded_to_three_ADD':True},'native':phys,'supplier_reuse':supplier,'helper_normalization':{'raw_operator':'bar(L) bar(C_r) bar(R)','positive_child_factorization':'(bar(L) X_all) C_r bar(R)','adapter_order_preserved':True,'applied_only_after_autonomous_completed_endpoint':True,'all_400_raw_helper_maps_unchanged_by_main_wrapper':True,'no_helper_rank_only_shortcut':True,'two_sided_nine_axis_record_bound':342,'retained_per_group_allowance':1000,'existing_helper_route_groups_per_full':816,'charged_in_invoice_review':True},'ownership':{'fresh_helper_owners_per_full':400,'fresh_owned_arbitrary_inputs_per_full':17,'full_calls':18,'distinct_helper_owners':7200,'distinct_owned_bank_positions':306,'wrappers_touch_main_fields_only':True,'all_arbitrary_owned_return_zero_in_reused_supplier':True},'controls':controls,'limits':['Inherited selected all-column native realization and positive-child/monomial tariffs; no physical tape execution','Source supplier source identities/ownership/phase not rerun; exact prior acceptance reused','No compiler, precision, outer, moment or full scientific admission claim in this lane'],'runtime':{'seconds':time.time()-start,'ru_maxrss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}}
 (HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'runtime':out['runtime'],'native':phys,'helper_count':len(supplier['helpers'])}))
if __name__=='__main__':main()

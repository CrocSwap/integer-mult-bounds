"""Exact critical-root arithmetic composition. Native physical bridge is a separately stated proof premise. Apache-2.0; substantial OpenAI assistance."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def require(ok,msg):
 if not ok:raise ValueError(msg)
def source(path,name):
 ns={'__file__':str(path),'__name__':name};exec(compile(path.read_bytes(),str(path),'exec'),ns);return ns
ROOT_ENGINE=ROOT/'research/adaptive-gate-existence/root_application.py'
ENDPOINT=ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
NATIVE=ROOT/'research/joint-helper-lattice/RESULT.json'
COMPILER=ROOT/'research/compact-joint-compiler/arithmetic/RESULT.json'
BENCH=ROOT/'research/rank-convergence/BENCHMARKS.json'
REGISTERED=ROOT/'research/adaptive-gate-existence/verify.py'
PATHS=[ROOT_ENGINE,ENDPOINT,NATIVE,COMPILER,BENCH,REGISTERED,ROOT/'research/adaptive-gate-existence/verify.py',ROOT/'research/adaptive-gate-existence/PROOF.md',ROOT/'research/adaptive-gate-existence/WITNESS.json']
def pins():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    live={row['path']:row for row in manifest['files'] if row['usage']=='input'}
    for path in PATHS:
        rel=path.relative_to(ROOT).as_posix()
        require(rel in live,'undeclared executable/input: '+rel)
    for rel,row in live.items():
        require(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==row['sha256'],'changed source: '+rel)
    return {rel:row['sha256'] for rel,row in live.items()}
def absorption(E,theta_lo,theta_hi,t,threshold=10**14):
 require(theta_lo<theta_hi<t,'closed root gap')
 log=lambda n:tuple(F(a,E['GRID']) for a in E['logarithm'](n))
 ell=650;M=1024;c=133;p=F(2,5)
 # A=n0^(1-theta)/(c+log n0)^p <=n0^(1-theta_lo).
 logA=(1-theta_lo)*(log(145)[1]+ell*log(M)[1]);gap=t-theta_hi
 require(gap-p/F(c+threshold)>0,'log absorption derivative')
 margin=gap*threshold-logA-p*log(c+threshold)[1]
 require(margin>0,'log absorption margin')
 require(2*log(2)[0]>1,'dyadic cutoff covers log threshold')
 return {'log_threshold':threshold,'secondary_conservative_N_cutoff':'2^'+str(2*threshold),'logA_upper':str(logA),'margin_lower':str(margin),'positive_gap':str(gap),'conclusion':'A*N^theta*(133+logN)^(2/5)<=N^t above this finite cutoff; physical implementation overhead not inferred'}
def finite_envelope(profile):
 targets={int(k):v for k,v in profile['targets'].items()}
 paid={int(k):v for k,v in profile['paid'].items()}
 W0=sum(targets.values());P0=sum(paid.values())
 surplus=sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items())
 require((W0,P0,surplus)==(10928,64620,752),'finite envelope raw inventory')
 require(W0<2**14 and W0+P0+1<2**17,'finite envelope branch bounds')
 # N=2^H, M=1024=2^10, and retained height multiplier2.
 H=10**14;G_depth=2*(H//10)
 require(H%10==0 and G_depth==2*10**13,'finite envelope height arithmetic')
 exponent=14+17*(G_depth+1)
 require(exponent==340000000000031,'finite envelope class exponent')
 return {'raw_productive_fields':W0,'raw_paid_jobs':P0,'raw_rank_surplus':surplus,
         'primary_N':'2^100000000000000','height_multiplier':2,'height_base':1024,
         'G_depth_upper':G_depth,'log2_C_N_strict_upper':exponent,
         'class_envelope':'C_N <= W0*(W0+P0+1)^(G_depth+1) < 2^340000000000031',
         'divisible_width_bound':'B_N < C_N^N',
         'raw_occurrence_bound':'U <= B_N*N/752',
         'full_call_centre_episodes_per_raw_unit':18*8,
         'thin_query_episodes_per_raw_unit':15*112,
         'owned_space_scope':'144U and1680U bound separate raw episodes, not total live scratch. Actual compiler/parking allocations require their own O ledger.',
         'proof_scope':'Height/class recurrence, denominator clearing and positive-surplus occurrence inequalities are inherited proof premises. Only their displayed integer arithmetic is checked; no gigantic word or B_N is materialized.'}
def run(profile_override=None,k_override=None,closed=False,small_threshold=False):
 source_pins=pins();E=source(ROOT_ENGINE,'root_exact');O=source(ENDPOINT,'outer_exact')
 # Re-execute source-bound registered arithmetic in this process; do not trust a status JSON.
 import contextlib,io
 registered=source(REGISTERED,'registered_adaptive');capture=io.StringIO()
 with contextlib.redirect_stdout(capture):registered['main']()
 require(json.loads(capture.getvalue())['status']=='PASS_EXACT_ADAPTIVE_GATE_WITNESS','registered source result')
 native=json.loads(NATIVE.read_text());compiler=json.loads(COMPILER.read_text());profile=native if profile_override is None else profile_override
 require(all(profile[x]==native[x]==compiler[x] for x in ['targets','paid']),'native profile altered')
 retained=E['run'](ROOT)
 witness=retained['applications']['p16']['critical_majorant']['parameters']
 require(witness['height_base']==1024 and witness['ell0']==650 and F(witness['c'])==133 and F(witness['p'])==F(2,5),'absorption parameters match critical majorant')
 lo,hi=F('.9969798340229'),F('.9969798340230');t=F('.996979834024')
 bracket=E['certify'](profile,lo,hi,F('.564'),F(1))
 absorb=absorption(E,lo,hi,hi if closed else t,1 if small_threshold else 10**14)
 # Independent exact finite absorption at N=2^(10^14), retained from cost audit.
 bound=1-F('.0030201659770');tl,th=E['moment'](E['histogram'](profile['targets']),bound);pl,ph=E['moment'](E['histogram'](profile['paid']),bound)
 require(tl>ph,'cost refined root sign')
 gap=F('.0030201659770')-(1-t);H=10**14
 require(F(E['logarithm'](2)[0],E['GRID'])>F(2,3) and F(E['logarithm'](2)[1],E['GRID'])<1,'elementary log2 bounds')
 require(F(E['logarithm'](145)[1],E['GRID'])<8,'elementary log145 bound')
 require(F('.003021')*(8+6500)<20 and 133+H<2**47,'cost log overhead below194/5')
 require(F(2,3)*H>8+6500,'absorption cutoff above base')
 require(gap*H*F(2,3)>F(194,5),'cost finite absorption margin')
 require(gap-F(2,5)/(133+F(2,3)*H)>0,'cost all-size monotonicity')
 absorb['primary_certified_N']='2^100000000000000';absorb['cost_margin_lower']=str(gap*H*F(2,3)-F(194,5));absorb['cost_all_larger_N_monotonicity']=True
 # Distinguish the two independently checked cutoffs (PR4536 reporting note).
 absorb['margin_evaluation_log_N']=absorb['log_threshold']
 absorb['cost_margin_evaluation_N']=absorb['primary_certified_N']
 absorb['margin_scope']='margin_lower is evaluated at log(N)=log_threshold; cost_margin_lower is the conservative certified margin at primary_certified_N. The two margins use different cutoffs.'
 k=F('.00302016597') if k_override is None else k_override;d=F(1,10**12);uniform=1-t
 require(k<uniform,'raw kappa lacks uniform slack')
 a={'kappa':k,'tested_saving':F('.003020165977'),'complex_uniform_saving':uniform,'b':F('.003020165975'),'a':F('.003020165974'),'q':F('.003020165973'),'bit_saving':F(compiler['ordinary_BIT']['admitted']),'epsilon':1-d,'beta':1-3*d,'r0':d/10,'stop':d,'layout':d,'d':d}
 outer=O['ledger'](a);outer['functional_checks']['actual_new_BIT_stock_sublinear']=a['beta']*(1-F(compiler['ordinary_BIT']['atom']))
 require(len(outer['strict_checks'])==54,'54 outer checks')
 require(all(v>0 for v in outer['strict_checks'].values()),'outer strict inequality')
 require(all(v>0 for v in outer['functional_checks'].values()),'outer functional guard')
 require(all(v>k for v in outer['margins'].values()),'outer margin')
 return {'status':'PASS_EXACT_CONDITIONAL_PARAMETER_CERTIFICATE','source_sha256':source_pins,'kappa':str(k),'uniform_saving':str(uniform),'critical_root':bracket,'absorption':absorb,'finite_envelope':finite_envelope(profile),'outer_parameters':O['encode'](a),'outer_checks':len(outer['strict_checks']),'functional_checks':len(outer['functional_checks']),'minimum_outer_margin_above_kappa':str(min(outer['margins'].values())-k),'BIT_admission':compiler['ordinary_BIT'],'physical_bridge':'Conditional proof premise: retained native, movement, precision, stock and fixed-tape closure must apply to the fixed expanded word; this arithmetic check does not establish physical admission.','retained_root_applications_replayed':list(retained['applications'])}
if __name__=='__main__':
 result=run();tests={};p=json.loads(NATIVE.read_text());p['paid']['1']+=1
 for name,kwargs in [('nativeprofile',{'profile_override':p}),('closedrootgap',{'closed':True}),('kappa_equals_uniform',{'k_override':F('.003020165976')}),('log_absorption_failure',{'small_threshold':True})]:
  try:run(**kwargs)
  except ValueError as e:
   expected={'nativeprofile':'native profile altered','closedrootgap':'closed root gap','kappa_equals_uniform':'raw kappa lacks uniform slack','log_absorption_failure':'log absorption derivative'}[name]
   require(str(e)==expected,'unexpected rejection: '+name);tests[name]=str(e)
  else:raise ValueError('mutation accepted: '+name)
 result['rejected_mutations']=tests
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 target=HERE/'RESULT.json'
 if args.write:target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:require(json.loads(target.read_text())==result,'stored RESULT mismatch')
 print(result['status'])

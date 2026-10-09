#!/usr/bin/env python3
"""Full finite replay; all-size compiler/selector and analytic conditions are inherited."""
from pathlib import Path
import subprocess,sys,json,importlib.util,hashlib,gzip
from fractions import Fraction as Q
sys.set_int_max_str_digits(0);sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SA=ROOT/'research/source-assisted';CP=ROOT/'research/source-assisted-v4';WORK=CP/'.work'
def run(*args):
 r=subprocess.run([sys.executable,'-B',*map(str,args)],cwd=ROOT,capture_output=True,text=True)
 if r.returncode:raise RuntimeError('Replay rejected: '+str(args)+'\n'+r.stdout[-6000:]+'\n'+r.stderr[-6000:])
 print(r.stdout[-2000:],end='',flush=True)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(p.read_text())
assert not sys.flags.optimize
before={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/paired_cube_assembly.py',SA/'decision/exact_complex_flow_lift.py',CP/'contract_v4.py']}
# Replay the actual82 new gauges, complete reflected ledgers and all new banks.
run(HERE/'joint/replay_joint.py');run(HERE/'borrow/replay.py');run(HERE/'borrow/boundary.py');run(HERE/'borrow/derive_profile.py');run(HERE/'gaugeb/replay.py');run(HERE/'gaugeb/boundary.py');run(HERE/'gaugeb/derive_profile.py');run(HERE/'newg/replay.py');run(HERE/'newg/schedule_audit.py');run(HERE/'newg/boundary.py');run(HERE/'newg/derive_profile.py');run(HERE/'extra/boundary.py');run(HERE/'joint/pack_joint.py');run(HERE/'targetagg/replay.py');run(HERE/'targetagg/boundary.py');run(HERE/'targetagg/derive_profile.py')
# The portable witness is checked again; original numerical search need not be repeated.
run(SA/'decision/exact_complex_flow_lift.py','--witness',WORK/'flow.witness.json','--profile',WORK/'flow.json','--out',WORK/'lift.json')
lift=read(WORK/'lift.json');expected=read(CP/'certificate.json');assert lift['exact_scalar_program_sha256']==expected['lift']['exact_scalar_program_sha256']
for key,name in [('certificate_path','lift.certificate.json.gz'),('witness_path','flow.witness.json')]:lift[key]=(WORK/name).relative_to(ROOT).as_posix()
lift['checker_path']=(SA/'decision/exact_complex_flow_lift.py').relative_to(ROOT).as_posix()
(WORK/'lift.json').write_text(json.dumps(lift,indent=2)+'\n',newline='\n')
run(CP/'contract_v4.py','--tree',WORK/'aligned','--cache',WORK/'aligned/cache','--witness',WORK/'flow.witness.json','--flow-profile',WORK/'flow.json','--lift-profile',WORK/'lift.json','--out',HERE/'complex-profile-replayed.json')
actual=read(HERE/'complex-profile-replayed.json')
for key in ['m','W_per_vertex','rank_per_vertex','deficit_per_vertex','child_histogram','contract_checks','exact_scalar_program_sha256']:
 assert actual[key]==expected['complex_profile'][key],('Complex mathematical output changed',key)
# Paid two-supplier moments, four finite leaf levels, and unchanged 47 constraints.
run(HERE/'joint/price_joint.py');assert read(HERE/'joint/assembly.json')==read(HERE/'certificate.json'),'Derived final certificate differs'
cert=read(HERE/'joint/assembly.json');assert all(Q(x)>0 for x in cert['assembly']['strict_constraints'].values());assert len(cert['assembly']['strict_constraints'])==47
# Independent base-two enclosure, no imports from the public moment implementation.
im=load('independent_base_two',HERE/'geometry/base_two_moment.py')
for side in ['bit','complex']:
 row=cert[side+'_profile'];a=Q(cert[side]['saving']);hist=[(int(t),n) for t,n in row['child_multiplicities'].items()]
 lo,hi=im.moment(row['m'],row['W'],hist,a);nl,nu=im.moment(row['m'],row['W'],hist,a+Q(1,10**18))
 if side=='bit':
  fallback=[(1,32*row['m']**2*sum(n for _,n in hist))];bl,bu=im.moment(row['m'],row['W'],fallback,a);bnl,bnu=im.moment(row['m'],row['W'],fallback,a+Q(1,10**18));hi+=Q(1,10**16)*bu;nl+=Q(1,10**16)*bnl
 assert hi<1<nl,side+' independent adjacent moment failed'
 corrupt=dict(row,total_rank=row['total_rank']+1)
 public=load('paid_moment_control',ROOT/'research/paired-cube-diagonal-bit-168/arithmetic/interval_moment.py')
 try:public.moment(corrupt,a)
 except ValueError:pass
 else:raise AssertionError('Rank-mass negative control accepted')
chart=read(HERE/'joint/joint-banks.json');assert chart['conservative_extra_selector_calls']==177924145968<2**40
aggregation=read(HERE/'targetagg/profile.json');assert aggregation['conservative_added_fixed_calls']==279072 and chart['conservative_extra_selector_calls']+aggregation['conservative_added_fixed_calls']==177924425040<2**40
assert chart['charts']==231 and chart['assignments']==3590784 and chart['literal_stock']==1315146
assert before=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in before}
print('PASS full offline bit/frame/bank/chart/complex-lift/contract replay, independent paid moments, 47 inequalities and controls; kappa='+cert['kappa'])
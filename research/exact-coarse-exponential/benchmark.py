"""Slow original-oracle comparison at a declared endpoint width; timings stay local."""
import argparse,json,hashlib,time,sys
from pathlib import Path
from fractions import Fraction as F
from verify import original
import integer_exp as fast
if not __debug__:raise RuntimeError('Assertions must be enabled')
ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,default=30000);ap.add_argument('--out',type=Path);ap.add_argument('--check-result',type=Path);ap.add_argument('--private-timings',type=Path);args=ap.parse_args()
assert args.digits>=24
assert args.out or args.check_result,'Choose an output or a committed-result comparison'
engine=original()
# Deterministic exact stress point close to the current supplier, not a new endpoint claim.
a=F('0.0016797549561255445')+F(1,10**args.digits)
l,u=engine.logarithm(F(73))
x,y=a*l,a*u
start=time.perf_counter();observed=fast.exponential(x,y,engine.DYAD);new_seconds=time.perf_counter()-start
start=time.perf_counter();expected=engine.exponential(x,y);old_seconds=time.perf_counter()-start
assert observed==expected
encoded=[str(v) for v in observed]
report={'status':'PASS_HIGH_PRECISION_LITERAL_ORACLE_EQUIVALENCE','endpoint_digits':args.digits,'dyad_bits':engine.DYAD.bit_length()-1,'reference':'Unmodified pinned engine exponential on a*log(73); no mocks, cache or reduced Taylor degree.','result_sha256':hashlib.sha256(json.dumps(encoded).encode()).hexdigest(),'result':encoded,'source_sha256':hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest(),'no_new_kappa':True,'public_privacy':'No host, user, private path or timing/hardware metadata included.'}
if args.out:args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
if args.check_result:assert json.loads(args.check_result.read_text())==report,'High-precision committed evidence differs'
if args.private_timings:args.private_timings.write_text(json.dumps({'original_seconds':old_seconds,'integer_seconds':new_seconds,'speed_ratio':old_seconds/new_seconds},indent=2)+'\n',encoding='utf-8',newline='\n')
print(report['status'],'digits='+str(args.digits),'equal=True')

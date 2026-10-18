"""Exact two-engine repricing with PR548's complete fixed idle remainder.
Physical owner admission and the fresh finite invoice are separate obligations.
"""
import argparse,gzip,json,sys
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import moment,base_two_moment
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
if not __debug__:raise SystemExit('Assertions must remain enabled.')
e=json.loads((ROOT/'inputs/PR548-EXPECTED.json').read_text());w=json.load(gzip.open(a.word))
oldlocal=Counter({1:2284,2:456,3:488,4:168,5:56,6:56,8:8})
newlocal=Counter({int(r):n for r,n in w['report']['local_profile'].items()})
assert newlocal==Counter({1:2285,2:455,3:487,4:169,5:56,6:56,8:8})
old=Counter({int(r):n for r,n in e['complex_global_profile'].items()})
idle=old.copy();idle.subtract({r:72*n for r,n in oldlocal.items()})
assert all(n>=0 for n in idle.values())
new=Counter({r:72*n for r,n in newlocal.items()});new.update(idle)
assert sum(r*n for r,n in new.items())==sum(r*n for r,n in old.items())==520704
cert=moment.certify(new,73,7168,True);b=Q(cert['lower']);assert b==Q('0.001593581126479114854212');receipts=[]
for x,accept in ((b,True),(b+Q(1,10**24),False)):
 lo,hi=base_two_moment.moment(73,7168,list(new.items()),x)
 fl,fh=base_two_moment.moment(73,7168,[(1,32*73*73*sum(new.values()))],x)
 lo+=fl/10**16;hi+=fh/10**16
 assert hi<1 if accept else lo>1
 receipts.append({'point':str(x),'accept':accept,'lower_minus_one':str(lo-1),'upper_minus_one':str(hi-1)})
res=dict(status='PASS_EXACT_FIXED_OWNER_PROFILE_PRICE_ONLY',global_profile=dict(sorted(new.items())),fixed_idle_remainder=dict(sorted((r,n) for r,n in idle.items() if n)),complex_lower=str(b),b_decimal=cert['lower'],moment=cert,independent_base_two=receipts,scope='Complete fixed-owner profile, including fallback, repriced by two rational engines. Fresh phases, owner template, finite invoice and assembly are separate requirements.')
a.out.write_text(json.dumps(res,indent=2)+'\n');print(res['status'],res['b_decimal'])

"""Exact fixed-geometry exclusion of all71 new-JP8 calls.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
Use after the native supplier/owner witness is admitted; this checks the
independent ideal-packing moment bound, not native construction semantics.
"""
import argparse,hashlib,importlib.util,json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
p=json.loads((args.package/'data/PLAN.json').read_text());reg=p['provider_registry'];profile=Counter()
for pid,count in [('j249',71),('ck',1)]:profile.update({int(r):n*count for r,n in reg[pid]['actual_paid_profile'].items()})
capacity=sum(cap*112 for cap,_ in p['windows'].values());width=71*sum(reg['j249']['widths'])+sum(reg['ck']['widths']);unused=capacity-width
if max(cap for cap,_ in p['windows'].values())!=48 or unused!=107099:raise ValueError('unexpected geometry or native width totals')
full,remainder=divmod(unused,48);profile[48]+=full
if remainder:profile[remainder]+=1
if sum(r*n for r,n in profile.items())!=520704:raise ValueError('rank conservation')
path=args.package/'extras/exact_intervals.py'
if hashlib.sha256(path.read_bytes()).hexdigest()!='aa3c2327c5d3742248b720a87b2de0bbe2e34ed2af89a578e3c8d5bd2656a9cf':raise ValueError('independent interval engine pin')
s=importlib.util.spec_from_file_location('exact',path);E=importlib.util.module_from_spec(s);s.loader.exec_module(E)
k=Q('0.001636461592777116');q=k/(1-k);lower=upper=Q(0)
for rank,n in profile.items():
 lo,hi=E.log(Q(73,rank));lo,hi=E.exp(q*lo,q*hi);lower+=Q(rank*n,73*7168)*lo;upper+=Q(rank*n,73*7168)*hi
if not lower>1:raise ValueError('fixed-dispatch exclusion not established')
report={'status':'EXACT_FIXED_DISPATCH_RAW249_EXCLUSION','reference_kappa':str(k),'q_from_reference_kappa':str(q),'ideal_profile':dict(profile),'ideal_idle':{remainder:1,48:full},'moment_lower':str(lower),'moment_upper':str(upper),'strict_lower_excess':str(lower-1),'scope':'Native J249 at all71 JP8 times and unchanged CK at time5, fixed geometry/maxcap48 and moment formula only. Concavity shows every owner moment is at least this ideal profile moment; its strict excess at the reference exponent excludes reaching PR639 kappa. No exclusion for other dispatch, suppliers, geometry or mathematics.'}
args.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'])

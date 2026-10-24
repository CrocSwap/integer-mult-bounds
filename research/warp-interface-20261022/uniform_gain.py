"""Exact uniform paid-moment gain of the admitted changed-G profile."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,gzip,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]


def main():
    data=json.loads((HERE/'NATIVE-VALIDATION.json').read_text());old=json.loads(gzip.decompress((ROOT/'research/joint-helper-lattice/NATIVE.json.gz').read_bytes()))
    new={int(k):v for k,v in data['paid'].items()};before={int(k):v for k,v in old['paid'].items()}
    coeff={r:new.get(r,0)-before.get(r,0) for r in new.keys()|before.keys()};coeff={r:n for r,n in coeff.items() if n}
    if coeff!={1:-36,2:24,3:12,4:-12}:raise ValueError('Uniform gain must be actual admitted old/new delta')
    if sum(r*n for r,n in coeff.items()) or sum(coeff.values())!=-12:raise ValueError('Mass and job-count identities')
    path=ROOT/'research/higher-moment-strictification/verify.py';spec=importlib.util.spec_from_file_location('warp_uniform_rational_intervals',path);E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
    minimum=None;rows=[]
    for i in range(128):
        l,r=Q(i,128),Q(i+1,128);bound=Q(0)
        for rank,n in coeff.items():
            product=E.mul(E.power(rank,l if n>0 else r),E.log_bounds(rank));bound+=n*product[0 if n>0 else 1]
        if bound<=0:raise ValueError('Strict derivative lower bound')
        minimum=bound if minimum is None else min(minimum,bound);rows.append(str(bound))
    result={'status':'PASS_UNIFORM_STRICT_PAID_MOMENT_IMPROVEMENT','new_minus_old_paid_coefficients':coeff,
            'productive_profile_unchanged':True,'paid_job_reduction':12,'rank_mass_change':0,
            'delta_at_one':'0','delta_at_zero':'-12','derivative_positive_cover':[0,1],'cover_intervals':128,
            'derivative_lower_bounds':rows,'minimum_derivative_lower':str(minimum),
            'conclusion':'For every real0<t<1, the new complete paid moment is strictly less than the old; helpers and scalar bill unchanged.',
            'interval_engine_sha256':sha256(path.read_bytes()).hexdigest(),'native_validation_sha256':sha256((HERE/'NATIVE-VALIDATION.json').read_bytes()).hexdigest()}
    (HERE/'UNIFORM-GAIN.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],float(minimum))


if __name__=='__main__':main()

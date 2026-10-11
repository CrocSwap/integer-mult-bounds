"""Exact necessary target probes; profiles are audited inputs, not realizations.

No supplier admission or universal architecture lower bound is asserted.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines/base_two_moment.py'
spec = importlib.util.spec_from_file_location('audit_second_moment', ENGINE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

def probe(path, key, m, W):
    data = json.loads(path.read_text())
    H = {int(r):int(n) for r,n in data[key].items()}
    mass = sum(r*n for r,n in H.items())
    E = sum(H.values())
    a = Q(1,99)
    lo,hi = engine.moment(m,W,list(H.items()),a)
    blo,bhi = engine.moment(m,W,[(1,32*m*m*E)],a)
    lo += blo/10**16
    hi += bhi/10**16
    # exp(a log(m/r)) >= 1 + a log(m/r). Thus positive deficit
    # must exceed a times weighted log mass plus fallback even at a=0.
    sl = sum((Q(r*n)*engine.log_bounds(Q(m,r))[0] for r,n in H.items()),Q(0))
    linear_required = a*sl + Q(32*m*m*E,10**16)
    assert lo > 1
    return dict(input=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        m=m,W=W,profile=H,calls=E,rank_mass=mass,deficit=m*W-mass,
        required_supplier_saving=str(a),target_moment=[str(lo),str(hi)],
        target_moment_decimal=[float(lo),float(hi)],
        necessary_deficit_linear_lower=str(linear_required),
        necessary_deficit_linear_decimal=float(linear_required),
        hypothetical_fixed_profile_W_lower=str(W*lo),
        hypothetical_fixed_profile_W_strict_minimum=(W*lo).__floor__()+1,
        hypothetical_scope='Adding free stock with fixed paid H only; real stock introduces payment and changes H.')

def main():
    b=Q(1183986549206329246771,10**24)
    k=Q(1132818179085294674300829,10**27)
    results=dict(status='EXACT_NECESSARY_CONDITIONS_FOR_CURRENT_ASSEMBLY_ONLY',
        current_kappa=str(k),target_kappa='1/100',necessary_both_supplier_savings='>1/99',
        retained_complex_cap=str(b/(1+b)),retained_complex_cap_decimal=float(b/(1+b)),
        required_complex_factor=float(Q(1,99)/b),
        engine_sha256=hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
        probes=[probe(ROOT/'experiments/stage-search/pr433-split/full/split-centres/INTEGRATION.json','global_profile',73,12720),
                probe(ROOT/'experiments/stage-search/pr440-signed-retime/full/bit426-source-centres/global/GLOBAL.json','profile',64,113829)])
    out=Path(__file__).with_name('TARGET-REQUIREMENTS.json')
    out.write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    print(json.dumps({p['m']:{key:p[key] for key in ['deficit','target_moment_decimal','necessary_deficit_linear_decimal','hypothetical_fixed_profile_W_strict_minimum']} for p in results['probes']},indent=2))

if __name__=='__main__':main()

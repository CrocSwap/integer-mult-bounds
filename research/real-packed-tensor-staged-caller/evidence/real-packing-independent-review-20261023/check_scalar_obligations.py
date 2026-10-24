#!/usr/bin/env python3
"""Frozen source authentication and scalar proof calibration only.

No Tensor/CRT/factory/archive/native code is imported or executed. This is not
the rounded finite implementation proposed in TEST-SPEC.md.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
 'outputs/mathematics-paper-research-20261023/notes/real-packing-5095-fit.md':'3b48e1790472a686ac1d7a50673b90fb2f456b5c72d35a85e5f96dbd54febf62',
 'outputs/outer-bilinear-interface-20261023/APPENDIX-5095.md':'87243c00536e42cbc8663b645b80c83a4cf3a8558a9442d37855c6de38b75a69',
 'outputs/outer-bilinear-interface-20261023/APPENDIX-5095-SOURCES.json':'a41239e2bca82f6f8fb63f79eebc11f40bd7cb3671cee30ce94d7ef217315d76',
 'outputs/mathematics-paper-research-20261023/papers/matusiak2001-real-fft.pdf':'aae9288bbf9e4c933f542ec4589b9de22cd591024c3947471893d0ec3995cfd8',
 'outputs/mathematics-paper-research-20261023/papers/johnson-frigo2008-ffts.pdf':'454dc303d65ee0279042e815d390abaa2ef59147cba115ee1fdfa5561a18ad9a',
}


def require(ok,label):
    if not ok:
        raise RuntimeError(label)


def authenticate():
    got = {p:sha256((ROOT/p).read_bytes()).hexdigest() for p in PINS}
    require(got == PINS, 'frozen review inputs changed')
    base = ROOT/'outputs/outer-bilinear-interface-20261023'
    manifest = json.loads((base/'APPENDIX-5095-SOURCES.json').read_text())
    require(len(manifest['files']) == 9, 'expected nine literal source snapshots')
    for item in manifest['files']:
        p = base/item['snapshot']
        require(sha256(p.read_bytes()).hexdigest() == item['sha256'] and p.stat().st_size == item['bytes'],
                'literal source hash/byte count '+str(p))
    return got


def cmul(a,b):
    return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])


def main():
    before = authenticate()
    cases = 0
    # H_j=(a+ib)/2^p, H_Jj=(c+id)/2^p. Split numerators at grid p+1.
    for a,b,c,d in ((32,16,32,16),(3,-7,4,9),(-11,2,0,-5),(0,0,1,-1)):
        split_a,split_b = (a+c,b-d),(b+d,c-a)
        prod = cmul(split_a,split_b)
        require(prod == (2*a*b+2*c*d,c*c+b*b-a*a-d*d), 'exact split-product integer identity')
        cases += 1
    p = 8
    numerator = cmul((64,0),(32,0))[0]
    correct_grid_numerator = numerator//(1<<(p+2))
    wrong_grid_numerator = numerator//(1<<p)
    require(correct_grid_numerator == 2 and wrong_grid_numerator == 8, 'factor4 wrong truncation control')
    # Literal complete Tensor restoration makes every returned numerator a
    # multiple of2^gamma, gamma>=1. Exact halves can alternatively stay on grid p.
    exact_halved_product = cmul((32,0),(16,0))[0]//(1<<p)
    require(exact_halved_product == correct_grid_numerator, 'exact numerator halves preserve p-grid alternative')
    emax = Q(1,384)
    require(Q(1,4)+emax < Q(26,100), 'split quarter-disk plus error below.26')
    require((Q(1,4)+emax)**2 < Q(1,2), 'opposite half-disk input safe')
    require(Q(1,2)+emax < 2, 'epsilon/2+epsilon²<2epsilon for epsilon<1/384')
    # Synthetic scalar equality control, not a production catalogue or E value.
    h,C = Q(1,1<<16),Q(64)
    equality_epsilon = (Q(1,2)/C-2*h)/3
    require(C*(3*equality_epsilon+2*h) == Q(1,2), 'strict guard equality control')
    require(not C*(3*equality_epsilon+2*h) < Q(1,2), 'guard equality must reject')
    require(C*(3*(equality_epsilon-h)+2*h) < Q(1,2), 'strict guard passing scalar control')
    # Actual finite source geometry: J and actual dilation commute and R² != I.
    source_shape,target_shape = (5,7),(8,8)
    coords = [(i,j) for i in range(5) for j in range(7)]
    J = lambda ij: tuple((-x)%s for x,s in zip(ij,source_shape))
    R = lambda ij: tuple((x*t)%s for x,t,s in zip(ij,target_shape,source_shape))
    require(all(R(J(ij)) == J(R(ij)) for ij in coords), 'J commutes with actual R')
    require([ij for ij in coords if J(ij) == ij] == [(0,0)], 'odd-box J fixed point')
    require(any(R(R(ij)) != ij for ij in coords), 'wrong opposite permutation control not degenerate')
    after = authenticate()
    out = {'status':'PASS_SCALAR_PROOF_CALIBRATION_ONLY_NO_ROUNDED_TENSOR_EXECUTION',
           'hashes_before':before,'hashes_after':after,'literal_source_snapshots_authenticated':9,
           'source_head':'e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1',
           'exact_split_integer_cases':cases,
           'raw_sum_representation':{'split_grid':'p+1','exact_product_grid':'2p+2','final_shift_to_p_grid':'p+2'},
           'literal_restoration_alternative':'gamma>=1 makes split sums even; divide numerator by2 exactly, retain p-grid, then ordinary product shift p',
           'wrong_shift_control':{'p':8,'correct_p_grid_numerator':correct_grid_numerator,
                                  'incorrect_reused_p_shift_numerator':wrong_grid_numerator},
           'epsilon_strict_upper':'1/384','opposite_half_disk_bound_verified':True,
           'same_guard_equality_rejected':True,'J_R_finite_coordinate_calibration':'PASS_5x7_target8x8',
           'rounded_or_physical_implementation':'NOT_RUN_SPECIFICATION_ONLY',
           'production_analytic_premises':'RETAINED_NOT_VERIFIED_HERE',
           'recursive_kappa_route':'STOP_COMMON_REAL_SCALING_NO_NEW_CLAIM','new_kappa':None}
    path = HERE/('SCALAR-CHECK-RESULT-OPTIMIZED.json' if sys.flags.optimize else 'SCALAR-CHECK-RESULT.json')
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'result':str(path)}))


if __name__ == '__main__':
    main()

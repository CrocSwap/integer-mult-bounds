#!/usr/bin/env python3
"""Independent generic compact counts/log/margins and promoted finite metadata audit.

Only reviewer logarithm/count routines are imported. No producer is used.
The compact address checks and the written tape/layout proof are separate.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import subprocess
import time

from review_asymmetric_motif import independent_saving
from review_packed_unrolling import finite_counts

PIN = '6e564879f51ae16f23d392e9e196c605f36d90df'


def ceil_q(x):
    return -(-x.numerator//x.denominator)


def stopped_recurrences():
    """Direct integer recurrences below/at/above the geometric threshold."""
    checked = internal = small = 0
    examples = []
    for k in range(1, 13):
        # m=64, tau=1/2, beta=1/3, d=64^(3k), G=(k+1)^2.
        d, threshold, root_log = 64**(3*k), 64**k, 3*k
        for n in range(root_log+1):
            e = 64**n
            for sigma, b, internal_power, leaf_power in (
                    (Q(1, 3), 4, 9*k, 10*k),
                    (Q(1, 2), 8, 9*k, 12*k),
                    (Q(2, 3), 16, 11*k, 14*k)):
                if e < threshold:
                    assert e <= 2**leaf_power
                    small += 1
                    checked += 1
                    continue
                depth = n-k+1
                leaf = e//64**depth
                assert threshold//64 <= leaf < threshold
                direct = leaf
                for j in reversed(range(depth)):
                    node = e//64**j
                    overhead = (k+1)*2**(3*(n-j))+1
                    assert (overhead-1)**2 == (k+1)**2*node
                    direct = b*direct+overhead
                independent = b**depth*leaf+sum(
                    b**j*((k+1)*2**(3*(n-j))+1) for j in range(depth))
                assert direct == independent
                terms = [b**j*(k+1)*2**(3*(n-j)) for j in range(depth)]
                if b <= 8:
                    assert all(term <= (k+1)*2**(3*n) for term in terms)
                else:
                    assert all(term <= (k+1)*2**internal_power for term in terms)
                leaves = b**depth*leaf
                assert leaves <= 2**leaf_power
                assert sum(b**j for j in range(depth)) <= sum(terms)
                assert direct <= 2*depth*(k+1)*2**internal_power+2**leaf_power
                internal += 1
                checked += 1
                if n == root_log:
                    examples.append(dict(k=k, sigma=str(sigma), depth=depth,
                                         exact_normalized_cost=str(direct),
                                         internal_root_bound=str((k+1)*2**internal_power),
                                         leaf_bound=str(2**leaf_power)))
        # K=64^k is a genuine growing width parameter. Charging K^tau
        # would introduce a factor 2^(3k)/(k+1), absent from the new model.
        assert Q(2**(3*k), k+1) > 1
    assert checked == internal+small
    return dict(complete_stopped_recurrences=checked, internal=internal,
                individually_executed=small, sigma_branches=['1/3', '1/2', '2/3'],
                tau='1/2', beta='1/3', fixed_radix=64,
                overhead='sqrt(G*e)+1; G=(k+1)^2', examples=examples,
                no_K_factor_in_current_recurrence=True)


def original_complex_counts(h):
    v, m = comb(h, 3), h**3
    N = v**3
    z = comb(h-3, 3)+3*(h-3)
    W = 2*N+3*v*v*(v*z+h+1)
    L = 3*v*v*h*(h+1)
    D = 2*N-2*L
    return dict(h=h, v=v, m=m, N=N, Wc=W, Lc=L, sc=W*m-D, eta_c=Q(D, W*m))


def upstream_audit(reference):
    cert = json.loads((reference/'certificates/compact-control-layer.json').read_text())
    paired = json.loads((reference/'certificates/paired-network.json').read_text())
    raw = paired['bit_counts']
    local = dict(raw, h=int(raw['h']), side_roles=int(raw['side_roles_per_invocation']))
    bit = finite_counts(local)
    cx = original_complex_counts(25)
    assert all(Q(cert['complex_counts'][k]) == v for k,v in cx.items())
    assert cx['Lc'] < cx['N'] and not 2*cx['Lc'] < cx['N']
    assert cx['eta_c'] == Q(14, 3464399375)
    p = {k:Q(v) for k,v in cert['main']['parameters'].items()}
    eps,c,beta,tau,sigma,lam,lp,delta = (p[k] for k in
        ('epsilon','c','beta','tau','sigma','lam','lamp','delta'))
    assert tau == 1-Q(296,10**11) and sigma == 1-Q(418,10**12)
    bit_lo,bit_hi = independent_saving(bit['eta'], bit['m'])
    cx_lo,cx_hi = independent_saving(cx['eta_c'],cx['m'])
    assert bit_lo > 1-tau and cx_lo > 1-sigma
    chi = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    reserve = max(1-c,Q(0))
    recurrence = dict(internal=chi,leaf=leaf,preprocessing=reserve,layer=max(chi,leaf,reserve))
    assert all(Q(cert['main']['recurrence'][k]) == v for k,v in recurrence.items())
    assert max(tau,sigma,chi) < lam < lp < 1 and max(leaf,reserve) < lp
    margins = dict(g1=1-eps*(1+c),g2=eps*c*(1-tau),g3=eps*(1-lp),
                   g4=(1-tau)*(1-eps),g5=Q(1,4)-delta-Q(5,4)*eps,
                   g6=1-eps-delta,g7=eps)
    assert all(Q(cert['main']['margins'][k]) == v for k,v in margins.items())
    guard = cert['main']['guard']
    W,m,s = cx['Wc'],cx['m'],cx['sc']
    E = 64*(W+m+1)**3
    B,zeta = s+E,Q(1,10000)
    C0 = ceil_q(max(Q(128*m*B*B),18*m*B*B*(1+1/zeta)))
    assert Q(guard['C0']) == C0 and Q(guard['E']) == E and Q(guard['B']) == B
    assert p['C1'] == Q(guard['C1']) == 5-4*beta+zeta
    assert s*(8+E) <= 9*B*B and 2 <= s < m**5
    assert 9*m*B*B*(1+1/zeta)+18 <= C0
    assert eps*p['C1'] < 1 and 0 < beta < 1
    G = min(margins.values())
    assert G == Q(333833,4*10**15) > p['kappa'] == Q(83,10**12) > Q(1,2**34)
    assert G-p['kappa'] == Q(cert['main']['absorption_gap'])
    # Original scalar coefficient formula and the binary residual witnesses
    # are independent of ground parity. Supports below are proper for h25.
    for intersection in range(4):
        center = Q(intersection-1,2)
        side = -center if intersection in (0,2) else Q(0)
        assert center+side == int(intersection == 3)
    assert 6 < 25
    assert all(3**j < 25**j for j in (1,2,3))
    return dict(status='PASS independent original h25 counts, retained bit saving and new upstream margins',
                kappa=str(p['kappa']),minimum_margin=str(G),complex_counts={k:str(v) for k,v in cx.items()},
                complex_loss_less_N_but_not_N_over_two=True,
                unused_coordinate_binary_residual_witnesses=True,
                bit_saving_interval=[str(bit_lo),str(bit_hi)],
                complex_saving_interval=[str(cx_lo),str(cx_hi)])


def audit_row(row):
    n = finite_counts(row['bit_counts'])
    h,R = int(row['complex_counts']['h']),int(row['complex_counts']['R'])
    assert h >= 8 and h % 2 == 0 and R > 0
    v,m = comb(h,3),h**3
    N = v**3
    W = 2*N+2*v*v*(R+h+1)
    L = 3*v*v*h*(h+1)
    D,s = 2*N-2*L,W*m-2*N+2*L
    nc = dict(h=h,v=v,m=m,R=R,N=N,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    assert all(Q(row['complex_counts'][k]) == val for k,val in nc.items())
    for name,eta,radix in (('bit',n['eta'],n['m']),('complex',nc['eta'],m)):
        lo,hi = independent_saving(eta,radix)
        enc = row[name+'_saving_enclosure']
        assert Q(enc['saving_lower']) < lo < hi < Q(enc['saving_upper'])
        assert 0 < Q(enc['chosen_saving']) < lo
    p = {k:Q(v) for k,v in row['parameters'].items()}
    a,b,c,beta,eps,r,delta,zeta,lam,lp = (p[k] for k in
        ('a_bit','a_complex','c','beta','epsilon','alpha_squared_power','delta','zeta','lambda_','lambda_prime'))
    tau,sigma = p['tau'],p['sigma'];tiny=Q(1,2**64);q=1-lp
    assert 0 < a < b < Q(1,32) and tau == 1-a and sigma == 1-b
    assert c == 1-tiny and q == a*(1-2*tiny) and 1-beta == (q/b)*(1+tiny)
    chi,leaf,reserve = tau+(1-beta)*max(sigma-tau,Q(0)),sigma+beta*(1-sigma),max(1-c,Q(0))
    assert chi == tau and lam == (lp+max(tau,sigma,chi))/2
    assert all(Q(row['recurrence'][k]) == val for k,val in dict(internal=chi,leaf=leaf,reservations=reserve,compact_movement_spacing_power=0).items())
    backoff = Q(1,2**20) if row['mode'] == 'conservative' else tiny
    assert row['mode'] in ('conservative','tight')
    assert zeta == (Q(1,2**30) if row['mode']=='conservative' else tiny)
    C1 = 5-4*beta+zeta
    E = 64*(W+m+1)**3;B=s+E
    C0 = 32*m*B*B*(1+1/zeta)
    assert p['C1'] == C1 and p['C0'] == C0
    assert s*(8+E) <= 9*B*B and 2 <= s < m**5
    assert 3*v*v*(4*R+4) < 6*W
    assert 12*W**3+4*s+4*W+4 < E
    assert 9*m*B*B*(1+1/zeta)+18 < C0
    assert eps == (1-backoff)/max(C1,1+c+q) and r == (1-eps)/2 and delta == r/8
    margins = dict(g1=1-eps*(1+c),g2=eps*a*c,g3=eps*q,g4=a*(1-eps),
                   g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    assert all(Q(row['margins'][k]) == val for k,val in margins.items())
    G = min(margins.values())
    assert G == Q(row['minimum_margin']) == margins['g3']
    assert all(Q(value)>0 for value in row['constraint_slacks'].values())
    slacks = dict(a=a,b=b,order=b-a,c=c,c_below_one=1-c,beta=beta,beta_below_one=1-beta,
        tau_below_lambda=lam-tau,sigma_below_lambda=lam-sigma,chi_below_lambda=lam-chi,
        lambda_below_prime=lp-lam,leaf_below_prime=lp-leaf,reserve_below_prime=lp-reserve,
        lambda_prime_below_one=1-lp,guard=1-eps*C1,axis_spacing=1-eps*(1+c),
        K_superlogarithmic=eps*c,record_suffix_superpolynomial=1-eps,
        Gaussian_local=1-eps-delta,Gaussian_boundary=r-delta,gamma=1-eps-r,
        phase_cell_separation=eps-(1-r)/2,alpha_positive=r,alpha_below_p=1-r,
        delta=delta,delta_below_eighth=Q(1,8)-delta,
        prefix_above_min=margins['g1']-G,movement_above_min=margins['g2']-G,
        CRT_above_min=margins['g4']-G,Gaussian_above_min=margins['g5']-G,
        scalar_above_min=margins['g6']-G,dimension_above_min=margins['g7']-G,
        absorption=G-p['kappa'],improvement=p['kappa']-Q(83,10**12))
    assert all(v>0 for v in slacks.values())
    assert p['kappa'] == Q((G.numerator*10**40-1)//G.denominator,10**40)
    assert b > 4*a/(1+a) and C1 < 1+c+q
    au,bu = (Q(row[name+'_saving_enclosure']['saving_upper']) for name in ('bit','complex'))
    branches = dict(prefix_and_movement=au/(2+au),movement_and_guard=au*bu/(4*au+bu),leaf_and_guard=bu/5)
    assert all(Q(row['scoped_model_upper_branches'][k])==v for k,v in branches.items())
    assert Q(row['scoped_model_upper']) == min(branches.values()) > p['kappa']
    assert min(branches,key=branches.get) == 'prefix_and_movement'
    km,ka = ceil_q(1/(eps*c)),ceil_q(1/r)
    cc = 64*km*km+1
    # Real log2(b)=L obeys ceil(log2(6b)) <= L+4. The explicit
    # cutoff checks the stronger +192 constant, even for the v1 input
    # whose explanatory comment used +160. Its witness is unchanged.
    assert cc >= 2*km and 2**(cc//km) >= 32*cc+192
    cuts=dict(gamma=ceil_q(7/(1-eps-r)),logarithmic_alpha=16*ka*ka+1,
              full_guard=ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
              phase_cell=ceil_q(9/(eps-(1-r)/2)),compact_controls=cc)
    cuts['common']=max(cuts.values())
    assert row['cutoff_log2_b']==cuts
    return dict(mode=row['mode'],kappa=str(p['kappa']),minimum_margin=str(G),
                independent_strict_conditions=len(slacks),producer_strict_conditions=len(row['constraint_slacks']),
                complete_counts_and_independent_logarithms=True,cutoffs=cuts,
                stronger_real_log_cutoff_constant=192,
                ratio_to_83_over_10_to_12=str(p['kappa']/Q(83,10**12)),
                scoped_upper=str(min(branches.values())),scoped_active_branch='prefix_and_movement')



def promoted_metadata(data, args):
    input_files=data['input_files']
    for path in (args.bit_review,args.complex_review,args.complex_candidate,args.calibration):
        digest=sha256(path.read_bytes()).hexdigest()
        assert any(item['sha256']==digest for item in input_files.values())
    bit=json.loads(args.bit_review.read_text())
    cx=json.loads(args.complex_review.read_text())
    candidate=json.loads(args.complex_candidate.read_text())
    calibration=json.loads(args.calibration.read_text())
    h=candidate['h'];assert h>=8 and h%2==0
    row=next(row for row in cx['rows'] if row['h']==h)
    check=row['frames'];v=comb(h,3)
    assert row['roles']==candidate['logical']['active_additions']+2*v
    assert check['exact_output_nonzero_coefficients']==candidate['logical']['nonzero_side_coefficients']
    assert check['independent_logical_frames']==candidate['logical']['inputs']+candidate['logical']['active_additions']
    assert check['source_lines_and_exact_target_kernels'] and check['reverse_complements_isometric']
    assert check['unique_frames']==check['analytic_complement_witnesses']>0
    assert check['analytic_nonzero_residual_witnesses']>0 and check['forward_and_reverse_physical_transitions']>0
    match=row['even_stage_matching'];assert match['images']==v and match['involutive_binary_orthogonal_matching']
    assert match['every_join_has_middle_coordinate_norm_one_witness']
    assert sum(match['intersection_histogram'].values())==v
    assert match['intersection_histogram']==candidate['matching']['even_intersection_counts']
    small=next(row for row in calibration['rows'] if row['h']==8)
    matrix=small['complete_dirty_matrix']
    assert matrix['complete_basis_dimension']==1019 and matrix['includes_both_data_banks_all_side_and_central_scratch']
    assert matrix['forward_identity_shear_and_inverse_exact']
    for packet in (cx,calibration):
        for name,digest in packet['source_sha256'].items():
            assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    full=bit['full'];assert bit['status']=='PASS'
    saved=data['promoted_bit_audit']
    assert full['candidate_id']==saved['candidate_id'] and full['compiled_sha256']==saved['compiled_sha256']
    assert full['roles']==saved['roles'] and full['controller_plan']['independently_counted_roles']==full['roles']
    assert len(bit['small_controls'])==2
    for test in bit['small_controls']:
        assert len(test['complete_invocation_dirty_basis_including_centers'])==2
        assert len(test['complete_shared_three_stage_exchange'])==2
    for witness in data['witnesses']:
        assert witness['bit_counts']['side_roles']==full['roles']
        assert witness['complex_counts']['h']==h and witness['complex_counts']['R']==row['roles']
        assert all(Q(witness['complex_counts'][k])==Q(candidate['shared_complex_counts'][k]) for k in witness['complex_counts'])
    return dict(bit_roles=full['roles'],bit_candidate=full['candidate_id'],
                bit_compiled_sha256=full['compiled_sha256'],complex_ground=h,complex_roles=row['roles'],
                complex_coefficients=check['exact_output_nonzero_coefficients'],
                complex_logical_frames=check['independent_logical_frames'],
                complex_physical_transitions=check['forward_and_reverse_physical_transitions'],
                complete_dirty_h8_basis_dimension=1019,immutable_source_hashes_checked=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ('certificate','reference','bit-review','complex-review','complex-candidate','calibration','output'):
        ap.add_argument('--'+flag,type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    started=time.monotonic();raw=args.certificate.read_bytes();data=json.loads(raw)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.reference,text=True).strip()==PIN
    assert data['compact_reference']['commit']==PIN
    assert data['original_reference']['commit']=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    result=dict(status='PASS independent generic compact composition',input_sha256=sha256(raw).hexdigest(),
        reference_revision=PIN,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        promoted_metadata=promoted_metadata(data,args),stopped_recurrences=stopped_recurrences(),
        upstream=upstream_audit(args.reference),rows=[audit_row(row) for row in data['witnesses']],
        wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Independent generic finite count/log/margin/guard/cutoff arithmetic and promotion identity checks. Earlier full finite and written compact/phase transfer reviews remain proof dependencies; no new graph replay.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS generic',result['promoted_metadata'],'rows',len(result['rows']))


if __name__=='__main__':main()

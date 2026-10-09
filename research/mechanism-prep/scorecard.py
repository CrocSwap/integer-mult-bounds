"""Mechanism accounting and a necessary joint design budget; no new network.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/kappa-nine'))
from target_budget import audit as baseline_audit, encode, moment, require, profile_parts


def log_bounds(x, terms=24, scale=10**24):
    """Independent rational atanh-series enclosure for log(x), x>=1."""
    x = Q(x)
    require(x >= 1 and terms > 0 and scale > 0, 'invalid logarithm')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def unit(r):
        z = (r-1)/(r+1)
        lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)),Q(0))
        return lo, lo+2*z**(2*terms+1)/((2*terms+1)*(1-z*z))

    a,b=unit(x); c,d=unit(Q(2))
    lower,upper=a+k*c,b+k*d
    floor=lambda r:r.numerator//r.denominator
    return Q(floor(lower*scale),scale),Q(-floor(-upper*scale),scale)


def profile_score(rows,m,W):
    """Numerical test of supplied counts, never a construction certificate."""
    require(m>1 and W>0 and rows,'nonempty profile required')
    for t,n in rows.items():
        require(type(t) is int and 0<t<m and n>=0,'invalid contracting child')
    mass=Q(sum(t*n for t,n in rows.items()),W*m)
    eta=1-mass
    Hlo=Hhi=Q(0)
    for t,n in rows.items():
        lo,hi=log_bounds(Q(m,t))
        weight=Q(n*t,W*m)
        Hlo+=weight*lo; Hhi+=weight*hi
    require(Hlo>0,'profile has no positive work')
    bound=moment(rows,m,W)
    return dict(rank_deficit=eta,rank_mass=mass,
        log_width_penalty_coefficient_interval=[Hlo,Hhi],
        necessary_saving_upper=eta/Hlo if eta>0 else Q(0),
        target_moment_interval=bound,
        target_arithmetic='below_one' if bound[1]<1 else 'above_one' if bound[0]>1 else 'unresolved',
        provenance_status='Supplied profile arithmetic only. Physical implementation and transfer obligations are external.')


def design_envelope(da,db):
    """Necessary screen for the explicitly assumed rank-one pair ledger.

    rho_i=auxiliary roles per label; lambda_i=copied central loss per label.
    Exact feasibility: sum rho_i*A_i + lambda_i*B_i < C.
    All macros are optimistically packed into their whole rank.
    """
    require(type(da) is int and type(db) is int and da>=2 and db>=2,'axis dimensions')
    m=da*db
    f=lambda t:moment({t:1},m,1)
    data=Counter({(da-1)*(db-1):2,1:1})
    data[da-1]+=2; data[db-1]+=2
    D=moment(data,m,1)
    C=(2-D[1],2-D[0])
    A=[]; B=[]
    for d in (da,db):
        x,y=f(d),f(m-d)
        A.append((x[0]+y[0]-1,x[1]+y[1]-1))
        B.append((x[0]/d,x[1]/d))
    require(all(x[0]>0 for x in A+B),'positive overhead coefficients')
    # C>0 in the three named illustrations. No parameter sweep is performed.
    require(C[0]>0,'even free geometry fails')
    rho=(C[0]/sum(x[1] for x in A),C[1]/sum(x[0] for x in A))
    residual=(C[0]-sum(x[1] for x in A),C[1]-sum(x[0] for x in A))
    denominators=(sum(x[0] for x in B),sum(x[1] for x in B))
    quotients=[n/d for n in residual for d in denominators]
    return dict(dimensions=[da,db],m=m,data_profile_per_pair=data,
        available_budget_interval=C,role_cost_coefficients=A,loss_cost_coefficients=B,
        equal_role_ratio_ceiling_with_zero_loss_interval=rho,
        equal_loss_ratio_ceiling_with_one_role_per_label_interval=[min(quotients),max(quotients)],
        scope='Necessary optimistic screen only for a rank-one two-stage copied-center ledger. New cores must prove that ledger and their actual ordered profiles. Passing is not a finite certificate.')


def envelope_residual(envelope,rhos,losses):
    """Positive returned lower bound certifies ONLY optimistic headroom."""
    require(len(rhos)==len(losses)==2 and all(Q(x)>=0 for x in (*rhos,*losses)),'nonnegative axis costs')
    lo,hi=envelope['available_budget_interval']
    for values,coefficients in ((rhos,envelope['role_cost_coefficients']),
                                (losses,envelope['loss_cost_coefficients'])):
        for v,(a,b) in zip(values,coefficients):
            lo-=Q(v)*b; hi-=Q(v)*a
    return lo,hi


def audit():
    pinned=baseline_audit()
    cert=json.loads((ROOT/'research/kappa-nine/baseline/certificate.json').read_text())
    profiles=[json.loads((ROOT/f'research/kappa-nine/baseline/profiles-{d}.json').read_text()) for d in (23,25)]
    b=cert['bit']; N,m,W,L=(b[k] for k in ('N','m','W','L'))
    rows=Counter({int(t):n for t,n in b['child_multiplicities'].items()})
    require(b['total_rank']==W*m-N+L,'modern rank ledger')
    require(L==sum(N//p['v']*p['h']*(p['h']-1) for p in profiles),'copied central losses')
    score=profile_score(rows,m,W)
    parts=profile_parts(cert,profiles)
    penalties={}
    for name,part in parts.items():
        mass=Q(sum(t*n for t,n in part.items()),W*m)
        lo,hi=moment(part,m,W)
        penalties[name]=[lo-mass,hi-mass]
    require(Q(cert['bit_saving'])<score['necessary_saving_upper'],'entropy necessary bound')
    examples=[design_envelope(12,12),design_envelope(16,16),design_envelope(23,25)]
    current=examples[-1]
    rhos=[Q(p['R'],p['v']) for p in profiles]
    losses=[Q(p['h']*(p['h']-1),p['v']) for p in profiles]
    # The new affine formula reproduces the old source-floor exclusion.
    source_floor=envelope_residual(current,[1,1],[0,0])
    require(source_floor[1]<0,'source floor must fail')
    raw=Counter(current['data_profile_per_pair'])
    for p,rho,loss in zip(profiles,rhos,losses):
        d=p['h'];raw[d]+=rho+loss/d;raw[m-d]+=rho
    direct=moment(raw,m,2+sum(rhos))
    residual=envelope_residual(current,rhos,losses)
    norm=2+sum(rhos)
    require(residual[0]<=norm*(1-direct[0]) and residual[1]>=norm*(1-direct[1]),'affine/direct consistency')
    sources=['docs/research/rank-product-core.md','notes/copied-centers-lemma.tex',
      'references/copied-centers/pr29/two-stage-16-note.tex',
      'research/kappa-nine/target_budget.py','research/kappa-nine/baseline/SOURCE.json',
      'docs/research/stronger-rank-screens.md','research/pair-assembly/balanced_assembly.py']
    return dict(status='MECHANISM AND REPLACEMENT SPECIFICATION; NO NEW CONSTRUCTION',
      pinned_baseline=pinned['baseline'],target_kappa=Q(1,512),
      necessary_bit_saving=Q(1,511),necessary_complex_at_beta_1_over_20=Q(20,9709),
      baseline=dict(N=N,m=m,W=W,L=L,gross_gain=N,surviving_gain=N-L,
        same_dimensions_without_copied_center_gain=N-2*L,
        central_loss_fraction=Q(L,N),surviving_gain_fraction=Q(N-L,N),
        roles_per_pair=Q(W,N),axis_role_ratios=rhos,axis_loss_ratios=losses,
        bit_saving=Q(cert['bit_saving']),conditional_kappa=Q(cert['kappa']),
        target_to_pinned_bit_saving=Q(1,511)/Q(cert['bit_saving']),
        score=score,target_penalty_by_physical_component=penalties),
      illustrative_envelopes=examples,
      storage_floor=dict(contract='V: k^n -> k^R, L: k^R -> k^R, J: k^R -> k^n, JLV=I_n',
        conclusion='R>=n by rank(I_n)<=rank(V)<=R',
        scope='One independent transparent producer factoring the entire identity through auxiliary space. Does not cover direct data-to-data paths, interleaved source access without this factorization, or cross-invocation encodings.'),
      envelope_checks=dict(actual_ratios_optimistic_residual=residual,
        direct_optimistic_moment=direct,one_source_zero_loss_residual=source_floor),
      construction_or_candidate_selected=False,parameter_search_performed=False,
      source_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print('PASS modern ledger, exact moment/entropy enclosures, joint budget and pinned baseline')
    print('No new geometry, circuit, exponent, or candidate selection')

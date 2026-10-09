#!/usr/bin/env python3
"""Exact stopped signed-gauge recurrence and balanced positional transfer.

Physical stopped-product construction: icekylinx; pair-order predecessor:
Rohan Arun; original semantic/bulk and balanced interfaces: Zhihao Chen,
RaD/hipotures, jamesyc and credited predecessors. The assembly function below
is retained verbatim from the pinned copied-fixed balanced arithmetic; its
validator explicitly checks the three-factor stopped row stock instead of
silently applying the older two-factor formula. Apache-2.0; Codex assistance.
"""
import sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE=ROOT/'references/stopped-recursion/pr107'
GRID=10**18
ATOM=Q(1,1000)
BETA=Q(1,10**12)
BACKOFF=Q(1,GRID)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def read(path):return json.loads(path.read_text())
def js(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):js(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [js(v)for v in value]
    return value

def input_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class InvalidAssembly(AssertionError):
    """A named exact input validation or strict inequality failed."""

def require(condition, message):
    if not condition:
        raise InvalidAssembly(message)

def rational(value):
    # Fraction(float) silently preserves binary floating error; forbid it.
    require(type(value) in (int, str, Q), 'expected integer or exact rational string/Fraction')
    return Q(value)

def integer(value):
    x = rational(value)
    require(x.denominator == 1, 'nonintegral graph constant')
    return x.numerator

def ceil(value):
    return -(-value.numerator // value.denominator)

def halving_degree(m, child):
    require(0 < child < m, 'child must strictly contract')
    degree = 1
    while m**degree <= 2 * child**degree:
        degree += 1
    return degree

def assembly(finite_bridge, a_bit, kappa, beta=Q(1,20), h=Q(1,10**12),
             a_complex=Q(717,10**7), *, original_prefix=False,
             old_guard=False, old_exposures=False):
    """Return 47 strict slacks and seven margins, or raise InvalidAssembly.

    The three keyword switches are negative controls: they impose the old
    prefix, nonlinear guard, or old separate movement charges at these SAME
    balanced parameters. They do not silently optimize an alternative family.
    """
    f = validate_bridge(finite_bridge)
    a, b, kappa, beta, h = map(rational, (a_bit,a_complex,kappa,beta,h))
    require(0 < h < Q(1,2) and kappa > 0, 'positive backoff and saving required')
    tau, sigma = 1-a, 1-b
    q = a*(1-2*h)
    require(1+q != 0, 'undefined balanced epsilon')
    lp, c, eps = 1-q, q+h/4, (1-h)/(1+q)
    lam = (tau+lp)/2
    G = eps*q
    r, delta = (G+1-eps)/2, h/8
    C1 = Q(19991,10000) if old_guard else Q(1)
    margins = dict(g1=1-eps, g2=a, g3=G, g4=a,
                   g5=min(1-eps-delta,r-delta), g6=1-eps-delta, g7=eps)
    if original_prefix:
        margins['g1'] = 1-eps*(1+c)
    if old_exposures:
        margins.update(g2=eps*c*a, g4=a*(1-eps))
    internal = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    slacks = dict(a_positive=a, a_below_b=b-a, b_below_one_over32=Q(1,32)-b,
        beta_positive=beta, beta_below_one=1-beta, phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf, compact_reservations=lp-(1-c), lambda_prime_below_one=q,
        epsilon_positive=eps, epsilon_below_one=1-eps, guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c), K_dominates_log=eps*c,
        record_suffix=1-eps, phase_local=1-eps-delta, phase_boundary=r-delta,
        gamma_sublinear=1-eps-r, cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r, delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta, short_record_fallback=eps-a,
        small_field_exposure=1-eps-G, artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(f['semantic']['strict_literal_gap']),
        row_product_gap=f['rows']['degree_gap'])
    slacks.update({name+'_above_kappa': value-kappa for name,value in margins.items()})
    require(len(slacks) == 47 and len(margins) == 7, 'constraint list incomplete')
    failed = {name:str(value) for name,value in slacks.items() if value <= 0}
    require(not failed, str(failed))
    require(min(margins.values()) == G, 'unexpected controlling margin')
    require(1-eps-G == h and 1-eps-r == h/2, 'balanced identities failed')
    require(1-eps*(1+c) == h-eps*h/4, 'geometric identity failed')
    parameters = dict(a_bit=a, a_complex=b, tau=tau, sigma=sigma, beta=beta,h=h,
        q=q,c=c,epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=parameters,constraints=slacks,margins=margins,
        minimum_margin=G,absorption_gap=G-kappa,scoped_limit=a/(1+a),
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c),finite_bridge=f)


def bit_profile(record):
    h,v,R=(integer(record[k])for k in ('h','v','R'))
    require(v==math.comb(h,3)and record['loss']==h*(h-1),'Bit dimensions/loss mismatch')
    H=list(record['histogram']);require(len(H)==h+1 and all(type(n)is int and n>=0 for n in H),'Malformed bit histogram')
    require(sum(r*n for r,n in enumerate(H))==h*R+2*h*(h-1),'Bit rank mass mismatch')
    H[h]-=h;H[1]+=h;require(min(H)>=0,'Unpaid center correction')
    m,N,bank=h*h,v*v,v*R;W=2*N+2*bank
    rows=Counter({m-h:2*bank,(h-1)**2:2*N,h-1:4*N,1:N})
    for r,n in enumerate(H):
        if r and n:rows[r]+=2*v*n
    rank=sum(r*n for r,n in rows.items());loss=2*v*h*(h-1)
    require(rank==m*W-N+loss,'Complete bit rank mismatch')
    return dict(dimensions=[h,h],m=m,N=N,B1=bank,B2=bank,W=W,L=loss,total_rank=rank,
        deficit=N-loss,maxchild=max(rows),copied_histogram=H,child_multiplicities=dict(rows))


def complex_profile(word,screen):
    h,v,R=(integer(word[k])for k in ('h','v','R'));m=h*h;N=v*v;W=2*N+2*v*R
    require(h==24 and v==math.comb(h,3),'Selected complex dimensions differ')
    require(word['status']=='EXACT_LOCAL_SCHEDULE_PASS','Local signed schedule did not pass')
    for key in ('all_data_readout_chains_verified','all_gates_equal_frame','all_moves_nested_and_nondegenerate',
                'all_reordered_precedence_edges_verified','all_sigma_signed_target_caps_verified',
                'center_phase_untouched_verified','reflected_opposite_signed_schedule_verified','reflected_rank_histogram_identical'):
        require(word[key]is True,'Missing local check: '+key)
    sigma={int(r):n for r,n in screen['sigma_dimensions'].items()}
    require(all(0<r<=h and type(n)is int and n>0 for r,n in sigma.items()),'Malformed sigma inventory')
    count=sum(sigma.values());mass=sum(r*n for r,n in sigma.items())
    require((count,mass)==(word['selected_gauges'],word['sigma_rank_sum']),'Sigma inventory mismatch')
    require((count,mass)==(screen['selected_positive_roles'],screen['sum_sigma_dimensions']),'Selection inventory mismatch')
    require(word['word_sha256']==screen['word_sha256'],'Unbound selected word')
    local={name:{int(r):n for r,n in entries.items()}for name,entries in word['local_histograms'].items()}
    require(set(local)=={'aux','data','center'},'Local classes incomplete')
    targets=dict(aux=h*R-mass,data=2*v*(h-1),center=h*(h-1))
    recorded=dict(aux=word['auxiliary_internal_rank_mass'],data=word['local_data_rank_mass'],center=word['center_copy_rank_mass'])
    rows=Counter({(h-1)**2:2*N,1:N,m-h:2*v*(R-count)})
    for rank,n in sigma.items():rows[m-h+rank]+=2*v*n
    for name,entries in local.items():
        require(all(0<=r<=h and type(n)is int and n>=0 for r,n in entries.items()),'Malformed local histogram')
        require(sum(r*n for r,n in entries.items())==targets[name]==recorded[name],'Local rank mismatch')
        for rank,n in entries.items():
            if rank and n:rows[rank]+=2*v*n
    rows={r:n for r,n in rows.items()if n}
    require(rows=={int(r):n for r,n in word['full_paid_histogram'].items()if n},'Literal paid histogram mismatch')
    require(rows=={int(r):n for r,n in screen['histogram'].items()if n},'Independent selection histogram mismatch')
    require(all(0<r<m and n>0 for r,n in rows.items()),'Improper complex child')
    rank=sum(r*n for r,n in rows.items());loss=2*v*h*(h-1)
    require(rank==m*W-N+loss==screen['rank_mass'],'Complex rank deficit mismatch')
    require((m,W,max(rows))==(screen['m'],screen['W'],word['maxchild']),'Complex widths differ')
    return dict(dimensions=[h,h],m=m,N=N,B1=v*R,B2=v*R,W=W,L=loss,total_rank=rank,
        deficit=N-loss,maxchild=max(rows),local_histograms=local,sigma_dimensions=sigma,child_multiplicities=rows)


def charge_inventory(word,charge):
    h,v,R=(integer(word[k])for k in ('h','v','R'))
    require((h,v,R)==tuple(charge[k]for k in ('h','v','R')),'Charge dimensions differ')
    require(word['word_sha256']==charge['word_sha256'],'Charge bound belongs to different word')
    require(charge['status']=='EXACT_COUNT_AND_CONSERVATIVE_BOUND','Scalar charge check missing')
    require(charge['forward_events']==word['forward_events']and charge['deferred_readout_nonzero_coefficients']==word['actual_deferred_signed_adds'],'Scalar event counts differ')
    require(charge['full_readout_nonzero_coefficients']==charge['early_readout_nonzero_coefficients']+charge['deferred_readout_nonzero_coefficients'],'Readout split mismatch')
    require(charge['expanded_center_terms']==h*v,'Center expansion mismatch')
    require(charge['coefficient_denominator']==42 and 0<charge['coefficient_absolute_numerator_bound']<2**16,'Coefficient bound mismatch')
    local=word['forward_events']+charge['early_readout_nonzero_coefficients']+2*h*v+8*h+8
    g=64*local;G=v*v+2*v*(g+2*h)
    require((local,g,G)==tuple(charge[k]for k in ('conservative_local_groups','local_scalar_charge','G0')),'Incomplete scalar charge')
    require(charge['coefficient_binary_height_charge']==64,'Height charge changed')
    return dict(h=h,v=v,forward_events=word['forward_events'],early_readout_nonzero_coefficients=charge['early_readout_nonzero_coefficients'],
        deferred_readout_nonzero_coefficients=charge['deferred_readout_nonzero_coefficients'],
        coefficient_absolute_numerator_bound=charge['coefficient_absolute_numerator_bound'],coefficient_denominator=42,
        coefficient_binary_height_charge=64,conservative_local_groups=local,local_scalar_charge=g)


def make_bridge(bit,cx,inventory):
    f={}
    for name,p in [('bit_coarse',bit),('complex',cx)]:
        f[name]=dict(m=p['m'],W=p['W'],maxchild=p['maxchild'],halving_degree=halving_degree(p['m'],p['maxchild']),wire_bits=p['W'].bit_length())
    h,v=inventory['h'],inventory['v'];G=v*v+2*v*(inventory['local_scalar_charge']+2*h)
    f['complex'].update(s=cx['total_rank'],scalar_inventory=inventory,scalar_group_upper=G)
    m,W,s,r=(cx[k]for k in ('m','W','total_rank','maxchild'));E=64*(W+m+G+1)**3;B=s+E
    literal=2*G*W*W+8*s+4*W+4+32*m
    f['semantic']=dict(E=E,B=B,C0=32*m*B*B,C1=1,literal_charge=literal,strict_literal_gap=E-literal,
        induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=21,
        exact_grid='One common dyadic grid times 21^K, K=G0*(D_complex+1); no child rounding')
    old=read(ARCHIVE/'certificates/copied-centers-network.json')['finite_bridge']['bit']
    degree=halving_degree(old['m'],old['maxchild'])*old['W'].bit_length();f['ordinary_leaf_row_degree']=degree
    coefficient=degree+sum(f[k]['halving_degree']*f[k]['wire_bits']for k in ('complex','bit_coarse'))
    f['rows']=dict(coefficient=coefficient,degree=10000,suffix_slope=40000,degree_gap=Q(10000)-Q(51,25)*coefficient,
        contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse')
    return validate_bridge(f)


def validate_bridge(f):
    coefficient=0
    for name in ('bit_coarse','complex'):
        p=f[name];m,W,r=(integer(p[k])for k in ('m','W','maxchild'))
        require(p['halving_degree']==halving_degree(m,r)and p['wire_bits']==W.bit_length(),'Stale recursion depth')
        coefficient+=p['halving_degree']*p['wire_bits']
    old=read(ARCHIVE/'certificates/copied-centers-network.json')['finite_bridge']['bit']
    degree=halving_degree(old['m'],old['maxchild'])*old['W'].bit_length()
    require(degree==252==f['ordinary_leaf_row_degree'],'Ordinary leaf reserve omitted')
    coefficient+=degree;p=f['complex'];i=p['scalar_inventory'];h,v=i['h'],i['v']
    local=i['forward_events']+i['early_readout_nonzero_coefficients']+2*h*v+8*h+8
    require(local==i['conservative_local_groups']and 64*local==i['local_scalar_charge'],'Incomplete scalar work')
    require(i['coefficient_binary_height_charge']==64 and i['coefficient_denominator']==42 and 0<i['coefficient_absolute_numerator_bound']<2**16,'Coefficient height contract')
    G=v*v+2*v*(64*local+2*h);require(G==p['scalar_group_upper'],'Wrong scalar charge')
    m,W,r,s=(integer(p[k])for k in ('m','W','maxchild','s'));E=64*(W+m+G+1)**3;B=s+E
    literal=2*G*W*W+8*s+4*W+4+32*m
    expected=dict(E=E,B=B,C0=32*m*B*B,C1=1,literal_charge=literal,strict_literal_gap=E-literal,induction_gap=2*B*(m-r)-s-E)
    require(all(f['semantic'][k]==value for k,value in expected.items()),'Stale semantic bridge')
    require(E>literal and expected['induction_gap']>=0 and expected['C0']>2*B+18,'Semantic induction fails')
    require(f['semantic']['fixed_odd_divisor']==21,'Changed odd denominator')
    rows=f['rows'];gap=Q(10000)-Q(51,25)*coefficient
    require(coefficient==rows['coefficient']==3528 and rows['degree']==10000 and rows['suffix_slope']==40000 and rows['degree_gap']==gap>0,'Three-factor row stock mismatch')
    return f


def sharp_moment(module,p):
    m,W,rows=(p[k]for k in ('m','W','child_multiplicities'))
    lo,hi=0.,.001
    for _ in range(60):
        a=(lo+hi)/2
        if math.fsum(t*n/(m*W)*math.exp(a*math.log(m/t))for t,n in rows.items())<1:lo=a
        else:hi=a
    center=int(lo*GRID);left,right=center-10**6,center+10**6
    require(module.exact_moment(m,W,rows,Q(left,GRID))['upper']<1<module.exact_moment(m,W,rows,Q(right,GRID))['lower'],'Moment bracket fails')
    while right-left>1:
        mid=(left+right)//2
        if module.exact_moment(m,W,rows,Q(mid,GRID))['upper']<1:left=mid
        else:right=mid
    accepted=module.exact_moment(m,W,rows,Q(left,GRID));rejected=module.exact_moment(m,W,rows,Q(right,GRID))
    require(accepted['upper']<1<rejected['lower'],'Adjacent moment grids not separated')
    return dict(saving=Q(left,GRID),moment=accepted,next_saving=Q(right,GRID),next_moment=rejected)


def compose(work=None):
    base=work or HERE
    data=dict(bit=read(base/'bit-axis.json'),bit_audit=read(base/'bit-audit.json'))
    if work:data.update({name:read(base/file)for name,file in [('complex_word','complex-word.json'),('complex_screen','complex-screen.json'),('complex_charge','complex-charge.json')]})
    else:
        combined=read(base/'complex-axis.json');data.update({name:combined[key]for name,key in [('complex_word','word'),('complex_screen','screen'),('complex_charge','charge')]})
    bit=bit_profile(data['bit']);ba=data['bit_audit']
    require(bit['copied_histogram']==ba['copied_rank_histogram'],'Copied bit ledger differs')
    require(data['bit']['source_word_sha256']==ba['source_word_sha256'],'Bit physical word binding differs')
    require(sum(r*n for r,n in enumerate(bit['copied_histogram']))==ba['rank_mass'],'Bit local mass differs')
    for key in ('nonidentity_label_events_match_actual_word','full_inherited_dirty_replay_equal','all_frame_gram_inverses_exact','all_side_hyperplane_inclusions_exact'):
        require(ba[key]is True,'Bit check missing: '+key)
    counted=Counter()
    for component in ba['paid_components'].values():
        for rank,n in component.items():require(type(n)is int and n>=0,'Invalid bit component');counted[int(rank)]+=n
    require([counted[r]for r in range(data['bit']['h']+1)]==bit['copied_histogram'],'Incomplete bit components')
    cx=complex_profile(data['complex_word'],data['complex_screen'])
    inventory=charge_inventory(data['complex_word'],data['complex_charge']);bridge=make_bridge(bit,cx,inventory)
    moments=load('gauge_primary_moments',ROOT/'references/signed-recursion/pr100/research/deferred-balanced/moments.py')
    old=read(ARCHIVE/'certificates/copied-centers-network.json')
    coarse=sharp_moment(moments,bit);phase=sharp_moment(moments,cx)
    leaf=Q(old['bit']['saving']);require(leaf==Q(384599,10**10),'Inherited ordinary leaf differs')
    stopped=(1-ATOM)*coarse['saving']+ATOM*leaf
    require(0<leaf<coarse['saving']<ATOM<1 and ATOM>stopped,'Stopped recurrence/adapter fails')
    require(bit['total_rank']<bit['m']*bit['W'],'Bit rank moment fails')
    b=phase['saving'];a=min(stopped,(1-BETA)*b-BACKOFF)
    q=a*(1-2*BACKOFF);g=(1-BACKOFF)*q/(1+q);k=Q((g*GRID).__floor__(),GRID)
    if k==g:k-=Q(1,GRID)
    result=assembly(bridge,a,k,beta=BETA,h=BACKOFF,a_complex=b)
    try:assembly(bridge,a,k+Q(1,GRID),beta=BETA,h=BACKOFF,a_complex=b)
    except InvalidAssembly:pass
    else:raise AssertionError('Adjacent kappa grid accepted')
    return dict(scope='Finite complete signed-gauge and rational-frame rank ledgers; opposite-bank, complex normal form, atom streaming, exact odd grid, balanced layout and inherited analytic/tape contracts remain explicit proof dependencies.',
        kappa=k,bit_saving=a,h=BACKOFF,beta=BETA,coarse_bit=dict(profile=bit,**coarse),
        ordinary_bit=dict(saving=stopped,atom_exponent=ATOM,leaf_saving=leaf,coarse_saving=coarse['saving'],adapter_gap=ATOM-stopped,ordinary_leaf_bridge=old['finite_bridge']['bit']),
        complex=dict(profile=cx,**phase),assembly=result,next_kappa_grid_rejected=True,
        input_sha256={name:input_hash(value)for name,value in data.items()},
        previous_pairtree_kappa=Q(7808981744031,10**17),improvement_over_pairtree=k-Q(7808981744031,10**17))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path);parser.add_argument('--output',type=Path,default=HERE/'certificate.json');args=parser.parse_args()
    certificate=compose(args.work);args.output.write_text(json.dumps(js(certificate),indent=2,sort_keys=True)+'\n')
    print('PASS complete stopped signed-gauge recurrence; complex saving',certificate['complex']['saving'],'kappa',certificate['kappa'],'47 constraints / seven margins')
if __name__=='__main__':main()

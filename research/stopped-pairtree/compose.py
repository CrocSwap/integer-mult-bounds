#!/usr/bin/env python3
"""Exact stopped pair-tree recurrence and balanced positional transfer.

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
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE=ROOT/'references/stopped-recursion/pr107'
GRID=10**18
COARSE=Q(4019,50000000)
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


def validate_bridge(f):
    """Check the coarse bit, ordinary leaf, and complex reserves together."""
    f={k:(dict(v)if isinstance(v,dict)else v)for k,v in f.items()}
    coefficient=0
    for name in ('bit_coarse','complex'):
        p=f[name];m,W,r=(integer(p[k])for k in ('m','W','maxchild'))
        require(p['halving_degree']==halving_degree(m,r)and p['wire_bits']==W.bit_length(),'Stale recursion depth')
        coefficient+=p['halving_degree']*p['wire_bits']
    old=read(ARCHIVE/'certificates/copied-centers-network.json')['finite_bridge']['bit']
    old_degree=halving_degree(old['m'],old['maxchild'])*old['W'].bit_length()
    require(old_degree==old['halving_degree']*old['wire_bits']==f['ordinary_leaf_row_degree'],'Ordinary leaf stock omitted')
    coefficient+=old_degree
    p=f['complex'];m,W,r,s=(integer(p[k])for k in ('m','W','maxchild','s'))
    N=math.comb(math.isqrt(m),3)**2;G=N
    for term in p['scalar_terms']:
        h,v,c=(integer(term[k])for k in ('h','v','c'))
        local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8
        require(term['local_group_upper']==local and term['copied_center_extra_groups']==2*h and term['invocations']*v==N,'Scalar term mismatch')
        G+=term['invocations']*(local+2*h)
    require(G==p['scalar_group_upper'],'Scalar charge mismatch')
    E=64*(W+m+G+1)**3;B=s+E;literal=2*G*W*W+8*s+4*W+4+32*m
    expected=dict(E=E,B=B,C0=32*m*B*B,C1=1,literal_charge=literal,strict_literal_gap=E-literal,induction_gap=2*B*(m-r)-s-E)
    require(all(f['semantic'][key]==value for key,value in expected.items()),'Semantic constants differ')
    require(E>literal and expected['induction_gap']>=0 and expected['C0']>2*B+18,'Semantic induction fails')
    require(f['semantic']['fixed_odd_divisor']==21,'Changed denominator contract')
    rows=f['rows'];degree=integer(rows['degree']);gap=Q(degree)-Q(51,25)*coefficient
    require(coefficient==rows['coefficient'] and degree==4000 and rows['suffix_slope']==4*degree and rows['degree_gap']==gap>0,'Three-factor row reserve mismatch')
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
    data={name:read(base/file)for name,file in [('complex','producer.json'),('construction','constructor.json')]}
    data['bit']=read(ARCHIVE/'certificates/stopped-product-bit-axis.json')
    row,construction=data['complex'],data['construction']
    for key in ('h','v','c','q','loss','central_disjoint','center_denominator'):require(row[key]==construction[key],'Construction/matching mismatch: '+key)
    require(row['baseline_R']==construction['R']==row['c']+row['q'],'Baseline role count mismatch')
    require(row['R']==row['baseline_R']-row['matched'],'Matched role count mismatch')
    checks=construction['scalar_validation']
    require(all(checks[k]for k in ('ordinary_supports_exact','centers_exact','rational_scalar_identity_exact','mixed_center_scatter_exact','binary_frames_nested','binary_frames_nondegenerate')),'Producer checks incomplete')
    require(data['bit']==read(ARCHIVE/'certificates/stopped-product-bit-axis.json'),'Inherited coarse bit axis changed')
    sys.path.insert(0,str(ARCHIVE/'scripts'))
    parent=load('pairtree_stopped_parent',ARCHIVE/'scripts/stopped_product_network.py')
    moments=load('pairtree_primary_moments',ROOT/'references/signed-recursion/pr100/research/deferred-balanced/moments.py')
    old=read(ARCHIVE/'certificates/copied-centers-network.json')
    bit,cx=parent.profile(data['bit']),parent.profile(row)
    bridge=parent.finite_bridge(bit,cx,row,old);validate_bridge(bridge)
    leaf=Q(old['bit']['saving']);require(leaf==parent.OLD,'Ordinary leaf saving changed')
    stopped=(1-ATOM)*COARSE+ATOM*leaf
    require(stopped==parent.AB and 0<leaf<COARSE<ATOM<1 and ATOM>stopped,'Stopped recurrence or adapter inequality failed')
    bit_moment=moments.exact_moment(bit['m'],bit['W'],bit['child_multiplicities'],COARSE)
    require(bit_moment['upper']<1 and bit['total_rank']<bit['m']*bit['W'],'Coarse rank and exponent moments fail')
    phase=sharp_moment(moments,cx);b=phase['saving'];a=min(stopped,(1-BETA)*b-BACKOFF)
    q=a*(1-2*BACKOFF);g=(1-BACKOFF)*q/(1+q);k=Q((g*GRID).__floor__(),GRID)
    if k==g:k-=Q(1,GRID)
    result=assembly(bridge,a,k,beta=BETA,h=BACKOFF,a_complex=b)
    try:assembly(bridge,a,k+Q(1,GRID),beta=BETA,h=BACKOFF,a_complex=b)
    except InvalidAssembly:pass
    else:raise AssertionError('Adjacent kappa grid accepted')
    return dict(scope='Finite supplied pair-tree profile and exact stopped recurrence; opposite-bank, atom-streaming, odd-grid, balanced-layout and inherited analytic/tape contracts remain explicit proof dependencies.',
        kappa=k,bit_saving=a,h=BACKOFF,beta=BETA,coarse_bit=dict(profile=bit,saving=COARSE,moment=bit_moment),
        ordinary_bit=dict(saving=stopped,atom_exponent=ATOM,leaf_saving=leaf,coarse_saving=COARSE,
            adapter_gap=ATOM-stopped,ordinary_leaf_bridge=old['finite_bridge']['bit']),
        complex=dict(profile=cx,**phase),assembly=result,next_kappa_grid_rejected=True,
        input_sha256={name:input_hash(value)for name,value in data.items()},
        previous_pr107_kappa=Q(7798412662809,10**17),improvement_over_pr107=k-Q(7798412662809,10**17))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path);parser.add_argument('--output',type=Path,default=HERE/'certificate.json');args=parser.parse_args()
    certificate=compose(args.work);args.output.write_text(json.dumps(js(certificate),indent=2,sort_keys=True)+'\n')
    print('PASS complete pair-tree recurrence; complex saving',certificate['complex']['saving'],'kappa',certificate['kappa'],'47 constraints / seven margins')
if __name__=='__main__':main()

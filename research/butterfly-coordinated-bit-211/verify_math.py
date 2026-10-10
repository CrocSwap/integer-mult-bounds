"""Fresh final-bit profile, finite ordinary leaf, packed bill and PR193 bridge."""
from common import *
import copy
from finite_bridge import validate_loose

def run(complex_root,bit_root,fresh,packing):
    expected=read(HERE/'expected-math.json');row=fresh['profile'];p=packing['profile']
    im=module('v5_moment',bit_root/'research/paired-cube-diagonal-bit-168/arithmetic/interval_moment.py')
    audit=module('v5_independent',HERE/'moment_audit.py')
    def profile(r):return dict(m=r['m'],W=r['W_per_vertex'],N=r['deficit_per_vertex'],L=0,total_rank=r['rank_per_vertex'],maxchild=r['maxchild'],child_multiplicities={int(k):v for k,v in r['child_histogram'].items()})
    def paid(p,a):
        z=im.moment(p,a);l,u=im.log_interval(Q(p['m']));l,u=im.exp_interval(a*l,a*u)
        debt=Q(32*p['m']*sum(p['child_multiplicities'].values()),10**16*p['W'])
        return dict(lower=z['lower']+debt*l,upper=z['upper']+debt*u)
    def root(p):
        lo,hi,den=0,10**16,10**18
        while hi-lo>1:
            mid=(lo+hi)//2;z=paid(p,Q(mid,den))
            if z['upper']<1:lo=mid
            elif z['lower']>1:hi=mid
            else:raise AssertionError('Increase interval precision')
        a=Q(lo,den);assert paid(p,a)['upper']<1<paid(p,a+Q(1,den))['lower'];return a
    original=profile(row);c0=root(original)
    retained=profile(read(HERE/'base-bit-certificate.json')['profile'])
    retained_c0=root(retained);assert retained_c0==Q(expected['bit_coarse'])
    old=Q(384599,10**10);threshold=retained_c0/(1+retained_c0-old);z=threshold*10**24;theta=Q(z.numerator//z.denominator+1,10**24)
    base=(1-theta)*retained_c0+theta*old;previous=theta-Q(1,10**24)
    assert base<theta<1-base and previous<=(1-previous)*retained_c0+previous*old
    assert base==Q(expected['bit_ordinary'])
    pc=root(p);assert pc==Q(expected['packed_coarse'])
    l,u=audit.moment(p,pc,True);nl,nu=audit.moment(p,pc+Q(1,10**18),True);assert u<1<nl
    chain=[base]
    for _ in range(3):
        a=(1-pc)*pc+pc*chain[-1];assert chain[-1]<a<pc<1-a;chain.append(a)
    assert list(map(str,chain))==expected['packed_ordinary_chain']
    assert json.loads(json.dumps(p))==expected['packed_profile']
    cp=read(complex_root/'research/source-assisted-v4/certificate.json');saving=Q(cp['complex_saving']);assert saving==Q(expected['complex_saving'])==Q(219037,312500000)
    cx=dict(Q=Q,GRID=1<<120,BAD=Q(1,10**16))
    functions(complex_root/'research/source-assisted/global/assemble_profiles.py',['up','log_upper','exp_upper','normalize','moment'],cx)
    cm=cx['normalize'](cp['complex_profile']);cmoment=cx['moment'](cm,saving)
    assert cmoment['strict_gap_lower']==Q(cp['assembly']['complex']['strict_gap_lower'])>0
    bridge=copy.deepcopy(cp['assembly']['finite_bridge']);bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
    finite=validate_loose(bridge,cp['complex_profile'],cm)
    scalar=packing['scalar'];assert scalar['all_nine_invocations_literal_xors']==expected['literal_xors']==7093890
    assert scalar['selector_calls_separate']==expected['selector_calls']==5701209426<2**40
    assert scalar['nine_invocation_guard']<scalar['nine_invocation_existing_v4_guard']<2**finite['local_groups_upper_power2']
    gap=1-chain[-1]-pc;assert gap>0 and Q(2*72**3,2**80)<Q(1,10**16)
    ac=dict(Q=Q);functions(complex_root/'scripts/paired_cube_assembly.py',['assembly'],ac)
    eta=beta=Q(1,10**24);a=min(chain[-1],(1-beta)*saving-Q(1,10**30));assert a==chain[-1]
    q=a*(1-2*eta);z=(1-eta)*q/(1+q)*10**18;k=Q((z.numerator-1)//z.denominator,10**18)
    assembly=ac['assembly'](a,saving,bridge,k,eta=eta,beta=beta)
    assert k==Q(expected['kappa']) and len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7
    assert all(x>0 for x in assembly['strict_constraints'].values()) and all(x>k for x in assembly['margins'].values())
    try:ac['assembly'](a,saving,bridge,k+Q(1,10**18),eta=eta,beta=beta)
    except AssertionError:pass
    else:raise AssertionError('Adjacent headline accepted')
    return dict(kappa=k,bit_profile=original,bit_coarse=c0,retained_seed_profile=retained,retained_seed_coarse=retained_c0,retained_seed_freshly_replayed=False,bit_ordinary=base,atom_theta=theta,packed_profile=p,packed_coarse=pc,packed_ordinary_chain=chain,paid_moment=paid(p,pc),adjacent_excluded=paid(p,pc+Q(1,10**18)),independent_interval=dict(lower=l,upper=u,next_lower=nl,next_upper=nu),complex_saving=saving,complex_moment=cmoment,finite_bill=finite,scalar_bill={k:v for k,v in scalar.items() if k!='maximum_original_adjoint_row_l1'},selector_gap=gap,assembly=assembly,incidence_sha256=packing['incidence_sha256'],charts=packing['fresh_charts'],conditions='Inherited weighted completed-core, separated residual, ordinary selector, restored-row and fixed-tape interfaces. Execution evidence is recorded separately.')

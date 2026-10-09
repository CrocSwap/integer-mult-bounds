"""Finite-depth stopped-leaf bootstrap using immutable PR182 ordinary supplier.
Exact arithmetic experiment; physical word validation remains a pinned input.
"""
from pathlib import Path
import hashlib,json,sys,copy,importlib.util
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];PARENT=ROOT/'research/paired-cube-local-bit-168'
sys.path.insert(0,str(PARENT/'arithmetic'));sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
import shared_bridge,balanced_shared
base_bytes=(PARENT/'certificate.json').read_bytes(); base=json.loads(base_bytes)
base_sha=hashlib.sha256(base_bytes).hexdigest()
row=base['complex']['profile'];arith=base['arithmetic'];C=Q(arith['coarse_bit_saving'])
base_uniform=arith['bridge']['bit_uniform'];A0=Q(arith['actual_uniform_bit_saving'])
assert A0==(1-Q(base_uniform['atom_beta']))*C+Q(base_uniform['atom_beta'])*Q(base_uniform['old_atom_saving'])
assert A0<C<Q(arith['complex_saving'])

# Preserve every original paid complex/scalar/row formula. Validate the base
# leaf separately using the original validator, and bind the replacement leaf
# by a finite exact recurrence with the published source certificate hash.
def validate_bootstrap_bridge(bridge,complex_row):
    shared_bridge.nofloat(bridge)
    meta=bridge['finite_leaf_bootstrap']
    shared_bridge.require(meta['base_certificate_sha256']==base_sha,'Unpinned base leaf')
    shared_bridge.require(meta['base_commit']=='af90b94783f7d104a0be75c762ade758bec75855','Wrong base commit')
    depth=meta['depth'];shared_bridge.require(type(depth)is int and 1<=depth<=3,'Finite bootstrap depth 1..3')
    values=[A0]
    for _ in range(depth):
        next_a=(1-C)*C+C*values[-1]
        shared_bridge.require(values[-1]<next_a<C<1-next_a,'Strict paid atom and row tolls')
        values.append(next_a)
    shared_bridge.require(list(map(Q,meta['ordinary_saving_chain']))==values,'Detached bootstrap recurrence')
    u=bridge['bit_uniform']
    for key,expected in [('coarse_saving',C),('atom_beta',C),('old_atom_saving',values[-2]),('ordinary_saving',values[-1])]:
        shared_bridge.require(Q(u[key])==expected,'Stale new leaf '+key)
    # The numeric external reserve is deliberately retained conservatively.
    # It is NOT represented as the new leaf's internal borrowing requirement.
    shared_bridge.require(meta['leaf_external_row_stock']==0,'New leaf must borrow its own rows')
    shared_bridge.require(meta['legacy_252_reserve_retained_as_slack'] is True,'Reserve accounting disclosure')
    legacy=copy.deepcopy(bridge);legacy['bit_uniform']=copy.deepcopy(base_uniform)
    checked=shared_bridge.validate_shared_bridge(legacy,complex_row)
    checked['bit_uniform']={k:Q(u[k]) for k in ('coarse_saving','atom_beta','old_atom_saving','ordinary_saving')}
    return checked
balanced_shared.validate_shared_bridge=validate_bootstrap_bridge

def js(v):
    if isinstance(v,Q):return str(v)
    if isinstance(v,dict):return {k:js(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [js(x) for x in v]
    return v

def below(x,den=10**18):
    y=x*den;return Q((y.numerator-1)//y.denominator,den)

def run(depth):
    values=[A0]
    for _ in range(depth):values.append((1-C)*C+C*values[-1])
    a=values[-1];b=Q(arith['complex_saving']);eta=beta=Q(1,10**24)
    q=a*(1-2*eta);ceiling=(1-eta)*q/(1+q);k=below(ceiling)
    bridge=copy.deepcopy(arith['bridge'])
    bridge['bit_uniform'].update(coarse_saving=C,atom_beta=C,old_atom_saving=values[-2],ordinary_saving=a)
    bridge['finite_leaf_bootstrap']=dict(base_commit='af90b94783f7d104a0be75c762ade758bec75855',base_certificate_sha256=base_sha,
      depth=depth,ordinary_saving_chain=values,leaf_external_row_stock=0,legacy_252_reserve_retained_as_slack=True)
    result=balanced_shared.assembly(bridge,row,a,k,beta=beta,h=eta,a_complex=b)
    assert len(result['constraints'])==47 and len(result['margins'])==7
    assert all(Q(v)>0 for v in result['constraints'].values())
    assert all(Q(v)>k for v in result['margins'].values())
    assert result['minimum_margin']==ceiling
    # Independent closed-form recurrence and limiting bound.
    assert a==C-C**depth*(C-A0)
    assert ceiling<a/(1+a)<C/(1+C)
    rejected=[]
    def reject(name,fn):
        try:fn()
        except (AssertionError,ValueError,KeyError):rejected.append(name)
        else:raise AssertionError('accepted '+name)
    reject('next_final_grid',lambda:balanced_shared.assembly(bridge,row,a,k+Q(1,10**18),beta=beta,h=eta,a_complex=b))
    def bad(change):
        z=copy.deepcopy(bridge);change(z);validate_bootstrap_bridge(z,row)
    reject('fake_leaf_saving',lambda:bad(lambda z:z['bit_uniform'].update(old_atom_saving=C)))
    reject('fake_result',lambda:bad(lambda z:z['bit_uniform'].update(ordinary_saving=C)))
    reject('missing_base_pin',lambda:bad(lambda z:z['finite_leaf_bootstrap'].update(base_certificate_sha256='0'*64)))
    reject('unbounded_depth',lambda:bad(lambda z:z['finite_leaf_bootstrap'].update(depth=0)))
    reject('unpaid_atom_toll',lambda:bad(lambda z:z['bit_uniform'].update(atom_beta=a)))
    reject('external_row_assumption',lambda:bad(lambda z:z['finite_leaf_bootstrap'].update(leaf_external_row_stock=252)))
    reject('scalar_stock_collapsed',lambda:bad(lambda z:z['complex'].update(scalar_role_reserve=row['R'])))
    reject('old_row_charge_deleted',lambda:bad(lambda z:z.update(ordinary_leaf_row_degree=0)))
    reject('row_degree_deleted',lambda:bad(lambda z:z['rows'].update(degree=0)))
    reject('fake_supplier',lambda:balanced_shared.assembly(bridge,row,a+Q(1,10**24),k,beta=beta,h=eta,a_complex=b))
    return dict(depth=depth,kappa=k,ordinary_saving=a,kappa_gain=k-Q(base['kappa']),relative_gain=(k/Q(base['kappa'])-1),
      chain=values,atom_exponent=C,assembly=result,bridge=bridge,controls_rejected=rejected,
      closed_form_checked=True,coarse_infinite_bootstrap_supremum=C/(1+C))

def generate():
    from interval_moment import moment,log_interval,exp_interval
    br=base['bit']['profile']
    profile=dict(m=br['m'],W=br['W_per_vertex'],N=br['deficit_per_vertex'],L=0,
       total_rank=br['rank_per_vertex'],maxchild=br['maxchild'],child_multiplicities={int(k):v for k,v in br['child_histogram'].items()})
    def paid(a):
        raw=moment(profile,a);ll,lu=log_interval(Q(profile['m']));el,eu=exp_interval(a*ll,a*lu)
        w=Q(1,10**16)*Q(32*profile['m']*sum(profile['child_multiplicities'].values()),profile['W'])
        return dict(lower=raw['lower']+w*el,upper=raw['upper']+w*eu)
    accepted=paid(C);rejected=paid(C+Q(1,10**18))
    assert accepted['upper']<1<rejected['lower']
    # Independently reproduce the published interval endpoints.
    for k in ('lower','upper'):assert accepted[k]==Q(base['bit']['coarse']['accepted'][k])
    cp=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
       total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    complex_moment=moment(cp,Q(arith['complex_saving']))
    assert complex_moment['upper']<1
    results=[run(j) for j in range(1,4)]
    return js(dict(status='PASS conditional finite bootstrap',kappa=results[-1]['kappa'],
      source_commit='af90b94783f7d104a0be75c762ade758bec75855',base_certificate_sha256=base_sha,
      selected=results[-1],comparisons=[{k:v for k,v in r.items() if k not in ('bridge','assembly')} for r in results],
      bit_moment=accepted,next_bit_grid_exclusion=rejected,complex_moment=complex_moment,
      scope='Immutable PR182 physical words and ordinary supplier; three finite acyclic wrapper levels, unchanged strict assembly. The compositional proof retains all stated all-size interfaces.'))

if __name__=='__main__':print(json.dumps(generate(),indent=2))

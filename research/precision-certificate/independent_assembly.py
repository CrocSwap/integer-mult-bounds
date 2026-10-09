"""Independent paired-cube bridge and balanced assembly arithmetic.

Apache-2.0, OpenAI Codex assistance. Derived as explicit relational tests,
without producer/assembly imports. Component inventories, fixed scalar/router
charge rules and inherited reserve allowances are mathematical inputs, not
independently proved circuits. Exact arithmetic does not prove the all-size
analytic, uniform weighted supplier, phase or tape contracts.
"""
from fractions import Fraction as Q
from math import prod
import json


def exact(value):
    if type(value) not in (Q,int,str):
        raise ValueError('exact rational required')
    return Q(value)

def require(condition, message):
    if not condition:
        raise ValueError(message)


def component_histogram(raw, max_rank):
    require(type(raw) is dict, 'component histogram must be object')
    result = {}
    for key, count in raw.items():
        require(type(key) is str and key.isascii() and key.isdigit() and str(int(key))==key,
                'component rank key')
        rank=int(key)
        require(0<=rank<=max_rank and type(count) is int and count>=0, 'component rank/count')
        if rank and count: result[rank]=count
    return result


def serialize(value):
    if isinstance(value,Q): return str(value)
    if isinstance(value,dict): return {str(k):serialize(v) for k,v in value.items()}
    if isinstance(value,list): return [serialize(v) for v in value]
    return value


def reconstruct_bridge(scalar, physical, *, coarse_row_reserve=9909,
                       ordinary_leaf_row_reserve=252, row_degree=70000):
    h,v,R,M=(scalar[k] for k in ('h','v','R','total_M_operations'))
    require(all(type(x) is int and x>0 for x in (h,v,R,M)), 'invalid scalar dimensions')
    require(type(scalar['loss']) is int and scalar['loss']>=0, 'invalid scalar loss')
    require(all(type(physical[k]) is int and physical[k]>=0 for k in ('h','v','loss')),
            'invalid physical dimensions/loss')
    require(h%2==0, 'even local complex dimension required')
    require((h,v,scalar['loss'])==(physical['h'],physical['v'],physical['loss']), 'source/physical dimensions')
    require(type(physical['physical_R']) is int and 0<physical['physical_R']<=R, 'physical roles exceed logical charge')
    require(type(scalar['c']) is int and scalar['c']>=0, 'invalid scalar additions')
    require(type(scalar['q']) is int and scalar['q']>0 and 3*scalar['q']<2**15,
            'root coefficient bitlength allowance')
    width=3*h
    role_stock=2*v+physical['physical_R']
    require(all(type(x) is int and x>=0 for x in (coarse_row_reserve,ordinary_leaf_row_reserve,row_degree)), 'invalid reserve')
    terms=[]
    for name in ('local_histogram','source_data_histogram','target_data_histogram'):
        terms.extend((rank,3*count) for rank,count in component_histogram(physical[name],h).items())
    terms.extend((3*rank,count) for rank,count in component_histogram(physical['physical_gauge_histogram'],h-1).items())
    terms.append((2,2*v))
    require(all(type(rank) is int and 0<rank<width and type(count) is int and count>0 for rank,count in terms), 'invalid paid child')
    children={rank:sum(count for rr,count in terms if rr==rank) for rank in sorted({r for r,n in terms})}
    require(children==component_histogram(physical['child_histogram'],width-1),'physical inventory mismatch')
    rank_local=sum(rank*count for rank,count in terms)
    require(role_stock*width-rank_local==2*v-3*scalar['loss']>0,'telescoping deficit')
    child=max(children)
    half=width//2
    vertices=2**(width-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W,N,s=vertices*role_stock,vertices*v,vertices*rank_local
    # Written finite scalar/router charge. All logical roles retained in L.
    L=(4*(scalar['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
       +8*R*v*(M+16)+32*v)
    logical=3*vertices*L+8*W+4*N+8*width*R*vertices
    G=64*(width+1)**3*(logical+1)*(W+1)**2
    E=64*(W+width+G+1)**3
    B=s+E
    charge=2*G*W*W+8*s+4*W+4+32*width
    C0=32*width*B*B
    require(E>charge and 2*B*(width-child)>=s+E and C0>2*B+18,
            'finite semantic guard fails')
    halving=1
    while width**halving<=2*child**halving: halving+=1
    bits=W.bit_length()
    coefficient=halving*bits+coarse_row_reserve+ordinary_leaf_row_reserve
    reserve_gap=Q(row_degree)-Q(51,25)*coefficient
    require(reserve_gap>0,'finite external row reserve')
    return dict(m=width,roles_per_vertex=role_stock,rank_per_vertex=rank_local,
        maxchild=child,vertices=vertices,W=W,N=N,s=s,local_group_upper=L,
        logical_group_upper=logical,scalar_group_upper=G,E=E,B=B,C0=C0,
        literal_charge=charge,literal_gap=E-charge,halving_degree=halving,
        wire_bits=bits,row_coefficient=coefficient,row_degree=row_degree,row_gap=reserve_gap,
        coefficient_bound=h+4,coefficient_denominator_divides=6,
        original_X_involution_scalar_group_upper=32*v,stages=3,
        auxiliary_banks_after_sharing=1,fixed_odd_divisor=3,
        conservative_old_coarse_row_reserve=coarse_row_reserve,
        ordinary_leaf_row_degree=ordinary_leaf_row_reserve,
        shared_assumptions=['finite scalar/phase/router bound in PR168 written note',
                           'inherited bit reserve9909 and ordinary leaf reserve252'])


def balanced_assembly(bridge, actual_bit, complex_saving, headline, *,
                      eta=Q(1,10**12), beta=Q(1,10**12), phase_gap=Q(1,10**15),
                      old_prefix=False, no_reservation=False):
    AB,b,headline,eta,beta,phase_gap=map(exact,(actual_bit,complex_saving,headline,eta,beta,phase_gap))
    require(0<AB<1 and 0<b<1 and 0<eta<Q(1,2) and 0<beta<1 and phase_gap>0 and headline>=0, 'assembly parameter domain')
    a=min(AB,(1-beta)*b-phase_gap)
    tau,sigma=1-a,1-b
    q=a*(1-2*eta)
    c=q if no_reservation else q+eta/4
    epsilon=(1-eta)/(1+q)
    lp=1-q
    lam=(tau+lp)/2
    g=epsilon*q
    alpha=(g+1-epsilon)/2
    delta=eta/8
    # Stopped recurrence powers, independently reduced at these parameters.
    internal=tau if sigma<=tau else beta*tau+(1-beta)*sigma
    leaf=1-(1-beta)*b
    margins={
        'balanced_prefix':1-epsilon*(1+c) if old_prefix else 1-epsilon,
        'coordinate_movement':a,
        'compact_phase_layer':g,
        'bulk_exposure':a,
        'Gaussian_arithmetic':min(1-epsilon-delta,alpha-delta),
        'scalar_work':1-epsilon-delta,
        'dimension':epsilon,
    }
    slacks={}
    def inequality(name,greater,lesser): slacks[name]=greater-lesser
    # Order/reservation constraints: slacks computed from explicit inequalities.
    for name,greater,lesser in [
        ('bit_positive',a,0),('complex_above_bit',b,a),
        ('complex_below_one_over32',Q(1,32),b),('beta_positive',beta,0),
        ('beta_below_one',1,beta),('leaf_saving_above_bit',(1-beta)*b,a),
        ('q_positive',q,0),('q_below_internal',1-internal,q),
        ('q_below_leaf',1-leaf,q),('c_positive',c,0),('c_below_one',1,c),
        ('q_below_reservations',c,q),('lambda_above_tau',lam,tau),
        ('lambda_above_sigma',lam,sigma),('lambda_above_internal',lam,internal),
        ('lambda_prime_above_lambda',lp,lam),('compact_leaf',lp,leaf),
        ('compact_reservations',lp,1-c),('lambda_prime_below_one',1,lp),
        ('epsilon_positive',epsilon,0),('epsilon_below_one',1,epsilon),
        ('guard_width',1,epsilon),('K_geometry',1,epsilon*(1+c)),
        ('K_dominates_log',epsilon*c,0),('record_suffix',1,epsilon),
        ('phase_local',1,epsilon+delta),('phase_boundary',alpha,delta),
        ('gamma_sublinear',1,epsilon+alpha),('cell_above_band',epsilon,(1-alpha)/2),
        ('prime_interval_packing',1,epsilon),('alpha_positive',alpha,0),
        ('alpha_below_one',1,alpha),('alpha_below_one_fourth',Q(1,4),alpha),
        ('delta_positive',delta,0),('delta_below_one_eighth',Q(1,8),delta),
        ('short_record_fallback',epsilon,a),('small_field_exposure',1,epsilon+g),
        ('artificial_boundary',8+alpha,epsilon+delta+g),
        ('literal_scalar_guard',bridge['E'],bridge['literal_charge']),
        ('row_product_gap',bridge['row_degree'],Q(51,25)*bridge['row_coefficient']),
    ]: inequality(name,greater,lesser)
    for name,margin in margins.items(): inequality(name+'_above_kappa',margin,headline)
    require(len(slacks)==47 and len(margins)==7,'incomplete inequality inventory')
    failed={name:str(value) for name,value in slacks.items() if value<=0}
    require(not failed,'nonpositive strict inequalities: '+json.dumps(failed))
    require(min(margins.values())==g,'incorrect minimum margin')
    require((1-epsilon)-g==eta and 1-epsilon-alpha==eta/2,'balanced backoff identities')
    require(1-epsilon*(1+c)==eta-epsilon*eta/4,'balanced geometric identity')
    return dict(parameters={'actual_bit':AB,'a_bit':a,'a_complex':b,'eta':eta,'beta':beta,
        'tau':tau,'sigma':sigma,'q':q,'c':c,'epsilon':epsilon,'lambda_':lam,
        'lambda_prime':lp,'alpha_squared_power':alpha,'delta':delta,'kappa':headline, 'C0':bridge['C0'],'C1':1},
        recurrence={'internal':internal,'leaf':leaf,'reservations':1-c},
        strict_constraints=slacks,margins=margins,minimum_margin=g,
        absorption_gap=g-headline,
        limiter=('bit' if AB<(1-beta)*b-phase_gap else
                 'complex' if AB>(1-beta)*b-phase_gap else 'bit_and_complex'))



def compare_assembly(computed, observed):
    """Reject positive but wrong stored answers and missing/extra named fields."""
    for name in ('strict_constraints','margins','recurrence'):
        require(set(computed[name])==set(observed[name]), 'saved '+name+' keys differ')
        for key,value in computed[name].items():
            require(exact(observed[name][key])==value, 'saved '+name+' differs: '+key)
    for key in ('minimum_margin','absorption_gap'):
        require(exact(observed[key])==computed[key], 'saved '+key+' differs')
    expected={k:v for k,v in computed['parameters'].items() if k!='actual_bit'}
    require(set(observed['parameters'])==set(expected), 'saved parameter keys differ')
    for key,value in expected.items():
        require(exact(observed['parameters'][key])==value, 'saved parameter differs: '+key)
    return True


def compare_bridge(computed, observed):
    """Check exact derived scalar/router, semantic and row numeric fields."""
    c,s,r=observed['complex'],observed['semantic'],observed['rows']
    complex_fields={'m':'m','W':'W','s':'s','N':'N','maxchild':'maxchild',
        'invocations_per_stage':'vertices','halving_degree':'halving_degree',
        'wire_bits':'wire_bits','local_group_upper':'local_group_upper',
        'logical_group_upper':'logical_group_upper','finite_group_router_upper':'scalar_group_upper',
        'scalar_group_upper':'scalar_group_upper'}
    complex_fields.update({key:key for key in ('coefficient_bound','coefficient_denominator_divides',
        'original_X_involution_scalar_group_upper','stages','auxiliary_banks_after_sharing')})
    for target,source in complex_fields.items():
        require(exact(c[target])==computed[source], 'saved bridge complex differs: '+target)
    semantic={'E':computed['E'],'literal_charge':computed['literal_charge'],
        'strict_literal_gap':computed['literal_gap'],'B':computed['B'],'C0':computed['C0'],
        'C1':1,'fixed_odd_divisor':computed['fixed_odd_divisor'],
        'induction_gap':2*computed['B']*(computed['m']-computed['maxchild'])-computed['s']-computed['E']}
    for key,value in semantic.items():
        require(exact(s[key])==value,'saved bridge semantic differs: '+key)
    rows={'coefficient':computed['row_coefficient'],'degree':computed['row_degree'],
        'complex_coefficient':computed['halving_degree']*computed['wire_bits'],
        'degree_gap':computed['row_gap'],'suffix_slope':4*computed['row_degree']}
    for key,value in rows.items(): require(exact(r[key])==value,'saved bridge rows differ: '+key)
    for key in ('conservative_old_coarse_row_reserve','ordinary_leaf_row_degree'):
        require(exact(observed[key])==computed[key],'saved inherited reserve differs: '+key)
    return True

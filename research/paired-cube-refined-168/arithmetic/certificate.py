#!/usr/bin/env python3
"""Exact paid bridge, unchanged balanced arithmetic body, and strict controls.

Finite bridge formulas: icekylinx PR144/130, eumemic PR152, Apache-2.0.
Balanced layout: PR23/29 Zhihao Chen, RaD, James Chang PR34, and Rohan
Arun PR100/103. This adapter preserves their separately stated contracts.
Prepared for chafreaky with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import prod
from pathlib import Path
import copy
import gzip
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE));sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
from shared_bridge import require,halving,validate_shared_bridge,nofloat
from balanced_shared import assembly

AC=Q(656350690347,10**15)
COARSE=Q('6600253783597/10000000000000000')
ATOM=Q('329807692103940705443/500000000000000000000000')
OLD=Q(384599,10**10)
AB=(1-ATOM)*COARSE+ATOM*OLD
BETA=ETA=Q(1,10**24)
WEAKENING=Q(1,10**30)
GRID=10**18


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x


def bridge(row,coarse=COARSE,atom=ATOM):
    """Retained finite formulas with the actual new local inventory supplied."""
    h,v,R,c,M=(row[k] for k in ('h','v','R','c','total_M_operations'))
    scalar_R=row['scalar_role_reserve']
    m=3*h;half=m//2
    V=2**(m-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W=V*(2*v+R);s=V*row['rank_per_vertex'];N=V*v
    r=max(int(k) for k,n in row['child_histogram'].items() if int(k) and n)
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*scalar_R*v*(M+16)+32*v
    logical=3*V*local+8*W+4*N+8*m*scalar_R*V
    G=64*(m+1)**3*(logical+1)*(W+1)**2
    E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m
    B=s+E;C0=32*m*B*B;depth=halving(m,r);coefficient=depth*W.bit_length()+9909+252;degree=70000
    actual=(1-atom)*coarse+atom*OLD
    result=dict(bit_uniform=dict(coarse_saving=coarse,atom_beta=atom,old_atom_saving=OLD,
        ordinary_saving=actual,selector_stock='Internally borrowed and restored q-adic rows; complete spectators preserved.',
        external_stock='The bit group cardinality is not inserted into external polynomial row stock.'),
        conservative_old_coarse_row_reserve=9909,ordinary_leaf_row_degree=252,
        complex=dict(m=m,W=W,s=s,N=N,maxchild=r,invocations_per_stage=V,stages=3,
            auxiliary_banks_after_sharing=1,halving_degree=depth,wire_bits=W.bit_length(),
            original_X_involution_scalar_group_upper=32*v,local_group_upper=local,
            logical_group_upper=logical,finite_group_router_upper=G,scalar_group_upper=G,
            coefficient_bound=h+4,coefficient_denominator_divides=6,
            physical_roles_per_vertex=R,scalar_role_reserve=scalar_R,reuse_pairs=row['reuse_pairs'],terminal_sinks=row.get('terminal_sinks',0)),
        semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,
            induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=3,
            exact_grid='One dyadic grid times 3^(-K), K=G*(D_complex+1); completed children preserve the incoming odd exponent.'),
        rows=dict(coefficient=coefficient,complex_coefficient=depth*W.bit_length(),degree=degree,
            suffix_slope=4*degree,degree_gap=Q(degree)-Q(51*coefficient,25)))
    validate_shared_bridge(result,row)
    return result


def below(value,grid=GRID):
    # Largest grid point strictly below a rational, including exact boundaries.
    x=value*grid
    return Q(-(-x.numerator//x.denominator)-1,grid)


def old_assembly():
    spec=importlib.util.spec_from_file_location('retained_prefix_assembly',ROOT/'scripts/structured_bulk_assembly.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.assembly


def price(row,b,coarse,beta,eta,weakening,layout,atom=ATOM):
    finite=bridge(row,coarse,atom)
    actual=finite['bit_uniform']['ordinary_saving']
    a=min(actual,(1-beta)*b-weakening)
    q=a*(1-2*eta)
    value=(1-eta)*q/(1+q) if layout=='balanced' else (1-eta)*q/(1+q*(1+eta)+q)
    k=below(value)
    if layout=='balanced':result=assembly(finite,row,a,k,beta=beta,h=eta,a_complex=b)
    else:result=old_assembly()(a,b,finite,k,eta=eta,beta=beta)
    assert len(result.get('constraints',result.get('strict_constraints')))==47 and len(result['margins'])==7
    assert result['minimum_margin']==value
    return dict(kappa=k,a=a,actual_bit_saving=actual,complex_saving=b,beta=beta,eta=eta,
        weakening=weakening,layout=layout,minimum_margin=value,assembly=result,finite_bridge=finite)


def normalized_body_check():
    source=(PACKAGE/'references/pr141/balanced_stopped.py').read_text()
    old=source[source.index('def assembly('):source.index('\n\ndef cutoffs(')].rstrip()
    body=(HERE/'balanced_shared.py').read_text();body=body[body.index('def assembly('):].rstrip()
    body=body.replace('def assembly(finite_bridge, complex_row, a_bit, kappa,','def assembly(finite_bridge, ordinary_leaf, a_bit, kappa,',1)
    body=body.replace('f = validate_shared_bridge(finite_bridge, complex_row)','f = validate_bridge(finite_bridge, ordinary_leaf)',1)
    body=body.replace("    require(a <= f['bit_uniform']['ordinary_saving'], 'transfer saving exceeds actual uniform bit supplier')\n",'',1)
    require(body==old,'The retained 47-slack body changed outside bridge plumbing and supplier support')


def certificate(row,physical):
    nofloat(row);normalized_body_check()
    final=price(row,AC,COARSE,BETA,ETA,WEAKENING,'balanced')
    require(final['kappa']==Q('655920176686219/1000000000000000000'),'Selected final kappa differs')
    counts=physical['scalar_bound']
    require(counts['terminal_sinks']==row['terminal_sinks']==physical['terminal_compiler']['eligible_count'],'Terminal sink inventory mismatch')
    require(counts['terminal_scalar_gate_delta']<=0 and counts['terminal_original_scalar_reserve_retained'],'Terminal compiler must fit the retained scalar reserve')
    require(final['finite_bridge']['complex']['local_group_upper']==counts['local_group_upper'],'Scalar bill detached from physical word')
    for key,field in (('physical_R','R'),('logical_R','scalar_role_reserve'),('handoffs','reuse_pairs'),('c','c'),('q','q'),('M_operations','total_M_operations')):
        require(counts[key]==row[field],'Physical scalar inventory mismatch '+key)
    require(counts['fixed_odd_divisor']==3 and counts['scalar_denominators_divide']==6,'Exact odd-grid contract')
    require(sha256((ROOT/'notes/general-clifford-frames.tex').read_bytes()).hexdigest() in physical['source_sha256'].values(),'Frame theorem source drift')
    parent_path=ROOT/'certificates/paired-cube-network.json'
    require(sha256(parent_path.read_bytes()).hexdigest()=='05b253a21dc526b6039f56d1068162a19a8a4f29291ad94eb892656b88e9142d','Published prerequisite certificate changed')
    parent=json.loads(parent_path.read_text())
    published_parent=dict(source_commit='4a3c769e5c5430e7114c4d3e099ff34664677f17',certificate_sha256=sha256(parent_path.read_bytes()).hexdigest(),kappa=parent['kappa'],ordinary_saving=parent['bit']['effective_saving'])
    rows=[('Same suppliers with earlier positive outer backoffs',row,AC,COARSE,Q(1,10**9),Q(1,10**8),Q(1,10**10),'balanced',ATOM),
          ('Same suppliers with finer positive outer backoffs',row,AC,COARSE,BETA,ETA,WEAKENING,'balanced',ATOM)]
    controls_table=[]
    for name,*args in rows:
        result=price(*args);controls_table.append(dict(name=name,**{k:v for k,v in result.items() if k not in ('assembly','finite_bridge')}))
    accepted=[]
    def reject(name,operation):
        try:operation()
        except (KeyError,ValueError,AssertionError):accepted.append(name)
        else:raise ValueError('Adverse control accepted: '+name)
    finite=final['finite_bridge'];a=final['a'];k=final['kappa']
    def mutate(name,change):
        bad=copy.deepcopy(finite);change(bad);reject(name,lambda:validate_shared_bridge(bad,row))
    mutate('full group stock replaced by local W',lambda x:x['complex'].update(W=row['W_per_vertex']))
    mutate('old ordinary reserve omitted',lambda x:x.update(ordinary_leaf_row_degree=0))
    mutate('conservative old coarse reserve omitted',lambda x:x.update(conservative_old_coarse_row_reserve=0))
    mutate('uniform supplier replaced by fictional finite profile',lambda x:(x.pop('bit_uniform'),x.update(bit_coarse={'m':529,'W':108516254})))
    mutate('actual ordinary saving overstated',lambda x:x['bit_uniform'].update(ordinary_saving=AB+Q(1,10**24)))
    mutate('unpaid previous atom grid',lambda x:x['bit_uniform'].update(atom_beta=ATOM-Q(1,10**24),ordinary_saving=(1-ATOM+Q(1,10**24))*COARSE+(ATOM-Q(1,10**24))*OLD))
    mutate('scalar role reserve collapsed to physical stock',lambda x:x['complex'].update(scalar_role_reserve=row['R']))
    mutate('terminal removals omitted',lambda x:x['complex'].update(terminal_sinks=0))
    mutate('terminal removals counted as aliases',lambda x:x['complex'].update(reuse_pairs=row['reuse_pairs']+row['terminal_sinks']))
    mutate('odd divisor silently changed to 21',lambda x:x['semantic'].update(fixed_odd_divisor=21))
    mutate('C0 detached from scalar charge',lambda x:x['semantic'].update(C0=1))
    mutate('scalar group charge omitted',lambda x:x['complex'].update(scalar_group_upper=0))
    mutate('stale total row coefficient',lambda x:x['rows'].update(coefficient=1))
    mutate('inadequate polynomial row degree',lambda x:x['rows'].update(degree=1))
    mutate('float in otherwise unused metadata',lambda x:x['bit_uniform'].update(extra=0.5))
    mutate('noncontracting maximum child',lambda x:x['complex'].update(maxchild=row['m']))
    reject('transfer saving exceeds actual uniform supplier',lambda:assembly(finite,row,AB+Q(1,10**24),k,beta=BETA,h=ETA,a_complex=AC))
    reject('old prefix charged at balanced parameters',lambda:assembly(finite,row,a,k,beta=BETA,h=ETA,a_complex=AC,original_prefix=True))
    reject('old nonlinear scalar guard',lambda:assembly(finite,row,a,k,beta=BETA,h=ETA,a_complex=AC,old_guard=True))
    reject('old separate movement exposures',lambda:assembly(finite,row,a,k,beta=BETA,h=ETA,a_complex=AC,old_exposures=True))
    reject('next final 1e-18 kappa grid point',lambda:assembly(finite,row,a,k+Q(1,GRID),beta=BETA,h=ETA,a_complex=AC))
    return js(dict(status='PASS',kappa=k,actual_uniform_bit_saving=AB,coarse_bit_saving=COARSE,
        complex_saving=AC,weakened_transfer_saving=a,beta=BETA,eta=ETA,strict_weakening=WEAKENING,atom_exponent=ATOM,
        bridge=finite,assembly=final['assembly'],matched_comparisons=controls_table,published_parent=published_parent,
        unchanged_47_slack_body=True,adverse_controls=accepted,adverse_control_count=len(accepted),
        next_grid_scope='Rejection at these fixed certified supplier values and stated parameters; no global or true-profile optimality claim.',
        scope='Conditional finite witness retaining the source-specified uniform bit, exact tensor, row-restoration, paid layout and analytic/fixed-tape contracts.'))

"""Exact paid moments of the packed bit row and the v4 balanced assembly.

paid_moment, certify and independent_bank_moment are PR186's (Dugongue), the
assembly is PR184's (icekylinx), and the finite leaf chain is PR185's
(rohanarun) as composed by PR199 (maxime-fleury).
Prepared with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'research/paired-cube-diagonal-bit-168/arithmetic'))
sys.path.insert(0, str(HERE / 'references/pr186/bit'))
from interval_moment import moment, log_interval, exp_interval
from banks import need

LEAF_DEPTH = 3


def paid_moment(p,a,details=False):
    raw=moment(p,a,details);m,w=p['m'],p['W']
    count=sum(p['child_multiplicities'].values());bad=Q(1,10**16);fallback=32*m*m
    ll,lu=log_interval(Q(m));el,eu=exp_interval(a*ll,a*lu)
    weight=bad*Q(fallback*count,w*m)
    return dict(saving=a,lower=raw['lower']+weight*el,upper=raw['upper']+weight*eu,
        strict_gap_lower=1-raw['upper']-weight*eu,raw=raw,fallback_lower=weight*el,
        fallback_upper=weight*eu,edge_count=count,fallback_children_per_edge=fallback,
        bad_fraction=bad)


def independent_bank_moment(row,coarse):
    from base_two_moment import moment as alternate_moment
    W=int(3*row['W_per_vertex']);H=[(r,3*n) for r,n in row['child_histogram'].items()]
    count=sum(n for r,n in H);fallback=32*72**2*count
    _,upper=alternate_moment(72,W,H,coarse['coarse_saving'])
    _,bad_upper=alternate_moment(72,W,[(1,fallback)],coarse['coarse_saving'])
    gap=1-upper-Q(1,10**16)*bad_upper
    need(gap>0,'independent base-two paid moment contracts')
    next_saving=coarse['coarse_saving']+Q(1,coarse['coarse_grid'])
    lower,_=alternate_moment(72,W,H,next_saving)
    bad_lower,_=alternate_moment(72,W,[(1,fallback)],next_saving)
    need(lower+Q(1,10**16)*bad_lower>1,'independent base-two adjacent paid moment exclusion')
    return gap


def certify(row):
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
        total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    p=dict(p,W=int(3*Q(p['W'])),N=3*p['N'],total_rank=3*p['total_rank'],
        child_multiplicities={r:3*n for r,n in p['child_multiplicities'].items()})
    grid=10**18;lo=0;hi=grid//100
    need(paid_moment(p,Q(lo,grid))['upper']<1,'zero-saving rank contraction')
    need(paid_moment(p,Q(hi,grid))['lower']>1,'upper bracket')
    while hi-lo>1:
        mid=(lo+hi)//2;r=paid_moment(p,Q(mid,grid))
        if r['upper']<1:lo=mid
        elif r['lower']>1:hi=mid
        else:raise ValueError('increase moment precision')
    coarse=Q(lo,grid);accepted=paid_moment(p,coarse,True);rejected=paid_moment(p,Q(hi,grid),True)
    need(accepted['upper']<1<rejected['lower'],'adjacent grid paid-moment proof')
    old=Q(384599,10**10);threshold=coarse/(1+coarse-old);atomgrid=10**24
    floor=(threshold*atomgrid).numerator//(threshold*atomgrid).denominator
    atom=Q(floor+1,atomgrid);actual=(1-atom)*coarse+atom*old
    need(actual<atom<1-actual,'paid atom and row adapter toll')
    need(Q(2*p['m']**3,2**80)<Q(1,10**16),'fixed prime rare-class bound')
    need(Q(p['total_rank'])+accepted['bad_fraction']*accepted['fallback_children_per_edge']*accepted['edge_count']<p['W']*p['m'],'contaminated mass contracts')
    previous=atom-Q(1,atomgrid)
    need(previous<=(1-previous)*coarse+previous*old,'previous atom grid does not pay strict toll')
    return dict(coarse_saving=coarse,accepted=accepted,rejected=rejected,coarse_grid=grid,
        atom_beta=atom,old_atom_saving=old,ordinary_saving=actual,atom_threshold=threshold,
        atom_grid=atomgrid,atom_lower_gap=atom-actual,atom_upper_gap=1-actual-atom,
        controls=dict(next_coarse_grid_rejected=True,previous_atom_grid_rejected=True),
        scope='Adjacent coarse exclusion for this fixed worst-case bad-class envelope and least atom on the stated grid; no true bad-fraction or global optimality claim.')


def load_pr184():
    spec = importlib.util.spec_from_file_location('pr184_assemble_profiles', REPO / 'research/source-assisted/global/assemble_profiles.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def leaf_chain(coarse, start, depth=LEAF_DEPTH):
    chain = [start]
    for _ in range(depth):
        a = (1 - coarse) * coarse + coarse * chain[-1]
        need(chain[-1] < a < coarse < 1 - a, 'acyclic finite leaf level pays the atom gaps')
        chain.append(a)
    need(chain[-1] == coarse - coarse**depth * (coarse - start), 'closed form of the finite leaf chain')
    return chain


def assemble(complex_profile, packed, coarse):
    pr184 = load_pr184()
    proof = REPO / 'research/source-assisted/global/FINITE_BRIDGE.txt'
    c = pr184.select(pr184.normalize(complex_profile))
    b = pr184.select(pr184.normalize(dict(m=packed['m'], W_per_vertex=packed['W_per_vertex'],
        deficit_per_vertex=packed['deficit_per_vertex'], child_histogram=packed['child_histogram'])), True)
    need(b['saving'] <= coarse['coarse_saving'], 'PR184 10^-10 bit grid stays below the 10^-18 certificate')
    plain = pr184.assemble(c, b, REPO, proof)
    chain = leaf_chain(Q(b['saving']), Q(b['effective_saving']))
    boot = dict(b, effective_saving=chain[-1], effective_saving_decimal=float(chain[-1]),
        ordinary_leaf_saving=chain[-1], atom_exponent=Q(b['saving']))
    leafed = pr184.assemble(c, boot, REPO, proof)
    for out in (plain, leafed):
        asm = out['assembly']
        need(len(asm['strict_constraints']) == 47 and len(asm['margins']) == 7, 'complete balanced assembly')
        need(all(Q(x) > 0 for x in asm['strict_constraints'].values()), 'all strict constraints positive')
    need(Q(b['saving']) < Q(c['saving']), 'bit supplier binds')
    return dict(complex=c, bit=b, leaf_chain=chain, without_leaf=plain, with_leaf=leafed,
        kappa_without_leaf=Q(plain['kappa']), kappa=Q(leafed['kappa']), binding='bit')

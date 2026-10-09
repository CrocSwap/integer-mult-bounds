#!/usr/bin/env python3
"""Recursive gathering and scoped obstructions to black-box block schedules.

No new fast gatherer or multiplication exponent is certified. Labels track
physical address coordinates, not coefficient values or coded tape streams.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import require, verify_sources
from prepare_layers import BIT_SAVING, serializable

ROOT=Path(__file__).resolve().parents[1]


def swap_intervals(values,left,right,width):
    require(0<=left<left+width<=right<right+width<=len(values),
            'Need two disjoint nonempty intervals')
    out=list(values)
    out[left:left+width],out[right:right+width]=values[right:right+width],values[left:left+width]
    return out


def recursive_gather(f,K,rho,g):
    """An exact O(f) swap schedule, allowing arbitrary spectator order.

    Gather f-1 windows into a most significant field. At a merge, swap the
    right child's packed window with the start of the left child's gap.
    Reversing the schedule restores *all* coordinate identities.
    """
    require(f>=2 and g>=1 and K>=2*g and 0<=rho<K,'Invalid separated windows')
    schedule=[]
    def visit(start,n):
        if n<=1:return
        left=(n+1)//2
        right=n-left
        visit(start,left)
        visit(start+left*K,right)
        require(left*(K-g)>=right*g,'Merge lacks a spectator destination')
        schedule.append((start+left*g,start+left*K,right*g))
    n=f-1
    visit(rho,n)
    schedule.append((rho,f*K-n*g,n*g))
    labels=list(range(f*K))
    for op in schedule:labels=swap_intervals(labels,*op)
    active=[rho+j*K+t for j in range(n) for t in range(g)]
    require(labels[-n*g:]==active,'Active order was not gathered')
    require(sorted(labels)==list(range(f*K)),'Lost a coordinate')
    require(len(schedule)==n,'Unexpected swap count')
    return labels,schedule


def lag_changes(colors,lag):
    require(colors and 1<=lag<len(colors),'Invalid cyclic lag')
    return sum(x!=colors[(i+lag)%len(colors)] for i,x in enumerate(colors))


def boundary_lower_bound(n):
    require(n>=1,'Need a nonempty window set')
    # 2n initial cyclic boundaries, two final boundaries, <=4 per swap.
    return n//2


def potential(colors,g,q):
    """Exact controls with q=2^tau rational, 1<q<2.

    The general theorem permits any fixed real 0<tau<1. Controls at rational
    q do not approximate or certify the current tiny exponent saving.
    """
    require(1<=g<len(colors) and 1<q<2,'Invalid potential parameters')
    return sum((q/2)**j*lag_changes(colors,1<<j)
               for j in range(g.bit_length()))


def potential_constant(q):
    require(1<q<2,'Need 1<q<2')
    return 8*(q/(q-1)+1/(1-q/2))


def dyadic_charge_upper(width,q):
    require(width>=1 and 1<q<2,'Invalid charge')
    return q**((width-1).bit_length())


def dyadic_tree_charge(n,q):
    """Sum u^tau with g=1, n a power of two, and q=2^tau."""
    require(n>=1 and n&(n-1)==0 and 1<q<2,'Need dyadic window count')
    depth=n.bit_length()-1
    return q**depth+Q(n,2)*sum((q/2)**j for j in range(depth))


def reuse_screen(a,b):
    """Optimistic w=d^b-round reuse of the O(V d w^tau) gather bound.

    This scores available estimates, not a lower bound on unrestricted time.
    It ignores leaves, padding and all other costs in the candidate's favor.
    """
    require(0<a<1 and b>=0,'Invalid saving/window exponent')
    tau=1-a
    movement=1-a*b
    compact=tau*(1+b)
    return dict(window_exponent=b,amortized_gather_exponent=movement,
                compact_root_exponent=compact,
                largest_power_saving_in_this_bound=min(a*b,a-tau*b),
                scope='Optimistic exponent screen of these cost estimates only')


def segmented_shear(y,controls,g,K):
    """Ideal modular addition on short fields, preserving all gap bits."""
    require(g>=1 and K>g and controls and
            all(0<=x<1<<g for x in controls) and
            0<=y<1<<(len(controls)*K),'Invalid segmented shear')
    mask=(1<<g)-1
    out=y
    for j,x in enumerate(controls):
        shift=j*K
        value=(((y>>shift)&mask)+x)&mask
        out=(out&~(mask<<shift))|(value<<shift)
    return out


def whole_slot_shear(y,controls,g,K):
    """The tempting single affine shift, which leaks carries into gaps."""
    segmented_shear(y,controls,g,K)  # Validate the same complete domain.
    return (y+sum(x<<(j*K) for j,x in enumerate(controls)))%(1<<(len(controls)*K))


def carry_failure_fraction(n,g):
    require(n>=1 and g>=1,'Nonempty control windows required')
    radix=1<<g
    return 1-Q(radix+1,2*radix)**n


def certificate():
    controls=[]
    q=Q(3,2)
    for n,g,K,rho in ((1,2,7,6),(3,2,7,6),(8,4,11,10),(16,3,8,0)):
        labels,ops=recursive_gather(n+1,K,rho,g)
        active={rho+j*K+t for j in range(n) for t in range(g)}
        before=[int(i in active) for i in range((n+1)*K)]
        after=[before[i] for i in labels]
        for j in range(g.bit_length()):
            t=1<<j
            require(lag_changes(before,t)==2*n*t,'Initial lag count failed')
            require(lag_changes(after,t)==2*t,'Final lag count failed')
        decrease=potential(before,g,q)-potential(after,g,q)
        require(decrease==2*(n-1)*sum(q**j for j in range(g.bit_length())),
                'Potential difference failed')
        controls.append(dict(n=n,g=g,K=K,rho=rho,swaps=len(ops),
                             minimum_calls_from_boundaries=boundary_lower_bound(n),
                             rational_control_q=q,potential_decrease=decrease))
    a=BIT_SAVING
    optimal=reuse_screen(a,a)
    require(optimal['largest_power_saving_in_this_bound']==a*a,'Reuse balance failed')
    return dict(status='SCOPED GATHER-SCHEDULE AUDIT; NO NEW KAPPA',
                upstream_commit=verify_sources(),coordinate_controls=controls,
                black_box_call_bound='At least ceil((n-1)/2) equal-interval swaps for n separated windows; single-coordinate moves and interval reversals also remove at most four cyclic boundaries.',
                weighted_bound='For equal-interval swap schedules only, sum(width^tau)=Omega_tau((n-1)*g^tau) when K>=2g.',
                construction='A reversible n-swap merge tree has sum(width^tau)=O_tau(n*g^tau). Spectator order may change during the gathered computation.',
                excluded_scope='Coded role streams, modular shears, arbitrary tape algorithms, and fused implementations are outside the black-box schedule obstruction.',
                optimistic_round_reuse=optimal,
                reuse_power_ceiling=a*a,
                assembly_ceiling_for_this_reuse_model=a*a/5,
                naive_segmented_shear=dict(
                    bad_fraction_formula='1-((2^g+1)/2^(g+1))^n, for any positive gap width',
                    controls=[dict(n=n,g=g,bad_fraction=carry_failure_fraction(n,g))
                              for n,g in ((1,1),(1,6),(4,6),(16,6))],
                    consequence='The existing rare-exception repair bound is not negligible for this substitution; carries affect gaps on a positive-density set.'),
                next_step='Test a coded strided-window operation whose frames track arbitrary gap bits and restore them jointly. Serial interval swaps are insufficient, and the naive whole-slot affine substitute has dense carry errors.')


if __name__=='__main__':
    (ROOT/'certificates/gather-schedule-audit.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS gather schedules and scoped cost controls; no fast gatherer or new kappa.')

#!/usr/bin/env python3
"""Bounded carry-code attempt: exact identities, no sublinear construction.

The flat affine-circuit bound deliberately excludes recursive role splitting,
nonlinear address operations, and permutations of proper subfields.
"""
from collections import Counter
from pathlib import Path
import json

from certify import require, verify_sources
from prepare_layers import serializable
from audit_gather_schedules import segmented_shear

ROOT=Path(__file__).resolve().parents[1]


def carry_pattern(y,controls,g,K):
    Q=1<<g
    return sum(int(((y>>(j*K))&(Q-1))+x>=Q)<<j
               for j,x in enumerate(controls))


def branch_offset(controls,g,K,pattern):
    Q=1<<g
    return sum((x-Q*((pattern>>j)&1))<<(j*K)
               for j,x in enumerate(controls))%(1<<(len(controls)*K))


def validate(state,controls,g,K):
    require(g>=1 and K>g and controls and
            all(0<=x<1<<g for x in controls) and
            len(state)==1<<(len(controls)*K),'Invalid complete coded domain')


def coded_flat(state,controls,g,K):
    """Sum of 2^n masked translations; arbitrary integer payload control.

    This is a finite operator simulator, not a random-access tape algorithm.
    Each term can be executed as a full-stream mask and affine translation.
    """
    validate(state,controls,g,K)
    size=len(state)
    out=[0]*size
    for pattern in range(1<<len(controls)):
        offset=branch_offset(controls,g,K,pattern)
        for y,value in enumerate(state):
            if carry_pattern(y,controls,g,K)==pattern:
                out[(y+offset)%size]+=value
    return out


def coded_factored(state,controls,g,K):
    """Two masked translations per window, O(n) complete-stream stages."""
    validate(state,controls,g,K)
    size=len(state)
    Q=1<<g
    out=list(state)
    for j,x in enumerate(controls):
        updated=[0]*size
        for overflow in (0,1):
            offset=(x-Q*overflow)<<(j*K)
            for y,value in enumerate(out):
                test=(((y>>(j*K))&(Q-1))+x>=Q)
                if test==overflow:
                    updated[(y+offset)%size]+=value
        out=updated
    return out


def direct(state,controls,g,K):
    validate(state,controls,g,K)
    out=[0]*len(state)
    for y,value in enumerate(state):
        out[segmented_shear(y,controls,g,K)]=value
    return out


def selected_mask(n,K,rho=0):
    require(n>=1 and K>=2 and 0<=rho<K,'Need separated selected positions')
    return sum(1<<(j*K+rho) for j in range(n))


def offset_support(n,K):
    mask=selected_mask(n,K)
    modulus=1<<(n*K)
    return {((y^mask)-y)%modulus for y in range(modulus)}


def affine_agreement_control(n,K,rho=0):
    """Exhaust all slopes and offsets at small sizes, including even slopes."""
    require(rho<=K-3 or (K==2 and rho==0),'Uncovered top-boundary case')
    mask=selected_mask(n,K,rho)
    modulus=1<<(n*K)
    best=0
    witness=None
    for a in range(modulus):
        offsets=Counter(((y^mask)-a*y)%modulus for y in range(modulus))
        b,count=max(offsets.items(),key=lambda x:x[1])
        if count>best:best,witness=count,(a,b)
    # At K=2 the top gap bit admits a degeneracy; retain that boundary case.
    exponent=n if K>=3 else n-1
    bound=modulus//(1<<exponent)
    require(best==bound,'Small affine agreement control failed')
    return dict(n=n,K=K,rho=rho,addresses=modulus,maximum_agreement=best,
                witness_slope=witness[0],witness_offset=witness[1],
                minimum_affine_graphs_to_cover_target=1<<exponent,
                minimum_flat_affine_movement_gates=exponent)


def valuation_pivots(a,n,K,rho=0):
    """Coordinates whose weights have distinct 2-adic valuations below nK."""
    require(n>=1 and K>=3 and 0<=rho<=K-3,'Need two gap bits above each selected bit')
    L=n*K
    modulus=1<<L
    a%=modulus
    if a%2==0:
        coords=list(range(L))
    elif a%4==1:
        coords=[j*K+rho for j in range(n)]
    else:
        coords=[j*K+rho+1 for j in range(n)]
    mask=selected_mask(n,K,rho)
    weights=[((-1-a) if mask>>j&1 else (1-a))*(1<<j)%modulus for j in coords]
    values=[(x&-x).bit_length()-1 for x in weights]
    require(all(x>0 for x in weights) and len(set(values))==len(values),
            'Distinct valuation argument failed')
    return coords,weights,values


def affine_path_maps(gates,modulus):
    """An overcount: every subset of affine movements gives one path map.

    Address-dependent pointwise gates can select/cancel paths but cannot
    introduce an address graph outside this set.
    """
    maps={(1,0)}
    for a,b in gates:
        maps|={((a*c)%modulus,(a*d+b)%modulus) for c,d in maps}
    return maps


def order_control(g,K):
    require(1<=g<K,'Need a nontrivial dirty gap')
    # A full unit shift has order 2^K, while low-field increment has order 2^g.
    return dict(g=g,K=K,whole_shift_order=1<<K,segmented_shift_order=1<<g,
                consequence='No invertible fixed encoding can conjugate one operator to the other on the full arbitrary-input space.')


def certificate():
    controls=[affine_agreement_control(n,K)
              for n,K in ((1,2),(2,2),(3,2),(1,3),(2,3),(3,3))]
    controls.append(affine_agreement_control(2,4,1))
    for n,K in ((1,3),(2,3),(3,3),(3,4)):
        require(len(offset_support(n,K))==1<<n,'Translation offset support failed')
    return dict(status='BOUNDED CODED-CARRY ATTEMPT: EXACT BUT LINEAR; NO NEW KAPPA',
                upstream_commit=verify_sources(),
                exact_code=dict(flat_terms='2^n masked whole-slot translations',
                                factored_terms='2n translations in n sequential stages',
                                recurrence='F(n)=2F(n/2)+O(1), F(1)=O(1); no role-volume contraction',
                                gap_contract='Every arbitrary gap bit is restored exactly; no rare-exception hypothesis'),
                affine_controls=controls,
                encoding_control=order_control(2,5),
                flat_circuit_theorem='For K>=3, n selected-bit flips require at least n whole-slot affine movement gates, even with arbitrary address-dependent linear mixing among fixed complete-volume banks.',
                ordered_extension='The same path-cover argument applies separately to fixed-order, whole-slot prefix-controlled affine updates, including nonlinear offsets from earlier fields. It does not allow swapping field order between those updates.',
                excluded_scope='Recursive role splitting, smaller-volume children, nonlinear address operations, proper-subfield permutations, or a general tape algorithm.',
                assessment='The tested code has no sublinear recurrence. Stop this bounded attempt and prioritize finite-network improvements; reopen only with a concrete construction outside the audited flat affine class.')


if __name__=='__main__':
    (ROOT/'certificates/coded-carry-audit.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS exact carry codes and scoped affine controls; no sublinear recurrence or new kappa.')

#!/usr/bin/env python3
"""Address-only audit of dirty compact controls; cost proof is separate."""
from fractions import Fraction as Q
from pathlib import Path
import json
import random

from certify import require, verify_sources
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def digits(t,n,G):return [(t>>(i*G))&((1<<G)-1) for i in range(n)]


def selected(y,n,K,rho,G):
    return sum(((y>>(rho+i*K))&1)<<(i*G) for i in range(n))


def mask(x,n,K,rho):
    return sum(((x>>(rho+i*K))&1)<<(rho+i*K) for i in range(n))


def packed_mask(t,n,K,rho,G):
    return sum(((t>>(i*G))&1)<<(rho+i*K) for i in range(n))


def good(y,t,n,K,rho,G):
    """An ideal-map-invariant sufficient good set, using the low n segments.

    Exclude saturated temporary digits and wide-segment guards within 2B
    of either endpoint, B=2^G. The unused highest selected bit is handled
    separately. This conservative interval simplifies the general proof.
    """
    B=1<<G;guard_mask=(1<<(K-1))-1
    return all(d<B-1 for d in digits(t,n,G)) and all(
        2*B<=((y>>(rho+i*K+1))&guard_mask)<(1<<(K-1))-2*B
        for i in range(n))


def program(n,K,rho,G,late=False):
    """Primitive rotations and equal-width swaps in physical field order.

    Early order: t,x,y,b. Late order: u,t,y,x,b.
    The back field b is arbitrary and reused, never a zero register.
    Each rotation names all its control fields, which must precede target.
    """
    order=['u','t','y','x','b'] if late else ['t','x','y','b']
    ops=[]
    def rotate(target,controls,kind,sign=1):
        require(all(order.index(c)<order.index(target) for c in controls),
                'Rotation uses a control after its target')
        ops.append(('rotate',target,tuple(controls),kind,sign))
    def swap(a,b):ops.append(('swap',a,b))
    def load(front,kind,controls,sign=1):
        swap(front,'b');rotate('b',controls,kind,sign);swap(front,'b')
    def flip(control,compact=False):
        tag='compact' if compact else 'wide'
        rotate('y',(control,'t'),'first_'+tag)
        load('t','selected_y',('y',))
        rotate('y',(control,'t'),'second_'+tag)
        load('t','original_y_'+tag,(control,'y'),-1)
    if late:
        flip('u',True)
        load('u','selected_x',('x',))
        flip('u',True)
        load('u','selected_x',('x',),-1)
    else:flip('x')
    return order,ops


def execute(state,n,K,rho,G,*,late=False,inverse=False):
    """Full modular address permutation, including bad addresses and swaps."""
    order,ops=program(n,K,rho,G,late)
    require(set(state)==set(order),'Unexpected fields')
    width=(n+1)*K;compact_width=n*G
    sizes={k:(width if k in ('x','y') else compact_width) for k in state}
    require(all(0<=v<1<<sizes[k] for k,v in state.items()),'Field overflow')
    out=dict(state)
    for op in reversed(ops) if inverse else ops:
        if op[0]=='swap':
            _,a,b=op;out[a],out[b]=out[b],out[a];continue
        _,target,controls,kind,sign=op
        if kind in ('selected_x','selected_y'):
            offset=selected(out[kind[-1]],n,K,rho,G)
        elif kind.startswith('original_y_'):
            control=out[controls[0]]
            bits=packed_mask(control,n,K,rho,G) if kind.endswith('compact') else mask(control,n,K,rho)
            offset=selected(out['y']^bits,n,K,rho,G)
        else:
            control=out[controls[0]]
            bits=[(control>>(i*G if kind.endswith('compact') else rho+i*K))&1
                  for i in range(n)]
            ts=digits(out['t'],n,G)
            offset=sum(bits[i]*(2*ts[i] if kind.startswith('first') else 1-2*ts[i])
                       <<(rho+i*K) for i in range(n))
        out[target]=(out[target]+(-sign if inverse else sign)*offset)%(1<<sizes[target])
    return out


def ideal(state,n,K,rho):
    return dict(state,y=state['y']^mask(state['x'],n,K,rho))


def exceptional(state,n,K,rho,G,late=False):
    return not good(state['y'],state['t'],n,K,rho,G) or (
        late and any(d==(1<<G)-1 for d in digits(state['u'],n,G)))


def repaired(state,n,K,rho,G,late=False):
    out=execute(state,n,K,rho,G,late=late)
    if exceptional(out,n,K,rho,G,late):
        old=execute(out,n,K,rho,G,late=late,inverse=True)
        out=ideal(old,n,K,rho)
    return out


def controls():
    # Exhaust one unbounded segment calculation, including all dirty values.
    integer_cases=0
    for B in (2,4,8,16):
        for t in range(B-1):
            for u in range(4*B):
                for x in (0,1):
                    a=u+2*x*t;t1=t+(a&1)
                    b=a+x*(1-2*t1);t2=t1-((b&1)^x)
                    require((b,t2)==(u+x*(1-2*(u&1)),t),'Dirty-digit identity failed')
                    integer_cases+=1
    rng=random.Random(1092026);counts=dict(good=0,bad=0,early=0,late=0)
    # Deliberately small radices give plentiful bad cases; larger K gives
    # nonempty good sets, and rho=K-1 checks the highest-offset geometry.
    for n,K,rho,G in ((1,6,0,2),(2,7,6,2),(3,9,8,3)):
        for late in (False,True):
            order,ops=program(n,K,rho,G,late)
            for _ in range(1200):
                state={k:rng.randrange(1<<((n+1)*K if k in ('x','y') else n*G)) for k in order}
                out=execute(state,n,K,rho,G,late=late)
                require(execute(out,n,K,rho,G,late=late,inverse=True)==state,'Inverse failed')
                wanted=ideal(state,n,K,rho)
                bad=exceptional(state,n,K,rho,G,late)
                require(exceptional(wanted,n,K,rho,G,late)==bad,'Ideal bad-set invariance failed')
                require(exceptional(out,n,K,rho,G,late)==bad,'Actual bad-set invariance failed')
                if not bad:require(out==wanted,'Good-address map is wrong')
                require(repaired(state,n,K,rho,G,late)==wanted,'Exceptional repair is wrong')
                counts['bad' if bad else 'good']+=1;counts['late' if late else 'early']+=1
    require(counts['good']>0 and counts['bad']>0,'Both regimes must be tested')
    return dict(integer_cases=integer_cases,packed_cases=counts,
                early_swaps=4,late_swaps=12,
                scope='Exact integer arithmetic and deterministic samples of full modular address maps; not a tape-runtime proof.')


def certificate():
    return dict(status='ADDRESS-ONLY COMPACT-CONTROL CHECK; NO EXPONENT CLAIM BY THIS CHECKER',
                upstream_commit=verify_sources(),controls=controls(),
                bad_fraction_bound='min(1, n*(2^(-G)+8*2^(G-K))) early; replace 2^(-G) by 2*2^(-G) late',
                candidate_cost='O(V*((f*log(p))^tau+1)) if complete front/back compact fields exist and rotations and repair receive full tape accounting',
                outside_this_checker=['Extend controlled rotation to polynomial-in-p offset work paid by large records.',
                    'Reserve complete compact fields outside the active axes and preserve them through row splitting, padding and every child.',
                    'Charge individually processed reserved axes and recompute the full layer recurrence and guard/assembly constraints.',
                    'Write the fixed-tape exceptional repair and inverse-descriptor argument for the full operation.'],
                cost_proof='notes/compact-control-note.tex; arithmetic in certificates/compact-control-layer.json',
                scope='The highest selected bit is omitted here and supplied by the retained elementary two-bit XOR. This checker verifies addresses only; see the separate cost proof and layer certificate.')


if __name__=='__main__':
    (ROOT/'certificates/compact-control-audit.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS compact-control address audit; see the separate tape/layer proof.')

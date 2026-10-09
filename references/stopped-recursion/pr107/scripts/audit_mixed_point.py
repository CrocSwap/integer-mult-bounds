#!/usr/bin/env python3
"""Bounded mixed-point circuits and a reusable source/target-span frame cut.

Full-size scalar counts are screened before expensive full-size frame work.
The successful frame controls below are small instances, not a new kappa.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
from types import SimpleNamespace
import gc
import json

from certify import require, verify_sources
from exclusion_circuit import ExclusionCircuit
from experiments.mixed_point_circuit import build, plan, factored_transpose
from prepare_layers import serializable
from rational_span_frames import audit, basis, dot, join, nondegenerate
from search_network import log_integer_bounds

ROOT = Path(__file__).resolve().parents[1]
TARGET = Q(1,2**30)


def scalar_check(c):
    """Every entry of the complete intersection-one map, including zeros."""
    require(c.k == c.l == 3 and c.r == 1, 'Wrong top-level relation')
    incident = [0]*c.n
    for i,triple in enumerate(c.inputs):
        for point in triple:
            incident[point] |= 1 << i
    require(c.inputs == c.targets, 'Mismatched source and target order')
    digest = sha256()
    for node in c.active:
        if c.args[node]:
            a,b = c.args[node]
            require(a < node and b < node, 'Non-topological addition')
            require(not c.support[a] & c.support[b], 'Cancellation in monotone circuit')
            require(c.support[node] == c.support[a] | c.support[b], 'Wrong intermediate sum')
        digest.update(json.dumps((node,c.args[node]),separators=(',',':')).encode()+b'\n')
    for i,((a,b,d),node) in enumerate(zip(c.targets,c.outputs)):
        # Odd intersections are one or three; remove the unique diagonal.
        expected = incident[a] ^ incident[b] ^ incident[d] ^ (1 << i)
        require(c.support[node] == expected, 'Incorrect intersection-one output')
        digest.update(json.dumps((i,node),separators=(',',':')).encode()+b'\n')
    return dict(h=c.n,additions=c.additions,outputs=len(c.outputs),
                roles=c.additions+len(c.outputs),all_coefficients_exact=True,
                every_addition_has_disjoint_support=True,circuit_sha256=digest.hexdigest())


def optimistic_score(h,R):
    v = comb(h,3)
    m = h**3
    W = 2*v*v*(v+R+h)
    D = v*v*(v-6*h*h)
    eta = Q(D,W*m)
    loglo,_ = log_integer_bounds(m)
    upper = eta/((1-eta)*loglo)
    qlog = 5*TARGET*loglo
    budget = Q(D)*(1+qlog)/(2*v*v*m*qlog)-v-h
    return dict(bit_saving_upper_if_no_extra_losses=upper,
                kappa_upper_if_no_extra_losses=upper/5,
                fraction_of_target=upper/(5*TARGET),
                necessary_integer_role_budget=(budget.numerator-1)//budget.denominator,
                scope='Retained dimension, central losses, stage sharing and Gaussian assembly; assumes a loss-free frame certificate that has NOT been supplied at this size.')


def dirty_side_check(c):
    adapter = SimpleNamespace(inputs=c.inputs,args=c.args,active=set(c.active),
                              outputs=dict(zip(c.targets,c.outputs)),additions=c.additions)
    code = ExclusionCircuit.compile(adapter)
    v = len(c.inputs)
    x = [1 << i for i in range(v)]
    scratch = [1 << (v+i) for i in range(code['roles'])]
    original = list(scratch)
    y = [0]*v
    operations = []
    for _,ins,outs in code['gates']:
        operations += [(ins[0],slot) for slot in ins[1:]]
        operations += [(slot,ins[0]) for slot in outs[1:]]
    def mix(inverse=False):
        for target,source in reversed(operations) if inverse else operations:
            scratch[target] ^= scratch[source]
    def copy():
        for source,slot in code['sources'].items():
            scratch[slot] ^= x[c.variables[source]-1]
    def inject():
        for i,target in enumerate(c.targets):
            y[i] ^= scratch[code['outputs'][target]]
    # The two side injections cancel every independent arbitrary scratch input.
    mix(); inject(); mix(True); copy()
    mix(); inject(); mix(True); copy()
    require(scratch == original, 'Dirty auxiliary inputs were not restored')
    require(y == [c.support[node] for node in c.outputs], 'Incorrect dirty side map')
    return dict(all_independent_scratch_inputs_restored=True,side_map_exact=True,
                independent_variables=v+code['roles'])


def enclosure_obstruction():
    h = 10
    sources = [(0,1,2),(3,4,5),(6,7,8)]
    targets = list(product(range(3),range(3,6),range(6,9)))
    vector = lambda t:tuple(int(i in t) for i in range(h))
    U = basis(tuple(map(vector,sources)))
    V = basis(tuple(map(vector,targets)))
    radical = (1,)*9+(0,)
    require(all(dot(a,b) == 0 for a in U for b in V), 'Nonorthogonal rectangle')
    require(not nondegenerate(U), 'Expected a degenerate source span')
    require(join(U,(radical,)) == U and join(V,(radical,)) == V, 'Missing shared radical')
    require(len(U)+len(V)-len(join(U,V)) == 1, 'Wrong intersection dimension')
    return dict(ambient_dimension=h,sources=sources,targets=targets,
                source_dimension=len(U),target_dimension=len(V),
                common_radical=radical,intersection_dimension=1,
                scope='No nondegenerate subspace E with U subset E subset V-perp; does not reject arbitrary nonnested matrix frames.')


def certificate():
    # Materialize one full-size example of each decomposition strategy.
    full = []
    for common in (False,True):
        c = build(50,3,3,1,common=common)
        full.append(dict(strategy='hybrid' if common else 'block_only',
                         plan=plan(50,3,3,1,common=common),scalar=scalar_check(c)))
        build.cache_clear()
        del c
        gc.collect()
    require(full[0]['scalar']['roles'] == 698661, 'Block-only screen changed')
    require(full[1]['scalar']['roles'] == 509194, 'Hybrid does not reproduce baseline')

    c = build(50,3,3,1)
    build.cache_clear()
    rounds = []
    for step in range(1,5):
        c,stats = factored_transpose(c)
        rounds.append(dict(step=step,factoring=stats,scalar=scalar_check(c)))
        gc.collect()
    roles = rounds[-1]['scalar']['roles']
    require(roles == 447488, 'Unexpected bounded factoring outcome')
    score = optimistic_score(50,roles)
    require(score['kappa_upper_if_no_extra_losses'] < TARGET, 'Target-capable candidate needs further review')
    del c
    gc.collect()

    controls = []
    for h in (10,12):
        c = build(h,3,3,1)
        for step in range(3):
            if step:
                c,_ = factored_transpose(c)
            scalar = scalar_check(c)
            frame = audit(c)
            require(frame['cut_certified'], 'Small frame-cut control failed')
            controls.append(dict(step=step,scalar=scalar,frames=frame,dirty=dirty_side_check(c)))
    proofs = ['docs/research/mixed-point-audit.md','scripts/experiments/mixed_point_circuit.py',
              'scripts/rational_span_frames.py']
    return dict(status='BOUNDED MIXED-POINT RESEARCH; NO NEW KAPPA',
                upstream_commit=verify_sources(),target=TARGET,
                full_size_decompositions=full,factored_transposition_rounds=rounds,
                role_reduction=Q(509194-roles,509194),optimistic_score=score,
                small_frame_controls=controls,enclosure_obstruction=enclosure_obstruction(),
                source_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in proofs},
                full_size_frame_certificate_supplied=False,
                decision='Stop this bounded topology/factoring search. Retain the source/target-span cut lemma and exact checker for future circuits; current full-size counts miss 2^-30 even with no extra rank losses.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/mixed-point-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS mixed-point screen: 509194 -> 447488 scalar roles; target not reached.')
    print('Small source/target-span cut certificates pass; no full-size frame or kappa claim.')

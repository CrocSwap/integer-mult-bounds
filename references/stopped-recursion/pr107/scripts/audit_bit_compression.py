#!/usr/bin/env python3
"""Bounded compression screen and a scoped paired-template obstruction.

All acceptance comparisons use rational arithmetic. This audit leaves every
published network, parameter witness and source patch unchanged.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import gc
import json

from certify import require, verify_sources
from experiments.bit_compression import Blocked, FilterTree
from paired_exclusion_circuit import PairedExclusionCircuit
from prepare_layers import serializable
from search_network import log_integer_bounds
from shared_point_circuit import SharedPointCircuit
from shared_point_network import counts

ROOT = Path(__file__).resolve().parents[1]
TARGET = Q(1, 2**30)


def verify_local(c):
    """Check every coefficient, using incident-edge masks to avoid sampling."""
    incident = [0]*c.n
    for i, (a, b) in enumerate(c.inputs):
        incident[a] |= 1 << i
        incident[b] |= 1 << i
    full = (1 << len(c.inputs))-1
    for node in c.active:
        if c.args[node]:
            a, b = c.args[node]
            require(a < node and b < node, 'Non-topological circuit')
            require(not c.support[a] & c.support[b], 'Overlapping summands')
            require(c.support[node] == c.support[a] | c.support[b], 'Wrong sum')
    require(set(c.outputs) == set(c.inputs), 'Missing exclusion output')
    for (a, b), node in c.outputs.items():
        require(c.support[node] == full ^ (incident[a] | incident[b]),
                'Incorrect pair-exclusion coefficient map')
    return True


def classify_nodes(c):
    """Local edge intersections classify globally shareable pair-star sums.

    A local sum with empty edge intersection has only its module's common
    point globally, so another module cannot compute that same sum. Retain
    every star that directly feeds such a node; credit all other stars free.
    """
    core = [0]+[(1 << a) | (1 << b) for a, b in c.inputs]
    for node in range(len(c.inputs)+1, len(c.args)):
        a, b = c.args[node]
        core.append(core[a] & core[b])
    unshareable = {node for node in c.active if c.args[node] and not core[node]}
    stars = {node for node in c.active if c.args[node] and core[node]}
    require(all(core[node].bit_count() == 1 for node in stars),
            'A nontrivial local sum must not have a two-point intersection')
    frontier = {child for node in unshareable for child in c.args[node]
                if child in stars}
    require(set(c.outputs.values()) <= unshareable,
            'Output is not an unshareable nontrivial sum')
    return dict(unshareable=len(unshareable), stars=len(stars),
                mandatory_frontier_stars=len(frontier))


def bound(h, c):
    """Necessary bound for unchanged local gates with equal-sum merging.

    Each mandatory frontier star can occur in at most two common-point
    modules. Non-frontier star subcircuits may disappear when alternate
    decompositions are chosen; they are deliberately not counted here.
    """
    require(h == c.n+1 and h >= 40 and h % 2 == 0, 'Invalid ground size')
    verify_local(c)
    cls = classify_nodes(c)
    q = h*len(c.outputs)
    roles = h*cls['unshareable']+(h*cls['mandatory_frontier_stars']+1)//2+q
    v = comb(h, 3)
    m = h**3
    deficit = v*v*(v-6*h*h)
    W = 2*v*v*(v+roles+h)
    eta = Q(deficit, W*m)
    loglo, _ = log_integer_bounds(m)
    upper = eta/((1-eta)*loglo)
    qlog = 5*TARGET*loglo
    budget = Q(deficit)*(1+qlog)/(2*v*v*m*qlog)-v-h
    return dict(h=h, local_additions=c.additions, **cls,
                side_roles_lower=roles, bit_saving_upper=upper,
                kappa_upper=upper/5, fraction_of_target=upper/(5*TARGET),
                necessary_integer_role_budget=(budget.numerator-1)//budget.denominator)


def local_configs():
    configs = [dict(family='filter', kind=kind) for kind in ('balanced', 'vertex')]
    configs += [dict(family='block', k=k, leaf=leaf, vec=vec, order=0, assoc=0)
                for k, leaf, vec in product((2,3,4,6,8), (3,4,6,8),
                                           ('prefix','tree','paired'))]
    configs += [dict(family='block', k=2, leaf=4, vec='prefix', order=order, assoc=assoc)
                for order, assoc in product(range(3), range(4))]
    return list({json.dumps(p, sort_keys=True):p for p in configs}.values())


def build(config, n=49):
    options = dict(config)
    family = options.pop('family')
    return Blocked(n, **options) if family == 'block' else FilterTree(n, **options)


def certificate():
    local = []
    for config in local_configs():
        c = build(config)
        result = bound(50, c)
        require(result['kappa_upper'] < TARGET, 'Screen found a target-capable candidate')
        local.append(dict(config=config, local_roles=c.additions+len(c.outputs),
                          optimistic_merging_bound=result))

    global_rows = []
    for leaf, vec, order in product((3,4), ('prefix','tree','paired'), range(3)):
        config = dict(family='block', k=2, leaf=leaf, vec=vec, order=order, assoc=0)
        c = SharedPointCircuit(50, build(config))
        n = counts(50, c)
        loglo, loghi = log_integer_bounds(n['m'])
        lower = n['eta']/loghi
        upper = n['eta']/((1-n['eta'])*loglo)
        global_rows.append(dict(config=config, side_roles=n['side_roles_per_invocation'],
                                bit_saving_lower=lower, bit_saving_upper=upper,
                                merged_additions=c.merged))
        del c
        gc.collect()
    best = min(global_rows, key=lambda row:row['side_roles'])
    c = SharedPointCircuit(50, build(best['config']))
    symbolic = c.verify()
    frames = c.verify_frames()
    require(best['side_roles'] == 509146, 'Unexpected best bounded circuit')
    require(best['bit_saving_upper']/5 < TARGET, 'Best circuit crosses the target')

    finite = [bound(h, PairedExclusionCircuit(h-1)) for h in range(40,112,2)]
    require(all(row['kappa_upper'] < TARGET for row in finite), 'Finite ground-size exception')
    # For h>=112, each module has C(h-1,2) distinct unshareable outputs.
    # Thus c>=3v, R=c+q>=6v, eta<1/(14 h^3). The following upper bound
    # decreases with h and already excludes the target at the endpoint.
    cutoff = 112
    loglo, _ = log_integer_bounds(cutoff**3)
    tail = 1/((14*cutoff**3-1)*loglo)
    require(tail/5 < TARGET, 'Large-ground tail does not exclude the target')
    peak = max(finite, key=lambda row:row['kappa_upper'])
    proofs = ['docs/research/bit-compression-audit.md',
              'scripts/experiments/bit_compression.py']
    return dict(status='BOUNDED NEGATIVE SCREEN; NO NEW MULTIPLICATION WITNESS',
                upstream_commit=verify_sources(), target=TARGET,
                current_bit_saving=Q(296,10**11),
                local_candidates=local, global_candidates=global_rows,
                best_global=best, best_global_symbolic_check=symbolic,
                best_global_frame_check=frames,
                role_improvement_ratio=Q(509194,best['side_roles']),
                paired_template_all_even_h=dict(finite=finite, finite_peak=peak,
                    tail_cutoff=cutoff, tail_bit_saving_upper=tail,
                    nonpositive_deficit_below=40,
                    scope='Existing paired local template, arbitrary independent relabelings, equal-sum identification and pruning only; c+q compiler, separate partial outputs and original central losses retained.'),
                source_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in proofs},
                decision='Stop this compression round. Larger gains must change local gates beyond the screened variants, combine different common-point contributions with new frame proofs, or alter the central/topological contract.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/bit-compression-audit.json').write_text(
        json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    print('PASS bounded bit compression: 509194 -> 509146 roles; no new kappa.')
    print('Paired-template relabel/merge-only route excludes 2^-30 for every admissible even h.')

#!/usr/bin/env python3
"""Frame-independent routing screen and a bounded cyclic-XOR experiment."""
from functools import lru_cache
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json

from certify import require, verify_sources
from finite_bit_contract import (xor_gate, scalar_permutation, zero_frame_candidate,
                                 inspect_candidate, find_routing)

ROOT = Path(__file__).resolve().parents[1]


def swap_word(a,b):
    return [xor_gate(a,b), xor_gate(b,a), xor_gate(a,b)]


def cyclic_seed(W, star=False):
    pairs = [(0,b) if star else (b-1,b) for b in range(1,W)]
    return [gate for a,b in pairs for gate in swap_word(a,b)]


def routing_state_search(W, max_depth):
    """Enumerate (GF2 scalar matrix, reachable port-routing permutations).

    Drop states whose routing set is all of S_W: that property persists under
    every subsequent gate, so such words can never escape the routing screen.
    Merge only identical joint states, not equal scalar maps alone. A closed
    frontier proves the result for all lengths; a depth cutoff does not.
    """
    require(W in (2,3,4), 'This bounded implementation permits at most four roles')
    require(type(max_depth) is int and 0 <= max_depth <= 7, 'Explicit depth cap is seven')
    perms = list(permutations(range(W))); index = {p:i for i,p in enumerate(perms)}
    full = (1 << len(perms))-1
    pairs = [(t,s) for t in range(W) for s in range(t)]
    swaps = []
    for t,s in pairs:
        targets = []
        for p in perms:
            q = list(p); q[t],q[s] = q[s],q[t]
            targets.append(index[tuple(q)])
        swaps.append(targets)

    @lru_cache(None)
    def extend(R,pair):
        bits = R; result = R
        while bits:
            bit = bits & -bits
            result |= 1 << swaps[pair][bit.bit_length()-1]
            bits -= bit
        return result

    initial = (tuple(1 << i for i in range(W)),1)
    seen = {initial}; frontier = {initial}; layers = []; saturated = 0
    all_length = False; survivors = []
    for depth in range(max_depth+1):
        terminals = 0; digest = sha256()
        for M,R in sorted(frontier):
            digest.update((repr((M,R))+'\n').encode())
            if all(x and x & (x-1) == 0 for x in M):
                terminals += 1
                p = tuple(x.bit_length()-1 for x in M)
                if not (R >> index[p]) & 1:
                    survivors.append(dict(depth=depth,scalar_rows=list(M),routing_set=R))
        layers.append(dict(depth=depth,new_states=len(frontier),
                           permutation_states=terminals,frontier_sha256=digest.hexdigest()))
        if survivors or not frontier or depth == max_depth:
            all_length = not frontier
            break
        nxt = set()
        for M,R in frontier:
            for pair,(a,b) in enumerate(pairs):
                S = extend(R,pair)
                if S == full:
                    saturated += 2
                    continue
                for t,s in ((a,b),(b,a)):
                    A = list(M); A[t] ^= A[s]
                    state = (tuple(A),S)
                    if state not in seen: nxt.add(state)
        seen.update(nxt); frontier = nxt
    return dict(W=W,depth_cap=max_depth,layers=layers,distinct_joint_states=len(seen),
                saturated_transitions_discarded=saturated,frontier_closed=all_length,
                all_lengths_excluded=all_length and not survivors,
                all_words_through_depth_excluded=not survivors,
                survivors=survivors,
                scope='Two-port XOR words on exactly W arbitrary-input roles. A closed joint-state frontier excludes every length; otherwise only lengths through depth_cap are covered.')


def certificate():
    seeds = []
    for W in range(3,7):
        for star in (False,True):
            gates = cyclic_seed(W,star)
            candidate = zero_frame_candidate(W,gates)
            score = inspect_candidate(candidate,require_deficit=False)
            route = find_routing(W,gates)
            require(route['routable'], 'Unexpected unroutable cyclic seed')
            require(score['deficit'] == 0, 'Equality control changed')
            seeds.append(dict(W=W,family='star' if star else 'adjacent',
                              gates=gates,rho=list(scalar_permutation(W,gates)),
                              equality_control=score,routing=route))
    searches = [routing_state_search(2,7),routing_state_search(3,7),routing_state_search(4,7)]
    require(all(not r['survivors'] for r in searches), 'Structural survivor requires investigation')
    require(searches[0]['all_lengths_excluded'] and searches[1]['all_lengths_excluded'],
            'Small-role closure failed')
    require(not searches[2]['frontier_closed'], 'Four-role search scope changed')
    sources = ('scripts/finite_bit_contract.py','scripts/audit_cyclic_topology.py',
               'docs/research/cyclic-topology-audit.md')
    return dict(status='GENERAL EXACT VERIFIER; ROUTING OBSTRUCTION; NO NEW KAPPA',
                upstream_commit=verify_sources(),cyclic_seeds=seeds,word_searches=searches,
                theorem='An edge-disjoint routing of the actual scalar permutation implies s>=W*m for all rational frames satisfying the endpoint contract, in every m>=2.',
                full_improved_frame_certificate_supplied=False,
                decision='Do not optimize frames on routable topologies. Seek a scalar-correct nonroutable circuit before matrix search; nonroutability alone is not a rank deficit.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/cyclic-topology-audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS exact contract controls and cyclic routing; two/three-role closure; four-role depth-seven screen; no new kappa.')
